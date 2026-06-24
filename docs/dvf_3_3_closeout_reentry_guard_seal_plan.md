# Implementation Plan

> Status: planned / roadmap-derived / WARN review incorporated / PASS review minor revisions incorporated / closeout reentry guard seal / no runtime mutation performed
> 작성일: 2026-06-23
> Roadmap input: `C:/Users/MW/.codex/attachments/b1594479-027f-40f2-b7fc-edaee92df52a/pasted-text.txt` / sha256 `AD5CEC639DA01B60E6E905FD1DBCC94702D2F604756DDE996A7E7417AEEBD6AA`
> Review input: `C:/Users/MW/.codex/attachments/6e67cf9c-0a55-470a-9dca-4726f8238595/pasted-text.txt` / sha256 `1023B47D9DAB90CD1EB25811C9FCAD49A2EBF7029DBBA6EAF25C298DEB39F4CD` / WARN revisions incorporated
> Review input: `C:/Users/MW/.codex/attachments/905013be-cd51-414b-bb08-fd7d1c972650/pasted-text.txt` / sha256 `73B89D055BA2DBC726D11CFAEA91E31421E257011CBF883306775069685E69A7` / PASS with minor revisions incorporated
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Direct plan artifact: `docs/dvf_3_3_closeout_reentry_guard_seal_plan.md`
> Evidence root target: `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/`

---

## 1. Objective

DVF 3-3 Closeout / Reentry Guard Seal을 실행하기 위한 governance plan을 작성한다. 이 계획의 목적은 broad consumer completion, terminal disposition completion, cutover subset completion, pre-apply readiness, live apply authorization, live migration execution completion을 하나의 `complete` claim으로 섞지 못하게 하는 것이다.

이 계획은 Current-Route Baseline / Source-Overlay Repair의 PASS 상태를 다시 실행하거나 확장하지 않는다. Problem 7 full current-route PASS가 Problem 8 / Closeout Guard completion으로 승격되지 않도록 별도 claim boundary와 validator gate를 둔다.

최대 claim은 다음으로 제한한다.

```text
DVF 3-3 closeout claim boundary is axis-qualified.
Broad completion and cutover subset completion are separated.
Predecessor 2105 / 2084 / 21 cannot reenter as current hard gate,
runtime authority, current debt, package authority, or release readiness.
Required-validation guard adoption is governance-only and does not mutate
source / rendered / Lua bridge / runtime / package authority surfaces.
```

이 계획의 완료는 live migration execution, live mutation completion, current authority cutover, release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game QA, semantic quality completion, public-facing text quality acceptance를 의미하지 않는다.

---

## 2. Scope

이 계획은 closeout claim boundary와 predecessor reentry guard를 봉인하는 execution plan이다.

포함 범위:

* closeout claim surface inventory
* claim surface scan universe manifest
* completion vocabulary / claim taxonomy axis 분리
* predecessor `2105 / 2084 / 21` reentry guard
* existing Shared Disposition reentry guard와 신규 Closeout / Reentry guard의 authority relation 판정
* Problem 7 PASS to Closeout Guard completion promotion guard
* broad completion과 cutover subset completion collision guard
* pre-apply readiness to live completion promotion guard
* required-validation manifest / contract-test adoption plan
* full current-route validation mandatory completion gate
* ROADMAP / DECISIONS / ARCHITECTURE / claim boundary docs vocabulary synchronization
* final seal report, no-mutation report, independent review status recording
* canonical seal pending gates: non-Claude independent review, owner-reserved seal, and execution evidence

Primary execution evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/`

Direct documentation artifacts:

* `docs/dvf_3_3_closeout_reentry_guard_seal_plan.md`
* `docs/dvf_3_3_closeout_reentry_claim_boundary.md`
* `docs/dvf_3_3_closeout_reentry_ledger_packet.md`

Expected policy / support docs:

* `docs/completion_vocabulary_separation_policy.md`
* `docs/predecessor_reentry_guard_policy.md`

Roadmap input provenance must be rebound before execution from transient attachment identity into a stable evidence or docs path with sha256 and line count.

### Explicitly Out Of Scope

* live migration execution
* Phase 4 live apply execution
* guarded live apply
* source facts mutation
* decisions mutation
* rendered output mutation
* Lua bridge mutation
* runtime chunk mutation
* package payload mutation
* current authority cutover re-execution
* terminal disposition re-adjudication
* denominator redefinition
* shared disposition ledger re-adoption
* Current-Route Baseline / Source-Overlay Repair reopen
* predecessor 2105 baseline restoration
* old chunks / monolith / legacy bridge reintroduction
* runtime payload enum redefinition
* semantic quality / publish policy change
* UI / Browser / Wiki / Tooltip exposure policy change
* package / release / Workshop / B42 / deployment readiness declaration
* broad consumer universe expansion into live mutation target
* unrelated refactor

---

## 3. Non-Goals

이 계획은 다음을 해결하지 않는다.

* `complete`, `closed`, `sealed`, `PASS`, `ready`, `allowed`, `migrated`, `current`를 하나의 lifecycle vocabulary로 통합하지 않는다.
* `migrated=153`을 live migration execution complete로 해석하지 않는다.
* `phase4_live_apply_allowed=true`를 live mutation complete로 해석하지 않는다.
* Problem 7 full current-route validation PASS를 Closeout / Reentry Guard Seal completion으로 해석하지 않는다.
* predecessor `2105 / 2084 / 21`을 current hard gate, runtime authority, current debt, package authority, release readiness 근거로 복구하지 않는다.
* raw audit / readiness / dry-run / predecessor artifact를 execution authority로 직접 읽지 않는다.
* required-validation manifest adoption을 runtime writer, source writer, rendered writer, package writer처럼 다루지 않는다.
* staging / generated / diagnostic artifact를 current authority로 승격하지 않는다.
* independent review pending 상태를 owner adoption PASS로 대체하지 않는다.
* final seal report를 release, deployment, Workshop, B42, manual QA, semantic quality, public-facing text acceptance claim으로 표현하지 않는다.
* `release_readiness`, `package_readiness`, `workshop_readiness`, `deployment_readiness`, `manual_qa_pass`, `semantic_quality_completion`, `public_text_acceptance`를 valid claim으로 통과시키지 않는다. 이들은 forbidden overclaim class다.
* complete-suffixed source-overlay repair class를 사용하지 않는다. Problem 7은 `source_overlay_repair_current_route_validation_pass` 또는 `problem7_full_current_route_validation_pass`로만 표현한다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 설계 권위다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 2026-06-21 current readpoint를 따른다.
* Iris는 runtime에서 source validation, semantic quality judgment, publish policy judgment, repair, compose regeneration을 수행하지 않는다.
* Runtime / build-time separation은 유지된다.
* DVF 3-3 current authority chain은 `source -> facts -> decisions -> rendered -> Lua bridge -> runtime chunks`로 읽는다.
* Denominator Governance, Terminal Disposition Adjudication, Shared Disposition Ledger Consumption, Current-Route Baseline / Source-Overlay Repair는 각각 닫힌 predecessor readpoint로 소비한다.
* Current-Route Baseline / Source-Overlay Repair PASS는 Closeout / Reentry Guard Seal PASS가 아니다.
* `2105 / 2084 / 21`은 historical / predecessor / comparison / evidence-contract / migration provenance / terminal disposition provenance context에서만 허용된다.
* `2105 / 2084 / 21`이 current hard gate, runtime authority, current debt, package authority, release readiness, required migration target expansion으로 쓰이면 fail-loud 처리한다.
* 모든 closeout claim은 machine-readable claim class를 가져야 한다.
* 단독 `complete` claim은 허용하지 않는다. 반드시 completion axis가 붙어야 한다.
* Taxonomy는 `allowed_claim_classes`와 `forbidden_overclaim_classes`를 분리한다. Forbidden class match는 classified PASS가 아니라 validation violation이다.
* Unmatched completion-bearing token은 `blocked_unclassified`로 처리한다.
* `_complete` suffix는 owning evidence의 `closeout_state`가 `complete` 또는 `canonical_complete`일 때만 허용한다.
* Problem 7 source-overlay repair readpoint는 current-route validation PASS일 수 있으나, Closeout / Reentry Guard Seal 전에는 `closeout_state=partial`로 읽는다.
* Required-validation manifest는 governance gate이며 runtime writer가 아니다.
* Existing Shared Disposition reentry guard surface는 owner decision 전까지 read-only predecessor / candidate relation input으로 소비한다. 신규 guard report 신설 또는 기존 guard 재사용은 Branch A/B owner-reserved decision이다.
* Dual reentry authority는 허용하지 않는다. Manifest와 final seal은 existing guard와 new guard 중 하나의 owning route 또는 명시적 supersession route만 current governance authority로 둘 수 있다.
* Full current-route validation is mandatory for final guard seal completion. The expected baseline is `PASS / 103 tests` or a newly pinned manifest baseline after approved changes.
* Any approved successor pinned baseline must include `baseline_id`, approving artifact path, command, expected test count, reason for replacing `PASS / 103 tests`, and owner approval status.
* Branch A/B guard attribution must be resolved before Phase 5 manifest adoption. If unresolved, Phase 5 remains candidate-only or closes as `blocked_dual_reentry_authority_unresolved`.
* No ad-hoc `_complete` suffix exception is allowed outside the taxonomy artifact.
* The roadmap input attachment is drafting provenance only until rebound to a stable docs path or sealed evidence path with line count and sha256.
* Canonical seal remains pending until non-Claude independent review, owner-reserved seal, and execution evidence are all present.
* Existing sealed predecessor artifact는 read-only input이다.
* New staging evidence는 current authority가 아니다.
* Protected source / rendered / Lua bridge / runtime / package surface changed count는 `0`이어야 한다.
* Dirty working tree changes outside this plan must be preserved.
* Missing validator, missing test, missing manifest entry, unclassified claim token, ambiguous predecessor use는 fail-open이 아니라 blocked state다.

---

## 5. Repository Areas Affected

### Code

Expected or candidate offline tooling surfaces:

* `Iris/build/description/v2/tools/build/validate_dvf_3_3_closeout_claim_taxonomy.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_closeout_claim_boundary.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_predecessor_reentry_guard.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_closeout_reentry_guard_seal.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_closeout_claim_taxonomy.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_closeout_claim_boundary.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_predecessor_reentry_guard.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_closeout_reentry_guard_manifest.py`

No runtime Lua, source facts, decisions, rendered output, Lua bridge, runtime chunk, or package payload mutation is planned.

### Docs

Direct plan artifact:

* `docs/dvf_3_3_closeout_reentry_guard_seal_plan.md`

Expected execution docs:

* `docs/dvf_3_3_closeout_reentry_claim_boundary.md`
* `docs/dvf_3_3_closeout_reentry_ledger_packet.md`
* `docs/completion_vocabulary_separation_policy.md`
* `docs/predecessor_reentry_guard_policy.md`

Canonical docs may be updated only as additive current-readpoint synchronization:

* `docs/ROADMAP.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`

Read-only authority inputs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/consumer_universe_denominator_lock_closeout.md`
* `docs/dvf_3_3_terminal_disposition_adjudication_closeout.md`
* `docs/dvf_3_3_shared_disposition_ledger_consumption_plan.md`
* `docs/dvf_3_3_current_route_baseline_source_overlay_repair_problem7_plan.md`
* `docs/dvf_3_3_live_migration_readiness_execution_plan.md`
* `docs/dvf_3_3_live_consumer_migration_execution_plan.md` - read-only readiness / execution-readiness context only; live consumer migration execution remains unapproved and out of scope for this guard seal round.

### Config

Candidate or live governance config surface:

* `Iris/_docs/round3/current_route_required_validations.json`

This file may receive a Closeout / Reentry Guard Seal required-validation entry only during execution if the manifest adoption gate permits it. Manifest adoption must remain governance-only and must not imply runtime / source / rendered / package mutation.

### Generated Artifacts

All generated evidence should be written under:

* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/`

Expected artifact families:

* `phase0/canonical_roadmap_input.md`
* `phase0/roadmap_input_binding.json`
* `phase0/owner_reserved_seal_requirements.json`
* `phase1/closeout_claim_surface_inventory.json`
* `phase1/closeout_claim_surface_inventory.md`
* `phase1/claim_surface_scan_manifest.json`
* `phase1/problem7_closeout_guard_surface_split_report.json`
* `phase2/dvf_3_3_closeout_claim_taxonomy.json`
* `phase2/final_completion_axis_matrix.json`
* `phase2/completion_vocabulary_separation_report.json`
* `phase3/predecessor_reentry_context_allowlist.json`
* `phase3/predecessor_reentry_guard_report.json`
* `phase3/raw_predecessor_authority_read_report.json`
* `phase3/current_debt_reentry_report.json`
* `phase3/dual_reentry_authority_report.json`
* `phase4/closeout_claim_boundary_guard_report.json`
* `phase4/problem7_to_closeout_guard_promotion_guard_report.json`
* `phase5/closeout_reentry_guard_manifest_adoption_report.json`
* `phase5/closeout_reentry_guard_required_artifacts_manifest.json`
* `phase5/closeout_reentry_guard_required_tests_manifest.json`
* `phase6/docs_claim_taxonomy_consistency_report.json`
* `phase7/final_pinned_command_manifest.json`
* `phase7/final_closeout_reentry_guard_seal_report.json`
* `phase7/final_predecessor_reentry_guard_report.json`
* `phase7/final_no_mutation_report.json`
* `phase7/independent_review_artifact_hash_report.json`

---

## 6. Planned Changes

### Change 0 - Roadmap Provenance / Owner Seal Preflight

Purpose:

Bind transient roadmap input into stable execution provenance and record owner-reserved seal requirements before any guard adoption work begins.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase0/canonical_roadmap_input.md`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase0/roadmap_input_binding.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase0/owner_reserved_seal_requirements.json`

Implementation Notes:

* Copy or bind the roadmap input to a stable docs path or sealed evidence path before Phase 1 inventory work.
* Record source attachment path, stable rebound path, sha256, line count, and binding status.
* Record owner-reserved decisions that cannot be self-sealed by this plan:
  * round identifier
  * Branch A/B guard attribution
  * completion token final string
  * seal gate kind
* Record canonical seal status separately from plan-level PASS status.

Validation:

* Roadmap input binding exists and includes stable path, sha256, and line count.
* Owner-reserved seal requirements are present before Phase 5 manifest adoption.
* Canonical seal status remains pending until non-Claude independent review, owner seal, and execution evidence exist.

---

### Change 1 - Claim Surface Inventory

Purpose:

Identify every DVF 3-3 closeout-related surface that can emit a completion-bearing claim.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase1/closeout_claim_surface_inventory.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase1/closeout_claim_surface_inventory.md`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase1/claim_surface_scan_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase1/problem7_closeout_guard_surface_split_report.json`
* candidate focused inventory test under `Iris/build/description/v2/tests/`

Implementation Notes:

* Search docs, reports, ledger packets, manifest entries, validators, tests, and generated evidence for `complete`, `closed`, `sealed`, `PASS`, `ready`, `allowed`, `migrated`, and `current`.
* Create `claim_surface_scan_manifest.json` before token classification.
* The scan manifest must define `included_roots`, `included_files`, `excluded_roots`, `excluded_files`, `historical_trace_policy`, `required_surface_families`, and `missing_required_surface_family_is_blocking=true`.
* Required surface families are `docs`, `reports`, `ledger_packets`, `required_validation_manifest`, `validators`, `tests`, and `generated_evidence`.
* Record denominator, lifecycle role, evidence root, artifact role, and current/predecessor status for each token occurrence.
* Separate Problem 7 repair artifacts from Closeout / Reentry Guard Seal artifacts.
* Include existing Shared Disposition reentry guard surfaces and live manifest predecessor reentry reports in the inventory.
* Historical trace tokens must be classified as historical or predecessor, not current closeout claims.

Validation:

* Inventory schema validation PASS.
* Claim surface scan manifest validation PASS.
* Missing required surface family count equals `0`.
* Unclassified claim token count equals `0`.
* Problem 7 artifact and Closeout Guard artifact role collision equals `0`.
* Historical-only surface current closeout claim count equals `0`.

---

### Change 2 - Completion Axis Taxonomy / Vocabulary Seal

Purpose:

Replace ambiguous standalone completion vocabulary with explicit claim classes.

Files:

* `docs/completion_vocabulary_separation_policy.md`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase2/dvf_3_3_closeout_claim_taxonomy.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase2/final_completion_axis_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase2/completion_vocabulary_separation_report.json`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_closeout_claim_taxonomy.py`
* candidate focused taxonomy test under `Iris/build/description/v2/tests/`

Implementation Notes:

Taxonomy must split claim classes into allowed classes and forbidden overclaim classes.

Allowed claim classes must include at least:

```text
terminal_disposition_complete
broad_consumer_completion
cutover_subset_completion
pre_apply_readiness_complete
phase4_live_apply_allowed
required_validation_gate_adopted
historical_predecessor_trace
source_overlay_repair_current_route_validation_pass
problem7_full_current_route_validation_pass
```

Forbidden overclaim classes must include at least:

```text
live_migration_execution_complete_without_execution
runtime_authority_current_without_runtime_authority_input
release_readiness
package_readiness
workshop_readiness
deployment_readiness
manual_qa_pass
semantic_quality_completion
public_text_acceptance
```

Each allowed claim class must define allowed denominator, allowed evidence root, forbidden inference, and acceptable surface roles. Each forbidden overclaim class must define the violation reason and blocked closeout state.

Problem 7 source-overlay repair must be represented as `source_overlay_repair_current_route_validation_pass` or `problem7_full_current_route_validation_pass`, not a complete-suffixed source-overlay repair class. Its class definition must include:

```text
closeout_state = partial
pending = closeout_reentry_guard_seal
allowed_evidence = full current-route validation PASS / 103 tests, or successor pinned baseline PASS
forbidden_inference = Problem 7 PASS != repair closeout complete != Closeout Guard completion
```

Validator behavior must be:

```text
allowed_claim_class matched -> classified
forbidden_overclaim_class matched -> violation
unmatched completion-bearing token -> blocked_unclassified
*_complete suffix -> allowed only when owning evidence closeout_state is complete/canonical_complete
```

No ad-hoc `_complete` suffix exception is allowed outside `dvf_3_3_closeout_claim_taxonomy.json`.

The taxonomy must reject standalone `complete` claims.

Validation:

* Every completion-bearing surface has exactly one allowed claim class or one forbidden violation class.
* Forbidden overclaim match count equals `0` in final seal artifacts.
* Standalone `complete` claim count equals `0`.
* `_complete` suffix violation count equals `0`.
* `migrated`, `ready`, `allowed`, and `PASS` are not collapsed into one lifecycle role.
* Broad denominator and subset denominator are not assigned to the same completion class.

---

### Change 3 - Predecessor Reentry Guard

Purpose:

Prevent predecessor `2105 / 2084 / 21` from reentering as current hard gate, runtime authority, or current debt.

Files:

* `docs/predecessor_reentry_guard_policy.md`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase3/predecessor_reentry_context_allowlist.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase3/predecessor_reentry_guard_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase3/raw_predecessor_authority_read_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase3/current_debt_reentry_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase3/dual_reentry_authority_report.json`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_predecessor_reentry_guard.py`
* candidate focused predecessor reentry test under `Iris/build/description/v2/tests/`

Implementation Notes:

Allowed contexts:

* historical predecessor trace
* frozen comparison baseline
* successor evidence contract denominator
* migration provenance
* terminal disposition provenance

Forbidden contexts:

* current hard gate
* current runtime authority
* package authority
* release readiness
* current debt
* required migration target expansion
* old chunks / monolith fallback
* raw predecessor artifact direct execution authority read

Guard axes:

* Axis 1: current hard gate reentry
* Axis 2: runtime authority reentry
* Axis 3: current debt reentry

Guard attribution is owner-reserved until sealed:

```text
Branch A: reuse / extend the existing Shared Disposition reentry guard as the owning governance route.
Branch B: supersede with a new Closeout / Reentry Guard report as the owning governance route.
```

Before owner seal, any new report is candidate-only. The execution must prove dual-reentry-authority equals `0`, either by Branch A reuse, Branch B supersession, or an explicit owner-approved relation record.

Positive-injection fixtures must include:

```text
fixture_predecessor_2105_as_current_hard_gate -> blocked_predecessor_reentry_detected
fixture_predecessor_2084_as_runtime_authority -> blocked_predecessor_reentry_detected
fixture_predecessor_21_as_current_debt -> blocked_predecessor_reentry_detected
fixture_problem7_pass_as_problem8_complete -> blocked_problem7_promotion_path_detected
```

Validation:

* Predecessor reentry violation equals `0`.
* Current hard gate predecessor count direct use equals `0`.
* Runtime authority predecessor artifact direct use equals `0`.
* Current debt claim predecessor count use equals `0`.
* Dual reentry authority count equals `0`.
* Positive-injection tests prove all three axes fail-closed.
* Positive-injection tests prove Problem 7 PASS promotion fails closed.
* Allowed evidence-contract context passes without false positive.
* Protected runtime / source / rendered / package changed count equals `0`.

---

### Change 4 - Closeout Claim Boundary Guard

Purpose:

Make future closeout reports fail-closed when broad completion and cutover subset completion are mixed.

Files:

* `docs/dvf_3_3_closeout_reentry_claim_boundary.md`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase4/closeout_claim_boundary_guard_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase4/problem7_to_closeout_guard_promotion_guard_report.json`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_closeout_claim_boundary.py`
* candidate focused closeout boundary test under `Iris/build/description/v2/tests/`

Implementation Notes:

* Require claim boundary sections in closeout docs and final reports.
* Broad completion claims must cite broad denominator and terminal disposition evidence.
* Cutover subset completion claims must cite cutover subset denominator and cutover-specific evidence.
* Pre-apply readiness must not become live migration completion.
* `phase4_live_apply_allowed=true` must be treated as permission to open a later execution round, not mutation completion.
* Problem 7 full current-route PASS must not become Closeout Guard completion.
* Problem 7 source-overlay repair status must remain `closeout_state=partial` until this guard seal or a successor owner-approved closeout changes it.
* Any `*_complete` suffix in this boundary is valid only when the owning evidence closeout state is `complete` or `canonical_complete`.

Validation:

* Ambiguous complete claim count equals `0`.
* Broad / cutover class collision count equals `0`.
* Pre-apply readiness to live completion promotion count equals `0`.
* Problem 7 PASS to Closeout Guard completion promotion count equals `0`.
* Problem 7 `partial` flattened to `complete` count equals `0`.
* Accidental release / package / Workshop readiness claim count equals `0`.

---

### Change 5 - Required-Validation Manifest / Contract-Test Adoption

Purpose:

Attach Closeout / Reentry Guard Seal to current-route required-validation governance.

Files:

* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase5/closeout_reentry_guard_manifest_adoption_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase5/closeout_reentry_guard_required_artifacts_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase5/closeout_reentry_guard_required_tests_manifest.json`
* candidate manifest focused test under `Iris/build/description/v2/tests/`

Implementation Notes:

* Add or align a Closeout / Reentry Guard Seal required-validation entry only if the execution round authorizes manifest mutation.
* Guard attribution must preserve Branch A/B owner-reserved status. New report creation remains candidate-only before owner seal.
* Branch A/B attribution must be resolved before Phase 5 live manifest adoption. If unresolved, this phase can only produce candidate-only artifacts or close as `blocked_dual_reentry_authority_unresolved`.
* The manifest must not contain both existing Shared Disposition reentry guard and new Closeout / Reentry Guard as independent current owning authorities.
* Required artifacts and required tests must be explicit.
* Owner adoption status and independent review status must be stored separately.
* Governance `adopted_required_gate` must be separated from runtime row vocabulary `adopted`.
* Candidate manifest artifacts must not remain as dual authority beside the live manifest.
* Manifest adoption must not imply runtime / source / rendered / package mutation.
* Non-blocking exception or escape hatch is forbidden.

Validation:

* Live required-validation manifest requires the guard artifacts and tests when adopted.
* Candidate manifest does not replace live authority.
* Required artifact missing count equals `0`.
* Required test missing count equals `0`.
* Owner adoption and independent review are recorded separately.
* Governance adoption and runtime row adoption are not conflated.
* Dual reentry authority count equals `0`.
* Branch A/B attribution status is resolved or the manifest output is candidate-only.
* Manifest adoption creates no runtime mutation claim.
* Full current-route validation is mandatory and exits with code `0`.

---

### Change 6 - Documentation / Ledger Synchronization

Purpose:

Make ROADMAP, DECISIONS, ARCHITECTURE, ledger packet, and claim boundary docs consume the same claim vocabulary.

Files:

* `docs/ROADMAP.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/dvf_3_3_closeout_reentry_claim_boundary.md`
* `docs/dvf_3_3_closeout_reentry_ledger_packet.md`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase6/docs_claim_taxonomy_consistency_report.json`

Implementation Notes:

* ROADMAP should stay a direction board, not an execution log.
* DECISIONS should receive compact current readpoint / non-decision text, not detailed command logs.
* ARCHITECTURE should receive only structural boundary text.
* Each canonical doc gets its own allowed density rule: ROADMAP = Next/Hold direction, DECISIONS = current readpoint/non-decision, ARCHITECTURE = structural boundary only.
* Sealed predecessor decision bodies should not be directly rewritten. Use additive supersession or ledger packet.
* Replace standalone `complete` prose with axis-qualified completion vocabulary where in scope.

Validation:

* Docs claim taxonomy consistency PASS.
* ROADMAP update remains summary-level.
* DECISIONS update remains decision-family / current-readpoint-level.
* ARCHITECTURE update remains structural-boundary-level.
* Per-doc allowed density validation PASS.
* Historical trace is not promoted to current claim.

---

### Change 7 - Final Seal / Independent Review Gate

Purpose:

Produce the final seal evidence and record independent review or explicit external gate status without overclaiming release or runtime readiness.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/final_closeout_reentry_guard_seal_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/final_completion_axis_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/final_predecessor_reentry_guard_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/final_no_mutation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/final_pinned_command_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/independent_review_artifact_hash_report.json`
* `docs/dvf_3_3_closeout_reentry_ledger_packet.md`

Implementation Notes:

* Final report must contain claim boundary, taxonomy state, predecessor reentry state, protected surface no-mutation state, and independent review state.
* Final report must include the full current-route validation result. Guard seal completion requires `PASS / 103 tests` or an approved successor pinned baseline.
* Approved successor pinned baseline must include `baseline_id`, approving artifact path, command, expected test count, replacement reason, and owner approval status.
* Final pinned command manifest must replace `Expected command candidates` before completion can be claimed.
* Owner adoption is not independent review.
* Independent review pending is not failure, but it blocks canonical guard seal PASS.
* Canonical seal requires non-Claude independent review PASS, owner-reserved seal, and execution evidence. Plan-level PASS alone is insufficient.
* Final report must not declare release readiness, package readiness, Workshop readiness, deployment readiness, B42 readiness, manual QA pass, semantic quality completion, or public text acceptance.

Validation:

* Focused guard tests PASS.
* Required-validation manifest check PASS.
* Full current-route validation PASS.
* Approved successor pinned baseline schema validation PASS if the successor baseline route is used.
* Protected surface no-mutation PASS.
* Predecessor reentry violation equals `0`.
* Ambiguous closeout claim equals `0`.
* Broad / cutover completion collision equals `0`.
* Independent review status recorded separately.

---

## 7. Validation Plan

### Automated Validation

Do not claim validation passed unless the exact relevant command exits with code `0`.

Required automated validation families:

* roadmap input stable provenance validation
* owner-reserved seal requirements validation
* claim surface inventory schema validation
* claim surface scan universe completeness validation
* missing required surface family validation
* unclassified claim token validation
* Problem 7 / Closeout Guard role split validation
* closeout claim taxonomy validation
* forbidden overclaim class violation validation
* completion axis matrix validation
* standalone `complete` claim rejection
* `_complete` suffix to owning evidence closeout-state validation
* broad / subset denominator collision validation
* existing Shared Disposition reentry guard to new guard relation validation
* dual reentry authority validation
* predecessor reentry allowlist validation
* current hard gate predecessor direct-use scan
* runtime authority predecessor direct-use scan
* current debt predecessor direct-use scan
* positive-injection fail-closed tests for three predecessor reentry axes
* positive-injection fail-closed test for Problem 7 PASS promotion path
* closeout claim boundary validation
* Problem 7 PASS promotion guard validation
* required-validation manifest artifact/test requirement validation
* docs claim taxonomy consistency validation
* per-doc allowed density validation
* full current-route validation mandatory gate
* approved successor pinned baseline schema validation, if successor baseline route is used
* protected source / rendered / Lua bridge / runtime / package no-mutation validation
* independent review artifact hash validation
* final seal claim boundary validation

Expected command candidates, to be promoted to `phase7/final_pinned_command_manifest.json` before any completion PASS claim:

```powershell
uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_closeout_claim_taxonomy.py --require-complete
```

```powershell
uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_closeout_claim_boundary.py --require-complete
```

```powershell
uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_predecessor_reentry_guard.py --require-complete
```

```powershell
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_closeout*.py"
```

```powershell
uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
```

The exact command list must be pinned in execution artifacts before any PASS claim. If a required tool or command is missing, validation is blocked, not passed.

Full current-route validation is not optional. Completion requires:

```text
uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
exit_code = 0
expected_result = PASS / 103 tests, or an approved successor pinned baseline
```

If the approved successor pinned baseline route is used, the approving artifact must include:

```text
baseline_id
approving_artifact_path
command
expected_test_count
replacement_reason
owner_approval_status
```

Required positive-injection expected states:

```text
fixture_predecessor_2105_as_current_hard_gate -> blocked_predecessor_reentry_detected
fixture_predecessor_2084_as_runtime_authority -> blocked_predecessor_reentry_detected
fixture_predecessor_21_as_current_debt -> blocked_predecessor_reentry_detected
fixture_problem7_pass_as_problem8_complete -> blocked_problem7_promotion_path_detected
```

### Manual Validation

Manual validation is inspection-only:

* inspect roadmap input stable binding path, sha256, and line count
* inspect owner-reserved seal requirements
* review claim taxonomy class names and forbidden inferences
* inspect ambiguous token inventory
* inspect predecessor context allowlist
* inspect false positive handling for historical trace
* inspect Problem 7 to Closeout Guard split report
* inspect required-validation manifest adoption status
* inspect final report wording for release / package / runtime overclaim
* inspect independent review scope and reviewer status
* inspect successor pinned baseline approval packet if used

### Validation Limits

This plan will not validate or claim:

* runtime behavior validation
* manual in-game validation
* multiplayer validation
* long-session runtime validation
* deployment validation
* package release validation
* Workshop readiness validation
* B42 readiness validation
* semantic quality acceptance
* public-facing text quality validation
* live migration execution validation
* source / rendered / runtime mutation equivalence validation
* full external ecosystem compatibility sweep
* full runtime equivalence

---

## 8. Risk Surface Touch

### Authority Surface

Limited / governance-only.

This plan creates claim authority and governance surface. It does not create new source authority, rendered authority, Lua bridge authority, runtime authority, package authority, or release authority.

### Runtime Behavior Surface

None.

No runtime Lua, Browser, Wiki, Tooltip, runtime chunk, Lua bridge, or package payload behavior is changed by this plan.

### Compatibility Surface

Low runtime / Medium internal workflow.

Runtime compatibility is not expected to change. Internal validation and closeout workflow may become stricter and may fail earlier when claims are ambiguous, scan coverage is incomplete, or existing generated evidence uses forbidden overclaim vocabulary.

### Sealed Artifact Surface

Additive only.

Existing sealed predecessor artifacts are read-only inputs. New staging and final seal artifacts may be generated under the evidence root.

### Public-Facing Output Surface

None.

No in-game text, public UI text, README release claim, Workshop copy, release note, or user-facing behavior is changed.

---

## 9. Risk Analysis

### Architecture Risk

* Standalone `complete` may again collapse broad completion and cutover subset completion.
* Claim taxonomy may be too broad and allow unsafe inference.
* Claim taxonomy may be too narrow and misclassify legitimate historical trace.
* Problem 7 current-route PASS may be consumed as Closeout Guard completion.
* Required-validation manifest adoption may be read as current authority mutation.
* Owner adoption and independent review may be collapsed into one status.
* Existing Shared Disposition reentry guard and a new Closeout / Reentry guard may become dual governance authorities if Branch A/B attribution is not sealed.

### Runtime Risk

* Direct runtime risk is intended to remain none.
* Risk appears only if implementation accidentally writes runtime chunk, Lua bridge, rendered, source, or package surfaces while producing guard evidence.
* Any protected surface change invalidates no-mutation claim and blocks guard seal completion.

### Compatibility Risk

* Stricter validators may fail existing docs or tests that previously used ambiguous vocabulary.
* Candidate manifest and live manifest may accidentally remain as dual authority.
* Existing reentry guard and new guard report may accidentally remain as dual authority.
* Current-route required-validation manifest changes may be overread as runtime writer changes.
* Historical trace may produce false positives if role classification is incomplete.
* Successor pinned baseline approval packet may be too weak and look like a validation bypass.

### Regression Risk

* Positive-injection tests may be missing, causing silent PASS on a weak reentry guard.
* `2105 / 2084 / 21` may be allowed in evidence-contract context but leak into current debt wording.
* `migrated=153` may be described as live completion in a generated report.
* `phase4_live_apply_allowed` may be described as live mutation completion.
* Final seal report may accidentally emit release / package / Workshop readiness wording.

---

## 10. Rollback Plan

Rollback is governance artifact rollback, not runtime rollback.

Before manifest adoption:

* discard or archive `Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/`
* discard candidate validators, tests, and docs generated for the guard seal
* keep predecessor artifacts unchanged

After manifest adoption:

* remove or downgrade the Closeout / Reentry Guard Seal required-validation entry from `Iris/_docs/round3/current_route_required_validations.json`
* do not lower validator behavior to advisory-only; remove it from required gate status instead
* preserve failed evidence root as historical / diagnostic evidence
* supersede docs additively rather than editing sealed predecessor decision text
* if Branch B supersession was attempted, restore the previous Shared Disposition reentry guard as the sole owning route or close with `blocked_dual_reentry_authority_unresolved`
* if Branch A reuse was attempted, remove any candidate-only new guard report from required current authority and preserve it as diagnostic evidence

If protected source / rendered / Lua bridge / runtime / package surface mutation is detected:

* stop the round
* record the changed surface in `final_no_mutation_report.json`
* restore only the accidental change after explicit operator approval where required
* close as blocked or rolled back; do not emit guard seal completion

Rollback must not restore predecessor `2105 / 2084 / 21` as current authority, current hard gate, current debt, package authority, or release readiness evidence.

---

## 11. Governance Constraints

* Preserve `docs/Philosophy.md` compliance.
* Preserve Hub & Spoke / SPI boundaries.
* Preserve Iris runtime as Lua-only display surface, not runtime validation / repair / policy engine.
* Preserve runtime / build-time separation.
* Preserve source / facts / decisions / rendered / Lua bridge / runtime chunk / package authority boundaries.
* Preserve FAIL-LOUD behavior.
* No silent fallback, advisory-only degradation, or non-blocking exception escape hatch.
* No source / rendered / Lua bridge / runtime / package mutation in this guard seal round.
* No release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, semantic quality, or public text quality claim.
* No terminal disposition re-adjudication.
* No denominator redefinition.
* No shared disposition ledger re-adoption.
* No Current-Route Baseline / Source-Overlay Repair reopen.
* No predecessor 2105 baseline restoration.
* No old chunks / monolith / legacy bridge reintroduction.
* Taxonomy must keep `allowed_claim_classes` and `forbidden_overclaim_classes` separate.
* Forbidden overclaim class match is a validation violation, not a classified pass.
* `complete` must be axis-qualified.
* `_complete` suffix is allowed only when the owning evidence closeout state is `complete` or `canonical_complete`.
* `PASS` must remain tied to its owning evidence root and lifecycle.
* `ready` / `allowed` must not become mutation completion.
* `migrated` must not become live execution completion.
* Problem 7 PASS must not become Closeout / Reentry Guard completion.
* Problem 7 source-overlay repair must remain `source_overlay_repair_current_route_validation_pass` / `problem7_full_current_route_validation_pass` with `closeout_state=partial` until an owner-approved successor closeout says otherwise.
* `2105 / 2084 / 21` may appear only in allowed predecessor / comparison / evidence-contract / provenance contexts.
* Raw audit / readiness / dry-run / predecessor artifact may not be direct execution authority.
* Required-validation manifest adoption is governance-only.
* Existing Shared Disposition reentry guard and new Closeout / Reentry guard must not coexist as independent current owning authorities.
* Branch A/B guard attribution is owner-reserved until sealed; new guard reports remain candidate-only before owner seal.
* Branch A/B attribution must be resolved before Phase 5 live manifest adoption.
* Candidate manifest must not become dual authority.
* Owner adoption and independent review must be distinct fields.
* Non-Claude independent review is required for canonical seal.
* Owner-reserved seal is required for round identifier, Branch A/B guard attribution, completion token final string, and seal gate kind.
* Full current-route validation must be mandatory for final guard seal completion.
* Approved successor pinned baseline, if used, must include `baseline_id`, approving artifact path, command, expected test count, replacement reason, and owner approval status.
* Roadmap input must be rebound from transient attachment identity into stable docs or evidence provenance with sha256 and line count before execution evidence can support canonical seal.
* Protected surface no-mutation evidence is required.
* Dirty working tree changes outside this plan must be preserved.

---

## 12. Expected Closeout State

Expected plan artifact closeout:

```text
closeout_reentry_guard_seal_plan_written / plan_level_pass
```

Expected execution closeout after implementation:

```text
closeout_reentry_guard_seal_complete
```

`closeout_reentry_guard_seal_complete` is allowed only if:

* closeout claim taxonomy is machine-readable.
* roadmap input stable binding exists with path, sha256, and line count.
* claim surface scan manifest exists and covers all required surface families.
* every completion claim is axis-qualified.
* ambiguous `complete` claim count is `0`.
* forbidden overclaim class violation count is `0`.
* `_complete` suffix violation count is `0`.
* broad completion / cutover subset completion collision count is `0`.
* predecessor `2105 / 2084 / 21` current hard gate reentry count is `0`.
* predecessor `2105 / 2084 / 21` runtime authority reentry count is `0`.
* predecessor `2105 / 2084 / 21` current debt claim reentry count is `0`.
* dual reentry authority count is `0`.
* raw audit / readiness / dry-run / predecessor artifact direct execution authority read count is `0`.
* Problem 7 PASS to Closeout Guard completion promotion path count is `0`.
* Problem 7 `partial` flattened to `complete` count is `0`.
* required-validation manifest requires Closeout / Reentry Guard Seal artifacts and tests when adopted.
* focused guard tests PASS.
* required-validation manifest check PASS.
* full current-route validation exits code `0` with `PASS / 103 tests` or approved successor pinned baseline.
* approved successor pinned baseline packet contains required schema fields if successor baseline route is used.
* protected source / rendered / Lua bridge / runtime / package changed count is `0`.
* ROADMAP / DECISIONS / ARCHITECTURE / claim boundary docs consume the same vocabulary.
* final report does not declare release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, semantic quality completion, or public-facing text quality acceptance.
* independent review or explicit external gate status is recorded separately from owner adoption.
* non-Claude independent review PASS, owner-reserved seal, and execution evidence are present before canonical seal is claimed.

Allowed alternate closeout states:

* `implemented_only`: docs, tools, or tests exist but required validation was not run.
* `blocked_claim_taxonomy_incomplete`: one or more completion-bearing surfaces remain unclassified.
* `blocked_scan_universe_incomplete`: required surface family or scan manifest coverage is missing.
* `blocked_ambiguous_completion_claim`: standalone `complete` or equivalent ambiguous claim remains.
* `blocked_forbidden_overclaim_detected`: release / package / runtime authority / manual QA / semantic quality / public text overclaim appears.
* `blocked_complete_suffix_state_mismatch`: `_complete` suffix appears while owning evidence closeout state is not complete/canonical_complete.
* `blocked_predecessor_reentry_detected`: predecessor `2105 / 2084 / 21` appears in forbidden current context.
* `blocked_dual_reentry_authority_unresolved`: existing and new reentry guards both remain current owning authorities.
* `blocked_problem7_promotion_path_detected`: Problem 7 PASS can still promote to Closeout Guard completion.
* `blocked_manifest_adoption_unapproved`: required-validation manifest adoption lacks approval or remains candidate-only.
* `blocked_full_current_route_validation_failed`: full current-route validation is missing, blocked, or exits non-zero.
* `blocked_successor_baseline_schema_missing`: successor pinned baseline is used without required approval schema.
* `blocked_owner_reserved_seal_pending`: round identifier, Branch A/B attribution, completion token final string, or seal gate kind is not owner-sealed.
* `blocked_independent_review_pending`: non-Claude independent review is missing or pending.
* `blocked_no_mutation_violation`: protected source / rendered / Lua bridge / runtime / package surface changed.
* `revised_plan_needed`: taxonomy, guard axis, or manifest adoption model proves insufficient.

If actual source / rendered / Lua bridge / runtime / package mutation count is greater than `0`, this plan cannot close as `closeout_reentry_guard_seal_complete`.

Final non-claim:

```text
This guard seal does not complete live migration execution, live mutation,
current authority cutover, terminal disposition re-adjudication, denominator
redefinition, package readiness, release readiness, Workshop readiness,
B42 readiness, deployment readiness, manual QA, semantic quality completion,
public-facing text quality acceptance, full runtime equivalence, or full
compatibility preservation.
```
