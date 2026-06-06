# Iris DVF 3-3 Structural Signal Authority Classification Round Plan

> 상태: Draft v0.3-minor-review-applied
> 기준일: 2026-05-29
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> authority input: `최종 종합 로드맵 - Iris DVF 3-3 Structural Signal Authority Classification Round` (2026-05-29 user-provided synthesis)
> 직접 상위 readpoint:
> - 2026-04-29 publish writer authority / `FUNCTION_NARROW` and `ACQ_DOMINANT` blanket isolation forbidden seal
> - 2026-05-19 `Runtime Payload Enum Rename Scope Round` Branch B/B1 closeout, current runtime payload vocabulary `adopted/unadopted`
> - 2026-05-23 current runtime chunk identity seal
> - 2026-05-27 default compose current authority source-path guard
> - 2026-05-27 `Structural Signal Current Referent Inventory and Anchor Recovery Round` `blocked_missing_anchor`
> - 2026-05-28 `Structural Signal Missing Anchor Authority Resolution Round` Branch B `closed_with_authoritative_reconstruction_adopted`
> - 2026-05-29 `Structural Signal Scope Split Seal Round` `closed_with_structural_signal_scope_split_sealed_observer_only`
> 계획 형식: `docs/PLAN_TEMPLATE.md`
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md` because the current repository/session instructions require `PLAN_TEMPLATE.md` for implementation plans. `PLAN_TEMPLATE.md` is an execution-plan scaffold only, not semantic authority over `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md`.
> 실행 상태: planning authority only. 이 문서는 structural signal occurrence authority classification round를 열기 위한 실행 계획이며, 작성 시점에는 runtime Lua, generated runtime artifacts, rendered text, source decisions, facts, publish_state, quality_state, runtime_state, deployed state, release state, or closeout state를 변경하지 않는다.

---

## 1. Objective

이번 execution plan의 목적은 current checkout 안의 structural signal occurrence가 publish / quality / runtime writer 권한으로 오독되지 않도록 occurrence별 authority class를 봉인하는 것이다.

핵심 질문:

```text
각 current structural signal occurrence는 writer 권한을 갖는가,
아니면 observer / report / preview / historical / diagnostic / test 계열의 non-writer occurrence인가?
```

이 round는 structural signal token의 존재 여부를 다시 문제 삼지 않는다. 문제는 `FUNCTION_NARROW`, `ACQ_DOMINANT`, `BODY_LACKS_ITEM_SPECIFIC_USE`, `SECTION_FUNCTION_NARROW`, structural reclassification / readpoint 관련 occurrence가 report, preview, diagnostic, test, doc, staging, tool surface에 흩어진 상태에서, 각 occurrence의 authority class가 봉인되어 있지 않다는 점이다.

Round id:

```text
structural_signal_authority_classification_round
```

Round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/
```

Expected success closeout branch:

```text
closed_with_structural_signal_authority_classification_sealed
```

`classified` may be used as summary wording only. It is not a separate closeout branch.

Blocked closeout branches:

```text
blocked_foundation_authority_conflict_unresolved
blocked_foundation_authority_revision_required
blocked_writer_input_disposition_unresolved
blocked_occurrence_inventory_incomplete
blocked_unclassified_occurrence_remaining
blocked_unknown_authority_class_remaining
blocked_forbidden_writer_reach_detected
blocked_writer_misread_unremediated
blocked_frozen_surface_invariant_failed
blocked_sealed_disposition_crosscheck_failed
blocked_validation_failed
blocked_claim_overreach
```

Success may claim only:

```text
current structural signal occurrences were inventoried and classified by authority class or writer-misread outcome
unknown and unclassified occurrence counts are zero
publish / quality / runtime writer misread paths are zero
report-only / preview-only / diagnostic / test / historical occurrences are not mutation candidates
quality / publish / runtime / rendered / Lua / source row surfaces were not mutated
```

Success must not claim:

```text
structural signal disposition complete
ACQ_DOMINANT remeasurement
ACQ_DOMINANT disposition complete
publish mutation review
FUNCTION_NARROW second rollout
missing anchor fully resolved beyond the already adopted Branch B reconstructed observer authority readpoint
corpus identity determinate unless independently proven
MIGV-QA Phase 1 identity pre-gate satisfied by this round
runtime rollout
deployment
Workshop readiness
release readiness
ready_for_release
```

---

## 2. Scope

This is a static classification, authority ledger, writer-reachability, and non-mutation validation round. It may create round-local staging artifacts, classification ledgers, reachability matrices, guard reports, adversarial review output, and closeout documents. It may add strictness-only guards or additive doc readpoint patches only if Phase 4 or Phase 5 finds a concrete writer-misread path.

In scope:

* Phase 1 Branch B reconstructed observer authority confirm / consume / cross-check.
* Phase 2 structural signal identifier universe seal and current occurrence inventory.
* Phase 3 authority class definition seal and writer-misread outcome schema.
* Phase 4 writer reachability matrix.
* Phase 5 occurrence authority classification ledger.
* Phase 6 writer-misread remediation only if forbidden writer reach or writer-misread candidate exists.
* Phase 7 surface separation and frozen-surface validation.
* Phase 8 hard gate.
* Phase 9 adversarial review and evidence-bound closeout.

No filesystem alias is introduced by this round. The round id and artifact root use the same canonical slug:

```text
structural_signal_authority_classification_round
```

Primary structural identifier universe:

```text
FUNCTION_NARROW
ACQ_DOMINANT
BODY_LACKS_ITEM_SPECIFIC_USE
SECTION_FUNCTION_NARROW
LAYER4_ABSORPTION
LAYER4_ABSORPTION_CONFIRMED
structural_signal
structural reclassification
structural flag
violation_type
violation_flags
section signal
structural-reclassification readpoint reference
```

Secondary context token universe:

```text
body_plan
quality_flag
publish_restore
internal_only
```

`secondary_context` occurrences are included in writer-reachability and context inventory. They still receive terminal classification sufficient to drive `unknown = 0` and `unclassified = 0`, but they must not be promoted into structural authority solely because a context token appears near a structural signal.

Allowed artifact families:

```text
phase1_foundation/*
phase2_inventory/*
phase3_class_definition/*
phase4_writer_reachability/*
phase5_classification/*
phase6_remediation/*
phase7_validation/*
phase8_hard_gate/*
phase9_closeout/*
artifact_hash_manifest.json
```

### Explicitly Out Of Scope

* `ACQ_DOMINANT` current-baseline remeasurement.
* `ACQ_DOMINANT` publish mutation review.
* `FUNCTION_NARROW` second rollout.
* `FUNCTION_NARROW` / `ACQ_DOMINANT` blanket isolation reopen.
* Structural signal disposition completion.
* Missing anchor recovery, old artifact restoration, or corpus identity declaration beyond Phase 1 foundation disposition.
* Source expansion.
* Quality / publish decision stage redesign.
* Default compose authority input expansion.
* Rendered text mutation.
* Runtime Lua regeneration.
* Packaged Lua mutation.
* Source facts row content mutation.
* Source decisions row content mutation.
* `quality_state`, `publish_state`, or `runtime_state` mutation.
* `quality_baseline_v4` mutation.
* Browser / Wiki / Tooltip behavior change.
* Sealed artifact body direct replacement.
* Deployment, Workshop readiness, release readiness, or `ready_for_release`.

---

## 3. Non-Goals

This plan does not attempt to:

* Rejudge the semantic validity of `FUNCTION_NARROW`, `ACQ_DOMINANT`, or structural flags.
* Treat report-only structural flags as cleanup or mutation targets.
* Treat preview artifacts as default compose authority.
* Treat diagnostic reports as quality / publish writer inputs.
* Treat test fixtures as production authority.
* Treat missing Phase D pair/readpoint references as current authority.
* Reopen the 2026-04-29 publish writer authority seal.
* Relax the default compose data-root guard.
* Redefine GUARD-A.
* Change runtime consumers or user-facing output behavior.
* Claim runtime behavior preservation beyond explicit static and non-mutation evidence.

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` remains top authority. Iris remains a 100% Lua wiki-style module and must not become a recommendation, gameplay policy, or cross-module authority system.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are current governance readpoints.
* Current checked-in readpoints as of this plan identify the 2026-05-28 Branch B reconstructed observer authority and the 2026-05-29 scope split seal as the latest structural signal readpoints.
* Phase 1 foundation is fixed to the current checked-in readpoint:

```text
Branch B reconstructed observer authority basis, consume-only
```

Branch B reconstructed observer authority root:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/
```

* Phase 1 must confirm, consume, and cross-check the Branch B reconstructed observer authority. It must not reopen the foundation choice.
* A live compose `body_plan` basis may appear only as a non-superseding explanatory lens. It may not supersede, narrow, repoint, or replace Branch B inside this classification round.
* If authority must be re-anchored to live compose `body_plan`, this plan must block and a separate authority re-resolution / foundation authority revision round must be opened.
* Forbidden Phase 1 foundation action:

```text
supersede / narrow / repoint Branch B reconstructed observer authority
```

Writer-input assumptions:

* `writer_input` is not a legitimate terminal authority class in this non-mutation classification round.
* The schema may use `intended_writer_input`, `writer_misread_violation`, and `writer_misread_remediation_target` as outcome fields.
* `writer_misread_violation = true` is a violation outcome and must be remediated or blocked.
* No Phase 5 ledger schema may treat `writer_input` as a success-state class.

Non-mutation assumptions:

* Runtime Lua is render-only for this round.
* Validators, report builders, preview builders, Lua bridge, Browser/Wiki consumer, and test fixtures are not writer authority.
* Source facts, source decisions, rendered text, runtime Lua, packaged Lua, `quality_state`, `publish_state`, `runtime_state`, and `quality_baseline_v4` remain frozen.
* `FUNCTION_NARROW` and `ACQ_DOMINANT` blanket isolation reopen remains forbidden.
* `ACQ_DOMINANT` publish candidacy is not evaluated in this round.
* For this round, `ACQ_DOMINANT` occurrences are classification-only and `mutation_candidate = false` unless an unintended writer-misread path is found. If such a path is found, the round blocks or remediates the misread path without opening publish mutation review.
* Publish mutation review is not opened by this plan.

Current deployable runtime invariants to verify in Phase 7:

```text
manifest + Chunk001..011
row_count 2105
runtime_state adopted 2084 / unadopted 21
monolith absent
current_runtime_hash_manifest sha256 = 790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171
```

Historical / source / semantic references are comparison-only and must not be used as current deployable runtime hard gates:

```text
0390272b... = historical staged comparison-only readpoint
publish split internal_only 617 / exposed 1467 = source/semantic reference, excluded from current runtime hard gate
quality split strong 1316 / adequate 0 / weak 768 = source/semantic reference, excluded from current runtime hard gate
```

---

## 5. Repository Areas Affected

### Code

* `Iris/build/description/v2/tools/build/*` only if Phase 6 finds a concrete writer-misread path requiring a strictness-only guard.
* `Iris/build/description/v2/tests/*` only if Phase 6 adds or updates guard tests.

### Docs

* `docs/Iris/iris-dvf-3-3-structural-signal-authority-classification-round-plan.md`
* `docs/DECISIONS.md` only as a Phase 9 addendum if required.
* `docs/ARCHITECTURE.md` only as a Phase 9 addendum if required.
* `docs/ROADMAP.md` only as a Phase 9 addendum if required.

### Config

* None expected.

### Generated Artifacts

* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase1_foundation/round_opening_manifest.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase1_foundation/authority_inputs.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase1_foundation/predecessor_disposition.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase1_foundation/non_mutation_baseline.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase1_foundation/forbidden_claims.md`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase2_inventory/identifier_universe_seal.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase2_inventory/occurrence_inventory.jsonl`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase2_inventory/occurrence_summary.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase2_inventory/surface_kind_summary.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase2_inventory/unclassified_initial.jsonl`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase3_class_definition/authority_class_definition_seal.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase3_class_definition/writer_input_disposition_decision.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase3_class_definition/classification_schema.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase4_writer_reachability/writer_reachability_matrix.jsonl`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase4_writer_reachability/writer_reachability_summary.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase4_writer_reachability/forbidden_writer_reach_candidates.jsonl`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase4_writer_reachability/non_writer_surface_summary.md`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase5_classification/authority_classification_ledger.jsonl`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase5_classification/authority_classification_summary.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase5_classification/mutation_candidate_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase5_classification/unknown_zero_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase5_classification/sealed_disposition_crosscheck.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase6_remediation/remediation_manifest.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase6_remediation/guard_delta_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase6_remediation/doc_readpoint_patch_manifest.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase6_remediation/post_remediation_writer_reachability_matrix.jsonl`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase7_validation/json_parse_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase7_validation/python_unittest_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase7_validation/lua_syntax_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase7_validation/non_mutation_hash_diff_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase7_validation/contract_delta_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase7_validation/surface_separation.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase7_validation/frozen_invariant_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase8_hard_gate/hard_gate_report.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase8_hard_gate/fail_loud_blockers.jsonl`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase9_closeout/adversarial_review.md`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase9_closeout/closeout.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase9_closeout/closeout.md`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase9_closeout/top_doc_update_decision.json`
* `Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/phase9_closeout/artifact_hash_manifest.json`

---

## 6. Planned Changes

### Change 1 - Phase 1 Branch B Foundation Confirm / Consume / Cross-Check

Purpose:

Confirm the fixed Branch B reconstructed observer authority foundation, consume it read-only, and block if any artifact identity or consume-only invariant fails.

Files:

* `phase1_foundation/round_opening_manifest.json`
* `phase1_foundation/authority_inputs.json`
* `phase1_foundation/predecessor_disposition.json`
* `phase1_foundation/non_mutation_baseline.json`
* `phase1_foundation/forbidden_claims.md`

Implementation Notes:

* Record round id `structural_signal_authority_classification_round`.
* Record evidence root.
* Record `selected_foundation = branch_b_reconstructed_observer_authority_consume_only`.
* Confirm the 2026-05-28 Branch B reconstructed observer authority and the 2026-05-29 scope split seal as direct predecessor readpoints.
* Treat live compose `body_plan` only as a non-superseding explanatory lens when needed. It cannot supersede, narrow, repoint, or replace Branch B in this round.
* If execution requires live compose `body_plan` to become authority foundation, block with `blocked_foundation_authority_revision_required` and open a separate authority re-resolution / foundation authority revision round.
* Record normal predecessor relation as:

```text
predecessor_relation = consumed_readonly_predecessor
```

* If predecessor identity, artifact identity, or consume-only status conflicts with the current readpoint, record `predecessor_relation = blocked_dependency` and do not run Phase 2.
* Confirm `ACQ_DOMINANT` remeasurement and publish mutation review are absent from the opening manifest.
* Do not run Phase 2 until Branch B artifact identity and consume-only status are confirmed.
* Record `no_filesystem_alias_introduced = true`.

Validation:

* Foundation is fixed to Branch B reconstructed observer authority consume-only.
* `authority_inputs.json` separates observer authority from writer authority.
* `authority_inputs.json` does not list live compose `body_plan` as replacement foundation.
* Branch B consume-only invariant is present.
* Forbidden claims are written before inventory starts.

---

### Change 2 - Phase 2 Identifier Universe Seal and Occurrence Inventory

Purpose:

Inventory all current structural signal occurrences under the sealed identifier universe.

Files:

* `phase2_inventory/identifier_universe_seal.json`
* `phase2_inventory/occurrence_inventory.jsonl`
* `phase2_inventory/occurrence_summary.json`
* `phase2_inventory/surface_kind_summary.json`
* `phase2_inventory/unclassified_initial.jsonl`

Implementation Notes:

* Scan generated artifacts, docs, tests, tools, runtime, staging, and source data as separate surface groups.
* Record path plus line number or JSON pointer for every occurrence.
* Use a deterministic `occurrence_id` format such as `ssa-000001`.
* Initial `unknown` is allowed, but only before closeout.
* Prior occurrence counts may be reference data only; current checkout scan is authoritative for this round.
* For `structural reclassification` and `structural-reclassification readpoint reference` occurrences, assign one `referent_kind`:

```text
reconstructed_current
historical_phase_d
legacy_readpoint_ref
not_applicable
unknown
```

* `ACQ_DOMINANT` count in this phase is classification inventory only. It is not residual/current-baseline remeasurement.

Minimum occurrence schema:

```json
{
  "occurrence_id": "ssa-000001",
  "path": "...",
  "line_or_json_pointer": "...",
  "token": "...",
  "token_tier": "primary_structural|secondary_context",
  "surface_kind": "report|preview|diagnostic|test|historical|tool|data|runtime|doc|unknown",
  "referent_kind": "reconstructed_current|historical_phase_d|legacy_readpoint_ref|not_applicable|unknown",
  "read_context": "...",
  "candidate_authority_class": "unknown",
  "writer_reach_candidate": false,
  "mutation_candidate_candidate": false,
  "notes": "..."
}
```

Validation:

* Inventory generation is deterministic across repeated runs.
* JSON and JSONL parse passes.
* Duplicate occurrence id count is zero.
* Missing path / line / JSON pointer count is zero.
* Structural reclassification occurrence with `referent_kind = unknown` blocks closeout.
* `ACQ_DOMINANT` scan report records `remeasurement_performed = false`.

---

### Change 3 - Phase 3 Authority Class Definition and Writer-Misread Outcome Seal

Purpose:

Seal terminal authority classes and represent writer misread as a violation outcome, not a success-state authority class.

Files:

* `phase3_class_definition/authority_class_definition_seal.json`
* `phase3_class_definition/writer_input_disposition_decision.json`
* `phase3_class_definition/classification_schema.json`

Implementation Notes:

* Common terminal classes:

```text
observer_only
report_only
preview_only
historical
diagnostic
test
unknown
```

* `writer_input` is not a terminal authority class in this non-mutation round.
* Track writer-related outcomes with explicit fields:

```text
intended_writer_input
writer_misread_violation
writer_misread_remediation_target
```

* `intended_writer_input` must be false for all occurrence rows in a successful non-mutation closeout.
* `writer_misread_violation = true` requires Phase 6 remediation or blocked closeout.
* Final ledger schema is blocked until `writer_input_disposition_decision.json` exists.

Validation:

* Class definitions are mutually exclusive.
* The schema can express writer-misread target count separately from ordinary non-writer class counts.
* The schema does not allow `writer_input` as a passing terminal class.
* `FUNCTION_NARROW` / `ACQ_DOMINANT` sealed disposition boundaries are not reopened.

---

### Change 4 - Phase 4 Writer Reachability Matrix

Purpose:

Determine whether each occurrence reaches any writer graph.

Files:

* `phase4_writer_reachability/writer_reachability_matrix.jsonl`
* `phase4_writer_reachability/writer_reachability_summary.json`
* `phase4_writer_reachability/forbidden_writer_reach_candidates.jsonl`
* `phase4_writer_reachability/non_writer_surface_summary.md`

Implementation Notes:

* Evaluate:

```text
default compose input path
quality/publish decision stage input path
report builder to mutation queue path
preview artifact to default writer path
diagnostic resolver mode to canonical write path
test fixture to production authority path
staging artifact to current data-root guard bypass path
structural-reclassification readpoint reference to current writer authority path
```

* Record per-occurrence reach axes:

```json
{
  "occurrence_id": "ssa-000001",
  "default_compose_writer_reach": false,
  "quality_publish_writer_reach": false,
  "runtime_writer_reach": false,
  "lua_bridge_writer_reach": false,
  "browser_wiki_consumer_reach": false,
  "diagnostic_mode_only": true,
  "test_only": false,
  "historical_only": false,
  "authority_class_preliminary": "diagnostic",
  "writer_misread_candidate": false
}
```

Validation:

* Forbidden writer reach candidate count is zero, or Phase 6 becomes mandatory.
* Diagnostic, test, and historical occurrences are proven not to enter default writer paths.
* Static path analysis is supplemented by CLI mode / entrypoint inspection where relevant.

---

### Change 5 - Phase 5 Occurrence Authority Classification

Purpose:

Join the Phase 2 inventory and Phase 4 writer reachability matrix into final occurrence classification.

Files:

* `phase5_classification/authority_classification_ledger.jsonl`
* `phase5_classification/authority_classification_summary.json`
* `phase5_classification/mutation_candidate_report.json`
* `phase5_classification/unknown_zero_report.json`
* `phase5_classification/sealed_disposition_crosscheck.json`

Implementation Notes:

* Assign final `authority_class` or `writer_misread_outcome` per occurrence.
* Explicitly set `mutation_candidate`; successful closeout requires `mutation_candidate = false` for every row.
* Track `writer_misread_remediation_target` separately from `mutation_candidate`.
* Record `allowed_reason` or `blocked_reason`.
* Classify structural reclassification referents with the triad rule:

```text
reconstructed_current -> observer_only, sealed authority, downgrade forbidden
historical_phase_d -> historical / provenance
legacy_readpoint_ref -> historical / diagnostic, writer reach triggers Phase 6 remediation
```

* `ACQ_DOMINANT` occurrence classification is an inventory/classification act only:

```text
remeasurement_performed = false
ACQ_DOMINANT publish candidacy is not evaluated in this round
ACQ_DOMINANT mutation_candidate = false unless an unintended writer-misread path is found
unintended writer-misread path handling = block or remediate without opening publish mutation review
```

Example ledger row:

```json
{
  "occurrence_id": "ssa-000001",
  "token": "ACQ_DOMINANT",
  "path": "...",
  "line_or_json_pointer": "...",
  "surface_kind": "report",
  "referent_kind": "not_applicable",
  "authority_class": "report_only",
  "writer_reach": false,
  "intended_writer_input": false,
  "writer_misread_outcome": false,
  "writer_misread_remediation_target": false,
  "mutation_candidate": false,
  "allowed_reason": "report-only structural occurrence; no quality/publish/runtime writer reach",
  "sealed_by_round": "structural_signal_authority_classification_round"
}
```

Validation:

* `unknown = 0`.
* `unclassified = 0`.
* `mutation_candidate = 0`.
* `writer_misread_remediation_target = 0` after Phase 6, or blocked closeout.
* `FUNCTION_NARROW` residual remains report / preview structural flag only.
* `ACQ_DOMINANT` publish candidacy is not evaluated by this classification round.
* `reconstructed_current` rows are not downgraded to historical.

---

### Change 6 - Phase 6 Writer-Misread Remediation

Purpose:

Block any concrete path that can misread structural signal occurrences as publish / quality / runtime writer authority.

Files:

* `phase6_remediation/remediation_manifest.json`
* `phase6_remediation/guard_delta_report.json`
* `phase6_remediation/doc_readpoint_patch_manifest.json`
* `phase6_remediation/post_remediation_writer_reachability_matrix.jsonl`
* Guard or test files only if a concrete writer-misread path exists.

Implementation Notes:

* Run only when Phase 4 or Phase 5 finds forbidden writer reach or writer-misread candidates.
* Allowed remediation:

```text
queue builder reject
preview-as-default-authority fail-loud guard
diagnostic output root enforcement
fixture path reject
additive doc readpoint wording patch
source-path guard strictness-only strengthening
missing pair/readpoint historical/diagnostic relabel or reject
```

* Allowed fail-loud codes:

```text
STRUCTURAL_SIGNAL_AUTHORITY_CLASS_REJECTED_WRITER_INPUT
STRUCTURAL_SIGNAL_REPORT_REJECTED_AS_MUTATION_CANDIDATE
STRUCTURAL_SIGNAL_PREVIEW_REJECTED_AS_DEFAULT_AUTHORITY
STRUCTURAL_SIGNAL_DIAGNOSTIC_REJECTED_CANONICAL_WRITE
STRUCTURAL_SIGNAL_TEST_FIXTURE_REJECTED_PRODUCTION_AUTHORITY
```

* Every added fail-loud guard must include:

```text
negative fixture: forbidden writer reach is rejected
positive fixture: explicit diagnostic/test mode remains usable
```

Validation:

* Pre/post writer reachability diff exists.
* Forbidden writer reach count is zero after remediation.
* Writer-misread count is zero after remediation.
* Explicit diagnostic and test modes still work.
* Each new guard has both negative and positive fixture coverage.
* Default current writer path is not widened.

---

### Change 7 - Phase 7 Surface Separation and Frozen-Surface Validation

Purpose:

Prove this round is authority classification only and does not mutate DVF output surfaces.

Files:

* `phase7_validation/json_parse_report.json`
* `phase7_validation/python_unittest_report.json`
* `phase7_validation/lua_syntax_report.json`
* `phase7_validation/non_mutation_hash_diff_report.json`
* `phase7_validation/contract_delta_report.json`
* `phase7_validation/surface_separation.json`
* `phase7_validation/frozen_invariant_report.json`

Implementation Notes:

* Separate report-only, preview-only, diagnostic, test, historical, observer-only, and writer surfaces.
* Verify Branch B reconstructed observer authority remains consume-only:

```text
reconstruction_hash_manifest verified
artifact hashes listed inside reconstruction_hash_manifest verified
runtime_state adopted 2084 / unadopted 21
current runtime chunk identity exact match
forbidden writer fields absent
```

* Verify current deployable runtime invariant using the current runtime baseline seal:

```text
manifest + Chunk001..011
row_count 2105
runtime_state adopted 2084 / unadopted 21
monolith absent
current_runtime_hash_manifest sha256 = 790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171
```

* Keep historical / source / semantic references out of the current runtime hard gate:

```text
0390272b... = historical staged comparison-only readpoint
publish split internal_only 617 / exposed 1467 = source/semantic reference only
quality split strong 1316 / adequate 0 / weak 768 = source/semantic reference only
```

* Record the `ACQ_DOMINANT` classification scan invariant:

```text
remeasurement_performed = false
ACQ_DOMINANT publish candidacy is not evaluated in this round
ACQ_DOMINANT mutation_candidate = false unless an unintended writer-misread path is found
unintended writer-misread path handling = block or remediate without opening publish mutation review
```

* Confirm zero delta for:

```text
rendered text
runtime Lua
packaged Lua
source facts row content
source decisions row content
quality_state
publish_state
runtime_state
quality_baseline_v4
```

* `quality_state`, `publish_state`, and `runtime_state` zero-delta validation compares current checked-in payload fields only. It must not import historical/source semantic split counts as current runtime invariants.

Validation:

* JSON / JSONL parse pass.
* Python unittest pass.
* Lua syntax pass.
* Non-mutation hash diff pass.
* Current runtime baseline invariant pass uses `current_runtime_hash_manifest`, not the historical staged hash.
* Branch B consume-only foundation invariant pass.
* Browser / Wiki / Tooltip behavior untouched by file diff and scope report.

---

### Change 8 - Phase 8 Hard Gate

Purpose:

Convert all closeout prerequisites into explicit pass/fail gates.

Files:

* `phase8_hard_gate/hard_gate_report.json`
* `phase8_hard_gate/fail_loud_blockers.jsonl`

Implementation Notes:

* Required pass axes:

```text
unknown = 0
unclassified = 0
writer_misread = 0
forbidden_writer_reach = 0
mutation_candidate = 0
writer_misread_remediation_target = 0
structural_reclassification_referent_kind_unknown = 0
Branch B consume-only foundation invariant pass
current runtime baseline invariant pass
frozen surface invariant pass
sealed disposition cross-check pass
JSON/JSONL parse pass
Python unittest pass
Lua syntax pass
```

Validation:

* Any failed axis forces blocked closeout.
* Partial pass must not be recorded as success.

---

### Change 9 - Phase 9 Adversarial Review and Closeout

Purpose:

Close the round without overclaiming mutation, remeasurement, rollout, or disposition completion.

Files:

* `phase9_closeout/adversarial_review.md`
* `phase9_closeout/closeout.json`
* `phase9_closeout/closeout.md`
* `phase9_closeout/top_doc_update_decision.json`
* `phase9_closeout/artifact_hash_manifest.json`

Implementation Notes:

* Directly rebut:

```text
ACQ_DOMINANT is a publish mutation candidate because it appears in reports
FUNCTION_NARROW preview occurrence opens a second rollout
test fixture structural flag is current writer input
diagnostic report is consumed by quality/publish writer
authority classification complete means structural signal disposition complete
missing anchor is fully resolved
runtime/deployment/release readiness is established
```

* Decide whether top-doc updates are required:
  * if yes, addendum-only;
  * if no, record `top_doc_update_not_required`.
* Use the single success closeout branch:

```text
closed_with_structural_signal_authority_classification_sealed
```

Validation:

* Adversarial review passes.
* Closeout non-claims are explicit.
* No runtime rollout, deployment, Workshop readiness, release readiness, or `ready_for_release` is claimed.

---

## 7. Validation Plan

### Automated Validation

Required commands for execution closeout:

```powershell
uv run python <round artifact/json-jsonl parse script>
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Required generated validation reports:

* Static occurrence inventory determinism report.
* JSON / JSONL parse report.
* Structural reclassification referent triad report.
* Writer reachability summary.
* Authority classification summary.
* Unknown zero report.
* Mutation candidate report.
* Branch B consume-only foundation invariant report.
* Current runtime baseline invariant report.
* Sealed disposition cross-check.
* Non-mutation hash diff report.
* Frozen invariant report.
* Hard gate report.

### Manual Validation

* Review `authority_inputs.json` for Branch B consume-only foundation / writer authority separation.
* Review `writer_input_disposition_decision.json` to confirm `writer_input` is not a passing terminal class.
* Review `referent_kind` samples for reconstructed current, historical Phase D, and legacy readpoint references.
* Review `authority_classification_ledger.jsonl` samples across all surface classes.
* Review adversarial scenarios in Phase 9.

### Validation Limits

This execution will not perform:

* In-game validation.
* Deployment validation.
* Multiplayer validation.
* Long-session runtime validation.
* External ecosystem compatibility sweep.
* Full runtime equivalence validation.
* Workshop readiness validation.
* Release readiness validation.
* MIGV-QA Phase 1 identity pre-gate validation.
* Corpus identity determinate proof unless independently opened and proven.

---

## 8. Risk Surface Touch

### Authority Surface

Touched. This round classifies structural signal occurrences by authority class. It must not redesign compose/body_plan authority or publish writer authority.

### Runtime Behavior Surface

None expected. Runtime Lua, rendered text, packaged Lua, Browser/Wiki/Tooltip behavior, and runtime consumer behavior remain frozen.

### Compatibility Surface

None expected. Diagnostic and test paths must remain available in explicit modes.

### Sealed Artifact Surface

Potentially touched only through new round-local artifacts and additive readpoint patches. Sealed body/hash artifact direct replacement is forbidden.

### Public-Facing Output Surface

None. No Browser, Wiki, Tooltip, rendered text, Lua output, or public-facing copy changes are planned.

---

## 9. Risk Analysis

### Architecture Risk

* Branch B reconstructed observer authority is not confirmed consume-only before inventory and classification.
* Live compose `body_plan` is accidentally treated as authority revision instead of non-superseding explanatory lens.
* Observer/report/preview/diagnostic/test/historical occurrence is silently promoted into writer authority.
* `writer_input` is accidentally used as a passing terminal class instead of a violation outcome.

### Runtime Risk

* Remediation accidentally mutates runtime Lua, packaged Lua, rendered text, or current state fields.
* A diagnostic output path guard incorrectly changes canonical runtime output.
* A test fixture reject path leaks into normal diagnostic usage.

### Compatibility Risk

* Overbroad guards break explicit diagnostic or regression-test workflows.
* Additive docs imply alias removal, artifact obsolete declaration, or current authority expansion.

### Regression Risk

* Identifier universe misses structural occurrence families, invalidating all-occurrence claims.
* Structural reclassification referent triad is not applied consistently.
* Generated report artifacts are confused with current writer inputs.
* Historical readpoint references are misread as live current authority.
* Historical staged hash is confused with the current runtime identity gate.
* Static path review misses dynamic CLI mode behavior.
* Hard gate records partial pass as success.

---

## 10. Rollback Plan

Rollback is limited to artifacts and patches created by this round.

1. Remove or revert the round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_authority_classification_round/
```

2. If Phase 6 added guard or reject code, revert only those guard patches. Existing default compose data-root guard must remain intact.

3. If Phase 9 added docs addenda, revert only the additive docs patch. Historical sealed body edits are forbidden; if such an edit occurs, the round fails and must be reverted.

4. After rollback, rerun:

```powershell
uv run python <round artifact/json-jsonl parse script>
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

5. Recheck non-mutation hash diff and frozen surface invariants. Any baseline delta after rollback is rollback failure.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` current readpoint compliance.
* Iris remains a 100% Lua wiki module and does not become recommendation, gameplay policy, or another module's role.
* Hub & Spoke / SPI boundaries remain intact.
* Runtime Lua remains render-only.
* Single-writer structure remains intact.
* Branch B reconstructed observer authority is consumed read-only and cannot be superseded, narrowed, or repointed inside this classification round.
* Live compose `body_plan` cannot become replacement foundation without a separate authority re-resolution / foundation authority revision round.
* Validator, report builder, preview builder, Lua bridge, Browser/Wiki consumer, and test fixtures are not writer authority.
* Sealed disposition is not redecided.
* `FUNCTION_NARROW` / `ACQ_DOMINANT` blanket isolation reopen remains forbidden.
* `ACQ_DOMINANT` residual remeasurement remains out of scope.
* Publish mutation review remains out of scope.
* Rendered text, runtime Lua, packaged Lua, source facts, source decisions, and state fields remain non-mutation targets.
* `mutation_candidate = 0` is required for success.
* Sealed artifact body direct replacement is forbidden.
* Classification ambiguity, unclassified occurrence, or contradictory authority evidence must block rather than silently fall back.
* Top-doc changes, if any, must be additive readpoint updates only.
* No filesystem alias may be introduced for this round.

---

## 12. Expected Closeout State

Expected closeout:

```text
complete
```

`complete` means this execution plan has produced a current checkout occurrence inventory, structural reclassification referent triad classification, authority class ledger, writer reachability matrix, zero-unknown report, zero-writer-misread report, Branch B consume-only foundation invariant evidence, current runtime baseline invariant evidence, frozen-surface validation evidence, adversarial review, and closeout document within the round-local artifact root.

```text
closed_with_structural_signal_authority_classification_sealed
```

If Branch B consume-only foundation cannot be confirmed, if `writer_input` is treated as a passing terminal class, or if current runtime baseline invariant verification cannot use the current runtime hash manifest, expected closeout becomes:

```text
blocked
```

Success closeout must explicitly preserve these non-claims:

```text
no structural signal disposition completion
no ACQ_DOMINANT remeasurement
no publish mutation review
no FUNCTION_NARROW second rollout
no missing anchor full recovery claim beyond the already adopted Branch B reconstructed observer authority readpoint
no runtime rollout
no deployment
no Workshop readiness
no release readiness
no ready_for_release
```
