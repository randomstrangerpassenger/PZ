# Iris DVF 3-3 Structural Signal Scope Split Seal Round Plan

> 상태: Draft v0.2-review-applied
> 기준일: 2026-05-29
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> authority input: `최종 종합 로드맵 - Iris DVF 3-3 Structural Signal Scope Split Seal / Re-Seal Round` (2026-05-28 user-provided synthesis)
> review input: `최종 종합 검토안 - Iris DVF 3-3 Structural Signal Scope Split Seal Round Plan v0.1-final-synthesis` (2026-05-29), R1 through R8 incorporated in v0.2.
> 공식 issue명: `Structural Signal Scope Split Seal Round`
> canonical round id: `structural_signal_scope_split_seal_round`
> staging/body alias: `Reconstruction-Based Re-Seal`
> filesystem alias: `structural_signal_scope_re_seal_round`
> unique execution identifier: `2026-05-29.structural_signal_scope_split_seal_round.reconstruction_based_re_seal`
> naming attestation: the canonical round id and filesystem alias identify the same execution round. The alias must not be treated as a separate round, and Phase 0 must disambiguate this round from any prior same-name or predecessor attempt.
> 직접 상위 readpoint:
> - 2026-04-29 publish writer authority / `FUNCTION_NARROW` and `ACQ_DOMINANT` blanket isolation forbidden seal
> - 2026-05-19 `Runtime Payload Enum Rename Scope Round` Branch B/B1 closeout, current runtime payload vocabulary `adopted/unadopted`
> - 2026-05-23 current runtime chunk identity seal
> - 2026-05-27 `Structural Signal Current Referent Inventory and Anchor Recovery Round` `blocked_missing_anchor`
> - 2026-05-28 `Structural Signal Missing Anchor Authority Resolution Round` Branch B `closed_with_authoritative_reconstruction_adopted`
> 계획 형식: `docs/PLAN_TEMPLATE.md`
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`; `docs/PLAN_TEMPLATE.md` is used only as a round-local planning form unless separately registered by sealed decision. It is not treated as semantic authority over `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md`.
> 실행 상태: planning authority only. 이 문서는 observer-only scope seal round를 열기 위한 실행 계획이며, 작성 시점에는 runtime Lua, generated runtime artifacts, rendered text, source decisions, facts, publish_state, quality_state, runtime_state, deployed state, release state, or closeout state를 변경하지 않는다.

---

## 1. Objective

이번 execution plan의 목적은 2026-05-28 reconstructed structural observer authority를 기준으로 structural signal scope separation을 positive sealed manifest로 닫는 것이다.

이번 round는 structural signal 품질 개선, `ACQ_DOMINANT` 재측정, publish mutation review, runtime rollout이 아니다. 이전 흐름에서 얽혀 있던 네 issue family를 분리하고, structural signal observer/readpoint scope만 observer-only로 봉인한다.

분리 대상 scope bucket:

```text
structural_signal_observer_readpoint_seal
acq_dominant_residual_remeasurement
publish_mutation_review
blanket_isolation_forbidden_maintenance
```

Expected success closeout branch:

```text
closed_with_structural_signal_scope_split_sealed_observer_only
```

Blocked closeout branches:

```text
blocked_predecessor_misanchored
blocked_authority_input_hash_mismatch
blocked_authority_consumption_contract_invalid
blocked_scope_separation_incomplete
blocked_separation_invariant_violation
blocked_non_deterministic_generator
blocked_adversarial_review_failed
blocked_claim_overreach
blocked_unexpected_mutation
```

Final claim boundary:

```text
새 reconstructed structural observer authority를 기준으로 structural signal scope separation이 observer-only로 봉인되었고, ACQ_DOMINANT residual remeasurement / publish mutation review / blanket isolation reopen과 분리되었다. 이번 라운드는 quality / publish / runtime / rendered / Lua mutation을 수행하지 않았다.
```

Success must not claim:

```text
structural signal disposition complete
ACQ_DOMINANT remeasurement complete
ACQ_DOMINANT disposition complete
publish mutation review complete
runtime rollout complete
deployed closeout
manual in-game QA pass
release readiness
Workshop readiness
ready_for_release
```

---

## 2. Scope

This is an observer-only, non-writer, non-measurement, non-runtime scope seal round. It may create round-local staging artifacts, scope manifests, invariant reports, hard gate reports, artifact hash manifests, addendum drafts, adversarial review output, and closeout documents. It must not mutate source facts, source decisions, rendered text, runtime Lua, generated runtime chunks, publish state, quality state, runtime state, or sealed historical bodies.

Round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_scope_re_seal_round/
```

In scope:

* Phase 0 predecessor verification, opening contract, and authority input hash check.
* Phase 1 current authority manifest and consume-only authority contract.
* Phase 2 scope inventory and 4-bucket scope split matrix.
* Phase 3 positive scope separation manifest and observer readpoint seal.
* Phase 4 non-mutation and separation invariant verification.
* Phase 5 `ACQ_DOMINANT` future-round pointer, hard gate, and artifact hash manifest.
* Phase 6 DECISIONS / ROADMAP addendum drafts and adversarial review.
* Phase 7 evidence-bound closeout with claim and non-claim sections.

Allowed artifacts:

```text
opening_contract.json
authority_readpoint_reflection.md
phase0_predecessor_verification_report.json
phase0_authority_input_hash_check.json
phase0_baseline_hash_manifest.json
structural_signal_current_authority_manifest.json
rejected_authority_sources.md
authority_consumption_contract.json
phase1_contract_validation_report.json
phase2_scope_inventory.jsonl
phase2_inventory_summary.json
structural_signal_scope_split_matrix.json
acq_dominant_remeasurement_boundary.md
scope_separation_manifest.json
phase3_manifest_validation_report.json
structural_signal_observer_readpoint_seal.json
observer_readpoint_summary.md
separation_invariant_report.json
non_mutation_invariant_report.json
phase4_hash_diff_evidence.json
hash_delta_summary.md
acq_dominant_current_baseline_remeasurement_round_pointer.json
phase5_hard_gate_report.json
artifact_hash_manifest.json
decisions_addendum_draft.md
roadmap_addendum_draft.md
phase6_adversarial_review.md
phase7_closeout.json
phase7_closeout.md
closeout_pass.json
```

### Explicitly Out Of Scope

* `ACQ_DOMINANT` residual remeasurement.
* `ACQ_DOMINANT` row reclassification.
* `ACQ_DOMINANT` publish mutation candidate generation.
* Publish mutation review.
* Structural signal disposition completion.
* Structural quality completion.
* New structural observer authority artifact regeneration.
* Historical 2026-04-24 artifact restoration or obsolete declaration.
* Default compose data-root guard relaxation.
* GUARD-A redefinition.
* Runtime Lua mutation.
* Packaged Lua regeneration.
* Rendered text mutation.
* `quality_state`, `publish_state`, or `runtime_state` mutation.
* `quality_baseline_v4` cutover or mutation.
* Source expansion.
* External mod compatibility sweep.
* Manual in-game validation QA.
* Deployed closeout.
* Workshop readiness.
* Release readiness.
* `ready_for_release` declaration.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md` sealed body modification.

---

## 3. Non-Goals

This plan does not attempt to:

* Improve semantic quality or complete structural signal disposition.
* Treat `ACQ_DOMINANT` as a publish mutation candidate before current-baseline remeasurement.
* Reopen `FUNCTION_NARROW` or `ACQ_DOMINANT` blanket isolation.
* Rejudge publish writer authority. Publish writer authority remains layer/position correctness, not semantic narrowness or acquisition dominance alone.
* Promote historical, diagnostic, staging, or Done walkthrough artifacts to current authority.
* Convert the reconstructed observer authority into default compose writer input.
* Change `compose_profiles_v2.json + body_plan` as current compose writer authority.
* Change Browser, Wiki, Tooltip, runtime consumer, or external compatibility behavior.
* Perform deployment, packaging, release notes, Workshop publish, or public rollout work.

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` remains the top authority. Iris remains a 100% Lua wiki-style module and must not expand into recommendation, gameplay policy, or another module's role.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are current governance readpoints.
* The current structural observer authority is the reconstructed observer-only Branch B artifact set under:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/
```

* The previous Branch C retirement attempt is superseded and isolated as invalid execution trace. It is not current closeout authority.
* The historical 2026-04-24 seven-hash set remains historical/provenance reference only.
* The reconstructed observer authority is consume-only for this round. It is not writer authority, publish authority, quality authority, runtime authority, or default compose input.
* Default compose data-root guard remains unchanged.
* GUARD-A current-surface re-entry prevention remains unchanged.
* `FUNCTION_NARROW` and `ACQ_DOMINANT` blanket isolation remain forbidden.

Current authority identity assumptions:

```text
row_count = 2105
runtime_state = adopted 2084 / unadopted 21
writer_role = observer_only
schema = pass
forbidden writer fields = 0
determinism = pass
```

Authority hash inputs that Phase 0 must verify against current checkout. This is a two-tier check: Phase 0 first verifies `reconstruction_hash_manifest.json` itself, then verifies the artifact hashes listed inside that manifest.

```text
reconstruction_hash_manifest.json sha256 = ea784c65d2cfcd0e716a50fce8c1d1c6370b1d44e63b875372bb79e56ed54375
surface_contract_signal.reconstructed.2105.jsonl sha256 = 5f101857e741d06ed12a02e1b27df87203374f1d802c52676660daadf118abd3
surface_contract_signal.reconstructed.summary.json sha256 = 72c15f94917481226e328ed1f2f3c9e1100fc8515375410b8c4ac00ae5fb1b3c
body_plan_structural_reclassification.reconstructed.2105.jsonl sha256 = 86b0fe4c7e8bc195734602e22dd7a06e89a45dec704e8d0462a1127300bd4094
body_plan_structural_reclassification.reconstructed.summary.json sha256 = c70f4f555462f6c43fe258e95afbd74a6f18073bfcf9f9adfa77a1ade663e9dc
reconstruction_input_manifest.json sha256 = 3548beac5e2aa915394598d2f1bc50f6b006a5f1b08a5580442ca255aaf85b1a
reconstruction_schema_report.json sha256 = bbe9f7a631060235b8cd7f23e2f3ff0c3d8c82f01b1b73b69d338eb39eb11535
reconstruction_distribution_report.json sha256 = 44bfa522d34985f0382208cb0822e852a4d1fbde6c21373ac37ee8d5a5f5e7e4
reconstruction_delta_report.json sha256 = 45adbeddae8835bf2c0e32164bef16dbfe065698851ae6447ba5f83634209600
phase3_branch_b_reconstruction_report.json sha256 = f43ed70107fdedf8d02821f87675d69472d51e78725df108eb166f99ccfe4f07
```

Validation assumptions:

* Required command absence or tool failure is reported as `blocked`, not `pass`.
* Prior Python unittest baseline is `398 tests / OK`; this plan requires the exact relevant command to exit `0` and observed test count to be at least the baseline unless a documented reason explains a count change.
* Prior Lua syntax baseline is `183 files / OK`; this plan requires the exact syntax command to exit `0` and observed file count to be at least the baseline unless a documented reason explains a count change.
* Hash and determinism checks use `sha256` unless an artifact explicitly records a stronger local algorithm.

---

## 5. Repository Areas Affected

### Code

None by default.

Optional round-local helper scripts may be created only under the round-local staging root if they are needed to generate reports deterministically:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_scope_re_seal_round/
```

Repo-level build tools or tests are not planned mutation targets. If execution needs them, the round must stop, amend the plan or open a separate implementation scope, and rerun the relevant validation.

### Docs

Planning doc:

```text
docs/Iris/iris-dvf-3-3-structural-signal-scope-split-seal-round-plan.md
```

Draft-only governance text generated during the round:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_scope_re_seal_round/decisions_addendum_draft.md
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_scope_re_seal_round/roadmap_addendum_draft.md
```

Direct sealed body mutation is not planned for:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

### Config

None.

### Generated Artifacts

Round-local evidence root:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_scope_re_seal_round/
```

All generated artifacts must be new additive evidence files. Historical sealed artifact bodies must not be rewritten.

---

## 6. Planned Changes

### Change 1 - Phase 0 Predecessor, Opening Contract, and Input Authority Verification

Purpose:

Open the round as observer-only and verify that the current execution basis is the 2026-05-28 reconstructed observer authority, not the previous same-name attempt or superseded Branch C retirement attempt.

Files:

```text
opening_contract.json
authority_readpoint_reflection.md
phase0_predecessor_verification_report.json
phase0_authority_input_hash_check.json
phase0_baseline_hash_manifest.json
```

Implementation Notes:

* Record round classification:

```text
observer_only = true
measurement_round = false
writer_round = false
runtime_round = false
release_round = false
```

* Record forbidden permissions:

```text
acq_dominant_remeasurement_allowed = false
publish_mutation_allowed = false
blanket_isolation_reopen_allowed = false
sealed_body_modification_allowed = false
```

* Verify predecessor state:
  * previous `Structural Signal Scope Split Seal Round` attempt is historical trace or absorbed predecessor only,
  * 2026-05-27 missing-anchor inventory round is blocked predecessor context,
  * 2026-05-28 Branch C retirement attempt is superseded and not current closeout authority,
  * 2026-05-28 Branch B reconstructed observer authority is current execution basis.
* `phase0_predecessor_verification_report.json` must carry these disambiguation fields:

```text
canonical_round_id = structural_signal_scope_split_seal_round
filesystem_alias = structural_signal_scope_re_seal_round
current_round_unique_identifier = 2026-05-29.structural_signal_scope_split_seal_round.reconstruction_based_re_seal
predecessor_closeout_date = <exact date if corroborated, otherwise unknown_or_uncorroborated>
predecessor_disposition = <exact disposition if corroborated, otherwise predecessor_not_found_or_absorbed>
current_round_opening_date = 2026-05-29
current_round_closeout_date = <set in Phase 7 only>
cross_reference_primary_anchor = Iris/build/description/v2/staging/compose_contract_migration/structural_signal_scope_re_seal_round/
```

* Hash-check the current checkout against the authority hash input set listed in Section 4.
* Verify `reconstruction_hash_manifest.json` by its own SHA-256 before trusting the artifact hashes listed inside it.
* If any required current authority artifact is missing or hash mismatched, stop before Phase 1 and close as `blocked_authority_input_hash_mismatch`.
* Generate `phase0_baseline_hash_manifest.json` covering every Phase 4 governed surface that will be checked by hash. For untouched governed surfaces where byte-level hashing is not required, Phase 0 must record the path set that will be checked by `git diff` absence.

Validation:

* `opening_contract.json` is valid JSON.
* Predecessor classification is explicit.
* Round id, filesystem alias, unique identifier, predecessor disposition, and primary cross-reference anchor are explicit.
* Two-tier authority input hash check has no mismatch.
* `phase0_baseline_hash_manifest.json` exists before Phase 4.
* The opening contract contains no mutation permission outside this plan.

---

### Change 2 - Phase 1 Current Authority Manifest and Authority Consumption Contract

Purpose:

Separate current structural readpoint authority from supporting trace and rejected current authority sources, then seal a consume-only contract for this round.

Files:

```text
structural_signal_current_authority_manifest.json
rejected_authority_sources.md
authority_consumption_contract.json
phase1_contract_validation_report.json
```

Implementation Notes:

* Classify sources into:

```text
current_authority
supporting_trace_only
rejected_as_current_authority
```

* Current authority must point to the reconstructed Branch B artifact set under `phase3_branch_b_reconstruction/`.
* Supporting trace may include historical 2026-04-24 references, 2026-05-27 blocked predecessor, and 2026-05-28 superseded Branch C attempt, but none may become current execution basis.
* Authority consumption contract must record:

```text
writer_role = observer_consumer_only
default_compose_input = false
writer_authority = false
publish_authority = false
quality_authority = false
runtime_authority = false
```

* Forbidden writer fields must not be consumed or emitted by this round.
* Record a negative default-compose input guard check: the reconstructed authority is explicit round-local observer input only.

Validation:

* Contract schema validation passes.
* `default_compose_input = false`.
* Forbidden writer field usage count is `0`.
* Historical, staging, diagnostic, and superseded artifacts are rejected as current authority.

---

### Change 3 - Phase 2 Scope Inventory and Scope Split Matrix

Purpose:

Inventory the issue family previously entangled with structural signal, then classify every issue into exactly one of four scope buckets.

Files:

```text
phase2_scope_inventory.jsonl
phase2_inventory_summary.json
structural_signal_scope_split_matrix.json
acq_dominant_remeasurement_boundary.md
```

Implementation Notes:

* Each JSONL row must include at minimum:

```json
{
  "issue_id": "...",
  "issue_family": "...",
  "bucket": "structural_signal_observer_readpoint_seal | acq_dominant_residual_remeasurement | publish_mutation_review | blanket_isolation_forbidden_maintenance",
  "current_round_action": "seal_observer_boundary | future_pointer_only | out_of_scope | maintain_forbidden",
  "current_round_consumed_as_signal": false,
  "publish_candidate_before_remeasurement": false,
  "blanket_isolation_reopen": false,
  "evidence": ["..."]
}
```

* The 4-bucket matrix must define for each bucket:
  * boundary,
  * current round status,
  * allowed action,
  * forbidden action,
  * trigger condition for future round,
  * sealed anchor or separation anchor.
* `ACQ_DOMINANT` is future measurement pointer only. It must not appear as current publish mutation candidate.
* `current_round_consumed_as_signal` indicates whether the issue was consumed as active input to mutation or measurement work. For this observer-only scope seal round, all rows are expected to be `false`; observer readpoint seal rows are sealed/read, not consumed as mutation or measurement signals.
* Define `acq_dominant_publish_candidate_count` as:

```text
count of rows in phase2_scope_inventory.jsonl
where bucket = acq_dominant_residual_remeasurement
AND publish_candidate_before_remeasurement = true
```

* Publish mutation review is out of scope and must not appear as current phase work.
* Blanket isolation forbidden maintenance preserves the existing forbidden state without reopening isolation.

Validation:

```text
phase2_scope_inventory_jsonl_parse_pass = true
unclassified_count = 0
acq_dominant_publish_candidate_count = 0
acq_dominant_remeasurement_performed = false
blanket_isolation_reopen_count = 0
publish_mutation_review_current_phase_count = 0
```

---

### Change 4 - Phase 3 Scope Separation Manifest and Observer Readpoint Seal

Purpose:

Create the positive sealed manifest that future rounds can read to decide whether an issue belongs to structural signal observer/readpoint seal, `ACQ_DOMINANT` remeasurement, publish mutation review, or blanket isolation forbidden maintenance.

Files:

```text
scope_separation_manifest.json
phase3_manifest_validation_report.json
structural_signal_observer_readpoint_seal.json
observer_readpoint_summary.md
```

Implementation Notes:

* `scope_separation_manifest.json` must include all four buckets and their boundaries.
* Each bucket must have a sealed anchor or separation anchor.
* Each bucket must have a trigger condition for future work.
* `scope_separation_manifest.json` remains the current scope-separation readpoint until superseded by an explicit sealed decision, such as `ACQ_DOMINANT Current Baseline Remeasurement Round` closeout or a future scope re-separation round after a source-expansion closeout.
* Future trigger wording must anchor to a sealed decision date and closeout document, not to qualitative wording alone.
* The observer readpoint seal must explicitly record:

```json
{
  "writer_authority": false,
  "publish_authority": false,
  "quality_authority": false,
  "runtime_authority": false
}
```

* The manifest must state that structural signal observer/readpoint seal is not structural signal disposition completion.
* The manifest must state that `ACQ_DOMINANT` remeasurement is a separate future round and not a current publish mutation candidate source.

Validation:

```text
phase3_scope_separation_manifest_schema_pass = true
phase3_unclassified_count_zero = true
all_four_buckets_have_boundary = true
all_four_buckets_have_anchor_or_separation_anchor = true
observer_seal_authority_flags_all_false = true
```

---

### Change 5 - Phase 4 Non-Mutation and Separation Invariant Verification

Purpose:

Prove that this round did not consume out-of-scope signal as current action input and did not mutate quality, publish, runtime, rendered, Lua, or sealed body surfaces.

Files:

```text
separation_invariant_report.json
non_mutation_invariant_report.json
phase4_hash_diff_evidence.json
hash_delta_summary.md
```

Implementation Notes:

* Record these separation invariants and require all to be `0`:

```text
acq_dominant_signal_consumed_count
publish_mutation_signal_consumed_count
blanket_isolation_reopen_signal_count
```

* Record these non-mutation invariants and require all to be `0`:

```text
sealed_body_mutation_count
default_compose_writer_input_mutation_count
runtime_lua_mutation_count
packaged_lua_mutation_count
rendered_text_mutation_count
quality_state_mutation_count
publish_state_mutation_count
runtime_state_mutation_count
quality_baseline_v4_mutation_count
guard_a_redefinition_count
data_root_default_compose_guard_relaxation_count
facts_mutation_count
decisions_row_content_mutation_count
```

* Hash/delta evidence must cover:
  * source facts and decisions row content,
  * rendered text outputs,
  * `quality_state`, `publish_state`, `runtime_state`,
  * runtime Lua and packaged chunks,
  * default compose authority inputs,
  * GUARD-A and default compose data-root guard surfaces,
  * sealed body ranges or files referenced by this round.
* `delta = 0` is measured by SHA-256 diff against `phase0_baseline_hash_manifest.json` unless the invariant explicitly records `git diff absence` as the evidence method.
* Required SHA-256 evidence:
  * current authority input artifacts,
  * all generated round-local artifacts,
  * any governed surface included in `phase0_baseline_hash_manifest.json`.
* Acceptable no-touch evidence:
  * `git diff` absence for untouched runtime Lua/chunks,
  * `git diff` absence for untouched facts/decisions/rendered surfaces,
  * `git diff` absence for untouched sealed docs.

Validation:

* `phase4_separation_invariant_all_zero = true`.
* `phase4_hash_diff_zero_mutation_pass = true`.
* Phase 4 invariants are computed against the Phase 0 baseline or the explicitly recorded `git diff absence` path set.
* Any unexpected mutation blocks success closeout and requires `blocked_unexpected_mutation` or a more specific blocked branch.

---

### Change 6 - Phase 5 Future Round Pointer, Hard Gate, and Artifact Hash Manifest

Purpose:

Separate `ACQ_DOMINANT Current Baseline Remeasurement Round` as a future-only pointer, then decide whether closeout is allowed through a hard gate and artifact hash manifest.

Files:

```text
acq_dominant_current_baseline_remeasurement_round_pointer.json
phase5_hard_gate_report.json
artifact_hash_manifest.json
```

Implementation Notes:

* The future pointer must record:

```text
current_round_performed_remeasurement = false
publish_candidate_before_remeasurement = false
blanket_isolation_allowed = false
future_round_required_for_acq_dominant_baseline = true
future_round_does_not_auto_include_publish_mutation_review = true
acq_dominant_publish_candidate_count = 0
acq_dominant_publish_candidate_count_definition = count of rows in phase2_scope_inventory.jsonl where bucket = acq_dominant_residual_remeasurement AND publish_candidate_before_remeasurement = true
```

* The hard gate must include at least:

```text
phase0_predecessor_verification_pass
phase0_authority_input_hash_match_pass
phase0_reconstruction_hash_manifest_self_hash_pass
phase0_baseline_hash_manifest_generated
phase1_authority_consumption_contract_schema_pass
phase1_default_compose_input_false_pass
phase2_scope_inventory_jsonl_parse_pass
phase3_scope_separation_manifest_schema_pass
phase3_unclassified_count_zero
phase4_separation_invariant_all_zero
phase4_hash_diff_zero_mutation_pass
python_unittest_pass
lua_syntax_pass
determinism_pass
artifact_hash_manifest_generated
all_gates_pass
```

* `artifact_hash_manifest.json` must include every generated artifact from this round and use `sha256`.
* Determinism must include a 2-run digest match for the generated manifest/report set.

Validation:

* `all_gates_pass = true` is required for success closeout.
* Any failed or blocked required gate prevents success closeout.
* `artifact_hash_manifest_generated = true`.

---

### Change 7 - Phase 6 Documentation Addendum Draft and Adversarial Review

Purpose:

Generate draft-only governance text and perform adversarial review before closeout. This phase must not modify sealed governance bodies.

Files:

```text
decisions_addendum_draft.md
roadmap_addendum_draft.md
phase6_adversarial_review.md
```

Implementation Notes:

* `decisions_addendum_draft.md` and `roadmap_addendum_draft.md` are draft-only artifacts under the round-local root.
* Drafts must say this is an observer-only scope seal and must include the non-claim boundary.
* Drafts must not promote themselves into `docs/DECISIONS.md` or `docs/ROADMAP.md`.
* Drafts must repeat the canonical round id, filesystem alias, and unique execution identifier so future cross-reference cannot confuse this round with a prior same-name attempt.
* Promotion of draft addenda into `docs/DECISIONS.md` or `docs/ROADMAP.md` requires a separate explicit doc-update task after this round closeout.
* Phase 6 is the round-internal adversarial self-check. An additional external review may be requested separately and absorbed into the same artifact path or a sibling artifact.
* Phase 6 reviews the draft of Phase 7 closeout claim and non-claim sections. If Phase 7 final wording diverges from the Phase 6-reviewed draft, a Phase 6.1 re-review is required before success closeout.
* `phase6_adversarial_review.md` follows `docs/REVIEW_TEMPLATE.md` section shape and must check:
  * predecessor misanchoring,
  * authority input hash mismatch,
  * consume-only contract overreach,
  * missing bucket classification,
  * `ACQ_DOMINANT` future pointer misread as current permission,
  * publish mutation overreach,
  * blanket isolation reopen,
  * non-mutation invariant coverage,
  * closeout claim overreach.
* Review verdict for success closeout must be `PASS` or `Conditional PASS` with no critical findings. Any critical finding blocks closeout.

Validation:

```text
addendum_draft_only = true
sealed_body_modification_count = 0
adversarial_review_verdict in PASS | Conditional PASS
critical_finding_count = 0
non_claim_section_present = true
phase7_closeout_draft_reviewed = true
phase6_1_rereview_required_if_phase7_wording_changes = true
```

---

### Change 8 - Phase 7 Final Closeout

Purpose:

Close the round with the evidence-bound branch `closed_with_structural_signal_scope_split_sealed_observer_only`, or block with the most specific failed gate branch.

Files:

```text
phase7_closeout.json
phase7_closeout.md
closeout_pass.json
```

Implementation Notes:

* Success closeout requires:

```text
phase5_hard_gate_report.all_gates_pass = true
phase6_adversarial_review verdict = PASS or Conditional PASS
critical_finding_count = 0
closeout_branch = closed_with_structural_signal_scope_split_sealed_observer_only
```

* Claimed section must be limited to:

```text
structural signal scope split sealed
current structural observer/readpoint authority consumed read-only
4 scope bucket boundary sealed
ACQ_DOMINANT remeasurement separated into future round
ACQ_DOMINANT is not a publish mutation candidate before current-baseline remeasurement
blanket isolation reopen remains forbidden
quality / publish / runtime / rendered / Lua mutation did not occur
```

* Not claimed section must include:

```text
structural signal disposition complete
ACQ_DOMINANT remeasurement complete
ACQ_DOMINANT disposition complete
publish mutation review complete
runtime rollout complete
deployed closeout
manual in-game QA pass
release readiness
Workshop readiness
ready_for_release
```

* `closeout_pass.json` is allowed only when every success condition is satisfied.
* `phase7_closeout.json` and `phase7_closeout.md` must repeat:

```text
canonical_round_id = structural_signal_scope_split_seal_round
filesystem_alias = structural_signal_scope_re_seal_round
current_round_unique_identifier = 2026-05-29.structural_signal_scope_split_seal_round.reconstruction_based_re_seal
cross_reference_primary_anchor = Iris/build/description/v2/staging/compose_contract_migration/structural_signal_scope_re_seal_round/
```

* Phase 7 final wording must match the Phase 6-reviewed draft claim/non-claim sections. If it does not, execution returns to Phase 6.1 before success closeout.
* Phase 7 must not promote `decisions_addendum_draft.md` or `roadmap_addendum_draft.md` into top-level governance docs. That promotion is a separate explicit doc-update task after this round closeout.

Validation:

* Closeout JSON is valid.
* Closeout MD exists.
* Claimed and not claimed sections are present.
* Closeout branch matches evidence ceiling.
* No forbidden claim appears.

---

## 7. Validation Plan

### Automated Validation

Required change review:

```powershell
git diff --stat
git diff
```

Required artifact validation:

```text
JSON parse for every generated JSON artifact
JSONL parse for every generated JSONL artifact
sha256 hash manifest for every generated artifact
two-tier authority input hash check against Section 4
Phase 0 baseline hash manifest generation
2-run determinism digest match for generated artifacts
scope inventory unclassified count check
non-mutation invariant zero-count check
acq_dominant_publish_candidate_count calculation
hard gate all_gates_pass check
```

Required Python regression validation:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Success condition:

```text
exit code = 0
observed tests >= 398 unless separately justified
```

Required Lua syntax validation:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Success condition:

```text
exit code = 0
observed files >= 183 unless separately justified
```

If an exact command cannot be run, the result must be recorded as `blocked` or `not_run`, not `pass`.

### Manual Validation

* Inspect Phase 0 predecessor classification and authority hash check.
* Inspect Phase 0 baseline manifest coverage for Phase 4 governed surfaces.
* Inspect Phase 1 contract for `default_compose_input = false`.
* Inspect Phase 2 inventory for missing or duplicated bucket assignments.
* Inspect Phase 2 `acq_dominant_publish_candidate_count` calculation against its row-filter definition.
* Inspect Phase 2 and Phase 5 `ACQ_DOMINANT` handling to ensure it is future-only.
* Inspect Phase 3 scope manifest for four bucket boundaries, anchors, and trigger conditions.
* Inspect Phase 3 manifest lifetime and replacement trigger wording.
* Inspect Phase 4 hash/delta evidence for omitted mutation surfaces.
* Inspect Phase 6 review against `docs/REVIEW_TEMPLATE.md`.
* Inspect Phase 6 confirmation that the draft Phase 7 closeout claim/non-claim sections were reviewed.
* Inspect Phase 7 closeout for claim ceiling and non-claim completeness.

### Validation Limits

This execution will not perform:

* runtime validation
* manual in-game QA
* multiplayer validation
* long-session runtime validation
* deployment validation
* Workshop validation
* external mod compatibility sweep
* semantic quality revalidation
* publish mutation review
* `ACQ_DOMINANT` remeasurement
* source expansion validation
* runtime equivalence validation
* release readiness validation

---

## 8. Risk Surface Touch

### Authority Surface

Consumed read-only without ownership change. The round consumes the 2026-05-28 reconstructed structural observer authority as read-only current execution basis and creates a scope separation seal. It does not create writer authority, publish authority, quality authority, runtime authority, or default compose authority.

### Runtime Behavior Surface

None expected. Runtime Lua, packaged Lua, rendered text, and runtime consumer behavior are immutable for this round.

### Compatibility Surface

None expected. Browser/Wiki/Tooltip behavior, PZ runtime behavior, external mod compatibility, SPI/API boundaries, and runtime payload contracts are out of scope.

### Sealed Artifact Surface

Touched additively by round-local sealed artifacts. New sealed round-local artifacts may be created. Existing sealed bodies and hash-sealed artifacts are read-only and must not be modified.

### Public-Facing Output Surface

None. The round does not change UI, tooltips, wiki/browser text, package output, release notes, Workshop state, or public readiness claims.

---

## 9. Risk Analysis

### Architecture Risk

* Authority overreach: reconstructed observer authority could be treated as writer, publish, quality, runtime, or default compose authority. Phase 1 blocks this with consume-only contract fields.
* Predecessor misanchoring: previous same-name attempt could be read as full seal. Phase 0 classifies it as historical trace or absorbed predecessor only.
* Historical promotion: 2026-04-24 artifacts could be elevated from provenance to current authority. Phase 1 requires source classification and rejection reasons.
* Scope leakage: `ACQ_DOMINANT`, publish mutation review, or blanket isolation reopen could be mixed into structural observer seal. Phase 2 and Phase 4 require bucket separation and zero consumed signals.
* Claim overreach: observer readpoint seal could be worded as structural signal disposition completion. Phase 6 and Phase 7 enforce non-claims.

### Runtime Risk

* Any runtime Lua, packaged chunk, rendered text, or runtime state mutation is a stop-the-line violation.
* Lua syntax pass cannot rescue a round that mutated runtime surfaces without authorization.

### Compatibility Risk

* The round could imply compatibility preservation without compatibility testing. The validation ceiling forbids that claim.
* Publish writer authority could be restated as semantic strength rather than layer/position correctness. Phase 2 matrix must preserve the existing publish authority boundary.

### Regression Risk

* Hash/delta evidence could omit a mutation surface. Phase 4 enumerates required invariant surfaces.
* JSONL inventory could leave unclassified issues. Phase 2 and Phase 3 require `unclassified_count = 0`.
* Future pointer wording could look like current permission. Phase 5 requires explicit `current_round_performed_remeasurement = false` and `publish_candidate_before_remeasurement = false`.
* Invariant evidence could be overread as requiring byte-level hash for every untouched path. Phase 4 distinguishes required SHA-256 evidence from acceptable `git diff` absence evidence.
* Validation could overclaim if tools are missing. Missing tools are blocked, not passed.

---

## 10. Rollback Plan

This round is designed as a zero-mutation observer-only round. Rollback should normally be limited to round-local artifacts and plan drafts created during execution.

Rollback rules:

1. Review touched surfaces with `git diff --stat` and `git diff`.
2. If source facts, source decisions row content, rendered text, runtime Lua/chunks, `quality_state`, `publish_state`, `runtime_state`, default compose authority, GUARD-A, or sealed bodies changed, treat the round as failed and revert only those unauthorized changes after verifying they were created by this round.
3. If `ACQ_DOMINANT` is recorded as a publish mutation candidate, discard the candidate artifact, rewrite the scope matrix, and block closeout until revalidated.
4. If historical artifacts are promoted to current authority, rewrite the authority manifest and re-run Phase 1 validation.
5. If closeout claim overreaches, close as `blocked_claim_overreach` or rewrite the non-claim section before closeout.
6. If non-mutation report coverage is incomplete, hold closeout until Phase 4 is complete.
7. Failed branch artifacts may remain under the round-local root as invalid execution trace, but must be marked invalid and must not become current execution basis.
8. Do not promote `decisions_addendum_draft.md` or `roadmap_addendum_draft.md` into sealed governance bodies as part of rollback or closeout. Promotion requires a separate explicit doc-update task after this round closeout.

This round's failure does not change the sealed status of the 2026-05-28 reconstructed observer authority.

---

## 11. Governance Constraints

* `docs/Philosophy.md` remains the top authority.
* Iris remains a 100% Lua wiki-style module and does not take on recommendation, optimization, or runtime stability roles.
* Hub & Spoke and SPI boundaries remain untouched.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` current readpoints remain authoritative unless superseded by a later sealed decision.
* This plan may create additive round-local evidence only.
* Existing sealed bodies and hash-sealed artifacts must not be modified.
* The 2026-05-28 reconstructed observer authority is consumed read-only.
* The reconstructed observer authority is not default compose input.
* Default compose data-root guard remains unchanged.
* GUARD-A remains unchanged.
* Publish writer authority remains layer/position correctness.
* Semantic narrowness or acquisition dominance alone does not change publish branch.
* `ACQ_DOMINANT` is not a publish mutation candidate before current-baseline remeasurement.
* `FUNCTION_NARROW` and `ACQ_DOMINANT` blanket isolation remain forbidden.
* Missing or blocked validation must not be reported as pass.
* Runtime rollout, deployment, Workshop readiness, release readiness, and `ready_for_release` claims are forbidden.

---

## 12. Expected Closeout State

Expected success closeout:

```text
closed_with_structural_signal_scope_split_sealed_observer_only
```

Success criteria:

```text
phase5_hard_gate_report.all_gates_pass = true
phase6_adversarial_review verdict in PASS | Conditional PASS
critical_finding_count = 0
phase0_baseline_hash_manifest exists
phase0_reconstruction_hash_manifest_self_hash_pass = true
current structural readpoint authority manifest exists
authority consumption contract exists
scope inventory exists
scope separation manifest exists
all 4 scope buckets have boundary / sealed anchor / trigger condition
unclassified_count = 0
ACQ_DOMINANT Current Baseline Remeasurement Round future pointer exists
acq_dominant_publish_candidate_count = 0
acq_dominant_publish_candidate_count uses the Phase 2 row-filter definition
acq_dominant_remeasurement_performed = false
blanket_isolation_reopen_count = 0
facts / decisions / rendered / quality_state / publish_state / runtime_state / Lua bridge / runtime chunks delta = 0
artifact hash manifest generated
2-run determinism digest match
Python unittest exits 0
Lua syntax exits 0
closeout has non-claim section
deployed closeout, manual QA, release readiness, Workshop readiness, ready_for_release are not claimed
```

Blocked closeout must use the most specific blocked branch:

| Blocked branch | Meaning |
|---|---|
| `blocked_predecessor_misanchored` | predecessor or previous same-name attempt cannot be safely classified without overclaiming |
| `blocked_authority_input_hash_mismatch` | current reconstructed authority artifact hash does not match the expected input identity |
| `blocked_authority_consumption_contract_invalid` | consume-only contract is invalid, too broad, or implies writer/default compose authority |
| `blocked_scope_separation_incomplete` | inventory or manifest leaves unclassified issue family or missing bucket boundary |
| `blocked_separation_invariant_violation` | out-of-scope signal was consumed or blanket/publish/measurement boundary was crossed |
| `blocked_non_deterministic_generator` | generated artifacts fail 2-run determinism |
| `blocked_adversarial_review_failed` | Phase 6 review has FAIL or critical unresolved findings |
| `blocked_claim_overreach` | closeout wording exceeds evidence ceiling |
| `blocked_unexpected_mutation` | forbidden quality/publish/runtime/rendered/Lua/sealed body mutation occurred |

Expected final claim:

```text
structural signal scope split sealed
current structural observer/readpoint authority consumed read-only
4 scope bucket boundary sealed
ACQ_DOMINANT remeasurement separated into future round
ACQ_DOMINANT is not a publish mutation candidate before current-baseline remeasurement
blanket isolation reopen remains forbidden
quality / publish / runtime / rendered / Lua mutation did not occur
```

Expected non-claims:

```text
structural signal disposition complete 아님
ACQ_DOMINANT remeasurement complete 아님
ACQ_DOMINANT disposition complete 아님
publish mutation review complete 아님
runtime rollout complete 아님
deployed closeout 아님
manual in-game QA pass 아님
release readiness 아님
Workshop readiness 아님
ready_for_release 아님
```
