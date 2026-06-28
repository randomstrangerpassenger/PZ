# Implementation Plan

> Status: planned / roadmap-derived / codebase-informed / previous-review-incorporated / governance-only guard hardening
> Date: 2026-06-29
> Roadmap input: `C:/Users/MW/.codex/attachments/7c015049-c06e-4541-9023-f31e7404fe58/pasted-text.txt` / sha256 `2A89009DCCFF20B6F37E64F4080279C87E4A209DE84F855CE18C331356B613D6`
> Review input: `C:/Users/MW/.codex/attachments/19b776da-d298-413f-82ca-3bbb54050ba9/pasted-text.txt` / sha256 `B93C6F15A45D75D2DFBAF93CDFFFFAFB2784A086A9CEAB331C75D87A27B3D4EB` / previous review disposition: WARN / incorporated
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Direct plan artifact: `docs/dvf_3_3_predecessor_stale_artifact_reentry_guard_plan.md`
> Candidate evidence root: `Iris/build/description/v2/staging/dvf_3_3_predecessor_stale_artifact_reentry_guard/`

---

## 1. Objective

DVF 3-3 Predecessor / Stale Artifact Reentry Guard를 실행하기 위한 계획을 정의한다. 이 계획의 목적은 stale bridge, old bridge, monolith side-output, predecessor fixture, rollback snapshot, historical staging evidence, diagnostic fixture 같은 predecessor / stale artifact를 삭제하는 것이 아니다.

목적은 이 artifact들이 다음 current authority surface로 다시 읽히지 못하게 하는 단일 fail-loud standing guard를 만드는 것이다.

* current source / rendered path
* runtime bridge / runtime fallback
* package staging / package zip / package output
* export output
* current-route required-validation manifest
* raw predecessor direct execution authority
* docs / closeout / release-readiness claim surface

이 계획은 existing Closeout / Reentry Guard Seal을 대체하지 않는다. 현재 코드베이스에는 `Iris/build/description/v2/tools/build/validate_dvf_3_3_predecessor_reentry_guard.py`, `dvf_3_3_closeout_reentry_guard_seal_common.py`, `docs/predecessor_reentry_guard_policy.md`, `docs/dvf_3_3_closeout_reentry_claim_boundary.md`가 이미 존재한다. 이 계획은 그 predecessor value guard를 artifact class / package / export / manifest / raw-read surface까지 확장하는 additive hardening round다.

이 계획의 최대 허용 claim은 다음이다.

```text
Predecessor / stale artifacts remain preserved as historical / diagnostic /
fixture / comparison / provenance trace, but cannot reenter current source,
rendered, runtime, package, export, required-validation, release-readiness,
or current-route authority surfaces.
```

이 계획의 완료는 source restoration, current authority cutover, rendered regeneration, Lua bridge export mutation, runtime chunk replacement, package payload mutation, live migration execution, package readiness, release readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game QA, semantic quality completion, public-facing text acceptance, independent-review PASS, or canonical seal을 의미하지 않는다.

Previous review disposition:

* Previous plan-level review verdict was `WARN`; this document incorporates that review.
* Execution readiness is conditional.
* R1-R3 are required before implementation execution begins:
  * artifact-universe denominator lock
  * adversarial negative fixture matrix
  * docs claim-scan scope / method pinning
* R4-R12 are PASS-blocking or strongly required before a machine PASS can be accepted:
  * package probe equivalence
  * `package_iris.ps1 -OutputRoot` / isolated-output mechanism validation
  * current-route tooling allowlist impact
  * classification precedence
  * manifest adoption sequencing
  * dual-guard responsibility split
  * stale-bridge independent-review linkage
  * `unknown_blocked` success policy
  * conservative final report field naming
* Independent-review gate remains `pending` or `BLOCKED` until an external non-author review artifact exists.
* Phase 0 / Phase 1 are go/no-go preflight gates, not optional implementation warm-up.
* Guard implementation, current-route adoption, package probe PASS, and final machine PASS cannot proceed unless the preflight records `go_no_go_decision=GO`.
* Final validation must re-read every phase artifact that carries `go_no_go_decision` or `preflight_go_no_go_decision` and prove all such values are consistent. A single GO report is not sufficient for PASS.

---

## 2. Scope

포함 범위:

* predecessor / stale artifact class inventory
* go/no-go preflight for denominator lock feasibility and docs claim-scan rule quality
* deterministic artifact-universe denominator lock
* artifact disposition taxonomy
* artifact class x reentry surface matrix
* current-looking classification precedence contract
* current-looking path guard
* stale bridge / old 6-entry bridge / monolith / rollback snapshot / predecessor fixture reentry guard
* package and package-zip forbidden artifact scan
* package probe equivalence report
* export route guard
* current-route required-validation manifest reentry guard
* raw predecessor direct authority read guard
* docs / claim surface overclaim scan with pinned scope and deterministic negation / role-qualified rules
* protected source / rendered / Lua bridge / runtime / package no-mutation proof
* additive current-route required-validation adoption plan
* current-route tooling allowlist impact report
* manifest adoption sequencing / self-reference cycle check
* focused runner / validator / unittest plan
* dual-guard responsibility split between existing value/denominator guard and new artifact-class guard
* stale-bridge independent-review linkage report
* final evidence packet, review input, claim boundary, ledger packet plan

Codebase readpoint used by this plan:

* `Iris/tools/package_iris.ps1` already fails on `IrisLayer3Data.lua` monolith source output, stale `IrisDvfBridgeData.lua`, and legacy 6-entry DVF bridge payload shape.
* `Iris/tools/package_iris.ps1` exposes `-OutputRoot`, so package probes can use the real package script against an isolated output root.
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua` and `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/` are the current runtime chunk authority surface.
* `fd IrisDvfBridgeData.lua Iris -H` returns no current checkout file at this readpoint.
* `Iris/build/description/v2/tools/build/consumer_universe_denominator_lock_common.py` already contains a denominator registry / fingerprint / row identity pattern that this round should adapt instead of inventing a separate denominator model.
* `Iris/build/description/v2/tools/build/run_dvf_3_3_durable_current_authority_surface_alignment.py` already contains artifact classification, required-manifest classification, and tooling allowlist impact patterns that this round should reuse where applicable.
* `Iris/build/description/v2/tools/build/dvf_3_3_closeout_reentry_guard_seal_common.py` already contains claim-context and negation classification helpers; docs claim scan should extend or reuse those helpers before introducing new text rules.
* `Iris/build/description/v2/staging/` contains rollback, predecessor snapshot, sandbox mirror, historical side-output, bridge, and chunk evidence roots that must be classified rather than deleted.
* `Iris/_docs/round3/current_route_required_validations.json` is the current required-validation manifest and already contains governance-only non-claims.
* Existing closeout/reentry guard artifacts live under `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/`.

### Explicitly Out Of Scope

* predecessor / stale artifact deletion
* broad staging unignore
* source facts mutation
* decisions mutation
* overlay support mutation
* rendered output regeneration
* Lua bridge live export mutation
* runtime chunk replacement
* live runtime apply
* package payload mutation
* current authority cutover reopen
* terminal disposition re-adjudication
* denominator redefinition
* full historical byte reproducibility
* clean-checkout required-evidence reproducibility
* semantic quality improvement
* public-facing text acceptance
* manual in-game QA
* release / package / Workshop / B42 / deployment readiness declaration
* current core or tooling allowlist expansion beyond reviewed additive guard tooling
* direct edits to user-facing Iris Lua runtime behavior
* replacing existing Closeout / Reentry Guard Seal with a new owner route

---

## 3. Non-Goals

This plan does not attempt to solve:

* stale bridge fallback restoration
* monolith runtime authority restoration
* old 6-entry fixture cleanup completion
* predecessor source restoration
* frozen `2105` byte-level recovery
* `2105 / 2084 / 21` denominator reinterpretation
* current runtime equivalence proof
* complete package release validation
* external mod compatibility sweep
* all legacy string removal
* old `active / silent` historical text rewrite
* runtime-side repair, compose rewrite, or adapter fallback
* semantic quality acceptance or public text quality review
* independent review verdict generation by the same machine guard
* canonical seal without owner / independent review records

The plan also does not treat tracked status as authority status, or ignored status as deletion safety.

---

## 4. Assumptions

* `docs/Philosophy.md` remains the top authority.
* Iris remains a 100% Lua runtime display mod; source validation, semantic judgment, and authority decisions remain offline build/governance concerns.
* Runtime / build-time separation remains mandatory.
* Current source facts, decisions, overlay, rendered output, Lua bridge, runtime chunks, and package payload are protected surfaces.
* Current DVF 3-3 authority remains successor source / rendered / runtime chunk authority.
* Runtime deployable authority is chunk manifest plus chunk files, not monolith.
* Predecessor / stale artifacts can remain in historical, diagnostic, fixture, comparison, provenance, and review-input roles.
* Predecessor / stale artifacts cannot become current source, rendered, runtime, package, export, required-validation, release-readiness, current debt, or raw execution authority.
* Existing guard routes are authoritative inputs, not rewrite targets.
* New guard evidence is additive and does not weaken existing required artifacts or tests.
* `Iris/_docs/round3/current_route_required_validations.json` may receive additive governance gate entries only after manifest adoption validation.
* Required-validation manifest adoption is a governance gate, not a writer capability.
* Package route validation must avoid mutating the existing `Iris/build/package` payload unless a later owner-approved execution plan explicitly permits it. Isolated package output under the evidence root is the default for this round.
* Package probe must use `Iris/tools/package_iris.ps1 -OutputRoot` or an explicitly equivalent isolated-output mechanism. If neither is available, package probe validation is blocked rather than passed.
* Phase 0 / Phase 1 preflight must prove that existing Iris patterns can support this guard before implementation continues. If denominator lock reuse, claim-scan sample adjudication, package isolated-output support, or durable-surface classification reuse cannot be confirmed, the round closes as `plan_revision_required_before_guard_implementation` instead of attempting a weaker guard.
* Artifact-universe denominator lock should adapt the registry / fingerprint / row identity approach from `consumer_universe_denominator_lock_common.py`. If that pattern cannot represent this artifact universe without turning coverage into "found rows only", implementation is blocked.
* Artifact-universe denominator id, membership, count, and lifecycle axis must remain distinct from consumer-universe denominators such as `1062`. This round reuses only the denominator mechanism, not consumer-universe membership, count, id, or authority axis.
* Artifact-universe coverage can be claimed only against a locked denominator id generated from deterministic glob/path contracts or an enumerated artifact-id set.
* `unknown_blocked` is not a successful coverage substitute. Machine PASS requires `unknown_blocked_count=0` unless an owner-approved disposition override is recorded before final report.
* Owner-approved disposition override must be auditable and hash-bound. The final report must include `owner`, `reason`, `artifact_id`, `requested_disposition`, `approved_disposition`, `why_not_current_authority`, `permanence_or_expiry`, `approval_artifact_path`, and `approval_artifact_sha256` for every override.
* Docs claim scan adopts Option A from review: pinned scan scope plus deterministic negation / role-qualified classification rules. If that scope/method cannot be pinned, docs claim scan is downgraded to advisory and the round cannot claim machine PASS.
* Docs claim scan must pass a preflight sample adjudication set before it becomes a hard gate. The sample set must include at least 24 sample fixtures, at least four fixtures per required category, and no false positives or false negatives.
* Required-manifest classification and current-route tooling allowlist impact should adapt the patterns in `run_dvf_3_3_durable_current_authority_surface_alignment.py` so this guard does not create a second, incompatible interpretation of current-route authority.
* Classification conflicts are resolved by conservative precedence. Protected current allowlist exact match is checked first, but any deny-rule or payload-marker conflict after allowlist resolution wins over historical / diagnostic / fixture disposition.
* Existing predecessor reentry guard owns value / denominator-axis claims. This new guard owns artifact-class / path / package / export / manifest / raw-read-axis claims. Overlap must be assigned to exactly one authoritative axis.
* Stale-bridge independent review is carried separately by default. This round may prepare review input, but it does not close a prior stale-bridge `review_pending` gate unless an external non-roadmap-author review artifact explicitly binds that gate.
* `review_input_only_non_authority` must remain the disposition spelling through intermediate artifacts and final reports. It must not be shortened to `review_input_only`.
* Machine PASS, independent review PASS, owner seal, and canonical seal are separate axes.
* Validation depth is set to heavy for governance / artifact / package / manifest / no-mutation surfaces, while runtime QA remains out of scope.
* Authority surface wording for this round is `governance boundary additive impact only`; no new source, rendered, runtime, package, or release authority is created.
* Canonical round id, final vocabulary token, final independent-review verdict, and final canonical seal state remain owner-reserved until execution evidence exists.

---

## 5. Repository Areas Affected

### Code

Candidate new offline tooling:

* `Iris/build/description/v2/tools/build/run_dvf_3_3_predecessor_stale_artifact_reentry_guard.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_predecessor_stale_artifact_reentry_guard.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_predecessor_stale_artifact_reentry_guard_common.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_predecessor_stale_artifact_reentry_guard.py`

Existing offline tooling to reuse or reference:

* `Iris/build/description/v2/tools/build/validate_dvf_3_3_predecessor_reentry_guard.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_closeout_reentry_guard_seal_common.py`
* `Iris/build/description/v2/tools/build/consumer_universe_denominator_lock_common.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_durable_current_authority_surface_alignment.py`
* `Iris/build/description/v2/tools/build/guard_dvf_3_3_vnext_output_paths.py`
* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/build/description/v2/tools/build/manage_dvf_3_3_runtime_chunk_cutover.py`
* `Iris/tools/package_iris.ps1`
* `Iris/_docs/round3/round3_run_contract_tests.py`

No runtime Lua code is planned for mutation.

### Docs

Direct plan artifact:

* `docs/dvf_3_3_predecessor_stale_artifact_reentry_guard_plan.md`

Candidate execution docs:

* `docs/dvf_3_3_predecessor_stale_artifact_reentry_guard_claim_boundary.md`
* `docs/dvf_3_3_predecessor_stale_artifact_reentry_guard_ledger_packet.md`
* `docs/dvf_3_3_predecessor_stale_artifact_reentry_policy.md`

Existing docs to consume as read-only or additive references:

* `docs/predecessor_reentry_guard_policy.md`
* `docs/dvf_3_3_closeout_reentry_claim_boundary.md`
* `docs/dvf_3_3_closeout_reentry_ledger_packet.md`
* `docs/dvf_3_3_closeout_reentry_guard_seal_plan.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Canonical docs may be updated only by a later execution step as additive current-readpoint synchronization. This plan-writing task does not update them.

### Config

Candidate governance config:

* `Iris/_docs/round3/current_route_required_validations.json`

This file may receive additive required artifacts/tests only during implementation. Existing entries must not be removed, weakened, or silently rewritten.

### Generated Artifacts

Candidate evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_predecessor_stale_artifact_reentry_guard/`

Expected artifact families:

* `phase0/scope_lock_report.json`
* `phase0/protected_surface_baseline.json`
* `phase0/go_no_go_preflight_report.json`
* `phase0/existing_pattern_reuse_report.json`
* `phase1/artifact_universe_denominator_lock.json`
* `phase1/artifact_universe_path_contract.json`
* `phase1/denominator_pattern_reuse_report.json`
* `phase1/predecessor_stale_artifact_inventory.jsonl`
* `phase1/artifact_disposition_taxonomy.json`
* `phase1/predecessor_stale_reentry_matrix.json`
* `phase1/artifact_disposition_coverage_report.json`
* `phase1/docs_claim_scan_sample_fixtures_manifest.json`
* `phase1/docs_claim_scan_sample_adjudication_report.json`
* `phase1/preflight_exit_decision.json`
* `phase2/unified_standing_guard_contract.json`
* `phase2/classification_precedence_report.json`
* `phase2/dual_guard_responsibility_split_report.json`
* `phase2/additive_invariant_report.json`
* `phase2/required_manifest_contract_report.json`
* `phase3/adversarial_negative_fixture_contract.json`
* `phase3/current_looking_path_guard_report.json`
* `phase3/stale_bridge_reentry_report.json`
* `phase3/monolith_reentry_report.json`
* `phase3/predecessor_fixture_reentry_report.json`
* `phase3/package_forbidden_artifact_scan_report.json`
* `phase3/package_guard_report.json`
* `phase3/export_route_guard_report.json`
* `phase3/protected_surface_no_mutation_report.json`
* `phase4/required_manifest_reentry_report.json`
* `phase4/raw_predecessor_direct_read_report.json`
* `phase4/no_dual_authority_read_report.json`
* `phase4/docs_claim_scan_scope_contract.json`
* `phase4/docs_claim_negation_role_qualification_rules.json`
* `phase4/claim_surface_scan_report.json`
* `phase4/manifest_adoption_sequence_report.json`
* `phase4/manifest_adoption_report.json`
* `phase5/current_route_validation_result.json`
* `phase5/negative_fixture_matrix_report.json`
* `phase5/go_no_go_phase_consistency_report.json`
* `phase5/package_predicate_extraction_report.json`
* `phase5/package_probe_equivalence_report.json`
* `phase5/package_route_validation_result.json`
* `phase5/current_route_tooling_allowlist_impact_report.json`
* `phase5/vcs_guard_validation_result.json`
* `phase6/final_predecessor_stale_artifact_reentry_guard_report.json`
* `phase6/primary_review_artifact_manifest.json`
* `phase6/independent_review_input.json`
* `phase6/stale_bridge_ir_linkage_report.json`
* `phase6/artifact_hash_report.json`
* `phase6/final_go_no_go_phase_consistency_report.json`

---

## 6. Planned Changes

### Change 0 - Scope Lock / Go-No-Go Preflight / Protected Surface Baseline

Purpose:

Fix this round as governance-only reentry guard hardening. Record protected surfaces and run a go/no-go preflight before any guard implementation, current-route adoption, package probe PASS, or final machine PASS path is attempted.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_predecessor_stale_artifact_reentry_guard/phase0/scope_lock_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_predecessor_stale_artifact_reentry_guard/phase0/protected_surface_baseline.json`
* `Iris/build/description/v2/staging/dvf_3_3_predecessor_stale_artifact_reentry_guard/phase0/go_no_go_preflight_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_predecessor_stale_artifact_reentry_guard/phase0/existing_pattern_reuse_report.json`
* `docs/dvf_3_3_predecessor_stale_artifact_reentry_guard_claim_boundary.md`

Implementation Notes:

* Bind this plan and the roadmap input into a stable phase0 record.
* Reuse protected surface concepts from `dvf_3_3_closeout_reentry_guard_seal_common.py`.
* Confirm that denominator locking can reuse or adapt `consumer_universe_denominator_lock_common.py` without reducing coverage to discovered rows only.
* Confirm that artifact classification, required-manifest classification, and current-route tooling allowlist impact can reuse or adapt `run_dvf_3_3_durable_current_authority_surface_alignment.py`.
* Confirm that docs claim scan can reuse or extend `dvf_3_3_closeout_reentry_guard_seal_common.py` claim-context / negation classification helpers.
* Confirm that `Iris/tools/package_iris.ps1 -OutputRoot` remains available for isolated package probing.
* Record `go_no_go_decision`.
* Treat phase0 `go_no_go_decision=GO` as a necessary but not sufficient implementation gate. Final validation must later compare it against every other phase artifact that records a GO/NO_GO decision.
* If any preflight item fails, stop before guard implementation and close as `plan_revision_required_before_guard_implementation`.
* Include current source facts, decisions, overlay support, rendered output, live chunk manifest, live chunk directory, stale bridge surface if present, and package peer output as protected surfaces.
* Record `authority_surface = governance_boundary_additive_impact_only`.
* Record `runtime_behavior_surface = none`.
* Record `package_payload_mutation_allowed = false`.

Validation:

* Scope lock exists.
* Go/no-go preflight report exists.
* Existing pattern reuse report exists.
* `denominator_pattern_reuse_status=usable`.
* `claim_scan_helper_reuse_status=usable`.
* `durable_surface_alignment_pattern_reuse_status=usable`.
* `package_output_root_probe_status=usable`.
* `go_no_go_decision=GO` before Change 1 implementation proceeds.
* Phase0 GO is marked as subject to final cross-phase consistency validation.
* Protected baseline exists.
* Protected baseline has deterministic path records.
* Mutation count is `0` at phase0.
* Claim boundary contains all non-claims.

---

### Change 1 - Artifact Inventory / Disposition Taxonomy / Reentry Matrix

Purpose:

Classify predecessor, stale, rollback, historical, diagnostic, and fixture artifacts by role before writing any guard assertion.

Files:

* `phase1/artifact_universe_denominator_lock.json`
* `phase1/artifact_universe_path_contract.json`
* `phase1/denominator_pattern_reuse_report.json`
* `phase1/predecessor_stale_artifact_inventory.jsonl`
* `phase1/artifact_disposition_taxonomy.json`
* `phase1/predecessor_stale_reentry_matrix.json`
* `phase1/artifact_disposition_coverage_report.json`
* `phase1/docs_claim_scan_sample_fixtures_manifest.json`
* `phase1/docs_claim_scan_sample_adjudication_report.json`
* `phase1/preflight_exit_decision.json`
* `Iris/build/description/v2/tests/fixtures/dvf_3_3_predecessor_stale_artifact_reentry_guard/docs_claim_scan_samples/`
* `docs/dvf_3_3_predecessor_stale_artifact_reentry_policy.md`

Implementation Notes:

Change 1 remains preflight until denominator lock and docs claim-scan sample adjudication both pass. It does not authorize guard implementation by itself.

Before any coverage claim, create a deterministic denominator lock. The lock must contain:

* `denominator_id`
* `generated_from`
* deterministic glob/path contract or enumerated artifact-id list
* `denominator_axis=predecessor_stale_artifact_universe`
* `mechanism_reuse_only=true`
* `consumer_universe_denominator_id_reused=false`
* `consumer_universe_membership_reused=false`
* `consumer_universe_count_reused=false`
* normalized row keys
* included roots
* excluded roots
* exclusion reasons
* denominator row count
* sha256 of the normalized denominator payload
* source pattern reference to `consumer_universe_denominator_lock_common.py` or explicit explanation for any intentionally different field

Coverage must be computed only against this locked denominator. Discovered rows outside the denominator must be classified as denominator drift and block PASS until the denominator lock is intentionally regenerated.

The denominator lock must adapt the existing denominator registry / fingerprint / row identity pattern used by `consumer_universe_denominator_lock_common.py`. If the predecessor/stale artifact universe cannot be represented as deterministic path contracts or enumerated artifact ids, the phase closes as `blocked_denominator_pattern_unusable`.

The artifact-universe denominator must be explicitly distinct from consumer-universe denominator ids and counts. In particular, this round must not substitute or inherit the `1062` consumer universe denominator, its membership, or any consumer lifecycle axis. Reuse of `consumer_universe_denominator_lock_common.py` is mechanism reuse only.

Inventory must include these artifact classes:

* predecessor fixture
* old 6-entry bridge
* stale bridge
* rollback snapshot / rollback residue
* historical staging evidence
* diagnostic fixture
* monolith historical / diagnostic side-output
* old package-adjacent path
* current-looking predecessor path

Known repository candidates to scan include:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_cutover/phase0/rollback_snapshot_payload/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase2/predecessor_snapshot_payload/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase2/restore_probe_snapshot_payload/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase3/sandbox_baseline/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase3/sandbox_after/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase5/`
* `Iris/build/description/v2/staging/lua_bridge_export/`
* `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/`
* `Iris/build/package/`

Disposition taxonomy must allow historical preservation without current authority. Suggested dispositions:

* `historical_trace_only`
* `diagnostic_trace_only`
* `fixture_only`
* `comparison_only`
* `rollback_snapshot_only`
* `provenance_trace_only`
* `review_input_only_non_authority`
* `package_forbidden`
* `current_authority_forbidden`
* `unknown_blocked`

Disposition names must remain stable through final report. `artifact_disposition_taxonomy.json` is the enum source for every disposition field in inventory, matrix rows, review manifests, and final summaries. In particular, `review_input_only_non_authority` must be the enum member and `review_input_only` must not exist as an enum member, alias, or accepted synonym.

Docs claim-scan sample adjudication must run before docs claim scan becomes a hard gate. The sample set must include:

* negated forbidden claim
* historical / provenance role-qualified statement
* actual current-authority overclaim
* Korean negation / prohibition wording
* English negation / prohibition wording
* quoted prior claim that is not adopted as current authority

Docs claim-scan sample fixtures must live under `Iris/build/description/v2/tests/fixtures/dvf_3_3_predecessor_stale_artifact_reentry_guard/docs_claim_scan_samples/` and be listed in `phase1/docs_claim_scan_sample_fixtures_manifest.json`.

The minimum fixture set is `sample_fixture_count>=24`, with at least four fixtures for each required category. The sample adjudication must record fixture path, expected classification, actual classification, classifier source file, classifier source hash, false positive count, and false negative count. Any missing category, insufficient fixture count, false positive, or false negative blocks implementation as `blocked_claim_scan_sample_adjudication_failed`.

Artifact classification and required-manifest classification should reuse or adapt the relevant current-surface patterns in `run_dvf_3_3_durable_current_authority_surface_alignment.py`. If this adaptation would conflict with the current-route interpretation of source/runtime/package authority, the phase closes as `blocked_existing_pattern_reuse_missing`.

At the end of Change 1, write `preflight_exit_decision.json` with `go_no_go_decision=GO` only if denominator lock, sample adjudication, and existing-pattern reuse all pass. Otherwise write `go_no_go_decision=NO_GO` and close as a plan revision state.

Validation:

* Inventory schema validation PASS.
* Denominator lock validation PASS.
* Denominator pattern reuse validation PASS.
* Denominator axis distinctness validation PASS.
* Denominator row-key coverage is 100 percent.
* Final report records the denominator id.
* Every inventory row has exactly one disposition.
* Matrix coverage is 100 percent for artifact class x reentry surface.
* Unknown or ambiguous rows are `0`.
* `unknown_blocked_count=0` for machine PASS. Any nonzero unknown count closes as `blocked_unknown_artifact` unless owner-approved disposition override exists.
* Every owner-approved disposition override is hash-bound and includes owner, reason, artifact id, approved disposition, why-not-current-authority explanation, and permanence/expiry.
* Taxonomy enum validation PASS for every disposition field.
* Bare `review_input_only` disposition count is `0`.
* Docs claim-scan sample fixture count is at least `24`.
* Docs claim-scan sample category coverage is at least four fixtures per required category.
* Docs claim-scan sample adjudication false positive count is `0`.
* Docs claim-scan sample adjudication false negative count is `0`.
* Preflight exit decision records `go_no_go_decision=GO`.
* No historical / diagnostic / fixture artifact has a current authority role.
* Protected surface mutation count remains `0`.

---

### Change 2 - Unified Standing Guard Contract

Purpose:

Define the single standing contract that maps every artifact class and reentry surface to an allow, deny, or blocked disposition.

Files:

* `phase2/unified_standing_guard_contract.json`
* `phase2/classification_precedence_report.json`
* `phase2/dual_guard_responsibility_split_report.json`
* `phase2/additive_invariant_report.json`
* `phase2/required_manifest_contract_report.json`
* `phase2/claim_boundary_draft.md`

Implementation Notes:

* The contract is additive. It must not replace `docs/predecessor_reentry_guard_policy.md` or the existing Closeout / Reentry Guard Seal.
* Current source / rendered / runtime / bridge / package / export / required-manifest allowlists must be explicit.
* Denylists must include stale bridge names, `IrisDvfBridgeData.lua`, monolith current paths, current-looking rollback paths, and old package-adjacent paths.
* Required-manifest reentry is a first-class guarded surface, not a side effect of docs scan.
* Count values such as `2105 / 2084 / 21`, fixture `6`, or rollback `2` may be used only by lifecycle role, not count equality.
* The final report must not be self-required before it exists. Avoid self-referential current-route recursion by requiring stable phase artifacts first, then final report only after the final artifact exists.
* Classification precedence must be encoded in `unified_standing_guard_contract.json` and validated separately:
  1. protected current authority allowlist exact match
  2. package/export deployable allowlist exact match
  3. current-looking path deny rule
  4. payload marker deny rule
  5. artifact role metadata
  6. historical / diagnostic / fixture disposition
  7. unknown -> `unknown_blocked`
* If path, payload marker, role metadata, and disposition conflict, the more conservative disposition wins.
* Dual-guard responsibility split must be explicit:
  * existing predecessor reentry guard: value / denominator-axis guard for `2105 / 2084 / 21`
  * new predecessor/stale artifact guard: artifact-class / path / package / export / manifest / raw-read-axis guard
  * overlap must name exactly one authoritative axis, with the other axis recorded as a non-owning reference.

Validation:

* Contract self-consistency PASS.
* Classification precedence validation PASS.
* Conservative conflict resolution fixture PASS.
* Dual-guard responsibility split validation PASS.
* Dual owning authority count is `0`.
* Existing required artifact removal count is `0`.
* Existing required test removal count is `0`.
* Existing required artifact/test weakening count is `0`.
* Required manifest contract report PASS.
* Claim boundary lint PASS.

---

### Change 3 - Current-Looking Path / Package / Export Guard

Purpose:

Prevent historical, diagnostic, fixture, rollback, or predecessor artifacts from occupying or being emitted through current-looking runtime/package/export paths.

Files:

* `phase3/adversarial_negative_fixture_contract.json`
* `phase3/current_looking_path_guard_report.json`
* `phase3/stale_bridge_reentry_report.json`
* `phase3/monolith_reentry_report.json`
* `phase3/predecessor_fixture_reentry_report.json`
* `phase3/package_forbidden_artifact_scan_report.json`
* `phase3/package_guard_report.json`
* `phase3/export_route_guard_report.json`
* `phase3/protected_surface_no_mutation_report.json`

Implementation Notes:

* Reuse the package rules in `Iris/tools/package_iris.ps1`: Layer3 monolith forbidden, stale DVF bridge filename/path forbidden, legacy 6-entry payload shape forbidden.
* Add artifact taxonomy awareness to package scan reports, so violations can point to artifact class and surface.
* Package validation should default to an isolated output root under the evidence directory rather than mutating `Iris/build/package/`.
* Because `Iris/tools/package_iris.ps1` already supports `-OutputRoot`, the package probe must call that script rather than reimplementing package copy/filter logic.
* Export route checks should confirm default export emits chunk authority only and does not create current/staging monolith output.
* Historical / diagnostic monolith route may remain side-output only if explicitly classified and package-forbidden.
* Current-looking path detection must not rely on filename alone. It must inspect normalized relative path, artifact class, intended role, and payload markers when a marker exists for that artifact class. Marker absence is recorded as `payload_marker_absent` and is not by itself a PASS.
* Negative fixture contract must include adversarial variants, not only known filenames:
  * payload-identical legacy 6-entry bridge with renamed filename
  * predecessor fixture relocated into current-looking path
  * predecessor fixture relocated into package path
  * predecessor fixture referenced from required manifest path
  * non-standard filename monolith payload variant
  * role metadata conflict fixture
  * payload marker conflict fixture

Validation:

* Adversarial negative fixture contract validation PASS.
* Renamed payload-identical legacy bridge fails closed.
* Relocated predecessor fixture fails closed in current-looking, package, and manifest surfaces.
* Non-standard filename monolith payload variant fails closed.
* Role metadata conflict fixture fails closed.
* Payload marker conflict fixture fails closed.
* Current-looking path violation count is `0`.
* Stale bridge current path violation count is `0`.
* Monolith current path violation count is `0`.
* Predecessor fixture current path violation count is `0`.
* Rollback snapshot current path violation count is `0`.
* Package forbidden hit count is `0`.
* Package zip forbidden hit count is `0`.
* Default export route does not generate current/staging monolith.
* Protected source / rendered / runtime / package mutation count is `0`.

---

### Change 4 - Required Manifest / Raw Authority Read / Claim Guard

Purpose:

Block predecessor / stale artifacts from becoming current-route required evidence, raw execution authority, or release-readiness support.

Files:

* `phase4/required_manifest_reentry_report.json`
* `phase4/raw_predecessor_direct_read_report.json`
* `phase4/no_dual_authority_read_report.json`
* `phase4/docs_claim_scan_scope_contract.json`
* `phase4/docs_claim_negation_role_qualification_rules.json`
* `phase4/claim_surface_scan_report.json`
* `phase4/manifest_adoption_sequence_report.json`
* `phase4/manifest_adoption_report.json`

Implementation Notes:

* Scan `Iris/_docs/round3/current_route_required_validations.json` as structured JSON, not substring-only text.
* Distinguish review evidence artifact, historical provenance artifact, and current-required execution artifact.
* Raw predecessor direct-read means a tool, validator, package script, or required manifest reads predecessor / stale artifact as execution authority rather than comparison or provenance.
* Docs claim scan uses Option A from review: hard gate with pinned scope and deterministic method.
* Docs claim scan may become a hard gate only after `phase1/docs_claim_scan_sample_adjudication_report.json` records zero false positives and zero false negatives.
* `docs_claim_scan_scope_contract.json` must list included files, excluded files, required doc families, exclusion reasons, and scan scope hash.
* `docs_claim_negation_role_qualification_rules.json` must define deterministic handling for:
  * Korean negation and prohibition phrases
  * English negation and prohibition phrases
  * role-qualified historical / diagnostic / fixture text
  * quoted prior claims
  * non-claim lists
  * claim-boundary statements
* Docs claim scan must block unnegated statements that turn predecessor / stale artifacts into current authority, current debt, package readiness, release readiness, or package authority.
* Historical explanation text remains allowed only when negated or explicitly role-qualified by the pinned rule set.
* If claim-scan scope or method cannot be pinned, the docs claim scan becomes advisory and machine PASS is blocked as `blocked_claim_scan_method_unpinned`.
* If claim-scan sample adjudication fails, the docs claim scan remains advisory and machine PASS is blocked as `blocked_claim_scan_sample_adjudication_failed`.
* Manifest adoption sequencing must be machine-readable:
  * stable pre-final artifacts/tests may be adopted first
  * final report can be required only after materialization
  * self-reference cycles are forbidden
  * existing entries cannot be removed or weakened

Validation:

* Required manifest predecessor reentry count is `0`.
* Raw predecessor direct authority read count is `0`.
* Dual authority read count is `0`.
* Docs claim scan scope contract validation PASS.
* Docs claim negation / role-qualified rule validation PASS.
* Docs claim-scan sample adjudication PASS before hard-gate enforcement.
* Docs claim violation count is `0`.
* Manifest adoption sequencing validation PASS.
* `pre_final_required_artifacts_adopted=true`.
* `pre_final_required_tests_adopted=true`.
* `final_report_required_only_after_materialized=true`.
* `self_reference_cycle_detected=false`.
* Required manifest mutation is additive only.
* Existing required artifacts/tests removed or weakened count is `0`.
* Protected surface mutation count is `0`.

---

### Change 5 - Current Route Integration / Focused Tests

Purpose:

Connect stable guard artifacts to the current-route validation chain without opening writer authority.

Files:

* `Iris/build/description/v2/tools/build/run_dvf_3_3_predecessor_stale_artifact_reentry_guard.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_predecessor_stale_artifact_reentry_guard.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_predecessor_stale_artifact_reentry_guard_common.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_predecessor_stale_artifact_reentry_guard.py`
* `phase5/current_route_validation_result.json`
* `phase5/negative_fixture_matrix_report.json`
* `phase5/go_no_go_phase_consistency_report.json`
* `phase5/package_predicate_extraction_report.json`
* `phase5/package_probe_equivalence_report.json`
* `phase5/package_route_validation_result.json`
* `phase5/current_route_tooling_allowlist_impact_report.json`
* `phase5/vcs_guard_validation_result.json`

Implementation Notes:

* Current-route integration cannot start unless `phase1/preflight_exit_decision.json` records `go_no_go_decision=GO`.
* The focused validator must produce `phase5/go_no_go_phase_consistency_report.json` as a pre-final scan of every materialized pre-final phase artifact that contains `go_no_go_decision` or `preflight_go_no_go_decision`. PASS requires all discovered values to be `GO`, no conflicting `NO_GO`, no stale GO after a later blocked phase, and `go_no_go_phase_drift_count=0`.
* Follow the existing runner / validator / unittest pattern used by `run_dvf_3_3_closeout_reentry_guard_seal.py`, `validate_dvf_3_3_predecessor_reentry_guard.py`, and `test_dvf_3_3_closeout_reentry_guard_seal.py`.
* Negative fixtures must prove fail-closed behavior for stale bridge current path, renamed old bridge payload, old bridge package path, monolith export, non-standard monolith filename, rollback snapshot package inclusion, relocated predecessor fixture, predecessor fixture required-manifest use, payload marker conflict, role metadata conflict, and raw predecessor execution authority.
* Current-route required-validation adoption must add stable required artifacts/tests only after focused validation passes.
* Current-route test count increase is not a release or completion claim by itself.
* If adoption would require adding a tooling module to the current-route tooling allowlist, that allowlist expansion must be separately reviewed and cannot be hidden inside this guard.
* `package_predicate_extraction_report.json` must be generated before package probe equivalence is evaluated.
* `package_predicate_extraction_report.json` must record package script path, package script hash, extraction command, extraction command hash, logical predicate ids, predicate source paths, line or AST spans, normalized predicate text or expression hash, and extraction coverage.
* If package predicates are distributed across `Iris/tools/package_iris.ps1`, the extraction report is the authority for `predicate_source_paths` and `predicate_source_sha256` used by `package_probe_equivalence_report.json`.
* `package_probe_equivalence_report.json` must include:
  * `package_script_path`
  * `package_script_sha256`
  * `probe_command`
  * `probe_command_sha256`
  * `input_root_identity`
  * `output_root_isolated=true`
  * `same_forbidden_predicates_as_package_iris=true`
  * `same_forbidden_predicates_evidence`
  * `predicate_source_paths`
  * `predicate_source_sha256`
  * `zip_scan_executed=true`
  * `live_package_payload_mutated=false`
  * `probe_vs_real_route_drift_count=0`
* `same_forbidden_predicates_as_package_iris=true` must be derived from the recorded script hash and predicate source hash, not written as an unsupported assertion.
* If predicate extraction is missing, ambiguous, or has incomplete extraction coverage, close as `blocked_package_predicate_extraction_missing` before accepting package probe equivalence.
* Package probe must verify `-OutputRoot` support on `Iris/tools/package_iris.ps1`. If unsupported, it must use a read-only dry-scan fallback or close as blocked; it must not mutate `Iris/build/package/`.
* `current_route_tooling_allowlist_impact_report.json` must include:
  * `new_tooling_modules`
  * `current_route_import_required`
  * `allowlist_expansion_required`
  * `allowlist_expansion_review_status`
  * `current_core_module_count_changed=false`
  * `tooling_allowlist_cap_bypassed=false`
* If allowlist expansion is required and not separately reviewed, close as `blocked_tooling_allowlist_review_required`.

Validation:

* Preflight exit decision exists and records `go_no_go_decision=GO`.
* Go/no-go phase consistency validation PASS.
* `go_no_go_phase_drift_count=0`.
* Focused runner PASS.
* Focused validator PASS.
* Focused unittest PASS.
* Negative fixtures fail-closed PASS.
* Adversarial negative fixture variants PASS.
* Package probe equivalence PASS.
* Package predicate extraction report PASS.
* Package probe command, script hash, predicate source hash, and equivalence evidence are present.
* `package_iris.ps1 -OutputRoot` support confirmed, or fallback blocked state recorded.
* Full current-route validation PASS with closure enforced.
* Package route validation PASS in isolated output.
* Current-route tooling allowlist impact validation PASS.
* `allowlist_expansion_required=false`, or reviewed expansion status is present before PASS.
* VCS guard PASS.
* Protected surface no-mutation PASS.

---

### Change 6 - Final Evidence / Review Packet / Ledger Packet

Purpose:

Emit a governance-only final bundle that records machine PASS, no-mutation proof, review input, and claim boundary without overclaiming canonical seal or release readiness.

Files:

* `phase6/final_predecessor_stale_artifact_reentry_guard_report.json`
* `phase6/primary_review_artifact_manifest.json`
* `phase6/independent_review_input.json`
* `phase6/stale_bridge_ir_linkage_report.json`
* `phase6/artifact_hash_report.json`
* `phase6/final_go_no_go_phase_consistency_report.json`
* `docs/dvf_3_3_predecessor_stale_artifact_reentry_guard_ledger_packet.md`
* `docs/dvf_3_3_predecessor_stale_artifact_reentry_guard_claim_boundary.md`

Implementation Notes:

* Final report must include inventory coverage, matrix coverage, guard status, manifest status, package status, export status, raw-read status, no-mutation status, and non-claims.
* Final report must include preflight status, GO phase consistency status, denominator pattern reuse status, denominator axis distinctness status, docs claim-scan sample adjudication status, taxonomy enum status, package predicate extraction status, and existing-pattern reuse status.
* `phase6/final_go_no_go_phase_consistency_report.json` must be generated by the final validator after all phase artifacts except that consistency report itself are materialized. It must scan every phase artifact that carries `go_no_go_decision` or `preflight_go_no_go_decision`, including the final report draft, and final report acceptance requires the final report GO fields to match the consistency report.
* Final report must use conservative field names:
  * `machine_contract_status`
  * `governance_guard_only=true`
  * `preflight_go_no_go_decision=GO`
  * `go_no_go_phase_consistency_status=PASS`
  * `go_no_go_phase_drift_count=0`
  * `denominator_pattern_reuse_status=usable`
  * `denominator_axis_distinct_from_consumer_universe=true`
  * `docs_claim_scan_sample_adjudication_status=PASS`
  * `docs_claim_scan_sample_fixture_count`
  * `taxonomy_enum_validation_status=PASS`
  * `package_predicate_extraction_status=PASS`
  * `existing_pattern_reuse_status=PASS`
  * `source_authority_mutated=false`
  * `runtime_authority_mutated=false`
  * `package_authority_mutated=false`
  * `release_readiness_claimed=false`
  * `canonical_seal_claimed=false`
  * `independent_review_status=pending_or_external`
  * `review_input_disposition_name=review_input_only_non_authority`
  * `bare_review_input_only_disposition_count=0`
  * `manual_override_used`
  * `owner_approved_disposition_override_count`
* Final report must include an `owner_approved_disposition_overrides` array. Each row must include `owner`, `reason`, `artifact_id`, `requested_disposition`, `approved_disposition`, `why_not_current_authority`, `permanence_or_expiry`, `approval_artifact_path`, and `approval_artifact_sha256`.
* If no overrides exist, final report must explicitly record `owner_approved_disposition_override_count=0` and `manual_override_used=false`.
* If any override exists, final report must explicitly record `manual_override_used=true`, `owner_approved_disposition_override_count>0`, and the complete hash-bound override rows.
* Independent review input must be prepared even if independent review is pending.
* Machine PASS does not satisfy independent review.
* Owner seal and independent review must be separate fields.
* Canonical seal may be `blocked_independent_review_pending` or `blocked_owner_seal_pending` while machine contract PASS remains true.
* Independent review, if required, must be external and non-roadmap-author. A same-machine or roadmap-author review can be recorded as advisory but cannot close the independent-review gate.
* `stale_bridge_ir_linkage_report.json` must state whether prior stale-bridge `review_pending` is:
  * `separate_carry`
  * `subsumed_by_external_review`
  * `closed_by_external_review`
  * `not_applicable`
* Default is `separate_carry`. This round does not close a prior stale-bridge IR gate unless a bound external review artifact explicitly says so.
* ROADMAP / DECISIONS / ARCHITECTURE update proposals, if any, must be additive and must not rewrite sealed predecessor decisions.

Validation:

* Final report `machine_contract_status=PASS`.
* Final report `governance_guard_only=true`.
* Final report `preflight_go_no_go_decision=GO`.
* Final report `go_no_go_phase_consistency_status=PASS`.
* Final report `go_no_go_phase_drift_count=0`.
* Final GO phase consistency report scans all materialized phase artifacts except itself.
* Final report `denominator_pattern_reuse_status=usable`.
* Final report `denominator_axis_distinct_from_consumer_universe=true`.
* Final report `docs_claim_scan_sample_adjudication_status=PASS`.
* Final report records `docs_claim_scan_sample_fixture_count>=24`.
* Final report `taxonomy_enum_validation_status=PASS`.
* Final report `package_predicate_extraction_status=PASS`.
* Final report `existing_pattern_reuse_status=PASS`.
* Final report `source_authority_mutated=false`.
* Final report `runtime_authority_mutated=false`.
* Final report `package_authority_mutated=false`.
* Final report `release_readiness_claimed=false`.
* Final report `canonical_seal_claimed=false`.
* Final report keeps `review_input_only_non_authority` spelling and reports bare `review_input_only` count as `0`.
* Final report `manual_override_used=false` when override count is `0`, or `manual_override_used=true` when override count is greater than `0`.
* Owner-approved disposition override audit rows are complete and hash-bound, or override count is `0`.
* Current-looking predecessor path violation count is `0`.
* Package forbidden hit count is `0`.
* Required manifest reentry count is `0`.
* Raw predecessor direct authority read count is `0`.
* Protected surface mutation count is `0`.
* Existing required artifact/test removal count is `0`.
* Claim boundary validation PASS.
* Stale-bridge IR linkage validation PASS.
* Independent review verdict is recorded separately and is not inferred from machine PASS.

---

## 7. Validation Plan

### Automated Validation

Do not claim validation passed unless the exact relevant command exits with code `0`.

Expected focused command candidates:

```powershell
uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_predecessor_stale_artifact_reentry_guard.py --mode preflight --go-no-go
```

```powershell
uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_predecessor_stale_artifact_reentry_guard.py --mode all
```

```powershell
uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_predecessor_stale_artifact_reentry_guard.py --require-complete
```

```powershell
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_predecessor_stale_artifact_reentry_guard.py"
```

Expected integration command:

```powershell
uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
```

Expected package guard command should use isolated output by default:

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -OutputRoot .\Iris\build\description\v2\staging\dvf_3_3_predecessor_stale_artifact_reentry_guard\phase5\package_probe -Clean -Zip
```

Expected automated validation areas:

* go/no-go preflight validation
* go/no-go phase consistency validation
* existing Iris pattern reuse validation
* artifact-universe denominator lock validation
* denominator pattern reuse validation
* denominator axis distinctness validation
* artifact inventory schema
* locked denominator row-key coverage
* single disposition per artifact
* `unknown_blocked_count=0`
* owner-approved disposition override audit validation
* manual override flag validation
* taxonomy enum validation for all disposition fields
* `review_input_only_non_authority` enum validation
* artifact class x reentry surface matrix coverage
* classification precedence validation
* current-looking path guard
* stale bridge / old bridge / monolith / rollback reentry guard
* package forbidden artifact scan
* package zip forbidden artifact scan
* package predicate extraction validation
* package probe equivalence validation
* package probe command / script hash / predicate source hash validation
* export route guard
* required manifest structured scan
* manifest adoption sequencing validation
* raw predecessor direct authority read scan
* docs claim scan scope / method validation
* docs claim-scan sample fixture manifest validation
* docs claim-scan sample adjudication validation
* docs claim surface scan
* additive invariant validation
* current-route tooling allowlist impact validation
* focused runner / validator / unittest
* negative fixture fail-closed validation
* adversarial rename / relocate / payload-shape fixture validation
* current-route closure
* no-mutation proof
* artifact hash manifest
* stale-bridge IR linkage validation
* claim boundary validation

If `uv`, PowerShell package command, or the current-route runner is missing or exits non-zero, validation is blocked, not passed.

### Manual Validation

Manual validation is inspection-only:

* inspect go/no-go preflight report
* inspect go/no-go phase consistency report
* inspect existing Iris pattern reuse report
* inspect inventory false positives
* inspect denominator lock and excluded root reasons
* inspect denominator pattern reuse report
* inspect denominator axis distinctness and confirm consumer-universe id/count/membership are not reused
* inspect `unknown_blocked` rows
* inspect owner-approved disposition overrides if any unknown row exists
* inspect `manual_override_used` consistency with override count
* inspect override owner, reason, artifact id, disposition, why-not-current-authority, permanence/expiry, and hash binding
* inspect disposition taxonomy naming
* inspect taxonomy enum validation and confirm `review_input_only_non_authority` is an enum member while `review_input_only` is not accepted
* inspect classification precedence conflict examples
* inspect package-forbidden scan output
* inspect package predicate extraction report
* inspect package probe equivalence block
* inspect package probe command, script hash, and predicate source hash evidence
* inspect tooling allowlist impact report
* inspect required manifest adoption diff
* inspect manifest adoption sequencing report for self-reference cycles
* inspect raw-read scanner exclusions for comparison / provenance reads
* inspect docs claim scan scope and negation / role-qualified rules
* inspect docs claim-scan sample fixture manifest and minimum sample count
* inspect docs claim-scan sample adjudication false positives / false negatives
* inspect claim boundary for release / package readiness overclaim
* inspect stale-bridge IR linkage report
* inspect independent review input scope
* inspect final non-claim list

No in-game manual QA is planned.

### Validation Limits

This plan will not validate or claim:

* manual in-game validation
* long-session runtime validation
* multiplayer validation
* deployment validation
* Workshop validation
* release packaging readiness
* semantic quality validation
* public-facing text acceptance
* full runtime equivalence
* full compatibility preservation
* full historical byte reproducibility
* clean-checkout required-evidence reproducibility
* live migration execution
* source restoration
* rendered regeneration
* Lua bridge live export mutation
* runtime chunk replacement
* package payload mutation

---

## 8. Risk Surface Touch

### Authority Surface

Governance boundary additive impact only.

The plan adds a standing guard contract and potential required-validation governance gate. It does not create or mutate source authority, rendered authority, runtime authority, package authority, or release authority.

### Runtime Behavior Surface

None.

No Lua runtime, Browser, Wiki, Tooltip, renderer, bridge, or runtime chunk behavior is changed.

### Compatibility Surface

Low runtime risk / medium internal workflow risk.

Runtime compatibility should not change. Internal validation may become stricter and may fail earlier when historical artifacts appear in current-looking paths, package output, required manifests, or overclaiming docs.

### Sealed Artifact Surface

Additive only.

Existing sealed evidence and closeout documents are consumed as read-only inputs. New evidence is written under a new staging root.

### Public-Facing Output Surface

None.

No Workshop copy, release note, README release claim, UI text, Browser/Wiki/Tooltip text, or user-facing behavior is changed.

---

## 9. Risk Analysis

### Architecture Risk

* A governance guard may be mistaken for new runtime/package authority.
* Existing Closeout / Reentry Guard Seal and the new guard may become dual owning authorities if relation is not explicit.
* Required-validation manifest adoption may be overread as runtime writer adoption.
* Repeated GO fields may drift if final validation trusts only one report.
* Artifact-universe denominator may drift, making 100 percent coverage meaningless.
* Artifact-universe denominator may become "100 percent of discovered artifacts" if the denominator registry is not locked before scan results are interpreted.
* Artifact-universe denominator may be confused with consumer-universe denominators if mechanism reuse is mistaken for id/count/membership reuse.
* Artifact taxonomy may be too broad and classify legitimate current tooling output as stale.
* Artifact taxonomy may be too narrow and miss current-looking predecessor paths.
* Classification precedence may be implemented inconsistently if not validated against conflict fixtures.
* Existing value-axis predecessor guard and new artifact-axis guard may appear as dual current authorities.
* Canonical seal may be overclaimed from machine PASS without independent review.

### Runtime Risk

* Direct runtime risk should remain none.
* Risk appears only if implementation accidentally writes live runtime chunks, stale bridge files, source data, rendered output, or package payload.
* Any protected surface change blocks completion.

### Compatibility Risk

* Package guard hardening can fail existing packaging flow if a historical artifact has leaked into package input.
* Export route guard can expose old side-output assumptions.
* Required manifest scanner can flag historical evidence if artifact role metadata is incomplete.
* Docs claim scanner can create false positives around negated Korean or English policy language.
* Docs claim scanner can create false negatives if scope or role-qualified rules are not pinned.
* Docs claim scanner can become a judgment-quality risk rather than an implementation risk if sample adjudication is skipped.
* Docs claim scanner can still false-positive in the full corpus if the sample fixture set is too small or lacks category coverage.
* Tooling allowlist integration can become an unreviewed current-route surface expansion.

### Regression Risk

* Negative fixtures may prove only filename detection and miss payload-shape or path-normalized violations.
* Rename / relocate / payload-shape adversarial variants may pass if scanner degenerates to filename matching.
* Scanner implementation may rely on substring matching instead of structured JSON and path normalization.
* Required manifest adoption may accidentally remove or modify existing entries.
* Required manifest adoption may create a self-referential final-report cycle.
* Isolated package probe may drift from the real package route if it does not use `Iris/tools/package_iris.ps1`.
* Package probe can pass without representing the real route if equivalence fields are missing.
* Package predicate hashes can become ambiguous if distributed PowerShell predicate fragments are not extracted into a separate report.
* Current-route test count may be overclaimed as release readiness.

---

## 10. Rollback Plan

Rollback is governance artifact rollback, not runtime rollback.

Before current-route manifest adoption:

* remove candidate new runner / validator / common module / focused test
* archive or remove the new evidence root
* preserve predecessor / stale artifacts in their original roles
* preserve existing Closeout / Reentry Guard Seal artifacts

If Phase 0 / Phase 1 preflight fails:

* do not implement guard tooling beyond preflight evidence
* do not add current-route required-validation entries
* do not run package probe as PASS evidence
* preserve the failed preflight reports as diagnostic planning evidence
* close as `plan_revision_required_before_guard_implementation`

After current-route manifest adoption:

* remove only the additive `dvf_3_3_predecessor_stale_artifact_reentry_guard` required artifacts/tests from `Iris/_docs/round3/current_route_required_validations.json`
* do not modify or weaken pre-existing required-validation entries
* preserve failed evidence as historical / diagnostic trace
* record rollback in a ledger packet if execution had produced adopted artifacts

If protected source / rendered / Lua bridge / runtime / package mutation is detected:

* stop the round
* record changed paths and hashes in the no-mutation report
* revert accidental changes only with explicit approval if outside normal generated evidence
* close as `blocked_no_mutation_violation`

Rollback must not restore predecessor / stale artifacts as current authority, runtime fallback, package authority, or release-readiness evidence.

---

## 11. Governance Constraints

* Preserve `docs/Philosophy.md` compliance.
* Preserve Iris as 100% Lua runtime display surface.
* Preserve runtime / build-time separation.
* Preserve current successor source / rendered / runtime chunk authority.
* Do not mutate source facts, decisions, overlay, rendered output, Lua bridge, runtime chunks, or package payload.
* Do not revive monolith runtime authority.
* Do not revive stale bridge fallback.
* Do not treat historical / diagnostic / fixture trace as deletion target by default.
* Do not treat tracked status as authority.
* Do not treat ignored status as deletion safety.
* Maintain fail-loud behavior.
* Do not proceed past Phase 0 / Phase 1 unless preflight records `go_no_go_decision=GO`.
* Do not accept a single GO artifact as sufficient; final validation must prove GO consistency across all phase artifacts that carry GO/NO_GO fields.
* Treat failed denominator pattern reuse, failed claim-scan sample adjudication, or missing existing-pattern reuse as plan-revision triggers, not implementation warnings.
* Do not claim coverage without locked artifact-universe denominator.
* Do not reuse consumer-universe denominator id, membership, count, or lifecycle role for the predecessor/stale artifact universe.
* Keep `unknown_blocked_count=0` as the normal PASS requirement.
* Treat nonzero unknown rows as `blocked_unknown_artifact` unless owner-approved disposition override exists.
* Require every owner-approved disposition override to be auditable and hash-bound.
* Require `manual_override_used=true` whenever owner-approved disposition override count is greater than `0`.
* Validate disposition names through taxonomy enum membership, not string search alone.
* Preserve `review_input_only_non_authority` as the taxonomy enum member through final reports; never shorten it to `review_input_only`.
* Enforce classification precedence and conservative conflict resolution.
* Maintain additive-only manifest adoption.
* Split manifest adoption into pre-final stable artifact/test adoption and final-report adoption after materialization.
* Reject self-referential current-route cycles.
* Do not remove or weaken existing required artifacts/tests.
* Keep required-validation manifest entries as governance gates, not runtime writers.
* Keep current-route tooling allowlist impact explicit and reviewed.
* Keep count values axis-qualified by lifecycle role.
* Keep package PASS separate from package readiness.
* Keep package probe equivalence separate from package readiness.
* Treat package probe equivalence as evidence-backed only when command, package script hash, and predicate source hash are recorded.
* Require a package predicate extraction report when package predicates are distributed or predicate source paths are ambiguous.
* Keep current-route PASS separate from release readiness.
* Keep machine PASS separate from independent review PASS.
* Keep owner seal separate from independent review.
* Keep stale-bridge independent-review pending state separate unless a bound external non-roadmap-author review closes it.
* Preserve dirty working tree changes outside this plan.
* Use isolated package output for package probes unless later owner-approved execution explicitly permits live package output mutation.

---

## 12. Expected Closeout State

Expected plan artifact closeout:

```text
predecessor_stale_artifact_reentry_guard_plan_written
```

Expected preflight-only closeout if Phase 0 / Phase 1 fails:

```text
plan_revision_required_before_guard_implementation
```

Expected implementation closeout after a later execution round:

```text
predecessor_stale_artifact_reentry_guard_machine_contract_pass
```

That implementation closeout is allowed only if:

* Phase 0 / Phase 1 preflight records `go_no_go_decision=GO`.
* final validator proves all phase GO/NO_GO fields are consistent and `go_no_go_phase_drift_count=0`.
* denominator pattern reuse status is `usable`.
* artifact-universe denominator id, axis, membership, and count are distinct from consumer-universe denominators.
* existing Iris pattern reuse status is `PASS`.
* docs claim-scan sample fixture count is at least `24`.
* docs claim-scan sample category coverage is at least four fixtures per required category.
* docs claim-scan sample adjudication false positive count is `0`.
* docs claim-scan sample adjudication false negative count is `0`.
* artifact-universe denominator is locked with a deterministic denominator id.
* final report records the denominator id.
* predecessor / stale artifact inventory coverage is 100 percent against the locked denominator.
* every artifact has exactly one disposition.
* unknown or ambiguous artifact count is `0`.
* `unknown_blocked_count=0`, unless owner-approved disposition override is recorded.
* every owner-approved disposition override includes owner, reason, artifact id, requested disposition, approved disposition, why-not-current-authority, permanence/expiry, approval artifact path, and approval artifact sha256.
* `manual_override_used=false` when override count is `0`, or `manual_override_used=true` when override count is greater than `0`.
* taxonomy enum validation passes for every disposition field.
* `review_input_only_non_authority` is preserved as the taxonomy enum member in intermediate artifacts and final reports.
* bare `review_input_only` disposition count is `0`.
* artifact class x reentry surface matrix coverage is 100 percent.
* classification precedence validation PASS.
* conservative conflict resolution fixtures PASS.
* current-looking predecessor path violation count is `0`.
* stale bridge current path violation count is `0`.
* monolith current path violation count is `0`.
* old 6-entry bridge current/package reentry count is `0`.
* rollback snapshot current/package reentry count is `0`.
* renamed payload-identical legacy bridge fixture fails closed.
* relocated predecessor fixture variants fail closed.
* non-standard filename monolith payload variant fails closed.
* role metadata conflict fixture fails closed.
* payload marker conflict fixture fails closed.
* package forbidden hit count is `0`.
* package zip forbidden hit count is `0`.
* package probe equivalence report has `same_forbidden_predicates_as_package_iris=true`.
* package predicate extraction report records predicate source paths, line or AST spans, normalized predicate hashes, and extraction coverage.
* package probe equivalence report records probe command, package script hash, and predicate source hash.
* package probe equivalence report has `zip_scan_executed=true`.
* package probe equivalence report has `live_package_payload_mutated=false`.
* package probe equivalence report has `probe_vs_real_route_drift_count=0`.
* required manifest predecessor reentry count is `0`.
* manifest adoption sequencing has `self_reference_cycle_detected=false`.
* stable pre-final artifacts/tests are adopted before final report adoption.
* raw predecessor direct authority read count is `0`.
* dual authority read count is `0`.
* dual-guard responsibility split assigns exactly one authoritative axis for overlap.
* current-route tooling allowlist impact report has `tooling_allowlist_cap_bypassed=false`.
* docs claim violation count is `0`.
* docs claim scan scope and negation / role-qualified method are pinned.
* protected source / rendered / Lua bridge / runtime / package mutation count is `0`.
* existing required artifact/test removal count is `0`.
* existing required artifact/test weakening count is `0`.
* focused runner, validator, and unittest exit with code `0`.
* negative fixtures fail closed.
* package route PASS is recorded from isolated output.
* VCS guard PASS is recorded.
* full current-route validation exits with code `0` and closure enforced.
* final report declares governance-only machine PASS with `governance_guard_only=true`.
* final report declares `source_authority_mutated=false`.
* final report declares `runtime_authority_mutated=false`.
* final report declares `package_authority_mutated=false`.
* final report declares `release_readiness_claimed=false`.
* final report declares `canonical_seal_claimed=false`.
* final report records `independent_review_status=pending_or_external`.
* stale-bridge IR linkage is explicit and does not false-close prior `review_pending` state.
* predecessor evidence remains comparison / provenance / historical / diagnostic / fixture trace only.
* no release readiness, package readiness, live migration execution, manual QA, semantic quality completion, or public-facing text acceptance claim is emitted.

Allowed alternate closeout states:

* `plan_revision_required_before_guard_implementation`: Phase 0 / Phase 1 proves the plan needs revision before guard implementation can safely start.
* `blocked_preflight_go_no_go_failed`: preflight records `go_no_go_decision=NO_GO`.
* `blocked_go_no_go_phase_drift`: final validator finds inconsistent GO/NO_GO values across phase artifacts.
* `blocked_existing_pattern_reuse_missing`: existing Iris denominator / claim-scan / durable-surface patterns cannot be reused or safely adapted.
* `blocked_denominator_pattern_unusable`: artifact universe cannot be locked without degrading coverage into discovered-row coverage.
* `blocked_denominator_axis_contamination`: artifact-universe denominator reuses consumer-universe id, membership, count, or lifecycle axis.
* `blocked_docs_claim_scan_sample_fixture_coverage`: docs claim-scan sample fixture count or category coverage is below the required minimum.
* `blocked_claim_scan_sample_adjudication_failed`: docs claim-scan sample false positive or false negative count is nonzero.
* `implemented_only`: docs/tools/tests exist but required validation was not run.
* `blocked_inventory_incomplete`: inventory coverage is incomplete.
* `blocked_denominator_unlocked`: denominator lock is missing or unstable.
* `blocked_unknown_artifact`: an artifact cannot be assigned a safe disposition.
* `blocked_override_audit_incomplete`: owner-approved disposition override is missing required audit or hash-binding fields.
* `blocked_manual_override_flag_missing`: override count and `manual_override_used` flag are missing or inconsistent.
* `blocked_taxonomy_enum_validation_failed`: a disposition value is not accepted by `artifact_disposition_taxonomy.json` or `review_input_only` is accepted as an alias.
* `blocked_review_input_disposition_abbreviated`: `review_input_only_non_authority` was shortened to `review_input_only`.
* `blocked_negative_fixture_matrix_weak`: adversarial rename / relocate / payload-shape fixtures are missing or not fail-closed.
* `blocked_classification_precedence_incomplete`: conflict precedence is missing or non-deterministic.
* `blocked_current_looking_path_violation`: predecessor/stale artifact appears in current-looking path.
* `blocked_package_reentry_detected`: predecessor/stale artifact appears in package output or zip.
* `blocked_package_probe_equivalence`: isolated package probe does not prove equivalence with the real package route.
* `blocked_package_predicate_extraction_missing`: package predicate extraction is missing, ambiguous, or incomplete.
* `blocked_package_probe_evidence_missing`: package probe command, script hash, or predicate source hash is missing.
* `blocked_required_manifest_reentry`: predecessor/stale artifact is consumed as current-required evidence.
* `blocked_manifest_self_reference_cycle`: manifest adoption creates a final-report self-reference cycle.
* `blocked_raw_predecessor_authority_read`: raw predecessor artifact is direct execution authority.
* `blocked_dual_authority_read`: old and successor artifact are both current authority.
* `blocked_claim_surface_violation`: docs or reports overclaim authority/readiness.
* `blocked_claim_scan_method_unpinned`: docs claim-scan scope or negation / role-qualified method is not pinned.
* `blocked_manifest_adoption_not_additive`: required manifest adoption removes or weakens existing gates.
* `blocked_tooling_allowlist_review_required`: current-route tooling allowlist expansion is required but not reviewed.
* `blocked_full_current_route_validation_failed`: current-route closure is missing or non-zero.
* `blocked_no_mutation_violation`: protected surface changed.
* `blocked_stale_bridge_ir_false_closure`: this round appears to close stale-bridge independent review without a bound external review artifact.
* `blocked_independent_review_pending`: canonical seal is waiting on review, while machine contract may still pass.
* `blocked_owner_seal_pending`: canonical naming, token, or seal state is not owner-sealed.

Final non-claim:

```text
This guard does not complete source restoration, current authority cutover,
rendered live regeneration, Lua bridge export mutation, runtime chunk
replacement, package payload mutation, live migration execution, release
readiness, package readiness, Workshop readiness, B42 readiness, deployment
readiness, manual in-game QA, semantic quality completion, public-facing text
acceptance, full runtime equivalence, full compatibility preservation, full
clean-checkout required-evidence reproducibility, full historical byte
reproducibility, predecessor artifact deletion, monolith authority restoration,
stale bridge fallback restoration, independent-review PASS, or canonical seal.
```
