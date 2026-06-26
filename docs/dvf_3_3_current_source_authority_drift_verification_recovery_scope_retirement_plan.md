# Implementation Plan

> Status: planned / roadmap-derived / review_passed / execution_ready_after_phase0_inventory / read-only verification / recovery scope retirement planned
> 작성일: 2026-06-24
> Roadmap input: `C:/Users/MW/.codex/attachments/fd3e068d-4576-4e34-9040-31c3f5838a18/pasted-text.txt` / sha256 `F880F8DD64F5123C57F7FD3798B676019A28D3000EAD05006899C201E40AC9DC` / lines `474`
> Feedback input: `C:/Users/MW/.codex/attachments/e710a4d8-2349-43ca-9f02-b381896ec0b6/pasted-text.txt` / sha256 `BCF49CD372EE16DCE3AC411E966769C4BFFCA3052F090ECAFE5E6534626175E5` / lines `302` / pre-revision plan-level verdict `FAIL` / requested revisions incorporated
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Primary stable artifact: `docs/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement_plan.md`
> Evidence root target: `Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement/`
> Execution readiness rule: review has passed at plan level, but execution may proceed only after Phase 0 inventory reports no unresolved `missing_blocks_validation` blocker.

---

## 1. Objective

DVF 3-3 Current Source Authority Drift Verification / Recovery Scope Retirement 라운드를 실행하기 위한 계획을 작성한다.

이 계획의 목적은 기존 `Current Source Authority Drift Recovery` 전제가 현재 checkout에서 여전히 live source 복구를 요구하는지 read-only로 검증하고, stale premise가 확인된 Recovery 범위를 current execution authority에서 은퇴시켜 future drift contingency로 격하하는 것이다.

이번 라운드는 source 복구, live write, cutover, rendered regeneration, Lua bridge export, runtime chunk replacement, package mutation, release readiness 선언이 아니다. 현재 최대 claim은 다음으로 제한한다.

```text
current_source_authority_drift_verification_recovery_scope_retirement_complete
Source manifest, facts, decisions, and overlay_support are verified against
the vNext successor 2105 identity.
Current-route consumers, direct compose, and rendered input contract consume
the successor current source identity without known missing overlay regression.
No current-looking 6-entry fixture payload or predecessor current-authority
reentry is present.
The prior Recovery live-write plan is retired to future-drift contingency only.
No source / rendered / Lua bridge / runtime / package mutation was performed.
```

이 completion token은 이 라운드의 read-only verification / stale Recovery scope retirement 축에만 적용된다. Broad consumer completion, terminal disposition completion, cutover subset completion, current authority cutover, live migration execution, package/release readiness를 뜻하지 않는다.

이 계획은 첨부 로드맵의 미확정 항목을 다음처럼 고정한다.

* Validation depth: `heavy no-write authority/governance validation`
* Phase granularity: `Phase 0` through `Phase 6`
* Independent review / author seal: canonical retirement seal에는 non-author / independent review와 owner seal을 요구한다.
* Required-validation integration: evidence bundle 안에 통합하되, live required-validation manifest mutation은 별도 승인 없이는 실행하지 않는다.
* Compatibility impact: runtime/public contract mutation은 없으며, stale consumer가 fail-loud로 드러나는 것은 compatibility mutation이 아니라 guard exposure로 분류한다.

---

## 2. Scope

이 계획은 이미 current로 선언된 vNext successor `2105` source chain이 current-route에서 일관되게 소비되는지 검증하고, stale Recovery 범위를 live-write execution authority에서 제거하는 governance / verification plan이다.

포함 범위:

* current source chain hash/count baseline capture
* stale premise capture for `CURRENT_FACTS=6` / `6 != 2105`
* Recovery-labeled plan / downstream authority surface scan
* manifest-declared identity versus live file hash/count verification
* `facts / decisions / overlay_support` successor `2105` identity verification
* `overlay_support`의 compose-support role 보존 확인
* current-route validator / compose runner / direct compose entrypoint / rendered input contract source path inventory
* direct current compose read-only 또는 sandboxed-output verification
* known `Base.CanOpener` missing overlay regression check
* rendered input identity alignment check
* current-looking 6-entry fixture payload scan
* predecessor `2105 / 2084 / 21` current hard gate / runtime authority / package authority / current debt reentry scan
* Recovery scope retirement report
* future drift contingency open conditions
* final claim boundary report
* protected surface manifest and pre/post hash no-mutation proof
* protected source / rendered / Lua bridge / runtime / package no-mutation verdict
* direct compose writer sink preflight with sandbox output root
* sealed predecessor fixture artifact discovery
* content-derived 6-entry signature generation and determinism check
* `Base.CanOpener` target-aware applicability classification
* execution harness preimplementation when current-source-authority drift runner / validator is missing
* existing evidence reuse map for prior repair and closeout reports
* validator/tool existence inventory separating existing tools from newly required tools
* supporting docs/readpoint existence inventory
* canonical roadmap artifact rebind report before seal
* primary review artifact manifest fixed before independent review
* evidence bundle and review bundle for canonical retirement seal

Primary execution evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement/`

Direct documentation artifacts:

* `docs/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement_plan.md`
* `docs/dvf_3_3_current_source_authority_drift_verification_claim_boundary.md`
* `docs/dvf_3_3_current_source_authority_drift_verification_ledger_packet.md`

Supporting predecessor/current readpoints:

* `docs/dvf_3_3_current_route_baseline_source_overlay_repair_problem7_plan.md`
* `docs/dvf_3_3_current_route_baseline_source_overlay_repair_plan.md`
* `docs/dvf_3_3_closeout_reentry_guard_seal_plan.md`
* `docs/dvf_3_3_closeout_reentry_claim_boundary.md`
* `docs/dvf_3_3_shared_disposition_consumption_policy.md`
* `docs/predecessor_reentry_guard_policy.md`

### Explicitly Out Of Scope

* source files 복구
* `facts / decisions / overlay_support` live rewrite
* rendered output rewrite
* Lua bridge export mutation
* runtime chunk regeneration or replacement
* package payload mutation
* monolith runtime 복귀
* old chunks / predecessor runtime fallback 복귀
* 6-entry fixture current source 재승격
* predecessor `2105 / 2084 / 21` baseline 복구
* Terminal Disposition 재판정
* Denominator 재정의
* Shared Disposition Ledger 재채택
* Closeout / Reentry Guard Seal 재봉인
* current authority cutover
* Phase 4 live migration execution
* live migration completion 선언
* release / package / Workshop / B42 readiness 선언
* manual in-game QA
* semantic quality / public-facing text quality acceptance
* Layer4 / Structural Signal / Acquisition Lexical 재개방
* broad architecture redesign
* unrelated refactor
* using a hard-coded item ID list as authoritative 6-entry fixture signature
* live required-validation manifest adoption without separate authorization

---

## 3. Non-Goals

이 계획은 다음을 해결하지 않는다.

* old predecessor baseline을 current authority로 복원하지 않는다.
* `2105`를 predecessor recovery target으로 재해석하지 않는다.
* `CURRENT_FACTS=6`을 current universe expectation으로 되살리지 않는다.
* direct compose 검증을 rendered live output write로 전환하지 않는다.
* rendered-only artifact를 source authority로 승격하지 않는다.
* `overlay_support`를 source authority로 승격하지 않는다.
* raw audit / readiness / dry-run / predecessor / fixture artifact를 current execution authority로 직접 소비하지 않는다.
* required-validation result를 writer authority로 읽지 않는다.
* verification PASS를 source restoration, cutover, live migration execution, release readiness로 과대 선언하지 않는다.
* stale Recovery 계획을 삭제하지 않는다. Provenance를 보존한 채 execution authority를 contingency로 격하한다.
* drift 영구 불가능 선언을 하지 않는다. Future drift는 새 read-only evidence가 증명할 때만 별도 scope로 연다.
* hard-coded fixture ID sample을 authoritative scan signature로 사용하지 않는다.
* `Base.CanOpener`가 selected successor compose target 밖에 있을 때 이를 PASS-by-exception으로 세지 않는다. 이 경우 `not_applicable`로 분류한다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 설계 authority다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 current readpoint를 따른다.
* Iris는 runtime에서 source validation, semantic quality judgment, publish policy judgment, compose regeneration을 수행하지 않는다.
* DVF 3-3 current authority chain은 `source -> facts -> decisions -> rendered -> Lua bridge -> runtime chunks`로 읽는다.
* Current source chain은 `Iris/build/description/v2/data/dvf_3_3_input_manifest.json -> dvf_3_3_facts.jsonl -> dvf_3_3_decisions.jsonl -> dvf_3_3_overlay_support.jsonl`로 읽는다.
* `dvf_3_3_overlay_support.jsonl`은 compose support artifact이며 source authority가 아니다.
* vNext successor source manifest의 `successor_current_source_authority`와 successor row universe count `2105`가 현재 source identity 검증의 기준이다.
* Predecessor `2105 / 2084 / 21`은 historical / comparison / diagnostic / migration provenance context에서만 허용된다.
* Predecessor `2105 / 2084 / 21`이 current hard gate, runtime authority, package authority, release readiness, current debt, old chunks fallback, monolith fallback으로 쓰이면 fail-loud 처리한다.
* `CURRENT_FACTS=6`과 6-entry fixture payload는 current universe expectation이 아니라 predecessor / fixture / diagnostic trace로만 허용된다.
* Current-Route Baseline / Source-Overlay Repair는 Problem 7 repair round로 닫힌 상태이며, 이 계획은 이를 재개방하지 않는다.
* Closeout / Reentry Guard Seal은 required-validation gate로 채택된 상태이며, 이 계획은 이를 재봉인하지 않는다.
* Closeout / Reentry Guard Seal의 current readpoint는 `canonical_complete`로 읽으며, 이 계획은 그 상태를 과소 기술하거나 새로 봉인하지 않는다.
* Direct current compose 검증은 read-only 또는 sandboxed output mode에서만 실행한다.
* Direct compose 검증 전 live rendered sink가 차단되고 sandbox output root가 고정됐음을 preflight report로 증명한다.
* Direct compose preflight and path comparisons must normalize Windows `\` and POSIX `/` separators before comparing paths.
* Protected surfaces는 실행 전 baseline hash를 기록하고 실행 후 unchanged를 증명한다.
* Protected surfaces는 Phase 0에서 path/glob universe, hash algorithm, normalization rule, unchanged policy가 기계적으로 고정돼야 한다.
* 6-entry predecessor fixture membership은 실행 시점에 sealed predecessor fixture artifact에서 content-derived로 도출한다.
* Hard-coded item ID sample은 authoritative source가 아니라 fixture-derived signature의 non-authoritative cross-check로만 허용된다.
* `Base.CanOpener`는 selected successor compose target에 있을 때만 known blocker check 대상이다. 대상에 있으면 missing overlay blocker count는 반드시 `0`이어야 하며, 대상 밖이면 `not_applicable`이다.
* Primary review artifact universe는 independent review 전에 `phase6/primary_review_artifact_manifest.json`으로 고정한다.
* Roadmap attachment provenance는 canonical seal 전 stable docs/evidence artifact path와 hash로 rebind한다.
* Roadmap provenance rebind must preserve both the transient attachment path/hash/line count and the stable canonical artifact path/hash/line count.
* Execution tools and validators are not assumed to exist. Phase 0 records existing tools, missing tools, and newly required tools separately, with status taxonomy that distinguishes validation-blocking absence from implementation-prerequisite absence.
* Execution harness preimplementation may create repo-level code files, but `read-only verification` means no mutation of protected source / rendered / Lua bridge / runtime / package surfaces.
* Supporting docs/readpoint paths are not assumed to exist. Phase 0 records present, missing_optional, missing_blocks_validation, and not_applicable docs/readpoint references separately.
* Independent review는 canonical retirement seal의 조건이며, owner adoption 또는 self-review로 대체하지 않는다.
* 이 계획 문서 작성 자체는 docs-only mutation이며, 향후 실행 계획의 protected source / rendered / Lua bridge / runtime / package no-mutation 원칙과 별개다.

---

## 5. Repository Areas Affected

### Code

Read-only inspection / possible future no-write helper 대상:

* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tools/build/compose_layer3_item.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_current_route_baseline_source_overlay_repair.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_closeout_reentry_guard_seal_common.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_closeout_reentry_guard_seal.py`
* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_current_authority_cutover.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_source_manifest.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_facts_decisions.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_predecessor_reentry_guard.py`

Allowed execution harness preimplementation before validation:

* `Iris/build/description/v2/tools/build/run_dvf_3_3_current_source_authority_drift_verification.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_current_source_authority_drift_verification.py`
* focused tests under `Iris/build/description/v2/tests/`

These helpers are expected if Phase 0 classifies the planned runner / validator as `missing_requires_preimplementation`. They must be evidence-bundle writers only, may write only under `Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement/`, and must reuse existing current-route repair / closeout guard helpers where possible instead of creating a second authority model.

No live source / rendered / Lua bridge / runtime / package writer is allowed by this plan or by the helper preimplementation.

### Docs

Direct docs mutation in this planning task:

* `docs/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement_plan.md`

Expected docs from future execution:

* `docs/dvf_3_3_current_source_authority_drift_verification_claim_boundary.md`
* `docs/dvf_3_3_current_source_authority_drift_verification_ledger_packet.md`
* documentation-only additive DECISIONS / ROADMAP packets if Recovery retirement is adopted

Read-only authority inputs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/dvf_3_3_current_route_baseline_source_overlay_repair_problem7_plan.md`
* `docs/dvf_3_3_closeout_reentry_guard_seal_plan.md`

### Config

Read-only by default:

* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/_docs/round3/round3_active_core_closure.json`
* `Iris/_docs/round3/round3_contract_manifest.json`

Possible candidate-only generated config, not live-adopted without separate approval:

* `Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement/phase5/current_route_required_validation_candidate.json`

### Generated Artifacts

All generated evidence goes under:

* `Iris/build/description/v2/staging/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement/`

Expected artifact groups:

* `phase0/baseline_fingerprint.json`
* `phase0/protected_surface_manifest.json`
* `phase0/stale_premise_capture_report.json`
* `phase0/recovery_plan_authority_scan_report.json`
* `phase0/no_mutation_baseline_hashes.json`
* `phase0/tooling_existence_inventory.json`
* `phase0/supporting_readpoint_existence_inventory.json`
* `phase0/execution_harness_preimplementation_report.json`
* `phase0/existing_evidence_reuse_map.json`
* `phase0/roadmap_provenance_rebind_report.json`
* `phase1/source_chain_identity_report.json`
* `phase1/source_hash_count_matrix.json`
* `phase1/manifest_live_hash_comparison.json`
* `phase1/source_identity_no_mutation_verdict.json`
* `phase2/consumer_path_identity_report.json`
* `phase2/source_path_classification_report.json`
* `phase2/no_raw_predecessor_execution_read_report.json`
* `phase2/direct_compose_writer_sink_preflight_report.json`
* `phase2/direct_current_compose_result.json`
* `phase2/known_overlay_blocker_regression_report.json`
* `phase2/base_canopener_applicability_report.json`
* `phase2/body_source_overlay_requirement_report.json`
* `phase2/protected_rendered_no_mutation_verdict.json`
* `phase3/rendered_input_contract_inventory.json`
* `phase3/successor_identity_continuity_report.json`
* `phase3/rendered_provenance_alignment_report.json`
* `phase3/rendered_no_mutation_verdict.json`
* `phase4/sealed_predecessor_fixture_source_manifest.json`
* `phase4/content_derived_six_entry_signature.json`
* `phase4/six_entry_signature_determinism_report.json`
* `phase4/six_entry_signature_cross_check_report.json`
* `phase4/six_entry_non_reentry_report.json`
* `phase4/current_looking_fixture_payload_scan.json`
* `phase4/predecessor_reentry_guard_report.json`
* `phase4/allowed_historical_trace_inventory.jsonl`
* `phase4/forbidden_predecessor_authority_claim_report.json`
* `phase4/predecessor_guard_no_mutation_verdict.json`
* `phase5/recovery_scope_retirement_report.json`
* `phase5/future_drift_contingency_open_conditions.json`
* `phase5/downstream_plan_authority_scan_report.json`
* `phase5/required_validation_integration_report.json`
* `phase6/final_current_source_authority_drift_verification_report.json`
* `phase6/final_claim_boundary_report.md`
* `phase6/final_no_mutation_report.json`
* `phase6/primary_review_artifact_manifest.json`
* `phase6/independent_review_artifact_hash_report.json`

---

## 6. Planned Changes

### Change 1 - Phase 0 Baseline / Stale Premise Capture

Purpose:

Capture the current checkout baseline and prove this round is read-only verification / retirement, not source restoration.

Files:

* Read: current source chain under `Iris/build/description/v2/data/`
* Read: recovery-labeled docs and downstream authority surfaces under `docs/`
* Write: `phase0/*` evidence under the staging root

Implementation Notes:

* Write `protected_surface_manifest.json` before any hash or verification step. It must list source / rendered / Lua bridge / runtime / package protected paths and globs, hash algorithm, newline / JSONL normalization rule, and expected unchanged policy.
* Hash protected source / rendered / Lua bridge / runtime / package surfaces from the manifest before any verification.
* Record manifest path, file sizes, row counts, and sha256 values for facts / decisions / overlay support.
* Capture `6 != 2105` and `CURRENT_FACTS=6` as stale premise candidates unless current live data proves otherwise.
* Scan docs and tooling for Recovery wording that still reads like live-write execution authority.
* Record existing, missing, and newly required runners / validators in `tooling_existence_inventory.json`.
* `tooling_existence_inventory.json` must use explicit statuses: `existing_ok`, `missing_blocks_validation`, `missing_requires_preimplementation`, `new_tool_required`, `optional_missing`, `not_applicable`, and `invalid_reference`.
* Missing planned runners / validators do not automatically mean plan failure. They are `missing_requires_preimplementation` when this plan needs a new helper implementation before execution, and `missing_blocks_validation` only when execution claims depend on a tool that should already exist or must be present before validation can proceed.
* If `run_dvf_3_3_current_source_authority_drift_verification.py` or `validate_dvf_3_3_current_source_authority_drift_verification.py` is missing, implement the minimal evidence-bundle runner / validator before Phase 1 and record this in `execution_harness_preimplementation_report.json`.
* `execution_harness_preimplementation_report.json` must record created helper paths, whether each helper is new or reused, allowed write roots, forbidden write roots, and an assertion that no live source / rendered / Lua bridge / runtime / package writer was introduced.
* Write `existing_evidence_reuse_map.json` to bind prior evidence inputs to this round. It should reference the existing current-route repair final report, body source overlay coverage report, `Base.CanOpener` classification report, closeout/reentry final report, full current-route validation result, independent review hash report, and final no-mutation report when present.
* `existing_evidence_reuse_map.json` must include machine-readable fields for each prior artifact: `path`, `sha256`, `role_in_this_round`, `reused_as_input_only=true`, and `does_not_satisfy_final_claim_by_itself=true`.
* Record supporting docs/readpoint references in `supporting_readpoint_existence_inventory.json`, including the docs listed in Supporting predecessor/current readpoints. Missing docs must be classified as `missing_blocks_validation`, `missing_optional`, or `not_applicable`.
* `supporting_readpoint_existence_inventory.json` must include summary counts for `present`, `missing_optional`, `missing_blocks_validation`, and `not_applicable`. Final report must carry these counts forward.
* Rebind the transient roadmap attachment into a stable docs/evidence artifact path and record canonical path/hash in `roadmap_provenance_rebind_report.json`.
* `roadmap_provenance_rebind_report.json` must preserve both provenance records: transient attachment path / sha256 / line count and stable canonical artifact path / sha256 / line count. Final seal reads the stable canonical artifact as authority while retaining the transient attachment as consumed-input provenance.
* Do not repair mismatches in this phase.

Validation:

* `baseline_fingerprint.json` exists.
* `protected_surface_manifest.json` exists and has non-empty protected path sets for each protected surface class.
* `stale_premise_capture_report.json` exists.
* `recovery_plan_authority_scan_report.json` classifies every found Recovery surface.
* `no_mutation_baseline_hashes.json` covers every path resolved from `protected_surface_manifest.json`.
* `tooling_existence_inventory.json` separates existing tools, validation-blocking missing tools, and preimplementation-required new tools.
* `execution_harness_preimplementation_report.json` exists when any planned runner / validator was initially missing, and reports only evidence-bundle writer capability.
* `existing_evidence_reuse_map.json` maps prior current-route repair and closeout evidence into this round with `reused_as_input_only=true` and `does_not_satisfy_final_claim_by_itself=true`.
* `supporting_readpoint_existence_inventory.json` covers supporting docs/readpoint paths, reports summary counts, and fails loud on missing required docs.
* `roadmap_provenance_rebind_report.json` records transient attachment provenance and stable canonical roadmap artifact path/hash before final seal.

---

### Change 2 - Phase 1 Successor Source Chain Identity Verification

Purpose:

Verify that manifest / facts / decisions / overlay_support match the vNext successor `2105` identity and preserve the `overlay_support` role boundary.

Files:

* Read: `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
* Read: `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
* Read: `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
* Read: `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`
* Write: `phase1/*` evidence under the staging root

Implementation Notes:

* Compare manifest-declared hash/count to live hash/count.
* Verify facts row count, decisions row count, and overlay support manifest-declared count/hash.
* Record `2105` as successor universe count, not predecessor recovery target.
* If any mismatch is found, record drift evidence and stop before Recovery retirement.
* Do not rewrite source files.

Validation:

* Manifest identity is `successor_current_source_authority` or equivalent current successor declaration.
* facts hash/count match manifest.
* decisions hash/count match manifest.
* overlay_support hash/count match manifest-declared compose support expectation. Literal `2105` is not assumed unless the manifest declares it for this artifact.
* `source_identity_no_mutation_verdict.json` reports protected mutation count `0`.

---

### Change 3 - Phase 2 Consumer Path / Direct Compose / Overlay Regression Verification

Purpose:

Confirm current-route consumers resolve to successor current source paths and direct current compose no longer depends on stale 6-entry predecessor fixtures or missing overlay blockers.

Files:

* Read: compose runner / validator / direct compose entrypoints under `Iris/build/description/v2/tools/build/`
* Read: `Iris/_docs/round3/current_route_required_validations.json`
* Write: `phase2/*` evidence under the staging root

Implementation Notes:

* Inventory execution readers separately from diagnostic-only readers.
* Classify raw audit / readiness / dry-run / predecessor / fixture reads as forbidden if they feed current execution authority directly.
* Run `direct_compose_writer_sink_preflight_report.json` before direct compose. It must fix sandbox output root to `Iris/build/description/v2/.tmp_tests/dvf_3_3_current_source_authority_drift_verification/direct_compose/`, prove live rendered output paths are blocked, normalize Windows and POSIX path separators before path comparison, and record the protected rendered baseline hash.
* Direct compose should use current source inputs from `Iris/build/description/v2/data/` with `compose_context=current`, and write only sandbox current-equivalent fixture outputs such as `dvf_3_3_rendered.json`, `style_normalization_changes.jsonl`, and `compose_requeue_candidates.jsonl` under the fixed `.tmp_tests` root.
* The preflight must inspect `compose_layer3_text.py` write-path classification expectations: `.tmp_tests` current-equivalent outputs are fixture outputs, while `Iris/build/description/v2/output/` remains live current output and must not be targeted.
* Run direct current compose only after writer sink preflight passes, and only in read-only or fixed sandbox output mode.
* Verify runtime-adopted compose rows satisfy `body_source_overlay`.
* Focus `Base.CanOpener` as known blocker regression, but do not let it replace full peer missing-overlay inventory.
* Classify `Base.CanOpener` applicability before asserting PASS. If it is in the selected successor compose target, missing overlay blocker count must be `0`; if it is absent, the result is `not_applicable`, not PASS-by-exception.
* Confirm `Base.CanOpener` is not patched into successor overlay support unless selected successor source membership is proven by evidence and the normal overlay requirement is satisfied.

Validation:

* `consumer_path_identity_report.json` shows current-route execution consumers consume successor current source identity.
* `no_raw_predecessor_execution_read_report.json` reports forbidden direct execution read count `0`.
* `direct_compose_writer_sink_preflight_report.json` reports fixed sandbox output root, expected sandbox output files, path separator normalization mode, live rendered output path blocked, compose context `current`, current input paths under `data/`, and preflight PASS.
* `direct_current_compose_result.json` reports PASS for direct current compose in read-only / sandboxed mode.
* `base_canopener_applicability_report.json` reports `checked_and_zero_missing_overlay` or `not_applicable_absent_from_selected_target`.
* `known_overlay_blocker_regression_report.json` reports known missing overlay blockers `0` for every applicable known blocker.
* `body_source_overlay_requirement_report.json` reports runtime-adopted missing overlay count `0`.
* `protected_rendered_no_mutation_verdict.json` reports rendered protected mutation count `0`.

---

### Change 4 - Phase 3 Rendered Input Contract / Successor Identity Alignment

Purpose:

Confirm rendered input contract consumes the same successor source identity as direct compose and current-route validation.

Files:

* Read: rendered generation input contract surfaces
* Read: `Iris/build/description/v2/output/dvf_3_3_rendered.json`
* Read: relevant bridge reports / provenance reports if present
* Write: `phase3/*` evidence under the staging root

Implementation Notes:

* Inventory rendered generation inputs and provenance references.
* Compare rendered provenance to source manifest / facts / decisions / overlay identity.
* Keep rendered output as static output, not source authority.
* Do not regenerate live rendered output.

Validation:

* `rendered_input_contract_inventory.json` exists.
* `successor_identity_continuity_report.json` shows source manifest -> facts/decisions/overlay -> compose -> rendered input continuity.
* `rendered_provenance_alignment_report.json` aligns with direct compose input identity.
* `rendered_no_mutation_verdict.json` reports protected rendered hash unchanged.

---

### Change 5 - Phase 4 6-Entry Fixture / Predecessor Reentry Guard Verification

Purpose:

Prove current-looking paths do not contain 6-entry fixture payloads and predecessor `2105 / 2084 / 21` cannot reenter as current hard gate, runtime authority, package authority, release readiness, or current debt.

Files:

* Read: current-looking source / rendered / Lua bridge / runtime / package paths
* Read: docs and tooling claims containing `2105`, `2084`, `21`, `CURRENT_FACTS=6`, and 6-entry signatures
* Write: `phase4/*` evidence under the staging root

Implementation Notes:

* Treat the number `2105` contextually. Successor universe count is allowed; predecessor recovery target is not.
* Preserve historical / diagnostic / fixture trace when it is non-execution.
* Discover sealed predecessor fixture artifacts and write `sealed_predecessor_fixture_source_manifest.json`.
* Define `fixture_threshold` before candidate selection. Default is `10`, matching `dvf_3_3_input_manifest.json.fixture_exclusion_rule.fixture_threshold` when present. If the manifest declares a different concrete threshold, use the manifest value and record `threshold_source=manifest`; otherwise record `threshold_source=plan_default_10`. The threshold value and source must be written to `sealed_predecessor_fixture_source_manifest.json`.
* Candidate discovery must be deterministic and provenance-first:
  * First, read manifest-declared fixture exclusions from `dvf_3_3_input_manifest.json.fixture_exclusion_rule.excluded_paths`.
  * Second, read prior repair evidence that classifies 6-row fixtures, especially `current_facts_6_disposition_lock.md`, `source_baseline_role_classification_report.json`, and `base_canopener_fixture_leak_report.json` when present.
  * Third, read vNext common fixture records such as `_dvf_3_3_vnext_common.py` `fixture_surfaces` only as candidate discovery hints, not as final membership authority.
  * Fourth, include stale bridge quarantine evidence only if it is explicitly classified as historical / fixture / non-authority.
* If multiple sealed predecessor fixture candidates exist, apply this deterministic selection rule before signature derivation: first prefer an existing candidate explicitly classified by prior repair evidence as `fixture_non_authority` / 6-row predecessor fixture with row count `<= fixture_threshold`; then prefer manifest-excluded candidates with row count `<= fixture_threshold` if the manifest exclusion points at a concrete fixture payload; then prefer stale bridge quarantine evidence only when explicitly historical / fixture / non-authority. If still tied, sort by normalized path and sha256 and select the first while recording all rejected candidates.
* The manifest must record all candidates, candidate role, row count when applicable, candidate sha256, selection rule, selected artifact path/hash, and rejected candidate reason.
* Derive the 6-entry membership from sealed predecessor fixture artifact content and write `content_derived_six_entry_signature.json`.
* Verify signature derivation determinism by repeating derivation from the same sealed inputs and writing `six_entry_signature_determinism_report.json`.
* Use hard-coded known IDs only as non-authoritative cross-check input in `six_entry_signature_cross_check_report.json`. Additional IDs beyond `Base.CanOpener` must not be asserted as facts unless they are present in the content-derived signature.
* Scan current-looking paths using the content-derived signature, not the cross-check sample.
* Classify allowed historical traces into `allowed_historical_trace_inventory.jsonl`.
* Fail if any allowed trace carries execution authority.

Validation:

* `sealed_predecessor_fixture_source_manifest.json` identifies candidate sealed fixture inputs, `fixture_threshold`, `threshold_source`, selection rule, rejected candidate reasons, and the selected fixture artifact hash used for signature derivation.
* `content_derived_six_entry_signature.json` records fixture-derived membership and provenance.
* `six_entry_signature_determinism_report.json` reports deterministic signature derivation PASS.
* `six_entry_signature_cross_check_report.json` treats hard-coded sample IDs as non-authoritative cross-check only.
* `current_looking_fixture_payload_scan.json` reports content-derived 6-entry current-looking payload count `0`.
* `predecessor_reentry_guard_report.json` reports current hard gate reentry count `0`.
* `forbidden_predecessor_authority_claim_report.json` reports runtime / package / current debt / release readiness reentry count `0`.
* `predecessor_guard_no_mutation_verdict.json` reports protected mutation count `0`.

---

### Change 6 - Phase 5 Recovery Scope Retirement / Required-Validation Integration

Purpose:

Retire stale Recovery live-write scope from current execution authority and define future drift contingency conditions.

Files:

* Read: Recovery-labeled plans, existing Problem 7 plan, Closeout / Reentry Guard docs
* Read: `Iris/_docs/round3/current_route_required_validations.json`
* Write: `phase5/*` evidence under the staging root
* Possible docs write after PASS: claim boundary and ledger packet under `docs/`
* Candidate-only config write: `phase5/current_route_required_validation_candidate.json`

Implementation Notes:

* Mark stale Recovery scope as `future_drift_contingency` or equivalent non-execution status.
* Preserve provenance; do not delete predecessor recovery material.
* Define reopen conditions: new read-only evidence of manifest/live mismatch, consumer path drift, rendered input identity drift, overlay regression, or predecessor reentry.
* Required-validation integration is evidence-bundle-first. Live manifest adoption is not automatic in this plan.
* If current-route required-validation adoption is later approved, classify it as governance gate only, not writer authority.

Validation:

* `recovery_scope_retirement_report.json` proves no Recovery plan remains live-write execution authority.
* `future_drift_contingency_open_conditions.json` lists explicit reopen conditions.
* `downstream_plan_authority_scan_report.json` shows no downstream live-write instruction remains.
* `required_validation_integration_report.json` classifies live manifest impact as none or candidate-only unless separately approved.

---

### Change 7 - Phase 6 Final Evidence / Claim Boundary / Review Seal

Purpose:

Close the round with a bounded claim, no-mutation proof, and independent review-ready artifact bundle.

Files:

* Write: `phase6/final_current_source_authority_drift_verification_report.json`
* Write: `phase6/final_claim_boundary_report.md`
* Write: `phase6/final_no_mutation_report.json`
* Write: `phase6/independent_review_artifact_hash_report.json`
* Write: `docs/dvf_3_3_current_source_authority_drift_verification_claim_boundary.md`
* Write: `docs/dvf_3_3_current_source_authority_drift_verification_ledger_packet.md`

Implementation Notes:

* Aggregate phases 0-5 into one final machine report.
* Write `primary_review_artifact_manifest.json` after required phase artifacts are generated and before independent review starts. It must include `generated_before_review=true`, `generated_after_artifact_generation=true`, `review_not_started_at_generation=true`, and a manifest generation timestamp or equivalent stable run id.
* `primary_review_artifact_manifest.json` must list phase0 through phase6 required reports, no-mutation reports, source hash/count matrix, consumer path identity report, direct compose result, overlay blocker report, rendered input alignment report, fixture/reentry scan reports, recovery retirement report, final claim boundary report, validation report, reviewer identity / review mode metadata fields, expected sha256 for each artifact after generation, and a missing artifact hard-fail rule.
* Freeze `primary_review_artifact_manifest.json` before review by hashing the manifest itself. Independent review must record both `primary_review_artifact_manifest_sha256` and each listed artifact sha256.
* After review starts, the manifest and listed artifacts are immutable for that review attempt. Any artifact regeneration requires a new manifest version, new manifest hash, and new review attempt id.
* Hash-seal primary artifacts by reading `primary_review_artifact_manifest.json`, not by constructing the review universe ad hoc.
* Claim boundary must explicitly forbid source restoration, old predecessor recovery, current authority cutover, live migration completion, release readiness, manual QA, semantic quality completion, and public-facing text acceptance.
* Canonical retirement seal requires independent review PASS and owner seal.

Validation:

* Final report status is PASS only if phases 0-5 PASS.
* Final no-mutation report shows source / rendered / Lua bridge / runtime / package protected mutation count `0`.
* Claim boundary exists and contains the expected non-claims.
* `primary_review_artifact_manifest.json` exists before independent review, has `generated_before_review=true`, has missing artifact hard-fail enabled, and records its own frozen manifest hash or stable run id.
* Independent review artifact hash report is generated from `primary_review_artifact_manifest.json` and has missing count `0`.

---

## 7. Validation Plan

### Automated Validation

Planned execution validation commands:

* `uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_current_source_authority_drift_verification.py --mode all`
* `uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_current_source_authority_drift_verification.py --require-complete`
* `uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure`
* `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_current_source_authority_drift_verification*.py"`
* Existing focused tests for current-route baseline/source-overlay repair and closeout/reentry guard, if this round consumes their reports directly.

These commands are planned execution surfaces. Phase 0 must classify each as existing, missing, or newly required before execution; a missing tool blocks validation until created under an approved implementation scope.

If the current-source-authority drift runner or validator is missing, implement the minimal evidence-bundle helper first and rerun Phase 0 inventory before claiming any validation result. Do not skip directly to existing predecessor reports.

Required machine checks:

* determinism check for generated verification reports
* protected surface manifest coverage check
* source manifest hash/count consistency
* current source authority identity
* current-route consumer path identity
* direct compose writer sink preflight with sandbox output root
* direct current compose PASS in read-only / sandboxed output mode
* source-overlay regression check
* `Base.CanOpener` target-aware applicability check
* rendered input contract alignment
* content-derived 6-entry fixture signature derivation check
* 6-entry fixture signature determinism check
* 6-entry fixture non-reentry check using the content-derived signature
* predecessor reentry guard
* no source / rendered / Lua bridge / runtime / package mutation proof
* primary review artifact manifest coverage check
* final claim boundary scan

### Manual Validation

* Review `source_path_classification_report.json` for execution-reader versus diagnostic-reader false positives.
* Review `direct_compose_writer_sink_preflight_report.json` before accepting any direct compose PASS.
* Confirm direct compose sandbox output root is exactly under `Iris/build/description/v2/.tmp_tests/dvf_3_3_current_source_authority_drift_verification/direct_compose/` or a recorded equivalent under `BUILD_TMP_ROOT`, and that live `output/` paths are not write targets.
* Review `content_derived_six_entry_signature.json` and `six_entry_signature_cross_check_report.json` to confirm no hard-coded sample is treated as authority.
* Review `sealed_predecessor_fixture_source_manifest.json` to confirm candidate selection rule, rejected candidate reasons, and selected artifact hash are reproducible.
* Review `allowed_historical_trace_inventory.jsonl` for historical trace versus current authority misclassification.
* Review Recovery retirement wording to ensure it is demotion, not deletion.
* Review final claim boundary for overclaim language.
* Independent reviewer confirms `primary_review_artifact_manifest.json`, artifact hashes, phase report consistency, reviewer identity / mode metadata, and missing artifact hard-fail behavior before owner seal.

### Validation Limits

This execution does not perform:

* multiplayer validation
* long-session runtime validation
* manual in-game validation
* release / package / Workshop validation
* B42 validation
* deployment validation
* external ecosystem compatibility sweep
* semantic quality acceptance
* public-facing text quality acceptance
* live migration execution validation
* source restoration validation
* old predecessor baseline recovery validation
* full runtime equivalence validation beyond the explicitly listed authority path checks

---

## 8. Risk Surface Touch

### Authority Surface

Limited governance impact.

Current source / rendered / Lua bridge / runtime / package authority is not changed. The only authority change is the demotion of stale Recovery live-write execution authority into future drift contingency, after read-only evidence proves that live repair is not currently justified.

### Runtime Behavior Surface

None.

Runtime Lua, Browser, Wiki, Tooltip, rendered display, package payload, and chunk files are not changed.

### Compatibility Surface

No runtime/public contract mutation.

If stale consumers are exposed by fail-loud validation, that is treated as guard evidence, not compatibility contract change.

### Sealed Artifact Surface

Additive only.

Expected additions are verification reports, no-mutation reports, claim boundary docs, ledger packets, primary review artifact manifest, and review hash reports. Existing sealed source / rendered / runtime artifacts are not rewritten.

### Public-Facing Output Surface

None.

User-facing Korean text, UI exposure, tooltip text, Browser presentation, semantic quality state, publish state, and release messaging are unchanged.

---

## 9. Risk Analysis

### Architecture Risk

* Recovery retirement can be mistaken for source restoration completion.
* Successor `2105` universe count can be confused with predecessor `2105 / 2084 / 21` recovery baseline.
* Required-validation governance gate can be mistaken for writer authority.
* `overlay_support` can be accidentally promoted from compose support to source authority.
* Historical / diagnostic traces can be over-pruned instead of preserved as non-execution provenance.
* Recovery retirement can be wrongly justified if fixture signature provenance is weak. This plan blocks retirement unless content-derived signature derivation passes.

### Runtime Risk

* Direct compose verification could accidentally write live rendered output if sandboxed output guard is wrong.
* A validation helper could import writer code paths without disabling writes.
* A stale 6-entry current-looking runtime payload could be missed if scan signatures are too narrow. This is mitigated by deriving the signature from sealed predecessor fixture content.

### Compatibility Risk

* Stale consumer paths can fail-loud after the guard is tightened.
* Diagnostic-only readers can be misclassified as execution readers.
* Context-free numeric scans can false-positive on allowed successor `2105` usage.

### Regression Risk

* Current-route validation can pass while rendered input provenance remains stale if identity continuity is not checked end to end.
* Known `Base.CanOpener` blocker can be fixed while peer missing-overlay rows remain uncovered.
* Final docs can retain stale live-write wording even if machine reports are correct.
* Independent review can hash the wrong bundle if primary review artifact manifest is incomplete or generated too late.

---

## 10. Rollback Plan

This plan is designed as read-only for protected source / rendered / Lua bridge / runtime / package surfaces, so data-level rollback should not be needed.

If execution produces incorrect evidence:

* Delete or supersede only the generated staging evidence for this round.
* Revert candidate-only required-validation artifacts if they were generated.
* Correct claim boundary or ledger packet with an additive correction, preserving provenance.
* Do not rewrite source / rendered / Lua bridge / runtime / package files to hide a failed validation.
* If any protected surface changed unexpectedly, restore from the phase0 baseline hash source and treat the round as failed.
* If content-derived fixture signature derivation is missing, nondeterministic, or falls back to hard-coded samples, stop before Recovery retirement.
* If direct compose writer sink preflight fails, do not run direct compose.
* If primary review artifact manifest is missing or generated after review, do not claim canonical retirement seal.
* If hash/count mismatch, overlay regression, consumer path drift, or predecessor reentry is found, stop Recovery retirement and open a separate authorized repair / correction scope.

For this planning document itself, rollback is removal or replacement of:

* `docs/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement_plan.md`

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Hub & Spoke / SPI boundaries remain unchanged.
* Iris remains a 100% Lua runtime display module with offline DVF production; runtime does not generate or validate source.
* Runtime / build-time separation must remain intact.
* Source / rendered / Lua bridge / runtime / package mutation is forbidden in this verification scope.
* `facts / decisions / overlay_support / rendered` live write is forbidden.
* Predecessor `2105 / 2084 / 21` cannot reenter as current hard gate, runtime authority, package authority, current debt, release readiness, old chunks fallback, or monolith fallback.
* `CURRENT_FACTS=6` cannot return as current universe expectation.
* Raw audit / readiness / dry-run / predecessor / fixture artifact cannot be direct execution authority.
* Current-route validation is a governance gate, not writer authority.
* Required-validation adoption, if later approved, is governance-only and not a source / rendered / runtime writer.
* Direct compose must use a preflight-proven sandbox output root or no-write mode before any compose PASS can be claimed.
* 6-entry fixture scan must use a content-derived signature from sealed predecessor fixture artifacts. Hard-coded IDs are cross-checks only.
* Primary review artifact universe must be fixed before independent review.
* Release / package / Workshop / B42 / deployment readiness declarations are forbidden.
* Manual in-game QA, semantic quality completion, public-facing text acceptance claims are forbidden.
* Terminal Disposition, Denominator Lock, Shared Disposition Ledger Consumption, and Closeout / Reentry Guard Seal are not reopened by this plan.
* Existing sealed hash/count values are not changed by this round; live state is only compared to sealed identity.
* Independent review and owner seal are required for canonical Recovery retirement seal.

---

## 12. Expected Closeout State

Expected closeout target: `current_source_authority_drift_verification_recovery_scope_retirement_complete_after_review`

The execution may close as `current_source_authority_drift_verification_recovery_scope_retirement_complete_after_review` only when all of the following are true:

* current source manifest declares successor current source authority
* live facts / decisions match manifest-declared hash/count
* live overlay_support matches manifest-declared compose-support hash/count
* successor current source universe count is confirmed as `2105`
* `2105` is explicitly classified as successor universe count, not predecessor recovery target
* protected surface manifest exists and covers source / rendered / Lua bridge / runtime / package surfaces
* tooling existence inventory classifies every planned runner / validator as `existing_ok`, `missing_requires_preimplementation`, `new_tool_required`, `optional_missing`, `not_applicable`, `invalid_reference`, or `missing_blocks_validation`, with no unresolved validation-blocking absence
* if the current-source-authority drift runner / validator was missing at first inspection, execution harness preimplementation report records minimal evidence-bundle helpers and no live writer capability
* existing evidence reuse map carries `reused_as_input_only=true` and `does_not_satisfy_final_claim_by_itself=true` for prior evidence artifacts
* supporting readpoint existence inventory covers docs/readpoint references, reports summary counts, and has no unresolved missing required docs
* roadmap provenance rebind report preserves both transient attachment hash/line count and stable canonical artifact hash/line count
* current-route consumers read successor current source paths
* raw audit / readiness / dry-run / predecessor / fixture artifacts are not direct current execution authority
* direct compose writer sink preflight fixes sandbox output root under `.tmp_tests` / `BUILD_TMP_ROOT`, records expected sandbox output files, normalizes Windows/POSIX path separators, and blocks live rendered writes
* direct current compose passes without known missing overlay regression
* `Base.CanOpener` is checked only when present in the selected successor compose target; if present, missing overlay blocker count is `0`; if absent, it is `not_applicable`, not PASS-by-exception
* known blocker PASS does not replace the full peer missing-overlay inventory
* rendered input contract consumes the same successor source identity
* 6-entry fixture signature is content-derived from selected sealed predecessor fixture artifact content with deterministic candidate discovery, `fixture_threshold`, `threshold_source`, selection rule, rejected candidate reasons, selected artifact hash, and derivation determinism PASS
* current-looking path contains no content-derived 6-entry fixture payload
* predecessor fixture/source remains historical / diagnostic / fixture trace only
* predecessor `2105 / 2084 / 21` does not reenter as current hard gate / runtime authority / package authority / current debt
* prior Recovery live-write plan is retired to future drift contingency
* future drift contingency open conditions are explicit
* source / rendered / Lua bridge / runtime / package protected mutation count is `0`
* final claim boundary is limited to read-only verification / stale recovery scope retirement
* primary review artifact manifest exists after artifact generation and before independent review, has `generated_before_review=true`, has missing artifact hard-fail enabled, records its own frozen manifest hash or stable run id, and is not changed during the review attempt
* independent review PASS and owner seal are recorded

If any source identity mismatch, consumer path drift, missing overlay blocker, rendered identity drift, 6-entry fixture reentry, predecessor authority reentry, or protected mutation is found, expected closeout becomes `blocked_authorized_repair_or_correction_scope_required`.
