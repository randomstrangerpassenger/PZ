# Iris DVF 3-3 Frozen 2105 Baseline Reconstruction Round Plan

> 상태: Draft v0.3-plan  
> 기준일: 2026-05-15  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> authority input: `Frozen 2105 Baseline Reconstruction Round - 종합 검토 로드맵` (2026-05-14 user-provided synthesis)  
> 계획 형식: `docs/PLAN_TEMPLATE.md`  
> template attestation: `docs/PLAN_TEMPLATE.md` exists in this checkout and this plan follows its 1-12 section structure.  
> 실행 상태: executed 2026-05-15 with closeout branch `blocked_reconstruction_incomplete`. 이 문서는 Resolver Compatibility Mapping Cleanup Round를 실행하지 않았으며, execution closeout 기준 resolver code, runtime Lua, chunk runtime topology, sealed measurement state는 변경하지 않았다. Closeout authority는 `Iris/build/description/v2/staging/compose_contract_migration/frozen_2105_baseline_reconstruction_round/phase6_closeout/frozen_2105_baseline_prerequisite_closeout.*` 및 `docs/DECISIONS.md` / `docs/ROADMAP.md`의 2026-05-15 addendum이다.

---

## 1. Objective

이번 execution plan의 목적은 Resolver Compatibility Mapping Cleanup Round를 열기 전에 필요한 frozen `2105` verification prerequisite를 결정하고, 필요한 경우에만 cleanup 검증용 `reconstructed_frozen_2105_baseline`을 isolated lane에서 재구성해 봉인하는 것이다.

이 round의 핵심 질문은 두 가지다.

1. Cleanup invariant preservation contract는 measurement reproducibility만으로 충분한가, 아니면 byte-level baseline identity가 별도 prerequisite인가.
2. Byte-level baseline identity가 필요하다면, 그 baseline referent는 historical sealed staged Lua monolith, current chunks-only active runtime topology, 또는 v4.1 이전 historical workspace monolith 중 무엇인가.

Most important boundary:

```text
This round reconstructs and seals a new frozen 2105 baseline
for cleanup verification only if byte-level identity is
determined to be a necessary prereq.

It does not claim recovery of the missing original byte-level
artifact unless deterministic regeneration reproduces the
historical sealed hash exactly.
```

Expected branch states:

```text
Branch A1:
  closed_with_prereq_decision_obviated_reconstruction_for_diagnostic_only_cleanup
  byte-level reconstruction obviated for diagnostic-only cleanup only
  complete removal cleanup remains blocked
  cleanup opening still requires selected_role bridge impact seal

Branch A2:
  closed_with_prereq_decision_obviated_reconstruction_for_complete_removal_cleanup
  byte-level reconstruction obviated for complete removal cleanup only
  requires stronger proof set than A1
  expected to be exceptional; if proof cannot distinguish complete removal
  safety from diagnostic-only safety, fall back to A3
  cleanup opening still requires selected_role bridge impact seal

Branch A3:
  decision_measurement_reproducibility_insufficient
  reconstruction required -> Phase 2 proceeds

Branch B:
  closed_with_byte_equivalent_reconstructed_frozen_2105_baseline_sealed
  byte-level baseline prerequisite closed
  cleanup opening still requires selected_role bridge impact seal

Branch C:
  closed_with_invariant_equivalent_reconstructed_baseline_but_no_byte_equivalence
  cleanup blocked pending hash mismatch / referent equivalence resolution round

Branch D:
  blocked_reconstruction_incomplete
  or closed_with_reconstruction_hash_mismatch_failure_handoff_pending
  cleanup blocked
```

---

## 2. Scope

This round is a prerequisite decision and conditional reconstruction round. It is not the cleanup round itself.

In scope:

* Phase 0 opening decision and scope lock.
* Cleanup validation requirement decision: measurement reproducibility versus byte-level identity prerequisite.
* Conditional referent, writer authority, and hash equivalence policy sealing.
* Conditional isolated reconstruction execution.
* Conditional invariant verification and hash equivalence sealing.
* Adversarial review.
* Closeout and explicit baseline prerequisite / selected-role follow-up gate decision.
* Round-local artifacts under:

```text
Iris/build/description/v2/staging/compose_contract_migration/frozen_2105_baseline_reconstruction_round/
```

Canonical current baseline read:

```text
persisted_old_profile_count         = 2105
active_old_profile_count            = 0
active_native_profile_count         = 2084
silent_old_profile_count            = 21

non_fallback_active_metadata_swap   = 2006
fallback_dependent_active           = 78
silent_metadata_inventory           = 21
mechanical_ready                    = 78
schema_gap                          = 0

legacy_fallback_target_count                = 0
default_path_legacy_fallback_reach_count    = 0
canonical_row_legacy_field_residue_count    = 0
rendered_output_delta                       = 0

quality_baseline_v4:
  strong 1316 / adequate 0 / weak 768

source distribution:
  BODY_LACKS_ITEM_SPECIFIC_USE 617
  FUNCTION_NARROW 7
  none 1481

bridge availability:
  internal_only 617 / exposed 1467

runtime path:
  cluster_summary 2040 / identity_fallback 17 / role_fallback 48

historical sealed staged Lua hash:
  0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062
```

The `Phase 0 sealed baseline Lua hash` value `9c5ceebea334277cb9b235e67fdfed8f2089d3eb1b7a2519ada424be11945ee9` is not a canonical current baseline target in this plan unless Phase 2 manifests it with `hash_value / artifact_path / artifact_type / referent_class / authority_class / allowed_use / forbidden_use / why_not_historical_039027`. Until then its authority class is `diagnostic_reference`, its allowed use is historical comparison only, and its forbidden use is cleanup baseline substitution.

Distribution values are not remeasured as new authority in this round. They are checked only as preservation constraints against existing sealed readpoints. Any mismatch blocks cleanup and does not create a new distribution seal.

Runtime topology scope:

* Current Layer 3 deployable data authority remains `Iris/Data/IrisLayer3DataChunks.lua` plus `Iris/Data/IrisLayer3DataChunks/Chunk001..011.lua`.
* `Iris/Data/IrisLayer3Data.lua` monolith is not active deployable runtime authority after v4.1 closeout.
* `Iris/Data/layer3_renderer.lua` must continue to read the chunk manifest as default source and must not reopen monolith fallback.

### Explicitly Out Of Scope

* Resolver Compatibility Mapping Cleanup execution.
* Adapter removal execution.
* Silent `21` metadata intake or cleanup.
* Runtime QA pass.
* Manual in-game validation pass.
* Deployed closeout.
* `ready_for_release` declaration.
* `quality_baseline_v4 -> v5` cutover.
* Runtime-side compose or rewrite.
* Compose-external repair.
* Facts modification.
* Source, section, overlap, bridge, or quality distribution remeasurement.
* `selected_role_precedence` / `selected_role_target` 신규 봉인.
* v4.1 closeout이 deprecated한 monolith path 재도입.
* Pre-migration `2105` source를 post-migration frozen baseline으로 간주.

---

## 3. Non-Goals

This plan does not attempt to:

* Execute resolver compatibility mapping cleanup.
* Remove or physically delete the compatibility adapter.
* Reintroduce the Layer 3 monolith into active workspace runtime layout.
* Treat current chunks-only runtime topology as byte-identical evidence for the historical monolith hash without an explicit referent decision.
* Claim recovery of the missing original byte-level artifact unless `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` is reproduced exactly.
* Treat rejected candidates as canonical reconstruction input.
* Use document readpoints as byte-level substitute artifacts.
* Reopen or redefine sealed measurement counts.
* Seal `selected_role_precedence` / `selected_role_target` counts from unverified working-session references.
* Declare runtime QA, deployed status, or release readiness.

Terminology locked for the round:

```text
historical_readpoint
missing_original_byte_artifact
reconstructed_frozen_2105_baseline
byte_equivalent_reconstruction
invariant_equivalent_reconstruction
```

---

## 4. Assumptions

* `docs/Philosophy.md` remains the constitutional top authority.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` current readpoints remain authoritative unless later entries supersede them.
* Later entries on the same issue supersede earlier entries.
* `docs/ARCHITECTURE.md` 11-61 remains authoritative that adapter removal execution and resolver compatibility mapping cleanup are separate follow-up rounds.
* `docs/ARCHITECTURE.md` 11-62 remains authoritative that active source-shape debt is closed while resolver compatibility mapping remains for explicit diagnostic/compat path.
* `docs/ARCHITECTURE.md` 11-68 and `docs/DECISIONS.md` 2026-05-12 remain authoritative that Layer 3 deployable runtime data is chunks-only and monolith fallback must not be reopened.
* `docs/DECISIONS.md` 2026-04-22 remains authoritative for the historical staged Lua hash `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`.
* The sealed Lua hash `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` captures the body-plan staged Lua output layer from the 2026-04-22 staged/static closeout.
* `docs/DECISIONS.md` 2026-04-25 remains authoritative for metadata migration closeout counts and invariant claims, including the statement that the sealed staged Lua hash remained unchanged after active metadata migration.
* Phase 3 expected measurements are metadata migration post-state preservation constraints cross-referenced against the 2026-04-25 seal, not a new authority remeasurement. The byte hash target and the post-migration measurements are distinct layers that must both be satisfied for Branch B.
* If the 2026-04-22 hash layer and 2026-04-25 metadata post-state layer cannot both be satisfied, the conflict blocks cleanup. A hash match with measurement mismatch is Branch D. A measurement match with hash mismatch is Branch C or D according to the Phase 2 hash equivalence policy. No historical reseal is allowed without an explicit Phase 2 policy branch and top-doc disclosure.
* `docs/Iris/iris-dvf-3-3-frozen-2105-baseline-recovery-analysis.md` is a current analysis artifact, not a top-doc authority, and its `blocked_missing_byte_level_frozen_2105_baseline` assessment is an input to Phase 1.
* The recovery-analysis assessment is challengeable evidence input. Phase 1 must validate or reject its reasoning within the evidence chain and must not treat it as automatically adopted.
* Existing `docs/Iris/iris-dvf-3-3-resolver-compatibility-mapping-cleanup-round-plan.md` is not executed by this round and remains blocked until this round closes an eligible baseline branch and a separate Selected Role Bridge Impact Seal Round closes the selected-role cleanup gate.
* The selected-role axis is intentionally unsealed in this round. The document readpoint values `288 / 894`, if referenced, are unverified working-session references, not sealed measurements, and shall not be cited as evidence in this round.

---

## 5. Repository Areas Affected

### Code

No code changes are required to write this plan.

Candidate execution surfaces only if Phase 1 adopts the reconstruction-required branch and Phase 2 chooses a reconstruction writer that requires tooling:

* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tools/build/compose_layer3_body_profile.py`
* New round-local reconstruction or validation scripts under `Iris/build/description/v2/tools/build/`
* New focused tests under `Iris/build/description/v2/tests/`

### Docs

Planning and conditional closeout surfaces:

* `docs/Iris/iris-dvf-3-3-frozen-2105-baseline-reconstruction-round-plan.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* Optional walkthrough after execution:

```text
docs/Iris/Done/Walkthrough/iris-dvf-3-3-frozen-2105-baseline-reconstruction-round-walkthrough.md
```

### Config

No build or runtime config changes are planned.

### Generated Artifacts

Round root:

```text
Iris/build/description/v2/staging/compose_contract_migration/frozen_2105_baseline_reconstruction_round/
```

Planned artifact topology:

```text
phase0_opening/
  pass_criteria_contract.json
  opening_decision_reflection.md
  scope_lock_axis_terminology.md
  missing_evidence_inventory.initial.json

phase1_validation_requirement_decision/
  cleanup_invariant_contract_analysis.md
  decision_branch_a1_evidence.json
  decision_branch_a2_evidence.json
  decision_branch_a3_evidence.json
  adopted_decision.json
  candidate_rejection_report.md
  blocked_assessment.json

phase2_referent_writer_sealing/
  referent_candidate_analysis.md
  adopted_referent.json
  writer_authority_decision.json
  hash_equivalence_policy.json
  reconstruction_input_manifest.json

phase3_reconstruction_execution/
  execution_log.json
  reconstructed_artifact_hash.json
  ambient_input_inventory.json
  isolated_environment_verification.json
  reconstructed_baseline_rows.2105.jsonl
  reconstructed_baseline_rows.2105.summary.json
  readiness_queue.reconstructed.json
  metadata_migration_post_state.reconstructed.json

phase4_invariant_verification/
  hash_comparison_result.json
  measurement_seal_preservation_report.json
  adopted_reseal_state.json
  reconstructed_frozen_2105_baseline.hash_manifest.json
  rendered_lua_runtime_invariant_report.json
  byte_equivalence_report.json

phase5_adversarial_review/
  review_result.md

phase6_closeout/
  closeout_handoff.md
  frozen_2105_baseline_prerequisite_closeout.md
  frozen_2105_baseline_prerequisite_closeout.json
```

---

## 6. Planned Changes

### Change 1 - Phase 0 Opening Decision and Scope Lock

Purpose:

Open the round as a separate prerequisite round, lock scope, and prevent cleanup/reconstruction/recovery terminology drift.

Files:

* `phase0_opening/pass_criteria_contract.json`
* `phase0_opening/opening_decision_reflection.md`
* `phase0_opening/scope_lock_axis_terminology.md`
* `phase0_opening/missing_evidence_inventory.initial.json`
* `docs/DECISIONS.md`
* `docs/ROADMAP.md`

Implementation Notes:

* Record an opening decision in `docs/DECISIONS.md`.
* State that this round may affect interpretation of the sealed staged Lua hash but does not rewrite it in Phase 0.
* Seal cleanup kind scope for Phase 1 evidence. Default scope is both cleanup kinds:

```text
diagnostic_only_isolation
complete_removal
```

* If Phase 0 narrows scope, it must state the selected cleanup kind explicitly and mark all non-selected cleanup kinds blocked outside this round.
* If both cleanup kinds remain in scope, Phase 1 must record per-kind conclusions in `adopted_decision.json` under `covered_cleanup_kinds`.
* Force canonical axis names such as `active_old_profile_count`, `active_native_profile_count`, and `default_path_legacy_fallback_reach_count`.
* Forbid the phrase `body_plan v2 preview` as a substitute axis label where canonical axis names are required.
* Mark `selected_role_precedence` and `selected_role_target` out of scope for new sealing.
* Include the Non-Goals list in the scope lock.
* Create an initial missing evidence inventory that distinguishes `historical_readpoint`, `missing_original_byte_artifact`, rejected candidates, and current active topology.

Validation:

* Opening decision exists in `docs/DECISIONS.md`.
* `docs/ROADMAP.md` has a current entry for this round.
* Phase 0 records either a narrowed cleanup kind scope or the default two-kind scope.
* No sealed measurement, runtime Lua, chunk manifest, chunk file, or resolver cleanup mutation occurs.

---

### Change 2 - Phase 1 Cleanup Validation Requirement Decision

Purpose:

Decide whether cleanup invariant preservation can be verified by measurement reproducibility alone or requires byte-level baseline identity as a separate prerequisite.

Files:

* `phase1_validation_requirement_decision/cleanup_invariant_contract_analysis.md`
* `phase1_validation_requirement_decision/decision_branch_a1_evidence.json`
* `phase1_validation_requirement_decision/decision_branch_a2_evidence.json`
* `phase1_validation_requirement_decision/decision_branch_a3_evidence.json`
* `phase1_validation_requirement_decision/adopted_decision.json`
* `phase1_validation_requirement_decision/candidate_rejection_report.md`
* `phase1_validation_requirement_decision/blocked_assessment.json`

Implementation Notes:

* Read `docs/ARCHITECTURE.md` 11-61 and 11-62 as the adapter/readiness/metadata migration contract surface.
* Read `docs/DECISIONS.md` 2026-04-25 metadata migration closeout as the current invariant readpoint.
* Analyze cleanup kinds separately:

```text
diagnostic-only isolation
complete removal
```

* Evaluate the measurement-reproducibility branch family as three cleanup-kind-specific branches:

```text
Branch A1:
  measurement reproducibility is sufficient for diagnostic-only isolation
  byte-level baseline is not required for diagnostic-only cleanup
  Phase 2-4 are skipped
  complete removal cleanup remains blocked
  selected_role bridge impact seal remains a cleanup opening prerequisite

Branch A2:
  measurement reproducibility is sufficient for complete removal cleanup
  byte-level baseline is not required for complete removal cleanup
  Phase 2-4 are skipped
  requires stronger proof set than Branch A1
  expected to be exceptional
  selected_role bridge impact seal remains a cleanup opening prerequisite

Branch A3:
  measurement reproducibility is insufficient for the requested cleanup kind
  reconstruction required
  Phase 2 proceeds
```

* Evaluate the reconstruction-required path:

```text
byte-level identity is required
evidence must explain why measurement reproducibility is insufficient
Phase 2-4 proceed
```

* Branch A2 proof set must explicitly justify why complete removal can be verified without byte-level identity. It must be stronger than Branch A1 and must address deletion irreversibility, historical diagnostic reproducibility, and hidden default dependency risk.
* Branch A2 is expected to be exceptional. If proof cannot distinguish complete removal safety from diagnostic-only safety, fall back to A3 for complete removal.
* Adopt exactly one conclusion per covered cleanup kind. Hybrid conclusions are allowed only when recorded explicitly in `adopted_decision.json`.
* `adopted_decision.json` must include a `covered_cleanup_kinds` object, for example:

```json
{
  "covered_cleanup_kinds": {
    "diagnostic_only_isolation": "A1_sufficient",
    "complete_removal": "A3_reconstruction_required"
  }
}
```

* If any covered cleanup kind resolves to A3, Phase 2 proceeds for that kind unless Phase 6 explicitly hands the reconstruction path to a later round.
* Do not require reconstruction merely as a conservative default without evidence.
* Update the blocked assessment from `blocked_missing_byte_level_frozen_2105_baseline` to the adopted state.
* Rejected candidates may be discussed only as rejected evidence, not consumed as inputs.
* The recovery-analysis assessment is input evidence only. Phase 1 may challenge, validate, or reject it; automatic adoption is forbidden.

Validation:

* Adopted decision cites canonical sealed artifacts or top-doc readpoints.
* Branch A1/A2 explicitly skip Phase 2-4 for the cleanup kind they cover.
* Branch A3 explicitly opens Phase 2 for the cleanup kind it covers.
* Hybrid cleanup-kind conclusions are represented in `covered_cleanup_kinds`.
* Branch A1/A2/B closeout does not open cleanup until the selected-role bridge impact gate is sealed.
* Sealed measurement, runtime Lua, chunk runtime topology, and cleanup code remain unchanged.

---

### Change 3 - Phase 2 Referent / Writer / Hash Equivalence Policy Sealing

Purpose:

If any covered cleanup kind adopts Branch A3, seal what reconstruction means before running any reconstruction.

Files:

* `phase2_referent_writer_sealing/referent_candidate_analysis.md`
* `phase2_referent_writer_sealing/adopted_referent.json`
* `phase2_referent_writer_sealing/writer_authority_decision.json`
* `phase2_referent_writer_sealing/hash_equivalence_policy.json`
* `phase2_referent_writer_sealing/reconstruction_input_manifest.json`

Implementation Notes:

* Analyze referent candidates:

```text
R1 historical sealed staged Lua artifact:
  monolith form, historical build output

R2 current active workspace chunks:
  IrisLayer3DataChunks.lua + Chunk001..011.lua

R3 historical workspace monolith:
  v4.1 closeout 이전 active workspace form
```

* Seal referent timing before selecting a referent:

```text
2026-04-22 layer:
  historical sealed staged Lua hash captures body-plan staged Lua output

2026-04-25 layer:
  metadata migration post-state captures active native metadata counts and
  reports the sealed staged Lua hash as unchanged

Phase 3 target relationship:
  hash reproduction target = 2026-04-22 staged Lua layer
  invariant measurement target = 2026-04-25 metadata migration post-state
  both must hold for Branch B
```

* Record conflict fallback:

```text
hash match + measurement mismatch -> Branch D
measurement match + hash mismatch -> Branch C or D under hash policy
hash/measurement top-doc conflict not resolved by artifacts -> cleanup blocked
```

* If a monolith referent is adopted, record explicitly that it is a reconstruction/staging referent only and not reintroduced as active deployable runtime authority.
* Adopt exactly one referent.
* Seal exactly one writer authority:

```text
compose pipeline rerun:
  requires deterministic input identity and tool version pinning

separate reconstruction script:
  must be isolated from canonical writer authority and classified as
  advisory/historical reconstruction lane unless explicitly approved
```

* Seal the hash equivalence policy:

```text
Does the reconstructed hash need to match
0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062?
```

* Define all mismatch branches without catch-all:

```text
(a) reconstruction failure:
  closed_with_reconstruction_hash_mismatch_failure

(b) historical reseal:
  0390272b... relabeled as historical reference with notes in
  ARCHITECTURE 11-58 / DECISIONS 2026-04-22

(c) separate referent reseal:
  old and new hashes sealed as different referent hashes
```

* Map hash policy branches to closeout branches:

```text
hash match:
  Branch B

(a) reconstruction failure:
  Branch D

(b) historical reseal:
  Branch C if invariant-equivalent and governance disclosure is complete
  Branch D if invariants fail or disclosure is incomplete

(c) separate referent reseal:
  Branch C if invariant-equivalent and referents are cleanly separated
  Branch D if referent separation or invariants fail
```

* Create `reconstruction_input_manifest.json` with fields:

```text
path
artifact_type
authority_class
source_round
expected_row_count
expected_hash
allowed_use
forbidden_use
```

* Allowed `authority_class` values:

```text
canonical_current
generated_reconstruction
historical_readpoint
diagnostic_reference
rejected_candidate
```

Validation:

* Referent decision is consistent with v4.1 chunks-only closeout.
* Writer authority does not violate the single-writer principle.
* Hash equivalence policy closes every mismatch branch.
* All canonical inputs exist in the checkout.
* Every input has a SHA-256 hash.
* Sealed measurement, runtime Lua, and active chunk topology remain unchanged.

---

### Change 4 - Phase 3 Reconstruction Execution

Purpose:

If any covered cleanup kind adopts Branch A3, execute reconstruction deterministically in an isolated staging lane under the Phase 2 referent and writer decisions.

Files:

* `phase3_reconstruction_execution/execution_log.json`
* `phase3_reconstruction_execution/reconstructed_artifact_hash.json`
* `phase3_reconstruction_execution/ambient_input_inventory.json`
* `phase3_reconstruction_execution/isolated_environment_verification.json`
* `phase3_reconstruction_execution/reconstructed_baseline_rows.2105.jsonl`
* `phase3_reconstruction_execution/reconstructed_baseline_rows.2105.summary.json`
* `phase3_reconstruction_execution/readiness_queue.reconstructed.json`
* `phase3_reconstruction_execution/metadata_migration_post_state.reconstructed.json`

Implementation Notes:

* Use only the adopted Phase 2 writer.
* If round-specific reconstruction or validation scripts are required, create them as part of Phase 3 before the first reconstruction run. Script creation, script hash capture, and validation script hash capture are Phase 3 execution responsibilities.
* Seal deterministic input identity:

```text
facts JSONL
body_source_overlay or equivalent adopted source
compose tool version
normalizer version
style linter version
serializer version
Lua renderer/bridge writer version
```

* Run only in isolated staging. Do not overwrite:

```text
Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua
Iris/Data/IrisLayer3DataChunks.lua
Iris/Data/IrisLayer3DataChunks/Chunk001..011.lua
historical staged Lua artifacts
```

* Use the direct default compose entrypoint with `compose_profiles_v2.json + body_plan`.
* Confirm legacy `sentence_plan` is unavailable on the default path and allowed only in explicit compatibility/diagnostic mode.
* Run a 2-run determinism check.
* Measure reconstructed artifact hash and compare with the Phase 2 hash policy.
* Validate every `expected_*` field in `phase2_referent_writer_sealing/reconstruction_input_manifest.json` against measured Phase 3 input/output. Any divergence is a hard fail.

Expected targets:

```text
total rows                               = 2105
active / adopted                         = 2084
silent / unadopted                       = 21
hard schema fail                         = 0
default_path_legacy_fallback_reach       = 0

active_execution_queue                   = 2084
non_fallback_active_metadata_swap        = 2006
fallback_dependent_active                = 78
silent_metadata_inventory                = 21
mechanical_ready                         = 78
schema_gap                               = 0

active_native_profile_count              = 2084
legacy_fallback_target_count             = 0
default_path_legacy_fallback_reach_count = 0
canonical_row_legacy_field_residue_count = 0
rendered_output_delta                    = 0
```

Validation:

* Isolated environment verification passes.
* Row count exact match.
* Active/silent exact match.
* Schema pass.
* 2-run determinism hash pass.
* `default_path_legacy_fallback_reach_count = 0`.
* All `expected_*` manifest fields match measured values.
* Sealed measurement seal remains unchanged.
* Bridge availability remains `internal_only 617 / exposed 1467`.

---

### Change 5 - Phase 4 Invariant Verification and Hash Equivalence Sealing

Purpose:

Verify reconstruction output against the Phase 2 hash equivalence policy and seal the result as byte-equivalent, invariant-equivalent, or blocked.

Files:

* `phase4_invariant_verification/hash_comparison_result.json`
* `phase4_invariant_verification/measurement_seal_preservation_report.json`
* `phase4_invariant_verification/adopted_reseal_state.json`
* `phase4_invariant_verification/reconstructed_frozen_2105_baseline.hash_manifest.json`
* `phase4_invariant_verification/rendered_lua_runtime_invariant_report.json`
* `phase4_invariant_verification/byte_equivalence_report.json`

Implementation Notes:

* Compare reconstructed hash with:

```text
0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062
```

* If hash matches, close as byte-equivalent reconstruction and leave the historical sealed hash unchanged.
* If hash mismatches, apply exactly one Phase 2 mismatch branch:

```text
(a) failure
(b) historical reseal
(c) separate referent reseal
```

* Apply the Phase 2 mismatch branch to closeout branch mapping:

```text
hash match -> Branch B
(a) failure -> Branch D
(b) historical reseal -> Branch C only if invariant-equivalent and fully disclosed, otherwise Branch D
(c) separate referent reseal -> Branch C only if invariant-equivalent and referents are separated, otherwise Branch D
```

* Classify hash equivalence:

```text
byte_equivalent_reconstruction      -> Branch B
invariant_equivalent_reconstruction -> Branch C
blocked_hash_mismatch               -> Branch D
```

* Preserve every sealed measurement seal.

Validation:

* Measurement seal preservation report shows row-level unchanged state.
* Bridge availability, quality distribution, runtime path counts, and runtime status are unchanged.
* Hash manifest includes every hash class.
* `0390272b...` match or mismatch result is explicit.
* Adopted hash policy resolves to one branch only.

---

### Change 6 - Phase 5 Adversarial Review

Purpose:

Review either the Branch A1/A2 decision path, the Branch A3 reconstruction path, or a hybrid per-kind result before closeout.

Files:

* `phase5_adversarial_review/review_result.md`

Implementation Notes:

* For Branch A1/A2, review whether Phase 1 evidence really proves byte-level reconstruction is unnecessary for the specific cleanup kind and whether the selected-role bridge gate remains correctly blocked.
* For Branch A3, review whether Phase 2-4 outputs remain consistent with v4.1 closeout and sealed measurement state.
* For hybrid per-kind results, review that `covered_cleanup_kinds` records every in-scope cleanup kind and that the most restrictive unresolved kind controls cleanup blocking.
* Cross-reference `docs/Philosophy.md`, `docs/DECISIONS.md`, and `docs/ARCHITECTURE.md`.
* Classify findings as:

```text
Critical
Important
Minor
```

Validation:

* PASS requires Critical `0` and Important `0`.
* FAIL hands off to reopen or separate blocker round.
* Review does not retroactively criticize sealed states beyond this round's authority.

---

### Change 7 - Phase 6 Closeout and Resolver Cleanup Gate Decision

Purpose:

Seal one closeout branch and explicitly state whether the frozen baseline prerequisite is closed, whether the selected-role bridge impact gate remains pending, and whether Resolver Compatibility Mapping Cleanup Round remains blocked.

Files:

* `phase6_closeout/closeout_handoff.md`
* `phase6_closeout/frozen_2105_baseline_prerequisite_closeout.md`
* `phase6_closeout/frozen_2105_baseline_prerequisite_closeout.json`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Implementation Notes:

* Select exactly one primary closeout branch and include `covered_cleanup_kinds` for every in-scope cleanup kind. If cleanup-kind conclusions are hybrid, the primary closeout branch follows the most restrictive unresolved kind.

```text
Branch A1:
  closed_with_prereq_decision_obviated_reconstruction_for_diagnostic_only_cleanup
  byte-level reconstruction obviated for diagnostic-only cleanup only
  complete removal cleanup blocked
  cleanup opening blocked until selected_role bridge impact seal

Branch A2:
  closed_with_prereq_decision_obviated_reconstruction_for_complete_removal_cleanup
  byte-level reconstruction obviated for complete removal cleanup
  stronger proof set sealed
  expected to be exceptional
  cleanup opening blocked until selected_role bridge impact seal

Branch A3:
  decision_measurement_reproducibility_insufficient
  reconstruction required
  same-round Phase 2 proceeds unless Phase 6 records external handoff

Branch B:
  closed_with_byte_equivalent_reconstructed_frozen_2105_baseline_sealed
  byte-level baseline prerequisite closed
  cleanup opening blocked until selected_role bridge impact seal

Branch C:
  closed_with_invariant_equivalent_reconstructed_baseline_but_no_byte_equivalence
  hash mismatch / referent equivalence resolution round required
  cleanup blocked

Branch D:
  blocked_reconstruction_incomplete
  or closed_with_reconstruction_hash_mismatch_failure_handoff_pending
  cleanup blocked
```

* Add a closeout entry to `docs/DECISIONS.md`.
* Add `docs/ARCHITECTURE.md` outcome section only if the result changes architecture readpoint interpretation.
* Add or update `docs/ROADMAP.md` Done / Next / Hold entry.
* Avoid wording such as `복구 완료` unless byte-equivalent hash reproduction succeeded.
* Do not declare deployed closeout, runtime QA pass, release readiness, adapter removal, or resolver cleanup execution.
* If Branch A1/A2/B closes successfully, set the next required gate to `Selected Role Bridge Impact Seal Round` before cleanup opening.
* Branch B path may include an internal `reconstructed_frozen_2105_baseline` seal, but the common closeout artifact remains `frozen_2105_baseline_prerequisite_closeout.*`.

Validation:

* Primary closeout branch is single-selection.
* `covered_cleanup_kinds` is present and accounts for every cleanup kind in Phase 0 scope.
* Branch A1 covers diagnostic-only cleanup only and blocks complete removal cleanup.
* Branch A2 includes the stronger proof set required for complete removal cleanup.
* Branch A1/A2/B close only the frozen baseline prerequisite; cleanup remains blocked until the selected-role bridge impact gate closes.
* Branch A3/C/D block cleanup.
* Top-doc updates match the selected branch.
* Sealed measurement seal remains unchanged after closeout.

---

## 7. Validation Plan

### Automated Validation

Use exact relevant commands and do not claim pass unless they exit with code 0.

Always planned for this round:

```powershell
git diff --stat
git diff -- docs\Iris\iris-dvf-3-3-frozen-2105-baseline-reconstruction-round-plan.md docs\DECISIONS.md docs\ARCHITECTURE.md docs\ROADMAP.md
```

If all covered cleanup kinds close with Branch A1 or Branch A2:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

The test command is supporting regression evidence only; the decisive evidence is the Phase 1 cleanup-kind-specific contract decision and Phase 5 review. Branch A1/A2 do not open cleanup while the selected-role bridge impact gate is unsealed.

If any covered cleanup kind adopts Branch A3:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Round-specific scripts, if created:

```powershell
python -B Iris\build\description\v2\tools\build\build_frozen_2105_baseline_reconstruction.py --dry-run
python -B Iris\build\description\v2\tools\build\build_frozen_2105_baseline_reconstruction.py --run 1
python -B Iris\build\description\v2\tools\build\build_frozen_2105_baseline_reconstruction.py --run 2
python -B Iris\build\description\v2\tools\build\validate_frozen_2105_baseline_reconstruction.py --require-complete
```

Required measured gates for Branch A3 reconstruction path:

```text
row_count = 2105
active_native_profile_count = 2084
silent_old_profile_count = 21
hard_schema_fail = 0
active_execution_queue = 2084
non_fallback_active_metadata_swap = 2006
fallback_dependent_active = 78
silent_metadata_inventory = 21
mechanical_ready = 78
schema_gap = 0
legacy_fallback_target_count = 0
default_path_legacy_fallback_reach_count = 0
canonical_row_legacy_field_residue_count = 0
rendered_output_delta = 0
bridge_availability_internal_only_count = 617
bridge_availability_exposed_count = 1467
2_run_determinism = pass
isolated_environment_verification = pass
manifest_expected_field_validation = pass
```

Hash gates:

```text
historical_sealed_hash =
  0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062

byte_equivalent_reconstruction:
  reconstructed_hash == historical_sealed_hash

invariant_equivalent_reconstruction:
  all invariant gates pass AND reconstructed_hash != historical_sealed_hash
```

### Manual Validation

* Inspect Phase 1 adopted decision for evidence sufficiency.
* Inspect Branch A1/A2 proof scope and confirm the selected cleanup kind cannot be generalized to the other cleanup kind.
* Inspect `covered_cleanup_kinds` and confirm every Phase 0 in-scope cleanup kind has one conclusion.
* Inspect Phase 2 referent choice against v4.1 chunks-only runtime closeout.
* Inspect reconstruction input manifest and confirm rejected candidates are not consumed as canonical input.
* Inspect manifest `expected_*` validation and confirm measured values match every expected value.
* Inspect isolated environment report and confirm no canonical Lua, runtime chunks, or sealed staged artifacts were overwritten.
* Inspect Phase 5 adversarial review and confirm Critical `0`, Important `0` before closeout.
* Inspect top-doc wording for absent cleanup execution, runtime QA, deployed, release-ready, adapter removal, and monolith restoration claims.

### Validation Limits

Not performed in this round:

* No Resolver Compatibility Mapping Cleanup execution.
* No adapter removal.
* No manual in-game QA.
* No multiplayer validation.
* No long-session runtime validation.
* No external mod compatibility sweep.
* No deployed closeout.
* No `ready_for_release` declaration.
* No `selected_role_precedence` / `selected_role_target` inventory sealing.

---

## 8. Risk Surface Touch

### Authority Surface

Touched. This round decides whether cleanup validation requires byte-level baseline identity and may alter how the historical sealed Lua hash is interpreted for cleanup prerequisite purposes.

### Runtime Behavior Surface

Guarded immutable. This round does not change runtime behavior, Browser/Wiki consumers, tooltips, `layer3_renderer.lua`, chunk manifest loading, or active Lua data topology.

### Compatibility Surface

Guarded immutable. This round does not change resolver compatibility mapping behavior, adapter behavior, or external mod compatibility. It only decides cleanup prerequisites.

### Sealed Artifact Surface

Touched conditionally. Phase 1 Branch A1/A2 avoids reconstruction and does not create a new byte-level seal. Phase 1 Branch A3 may create a new reconstruction hash manifest or reseal interpretation, but only under Phase 2 policy.

Existing sealed measurements remain immutable in every branch.

### Public-Facing Output Surface

None. This round does not change public rollout language, release notes, in-game UI, published compatibility claims, or Workshop state.

---

## 9. Risk Analysis

### Architecture Risk

* The round could confuse reconstruction with recovery. The plan prevents this by reserving recovery language for exact historical hash reproduction.
* A monolith referent could be misread as reintroducing monolith runtime authority. Phase 2 must explicitly keep any monolith output in isolated reconstruction/staging only.
* A separate reconstruction script could bypass the compose single-writer principle. Phase 2 must decide whether it is advisory/historical only or an approved writer.
* Hash mismatch reseal could redefine the authority hierarchy between measurement seals and hash seals. Phase 2 must pre-seal mismatch handling before reconstruction runs.

### Runtime Risk

* Reconstruction output could accidentally overwrite active chunk runtime data. Phase 3 must run in isolated staging and verify workspace runtime paths unchanged.
* Reopening `IrisLayer3Data.lua` fallback would violate v4.1 closeout. The plan explicitly forbids runtime fallback restoration.

### Compatibility Risk

* Cleanup could be opened before the selected-role bridge impact seal by mistake. Phase 6 must state that Branch A1/A2/B close only the frozen baseline prerequisite and do not open cleanup by themselves.
* Branch A1 evidence could be over-generalized to complete removal cleanup. The branch names and proof sets must keep diagnostic-only isolation and complete removal separate.
* Hybrid cleanup-kind evidence could be flattened into a single branch. Phase 1 and Phase 6 must preserve the `covered_cleanup_kinds` map.
* Rejected candidates could be treated as substitute baselines. The input manifest allows them only as `rejected_candidate` references.
* `selected_role` document references could become accidental sealed evidence. The plan keeps them out of scope and blocks cleanup until a separate selected-role bridge impact seal closes.

### Regression Risk

* Ambient input drift may prevent deterministic reproduction.
* Row ordering or Lua serialization differences may cause hash mismatch even with invariant-equivalent content.
* Top-doc wording may overstate `복구`, `ready_for_release`, deployed closeout, or cleanup completion.
* Existing untracked planning artifacts may be confused with canonical top-doc closeout. Phase 6 must rely on explicit DECISIONS / ARCHITECTURE / ROADMAP updates.

Branch trigger model:

```text
Branch A1:
  Phase 1 proves measurement reproducibility is sufficient for
  diagnostic-only cleanup only.

Branch A2:
  Phase 1 proves measurement reproducibility is sufficient for
  complete removal cleanup using the stronger A2 proof set.

Branch A3:
  Phase 1 proves measurement reproducibility is insufficient for at least
  one covered cleanup kind and reconstruction is required for that kind.

Branch B:
  Phase 1 requires byte-level identity,
  Phase 2 policy requires historical hash match,
  Phase 3 reconstruction succeeds,
  Phase 4 hash matches 0390272b...

Branch C:
  Phase 1 requires byte-level identity,
  Phase 3 reconstruction is invariant-equivalent,
  Phase 4 hash does not match but mismatch is explained under Phase 2 policy.

Branch D:
  Phase 1 evidence chain fails,
  reconstruction cannot produce 2105 rows,
  active/silent/readiness counts mismatch,
  default legacy fallback reach reappears,
  rendered delta appears,
  hash mismatch is unexplained,
  single-writer principle is violated,
  cleanup mutation leaks into this round.
```

---

## 10. Rollback Plan

Phase 0-1 abort:

* Add a historical note labeling the opening as `closed_aborted_pre_decision`.
* Do not delete historical DECISIONS entries.
* Sealed measurement, runtime Lua, and chunk topology remain unchanged.

Phase 2 abort:

* Add a historical note labeling the round as `closed_aborted_post_referent_sealing`.
* Keep referent/writer decisions as historical, not current cleanup permission.
* Sealed measurement, runtime Lua, and chunk topology remain unchanged.

Phase 3-4 hash mismatch:

* Do not rollback. Apply the Phase 2 hash equivalence branch.
* If failure branch is selected, hand off to hash mismatch / referent equivalence resolution before cleanup.

Unintended sealed artifact or runtime mutation:

* Restore canonical sealed hash and measurement references from top docs.
* Revert any accidental modifications to active runtime chunks or renderer paths.
* Mark the round blocked unless preservation can be proven with evidence.

Forbidden rollback:

```text
legacy sentence_plan default path 복귀
pre-migration 2105 source를 임시 baseline으로 승격
selected_role mismatch를 무시하고 cleanup 착수
hash mismatch를 사소한 차이로 처리
runtime QA 없이 deployed closeout 선언
monolith/chunk dual runtime loading 재도입
```

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance remains mandatory.
* Hub-and-spoke boundaries remain intact.
* Iris remains a Lua wiki module and does not acquire Pulse or other-spoke dependencies.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` current readpoints must be followed.
* Same-issue later decisions supersede earlier readpoints.
* `docs/PLAN_TEMPLATE.md` is the required implementation plan shape.
* For execution, `docs/EXECUTION_CONTRACT.md` disclosure, evidence, and closeout obligations apply.
* Default compose authority remains `compose_profiles_v2.json + body_plan`.
* Legacy `sentence_plan` remains compatibility/diagnostic only.
* Implicit legacy fallback is forbidden.
* Runtime-side compose rewrite is forbidden.
* Compose-external repair is forbidden.
* Lua/runtime consumer remains render-only.
* Single-writer principle remains intact.
* v4.1 chunks-only runtime closeout remains intact.
* `Iris/Data/IrisLayer3Data.lua` monolith path must not be restored as active deployable runtime authority.
* Existing sealed measurement states must not be redefined.
* `quality_baseline_v4` remains frozen.
* Runtime state remains `ready_for_in_game_validation`.
* Bridge availability remains `internal_only 617 / exposed 1467`.
* Cleanup lane and reconstruction lane must not be mixed.
* Phase 0 cleanup kind scope and Phase 1 `covered_cleanup_kinds` conclusions must be preserved through closeout.
* Branch A1/A2/B close only the frozen baseline prerequisite.
* Resolver cleanup cannot open until the separate `Selected Role Bridge Impact Seal Round` closes or a later top-doc decision removes that axis from cleanup validation scope with evidence.
* Branch A3/C/D block cleanup.

---

## 12. Expected Closeout State

Expected closeout is branch-dependent. Branch A3 is a continuation decision, not a final closeout, unless Phase 6 explicitly records external handoff.

PASS - Full, Branch A1:

```text
closed_with_prereq_decision_obviated_reconstruction_for_diagnostic_only_cleanup
```

Required:

```text
Phase 1 evidence chain proves measurement reproducibility is sufficient for diagnostic-only cleanup
Phase 2-4 explicitly skipped
complete removal cleanup remains blocked
selected-role bridge impact seal remains required before cleanup opening
sealed measurement seal unchanged
```

PASS - Full, Branch A2:

```text
closed_with_prereq_decision_obviated_reconstruction_for_complete_removal_cleanup
```

Required:

```text
Phase 1 evidence chain proves measurement reproducibility is sufficient for complete removal cleanup
stronger A2 proof set is sealed
Branch A2 is treated as exceptional
Phase 2-4 explicitly skipped
selected-role bridge impact seal remains required before cleanup opening
sealed measurement seal unchanged
```

PROCEED or HANDOFF, Branch A3:

```text
decision_measurement_reproducibility_insufficient
```

Required:

```text
Phase 1 evidence chain proves measurement reproducibility is insufficient for at least one covered cleanup kind
same-round Phase 2 reconstruction path proceeds by default
external handoff is recorded only if Phase 6 explicitly pauses reconstruction
sealed measurement seal unchanged
```

PASS - Full, Branch B:

```text
closed_with_byte_equivalent_reconstructed_frozen_2105_baseline_sealed
```

Required:

```text
active_native_profile_count = 2084
legacy_fallback_target_count = 0
default_path_legacy_fallback_reach_count = 0
canonical_row_legacy_field_residue_count = 0
rendered_output_delta = 0
active_execution_queue = 2084
non_fallback_active_metadata_swap = 2006
fallback_dependent_active = 78
silent_metadata_inventory = 21
Lua hash 0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062 reproduced
2-run determinism pass
isolated environment verification pass
rejected candidates not consumed as canonical input
cleanup not executed
selected-role bridge impact seal remains required before cleanup opening
```

PASS - Limited, Branch C:

```text
closed_with_invariant_equivalent_reconstructed_baseline_but_no_byte_equivalence
```

Required:

```text
all count/state/readiness invariants match
byte hash mismatch is explicit and explained
hash mismatch / referent equivalence resolution round required
cleanup blocked
```

FAIL / BLOCKED, Branch D:

```text
blocked_reconstruction_incomplete
```

or

```text
closed_with_reconstruction_hash_mismatch_failure_handoff_pending
```

Triggered by any of:

```text
Phase 1 evidence chain not established
2105 row reconstruction failure
active/silent or readiness queue mismatch
metadata migration post-state mismatch
legacy default fallback reach reappears
rendered delta occurs
runtime validation failure
hash mismatch unexplained
cleanup mutation mixed into this round
single-writer principle violation
```

Closeout non-claims:

```text
This closeout does not execute Resolver Compatibility Mapping Cleanup.
This closeout does not remove the adapter.
This closeout does not pass manual in-game QA.
This closeout does not declare deployed closeout.
This closeout does not declare ready_for_release.
This closeout does not restore monolith runtime authority.
This closeout does not seal selected_role_precedence / selected_role_target.
This closeout does not open Resolver Compatibility Mapping Cleanup while
selected_role bridge impact remains unsealed.
```
