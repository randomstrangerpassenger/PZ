# Implementation Plan

> Status: planned / roadmap-derived / WARN feedback incorporated / DVF 3-3 current-route required-validation evidence freshness reseal / governance-only validation gate / no source-runtime-package mutation planned
> 작성일: 2026-06-25
> Roadmap input: `C:/Users/MW/.codex/attachments/923bdc23-8773-4560-925b-fdeb3b312cc7/pasted-text.txt` / sha256 `A41802CE12907F76EFFBE314146A80585F2AFC5C51D32FD74717BF061A2786DF` / lines `590`
> Feedback input: `C:/Users/MW/.codex/attachments/eefab083-3202-4251-9533-d6f460e72cf1/pasted-text.txt` / sha256 `0CD411DDCBA55901E2C4BC89254838C3D883FCADE49DEC96DC0E3479ED8DC858` / lines `407` / WARN revisions incorporated
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Direct plan artifact: `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_plan.md`
> Evidence root target: `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/`
> Execution readiness rule: Phase 0~1 inventory / blocker triage may proceed, but Phase 2+ manifest update, runner integration, external bundle reseal, and any PASS / canonical closeout claim are blocked until the feedback-required freshness, target-pinning, semantic-preservation, owner-gate, rollback, and independent-review constraints below are satisfied.

---

## 1. Objective

DVF 3-3 Current-Route Required Validation / Evidence Freshness Reseal 라운드를 실행하기 위한 계획을 작성한다.

이 계획의 목적은 기존 evidence에 남아 있는 `current route PASS`, `required validations PASS`, `external validation bundle PASS`, `107 tests / PASS / closure_enforced=true`가 현재 checkout의 runner, live manifest, stored evidence, external validation bundle과 같은 readpoint에서 나온 결과인지 fail-closed로 재증명하는 것이다.

이번 라운드의 본질은 source 복구, current authority cutover, rendered regeneration, Lua bridge export, runtime chunk replacement, package readiness가 아니라 다음 네 surface의 evidence freshness / readpoint identity 결속이다.

* current-route runner
* live `Iris/_docs/round3/current_route_required_validations.json`
* stored evidence
* external validation bundle

완료 후 허용되는 최대 claim은 기존 `required_validation_gate_adopted` axis 아래 sub-state로 제한한다. 단독 `complete` 또는 `current_route_required_validation_freshness_reseal_pass` 같은 신규 canonical claim-class vocabulary는 이 계획에서 확정하지 않는다.

Closeout is intentionally staged. The first execution target uses the non-canonical internal machine-verification state label `evidence_freshness_reseal_machine_pass`; owner confirms the exact closeout-state vocabulary at seal time. Canonical / axis-qualified complete closeout is a later seal state that additionally requires non-Claude independent review and owner seal. Machine pass evidence may exist without final seal and must not surface as a standalone canonical claim.

```text
required_validation_gate_adopted /
evidence_freshness_reseal_closeout_state=complete

Current-route required validation / evidence freshness reseal PASS under the
required-validation governance gate, with the current checkout runner, live
manifest, stored evidence, and external validation bundle bound to the same
evidence readpoint. This is governance-only validation evidence and does not
claim release, package, runtime, manual QA, semantic quality, or public-facing
text readiness.
```

이 claim은 latest drift-verification evidence root를 단순히 fresh anchor로 재사용해서 성립하지 않는다. Mainline은 현재 checkout source에 대해 drift report가 주장한 `facts / decisions / overlay` hash parity와 successor `2105` identity를 재도출하고, drift report 기록값과 현재 재도출값을 비교하는 것이다. 재도출이 불가능하면 drift evidence root는 provenance-only로 강등되며, fresh source-identity 보증은 current-route broad runner가 현재 checkout에서 별도로 재검증했다는 evidence로 대체해야 한다. 어느 쪽도 충족하지 못하면 reseal PASS는 fail-closed한다.

이 계획의 완료는 다음을 의미하지 않는다.

* release readiness
* package readiness
* Workshop readiness
* B42 readiness
* deployment readiness
* manual in-game QA
* semantic quality completion
* public-facing text acceptance
* live migration execution
* source / rendered / Lua bridge / runtime / package mutation

---

## 2. Scope

이 계획은 current-route required validation evidence가 현재 checkout의 live manifest와 최신 drift-verification evidence를 실제로 소비했는지 확인하고, stale PASS / stale bundle / candidate manifest를 current success 근거로 사용할 수 없게 만드는 governance / validation plan이다.

포함 범위:

* current branch / commit / dirty state inventory
* current-route command path와 runner script readpoint capture
* live `current_route_required_validations.json` hash capture
* stored evidence root inventory
* external validation bundle inventory
* external validation bundle canonical target / role / generator / content contract pinning
* latest Current Source Authority Drift Verification / Recovery Scope Retirement evidence root inventory
* current checkout source identity / hash parity re-derivation for drift evidence freshness
* stored evidence role taxonomy 작성
* candidate manifest와 live manifest role separation
* `OSError 22` 또는 유사 broad rerun blocker triage
* harness / evidence-write blocker가 재현될 경우 evidence-write 경계 안에서만 repair
* harness repair semantic-preservation negative fixture validation
* sealed-round evidence content hash protection
* drift-verification result를 live required-validation manifest가 소비할 수 있게 하는 field spec / freshness taxonomy 작성
* live `current_route_required_validations.json`의 additive required artifact / required test reseal
* live manifest rollback snapshot and single-writer assertion
* runner fail-closed integration
* fresh current-route execution
* external validation bundle reseal
* final claim boundary, no-mutation verdict, review artifact manifest, hash report 작성

Primary execution evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/`

Direct documentation artifact:

* `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_plan.md`

Expected execution docs:

* `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_claim_boundary.md`
* `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_ledger_packet.md`

Read-only authority / context inputs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/EXECUTION_CONTRACT.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement_plan.md`
* `docs/dvf_3_3_current_source_authority_drift_verification_claim_boundary.md`
* `docs/dvf_3_3_current_source_authority_drift_verification_ledger_packet.md`
* `docs/dvf_3_3_closeout_reentry_guard_seal_plan.md`
* `docs/dvf_3_3_closeout_reentry_claim_boundary.md`
* `docs/dvf_3_3_current_route_baseline_source_overlay_repair_problem7_plan.md`

### Explicitly Out Of Scope

* source restoration
* current authority cutover re-execution
* rendered live regeneration
* Lua bridge export
* runtime chunk replacement
* package route mutation
* Phase 4 live migration execution
* terminal disposition re-adjudication
* denominator redefinition
* shared disposition ledger re-adoption
* semantic quality judgment
* public-facing text acceptance
* manual in-game QA
* release / Workshop / B42 / deployment readiness declaration
* current-route test suite semantic expansion
* broad architecture redesign
* unrelated refactor
* legacy predecessor fixture restoration
* old chunks / monolith fallback reintroduction
* live-write recovery plan reopening
* 신규 claim-class vocabulary 확정

---

## 3. Non-Goals

이 계획은 다음을 해결하지 않는다.

* Current Source Authority Drift Verification / Recovery Scope Retirement를 source writer authority로 승격하지 않는다.
* Current Source Authority Drift Verification evidence root를 현재 checkout 재도출 없이 fresh anchor로 소비하지 않는다.
* stale `CURRENT_FACTS=6` premise를 current-route universe expectation으로 되살리지 않는다.
* predecessor `2105 / 2084 / 21`을 current hard gate, runtime authority, current debt, package authority, release readiness 근거로 재진입시키지 않는다.
* candidate required-validation manifest를 live manifest처럼 사용하지 않는다.
* stored PASS evidence를 fresh current-route PASS로 재사용하지 않는다.
* external validation bundle이 old run을 가리키는데도 current success로 인정하지 않는다.
* required artifact 존재만으로 field freshness를 대체하지 않는다.
* skipped required test를 전체 PASS 아래에 묻지 않는다.
* `PASS`, `complete`, `current`, `ready`를 evidence root와 owning axis 없이 독립 claim으로 쓰지 않는다.
* harness / evidence-write repair를 validation semantic 변경 수단으로 쓰지 않는다.
* source / rendered / Lua bridge / runtime / package protected surface의 mutation을 허용하지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 설계 authority다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 current readpoint를 따른다.
* Iris는 runtime에서 source validation, semantic quality judgment, publish policy judgment, compose regeneration을 수행하지 않는다.
* `Iris/_docs/round3/current_route_required_validations.json`은 current-route required-validation live manifest다.
* Required-validation manifest entry는 governance gate이며 source / rendered / Lua bridge / runtime / package writer가 아니다.
* Current Source Authority Drift Verification / Recovery Scope Retirement는 canonical PASS 상태로 읽되, read-only governance evidence로만 소비한다.
* Latest drift-verification evidence root는 filesystem mtime으로 선택하지 않는다. Phase 0은 `docs/DECISIONS.md` / `docs/ROADMAP.md`에 기록된 canonical evidence root, 또는 drift final report의 `closeout_state` / canonical PASS seal을 기준으로 선택하고 그 선택 근거를 기록한다.
* Current Source Authority Drift Verification evidence는 live required-validation manifest / taxonomy에 additive하게 소비될 수 있다.
* Drift verification evidence freshness는 mainline에서 current checkout source에 대해 source manifest identity, facts / decisions / overlay hash parity, and successor `2105` identity를 재도출해 증명한다.
* Drift verification evidence root를 provenance-only로 강등하는 fallback은 허용되지만, 그 경우 current-route broad runner가 current checkout source identity를 재검증했다는 별도 evidence 없이는 reseal PASS가 불가능하다.
* Provenance-only fallback is legitimate only when the drift artifact lacks machine-comparable recorded hash/count fields, records an obsolete hash algorithm or normalization rule that cannot be reproduced, or was already classified as historical/provenance-only before comparison. If current checkout re-derivation and recorded-value comparison are possible, mismatch must fail closed and cannot be reclassified as provenance-only.
* Existing drift recovery live-write scope는 current execution authority가 아니라 future drift contingency다.
* External validation bundle은 성공률을 높이기 위해 기존 미확정 artifact를 억지로 찾는 방식이 아니라, 이 reseal round가 생성하는 canonical bundle을 기본 target으로 둔다. Phase 0에서 기존 concrete target이 하나만 발견되면 `external_bundle_previous_readpoint`로 기록할 수 있지만, 기존 target 부재는 failure가 아니다. 복수 target, stale target, non-regenerable target은 existing-target adoption을 fail-closed하고 새 canonical reseal bundle route로 전환한다.
* Canonical external bundle target is `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase5/external_validation_bundle_manifest.json` plus its hash/freshness reports. Phase 0 must still record `external_bundle_current_target_path`, `external_bundle_role`, `external_bundle_previous_readpoint`, `external_bundle_update_allowed`, `external_bundle_reseal_required`, `external_bundle_stale_reference_policy`, `external_bundle_generator_command`, `external_bundle_content_contract`.
* External bundle generator output must be deterministic after normalization. Wall-clock-only freshness fields, host-local absolute paths, unordered maps, environment-dependent values, and run IDs are either forbidden or must be normalized / separately excluded from content hash calculation by the bundle content contract.
* Current-route runner는 live manifest를 default로 소비해야 하며, candidate manifest나 stale bundle을 current authority로 사용하면 fail-closed되어야 한다.
* Current-route runner core changes are minimized. Mainline implementation uses a reseal wrapper / validator that invokes `round3_run_contract_tests.py --class current --enforce-current-build-closure --out <phase4/current_route_validation_result.json>` and augments that output with manifest hash, source re-derive, external bundle, protected mutation, and claim-boundary evidence. Direct edits to `round3_run_contract_tests.py` are allowed only for narrow harness/evidence-write bugs or impossible-to-wrap output gaps.
* Wrapper / validator는 runner output을 증강하고 검증할 뿐, runner exit code, failed/skipped/missing required counts, field-check failures, or fail-closed verdict를 PASS로 보정하거나 재해석할 수 없다.
* 기존 `107 tests / PASS / closure_enforced=true`는 baseline trace일 뿐, 새 run의 hard-coded expected truth가 아니다.
* 최종 test count, required test count, required artifact count는 실행 시점의 live manifest와 runner output에서 기록한다.
* `OSError 22` 또는 유사 write failure가 재현되면 source-authority failure가 아니라 먼저 harness / evidence-write blocker로 분류한다.
* Harness repair가 필요한 경우 path sanitization, directory guarantee, atomic write 경계에 한정하며 validation semantic은 바꾸지 않는다.
* Harness repair semantic preservation은 선언문이 아니라 negative fixture와 diff classifier로 증명한다. known-stale bundle, candidate manifest reference, skipped required test, failed field-check fixture는 repair 이후에도 fail해야 하며, validation rule / required set / PASS predicate 변경 count는 `0`이어야 한다.
* Negative fixtures must execute only against sandbox copies of the manifest, evidence root, and external bundle. They must not mutate live `current_route_required_validations.json`, the pinned live external bundle, or sealed evidence roots.
* Protected surfaces are source facts, decisions, overlay support, rendered outputs, Lua bridge outputs, runtime chunks, package payloads, equivalent current authority payloads, and sealed-round evidence content that a broad run may regenerate.
* At minimum, sealed-round evidence content protection includes `shared_disposition_packet.json` or the exact current equivalent discovered in Phase 0. Its pre/post content hash must remain unchanged unless an explicit owner-approved evidence regeneration scope exists.
* Phase 0 must discover and classify all sealed-round evidence that the broad runner may regenerate. Any discovered sealed evidence writer output is added to the protected content set before Phase 1.
* Protected source / rendered / Lua bridge / runtime / package changed count는 최종 `0`이어야 한다.
* If `docs/EXECUTION_CONTRACT.md` is absent in a checkout, Phase 0 must classify the absence as either `blocked_missing_authority_doc` or `document_absent_not_applicable` with explicit rationale. Because this plan lists it as an authority input, the default classification is `blocked_missing_authority_doc`; `document_absent_not_applicable` is allowed only when Phase 0 proves from `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, or an owner-sealed replacement contract that this checkout intentionally has no execution-contract authority. Weak or missing rationale remains blocked.
* Dirty working tree changes outside this plan must be preserved.
* Authority Surface label for this plan is fixed as `validation/governance surface impact only`; source / rendered / Lua bridge / runtime / package authority mutation is `none`.
* Validation depth 라벨은 owner-reserved decision이다. 실행 검증 항목은 Heavy/standard 라벨과 무관하게 이 계획의 checklist 전체를 따른다.
* Owner-reserved decisions are phase-gated: pre-execution decisions, pre-manifest-update decisions, and pre-final-seal decisions are separate blockers.
* `validator-complete` 산출물의 지위는 Phase 2 전, 늦어도 live manifest update 전까지 required/supporting 중 하나로 확정해야 한다.
* Canonical / axis-qualified complete closeout requires machine pass, non-Claude independent review PASS, and owner seal PASS. Owner adoption does not substitute for independent review. Plan-level PASS, machine pass, review PASS, owner seal, and canonical seal PASS are separate states.
* 새 claim-class vocabulary는 이 계획에서 확정하지 않는다. `evidence_freshness_reseal_machine_pass` is a non-canonical internal state label until owner confirms the seal-time vocabulary.

---

## 5. Repository Areas Affected

### Code

Expected or possible offline tooling surfaces:

* `Iris/_docs/round3/round3_run_contract_tests.py`, read-mostly; edit only for narrow harness/evidence-write defects or wrapper-impossible output gaps
* `Iris/build/description/v2/tools/build/dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py`

The focused test should be subprocess-only for round-local tooling. It must not import new `tools.build.*` modules in-process from the current-route test runner, because current-route build closure allows only the 12 current core modules plus the existing narrow tooling allowlist. This follows the existing drift-verification and closeout guard test pattern.

Read-only supporting tooling inputs:

* `Iris/build/description/v2/tools/build/dvf_3_3_current_source_authority_drift_verification.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_current_source_authority_drift_verification.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_closeout_reentry_guard_seal_common.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_shared_disposition_consumption_common.py`
* `Iris/build/description/v2/tools/build/consumer_universe_denominator_lock_common.py`

No runtime Lua, source facts, decisions, rendered output, Lua bridge, runtime chunk, or package payload mutation is planned.

### Docs

Direct docs mutation in this planning task:

* `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_plan.md`

Expected docs from future execution:

* `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_claim_boundary.md`
* `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_ledger_packet.md`

Possible additive current-readpoint synchronization after successful execution:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

These docs are not updated by the reseal execution itself. They may be updated only by a separate post-final-seal doc-sync step after the required-validation reseal evidence, independent review, and owner seal states are complete.

### Config

Governance config surface:

* `Iris/_docs/round3/current_route_required_validations.json`

Candidate / supporting config surfaces:

* `Iris/_docs/round3/current_route_required_validations.shared_disposition_candidate.json`
* round-local candidate or snapshot artifacts under the evidence root

### Generated Artifacts

All new evidence should be written under:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/`

Expected artifact groups:

* `phase0/readpoint_inventory.json`
* `phase0/roadmap_input_provenance_rebind.json`
* `phase0/live_manifest_hash_report.json`
* `phase0/live_required_manifest_rollback_snapshot.json`
* `phase0/stored_evidence_inventory.json`
* `phase0/stored_evidence_role_taxonomy.json`
* `phase0/external_bundle_inventory.json`
* `phase0/external_bundle_target_pin.json`
* `phase0/external_bundle_rollback_snapshot.json`
* `phase0/protected_surface_baseline_hash_report.json`
* `phase0/sealed_round_evidence_protected_set.json`
* `phase0/authority_doc_existence_report.json`
* `phase0/readpoint_identity_gap_statement.json`
* `phase1/blocker_triage_report.json`
* `phase1/harness_evidence_write_repair_report.json`
* `phase1/harness_repair_semantic_preservation_report.json`
* `phase1/harness_negative_fixture_matrix.json`
* `phase1/validation_rule_diff_classifier.json`
* `phase1/terminal_reachability_report.json`
* `phase1/protected_surface_no_mutation_report.json`
* `phase2/drift_verification_consumption_contract.json`
* `phase2/required_artifact_field_spec.json`
* `phase2/evidence_freshness_taxonomy.json`
* `phase2/current_checkout_source_identity_redrive_report.json`
* `phase2/drift_verification_field_check_report.json`
* `phase2/owner_reserved_decision_gate_report.json`
* `phase3/live_required_manifest_update_report.json`
* `phase3/live_manifest_single_writer_report.json`
* `phase3/manifest_count_report.json`
* `phase3/taxonomy_separation_report.json`
* `phase3/additive_diff_bijection_report.json`
* `phase4/current_route_required_validation_freshness_report.json`
* `phase4/source_identity_reverification_linkage_report.json`
* `phase4/current_route_validation_result.json`
* `phase4/validation_report.all.json`
* `phase4/required_test_execution_matrix.json`
* `phase4/required_artifact_field_check_report.json`
* `phase5/external_validation_bundle_manifest.json`
* `phase5/external_validation_bundle_hash_report.json`
* `phase5/external_validation_bundle_freshness_report.json`
* `phase6/final_current_route_required_validation_evidence_freshness_reseal_report.json`
* `phase6/primary_review_artifact_manifest.json`
* `phase6/independent_review_artifact_hash_report.json`
* `phase6/no_protected_mutation_verdict.json`

---

## 6. Planned Changes

The terms `Change N` and `Phase N` are intentionally one-to-one in this plan. Each `Change N` writes evidence under `phaseN/`, and any future execution report should preserve this numbering to avoid phase/change drift.

### Change 0 - Readpoint Baseline and Scope Lock

Purpose:

현재 checkout 기준 runner, live manifest, stored evidence, external bundle, latest drift evidence root가 각각 어떤 readpoint를 가리키는지 inventory로 고정한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase0/readpoint_inventory.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase0/roadmap_input_provenance_rebind.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase0/live_manifest_hash_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase0/live_required_manifest_rollback_snapshot.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase0/stored_evidence_inventory.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase0/stored_evidence_role_taxonomy.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase0/external_bundle_inventory.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase0/external_bundle_target_pin.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase0/external_bundle_rollback_snapshot.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase0/protected_surface_baseline_hash_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase0/sealed_round_evidence_protected_set.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase0/authority_doc_existence_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase0/readpoint_identity_gap_statement.json`

Implementation Notes:

* current branch / commit / dirty state를 기록한다.
* transient roadmap attachment provenance를 repo-tracked docs 또는 evidence artifact path, sha256, line count로 rebind한다.
* current-route command path와 runner script hash를 기록한다.
* live `Iris/_docs/round3/current_route_required_validations.json` hash를 기록한다.
* live required-validation manifest rollback snapshot을 작성한다.
* candidate manifest와 live manifest를 명시적으로 분리한다.
* latest drift-verification evidence root와 final report readpoint를 기록한다. Latest root selection must use canonical docs/readpoint evidence from `docs/DECISIONS.md` / `docs/ROADMAP.md` or final report `closeout_state`, not filesystem mtime.
* stored evidence를 `consumed_current_evidence`, `supporting_trace`, `historical_evidence`, `stale_or_rejected_evidence`로 분류한다.
* external validation bundle target을 단일 concrete target으로 pinning한다. 필수 필드는 `external_bundle_current_target_path`, `external_bundle_role`, `external_bundle_previous_readpoint`, `external_bundle_update_allowed`, `external_bundle_reseal_required`, `external_bundle_stale_reference_policy`, `external_bundle_generator_command`, `external_bundle_content_contract`다. The default current target is the new round-local Phase 5 canonical bundle manifest, not an ambiguous predecessor artifact. The content contract must define deterministic hash normalization and exclude or normalize wall-clock-only / environment-dependent fields.
* If exactly one existing external bundle target is found and it is fresh-regenerable, Phase 0 may classify it as `previous_external_bundle_readpoint`. If no existing target exists, Phase 0 records `previous_external_bundle_readpoint=null` and continues with the new canonical bundle route. If multiple existing targets exist, Phase 0 records ambiguity and refuses to adopt any old target, but still continues with the new canonical bundle route unless owner explicitly blocks.
* external bundle rollback snapshot 또는 previous hash/readpoint snapshot을 작성한다.
* `docs/ARCHITECTURE.md`, `docs/PLAN_TEMPLATE.md`, `docs/EXECUTION_CONTRACT.md`와 기타 참조 authority docs의 실존과 role을 확인한다. Missing `docs/EXECUTION_CONTRACT.md` must become either `blocked_missing_authority_doc` or `document_absent_not_applicable`; the classification requires rationale.
* Since `docs/EXECUTION_CONTRACT.md` is a listed authority input, absence defaults to `blocked_missing_authority_doc`. `document_absent_not_applicable` requires positive proof that this checkout intentionally replaces or does not use that contract; absence alone is not proof.
* broad run이 재생성할 수 있는 sealed-round evidence protected set을 discover-and-classify 방식으로 기록한다. Any discovered sealed evidence writer output is included in the protected content set before Phase 1.
* protected source / rendered / Lua bridge / runtime / package no-mutation baseline을 기록한다.

Validation:

* readpoint inventory schema validation
* live manifest path existence check
* candidate / live manifest role separation check
* current-route runner discoverability check
* authority docs existence and role check
* missing `docs/EXECUTION_CONTRACT.md` classification check
* `document_absent_not_applicable` rationale sufficiency check
* canonical latest drift root selection check, with mtime selection forbidden
* stored evidence role taxonomy validation
* external bundle existing-target ambiguity hard-fail for old target adoption, with fallback to new canonical bundle route
* external bundle determinism / normalization contract validation
* rollback snapshot existence validation
* sealed-round evidence discover-and-classify completeness check
* protected surface baseline hash completeness check

---

### Change 1 - Blocker Triage / Harness Evidence-Write Repair

Purpose:

`OSError 22` 또는 유사 broad runner blocker가 현재 checkout에서 재현되는지 확인하고, 재현될 경우 source/runtime/rendered/package가 아니라 harness / evidence-write 경계 안에서만 해소한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase1/blocker_triage_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase1/harness_evidence_write_repair_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase1/harness_repair_semantic_preservation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase1/harness_negative_fixture_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase1/validation_rule_diff_classifier.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase1/terminal_reachability_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase1/protected_surface_no_mutation_report.json`
* possible harness-only edits in `Iris/_docs/round3/round3_run_contract_tests.py` or round-local tooling

Implementation Notes:

* current-route broad runner를 as-is로 실행해 terminal verdict 도달 여부를 확인한다.
* artifact sink write failure가 있으면 source-authority signal이 아니라 evidence-write blocker로 분류한다.
* repair는 path sanitization, directory guarantee, atomic write, invalid Windows path handling에 한정한다.
* pass/fail semantic, required test set, required artifact field expectation은 repair 과정에서 완화하지 않는다.
* pre-repair / post-repair command behavior를 비교한다. Pre-repair가 terminal verdict에 도달하지 못한 경우에도 fixture-level expected failures가 post-repair에서 유지되는지 기록한다.
* known-stale bundle fixture, candidate manifest reference fixture, skipped required test fixture, failed field-check fixture는 repair 후에도 fail해야 한다.
* Negative fixtures run only against sandbox copies under the Phase 1 evidence root. They must not write live `Iris/_docs/round3/current_route_required_validations.json`, the pinned live external bundle, or any sealed evidence root.
* diff classifier는 path handling / directory creation / atomic write 외 변경을 별도 `semantic_touch`로 분류하고, `semantic_touch_count`가 `0`이 아니면 Phase 1은 blocked다.
* validation rule / required set / PASS predicate 변경 count는 machine-readable field로 기록하고 모두 `0`이어야 한다.
* sealed-round evidence protected set의 pre/post content hash를 비교한다.

Validation:

* blocker reproduced or not reproduced 기록
* repair 이후 broad runner terminal verdict 도달
* pre-repair / post-repair command comparison
* known-stale bundle fixture remains failing
* candidate manifest reference fixture remains failing
* skipped required test fixture remains failing
* failed field-check fixture remains failing
* negative fixture sandbox isolation proof
* validation rule / required set / PASS predicate changed count `0`
* diff classifier semantic touch count `0`
* sealed-round evidence protected content hash unchanged
* protected surface changed count `0`

---

### Change 2 - Drift Verification Consumption Contract / Field Spec

Purpose:

Current Source Authority Drift Verification / Recovery Scope Retirement 결과를 live required-validation manifest가 machine-readable하게 소비할 수 있도록 field spec과 evidence freshness taxonomy를 정의한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase2/drift_verification_consumption_contract.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase2/required_artifact_field_spec.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase2/evidence_freshness_taxonomy.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase2/current_checkout_source_identity_redrive_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase2/drift_verification_field_check_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase2/owner_reserved_decision_gate_report.json`

Implementation Notes:

* Drift verification final report의 required fields를 정의한다.
* 최소 field는 `status`, `closeout_state`, source manifest identity, successor source count, facts / decisions / overlay hash parity, direct compose sandbox evidence, missing overlay count, protected live write count, recovery live-write scope retirement state, candidate manifest non-authority, release/manual QA/semantic quality non-claim을 포함한다.
* Drift evidence가 source writer가 아니라 read-only governance evidence임을 taxonomy에 명시한다.
* Mainline은 current checkout source에서 source manifest identity, facts / decisions / overlay hash parity, successor `2105` identity를 재도출하고, drift report의 recorded values와 비교한다.
* 재도출값과 recorded drift values가 불일치하면 fail-closed한다.
* 재도출을 수행할 수 없으면 drift evidence root는 `provenance_only`로 강등하고, Phase 4 broad runner가 current checkout source identity를 재검증했다는 linkage evidence를 요구한다.
* Legitimate provenance-only triggers are limited to: missing machine-comparable hash/count fields in the historical drift report, obsolete or unreproducible hash normalization metadata, or Phase 0 pre-classification as historical/provenance-only before comparison.
* Precedence rule: if current checkout re-derivation and recorded-value comparison are possible, any mismatch is fail-closed and cannot be reclassified as provenance-only.
* `validator-complete` 산출물을 required artifact로 둘지 supporting evidence로 둘지는 Phase 2 이전, 늦어도 live manifest update 전까지 봉인한다.
* Owner-reserved decision gates를 `pre-execution`, `pre-manifest-update`, `pre-final-seal`로 분리한 report를 작성한다.

Validation:

* field spec validator
* drift-verification artifact presence check
* drift-verification artifact field check
* current checkout source identity / hash parity re-derivation check
* drift recorded values versus current re-derived values comparison
* provenance-only fallback trigger classification
* mismatch cannot downgrade to provenance-only check
* provenance-only fallback requires Phase 4 source-identity linkage evidence
* `validator-complete` required/supporting status resolved before manifest update
* non-authority / candidate guard check
* no live-write assertion check

---

### Change 3 - Live Required Manifest / Taxonomy Reseal

Purpose:

Drift verification consumption contract를 live `current_route_required_validations.json`에 required artifact / required test로 additive 채택한다.

Files:

* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase3/live_required_manifest_update_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase3/live_manifest_single_writer_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase3/manifest_count_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase3/taxonomy_separation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase3/additive_diff_bijection_report.json`

Implementation Notes:

* Live manifest에 drift-verification required artifacts와 focused freshness tests를 additive하게 추가한다.
* Existing required entries를 제거하지 않는다.
* Candidate manifest는 supporting trace로만 둔다.
* Manifest entry별 owning axis를 required-validation freshness reseal 범위로 둔다.
* Manifest는 live manifest hash, owning evidence root, required artifact list, required test list, required artifact field spec reference, non-claim boundary reference, external bundle reseal requirement를 요구해야 한다.
* Live manifest single-writer status와 concurrent-writer absence를 기록한다.
* `additive_diff_bijection_report`는 `removed_existing_entries=0`, `modified_existing_entries=0`, `added_entries=N`, `duplicate_entries=0`을 필수 필드로 가진다.
* Existing entry key / path / check mutation이 감지되면 manifest update는 fail-closed한다.
* Existing `107 tests / closure_enforced=true`는 baseline trace로만 기록하고, 최종 성공 기준은 fresh run의 actual count로 둔다.

Validation:

* manifest schema validation
* manifest count derivation validation
* additive diff-to-prior check with removed existing entries `0`
* modified existing entries `0`
* added entries `N`
* duplicate entries `0`
* live manifest single-writer / concurrent-writer absence check
* candidate manifest rejection test
* required artifact / required test duplicate check
* required entry owning-axis check
* required gate vocabulary and runtime row vocabulary separation check

---

### Change 4 - Current-Route Runner Fail-Closed Integration / Fresh Execution

Purpose:

Current-route runner가 live required manifest와 evidence freshness contract를 실제로 소비하고, 현재 checkout에서 fresh exit code `0`을 관측한다.

Files:

* `Iris/_docs/round3/round3_run_contract_tests.py`, read-mostly; wrapper should consume its `--out` result
* round-local tooling under `Iris/build/description/v2/tools/build/`
* focused test under `Iris/build/description/v2/tests/`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase4/current_route_required_validation_freshness_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase4/source_identity_reverification_linkage_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase4/current_route_validation_result.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase4/validation_report.all.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase4/required_test_execution_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase4/required_artifact_field_check_report.json`

Implementation Notes:

* Mainline은 runner core를 수정하지 않고 reseal wrapper가 `round3_run_contract_tests.py --class current --enforce-current-build-closure --out phase4/current_route_validation_result.json`을 실행한다.
* Runner 자체는 live manifest를 읽고 required artifact/test를 fail-closed 처리하는 기존 역할을 유지한다.
* Wrapper / validator는 runner verdict를 단조롭게 강화할 수만 있다. Runner가 실패하거나 required check failure를 기록하면 wrapper도 실패해야 하며, 추가 evidence가 runner failure를 PASS로 바꿀 수 없다.
* Wrapper / validator는 live manifest hash를 기록한다.
* Wrapper / validator는 runner output의 required validation payload를 분해해 missing / skipped / failed required test count를 별도 필드로 기록한다.
* Wrapper / validator는 required artifact field check 결과를 재분류한다.
* Wrapper / validator는 external validation bundle freshness requirement를 검사한다.
* Stale stored evidence, stale external bundle, candidate manifest reference는 fail-closed 처리한다.
* Phase 2가 drift evidence를 `provenance_only`로 강등한 경우, wrapper / validator는 current checkout source identity / hash parity / successor `2105` identity를 직접 재검증했다는 linkage evidence를 남긴다.
* Wrapper / validator는 final report가 요구할 `current_route_command_text`, `exit_code`, `started_at`, `finished_at`, `working_tree_dirty_state`, `runner_script_hash`를 산출한다.
* Wrapper output은 `actual_test_count`, `required_test_count`, `required_artifact_count`, `missing_required_test_count`, `skipped_required_test_count`, `failed_required_test_count`, `missing_required_artifact_count`, `failed_required_artifact_field_check_count`, `closure_enforced`, `manifest_hash`, `runner_readpoint`, `evidence_root`, `external_bundle_readpoint`, `protected_mutation_changed_count`를 포함한다.
* Wrapper output must include `runner_exit_code`, `runner_status`, `wrapper_status`, and `pass_reinterpretation_count=0`.
* Direct runner edit is a fallback only. If used, `harness_repair_semantic_preservation_report.json` must prove the change is not a PASS predicate / required set / validation rule change.

Validation:

* `uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure`
* focused manifest freshness test, subprocess-only for round-local tooling
* focused drift-verification field check test
* source identity re-verification linkage test
* focused external bundle freshness test
* skipped required test hard-fail test
* candidate manifest hard-fail test
* stale bundle hard-fail test
* wrapper cannot convert runner failure to PASS test
* final exit code `0` only when all required checks pass

---

### Change 5 - External Validation Bundle Reseal

Purpose:

External validation bundle이 새 current-route run 결과를 반영하도록 재생성하고 hash / readpoint를 봉인한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase5/external_validation_bundle_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase5/external_validation_bundle_hash_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase5/external_validation_bundle_freshness_report.json`
* round-local canonical external validation bundle selected by Phase 0 target pin

Implementation Notes:

* External bundle은 기본적으로 이 라운드가 생성하는 Phase 5 canonical target만 current success evidence로 사용한다.
* Phase 0의 `external_bundle_target_pin.json`은 새 canonical target을 `external_bundle_current_target_path`로 고정하고, 기존 concrete target이 하나만 발견될 경우에만 `external_bundle_previous_readpoint`로 기록한다.
* 기존 target이 없으면 new canonical bundle route로 계속 진행한다. 이는 failure가 아니다.
* 기존 target이 복수이거나, stale이거나, non-regenerable이거나, role / generator / content contract가 모호하면 existing-target adoption만 fail-closed하고 새 canonical bundle route로 전환한다.
* 새 canonical target 생성, schema validation, deterministic hash validation, runner-output readpoint binding 중 하나라도 실패하면 Phase 5는 fail-closed한다.
* Generator command must be deterministic under the Phase 0 content contract. Wall-clock-only freshness, host-local absolute path, unordered map ordering, and environment-derived nondeterminism must be normalized or excluded from the content hash contract.
* External bundle을 fresh current-route result에서 재생성한다.
* Bundle manifest는 run id, runner readpoint, live manifest hash, evidence root, actual test count, required test count, required artifact count, required artifact field-check result, missing/skipped/failed required test counts, drift-verification consumption status, non-claim boundary를 포함한다.
* 이전 external bundle은 historical trace로만 남긴다.
* Stale bundle이 current-route PASS 근거가 되지 않도록 guard를 추가한다.

Validation:

* external bundle schema validation
* external bundle target path matches Phase 0 pin
* external bundle role / generator / content contract validation
* external bundle generator determinism / normalized hash validation
* old external bundle multiple-target ambiguity hard-fails existing-target adoption only
* old external bundle absence continues through new canonical bundle route
* new canonical external bundle missing-target hard-fail
* external bundle hash validation
* bundle readpoint matches runner output
* bundle manifest hash matches live manifest hash
* bundle evidence root matches final current-route result
* stale bundle regression test

---

### Change 6 - Final Reseal, Review, and Claim Boundary

Purpose:

이번 라운드를 required-validation evidence freshness reseal로 닫고, success claim과 non-claim boundary를 분리한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase6/final_current_route_required_validation_evidence_freshness_reseal_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase6/primary_review_artifact_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase6/independent_review_artifact_hash_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_required_validation_evidence_freshness_reseal/phase6/no_protected_mutation_verdict.json`
* `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_claim_boundary.md`
* `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_ledger_packet.md`

Implementation Notes:

* Final report는 `required_validation_gate_adopted / evidence_freshness_reseal_closeout_state` 아래에 closeout sub-state를 기록한다. Standalone `complete` field는 사용하지 않는다.
* Final report는 `current_route_command_text`, `exit_code`, `started_at`, `finished_at`, `working_tree_dirty_state`, `runner_script_hash`, actual test count, required test count, required artifact count, missing/skipped/failed required test count `0`, failed required artifact field check count `0`, external bundle freshness PASS, live manifest consumed PASS, drift-verification evidence consumed or provenance-only-plus-current-redrive PASS, candidate manifest not authority PASS, protected source/rendered/Lua/runtime/package mutation `0`, sealed-round evidence content mutation `0`, non-claim boundary를 명시한다.
* If machine-verifiable validation passes before review/seal, final report may close using the internal non-canonical state label `evidence_freshness_reseal_machine_pass` or `machine_pass_review_pending`, not canonical `complete`.
* Canonical / axis-qualified complete closeout은 machine pass, non-Claude independent review PASS, and owner seal이 모두 없으면 blocked다.
* Owner adoption is recorded separately and does not substitute for independent review.
* Plan-level PASS, machine validation PASS, independent review PASS, owner seal, and canonical seal PASS are separate fields.
* Authority Surface label은 `validation/governance surface impact only`로 기록한다. Validation depth label 또는 owner-reserved 항목이 미해결이면 final closeout sub-state는 `blocked_owner_decision_pending`, `machine_pass_review_pending`, 또는 `partial_review_pending`으로 닫는다.

Validation:

* final report schema validation
* claim boundary scan
* no protected mutation validation
* machine pass state validation independent from canonical complete state
* non-Claude independent review artifact hash validation for canonical / axis-qualified complete closeout
* owner seal state recorded separately from independent review
* current-route command rerun after final bundle reseal
* required manifest hash equals final report manifest hash
* external bundle manifest hash equals final report manifest hash

---

## 7. Validation Plan

### Automated Validation

Primary current-route command:

* `uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure`

Expected focused commands if round-local tooling is implemented:

* `uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py --mode machine-pass`
* `uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py --mode all`
* `uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py --require-complete`
* `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py"`

Required automated validation areas:

* current-route regression
* live required-validation manifest consumption
* manifest hash binding
* current checkout source identity / hash parity re-derivation or provenance-only-plus-current-redrive linkage
* artifact presence
* artifact field freshness
* stored evidence role classification
* old external bundle ambiguity rejects old-target adoption without blocking the new canonical bundle route
* new canonical external bundle target creation / binding hard-fail
* external validation bundle freshness
* deterministic count recording
* readpoint identity / fingerprint binding
* round-local focused tests remain subprocess-only and add no new in-process `tools.build.*` imports to the current-route closure
* no protected mutation
* sealed-round evidence content hash invariance
* rollback snapshot existence
* candidate manifest rejection
* stale manifest rejection
* stale bundle rejection
* skipped required test hard-fail
* failed field-check hard-fail
* harness repair negative fixture preservation
* live manifest single-writer assertion
* additive manifest diff hard rule
* claim boundary scan
* completion vocabulary separation
* Windows path / artifact sink failure handling

### Manual Validation

Manual validation is governance review only:

* pre-manifest-update owner decision on `validator-complete` required/supporting status
* pre-final-seal owner decision on validation depth label if the final report wants to display one
* non-Claude independent review of primary review artifact manifest and hash report for canonical / axis-qualified complete closeout
* owner seal recorded separately after independent review; owner adoption does not replace independent review

No runtime UI, Browser, Wiki, Tooltip, in-game, multiplayer, or package manual validation is planned.

### Validation Limits

This plan will not validate:

* runtime in-game behavior
* multiplayer behavior
* long-session runtime behavior
* manual in-game QA
* package zip readiness
* Workshop readiness
* B42 readiness
* deployment readiness
* semantic quality completion
* public-facing Korean text acceptance
* live migration execution
* full source / rendered / runtime equivalence beyond required field freshness
* historical route full byte reproducibility
* external ecosystem compatibility sweep

---

## 8. Risk Surface Touch

### Authority Surface

Authority Surface: `validation/governance surface impact only`.

Source facts / decisions / overlay / rendered / Lua bridge / runtime chunk / package payload authority mutation: none.

This plan touches only:

* `Iris/_docs/round3/current_route_required_validations.json`
* required-validation taxonomy or equivalent field spec
* current-route runner validation report surface
* external validation bundle manifest/report
* new evidence root

This label is fixed for the plan to avoid execution-time owner-reserved ambiguity.

### Runtime Behavior Surface

None.

No Lua runtime behavior, Browser/Wiki/Tooltip display, runtime payload shape, package payload, or in-game behavior changes are planned.

### Compatibility Surface

Limited validation compatibility impact.

Current-route command may become stricter. Stale artifact, skipped required test, external bundle mismatch, or candidate manifest reference that previously passed may fail after this reseal.

No public API, runtime compatibility, external mod compatibility, or in-game compatibility surface is changed.

### Sealed Artifact Surface

Additive impact.

This plan creates a new evidence root and may update the live required-validation manifest additively. Existing sealed drift verification / closeout / cutover evidence remains read-only and is consumed as input, not reopened.

Broad-run-regenerable sealed-round evidence is included in the protected content hash set. At minimum, Phase 0 must discover and protect `shared_disposition_packet.json` or the current equivalent; pre/post content hash mutation must be `0` unless a separate owner-approved evidence regeneration scope exists.

### Public-Facing Output Surface

None.

README, Workshop page, release note, user-facing text quality claim, and public-facing Korean content acceptance are out of scope.

---

## 9. Risk Analysis

### Architecture Risk

* Live required-validation manifest adoption could be misread as source/runtime authority mutation.
* Drift-verification PASS could be overread as source restoration or live-write authorization.
* Stale drift-verification evidence could be consumed as a fresh anchor without current checkout re-derivation.
* Candidate manifest and live manifest could be conflated.
* New claim-class vocabulary could leak into canonical docs before owner approval.

### Runtime Risk

* Direct runtime risk is none because no runtime Lua, runtime chunk, rendered output, Lua bridge, or package payload mutation is planned.
* Indirect risk is overclaiming governance PASS as runtime readiness.

### Compatibility Risk

* Stricter current-route fail-closed behavior can expose stale evidence or skipped required tests that previously passed.
* Harness repair can accidentally mask real validation failure if it changes pass/fail semantics instead of write handling.
* External bundle ambiguity can make the reseal consume an old artifact unless Phase 0 pins the new canonical target and downgrades old bundles to previous-readpoint evidence.
* Windows path normalization differences can create false mismatches if not explicitly normalized.

### Regression Risk

* Hard-coding the old `107 tests` count can hide manifest drift.
* Existing required entries could be accidentally removed while adding drift-verification entries.
* External validation bundle may be regenerated from stale stored evidence instead of the fresh runner output.
* Drift evidence field check may pass without current-readpoint source identity re-derivation.
* Final report may use `PASS`, `complete`, `ready`, or `current` without an owning evidence root and claim axis.

---

## 10. Rollback Plan

Rollback is limited to validation / governance surfaces.

If validation fails or unexpected regressions appear:

* Revert live `Iris/_docs/round3/current_route_required_validations.json` to `phase0/live_required_manifest_rollback_snapshot.json`.
* Revert external validation bundle to `phase0/external_bundle_rollback_snapshot.json` or to the recorded previous target hash/readpoint.
* Revert round-local runner / validator / test changes.
* Revert harness / evidence-write repair if it changed validation semantics or caused false PASS.
* Mark new external validation bundle as `failed_reseal_attempt` or `superseded_attempt`; do not reuse it as current success evidence.
* Preserve the failed evidence root as provenance unless owner requests cleanup.
* Remove or downgrade final report canonical wording if independent review / owner seal is incomplete.
* If protected source / rendered / Lua bridge / runtime / package surfaces changed, stop and treat rollback as blocking before any closeout claim.
* If sealed-round evidence protected content changed without explicit owner-approved evidence regeneration scope, stop and treat rollback as blocking before any closeout claim.

Rollback must not:

* resurrect stale PASS bundle as current success evidence
* lower required artifact / required test count to make PASS easier
* modify existing required manifest entries to turn a failure into PASS
* promote candidate manifest to live authority
* treat drift-verification evidence as source writer authority
* claim release/package/runtime readiness as a substitute success

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Hub & Spoke / SPI boundaries remain unchanged.
* Iris remains offline-sealed evidence producer plus runtime viewer; runtime does not infer, repair, recommend, compare, or judge semantic quality.
* Required-validation manifest entries are governance gates, not runtime/source/rendered/package writers.
* Existing sealed surfaces are read-only inputs unless this plan explicitly opens additive governance consumption.
* Source / rendered / Lua bridge / runtime / package protected mutation count must remain `0`.
* Candidate manifests are not current authority.
* Stale stored evidence and stale external bundles cannot support fresh current-route PASS.
* Stale drift-verification evidence cannot support fresh readpoint identity without current checkout source re-derivation or provenance-only-plus-current-redrive linkage.
* Latest drift-verification evidence root selection must follow canonical docs/readpoint or final report closeout state, never filesystem mtime alone.
* Provenance-only fallback is allowed only for explicit non-comparable historical drift evidence. If current re-derivation and recorded-value comparison are possible, mismatch is fail-closed and cannot be downgraded to provenance-only.
* Exact validation commands must exit with code `0` before any PASS claim is made.
* Required test count and required artifact count must be derived from the live manifest, not hard-coded from old `107 tests` evidence.
* Missing / skipped / failed required tests must fail closed.
* Required artifact field-check failures must fail closed.
* Wrapper / validator must not convert runner failure, skipped/missing/failed required tests, or required artifact field-check failure into PASS.
* Live manifest diff must be additive-only: removed existing entries `0`, modified existing entries `0`, duplicate entries `0`, added entries `N`.
* Live manifest single-writer status and concurrent-writer absence must be recorded before mutation.
* External validation bundle target must be pinned in Phase 0 as the new round-local canonical Phase 5 bundle; any old bundle is previous-readpoint evidence only.
* External validation bundle generator output must be deterministic after the Phase 0 content normalization contract.
* Negative fixtures must run against sandbox copies only and must not mutate live manifest, live external bundle, or sealed evidence roots.
* Sealed-round evidence protected set must be discover-and-classify based; any broad-run-regenerable sealed evidence discovered in Phase 0 is protected before Phase 1.
* Missing `docs/EXECUTION_CONTRACT.md` must be explicitly classified as `blocked_missing_authority_doc` or `document_absent_not_applicable`; because it is a listed authority input, weak rationale or mere absence defaults to `blocked_missing_authority_doc`.
* `validator-complete` required/supporting status is a pre-manifest-update blocker.
* Validation depth label is a pre-final-seal display decision only; it cannot remove required checks.
* Machine pass may close before review, but non-Claude independent review PASS is a pre-final-seal hard gate for canonical / axis-qualified complete closeout.
* Owner adoption does not substitute for independent review.
* New claim-class vocabulary remains unapproved; final report uses `required_validation_gate_adopted / evidence_freshness_reseal_closeout_state`. `evidence_freshness_reseal_machine_pass` remains a non-canonical internal state label unless owner confirms it at seal time.
* Dirty working tree changes outside this plan must be preserved.

---

## 12. Expected Closeout State

Expected first closeout target: `required_validation_gate_adopted / evidence_freshness_reseal_closeout_state=evidence_freshness_reseal_machine_pass`, as a non-canonical internal machine-verification state label only if all machine validation conditions pass. Owner confirms the exact token at seal time.

Canonical final closeout target: `required_validation_gate_adopted / evidence_freshness_reseal_closeout_state=complete`, only if machine validation, non-Claude independent review, and owner seal all pass.

`required_validation_gate_adopted / evidence_freshness_reseal_closeout_state=evidence_freshness_reseal_machine_pass` requires:

* current-route command exits with code `0` on current checkout
* `closure_enforced=true`
* wrapper `pass_reinterpretation_count=0`
* wrapper status cannot be PASS unless runner exit code and runner status are PASS
* runner / live manifest / stored evidence / external bundle are bound to one evidence readpoint or fingerprint
* current checkout source identity / hash parity / successor `2105` identity is re-derived, or drift evidence is provenance-only and Phase 4 proves source-identity revalidation linkage
* actual current-route test count is recorded
* required test count is recorded
* required artifact count is recorded
* missing required test count is `0`
* skipped required test count is `0`
* failed required test count is `0`
* missing required artifact count is `0`
* failed required artifact field check count is `0`
* live manifest hash is recorded consistently in runner output and final report
* drift-verification evidence root is consumed by live required-validation manifest / taxonomy only with current-readpoint re-derivation or provenance-only-plus-current-redrive linkage
* candidate manifest is proven non-authority
* stored evidence role taxonomy classifies consumed current evidence, supporting trace, historical evidence, and stale/rejected evidence
* external validation bundle reflects the fresh current-route run
* external bundle target matches Phase 0 pin and content contract
* external bundle hash report points to the same run / readpoint as the final report
* protected source / rendered / Lua bridge / runtime / package mutation count is `0`
* sealed-round evidence protected content mutation count is `0`
* live manifest additive diff records removed existing entries `0`, modified existing entries `0`, duplicate entries `0`, added entries `N`
* live manifest single-writer / concurrent-writer absence is recorded
* `OSError 22` or equivalent blocker is resolved or the round closes as explicit FAIL
* final claim boundary preserves release/package/Workshop/B42/deployment/manual QA/semantic quality/public-facing text non-claims
* machine pass report explicitly states that canonical complete is not claimed until review and owner seal pass

`required_validation_gate_adopted / evidence_freshness_reseal_closeout_state=complete` additionally requires:

* non-Claude independent review PASS is present
* owner seal PASS is recorded separately and does not substitute for independent review
* final report links the machine pass report, independent review artifact hash report, and owner seal evidence

Expected alternate closeout states:

* `machine_pass_review_pending`: machine validation passed, but non-Claude independent review or owner seal remains pending.
* `partial_review_pending`: implementation and some evidence exist, but one or more reviewable artifacts are incomplete.
* `blocked_owner_decision_pending`: validator-complete status, validation depth display label, or other phase-gated owner decision blocks final seal.
* `blocked`: live manifest cannot be consumed, current-route runner cannot reach terminal verdict, drift source identity freshness cannot be re-derived or linked, new canonical external bundle cannot be generated or bound, required artifact/test failures remain, protected mutation is nonzero, sealed-round evidence content mutation is nonzero, or an owner-reserved decision blocks final seal.
* `failed_reseal_attempt`: stale evidence, stale bundle, candidate manifest, skipped required test, or failed field-check is detected and not repaired in this round.
