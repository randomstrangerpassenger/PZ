# Iris DVF 3-3 Resolver Compatibility Mapping Cleanup Round Plan

> 상태: Draft v0.3-plan  
> 기준일: 2026-05-13  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> authority input: `Resolver Compatibility Mapping Cleanup Round - 최종 통합 로드맵` (2026-05-13 user-provided synthesis)  
> 계획 형식: `docs/PLAN_TEMPLATE.md`  
> template attestation: `docs/PLAN_TEMPLATE.md` exists in this checkout and is the canonical plan template named by the repository session instructions; this plan follows its 1-12 section structure.  
> 실행 상태: planning authority only. 이 문서는 resolver cleanup round를 열기 위한 계획이며, 작성 시점에는 resolver code, namespace contract, rendered text, Lua runtime artifact, top-doc closeout state를 변경하지 않는다.

---

## 1. Objective

이번 execution plan의 목적은 `Adapter / Native Body Plan Metadata Migration Round` closeout에서 carry-forward obligation으로 남은 두 부채를 하나의 governance-scale cleanup round로 닫는 것이다.

1. v2 resolver 내부에 남아 있는 legacy label compatibility mapping이 default authority source로 작동하지 못하도록 default resolver path 밖으로 fence한다.
2. `selected_role` bridge disposition을 measurable count와 namespace contract additive amendment로 명문화한다.

Expected authority target:

```text
default resolver path = compose_profiles_v2.json + native body_plan authority only
legacy compatibility mapping = explicit compat_legacy / diagnostic_legacy only
selected_role_precedence = native diagnostic trace for resolver legacy-origin path, default influence 0
selected_role_target = resolved native target trace, legacy authority 0
```

Expected closeout ceiling:

```text
closed_with_default_resolver_legacy_mapping_fenced
```

---

## 2. Scope

This round is a governance cleanup round, not a runtime behavior or release readiness round.

In scope:

* Phase 0 opening scope lock and pass criteria contract.
* Phase 1 baseline freeze and reachability inventory.
* Resolver compatibility mapping disposition decision.
* `selected_role` bridge disposition decision.
* Additive namespace contract amendment confirming `selected_role` as native namespace member.
* Resolver default/compat/diagnostic path guard design and implementation if `relegate_to_diagnostic_only` is selected.
* Round-local diagnostic scripts and artifacts under:

```text
Iris/build/description/v2/staging/compose_contract_migration/resolver_compatibility_mapping_cleanup_round/
```

* Dry-run and post-apply invariant verification.
* Adversarial review.
* Top-doc closeout notes only after validation passes.

Opening decisions are locked as follows:

| ID | Decision | Selected |
|---|---|---|
| `[OPEN-A]` | phase structure | `A2_single_integrated_surface` |
| `[OPEN-B-1]` | resolver compatibility mapping disposition | `relegate_to_diagnostic_only` |
| `[OPEN-B-2]` | selected_role bridge disposition | `maintain_as_native_metadata` |
| `[OPEN-C]` | adapter non-decision location | closeout pass JSON `adapter_disposition_status` |
| `[OPEN-D]` | namespace amendment classification | `additive_amendment` |
| `[OPEN-E]` | validation depth | `standard` because resolver guard mutation is planned |

Decision rationale:

* `[OPEN-A] A2_single_integrated_surface` is selected because resolver path classification and `selected_role` namespace disposition are the same carry-forward obligation and must be verified by the same Phase 5/7 invariant matrix. Sub-scope separation is rejected because it would let one debt close without the other count/influence evidence.
* `[OPEN-B-1] relegate_to_diagnostic_only` is selected because code-level default guard coverage is needed even if Phase 1 proves current default reach is zero. `maintain_as_explicit_compat_path` is rejected for this round because documentation-only preservation leaves future drift risk unresolved; `physical_removal` is out of scope because historical diagnostic reproducibility must be preserved.
* `[OPEN-B-2] maintain_as_native_metadata` is selected because the prior Branch A interpretation treats `selected_role` as native metadata, and this round's contract amendment exists to seal that interpretation. Removal or diagnostic-only relocation is rejected because it risks rendered delta and source-shape churn outside cleanup scope.
* `[OPEN-C] closeout_pass JSON field` is selected so the adapter non-decision is visible at the same read point as the cleanup result. A separate adapter artifact is rejected because adapter removal is not being opened.
* `[OPEN-D] additive_amendment` is selected because the legacy scan list remains unchanged and only native namespace membership is clarified. Boundary modification is rejected because 11-53 remains intact.
* `[OPEN-E] standard` validation is selected because `relegate_to_diagnostic_only` includes resolver guard mutation. Lightweight validation is rejected for this selected disposition.

Phase 0 must mirror this rationale in `phase0_opening/opening_decision_reflection.md`.

### Explicitly Out Of Scope

* Adapter physical removal.
* `persisted_old_profile_count = 0` declaration.
* Silent metadata `21` cleanup.
* Runtime Lua regeneration or rebaseline.
* `IrisLayer3DataChunks` changes.
* Browser/Wiki runtime consumer changes.
* Runtime-side compose/rewrite.
* Rendered text changes.
* Body plan section emission changes.
* `quality_state` / `publish_state` mutation.
* `quality_baseline_v4 -> v5` cutover.
* Group B source expansion.
* SDRG baseline mutation.
* Schema extension / Branch B reopening.
* Manual in-game validation pass.
* Deployed closeout or `ready_for_release` declaration.

---

## 3. Non-Goals

This plan does not attempt to:

* Remove the compatibility adapter.
* Delete all historical legacy mapping tables.
* Convert diagnostic historical views into default authority.
* Reduce the `selected_role_precedence` or `selected_role_target` row counts to zero.
* Reclassify `selected_role` as a legacy profile field.
* Modify `legacy_profile_fields_to_scan`.
* Change the 2105 row baseline.
* Change staged/workspace Lua hash `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`.
* Claim runtime QA, release readiness, or deployed state.

The target is disposition and fencing, not count erasure.

Forward boundary:

```text
Group B and all subsequent source expansions must not supply legacy labels
through default resolver mode after this round. Such input is expected to
fail-loud and must use native body_plan metadata or explicit compat/diagnostic
mode.
```

---

## 4. Assumptions

* `docs/ARCHITECTURE.md` 11-53 remains the forward compose authority read: `facts + body_source_overlay + decisions + profiles -> body_plan -> rendered flat string -> quality/publish decision stage -> Lua bridge -> Browser/Wiki`.
* `docs/ARCHITECTURE.md` 11-61 remains authoritative that adapter removal execution requires a separate round and keeps resolver code modification out of adapter-removal scope.
* `docs/ARCHITECTURE.md` 11-62 remains authoritative that resolver compatibility mapping remains for explicit diagnostic/compat path and resolver cleanup is a separate round.
* `docs/DECISIONS.md` 2026-04-25 remains authoritative that Resolver Compatibility Mapping Cleanup Round does not open automatically and requires a separate opening decision.
* `docs/ARCHITECTURE.md` 11-58 has been verified in the current checkout and remains the direct default entrypoint authority seal. If a later checkout renumbers this section, Phase 0 must cite the exact superseding EDPAS read point from `docs/DECISIONS.md` or `docs/ARCHITECTURE.md`.
* Working interpretation: `selected_role` is treated as native metadata unless Phase 1 / Phase 3 evidence disproves it. This interpretation must be sealed by the Phase 3 namespace contract additive amendment before closeout.
* Baseline counts are taken from the prior closeout read point:

```text
active row count = 2084
silent row count = 21
total row count = 2105
resolution distribution = 720 / 46 / 136 / selected_role_precedence 288 / selected_role_target 894
quality distribution = strong 1316 / adequate 0 / weak 768
publish split = internal_only 617 / exposed 1467
runtime state = ready_for_in_game_validation
```

* If the sealed prior-round baseline artifacts are absent in the working checkout, Phase 1 must report `blocked_missing_baseline_artifact` rather than reconstructing unstated evidence.

---

## 5. Repository Areas Affected

### Code

Planned or candidate surfaces:

* `Iris/build/description/v2/tools/build/compose_layer3_body_profile.py`
* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tools/build/build_adapter_native_body_plan_metadata_migration.py` (baseline inventory reuse only unless Phase 2 explicitly approves a narrow helper extraction; it is not this round's migration executor)
* `Iris/build/description/v2/tests/test_compose_layer3_text_v2.py`
* `Iris/build/description/v2/tests/test_resolver_compatibility_mapping_cleanup.py`
* New round-local diagnostic and validation scripts, if needed:

```text
Iris/build/description/v2/tools/build/build_resolver_compatibility_mapping_cleanup.py
Iris/build/description/v2/tools/build/validate_resolver_compatibility_mapping_cleanup.py
```

### Docs

Planning and closeout docs:

* `docs/Iris/iris-dvf-3-3-resolver-compatibility-mapping-cleanup-round-plan.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* Optional walkthrough after closeout:

```text
docs/Iris/Done/Walkthrough/iris-dvf-3-3-resolver-compatibility-mapping-cleanup-round-walkthrough.md
```

### Config

No build config changes are planned.

### Generated Artifacts

Round root:

```text
Iris/build/description/v2/staging/compose_contract_migration/resolver_compatibility_mapping_cleanup_round/
```

Planned artifact topology:

```text
phase0_opening/
  opening_decision_reflection.md
  scope_lock.md
  pass_criteria_contract.json
  phase0_opening_seal.json

phase1_baseline/
  baseline_freeze.json
  branch_a_attestation.md
  legacy_mapping_inventory.json
  selected_role_bridge_inventory.json
  resolver_reachability_report.json
  pre_change_artifact_hashes.json

phase2_disposition/
  resolver_compat_mapping_disposition_design.md
  selected_role_bridge_disposition_design.md
  disposition_decision_seal.json

phase3_contract_amendment/
  namespace_contract_v2.json
  amendment_invariant_check.json

phase4_resolver_disposition/
  resolver_source_hash_before_after.json
  default_path_reach_verification.json
  diagnostic_path_reach_verification.json

phase5_dry_run/
  dry_run_verification_report.json
  invariant_preservation_matrix.json

phase6_source_contract_apply/
  executor_script_hash.json
  source_contract_apply_log.json

phase7_post_apply/
  post_apply_verification_report.json
  regression_test_result.json

phase8_review/
  adversarial_review.md

phase9_closeout/
  closeout_pass.json
```

---

## 6. Planned Changes

### Change 1 - Phase 0 Opening Scope Lock

Purpose:

Lock round identity, mutable/immutable surface, pass criteria, and open decisions before any resolver or contract mutation.

Files:

* `phase0_opening/opening_decision_reflection.md`
* `phase0_opening/scope_lock.md`
* `phase0_opening/pass_criteria_contract.json`
* `phase0_opening/phase0_opening_seal.json`

Implementation Notes:

* Record `[OPEN-A]` through `[OPEN-E]` using the selected values in section 2.
* Mark adapter removal as an explicit non-goal.
* Mark rendered text, Lua artifacts, quality/publish state, runtime consumers, and `legacy_profile_fields_to_scan` as immutable.
* Quote architecture read points 11-53, 11-58, 11-61, 11-62 and the 2026-04-25 decisions.
* Record failure semantics:

```text
default legacy label input = fail-loud validation error
missing sealed baseline = blocked_missing_baseline_artifact
rendered delta = Branch C hard closeout
diagnostic write outside diagnostic root = hard fail
any required final pass value in section 12 fails = Branch C
```

Validation:

* Phase 0 seal exists.
* Mutable and immutable surfaces are explicit.
* No code/data/runtime mutation occurs in Phase 0.

---

### Change 2 - Phase 1 Baseline Freeze and Reachability Inventory

Purpose:

Freeze the prior metadata-migration closeout read as this round's baseline and measure whether legacy compatibility mapping or `selected_role` bridge affects default authority.

Files:

* `phase1_baseline/baseline_freeze.json`
* `phase1_baseline/branch_a_attestation.md`
* `phase1_baseline/legacy_mapping_inventory.json`
* `phase1_baseline/selected_role_bridge_inventory.json`
* `phase1_baseline/resolver_reachability_report.json`
* `phase1_baseline/pre_change_artifact_hashes.json`

Implementation Notes:

* Capture baseline counts:

```text
resolution_distribution.bucket_1 = 720
resolution_distribution.bucket_2 = 46
resolution_distribution.bucket_3 = 136
selected_role_precedence_count = 288
selected_role_target_count = 894
resolution_distribution.total_active = 2084
silent_row_count = 21
total_row_count = 2105
legacy_mapping_default_reach_count = measured
legacy_mapping_compat_reach_count = measured
legacy_mapping_diagnostic_reach_count = measured
selected_role_precedence_default_influence_count = measured
selected_role_target_default_influence_count = measured
selected_role_target_native_trace_count = measured
selected_role_target_legacy_authority_count = measured
```

* `baseline_freeze.json` must include the five resolution buckets `720 / 46 / 136 / 288 / 894` as a byte-level snapshot copied from the prior closeout read point, plus `quality_distribution`, `publish_split`, and `bridge_availability`.

* Measure `legacy_mapping_default_reach_count` using both methods:

```text
static_call_graph_analysis:
  resolver/default entry edges must not call LEGACY_PROFILE_FALLBACK
  compat_legacy/diagnostic_legacy edges may call it explicitly

dynamic_dry_run_measurement:
  resolve the frozen 2105 baseline in default mode and count legacy mapping
  invocations; default count must be 0

closeout rule:
  static_default_reach_count = 0 AND dynamic_default_reach_count = 0
```

* Measure `selected_role` influence by separating namespace membership from resolver outcome influence:

```text
selected_role_precedence_count = row trace bucket count
selected_role_precedence_default_influence_count = default authority override count
selected_role_target_native_trace_count = native trace count
selected_role_target_legacy_authority_count = legacy authority count
```

* Reconfirm:

```text
default_path_legacy_fallback_reach_count = 0
default_adapter_dependency_count = 0
canonical_row_legacy_field_residue_count = 0
legacy_fallback_target_count = 0
bridge_availability_delta = 0
```

* If the sealed prior artifact path is unavailable, record a blocked inventory state instead of fabricating parity.

Validation:

* Phase 1 hidden dependency findings are pre-change investigation triggers, not automatic hard closeout triggers:

```text
legacy_mapping_default_reach_count > 0
selected_role_precedence_default_influence_count > 0
selected_role_target_default_influence_count > 0
```

* If any pre-change investigation trigger fires, Phase 2 must decide whether safe fencing can be implemented without rendered, artifact, or authority delta. If safe fencing cannot be implemented, Branch C closes the round as blocked.

---

### Change 3 - Phase 2 Disposition Design Decision

Purpose:

Seal the resolver and `selected_role` disposition before code or contract changes.

Files:

* `phase2_disposition/resolver_compat_mapping_disposition_design.md`
* `phase2_disposition/selected_role_bridge_disposition_design.md`
* `phase2_disposition/disposition_decision_seal.json`

Implementation Notes:

* Resolver disposition: `relegate_to_diagnostic_only`.
* `selected_role` disposition: `maintain_as_native_metadata`.
* Adapter removal: non-decision recorded in closeout JSON.
* Namespace amendment classification: additive-only over 11-53 boundary.
* Validation depth: standard.
* Define `safe_fencing_cannot_be_implemented_without_authority_or_artifact_delta` operationally before Phase 4 begins.

Operational definition:

```text
safe_fencing_cannot_be_implemented_without_authority_or_artifact_delta = true
if any required default fail-loud guard would require changing rendered output,
Lua/runtime artifacts, quality_state, publish_state, bridge availability,
canonical row source shape, or compose/quality writer ownership.

safe_fencing_cannot_be_implemented_without_authority_or_artifact_delta = false
only if default guard implementation can preserve all section 12 required
final pass values while keeping compat_legacy / diagnostic_legacy explicit.
```

Validation:

* Decision seal includes rationale, selected option, rejected options, and branch-C stop criteria.
* Single-writer compliance is explicitly asserted.

---

### Change 4 - Phase 3 Namespace Contract Amendment

Purpose:

Confirm `selected_role` as native namespace member without expanding the legacy scan list.

Files:

* `phase3_contract_amendment/namespace_contract_v2.json`
* `phase3_contract_amendment/amendment_invariant_check.json`
* If a canonical namespace contract exists, update it additively only.

Implementation Notes:

* Preserve `legacy_profile_fields_to_scan` exactly:

```text
compose_profile
legacy_compose_profile
fallback_profile
resolver_profile
```

* Add native membership for:

```text
selected_role
selected_role_precedence
selected_role_target
```

* Classification reconciliation:

```text
namespace classification = native member
semantic function = resolver legacy-origin path trace, where applicable
"legacy-origin" describes provenance/function, not namespace class
```

* Do not classify `selected_role` as legacy.
* Do not mutate canonical rows while amending the contract.

Validation:

* `legacy_profile_fields_to_scan` unchanged.
* `legacy_dependency_fields` unchanged, if present.
* Additive-only amendment check passes.
* `canonical_row_legacy_field_residue_count = 0` remains true.

---

### Change 5 - Phase 4 Resolver Code Disposition

Purpose:

Fence legacy label mapping out of default authority while preserving explicit diagnostic/compatibility reproducibility.

Files:

* `Iris/build/description/v2/tools/build/compose_layer3_body_profile.py`
* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tests/test_compose_layer3_text_v2.py`
* `phase4_resolver_disposition/resolver_source_hash_before_after.json`
* `phase4_resolver_disposition/default_path_reach_verification.json`
* `phase4_resolver_disposition/diagnostic_path_reach_verification.json`

Implementation Notes:

* Separate resolver paths conceptually:

```text
default -> native body_plan authority only, fail-loud on legacy labels
compat_legacy -> explicit compatibility mapping allowed
diagnostic_legacy -> explicit diagnostic mapping allowed under diagnostic root only
```

* Default mode must not call the legacy mapping table.
* Default mode must reject legacy labels such as `interaction_tool`, `interaction_component`, `interaction_output` when supplied as authority labels.
* `selected_role_precedence` must not override native `body_plan` in default authority.
* `selected_role_target` remains a native trace, not writer authority.

Validation:

* Add or update tests:

```text
test_default_resolver_rejects_legacy_labels
test_default_resolver_does_not_call_legacy_mapping
test_default_resolver_legacy_label_rejects_before_mapping_call
test_compat_legacy_resolver_allows_legacy_mapping
test_diagnostic_legacy_output_stays_in_diagnostic_root
test_canonical_artifact_not_overwritten_by_diagnostic
test_unknown_mode_fail_loud
test_selected_role_precedence_no_default_influence
```

Test file placement:

```text
Iris/build/description/v2/tests/test_resolver_compatibility_mapping_cleanup.py:
  test_default_resolver_rejects_legacy_labels
  test_default_resolver_does_not_call_legacy_mapping
  test_default_resolver_legacy_label_rejects_before_mapping_call
  test_compat_legacy_resolver_allows_legacy_mapping
  test_diagnostic_legacy_output_stays_in_diagnostic_root
  test_canonical_artifact_not_overwritten_by_diagnostic
  test_unknown_mode_fail_loud
  test_selected_role_precedence_no_default_influence

Iris/build/description/v2/tests/test_compose_layer3_text_v2.py:
  existing v2 resolver behavior updates only, if needed for compatibility
  with the new guard surface
```

Test purpose split:

* `test_default_resolver_rejects_legacy_labels` verifies input-stage fail-loud behavior.
* `test_default_resolver_does_not_call_legacy_mapping` verifies default call graph / instrumentation reach is zero.
* `test_default_resolver_legacy_label_rejects_before_mapping_call` verifies the reject happens before the mapping table can influence resolution.

---

### Change 6 - Phase 5 Dry-run Verification

Purpose:

Verify all invariant gates in an isolated simulation without canonical writes.

Files:

* `phase5_dry_run/dry_run_verification_report.json`
* `phase5_dry_run/invariant_preservation_matrix.json`

Implementation Notes:

* Dry-run must compare against Phase 1 baseline.
* Canonical writes must be disabled.
* Any rendered delta fails the round.

Validation:

Required pass gates:

```text
rendered_delta_count = 0
lua_hash_delta = 0
runtime_state_delta = 0
runtime_artifact_delta = 0
quality_state_delta = 0
publish_state_delta = 0
canonical_row_legacy_field_residue_count = 0
legacy_fallback_target_count = 0
default_path_legacy_fallback_reach_count = 0
default_adapter_dependency_count = 0
selected_role_precedence_default_influence_count = 0
selected_role_target_legacy_authority_count = 0
legacy_mapping_default_reach_count = 0
bridge_availability_delta = 0
```

---

### Change 7 - Phase 6 Approved Source/Contract Apply

Purpose:

Apply the approved namespace contract amendment and resolver disposition only after dry-run pass.

Files:

* `phase6_source_contract_apply/executor_script_hash.json`
* `phase6_source_contract_apply/source_contract_apply_log.json`
* Approved code/contract files from Changes 4 and 5.

Implementation Notes:

* Phase 6 is unconditional under the locked v0.2 disposition because `[OPEN-B-1] = relegate_to_diagnostic_only` and `[OPEN-B-2] = maintain_as_native_metadata`.
* Executor script hash must match the dry-run script hash.
* No rendered, Lua, runtime, quality, or publish artifacts may be written.

Validation:

* Apply log records changed files and unchanged surfaces.
* Post-apply parity is ready for Phase 7.

---

### Change 8 - Phase 7 Post-apply Verification

Purpose:

Re-run Phase 5 invariant gates against the applied state.

Files:

* `phase7_post_apply/post_apply_verification_report.json`
* `phase7_post_apply/regression_test_result.json`

Implementation Notes:

* Re-run the relevant Python test suite.
* Re-run resolver reachability checks.
* Re-run artifact hash checks.

Validation:

* Phase 5 invariant matrix re-passes post-apply.
* Relevant regression command exits with code 0.

---

### Change 9 - Phase 8 Adversarial Review

Purpose:

Review the round from a failure-first stance before top-doc closeout.

Files:

* `phase8_review/adversarial_review.md`

Implementation Notes:

* Review must check hidden default dependency, rendered delta, namespace contract drift, diagnostic write containment, and adapter-removal wording.

Validation:

* Critical findings: 0.
* Important findings: 0 unresolved.

---

### Change 10 - Phase 9 Documentation and Closeout

Purpose:

Record the cleanup result as a current governance read point without claiming runtime or release readiness.

Files:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `phase9_closeout/closeout_pass.json`

Implementation Notes:

* DECISIONS entry states:

```text
default resolver path is native body_plan authority only
legacy label mapping is not default authority
compat_legacy / diagnostic_legacy are explicit-only
selected_role_precedence is native diagnostic trace for resolver legacy-origin path
selected_role_target is resolved native target trace
selected_role is native namespace member
adapter removal is not declared
```

* ARCHITECTURE addendum must be consistent with 11-53, 11-58, 11-61, 11-62.
* ROADMAP Done/Next must not imply adapter removal or release readiness.
* `adapter_disposition_status` is a documentation note, not a machine-readable lifecycle enum. The only machine gates are the explicit boolean fields such as `adapter_removal_declared`.
* Closeout JSON must include:

```json
{
  "closeout_state": "closed_with_default_resolver_legacy_mapping_fenced",
  "adapter_disposition_status": "non-decision - adapter removal requires separate round",
  "rendered_delta": 0,
  "lua_hash_delta": 0,
  "runtime_state_delta": 0,
  "runtime_artifact_delta": 0,
  "quality_state_delta": 0,
  "publish_state_delta": 0,
  "bridge_availability_delta": 0,
  "default_path_legacy_fallback_reach_count": 0,
  "default_adapter_dependency_count": 0,
  "canonical_row_legacy_field_residue_count": 0,
  "legacy_fallback_target_count": 0,
  "selected_role_precedence_default_influence_count": 0,
  "selected_role_target_legacy_authority_count": 0,
  "legacy_mapping_default_reach_count": 0,
  "deployed_closeout_declared": false,
  "ready_for_release_declared": false,
  "adapter_removal_declared": false
}
```

Validation:

* Top docs updated only after Phase 7 and Phase 8 pass.
* No deployed closeout wording.
* No `ready_for_release` wording.
* No adapter removal declaration.

---

## 7. Validation Plan

### Automated Validation

Use the exact relevant commands and do not claim pass unless they exit with code 0.

Planned commands:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Round-specific scripts, if created:

```powershell
python -B Iris\build\description\v2\tools\build\build_resolver_compatibility_mapping_cleanup.py --dry-run
python -B Iris\build\description\v2\tools\build\validate_resolver_compatibility_mapping_cleanup.py --require-complete
```

Artifact/hash checks:

```powershell
git diff --stat
git diff -- docs\DECISIONS.md docs\ARCHITECTURE.md docs\ROADMAP.md
git diff -- Iris\build\description\v2\tools\build\compose_layer3_body_profile.py Iris\build\description\v2\tools\build\compose_layer3_text.py
```

Required measured gates:

```text
legacy_mapping_default_reach_count = 0
default_path_legacy_fallback_reach_count = 0
default_adapter_dependency_count = 0
selected_role_precedence_default_influence_count = 0
selected_role_target_legacy_authority_count = 0
rendered_delta_count = 0
lua_hash_delta = 0
runtime_artifact_delta = 0
quality_state_delta = 0
publish_state_delta = 0
canonical_row_legacy_field_residue_count = 0
bridge_availability_delta = 0
```

Measurement methodology:

```text
legacy_mapping_default_reach_count passes only if:
  static_default_reach_count = 0
  dynamic_default_reach_count = 0

static_default_reach_count:
  default resolver call graph has no path to the legacy mapping table

dynamic_default_reach_count:
  frozen 2105 default-mode dry-run records zero legacy mapping invocations
```

Forward fail-loud verification:

```text
test_default_resolver_rejects_legacy_labels:
  verifies default mode rejects legacy authority labels

test_default_resolver_does_not_call_legacy_mapping:
  verifies the default resolver has no mapping-table reach

test_default_resolver_legacy_label_rejects_before_mapping_call:
  verifies fail-loud occurs before compatibility mapping can affect output
```

### Manual Validation

* Inspect Phase 1 reachability report for default/non-default separation.
* Inspect namespace contract v2 amendment for additive-only behavior.
* Perform an author pre-closeout sanity check on Phase 8 outputs, confirming Critical findings are 0 and Important findings are 0 unresolved.
* Inspect top-doc wording for absent release, deployed, runtime QA, and adapter removal claims.

### Validation Limits

Not performed in this round:

* No manual in-game QA.
* No multiplayer validation.
* No long-session runtime validation.
* No deployment validation.
* No external mod compatibility sweep.
* No Browser/Wiki runtime consumer validation.
* No runtime Lua regeneration.

---

## 8. Risk Surface Touch

### Authority Surface

Touched. The round changes resolver authority classification by fencing legacy compatibility mapping out of default authority and formalizing `selected_role` native namespace membership.

### Runtime Behavior Surface

Existing 2105 rows: none intended. Rendered text, Lua payload, runtime state, Browser/Wiki consumer, and in-game behavior must remain unchanged. Any rendered delta blocks closeout.

Forward default resolver behavior: touched intentionally. Default mode adds fail-loud guards on legacy labels. For the frozen 2105 rows where prior closeout proved `default_path_legacy_fallback_reach_count = 0`, this is a no-op codification. For forward inputs, including future source expansion rows that supply legacy labels in default mode, fail-loud now fires. This forward-compat behavior change is the intended scope of `relegate_to_diagnostic_only`.

### Resolver Code Surface

Touched. This is a planning disclosure label for the resolver guard patch, not a new closeout taxonomy. It records that resolver source code may change while rendered/Lua/runtime artifacts remain immutable.

### Compatibility Surface

Touched but constrained. Legacy mapping is preserved only as explicit `compat_legacy` / `diagnostic_legacy` behavior. Historical diagnostic reproducibility is preserved while default authority stops accepting silent legacy mapping.

### Sealed Artifact Surface

Guarded immutable. Existing rendered, Lua, quality, publish, and bridge artifacts must remain byte-level unchanged. New artifacts are round-local diagnostics only.

### Public-Facing Output Surface

None. This round does not alter public rollout, release readiness, deployed state, tooltips, Browser/Wiki output, or in-game UI.

---

## 9. Risk Analysis

### Architecture Risk

* `selected_role` could be accidentally reclassified as legacy if the namespace amendment touches `legacy_profile_fields_to_scan`.
* Resolver code cleanup could blur the 11-53 adapter boundary if adapter removal wording enters the closeout.
* Documentation could overstate the cleanup as release readiness.

### Runtime Risk

* If default resolver currently relies on legacy mapping or `selected_role_precedence`, fail-loud guards may reveal hidden default dependency.
* Any rendered delta means this is no longer a governance-only cleanup.

### Compatibility Risk

* Fully deleting legacy mapping would damage diagnostic reproduction. This plan fences rather than deletes it.
* Existing tests that assert default legacy mapping acceptance must be revised only if Phase 1 proves default influence is zero and Phase 2 adopts fail-loud default mode.

### Regression Risk

* Diagnostic output could accidentally write canonical artifacts unless root guards are kept.
* The local checkout may lack prior closeout artifacts referenced by the roadmap; Phase 1 must block on missing evidence rather than substitute current sample data.

Branch trigger model:

Pre-change investigation triggers:

```text
legacy_mapping_default_reach_count > 0
or selected_role_precedence_default_influence_count > 0
or selected_role_target_default_influence_count > 0
```

These Phase 1 findings do not automatically close the round as blocked. They require Phase 2 to decide whether safe fencing can be implemented without authority or artifact delta.

Hard Branch C closeout triggers:

```text
rendered_delta_count > 0
or post_patch_legacy_mapping_default_reach_count > 0
or post_patch_selected_role_precedence_default_influence_count > 0
or post_patch_selected_role_target_legacy_authority_count > 0
or safe_fencing_cannot_be_implemented_without_authority_or_artifact_delta
```

Prior sealed invariant regression triggers:

```text
default_path_legacy_fallback_reach_count > 0
or default_adapter_dependency_count > 0
or canonical_row_legacy_field_residue_count > 0
or legacy_fallback_target_count > 0
or lua_hash_delta > 0
or runtime_state_delta > 0
or runtime_artifact_delta > 0
or quality_state_delta > 0
or publish_state_delta > 0
or bridge_availability_delta > 0
or any section 12 required final pass value fails
```

Branch C closeout:

```text
closed_with_cleanup_blocked_by_hidden_default_dependency
```

---

## 10. Rollback Plan

Rollback targets:

* Revert resolver guard changes in:

```text
Iris/build/description/v2/tools/build/compose_layer3_body_profile.py
Iris/build/description/v2/tools/build/compose_layer3_text.py
```

* Revert or supersede namespace contract amendment if validation fails.
* Remove or mark invalid round-local diagnostic artifacts under:

```text
Iris/build/description/v2/staging/compose_contract_migration/resolver_compatibility_mapping_cleanup_round/
```

* Revert tests added solely for failed guard behavior.

Rollback exclusions:

* Do not touch rendered baseline artifacts.
* Do not touch staged/workspace Lua artifacts.
* Do not touch quality or publish baseline.
* Do not touch Browser/Wiki runtime consumers.

Documentation rollback:

* If top-doc closeout was already written, add a correction addendum rather than deleting historical DECISIONS entries.
* Latest correction entry becomes the authoritative read point for the same issue.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance: Iris remains Lua/wiki-focused and does not take runtime mutation responsibility.
* Hub-and-spoke boundaries remain intact; this round does not create cross-module dependencies.
* Compose authority single-writer remains intact.
* Post-compose quality/publish decision stage remains single-writer.
* Lua bridge and runtime consumer remain render-only.
* Runtime/build-time separation remains intact.
* Compatibility adapter remains compose-internal and non-writer.
* Adapter removal requires a separate decision round.
* Namespace contract amendment is additive-only.
* `legacy_profile_fields_to_scan` remains unchanged.
* `selected_role` is not a legacy profile field.
* `selected_role_precedence` and `selected_role_target` namespace classification is native; any `legacy-origin` wording describes semantic provenance/function, not legacy namespace membership.
* Group B and later source expansion rounds must use native body_plan metadata in default mode. Legacy labels in default mode are expected to fail-loud after this round.
* 2105 baseline is immutable: active `2084`, silent `21`.
* `quality_baseline_v4` remains frozen.
* `rendered_delta_count = 0` is mandatory.
* Lua hash delta must remain zero against `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`.
* Bridge availability remains unchanged: `internal_only 617 / exposed 1467`.
* No deployed closeout, no `ready_for_release`, no manual QA pass.

---

## 12. Expected Closeout State

Expected closeout:

```text
closed_with_default_resolver_legacy_mapping_fenced
```

Closeout declaration:

```text
Resolver Compatibility Mapping Cleanup Round is closed with default resolver
legacy mapping fenced out of the default authority path.

Legacy label mapping, if retained, is explicit compat_legacy /
diagnostic_legacy only and is not a default authority source.

selected_role_precedence is dispositioned as native diagnostic trace for a
resolver legacy-origin path with zero default authority influence.

selected_role_target is dispositioned as resolved native target trace,
not writer authority, and is confirmed native namespace member via
namespace contract additive amendment.

Classification note: selected_role, selected_role_precedence, and
selected_role_target are native namespace members. Legacy-origin wording
describes resolver provenance/function only, not namespace classification.

rendered delta is 0. Lua hash is unchanged. Runtime artifacts are unchanged.
Adapter removal is not declared.
```

Required final pass values:

```text
legacy_mapping_default_reach_count = 0
default_path_legacy_fallback_reach_count = 0
default_adapter_dependency_count = 0
selected_role_precedence_default_influence_count = 0
selected_role_target_legacy_authority_count = 0
rendered_delta_count = 0
lua_hash_delta = 0
runtime_state_delta = 0
runtime_artifact_delta = 0
quality_state_delta = 0
publish_state_delta = 0
canonical_row_legacy_field_residue_count = 0
bridge_availability_delta = 0
bridge_availability_internal_only_count = 617
bridge_availability_exposed_count = 1467
adapter_removal_declared = false
deployed_closeout_declared = false
ready_for_release_declared = false
```

If any Branch C trigger is hit, expected closeout changes to:

```text
closed_with_cleanup_blocked_by_hidden_default_dependency
```

and a separate hidden dependency repair round must be opened before cleanup resumes.
