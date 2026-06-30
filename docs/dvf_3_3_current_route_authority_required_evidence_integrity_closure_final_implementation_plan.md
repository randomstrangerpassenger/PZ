# Implementation Plan

> Status: planned / roadmap-derived / codebase-inspected / final reconciliation plan / `plan_document_complete` target / governance-only / no source-rendered-lua-bridge-runtime-package mutation planned
> 작성일: 2026-06-30
> Roadmap input: `C:/Users/MW/.codex/attachments/785135f7-e856-46a8-a4cd-288a76914458/pasted-text.txt` / sha256 `42A965FE141BD94E04DE500711C31AC2B969F30A028ACE2C2B8A8A3F191E58DB` / lines `586`
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Predecessor parent plan: `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_plan.md` / sha256 `24A22F12A1730747F07D4D1DBF20BE784EB9CE1E9DE02794FDD48931E5936D75`
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

---

## 1. Objective

Create the final implementation plan for DVF 3-3 current-route authority / required-evidence integrity closure after consuming the sealed Required Artifact Surface Preflight Census and Required Artifact Disposition Seal results.

The concrete objective is not to execute the parent closure. It is to rewrite and reconcile the parent closure plan so that the already sealed preflight and disposition results are consumed as read-only input, required-manifest adoption rules are fixed, non-hash exception handling has a class ceiling, top-doc sync state is axis-qualified, and post-machine governance gates remain separate from machine success.

The target closeout for this planning artifact is:

```text
plan_document_complete
```

This token means only that the final implementation plan document is complete enough to be used as the next execution plan. It does not mean parent closure machine PASS, current authority cutover, runtime deployability, independent review completion, owner seal, canonical seal, package readiness, release readiness, Workshop readiness, B42 readiness, manual QA, semantic quality completion, or public-facing text acceptance.

Codebase inspection summary:

* Iris runtime remains Lua-facing under `Iris/media/lua/`, with build and generated surfaces under `Iris/build/`, `Iris/output/`, and `Iris/build/package/`.
* The current-route required-validation manifest exists at `Iris/_docs/round3/current_route_required_validations.json` and currently carries `required_artifacts=93` and `required_tests=48`.
* Preflight tooling exists under `Iris/build/description/v2/tools/build/*required_artifact_surface_preflight_census*` with a focused unittest.
* Disposition seal tooling exists under `Iris/build/description/v2/tools/build/*required_artifact_disposition_seal*` with a focused unittest.
* A final closure reconciliation tool surface for this new plan does not currently exist and must be added only during a future execution of this plan.

---

## 2. Scope

This plan covers final plan reconciliation only.

Included scope:

* sealed input readpoint and fingerprint binding
* preflight result consumption
* disposition seal result consumption
* denominator lifecycle-role binding for `93 / 48 / 56 / 153 / 2105 / 2084 / 21`
* required manifest adoption contract
* non-hash exception class ceiling
* top-doc sync state split
* final implementation plan rewrite
* primary review artifact manifest requirement
* residual blocker sweep
* machine-level plan-document completion validation
* post-machine independent review / owner seal / canonical seal separation

### Explicitly Out Of Scope

* parent closure machine PASS execution
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

The existing preflight report's `blocked / owner_pending` state is treated as predecessor evidence that triggered disposition, not as a live blocker after the Required Artifact Disposition Seal reports `terminal_state=ready`. The disposition seal still does not grant parent machine PASS; it only provides `parent_required_surface_disposition_ready_for_rerun`.

---

## 4. Assumptions

* `docs/Philosophy.md` is the top authority.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are current readpoints as of 2026-06-30.
* `docs/EXECUTION_CONTRACT.md` applies to future execution because this work touches authority and sealed-artifact governance surfaces.
* Iris remains a 100% Lua runtime module; this plan may add offline Python tooling in a future execution but must not create JVM+Lua runtime mixing.
* `Iris/_docs/round3/current_route_required_validations.json` is the live required-validation manifest and is currently read as `93` required artifacts and `48` required tests.
* The Required Artifact Disposition Seal final report is read-only input with `terminal_state=ready`, `required_artifact_disposition_problem_status=SOLVED`, `machine_pass_blocked=false`, `negative_exception_auto_disposition_count=93`, and `bare_diagnostic_count=0`.
* The disposition seal's independent review and owner/canonical seal evidence is scoped to the disposition seal round. It does not satisfy the parent closure independent review or canonical seal gate.
* A future parent closure execution must recompute Phase 0 / Phase 5 required-surface evidence and rerun current-route validation at a bound readpoint.
* Top-doc sync is draft-first. `top_doc_sync_state=owner_applied_and_validated` is allowed only if owner-applied top-doc changes are present, hash-bound, additive-only validated, and rerun-bound.
* `top_doc_sync_state=draft_prepared_owner_application_pending` is the preferred default for Codex-authored execution.
* `top_doc_sync_state=not_claimed` is valid only with an explicit omission rationale.
* `plan_document_complete` is a planning-artifact token, not parent execution completion.
* Existing dirty worktree changes outside this new plan file are user or previous-session changes and must not be reverted.

---

## 5. Repository Areas Affected

### Code

Expected future offline tooling surfaces:

* `Iris/build/description/v2/tools/build/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py`

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

Expected future docs:

* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation_claim_boundary.md`
* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation_ledger_packet.md`
* optional `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation_closeout.md`

### Config

Potential future additive-only target:

* `Iris/_docs/round3/current_route_required_validations.json`

No config mutation is performed by this planning artifact.

### Generated Artifacts

Expected future evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation/`

Read-only input evidence roots:

* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/`

---

## 6. Planned Changes

### Change 1 - Sealed Input Readpoint Binding

Purpose:

Bind the final plan to the live manifest, predecessor parent plan, preflight report, disposition final report, parent input packet, parent terminal mapping, and parent compatibility contract.

Files:

* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_implementation_plan.md`
* future `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation/phase1/sealed_result_intake_manifest.json`
* future `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation/phase1/closure_input_readpoint_report.json`

Implementation Notes:

* Record repo-relative paths and sha256 values for all consumed inputs.
* Treat ephemeral attachment paths as provenance only; execution evidence must bind repo files.
* Record the preflight predecessor as historical consumed input, then record the later disposition seal as the active required-surface resolution input.

Validation:

* sha256 recomputation for every consumed repo artifact
* stale attachment authority scan
* predecessor vs active input role check

---

### Change 2 - Preflight and Disposition Result Consumption

Purpose:

Convert preflight/disposition outputs from pending blockers into final plan inputs with explicit lifecycle roles.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p8_closeout_no_mutation/final_preflight_census_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase6_closeout_claim_boundary/final_required_artifact_disposition_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase6_closeout_claim_boundary/parent_closure_input_packet.json`
* future `phase2/preflight_result_consumption_report.json`
* future `phase2/disposition_result_consumption_report.json`

Implementation Notes:

* Preflight counts are consumed as historical problem and surface census evidence.
* Disposition final state is consumed as `parent_required_surface_disposition_ready_for_rerun`.
* `machine_pass_blocked=false` is disposition-scope evidence only.
* `canonical_seal_allowed=true` inside the disposition report is not parent canonical seal.

Validation:

* parent overclaim scan
* field parity check for `terminal_state`, `machine_pass_blocked`, `required_artifact_disposition_problem_status`, `bare_diagnostic_count`, and `negative_exception_auto_disposition_count`
* parent rerun-required check

---

### Change 3 - Denominator Lifecycle-Role Binding

Purpose:

Prevent `93 / 48 / 56 / 153 / 2105 / 2084 / 21` from being mixed as one completion denominator.

Files:

* `Iris/_docs/round3/current_route_required_validations.json`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* future `phase3/denominator_lifecycle_role_binding_report.json`

Implementation Notes:

* `93` is the live required artifact count for the current readpoint.
* `48` is the live required test count for the current readpoint.
* `56` belongs to earlier required-manifest readpoints and must not override the live count.
* `153`, `2105`, `2084`, and `21` remain predecessor or lifecycle-specific values unless a later approved plan rebinds them.

Validation:

* denominator scan across plan, claim boundary, ledger packet, and top-doc drafts
* forbidden denominator-role overclaim check

---

### Change 4 - Required Manifest Adoption Contract

Purpose:

Fix the candidate-to-live manifest adoption contract for any new final-plan validation requirements.

Files:

* `Iris/_docs/round3/current_route_required_validations.json`
* future `phase4/candidate_required_manifest_patch.json`
* future `phase4/required_manifest_adoption_report.json`
* future `phase4/current_route_after_manifest_adoption_result.json`

Implementation Notes:

* Candidate manifest patches are not live authority.
* Live adoption must be additive-only.
* Existing required artifact removal count must be `0`.
* Existing required test removal count must be `0`.
* Existing predicate meaning change count must be `0`.
* Do not require a self-referential final completion field directly in the live manifest.

Validation:

* candidate-vs-live diff report
* additive-only adoption check
* no-removal check
* no-predicate-meaning-change check
* self-reference recursion scan
* current-route rerun

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

Validation:

* unclassified non-hash exception count equals `0`
* substitute validation check
* primary review manifest coverage check

---

### Change 6 - Top-Doc Sync State Split

Purpose:

Separate top-doc draft preparation from owner-applied top-doc sync completion.

Files:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* future `phase6/top_doc_sync_plan.md`
* future `phase6/top_doc_sync_draft_patch.diff`
* future `phase6/top_doc_sync_state.json`
* future `phase6/top_doc_sync_validation_report.json`

Implementation Notes:

* Default Codex execution target is `top_doc_sync_state=draft_prepared_owner_application_pending`.
* `owner_applied_and_validated` requires owner-applied docs, hashes, additive-only diff validation, and rerun binding.
* `not_claimed` requires an explicit omission rationale.
* Top-doc draft state must not be written as top-doc sync PASS.

Validation:

* stale blocker phrase scan
* overclaim scan
* no runtime/package/release readiness claim scan
* draft hash binding or owner-applied hash binding, depending on selected state

---

### Change 7 - Final Implementation Plan Rewrite

Purpose:

Make the final implementation plan a single primary plan that consumes sealed inputs and no longer leaves preflight/disposition blockers unresolved in side documents.

Files:

* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_implementation_plan.md`
* future `phase7/final_implementation_plan_completeness_report.json`
* future `phase7/reconciliation_trace_report.json`
* future `phase7/closure_plan_claim_boundary.md`
* future `phase7/closure_plan_ledger_packet.md`

Implementation Notes:

* Replace unresolved sections with consumed-input sections.
* Keep independent review, owner seal, and canonical seal out of machine success.
* Keep final plan completion limited to `plan_document_complete`.
* Preserve predecessor plan as predecessor context, not concurrent execution authority.

Validation:

* plan completeness validator
* phase dependency graph check
* single primary plan authority check
* no-mutation scope check

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

Validation:

* missing primary review artifact count equals `0`
* hash-cycle scan
* role coverage check

---

### Change 9 - Residual Blocker Sweep and Single-Plan Consolidation

Purpose:

Ensure no side document still claims a live plan blocker after the final plan consumes the sealed inputs.

Files:

* future `phase9/residual_blocker_sweep_report.json`
* future `phase9/open_finding_carryover_report.json`
* future `phase9/single_plan_consolidation_note.md`

Implementation Notes:

* Scan claim boundary, ledger packet, parent plan, preflight plan, disposition plan, closeout, and top-doc drafts.
* Predecessor documents may preserve historical blocker states, but they must not claim current execution authority over the final plan.
* Any unresolved blocker that remains must be explicitly carried into the final plan expected closeout state.

Validation:

* residual blocker token scan
* open-finding carryover check
* concurrent execution authority count equals `0`

---

### Change 10 - Machine Plan Completion and Post-Machine Gate Separation

Purpose:

Validate `plan_document_complete` without collapsing it into parent closure PASS, independent review PASS, owner seal, or canonical seal.

Files:

* future `phase10/final_plan_document_complete_report.json`
* future `phase10/validation_report.require_complete.json`
* future `phase10/protected_no_mutation_report.json`
* future `phase10/current_route_final_rerun_result.json`
* future `phase10/post_machine_governance_gate_boundary.md`
* future `phase10/independent_review_input_packet.json`

Implementation Notes:

* `plan_document_complete=true` is allowed only for plan-document completion.
* Parent machine PASS still requires rerun-bound current-route and protected no-mutation checks.
* Parent independent review requires a non-roadmap-author, artifact-bound review record.
* Owner seal and canonical seal remain separate owner/governance states.

Validation:

* final plan validator
* focused unittest or focused validation
* current-route rerun
* protected no-mutation validation
* post-machine claim boundary scan

---

## 7. Validation Plan

### Automated Validation

Expected commands for future execution:

* `uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure`
* `uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_required_artifact_disposition_seal.py --mode all`
* `uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_required_artifact_disposition_seal.py --require-complete`
* `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_required_artifact_disposition_seal.py"`
* `uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py --mode all`
* `uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py --require-complete`
* `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_current_route_authority_required_evidence_integrity_closure_final_reconciliation.py"`

Conditional validation:

* `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` if any Lua surface is touched. This plan does not intend to touch Lua.
* package guard probe only if separately owner-approved. Package probe output is guard evidence, not package readiness.

### Manual Validation

* Review final plan, claim boundary, and ledger packet for overclaim.
* Confirm top-doc sync state uses one of the allowed tokens.
* Confirm predecessor blocker text is role-qualified as historical or consumed input.
* Confirm primary review manifest includes every machine-critical artifact.

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

### Runtime Behavior Surface

None intended.

No Iris runtime Lua, tooltip behavior, browser behavior, package payload, or game-facing output is changed by this plan.

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
* Stale blocker phrases may remain in side docs and conflict with `plan_document_complete`.

---

## 10. Rollback Plan

Rollback is documentation and governance-artifact rollback, not runtime rollback.

If validation fails or overclaim is found:

1. Do not promote the final plan as `plan_document_complete`.
2. Revert or supersede the final plan document with a corrected plan patch.
3. Discard candidate required-manifest patches before live adoption.
4. If live required-manifest adoption already occurred, revert only the additive adoption diff and preserve a failure report.
5. Remove or correct new final reconciliation tooling and focused tests if they produce false PASS or false FAIL behavior.
6. Preserve failed evidence as diagnostic trace only if it does not claim PASS.
7. Keep source / rendered / Lua bridge / runtime / package surfaces unchanged.
8. If protected no-mutation fails, close as `blocked / no-authority-mutation`.
9. If parent independent review, owner seal, or canonical seal is missing, do not weaken the final report; keep the corresponding gate pending or blocked.

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
* Required-validation manifest changes, if any, must be additive-only.
* Candidate manifest patches are not live authority.
* Required artifact/test removal count must be `0`.
* Existing predicate meaning change count must be `0`.
* Source facts / decisions / overlay support writer authority must not be bypassed.
* Rendered output, Lua bridge, runtime chunks, and package payloads must not be mutated.
* Required-validation manifest entries are governance gates, not writer authorities.
* Denominators must be lifecycle-role qualified.
* Non-hash exceptions require class ceilings and substitute validation.
* Top-doc sync state must be one of `draft_prepared_owner_application_pending`, `owner_applied_and_validated`, or `not_claimed`.
* Owner-applied top-doc sync completion must not be claimed without owner-applied hashes, additive-only validation, and rerun binding.
* Machine PASS, independent review PASS, owner seal, and canonical seal are separate states.
* Roadmap-authored or self-authored review cannot satisfy parent independent review.
* Release readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, semantic quality completion, public-facing text acceptance, package publication, and live migration remain non-claims.

---

## 12. Expected Closeout State

Expected closeout for this planning artifact:

* `plan_document_complete`

Expected closeout for a future execution of this plan:

* `machine_plan_document_complete / top_doc_sync_state=draft_prepared_owner_application_pending / parent_independent_review_gate=BLOCKED / parent_canonical_seal_pending` if machine validation passes and top-doc drafts are prepared but no owner-applied top-doc validation or parent independent review exists.
* `machine_plan_document_complete / top_doc_sync_state=owner_applied_and_validated / parent_independent_review_gate=BLOCKED / parent_canonical_seal_pending` if owner-applied top-doc changes are hash-bound, additive-only validated, and rerun-bound, but parent independent review is still missing.
* `machine_plan_document_complete / top_doc_sync_state=not_claimed / parent_independent_review_gate=BLOCKED / parent_canonical_seal_pending` only if execution records an explicit omission rationale for top-doc draft generation.
* `blocked / no-authority-mutation` if required artifact integrity, required manifest adoption, non-hash exception ceiling, residual blocker sweep, top-doc sync-state validation, current route, focused validator, or protected no-mutation checks fail.
* `parent_canonical_seal_allowed` only if parent machine evidence, artifact-bound independent review by a reviewer outside the roadmap authoring chain, owner seal, and final token sign-off are all present and bound to the same readpoint.

Bare `complete` is not a valid future execution closeout token for this round. `plan_document_complete` is valid only for the plan-document axis and must not be expanded into parent closure execution completion.
