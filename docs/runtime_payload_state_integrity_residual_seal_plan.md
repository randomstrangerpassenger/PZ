# Runtime Payload State Integrity Residual Seal Plan

> Status: planned / WARN cycle 2 revisions incorporated / roadmap-derived / authority-closeout only / no runtime mutation / author decision coverage pending / independent review pending / complete seal not allowed yet
> 작성일: 2026-06-18
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Embedded roadmap basis: sections `1`, `1-A`, and `1-B` in this plan
> Drafting roadmap trace: `C:/Users/MW/.codex/attachments/b85ba347-374a-4ea5-98fb-c332b275137b/pasted-text.txt` / sha256 `B390906841328FB6B3929E4FA04A77B18BDCC7BC4D82B1C98CE23C4756DB1E2C`
> Final review input cycle 1: `C:/Users/MW/.codex/attachments/83e9d50c-1e56-4992-b57e-480f36129947/pasted-text.txt` / sha256 `B79D2FA835429929A3E4E1D04B270114DC94DFD2893F7D8FB25587D00347B3CF` / external review trace, WARN revisions incorporated
> Final review input cycle 2: `C:/Users/MW/.codex/attachments/5767ef2b-3c36-4d4f-874b-ace6de4c393d/pasted-text.txt` / sha256 `6E623080BE6F44298A280507B83D20F01018EB51DC59B0FD6288338F9516E3AC` / external review trace, Branch closeout predicate revisions incorporated
> Predecessor guard plan: `docs/runtime_payload_state_integrity_plan.md`
> Evidence root: `Iris/build/description/v2/staging/runtime_payload_state_integrity/`

---

## 1. Objective

`Runtime Payload State Integrity Residual Seal Round`를 current payload mutation이 아니라 authority closeout round로 실행한다.

이 계획의 목적은 current-like surface에서 canonical forbidden tuple set을 금지한다는 결정을 author decision, evidence, required validation, authority-doc packet flow, independent review gate로 봉인하는 것이다.

predecessor rollback snapshot의 `unadopted + exposed + non_nil text_ko` residue 2건은 historical-only residue로 보존한다. 이 residue는 current debt, source/runtime/package/rendered payload mutation 근거, publish policy, renderer policy, deletion/suppression 의미로 승격하지 않는다.

완료 claim은 independent review 상태에 따라 분리한다.

```text
complete_residual_seal:
Current-like forbidden payload shape and predecessor/historical residue preservation boundary are sealed by author decision, evidence, required validation, authority-doc reflection, and independent review.

external_gate_pending:
Guard pass and author decision are sealed, but independent review remains an explicit external gate. This is not a current runtime implementation blocker.
```

---

## 1-A. Canonical Forbidden Tuple Set

Phase 1 census, Phase 2 contract, Phase 4 validator, and final closeout must consume the same canonical forbidden tuple set.

* F1: current-like surface row has `state == unadopted` and a non-nil display body such as non-nil `text_ko`.
* F2: current-like surface row has any `publish_state` field present. This includes legacy `publish_state == exposed`.
* F3: current-like surface row uses legacy `active` or `silent` as current writer/runtime state vocabulary.
* F4: current-like surface row has forbidden or unclassified state outside the sealed current vocabulary.
* F5: current-like dynamic renderer-visible reach exposes a display body for a current-like `unadopted` row.

`exposed` means legacy `publish_state == exposed` unless a report explicitly says `renderer_listing_exposed`. A row being reachable in an all-item browser/listing with `missing` or explicit `nil` display body is not by itself a payload-shape violation. `unadopted + renderer_listing_exposed + nil/missing body` is allowed unless it also hits F1, F2, F3, F4, or F5.

Current-like surface means live current runtime, package peer, and candidate bridge. Package peer payload scan is mandatory for complete seal. Full package build is a separate regression route and does not replace package peer payload scan.

---

## 1-B. Embedded Roadmap Basis

This section is an embedded convenience restatement of the roadmap basis consumed by this plan. It is not a separate authority artifact and does not replace `docs/ROADMAP.md`.

### Problem Statement

Runtime Payload State Integrity Guard는 current-like runtime surface 기준의 핵심 payload collision을 이미 닫았다. live current runtime, package peer, candidate bridge에서 current-like `unadopted + publish_state`, `unadopted + non_nil text_ko`, legacy `active / silent` current re-entry는 금지되며, current-compatible payload shape는 guard를 통과한다.

남은 문제는 runtime payload 자체가 아니라 authority closeout의 미완성이다. predecessor rollback snapshot에 남아 있는 `unadopted + exposed + non_nil text_ko` residue 2건은 current debt가 아니라 historical-only residue로 분리되어야 한다. 이 분리가 author decision artifact, validator/evidence/docs/manifest 소비 경로, independent review gate까지 complete seal로 닫히지 않았다.

### Desired Outcome

* current-like surface와 predecessor/historical surface의 `unadopted` allowed shape를 명확히 분리한다.
* current-like runtime, package peer, candidate bridge에서 canonical forbidden tuple set을 fail-loud로 금지한다.
* predecessor rollback snapshot의 residue 2건은 historical-only residue로만 보존한다.
* residue 2건은 publish policy, runtime policy, renderer policy, source authority, deletion/suppression 의미로 승격하지 않는다.
* author decision coverage는 current-like forbidden boundary와 historical residue preservation boundary를 각각 명시적으로 채택하거나 보류한다.
* complete seal은 두 coverage 축이 모두 `adopted`이고 `no_branch_external_gate == false`일 때만 허용한다.
* validator, evidence, authority-doc packets, Round 3 required validation manifest가 동일한 boundary language를 소비한다.
* independent review는 complete seal을 승인하거나, 미완료 시 explicit external gate로 남긴다.
* review pending은 current implementation blocker가 아니라 governance seal level pending gate로 기록한다.

### Phase Roadmap

* Phase 1: current checkout 기준 residual state를 재근거화하고 live current / package peer / candidate bridge를 current-like surface로, predecessor rollback snapshot을 predecessor/historical surface로 분리한다.
* Phase 2: current-like vs historical payload shape contract를 작성한다.
* Phase 3: author decision coverage를 capture하거나 `author_decision_pending`으로 fail-closed한다.
* Phase 4: focused residual tests, validator evidence, current route required validation manifest, package peer scan, no-mutation evidence를 canonical forbidden tuple set 기준으로 정렬한다.
* Phase 5: policy, ledger, roadmap, architecture reflection을 staging update packet으로 작성하고 canonical docs는 author-applied target으로 남긴다.
* Phase 6: independent review packet과 final closeout을 작성한다. Complete seal은 independent review 뒤에만 허용한다.

### Claim Boundary

This plan does not mean full runtime equivalence, full compatibility preservation, source authority reconstruction, rendered text quality acceptance, semantic quality completion, package release readiness, Workshop readiness, deployment readiness, B42 readiness, manual in-game validation completion, public-facing text approval, runtime policy change, publish policy change, `quality_state` UI exposure, predecessor residue deletion, current runtime payload mutation, or successor baseline / cutover / consumer migration revalidation.

If complete review is satisfied, the maximum claim is:

```text
Runtime Payload State Integrity Residual Seal has sealed the current-like forbidden payload shape and predecessor/historical residue preservation boundary through author decision, evidence, required validation, authority-doc packet flow, and independent review.
```

If complete review is not satisfied, the maximum claim is:

```text
Guard pass and author decision are sealed, and independent review remains an explicit external gate. This is not a current runtime implementation blocker.
```

---

## 2. Scope

이 계획은 residual seal을 위해 다음 범위를 수행한다.

* current checkout 기준 residual state 재근거화
* current-like surface와 predecessor/historical surface 분리
* `unadopted` payload shape bifurcation contract 작성
* canonical forbidden tuple set을 Phase 1 / Phase 2 / Phase 4 / final closeout에서 동일하게 소비
* author decision coverage packet 작성
* Branch A / Branch B framing disposition 작성
* no-branch external gate disposition 작성
* validator / evidence report / current-route required validation manifest alignment
* package peer payload scan mandatory coverage 확보
* protected source/runtime/package/rendered surface no-mutation 증명
* authority docs / ledger / roadmap / architecture staging update packet 작성
* canonical `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` author-applied target 경계 기록
* Round 3 runner modification boundary report 작성, if runner changes are unavoidable
* independent review packet 작성
* final closeout status를 `complete_residual_seal` 또는 explicit external gate pending으로 기계적으로 분리

Preferred residual seal evidence subroot:

* `Iris/build/description/v2/staging/runtime_payload_state_integrity/residual_seal/`

If existing tooling requires the parent evidence root directly, Phase 1 must record the selected artifact root and alias policy before producing seal evidence.

### Explicitly Out Of Scope

* runtime payload mutation
* source facts / decisions / rendered text mutation
* Lua source mutation
* live chunk replacement
* direct runtime chunk edit
* current cutover reopen
* successor baseline identity reseal
* 2105 consumer migration re-execution
* predecessor residue deletion
* predecessor rollback snapshot promotion to current authority
* `unadopted` enum redefinition
* `publish_state` runtime policy reintroduction
* `quality_state` UI exposure
* Browser / Wiki / Tooltip policy redesign
* renderer behavior change
* legacy `active / silent` current vocabulary restoration
* package release readiness
* Workshop readiness
* B42 readiness
* deployment readiness
* manual in-game QA completion
* semantic or public-facing text quality acceptance
* external mod compatibility sweep
* DVF 3-3 외 타 모듈 작업

---

## 3. Non-Goals

* Codex, tooling, validator output이 author decision coverage를 임의 채택하지 않는다.
* review pending을 current runtime implementation blocker로 승격하지 않는다.
* implemented guard pass를 complete residual seal로 과대 선언하지 않는다.
* predecessor residue allowance를 current-like allowance처럼 문서화하지 않는다.
* `unadopted`를 quality-fail, suppression, deletion, hidden, publish-state 신호로 해석하지 않는다.
* broad current-route failure를 runtime payload policy 우회 변경 근거로 사용하지 않는다.
* validator one-line patch나 문구 수정만으로 complete seal을 주장하지 않는다.
* release / package / Workshop / deployment readiness를 closeout에 암시하지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 기준이다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 Iris DVF 3-3 runtime payload state integrity readpoint를 따른다.
* current-compatible payload shape의 current readpoint는 `2105` rows, `21` unadopted rows, current-like `publish_state` rows `0`, current-like forbidden/unclassified state rows `0`이다.
* current-like surfaces are live current runtime, package peer, and candidate bridge surfaces.
* package peer payload scan is mandatory for complete seal. Full package build may be unavailable or separately blocked, but package peer scan cannot be omitted from current-like denominator without blocking complete seal.
* predecessor rollback snapshot의 `unadopted + exposed + non_nil text_ko` residue count는 `2`이며, current-like denominator에 포함하지 않는다.
* current-like `unadopted` row의 display text fields는 `missing` 또는 explicit `nil`이어야 한다.
* field absence, explicit `nil`, and non-nil string body are distinct states.
* `exposed` means legacy `publish_state == exposed` unless a report explicitly says `renderer_listing_exposed`.
* `unadopted + renderer_listing_exposed + nil/missing body` is not a payload-shape violation unless it also hits the canonical forbidden tuple set.
* runtime Lua remains a sealed payload renderer and does not compose, repair, validate source, normalize state, decide publish policy, or judge semantic quality.
* `Iris/_docs/round3/current_route_required_validations.json`은 payload state guard artifacts와 focused tests를 fail-closed required validation으로 소비해야 한다.
* `Iris/_docs/round3/round3_run_contract_tests.py` should not be changed if manifest-only alignment can consume the residual seal artifact. If it must change, the change must be limited to residual seal artifact consumption and must emit a runner boundary report.
* author decision coverage is project author / maintainer reserved decision.
* Branch A / Branch B are framing labels for decision coverage dimensions, not sufficient complete-seal choices by themselves.
* no-branch is an external gate / defer state and cannot satisfy complete seal.
* Codex and tooling may not redefine branch meaning or author-decision coverage during execution.
* If Phase 1 census changes any assumed count, the execution must update the evidence and close as blocked or revised-plan-needed instead of forcing a pass.
* Independent review is required for complete seal. A review authored by the same roadmap or plan authorship chain does not count as independent final verification.
* Canonical `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` reflection is author-applied. Executor output is limited to staging update packets unless the author separately requests direct canonical edits.
* Dirty working tree changes outside this plan are preserved.

---

## 5. Repository Areas Affected

### Code

Expected build-time tooling or tests, only if Phase 4 alignment requires implementation changes:

* `Iris/build/description/v2/tools/build/runtime_payload_state_integrity.py`
* `Iris/build/description/v2/tests/test_runtime_payload_state_integrity.py`
* `Iris/build/description/v2/tests/test_runtime_payload_state_integrity_residual_seal.py`

Runner touch boundary:

* `Iris/_docs/round3/round3_run_contract_tests.py` - do not modify if manifest-only alignment is sufficient. If modified, the change is limited to residual seal artifact consumption and must preserve current core closure count, current-route tooling allowlist, and unknown-test fail-closed behavior.

Runtime Lua and payload surfaces are read-only unless a later author-approved execution plan explicitly changes that boundary.

### Docs

Direct plan artifact:

* `docs/runtime_payload_state_integrity_residual_seal_plan.md`

Expected policy / closeout / authority packet docs:

* `docs/runtime_payload_residual_shape_contract.md`
* `docs/runtime_payload_state_residual_author_decision.md`
* `docs/runtime_payload_state_integrity_residual_seal_closeout.md`
* `docs/runtime_payload_state_integrity_residual_seal_ledger_packet.md`
* `docs/runtime_payload_state_integrity_residual_seal_roadmap_update_packet.md`
* `docs/runtime_payload_state_integrity_residual_seal_architecture_update_packet.md`
* `docs/runtime_payload_state_policy.md`
* `docs/runtime_payload_shape_contract.md`

Author-applied canonical targets, not executor-written surfaces in this plan:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Read-only authority inputs:

* `docs/Philosophy.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/runtime_payload_state_integrity_plan.md`
* `docs/runtime_payload_state_integrity_closeout.md`
* `docs/runtime_payload_state_integrity_ledger_packet.md`

### Config

* `Iris/_docs/round3/current_route_required_validations.json`

### Generated Artifacts

Preferred generated evidence root:

* `Iris/build/description/v2/staging/runtime_payload_state_integrity/residual_seal/`

Expected artifact families:

* `phase1/residual_state_regrounding_census_report.json`
* `phase1/surface_classification_matrix.json`
* `phase1/evidence_baseline_inventory.json`
* `phase1/docs_path_disposition_matrix.json`
* `phase1/canonical_forbidden_tuple_set.json`
* `phase1/protected_surface_no_mutation_precheck.json`
* `phase2/current_like_payload_shape_contract.json`
* `phase2/predecessor_residue_allowance_ledger.jsonl`
* `phase2/forbidden_tuple_scan_report.json`
* `phase2/shape_contract_consistency_report.json`
* `phase3/author_decision_coverage_packet.json`
* `phase3/branch_framing_disposition.json`
* `phase3/no_branch_external_gate_disposition.json`
* `phase3/author_decision_validation_report.json`
* `phase4/required_validation_manifest_alignment_report.json`
* `phase4/current_route_payload_residual_validation_report.json`
* `phase4/package_peer_forbidden_tuple_scan_report.json`
* `phase4/round3_runner_boundary_report.json` - required only if runner code changes
* `phase4/protected_surface_no_mutation_verdict.json`
* `phase4/cross_consumption_check.json`
* `phase5/authority_doc_alignment_report.json`
* `phase6/independent_review_packet.md`
* `phase6/independent_review_status.json`
* `phase6/header_status_update_packet.md`
* `phase6/final_residual_seal_contract_report.json`

---

## 6. Planned Changes

### Change 1 - Phase 1 Scope Lock and Residual State Re-Grounding

Purpose:

Residual Seal Round의 범위를 current payload mutation이 아니라 authority closeout으로 잠그고, current checkout 기준 residual state를 다시 census한다.

Files:

* `docs/runtime_payload_state_integrity_residual_seal_plan.md`
* `Iris/build/description/v2/staging/runtime_payload_state_integrity/residual_seal/phase1/*`

Implementation Notes:

* existing `runtime_payload_state_integrity` evidence root 산출물 목록을 작성한다.
* expected docs existence / path / disposition matrix를 작성한다: `create`, `update`, `no-op`, `missing_blocked`.
* repo root / `docs/` prefix canonical path를 확정한다.
* `phase1/canonical_forbidden_tuple_set.json`을 작성하고 이후 phase는 이 파일을 소비한다.
* live current / package peer / candidate bridge를 current-like surface로 분류한다.
* package peer payload scan availability를 확인한다. package peer scan이 실행되지 않으면 complete seal은 금지된다.
* predecessor rollback snapshot을 predecessor/historical surface로 분리한다.
* current-like collision count를 canonical forbidden tuple set 기준으로 occurrence-level 재측정한다: `unadopted + non_nil text_ko`, any `publish_state` present including `publish_state == exposed`, forbidden/unclassified state, legacy `active / silent`, dynamic renderer-visible unadopted body reach.
* predecessor rollback residue count `2`를 current-like denominator 밖에서 측정한다.
* pending state vocabulary를 작성한다: `implemented_guard_pass`, `author_decision_pending`, `review_pending`, `complete_claim_not_allowed`.
* protected source/runtime/package/rendered surface no-mutation precheck를 기록한다.

Validation:

* evidence root path exists.
* current-like collision count is `0`.
* package peer scan status is `executed`; otherwise complete seal is blocked.
* predecessor/historical residue count is exactly `2`.
* field absence / explicit `nil` / non-nil string body distinction is represented.
* predecessor residue rows are not counted as current-like violations.
* docs path disposition matrix exists and has no unresolved `missing_blocked` target required for complete seal.
* forbidden tuple set is written once and referenced by downstream phases.
* no protected surface mutation is observed during census.

---

### Change 2 - Phase 2 Current-like vs Historical Payload Shape Contract

Purpose:

`unadopted` payload의 허용 shape를 current-like 규칙과 predecessor/historical residue 규칙으로 분리한다.

Files:

* `docs/runtime_payload_residual_shape_contract.md`
* `docs/runtime_payload_shape_contract.md`
* `docs/runtime_payload_state_policy.md`
* `Iris/build/description/v2/staging/runtime_payload_state_integrity/residual_seal/phase2/*`

Implementation Notes:

* current-like surface 규칙을 명시한다.
  * `unadopted + non_nil text_ko` forbidden.
  * any current-like `publish_state` field present is forbidden, including `publish_state == exposed`.
  * `unadopted + legacy_publish_state_exposed` is forbidden because it hits the `publish_state` field-present rule.
  * `unadopted + renderer_listing_exposed + nil/missing body` is allowed unless it also hits another canonical forbidden tuple.
  * display text fields are `missing` or explicit `nil`.
  * legacy `active / silent` are forbidden current vocabulary.
* predecessor/historical surface 규칙을 명시한다.
  * residue 2건은 historical-only residue.
  * current promotion, deletion/suppression signal, quality-fail signal, publish policy signal로 승격 불가.
* `missing`, explicit `nil`, non-nil string body의 차이를 contract에 고정한다.
* `exposed` is defined as legacy `publish_state == exposed` unless the artifact explicitly says `renderer_listing_exposed`.
* renderer listing / all-item browser reach is separated from payload display body exposure.
* `quality_state` UI non-exposure와 payload shape guard의 관계를 분리한다.

Validation:

* forbidden tuple scan passes for current-like surfaces.
* the scan reports `legacy_publish_state_exposed` separately from `renderer_listing_exposed`.
* predecessor residue allowance ledger contains exactly the historical-only residues.
* contract consistency report matches Phase 1 census.
* contract text does not introduce new enum semantics, source authority, UI exposure, or renderer policy.

---

### Change 3 - Phase 3 Author Decision Coverage Capture

Purpose:

author-reserved decision coverage를 명시적으로 닫거나, 닫히지 않으면 final seal을 fail-closed한다.

Files:

* `docs/runtime_payload_state_residual_author_decision.md`
* `Iris/build/description/v2/staging/runtime_payload_state_integrity/residual_seal/phase3/*`

Implementation Notes:

* Branch A / Branch B labels are retained only as framing labels for the two required decision dimensions:
  * Branch A framing: `current_like_forbid_boundary` - author explicitly adopts the canonical current-like forbidden tuple set as the seal boundary. Any current-like violation blocks complete seal.
  * Branch B framing: `historical_residue_preservation_boundary` - author explicitly preserves the predecessor rollback residue 2건 as historical-only residue while keeping all current-like forbidden tuple rules intact.
  * no-branch framing: `no_branch_external_gate` - author declines residual boundary seal for now. This records defer / external gate status and cannot be treated as complete seal.
* complete seal uses the author decision coverage booleans as the predicate, not a mutually exclusive branch label.
* complete seal requires a single candidate decision frame:

```text
selected_author_decision = residual_boundary_seal
author_decision_coverage.current_like_forbid_boundary == adopted
author_decision_coverage.historical_residue_preservation_boundary == adopted
author_decision_coverage.no_branch_external_gate == false
author_decision_coverage.runtime_mutation_allowed == false
```

* `selected_author_decision = no_branch_external_gate` always forbids `complete_residual_seal`.
* Codex and tooling may not introduce new branch labels, broaden these coverage meanings, or convert any coverage dimension into a runtime mutation plan.
* if any author decision coverage requires runtime/source/rendered/chunk mutation, this plan must close as `revised_plan_needed`.
* each framing label records meaning, adoption condition, disposition, and runtime mutation boundary.
* decision packet includes `decision_owner=author`.
* decision packet includes `selected_author_decision` only when author decision exists.
* decision packet includes `author_decision_coverage` with the four required fields above.
* framing dispositions remain as predecessor trace.

Validation:

* author decision packet exists.
* `decision_owner=author` exists.
* `selected_author_decision == residual_boundary_seal` for complete seal.
* `author_decision_coverage.current_like_forbid_boundary == adopted`.
* `author_decision_coverage.historical_residue_preservation_boundary == adopted`.
* `author_decision_coverage.no_branch_external_gate == false`.
* `author_decision_coverage.runtime_mutation_allowed == false`.
* `selected_author_decision == no_branch_external_gate` forbids complete seal.
* author decision absence blocks complete seal.
* Branch A / Branch B framing dispositions exist.

---

### Change 4 - Phase 4 Validator / Evidence / Required Validation Manifest Alignment

Purpose:

validator, evidence report, authority-doc packets, and Round 3 required validation manifest consume the same residual seal boundary.

Files:

* `Iris/build/description/v2/tools/build/runtime_payload_state_integrity.py`
* `Iris/build/description/v2/tests/test_runtime_payload_state_integrity.py`
* `Iris/build/description/v2/tests/test_runtime_payload_state_integrity_residual_seal.py`
* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/build/description/v2/staging/runtime_payload_state_integrity/residual_seal/phase4/*`

Implementation Notes:

* focused residual seal tests are added or existing focused tests are extended.
* current-like guard pass and predecessor residue preservation are separate validation families.
* required validation manifest distinguishes implemented guard pass from complete residual seal.
* static current-like collision count, dynamic renderer-visible reach, package peer payload scan, and historical residue census are separate gates.
* dynamic renderer-visible reach report schema must name its denominator, input surfaces, and row identity keys.
* forbidden tuple collision count and historical residue census are occurrence-level measurements.
* protected source/runtime/package/rendered no-mutation verdict is hash-level measurement.
* package peer forbidden tuple scan is mandatory for complete seal. Full package build is a separate regression route and cannot substitute for package peer payload scan.
* protected source/runtime/package/rendered surface hash-level no-mutation verdict is generated.
* manifest-only alignment is preferred. Runner code changes are allowed only when required for residual seal artifact consumption.
* if `round3_run_contract_tests.py` changes, generate `phase4/round3_runner_boundary_report.json` proving current core closure count, tooling allowlist, and unknown-test fail-closed behavior were not expanded.
* broad current-route failure must route to source facts / overlay completeness correction scope, not runtime payload policy bypass.

Validation:

* focused residual seal tests pass.
* current route required validation run passes.
* package peer forbidden current-like surface scan runs and records `executed`.
* if package peer scan status is `unavailable_blocked` or `not_applicable_with_reason`, complete seal is forbidden.
* full package build status is recorded separately from package peer scan status.
* `static_forbidden_current_count == 0`.
* `dynamic_renderer_visible_reach == 0`.
* dynamic renderer-visible reach report includes denominator and input-surface metadata.
* `historical_residue_count == 2`.
* `changed_count == 0` for protected no-mutation verdict unless an explicitly approved later branch changes the scope.
* occurrence-level measurement and hash-level measurement are both present and not conflated.
* `round3_runner_boundary_report.json` exists if runner code changes.
* artifact schema validation passes.

---

### Change 5 - Phase 5 Authority Docs Packet and Ledger Reflection

Purpose:

policy, shape contract, DECISIONS ledger packet, ROADMAP packet, and ARCHITECTURE packet read the same residual seal boundary. Canonical top-doc edits remain author-applied targets.

Files:

* `docs/runtime_payload_state_integrity_residual_seal_closeout.md`
* `docs/runtime_payload_state_integrity_residual_seal_ledger_packet.md`
* `docs/runtime_payload_state_integrity_residual_seal_roadmap_update_packet.md`
* `docs/runtime_payload_state_integrity_residual_seal_architecture_update_packet.md`
* `docs/DECISIONS.md` - author-applied target only
* `docs/ARCHITECTURE.md` - author-applied target only
* `docs/ROADMAP.md` - author-applied target only
* `Iris/build/description/v2/staging/runtime_payload_state_integrity/residual_seal/phase5/*`

Implementation Notes:

* predecessor rollback residue 2건 is recorded as historical-only residue, not current debt.
* implemented guard pass and complete seal are separate lifecycle states.
* closeout wording includes release/package/Workshop/B42/deployment/manual QA/public text quality non-claims.
* executor writes staging update packets only.
* canonical `DECISIONS.md`, `ARCHITECTURE.md`, and `ROADMAP.md` reflection is labeled `author_applied_target`.
* authority docs packet must be additive or superseding, not history rewrite.
* DECISIONS compact ledger rules are respected by using `ledger packet first, top-doc patch second`.

Validation:

* docs token scan finds no current allowance wording for `unadopted + text_ko`.
* docs token scan finds no current allowance wording for legacy `publish_state == exposed`.
* docs token scan does not conflate `renderer_listing_exposed + nil/missing body` with legacy `publish_state == exposed`.
* docs token scan finds no current `active / silent` vocabulary restoration.
* docs token scan finds no `quality_state` UI exposure.
* ledger packet claim-boundary check passes.
* author-applied target labels exist for canonical docs.
* no executor-written canonical doc mutation is required for plan completion.
* authority doc alignment report passes.

---

### Change 6 - Phase 6 Independent Review Gate and Final Closeout

Purpose:

complete seal을 승인하거나, independent review 미완료를 explicit external gate로 봉인한다.

Files:

* `Iris/build/description/v2/staging/runtime_payload_state_integrity/residual_seal/phase6/independent_review_packet.md`
* `Iris/build/description/v2/staging/runtime_payload_state_integrity/residual_seal/phase6/independent_review_status.json`
* `Iris/build/description/v2/staging/runtime_payload_state_integrity/residual_seal/phase6/final_residual_seal_contract_report.json`
* `docs/runtime_payload_state_integrity_residual_seal_closeout.md`

Implementation Notes:

* independent review packet lists minimum review items.
* reviewer independence and certification ceiling are disclosed with fields:
  * `reviewer_not_plan_author`
  * `reviewer_not_executor`
  * `review_scope`
  * `certification_ceiling`
  * `reviewer_conflict_disclosure`
  * `plan_template_checked`
  * `execution_contract_checked`
* review complete and external gate terminal are separate.
* if review is pending, current implementation blocker remains false.
* final closeout status uses machine-readable vocabulary: `implemented_guard_pass`, `author_decision_sealed`, `independent_review_pending_external_gate`, `independent_review_complete`, `complete_residual_seal`, `complete_claim_not_allowed`.
* if status changes to `complete_residual_seal`, generate `phase6/header_status_update_packet.md` so the plan header/status transition is traceable without editing history silently.

Validation:

* review packet schema validation passes.
* reviewer qualification fields are present.
* if `PLAN_TEMPLATE.md` or `EXECUTION_CONTRACT.md` was not checked by the final reviewer, the final status records a certification ceiling instead of silently claiming full certification.
* chain-internal review is not counted as independent verification.
* final status validation matches review state.
* complete claim allowed predicate is false without independent review completion.
* current implementation blocker predicate remains false when only review is pending.
* no-mutation final verification passes.

---

## 7. Validation Plan

### Automated Validation

Do not claim validation passed unless the exact relevant command exits with code 0.

Required validation families:

* residual state census validation
* canonical current-like forbidden tuple scan
* predecessor/historical residue classification
* field absence / explicit `nil` / non-nil body distinction validation
* artifact schema validation
* focused residual seal unit tests as authoritative residual gate
* Round 3 current route required validation / current route closure as authoritative route gate
* package peer payload forbidden tuple scan as mandatory current-like denominator gate
* full package build as separate regression route, if in scope
* current-like dynamic renderer-visible reach scan
* protected source/runtime/package/rendered surface no-mutation verdict
* required validation manifest alignment
* Round 3 runner boundary report validation, if runner code changes
* docs claim-boundary scan
* independent review status validation

Exact command candidates:

```powershell
python -B -m unittest Iris.build.description.v2.tests.test_runtime_payload_state_integrity
python -B -m unittest Iris.build.description.v2.tests.test_runtime_payload_state_integrity_residual_seal
python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Package peer payload scan is mandatory for complete seal and must be pinned by Phase 4. Full package build is separate:

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean -Zip
```

Full `test_*.py` discovery may be run as supplemental regression evidence, but it is not the authoritative residual seal gate. Pre-existing full-discovery failure is neither residual pass evidence nor residual blocker. A new discovery failure caused by residual seal changes remains fail-loud and must be recorded separately.

The residual seal validator command must be pinned by Phase 4. If the validator tool is missing, validation is blocked, not passed.

### Manual Validation

* author reviews and selects `residual_boundary_seal` or records `no_branch_external_gate`.
* author confirms `author_decision_coverage.current_like_forbid_boundary == adopted`.
* author confirms `author_decision_coverage.historical_residue_preservation_boundary == adopted`.
* author confirms `author_decision_coverage.no_branch_external_gate == false` before complete seal.
* author confirms `author_decision_coverage.runtime_mutation_allowed == false`.
* author confirms Branch A / Branch B framing labels were not broadened by Codex or tooling.
* reviewer confirms predecessor residue 2건 are historical-only and not current debt.
* reviewer confirms docs / validator / manifest use the same boundary language.
* reviewer confirms package peer payload scan executed or complete seal is blocked.
* reviewer confirms canonical docs are author-applied targets and executor output is packet-only.
* reviewer confirms any Round 3 runner change stayed within residual seal artifact consumption.
* reviewer confirms no release, package, Workshop, B42, deployment, manual QA, or public text quality readiness claim is present.
* independent reviewer confirms complete seal or records external gate pending.

### Validation Limits

This plan will not perform:

* multiplayer validation
* deployment validation
* long-session runtime validation
* manual in-game QA
* package release readiness validation
* Workshop validation
* B42 compatibility sweep
* external ecosystem compatibility sweep
* public-facing text quality review
* semantic quality review
* rendered text rewrite validation
* runtime equivalence beyond payload-shape guard
* source coverage re-audit
* full vNext baseline migration reopen
* successor baseline / cutover / consumer migration re-execution

---

## 8. Risk Surface Touch

### Authority Surface

Touched.

This round seals the decision authority for current-like forbidden payload shape and predecessor/historical residue preservation. It does not change source authority or runtime authority.

### Runtime Behavior Surface

None by default.

Runtime Lua remains a sealed payload renderer. Any proposed runtime behavior change is out of scope for this plan.

### Compatibility Surface

No runtime/package behavior change is expected.

There is conditional fail-loud risk if any consumer incorrectly treats predecessor residue as current-like surface. That risk is intentional validation behavior, not compatibility policy change.

Package peer payload scan coverage is mandatory for complete seal. Full package build failure may be reported separately, but it does not excuse missing package peer scan coverage.

### Sealed Artifact Surface

Touched.

New residual seal artifacts, validation reports, review packets, closeout, and ledger packets are created. Existing guard artifacts are consumed as predecessor/current-readpoint evidence and are not rewritten.

### Public-Facing Output Surface

None.

This round does not change tooltip, Browser, Wiki, rendered text, badges, sorting, filtering, recommendation, confidence, or quality display.

---

## 9. Risk Analysis

### Architecture Risk

* predecessor rollback residue may be reclassified as current runtime debt.
* historical-only allowance may be written as current-like allowance.
* author decision may be replaced by tooling convenience.
* independent review pending may be confused with current implementation failure.
* residual seal may smuggle new enum semantics, source authority, UI exposure, or renderer policy.
* canonical docs may be silently promoted by executor-written edits instead of author-applied packets.
* branch option semantics may drift beyond the seed meanings in this plan.
* Branch A or Branch B framing may be mistaken for a sufficient complete-seal decision by itself.
* no-branch may be mistaken for complete-seal eligible instead of external gate / defer.

### Runtime Risk

* runtime Lua may be modified to compensate for a build-time authority issue.
* current-like scan may accidentally consume predecessor rollback snapshot.
* dynamic renderer reach scan may treat `nil` / missing / non-nil body as the same state.
* `renderer_listing_exposed` may be confused with legacy `publish_state == exposed`.

### Compatibility Risk

* package/current route may fail loud if stale predecessor payload is exposed through a current-looking surface.
* manifest alignment may break if implemented guard pass and complete residual seal are represented as the same status.
* package peer payload scan may be skipped or confused with full package build.
* Round 3 runner changes may expand current core closure, tooling allowlist, or unknown-test handling if not bounded.

### Regression Risk

* residue count may drift from `2` and be force-fit instead of blocking.
* current-like collision count may drift from `0` and be papered over.
* docs and validator may diverge after one side is updated.
* occurrence-level collision measurement may be weakened into path-level presence checks.
* closeout wording may overclaim release readiness or public text quality acceptance.

---

## 10. Rollback Plan

Rollback is artifact-level and authority-doc-level.

* New residual seal docs can be reverted or superseded by a later blocked / invalidated closeout.
* Required validation manifest changes can be reverted if the alignment report proves incorrect.
* Focused residual tests can be removed, quarantined, or superseded if their surface classification is wrong.
* Residual seal evidence can be marked stale or invalidated under the staging root.
* Incorrect author decision packet must be replaced by an `invalidated_author_decision` record and complete seal must be forbidden until a new decision exists.
* Scope-breaking review must be invalidated and independent review returned to external gate pending.
* No rollback path may mutate runtime chunks, package chunks, source facts, source decisions, or rendered output under this plan.
* Existing Runtime Payload State Integrity Guard pass remains predecessor/current readpoint evidence unless explicitly superseded.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance must be preserved.
* Hub & Spoke + SPI boundaries remain unchanged.
* Iris runtime remains Lua-only render surface, not runtime analysis / repair / policy engine.
* Runtime / build-time separation must be preserved.
* Runtime Lua must not compose, repair, validate source, normalize state, judge semantic quality, or judge publish policy.
* Source facts / decisions / rendered text / runtime Lua / packaged Lua / bridge payload mutation is forbidden in this plan.
* `adopted / unadopted` remains current enum and must not become quality, publish, deletion, or suppression vocabulary.
* Legacy `active / silent` must not return as current writer / validator / runtime vocabulary.
* Legacy `publish_state == exposed` must not be confused with renderer listing reach.
* `quality_state` must not be exposed in UI or consumed as visibility, sorting, filtering, recommendation, trust, or confidence signal.
* Predecessor rollback residue must remain historical evidence only.
* Author-reserved decision must not be bypassed by Codex, tooling, validator output, or review text.
* Branch A / Branch B / no-branch semantics are fixed by this plan's seed definitions and cannot be broadened during execution.
* Complete seal requires `selected_author_decision == residual_boundary_seal`.
* Complete seal requires both author decision coverage axes adopted: current-like forbidden boundary and historical residue preservation boundary.
* `no_branch_external_gate == true` forbids complete seal.
* Independent review is required for complete seal.
* Review pending is not a current runtime blocker.
* Round 3 required validation manifest must remain fail-closed.
* Round 3 runner changes must be avoided when manifest-only alignment is enough.
* Any Round 3 runner change must preserve current core closure count, current-route tooling allowlist, and unknown-test fail-closed behavior.
* Package peer payload scan is mandatory for complete seal.
* Full package build does not substitute for package peer payload scan.
* Focused residual seal test and Round 3 current route closure are authoritative residual gates; full discovery is supplemental unless a new failure is caused by this round.
* Monolith fallback, stale bridge, and legacy payload shape re-entry remain forbidden.
* Executor output for canonical docs is limited to staging update packets. Canonical docs reflection is author-applied.
* Authority docs packets must be additive or superseding, not silent rewrite of predecessor traces.
* Occurrence-level granularity must be preserved.
* Collision/residue counts are occurrence-level measurements; no-mutation verdict is hash-level measurement.
* Complete closeout must not claim release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA completion, or public-facing text quality acceptance.

---

## 12. Expected Closeout State

Expected closeout target is conditional.

`complete_residual_seal` is allowed only when all conditions below are true:

* current-like and predecessor/historical surfaces are classified.
* canonical forbidden tuple set is consumed consistently by Phase 1 census, Phase 2 contract, Phase 4 validator, and final closeout.
* current-like `unadopted + non_nil text_ko`, any current-like `publish_state` present including `publish_state == exposed`, forbidden/unclassified state, legacy `active / silent`, and dynamic renderer-visible `unadopted` body reach are forbidden and validated.
* `renderer_listing_exposed + nil/missing body` is not misclassified as legacy `publish_state == exposed`.
* predecessor rollback residue count `2` is preserved as historical-only residue.
* `selected_author_decision == residual_boundary_seal`.
* `author_decision_coverage.current_like_forbid_boundary == adopted`.
* `author_decision_coverage.historical_residue_preservation_boundary == adopted`.
* `author_decision_coverage.no_branch_external_gate == false`.
* `author_decision_coverage.runtime_mutation_allowed == false`.
* Branch A and Branch B framing dispositions exist, but neither framing alone is sufficient for complete seal.
* validator, evidence, authority-doc packets, and required validation manifest consume the same boundary.
* current-like collision count is `0`.
* package peer payload scan is executed and included in the current-like denominator.
* historical residue count is `2`.
* collision/residue counts are occurrence-level.
* protected source/runtime/package/rendered surface no-mutation is verified.
* no-mutation verdict is hash-level.
* canonical docs reflection is represented as author-applied update packets, not executor-written silent promotion.
* Round 3 runner is unchanged, or `round3_runner_boundary_report.json` proves the change was limited to residual seal artifact consumption.
* focused residual seal test and Round 3 current route closure pass as authoritative gates.
* full discovery, if run, is classified as supplemental regression evidence unless a new failure is caused by this round.
* independent review approves complete seal.
* independent review packet includes `reviewer_not_plan_author`, `reviewer_not_executor`, `review_scope`, `certification_ceiling`, `reviewer_conflict_disclosure`, `plan_template_checked`, and `execution_contract_checked`.
* if final status changes to `complete_residual_seal`, `phase6/header_status_update_packet.md` exists.
* final closeout includes release/package/Workshop/B42/deployment/manual QA/public text quality non-claims.

If author decision is missing, expected closeout is `author_decision_pending`, not complete.

If only one of `current_like_forbid_boundary` or `historical_residue_preservation_boundary` is adopted, expected closeout is `author_decision_pending` or `partial`, not complete.

If `selected_author_decision == no_branch_external_gate` or `author_decision_coverage.no_branch_external_gate == true`, expected closeout is `author_decision_pending` or `independent_review_pending_external_gate`, not complete.

If independent review is missing but implementation and author decision are otherwise sealed, expected closeout is `independent_review_pending_external_gate`, not complete.

If package peer payload scan is missing, expected closeout is `blocked` or `external_gate_pending`, not complete.

If canonical docs were edited directly by executor without author-applied target confirmation, expected closeout is `blocked`, not complete.

If Branch A / Branch B / no-branch semantics require runtime/source/rendered/chunk mutation, expected closeout is `revised_plan_needed`, not complete.

If validation fails or artifact paths cannot be produced, expected closeout is `blocked` or `implemented_only` depending on whether implementation exists.

If Phase 1 evidence contradicts assumed counts, expected closeout is `revised_plan_needed` or `blocked`, not forced success.
