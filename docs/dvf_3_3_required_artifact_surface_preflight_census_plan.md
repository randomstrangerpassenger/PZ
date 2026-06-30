# Implementation Plan

> Status: planned / roadmap-derived / codebase-inspected / WARN feedback incorporated / Cycle 2 PASS advisory revisions incorporated / DVF 3-3 required artifact surface preflight-resolution / governance-only / committed-surface fast path added / census + conditional disposition + rerun required / scope revised by owner intent
> 작성일: 2026-06-29
> Roadmap input: `C:/Users/MW/.codex/attachments/1f416f24-8b87-4275-a4b4-7d0376635999/pasted-text.txt` / sha256 `207B472B1D944C2DD92727E5D81C527574A46284716C7289018D34891ED5BA64` / lines `623`
> Review input: `C:/Users/MW/.codex/attachments/163aeb76-6849-4f42-9782-34af301b332b/pasted-text.txt` / sha256 `A43F17FA964472C05FE8FB524BEAC89A8636B048C9D2AEDE81370EF5209D1C01` / lines `433` / verdict `WARN` / required revisions incorporated
> Review input: `C:/Users/MW/.codex/attachments/64d9e686-d29a-414c-b2f9-21872ca2c5c8/pasted-text.txt` / sha256 `76F1188D151313FD5B95394C693C763CBCD19695A8AC08D6B13D64C6D25C4EB2` / lines `247` / verdict `PASS` / advisory revisions incorporated
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Direct plan artifact: `docs/dvf_3_3_required_artifact_surface_preflight_census_plan.md`
> Artifact naming note: existing `preflight_census` filename is retained for continuity; current scope is required-surface preflight resolution, not census-only.
> Parent closure plan artifact: `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_plan.md`
> Working round identifier: `dvf_3_3_required_artifact_surface_preflight_census`
> Parent working round identifier: `dvf_3_3_current_route_authority_required_evidence_integrity_closure`
> Primary evidence root target: `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/`
> Parent evidence root target: `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/`
> Parent compatibility role: predecessor required-surface preflight resolution input for parent Change 1 / `parent_closure_preflight_phase0` baseline census and parent Change 6 / `parent_closure_phase5_vcs_surface` reconciliation.
> Live manifest inspected: `Iris/_docs/round3/current_route_required_validations.json` / sha256 `7773F58CB6D7650539AB16DD887F8CCB0FF031AB7357B0AD851072B362578343`
> Live manifest current read: schema `round3-current-route-required-validations-v1`, route `current`, status `PASS`, `required_artifacts=93`, `required_tests=48`
> Post-commit readiness observation: after owner commit/push at `288d5b61`, required artifacts measured `missing=0`, `dirty=0`, `tracked=93`, `untracked=0`, `ignored=0`; required test modules measured `missing=0`, `tracked=17`, `untracked=0`, `ignored=0`.
> Current-route timing observation: `python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure` completed `PASS / 127 tests / closure_enforced=true` in `253.254s`; validation timeout budgets must be at least `360s`.
> Validation depth decision for this plan: `standard census + disposition + rerun validation + mandatory synthetic fail-closed predicate matrix`. Heavy live Git fixtures remain isolated because source/rendered/runtime/package mutation is still out of scope.
> Ignored-artifact verdict rule for this plan: strict fail-closed before disposition. `effectively_ignored_required_artifact_count > 0` blocks immediate parent closure entry, then must be resolved through this plan's disposition lane or explicitly carried as unresolved.
> Canonical verdict token: author-reserved. Final reports must record semantic verdict and `canonical_verdict_token=author_reserved/not_claimed` together; this plan does not pre-seal a canonical blocker token.
> Plan-level review state: `REVISION_REQUIRED_AFTER_SCOPE_EXPANSION`. Prior PASS applied to census-only scope and does not satisfy this resolution-expanded plan.
> Independent review gate: `BLOCKED` until a non-Claude / non-roadmap-author artifact-bound review exists. Plan-level revision does not satisfy independent review, owner seal, or canonical seal.

---

## 1. Objective

Create an execution plan for a DVF 3-3 required artifact surface preflight resolution round.

The concrete objective is to resolve the required artifact surface preflight blocker for every live required artifact listed by `Iris/_docs/round3/current_route_required_validations.json`. Resolution means census first, then disposition dirty / ignored / untracked / missing / hash-ineligible surface, apply only approved governance-surface remediation, rerun the preflight, and emit a parent-closure entry state that is based on the post-disposition readpoint.

This plan is a predecessor to `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_plan.md`, not a replacement for it. Its output is a compatibility packet that lets the parent closure plan decide whether `parent_closure_preflight_phase0` can enter a preflight-clean path, whether it must remain blocked because required-surface remediation could not be completed inside scope, or whether an owner-only disposition is still required before parent closure execution.

In this predecessor plan, `blocked` is a diagnostic / routing verdict. It is not a claim that the overall DVF current-route / authority / seal closure problem should remain unsolved. It means the parent closure plan must not pretend the surface is already clean; it must either disposition the blocker, rerun the relevant preflight, or close as intentionally unresolved.

The round should produce a machine-readable inventory for the required artifact universe and classify each artifact along these axes:

* `missing / present`
* `dirty / clean`
* `ignore-rule-match / no-rule-match`
* `effectively-ignored / not-effectively-ignored`
* `tracked / untracked`
* `field-pass / field-fail`
* `hash-candidate / non-hash-candidate`

These axes cover the roadmap's named classifications (`missing`, `dirty`, `ignored`, `tracked`, `untracked`, `field-pass`, `hash-candidate`, `non-hash-candidate`) while splitting the dangerous `ignored` axis into diagnostic rule-match and verdict-relevant effective ignored state.

The closeout target is a fail-closed resolved preflight verdict:

* `ready`
* `blocked`
* `disposition_required`

`blocked` is valid only when the plan has produced a disposition ledger and either an allowed remediation failed validation, an owner-only decision remains unresolved, or the current checkout cannot be made closure-safe without leaving the approved scope.

If the initial census at execution readpoint matches the post-commit readiness observation (`missing=0`, `dirty=0`, `tracked=93`, `untracked=0`, `ignored=0` for required artifacts and all required test modules tracked/not ignored), the plan must use the committed-surface fast path: skip remediation, record `artifact_disposition_state=not_needed`, run validation/rerun binding, and emit `ready` only after the post-census validation confirms the same counts.

The maximum allowed claim is:

```text
DVF 3-3 required artifacts listed by the live current-route required-validation
manifest were censused, dispositioned, and rerun at bound checkout readpoints.
The round separated field-level required-validation success from VCS preservation
state, partitioned hash-candidate and non-hash-candidate artifacts, reconciled
bounded durable surface claims against the full live-manifest denominator, applied
only approved governance-surface remediation, and produced a fail-closed parent
closure-entry verdict.
```

This objective includes required-surface disposition and approved governance-surface remediation. It does not include source authority cutover, runtime deployability, release readiness, package readiness, independent review completion, owner seal, or canonical seal completion.

The predecessor handoff does not satisfy the parent closure plan's machine PASS, independent review gate, owner seal, top-doc sync claim, or canonical seal boundary. The parent plan remains responsible for recomputing and validating its own `parent_closure_preflight_phase0` and `parent_closure_phase5_vcs_surface` evidence at the same readpoint.

---

## 2. Scope

This plan covers one governance-only, build-time required-surface preflight resolution round for Iris DVF 3-3.

Included scope:

* current checkout readpoint capture
* live required-validation manifest fingerprint capture
* live manifest `required_artifacts` universe derivation
* artifact path normalization and duplicate detection
* per-artifact VCS state census
* per-artifact JSON parse and required field-check redrive
* strict separation of field-pass and VCS-pass
* ignored-state semantic split: rule match, tracked-but-rule-matched, untracked ignored, effective ignored, and blocker reason
* hash-candidate and non-hash-candidate partition
* dirty / ignored / untracked / missing lists
* bounded durable-surface denominator reconciliation
* census output root disjointness guard
* current-route test collection isolation check
* protected no-mutation proof
* required-surface disposition ledger
* minimum-scope governance remediation for dirty / ignored / untracked / missing required surface when allowed by disposition
* post-remediation preflight rerun and readpoint binding
* committed-surface fast path when no required-surface blocker remains
* closure-entry verdict predicate and machine report
* parent closure plan compatibility packet
* parent `parent_closure_preflight_phase0` / `parent_closure_phase5_vcs_surface` input mapping
* unresolved owner-disposition queue, only for blockers that cannot be safely resolved inside this plan
* claim-boundary and ledger packet planning
* standard census / disposition / rerun validation plus mandatory synthetic fail-closed predicate matrix

Primary evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/`

Direct documentation artifact:

* `docs/dvf_3_3_required_artifact_surface_preflight_census_plan.md`

Expected execution docs:

* `docs/dvf_3_3_required_artifact_surface_preflight_census_claim_boundary.md`
* `docs/dvf_3_3_required_artifact_surface_preflight_census_ledger_packet.md`
* optional `docs/dvf_3_3_required_artifact_surface_preflight_census_closeout.md`

Read-only context inputs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/dvf_vcs_tracking_policy.md`
* `docs/dvf_3_3_durable_surface_policy.md`
* `docs/dvf_3_3_durable_current_authority_surface_alignment_plan.md`
* `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_plan.md`
* `docs/dvf_3_3_predecessor_stale_artifact_reentry_guard_plan.md`
* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_plan.md`
* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/_docs/round3/round3_run_contract_tests.py`
* existing DVF 3-3 VCS / durable / predecessor guard tooling and tests

### Explicitly Out Of Scope

* unreviewed dirty required artifact modification
* broad or convenience ignored required artifact unignore
* unreviewed untracked required artifact `git add`
* required artifact deletion without owner disposition
* required artifact regeneration as source/rendered/runtime/package writer authority
* unreviewed or broad `.gitignore` mutation
* live `current_route_required_validations.json` mutation
* required artifact set add / remove
* required test set add / remove
* current-route predicate weakening
* source facts / decisions / overlay support mutation
* rendered output regeneration
* Lua bridge export mutation
* runtime chunk replacement
* package payload mutation
* package probing and package readiness; only read-only package path membership classification may be recorded if required for a no-mutation boundary
* release / Workshop / B42 / deployment readiness
* manual in-game QA
* semantic quality acceptance
* public-facing text quality acceptance
* independent review completion
* owner seal
* canonical seal
* Durable Current Authority Surface Alignment body rewrite or reopen
* broad staging root unignore
* cleanup of unrelated dirty working tree changes

Allowed in scope after disposition:

* record an intentional dirty required artifact as an accepted governance artifact update and bind its post-resolution hash/freshness evidence
* stage or track required governance evidence when the ledger proves it is required for clean-checkout preservation and does not touch source/rendered/runtime/package authority
* narrow `.gitignore` exception proposals or drafts for required governance evidence, with owner review before adoption
* classify tracked-but-ignore-rule-matched artifacts separately from untracked ignored artifacts and resolve only the preservation problem that remains
* produce non-hash exception candidates only with deterministic substitute checks, role ceiling, and parent closure compatibility impact
* rerun the required-surface preflight after every accepted remediation

---

## 3. Non-Goals

This plan is specifically intended to solve the dirty / ignored / untracked required artifact surface preflight problem. It measures first because remediation without a complete denominator is unsafe, then dispositions the blockers, applies only approved governance-surface remediation, and reruns the checks.

The plan does not convert current-route `PASS / closure_enforced=true` into VCS preservation readiness. The codebase inspection confirms that `Iris/_docs/round3/round3_run_contract_tests.py` checks required artifact presence, JSON validity, and configured field equality, but it does not treat Git cleanliness, ignored state, tracked state, or hashability as the same predicate.

The plan does not reinterpret the Durable Current Authority Surface Alignment result. Its `post_reconciliation_untracked_ignored_required_artifact_count=0` claim remains bounded to that round's durable surface denominator and must not be silently applied to the full live-manifest `93` artifact universe.

The plan does not promote staging artifacts to current authority. `Iris/build/description/v2/staging/README.md` explicitly states that staging artifacts are not current authority by path existence.

The plan does not introduce a public artifact format, runtime behavior, package layout, or user-facing Iris feature.

---

## 4. Assumptions

* `docs/Philosophy.md` is the top project authority.
* Iris remains a 100% Lua runtime mod; this round is build-time / governance-only.
* DVF 3-3 current authority remains axis-separated across source facts, decisions, overlay support, rendered output, Lua bridge output, runtime chunks, package payload, and governance evidence.
* The live required-validation manifest is `Iris/_docs/round3/current_route_required_validations.json`.
* Current inspected manifest values are descriptive readpoint observations: `required_artifacts=93`, `required_tests=48`, schema `round3-current-route-required-validations-v1`, route `current`, status `PASS`.
* Execution must rederive the required artifact count from the live manifest at runtime; `93` is the expected current readpoint, not a hardcoded substitute for manifest parsing.
* The current route may still report `PASS / 127 tests / closure_enforced=true`; that route count is the union of current taxonomy tests plus live manifest required tests, while `required_tests=48` is the manifest-required subset. Neither count answers the VCS preservation census.
* Existing `round3_run_contract_tests.py` already performs artifact field-check fail-closed behavior through `artifact_check_errors()`.
* Existing VCS policy tooling (`dvf_vcs_tracking_policy.py`) and durable surface tooling provide useful Git inspection patterns, but this round must not broaden their authority claims.
* Initial Git introspection is read-only: `git status`, `git ls-files`, `git check-ignore`, `git diff --name-only`, `git diff --cached --name-only`, and optional `git hash-object` for provenance/hashability only. Any later Git-affecting remediation, such as tracking a required governance artifact or proposing `.gitignore` changes, requires an approved disposition row.
* Git status ignored-mode is pinned to `git status --porcelain=v1 --ignored=matching -- <path>` unless the execution environment proves a different mode is required and records it in `git_environment_report.json`.
* Git version, `core.excludesFile`, `.git/info/exclude`, local `.gitignore` state, and relevant global ignore accessibility must be recorded in census readpoint freeze.
* `git check-ignore --no-index -v` is diagnostic rule-match evidence only. It must populate `ignore_rule_match` / `ignore_match_source`; it must not directly populate verdict-relevant ignored state.
* Reports and tests must expose this as `check_ignore_no_index_is_diagnostic_only=true`.
* Windows and POSIX path forms must normalize to one repo-relative path identity.
* Staged dirty and unstaged dirty are different fields and must not be collapsed into a single opaque status.
* Ignored status is not deletion approval and not evidence that an artifact is unimportant. The verdict-relevant field is `effectively_ignored`, derived from tracked state, ignore-rule match, and explicit strict preflight policy.
* Strict ignored handling is selected for the pre-disposition gate: `effectively_ignored_required_artifact_count > 0` blocks immediate `ready`. Bounded/residual and expected/policy-conflicting ignored splits are retained for report readability and this plan's disposition routing.
* Tracked status is not authority promotion.
* Hash vocabulary is separated: `local_provenance_hash` is a local content digest, `canonical_candidate_hash` is a deterministic candidate for later review, and `sealed_hash` is not produced by this round.
* Local hash availability is not hash seal, reproducibility proof, or preservation proof.
* Dirty artifact local hashes may be recorded only as `local_provenance_hash`, not as sealable canonical hashes.
* Ignored artifact local hashes may be recorded only as `local_provenance_hash`, not as VCS preservation evidence.
* Heavy live Git fixture validation is not default for this plan because the requested round is a census / inventory round. Mandatory synthetic fail-closed predicate validation is still in scope and required.
* New focused tests for this round must be isolated from current-route collection unless the live manifest is separately amended in an approved adoption round.
* Dirty working tree changes outside this plan must be preserved.

---

## 5. Repository Areas Affected

### Code

Expected future implementation surfaces:

* `Iris/build/description/v2/tools/build/run_dvf_3_3_required_artifact_surface_preflight_census.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_required_artifact_surface_preflight_census.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_required_artifact_surface_preflight_census_common.py` if shared helpers are justified
* `Iris/build/description/v2/tests/test_dvf_3_3_required_artifact_surface_preflight_census.py`

Read-only implementation references:

* `Iris/_docs/round3/round3_run_contract_tests.py`
* `Iris/build/description/v2/tools/build/dvf_vcs_tracking_policy.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_durable_current_authority_surface_alignment.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_durable_current_authority_surface_alignment.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_predecessor_stale_artifact_reentry_guard.py`

### Docs

Direct plan:

* `docs/dvf_3_3_required_artifact_surface_preflight_census_plan.md`

Expected future docs:

* `docs/dvf_3_3_required_artifact_surface_preflight_census_claim_boundary.md`
* `docs/dvf_3_3_required_artifact_surface_preflight_census_ledger_packet.md`
* optional `docs/dvf_3_3_required_artifact_surface_preflight_census_closeout.md`

Read-only docs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/dvf_vcs_tracking_policy.md`
* `docs/dvf_3_3_durable_surface_policy.md`

### Config

None planned.

The live required-validation manifest is an input, not a mutation target:

* `Iris/_docs/round3/current_route_required_validations.json`

### Generated Artifacts

Expected generated artifacts under:

* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/`

Expected phase outputs include:

* `census_p0_readpoint_freeze/readpoint_freeze_report.json`
* `census_p0_readpoint_freeze/manifest_fingerprint.json`
* `census_p0_readpoint_freeze/protected_surface_baseline_hashes.json`
* `census_p0_readpoint_freeze/git_environment_report.json`
* `census_p0_readpoint_freeze/current_route_collection_baseline.json`
* `census_p1_denominator_lock/required_artifact_universe.json`
* `census_p1_denominator_lock/census_denominator_declaration.json`
* `census_p1_denominator_lock/manifest_path_normalization_report.json`
* `census_p1_denominator_lock/output_root_disjointness_report.json`
* `census_p2_vcs_census/required_artifact_vcs_inventory.jsonl`
* `census_p2_vcs_census/required_artifact_vcs_summary.json`
* `census_p2_vcs_census/dirty_required_artifact_list.json`
* `census_p2_vcs_census/ignored_required_artifact_list.json`
* `census_p2_vcs_census/tracked_required_artifact_list.json`
* `census_p2_vcs_census/untracked_required_artifact_list.json`
* `census_p3_field_join/required_artifact_field_inventory.jsonl`
* `census_p3_field_join/field_pass_vcs_state_join_report.json`
* `census_p4_hash_partition/hash_candidate_inventory.jsonl`
* `census_p4_hash_partition/non_hash_candidate_inventory.jsonl`
* `census_p4_hash_partition/hash_candidate_summary.json`
* `census_p4_hash_partition/non_hash_candidate_summary.json`
* `census_p5_durable_split/denominator_scope_split_report.json`
* `census_p5_durable_split/bounded_durable_reconciliation_report.json`
* `census_p6_verdict/closure_entry_readiness_verdict.json`
* `census_p6_verdict/parent_closure_preflight_phase0_input.json`
* `census_p6_verdict/parent_closure_phase5_vcs_surface_input.json`
* `census_p6_verdict/preflight_blocker_summary.json`
* `census_p6_verdict/disposition_required_summary.json`
* `census_p6_verdict/carry_forward_disposition_queue.json`
* `census_p6_resolution/required_surface_disposition_ledger.json`
* `census_p6_resolution/approved_governance_remediation_plan.json`
* `census_p6_resolution/remediation_application_report.json`
* `census_p6_resolution/post_remediation_required_surface_rerun_report.json`
* `census_p6_resolution/unresolved_owner_disposition_queue.json`
* `census_p6_resolution/parent_closure_preflight_phase0_resolved_input.json`
* `census_p6_resolution/parent_closure_phase5_vcs_surface_resolved_input.json`
* `census_p7_validation/synthetic_fail_closed_matrix_report.json`
* `census_p7_validation/current_route_collection_isolation_report.json`
* `census_p7_validation/validation_report.json`
* `census_p7_validation/validation_report.require_complete.json`
* `census_p8_closeout_no_mutation/protected_surface_no_mutation_report.json`
* `census_p8_closeout_no_mutation/main_plan_compatibility_packet.json`
* `census_p8_closeout_no_mutation/final_preflight_census_report.json`

The `census_p*` prefix is mandatory. Parent closure preflight references must use `parent_closure_preflight_phase0` and must not reuse the bare `phase0` token.

### Parent Closure Compatibility Contract

This predecessor round is compatible with the parent closure plan only through read-only handoff artifacts. It must not write into `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/`, and it must not create parent closure evidence on behalf of the parent plan.

Parent consumption points:

* Parent Change 1 / `parent_closure_preflight_phase0` may consume `parent_closure_preflight_phase0_input.json` as an early blocker and readpoint alignment input.
* Parent Change 1 / `parent_closure_preflight_phase0` should consume `parent_closure_preflight_phase0_resolved_input.json` as the post-resolution parent entry input when this plan reaches `ready`.
* Parent Change 6 / `parent_closure_phase5_vcs_surface` may consume `parent_closure_phase5_vcs_surface_input.json` as pre-resolution VCS required-surface census input.
* Parent Change 6 / `parent_closure_phase5_vcs_surface` should consume `parent_closure_phase5_vcs_surface_resolved_input.json` as the post-resolution VCS required-surface input when this plan reaches `ready`.
* Parent final review may consume `main_plan_compatibility_packet.json` as predecessor provenance, not as machine PASS evidence.

The compatibility packet must include at least:

* `parent_plan_artifact`
* `parent_round_identifier`
* `parent_evidence_root`
* `predecessor_plan_artifact`
* `predecessor_round_identifier`
* `predecessor_evidence_root`
* `readpoint_git_head`
* `readpoint_index_state`
* `live_required_manifest_path`
* `live_required_manifest_sha256`
* `required_artifact_count`
* `missing_required_artifact_count`
* `dirty_required_artifact_count`
* `effectively_ignored_required_artifact_count`
* `tracked_but_ignore_matched_blocker_count`
* `untracked_ignored_blocker_count`
* `untracked_required_artifact_count`
* `field_pass_count`
* `field_fail_count`
* `hash_candidate_count`
* `non_hash_candidate_count`
* `semantic_verdict`
* `artifact_disposition_state`
* `post_resolution_rerun_performed`
* `parent_phase0_entry_state`
* `parent_phase5_vcs_surface_state`

Parent state mapping:

* Pre-resolution `dirty_required_artifact_count > 0` maps to `parent_phase0_entry_state=blocked_input` and parent blocker token `preflight_blocked_required_dirty_surface` until disposition and rerun complete.
* Post-resolution missing, dirty, field-fail, effectively ignored without accepted disposition, VCS query error, or protected mutation maps to `parent_phase0_entry_state=blocked_input` and parent execution closeout `blocked / no-authority-mutation`.
* Absence of post-resolution blocked conditions with unresolved owner disposition maps to `parent_phase0_entry_state=disposition_required_input`.
* Only absence of post-resolution blocked and owner-pending conditions maps to `parent_phase0_entry_state=ready_input`.

`ready_input` is not parent closure PASS. It only says the parent closure plan may enter its next preflight-clean stage and must still recompute `parent_closure_preflight_phase0` and `parent_closure_phase5_vcs_surface` facts at the same checkout readpoint.

---

## 6. Planned Changes

### Change 1 - Readpoint freeze and protected no-mutation guard

Purpose:

Capture the exact checkout, manifest, and protected surface baseline before any census output is written.

Files:

* `Iris/build/description/v2/tools/build/run_dvf_3_3_required_artifact_surface_preflight_census.py`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p0_readpoint_freeze/readpoint_freeze_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p0_readpoint_freeze/manifest_fingerprint.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p0_readpoint_freeze/protected_surface_baseline_hashes.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p0_readpoint_freeze/git_environment_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p0_readpoint_freeze/current_route_collection_baseline.json`

Implementation Notes:

* Record branch, HEAD, pinned `git status --porcelain=v1 --ignored=matching`, manifest path, manifest SHA-256, and manifest schema.
* Record parent closure plan path, SHA-256, round identifier, and evidence root target.
* Record Git version, `core.excludesFile`, `.git/info/exclude` presence/hash when accessible, repository `.gitignore` hash, and whether global ignore files are inaccessible.
* Treat user/global ignore permission warnings as environment warnings, not automatic blockers, when repository `.gitignore`, per-path `git status --ignored=matching`, and final `git check-ignore --no-index -v` predicates are available for every required path.
* Record source / rendered / Lua bridge / runtime chunk / package protected path hashes before generation.
* Record the pre-implementation current-route collection baseline: current route list/count, current route PASS status when runnable, and whether discovery is explicit manifest-based or glob-based.
* Treat existing dirty files as facts to capture, not as cleanup targets. Only dirty paths intersecting required artifacts, required tests, live required manifest, parent/child plan docs, or protected source/rendered/Lua/runtime/package surfaces can block this preflight.
* Record unrelated dirty paths, including transient build locks or non-required staging drift, in an advisory bucket so they do not reduce `ready` probability for the required surface.
* Write only under the selected staging evidence root.
* If the output root already exists, write a superseding run record or fail-closed rather than silently mixing readpoints.
* Refer to the parent closure blocker only as `parent_closure_preflight_phase0`; do not use bare `Phase 0` in generated reports.
* Record that the predecessor evidence root is disjoint from the parent closure evidence root and cannot create parent closure evidence.

Validation:

* Manifest hash is captured.
* Parent closure plan artifact hash and evidence root target are captured.
* Protected surface baseline exists.
* Census output root is the only planned write root.
* Census output root is disjoint from the parent closure evidence root.
* Git environment and ignore configuration are captured.
* Global ignore permission warning is classified as advisory when all required-path repo-local predicates succeeded.
* Unrelated dirty paths are separated from required-surface blockers.
* Current-route collection baseline is captured before new focused tests are introduced.
* Protected surface changed count is `0` at final no-mutation check.

---

### Change 2 - Required artifact universe and denominator lock

Purpose:

Derive the required artifact universe directly from the live manifest and prevent denominator substitution.

Files:

* `Iris/_docs/round3/current_route_required_validations.json` read-only
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p1_denominator_lock/required_artifact_universe.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p1_denominator_lock/census_denominator_declaration.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p1_denominator_lock/manifest_path_normalization_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p1_denominator_lock/output_root_disjointness_report.json`

Implementation Notes:

* Parse `required_artifacts` and require every row to have a repo-relative `path`.
* Expect the current readpoint to derive `93` artifacts, but report mismatch instead of substituting another denominator.
* Keep required artifacts and required tests separate. Current inspected manifest has `48` required tests; they are not part of the artifact denominator.
* Normalize separators to repo-relative forward-slash paths.
* Detect duplicate artifact paths and duplicate logical checks.
* Fail-loud on absolute paths, parent traversal, empty paths, or paths outside the repo.
* Assert `census_output_root ∩ required_artifact_paths = ∅`; if not empty, block the round as self-contaminating.

Validation:

* Derived count is `93`, or mismatch is recorded as a blocker.
* Required test count is recorded separately.
* Duplicate path handling is deterministic.
* Census output root disjointness passes.
* Denominator non-substitution report explicitly rejects `56 / 28 / 2105 / 2084 / 21 / 1062 / 311 / 163 / 148` as substitutes for the live artifact denominator.

---

### Change 3 - Per-artifact VCS state census

Purpose:

Measure Git preservation state for each required artifact without editing the working tree.

Files:

* `Iris/build/description/v2/tools/build/run_dvf_3_3_required_artifact_surface_preflight_census.py`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p2_vcs_census/required_artifact_vcs_inventory.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p2_vcs_census/required_artifact_vcs_summary.json`

Implementation Notes:

For every required artifact, record:

* `exists`
* `tracked`
* `untracked`
* `ignore_rule_match`
* `ignore_match_source`
* `tracked_but_ignore_matched`
* `untracked_ignored`
* `effectively_ignored`
* `ignored_blocker_reason`
* `dirty`
* `dirty_index`
* `dirty_staged`
* `dirty_unstaged`
* `git_status_code`
* `git_ignore_source`
* `file_mode`
* `is_symlink`
* `is_directory`
* `size_bytes`
* `vcs_query_error`

Use read-only commands only:

* `git status --porcelain --ignored -- <path>`
* `git ls-files -- <path>`
* `git check-ignore --no-index -v <path>`
* `git diff --name-only -- <path>`
* `git diff --cached --name-only -- <path>`

Implementation should follow the existing VCS policy tooling pattern where useful, but this census must include all live required artifacts rather than only the bounded durable subset.

Ignored-state derivation rules:

* `git check-ignore --no-index -v` populates only `ignore_rule_match` and `ignore_match_source`.
* `tracked_but_ignore_matched=true` is diagnostic and must not be silently merged into `untracked_ignored`.
* `untracked_ignored=true` requires an untracked path plus an active ignore rule match.
* `effectively_ignored=true` is the pre-disposition verdict-relevant value. Under this plan's strict preflight rule, it is true for `untracked_ignored=true` and for any `tracked_but_ignore_matched=true` required artifact. Any later exception or accepted disposition belongs to this plan's resolution lane and must be proven by post-resolution rerun evidence.
* `ignored_blocker_reason` must be one of `untracked_ignored`, `tracked_rule_match_without_preservation_disposition`, `git_query_error`, `none`, or a later explicitly documented value. Unknown ignored semantics must fail-loud.
* `tracked_but_ignore_matched` and `untracked_ignored` must remain separate final-report buckets. If a tracked-but-rule-matched artifact contributes to `blocked`, the report must state that the artifact is tracked and therefore preserved in clean checkout, while still blocked by this round's strict preflight rule.
* `check_ignore_no_index_is_diagnostic_only=true` must be present in the VCS inventory summary or validation report.

Validation:

* Every artifact has exactly one VCS tuple.
* VCS query failure count is `0`.
* Dirty, ignore-rule-match, tracked-but-rule-matched, untracked-ignored, effectively-ignored, tracked, untracked, and missing counts are all summarized.
* Dirty staged and dirty unstaged states are separately visible.
* Tracked-but-rule-matching and untracked-ignored fixtures are covered by focused validation.
* Tracked-but-rule-matching rows are not merged into the untracked ignored list.
* Roadmap premises `dirty required artifact 6` and `ignored required artifact 19` are reconciled against current execution counts or recorded as readpoint drift.

---

### Change 4 - Field-pass redrive and VCS-state join

Purpose:

Redrive existing field-level manifest checks and join them with VCS state without conflating the predicates.

Files:

* `Iris/_docs/round3/round3_run_contract_tests.py` read-only reference
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p3_field_join/required_artifact_field_inventory.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p3_field_join/field_pass_vcs_state_join_report.json`

Implementation Notes:

* Reuse the same conceptual field-path lookup model as `artifact_check_errors()` in `round3_run_contract_tests.py`.
* For every artifact, record JSON parse state, missing required field count, field mismatch count, and field-pass boolean.
* Non-JSON artifacts should be fail-loud if they have manifest field checks.
* Field-pass must never imply tracked, not ignored, clean, hashable, or ready.
* VCS-pass must never imply field-pass.

Validation:

* JSON invalid count is reported.
* Field mismatch count is reported.
* Missing required field count is reported.
* `field_pass=true` plus `dirty=true` remains a blocker.
* `field_pass=true` plus `effectively_ignored=true` remains blocked under this plan's strict fail-closed rule.

---

### Change 5 - Hash-candidate and non-hash-candidate partition

Purpose:

Classify each artifact's hashability without claiming hash seal or reproducibility.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p4_hash_partition/hash_candidate_inventory.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p4_hash_partition/non_hash_candidate_inventory.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p4_hash_partition/hash_candidate_summary.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p4_hash_partition/non_hash_candidate_summary.json`

Implementation Notes:

Classify every artifact into exactly one partition:

* `hash_candidate`
* `non_hash_candidate`

Allowed non-hash reasons include:

* missing artifact
* directory artifact
* unreadable content
* symlink target unresolved
* dirty local artifact blocks canonical candidate hash
* ignored local artifact blocks preservation proof
* volatile content marker
* unresolved artifact class

Hash vocabulary:

* `local_provenance_hash` may be recorded for readable files as a local content digest only.
* `canonical_candidate_hash` may be recorded only when the artifact is present, readable, deterministic enough for candidate identity, and not blocked by dirty/effective ignored state.
* `sealed_hash` is not produced by this round.

Do not call any value reproducible, sealed, or preservation proof.

Validation:

* Partition coverage is `100%`.
* Non-hash reason coverage is `100%`.
* Dirty artifact may have `local_provenance_hash` but not `canonical_candidate_hash`.
* Effectively ignored artifact may have `local_provenance_hash` but not preservation proof.
* `local_provenance_hash`, `canonical_candidate_hash`, and `sealed_hash` vocabulary remain separate.

---

### Change 6 - Bounded durable-surface reconciliation

Purpose:

Reconcile Durable Current Authority Surface Alignment's bounded `0` claim against the full `93` live-manifest census without reopening the durable seal.

Files:

* `docs/dvf_3_3_durable_surface_policy.md` read-only
* `docs/dvf_3_3_durable_current_authority_surface_alignment_plan.md` read-only
* `Iris/build/description/v2/staging/dvf_3_3_durable_current_authority_surface_alignment/` read-only
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p5_durable_split/denominator_scope_split_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p5_durable_split/bounded_durable_reconciliation_report.json`

Implementation Notes:

* Map each required artifact to bounded durable surface membership when possible.
* Keep durable seal claims scoped to their bounded denominator.
* Attribute full live-manifest dirty / ignored / untracked residuals outside that bounded set without treating them as prior seal regression.
* Preserve the selected pre-disposition rule: bounded/residual split is used for report readability and resolution routing only; it does not override the need to disposition `effectively_ignored > 0` before any final `ready` claim.
* Do not edit durable seal docs, reports, or staging evidence.

Validation:

* Durable seal body mutation count is `0`.
* Full manifest denominator remains `93` at the current readpoint unless mismatch is explicitly reported.
* Bounded durable denominator and full live-manifest denominator are separately named.
* Count equality is never used as identity proof.
* Verdict report states that the split was consumed as report-only evidence under strict fail-closed policy.

---

### Change 7 - Required Surface Resolution, Rerun, and Closure-Entry Verdict

Purpose:

Resolve the required artifact surface preflight blocker by turning census findings into a disposition ledger, applying only approved governance-surface remediation, rerunning the required-surface checks, and producing a fail-closed parent closure-entry verdict.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p6_verdict/closure_entry_readiness_verdict.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p6_verdict/parent_closure_preflight_phase0_input.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p6_verdict/parent_closure_phase5_vcs_surface_input.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p6_verdict/preflight_blocker_summary.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p6_verdict/disposition_required_summary.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p6_verdict/carry_forward_disposition_queue.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p6_resolution/required_surface_disposition_ledger.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p6_resolution/approved_governance_remediation_plan.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p6_resolution/remediation_application_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p6_resolution/post_remediation_required_surface_rerun_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p6_resolution/unresolved_owner_disposition_queue.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p6_resolution/parent_closure_preflight_phase0_resolved_input.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p6_resolution/parent_closure_phase5_vcs_surface_resolved_input.json`

Implementation Notes:

Initial blocker conditions:

* required artifact denominator mismatch
* missing required artifact count > 0
* dirty required artifact count > 0
* `effectively_ignored_required_artifact_count > 0` under this plan's strict fail-closed rule
* invalid JSON count > 0
* field mismatch count > 0
* missing required field count > 0
* VCS query error count > 0
* protected surface mutation detected

Committed-surface fast path:

* If initial required artifact counts are `missing=0`, `dirty=0`, `tracked=93`, `untracked=0`, `ignored=0`, and required test module counts are `missing=0`, `tracked=17`, `untracked=0`, `ignored=0`, write an empty disposition ledger with `artifact_disposition_state="not_needed"`.
* In the fast path, do not apply `.gitignore`, `git add`, regeneration, or remediation actions.
* The fast path still requires post-census validation, protected no-mutation verification, parent compatibility packet generation, and current-route timeout-budgeted regression validation before final `ready`.
* If validation commands create non-required staging drift, record it as `validation_induced_non_required_staging_drift` and rerun the required-surface census. It blocks final `ready` only if the drift intersects required artifacts/tests, live required manifest, protected surfaces, or parent/child plan docs.

For every initial blocker, write one ledger row with:

* artifact path
* blocker class
* pre-resolution VCS tuple
* required field status
* hash-candidate status
* proposed disposition
* allowed action type
* owner-review requirement
* expected post-resolution predicate
* rerun evidence path

Allowed action types:

* `accept_current_dirty_content_as_governance_artifact_update`
* `restore_or_regenerate_governance_artifact_from_approved_producer`
* `track_required_governance_artifact`
* `propose_minimum_gitignore_exception`
* `reclassify_tracked_rule_match_as_preserved_with_warning`
* `bind_non_hash_exception_with_substitute_checks`
* `mark_unrelated_checkout_drift_owner_action_required`
* `owner_adjudication_required`

The plan may apply an action only when it stays inside the governance surface and does not mutate source facts, rendered output, Lua bridge output, runtime chunks, or package payloads. If an action requires owner single-writer authority, source/rendered/runtime/package mutation, or ambiguous authority judgment, it must be recorded in `unresolved_owner_disposition_queue.json` instead of being applied.

Post-resolution rerun requirements:

* rerun VCS census for all required artifacts
* rerun field-pass / VCS-state join
* rerun hash-candidate / non-hash-candidate partition
* rerun output root disjointness check
* rerun protected no-mutation check
* compare pre-resolution and post-resolution counts

Final blocked conditions:

* unresolved owner disposition queue count > 0
* missing required artifact count > 0 after remediation
* dirty required artifact count > 0 after remediation
* effectively ignored required artifact count > 0 after remediation, unless classified as tracked-preserved with an accepted minimum-scope disposition
* invalid JSON, field mismatch, missing required field, VCS query error, or protected mutation count > 0 after remediation
* non-hash exception lacks deterministic substitute checks, role ceiling, or parent compatibility impact
* current-route regression validation fails when run with a timeout budget of at least `360s`
* validation-induced drift intersects required artifacts, required tests, live required manifest, protected surfaces, or parent/child plan docs

Final disposition-required conditions:

* no final blocked conditions, but a closure-relevant owner decision is still pending
* no final blocked conditions, but an approved remediation was intentionally deferred

Default ready conditions:

* denominator is derived from live manifest and matches expected current readpoint
* post-resolution missing / dirty / invalid JSON / field mismatch / VCS query error / protected mutation counts are all `0`
* post-resolution effectively ignored count is `0`, or remaining tracked-rule-match rows have explicit accepted preservation disposition
* untracked artifacts are `0` or have an accepted tracked/non-tracked preservation disposition
* every artifact has accepted hash-candidate or non-hash-candidate classification after remediation
* required-surface disposition ledger has no unresolved blocker row
* current-route regression validation is PASS with `closure_enforced=true` and `test_count=127` or a recorded same-readpoint count update
* unrelated dirty paths, if any, are explicitly outside required/protected surfaces

Parent ready-input mapping:

* ready conditions yield `parent_phase0_entry_state="ready_input"` and `parent_phase5_vcs_surface_state="ready_input"`.
* `ready_input` permits only parent preflight-clean entry. The parent closure plan must still recompute `parent_closure_preflight_phase0` and `parent_closure_phase5_vcs_surface` facts before machine PASS.

The verdict report must include:

* `semantic_verdict`
* `canonical_verdict_token="author_reserved"` or `canonical_verdict_token="not_claimed"`
* `ready_claim_boundary="parent_closure_preflight_clean_entry_only"` when semantic verdict is `ready`
* `parent_phase0_entry_state`
* `parent_phase5_vcs_surface_state`
* `parent_blocker_token` when applicable
* `artifact_disposition_state`
* `post_resolution_rerun_performed=true`
* `package_probe_performed=false`
* `package_membership_classification_only=true` if any package path membership evidence is recorded
* `bounded_residual_split_verdict_override=false`
* `independent_review_gate="BLOCKED"`

Validation:

* Dirty > 0 before remediation creates a disposition ledger row, not an immediate final closeout.
* Dirty > 0 after remediation yields semantic verdict `blocked`.
* Effectively ignored > 0 before remediation creates disposition rows.
* Effectively ignored > 0 after remediation yields semantic verdict `blocked` unless every remaining row has accepted tracked-preserved disposition.
* Missing > 0 after remediation yields semantic verdict `blocked`.
* Field-fail > 0 after remediation yields semantic verdict `blocked`.
* Untracked-only residual after remediation yields `disposition_required`, not `ready`, unless every row has accepted preservation disposition.
* Final `ready` requires post-resolution rerun evidence.
* Verdict is derived from machine inventories, not pre-decided text.
* Canonical token remains author-reserved.
* `ready` is not closure PASS, canonical seal, review complete, release readiness, or package readiness.

---

### Change 8 - Standard Resolution Validation and No-Mutation Verification

Purpose:

Validate the census, disposition, remediation, rerun, and final verdict reports without mutating protected source / rendered / runtime / package surfaces.

Files:

* `Iris/build/description/v2/tools/build/validate_dvf_3_3_required_artifact_surface_preflight_census.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_required_artifact_surface_preflight_census.py`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p7_validation/synthetic_fail_closed_matrix_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p7_validation/current_route_collection_isolation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p7_validation/validation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p7_validation/validation_report.require_complete.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p8_closeout_no_mutation/protected_surface_no_mutation_report.json`

Implementation Notes:

Standard validation covers:

* manifest parsing and denominator derivation
* path normalization determinism
* VCS tuple coverage
* field-pass / VCS-state separation
* hash partition coverage
* durable denominator split
* disposition ledger completeness
* allowed remediation action validation
* post-remediation rerun binding
* pre/post count comparison
* verdict predicate behavior
* mandatory synthetic fail-closed predicate matrix
* ignored-state semantics unit validation
* current-route test collection isolation
* output ordering determinism
* protected surface no-mutation
* `parent_closure_preflight_phase0` FAIL-LOUD semantics preservation

Mandatory synthetic matrix cases:

* `pre_dirty > 0` -> disposition ledger required
* `pre_effectively_ignored > 0` -> disposition ledger required
* `pre_untracked_only` -> disposition ledger required
* `post_missing > 0` -> `blocked`
* `post_dirty > 0` -> `blocked`
* `post_effectively_ignored > 0` without accepted tracked-preserved disposition -> `blocked`
* `post_invalid_json > 0` -> `blocked`
* `post_field_mismatch > 0` -> `blocked`
* `post_vcs_query_error > 0` -> `blocked`
* `post_protected_mutation > 0` -> `blocked`
* `owner_disposition_pending > 0` -> `disposition_required`
* `post_all_clear` -> `ready`
* `post_all_clear_with_accepted_tracked_rule_match` -> `ready`

Ignored-state validation must cover at least:

* tracked but ignore-rule-matched artifact
* untracked ignored artifact
* no ignore-rule-match artifact
* Git ignore query warning/failure

Current-route collection isolation validation:

* Determine whether current-route collection is explicit manifest-based or glob-based.
* Capture current-route test list/count before adding the focused census test file.
* Capture current-route test list/count after adding the focused census test file.
* If collection is glob-based, before/after test list and count must be identical unless there is separate live manifest adoption; otherwise isolate the new test and classify the change as `round_introduced_collection_regression`.
* If collection is explicit manifest-based, the primary assertion is no-adoption evidence: the focused census test must not appear in live `required_tests`, current taxonomy-selected IDs, or current-route selected IDs unless a separate adoption round amends those inputs.
* Current-route failure classification must be one of `pre_existing`, `round_introduced_import_regression`, `round_introduced_collection_regression`, or `unrelated_checkout_drift`.

Heavy live Git fixtures are not default. If later selected, fixture execution must occur under isolated temp paths and must not modify live required artifacts or Git state.

Validation:

* Focused unittest passes.
* Validator `--require-complete` passes.
* Synthetic fail-closed matrix passes.
* Ignored-state semantic validation passes.
* Current-route collection isolation report shows either glob-based no unauthorized count change or manifest-based no-adoption evidence.
* Standard report records no protected source / rendered / Lua bridge / runtime / package mutation.
* Current route still passes or any failure is reported as a regression, not hidden by this census.

---

### Change 9 - Documentation, claim boundary, and handoff

Purpose:

Document exactly what the resolution round proved, what was remediated, and what remains unresolved.

Files:

* `docs/dvf_3_3_required_artifact_surface_preflight_census_claim_boundary.md`
* `docs/dvf_3_3_required_artifact_surface_preflight_census_ledger_packet.md`
* optional `docs/dvf_3_3_required_artifact_surface_preflight_census_closeout.md`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p8_closeout_no_mutation/main_plan_compatibility_packet.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/census_p8_closeout_no_mutation/final_preflight_census_report.json`

Implementation Notes:

* Claim boundary must say `required surface preflight resolved` only when disposition, allowed remediation, rerun, and final verdict evidence are all present.
* Claim boundary must say `required surface preflight unresolved / owner disposition pending` when unresolved owner disposition remains.
* Ledger packet must list dirty, ignored, untracked, hash-candidate, non-hash-candidate, disposition, remediation, and rerun evidence.
* If verdict is `blocked`, document which remediation or owner-disposition condition remains unresolved.
* If verdict is `ready`, state that it only means the parent closure can enter the next preflight-clean stage; it is not closure PASS, canonical seal, review complete, release readiness, package readiness, or runtime readiness.
* Generate `main_plan_compatibility_packet.json` and bind it to the parent closure plan artifact hash, parent evidence root target, predecessor readpoint, live manifest hash, census counts, semantic verdict, parent `parent_closure_preflight_phase0` entry state, and parent `parent_closure_phase5_vcs_surface` state.
* If parent and predecessor readpoints cannot be proven identical at parent consumption time, the packet is advisory only and the parent plan must recompute from scratch.
* Final report must put `semantic_verdict` and `canonical_verdict_token=author_reserved/not_claimed` in the same verdict object.
* Final report must include `required_surface_preflight_resolution_state`, not a bare `complete` field.
* Final report must include `artifact_disposition_state=performed`, `not_needed`, or `owner_pending`.
* Final report must include `post_resolution_rerun_performed=true` for any `ready` claim.
* Final report must include `package_probe_performed=false`; if package path evidence is recorded, it must use `package_membership_classification_only=true`.
* Final report must include separate `tracked_but_ignore_matched_blocker_count` and `untracked_ignored_blocker_count` fields when either contributes to blocked status.

Validation:

* Claim boundary includes all non-goals.
* Final report verdict matches machine report.
* Final report records ready claim boundary if semantic verdict is `ready`.
* Final report records `parent_phase0_entry_state` and `parent_phase5_vcs_surface_state`.
* Compatibility packet records parent plan hash, parent evidence root, predecessor readpoint, live manifest hash, and semantic verdict.
* Compatibility packet does not claim parent machine PASS, parent independent review PASS, owner seal, canonical seal, release readiness, package readiness, or runtime readiness.
* Final report records independent review gate remains `BLOCKED`.
* Final report records artifact disposition state and unresolved owner queue count.
* Final report records post-resolution rerun binding when any remediation was applied.
* Final report records package probe was not performed, or package evidence was membership classification only.
* No release readiness claim exists.
* No mutation claim exists.
* Successor disposition input paths are listed.

---

## 7. Validation Plan

### Automated Validation

Default standard resolution validation commands for the eventual implementation:

```powershell
uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_required_artifact_surface_preflight_census.py --mode standard
```

```powershell
uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_required_artifact_surface_preflight_census.py --require-complete
```

```powershell
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_required_artifact_surface_preflight_census.py"
```

The focused unittest must include the mandatory synthetic fail-closed predicate matrix, committed-surface fast path fixture, and validation-induced non-required staging drift fixture. This matrix is part of standard validation, not a heavy optional fixture campaign.

Regression check against the existing current route:

```powershell
uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
```

This command must be run with a timeout budget of at least `360s`; planning-time observation on this workstation was `253.254s` for `PASS / 127 tests / closure_enforced=true`. A shorter timeout is a harness failure, not a current-route failure.

The regression report must classify any failure as `pre_existing`, `round_introduced_import_regression`, `round_introduced_collection_regression`, or `unrelated_checkout_drift`. It must also compare current-route test list/count before and after the focused census test file exists.

After the current-route regression command, rerun the required-surface VCS census. If non-required staging artifacts became dirty, record `validation_induced_non_required_staging_drift`; if required artifacts/tests, the live manifest, plan docs, or protected source/rendered/Lua/runtime/package surfaces became dirty, final `ready` is blocked.

Existing VCS policy guard should remain compatible:

```powershell
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_vcs_tracking_policy.py"
```

If execution touches no Lua file, Lua syntax validation is not a required validation for this round. If any Lua file is touched despite the plan, that is scope drift and the exact relevant command must be run before any pass claim:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

### Manual Validation

Manual review should inspect:

* denominator declaration
* dirty required artifact list
* ignored required artifact list
* tracked-but-rule-matched and untracked-ignored split
* untracked required artifact list
* field-pass / VCS-state join report
* hash-candidate and non-hash-candidate summaries
* durable denominator split report
* committed-surface fast path report, when initial counts are already clean
* validation-induced drift classification
* closure-entry verdict
* diagnostic-only `check-ignore --no-index` assertion
* required-surface disposition ledger
* approved remediation plan and application report
* post-resolution rerun report
* `artifact_disposition_state`
* package probe / package membership classification flags
* parent closure compatibility packet
* parent `parent_closure_preflight_phase0` / `parent_closure_phase5_vcs_surface` input state mapping
* synthetic fail-closed matrix report
* current-route collection isolation report
* claim boundary and ledger packet

Manual in-game validation is not part of this plan.

### Validation Limits

This plan will not validate:

* runtime behavior
* package release
* Workshop release
* B42 readiness
* deployment readiness
* manual in-game QA
* semantic quality
* public-facing text quality
* source facts correctness
* rendered text quality
* Lua bridge deployability
* runtime chunk replacement safety
* package payload safety
* clean checkout full reproduction
* full historical byte reproducibility
* hash stability / reproducibility
* independent external review completion
* canonical seal

---

## 8. Risk Surface Touch

### Authority Surface

No new source / rendered / runtime / package authority.

The only new surface is an isolated staging measurement record under:

* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/`

That staging record is governance evidence, not authority promotion.

### Runtime Behavior Surface

None.

Lua runtime, Browser, Wiki, Tooltip, package payload, runtime loading contract, and runtime chunks are out of scope.

### Compatibility Surface

None.

The plan does not change external mod compatibility, package layout, runtime API, or public user-facing behavior.

Parent closure plan compatibility is limited to read-only handoff artifacts and same-readpoint recomputation rules. It does not create runtime or package compatibility surface.

### Sealed Artifact Surface

None mutated.

Durable Current Authority Surface Alignment, Current Route Required Validation Evidence Freshness Reseal, Completion Vocabulary External Gate Split, Successor Readpoint Seal, and Predecessor / Stale Artifact Reentry Guard are read-only inputs.

### Public-Facing Output Surface

None.

README, Workshop text, user-facing Iris descriptions, public UI text, and public release messaging are out of scope.

---

## 9. Risk Analysis

### Architecture Risk

* The census may be mistaken for a new authority layer. Mitigation: all reports must state `measurement_only` and `no_writer_authority`.
* The live required-validation manifest may be treated as a source / runtime writer. Mitigation: manifest is read-only input and not a mutation target.
* Durable bounded `0` may be incorrectly generalized to the full `93` artifact universe. Mitigation: `census_p5_durable_split` denominator split is mandatory.
* A future implementation may copy durable-surface tooling and accidentally inherit its bounded scope. Mitigation: `census_p1_denominator_lock` must derive directly from live manifest `required_artifacts`.

### Runtime Risk

* Direct runtime risk is low because runtime surfaces are not touched.
* Accidental protected surface writes would invalidate the round. Mitigation: `census_p0_readpoint_freeze` and `census_p8_closeout_no_mutation` protected hash checks.
* Package path membership classification could drift into package-readiness claims. Mitigation: package probing, package mutation, and package readiness are out of scope.

### Compatibility Risk

* Low direct compatibility risk because no public API or runtime behavior changes are planned.
* Tooling risk exists if new tests are accidentally added to current-route closure without approval. Mitigation: no live manifest adoption in this plan.
* Git command behavior may differ on Windows paths. Mitigation: repo-relative normalized path identity and roundtrip checks.

### Regression Risk

* Existing current route may fail after new tooling if imports violate current closure. Mitigation: focused tests should avoid unallowlisted current-route imports and use subprocess / report validation where necessary.
* Output generation may dirty staging paths and confuse the census. Mitigation: `census_output_root ∩ required_artifact_paths = ∅` is asserted in `census_p1_denominator_lock`.
* Local dirty working tree may cause a `blocked` verdict only when it intersects required/protected surfaces. Mitigation: unrelated dirty paths are advisory and separated from required-surface blockers.
* `git check-ignore` warnings or user-level ignore permission issues can appear on this workstation. The tool must record query errors and fail-loud rather than treating warnings as pass.
* Tracked-but-rule-matching artifacts could be over-reported as ignored if `--no-index` output is consumed directly. Mitigation: `--no-index` populates only `ignore_rule_match`; verdict consumes `effectively_ignored`.
* Current-route validation can take more than two minutes and may create non-required staging drift. Mitigation: timeout budget is at least `360s`; required-surface census is rerun afterward; non-required staging drift is advisory unless it intersects required/protected surfaces.

---

## 10. Rollback Plan

Because this round is governance-only and should not mutate source / rendered / Lua bridge / runtime / package surfaces, rollback is limited to removing or reverting the round's own docs, tooling, tests, and staging output.

Rollback steps:

* Remove or revert `docs/dvf_3_3_required_artifact_surface_preflight_census_plan.md` if the plan itself is rejected.
* Remove or revert any future census tooling and focused tests created for this round.
* Discard generated staging output under `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/`.
* Do not restore, clean, unignore, add, delete, or regenerate the required artifacts as part of rollback.
* If protected source / rendered / Lua bridge / runtime / package surfaces changed, treat the round as invalid and revert only the offending round-introduced changes after identifying them.
* If live `current_route_required_validations.json` was modified without separate approval, revert that change and rerun current-route validation.

Dirty / ignored / untracked required artifact findings are not rollback targets by themselves. Applied remediation introduced by this round is rollback-relevant only if its disposition row is rejected or validation proves it unsafe.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Hub & Spoke boundary remains unchanged.
* Iris remains 100% Lua at runtime; new tooling is offline build/governance tooling only.
* Source / rendered / Lua bridge / runtime / package writer authority remains closed.
* Required-validation manifest field-pass is separate from VCS preservation.
* Tracking status is separate from artifact authority.
* Ignored status is not deletion approval.
* Dirty status is not sealable state.
* `local_provenance_hash` is not `canonical_candidate_hash` or `sealed_hash`.
* Live manifest `required_artifacts` denominator must be derived, not substituted.
* Durable bounded denominator and full live-manifest denominator must remain separate.
* Bounded/residual ignored split is report-only before disposition; it cannot override the need to disposition `effectively_ignored > 0` before final `ready`.
* `check-ignore --no-index` output is diagnostic-only and cannot be wired directly to verdict state.
* Tracked-but-rule-matched rows and untracked-ignored rows must remain separate buckets.
* Synthetic fail-closed predicate validation is mandatory standard validation.
* Current-route collection must not gain the focused census test without separate live manifest adoption; assertion strength depends on whether the route is manifest-based or glob-based.
* Census output root must remain disjoint from measured required artifact paths.
* Census output root must remain disjoint from the parent closure evidence root.
* Parent closure compatibility packet is predecessor provenance only, not parent PASS evidence.
* Artifact disposition state must be `performed`, `not_needed`, or `owner_pending`.
* `ready` requires post-resolution rerun evidence.
* Package probe must remain `false`; any package evidence is membership classification only.
* Existing sealed artifacts are read-only unless a separate approved plan reopens them.
* No broad staging root unignore.
* No current-route core module expansion.
* No current-route tooling allowlist expansion.
* No release / package / Workshop / B42 / deployment readiness claims.
* No independent review or owner seal self-generation.
* Minimal diff preservation and additive evidence preference apply.
* Dirty working tree changes not made by this round must not be reverted.

---

## 12. Expected Closeout State

Expected closeout target: `required_surface_preflight_resolution_state=ready`, `blocked`, or `owner_pending`.

`required_surface_preflight_resolution_state=ready` means:

* live manifest artifact universe was derived
* current expected denominator `93` was confirmed or mismatch was recorded
* all required artifacts received VCS tuples
* field-pass and VCS-state were joined but not conflated
* hash-candidate and non-hash-candidate partitions covered all artifacts
* dirty / effectively ignored / tracked / untracked / missing lists were emitted
* every blocker row received a disposition
* approved governance remediation was applied or no remediation was needed
* post-resolution rerun was performed
* post-resolution missing / dirty / invalid JSON / field mismatch / VCS query error / protected mutation counts are `0`
* post-resolution effectively ignored count is `0`, or every remaining tracked-rule-match row has accepted preservation disposition
* committed-surface fast path was used with `artifact_disposition_state=not_needed`, or disposition/remediation was performed and rerun-bound
* Durable `0` and full census residuals were reconciled by denominator scope
* protected no-mutation report passed
* synthetic fail-closed predicate matrix passed
* current-route collection isolation was verified
* `check_ignore_no_index_is_diagnostic_only=true` was recorded
* `artifact_disposition_state=performed` or `not_needed` was recorded
* `post_resolution_rerun_performed=true` was recorded
* `package_probe_performed=false` was recorded
* tracked-but-rule-matched and untracked-ignored blocker counts were separately reported
* semantic verdict was emitted as `ready`
* current-route regression validation PASS was recorded with timeout budget at least `360s`
* unrelated dirty paths, if present, were classified outside required/protected surfaces
* semantic verdict and `canonical_verdict_token=author_reserved/not_claimed` were recorded together
* `main_plan_compatibility_packet.json` was emitted
* `parent_phase0_entry_state` and `parent_phase5_vcs_surface_state` were recorded
* claim boundary states `required surface preflight resolved`

`required_surface_preflight_resolution_state=blocked` means the plan attempted disposition/remediation inside approved scope, but final post-resolution checks still failed or protected no-mutation was violated. It is a real unresolved state, not a successful final outcome.

`required_surface_preflight_resolution_state=owner_pending` means the blocker requires owner single-writer authority, source/rendered/runtime/package mutation, deletion, broad ignore-policy change, or another decision this plan cannot safely perform. It must include `unresolved_owner_disposition_queue.json` and cannot be reported as parent closure ready.
