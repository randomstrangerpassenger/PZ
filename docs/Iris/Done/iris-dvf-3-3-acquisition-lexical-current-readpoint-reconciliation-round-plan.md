# Iris DVF 3-3 Acquisition Lexical Current Readpoint Reconciliation Round Plan

> 상태: Draft v0.2-review-response
> 기준일: 2026-06-05
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> authority input: `ROADMAP - Acquisition Lexical Current Readpoint Reconciliation 종합본` (user-provided pasted roadmap)
> review input: `REVIEW - Acquisition Lexical Current Readpoint Reconciliation Round Plan 최종 종합 검토안` (user-provided pasted review). v0.2 resolves the three blocking revisions by moving canonical promotion to Phase 6 only, completing the predecessor input count tuple, and adding read-state / suppress-disposition crosswalk plus numeric gate fields.
> 직접 상위 readpoint: 2026-06-05 `Iris DVF 3-3 Acquisition Lexical Current Inventory / Readpoint Audit Round` closed as `closed_with_followup_suppress_disposition_required`
> 계획 형식: `docs/PLAN_TEMPLATE.md`; observed planning-time identity: path readable; sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`; line_count `109`. Execution must re-check template identity or carry drift as a validation limitation/blocker under Phase 0.
> execution contract reference: `docs/EXECUTION_CONTRACT.md`; observed planning-time identity: path readable; status `v1.3`; closeout-state vocabulary includes `complete / partial / implemented_only / blocked`. Execution must re-check contract availability and closeout vocabulary before using those states.
> 실행 상태: planning authority only. This document does not execute reconciliation, mutate source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, state axes, public-facing behavior, suppress retirement, contract expansion, rollout, or release readiness.

---

## 1. Objective

이번 execution plan의 목적은 선행 `Acquisition Lexical Current Inventory / Readpoint Audit Round`를 입력 readpoint로 삼아, Iris DVF 3-3 acquisition lexical 관련 top-doc closeout, lower plan, stale artifact, validator/utility readpoint가 같은 read order로 읽히도록 정렬하는 것이다.

이번 라운드가 답해야 하는 질문은 다음으로 제한한다.

```text
선행 inventory readpoint가 current reconciliation 입력으로 잠겼는가?
top-doc, lower plan, stale artifact, validator/utility surface는 current / stale / historical / follow-up 후보로 분리되었는가?
suppress 의존 과거 문구는 current blocker가 아니라 historical premise로 격하되었는가?
live suppress validator surface 3건은 current blocker가 아니라 follow-up disposition candidate로 분리되었는가?
josa_adaptive / phrasebook / array acquisition / runtime-side repair / contract expansion은 다시 열리지 않았는가?
```

이번 라운드의 최대 claim은 다음이다.

```text
선행 Acquisition Lexical Current Inventory / Readpoint Audit을 입력으로,
acquisition lexical 관련 top-doc closeout / lower plan / stale artifact /
validator-utility readpoint의 current-vs-historical 읽기 방식이 모순 없이 정렬되었다.
```

이번 라운드는 기능 구현, 문장 품질 개선, source data mutation, rendered/runtime regeneration, suppress retirement, deployment, release readiness를 주장하지 않는다.

---

## 2. Scope

This is a docs/governance readpoint reconciliation planning round. Execution under this plan may create round-local staging reports, classification manifests, documentation patches, and an additive closeout record.

In scope:

* Input authority lock for the 2026-06-05 inventory readpoint.
* Document and claim universe enumeration.
* Read-state classification matrix.
* Suppress premise demotion.
* Live suppress validator surface follow-up separation.
* Non-reopen boundary seal for closed acquisition lexical expansion candidates.
* Top-doc / lower-plan / stale-artifact read-order reconciliation draft and sidecar interpretation notes.
* Standard docs/governance validation.
* Phase 6-only closeout and optional additive canonical promotion if hard gates pass.

### Explicitly Out Of Scope

* Source facts patch.
* Source decisions patch.
* Rendered text regeneration.
* Runtime Lua mutation.
* Packaged Lua mutation.
* Bridge payload mutation.
* `quality_state`, `publish_state`, or `runtime_state` mutation.
* Public-facing Browser / Wiki / Tooltip output changes.
* Acquisition wording improvement.
* Acquisition hint sentence rewrite.
* `suppress` retirement, removal, validator deletion, or implementation fix.
* Current suppress validator surface `3` disposition execution.
* Acquisition contract expansion.
* `josa_adaptive` design or implementation.
* Phrasebook introduction.
* Array acquisition input contract introduction.
* Runtime-side lexical repair.
* Coverage, quality, or completion remeasurement.
* Manual in-game validation.
* Workshop, B42, deployment, or release readiness claim.
* Sealed predecessor artifact body rewrite.
* Historical artifact deletion to hide contradiction.

---

## 3. Non-Goals

* Do not improve acquisition lexical Korean wording.
* Do not decide whether `suppress` should be retired.
* Do not remove live suppress dependencies.
* Do not promote validator/utility evidence into writer authority.
* Do not reopen source acquisition contract scope.
* Do not introduce a new runtime language repair system.
* Do not remeasure the 2026-06-05 inventory counts unless a prerequisite drift blocker is found.
* Do not claim runtime equivalence, compatibility sweep completion, or release readiness.
* Do not make stale plans disappear by deleting them.
* Do not treat historical addendum text as stronger authority than current top-doc readpoints.

---

## 4. Assumptions

* `docs/Philosophy.md` remains the highest authority.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` remain the current canonical governance readpoints as of 2026-06-05.
* `docs/PLAN_TEMPLATE.md` is the required implementation plan form for this repository context.
* The direct predecessor readpoint is `closed_with_followup_suppress_disposition_required`.
* The predecessor readpoint carries this complete input tuple: logical surface `507`, raw occurrence `8828`, classified `507`, `UNCLASSIFIED_BLOCKED = 0`, `writer_path_reachable_but_unindexed_count = 0`, protected mutation `0`, current gate surface count `0`, current suppress validator surface count `3`, JSON parse `20`, JSONL parse `5`, JSONL rows `18961`, JSON/JSONL parse error count `0`, helper py_compile exit code `0`.
* Old suppress-dependent plans are historical/stale premises unless this reconciliation finds a current authoritative successor claim.
* Live suppress dependency is limited to current style-validator surface follow-up candidates unless this reconciliation finds a fail-loud contradiction.
* `suppress current blocker count = 0` is anchored to the predecessor `current gate surface count = 0` and the round-local derived condition defined in Phase 3, not to an informal reading.
* This reconciliation is documentation/governance read-order alignment, not a new source-data or runtime single-writer authority.
* Execution may run in a dirty worktree and must preserve unrelated user changes.
* Any future validation pass claim must name the exact command and exit code.

---

## 5. Repository Areas Affected

### Code

* None expected for production/build/runtime code.
* Round-local helper scripts are out of the default scope. If a helper becomes necessary, execution must keep it outside production/runtime surfaces and record it as generated or staging support, not current product authority.

### Docs

* `docs/Iris/iris-dvf-3-3-acquisition-lexical-current-readpoint-reconciliation-round-plan.md`
* `docs/Iris/iris-dvf-3-3-acquisition-lexical-current-readpoint-reconciliation-round-closeout.md`
* `docs/DECISIONS.md` (Phase 6-only optional additive closeout entry)
* `docs/ARCHITECTURE.md` (Phase 6-only optional additive readpoint entry)
* `docs/ROADMAP.md` (Phase 6-only optional current-state / Done movement)
* Existing lower plans only through Phase 6-approved additive read-state labels, not destructive deletion.
* Stale artifacts through sidecar interpretation notes by default; direct stale artifact body edits require an explicit non-sealed-body finding and Phase 6 promotion approval.

### Config

* None.

### Generated Artifacts

Expected staging root:

* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/`

Expected generated artifacts:

* `input_authority_lock.json`
* `inventory_readpoint_summary.md`
* `reconciliation_document_universe.jsonl`
* `document_surface_classification.md`
* `acquisition_lexical_contract_claim_disposition_map.jsonl`
* `read_state_classification_matrix.jsonl`
* `four_surface_expected_read_state_map.md`
* `ambiguous_surface_blocker_report.md`
* `current_vs_stale_contradiction_report.md` with machine-readable `contradiction_count`
* `suppress_occurrence_disposition.jsonl`
* `suppress_label_to_read_state_crosswalk.json`
* `suppress_historical_premise_note.md`
* `live_suppress_validator_surface_followup_note.md`
* `non_reopen_boundary_manifest.json`
* `forbidden_reopen_scan_report.md` with `allowed_context_reason`
* `doc_patch_manifest.jsonl`
* `reconciliation_validation_summary.json`
* `successor_trigger_matrix.md`

---

## 6. Planned Changes

### Change 1 - Phase 0 Input Authority Gate

Purpose:

Lock the predecessor inventory readpoint before any reconciliation claim is made.

Files:

* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/input_authority_lock.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/inventory_readpoint_summary.md`

Implementation Notes:

* Confirm the predecessor closeout branch is `closed_with_followup_suppress_disposition_required`.
* Record the complete predecessor count tuple:

```text
logical_surface_count = 507
raw_occurrence_total = 8828
classified_count = 507
UNCLASSIFIED_BLOCKED_count = 0
writer_path_reachable_but_unindexed_count = 0
protected_mutation_count = 0
current_gate_surface_count = 0
current_suppress_validator_surface_count = 3
json_parse_count = 20
jsonl_parse_count = 5
jsonl_row_count = 18961
json_jsonl_parse_error_count = 0
helper_py_compile_exit_code = 0
```

* Record that the round-local `suppress_current_blocker_count` must derive from `current_gate_surface_count = 0` plus Phase 3 cross-manifest consistency, not from prose-only review.
* Copy predecessor non-claim boundaries into the reconciliation input lock.
* If predecessor metadata is missing or count identity drifts, stop before doc patching and close as prerequisite drift.
* Re-check `docs/PLAN_TEMPLATE.md` identity and `docs/EXECUTION_CONTRACT.md` closeout vocabulary. If `PLAN_TEMPLATE.md` is unavailable or no longer exposes the 1-12 section plan form, close as `blocked_template_recognition_indeterminate`. If the template hash/line count drift but the structure remains recognizable, carry it as a validation limitation and continue only if no authority conflict is found. If `EXECUTION_CONTRACT.md` is unavailable or no longer recognizes `complete / partial / implemented_only / blocked`, close as `blocked_execution_contract_unavailable_or_closeout_vocabulary_mismatch`.

Validation:

* Required field existence check.
* Complete count-tuple consistency check.
* Input readpoint branch token check.
* Template identity / execution contract availability branch check.
* Block if required predecessor fields are unavailable.

---

### Change 2 - Phase 1 Document / Claim Universe Lock

Purpose:

Enumerate every document, stale plan, artifact, validator/utility reference, and claim that can affect acquisition lexical current read-order interpretation.

Files:

* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/reconciliation_document_universe.jsonl`
* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/document_surface_classification.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/acquisition_lexical_contract_claim_disposition_map.jsonl`

Implementation Notes:

* Adopt the pasted roadmap's Phase 0-6 granularity as the round-local execution scaffold. This scaffold is not semantic authority over `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md`.
* Lock both document universe and claim universe before applying interpretation notes.
* Separate top-doc current readpoints, lower plans, stale predecessor plans, historical premises, diagnostic/test surfaces, current validator surfaces, and utility supporting evidence.
* Treat missing or ambiguous document references as fail-loud findings, not silent cleanup.

Validation:

* Path canonicalization check.
* Duplicate path check.
* Unclassified document count must be `0`, or execution must close blocked.
* Unclassified claim count must be `0`, or execution must close blocked.

---

### Change 3 - Phase 2 Read-State Classification Matrix

Purpose:

Assign each document/claim/occurrence a read-state so current authority and historical premise are no longer mixed.

Files:

* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/read_state_classification_matrix.jsonl`
* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/four_surface_expected_read_state_map.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/ambiguous_surface_blocker_report.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/current_vs_stale_contradiction_report.md`

Implementation Notes:

Use this classification vocabulary:

```text
current_authority_readpoint
current_validator_surface
current_utility_supporting_evidence
diagnostic_or_test_surface
stale_predecessor_plan
historical_premise_only
followup_disposition_candidate
blocked_ambiguous
```

Expected surface mapping:

| Surface | Expected Read-State |
|---|---|
| top-doc closeout | `current_authority_readpoint` |
| lower current plan | `current_authority_readpoint` or explicit successor label |
| stale predecessor plan | `stale_predecessor_plan` |
| historical artifact | `historical_premise_only` |
| validator surface | `current_validator_surface` |
| utility surface | `current_utility_supporting_evidence` |
| live suppress surface `3` | `followup_disposition_candidate` |

* Validator/utility evidence must not become writer authority.
* Stale predecessor plans must not remain current execution plans.
* `blocked_ambiguous` may not be auto-resolved. It either becomes `0` through evidence, or the round closes blocked.
* `current_vs_stale_contradiction_report.md` must contain a machine-readable `contradiction_count` field and normalized `claim_id` references sufficient to show which current/stale claims were compared.

Validation:

* Classification coverage must be `100%`.
* `blocked_ambiguous = 0` from `read_state_classification_matrix.jsonl.read_state == blocked_ambiguous` is required for complete closeout.
* Top-doc vs lower-plan contradiction count must be `0` from `current_vs_stale_contradiction_report.md.contradiction_count` for complete closeout.
* Current authority and stale predecessor claims must not both own the same current reading.

---

### Change 4 - Phase 3 Suppress Premise Demotion

Purpose:

Demote stale suppress-dependent language from current blocker status to historical premise, while preserving live suppress validator surface `3` as a separate follow-up candidate.

Files:

* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/suppress_occurrence_disposition.jsonl`
* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/suppress_label_to_read_state_crosswalk.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/suppress_historical_premise_note.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/live_suppress_validator_surface_followup_note.md`

Implementation Notes:

* Classify suppress occurrences as `CURRENT_LIVE_EVIDENCE`, `HISTORICAL_PREMISE`, or `FOLLOWUP_DISPOSITION_CANDIDATE`.
* The predecessor live suppress validator surface `3` is expected to classify as `FOLLOWUP_DISPOSITION_CANDIDATE` paired to `followup_disposition_candidate` in this reconciliation. It is not resolved, not retired, and not a current blocker unless the cross-manifest gate produces a fail-loud drift.
* Produce the following crosswalk in `suppress_label_to_read_state_crosswalk.json`:

| Suppress Disposition Label | Allowed Read-State Label |
|---|---|
| `CURRENT_LIVE_EVIDENCE` | `current_validator_surface` or `current_utility_supporting_evidence` |
| `HISTORICAL_PREMISE` | `historical_premise_only` or `stale_predecessor_plan` |
| `FOLLOWUP_DISPOSITION_CANDIDATE` | `followup_disposition_candidate` |

* Each `suppress_occurrence_disposition.jsonl` row must include `occurrence_id`, `path`, `disposition`, `paired_read_state`, `is_predecessor_live_suppress_validator_surface`, and `derived_current_blocker`.
* Define `suppress_current_blocker_count` as `count(row.derived_current_blocker == true)`.
* `derived_current_blocker` is `true` if a suppress-related occurrence is asserted as a current blocker / current contract-incomplete gate / current execution prerequisite, or if a predecessor live suppress validator surface `3` row is not paired to `FOLLOWUP_DISPOSITION_CANDIDATE -> followup_disposition_candidate`.
* Define `suppress_crosswalk_violation_count` as the count of rows whose `disposition -> paired_read_state` pair is not allowed by `suppress_label_to_read_state_crosswalk.json`.
* The current live validator surface count remains `3` unless a fail-loud drift is found.
* The live suppress `3` surface must pass a cross-manifest consistency gate between `suppress_occurrence_disposition.jsonl`, `suppress_label_to_read_state_crosswalk.json`, and `read_state_classification_matrix.jsonl`.
* Do not delete suppress references to manufacture a clean state.
* Do not claim suppress retirement or removal.

Validation:

* Suppress occurrence report.
* `suppress_current_blocker_count = 0` as derived above is required for complete closeout.
* `suppress_crosswalk_violation_count = 0` is required for complete closeout.
* `live_suppress_surface_cross_manifest_mismatch_count = 0` is required for complete closeout.
* Live validator surface classification count must match predecessor input `current_suppress_validator_surface_count = 3` unless drift blocks the round.
* Suppress retirement/removal claim scan must be `0`.

---

### Change 5 - Phase 4 Non-Reopen Boundary Seal

Purpose:

Seal that this reconciliation does not reopen closed acquisition lexical expansion paths.

Files:

* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/non_reopen_boundary_manifest.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/forbidden_reopen_scan_report.md`

Implementation Notes:

* Record non-reopen boundaries for `josa_adaptive`, phrasebook, array acquisition, runtime-side repair, acquisition contract expansion, source/rendered/runtime mutation, and state-axis mutation.
* Allowed mentions must be historical, non-goal, blocker, or non-claim references.
* `forbidden_reopen_scan_report.md` must include `token`, `path`, `line`, `context`, `classification`, and `allowed_context_reason` so Non-Goals references do not become false positive reopen failures.
* Future successor triggers must be narrow and explicit, not broad reopen invitations.

Validation:

* Forbidden reopen phrase scan with `allowed_context_reason` for permitted historical/non-goal/blocker/non-claim mentions.
* Candidate / next / implement / enable context scan for forbidden tokens.
* Non-claim boundary presence check in staged closeout and any top-doc patch.

---

### Change 6 - Phase 5 Top-Doc / Lower-Plan Reconciliation Staged Draft

Purpose:

Prepare staged reconciliation drafts for top-doc closeout, lower plan, stale artifact, and validator/utility readpoint language after Phase 0-4 gates have staging evidence. Canonical governance docs remain unchanged in this phase.

Files:

* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/doc_patch_manifest.jsonl`
* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/top_doc_reconciliation_patch.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/lower_plan_read_state_patch.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/stale_artifact_interpretation_sidecar.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/acquisition_lexical_readpoint_reconciliation_note.md`

Implementation Notes:

* Phase 5 is staged-draft only. It must not modify `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, or the final closeout path.
* Canonical governance docs remain unchanged in Phase 5 even if the draft is internally consistent.
* Keep sealed predecessor artifact bodies read-only.
* Use sidecar interpretation notes for stale artifacts by default. Do not delete stale artifacts.
* State that validator/utility readpoints are current evidence or support, not writer authority.
* State that this reconciliation is read-order alignment, not a new source/runtime authority.

Validation:

* Protected sealed body mutation scan.
* Top-doc vs lower-plan contradiction scan.
* Read-order consistency check.
* Doc patch manifest path coverage.
* Canonical governance docs unchanged check for `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md`.
* Sealed predecessor identity/hash stability check where applicable.

---

### Change 7 - Phase 6 Closeout Seal / Canonical Promotion Decision

Purpose:

Close the reconciliation as a docs/governance readpoint if hard gates pass, or fail-loud with a blocked closeout if they do not.

Files:

* `docs/Iris/iris-dvf-3-3-acquisition-lexical-current-readpoint-reconciliation-round-closeout.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/reconciliation_validation_summary.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/successor_trigger_matrix.md`
* Optional Phase 6-only additive entries in `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md`.

Implementation Notes:

* Use standard docs/governance validation depth.
* Canonical promotion is centralized in Phase 6. No canonical governance doc mutation is allowed before this phase.
* Optional canonical promotion is allowed only after all of the following are true:
  * Phase 0-4 gates pass.
  * Phase 5 contradiction scan, read-order consistency check, sealed-body mutation scan, and canonical-governance-docs-unchanged check pass.
  * Adversarial review verdict is `PASS`.
  * Classification residue is `0`.
  * `current_vs_stale_contradiction_report.md.contradiction_count = 0`.
  * Non-reopen scan passes.
  * Protected mutation scan passes.
  * `suppress_current_blocker_count = 0`.
  * `live_suppress_surface_cross_manifest_mismatch_count = 0`.
* If promotion occurs, it must be additive. A later correction must be additive too unless the changed surface is explicitly non-sealed and reverted before closeout.
* Carry validation ceiling and non-claims in the closeout.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are `may-promote` surfaces only. The required closeout artifact is the round closeout under `docs/Iris/`; top-doc promotion is optional and evidence-gated.

Validation:

* Closeout schema / required field check.
* JSON/JSONL parse check for generated manifests.
* Determinism check for generated reports where helpers are used.
* Mutation count check.
* Non-claim boundary scan.
* Reviewer/adversarial checklist with explicit `PASS` before complete closeout or canonical top-doc promotion.

---

## 7. Validation Plan

### Automated Validation

Future execution should run the exact relevant commands available in the checkout and record exit code `0` before claiming pass. The minimum validation set is:

* `docs/PLAN_TEMPLATE.md` existence/hash/line-count check.
* `docs/EXECUTION_CONTRACT.md` availability and closeout-state vocabulary check.
* Predecessor inventory readpoint required-field and complete count-tuple consistency check.
* JSON/JSONL parse checks for all generated manifests.
* Document universe path canonicalization and duplicate check.
* Claim classification coverage check.
* Read-state classification coverage check.
* `read_state_classification_matrix.jsonl` `blocked_ambiguous` label count check.
* `current_vs_stale_contradiction_report.md.contradiction_count` numeric field check.
* `suppress_occurrence_disposition.jsonl` disposition count check.
* `suppress_label_to_read_state_crosswalk.json` parse and allowed mapping check.
* `suppress_crosswalk_violation_count` check.
* Live suppress `3` cross-manifest consistency check across suppress disposition, crosswalk, and read-state matrix.
* `suppress_current_blocker_count` derived-condition check.
* Suppress retirement/removal claim scan.
* Forbidden reopen phrase/context scan for `josa_adaptive`, phrasebook, array acquisition, runtime repair, and contract expansion, including `allowed_context_reason` for allowed mentions.
* Protected source/rendered/runtime/package/state mutation scan.
* Sealed predecessor body/hash stability check where applicable.
* Phase 5 canonical governance docs unchanged check before Phase 6.
* Phase 6 adversarial review `PASS` check before canonical promotion.
* Generated report determinism check if helpers generate artifacts.

### Manual Validation

* Review that the closeout claim does not exceed docs/governance reconciliation.
* Review that stale plans are labeled rather than deleted.
* Review that live suppress validator surface `3` remains a follow-up candidate, not a current blocker and not resolved.
* Review that validator/utility evidence is not promoted to writer authority.
* Review that top-doc, lower-plan, stale artifact, and validator/utility readpoints read in one consistent order.
* Review that successor triggers do not reopen closed lexical expansion paths by broad wording.

### Validation Limits

* No runtime validation.
* No Lua syntax validation unless execution unexpectedly touches Lua, which should block scope.
* No packaged Lua validation.
* No rendered text diff validation.
* No manual in-game validation.
* No multiplayer validation.
* No external mod compatibility sweep.
* No acquisition wording quality validation.
* No suppress retirement validation.
* No acquisition contract expansion validation.
* No coverage / quality / completion remeasurement.
* No deployment, Workshop, B42, or release readiness validation.

---

## 8. Risk Surface Touch

### Authority Surface

Documentation/governance authority surface is touched.

This plan resolves the roadmap's authority-expression ambiguity by treating the round as read-order reconciliation only. It does not create source-data writer authority, runtime authority, or a new semantic contract writer. Any Phase 6 DECISIONS/ARCHITECTURE/ROADMAP promotion must be an additive closeout/readpoint entry.

Canonical governance promotion is Phase 6-only and requires Phase 0-5 gate pass plus adversarial review `PASS`. Phase 5 staged drafts are not authority until Phase 6 promotion explicitly adopts them.

### Runtime Behavior Surface

None.

Runtime Lua, packaged Lua, bridge payload, Browser, Wiki, Tooltip, and in-game behavior must remain unchanged.

### Compatibility Surface

Documentation-only.

No external mod consumer behavior changes are expected or claimed.

### Sealed Artifact Surface

Read-only.

Sealed predecessor artifact bodies must not be rewritten. If a sealed surface would need correction, execution must use an additive successor/correction readpoint rather than mutating history.

### Public-Facing Output Surface

None.

User-facing strings, rendered item text, UI copy, sort/filter behavior, recommendations, and trust/quality exposure are outside this round.

---

## 9. Risk Analysis

### Architecture Risk

* Reconciliation could accidentally be worded as a new single-writer source authority instead of read-order alignment.
* Validator/utility evidence could be over-promoted into writer authority.
* Historical addendum text could be allowed to override current canonical readpoints.
* Stale plan labels could be incomplete, leaving more than one current reading for the same claim.
* Read-state labels and suppress disposition labels could drift unless the crosswalk and cross-manifest consistency gate are enforced.

### Runtime Risk

* Direct runtime risk is none if scope is preserved.
* Any Lua, packaged payload, rendered output, or build/runtime consumer mutation is a scope violation and should block the round.

### Compatibility Risk

* Documentation wording could imply external behavior or release readiness that was not validated.
* Broad successor triggers could invite unapproved `josa_adaptive`, phrasebook, array acquisition, runtime repair, or contract expansion work.

### Regression Risk

* A lower plan may still read as current if only top docs are patched.
* Suppress-dependent stale language may be hidden rather than classified.
* Live suppress validator surface `3` may be misread as resolved.
* Protected predecessor body mutation could corrupt historical trace.
* Input readpoint drift may be missed if Phase 0 is treated as a formality.

---

## 10. Rollback Plan

Rollback is split by surface type.

Before canonical promotion:

* Discard round-local staging artifacts under `Iris/build/description/v2/staging/acquisition_lexical_current_readpoint_reconciliation_round/`.
* Do not patch top docs if Phase 0-5 gates or adversarial review fail.
* Phase 5 staged drafts can be discarded without changing canonical governance docs.

For non-sealed doc patches:

* Use `doc_patch_manifest.jsonl` and `git diff` to identify the exact additive changes.
* Revert only this round's changes. Do not revert unrelated dirty worktree changes.
* If a non-sealed patch produced ambiguity but no closeout was promoted, correct or remove the round-local patch before closeout.

For sealed or additive canonical promotion:

* Do not rewrite sealed predecessor bodies.
* Add a successor/correction readpoint that states the incorrect claim, correction basis, affected surfaces, and new read order.

Blocked conditions:

* If predecessor inventory metadata drifts, close as prerequisite drift.
* If read-state ambiguity remains, close as ambiguous claim conflict.
* If sealed historical body mutation is detected, close as protected history mutation failure.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance remains mandatory.
* Pulse ecosystem Hub & Spoke / SPI boundaries are unaffected.
* Iris remains a wiki-mode module and does not perform recommendation, interpretation, comparison, or runtime language repair in this round.
* Runtime/build-time separation must be preserved.
* Source facts and source decisions must not be patched.
* Rendered text, runtime Lua, packaged Lua, bridge payload, and state axes must not change.
* Existing authority ownership must not be bypassed.
* Sealed predecessor artifact bodies must remain read-only.
* Additive amendment is preferred for governance records.
* Fail-loud handling is required for ambiguous, missing, or contradictory read-state findings.
* Minimal diff preservation is required.
* Stale artifacts must be interpreted, not deleted to erase evidence.
* `suppress` retirement/removal and acquisition contract expansion remain non-claims.
* `josa_adaptive`, phrasebook, array acquisition, and runtime-side repair remain closed unless a separate successor plan explicitly opens them.
* Release readiness, deployment readiness, Workshop readiness, and manual in-game validation must not be claimed.

---

## 12. Expected Closeout State

Expected closeout target: `complete`, only if all hard gates pass.

Allowed complete closeout token:

```text
closed_with_acquisition_lexical_current_readpoint_reconciled
```

Complete closeout may claim only:

```text
선행 Acquisition Lexical Current Inventory / Readpoint Audit을 입력으로,
acquisition lexical 관련 top-doc closeout / lower plan / stale artifact /
validator-utility readpoint의 current-vs-historical 읽기 방식이 모순 없이 정렬되었다.
```

Complete closeout requires:

* Input authority lock pass with the complete predecessor tuple in `input_authority_lock.json`: logical surface `507`, raw occurrence `8828`, classified `507`, `UNCLASSIFIED_BLOCKED_count = 0`, `writer_path_reachable_but_unindexed_count = 0`, `protected_mutation_count = 0`, `current_gate_surface_count = 0`, `current_suppress_validator_surface_count = 3`, JSON parse `20`, JSONL parse `5`, JSONL rows `18961`, parse error count `0`, helper py_compile exit code `0`.
* Template / execution contract branch check recorded in `input_authority_lock.json`.
* Document universe classified with unclassified count `0` in `reconciliation_document_universe.jsonl`.
* Claim universe classified with unclassified count `0` in `acquisition_lexical_contract_claim_disposition_map.jsonl`.
* `blocked_ambiguous = 0` from `read_state_classification_matrix.jsonl.read_state == blocked_ambiguous`.
* Top-doc / lower-plan / stale-artifact / validator-utility contradiction count `0` from `current_vs_stale_contradiction_report.md.contradiction_count`.
* `suppress_current_blocker_count = 0` from the Phase 3 derived condition over `suppress_occurrence_disposition.jsonl`, `suppress_label_to_read_state_crosswalk.json`, and `read_state_classification_matrix.jsonl`.
* `suppress_crosswalk_violation_count = 0`.
* `live_suppress_surface_cross_manifest_mismatch_count = 0`.
* Live suppress validator surface `3` retained as `followup_disposition_candidate` unless a blocked drift closeout is used.
* Non-reopen boundary pass in `non_reopen_boundary_manifest.json` and `forbidden_reopen_scan_report.md`.
* Protected source/rendered/runtime/package/state mutation count `0`.
* Sealed predecessor body mutation count `0`.
* Phase 5 staged draft scan pass and canonical governance docs unchanged before Phase 6 promotion.
* Adversarial review verdict `PASS` before complete closeout or any canonical governance doc promotion.
* Validation ceiling recorded as docs/governance reconciliation only.

Canonical blocked closeout candidates:

```text
blocked_inventory_readpoint_mismatch
blocked_ambiguous_read_state
blocked_due_to_protected_history_mutation
blocked_claim_overreach
blocked_non_reopen_boundary_failed
blocked_protected_surface_mutation_detected
blocked_validation_artifact_parse_failed
blocked_template_recognition_indeterminate
blocked_execution_contract_unavailable_or_closeout_vocabulary_mismatch
blocked_adversarial_review_failed
blocked_cross_manifest_consistency_failed
blocked_canonical_promotion_sequencing_failed
```

If any blocked condition remains, expected closeout is `blocked`, not partial success. If staging artifacts are produced but no canonical doc/readpoint promotion occurs, closeout should be `implemented_only` or `partial` only when the execution contract explicitly permits that vocabulary for the observed state and the non-claim boundary is preserved.
