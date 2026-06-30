# Implementation Plan

> Status: planned / roadmap-derived / codebase-inspected / compatible predecessor final-reconciliation plan for parent closure / WARN review required revisions incorporated / repo-surface preflight-disposition reconciliation required / `predecessor_plan_document_complete` target / governance-only / no source-rendered-lua-bridge-runtime-package mutation planned
> 작성일: 2026-06-30
> Roadmap input: `C:/Users/MW/.codex/attachments/785135f7-e856-46a8-a4cd-288a76914458/pasted-text.txt` / sha256 `42A965FE141BD94E04DE500711C31AC2B969F30A028ACE2C2B8A8A3F191E58DB` / lines `586`
> Feedback input: `C:/Users/MW/.codex/attachments/1b57f3be-e0d4-4c83-befd-042d4463c73d/pasted-text.txt` / sha256 `909FED6F551C4F53110517D65C9B4C6A4F3D05B0C148213BDC2516DB04296A6B` / lines `398` / verdict `WARN` / C1-C3 required revisions and N1-N8 hardening incorporated
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Parent/main plan: `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_plan.md` / sha256 `69C3994BFEC11297FD50640EF55F6D788D47C00E210148F1A0062BD9EF4451BE`
> Parent/main round identifier: `dvf_3_3_current_route_authority_required_evidence_integrity_closure`
> Parent/main evidence root: `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/`
> Parent compatibility role: predecessor final-reconciliation / plan-document completion lane. This plan may produce parent-intake evidence, but it does not replace the parent/main plan or claim the parent round's machine PASS.
> Live required-validation manifest: `Iris/_docs/round3/current_route_required_validations.json` / sha256 `7773F58CB6D7650539AB16DD887F8CCB0FF031AB7357B0AD851072B362578343`
> Historical preflight report: `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p8_closeout_no_mutation/final_preflight_census_report.json` / sha256 `5D8BA78C90EDEDF1C90E9141059702B2E0A59C76EF78B576228E9C53BA06F94E`
> Sealed disposition report: `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase6_closeout_claim_boundary/final_required_artifact_disposition_report.json` / sha256 `E2EBA5F3B72367341600103E6619418A57114D3432ADBEB9A67F942013CF1C81`
> Parent disposition input packet: `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase6_closeout_claim_boundary/parent_closure_input_packet.json` / sha256 `40975E5855F38E196E080B051879C4A22626AC19433E570081E4B2A01BB0996B`
> Working round identifier: `dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation`
> Primary evidence root target: `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation/`
> Phase granularity decision: 10-phase detailed structure.
> Validation depth decision: Heavy, because authority and sealed-artifact governance surfaces are touched.
> Top-doc sync decision: draft-first. Owner-applied top-doc validation is a separate state and is not claimed by this plan.
> Review boundary: roadmap-authored or self-authored review cannot satisfy the parent independent review gate.
> Tooling authority decision: final-reconciliation tooling is validator-only and cannot define a second current-route, required-evidence, required-set, or predicate authority.
> Provenance normalization decision: attachment paths are ephemeral provenance only; future execution must rebind roadmap / feedback provenance to repo-tracked artifacts or current top-doc readpoints, and sha256 comparisons are case-insensitive after lowercase normalization.

---

## 1. Objective

Create the compatible predecessor final-reconciliation plan for the parent DVF 3-3 current-route authority / required-evidence integrity closure plan after consuming the sealed Required Artifact Surface Preflight Census and Required Artifact Disposition Seal results.

The concrete objective is not to execute the parent closure and not to replace the parent/main plan. It is to prepare parent-compatible plan-document reconciliation evidence so that the parent/main plan can consume sealed preflight and disposition results as read-only input, with required-manifest adoption rules fixed, non-hash exception handling class-ceiled, top-doc sync state axis-qualified, and post-machine governance gates kept separate from machine success.

This predecessor plan must close the final-review problem that the preflight and disposition results were not yet reflected in the implementation plan. `predecessor_plan_document_complete` is not allowed until the actual repo-surface preflight report, the governing top-doc readpoint, the disposition final report, and the parent disposition input packet are all hash-bound, field-bound, role-classified, and reconciled in explicit consumption reports. The parent/main closure must not inherit a separate unresolved blocker document for these two predecessor rounds.

The target closeout for this planning artifact is:

```text
predecessor_plan_document_complete
```

This token means only that this predecessor plan-document lane is complete enough to be consumed by the parent/main plan. It does not mean parent closure machine PASS, current authority cutover, runtime deployability, independent review completion, owner seal, canonical seal, package readiness, release readiness, Workshop readiness, B42 readiness, manual QA, semantic quality completion, or public-facing text acceptance. The older `plan_document_complete` wording is retained only as a legacy/template axis alias inside prose or compatibility fields; execution closeout artifacts must use `predecessor_plan_document_complete` as the primary token.

Codebase inspection summary:

* Iris runtime remains Lua-facing under `Iris/media/lua/`, with build and generated surfaces under `Iris/build/`, `Iris/output/`, and `Iris/build/package/`.
* The current-route required-validation manifest exists at `Iris/_docs/round3/current_route_required_validations.json` and currently carries `required_artifacts=93` and `required_tests=48`.
* The current working surface has `required_dirty_overlap_count=0`; all `93` required artifact paths exist; all `48` required test module prefixes map to current test files.
* Preflight tooling exists under `Iris/build/description/v2/tools/build/*required_artifact_surface_preflight_census*` with a focused unittest.
* The bound preflight report currently records `status=PASS`, `semantic_verdict=blocked`, `artifact_disposition_state=owner_pending`, `unresolved_owner_queue_count=1`, `protected_surface_changed_count=0`, and `current_route_validation_state=PASS`.
* Disposition seal tooling exists under `Iris/build/description/v2/tools/build/*required_artifact_disposition_seal*` with a focused unittest.
* The bound disposition final report records `terminal_state=ready`, `status=PASS`, `required_artifact_disposition_problem_status=SOLVED`, `machine_pass_blocked=false`, `final_dirty_required_artifact_count=0`, `final_untracked_required_artifact_count=0`, `final_active_ignore_required_artifact_count=0`, `final_effectively_ignored_required_artifact_count=0`, `bare_diagnostic_count=0`, `negative_exception_auto_disposition_count=93`, and `current_route_validation_state=PASS`.
* A final closure reconciliation tool surface for this new plan does not currently exist. This plan owns creating it as a required implementation deliverable; `predecessor_plan_document_complete` is blocked until the dedicated runner, validator, common module, focused test, and evidence root exist and pass their required checks.

Review hardening incorporated by this revision:

* Live top-doc files are not Codex mutation targets in this round. They are read-only context or owner-apply targets only; Codex execution may generate draft patch artifacts under the evidence root.
* This round's current-route rerun is a plan-doc-scoped sanity rerun. It does not replace parent closure Phase 0 / Phase 5 / Phase 7 rerun-bound validation and cannot be cited as parent machine PASS evidence.
* This plan's final-reconciliation tooling is mandatory and validator-only. It may verify existing route/contract surfaces and generate additive evidence, but it must not define required sets, predicate meanings, current-route authority, or required-evidence authority.
* Missing dedicated final-reconciliation tooling is not a reason to create another predecessor plan. It is a blocker inside this plan until the tooling is implemented and validated.
* Required manifest adoption has an explicit state enum so future execution can distinguish no live manifest change, candidate-only preparation, live additive adoption, and blocked adoption.
* `volatile_environment_report` is allowed only as a narrowly justified non-hash exception class and must be justified row by row.
* Preflight/disposition result consumption is now a predecessor hard gate: a future execution must not silently downgrade the bound preflight `blocked / owner_pending` artifact state; it must reconcile that state against the governing top-doc readpoint and the later disposition seal before `predecessor_plan_document_complete`.
* Parent/main compatibility is explicit: this predecessor can emit parent-intake packets, but the parent/main plan still owns Phase 0 / Phase 5 / Phase 7 recomputation, current-route PASS, `machine_pass_governance_only`, independent review, owner seal, and canonical seal gates.

---

## 2. Scope

This plan covers final plan reconciliation only.

Included scope:

* parent/main plan compatibility mapping
* sealed input readpoint and fingerprint binding
* preflight result consumption
* disposition seal result consumption
* denominator lifecycle-role binding for `93 / 48 / 56 / 153 / 2105 / 2084 / 21`
* required manifest adoption contract
* non-hash exception class ceiling
* top-doc sync state split
* final implementation plan rewrite
* primary review artifact manifest requirement
* artifact schema floors and final validator hard-fail matrix
* dedicated final-reconciliation runner / validator / common module / focused test implementation
* roadmap / feedback provenance rebinding and sha256 case normalization
* residual blocker sweep
* machine-level plan-document completion validation
* post-machine independent review / owner seal / canonical seal separation
* parent-intake packet generation for the parent/main plan

### Explicitly Out Of Scope

* parent closure machine PASS execution
* parent/main plan replacement
* parent/main plan Phase 0 / Phase 5 / Phase 7 rerun-bound validation
* source facts / decisions / overlay support mutation
* rendered output regeneration
* Lua bridge export or mutation
* runtime chunk replacement
* package payload mutation
* live migration execution
* current authority cutover
* runtime behavior change
* package build or package readiness declaration
* release / Workshop / B42 / deployment readiness declaration
* manual in-game QA
* semantic quality completion
* public-facing text acceptance
* required artifact denominator redefinition
* terminal disposition re-adjudication
* sealed preflight / disposition result rewrite
* historical / diagnostic / fixture artifact deletion
* broad staging root unignore
* unrelated refactor
* Pulse / Iris architecture redesign

---

## 3. Non-Goals

This plan does not attempt to solve:

* full runtime equivalence
* full historical artifact byte reproducibility
* full clean-checkout required-evidence reproducibility
* public release copy or Workshop copy acceptance
* final owner sign-off
* independent review completion
* canonical seal completion
* source authority restoration
* any change to Iris user-facing wiki text
* any change to Iris tooltip, browser, or runtime Lua behavior
* any reinterpretation of predecessor `2105 / 2084 / 21` values as current runtime authority
* any replacement of parent rerun-bound validation with predecessor PASS evidence
* any replacement of parent rerun-bound validation with this round's plan-doc-scoped current-route sanity rerun
* any use of final-reconciliation tooling as a second current-route or required-evidence authority
* any claim that this predecessor plan's `predecessor_plan_document_complete` equals the parent/main plan's `machine_pass_governance_only`

The preflight/disposition surface is a required predecessor resolution item for this plan. The bound preflight artifact currently reasserts `semantic_verdict=blocked` and `artifact_disposition_state=owner_pending`, while the current governing top-doc readpoint records the preflight as ready input and the later Required Artifact Disposition Seal closes the required-surface disposition problem as `terminal_state=ready`. This split must be consumed as `preflight_artifact_ledger_split_resolved_by_disposition`, not silently ignored. The Required Artifact Disposition Seal still does not grant parent machine PASS; it only provides `parent_required_surface_disposition_ready_for_rerun`.

---

## 4. Assumptions

* `docs/Philosophy.md` is the top authority.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are current readpoints as of 2026-06-30.
* `docs/EXECUTION_CONTRACT.md` applies to future execution because this work touches authority and sealed-artifact governance surfaces.
* Iris remains a 100% Lua runtime module; this plan may add offline Python tooling in a future execution but must not create JVM+Lua runtime mixing.
* `Iris/_docs/round3/current_route_required_validations.json` is the live required-validation manifest and is currently read as `93` required artifacts and `48` required tests.
* The bound preflight final report is repo-surface evidence with `status=PASS`, `semantic_verdict=blocked`, `artifact_disposition_state=owner_pending`, `unresolved_owner_queue_count=1`, and `protected_surface_changed_count=0`; it must not be summarized as ready without an explicit artifact-ledger-disposition reconciliation row.
* The Required Artifact Disposition Seal final report is read-only input with `terminal_state=ready`, `required_artifact_disposition_problem_status=SOLVED`, `machine_pass_blocked=false`, `negative_exception_auto_disposition_count=93`, and `bare_diagnostic_count=0`.
* The Required Artifact Disposition Seal final report resolves the dirty/ignored required-surface disposition with `final_dirty_required_artifact_count=0`, `final_untracked_required_artifact_count=0`, `final_active_ignore_required_artifact_count=0`, and `final_effectively_ignored_required_artifact_count=0`.
* The disposition seal's independent review and owner/canonical seal evidence is scoped to the disposition seal round. It does not satisfy the parent closure independent review or canonical seal gate.
* The current predecessor completion route is valid only if future execution records `preflight_consumption_state=consumed_with_disposition_supersession` and `disposition_consumption_state=consumed_ready_for_parent_rerun`, or otherwise blocks `predecessor_plan_document_complete`.
* A future parent closure execution must recompute Phase 0 / Phase 5 required-surface evidence and rerun current-route validation at a bound readpoint.
* The parent/main plan remains the execution authority for `dvf_3_3_current_route_authority_required_evidence_integrity_closure`.
* This predecessor plan's evidence is advisory unless a parent-intake packet binds parent round id, parent evidence root, readpoint id, manifest hash, denominator hash, final plan hash, and terminal mapping.
* Top-doc sync is draft-first. `top_doc_sync_state=owner_applied_and_validated` is allowed only if owner-applied top-doc changes are present, hash-bound, additive-only validated, and rerun-bound.
* `top_doc_sync_state=draft_prepared_owner_application_pending` is the preferred default for Codex-authored execution.
* `top_doc_sync_state=not_claimed` is valid only with an explicit omission rationale.
* Live `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are read-only context unless the owner separately applies a draft. They are not direct mutation targets for this plan.
* The only Codex-authored top-doc output in this plan is a draft patch artifact under the evidence root.
* This round's current-route rerun is plan-doc-scoped sanity evidence and cannot be cited as parent Phase 0 / Phase 5 / Phase 7 rerun-bound validation.
* This plan execution's final-reconciliation tooling is mandatory, validator-only, and cannot define required sets, predicates, current-route authority, or required-evidence authority.
* Roadmap and feedback attachment paths in this plan are not execution authority. Future execution must rebind them to repo-tracked artifacts or to the current `docs/DECISIONS.md` / `docs/ROADMAP.md` readpoint before treating them as consumed evidence.
* sha256 values are compared case-insensitively after lowercase normalization. Reports may preserve display casing, but validation uses normalized lowercase hex.
* `predecessor_plan_document_complete` is the primary planning-artifact closeout token, not parent execution completion. `plan_document_complete` is only a legacy/template alias and must not be the primary token in execution closeout artifacts.
* Existing dirty worktree changes outside this new plan file are user or previous-session changes and must not be reverted.

---

## 5. Repository Areas Affected

### Code

Required implementation surfaces for this plan execution:

* `Iris/build/description/v2/tools/build/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py`

These files are mandatory deliverables of this plan execution, not optional follow-up work. If any one is missing, the only valid closeout is `blocked / dedicated-final-reconciliation-tooling-missing`.

Read-only inspected / consumed code surfaces:

* `Iris/_docs/round3/round3_run_contract_tests.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_required_artifact_surface_preflight_census.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_required_artifact_surface_preflight_census.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_required_artifact_disposition_seal.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_required_artifact_disposition_seal.py`

### Docs

Direct plan artifact:

* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_implementation_plan.md`

Read-only context docs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/EXECUTION_CONTRACT.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_plan.md`
* `docs/dvf_3_3_required_artifact_surface_preflight_census_plan.md`
* `docs/dvf_3_3_required_artifact_disposition_seal_plan.md`
* `docs/dvf_3_3_required_artifact_disposition_seal_closeout.md`

Owner-apply top-doc targets, not Codex mutation targets:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Expected future docs:

* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation_claim_boundary.md`
* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation_ledger_packet.md`
* optional `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation_closeout.md`
* optional parent-intake draft under the parent/main plan evidence root: `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/phase0/predecessor_final_reconciliation_intake_report.json`

### Config

Potential future additive-only target:

* `Iris/_docs/round3/current_route_required_validations.json`

No config mutation is performed by this planning artifact.

Any future change to `Iris/_docs/round3/current_route_required_validations.json` must be additive-only, validator-only in purpose, and must not redefine required sets or predicate meanings.

### Generated Artifacts

Required evidence root for this plan execution:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation/`

The runner must create this root and its phase subdirectories. A missing evidence root is a plan execution failure, not a reason to add another predecessor plan.

Optional parent-intake evidence target:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/phase0/predecessor_final_reconciliation_intake_report.json`

Read-only input evidence roots:

* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/`

---

## 6. Planned Changes

### Change 0 - Dedicated Final-Reconciliation Tooling Bootstrap

Purpose:

Implement the runner, validator, shared common module, focused unittest, and evidence-root bootstrap that make this plan executable rather than diagnostic-only.

Files:

* `Iris/build/description/v2/tools/build/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation/phase0/tooling_bootstrap_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation/phase0/tooling_contract_report.json`

Implementation Notes:

* This plan must create the dedicated tooling itself. It must not defer missing runner / validator / test coverage to a new predecessor plan.
* The runner owns additive evidence generation for this final-reconciliation plan only.
* The validator owns hard-fail validation for this final-reconciliation plan only.
* The shared common module may read repo artifacts, compute hashes, write evidence JSON under this plan's evidence root, and evaluate schema floors. It must not mutate source, rendered output, Lua bridge, runtime chunks, package payload, or live top-doc files.
* The focused unittest must cover at minimum: hash binding, preflight `blocked / owner_pending` preservation, disposition supersession, parent machine PASS non-claim, missing-tooling hard fail, and second-authority rejection.
* The runner must support `--mode all` and write a final summary containing `predecessor_plan_document_complete`, `parent_intake_ready`, `preflight_consumption_state`, `disposition_consumption_state`, `dedicated_tooling_state`, and `parent_machine_pass_claimed`.
* The validator must support `--require-complete` and fail nonzero unless every hard-fail matrix value is satisfied.
* Required schema floor for `tooling_bootstrap_report.json`: `schema_version`, `round_id`, `common_module_path`, `runner_path`, `validator_path`, `focused_test_path`, `evidence_root`, `common_module_exists`, `runner_exists`, `validator_exists`, `focused_test_exists`, `tooling_generation_delegated_to_separate_plan`, `status`.
* Required schema floor for `tooling_contract_report.json`: `schema_version`, `round_id`, `runner_mode_all_supported`, `validator_require_complete_supported`, `writes_only_final_reconciliation_evidence_root`, `source_rendered_lua_bridge_runtime_package_mutation_count`, `top_doc_live_mutation_target_count`, `required_set_definition_count`, `predicate_meaning_definition_count`, `current_route_authority_definition_count`, `required_evidence_authority_definition_count`, `second_authority_count`, `status`.

Validation:

* `common_module_exists == true`
* `dedicated_runner_exists == true`
* `dedicated_validator_exists == true`
* `dedicated_focused_test_exists == true`
* `tooling_generation_delegated_to_separate_plan == false`
* `runner_mode_all_supported == true`
* `validator_require_complete_supported == true`
* `writes_only_final_reconciliation_evidence_root == true`
* `source_rendered_lua_bridge_runtime_package_mutation_count == 0`
* `top_doc_live_mutation_target_count == 0`
* `required_set_definition_count == 0`
* `predicate_meaning_definition_count == 0`
* `current_route_authority_definition_count == 0`
* `required_evidence_authority_definition_count == 0`
* `second_authority_count == 0`

---

### Change 1 - Sealed Input Readpoint Binding

Purpose:

Bind this predecessor final-reconciliation plan to the live manifest, parent/main plan, preflight report, disposition final report, parent input packet, parent terminal mapping, and parent compatibility contract.

Files:

* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_implementation_plan.md`
* future `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation/phase1/sealed_result_intake_manifest.json`
* future `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation/phase1/closure_input_readpoint_report.json`
* future `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation/phase1/parent_main_plan_compatibility_report.json`

Implementation Notes:

* Record repo-relative paths and sha256 values for all consumed inputs.
* Treat ephemeral attachment paths as provenance only; execution evidence must bind repo files or current top-doc readpoints.
* Rebind roadmap and feedback provenance to repo-tracked artifacts or to `docs/DECISIONS.md` / `docs/ROADMAP.md` readpoints before final evidence consumption.
* Bind `parent_round_id=dvf_3_3_current_route_authority_required_evidence_integrity_closure` and `parent_evidence_root=Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/`.
* Record the current preflight artifact and the current top-doc readpoint separately. Because the bound preflight report reasserts `semantic_verdict=blocked` and `artifact_disposition_state=owner_pending`, future execution must not mark the preflight input as directly ready; it must record the split and close it through the later disposition seal or block this predecessor plan.
* Record the later disposition seal as the active required-surface resolution input.
* Required schema floor for `sealed_result_intake_manifest.json`: `schema_version`, `round_id`, `generated_at`, `inputs[]`, `path`, `sha256`, `sha256_normalized`, `role`, `consumption_state`, `authority_claim_allowed`, `repo_bound_rebinding_status`, `artifact_report_state`, `top_doc_readpoint_state`, `disposition_supersession_state`.
* Required schema floor for `closure_input_readpoint_report.json`: `schema_version`, `round_id`, `parent_round_id`, `parent_evidence_root`, `readpoint_id`, `live_manifest_sha256`, `parent_main_plan_sha256`, `preflight_report_sha256`, `preflight_artifact_semantic_verdict`, `preflight_artifact_disposition_state`, `preflight_top_doc_readpoint_state`, `disposition_report_sha256`, `disposition_terminal_state`, `disposition_problem_status`, `parent_input_packet_sha256`, `status`.
* Required schema floor for `parent_main_plan_compatibility_report.json`: `schema_version`, `round_id`, `parent_round_id`, `parent_plan_path`, `parent_plan_sha256`, `parent_evidence_root`, `predecessor_role`, `parent_phase0_consumable`, `parent_phase5_consumable`, `parent_phase7_consumable`, `parent_machine_pass_claimed`, `status`.

Validation:

* sha256 recomputation for every consumed repo artifact
* sha256 lowercase normalization check
* stale attachment authority scan
* roadmap / feedback repo-bound rebinding check
* predecessor vs active input role check
* parent/main round id compatibility check
* preflight artifact vs top-doc readpoint split check
* disposition supersession binding check
* missing required field count equals `0`

---

### Change 2 - Preflight and Disposition Result Consumption

Purpose:

Convert preflight/disposition outputs from unresolved predecessor blockers into final plan inputs with explicit lifecycle roles, using the actual repo-surface fields rather than narrative-only readiness.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p8_closeout_no_mutation/final_preflight_census_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase6_closeout_claim_boundary/final_required_artifact_disposition_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase6_closeout_claim_boundary/parent_closure_input_packet.json`
* future `phase2/preflight_result_consumption_report.json`
* future `phase2/disposition_result_consumption_report.json`

Implementation Notes:

* Preflight counts are consumed as historical problem and surface census evidence, with the current bound artifact state preserved as `status=PASS / semantic_verdict=blocked / artifact_disposition_state=owner_pending / unresolved_owner_queue_count=1`.
* Allowed `preflight_consumption_state` enum:
  * `consumed_ready_direct`
  * `consumed_with_disposition_supersession`
  * `blocked_unresolved_preflight`
* The expected state for the current repo surface is `consumed_with_disposition_supersession`.
* `consumed_ready_direct` is forbidden for the current bound preflight report unless a future rerun or superseding bound report has `semantic_verdict=ready`.
* The disposition final state is consumed as `parent_required_surface_disposition_ready_for_rerun`.
* Allowed `disposition_consumption_state` enum:
  * `consumed_ready_for_parent_rerun`
  * `blocked_disposition_not_ready`
* The expected state for the current repo surface is `consumed_ready_for_parent_rerun`.
* `machine_pass_blocked=false` is disposition-scope evidence only.
* `canonical_seal_allowed=true` inside the disposition report is not parent canonical seal.
* `final_dirty_required_artifact_count=0`, `final_untracked_required_artifact_count=0`, `final_active_ignore_required_artifact_count=0`, and `final_effectively_ignored_required_artifact_count=0` are consumed as dirty/ignored disposition closure, not as parent Phase 0 / Phase 5 recomputation.
* Disposition seal full rerun, if performed, is an input freshness regression guard. It remains predecessor-scope validation and does not become parent closure PASS evidence.
* If a future execution skips full disposition rerun, it must replace it with hash-bound input parity, required field parity, and `parent_rerun_required=true` validation against the parent input packet.
* `predecessor_plan_document_complete` is blocked unless both result consumption reports exist and record `unrepresented_preflight_disposition_result_count=0`.
* Required schema floor for `preflight_result_consumption_report.json`: `schema_version`, `round_id`, `preflight_report_path`, `preflight_report_sha256`, `artifact_status`, `artifact_semantic_verdict`, `artifact_disposition_state`, `artifact_unresolved_owner_queue_count`, `artifact_protected_surface_changed_count`, `top_doc_readpoint_state`, `artifact_ledger_split_state`, `preflight_consumption_state`, `silent_downgrade_count`, `consumption_role`, `parent_machine_pass_claimed`, `status`.
* Required schema floor for `disposition_result_consumption_report.json`: `schema_version`, `round_id`, `disposition_report_path`, `disposition_report_sha256`, `parent_input_packet_path`, `parent_input_packet_sha256`, `terminal_state`, `required_artifact_disposition_problem_status`, `machine_pass_blocked`, `final_dirty_required_artifact_count`, `final_untracked_required_artifact_count`, `final_active_ignore_required_artifact_count`, `final_effectively_ignored_required_artifact_count`, `bare_diagnostic_count`, `negative_exception_auto_disposition_count`, `parent_rerun_required`, `disposition_consumption_state`, `consumption_role`, `parent_machine_pass_claimed`, `status`.

Validation:

* parent overclaim scan with `parent_overclaim_count == 0`
* field parity check for preflight `semantic_verdict`, `artifact_disposition_state`, `unresolved_owner_queue_count`, and `protected_surface_changed_count`
* field parity check for disposition `terminal_state`, `machine_pass_blocked`, `required_artifact_disposition_problem_status`, `final_dirty_required_artifact_count`, `final_untracked_required_artifact_count`, `final_active_ignore_required_artifact_count`, `final_effectively_ignored_required_artifact_count`, `bare_diagnostic_count`, and `negative_exception_auto_disposition_count`
* `preflight_consumption_state == consumed_with_disposition_supersession` for the current bound repo surface
* `disposition_consumption_state == consumed_ready_for_parent_rerun`
* `preflight_blocked_token_silently_downgraded_count == 0`
* `preflight_blocked_token_resolved_by_disposition_count == artifact_unresolved_owner_queue_count`; for the current bound repo surface this evaluates to `1`.
* `unrepresented_preflight_disposition_result_count == 0`
* `pre_parent_blocker_document_count == 0`
* parent rerun-required check
* `disposition_seal_cited_as_parent_machine_pass_count == 0`

---

### Change 3 - Denominator Lifecycle-Role Binding

Purpose:

Prevent `93 / 48 / 56 / 153 / 2105 / 2084 / 21` from being mixed as one completion denominator.

Files:

* `Iris/_docs/round3/current_route_required_validations.json` as read-only live manifest input unless a later additive validator-only manifest patch is approved
* `docs/DECISIONS.md` as read-only context / owner-apply target
* `docs/ARCHITECTURE.md` as read-only context / owner-apply target
* `docs/ROADMAP.md` as read-only context / owner-apply target
* future `phase3/denominator_lifecycle_role_binding_report.json`

Implementation Notes:

* `93` is the live required artifact count for the current readpoint.
* `48` is the live required test count for the current readpoint.
* `56` belongs to earlier required-manifest readpoints and must not override the live count.
* `153`, `2105`, `2084`, and `21` remain predecessor or lifecycle-specific values unless a later approved plan rebinds them.
* Top-doc denominator references are draft-patch output only in this plan. Live top-doc edits are owner-applied or not claimed.

Validation:

* denominator scan across plan, claim boundary, ledger packet, and top-doc drafts
* forbidden denominator-role overclaim check
* `top_doc_live_mutation_target_count == 0`

---

### Change 4 - Required Manifest Adoption Contract

Purpose:

Fix the candidate-to-live manifest adoption contract for any new final-plan validation requirements.

Files:

* `Iris/_docs/round3/current_route_required_validations.json`
* future `phase4/candidate_required_manifest_patch.json`
* future `phase4/required_manifest_adoption_report.json`
* future `phase4/plan_doc_scoped_current_route_sanity_rerun_result.json`

Implementation Notes:

* Candidate manifest patches are not live authority.
* Required manifest adoption state enum:
  * `no_live_change_required`
  * `candidate_patch_prepared`
  * `live_additive_adopted`
  * `blocked_manifest_adoption`
* Live adoption must be additive-only.
* Existing required artifact removal count must be `0`.
* Existing required test removal count must be `0`.
* Existing predicate meaning change count must be `0`.
* Do not require a self-referential final completion field directly in the live manifest.
* Any added required validation must consume existing contract surfaces. It must not define a new current-route authority, required-evidence authority, required set, or predicate meaning.
* `blocked_manifest_adoption` blocks `predecessor_plan_document_complete` until a corrected candidate or no-live-change route is recorded.
* Required schema floor for `required_manifest_adoption_report.json`: `schema_version`, `round_id`, `required_manifest_adoption_state`, `candidate_manifest_sha256`, `live_manifest_before_sha256`, `live_manifest_after_sha256`, `added_required_artifact_count`, `added_required_test_count`, `removed_required_artifact_count`, `removed_required_test_count`, `predicate_meaning_change_count`, `self_reference_detected`, `second_authority_count`, `status`.

Validation:

* candidate-vs-live diff report
* additive-only adoption check
* no-removal check
* no-predicate-meaning-change check
* self-reference recursion scan
* required manifest adoption state enum check
* plan-doc-scoped current-route sanity rerun
* `second_authority_count == 0`

---

### Change 5 - Non-Hash Exception Class Ceiling

Purpose:

Make non-hash exceptions bounded, review-visible, and substitute-validated rather than arbitrary hash-bypass entries.

Files:

* future `phase5/non_hash_exception_class_ceiling_policy.md`
* future `phase5/non_hash_exception_inventory.json`
* future `phase5/non_hash_exception_validation_report.json`
* future `phase5/primary_review_hash_candidate_matrix.json`

Implementation Notes:

* Each non-hash exception must record path, reason, class, substitute validation, and reviewer visibility.
* Allowed classes are ceiling values, not examples.
* Unclassified non-hash artifacts are blockers.
* `comparison-exempt` is not `review-exempt`.
* Allowed non-hash exception class enum:
  * `hash_cycle_self_manifest` - artifact would have to contain its own final hash.
  * `owner_apply_target_placeholder` - live owner-apply target not mutated by this round; the draft patch artifact must be hash-bound instead.
  * `post_machine_gate_placeholder` - independent review, owner seal, or canonical seal artifact is intentionally post-machine and absent from machine completion.
  * `volatile_environment_report` - environment/timestamp-bearing report where substitute field validation is mandatory; if a concrete file exists, its raw file hash is still recorded outside the comparison-exempt field set.
* Adding a new class requires a superseding approved plan or hard fail.
* Every `volatile_environment_report` row must include a row-specific justification, allowed volatile fields, substitute validation, and raw file hash if a concrete file exists.
* Required schema floor for `non_hash_exception_validation_report.json`: `schema_version`, `round_id`, `allowed_classes[]`, `exceptions[]`, `path`, `class`, `reason`, `row_justification`, `substitute_validation`, `review_visibility`, `comparison_exempt`, `review_exempt`, `volatile_environment_report_count`, `volatile_environment_report_unjustified_count`, `unclassified_exception_count`, `status`.

Validation:

* unclassified non-hash exception count equals `0`
* enum violation count equals `0`
* review-exempt non-hash exception count equals `0`
* volatile environment report unjustified count equals `0`
* substitute validation check
* primary review manifest coverage check

---

### Change 6 - Top-Doc Sync State Split

Purpose:

Separate top-doc draft preparation from owner-applied top-doc sync completion.

Files:

* `docs/DECISIONS.md` as read-only context / owner-apply target
* `docs/ARCHITECTURE.md` as read-only context / owner-apply target
* `docs/ROADMAP.md` as read-only context / owner-apply target
* future `phase6/top_doc_sync_plan.md`
* future `phase6/top_doc_sync_draft_patch.diff`
* future `phase6/top_doc_sync_state.json`
* future `phase6/top_doc_sync_validation_report.json`

Implementation Notes:

* Default Codex execution target is `top_doc_sync_state=draft_prepared_owner_application_pending`.
* `owner_applied_and_validated` requires owner-applied docs, hashes, additive-only diff validation, and rerun binding.
* `not_claimed` requires an explicit omission rationale.
* Top-doc draft state must not be written as top-doc sync PASS.
* Top-doc target patch boundaries:
  * `docs/ROADMAP.md`: addendum or current summary patch only.
  * `docs/DECISIONS.md`: ledger addendum only.
  * `docs/ARCHITECTURE.md`: no authority rewrite; claim-boundary correction only.
* Required schema floor for `top_doc_sync_state.json`: `schema_version`, `round_id`, `top_doc_sync_state`, `draft_patch_path`, `draft_patch_sha256`, `owner_applied_doc_hashes`, `owner_applied_rerun_binding`, `owner_applied_branch_missing_hash_or_rerun_binding_count`, `omission_rationale`, `top_doc_live_mutation_target_count`, `top_doc_patch_boundary_violation_count`, `status`.

Validation:

* stale blocker phrase scan with `stale_blocker_phrase_count == 0`
* overclaim scan with `overclaim_count == 0`
* no runtime/package/release readiness claim scan
* draft hash binding or owner-applied hash binding, depending on selected state
* owner-applied branch missing hash or rerun binding count equals `0`
* `top_doc_live_mutation_target_count == 0`
* `top_doc_patch_boundary_violation_count == 0`

---

### Change 7 - Final Implementation Plan Rewrite

Purpose:

Make this predecessor final-reconciliation plan a single parent-compatible predecessor artifact that consumes sealed inputs and no longer leaves preflight/disposition blockers unresolved in side documents.

Files:

* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_implementation_plan.md`
* future `phase7/final_implementation_plan_completeness_report.json`
* future `phase7/reconciliation_trace_report.json`
* future `phase7/closure_plan_claim_boundary.md`
* future `phase7/closure_plan_ledger_packet.md`
* future `phase7/parent_intake_mapping_report.json`

Implementation Notes:

* Replace unresolved sections with consumed-input sections.
* Keep independent review, owner seal, and canonical seal out of machine success.
* Keep final plan completion limited to `predecessor_plan_document_complete`; `plan_document_complete` may appear only as a legacy/template alias and must not be the execution closeout token.
* Preserve the parent/main plan as the execution authority; this predecessor is context and parent-intake evidence only.
* Required schema floor for `final_implementation_plan_completeness_report.json`: `schema_version`, `round_id`, `parent_round_id`, `parent_plan_path`, `plan_path`, `plan_sha256`, `predecessor_plan_document_complete`, `plan_document_complete_legacy_alias`, `parent_intake_ready`, `dedicated_tooling_state`, `common_module_exists`, `dedicated_runner_exists`, `dedicated_validator_exists`, `dedicated_focused_test_exists`, `preflight_consumption_state`, `disposition_consumption_state`, `preflight_blocked_token_silently_downgraded_count`, `unrepresented_preflight_disposition_result_count`, `pre_parent_blocker_document_count`, `hard_fail_matrix_status`, `top_doc_sync_state`, `parent_overclaim_count`, `second_authority_count`, `this_round_rerun_cited_as_parent_rerun_count`, `status`.
* Required schema floor for `parent_intake_mapping_report.json`: `schema_version`, `round_id`, `parent_round_id`, `parent_phase0_input_role`, `parent_phase5_input_role`, `parent_phase7_input_role`, `preflight_consumption_state`, `disposition_consumption_state`, `parent_machine_pass_claimed`, `parent_recompute_required`, `status`.

Validation:

* plan completeness validator
* phase dependency graph check
* `single_predecessor_reconciliation_plan_check`
* no-mutation scope check
* dedicated tooling bootstrap gate
* preflight/disposition result consumption gate
* `dedicated_tooling_state == implemented_and_validated`
* `this_round_rerun_cited_as_parent_rerun_count == 0`
* `parent_machine_pass_claimed == false`

---

### Change 8 - Primary Review Artifact Manifest

Purpose:

Provide a complete artifact list for later independent review without creating hash cycles.

Files:

* future `phase8/primary_review_artifact_manifest.json`
* future `phase8/primary_review_artifact_hash_report.json`
* future `phase8/primary_review_bundle_shape_report.json`

Implementation Notes:

* Each artifact row must include repo-relative path, sha256 or non-hash class, role, phase, and review relevance.
* The manifest must include final plan, input consumption reports, manifest adoption report, top-doc sync report, non-hash exception ceiling report, protected no-mutation report, current-route rerun result, and completeness report.
* The manifest must not require its own final hash as a prerequisite field.
* Required role taxonomy:
  * `plan`
  * `input_consumption`
  * `manifest_adoption`
  * `top_doc_sync`
  * `non_hash_exception`
  * `no_mutation`
  * `current_route_rerun`
  * `complete_validation`
  * `claim_boundary`
  * `ledger_packet`
* Required schema floor for `primary_review_artifact_manifest.json`: `schema_version`, `round_id`, `artifacts[]`, `path`, `sha256`, `non_hash_exception_class`, `role`, `phase`, `review_relevance`, `role_coverage`, `missing_primary_review_artifact_count`, `role_coverage_missing_count`, `hash_cycle_detected`, `status`.

Validation:

* missing primary review artifact count equals `0`
* hash-cycle scan
* role coverage check
* role coverage missing count equals `0`

---

### Change 9 - Residual Blocker Sweep and Predecessor Reconciliation Consolidation

Purpose:

Ensure no side document still claims a live plan blocker after the final plan consumes the sealed inputs.

Files:

* future `phase9/residual_blocker_sweep_report.json`
* future `phase9/open_finding_carryover_report.json`
* future `phase9/single_predecessor_reconciliation_plan_note.md`

Implementation Notes:

* Scan claim boundary, ledger packet, parent plan, preflight plan, disposition plan, closeout, and top-doc drafts.
* Predecessor documents may preserve historical blocker states, but they must not claim parent/main execution authority or create a second predecessor final-reconciliation plan. The parent/main plan is explicitly exempt from predecessor-concurrency counts because it intentionally remains the closure execution authority.
* Any unresolved blocker that remains must be explicitly carried into the final plan expected closeout state.
* Required schema floor for `residual_blocker_sweep_report.json`: `schema_version`, `round_id`, `parent_round_id`, `residual_live_blocker_count`, `historical_blocker_count`, `parent_main_plan_exempt_from_predecessor_concurrency`, `concurrent_predecessor_reconciliation_plan_count`, `parent_overclaim_count`, `status`.
* Required schema floor for `single_predecessor_reconciliation_plan_note.md`: it must state that this predecessor is the only final-reconciliation predecessor for the parent/main plan, and that the parent/main closure plan is exempt because it remains the intended execution authority.

Validation:

* residual blocker token scan with `residual_live_blocker_count == 0`
* open-finding carryover check
* `concurrent_predecessor_reconciliation_plan_count == 0`, with the parent/main plan explicitly exempt
* `parent_main_plan_exempt_from_predecessor_concurrency == true`
* parent overclaim scan with `parent_overclaim_count == 0`

---

### Change 10 - Machine Plan Completion and Post-Machine Gate Separation

Purpose:

Validate `predecessor_plan_document_complete` without collapsing it into parent closure PASS, independent review PASS, owner seal, or canonical seal.

Files:

* future `phase10/final_predecessor_plan_document_complete_report.json`
* future `phase10/validation_report.require_complete.json`
* future `phase10/protected_no_mutation_report.json`
* future `phase10/plan_doc_scoped_current_route_sanity_rerun_result.json`
* future `phase10/post_machine_governance_gate_boundary.md`
* future `phase10/independent_review_input_packet.json`
* future `phase10/parent_intake_packet.json`

Implementation Notes:

* `predecessor_plan_document_complete=true` is allowed only for predecessor plan-document completion.
* `plan_document_complete` is a legacy/template alias only; if retained in compatibility fields, it must mirror `predecessor_plan_document_complete` and must not be used as the primary execution closeout token.
* `parent_intake_packet.json` is required when this predecessor claims `parent_intake_ready=true`; otherwise it is optional diagnostic output. It must not claim `machine_pass_governance_only`.
* The parent/main plan owns actual consumption of `parent_intake_packet.json`. The packet may provide Phase 0 / Phase 5 / Phase 7 input context, but it cannot substitute for parent recomputation, mutate parent plan behavior, or force parent acceptance.
* `plan_doc_scoped_current_route_sanity_rerun_result.json` is a plan-doc-scoped sanity rerun result only.
* This round's current-route rerun cannot substitute for parent closure Phase 0 repopulation, Phase 5 required-surface validation, or Phase 7 rerun-bound validation.
* This round's current-route rerun cannot be cited as parent machine PASS evidence.
* Parent machine PASS still requires rerun-bound current-route and protected no-mutation checks.
* Parent independent review requires a non-roadmap-author, artifact-bound review record.
* Owner seal and canonical seal remain separate owner/governance states.
* Required schema floor for `final_predecessor_plan_document_complete_report.json`: `schema_version`, `round_id`, `parent_round_id`, `predecessor_plan_document_complete`, `plan_document_complete_legacy_alias`, `parent_intake_ready`, `dedicated_tooling_state`, `common_module_exists`, `dedicated_runner_exists`, `dedicated_validator_exists`, `dedicated_focused_test_exists`, `focused_unittest_exit_code`, `validator_require_complete_exit_code`, `preflight_consumption_state`, `disposition_consumption_state`, `top_doc_sync_state`, `hard_fail_matrix`, `this_round_rerun_scope`, `this_round_rerun_cited_as_parent_rerun_count`, `final_reconciliation_tool_second_authority_count`, `parent_machine_pass_claimed`, `parent_independent_review_claimed`, `owner_seal_claimed`, `canonical_seal_claimed`, `status`.
* Required schema floor for `parent_intake_packet.json`: `schema_version`, `predecessor_round_id`, `parent_round_id`, `parent_plan_path`, `parent_evidence_root`, `predecessor_plan_sha256`, `terminal_state`, `parent_intake_ready`, `parent_consumption_authority`, `parent_recompute_substitution_allowed`, `preflight_consumption_state`, `disposition_consumption_state`, `parent_phase0_recompute_required`, `parent_phase5_recompute_required`, `parent_phase7_recompute_required`, `parent_machine_pass_claimed`, `status`.

Validation:

* final plan validator
* dedicated focused unittest
* plan-doc-scoped current-route sanity rerun
* protected no-mutation validation
* post-machine claim boundary scan
* `dedicated_tooling_state == implemented_and_validated`
* `focused_unittest_exit_code == 0`
* `validator_require_complete_exit_code == 0`
* `this_round_rerun_cited_as_parent_rerun_count == 0`
* `final_reconciliation_tool_second_authority_count == 0`
* `parent_machine_pass_claimed == false`

---

## 7. Validation Plan

### Automated Validation

Required commands for this plan execution:

* `uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure`
* `uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_required_artifact_disposition_seal.py --mode all`
* `uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_required_artifact_disposition_seal.py --require-complete`
* `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_required_artifact_disposition_seal.py"`
* `uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py --mode all`
* `uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py --require-complete`
* `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py"`

The three final-reconciliation commands above are not optional. If the runner, validator, or focused unittest file is missing, execution must first implement it within this plan and then rerun the same command list. It must not create a separate predecessor plan to cover missing tooling.

The current-route command in this plan is a plan-doc-scoped sanity rerun only. It does not replace parent closure Phase 0 / Phase 5 / Phase 7 rerun-bound validation and must be reported with `this_round_rerun_cited_as_parent_rerun_count == 0`.

Conditional validation:

* `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` if any Lua surface is touched. This plan does not intend to touch Lua.
* package guard probe only if separately owner-approved. Package probe output is guard evidence, not package readiness.

Final validator hard-fail matrix:

| Condition | Required value |
| --- | --- |
| `dedicated_tooling_state` | `implemented_and_validated` |
| `common_module_exists` | `true` |
| `dedicated_runner_exists` | `true` |
| `dedicated_validator_exists` | `true` |
| `dedicated_focused_test_exists` | `true` |
| `tooling_generation_delegated_to_separate_plan` | `false` |
| `runner_mode_all_supported` | `true` |
| `validator_require_complete_supported` | `true` |
| `focused_unittest_exit_code` | `0` |
| `validator_require_complete_exit_code` | `0` |
| `required_set_definition_count` | `0` |
| `predicate_meaning_definition_count` | `0` |
| `current_route_authority_definition_count` | `0` |
| `required_evidence_authority_definition_count` | `0` |
| `missing_primary_review_artifact_count` | `0` |
| `role_coverage_missing_count` | `0` |
| `preflight_consumption_state` | `consumed_with_disposition_supersession` for the current bound repo surface |
| `disposition_consumption_state` | `consumed_ready_for_parent_rerun` |
| `preflight_blocked_token_silently_downgraded_count` | `0` |
| `preflight_blocked_token_resolved_by_disposition_count` | `artifact_unresolved_owner_queue_count`; currently `1` |
| `unrepresented_preflight_disposition_result_count` | `0` |
| `pre_parent_blocker_document_count` | `0` |
| `concurrent_predecessor_reconciliation_plan_count` | `0`, parent/main plan exempt |
| `parent_main_plan_exempt_from_predecessor_concurrency` | `true` |
| `unclassified_non_hash_exception_count` | `0` |
| `non_hash_exception_enum_violation_count` | `0` |
| `review_exempt_non_hash_exception_count` | `0` |
| `required_manifest_adoption_state` | `no_live_change_required`, `candidate_patch_prepared`, or `live_additive_adopted` |
| `blocked_manifest_adoption_count` | `0` |
| `removed_required_artifact_count` | `0` |
| `removed_required_test_count` | `0` |
| `predicate_meaning_change_count` | `0` |
| `source_rendered_lua_bridge_runtime_package_mutation_count` | `0` |
| `stale_blocker_phrase_count` | `0` |
| `overclaim_count` | `0` |
| `parent_overclaim_count` | `0` |
| `this_round_rerun_cited_as_parent_rerun_count` | `0` |
| `final_reconciliation_tool_second_authority_count` | `0` |
| `parent_machine_pass_claimed` | `false` |
| `parent_consumption_authority` | `parent_main_plan_only` when `parent_intake_ready=true` |
| `parent_recompute_substitution_allowed` | `false` |
| `top_doc_live_mutation_target_count` | `0` |
| `top_doc_patch_boundary_violation_count` | `0` |
| `owner_applied_branch_missing_hash_or_rerun_binding_count` | `0` |
| `roadmap_feedback_repo_bound_rebinding_count` | expected input count |
| `sha256_case_normalization_error_count` | `0` |
| `volatile_environment_report_unjustified_count` | `0` |
| `self_reference_detected` | `false` |

Minimum required artifact set and decision table:

| Artifact / check | Required producer | PASS condition | BLOCK condition |
| --- | --- | --- | --- |
| common module | plan execution | `dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py` exists and exposes shared hash/schema/no-mutation helpers; required-set / predicate / current-route / required-evidence authority definition counts are all `0` | file missing or defines required-set / predicate / current-route / required-evidence authority |
| runner | plan execution | `run_*_final_reconciliation.py --mode all` exits `0` and writes phase evidence under this round root only | runner missing, nonzero exit, or writes outside allowed evidence root |
| validator | plan execution | `validate_*_final_reconciliation.py --require-complete` exits `0` only when every hard-fail matrix value is satisfied | validator missing, false PASS, or incomplete hard-fail coverage |
| focused unittest | plan execution | focused unittest exits `0` and covers tooling bootstrap, preflight split, disposition supersession, parent non-claim, and second-authority rejection | test missing, nonzero exit, or no assertion for the split/supersession path |
| `phase0/tooling_bootstrap_report.json` | dedicated runner | all dedicated tooling existence fields are `true` and delegation-to-separate-plan is `false` | any dedicated tooling file missing or delegation flag not `false` |
| `phase0/tooling_contract_report.json` | dedicated runner | runner/validator modes supported, write scope constrained, mutation counts `0`, second authority `0` | unsupported mode, out-of-scope write, protected mutation, or second authority |
| `phase1/closure_input_readpoint_report.json` | dedicated runner | live manifest, parent plan, preflight, disposition, and parent packet hashes match current repo files | stale hash, missing input, or unbound parent/main round id |
| `phase2/preflight_result_consumption_report.json` | dedicated runner | `preflight_consumption_state=consumed_with_disposition_supersession` and blocked token is represented verbatim | direct ready claim from current bound preflight, silent downgrade, or missing blocked token |
| `phase2/disposition_result_consumption_report.json` | dedicated runner | `disposition_consumption_state=consumed_ready_for_parent_rerun` with dirty/untracked/ignored counts `0` | disposition not ready, dirty/ignored closure omitted, or parent PASS claimed |
| `phase7/final_implementation_plan_completeness_report.json` | dedicated validator | `predecessor_plan_document_complete=true`, `parent_intake_ready=true`, dedicated tooling validated, parent PASS not claimed | missing phase evidence, missing tooling, unresolved preflight/disposition result, or parent overclaim |
| `phase10/final_predecessor_plan_document_complete_report.json` | dedicated validator | final hard-fail matrix passes, primary closeout token is `predecessor_plan_document_complete`, and post-machine gates remain non-claims | any hard-fail mismatch, primary `plan_document_complete` closeout, or independent-review/owner-seal treated as machine success |

### Manual Validation

* Review final plan, claim boundary, and ledger packet for overclaim.
* Confirm the bound preflight `blocked / owner_pending` artifact state is represented verbatim before any ready-input conclusion is made.
* Confirm the disposition seal's `ready / SOLVED / dirty=0 / ignored=0` result is represented as the superseding required-surface disposition input.
* Confirm top-doc sync state uses one of the allowed tokens.
* Confirm predecessor blocker text is role-qualified as historical or consumed input.
* Confirm primary review manifest includes every machine-critical artifact.
* Confirm final-reconciliation tooling is validator-only and does not define required sets, predicates, current-route authority, or required-evidence authority.
* Confirm roadmap and feedback provenance is rebound to repo-tracked artifacts or current top-doc readpoints before final execution evidence consumption.

### Validation Limits

This plan does not validate:

* runtime equivalence
* in-game behavior
* multiplayer behavior
* package deployment
* Workshop readiness
* B42 readiness
* release readiness
* public text acceptance
* semantic quality completion
* live migration execution
* source restoration
* rendered regeneration
* Lua bridge mutation
* runtime chunk replacement
* parent closure completion
* independent review completion
* owner seal completion
* canonical seal completion

No validation may be claimed as passed unless the exact relevant command exits with code `0`.

---

## 8. Risk Surface Touch

### Authority Surface

Touched in governance-document form only.

The plan affects final implementation plan authority, claim boundary wording, required manifest adoption rules, denominator lifecycle-role binding, top-doc sync-state vocabulary, and post-machine gate separation. It does not mutate Iris source authority, rendered authority, Lua bridge authority, runtime authority, or package authority.

Live top-doc files are not direct mutation targets. They are read-only context or owner-apply targets, with Codex output limited to draft patch artifacts unless a separate owner-applied execution exists.

### Runtime Behavior Surface

None intended.

No Iris runtime Lua, tooltip behavior, browser behavior, package payload, or game-facing output is changed by this plan.

This plan execution's final-reconciliation tooling is offline validator-only. It must not become runtime code and must not alter game-facing behavior.

### Compatibility Surface

Low.

Runtime compatibility is untouched. Future validation tooling may become stricter around governance evidence, but no external mod API or runtime compatibility contract is changed.

### Sealed Artifact Surface

Touched by consumption only.

Existing sealed preflight and disposition artifacts are read-only inputs. New final reconciliation artifacts are additive evidence. Existing sealed artifact bodies must not be rewritten.

### Public-Facing Output Surface

None intended.

Top-doc sync-state governance wording is not public release copy, Workshop copy, in-game text, or public-facing text acceptance.

---

## 9. Risk Analysis

### Architecture Risk

* Final reconciliation tooling could become a second current-route authority instead of a validator around existing route contracts.
* Required manifest adoption could add self-referential completion fields and create validation recursion.
* Denominator values could be mixed across lifecycle roles.
* Top-doc draft sync could be overread as owner-applied canonical sync.
* Final reconciliation tooling could define required sets or predicate meanings unless validator-only constraints and second-authority checks hard-fail.

### Runtime Risk

* Runtime risk is low because runtime surfaces are not targets.
* The main runtime-adjacent risk is accidental invocation of writer paths during evidence generation. Protected no-mutation checks must cover source, rendered, Lua bridge, runtime chunk, and package payload surfaces.

### Compatibility Risk

* Runtime compatibility risk is low.
* Tooling compatibility risk is medium because stricter validation may fail older evidence packets that were previously tolerated.

### Regression Risk

* The final plan may overclaim parent closure execution instead of plan-document completion.
* The disposition seal's scoped independent review / owner seal may be mistaken for parent independent review / owner seal.
* Non-hash exceptions may become unbounded if class ceilings are written as examples rather than allowed classes.
* Primary review manifest may omit machine-critical artifacts.
* The bound preflight artifact's `blocked / owner_pending` state may be hidden behind the later ready readpoint instead of being explicitly reconciled.
* The disposition seal's dirty/ignored closure could be cited as parent Phase 0 / Phase 5 recomputation rather than as predecessor input readiness.
* Stale blocker phrases may remain in side docs and conflict with `predecessor_plan_document_complete`.
* A plan-doc-scoped current-route sanity rerun may be cited as parent rerun-bound validation unless the firewall check stays at `0`.

---

## 10. Rollback Plan

Rollback is documentation and governance-artifact rollback, not runtime rollback.

If validation fails or overclaim is found:

1. Do not promote the final plan as `predecessor_plan_document_complete`.
2. Revert or supersede the final plan document with a corrected plan patch.
3. Discard candidate required-manifest patches before live adoption.
4. If live required-manifest adoption already occurred, revert only the additive adoption diff and preserve a failure report.
5. Remove or correct new final reconciliation tooling and focused tests if they produce false PASS or false FAIL behavior.
6. Preserve failed evidence as diagnostic trace only if it does not claim PASS.
7. Keep source / rendered / Lua bridge / runtime / package surfaces unchanged.
8. If protected no-mutation fails, close as `blocked / no-authority-mutation`.
9. If parent independent review, owner seal, or canonical seal is missing, do not weaken the final report; keep the corresponding gate pending or blocked.
10. After stable PASS convergence, freeze the plan text. Later revisions must be additive replacement items or a superseding plan, not silent in-place drift.

Sealed predecessor preflight and disposition results are not rollback targets for this plan.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance.
* Hub & Spoke boundary preservation.
* Iris remains runtime Lua-only.
* Runtime/build-time separation.
* Additive amendment preference.
* Minimal diff preservation.
* Existing dirty worktree changes outside this plan must be preserved.
* Existing sealed preflight / disposition artifacts are read-only inputs.
* Dedicated final-reconciliation runner, validator, common module, focused test, and evidence root are required outputs of this plan execution.
* Missing dedicated tooling must be fixed inside this plan execution or closed as `blocked / dedicated-final-reconciliation-tooling-missing`; it must not be outsourced to another predecessor plan.
* The bound preflight artifact result and bound disposition result must both be represented before `predecessor_plan_document_complete`.
* The current bound preflight `blocked / owner_pending` state must not be silently downgraded; it may only close through explicit `consumed_with_disposition_supersession` evidence or a future rerun/superseding report that is hash-bound.
* The bound disposition `ready / SOLVED / dirty=0 / ignored=0` state must be consumed as predecessor input readiness, not parent closure PASS.
* No separate preflight/disposition blocker document may remain unresolved before this predecessor claims `parent_intake_ready`.
* Live top-doc files are read-only context or owner-apply targets, not Codex mutation targets.
* Codex-authored top-doc output is draft patch artifact only unless a separate owner-applied execution exists.
* Required-validation manifest changes, if any, must be additive-only.
* Required manifest adoption state must be one of `no_live_change_required`, `candidate_patch_prepared`, `live_additive_adopted`, or `blocked_manifest_adoption`.
* `blocked_manifest_adoption` prevents `predecessor_plan_document_complete`.
* Candidate manifest patches are not live authority.
* Required artifact/test removal count must be `0`.
* Existing predicate meaning change count must be `0`.
* Final-reconciliation tooling is validator-only.
* Final-reconciliation tooling must not define a second current-route authority, required-evidence authority, required set, or predicate meaning.
* `final_reconciliation_tool_second_authority_count` must be `0`.
* Source facts / decisions / overlay support writer authority must not be bypassed.
* Rendered output, Lua bridge, runtime chunks, and package payloads must not be mutated.
* Required-validation manifest entries are governance gates, not writer authorities.
* Denominators must be lifecycle-role qualified.
* Non-hash exceptions require class ceilings and substitute validation.
* `volatile_environment_report` exceptions must be justified row by row; `volatile_environment_report_unjustified_count` must be `0`.
* Top-doc sync state must be one of `draft_prepared_owner_application_pending`, `owner_applied_and_validated`, or `not_claimed`.
* Owner-applied top-doc sync completion must not be claimed without owner-applied hashes, additive-only validation, and rerun binding.
* Roadmap and feedback attachment paths are ephemeral provenance only and must be rebound to repo-tracked artifacts or current top-doc readpoints before final evidence consumption.
* sha256 comparisons normalize hex casing before comparison.
* This round's current-route rerun is plan-doc-scoped sanity evidence only.
* This round's current-route rerun must not be cited as parent Phase 0 / Phase 5 / Phase 7 rerun-bound validation.
* `this_round_rerun_cited_as_parent_rerun_count` must be `0`.
* Scan validations use explicit `count == 0` pass criteria for stale blockers, overclaims, parent overclaims, second authority, and protected-surface mutation.
* Stable PASS convergence freezes plan text. Later changes require an additive replacement item or superseding plan.
* Machine PASS, independent review PASS, owner seal, and canonical seal are separate states.
* Roadmap-authored or self-authored review cannot satisfy parent independent review.
* Release readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, semantic quality completion, public-facing text acceptance, package publication, and live migration remain non-claims.

---

## 12. Expected Closeout State

Expected closeout for this planning artifact:

* `predecessor_plan_document_complete`

Expected closeout for a future execution of this plan:

* `predecessor_plan_document_complete / parent_intake_ready / top_doc_sync_state=draft_prepared_owner_application_pending / parent_independent_review_gate=not_satisfied_by_predecessor / parent_canonical_seal_not_satisfied_by_predecessor` if predecessor validation passes and top-doc drafts are prepared but no owner-applied top-doc validation exists.
* `predecessor_plan_document_complete / parent_intake_ready / top_doc_sync_state=owner_applied_and_validated / parent_independent_review_gate=not_satisfied_by_predecessor / parent_canonical_seal_not_satisfied_by_predecessor` if owner-applied top-doc changes are hash-bound, additive-only validated, and rerun-bound, but the parent/main plan still has not performed its own independent review and seal gates.
* `predecessor_plan_document_complete / parent_intake_ready / top_doc_sync_state=not_claimed / parent_independent_review_gate=not_satisfied_by_predecessor / parent_canonical_seal_not_satisfied_by_predecessor` only if execution records an explicit omission rationale for top-doc draft generation.
* `blocked / dedicated-final-reconciliation-tooling-missing` if the dedicated common module, runner, validator, focused test, or evidence root is missing, if focused unittest fails, if `--require-complete` validation fails, or if tooling creation is delegated to another plan.
* `blocked / unresolved-preflight-disposition-consumption` if the bound preflight artifact state, top-doc preflight readpoint, bound disposition final state, and parent input packet are not all represented in consumption reports, if the current preflight `blocked / owner_pending` token is silently downgraded, if the disposition `ready / SOLVED / dirty=0 / ignored=0` result is missing, or if a separate preflight/disposition blocker document remains before parent intake.
* `blocked / no-authority-mutation` if required artifact integrity, required manifest adoption, non-hash exception ceiling, volatile exception justification, residual blocker sweep, top-doc sync-state validation, provenance rebinding, plan-doc-scoped current-route sanity rerun, focused validator, second-authority check, parent-rerun firewall check, or protected no-mutation checks fail.
* `parent_intake_blocked / no-authority-mutation` if the predecessor cannot bind the parent/main round id, parent evidence root, readpoint, manifest hash, denominator hash, or terminal mapping.

Bare `complete` is not a valid future execution closeout token for this round. `predecessor_plan_document_complete` is the primary valid closeout token for this predecessor plan-document axis and must not be expanded into parent closure execution completion. `plan_document_complete` is retained only as a legacy/template alias and, if emitted in compatibility fields, must mirror `predecessor_plan_document_complete`. Parent `machine_pass_governance_only`, parent independent review, parent owner seal, and parent canonical seal remain owned by `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_plan.md`. After a stable PASS for the plan-document axis, the plan text is frozen; further changes require an additive replacement item or superseding plan.
