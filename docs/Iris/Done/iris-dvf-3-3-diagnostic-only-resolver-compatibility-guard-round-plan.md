# Iris DVF 3-3 Diagnostic-only Resolver Compatibility Guard Round Plan

> 상태: Draft v0.1-plan  
> 기준일: 2026-05-17  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> authority input: `ROADMAP -- Diagnostic-only Resolver Compatibility Guard Round` (2026-05-17 user-provided synthesis)  
> 계획 형식: `docs/PLAN_TEMPLATE.md`  
> template attestation: `docs/PLAN_TEMPLATE.md` exists in this checkout and this plan follows its 1-12 section structure.  
> 실행 상태: planning authority only. 이 문서는 diagnostic-only resolver compatibility guard round를 열기 위한 실행 계획이며, 작성 시점에는 resolver code, runtime Lua, generated runtime artifacts, rendered text, quality/publish state, deployed state, top-doc closeout state를 변경하지 않는다.

---

## 1. Objective

이번 execution plan의 목적은 `Resolver Compatibility / Selected Role Bridge Cleanup Debt`를 `selected_role` 제거 문제가 아니라 `Diagnostic-only Resolver Compatibility Guard Round`로 닫기 위한 실행 범위와 검증 계약을 고정하는 것이다.

핵심 objective:

```text
legacy compatibility mapping must not act as silent default authority
selected_role is native resolver authority
selected_role influence zero is not a success criterion
```

이번 round는 default resolver 안에 남아 있는 legacy compatibility mapping이 forward/default 입력에서 조용히 authority로 작동하지 못하도록 fail-loud guard 또는 diagnostic-only boundary를 둔다. 동시에 `selected_role`, `selected_role_precedence`, `selected_role_target`은 Iris DVF 3-3 native resolver authority / trace로 유지한다.

Expected closeout target:

```text
closed_with_diagnostic_only_resolver_guard
```

Alternative accepted closeout wording:

```text
closed_with_default_legacy_mapping_guard
```

Rejected closeout wording:

```text
complete_removal_closed
selected_role_cleanup_completed
selected_role_influence_zeroed
runtime_deployed
ready_for_release
```

---

## 2. Scope

This round is a build-time resolver boundary and governance seal round. It is not a runtime behavior round, release readiness round, or complete-removal cleanup round.

In scope:

* Opening scope lock for `Diagnostic-only Resolver Compatibility Guard Round`.
* Canonical disposition seal for:

```text
selected_role = native resolver authority
selected_role_precedence = native resolver trace
selected_role_target = native resolver trace / authority observation
```

* Resolver surface inventory for default, build, diagnostic, test, archival, and unreachable paths.
* Two-method cross-check of resolver entrypoints and legacy mapping callsites.
* Default path boundary plan for legacy compatibility labels such as:

```text
interaction_tool
interaction_component
interaction_output
```

* Option selection for guard design:

```text
Option A = fail-loud guard only
Option B = diagnostic-only isolation with structural default-path rejection
Option C = fail-loud default guard + diagnostic-only isolation
```

Default proposal: Option C, with an explicit Phase 2 fork point to reduce to Option A if diagnostic-only isolation is unnecessary. Option B is not selectable as a standalone diagnostic-only path unless Phase 2 proves it structurally rejects legacy labels from the default path with fail-loud-equivalent behavior. Without that default-path rejection guarantee, Option B does not satisfy this round's invariant.

* Build-time guard implementation if Phase 2 selects Option A or C. Option B is allowed only under the fail-loud-equivalent exception above.
* Diagnostic-only path root guard and canonical write prohibition if Phase 2 selects Option B under the exception above or Option C.
* Selected-role allow-list preservation, with non-zero influence treated as native authority evidence.
* Adapter disposition surface separation. Adapter removal is not performed.
* No-delta verification and hard gate report.
* Negative/adversarial guard tests.
* Closeout documentation with an explicit claim ceiling.

Round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/
```

Planned docs surface:

```text
docs/Iris/iris-dvf-3-3-diagnostic-only-resolver-compatibility-guard-round-plan.md
docs/Iris/iris-dvf-3-3-diagnostic-only-resolver-compatibility-guard-round-roadmap.md
docs/Iris/iris-dvf-3-3-diagnostic-only-resolver-compatibility-guard-round-scope-lock.md
docs/Iris/Done/Walkthrough/iris-dvf-3-3-diagnostic-only-resolver-compatibility-guard-round-walkthrough.md
```

### Explicitly Out Of Scope

* `selected_role` removal.
* `selected_role_precedence` removal.
* `selected_role_target` removal.
* selected-role influence `0` as a success criterion.
* Complete-removal cleanup.
* Adapter removal.
* Frozen 2105 byte-level recovery.
* AI-trace reconstruction as a replacement for historical frozen baseline authority.
* Runtime Lua regeneration.
* Runtime Lua rebaseline.
* Chunk manifest changes.
* Chunk file changes.
* Rendered body changes.
* Body plan schema changes.
* Compose authority redesign.
* `quality_state` / `publish_state` mutation.
* Metadata migration deferred 21 silent rows cleanup.
* Group B 569 source expansion.
* A-4-1 rework / cluster budget round.
* `quality_baseline_v4 -> v5` cutover.
* `quality_exposed` activation or semantic quality UI exposure.
* Manual in-game QA pass.
* Deployed closeout.
* Workshop release.
* `ready_for_release` declaration.

---

## 3. Non-Goals

This plan does not attempt to:

* Reopen the 2026-04 metadata migration round.
* Reopen SDRG, SAPR, or EDPAS sealed decisions.
* Treat `selected_role`, `selected_role_precedence`, or `selected_role_target` as legacy residue.
* Add selected-role fields to `legacy_field_namespace_contract.json` `legacy_profile_fields_to_scan`.
* Delete the legacy compatibility mapping merely because it exists.
* Declare `Resolver Compatibility Mapping Cleanup` success closeout for the earlier complete-removal framing.
* Declare adapter diagnostic-only retention or adapter removal as a final decision.
* Change external mod compatibility contracts.
* Change public-facing rendered description output.
* Claim full runtime equivalence, production validation, or release readiness.

The target is structural guard and diagnostic isolation, not historical deletion.

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` is the constitutional top authority.
* `docs/DECISIONS.md` latest 2026-05-17 decisions are current:
  * `Resolver cleanup framing is split by cleanup kind`
  * `Selected role is adopted as native resolver design element`
* `docs/ARCHITECTURE.md` current resolver readpoint controls this round:
  * `selected_role`, `selected_role_precedence`, `selected_role_target` are native resolver authority / trace.
  * Active resolver debt is diagnostic-only legacy compatibility guard debt.
* `docs/ROADMAP.md` `#5 Iris` current state controls the next-round posture.

Baseline assumptions:

```text
legacy_fallback_target_count = 0
default_path_legacy_fallback_reach_count = 0
default_adapter_dependency_count = 0
selected_role_target_legacy_authority_count = 0
selected_role_target_masked_legacy_fallback_reach_count = 0
selected_role_precedence_default_influence_count = 264
selected_role_target_default_influence_count = 642
diagnostic-only isolation frozen-baseline prerequisite = A1_sufficient
```

Baseline input artifacts for the 264 / 642 selected-role native influence stability check:

```text
Iris/build/description/v2/staging/compose_contract_migration/selected_role_bridge_impact_seal_round/phase7_ai_trace_reconstruction/phase7_closeout/closeout_non_zero_finding.json
Iris/build/description/v2/staging/compose_contract_migration/selected_role_bridge_impact_seal_round/phase7_ai_trace_reconstruction/selected_role_rowwise_mask.ai_trace.measurement.json
Iris/build/description/v2/staging/compose_contract_migration/selected_role_bridge_impact_seal_round/phase7_ai_trace_reconstruction/metadata_migration_probe/metadata_migration_probe_report.json
```

Qualifier: the 264 / 642 values are current AI-trace/native influence stability check values only; they are not a historical frozen 2105 baseline substitute and do not replace the historical `288 / 894 / 039027...` frozen baseline trace.

Execution assumptions:

* Build-time resolver files live under the Iris DVF 3-3 description pipeline.
* Runtime Lua is a render-only consumer and must remain unchanged.
* Diagnostic outputs must be written outside canonical artifact roots.
* Default mode must fail-loud on legacy compatibility labels rather than silently fallback.
* Diagnostic mode requires an explicit mode flag.
* Diagnostic mode cannot write canonical rendered, Lua, or runtime artifacts.
* Adapter remains a non-writer boundary.

---

## 5. Repository Areas Affected

### Code

Potential Phase 3 build-time files only:

* `Iris/build/description/v2/**`
* `Iris/build/description/v2/tools/**`
* `Iris/build/description/v2/tests/**`

Runtime Lua files must not be edited:

* `Iris/Iris/media/lua/**`
* `lua/**`
* `media/**`

### Docs

* `docs/Iris/iris-dvf-3-3-diagnostic-only-resolver-compatibility-guard-round-plan.md`
* `docs/Iris/iris-dvf-3-3-diagnostic-only-resolver-compatibility-guard-round-roadmap.md`
* `docs/Iris/iris-dvf-3-3-diagnostic-only-resolver-compatibility-guard-round-scope-lock.md`
* `docs/Iris/Done/Walkthrough/iris-dvf-3-3-diagnostic-only-resolver-compatibility-guard-round-walkthrough.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Top-doc edits are allowed only after validation evidence exists and must be additive / claim-limited.

### Config

Potential config or contract files:

* `legacy_field_namespace_contract.json` under the existing metadata migration artifact root, if Phase 2 proves a contract readpoint copy or additive reference is needed.
* Round-local error code and validation matrix artifacts under the staging root.

Hard constraint:

```text
Do not add selected_role, selected_role_precedence, or selected_role_target to legacy_profile_fields_to_scan.
```

### Generated Artifacts

Planned generated artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/
```

Planned artifact groups:

```text
phase1_opening/
phase1_disposition_sealing/
phase2_inventory/
phase2_boundary_plan/
phase3_guard_design/
phase3_implementation/
phase3_patch/
phase4_adapter_disposition/
phase5_no_delta/
phase5_hard_gate/
phase6_adversarial/
phase6_review/
phase7_docs/
phase7_closeout/
phase8_closeout/
```

Diagnostic-only artifacts must remain under diagnostic or round-local staging roots and must not become canonical rendered/Lua/runtime artifacts.

---

## 6. Planned Changes

### Change 1 -- Opening Scope Lock / Selected-role Native Authority Disposition Sealing

Purpose:

Lock this round as `Diagnostic-only Resolver Compatibility Guard Round` and record a round-local selected-role native authority / trace disposition before any guard design work begins.

Files:

* `docs/Iris/iris-dvf-3-3-diagnostic-only-resolver-compatibility-guard-round-scope-lock.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase1_opening/opening_scope_lock.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase1_opening/authority_readpoint.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase1_disposition_sealing/disposition_seal.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase1_disposition_sealing/disposition_seal.md`

Implementation Notes:

* Record authoritative read order:

```text
Philosophy.md -> DECISIONS.md -> ARCHITECTURE.md -> ROADMAP.md -> this plan / round roadmap
```

* Include the required scope-lock statements:

```text
selected_role is native resolver authority
selected_role_precedence and selected_role_target are native resolver trace / authority observation
selected_role influence zero is not a success criterion
complete-removal is out of scope
frozen 2105 byte-level recovery is not a blocker for this diagnostic-only guard round
adapter removal is out of scope
legacy compatibility mapping must not act as silent default authority
```

* Cross-reference the 2026-05-17 selected-role native adoption decision from the round scope lock and disposition seal only. `docs/ARCHITECTURE.md` and `docs/ROADMAP.md` are not Phase 1 edit targets; top-doc edits are deferred to Phase 7 after validation evidence exists.
* Keep all docs wording claim-limited. This is not selected-role cleanup completion.

Validation:

* Grep-based cross-document consistency check for active sections.
* Verify active text does not call selected-role fields legacy residue.
* Verify all required scope-lock statements listed in Implementation Notes are present.

---

### Change 2 -- Resolver Surface Inventory / Default Path Legacy Label Boundary Plan

Purpose:

Inventory every resolver entrypoint and legacy mapping callsite so the guard cannot be bypassed by an unclassified default path.

Files:

* `Iris/build/description/v2/**`
* `Iris/build/description/v2/tests/**`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase2_inventory/resolver_surface_inventory.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase2_inventory/resolver_surface_inventory.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase2_inventory/legacy_mapping_callsite_scan.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase2_inventory/selected_role_trace_disposition.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase2_inventory/adapter_boundary_scan.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase2_boundary_plan/entry_point_inventory.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase2_boundary_plan/two_method_choice.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase2_boundary_plan/selected_role_allow_list.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase2_boundary_plan/guard_trigger_condition_spec.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase2_boundary_plan/option_selection.json`

Implementation Notes:

* Classify every resolver callsite as one of:

```text
default_authority_path
explicit_diagnostic_path
compat_test_only
legacy_archival
dead_or_unreachable
```

* Record each callsite's transitively reachable write-capable output paths, not only direct write API calls, including canonical rendered/Lua/runtime paths and diagnostic-only staging paths.
* Seal two independent extraction methods in `two_method_choice.json` before inventory begins:
  * Method A: `rg` text/import/callsite scan over resolver modules, tests, and tool entrypoints.
  * Method B: Python AST/module graph scan for Python resolver and tool modules.
  * If Method B is not practical for a specific file type, the only allowed fallback is a deterministic tokenized symbol/call graph scan plus an explicit unresolved-surface list. Any unresolved default-path surface blocks Phase 2 option selection.
* Separate selected-role trace fields from legacy profile label inventory.
* Confirm adapter callsites remain non-writer.
* Simulate the proposed guard trigger condition against the current baseline to catch false positives before implementation.
* Select Option C by default or reduce to Option A if diagnostic-only isolation is unnecessary. Option B is excluded unless it structurally guarantees fail-loud-equivalent default-path rejection.

Validation:

* No unclassified resolver entrypoint remains.
* Selected-role fields are not included in legacy label inventory.
* Default path legacy mapping callable status is explicitly recorded.
* Selected-role allow-list alignment unit is row-level, keyed by per-item identifier. Validation must compare the row-level selected-role influence set against the AI-trace/native influence stability artifacts, then also confirm aggregate counts remain 264 / 642.
* The 264 / 642 comparison is a current AI-trace/native influence stability check only; it is not a historical frozen 2105 baseline substitute.
* Guard trigger simulation does not fire on valid current native default rows.

---

### Change 3 -- Guard Design Confirmation / Boundary Enforcement Implementation

Purpose:

Implement the chosen default boundary in the build-time resolver without changing runtime Lua or rendered output.

Files:

* `Iris/build/description/v2/**`
* `Iris/build/description/v2/tests/**`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase3_guard_design/default_path_legacy_guard_design.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase3_guard_design/diagnostic_only_boundary_design.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase3_guard_design/error_code_contract.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase3_guard_design/validation_matrix.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase3_implementation/implementation_summary.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase3_implementation/regression_test_log.txt`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase3_patch/patch_manifest.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase3_patch/touched_surface_report.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase3_patch/guard_invariant_test_report.json`

Implementation Notes:

Required invariants:

```text
default path accepts only native v2 authority inputs
legacy profile labels require explicit diagnostic mode
diagnostic mode cannot write canonical rendered/Lua/runtime artifacts
selected_role path remains native
adapter remains non-writer
```

Option B guard condition:

```text
Option B cannot be selected as diagnostic-only isolation without structural default-path rejection.
Option B is valid only if its design also provides structural fail-loud-equivalent rejection for default-path legacy labels.
```

Expected fail-loud error code candidates:

```text
LEGACY_PROFILE_LABEL_IN_DEFAULT_RESOLVER
LEGACY_COMPAT_MAPPING_REQUIRES_DIAGNOSTIC_MODE
DEFAULT_RESOLVER_REJECTED_LEGACY_COMPAT_LABEL
```

* Introduce resolver authority context or mode flag only in build-time code.
* Phase 3 must define the mode-token surface before implementation. Mode token means the exact build-time selector used to request default or diagnostic authority context, such as a resolver context object, function argument, CLI flag, or test fixture. Runtime Lua, canonical artifacts, and implicit module globals must not become mode-token sources.
* Default mode rejects legacy compatibility labels.
* Diagnostic mode can access legacy mapping only through explicit diagnostic surface.
* Existing test helpers must not bypass default mode implicitly.
* Add dedicated diagnostic helpers for diagnostic-only tests.
* If Phase 2 selects the narrow Option B exception, `diagnostic_only_boundary_design.md` must identify the structural default-path rejection mechanism and why it is fail-loud-equivalent.
* Keep selected-role resolution logic unchanged.
* Keep adapter non-writer boundary unchanged.

Validation:

* Default mode legacy label reject test passes.
* Diagnostic mode legacy label mapping test passes.
* Selected-role native resolution unchanged test passes.
* Adapter non-writer test passes.
* Diagnostic output root guard test passes.
* Canonical write prohibition test passes.
* Full relevant test suite passes.

---

### Change 4 -- Adapter Disposition Surface Separation

Purpose:

Separate adapter disposition from this guard round so adapter retention, diagnostic-only retention, or removal cannot be inferred from the guard closeout.

Files:

* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase4_adapter_disposition/adapter_disposition_boundary.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase4_adapter_disposition/adapter_disposition_boundary.md`

Implementation Notes:

* Record that adapter removal is not performed.
* Record that adapter writer promotion is not performed.
* If a future adapter disposition decision is needed, park it as a separate decision surface in the round-local artifact. Any `docs/ROADMAP.md` Hold/Next wording is deferred to Phase 7 after validation evidence exists.
* Do not let adapter disposition become a hidden blocker for this round.

Validation:

* Closeout artifact includes:

```text
adapter removal was not performed
adapter writer promotion was not performed
```

* Measurement confirms adapter remains non-writer.

---

### Change 5 -- No-Delta Build Verification / Hard Gate Verification

Purpose:

Prove this round is a guard/boundary seal and not a behavior-changing resolver redesign.

Files:

* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase5_no_delta/pre_change_manifest.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase5_no_delta/post_change_manifest.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase5_no_delta/rendered_delta_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase5_no_delta/lua_runtime_unchanged_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase5_no_delta/default_path_guard_probe_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase5_no_delta/selected_role_trace_stability_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase5_hard_gate/hard_gate_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase5_hard_gate/hard_gate_report.md`

Implementation Notes:

Hard gates:

```text
rendered_output_delta_count = 0
staged Lua hash unchanged
workspace Lua hash unchanged
default_path_legacy_fallback_reach_count = 0
legacy compatibility mapping default authority call surface absent
```

Required PASS values:

```text
rendered_delta_count = 0 (scope: active_rendered_preview_only)
lua_runtime_changed = false (scope: staged_lua + workspace_lua)
chunk_manifest_changed = false (scope: runtime_chunk_manifest)
chunk_files_changed = false (scope: runtime_chunk_files)
default_path_legacy_fallback_reach_count = 0 (scope: default_path)
legacy_fallback_target_count = 0 (scope: canonical_source_metadata)
default_adapter_dependency_count = 0 (scope: default_path; derived alias of default_path_legacy_fallback_reach_count)
selected_role_target_legacy_authority_count = 0 (scope: all_resolver_paths)
selected_role_target_masked_legacy_fallback_reach_count = 0 (scope: all_resolver_paths)
selected_role_precedence_default_influence_count = 264 (scope: current AI-trace/native influence stability check only; not a historical frozen 2105 baseline substitute)
selected_role_target_default_influence_count = 642 (scope: current AI-trace/native influence stability check only; not a historical frozen 2105 baseline substitute)
diagnostic artifacts under diagnostic root only (scope: diagnostic_outputs)
```

Validation:

* Pre-change and post-change manifests compare cleanly.
* Rendered delta is 0 in `active_rendered_preview_only` scope.
* Lua/runtime hashes are unchanged.
* Selected-role influence baseline remains 264 / 642 in deterministic re-run. This is a current AI-trace/native influence stability check only, not a historical frozen 2105 baseline substitute.
* Diagnostic artifacts do not appear under canonical roots.

---

### Change 6 -- Negative / Adversarial Guard Tests / Adversarial Review

Purpose:

Prove the default guard fails loud on legacy labels and does not block native selected-role resolution.

Files:

* `Iris/build/description/v2/tests/**`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase6_adversarial/default_legacy_label_rejection_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase6_adversarial/diagnostic_legacy_mapping_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase6_adversarial/canonical_write_guard_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase6_adversarial/adversarial_summary.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase6_review/adversarial_review.md`

Implementation Notes:

Required probes:

```text
default mode + interaction_tool -> fail-loud
default mode + interaction_component -> fail-loud
default mode + interaction_output -> fail-loud
default mode + malformed legacy profile -> fail-loud
default mode + valid selected_role native row -> pass
default helper/test path + injected diagnostic mode token through the Phase 3-defined mode-token surface -> fail-loud or rejected as unauthorized mode escalation
diagnostic mode + legacy mapping explicit call -> pass
diagnostic mode + output root set outside diagnostic root -> fail-loud
diagnostic mode + canonical rendered/Lua/runtime write attempt -> fail-loud
```

Review format:

```text
Good points
Critical
Important
Minor
Verdict
```

Validation:

* Default legacy label probes fail-loud.
* Fail-loud error codes match the error code contract.
* Selected-role native probe passes.
* Diagnostic legacy probe passes only with explicit diagnostic mode.
* Default helper/test path cannot open diagnostic mode implicitly or by injected mode-token bypass.
* Canonical write guard rejects canonical writes.
* No silent fallback is observed.
* Review verdict is PASS or a narrowly scoped Conditional PASS with one resolvable Critical.

---

### Change 7 -- Documentation / Authority Seal / Closeout

Purpose:

Record the validated guard boundary in canonical docs without overstating completion.

Files:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/Iris/Done/Walkthrough/iris-dvf-3-3-diagnostic-only-resolver-compatibility-guard-round-walkthrough.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase7_docs/decisions_addendum.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase7_docs/architecture_patch_summary.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase7_docs/roadmap_patch_summary.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase7_docs/closeout_claim_ceiling.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase7_closeout/closeout.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase7_closeout/closeout.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase8_closeout/round_manifest.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase8_closeout/validation_summary.json`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase8_closeout/known_non_goals.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase8_closeout/followup_decisions.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase8_closeout/diagnostic_only_resolver_compatibility_guard_round_closeout.md`
* `Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round/phase8_closeout/review_packet.md`

Implementation Notes:

Required closeout statements:

```text
selected_role is native resolver authority
selected_role_precedence and selected_role_target are native resolver trace / authority observation
legacy compatibility mapping is not default authority
legacy compatibility mapping is guarded from default path or diagnostic-only
adapter removal was not performed
rendered delta is 0
Lua/runtime artifacts are unchanged
complete-removal is out of scope
ready_for_release is not declared
```

* Add a `DECISIONS.md` addendum only after Phase 5 and Phase 6 pass.
* Update `ARCHITECTURE.md` only with current readpoint absorption and trace pointer language.
* Update `ROADMAP.md` Done / Doing / Next / Hold without implying deployed closeout.
* Write follow-up decisions separately, especially adapter disposition.

Validation:

* Closeout non-decision section maps one-to-one to the non-goals.
* Docs do not imply selected-role removal, complete-removal success, adapter removal, runtime deployment, or release readiness.
* Canonical docs agree on selected-role native authority and legacy mapping default guard boundary.

---

## 7. Validation Plan

### Automated Validation

Required validation commands are determined by Phase 2/3 touched surfaces. Do not claim validation passed unless the exact relevant command exits with code 0.

Baseline Python suite:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

The Phase 5 validation packet must record the observed test count and compare it against the selected current readpoint for the touched surface. Historical readpoints include `307 tests / OK` for the metadata migration round and `380 tests / OK` for Iris refactor v4.1; unexpected count drift must be explained rather than silently accepted.

Expected build-time validation areas:

* Resolver entrypoint inventory cross-check.
* Default legacy label fail-loud tests.
* Diagnostic-only legacy mapping tests.
* Selected-role native resolution stability tests.
* Adapter non-writer boundary test.
* Diagnostic output root guard test.
* Canonical write prohibition test.
* Rendered delta comparison in `active_rendered_preview_only` scope.
* Lua/runtime hash comparison.
* Chunk manifest and chunk file unchanged checks.
* Deterministic re-run of Phase 5 measurements, including the 264 / 642 current AI-trace/native influence stability check. This re-run is not a historical frozen 2105 baseline substitute.

Optional or surface-dependent validation:

```powershell
uv run python <script>
```

Use this only if the relevant build script is already UV-compatible in the target surface.

### Manual Validation

Manual validation for this round is documentation and artifact review only:

* Review `resolver_surface_inventory.md`.
* Review `guard_trigger_condition_spec.md`.
* Review `hard_gate_report.md`.
* Review `adversarial_review.md`.
* Review docs diff for claim ceiling.

No manual in-game QA pass is performed or declared.

### Validation Limits

This round does not perform:

* no multiplayer validation
* no long-session runtime validation
* no external mod compatibility sweep
* no in-game QA pass
* no deployment validation
* no Workshop release validation
* no full runtime equivalence declaration
* no Group B 569 source expansion validation
* no `quality_exposed` UI validation

---

## 8. Risk Surface Touch

### Authority Surface

Touched intentionally, but only at build-time resolver boundary:

* `selected_role` remains native resolver authority.
* `selected_role_precedence` and `selected_role_target` remain native trace / authority observation.
* Legacy compatibility mapping loses any silent default authority path.
* No new runtime authority surface is created.

### Runtime Behavior Surface

None intended.

Runtime Lua must remain unchanged. Runtime consumers remain render-only.

### Compatibility Surface

Build-time compatibility surface is touched:

* Future default inputs that supply legacy compatibility labels must fail-loud.
* Explicit diagnostic compatibility surface may remain available if selected in Phase 2.

External mod runtime compatibility is not changed by this round.

### Sealed Artifact Surface

Touched only by new round-local staging artifacts.

Must remain unchanged:

* staged Lua hash
* workspace Lua hash
* chunk manifest
* chunk files
* rendered active preview output
* sealed metadata migration round artifacts
* historical 2105 / 288 / 894 artifacts

### Public-Facing Output Surface

None.

Rendered description text and user-facing Iris UI text must not change.

---

## 9. Risk Analysis

### Architecture Risk

* selected-role fields may be misread again as legacy residue. Mitigation: Phase 1 disposition seal and required closeout wording.
* Complete-removal cleanup may be conflated with diagnostic-only guard. Mitigation: explicit out-of-scope and closeout claim ceiling.
* Adapter removal may drift into this round. Mitigation: Phase 4 surface separation.
* Single-writer boundary may be bypassed if resolver guard changes decision authority. Mitigation: guard only rejects legacy labels and does not write quality/publish state.

### Runtime Risk

* Runtime Lua or chunk files may be changed accidentally. Mitigation: Phase 5 hash and chunk unchanged gates.
* Rendered output delta may appear. Mitigation: hard stop if rendered delta is non-zero.
* Diagnostic mode may write canonical artifacts. Mitigation: diagnostic root guard and canonical write prohibition tests.

### Compatibility Risk

* A legitimate native selected-role row may be rejected as legacy. Mitigation: explicit selected-role allow-list and 264 / 642 current AI-trace/native influence stability checks, not historical frozen 2105 baseline substitution.
* Legacy compatibility mapping existence may be treated as failure. Mitigation: round goal is guard/isolation, not physical deletion.
* Default path guard may be too narrow and leave a bypass. Mitigation: two-method entrypoint inventory and adversarial probes.
* Default path guard may be too broad and reject valid native rows. Mitigation: Phase 2 false-positive simulation and Phase 3 selected-role tests.

### Regression Risk

* Existing tests may rely on legacy labels through default helpers. Mitigation: move those tests to explicit diagnostic helpers or rewrite them to assert fail-loud default behavior.
* Reach measurement may double-count diagnostic-only surfaces. Mitigation: define default path metrics separately from diagnostic surface metrics.
* Docs may overclaim closeout. Mitigation: Phase 7 claim ceiling and required non-decision list.

---

## 10. Rollback Plan

Rollback is split by change type.

Documentation rollback:

* Revert Phase 1 or Phase 7 docs patches if wording overclaims or conflicts with current readpoints.
* Do not erase sealed historical decisions. If a closeout decision was already added and later invalidated, add a superseding rollback decision instead.

Build-time implementation rollback:

* Revert Phase 3 build-time guard patches if:

```text
selected_role_precedence_default_influence_count != 264 (scope: current AI-trace/native influence stability check only)
selected_role_target_default_influence_count != 642 (scope: current AI-trace/native influence stability check only)
rendered_output_delta_count != 0
Lua/runtime hashes changed
default_path_legacy_fallback_reach_count != 0
Phase 6 Critical remains unresolved
```

Artifact rollback:

* Keep failed or blocked diagnostic artifacts as provenance if the round reaches a blocked/FAIL closeout.
* Do not promote failed diagnostic artifacts to canonical root.

Rollback must not reopen:

* selected-role native authority decision
* complete-removal exclusion decision
* frozen 2105 debt separation decision
* diagnostic-only guard problem definition

Rollback does not automatically open Frozen 2105 baseline reconstruction or complete-removal cleanup.

---

## 11. Governance Constraints

Mandatory constraints:

* `docs/Philosophy.md` compliance.
* Hub & Spoke preservation.
* SPI preservation.
* Compatibility remains priority 1.
* Runtime/build-time separation.
* Offline build authority preservation.
* Lua runtime render-only principle.
* Single-writer principle: decision stage remains the only quality/publish state writer.
* Fail-loud behavior for default legacy compatibility labels.
* No silent fallback.
* Determinism: same input produces same output.
* Sealed decision irreversibility.

Round-specific constraints:

```text
selected_role removal is forbidden
selected_role_precedence removal is forbidden
selected_role_target removal is forbidden
selected-role influence zero is not a success criterion
complete-removal is out of scope
frozen 2105 byte-level recovery is not a blocker for this diagnostic-only guard round
adapter removal is out of scope
legacy compatibility mapping must not act as silent default authority
runtime Lua regeneration is forbidden
manual in-game QA pass is not declared
ready_for_release is not declared
```

Namespace constraint:

```text
legacy_field_namespace_contract.json must not add selected_role, selected_role_precedence, or selected_role_target to legacy_profile_fields_to_scan.
```

Output constraints:

```text
rendered delta = 0
Lua/runtime artifacts unchanged
default_path_legacy_fallback_reach_count = 0
selected_role_target_legacy_authority_count = 0
selected_role_target_masked_legacy_fallback_reach_count = 0
selected_role native influence baseline remains 264 / 642 (scope: current AI-trace/native influence stability check only; not a historical frozen 2105 baseline substitute)
diagnostic output is not written to canonical artifact root
```

---

## 12. Expected Closeout State

Expected closeout:

```text
complete, but only as diagnostic guard closeout
```

Allowed final closeout labels:

```text
closed_with_diagnostic_only_resolver_guard
closed_with_default_legacy_mapping_guard
```

Closeout requires all of the following:

* `selected_role` remains present.
* `selected_role_precedence` remains present.
* `selected_role_target` remains present.
* selected-role influence `0` is not used as a success criterion.
* Complete-removal is not executed.
* Adapter removal is not executed.
* Runtime Lua regeneration is not executed.
* `rendered_output_delta_count = 0`.
* staged Lua hash unchanged.
* workspace Lua hash unchanged.
* chunk manifest unchanged.
* chunk files unchanged.
* `default_path_legacy_fallback_reach_count = 0`.
* `legacy_fallback_target_count = 0`.
* `default_adapter_dependency_count = 0`.
* `selected_role_target_legacy_authority_count = 0`.
* `selected_role_target_masked_legacy_fallback_reach_count = 0`.
* selected-role native influence baseline remains 264 / 642 for the current AI-trace/native influence stability check only; this is not a historical frozen 2105 baseline substitute.
* Default path legacy labels do not silently resolve through compatibility mapping.
* Legacy compatibility mapping exists only behind fail-loud default guard or explicit diagnostic-only path.
* Diagnostic-only path cannot write canonical rendered/Lua/runtime artifacts.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` agree on selected-role native authority / trace.
* Test suite passes for the relevant touched surfaces.
* Phase 6 adversarial review is PASS or narrowly scoped Conditional PASS.
* Closeout does not declare deployed state, manual QA pass, or `ready_for_release`.

If any required closeout condition fails, expected closeout becomes:

```text
blocked
```

or:

```text
FAIL
```

depending on whether the failure is an implementation blocker or an invalidated guard claim.
