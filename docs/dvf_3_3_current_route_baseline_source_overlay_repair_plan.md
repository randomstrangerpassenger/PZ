# Implementation Plan

> Status: planned / WARN review incorporated / no-write diagnostic and classification allowed / contract packet seal and executable handoff gated
> 작성일: 2026-06-23
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Execution 기준: `docs/EXECUTION_CONTRACT.md`
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Primary stable artifact: `docs/dvf_3_3_current_route_baseline_source_overlay_repair_plan.md`
> Predecessor planning trace: `C:/Users/MW/.codex/attachments/25c9684e-d6d9-444f-9e90-4b70fbf8433d/pasted-text.txt` / sha256 `2AB32A71EB7EE772C36B80BCF9A74613B399BB9111CFBD822B6655A0DD474FF0`
> Review input: `C:/Users/MW/.codex/attachments/664961a2-4575-46ad-9326-f4e3d16cc07f/pasted-text.txt` / sha256 `01B6379EED2DF96EDF8B0044721A3567577E00DC56B9EE218BB16C691F67A3DA`
> Stable plan provenance: this plan is the primary docs artifact; no separate pre-plan artifact is required
> Empirical codebase readpoint: 2026-06-23 / live source split-materialization confirmed by no-write inspection
> Evidence root target: `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/`

---

## 1. Objective

DVF 3-3 full current-route failure를 live repair로 바로 고치지 않고, 후속 repair implementation round를 열 수 있는지 판단하기 위한 no-write 선행 분류와 계약을 작성한다.

현재 failure는 Denominator Lock, Terminal Disposition Adjudication, Shared Disposition Ledger Consumption, Live Migration Readiness의 미완료가 아니라 다음 surface의 불일치로 읽는다.

```text
live facts/decisions materialized as 6-row fixture while live manifest expects 2105
corrected 2105 facts/decisions snapshot exists but is not yet authorized live write authority
current 2105 overlay support artifact exists and matches manifest expectation
compose current default can still resolve to staging 6-row overlay support
Base.CanOpener as fixture-leak exemplar unless selected source universe proves membership
compose / current-authority / Layer4 trace source-overlay contract divergence
```

이 계획의 실행 가능 범위는 다음으로 제한한다.

* no-write diagnostic
* inventory
* source / overlay / validator / trace role classification
* heavy no-write authority / governance validation
* non-executable authorization-request draft where needed

이 계획은 WARN review를 반영해 다음을 hard gate로 둔다.

* Phase 4 Branch A/B 또는 equivalent overlay contract가 sealed 상태가 아니면 Phase 6은 executable implementation handoff를 만들 수 없다.
* 모든 runtime-adopted full current-route row는 compose 이전에 `body_source_overlay`를 가져야 한다. absence는 full current route에서 fail-loud다.
* Phase 3 cross-attestation은 Phase 2의 `selected_source_candidate_status == selected`일 때만 실행한다.
* no-write claim은 `phase1/protected_surface_manifest.json`의 path-level protected set과 before/after hash에 의해 검증되어야 한다.
* contract packet seal은 stable plan provenance, overlay contract seal, selected source candidate gate, protected-surface guard, validation report가 모두 닫힌 뒤에만 가능하다.

이 계획의 최대 claim은 다음으로 제한한다.

```text
Current-Route Baseline / Source-Overlay Repair implementation round를 열기 전에
필요한 source classification, source-overlay contract, compose read-path alignment,
Layer4 trace disposition, authorization boundary, future complete gate가 no-write
조건에서 검토 가능한 형태로 작성되었다.
```

이 최대 claim도 Phase 4 overlay contract가 sealed되지 않으면 `implementation_plan_ready`로 승격할 수 없다.

---

## 2. Scope

포함 범위:

* plan input provenance reconciliation: this plan is the stable docs artifact and attachment paths are predecessor traces only
* full current-route failure intake and taxonomy
* path-level protected surface manifest 작성
* protected source / rendered / Lua bridge / runtime / package surface no-mutation proof
* manifest-declared count/hash versus live facts/decisions/overlay actual count/hash drift report
* live `data/dvf_3_3_input_manifest.json`, `data/dvf_3_3_facts.jsonl`, `data/dvf_3_3_decisions.jsonl`, `data/dvf_3_3_overlay_support.jsonl` role classification
* selected source candidate gate 작성
* staging `layer3_body_source_overlay.jsonl` current-route consumption 여부 분류
* corrected source snapshot / successor source artifact 후보 role classification
* corrected 2105 source snapshot hash and row-key comparison against manifest expectations
* `2105` source candidate와 runtime-deployable `2105` universe의 exact row identity cross-attestation, only after selected source candidate is sealed
* all missing-overlay runtime-adopted rows inventory, with `Base.CanOpener` as focused exemplar
* unconditional `body_source_overlay` coverage rule 작성
* compose default read path와 current / staging / historical / diagnostic route separation contract, including current-mode rejection of staging overlay fallback
* current-authority validator baseline and fail-loud rule alignment, including `overlay_path` as a guarded current-authority input
* Layer4 trace artifact / consumer discovery and role matrix
* `layer_boundary_hard_block_namespace` / readpoint-only Layer4 reading preservation
* new no-write diagnostic cap check: diagnostic helpers must not expand the 12-module current active build closure or the cap-1 current-route tooling allowlist
* non-executable authorization request draft, exact target allowlist draft, writer boundary draft, no-write diagnostic validator contract
* future implementation target draft for reconnecting live facts/decisions to an authorized 2105 source snapshot, if Phase 2/3 validate that candidate
* final claim boundary, downstream readiness status, closeout packet

Primary execution evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/`

Direct plan artifact:

* `docs/dvf_3_3_current_route_baseline_source_overlay_repair_plan.md`

### Explicitly Out Of Scope

* contract packet seal while plan provenance is attachment-only / ephemeral-only
* executable implementation handoff while overlay Branch A/B or equivalent source-overlay contract is unsealed
* implementation round 진입
* live `Iris/build/description/v2/data/dvf_3_3_facts.jsonl` write
* live `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl` write
* live `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl` write
* rendered regeneration
* `build_rendered()` current write
* Lua bridge export
* runtime chunk regeneration or replacement
* package route mutation
* adopted required-gate mutation
* current-route PASS / closure claim
* release / Workshop / B42 / deployment readiness claim
* manual in-game QA
* semantic text quality acceptance
* `quality_state`, `publish_state`, `runtime_state` mutation
* terminal disposition re-adjudication
* denominator redefinition
* shared disposition ledger rewrite
* consumer migration live execution
* broad `2105` universe를 새 migration 대상으로 다시 여는 것
* 6-row fixture를 current source authority로 승격하는 것
* runtime-derived payload를 source authority로 역수입하는 것
* compose external repair / post-compose rewrite / runtime-side repair 도입
* `Base.CanOpener`를 selected 2105 source-universe membership 없이 `data/dvf_3_3_overlay_support.jsonl`에 patch하는 것
* new diagnostic helper를 current-route active build closure 또는 current-route tooling allowlist에 추가하는 것

---

## 3. Non-Goals

이 계획은 다음을 해결하려 하지 않는다.

* user-facing Korean text 개선
* Iris browser / tooltip / wiki runtime behavior 변경
* Layer4 publish policy redesign
* full historical byte reproducibility
* public-facing quality pass or publish acceptance
* old chunks와 successor chunks의 동시 current 인정
* current route를 denominator / terminal / shared disposition 문제로 재해석
* closed readpoint를 새 authority 없이 재개방
* staging / generated / diagnostic / fixture artifact를 current authority로 승격
* `adopted / unadopted` vocabulary를 quality-pass / publish-state / deletion / suppression 의미로 확장
* `active / silent` vocabulary를 current vocabulary로 복귀
* independent review completion claim

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 authority이며, Pulse 생태계 경계와 Iris runtime/source 분리가 우선한다.
* `docs/ROADMAP.md`는 Current-Route Baseline / Source-Overlay Repair를 #7 Closeout / Reentry Guard Seal 전의 별도 round candidate로 둔다.
* `docs/ARCHITECTURE.md`는 `CURRENT_FACTS=6` vs `2105`와 missing `body_source_overlay`를 current source baseline / source-overlay contract 문제로 분류한다.
* live source chain은 `Iris/build/description/v2/data/dvf_3_3_input_manifest.json -> dvf_3_3_facts.jsonl -> dvf_3_3_decisions.jsonl -> dvf_3_3_overlay_support.jsonl`로 읽는다.
* `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`은 `compose_support_not_source_authority` 역할이며 source authority 자체가 아니다.
* `body_source_overlay`는 compose support input이며 quality pass, publish state, semantic strength signal이 아니다.
* every runtime-adopted full current-route row must have `body_source_overlay`; absence is fail-loud.
* row identity equivalence는 count equality가 아니라 exact row key identity로 검증한다.
* `Base.CanOpener`는 focused exemplar이며, 모든 missing-overlay runtime-adopted row를 별도로 inventory해야 한다.
* `Base.CanOpener`는 먼저 selected source universe membership을 확인해야 하며, fixture-only row라면 2105 overlay support에 patch하지 않는다.
* 2026-06-23 no-write inspection observed live facts and decisions as 6 rows while `data/dvf_3_3_input_manifest.json` declares 2105 and expected hashes.
* 2026-06-23 no-write inspection observed `data/dvf_3_3_overlay_support.jsonl` as the 2105 overlay support artifact matching the manifest overlay hash.
* 2026-06-23 no-write inspection observed corrected 2105 facts/decisions snapshots under `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/corrected_input_snapshot/` whose hashes match the manifest expected facts/decisions hashes.
* 2026-06-23 no-write inspection observed rendered/runtime-deployable 2105 successor evidence containing `Base.TinOpener` and not `Base.CanOpener`.
* 2026-06-23 no-write compose probe observed corrected 2105 facts + corrected normalized decisions + current 2105 overlay can compose 2105 rows in staging context; this is diagnostic evidence only, not live materialization authorization.
* `Base.CanOpener` is therefore treated as a fixture-leak / mismatched-read-path symptom unless Phase 2 selected source evidence proves otherwise.
* Problem 8 / Closeout-Reentry Guard Seal cannot use this predecessor plan as broad completion; it may consume only the final downstream readiness state emitted by Phase 7.
* 이 라운드의 executable mode는 no-write diagnostic / classification / contract writing이다.
* default validation depth is heavy no-write authority / governance validation.
* heavy runtime validation, rendered regeneration validation, Lua bridge export validation, runtime chunk replacement validation은 이 계획에서 제외한다.
* predecessor planning input is LLM-authored for this round; non-Claude independent adversarial review is a structural precondition of canonical seal and `implementation_plan_ready`.
* Claude review is self-confirmation and cannot satisfy the independent review gate.
* Repository constitution path resolves to `docs/Philosophy.md`; references to `Philosophy.md` in governance language refer to that file in this checkout.

---

## 5. Repository Areas Affected

### Code

Read / diagnostic 대상:

* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tools/build/compose_layer3_item.py`
* `Iris/build/description/v2/tools/build/layer3_current_authority_reconstruction.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_current_authority_cutover.py`
* `Iris/build/description/v2/tools/build/generate_dvf_3_3_overlay_support_artifact.py`
* `Iris/build/description/v2/tools/build/validate_*`

Future authorized implementation touch candidates, not writable in this plan:

* `Iris/build/description/v2/tools/build/compose_layer3_text.py`, for current-mode overlay default path alignment
* `Iris/build/description/v2/tools/build/layer3_current_authority_reconstruction.py`, for guarding `overlay_path` as part of current-authority input context
* `Iris/build/description/v2/tests/test_current_authority_source_path_guard.py`, for current-source path and overlay-path guard coverage
* `Iris/build/description/v2/tests/test_compose_entrypoint_guard_hardening.py`, for compose entrypoint / staging fallback guard coverage
* `Iris/build/description/v2/tests/test_dvf_3_3_vnext_current_authority_cutover.py`, for live facts/decisions 2105 materialization validation after authorization

No live mutation is permitted in this plan. If new helper scripts are needed, they must be no-write diagnostics and must remain outside current-route active build closure and outside the current-route tooling allowlist unless a separate reviewed scope authorizes expansion.

### Docs

* `docs/dvf_3_3_current_route_baseline_source_overlay_repair_plan.md`
* stable plan artifact: `docs/dvf_3_3_current_route_baseline_source_overlay_repair_plan.md`
* no separate per-round pre-plan artifact is required for this plan
* possible closeout / claim boundary packets under `docs/` only after execution
* source references: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/EXECUTION_CONTRACT.md`

### Config

* No config mutation by default.
* `Iris/_docs/round3/current_route_required_validations.json` may be read for alignment, but adopted required-gate mutation is out of scope unless a later authorized round explicitly opens it.
* Candidate-only manifests must be named as candidate / draft / diagnostic and must not be written to live manifest paths.

### Generated Artifacts

All generated artifacts go under:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/`

Expected phase artifact groups:

* `phase0/plan_input_provenance_reconciliation.json`
* `phase0/review_warn_resolution_matrix.md`
* `phase1/protected_surface_manifest.json`
* `phase1/current_route_failure_intake_report.json`
* `phase1/protected_surface_no_mutation_report.json`
* `phase1/current_route_baseline_surface_inventory.json`
* `phase1/live_manifest_vs_actual_hash_drift_report.json`
* `phase1/current_overlay_membership_report.json`
* `phase1/fingerprint_manifest.json`
* `phase1/dirty_baseline_non_overlap_report.json`
* `phase1/new_diagnostic_cap_check.json`
* `phase2/source_baseline_role_classification_report.json`
* `phase2/selected_source_candidate_gate.json`
* `phase2/current_facts_6_disposition_lock.md`
* `phase2/corrected_snapshot_candidate_report.json`
* `phase2/base_canopener_fixture_leak_report.json`
* `phase3/source_runtime_2105_cross_attestation_report.json`
* `phase3/source_runtime_row_identity_diff.jsonl`
* `phase3/cross_attestation_precondition_report.json`
* `phase4/overlay_branch_decision_gate.json`
* `phase4/source_overlay_contract_report.json`
* `phase4/body_source_overlay_coverage_report.json`
* `phase4/body_source_overlay_gap_ledger.jsonl`
* `phase4/compose_overlay_readpath_contract.md`
* `phase4/current_overlay_default_path_contract.json`
* `phase5/current_authority_validator_alignment_report.json`
* `phase5/compose_current_read_path_contract.json`
* `phase5/current_authority_overlay_input_guard_contract.json`
* `phase5/layer4_trace_artifact_consumer_inventory.json`
* `phase5/layer4_trace_consumption_disposition.json`
* `phase5/no_dual_authority_read_report.json`
* `phase6/authorization_request_draft.md`
* `phase6/exact_target_allowlist_draft.json`
* `phase6/authorized_write_runner_boundary_draft.md`
* `phase6/no_write_diagnostic_validator_contract.md`
* `phase6/future_complete_gate_spec.json`
* `phase6/residual_isolation_rule.md`
* `phase6/handoff_blocker_report.json`
* `phase7/final_current_route_baseline_source_overlay_repair_predecessor_report.json`
* `phase7/downstream_repair_readiness_status.json`
* `phase7/claim_boundary.md`
* `phase7/plan_closeout_packet.md`
* `phase7/current_route_baseline_repair_contract_packet_draft.md`
* `phase7/current_route_baseline_repair_contract_packet.sealed.md`, only after all seal gates pass

---

## 6. Planned Changes

### Change 1 - Review Resolution / Plan Input Provenance / Execution Gate

Purpose:

WARN review의 blocking 항목을 execution gate로 반영하고, this plan document를 stable docs artifact로 둔다. Ephemeral attachment path는 predecessor trace로만 기록하며, 별도 pre-plan artifact는 요구하지 않는다.

Files:

* primary stable artifact: `docs/dvf_3_3_current_route_baseline_source_overlay_repair_plan.md`
* predecessor trace, optional: `C:/Users/MW/.codex/attachments/25c9684e-d6d9-444f-9e90-4b70fbf8433d/pasted-text.txt`
* read: `C:/Users/MW/.codex/attachments/664961a2-4575-46ad-9326-f4e3d16cc07f/pasted-text.txt`
* write evidence only: `phase0/plan_input_provenance_reconciliation.json`
* write evidence only: `phase0/review_warn_resolution_matrix.md`

Implementation Notes:

* Record stable plan artifact hash, predecessor planning trace hash if available, and review input hash.
* `phase0/plan_input_provenance_reconciliation.json` must include:

```json
{
  "canonical_plan_artifact_status": "exact_path | missing",
  "canonical_plan_artifact_path": "docs/dvf_3_3_current_route_baseline_source_overlay_repair_plan.md",
  "canonical_plan_sha256": "... or null",
  "separate_preplan_artifact_required": false,
  "predecessor_planning_trace_sha256": "2AB32A71EB7EE772C36B80BCF9A74613B399BB9111CFBD822B6655A0DD474FF0",
  "attachment_available": true,
  "phase0_pass_allowed_without_attachment": true
}
```

* If this plan artifact is missing or cannot be hashed, close as `revised_plan_needed`; do not invent or require a separate pre-plan file.
* No-write diagnostic / classification may proceed when this plan exists at the stable docs path; attachment-only provenance is insufficient for seal.
* Record which WARN issues are resolved in plan text and which remain mandatory future seal gates.

Validation:

* stable plan hash reconciliation present
* attachment path is optional predecessor trace, not primary input
* exact plan path schema present, with `separate_preplan_artifact_required = false`
* review WARN issues mapped to plan sections
* no claim that review WARN equals PASS

---

### Change 2 - Failure Intake / Protected Surface Manifest / Fingerprint Baseline

Purpose:

full current-route failure를 단일 오류로 뭉개지 않고 source baseline mismatch, overlay missing, compose read-path mismatch, Layer4 trace consumption mismatch로 분해하며, no-write guarantee를 path-level로 증명한다.

Files:

* read: `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
* read: `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
* read: `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
* read: `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`
* write evidence only: `phase1/protected_surface_manifest.json`
* write evidence only: `phase1/live_manifest_vs_actual_hash_drift_report.json`
* write evidence only: `phase1/current_overlay_membership_report.json`
* write evidence only: `phase1/*`

Implementation Notes:

* `phase1/protected_surface_manifest.json` is the first required Phase 1 artifact.
* Manifest must include:

```json
{
  "protected_live_source_paths": [],
  "protected_rendered_paths": [],
  "protected_lua_bridge_paths": [],
  "protected_runtime_chunk_paths": [],
  "protected_package_paths": [],
  "allowed_evidence_write_root": "Iris/build/description/v2/staging/dvf_3_3_current_route_baseline_source_overlay_repair/",
  "dirty_baseline_policy": "record_and_exclude_unrelated_dirty | fail_closed",
  "hash_before": {},
  "hash_after": {},
  "changed_count": 0
}
```

* Run current-route diagnostic only if protected-surface no-write guard is active.
* Record observed `CURRENT_FACTS=6`, expected `2105`, facts hash drift, decisions hash drift, overlay hash match/mismatch, all missing `body_source_overlay` rows, compose overlay path, and Layer4 trace failures separately.
* `phase1/live_manifest_vs_actual_hash_drift_report.json` must distinguish:
  * manifest-declared facts count/hash versus actual live facts count/hash
  * manifest-declared decisions count/hash versus actual live decisions count/hash
  * manifest-declared overlay count/hash versus actual live overlay count/hash
* `phase1/current_overlay_membership_report.json` must record whether `Base.CanOpener`, `Base.TinOpener`, and every selected fixture-exemplar row is present in the live 2105 overlay support artifact.
* Treat staging overlay path as discovered value, not pre-asserted truth, until Phase 1 read-path discovery records it.
* Produce dirty baseline / unrelated user-change isolation evidence.
* Produce new diagnostic cap check showing no active-core closure or tooling allowlist expansion.

Validation:

* protected surface manifest validator
* protected `changed_count = 0`
* dirty baseline / unrelated user-change isolation validator
* inventory completeness check
* manifest-declared versus actual count/hash drift validation
* current overlay support count/hash membership validation
* fingerprint reproducibility check
* failure taxonomy includes source count, overlay coverage, read path, validator, and Layer4 trace axes
* diagnostic cap check passes

---

### Change 3 - Source Baseline Role Classification / Selected Source Candidate Gate

Purpose:

6-row facts / decisions surface를 full current authority로 승격하지 않고 role disposition하며, Phase 3 cross-attestation에 들어갈 selected source candidate를 명시적으로 고른다.

Files:

* read: live facts / decisions / manifest
* read: corrected source snapshot / manifest if present
* read candidate: `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/corrected_input_snapshot/dvf_3_3_facts.corrected.jsonl`
* read candidate: `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/corrected_input_snapshot/dvf_3_3_decisions.corrected.normalized.jsonl`
* write evidence only: `phase2/source_baseline_role_classification_report.json`
* write evidence only: `phase2/selected_source_candidate_gate.json`
* write evidence only: `phase2/current_facts_6_disposition_lock.md`
* write evidence only: `phase2/corrected_snapshot_candidate_report.json`
* write evidence only: `phase2/base_canopener_fixture_leak_report.json`

Implementation Notes:

* Compare manifest-declared `2105` expectation against live facts / decisions count.
* Identify whether corrected source snapshot is live authority, candidate source artifact, or diagnostic recovery artifact. At the 2026-06-23 readpoint it is only a candidate, not live write authority.
* Forbid runtime-derived payload as source authority.
* `phase2/corrected_snapshot_candidate_report.json` must compare corrected snapshot hashes and row keys against `data/dvf_3_3_input_manifest.json`.
* `phase2/base_canopener_fixture_leak_report.json` must record whether `Base.CanOpener` appears in live 6-row facts, selected 2105 candidate, current overlay support, rendered output, and runtime-deployable evidence.
* `phase2/selected_source_candidate_gate.json` must include:

```json
{
  "selected_source_candidate_status": "selected | blocked_no_candidate | blocked_multiple_candidates | blocked_forbidden_provenance",
  "selected_source_candidate_facts_path": null,
  "selected_source_candidate_decisions_path": null,
  "selection_basis": null,
  "manifest_hash_match": false,
  "base_canopener_classification": "selected_source_member | fixture_leak | unresolved",
  "forbidden_inputs_rejected": [
    "runtime-derived payload",
    "rendered-only artifact",
    "staging-only artifact",
    "diagnostic-only artifact"
  ]
}
```

* Stop Phase 3 if `selected_source_candidate_status != selected`.
* Stop the round if source baseline cannot be classified without importing a forbidden authority.

Validation:

* selected source candidate selection validator
* role taxonomy covers every source-like surface
* `CURRENT_FACTS=6` is not accepted as full current authority
* manifest drift is fail-loud
* corrected snapshot candidate hash / row-key comparison is recorded before selection
* `Base.CanOpener` is classified before any overlay support action
* no source authority is imported from runtime / rendered / staging-only / diagnostic-only artifacts
* multiple candidate state blocks cross-attestation

---

### Change 4 - `2105` Row Identity Cross-Attestation

Purpose:

selected source candidate와 runtime-deployable `2105` universe가 count equality가 아니라 exact row identity 기준으로 같은 universe인지 검증한다.

Files:

* read: selected source candidate from Phase 2
* read: runtime chunk manifest / runtime-deployable evidence
* read: `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`
* write evidence only: `phase3/cross_attestation_precondition_report.json`
* write evidence only: `phase3/source_runtime_2105_cross_attestation_report.json`
* write evidence only: `phase3/source_runtime_row_identity_diff.jsonl`

Implementation Notes:

* Phase 3 runs only when `selected_source_candidate_status == selected`.
* Compare row keys exactly.
* Separate missing rows, additional rows, divergent rows, vocabulary divergence.
* Keep text equivalence, semantic quality, publish state, and rendered promotion out of the claim.
* If identity diverges, close downstream status as `blocked_source_identity_mismatch`.

Validation:

* Phase 3 precondition validator
* exact row-key identity validation
* missing / additional / divergent row reports
* adopted / unadopted vocabulary validation
* denominator non-substitution self-check

---

### Change 5 - Source-Overlay Contract / Compose Default Overlay Read Path

Purpose:

full current-route에서 어떤 overlay artifact를 current source-overlay support로 읽을 수 있는지 봉인하거나, 봉인 실패 시 handoff를 차단한다.

Files:

* read: `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`
* read: discovered staging overlay path from Phase 1
* read: compose tooling
* write evidence only: `phase4/overlay_branch_decision_gate.json`
* write evidence only: `phase4/source_overlay_contract_report.json`
* write evidence only: `phase4/body_source_overlay_coverage_report.json`
* write evidence only: `phase4/body_source_overlay_gap_ledger.jsonl`
* write evidence only: `phase4/compose_overlay_readpath_contract.md`
* write evidence only: `phase4/current_overlay_default_path_contract.json`

Implementation Notes:

* Branch A candidate: include `data/dvf_3_3_overlay_support.jsonl` as current compose support, with role `compose_support_not_source_authority`.
* Branch B candidate: fail-closed if full current route consumes staging 6-row `layer3_body_source_overlay.jsonl`.
* At the 2026-06-23 readpoint, `data/dvf_3_3_overlay_support.jsonl` is the 2105 overlay support artifact and should be treated as already-present support, not as missing source data.
* `phase4/current_overlay_default_path_contract.json` must state whether current compose default currently resolves to `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl` or to staging `layer3_body_source_overlay.jsonl`.
* If current compose default resolves to staging `layer3_body_source_overlay.jsonl`, classify that as current-route read-path drift to be fixed in the authorized implementation round.
* Branch A/B or equivalent overlay contract must be resolved before any executable implementation handoff.
* If Branch A/B remains unresolved:
  * close downstream as `blocked_overlay_contract_unsealed`
  * do not produce `implementation_plan_ready`
  * do not produce executable implementation handoff
  * Phase 6 may only emit diagnostic authorization-request drafts
* Every runtime-adopted full current-route row must have `body_source_overlay`.
* Absence is fail-loud in the full current route.
* No row-level non-blocking exception is available in this plan. A future exception path would require a separate approved policy with row identity, evidence, named authority, fail-loud default, and dedicated validator.
* Inventory all missing-overlay runtime-adopted rows; keep `Base.CanOpener` as focused exemplar.
* `Base.CanOpener` must be classified as selected source-universe member or fixture-leak symptom before any overlay action. If it is absent from the selected 2105 source candidate and runtime-deployable 2105 evidence, do not patch it into the 2105 overlay support artifact.

Validation:

* Phase 4 sealed-branch dependency validator
* overlay row coverage validation
* runtime-adopted row overlay requirement validation
* missing-overlay all-row inventory validation
* compose default overlay path validation
* current overlay default path contract validation
* staging overlay current-route fail-closed validation
* `Base.CanOpener` focused trace

---

### Change 6 - Compose / Current-Authority Validator / Layer4 Trace Alignment

Purpose:

compose, current-authority validator, and Layer4 trace consumer가 같은 current-route source-overlay contract를 소비하도록 정렬한다.

Files:

* read: compose tools and validators
* read: Layer4 trace artifacts / consumers
* write evidence only: `phase5/compose_current_read_path_contract.json`
* write evidence only: `phase5/current_authority_validator_alignment_report.json`
* write evidence only: `phase5/current_authority_overlay_input_guard_contract.json`
* write evidence only: `phase5/layer4_trace_artifact_consumer_inventory.json`
* write evidence only: `phase5/layer4_trace_consumption_disposition.json`
* write evidence only: `phase5/no_dual_authority_read_report.json`

Implementation Notes:

* Separate current / staging / historical / diagnostic read contexts.
* Forbid fixture / staging overlay fallback in current mode.
* Require current compose mode to consume the sealed current overlay support path from Phase 4, not the 6-row staging overlay, unless the run is explicitly marked staging / diagnostic.
* Require current-authority validator to treat `2105` as the expected full current baseline unless Phase 2 blocks.
* Extend current-authority input context so `overlay_path` is guarded alongside facts, decisions, profiles, identity rules, and precedence rules.
* `phase5/current_authority_overlay_input_guard_contract.json` must specify the expected overlay path, allowed context labels, fail-closed behavior, and tests that reject staging overlay fallback in current mode.
* Discover Layer4 trace artifacts and consumers explicitly before disposition.
* Classify Layer4 trace as diagnostic trace, historical readpoint, follow-up candidate, `layer_boundary_hard_block_namespace` readpoint-only surface, or forbidden-current-looking surface; never as source authority.
* Preserve `layer_boundary_hard_block_namespace` reading where applicable.
* Prevent raw audit / readiness / dry-run / predecessor artifacts from reentering execution authority.

Validation:

* current compose read-path validation
* no staging fallback in current mode
* current-authority validator path validation
* current-authority `overlay_path` guard validation
* Layer4 trace artifact / consumer discovery validator
* `layer_boundary_hard_block_namespace` preservation check
* `RAW_AUTHORITY_READ=0`
* `DUAL_AUTHORITY_READ=0`
* `PREDECESSOR_REENTRY=0`
* Layer4 read-only boundary check

---

### Change 7 - Authorization Boundary / Non-Executable Handoff Drafts

Purpose:

후속 repair implementation round가 사용할 수 있는 입력, 쓰기 대상, 실행자, 검증자, 금지 범위를 draft로 정리하되, 이 라운드 산출물이 실행 승인처럼 읽히지 않게 한다.

Files:

* write evidence only: `phase6/authorization_request_draft.md`
* write evidence only: `phase6/exact_target_allowlist_draft.json`
* write evidence only: `phase6/authorized_write_runner_boundary_draft.md`
* write evidence only: `phase6/no_write_diagnostic_validator_contract.md`
* write evidence only: `phase6/future_complete_gate_spec.json`
* write evidence only: `phase6/residual_isolation_rule.md`
* write evidence only: `phase6/handoff_blocker_report.json`

Implementation Notes:

* If live materialization reconnect is needed, request authorization; do not execute it in this plan.
* If `overlay_contract_status != sealed`, executable handoff is forbidden.
* If Phase 2/3 select the corrected 2105 source snapshot, the target allowlist draft may propose live reconnect of `Iris/build/description/v2/data/dvf_3_3_facts.jsonl` and `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`; it must not include overlay rewrite unless Phase 4 proves overlay artifact drift.
* If Phase 4/5 identify current compose default or validator guard gaps, the target allowlist draft may separately list code/test hardening candidates; these remain non-executable until authorized.
* Any Phase 6 handoff-related artifact must include:

```json
{
  "execution_authorized": false,
  "requires_separate_authorization": true,
  "forbidden_to_run_as_writer": true
}
```

* Exact target allowlist draft must not include rendered, Lua bridge, runtime chunks, package route, or broad `data/` glob.
* Exact target allowlist draft must explain why `data/dvf_3_3_overlay_support.jsonl` is excluded when its count/hash already matches manifest.
* Write runner and no-write diagnostic validator must remain separate.
* Authorization request is not authorization granted.
* Residual 6-row fixture, staging overlay, stale bridge, predecessor trace must be isolated as historical / diagnostic residue.
* `future_complete_gate_spec.json` must include `non_claude_independent_adversarial_review_passed`.
* LLM-authored predecessor planning input plus same-family LLM review is self-confirmation and cannot satisfy the independent review gate.
* This plan does not claim independent review completion.

Validation:

* Phase 6 handoff blocker validator
* authorization requirement checklist
* target allowlist completeness validation
* forbidden target validation
* writer / validator boundary validation
* no-write guarantee validation
* non-executable handoff metadata validation
* downstream complete gate dry validation

---

### Change 8 - Closeout Packet / Downstream Readiness Classification

Purpose:

이 선행 라운드를 full current-route closure가 아니라 downstream diagnostic / authorization-pending / blocked state로 닫는다.

Files:

* write evidence only: `phase7/final_current_route_baseline_source_overlay_repair_predecessor_report.json`
* write evidence only: `phase7/downstream_repair_readiness_status.json`
* write evidence only: `phase7/claim_boundary.md`
* write evidence only: `phase7/plan_closeout_packet.md`
* write evidence only: `phase7/current_route_baseline_repair_contract_packet_draft.md`
* write evidence only, seal-gated: `phase7/current_route_baseline_repair_contract_packet.sealed.md`

Implementation Notes:

* Closeout labels are restricted by gates:
  * `partial`
  * `blocked_authorization_pending`
  * `blocked_source_identity_mismatch`
  * `blocked_reclassification_required`
  * `blocked_source_candidate_unsealed`
  * `blocked_overlay_contract_unsealed`
  * `revised_plan_needed`
* Before all gates pass, the only contract packet artifact is `phase7/current_route_baseline_repair_contract_packet_draft.md`.
* After all gates pass, including non-Claude independent adversarial review, the sealed artifact name is `phase7/current_route_baseline_repair_contract_packet.sealed.md`.
* `implementation_plan_ready` is allowed only if stable plan provenance, selected source candidate, row identity, sealed overlay contract, read-path alignment, protected no-mutation, non-executable handoff metadata, non-Claude independent adversarial review, and claim-boundary validation all pass.
* `implementation_plan_ready` also requires the 2026-06-23 split-materialization findings to be reconciled or superseded by newer evidence: live facts/decisions drift, overlay hash status, corrected snapshot status, compose default overlay path, and `Base.CanOpener` classification.
* No-write diagnostic success must not be read as live repair success.
* Reviewer-independence wiring may be author-reserved, but the disclosure-level requirement is mandatory: Claude review alone cannot seal this round.
* A later implementation round must cite this contract packet draft and separately prove authorization before mutation.

Validation:

* final report completeness validation
* protected no-mutation validation
* required deliverables present
* claim boundary validation
* downstream status one-of validation
* closeout label gate validation
* contract packet completeness self-check

---

## 7. Validation Plan

### Automated Validation

Required for this no-write plan execution:

* plan input provenance reconciliation validator
* WARN issue resolution matrix check
* protected-surface manifest validator
* protected-surface hash before / after diagnostics
* dirty baseline / unrelated user-change isolation validator
* live manifest versus actual count/hash drift validator
* current overlay support membership validator
* inventory completeness validator
* fingerprint reproducibility validator
* new diagnostic cap check
* source baseline role taxonomy validator
* selected source candidate selection validator
* corrected snapshot candidate hash / row-key validator
* `Base.CanOpener` fixture-leak classification validator
* Phase 3 cross-attestation precondition validator
* exact row identity cross-attestation validator
* Phase 4 sealed-branch dependency validator
* overlay coverage validator
* all missing-overlay runtime-adopted row inventory validator
* compose read-path validator
* current overlay default path contract validator
* current-authority validator alignment checker
* current-authority `overlay_path` guard checker
* Layer4 trace artifact / consumer discovery validator
* Layer4 trace role classification validator
* no raw-authority read / no dual-authority read / no predecessor reentry checks
* Phase 6 handoff blocker validator
* non-executable handoff metadata validator
* non-Claude independent adversarial review gate validator for seal / `implementation_plan_ready`
* claim-boundary lint
* downstream status one-of validation
* closeout label gate validation

Preferred command style:

* `uv run python <script>` for Python diagnostics if `uv` is available
* targeted `python -B -m unittest ...` only when a new or existing unittest directly validates this scope

Validation depth:

* Default for this plan is heavy no-write authority / governance validation.
* Heavy runtime validation is excluded.
* Rendered regeneration validation is excluded.
* Lua bridge export validation is excluded.
* Runtime chunk replacement validation is excluded.
* Package route validation is excluded.

### Manual Validation

Manual review is limited to document / evidence review:

* confirm stable plan provenance exists before any seal claim
* confirm every source-like artifact has one role
* confirm live facts/decisions count/hash drift is separated from live overlay support count/hash status
* confirm `CURRENT_FACTS=6` is not current authority
* confirm selected source candidate is singular, evidenced, and not forbidden-provenance
* confirm corrected 2105 snapshot, if selected, matches manifest hash and row-key expectations
* confirm `Base.CanOpener` is classified as selected source member or fixture leak before overlay action
* confirm `body_source_overlay` remains compose support only
* confirm every runtime-adopted full current-route row has overlay coverage or fail-loud blocker status
* confirm current compose mode does not silently consume staging `layer3_body_source_overlay.jsonl`
* confirm current-authority validation guards `overlay_path`
* confirm Branch A/B overlay decision is sealed before handoff
* confirm Layer4 trace disposition preserves readpoint-only / `layer_boundary_hard_block_namespace` status
* confirm authorization request is not written as authorization granted
* confirm closeout text does not claim full current-route PASS
* confirm non-Claude independent adversarial review passed before any canonical seal or `implementation_plan_ready` claim
* confirm Claude review is not counted as the independent review gate

### Validation Limits

This plan will not perform:

* full current-route PASS validation
* broad current-route green validation
* live source write validation
* live materialization validation
* rendered regeneration validation
* Lua bridge export validation
* runtime chunk replacement validation
* package route validation
* release / Workshop / B42 / deployment validation
* manual in-game validation
* long-session runtime validation
* multiplayer validation
* external mod compatibility sweep
* semantic text quality acceptance
* public-facing behavior validation
* full runtime equivalence validation
* independent review execution; canonical seal remains blocked until non-Claude independent adversarial review is separately performed and passed

---

## 8. Risk Surface Touch

### Authority Surface

Authority mutation: none.

Authority classification impact: yes. The round classifies live source, selected source candidate, overlay support, staging overlay, rendered/runtime evidence, validators, and Layer4 trace roles. Classification must not become live source mutation.

### Runtime Behavior Surface

None. Runtime Lua, deployed chunks, Browser, Wiki, Tooltip behavior, and in-game behavior are not changed.

### Compatibility Surface

Runtime compatibility impact: none.

Build / validation route compatibility may be affected in a later authorized implementation if staging fallback is fail-closed. This plan only records the contract and requires an explicit later authorization before mutation.

### Sealed Artifact Surface

Concern. This plan can produce documentation and staging evidence artifacts, but seal is gated. Contract packet seal is blocked until stable plan provenance, selected source candidate, overlay contract, protected no-mutation, heavy no-write authority validation, and non-Claude independent adversarial review all pass.

### Public-Facing Output Surface

None. Public text, tooltip, Browser, Wiki, Workshop description, release note, and package metadata are not changed.

---

## 9. Risk Analysis

### Architecture Risk

* 6-row fixture can be mistaken for full current authority.
* `data/dvf_3_3_overlay_support.jsonl` can be over-read as source authority instead of compose support.
* `Base.CanOpener` can be incorrectly patched into 2105 overlay support when the real issue is fixture leakage or mismatched current read path.
* `body_source_overlay` can be weakened if any exception path is reintroduced without a separate approved policy.
* Layer4 trace can be promoted from diagnostic / readpoint evidence into production authority.
* current / staging / historical / diagnostic routes can be collapsed into one implicit fallback path.
* facts/decisions hash drift can be conflated with overlay support drift even when the overlay artifact already matches manifest.
* new diagnostic helpers can silently expand current active build closure or tooling allowlist if cap checks are missing.

### Runtime Risk

* Direct runtime risk is low because no runtime files are changed.
* Indirect risk exists if no-write evidence is later misread as approval for runtime chunk replacement.
* Runtime-derived payload could be incorrectly imported as source truth if claim boundaries are weak.

### Compatibility Risk

* Future fail-closed staging fallback can break current tooling that quietly depended on staging overlay paths.
* Existing focused fixture routes can be broken if `CURRENT_FACTS=6` is deleted or reclassified without route separation.
* Validators can become too broad if exact target allowlist is replaced by path globs.
* Changing compose defaults without extending current-authority `overlay_path` guard tests can leave an unguarded fallback path.
* Candidate-only manifests can be mistaken for live manifest mutation if naming is ambiguous.

### Regression Risk

* default current contract route's existing PASS state can be regressed by over-broad validation changes.
* Denominator / Terminal / Shared Disposition gates can be reopened accidentally if failure attribution is not kept separate.
* no-mutation reports can miss dirty baseline noise unless baseline hash and dirty non-overlap are recorded.
* closeout labels can overclaim implementation completion.
* Phase 6 draft artifacts can be misread as executable handoff.

---

## 10. Rollback Plan

This plan is no-write against live source / rendered / Lua bridge / runtime / package surfaces, so rollback is documentation and staging evidence rollback.

* If a generated evidence artifact overclaims source authority, mark it `superseded / invalid_predecessor` and regenerate with corrected claim boundary.
* If `CURRENT_FACTS=6` classification is wrong, discard the Phase 2 disposition and close as `blocked_reclassification_required`.
* If selected source candidate gate admits multiple candidates or forbidden provenance, invalidate Phase 3 and close as `blocked_source_candidate_unsealed`.
* If cross-attestation is wrong, set downstream status to `blocked_source_identity_mismatch` and do not hand off implementation.
* If overlay contract permits staging fallback silently, replace it with a fail-closed contract or close as `blocked_overlay_contract_unsealed`.
* If Branch A/B remains unresolved, remove any executable handoff language and retain only diagnostic authorization-request drafts.
* If authorization request reads like execution approval, split request / runner / validator documents and reissue claim boundary.
* If protected no-mutation validation fails, mark all round deliverables non-authoritative and open a separate incident for the mutation.
* If any live `data/`, rendered, Lua bridge, runtime chunk, or package file is modified during this round, revert only this round's own changes and do not touch unrelated user changes.
* If a current required-validation manifest is edited without explicit authorization, revert or quarantine that edit as candidate-only.
* If stable plan provenance cannot be produced, close as `revised_plan_needed` and do not seal a contract packet.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Hub & Spoke / Iris runtime-source separation must remain intact.
* Source / facts / decisions / rendered / Lua bridge / runtime chunks authority ownership must not be bypassed.
* runtime does not validate source, compose source, repair source, judge semantic quality, or decide publish policy.
* build-time and runtime authority surfaces must remain separated.
* runtime-derived payload must not be imported as source authority.
* corrected source snapshot must not become live write authority without authorization.
* raw audit / readiness / dry-run / predecessor artifacts must not become execution authority.
* Denominator / Terminal / Shared Disposition are not reopened by this round.
* live `data/` writes are forbidden in this round.
* rendered regeneration, Lua bridge export, runtime chunk replacement, package route mutation are forbidden.
* `adopted_required_gate` and runtime row vocabulary `adopted` must remain separate concepts.
* `adopted / unadopted` must not become quality-pass / publish-state / deletion / suppression semantics.
* 6-row fixture must not become current source authority.
* `Base.CanOpener` must not be promoted into 2105 overlay support unless selected source-universe membership is independently proven.
* staging / generated / diagnostic / fixture artifacts must not be silently promoted.
* current-route failure must not be reclassified as denominator / terminal / shared disposition failure.
* FAIL-LOUD / FAIL-CLOSED behavior must be preserved.
* every runtime-adopted full current-route row must have `body_source_overlay`; absence is fail-loud.
* current compose mode must not silently consume staging overlay support.
* current-authority input context must guard `overlay_path` after the authorized implementation round opens that surface.
* selected source candidate must be singular, evidenced, and not forbidden-provenance before Phase 3.
* exact target allowlist is required before any future authorized write round.
* no-write diagnostic validator and authorized write runner must remain separate.
* Phase 6 handoff artifacts must be non-executable unless separate authorization is granted.
* new no-write diagnostics must not expand current-route active build closure or tooling allowlist without a separate reviewed scope.
* independent review completion must not be claimed unless independently performed.
* canonical seal and `implementation_plan_ready` require non-Claude independent adversarial review passed; Claude review cannot satisfy this gate.

---

## 12. Expected Closeout State

Expected closeout is not `complete`.

Allowed closeout states:

* `partial`
* `blocked_authorization_pending`
* `blocked_source_identity_mismatch`
* `blocked_reclassification_required`
* `blocked_source_candidate_unsealed`
* `blocked_overlay_contract_unsealed`
* `revised_plan_needed`
* `implementation_plan_ready`, only if all readiness gates below pass

`implementation_plan_ready` requires all of the following:

* stable plan provenance is present and hash-reconciled at `docs/dvf_3_3_current_route_baseline_source_overlay_repair_plan.md`
* WARN review blocking items are resolved or explicitly blocked
* protected surface manifest exists with `changed_count = 0`
* live manifest versus actual facts/decisions/overlay count/hash drift is recorded and reconciled
* `Base.CanOpener` is classified as selected source member or fixture leak before any overlay action
* selected source candidate status is `selected`
* source/runtime row identity cross-attestation passes
* Branch A/B or equivalent overlay contract is sealed
* all runtime-adopted full current-route rows have `body_source_overlay` or fail-loud blocker disposition
* compose / current-authority / Layer4 trace alignment reports pass, including current compose default path and current-authority `overlay_path` guard
* Phase 6 artifacts are explicitly non-executable
* non-Claude independent adversarial review passed
* no adopted required-gate mutation is claimed
* claim-boundary lint passes
* sealed packet, if emitted, uses `phase7/current_route_baseline_repair_contract_packet.sealed.md`; otherwise the packet remains `phase7/current_route_baseline_repair_contract_packet_draft.md`

If Phase 4 Branch A/B or equivalent overlay contract is unresolved:

* close as `blocked_overlay_contract_unsealed`
* do not emit executable `implementation_handoff_packet`
* do not close as `implementation_plan_ready`
* Phase 6 may emit only diagnostic authorization-request drafts

If live materialization reconnect is required but not authorized, close as `blocked_authorization_pending`.

If `2105` source/runtime row identity fails, close as `blocked_source_identity_mismatch`.

If stable plan provenance is unavailable, close as `revised_plan_needed`. Attachment predecessor trace alone is insufficient.

If Phase 1 disproves the plan hypothesis, close as `revised_plan_needed`.

This closeout must not claim:

* full current-route PASS
* current source authority recovery complete
* live `data/` materialization
* rendered regeneration
* Lua bridge export
* runtime chunk replacement
* package / release / Workshop / B42 readiness
* manual in-game validation
* independent review completion unless a separate review gate actually occurred
