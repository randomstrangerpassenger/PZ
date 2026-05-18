# Iris DVF 3-3 Selected Role Bridge Impact Seal Round Plan

> 상태: Draft v0.2-plan  
> 기준일: 2026-05-16  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> authority input: `Iris DVF 3-3 Selected Role Bridge Impact Seal -> Diagnostic-only Resolver Compatibility Mapping Cleanup Roadmap` (2026-05-15 user-provided synthesis) and adversarial review FAIL feedback (2026-05-16)  
> 계획 형식: `docs/PLAN_TEMPLATE.md`  
> template attestation: `docs/PLAN_TEMPLATE.md` exists in this checkout and this plan follows its 1-12 section structure.  
> 실행 상태: planning authority only. 이 문서는 `Selected Role Bridge Impact Seal Round`만 다루며, Resolver Compatibility Mapping Cleanup 실행 계획이 아니다. 작성 시점에는 resolver code, runtime Lua, generated runtime artifacts, rendered text, quality/publish state, deployed state, top-doc closeout state를 변경하지 않는다.  
> supersession note: 2026-05-15 bundled draft that included diagnostic-only resolver cleanup phases is superseded. Round B must be planned separately only after a real Round A `sealed_pass` closeout artifact exists.

---

## 1. Objective

이번 execution plan의 목적은 Resolver Compatibility Mapping Cleanup을 열기 전에 남아 있는 `Selected Role Bridge Impact Seal Round` gate를 별도 governance-seal round로 측정 및 봉인하는 것이다.

핵심 문제 정의:

```text
complete-removal cleanup을 즉시 수행하는 문제가 아니라,
diagnostic-only cleanup을 열 수 있도록
selected_role bridge impact를 먼저 측정 및 봉인하는 문제다.
```

This plan is Round A only:

```text
Round A:
  Selected Role Bridge Impact Seal Round
  Phase 0-5
  measurement/seal only
  canonical source/artifact mutation 없음
```

Expected closeout target:

```text
Selected Role Bridge Impact Seal Round:
  closed_with_selected_role_bridge_impact_sealed
```

Forward boundary:

```text
Round A sealed_pass closeout may only create eligibility.
It must not create execution authorization for diagnostic-only resolver cleanup.
Diagnostic-only Resolver Compatibility Mapping Cleanup may be planned only after
a real Round A sealed_pass closeout artifact exists and a separate opening
decision is recorded.
```

The claim ceiling is limited. This plan does not claim diagnostic-only cleanup execution, complete-removal cleanup, adapter removal, runtime QA, deployed closeout, or `ready_for_release`.

---

## 2. Scope

In scope:

* Create the round root:

```text
Iris/build/description/v2/staging/compose_contract_migration/selected_role_bridge_impact_seal_round/
```

* Record explicit opening governance for selected-role bridge impact sealing.
* Declare the execution scale:

```text
execution_scale: governance-seal
review_required: true
closeout_ceremony: full closeout packet required
```

* Measure and classify the fields:

```text
selected_role
selected_role_precedence
selected_role_target
```

* Snapshot `legacy_profile_fields_to_scan` and `legacy_dependency_fields`.
* Measure whether selected-role fields affect default authority or legacy authority.
* Verify six-axis invariant delta:

```text
rendered = 0
lua = 0
runtime = 0
quality_state = 0
publish_state = 0
bridge_availability = 0
```

* Run adversarial review.
* Close this round as `sealed_pass`, `sealed_with_non_zero_finding`, or `inconclusive`.
* Update top docs only after closeout evidence exists.

### Explicitly Out Of Scope

* Diagnostic-only Resolver Compatibility Mapping Cleanup planning or execution.
* Any Phase 6-9 cleanup phase.
* Resolver compatibility mapping default-path isolation patch.
* Resolver compatibility mapping artifact topology predefinition.
* Complete-removal cleanup.
* Physical deletion of resolver compatibility mapping tables.
* Compatibility adapter removal.
* `selected_role_precedence` or `selected_role_target` row-count reduction.
* Frozen 2105 byte-level baseline recovery or reconstruction.
* Historical sealed Lua hash `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` byte artifact restoration.
* `body_source_overlay` 2105-row reconstruction.
* Runtime Lua regeneration.
* Monolith runtime authority restoration.
* Runtime-side compose or rewrite.
* Manual in-game QA pass.
* Deployed closeout.
* `ready_for_release` declaration.
* `quality_baseline_v4 -> v5` cutover.
* Source expansion Group B or other holdback work.

---

## 3. Non-Goals

This plan does not attempt to:

* Reopen the Frozen 2105 Baseline Reconstruction Round.
* Convert diagnostic-only cleanup eligibility into cleanup authorization.
* Convert diagnostic-only isolation into complete-removal cleanup.
* Reclassify selected-role fields as legacy profile fields.
* Add selected-role fields to `legacy_profile_fields_to_scan` or `legacy_dependency_fields`.
* Use document-only counts `selected_role_precedence 288` and `selected_role_target 894` as sealed cleanup measurements.
* Delete or weaken diagnostic/compat historical reproduction paths.
* Modify `compose_profiles_v2.json + body_plan` default authority.
* Change rendered strings, staged/workspace Lua chunks, runtime consumer behavior, quality state, publish state, or bridge availability.
* Claim external mod expansion readiness, Workshop deployment, or release readiness.
* Pre-write the diagnostic-only resolver cleanup closeout JSON. That JSON belongs to a later separate plan, if opened.

---

## 4. Assumptions

* `docs/Philosophy.md` remains the top authority for Pulse ecosystem boundaries.
* `docs/DECISIONS.md` same-topic later entries are authoritative over earlier historical trace.
* `docs/DECISIONS.md` 2026-05-15 Frozen 2105 closeout remains authoritative:

```text
diagnostic_only_isolation frozen-baseline prerequisite = A1_sufficient
complete_removal frozen-baseline prerequisite = blocked_reconstruction_incomplete
```

* `docs/DECISIONS.md` 2026-05-15 selected-role gate entry remains authoritative that diagnostic-only Resolver Compatibility Mapping Cleanup cannot open before selected-role bridge impact is sealed.
* `docs/ARCHITECTURE.md` 11-62 remains authoritative for current runtime/build state:

```text
active_native_profile_count = 2084
legacy_fallback_target_count = 0
default_path_legacy_fallback_reach_count = 0
canonical_row_legacy_field_residue_count = 0
runtime state = ready_for_in_game_validation
```

* `docs/ARCHITECTURE.md` 11-69 remains authoritative that selected-role bridge impact is a separate resolver cleanup opening gate.
* `docs/ROADMAP.md` Section 35 remains authoritative that selected-role seal is the Next gate, not already completed evidence.
* The binding opening instruction for this plan is `docs/ROADMAP.md` Section 35 Next plus `docs/DECISIONS.md` 2026-05-15 second selected-role gate entry.
* The current default authority path remains:

```text
compose_profiles_v2.json + body_plan
  -> rendered flat string
  -> quality/publish decision stage
  -> Lua bridge
  -> runtime consumer
```

* `sentence_plan` remains compatibility/diagnostic input only. Implicit legacy fallback remains forbidden.
* Measurement work must be offline diagnostic / build-time only and must not mutate sealed source or runtime-facing artifact.
* If any required baseline artifact is absent, the relevant phase reports `blocked_missing_baseline_artifact` or `inconclusive` rather than reconstructing unstated evidence.
* Diagnostic-only Resolver Compatibility Mapping Cleanup is outside this plan and requires a later separate plan after a real Round A `sealed_pass` closeout artifact exists.

---

## 5. Repository Areas Affected

### Code

No production code changes are planned.

Read-only inspection surfaces:

* `Iris/build/description/v2/tools/build/compose_layer3_body_profile.py`
* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tests/test_compose_layer3_text_v2.py`

Round-local diagnostic scripts, if needed, must be isolated under the round root rather than committed as shared build tooling:

```text
Iris/build/description/v2/staging/compose_contract_migration/selected_role_bridge_impact_seal_round/tools/
  measure_selected_role_bridge_impact.py
  validate_selected_role_bridge_impact_seal.py
```

If a later executor chooses to add shared scripts under `Iris/build/description/v2/tools/build/`, that is no longer measurement-only and must be declared as a build-tooling code change with `changed_files_manifest.json`, rollback coverage, and review.

### Docs

Planning and closeout docs:

* `docs/Iris/iris-dvf-3-3-selected-role-bridge-impact-seal-round-plan.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/REVIEW_TEMPLATE.md` as the adversarial review template source.
* Optional closeout walkthrough after execution:

```text
docs/Iris/Done/Walkthrough/iris-dvf-3-3-selected-role-bridge-impact-seal-round-walkthrough.md
```

Top-doc closeout form:

* `docs/DECISIONS.md`: new dated entry with `status / decision / reason / impact` shape.
* `docs/ARCHITECTURE.md`: new Section 11-70 for selected-role bridge impact seal closeout. If closeout is `inconclusive`, update 11-69 instead to keep the gate pending.
* `docs/ROADMAP.md`: new Section 36 addendum for this round's closeout state and next/hold status.

### Config

No build, package, Gradle, Python environment, or Lua runtime config changes are planned.

### Generated Artifacts

Round artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/selected_role_bridge_impact_seal_round/
```

Required topology:

```text
phase0_opening/
  opening_decision.md
  scope_lock.json
  authority_matrix.json

phase1_static_inventory/
  selected_role_namespace_classification_inventory.json
  legacy_field_list_snapshot.json

phase2_dynamic_trace/
  selected_role_precedence_default_influence_measurement.json
  selected_role_target_legacy_authority_measurement.json
  selected_role_bridge_impact_measurement_methodology.md

phase3_six_axis_invariants/
  six_axis_invariant_delta_measurement.json
  baseline_read_point_map.json
  read_only_procedure_trace.md

phase4_adversarial_review/
  phase4_adversarial_review.md

phase5_closeout/
  closeout_pass.json
  closeout.md
  seal_question_answer_mapping.md
```

No diagnostic-only resolver cleanup artifact topology is defined by this plan.

---

## 6. Planned Changes

### Change 1 - Phase 0 Opening and Governance Authority

Purpose:

Open `selected_role_bridge_impact_seal_round` as a separate diagnostic-only prerequisite seal round and prevent scope drift before measurement begins.

Files:

* `selected_role_bridge_impact_seal_round/phase0_opening/opening_decision.md`
* `selected_role_bridge_impact_seal_round/phase0_opening/scope_lock.json`
* `selected_role_bridge_impact_seal_round/phase0_opening/authority_matrix.json`
* `docs/DECISIONS.md`, only at closeout if the round reaches a valid closeout branch.

Implementation Notes:

* Record binding opening authority:

```text
ROADMAP §35 Next binding:
  "Selected Role Bridge Impact Seal Round를 별도 implementation plan으로 작성하거나 실행한다"

DECISIONS 2026-05-15 second selected-role gate entry:
  Selected Role Bridge Impact Seal Round is required before diagnostic-only resolver cleanup
```

* Record that this is a new selected-role bridge impact opening, not a reopening of the terminal sealed Frozen 2105 Baseline Reconstruction Round.
* Declare:

```text
cleanup_kind: diagnostic_only_prerequisite
execution_scale: governance-seal
review_required: true
closeout_ceremony: full closeout packet required
complete_removal: false
runtime_lua_regeneration: false
adapter_removal: false
ready_for_release: false
resolver_cleanup_execution: false
```

* Scope-lock the six-axis required delta policy to `0`.
* Record that diagnostic-only resolver cleanup remains out of scope and requires a future separate plan after a real `sealed_pass` artifact exists.

Validation:

* Cross-reference `docs/Philosophy.md`, `docs/DECISIONS.md` 2026-05-15 second selected-role gate entry, `docs/ARCHITECTURE.md` 11-69, and `docs/ROADMAP.md` Section 35.
* Confirm selected-role fields are seal targets, not cleanup deletion targets.
* Confirm all non-goals are reflected in the opening decision.

---

### Change 2 - Phase 1 Static Inventory: Namespace Classification and Legacy Field Lists

Purpose:

Create a static inventory that classifies selected-role occurrences and seals whether selected-role fields are absent from legacy scan/dependency field lists.

Files:

* `selected_role_bridge_impact_seal_round/phase1_static_inventory/selected_role_namespace_classification_inventory.json`
* `selected_role_bridge_impact_seal_round/phase1_static_inventory/legacy_field_list_snapshot.json`

Implementation Notes:

* Search all repository references to:

```text
selected_role
selected_role_precedence
selected_role_target
```

* Classify each occurrence by source type:

```text
canonical source
generated artifact
diagnostic report
test fixture
docs/readpoint
script logic
resolver input
runtime Lua
```

* Classify each occurrence by namespace:

```text
native_metadata
native_trace
legacy_profile_field
legacy_dependency_field
undetermined
```

* Snapshot current `legacy_profile_fields_to_scan` and `legacy_dependency_fields`.
* Record mutation authority for each occurrence.
* Treat `undetermined` as an escalation input, not an automatic pass.

Validation:

* Total discovered references equals total classified references.
* `legacy_profile_fields_to_scan contains selected_role* = false`.
* `legacy_dependency_fields contains selected_role* = false`.
* Runtime Lua selected-role occurrence count is reported.
* Default path reader count is reported.

---

### Change 3 - Phase 2 Dynamic Trace: Default Authority Influence and Legacy Authority Measurement

Purpose:

Measure whether selected-role fields influence default compose authority or operate as legacy authority.

Files:

* `selected_role_bridge_impact_seal_round/phase2_dynamic_trace/selected_role_precedence_default_influence_measurement.json`
* `selected_role_bridge_impact_seal_round/phase2_dynamic_trace/selected_role_target_legacy_authority_measurement.json`
* `selected_role_bridge_impact_seal_round/phase2_dynamic_trace/selected_role_bridge_impact_measurement_methodology.md`

Implementation Notes:

* Build read-only masked diagnostic inputs under the isolated round root.
* Do not overwrite canonical staged artifacts.
* Methodology must define `default influence` and `legacy authority` before measurement.
* Required minimum definitions:

```text
default influence:
  selected_role* field masking changes body_plan selection, section selection,
  rendered string, Lua bridge payload, quality/publish/bridge availability,
  or default resolver branch outcome.

legacy authority:
  selected_role* participates in legacy label -> native body profile mapping,
  fallback eligibility, legacy scan field classification,
  or default-path compatibility decision.
```

* Measure:

```text
selected_role_precedence_default_influence_count
selected_role_target_legacy_authority_count
```

* Include trace evidence with code path, row identity, and decision step.
* If either count is non-zero, proceed to `sealed_with_non_zero_finding` closeout branch rather than forcing a cleanup pass.

Validation:

* Measurement is deterministic.
* Masking output remains under the isolated diagnostic root.
* Canonical artifacts are unchanged.
* Methodology is explicit enough for adversarial review.

---

### Change 4 - Phase 3 Six-Axis Invariant Delta Measurement

Purpose:

Prove the measurement process itself does not mutate rendered output, Lua artifacts, runtime state, quality state, publish state, or bridge availability.

Files:

* `selected_role_bridge_impact_seal_round/phase3_six_axis_invariants/six_axis_invariant_delta_measurement.json`
* `selected_role_bridge_impact_seal_round/phase3_six_axis_invariants/baseline_read_point_map.json`
* `selected_role_bridge_impact_seal_round/phase3_six_axis_invariants/read_only_procedure_trace.md`

Implementation Notes:

* Capture pre/post hashes and read points.
* Baseline axes must be explicitly mapped:

```text
rendered:
  current 2105 rendered output artifact hash

Lua:
  Iris/Data/IrisLayer3DataChunks.lua manifest hash
  Iris/Data/IrisLayer3DataChunks/Chunk001..011.lua hashes

runtime:
  authority read: ARCHITECTURE 11-62
  artifact evidence:
    Iris/Data/IrisLayer3DataChunks.lua manifest hash
    Iris/Data/IrisLayer3DataChunks/Chunk001..011.lua hashes
    installed monolith path absent check, if installed runtime path is available

quality:
  quality_baseline_v4 frozen snapshot

publish:
  quality_publish_decision baseline

bridge availability:
  resolver source file hash
  compose_layer3_body_profile.py selected-role resolution region sub-hash
  compose_layer3_text.py compat/diagnostic mode boundary region sub-hash, if present
```

* If a named sub-hash region is absent in the current checkout, record `not_applicable` with a separate invariant explaining why the boundary is not represented by that file region.
* Record that runtime deployable source remains chunk manifest plus chunks.
* Record `monolith_restoration = false`.

Validation:

* All six delta counts are `0`.
* Row count unchanged.
* Runtime deployable topology remains chunks-only.
* No runtime Lua regeneration occurs.
* Bridge availability measurement has a hashable source or an explicit invariant for any non-hashable boundary.

---

### Change 5 - Phase 4 Adversarial Review

Purpose:

Review Phase 0-3 artifacts against governance, methodology, and fail-loud criteria before closeout.

Files:

* `selected_role_bridge_impact_seal_round/phase4_adversarial_review/phase4_adversarial_review.md`

Implementation Notes:

* Use `docs/REVIEW_TEMPLATE.md`.
* Classify findings as Critical, Important, or Minor.
* Review:

```text
Philosophy.md / DECISIONS consistency
scope drift
missing validation
governance compliance
Phase 2 methodology definitions
Round B exclusion
```

Validation:

* PASS requires Critical `0` and Important `0`.
* Any contested methodology that invalidates measurement sends the round to `inconclusive`.

---

### Change 6 - Phase 5 Selected Role Bridge Impact Seal Closeout

Purpose:

Close the selected-role bridge impact seal round and determine whether a future diagnostic-only cleanup plan may be drafted.

Files:

* `selected_role_bridge_impact_seal_round/phase5_closeout/closeout_pass.json`
* `selected_role_bridge_impact_seal_round/phase5_closeout/closeout.md`
* `selected_role_bridge_impact_seal_round/phase5_closeout/seal_question_answer_mapping.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Implementation Notes:

Closeout branches:

```text
sealed_pass:
  all measured influence/authority counts are 0
  selected-role namespace is native
  legacy lists unchanged and do not absorb selected-role fields
  six-axis deltas are 0
  adversarial review PASS

sealed_with_non_zero_finding:
  one or more measurements are non-zero or classification is not native
  result is measurement-backed
  diagnostic-only cleanup opening is not enabled automatically

inconclusive:
  required measurement, artifact, classification, or review evidence is incomplete
  rerun or holdback required
```

Required closeout sentence:

```text
Round A closeout may only create eligibility.
It must not create execution authorization for Round B.
```

Top-doc addendum form:

* `docs/DECISIONS.md`: new dated entry using status / decision / reason / impact. It must state whether the round closed `sealed_pass`, `sealed_with_non_zero_finding`, or `inconclusive`.
* `docs/ARCHITECTURE.md`: expected `sealed_pass` branch adds Section 11-70. Non-pass branches update 11-69 and keep the gate pending.
* `docs/ROADMAP.md`: Section 36 addendum records Done/Next/Hold. If `sealed_pass`, Next may be "write separate diagnostic-only resolver cleanup plan"; it must not say cleanup execution is authorized.

Validation:

* Closeout ceiling is `selected_role_bridge_impact_sealed`.
* `diagnostic_only_cleanup_opening_automatic = false`.
* `complete_removal_cleanup_opening_allowed = false`.
* `ready_for_release = false`.
* Runtime QA remains separate.
* All five seal questions have answer mapping.

---

## 7. Validation Plan

### Automated Validation

Round validation:

* Static reference inventory using `rg` or an equivalent deterministic scanner.
* Deterministic selected-role masking and trace measurement script, if created.
* Six-axis pre/post hash and count comparison.
* Artifact root isolation checks.
* Canonical artifact unchanged checks.

Candidate command shape, only if round-local scripts are created:

```powershell
python -B Iris\build\description\v2\staging\compose_contract_migration\selected_role_bridge_impact_seal_round\tools\measure_selected_role_bridge_impact.py --round-root Iris\build\description\v2\staging\compose_contract_migration\selected_role_bridge_impact_seal_round
python -B Iris\build\description\v2\staging\compose_contract_migration\selected_role_bridge_impact_seal_round\tools\validate_selected_role_bridge_impact_seal.py --require-complete
```

Existing repository tests are optional for Round A unless the executor creates shared tooling or touches existing code. If existing code is touched despite this plan's measurement-only scope, run:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Lua syntax validation is required only if a Lua file is touched, which this plan forbids:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Do not claim validation passed unless the exact relevant command exits with code `0`.

### Manual Validation

* Adversarial review using `docs/REVIEW_TEMPLATE.md`.
* Closeout wording review against claim boundary.
* Top-doc addendum review for DECISIONS/ARCHITECTURE/ROADMAP consistency.
* Confirm no diagnostic-only cleanup phase or artifact topology is introduced by this plan.

### Validation Limits

This plan does not perform or claim:

* Diagnostic-only resolver cleanup validation.
* Resolver default-path isolation validation.
* Manual in-game validation.
* Long-session runtime validation.
* Multiplayer validation.
* Packaging validation.
* Workshop deployment validation.
* External mod compatibility sweep.
* Complete-removal cleanup safety validation.
* Byte-level frozen 2105 baseline restoration validation.

---

## 8. Risk Surface Touch

### Authority Surface

Touched. This round measures selected-role bridge authority impact and may seal selected-role namespace classification. It does not authorize resolver cleanup execution and does not change the default authority source from `compose_profiles_v2.json + body_plan`.

### Runtime Behavior Surface

None. Measurement-only and build-time diagnostic only.

### Compatibility Surface

Guarded immutable. Explicit diagnostic/compat mapping is not modified, deleted, or preplanned for isolation here.

### Sealed Artifact Surface

Guarded immutable. Sealed artifacts are read as baselines and must not be overwritten by measurement or validation.

### Public-Facing Output Surface

None. No rendered text, Lua bridge output, public release artifact, Workshop package, or user-facing runtime claim changes are planned.

---

## 9. Risk Analysis

### Architecture Risk

* Diagnostic-only cleanup eligibility could be misread as cleanup authorization.
* Selected-role fields could be accidentally treated as legacy profile residue rather than native trace/metadata.
* Prior document readpoint counts `288 / 894` could be mistaken for sealed measurement evidence.
* A future cleanup plan could cite this closeout too broadly if the Phase 5 claim boundary is weak.

### Runtime Risk

* Runtime Lua hash or chunk topology could change if validation tooling writes to runtime-facing locations.
* Monolith runtime authority could be accidentally restored while trying to compare historical baselines.
* A generated artifact could be touched during what should be read-only measurement.

### Compatibility Risk

* Misclassifying selected-role fields as legacy could weaken historical diagnostic interpretation.
* Failing to distinguish diagnostic references from canonical source references could make the inventory evidence misleading.

### Regression Risk

* Rendered output delta could be normalized as expected seal churn, which is forbidden here.
* Quality or publish state could drift if measurement validation reuses writer-capable tooling.
* Bridge availability counts could shift if measurement tooling invokes writer paths instead of read-only diagnostics.

---

## 10. Rollback Plan

Round rollback:

* This round is measurement/seal only.
* All artifacts are isolated under `selected_role_bridge_impact_seal_round/`.
* If validation fails before top-doc closeout, delete or mark the round artifact root as invalid and do not update DECISIONS/ARCHITECTURE/ROADMAP.
* If a defect is found after closeout, add a superseding top-doc decision and open a follow-up seal/review round. Do not rewrite historical evidence in place.

Hard rollback triggers:

```text
any six-axis delta > 0
selected_role fields absorbed into legacy scan field lists
measurement mutates sealed artifacts
diagnostic-only cleanup phases or artifacts are introduced in this round
```

For this planning document itself, rollback is a normal documentation revert or a superseding plan note. No runtime or generated artifact rollback is needed from writing this file.

---

## 11. Governance Constraints

* `docs/Philosophy.md` remains top authority.
* Later same-topic `docs/DECISIONS.md` entries are authoritative read points.
* This plan supersedes the bundled 2026-05-15 draft that included diagnostic-only resolver cleanup phases.
* Diagnostic-only Resolver Compatibility Mapping Cleanup is outside this plan.
* A later cleanup plan may be written only after a real `sealed_pass` closeout artifact exists.
* Runtime/build-time separation must remain intact.
* Runtime Lua must not interpret resolver compatibility mapping or selected-role namespace.
* Lua/runtime consumer remains render-only and consumes rendered artifacts only.
* Default compose authority path remains `compose_profiles_v2.json + body_plan`.
* Diagnostic/compat path historical reproducibility must be preserved.
* Complete-removal cleanup remains blocked by the frozen 2105 byte-level baseline problem.
* Measurement must not mutate canonical source or sealed artifacts.
* Any non-zero selected-role default influence or legacy authority count is a fail-loud branch input, not a value to normalize away.
* Top-doc changes happen only after closeout evidence exists.
* No validation pass may be claimed without the exact relevant command exiting `0`.

---

## 12. Expected Closeout State

Expected `sealed_pass` closeout:

```json
{
  "round": "selected_role_bridge_impact_seal_round",
  "closeout_state": "closed_with_selected_role_bridge_impact_sealed",
  "closeout_branch": "sealed_pass",
  "selected_role_namespace": "native_trace_metadata",
  "selected_role_precedence_default_influence_count": 0,
  "selected_role_target_legacy_authority_count": 0,
  "legacy_profile_fields_to_scan_absorbed_selected_role": false,
  "legacy_dependency_fields_absorbed_selected_role": false,
  "rendered_delta_count": 0,
  "lua_delta_count": 0,
  "runtime_delta_count": 0,
  "quality_state_delta_count": 0,
  "publish_state_delta_count": 0,
  "bridge_availability_delta_count": 0,
  "diagnostic_only_cleanup_opening_eligible": true,
  "diagnostic_only_cleanup_opening_automatic": false,
  "diagnostic_only_cleanup_execution_authorized": false,
  "complete_removal_cleanup_opening_allowed": false,
  "manual_in_game_qa_pass": false,
  "ready_for_release": false
}
```

If any selected-role measurement is non-zero or classification is not native, expected closeout becomes:

```text
sealed_with_non_zero_finding
```

In that branch, diagnostic-only cleanup opening is not enabled automatically and requires a separate decision based on the non-zero evidence.

If required measurement evidence is incomplete, expected closeout becomes:

```text
inconclusive
```

In that branch, no cleanup plan should be drafted from this round's evidence.

This plan intentionally has no Round B expected closeout. Diagnostic-only Resolver Compatibility Mapping Cleanup must receive its own separate plan only after this round produces a real `sealed_pass` closeout artifact.
