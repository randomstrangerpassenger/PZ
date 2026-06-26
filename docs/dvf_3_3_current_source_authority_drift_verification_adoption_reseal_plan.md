# Implementation Plan

> Status: planned / roadmap-derived / current-checkout-informed / PASS for Phase 0~3 / branch-closeout gated / Branch A closeout WARN revisions incorporated / DVF 3-3 current source authority drift verification adoption reseal / governance-only branch decision and reseal plan
> 작성일: 2026-06-25
> Roadmap input: `C:/Users/MW/.codex/attachments/0823d17f-91c3-408f-b04c-9f06e3196191/pasted-text.txt` / sha256 `61472555F3E29BC5862FA54A0A46C4DDF1E1825CEE208C6947888A56DB612AFA` / lines `669`
> Final review input: `C:/Users/MW/.codex/attachments/e31c909e-aec2-479f-b836-f4311ae80d6f/pasted-text.txt` / sha256 `7E3E2AC67D7C242C11235D0DA2571992B8C893CE008A4F74B0873E6A20382F3D` / lines `272` / verdict `WARN` / required revisions incorporated
> Cycle 2 final review input: `C:/Users/MW/.codex/attachments/6170d62a-b28a-4238-a772-d8e7425b6b4a/pasted-text.txt` / sha256 `2BDC0AA7B249B6D44B13B100B120F4725EE203B52D1BB322114B24A3DC5B869D` / lines `196` / verdict `PASS with minor revisions` / minor revisions incorporated
> Preflight seed review input: `C:/Users/MW/.codex/attachments/4ce2eb8d-d3ff-4c61-b469-d6aaf0918f93/pasted-text.txt` / verdict `WARN` / identity, original-scope, parity, and JSON-aware matching revisions incorporated into this plan
> Adoption reseal review input: `C:/Users/MW/.codex/attachments/cd1fe61d-c615-4dcd-8625-440b4c822ac1/pasted-text.txt` / verdict `PASS for Phase 0~3 / WARN for Branch A closeout` / selected-branch validation and Branch A clean-checkout forward-dependency revisions incorporated
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Direct plan artifact: `docs/dvf_3_3_current_source_authority_drift_verification_adoption_reseal_plan.md`
> Primary evidence root target: `Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_adoption_reseal/`
> Current checkout observation, provisional: `Iris/_docs/round3/current_route_required_validations.json` appears to contain evidence-freshness reseal required artifacts/tests, and existing phase6 evidence appears to report `required_validation_gate_adopted=true`. Phase 0 must re-derive this sealed-reseal-record to live-manifest relationship. If the observation is false or divergent, the plan must stop as `blocked_sealed_reseal_live_divergence_resolution_required`, not absorb the divergence into Branch A or Branch B.
> Execution readiness rule: Phase 0~3 inventory, re-derivation, source identity redrive, and branch predicate reporting may proceed. Branch A adoption closeout, Branch B isolation closeout, shared runner containment fix, and final seal remain gated by the Branch Selection Contract, selected-branch fresh current-route validation, sealed/live divergence terminal, minimal runner write-sink gate, single-writer models, taxonomy separation cross-check, co-readpoint token, no-intervening-write report, negative fixture matrix, artifact field schema, tracking enum, Branch A clean-checkout forward-dependency report, non-Claude independent review, and owner seal. This PASS is plan-structure PASS, not empirical verification of manifest / taxonomy / tracking / `2105` / `OSError 22` state. This exact limitation must survive into the final report.
> Implementation compression rule: if implementation omits the Branch Selection Contract validator, sealed-reseal/live-manifest re-derivation, Branch B fresh current-route PASS, B-marked schema-supported marker validation, taxonomy single-writer report, co-readpoint token, no-intervening-write report, or negative fixture matrix, the execution verdict must downgrade to `WARN` or `FAIL` instead of closing as Branch A, Branch B, final seal, or canonical seal.
> Limitation: `docs/EXECUTION_CONTRACT.md` compliance is recommended but not plan-blocking because the contract was not part of the reviewed surface. If the contract exists in the checkout, docs reconciliation or independent review should add a one-line compliance statement.
> Original reproducibility/taxonomy preflight limitation: this Adoption Reseal plan does not close the broader Current-Route Required Evidence Reproducibility / Taxonomy Disposition Preflight unless a separately scoped closeout explicitly proves clean-checkout required-input reproducibility and Execution Contract compliance for that original identity.

---

## 1. Objective

Write and execute a governance-only plan for DVF 3-3 Current Source Authority Drift Verification / Adoption Reseal.

The concrete objective is to make the current source authority drift verification round unambiguous in the current-route governance chain. After execution, it must be readable as exactly one of the following:

* `current_source_authority_drift_required_gate_adopted`
* `current_source_authority_drift_candidate_isolated`
* `current_source_authority_drift_historical_only`
* `current_source_authority_drift_diagnostic_only`
* `current_source_authority_drift_non_current_contingency`
* `current_source_authority_drift_adoption_reseal_complete`

The plan reconciles these surfaces to one readpoint:

* docs canonical PASS claims
* `Iris/_docs/round3/round3_test_taxonomy.json`
* live `Iris/_docs/round3/current_route_required_validations.json`
* current-route runner behavior
* current source identity evidence
* drift verification evidence root
* evidence freshness reseal evidence root
* VCS tracking / reproducibility status
* independent review and owner seal reports

The objective is not source restoration, old predecessor recovery, live writer authorization, runtime mutation, package mutation, release readiness, or public text acceptance.

The final report must also carry the original-scope ceiling fields so this adoption reseal cannot be mistaken for the broader reproducibility/taxonomy preflight closeout:

```text
clean_checkout_reproducibility_proof_status = out_of_scope_not_claimed | separately_proven_by_this_execution
original_required_evidence_reproducibility_preflight_status = not_closed_by_this_plan | separately_closed_with_evidence
```

---

## 2. Scope

This plan covers current-route governance adoption or explicit non-current isolation for the Current Source Authority Drift Verification / Recovery Scope Retirement round.

Included:

* current-state re-derivation and inventory lock
* sealed-reseal-record to live-manifest re-derivation
* docs claim scan across `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, and existing related plan / claim-boundary / ledger docs
* taxonomy presence and status scan
* JSON-aware manifest/taxonomy matching with exact-match vs substring-only distinction
* taxonomy separation additive-compatibility cross-check
* taxonomy single-writer ownership model or explicit non-writer rationale
* live required-validation manifest presence and field-check scan
* live manifest single-writer ownership model
* distinction between original drift verification artifacts and evidence-freshness reseal drift-consumption artifacts
* tracking / untracked / ignored / missing classification for related tools, tests, docs, compact evidence, and raw staging evidence
* fixed tracking / reproducibility enum classification
* `OSError 22` or equivalent current-route rerun blocker triage
* `minimal_runner_write_sink_fix` gate, only if diagnosis proves code containment is required
* current source identity re-derivation for successor `2105`
* adoption decision matrix and mechanical Branch Selection Contract
* branch label / tracking enum / blocked state / mandatory guard token parity checks internal to this plan
* owner-reserved Branch A / Branch B selection after machine predicates pass
* Branch A adopted-required-gate integration, if approved
* Branch A new adopted required-input clean-checkout reproducibility basis or explicit forward dependency
* Branch A required-validation count delta reporting
* Branch B non-current / candidate / historical / diagnostic isolation, split into B-pure and schema-supported B-marked
* artifact tracking and reproducibility reseal
* required artifact field schema for final reports, review manifests, source identity, manifest mutation, taxonomy adoption, and no-mutation reports
* fresh current-route validation reseal
* co-readpoint identity token and no-intervening-write check
* docs / ledger reconciliation by additive supersession
* non-Claude independent review and owner seal

### Explicitly Out Of Scope

* source restoration
* old predecessor recovery
* `facts / decisions / overlay_support` live-write
* rendered output regeneration or promotion
* Lua bridge export
* runtime chunk replacement
* package payload mutation
* Phase 4 live migration execution
* terminal disposition re-adjudication
* denominator redefinition
* shared disposition ledger re-adoption
* current-route test architecture redesign
* broad runner architecture rewrite
* shared runner behavior changes outside the `minimal_runner_write_sink_fix` gate
* validation predicate changes disguised as `OSError 22` containment
* sealed drift verification report body rewrite
* sealed evidence freshness reseal report body rewrite
* Branch A adoption without mechanical predicate proof
* Branch B isolation without fresh current-route validation PASS
* owner seal as substitute for branch predicate validation
* release / package / Workshop / B42 / deployment readiness
* manual in-game QA
* semantic quality completion
* public-facing text acceptance
* full external mod compatibility sweep

---

## 3. Non-Goals

This plan does not attempt to:

* prove that Iris runtime output is semantically complete
* change Browser / Wiki / Tooltip behavior
* change Lua runtime data, chunks, or package payloads
* reopen vNext current authority implementation / `2105` consumer migration
* convert predecessor `2105 / 2084 / 21` into current debt, runtime authority, package authority, or release readiness
* treat `Base.CanOpener` or the old 6-entry predecessor fixture payload as current-looking source
* treat raw staging evidence as direct execution authority
* treat tracked status as authority status
* treat ignored status as proof of irrelevance
* count post-run external bundle checks as current-route required tests unless the live manifest explicitly requires them
* treat owner branch selection as machine proof
* close Branch B on unchanged-hash evidence without fresh current-route PASS
* absorb sealed-reseal-record to live-manifest divergence into Branch A or Branch B
* change current-route validation predicates while calling it write-sink containment
* use standalone `PASS`, `complete`, `closed`, `current`, or `ready` without an owning claim axis
* claim that this adoption reseal closes the broader clean-checkout required evidence reproducibility preflight without explicit proof fields and separate evidence

---

## 4. Assumptions

* `docs/Philosophy.md` is the top authority.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are current ecosystem readpoints.
* Iris remains a 100% Lua runtime mod; Python tooling here is offline build / evidence tooling, not Iris runtime behavior.
* Current source authority is the successor chain `data/dvf_3_3_input_manifest.json -> data/dvf_3_3_facts.jsonl -> data/dvf_3_3_decisions.jsonl -> data/dvf_3_3_overlay_support.jsonl` under successor `2105` row identity.
* Drift verification is read-only governance evidence and cannot authorize source, rendered, Lua bridge, runtime, package, or release mutation.
* Existing evidence freshness reseal artifacts are current-checkout inputs, not automatic final proof for this new adoption-reseal plan.
* The current checkout observation in the header is provisional. Phase 0 must re-derive whether sealed reseal consumption claims in docs/evidence correspond to live manifest entries in this checkout.
* Sealed-reseal-record to live-manifest divergence is a terminal blocked state: `blocked_sealed_reseal_live_divergence_resolution_required`.
* Branch A adoption is allowed only if the Branch Selection Contract proves direct drift adoption and evidence-freshness reseal drift-consumption are distinguished, live manifest / taxonomy / runner / field-check / negative fixture / tracking alignment all pass, and any sealed candidate boundary conflict is resolved by additive supersession.
* If any Branch A predicate fails, Branch A is forbidden. Owner decision cannot override failed machine predicates.
* Branch B isolation is allowed only as an explicit non-current adoption/isolation decision, not as a fallback for failed Branch A proof.
* Branch B requires fresh current-route validation PASS with `closure_enforced=true`. Live manifest unchanged hash and expected count unchanged are supporting evidence only.
* Branch B has two modes: `B-pure` means live manifest unchanged; `B-marked` means an additive evidence-only marker may be written only if the live manifest schema explicitly supports `evidence_only_marker` or an equivalent non-required marker class. `B-marked` must not claim unchanged manifest hash.
* If the live manifest schema does not explicitly support a non-required marker class, B-marked evidence must be recorded only in ledger packet, claim boundary, and/or taxonomy candidate status; it must not be written to live `current_route_required_validations.json`.
* If neither Branch A nor Branch B predicates pass, the closeout state is `blocked_branch_selection_predicate_unsatisfied`.
* If fresh current-route validation is blocked by `OSError 22` or equivalent failure, Branch A and Branch B cannot close and the closeout state is `blocked_fresh_readpoint_validation_required`.
* `OSError 22` handling is diagnosis-only by default. Code changes require the separate `minimal_runner_write_sink_fix` gate.
* `minimal_runner_write_sink_fix` may only alter write-sink mechanics such as path normalization, directory guarantee, per-run sink routing, or atomic write handling. It must not alter validation predicates, required sets, runner semantics, branch predicates, or PASS interpretation.
* Runner predicate diff scope includes the whole current-route class and existing sealed baseline expectations, not only this plan's new tests.
* Taxonomy changes must include a taxonomy separation additive-compatibility check proving this round does not implicitly supersede the earlier evidence-freshness reseal taxonomy separation.
* Live `current_route_required_validations.json` must have a single-writer model. Adoption-reseal tooling must prove it is either the canonical writer for this round's approved additive patch or only emits candidate/sandbox patches.
* `Iris/_docs/round3/round3_test_taxonomy.json` must also have a single-writer model for this round, or the plan must record why taxonomy is classification metadata outside the required-validation writer model. Branch A/B taxonomy changes cannot be dual-written by unrelated tools.
* Fresh validation must stamp runner hash, taxonomy hash, live manifest hash, evidence root hash, external bundle hash, current source identity hash, and dirty-state summary into a co-readpoint identity token. No intervening writes are allowed between token capture and validation closeout.
* Required artifact field schema is fixed before Branch A mutation. Final report, primary review manifest, source identity redrive, manifest mutation report, taxonomy adoption report, and no-mutation report each need required fields.
* Branch A may adopt new live required inputs only when each new input has `clean_checkout_reproducibility_basis=tracked_required` or an explicit forward dependency to the broader reproducibility/taxonomy preflight. New untracked `generated_reproducible` inputs cannot imply clean-checkout reproducibility in this plan.
* Branch A live-manifest count changes must emit a required-validation count delta report before branch closeout.
* Tracking / reproducibility classification uses a fixed enum: `tracked_required`, `generated_reproducible`, `raw_staging_ignored`, `historical_only`, `diagnostic_only`, `forbidden_current_consumption`, `missing_blocks_validation`, `not_applicable`.
* Branch labels, blocked states, tracking / reproducibility enum values, and mandatory guard names are fixed tokens for this plan. Phase 0 must emit a parity report proving implementation token sets match the plan token sets before Phase 0~3 can be treated as execution-ready.
* Manifest and taxonomy presence reports are JSON-aware machine predicates. Text search may be retained as preliminary inspection only and cannot satisfy Branch A or Branch B predicates by itself.
* Exact ID/path matches and substring-only matches are distinct. Substring-only matches cannot satisfy adoption/isolation predicates unless a named exception is recorded and reviewed.
* Negative fixtures must run against sandbox copies and must not mutate live manifest, sealed evidence roots, source, rendered, Lua bridge, runtime chunks, or package payloads.
* Dirty working tree changes outside this plan are preserved. This plan must not revert existing user or generated changes.
* Validation depth is heavy because this changes or confirms governance consumption, even though runtime behavior is unchanged.
* Canonical completion requires machine PASS, non-Claude independent review PASS, and owner seal PASS.
* The broader Current-Route Required Evidence Reproducibility / Taxonomy Disposition Preflight remains outside this plan's closeout unless this execution separately proves clean-checkout required-input reproducibility and records that proof explicitly.
* `docs/EXECUTION_CONTRACT.md` compliance remains recommended / non-blocking for this plan overall, but Branch A closeout must include an owner review entry deciding whether live-manifest mutation requires blocking-unless-proven-N/A contract treatment in a later revision.

---

## 5. Repository Areas Affected

### Code

Possible offline tooling / test surfaces:

* `Iris/_docs/round3/round3_run_contract_tests.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py`

Read-only supporting tooling / tests:

* `Iris/build/description/v2/tools/build/dvf_3_3_current_source_authority_drift_verification.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_current_source_authority_drift_verification.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py`

### Docs

New direct plan:

* `docs/dvf_3_3_current_source_authority_drift_verification_adoption_reseal_plan.md`

Expected execution docs:

* `docs/dvf_3_3_current_source_authority_drift_verification_adoption_reseal_claim_boundary.md`
* `docs/dvf_3_3_current_source_authority_drift_verification_adoption_reseal_ledger_packet.md`

Additive reconciliation candidates:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Read-only context docs:

* `docs/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement_plan.md`
* `docs/dvf_3_3_current_source_authority_drift_verification_claim_boundary.md`
* `docs/dvf_3_3_current_source_authority_drift_verification_ledger_packet.md`
* `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_plan.md`
* `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_claim_boundary.md`
* `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_ledger_packet.md`
* `docs/dvf_vcs_tracking_policy.md`

### Config

Branch A possible mutation, only after owner decision:

* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `.gitignore`, only if raw staging / compact evidence tracking policy requires an additive ignore rule

Branch B expected behavior:

* B-pure: live `Iris/_docs/round3/current_route_required_validations.json` remains unchanged
* B-marked: live `Iris/_docs/round3/current_route_required_validations.json` may receive an owner-approved evidence-only marker only when the manifest schema explicitly supports `evidence_only_marker` or an equivalent non-required class; otherwise B-marked evidence is recorded outside the live manifest
* taxonomy may record candidate / historical / diagnostic / non-current classification if approved
* `.gitignore` changes must not hide already-tracked required artifacts or manifest-consumed compact evidence

### Generated Artifacts

Primary new evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_adoption_reseal/`

Key expected artifacts:

* `phase0/current_state_rederivation_report.json`
* `phase0/docs_claim_scan_report.json`
* `phase0/taxonomy_presence_report.json`
* `phase0/taxonomy_presence_structured_match_report.json`
* `phase0/taxonomy_separation_additive_compatibility_report.json`
* `phase0/required_manifest_presence_report.json`
* `phase0/required_manifest_presence_structured_match_report.json`
* `phase0/sealed_reseal_record_live_manifest_rederivation_report.json`
* `phase0/vcs_tracking_reproducibility_report.json`
* `phase0/protected_surface_no_mutation_report.json`
* `phase0/plan_token_parity_report.json`
* `phase1/oseerror22_diagnosis.json`
* `phase1/minimal_runner_write_sink_fix_report.json`, only if code containment is required
* `phase1/shared_runner_predicate_diff_report.json`
* `phase1/runner_write_sink_diff_scope_report.json`, only if code containment is required
* `phase2/current_source_identity_redrive_report.json`
* `phase3/adoption_decision_matrix_report.json`
* `phase3/branch_selection_contract_report.json`
* `phase4a/current_route_required_gate_consumption_report.json`
* `phase4a/required_artifact_field_schema.json`
* `phase4a/adopted_required_input_reproducibility_forward_dependency_report.json`
* `phase4a/required_validation_count_delta_report.json`
* `phase4a/live_manifest_single_writer_report.json`
* `phase4a/taxonomy_single_writer_report.json`
* `phase4b/current_source_authority_drift_non_current_isolation_report.json`
* `phase4b/branch_b_mode_report.json`
* `phase4b/branch_b_field_schema_report.json`
* `phase5/required_artifact_tracking_matrix.json`
* `phase5/tracking_reproducibility_enum_report.json`
* `phase5/raw_staging_direct_authority_read_report.json`
* `phase6/current_route_validation_result.json`
* `phase6/co_readpoint_identity_token.json`
* `phase6/no_intervening_write_report.json`
* `phase6/external_validation_bundle_manifest.json`
* `phase6/final_validation_wrapper_report.json`
* `phase7/docs_reconciliation_report.json`
* `phase7/forbidden_overclaim_scan_report.json`
* `phase8/primary_review_artifact_manifest.json`
* `phase8/independent_review_artifact_hash_report.json`
* `phase8/owner_seal_report.json`
* `phase8/final_current_source_authority_drift_verification_adoption_reseal_report.json`

---

## 6. Planned Changes

### Change 1 - Phase 0 Current-State Re-derivation / Inventory Lock

Purpose:

Lock the current checkout readpoint across docs claims, taxonomy, live required manifest, runner, evidence roots, and VCS tracking.

Files:

* Read: `docs/DECISIONS.md`
* Read: `docs/ARCHITECTURE.md`
* Read: `docs/ROADMAP.md`
* Read: `Iris/_docs/round3/round3_test_taxonomy.json`
* Read: `Iris/_docs/round3/current_route_required_validations.json`
* Write: `phase0/current_state_rederivation_report.json`
* Write: `phase0/docs_claim_scan_report.json`
* Write: `phase0/taxonomy_presence_report.json`
* Write: `phase0/taxonomy_presence_structured_match_report.json`
* Write: `phase0/taxonomy_separation_additive_compatibility_report.json`
* Write: `phase0/required_manifest_presence_report.json`
* Write: `phase0/required_manifest_presence_structured_match_report.json`
* Write: `phase0/sealed_reseal_record_live_manifest_rederivation_report.json`
* Write: `phase0/vcs_tracking_reproducibility_report.json`
* Write: `phase0/plan_token_parity_report.json`

Implementation Notes:

* Separate original drift verification artifacts from evidence-freshness reseal drift-consumption artifacts.
* Record whether existing live manifest entries are direct drift adoption, evidence-freshness consumption, candidate-only evidence, or unrelated required gates.
* Produce JSON-aware manifest/taxonomy structured match rows. `Select-String` or equivalent text search may be logged as preliminary inspection only.
* Each structured match row must include `match_kind`, `matched_path_or_test_id`, `matched_by`, `exact_id_match`, `substring_only`, and `supports_branch_predicate`.
* `exact_id_match=false` or `substring_only=true` cannot satisfy Branch A / Branch B machine predicates without an explicit reviewed exception.
* Re-derive whether sealed reseal records and docs claims that assert live manifest consumption correspond to the actual live `current_route_required_validations.json` in this checkout.
* If sealed reseal record and live manifest diverge, stop with `blocked_sealed_reseal_live_divergence_resolution_required`. Do not convert the divergence into Branch A adoption or Branch B isolation.
* Check that this round's planned taxonomy status does not implicitly supersede the earlier evidence-freshness reseal taxonomy separation.
* Classify tools/tests/docs/evidence as tracked, untracked, ignored, missing, generated-reproducible, raw-staging, historical, or diagnostic.
* Emit `phase0/plan_token_parity_report.json` proving branch labels, tracking / reproducibility enum values, blocked states, and mandatory guard names used by implementation match this plan.
* Record dirty working tree state without reverting it.

Validation:

* inventory generator PASS
* docs claim scanner PASS
* taxonomy parser PASS
* required manifest parser PASS
* JSON-aware manifest/taxonomy structured match reports PASS
* sealed-reseal-record to live-manifest re-derivation PASS or terminal blocked state recorded
* taxonomy separation additive-compatibility PASS
* git tracking report generated
* plan token parity report PASS
* protected source / rendered / Lua bridge / runtime / package no-mutation check PASS

---

### Change 2 - Phase 1 Freshness Blocker / `OSError 22` Check

Purpose:

Determine whether a current-route broad rerun is blocked by `OSError 22` or equivalent write-sink / Windows path failure, without silently changing runner semantics.

Files:

* Read: `Iris/_docs/round3/round3_run_contract_tests.py`
* Write: `phase1/oseerror22_diagnosis.json`
* Write: `phase1/containment_no_seal_mutation_proof.json`, if containment is needed
* Write: `phase1/minimal_runner_write_sink_fix_report.json`, only if code containment is required
* Write: `phase1/shared_runner_predicate_diff_report.json`
* Write: `phase1/runner_write_sink_diff_scope_report.json`, only if code containment is required

Implementation Notes:

* Reproduce or classify the blocker before any branch closeout.
* Record `blocker_artifact_path`, `blocker_log_reference`, and `blocker_observed_command` when blocker evidence exists.
* Default outcome is diagnosis-only. If diagnosis shows fresh validation is blocked, Branch A and Branch B closeout remain blocked until the blocker is resolved.
* If code containment is needed, open the `minimal_runner_write_sink_fix` sub-gate before changing shared runner code.
* `minimal_runner_write_sink_fix` is limited to per-run sink redirect, path normalization, directory creation, or atomic write handling.
* Runner architecture rewrite, validation predicate change, required-set change, PASS reinterpretation, or branch predicate change is forbidden in this plan.
* If containment changes shared runner code, `runner_write_sink_diff_scope_report.json` must include `required_set_json_diff_count`, `selected_test_ids_diff_count`, `artifact_field_check_diff_count`, `current_route_class_diff_count`, and `sealed_baseline_expectation_diff_count`.
* Do not modify sealed evidence content to make the rerun pass.

Validation:

* blocker reproduced or non-reproducible result recorded
* blocker artifact path / log reference / observed command recorded when a blocker is present
* clean rerun result after containment, if applicable
* `minimal_runner_write_sink_fix` report PASS before any shared runner code change is accepted
* sealed packet before/after hash unchanged
* validation predicate diff count `0` across the whole current-route class and existing sealed baseline expectations
* runner write-sink diff scope fields are present and zero for required-set, selected-test, artifact-field-check, current-route-class, and sealed-baseline-expectation diffs
* current-route test count unchanged or explained delta recorded
* containment fix failure yields `blocked_fresh_readpoint_validation_required`, not Branch A or Branch B success

---

### Change 3 - Phase 2 Current Source Identity Re-derivation / Freshness Seal

Purpose:

Re-derive successor `2105` current source identity from the current checkout and compare it with drift/reseal evidence claims.

Files:

* Read: `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
* Read: `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
* Read: `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
* Read: `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`
* Write: `phase2/current_source_identity_redrive_report.json`
* Write: `phase2/source_identity_parity_table.json`
* Write: `phase2/direct_compose_sandbox_verification_report.json`, if direct compose verification is used

Implementation Notes:

* Recompute count/hash for manifest, facts, decisions, and overlay support.
* Verify successor universe count `2105` and missing overlay count `0`, where applicable.
* Direct compose verification must write only to sandbox output sinks.
* If old evidence cannot be machine-compared, classify it explicitly as provenance-only and require separate current checkout proof.

Validation:

* source identity redrive PASS
* facts / decisions / overlay support hash parity PASS
* protected surface mutation count `0`
* sandbox compose verification PASS, if used

---

### Change 4 - Phase 3 Adoption Decision Matrix / Branch Selection

Purpose:

Select Branch A adopted-required-gate or Branch B non-current isolation with owner-visible evidence.

Files:

* Write: `phase3/adoption_decision_matrix_report.json`
* Write: `phase3/branch_selection_contract_report.json`
* Write: `phase3/branch_selection_record.json`
* Write: `phase3/sealed_candidate_boundary_supersession_report.json`, if Branch A needs additive supersession

Implementation Notes:

* Status enum:
  * `adopted_required_gate`
  * `candidate_required_gate`
  * `historical_only`
  * `diagnostic_only`
  * `non_current_contingency`
  * `rejected_stale`
* Branch A requires proof that live manifest, taxonomy, runner, field checks, tests, evidence freshness, and VCS tracking all point to the same readpoint.
* Branch A requires every newly adopted required input to record clean-checkout reproducibility basis or an explicit forward dependency before Branch A closeout.
* Branch B requires proof that non-adoption is intentional and cannot be read as a failed source restoration.
* Branch A and Branch B both require Phase 0 plan token parity PASS. Implementation-local branch labels, blocked states, tracking enum values, or mandatory guard names cannot drift from this plan.
* If existing sealed candidate boundaries conflict with Branch A, use additive supersession only.
* Owner branch selection is a governance decision after machine predicate proof. It cannot substitute for failed predicate proof.

Branch Selection Contract:

| Outcome | Required predicates | Forbidden if |
| --- | --- | --- |
| Branch A: `adopted_required_gate` | Direct drift adoption and evidence-freshness reseal drift-consumption are distinguished; sealed-reseal-record to live-manifest re-derivation PASS; taxonomy status supports required-gate adoption; live manifest consumes compact evidence with required field checks; runner consumes required tests fail-closed; negative fixtures fail as expected; current-route validation PASS with `closure_enforced=true`; VCS required artifacts are tracked or deterministically regenerable; every newly adopted required input has clean-checkout reproducibility basis or explicit forward dependency; taxonomy separation additive-compatibility PASS; live manifest single-writer PASS; taxonomy single-writer PASS or explicit non-writer rationale; co-readpoint token PASS; owner approves adoption. | Any predicate fails; sealed candidate boundary conflict lacks additive supersession; validation is blocked; evidence is raw-staging direct authority; owner approval is the only proof; new generated/untracked required input implies clean-checkout reproducibility without forward dependency. |
| Branch B-pure: non-current isolation without live manifest marker | Explicit owner decision chooses non-current / candidate / historical / diagnostic isolation; sealed-reseal-record to live-manifest re-derivation PASS; live manifest unchanged hash recorded; expected required-test/artifact count unchanged; current-route validation PASS with `closure_enforced=true`; taxonomy records non-current status if needed; docs claim boundary says canonical PASS does not imply live required-gate adoption; single-writer PASS; taxonomy single-writer PASS or explicit non-writer rationale; co-readpoint token PASS. | Used as fallback for failed Branch A proof; current-route validation is skipped/blocked; live manifest receives a marker; unchanged hash is not true. |
| Branch B-marked: non-current isolation with evidence-only marker | Same as Branch B-pure except an owner-approved additive evidence-only marker may be written to live manifest only when the live manifest schema explicitly supports `evidence_only_marker` or an equivalent non-required class; marker is not a required gate; manifest hash delta and marker role are recorded; runner enumeration, required count, artifact fail-closed set, and required-test count do not include the marker; current-route validation PASS with `closure_enforced=true`; docs state marker is evidence-only. | Claims unchanged manifest hash; marker becomes required validation; marker is used as current authority; current-route validation is skipped/blocked; manifest schema lacks an explicit non-required marker class. |
| `blocked_sealed_reseal_live_divergence_resolution_required` | Sealed reseal record or docs claim live manifest consumption that current checkout cannot re-derive from live manifest. | Must not be converted into Branch A or Branch B. |
| `blocked_branch_selection_predicate_unsatisfied` | Branch A and Branch B predicates are both unsatisfied after Phase 0~3. | Must not be overridden by owner seal. |
| `blocked_fresh_readpoint_validation_required` | Current-route validation cannot produce a fresh PASS with `closure_enforced=true`, including unresolved `OSError 22`. | Must not close Branch A or Branch B. |

Validation:

* decision matrix schema PASS
* Branch Selection Contract validator PASS
* Phase 0 plan token parity PASS
* owner decision recorded after machine predicate proof
* no standalone `PASS` / `complete` claim without branch status
* sealed candidate boundary conflict either absent or superseded additively
* Branch A forbidden if any Branch A predicate fails
* Branch A forbidden if any newly adopted required input lacks a clean-checkout basis or explicit forward dependency
* Branch B forbidden if fresh current-route validation PASS is absent

---

### Change 5A - Phase 4A Branch A Required-Gate Adoption, If Approved

Purpose:

Make current source authority drift verification explicitly consumed by current-route required validation.

Files:

* Possible write: `Iris/_docs/round3/current_route_required_validations.json`
* Possible write: `Iris/_docs/round3/round3_test_taxonomy.json`
* Write: `phase4a/live_manifest_mutation_report.json`
* Write: `phase4a/taxonomy_adoption_report.json`
* Write: `phase4a/taxonomy_separation_additive_compatibility_report.json`
* Write: `phase4a/required_artifact_field_schema.json`
* Write: `phase4a/required_artifact_field_check_report.json`
* Write: `phase4a/adopted_required_input_reproducibility_forward_dependency_report.json`
* Write: `phase4a/required_validation_count_delta_report.json`
* Write: `phase4a/current_route_required_gate_consumption_report.json`
* Write: `phase4a/negative_fixture_matrix_report.json`
* Write: `phase4a/single_writer_guarantee_report.json`
* Write: `phase4a/taxonomy_single_writer_report.json`

Implementation Notes:

* Additive live manifest mutation only.
* Required artifact entries must include path, role, expected fields, hash or regeneration basis, and consumed-by-manifest status.
* Every newly adopted required input must record `required_input_path`, `adoption_source`, `clean_checkout_reproducibility_basis`, `generated_reproducible_untracked`, `forward_dependency_artifact`, and `clean_checkout_reproducibility_claimed_by_this_plan`.
* `clean_checkout_reproducibility_basis` is limited to `tracked_required` or `reproducibility_preflight_forward_dependency`.
* If a newly adopted input is `generated_reproducible` and untracked, set `generated_reproducible_untracked=true`, `clean_checkout_reproducibility_claimed_by_this_plan=false`, `clean_checkout_reproducibility_proof_status=out_of_scope_not_claimed`, and `reproducibility_obligation_forwarded_to=current_route_required_evidence_reproducibility_taxonomy_disposition_preflight`.
* Branch A must not imply clean-checkout reproducibility for generated/untracked newly adopted inputs unless a separate reproducibility/taxonomy closeout proves it.
* `required_validation_count_delta_report.json` must record old/new required artifact counts, old/new required test counts, delta reason, and whether downstream expected-count updates are required.
* Required tests must fail closed on missing artifact, skipped test, failed field check, stale bundle, or candidate-manifest override.
* Do not count wrapper-only post-run checks as live current-route tests unless the live manifest explicitly requires them.
* Record the live manifest canonical writer for this adoption patch and prove the adoption-reseal tool is not a second writer over the same entry family.
* Record the taxonomy canonical writer for this round, or record that taxonomy is classification metadata outside the required-validation writer model and why this does not create dual-writer risk.
* Prove taxonomy adoption does not silently supersede the earlier evidence-freshness reseal taxonomy separation.

Required artifact field schema:

| Artifact | Required fields |
| --- | --- |
| final adoption reseal report | `status`, `selected_branch`, `machine_contract_status`, `current_route_validation_status`, `closure_enforced`, `protected_source_rendered_lua_runtime_package_changed_count`, `non_claims`, `independent_review_status`, `owner_seal_status` |
| primary review manifest | `status`, `artifact_count`, `missing_count`, `artifacts[].path`, `artifacts[].role`, `artifacts[].sha256` or explicit comparison exemption |
| source identity redrive report | `status`, `authority_role`, `successor_universe_count`, `manifest_sha256`, `facts_sha256`, `decisions_sha256`, `overlay_support_sha256`, `checks.facts_match_manifest`, `checks.decisions_match_manifest`, `checks.overlay_match_manifest` |
| manifest mutation report | `status`, `old_manifest_sha256`, `new_manifest_sha256`, `added_entries`, `modified_existing_entries`, `removed_existing_entries`, `duplicate_entries`, `writer_id`, `single_writer_status` |
| taxonomy adoption report | `status`, `old_taxonomy_sha256`, `new_taxonomy_sha256`, `added_rows`, `modified_existing_rows`, `taxonomy_separation_compatibility_status`, `selected_branch_status` |
| adopted required input reproducibility forward dependency report | `status`, `new_required_inputs[]`, `new_required_inputs[].required_input_path`, `new_required_inputs[].adoption_source`, `new_required_inputs[].clean_checkout_reproducibility_basis`, `new_required_inputs[].generated_reproducible_untracked`, `new_required_inputs[].forward_dependency_artifact`, `new_required_inputs[].clean_checkout_reproducibility_claimed_by_this_plan`, `reproducibility_obligation_forwarded_to` |
| required validation count delta report | `status`, `old_required_artifact_count`, `new_required_artifact_count`, `old_required_test_count`, `new_required_test_count`, `delta_reason`, `downstream_expected_count_update_required` |
| no-mutation report | `status`, `protected_source_changed_count`, `protected_rendered_changed_count`, `protected_lua_bridge_changed_count`, `protected_runtime_chunk_changed_count`, `protected_package_changed_count`, `sealed_evidence_changed_count` |

Validation:

* taxonomy schema validation PASS
* required manifest schema validation PASS
* required artifact field schema PASS
* adopted required input reproducibility forward dependency report PASS
* required validation count delta report PASS
* live manifest single-writer guarantee PASS
* taxonomy single-writer or explicit non-writer rationale PASS
* taxonomy separation additive-compatibility PASS
* focused adoption unittest PASS
* current-route runner with closure enforcement PASS
* missing artifact negative fixture FAIL as expected
* skipped test negative fixture FAIL as expected
* failed field-check negative fixture FAIL as expected
* protected surface no-mutation PASS
* single-writer guarantee PASS

---

### Change 5B - Phase 4B Branch B Non-Current Isolation, If Not Adopted

Purpose:

Seal the drift verification round as candidate / historical / diagnostic / non-current while preserving canonical docs provenance.

Files:

* Read: `Iris/_docs/round3/current_route_required_validations.json`
* Possible write: `Iris/_docs/round3/round3_test_taxonomy.json`
* Write: `phase4b/current_source_authority_drift_non_current_isolation_report.json`
* Write: `phase4b/candidate_or_historical_disposition_report.json`
* Write: `phase4b/branch_b_mode_report.json`
* Write: `phase4b/branch_b_field_schema_report.json`
* Write: `phase4b/live_manifest_unchanged_report.json`
* Write: `phase4b/live_manifest_marker_delta_report.json`, only for B-marked
* Write: `phase4b/current_route_validation_result.branch_b.json`

Implementation Notes:

* Branch B is not a failure-avoidance fallback. It requires an explicit non-current adoption/isolation decision.
* Branch B still requires fresh current-route validation PASS with `closure_enforced=true`.
* B-pure: live required manifest remains unchanged; unchanged hash and expected required-test/artifact count unchanged are recorded.
* B-marked: owner may approve an additive evidence-only marker only if live manifest schema explicitly supports `evidence_only_marker` or an equivalent non-required marker class. If schema support is absent, marker evidence must stay in ledger packet / claim boundary / taxonomy candidate status and the live manifest must follow B-pure behavior.
* B-marked marker must not enter runner enumeration, required count, artifact fail-closed set, or required-test count.
* Docs must say that canonical PASS does not imply live required-validation adoption.
* Future drift recovery remains a contingency requiring fresh drift evidence and a new scope.
* If fresh current-route validation is blocked or fails, Branch B closeout is blocked as `blocked_fresh_readpoint_validation_required`.

Branch B field schema:

| Artifact | Required fields |
| --- | --- |
| `branch_b_mode_report` | `status`, `selected_mode`, `reason`, `owner_decision_id`, `current_route_validation_status`, `closure_enforced`, `schema_supported_marker` |
| `live_manifest_unchanged_report` | `status`, `old_manifest_sha256`, `new_manifest_sha256`, `unchanged`, `required_test_count_unchanged`, `required_artifact_count_unchanged`, `runner_required_count_delta` |
| `live_manifest_marker_delta_report` | `status`, `old_manifest_sha256`, `new_manifest_sha256`, `marker_path`, `marker_role`, `required_gate`, `runner_required_count_delta`, `required_artifact_count_delta`, `artifact_fail_closed_set_delta`, `schema_support_status` |

Validation:

* docs claim scanner PASS
* overclaim scanner PASS
* Branch B field schema PASS
* Branch B mode report PASS
* current-route validation PASS with `closure_enforced=true`
* B-pure: live manifest unchanged hash PASS and expected count unchanged PASS
* B-marked: marker delta report PASS, `required_gate=false`, `runner_required_count_delta=0`, `artifact_fail_closed_set_delta=0`, schema support PASS, and no unchanged-hash claim
* candidate / non-current isolation report schema PASS
* marker is not consumed as a required gate, if B-marked

---

### Change 6 - Phase 5 Artifact Tracking / Reproducibility Reseal

Purpose:

Classify related untracked and generated artifacts by current-route reproducibility role.

Files:

* Possible write: `.gitignore`
* Write: `phase5/artifact_tracking_reproducibility_policy.md`
* Write: `phase5/required_artifact_tracking_matrix.json`
* Write: `phase5/tracking_reproducibility_enum_report.json`
* Write: `phase5/untracked_artifact_disposition_report.json`
* Write: `phase5/raw_staging_direct_authority_read_report.json`

Implementation Notes:

* Compact required evidence and validators should be tracked or have deterministic regeneration commands.
* Branch A newly adopted required inputs must either be `tracked_required` in this plan's evidence or explicitly forwarded to the broader reproducibility/taxonomy preflight.
* Bulk raw staging evidence should be ignored or kept generated unless explicitly required.
* Historical / diagnostic residue must not be consumed by current route.
* Tracking status is recorded separately from authority status.
* Fixed enum:
  * `tracked_required`
  * `generated_reproducible`
  * `raw_staging_ignored`
  * `historical_only`
  * `diagnostic_only`
  * `forbidden_current_consumption`
  * `missing_blocks_validation`
  * `not_applicable`
* `.gitignore` changes must include a guard proving they do not newly ignore already-tracked required artifacts or manifest-consumed compact evidence.

Validation:

* VCS tracking / reproducibility validator PASS
* tracking enum coverage PASS
* required artifact path exists or regenerate command is recorded
* Branch A newly adopted required input forward-dependency coverage PASS, if Branch A selected
* manifest-consumed artifact hash present
* raw staging direct authority read count `0`
* `.gitignore` required artifact visibility guard PASS, if `.gitignore` changes
* protected surface no-mutation PASS

---

### Change 7 - Phase 6 Fresh Current-Route Validation Reseal

Purpose:

Prove that runner, taxonomy, live manifest, evidence root, and external validation bundle share one fresh readpoint after Branch A or Branch B execution.

Files:

* Read: `Iris/_docs/round3/round3_run_contract_tests.py`
* Write: `phase6/current_route_validation_result.json`
* Write: `phase6/co_readpoint_identity_token.json`
* Write: `phase6/no_intervening_write_report.json`
* Write: `phase6/external_validation_bundle.json`
* Write: `phase6/external_validation_bundle_manifest.json`
* Write: `phase6/evidence_freshness_report.json`
* Write: `phase6/final_validation_wrapper_report.json`
* Write: `phase6/negative_fixture_matrix_report.json`

Implementation Notes:

* Run current-route validation with closure enforcement for the selected branch.
* Capture live manifest hash, taxonomy hash, runner hash, evidence root hash inventory, and external bundle hash.
* Stamp runner hash, taxonomy hash, live manifest hash, evidence root hash, external bundle hash, source identity hash, dirty-state summary, and validation command into one co-readpoint identity token.
* Verify no intervening write occurred between token capture and validation closeout for live manifest, taxonomy, runner, required evidence, and external bundle.
* Official wrapper must not expose a live manifest override.
* Lower-level override surfaces are allowed only for sandbox fail-closed fixtures.

Validation:

* Branch A current-route validation PASS with `closure_enforced=true`, if Branch A selected
* Branch B current-route validation PASS with `closure_enforced=true`, if Branch B selected
* co-readpoint identity token PASS
* no-intervening-write report PASS
* focused adoption/isolation validator PASS
* focused unittest PASS
* external validation bundle freshness PASS
* normalized bundle hash matches manifest PASS
* stale bundle negative fixture FAIL as expected
* candidate manifest override rejection PASS, if applicable
* protected surface no-mutation PASS

---

### Change 8 - Phase 7 Documentation / Ledger Reconciliation

Purpose:

Make docs canonical PASS wording, live runner consumption, manifest status, and branch status use the same claim boundary.

Files:

* Write: `docs/dvf_3_3_current_source_authority_drift_verification_adoption_reseal_claim_boundary.md`
* Write: `docs/dvf_3_3_current_source_authority_drift_verification_adoption_reseal_ledger_packet.md`
* Possible additive write: `docs/DECISIONS.md`
* Possible additive write: `docs/ARCHITECTURE.md`
* Possible additive write: `docs/ROADMAP.md`
* Write: `phase7/docs_reconciliation_report.json`
* Write: `phase7/forbidden_overclaim_scan_report.json`
* Write: `phase7/manifest_mutation_evidence.json`
* Write: `phase7/execution_contract_owner_review_report.json`

Implementation Notes:

* Use additive supersession, not sealed-body rewrite.
* Record Branch A or Branch B status, live manifest mutation or unchanged hash, taxonomy status, validation result, and non-decision scope.
* Record `clean_checkout_reproducibility_proof_status` and `original_required_evidence_reproducibility_preflight_status`.
* Re-state that Recovery live-write contingency is not automatically reopened.
* Cite the ROADMAP closed-readpoint reopen rule: closed readpoints must not be reopened without new authority, explicit successor / correction scope, or separately approved plan.
* If Branch A changes a prior candidate / non-current disposition, frame the change as an approved correction scope with additive supersession evidence, not as an implicit reopening of the sealed drift verification body.
* If Branch B is selected, state whether the isolation is B-pure or B-marked and where any non-required marker is recorded.
* Preserve the phrase `plan-structure PASS, not empirical verification of manifest / taxonomy / tracking / 2105 / OSError 22 state` or an exact semantic equivalent in the final report and claim boundary.
* If `docs/EXECUTION_CONTRACT.md` exists in the checkout, add a one-line compliance statement in docs reconciliation or independent review. If it cannot be evaluated, record it as `execution_contract_compliance_unverified_non_blocking`.
* If Branch A is selected, record an owner review entry deciding whether `docs/EXECUTION_CONTRACT.md` compliance should become blocking-unless-proven-N/A for the live-manifest mutation path in a later revision. This plan does not make that owner review a hard blocker by itself.

Validation:

* docs claim scanner PASS
* forbidden overclaim scanner PASS
* required status vocabulary scanner PASS
* closed-readpoint reopen rule citation present, if Branch A supersedes prior candidate/non-current disposition
* final report limitation phrase preserved
* original reproducibility/taxonomy preflight status is present and not overclaimed
* `EXECUTION_CONTRACT.md` compliance statement present or non-blocking limitation recorded
* Branch A execution-contract strictness owner review present, if Branch A selected
* no standalone `complete` / `PASS` lifecycle claim without axis PASS
* docs-to-evidence path existence PASS
* docs-to-consumption cross-check PASS

---

### Change 9 - Phase 8 Independent Review / Owner Seal

Purpose:

Close the adoption reseal only after independent review and owner seal.

Files:

* Write: `phase8/primary_review_artifact_manifest.json`
* Write: `phase8/independent_review_artifact_hash_report.json`
* Write: `phase8/owner_seal_report.json`
* Write: `phase8/final_current_source_authority_drift_verification_adoption_reseal_report.json`
* Write: `phase8/final_no_mutation_report.json`
* Write: `phase8/final_claim_boundary_report.json`

Implementation Notes:

* The independent review must be non-Claude because the roadmap input explicitly raises author independence.
* Owner seal does not substitute for independent review.
* The final report must name the exact branch state and must not claim release, runtime, package, manual QA, semantic quality, or public-facing readiness.
* The final report must include `clean_checkout_reproducibility_proof_status` and `original_required_evidence_reproducibility_preflight_status`.
* The final report must preserve that this plan's PASS is a plan-structure PASS, not empirical verification of manifest / taxonomy / tracking / `2105` / `OSError 22` state.
* The final report must list whether each implementation-compression guard artifact exists and passed: Branch Selection Contract validator, sealed-reseal/live-manifest re-derivation, Branch B fresh current-route PASS, B-marked schema-supported marker validation, taxonomy single-writer report, co-readpoint token, no-intervening-write report, and negative fixture matrix.

Validation:

* primary review artifact missing count `0`
* frozen hash mismatch `0`, except explicitly exempt artifacts
* independent review status PASS
* owner seal status PASS
* final report schema PASS
* final original-scope ceiling fields PASS
* implementation-compression guard artifact checklist PASS
* protected surface mutation `0`
* final claim boundary scanner PASS

---

## 7. Validation Plan

### Automated Validation

Required validation commands, subject to final tool implementation names:

* `uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py --mode all`
* `uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py --require-complete`
* `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py"`
* `uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure`

Automated checks:

* JSON schema validation for reports, manifest, taxonomy, and final seal
* Phase 0 plan token parity validation
* JSON-aware manifest/taxonomy structured matching validation
* Branch Selection Contract validator
* sealed-reseal-record to live-manifest re-derivation validator
* Branch B current-route PASS enforcement
* B-marked schema-supported marker validator, if B-marked is selected
* live manifest single-writer model validation
* taxonomy single-writer model or explicit non-writer rationale validation
* taxonomy separation additive-compatibility validation
* B-marked schema-supported non-required marker validation, if B-marked is selected
* Branch B field schema validation
* co-readpoint identity token validation
* source identity count/hash redrive
* required artifact field checks
* required test missing/skipped/failed checks
* Branch A adopted required input reproducibility forward-dependency validation, if Branch A is selected
* Branch A required validation count delta validation, if Branch A is selected
* negative fixture matrix
* VCS tracking / reproducibility classification
* raw staging direct authority read scan
* protected source / rendered / Lua bridge / runtime / package no-mutation scan
* docs claim / forbidden overclaim scanner
* shared runner predicate diff scan across current-route class and existing sealed baseline expectations, if `minimal_runner_write_sink_fix` is used
* runner write-sink diff scope validation for required set JSON, selected test IDs, artifact field checks, current-route class, and sealed baseline expectations, if `minimal_runner_write_sink_fix` is used
* `.gitignore` required artifact visibility guard, if `.gitignore` changes
* implementation-compression guard artifact checklist
* final review artifact hash comparison
* original reproducibility/taxonomy preflight overclaim guard

Mandatory guard artifacts:

* `phase3/branch_selection_contract_report.json`
* `phase0/sealed_reseal_record_live_manifest_rederivation_report.json`
* `phase0/plan_token_parity_report.json`
* `phase0/required_manifest_presence_structured_match_report.json`
* `phase0/taxonomy_presence_structured_match_report.json`
* `phase1/runner_write_sink_diff_scope_report.json`, if `minimal_runner_write_sink_fix` is used
* `phase4a/adopted_required_input_reproducibility_forward_dependency_report.json`, if Branch A is selected
* `phase4a/required_validation_count_delta_report.json`, if Branch A is selected
* `phase4b/current_route_validation_result.branch_b.json`, if Branch B is selected
* `phase4b/live_manifest_marker_delta_report.json` with schema-supported non-required marker fields, if B-marked is selected
* `phase4a/taxonomy_single_writer_report.json` or Branch B equivalent taxonomy single-writer / non-writer rationale
* `phase6/co_readpoint_identity_token.json`
* `phase6/no_intervening_write_report.json`
* `phase6/negative_fixture_matrix_report.json`

If any mandatory guard artifact is omitted or downgraded to advisory while its branch applies, the execution verdict must be `WARN` or `FAIL`; Branch A / Branch B closeout and final seal are forbidden.

### Manual Validation

Manual validation is review-focused:

* inspect branch selection and owner decision record
* inspect that owner decision happened after machine branch predicate proof
* inspect additive docs reconciliation for claim overreach
* inspect live manifest mutation or unchanged-hash evidence
* inspect B-pure / B-marked classification if Branch B is selected
* inspect whether B-marked marker was live-manifest schema-supported or recorded outside the live manifest
* inspect closed-readpoint reopen rule citation and approved correction scope framing if Branch A supersedes prior candidate/non-current disposition
* inspect that mandatory guard artifacts were not reduced to advisory evidence
* inspect that final report preserves the plan-structure PASS limitation
* inspect independent review report and owner seal report
* inspect dirty working tree diff before closeout to ensure unrelated changes were preserved

### Validation Limits

This plan will not validate:

* runtime equivalence
* live source mutation correctness
* rendered regeneration correctness
* Lua bridge export correctness
* runtime chunk replacement correctness
* package payload correctness
* release readiness
* Workshop readiness
* B42 readiness
* deployment readiness
* manual in-game QA
* semantic quality completion
* public-facing text acceptance
* live migration execution
* old Recovery live-write execution
* full external ecosystem compatibility sweep
* production validation

---

## 8. Risk Surface Touch

### Authority Surface

Touched, but governance-only.

The plan may change or confirm current-route required-validation governance authority through taxonomy, live manifest, field checks, and evidence freshness. It does not create source, rendered, Lua bridge, runtime, package, release, or public-facing authority.

### Runtime Behavior Surface

None.

Runtime Lua behavior, Browser / Wiki / Tooltip behavior, item rendering, bridge payload, chunks, and package output are not modified.

### Compatibility Surface

Minimal.

Branch A may increase or confirm required current-route validation gates, affecting local / CI validation expectations. Runtime compatibility and save / mod compatibility surfaces are unchanged.

### Sealed Artifact Surface

Touched by reference and hash comparison only.

Sealed reports are not rewritten. Any correction must be additive supersession with before/after hash evidence and explicit comparison-exempt entries where applicable.

### Public-Facing Output Surface

None.

No in-game text, UI, release note, Workshop page, package output, or public-facing description is changed by this plan.

---

## 9. Risk Analysis

### Architecture Risk

* Governance adoption could be misread as source writer authority.
* Branch A could bypass a sealed candidate boundary without additive supersession.
* Branch B could weaken required-validation expectations if written as a silent non-adoption without fresh current-route PASS.
* Sealed reseal record and live manifest divergence could be hidden inside A/B reconciliation instead of stopping fail-loud.
* Owner decision could be misused as branch predicate proof.
* Live manifest single-writer ownership could be bypassed by an adoption-reseal tool acting as a second writer.
* Taxonomy writes could become dual-writer if classification metadata ownership is not recorded.
* B-marked marker semantics could blur live manifest meaning if schema support is assumed rather than proven.
* Runner / wrapper responsibilities could blur if wrapper output reinterprets failed required tests.

### Runtime Risk

* Runtime risk is low because no runtime mutation is planned.
* The main runtime-adjacent risk is accidental writes to rendered, Lua bridge, runtime chunks, or package payload during validation.

### Compatibility Risk

* Branch A may increase required validation count and expose stale local evidence as a validation failure.
* Existing downstream scripts that assume the old required-test count may need updated expectations.
* Candidate manifest override paths must remain sandbox-only or they can create false current-route success.
* `minimal_runner_write_sink_fix` could alter shared runner behavior if predicate diff scope is too narrow.

### Regression Risk

* Docs canonical PASS and live manifest status may diverge again if docs are updated without evidence cross-checks.
* Untracked compact evidence may be required by live manifest but unavailable in a clean checkout.
* Raw staging evidence could be consumed directly if a validator uses broad glob reads instead of required artifact matrices.
* Windows path handling could make readpoint freshness fail for operational reasons unrelated to drift authority.
* Co-readpoint identity could degrade into independent hash capture without no-intervening-write proof.
* `.gitignore` changes could accidentally hide required compact evidence.

---

## 10. Rollback Plan

Rollback is governance-only.

Branch A rollback:

* Remove or downgrade the adoption entry in `Iris/_docs/round3/current_route_required_validations.json` to candidate / non-current status.
* Reclassify related taxonomy rows as candidate / historical / diagnostic / non-current.
* Move focused tests and artifact field checks out of the live required route.
* Record old/new manifest hashes and rollback reason in the adoption reseal evidence root.
* Preserve evidence root as historical rollback trace.
* Re-run protected no-mutation checks.

Branch B rollback:

* If live manifest was unchanged, runner rollback is not needed.
* If B-marked wrote an evidence-only marker, remove or downgrade only that marker and retain the marker delta evidence as rollback trace.
* If docs isolation wording is wrong, correct it additively.
* Preserve candidate / historical evidence and record why non-current isolation was withdrawn or revised.

Common containment:

* Do not rollback by deleting raw evidence, restoring old predecessor payloads, or reopening old Recovery live-write scope.
* Do not mutate source, rendered, Lua bridge, runtime chunks, or package payloads during rollback.
* If `OSError 22` containment was added, rollback only the write-sink / path-handling change after proving sealed evidence hashes remain unchanged.
* If `minimal_runner_write_sink_fix` changed predicate behavior or sealed baseline expectations, revert it and close as blocked rather than continuing adoption/isolation.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Iris remains within its role: evidence-based wiki information, not recommendation / comparison / runtime inference.
* Pulse / other modules must not be drawn into this Iris governance plan.
* Hub & Spoke boundaries remain unchanged.
* Runtime/build-time separation must remain intact.
* Current-route required-validation manifest entries are governance gates, not writers.
* Source -> facts -> decisions -> rendered -> Lua bridge -> runtime chunks boundary remains intact.
* Additive amendment is preferred over sealed-body rewrite.
* Sealed artifacts must be preserved unless a separate owner-approved regeneration scope exists.
* Existing dirty working tree changes must be preserved.
* Candidate, historical, diagnostic, and non-current artifacts must not be consumed as current authority.
* Missing / skipped / failed required tests and missing / stale / failed artifact fields must fail closed.
* Sealed-reseal-record to live-manifest divergence must fail loud as `blocked_sealed_reseal_live_divergence_resolution_required`.
* Branch A / Branch B selection must follow the Branch Selection Contract. Owner decision cannot replace predicate proof.
* Branch B requires fresh current-route validation PASS with `closure_enforced=true`.
* Branch B must be classified as B-pure or B-marked; B-marked cannot claim unchanged manifest hash.
* B-marked can write a live manifest marker only if the manifest schema explicitly supports `evidence_only_marker` or an equivalent non-required marker class. Otherwise the marker must live in ledger / claim boundary / taxonomy candidate status outside the live manifest.
* `OSError 22` containment is diagnosis-only unless `minimal_runner_write_sink_fix` passes.
* Shared runner predicate diff scope includes the whole current-route class and existing sealed baseline expectations.
* Live manifest single-writer model must be recorded before Branch A mutation or B-marked marker write.
* Taxonomy single-writer model or explicit non-writer rationale must be recorded before Branch A or Branch B taxonomy mutation.
* Co-readpoint identity token and no-intervening-write report are required before final seal.
* Branch A additive supersession must cite the closed-readpoint reopen rule and frame itself as an approved correction scope.
* Mandatory guard artifacts cannot be collapsed into advisory notes. Omitting Branch Selection Contract validator, sealed-reseal/live-manifest re-derivation, Branch B fresh current-route PASS, B-marked schema-supported marker validation, taxonomy single-writer report, co-readpoint token, no-intervening-write report, or negative fixture matrix requires `WARN` or `FAIL`.
* Final reports and claim boundaries must preserve the limitation that plan PASS is not empirical verification of manifest / taxonomy / tracking / `2105` / `OSError 22` state.
* `docs/EXECUTION_CONTRACT.md` compliance is recommended. If the contract exists and is evaluated, record one-line compliance; if it cannot be evaluated, record `execution_contract_compliance_unverified_non_blocking`.
* Branch decision is owner-reserved.
* Independent review must be non-Claude before canonical final seal.
* No release, package, Workshop, B42, deployment, manual QA, semantic quality, or public-facing text readiness claim is allowed.

---

## 12. Expected Closeout State

Expected closeout target:

* `current_source_authority_drift_adoption_reseal_complete_after_branch_decision_review_and_owner_seal`

This closeout is complete only if all of the following are true:

* Branch A or Branch B is explicitly selected.
* Branch Selection Contract validator passes for the selected branch.
* Phase 0 plan token parity report passes.
* Sealed-reseal-record to live-manifest re-derivation passes.
* JSON-aware manifest/taxonomy structured match reports pass, and substring-only matches are not used as predicate proof without an explicit reviewed exception.
* Docs canonical PASS wording and live runner / manifest consumption state do not conflict.
* Taxonomy status matches the selected branch.
* Taxonomy separation additive-compatibility passes.
* Live manifest single-writer model passes.
* Taxonomy single-writer model or explicit non-writer rationale passes.
* Live manifest mutation or unchanged hash is recorded.
* Branch B is classified as B-pure or B-marked, if Branch B is selected.
* B-marked live manifest marker is schema-supported as non-required, or marker evidence is recorded outside live manifest.
* Branch B field schema reports pass, if Branch B is selected.
* Branch A supersession cites closed-readpoint reopen rules and is framed as approved correction scope, if Branch A changes a prior candidate/non-current disposition.
* Current source identity is re-derived from the current checkout.
* Required artifact tracking / reproducibility is classified.
* Branch A newly adopted required inputs have clean-checkout basis or explicit reproducibility/taxonomy forward dependency, if Branch A is selected.
* Branch A required validation count delta report passes, if Branch A is selected.
* Raw staging direct authority read count is `0`.
* Current-route validation passes with `closure_enforced=true` for the selected branch.
* If Branch A is selected, Branch A current-route validation passes.
* If Branch B is selected, Branch B current-route validation passes.
* Branch B unchanged expectation is supporting evidence only, not a PASS substitute.
* Co-readpoint identity token and no-intervening-write report pass.
* If `minimal_runner_write_sink_fix` was used, shared runner predicate diff count is `0` across current-route class and existing sealed baseline expectations, with test count unchanged or explained.
* Mandatory guard artifact checklist passes for the selected branch.
* Focused validator and unittest pass.
* Negative fixtures fail as expected.
* Protected source / rendered / Lua bridge / runtime / package mutation count is `0`.
* Independent review artifact hash report passes.
* Owner seal report passes.
* Final report states the selected branch, claim boundary, non-decision scope, and no-mutation result.
* Final report preserves the plan-structure PASS limitation and includes execution-contract compliance or non-blocking limitation status.
* Final report includes `clean_checkout_reproducibility_proof_status` and `original_required_evidence_reproducibility_preflight_status`.

This adoption reseal closeout does not close the broader Current-Route Required Evidence Reproducibility / Taxonomy Disposition Preflight unless the final report explicitly records `clean_checkout_reproducibility_proof_status=separately_proven_by_this_execution` and `original_required_evidence_reproducibility_preflight_status=separately_closed_with_evidence`.

If owner does not select Branch A or Branch B, expected closeout is `blocked_owner_branch_decision_required`.

If sealed reseal record and live manifest consumption cannot be re-derived from the current checkout, expected closeout is `blocked_sealed_reseal_live_divergence_resolution_required`.

If fresh current-route validation is blocked by reproducible `OSError 22` or equivalent write-sink failure, expected closeout is `blocked_fresh_readpoint_validation_required`.

If Branch A and Branch B predicates are both unsatisfied, expected closeout is `blocked_branch_selection_predicate_unsatisfied`.

If Branch A adoption cannot satisfy sealed-boundary, field-check, tracking, or negative-fixture requirements, expected closeout must be Branch B isolation or a blocked state. It must not be forced into `adopted_required_gate`.

If implementation omits any mandatory guard artifact that applies to the selected branch, expected closeout is `warn_or_fail_implementation_guard_omitted`; it cannot close as Branch A, Branch B, final seal, or canonical seal.

Cycle-2 review gives this plan `PASS with minor revisions` after the minor revisions above are incorporated. This allows Phase 0~3 execution to proceed, but it still does not imply empirical validation of manifest / taxonomy / tracking / `2105` / `OSError 22` state. Branch A closeout, Branch B closeout, final seal, and canonical seal remain gated by the plan's validation evidence, non-Claude independent review, and owner seal.
