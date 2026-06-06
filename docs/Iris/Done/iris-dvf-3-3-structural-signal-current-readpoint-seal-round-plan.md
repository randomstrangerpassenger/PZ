# Iris DVF 3-3 Structural Signal Current Readpoint Seal Round Plan

> 상태: Draft v0.3-minor-review-applied
> 기준일: 2026-05-29
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> authority input: `ROADMAP - Iris DVF 3-3 Structural Signal Disposition / Current Readpoint Seal Round` (2026-05-29 user-provided synthesis)
> review input: `REVIEW - Iris DVF 3-3 Structural Signal Current Readpoint Seal Round Plan` (2026-05-29 user-provided synthesis), WARN required revisions applied in v0.2; second review PASS-with-minor-revisions clarifications applied in v0.3
> 직접 상위 readpoint:
> - 2026-04-29 publish writer authority / `FUNCTION_NARROW` and `ACQ_DOMINANT` blanket isolation forbidden seal
> - 2026-05-26 historical runtime vocabulary readpoint anchor
> - 2026-05-28 Branch B reconstructed structural observer authority
> - 2026-05-29 structural signal scope split seal
> - 2026-05-29 structural signal authority classification seal
> 계획 형식: `docs/PLAN_TEMPLATE.md`
> contract vocabulary: `docs/EXECUTION_CONTRACT.md` closeout states are `complete`, `partial`, `implemented_only`, and `blocked`
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`. The template is an execution-plan form only and does not create semantic authority over `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md`.
> 실행 상태: planning authority only. This document opens no runtime rollout, source mutation, rendered text mutation, Lua mutation, `quality_state`, `publish_state`, `runtime_state`, deployment, release, or closeout claim.

---

## 1. Objective

이번 execution plan의 목적은 structural signal occurrence가 publish writer authority로 오독되지 않도록 current readpoint를 문서 권위면에서 봉인하거나, 이미 충분히 봉인된 상태라면 no-op evidence closeout으로 닫는 것이다.

이 round의 공식 명칭과 id는 다음으로 제한한다.

```text
Structural Signal Current Readpoint Seal Round
structural_signal_current_readpoint_seal_round
```

이 명칭은 structural signal disposition completion을 뜻하지 않는다. `Disposition`은 source roadmap의 문제 배경으로만 읽고, round title, round id, artifact root, closeout label에는 사용하지 않는다.

핵심 질문:

```text
current repo evidence 기준 structural signal current readpoint가 이미 live canonical surface에 충분히 반영되어 있는가,
아니면 이미 봉인된 readpoint를 docs-only로 흡수해야 하는가,
아니면 sealed evidence를 소비할 수 없어 evidence-reconstruction-only path가 필요한가?
```

Phase 0은 반드시 다음 branch 중 하나를 evidence로 결정한다. 기본값은 없다.

```text
blocked_conflicting_authority
already_closed_noop
doc_absorption_only
new_execution_required
```

Branch precedence:

```text
1. sealed/current authority conflict exists
   -> blocked_conflicting_authority

2. current canonical surfaces already contain the same readpoint without contradiction
   -> already_closed_noop

3. sealed closeout exists and is consumable, but live canonical surfaces are silent or incomplete
   -> doc_absorption_only

4. sealed closeout is absent / insufficient / unsafe
   -> new_execution_required
```

Round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_current_readpoint_seal_round/
```

Success may claim only the branch-specific evidence-bounded result. The strongest intended `doc_absorption_only` claim is:

```text
이미 봉인된 structural-signal observer/readpoint authority가 live canonical document surface에 additive로 승격되었고, top-doc / architecture / roadmap / decision ledger 사이의 readpoint wording이 정합되었다. 이 승격은 source/rendered/runtime/state mutation을 포함하지 않으며, ACQ_DOMINANT remeasurement와 publish mutation review는 별도 explicit round 없이는 열리지 않는다.
```

Success must not claim:

```text
structural signal disposition completion
ACQ_DOMINANT current-baseline remeasurement completion
ACQ_DOMINANT disposition completion
publish mutation review completion
FUNCTION_NARROW second rollout
source expansion
runtime equivalence
manual in-game QA
runtime rollout
deployment
Workshop readiness
release readiness
ready_for_release
```

---

## 2. Scope

This is a governance/document-readpoint execution plan with a mandatory Phase 0 branch decision. It may create round-local evidence artifacts and may perform additive document updates only after the hard gate for the chosen branch passes.

Branch map:

```text
Branch D: blocked_conflicting_authority
Branch C: already_closed_noop
Branch A: doc_absorption_only
Branch B: new_execution_required
```

In scope:

* Phase 0 opening authority check, current surface presence check, canonical surface equivalence check, duplicate-update prevention check, and predecessor disambiguation.
* Branch C `already_closed_noop` equivalence evidence and no-op closeout if live canonical surfaces already contain the current readpoint.
* Branch A `doc_absorption_only` readpoint draft, live current-authority surface inventory, hard gate, adversarial review, gated promotion, and closeout.
* Branch B `new_execution_required` evidence-reconstruction-only inventory/classification if sealed evidence cannot be consumed. Branch B is not a reopening of the sealed 2026-05-29 authority classification decision.
* Branch D `blocked_conflicting_authority` conflict report if sealed/current authorities conflict or current evidence cannot safely support no-op, promotion, or evidence reconstruction.
* Additive updates to `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, and `docs/DECISIONS.md` only if Branch A requires live canonical surface alignment and the hard gate passes.
* Round-local reports proving touched files and non-mutation posture for source/rendered/runtime/state surfaces.

Allowed live-doc insertion points for Branch A:

```text
docs/ARCHITECTURE.md 9-2: append a structural signal observer/readpoint subsection if equivalent wording is absent
docs/ARCHITECTURE.md fallback: if 9-2 is absent or structurally moved, use the equivalent current architecture readpoint location
docs/ROADMAP.md #5 Iris: append a current canonical summary line if equivalent wording is absent
docs/ROADMAP.md ledger: append a provenance pointer only if needed
docs/DECISIONS.md: append a new dated section only after duplicate-update prevention passes
```

### Explicitly Out Of Scope

* `FUNCTION_NARROW` second rollout.
* `FUNCTION_NARROW` re-disposition.
* `ACQ_DOMINANT` current-baseline remeasurement.
* `ACQ_DOMINANT` disposition completion.
* Publish mutation review.
* Source expansion.
* Source facts mutation.
* Source decisions mutation.
* Rendered text regeneration as an adopted output.
* Runtime Lua regeneration.
* Packaged Lua redeployment.
* Browser / Wiki / Tooltip behavior change.
* New machine-enforced guard, validator, or linter rule.
* Manual in-game QA.
* Runtime rollout.
* Deployment closeout.
* Workshop readiness.
* Release readiness.
* `ready_for_release`.
* Repo-wide lexical zero claim.
* Structural signal token removal as cleanup.
* Full runtime equivalence claim.
* Full compatibility preservation claim.
* Historical sealed body, staging body, Done walkthrough, diagnostic/test fixture, or dated sealed decision body rewrite.

---

## 3. Non-Goals

This plan does not attempt to:

* Reopen `FUNCTION_NARROW` / `ACQ_DOMINANT` blanket isolation.
* Treat structural signal occurrence count as mutation pressure.
* Promote old structural count/report artifacts directly to current authority.
* Convert observer/readpoint/report/preview/diagnostic/test/historical occurrences into publish writer inputs.
* Rejudge semantic correctness or publish disposition from structural signal token presence.
* Perform `ACQ_DOMINANT` publish candidacy evaluation before current-baseline remeasurement.
* Reopen or supersede the sealed 2026-05-29 structural signal authority classification decision.
* Rewrite historical sealed bodies, fixtures, staging bodies, Done docs, or dated decision bodies.
* Relax existing fail-loud guards.
* Create new publish/write authority.
* Change user-facing Iris output, tooltip output, wiki behavior, or runtime behavior.

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` remains the top authority. Iris remains a 100% Lua wiki-style information module and must not become a recommendation, comparison, or gameplay-policy system.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are the current governance readpoints at execution start.
* Runtime/build-time separation remains intact. Offline Python pipeline authority remains separate from runtime Lua render/consume-only surfaces.
* The 2026-04-29 publish-writer seal remains in force: publish writer authority is layer/position correctness, not semantic strength alone.
* `FUNCTION_NARROW` / `ACQ_DOMINANT` blanket isolation reopen remains forbidden.
* `ACQ_DOMINANT` remains non-candidate for publish mutation before a separately opened current-baseline remeasurement round.
* Publish mutation review remains closed unless a separate explicit opening decision opens it.
* The 2026-05-28 Branch B reconstructed structural observer authority is consume-only unless Phase 0 finds conflicting current authority.
* The 2026-05-29 scope split and authority classification closeouts are read-only input candidates, not automatic proof, until Phase 0 confirms their current evidence paths and wording compatibility.

Branch assumptions:

* `already_closed_noop` is valid only if `current_surface_presence_report.json` and `canonical_surface_equivalence_report.json` show equivalent current readpoint wording on live canonical surfaces and no live current-authority contradiction.
* `doc_absorption_only` is valid only if existing sealed closeout artifacts are present, parseable, current-consumable, and live canonical surfaces are silent or incomplete.
* `new_execution_required` is valid only if existing closeout evidence is absent, insufficient, or unsafe to consume. This branch reconstructs evidence for the current readpoint; it does not reopen the sealed 2026-05-29 decision as a policy matter.
* `blocked_conflicting_authority` is required if sealed/current authorities conflict, old reports have been promoted as current authority, or the round cannot close without source/rendered/runtime/state mutation.

Path assumptions:

* Repository paths in this plan are rooted at `C:\Users\MW\Downloads\coding\PZ`.
* The plan artifact location follows the current repository's Iris plan-file convention. Its location is not evidence that the round has already executed or closed.
* Execution must verify that `docs/PLAN_TEMPLATE.md` is still the sanctioned execution-plan form for this repository context. If a higher-priority current template or contract supersedes it, the plan must be restated in that approved form before execution.

---

## 5. Repository Areas Affected

### Code

None intended.

### Docs

Potentially affected after Branch A hard gate:

* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/DECISIONS.md`

Plan artifact:

* `docs/Iris/Done/iris-dvf-3-3-structural-signal-current-readpoint-seal-round-plan.md`

### Config

None intended.

### Generated Artifacts

Round-local evidence artifacts may be created under:

* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_current_readpoint_seal_round/`

No generated runtime artifact is an intended final output.

---

## 6. Planned Changes

### Change 1

Purpose:

Decide the execution branch by checking current authority, current canonical surface presence, equivalence, duplicate-update risk, predecessor closeouts, and conflict conditions.

Files:

* round-local `phase0_opening_authority_check.json`
* round-local `phase0_authority_inputs.json`
* round-local `phase0_existing_closeout_inventory.json`
* round-local `current_surface_presence_report.json`
* round-local `canonical_surface_equivalence_report.json`
* round-local `duplicate_update_prevention_report.json`
* round-local `template_contract_attestation.json`
* round-local `phase0_branch_decision.json`
* round-local `branch_decision_reason.json`

Implementation Notes:

* Inspect `docs/DECISIONS.md`, `docs/ARCHITECTURE.md 9-2`, and `docs/ROADMAP.md #5 Iris` as live current-authority surfaces.
* Verify the presence and consumability of the 2026-04-29, 2026-05-26, 2026-05-28, and 2026-05-29 predecessor evidence paths.
* Apply branch precedence exactly as listed in Section 1.
* Do not perform remeasurement, publish mutation review, or authority reclassification before this branch decision is written.
* Do not add duplicate live-doc readpoint content if `canonical_surface_equivalence_report.json` shows exact wording or semantic-equivalent current readpoint content already exists.
* Duplicate-prevention blocks duplicate readpoint content, but does not suppress this round's own promotion/noop closeout record.
* Prior 2026-05-29 scope split or authority classification closeout entries alone do not make this round's promotion/noop closeout record duplicate.
* Verify `docs/PLAN_TEMPLATE.md` and `docs/EXECUTION_CONTRACT.md` are still the applicable plan/closeout vocabulary sources before execution.

Validation:

* Top-doc grep with explicit path list.
* Existing closeout artifact path existence check.
* Sealed input hash/presence check where hash manifests exist.
* JSON parse validation for Phase 0 reports.
* Branch reason recorded.
* Duplicate-update prevention report recorded.
* Template/contract attestation recorded.

---

### Change 2

Purpose:

For `already_closed_noop`, close without live-doc mutation when equivalent current readpoint wording already exists.

Files:

* round-local `noop_current_surface_equivalence_report.json`
* round-local `noop_duplicate_update_prevention_report.json`
* round-local `noop_closeout.json`
* round-local `noop_closeout.md`

Implementation Notes:

* `already_closed_noop` is not "no evidence." It must show that live current-authority surfaces already contain the current readpoint.
* The closeout state remains `complete` only if `docs/EXECUTION_CONTRACT.md` requirements are satisfied, with a branch sublabel of `complete_with_noop_evidence` or human-readable wording `noop evidence closeout`.
* Do not touch `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, or `docs/DECISIONS.md`.
* Record which exact surfaces carry equivalent wording and why additional live-doc entries would be duplicates.
* Record that this round's own noop closeout record is not suppressed merely because prior 2026-05-29 scope split or authority classification closeout entries exist.

Validation:

* `git diff --name-only` for this branch must show only round-local artifacts, if any.
* No live-doc update allowed.
* Closeout JSON parse.
* Non-claim checklist pass.
* `complete_with_noop_evidence` sublabel or `noop evidence closeout` wording present when closing as `complete`.

---

### Change 3

Purpose:

For `doc_absorption_only`, draft a canonical readpoint statement without redeciding sealed facts.

Files:

* round-local `phaseA1_structural_signal_current_readpoint_draft.md`
* round-local `phaseA1_clause_source_crosscheck.json`

Implementation Notes:

* State that structural signal occurrence is not publish / quality / runtime writer input.
* State that `FUNCTION_NARROW` residual is report/preview structural flag only.
* State that `ACQ_DOMINANT` is not a publish mutation candidate before separate current-baseline remeasurement.
* Keep historical, diagnostic, report, preview, and test occurrences in non-mutation authority classes.
* Avoid wording that sounds like new publish/write authority or full disposition completion.

Validation:

* Clause-to-source crosscheck.
* No new publish/write authority wording.
* No `ACQ_DOMINANT` remeasurement wording.
* No publish mutation review wording.
* Explicit non-claim: `This does not complete structural signal disposition.`

---

### Change 4

Purpose:

For `doc_absorption_only`, inventory cross-document wording and identify live current-authority surfaces that are silent or incomplete.

Files:

* round-local `phaseA2_cross_doc_readpoint_inventory.jsonl`
* round-local `phaseA2_consistency_matrix.json`
* round-local `phaseA2_silent_canonical_surface_report.json`
* round-local `phaseA2_contradiction_scope_report.json`

Implementation Notes:

* Classify each relevant location as `consistent`, `silent`, `contradictory`, or `historical_provenance`.
* `contradiction_count` applies only to live current-authority surfaces:

```text
docs/DECISIONS.md current readpoint entries
docs/ARCHITECTURE.md 9-2 current readpoints
docs/ROADMAP.md #5 Iris current canonical summary
```

* Historical/provenance bodies, staging bodies, Done walkthroughs, diagnostic fixtures, test fixtures, and old report artifacts are not counted as contradictions unless they are currently presented as live authority.
* Include relevant `docs/Iris/Done/*` plans/walkthroughs and predecessor artifacts as provenance inventory, not contradiction-count targets by default.
* If a live current-authority contradiction exists, do not rewrite sealed bodies; choose `blocked_conflicting_authority` or flag additive clarification only if the branch remains safe.

Validation:

* Inventory completeness check.
* Live current-authority `contradiction_count = 0` required for Branch A promotion.
* Historical/provenance contradiction exclusion documented.
* `silent` live canonical surfaces converted into projected additive updates only after hard gate.

---

### Change 5

Purpose:

Run duplicate-doc guard, docs-only non-mutation gate, hard gate, and adversarial review before any live-doc promotion.

Files:

* round-local `phaseA3_hard_gate_report.json`
* round-local `phaseA3_duplicate_doc_guard_report.json`
* round-local `touched_files_docs_only_report.json`
* round-local `source_rendered_runtime_hash_diff_report.json` if validation commands are run
* round-local `validation_side_effect_restore_report.json` if validation commands change generated output
* round-local `phaseA4_adversarial_review.md`

Implementation Notes:

* Confirm sealed inputs are unchanged.
* Confirm no `ACQ_DOMINANT` remeasurement, publish mutation review, `FUNCTION_NARROW` second rollout, or blanket isolation reopen occurred.
* Confirm source facts, source decisions, rendered text, runtime Lua, packaged Lua, `quality_state`, `publish_state`, and `runtime_state` are not intended mutation targets.
* If validation commands are run and generate side effects, restore side effects and record the restoration report before any non-mutation claim.
* Review projected wording for claim overreach.

Validation:

* Hard gate `all_gates_pass = true`.
* Adversarial review verdict `PASS`.
* Additive-only projection review.
* Duplicate-doc guard pass.
* Duplicate-doc guard checks exact wording and semantic-equivalent current readpoints.
* Docs-only touched-files gate:

```text
Allowed for Branch A after promotion:
docs/ARCHITECTURE.md
docs/ROADMAP.md
docs/DECISIONS.md
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_current_readpoint_seal_round/*

Allowed for Branch C:
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_current_readpoint_seal_round/*
```

---

### Change 6

Purpose:

For `doc_absorption_only`, promote the readpoint to live canonical surfaces only after Change 5 passes.

Files:

* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/DECISIONS.md`
* round-local `phaseA5_doc_sync_manifest.json`
* round-local `phaseA5_authority_phrase_consistency_report.json`

Implementation Notes:

* Add a structural signal observer/readpoint subsection to `ARCHITECTURE.md 9-2` only if equivalent wording is absent.
* If `ARCHITECTURE.md 9-2` is absent or moved, add the subsection to the equivalent current architecture readpoint location and record the fallback in `phaseA5_doc_sync_manifest.json`.
* Add a current canonical Iris summary line to `ROADMAP.md #5 Iris` only if equivalent wording is absent.
* Add a `ROADMAP.md` ledger pointer only if needed for provenance consistency.
* Add a dated closeout entry to `DECISIONS.md` only if duplicate-update prevention passes for readpoint content.
* Do not treat prior 2026-05-29 scope split or authority classification closeout entries as duplicates of this round's own promotion/noop closeout record solely because they share predecessor evidence.
* Keep ledger/provenance entries as pointers and do not rewrite historical sealed bodies.
* The `DECISIONS.md` entry must include:

```text
This does not complete structural signal disposition.
This does not complete ACQ_DOMINANT remeasurement.
This does not open publish mutation review.
```

Validation:

* Post-write consistency re-check.
* Additive-only diff inspection.
* Historical body mutation diff `0`.
* Top-doc / architecture / roadmap phrase consistency check.
* Duplicate update prevention still passes after write.
* Any architecture insertion fallback location is recorded if used.

---

### Change 7

Purpose:

For `new_execution_required`, reconstruct current evidence and classify the structural signal universe only when Phase 0 proves sealed evidence cannot be consumed.

Files:

* round-local `phaseB1_structural_signal_occurrence_inventory.jsonl`
* round-local `phaseB1_occurrence_summary.json`
* round-local `phaseB1_identifier_universe.json`
* round-local `phaseB1_current_vs_historical_surface_report.json`
* round-local `phaseB2_surface_classification.jsonl`
* round-local `phaseB2_surface_class_counts.json`
* round-local `phaseB3_authority_classification.jsonl`
* round-local `phaseB3_authority_class_counts.json`
* round-local `phaseB3_forbidden_writer_reach_report.json`
* round-local `phaseB3_mutation_candidate_report.json`

Implementation Notes:

* Branch B is evidence-reconstruction-only when sealed evidence cannot be consumed.
* Branch B is not a policy reopening of the sealed 2026-05-29 authority classification decision.
* Branch B follows the observer-only authoritative reconstruction pattern used in the 2026-05-28 Branch B reconstruction round, but only as a precedent for evidence reconstruction and not as permission to create publish/write authority.
* Inventory `FUNCTION_NARROW`, `ACQ_DOMINANT`, report fields, preview flags, diagnostic/test labels, historical references, top-doc references, and generated artifact references.
* Classify surface and authority separately.
* Passing terminal classes are non-writer classes only.
* Unknowns block mutation and may require partial/blocked closeout.

Validation:

* JSONL parse.
* Duplicate key check.
* `unknown_surface_count = 0` target.
* `unknown_count = 0` target.
* `unclassified_count = 0` target.
* `writer_input_passing_count = 0`.
* `forbidden_writer_reach_count = 0`.
* `writer_misread_count = 0`.
* `mutation_candidate_count = 0`.

---

### Change 8

Purpose:

For `new_execution_required`, run `FUNCTION_NARROW` / `ACQ_DOMINANT` special gates and documentation sync.

Files:

* round-local `phaseB4_function_narrow_gate_report.json`
* round-local `phaseB4_acq_dominant_gate_report.json`
* round-local `phaseB4_blanket_isolation_forbidden_report.json`
* round-local `phaseB5_doc_sync_manifest.json`
* round-local `phaseB5_current_readpoint_addendum.md`
* round-local `phaseB5_stale_wording_scan_report.json`
* round-local `phaseB5_authority_phrase_consistency_report.json`

Implementation Notes:

* Seal `FUNCTION_NARROW` residual as report/preview structural flag only.
* Keep `ACQ_DOMINANT` as classification-only or future remeasurement pointer.
* State that `ACQ_DOMINANT Current Baseline Remeasurement Round` is a separate future-only path.
* State that publish mutation review requires separate explicit opening decision.

Validation:

* `function_narrow_second_rollout_opened = false`.
* `acq_dominant_remeasurement_performed = false`.
* `acq_dominant_publish_candidate_count = 0`.
* `blanket_isolation_reopen_count = 0`.
* Additive-only doc sync review.

---

### Change 9

Purpose:

Close the chosen branch with non-mutation evidence, validation ceiling, and non-claims.

Files:

* round-local `phaseA6_closeout.json` / `phaseA6_closeout.md`, or
* round-local `phaseB6_non_mutation_hash_diff_report.json`
* round-local `phaseB6_frozen_surface_manifest_before.json`
* round-local `phaseB6_frozen_surface_manifest_after.json`
* round-local `phaseB6_validation_side_effect_report.json`
* round-local `phaseB7_closeout.json` / `phaseB7_closeout.md`, or
* round-local `noop_closeout.json` / `noop_closeout.md`, or
* round-local `blocked_conflicting_authority_report.json` / `blocked_conflicting_authority_closeout.md`
* round-local `artifact_hash_manifest.json`

Implementation Notes:

* Use `complete`, `partial`, `implemented_only`, or `blocked` closeout state as defined by `docs/EXECUTION_CONTRACT.md`.
* Include validation ceiling with `validated`, `out_of_scope`, and `unvalidated_but_in_scope`.
* Include non-claims explicitly.
* Record future-only paths without opening them.

Validation:

* Closeout JSON parse.
* Evidence manifest path existence check.
* Hard gate pass for non-blocked closeout.
* Non-claim checklist pass.

---

## 7. Validation Plan

### Automated Validation

Branch-independent minimum:

* `rg` scans over `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, and relevant `docs/Iris/Done/*` files.
* Round-local JSON / JSONL parse validation.
* Path existence checks for consumed sealed input artifacts.
* `git diff --stat` and `git diff` review for touched files.
* `git diff --name-only` against the branch-specific allowed touched-file list.
* Template/contract attestation confirming `PLAN_TEMPLATE.md` and `EXECUTION_CONTRACT.md` are the applicable planning and closeout vocabulary references for this execution context.

`already_closed_noop` expected validation:

* Current surface equivalence report.
* Duplicate-update prevention report, including semantic-equivalence checks.
* No live-doc diff.
* No source/rendered/runtime/state mutation.
* `complete_with_noop_evidence` sublabel or `noop evidence closeout` wording in closeout.

`doc_absorption_only` expected validation:

* Clause-to-source crosscheck.
* Cross-document consistency matrix.
* Live current-authority contradiction scope report.
* Duplicate-doc guard.
* Touched-files docs-only report.
* Hard gate report.
* Adversarial review.
* Additive-only document diff inspection.
* Historical body mutation diff `0`.
* Architecture insertion fallback report if `ARCHITECTURE.md 9-2` is unavailable or moved.
* Source/rendered/runtime hash diff if validation commands are run.
* Validation side-effect restore report if generated output changes.

`new_execution_required` expected validation:

* Current occurrence inventory determinism.
* Surface classification counts.
* Authority classification counts.
* Writer reachability reports.
* Mutation candidate report.
* Frozen surface manifest before/after hash diff.
* Relevant Python artifact validators, if created for the round.
* Existing Python tests only if the chosen branch touches tooling or requires current pipeline validation:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Lua syntax validation only if the branch touches Lua or if the closeout wants to claim Lua surface unchanged by exact command:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

### Manual Validation

* Document review of projected and final wording.
* Adversarial review of claim boundary, branch label, duplicate-update prevention, and non-claims.

### Validation Limits

The plan does not perform or claim:

* Manual in-game validation.
* Runtime behavior validation.
* Deployment validation.
* Multiplayer validation.
* Long-session runtime validation.
* External ecosystem compatibility sweep.
* Workshop validation.
* Release validation.
* Runtime equivalence validation.
* `ACQ_DOMINANT` current-baseline remeasurement.
* Publish mutation review.
* Semantic quality revalidation.
* Browser / Wiki / Tooltip behavior validation.

---

## 8. Risk Surface Touch

### Authority Surface

Yes. The round may update canonical document readpoint surfaces and decision ledger wording. It must not create new publish/write authority.

### Runtime Behavior Surface

None intended. Browser / Wiki / Tooltip runtime behavior must remain unchanged.

### Compatibility Surface

None intended or very low. Runtime artifacts and external module compatibility surfaces are not intended mutation targets.

### Sealed Artifact Surface

Yes, read-only. The round may classify which sealed artifacts are current-consumable evidence, provenance-only, or non-authority. Existing sealed artifact bodies must not be rewritten.

### Public-Facing Output Surface

None intended. User-facing Iris text, tooltip output, wiki output, README public release claims, and public rollout statements are not intended mutation targets.

---

## 9. Risk Analysis

### Architecture Risk

* Already sealed authority classification could be reopened unnecessarily if Branch B is not kept evidence-reconstruction-only.
* Current canonical surface could receive duplicate addenda if equivalence is not checked first.
* New document wording could imply new publish/write authority.
* Historical/stale report artifacts could be incorrectly promoted to current authority.

### Runtime Risk

* Expected runtime risk is none if scope is respected.
* Validation commands may regenerate rendered output as a side effect; any such side effect must be recorded and restored before non-mutation closeout.

### Compatibility Risk

* Expected compatibility risk is none if runtime artifacts and public outputs remain untouched.
* Any unexpected runtime/package diff blocks docs-only closeout until explained or reverted by the responsible branch.

### Regression Risk

* Top-doc and lower-doc wording may drift if only one surface is updated.
* Cross-document inventory may miss a stale current-looking reference.
* Closeout may overclaim disposition, release, deployment, runtime equivalence, or public behavior validation.

---

## 10. Rollback Plan

Rollback is authority/doc rollback, not runtime rollback.

* If source/rendered/runtime/state surfaces are changed unexpectedly, stop and close as blocked or restore only changes made by this round after identifying them.
* If round-local artifacts are invalid, quarantine them as invalid execution trace or replace them with corrected artifacts under the same round root before closeout.
* If live-doc additive wording is wrong, correct it with additive clarification when possible; do not rewrite sealed historical bodies.
* If Branch A live-doc promotion is invalid, revert only the newly added `ARCHITECTURE.md` subsection, `ROADMAP.md` line, `ROADMAP.md` pointer, and `DECISIONS.md` entry created by this round.
* If duplicate-update prevention fails after writing, remove only the duplicate addition made by this round or convert the branch to `already_closed_noop` if evidence supports it.
* If `ACQ_DOMINANT` remeasurement or publish mutation review is mixed into this round, close this round as failed/blocked and split that work into a separate explicit round.
* Sealed bodies, staging artifact bodies, runtime output, fixtures, Done walkthroughs, and dated historical decision bodies are not rollback targets for this round.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Iris remains a wiki-style information module: no interpretation, recommendation, comparison, or gameplay policy expansion.
* Runtime/build-time separation must remain intact.
* Offline Python pipeline authority and runtime Lua consume/render-only boundary must remain intact.
* Current runtime baseline must remain unchanged.
* Source facts and source decisions row identity must remain unchanged.
* Rendered text must remain unchanged unless an explicitly separate round opens that surface.
* Runtime Lua and packaged Lua must remain unchanged.
* `quality_state`, `publish_state`, and `runtime_state` semantics must remain unchanged.
* `FUNCTION_NARROW` / `ACQ_DOMINANT` blanket isolation reopen is forbidden.
* Old structural count/report artifact direct succession is forbidden.
* Stale report artifacts must not be promoted directly to current authority.
* `ACQ_DOMINANT` must not become a publish mutation candidate without separate current-baseline remeasurement.
* Historical sealed bodies, fixtures, staging bodies, Done docs, and dated decision bodies must not be directly rewritten.
* Top-doc changes should be additive and must pass duplicate-update prevention.
* No new publish/write authority may be created.
* Existing fail-loud guards must not be removed.
* Branch B reconstructed observer authority, if consumed, is read-only input.
* Branch B in this plan is evidence-reconstruction-only, not sealed decision reopening, and follows the 2026-05-28 observer-only reconstruction precedent only for evidence-reconstruction shape.
* `docs/EXECUTION_CONTRACT.md` closeout discipline applies to any authority/sealed/public surface claim.

---

## 12. Expected Closeout State

Expected closeout target:

```text
complete, if Phase 0 selects already_closed_noop or doc_absorption_only and all branch validation passes within the stated validation ceiling.
```

Alternative closeout targets:

```text
complete, if Phase 0 selects new_execution_required and all evidence reconstruction, occurrence inventory, surface classification, authority classification, special gates, documentation sync, and non-mutation validation pass.
partial, if non-critical docs alignment is incomplete but evidence and branch constraints are recorded without overclaim.
implemented_only, if artifacts/docs are written but required validation is not run.
blocked, if authority conflict, missing evidence, unexpected mutation, branch ambiguity, duplicate-update risk, or claim-boundary violation prevents safe closeout.
```

Branch-specific expected closeout:

* `blocked_conflicting_authority`: conflicting sealed/current sources or unsafe authority conditions are named; no publish mutation, remeasurement, runtime mutation, or sealed body rewrite occurs.
* `already_closed_noop`: current canonical surfaces already contain the equivalent readpoint; duplicate live-doc update is prevented; no live-doc mutation is needed; closeout may use `complete` only with `complete_with_noop_evidence` sublabel or `noop evidence closeout` wording.
* `doc_absorption_only`: sealed structural-signal observer/readpoint authority is promoted additively to current canonical document surface; live current-authority contradiction count is `0`; hard gate and adversarial review pass; no source/rendered/runtime/state mutation is adopted.
* `new_execution_required`: current occurrence universe, surface classification, and authority classification are reconstructed as evidence only; unknown/unclassified counts are `0` or honestly blocked; writer reach and mutation candidate counts are `0`; non-mutation evidence passes.
