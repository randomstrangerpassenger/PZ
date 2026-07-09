# Implementation Plan

> Status: planned / roadmap-derived / codebase-inspected / review-required-revisions-incorporated-through-NR3 / governance-only terminology retirement plan / not execution-approved without owner ratification
> 작성일: 2026-07-09
> Round candidate: `dvf_3_3_dvf_system_naming_realignment`
> Roadmap input: `C:/Users/MW/.codex/attachments/9ea7f7f2-b4be-4224-8da1-439bb741dedc/pasted-text.txt` / sha256 `DC3A6104B091758B6FE41E7A1265708610DBA22C02CB270AB1A5CADF7A766181` / lines `817`
> Review input cycle 1 consolidated: `C:/Users/MW/.codex/attachments/b18ea1eb-644b-46af-8e09-1db444c38404/pasted-text.txt` / sha256 `C05852F645FB9C3DB2A5900C50B3A17A7C5BD3511DC0425312272E8D4CB12CE2` / lines `743` / verdict `FAIL` / Required Revisions 1-18 incorporated
> Review input cycle 2 delta: current thread prompt beginning `DVF System Naming Realignment PASS positive fixture` / planned materialization target `Iris/build/description/v2/staging/dvf_3_3_dvf_system_naming_realignment/phase0/review_input_cycle2_delta.md` / sha256 to be recorded by `phase0/input_materialization_report.json` before execution / verdict `review-delta` / NR2-M1, NR2-M2, NR2-M3, NR2-M4, NR-I7 incorporated
> Review input cycle 3 delta: current thread prompt dated 2026-07-10 beginning `NR3-I1 - closeout-guard wording cleanup` / planned materialization target `Iris/build/description/v2/staging/dvf_3_3_dvf_system_naming_realignment/phase0/review_input_cycle3_NR3.md` / sha256 to be recorded by `phase0/input_materialization_report.json` before execution / verdict `FAIL` / NR3-I1, NR3-M1, NR3-M2, NR3-M3 incorporated
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Top authority: `docs/Philosophy.md` / sha256 `938C52E9090C36AF00DAC18B64905E12A4F2390AC238A26121A63A14F81F44B2`
> Current ecosystem readpoints: `docs/DECISIONS.md` / sha256 `678EB5E2A5ACA54F040F556C802AE6AD97669ABB56938414771EA5F91767C3BF`; `docs/ARCHITECTURE.md` / sha256 `FFF017B6DFBECEE602B2C092CF7041E329F04BE47113F8AE1A8A97D901304DA8`; `docs/ROADMAP.md` / sha256 `3B1E84E53E59F9E56EB26E96AF8379967293390D1F93598305A124EA76143410`
> Execution obligations readpoint: `docs/EXECUTION_CONTRACT.md` / sha256 `A185BBD78EB849B0310D9AADC9102CB156B892513266FAC0EC7903EB3D3A9493` / checked `true` / no known conflict
> Direct plan artifact: `docs/dvf_3_3_dvf_system_naming_realignment_plan.md`

---

## 1. Objective

`DVF Core`를 current canonical terminology에서 retired / historical label로 격하하고, Iris 3-3 본문 생산 책임의 current canonical name을 `DVF System` / `DVF Body Compiler` 계열로 재정렬하기 위한 실행 계획을 작성한다.

이 계획은 rename plan이 아니라 retirement plan이다. 실행 목표는 기존 boundary split의 의미를 바꾸지 않고, 다음 canonical read를 문서와 governance tooling에서 검증 가능하게 만드는 것이다.

```text
DVF System
= facts / decisions / profile / body_plan -> rendered 3-3 body

DVF Body Compiler
= role-granularity name for the same body-production responsibility

Iris Artifact Registry
= artifact lifecycle / authority / runtime-package identity pipeline

Legacy Combined DVF Governance Route
= historical polluted governance route surface

retired label: DVF Core
= historical / previous wording only, not current canonical terminology
```

`DVF System`의 responsibility ceiling은 위 production path 하나로 끝난다. `DVF Body Compiler`는 그 동일 책임을 PASS token / routing / validation에서 더 좁게 부르기 위한 role-granularity name이며, `DVF System` 안에 Registry, Runtime Compatibility, Publish Boundary, release, package, public text, semantic quality 책임이 추가로 존재한다는 뜻이 아니다.

최대 성공 claim은 다음으로 제한한다.

```text
DVF System Naming Realignment PASS
= terminology / claim vocabulary governance-only closure
= round-scoped naming claim, not a system-state or release-state claim
```

이 claim은 다음을 의미하지 않는다.

```text
DVF Body Compiler PASS
Registry Authority PASS
Registry Runtime Compatibility PASS
Publish Boundary PASS
runtime compatibility closure
package readiness
release readiness
public text acceptance
source / rendered / Lua bridge / runtime / package mutation
```

Codebase inspection summary:

* `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/DECISIONS.md`에는 아직 current-looking `DVF Core` / `DVF Core PASS` wording이 남아 있다.
* `docs/dvf_3_3_core_registry_boundary_claim_contract.md`는 현재 `DVF Core PASS`, `Registry Authority PASS`, `Registry Runtime Compatibility PASS`, `Publish Boundary PASS`, `Legacy Combined Current Route PASS`의 claim meaning authority다. 새 작업은 이 문서를 삭제하거나 의미 재정의하지 않고 successor / retirement contract를 추가해야 한다.
* `docs/completion_vocabulary_separation_policy.md`는 completion word axis qualification을 이미 요구한다. 새 `DVF System` terminology도 standalone `PASS` claim을 만들 수 없다.
* `docs/dvf_3_3_legacy_combined_route_axis_policy.md`는 `current_route_required_validations.json = legacy_combined_governance_route != DVF Core PASS authority` freeze sentence를 이미 보존한다.
* `Iris/_docs/round3/current_route_required_validations.json`은 live required-validation manifest이며 현재 `required=true`, `enforcement=fail_closed`, `required_artifacts=102`, `required_tests=51`, `non_claims=30`이다.
* `Iris/_docs/round3/round3_run_contract_tests.py`는 current route runner이며, required tests / artifacts를 fail-closed로 소비한다.
* `Iris/_docs/round3/round3_active_core_closure.json`은 current core module `12`개와 allowed tooling module `export_dvf_3_3_lua_bridge` 1개만 current-route import allowlist로 둔다.
* Existing governance tooling already exists for adjacent work:
  * `Iris/build/description/v2/tools/build/dvf_3_3_legacy_combined_route_axis_inventory.py`
  * `Iris/build/description/v2/tools/build/dvf_3_3_core_registry_boundary_claim_contract_closure.py`
  * `Iris/build/description/v2/tools/build/dvf_3_3_core_registry_boundary_required_gate_adoption.py`
  * matching focused tests under `Iris/build/description/v2/tests/`
* `Iris/build/description/v2/staging/` and many Iris build paths are ignored by default and exposed through narrow `.gitignore` allowlists. Any execution that emits new tools, tests, or evidence must include VCS visibility checks.

---

## 2. Scope

This plan covers governance-only terminology retirement, successor claim vocabulary, top-doc realignment, optional machine gate adoption, and closeout verification.

Included scope:

* repo-wide terminology census for `DVF Core`, `DVF Core PASS`, standalone `DVF PASS`, `DVF System`, `DVF Body Compiler`, legacy route labels, and `Iris Artifact Registry` relationship claims
* occurrence disposition classification:
  * `current_canonical_prose`
  * `retirement_self_mention`
  * `sealed_historical`
  * `quoted_prior_claim`
  * `predecessor_trace`
  * `historical_path_or_root`
  * `frozen_machine_token`
  * `machine_schema_compatibility`
  * `template_or_example`
  * `forbidden_current_claim`
  * `unclassifiable_blocker`
* new canonical vocabulary / retired vocabulary policy
* meaning-identity mapping from existing `DVF Core PASS` claim class to successor body compiler claim without changing historical claim meaning
* additive successor claim boundary docs
* top-doc realignment plan for `ARCHITECTURE.md`, `ROADMAP.md`, and append-only `DECISIONS.md`
* scanner / validator plan for forbidden current overclaims
* owner decision intake and ratification schema for D1-D6
* literal occurrence count vs resolved current canonical usage count separation
* predecessor / successor precedence handling for `DECISIONS.md`
* Option A / Option B closeout ceiling separation
* retired-token default-deny rule
* Korean / mixed-language forbidden fixture coverage
* top-doc baseline hash and dirty-overlap fail-closed evidence
* independent review eligibility schema
* owner seal source boundary
* `EXECUTION_CONTRACT.md` checked-state evidence
* protected source / rendered / Lua bridge / runtime chunk / package payload no-mutation proof
* optional current-route required gate adoption if import closure and owner decision allow it

### Explicitly Out Of Scope

* source facts / decisions mutation
* `Iris/build/description/v2/output/dvf_3_3_rendered.json` mutation
* Lua bridge export mutation
* runtime chunk mutation
* package payload mutation
* current route runner rewrite
* manifest physical split
* machine schema breaking rename
* bulk file/path rename
* historical closeout title rename
* sealed decision body rewrite
* required gate meaning redefinition
* Registry Authority PASS closure
* Registry Runtime Compatibility PASS closure
* Runtime Payload Consumer Compatibility closure
* Publish Boundary PASS closure
* Public Text Quality acceptance
* semantic quality acceptance
* package publication
* release / Workshop / B42 / deployment readiness
* manual in-game QA
* ACQ_DOMINANT / FUNCTION_NARROW / Acquisition Lexical follow-up disposition
* Layer4 follow-up execution
* external mod compatibility sweep
* tooling-generated owner decisions
* tooling-generated owner seal records

---

## 3. Non-Goals

This plan does not attempt to prove or achieve:

* `DVF Body Compiler PASS`
* `Registry Authority PASS`
* `Registry Runtime Compatibility PASS`
* `Publish Boundary PASS`
* runtime deployability
* package safety
* release readiness
* public text acceptance
* in-game visibility
* semantic quality completion
* full runtime equivalence
* full historical byte reproducibility

This plan also does not:

* make `DVF System` a new runtime module
* make `DVF System` an umbrella over Registry, Runtime Compatibility, Publish Boundary, release, package, public text, or semantic quality responsibilities
* make Iris Artifact Registry a subcomponent of DVF System
* replace `DVF Core PASS` with `DVF System PASS` by string substitution
* preserve `DVF Core` as current canonical terminology
* erase historical `DVF Core` mentions from sealed traces
* route Runtime Payload Consumer Compatibility or Public Text Quality into DVF System closure
* use current-route validation PASS as release or package readiness evidence

---

## 4. Assumptions

* `docs/Philosophy.md` remains the top authority.
* Iris remains 100% Lua at runtime; Python changes in this plan are offline governance / build tooling only.
* The current Core / Registry / Publish boundary split is already closed and is not reopened.
* `DVF Core` is retired as current terminology, not deleted as a historical term.
* Existing `dvf_core` machine tokens, historical paths, evidence roots, and gate role names may remain as compatibility / historical surfaces.
* Existing sealed decision bodies are not rewritten. `DECISIONS.md` receives only additive successor entries.
* `docs/dvf_3_3_core_registry_boundary_claim_contract.md` remains the predecessor claim meaning authority for the existing claim classes.
* New successor docs must cite predecessor contract hashes instead of redefining prior claim classes in place.
* Current route required-validation manifest remains a combined governance route container.
* Current route runner remains `Iris/_docs/round3/round3_run_contract_tests.py`.
* New current-route tooling must respect `round3_active_core_closure.json`; if import closure requires allowlist expansion, required-gate adoption is blocked and deferred.
* `DVF Body Compiler PASS` is the default proposed canonical successor PASS token for the body compiler claim.
* `DVF System Body Compiler PASS` may be allowed only as an expanded form that names the same body compiler axis; it is not a separate broader claim.
* Bare `DVF System PASS` is forbidden as a current claim in this plan.
* Current prose route label defaults to `Legacy Combined DVF Governance Route PASS`; existing `Legacy Combined Current Route PASS`, `Legacy Combined Governance Route PASS`, and `legacy_combined_governance_route` remain historical / compatibility variants unless owner decides otherwise.
* `Registry Runtime Compatibility PASS` is not renamed in this round; adjacent token drift is observed and reported only.
* Independent review and owner seal are separate governance gates. Machine PASS does not imply either.
* Dirty worktree changes outside this plan are treated as pre-existing user / prior-work changes and must not be reverted by this plan.
* `EXECUTION_CONTRACT.md` was checked for this plan. This plan touches Authority Surface and Sealed Artifact Surface, so execution is treated as validation-required / disclosure-required inside this plan's scope.
* Default proposed terminology values are proposal fields only. Default does not equal owner decision.
* Every owner decision queue entry has one of these states:

```text
proposed_default
owner_ratified
owner_overridden
missing
```

* `owner_ratified` or `owner_overridden` is required before a D1-D6 value may be projected into final closeout fields.
* If any D1-D6 entry remains `proposed_default` or `missing`, final closeout must set:

```text
owner_required_decision_missing=true
canonical_closure=false
full_execution_approved=false
```

* Required owner decisions:

```text
D1: canonical body compiler PASS token selection
D2: expanded alias allowance and primary/expanded token split
D3: Legacy Combined route prose label selection
D4: DECISIONS append-only supersession / predecessor handling
D5: Option A vs Option B enforcement selection
D6: canonical seal eligibility condition
```

* D6 allowed values are restricted to:

```text
canonical_seal_deferred_this_round
doc_normative_canonical_seal_allowed
required_gate_only_canonical_seal
```

* Expected closeout token fields must be projections of owner-ratified or owner-overridden D1-D6 values.
* `DECISIONS.md` append entry must be owner-authored or owner-ratified. Tooling may verify append-only proof but must not author owner decisions.
* Adjacent drift between `Registry Runtime Compatibility PASS` and `Runtime Compatibility PASS` is observed in this round, not silently normalized, unless an owner-ratified decision explicitly includes it.
* `literal_dvf_core_occurrence_count` may remain greater than zero because historical / predecessor / sealed decision text remains.
* `resolved_current_canonical_dvf_core_usage_count` must be zero after disposition and precedence rules are applied.
* `DVF System Naming Realignment PASS` is a round-scoped governance claim, not a system-state claim.

---

## 5. Repository Areas Affected

### Code

Planned offline governance tooling:

* `Iris/build/description/v2/tools/build/dvf_3_3_dvf_system_naming_realignment.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_dvf_system_naming_realignment.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_dvf_system_naming_realignment.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_dvf_system_naming_realignment.py`

Read-only predecessor / adjacent tooling:

* `Iris/build/description/v2/tools/build/dvf_3_3_legacy_combined_route_axis_inventory.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_legacy_combined_route_axis_inventory.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_core_registry_boundary_claim_contract_closure.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_core_registry_boundary_claim_contract_closure.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_core_registry_boundary_required_gate_adoption.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_core_registry_boundary_required_gate_adoption.py`
* `Iris/_docs/round3/round3_run_contract_tests.py`

No runtime Lua code change is planned.

### Docs

Direct plan artifact:

* `docs/dvf_3_3_dvf_system_naming_realignment_plan.md`

Planned execution docs:

* `docs/dvf_3_3_dvf_system_naming_realignment_policy.md`
* `docs/dvf_3_3_dvf_system_naming_realignment_claim_boundary.md`
* `docs/dvf_3_3_dvf_system_naming_realignment_ledger_packet.md`
* `docs/dvf_3_3_dvf_system_naming_realignment_closeout.md`
* optional `docs/dvf_3_3_dvf_system_naming_realignment_walkthrough.md`

Top-doc sync targets:

* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/DECISIONS.md`

Read-only context docs:

* `docs/Philosophy.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/EXECUTION_CONTRACT.md`
* `docs/dvf_3_3_core_registry_boundary_claim_contract.md`
* `docs/dvf_3_3_core_registry_boundary_claim_boundary.md`
* `docs/dvf_3_3_core_registry_boundary_required_gate_adoption_contract.md`
* `docs/dvf_3_3_legacy_combined_route_axis_policy.md`
* `docs/completion_vocabulary_separation_policy.md`

### Config

Possible additive mutation only if Option B enforcement is selected:

* `Iris/_docs/round3/current_route_required_validations.json`

Possible narrow visibility update if new execution artifacts are ignored:

* `.gitignore`

Read-only config:

* `Iris/_docs/round3/round3_active_core_closure.json`
* `Iris/_docs/round3/round3_test_taxonomy.json`

### Generated Artifacts

Planned evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_dvf_system_naming_realignment/`

Expected generated artifacts include:

* `phase0/terminology_occurrence_inventory.json`
* `phase0/terminology_occurrence_inventory.md`
* `phase0/protected_surface_baseline_hashes.json`
* `phase0/current_route_manifest_readpoint.json`
* `phase0/current_route_baseline_precondition_report.json`
* `phase0/predecessor_required_gate_readpoint_freshness_report.json`
* `phase0/vcs_visibility_preflight.json`
* `phase0/top_doc_baseline_hashes.json`
* `phase0/top_doc_dirty_overlap_report.json`
* `phase0/execution_contract_check_report.json`
* `phase0/input_materialization_report.json`
* `phase0/top_doc_closeout_guard_pre_census.json`
* `phase1/canonical_vocabulary_policy.json`
* `phase1/canonical_vocabulary_policy.md`
* `phase1/retired_label_allowance_matrix.json`
* `phase1/owner_decision_ratification_schema.json`
* `phase1/owner_decision_queue.json`
* `phase1/d1_d6_owner_decision_projection_report.json`
* `phase1/roadmap_plan_decision_provenance_map.json`
* `phase2/meaning_identity_mapping_table.json`
* `phase2/claim_boundary_contract.json`
* `phase2/claim_boundary_contract.md`
* `phase2/predecessor_successor_precedence_report.json`
* `phase2/adjacent_token_drift_observation_report.json`
* `phase3/top_doc_patch_plan.json`
* `phase3/top_doc_closeout_guard_compatibility_report.json`
* `phase3/top_doc_current_canonical_scan_report.json`
* `phase3/literal_vs_resolved_usage_report.json`
* `phase3/decisions_append_only_proof.json`
* `phase4/forbidden_claim_scan_report.json`
* `phase4/allowed_retired_label_scan_report.json`
* `phase4/retired_token_default_deny_report.json`
* `phase4/negative_fixture_matrix_report.json`
* `phase4/korean_mixed_language_fixture_report.json`
* `phase4/protected_surface_no_mutation_report.json`
* `phase5/required_gate_adoption_decision_report.json`
* `phase5/option_closeout_ceiling_report.json`
* `phase5/import_closure_compatible_test_design_report.json`
* `phase5/vcs_visibility_required_path_report.json`
* `phase5/current_route_required_validation_patch.json`
* `phase5/current_route_validation_result.json`
* `phase6/final_naming_realignment_machine_report.json`
* `phase6/independent_review_gate_report.json`
* `phase6/independent_review_eligibility_report.json`
* `phase6/owner_seal_input_manifest.json`
* `phase6/owner_seal_record_validation_report.json`

---

## 6. Planned Changes

### Change 0

Purpose:

Establish owner-reserved decisions, execution-contract status, top-doc baseline evidence, and dirty-overlap guards before any execution beyond census / policy draft.

Files:

* read: `docs/EXECUTION_CONTRACT.md`
* read: `docs/ARCHITECTURE.md`
* read: `docs/ROADMAP.md`
* read: `docs/DECISIONS.md`
* write: `Iris/build/description/v2/staging/dvf_3_3_dvf_system_naming_realignment/phase0/*`
* optional owner-supplied input: `Iris/build/description/v2/owner_inputs/dvf_3_3_dvf_system_naming_realignment/owner_decisions/*.json`

Implementation Notes:

* Emit `execution_contract_checked=true` with the checked document hash and no-known-conflict verdict.
* Materialize the roadmap input bytes and all review input bytes named in the header, or hash-bound provenance copies of them, under the evidence root so later validation does not depend only on transient attachment paths. Conversation-sourced review deltas must be copied into their planned materialization targets and assigned concrete sha256 values before execution may proceed beyond Phase 0.
* Emit `phase0/current_route_baseline_precondition_report.json` before any Option B adoption decision. The report classifies the live current-route baseline as:

```text
green
required_prework
blocked
```

* A non-green current-route baseline does not change this round's naming objective. It blocks Option B adoption only, with `blocked_reason=preexisting_current_route_baseline_failed`, unless the owner explicitly opens a separate prerequisite-fix scope.
* Emit `phase0/predecessor_required_gate_readpoint_freshness_report.json` proving whether the predecessor claim contract and required-gate adoption readpoints are currently consumable. A stale predecessor readpoint blocks only successor projection / Option B, not the doc-normative terminology objective.
* Emit `phase0/vcs_visibility_preflight.json` with `git ls-files`, ignore status, and planned required path coverage for new tools, tests, docs, and evidence roots. Preflight may report planned allowlist edits, but it must not count untracked required paths as VCS-visible.
* Emit `phase0/top_doc_baseline_hashes.json` with pre-edit hashes for `ARCHITECTURE.md`, `ROADMAP.md`, and `DECISIONS.md`.
* Emit `phase0/top_doc_dirty_overlap_report.json`.
* Emit `phase0/top_doc_closeout_guard_pre_census.json` before top-doc mutation. The closeout-guard rule source is `docs/completion_vocabulary_separation_policy.md` at sha256 `7FE70E8003B89655EED9A94E27790ADE158E4C5B4966BD4A7F6298366A8AB82D`, plus only the rule rows explicitly referenced by this plan. The census must distinguish this round's planned patch regions from preexisting doc-wide surfaces.
* If a top-doc target is already dirty and the dirty region overlaps the planned edit region, set:

```text
top_doc_dirty_overlap_detected=true
block_further_execution=true
```

* Emit `phase1/owner_decision_ratification_schema.json`.
* Owner decision entries must use:

```text
decision_id
decision_name
proposed_default
owner_value
state
decided_by
decided_at
source_artifact
source_sha256
```

* Valid states:

```text
proposed_default
owner_ratified
owner_overridden
missing
```

* Default values may appear only as `proposed_default`; they must not be projected into final closeout fields.
* D1-D6 are mandatory. Missing owner ratification blocks full execution, required-gate adoption, and canonical closeout.
* `owner_decision_ratification_schema.json` must define `D6.allowed_values` exactly as:

```text
canonical_seal_deferred_this_round
doc_normative_canonical_seal_allowed
required_gate_only_canonical_seal
```

* D6 values mean:

```text
canonical_seal_deferred_this_round = no canonical seal is claimed in this round
doc_normative_canonical_seal_allowed = owner permits doc-normative canonical seal without required-gate adoption
required_gate_only_canonical_seal = canonical seal requires Option B required-gate adoption
```

* Emit `phase1/roadmap_plan_decision_provenance_map.json` so owner decision IDs cannot be misread against the roadmap D-numbering:

```text
roadmap D1 successor PASS token selection -> plan D1 primary body compiler PASS token and plan D2 expanded alias split
roadmap D2 route label -> plan D3 Legacy Combined route prose label
roadmap D3 enforcement depth -> plan D5 Option A vs Option B enforcement selection
roadmap D4 adjacent token drift -> observed-only report unless owner adds a new decision
roadmap D5 bare DVF System PASS ban -> fixed conservative constraint, not a plan decision
roadmap D6 round identifier / independent review identity constraint -> round metadata, independent review schema, and plan D6 seal eligibility boundary
plan-added scope top-doc closeout-guard wording cleanup -> patch-region-only compatibility cleanup sourced from docs/completion_vocabulary_separation_policy.md; doc-wide absorption requires owner ratification or blocks as preexisting_closeout_guard_surfaces
```

* The round identifier is fixed as `round_id=dvf_3_3_dvf_system_naming_realignment` by plan ratification or by the owner-ratified D6 record.

Validation:

* `execution_contract_checked=true`
* `roadmap_input_materialized=true`
* `review_input_materialized=true`
* `review_input_cycle2_delta_materialized=true`
* `review_input_cycle3_NR3_materialized=true`
* `current_route_baseline_state` is recorded before D5 projection
* `preexisting_current_route_baseline_failed` blocks Option B only
* `predecessor_required_gate_readpoint_freshness_status` is recorded
* `vcs_visibility_preflight_status=PASS`
* `top_doc_baseline_hashes_present=true`
* `top_doc_dirty_overlap_detected=false`
* `top_doc_closeout_guard_pre_census_recorded=true`
* `owner_decision_queue_entry_count=6`
* `d6_allowed_values_schema_valid=true`
* `default_value_projected_without_owner_ratification=false`

---

### Change 1

Purpose:

Create a reproducible terminology census before any wording change.

Files:

* read: `docs/`
* read: `Iris/_docs/`
* read: `Iris/build/description/v2/tools/`
* read: `Iris/build/description/v2/tests/`
* read: `Iris/build/description/v2/data/`
* read: `Iris/build/description/v2/output/`
* read: `Iris/media/`
* write: `Iris/build/description/v2/staging/dvf_3_3_dvf_system_naming_realignment/phase0/*`

Implementation Notes:

* Scan exact terms and known variants:

```text
DVF Core
DVF Core PASS
DVF PASS
DVF System
DVF System PASS
DVF Body Compiler
DVF Body Compiler PASS
DVF System Body Compiler PASS
Legacy Combined Current Route PASS
Legacy Combined Governance Route PASS
Legacy Combined DVF Governance Route PASS
legacy_combined_governance_route
Iris Artifact Registry
Runtime Payload Consumer Compatibility
Public Text Quality
DVF 시스템
DVF 코어
```

* Every occurrence must receive a disposition class.
* `unclassifiable_blocker_count > 0` blocks execution beyond Phase 0.
* Historical path / machine token / sealed quote rows must be preserved, not patched.
* Current canonical prose rows become candidate patch targets.
* Census reports must distinguish:

```text
literal_dvf_core_occurrence_count
resolved_current_canonical_dvf_core_usage_count
all_literal_dvf_core_occurrences_disposition_classified
dvf_core_current_looking_predecessor_usage_classified
```

Validation:

* inventory row count is deterministic across two runs
* scan universe is non-empty
* included / excluded roots are recorded with reasons
* protected runtime / source / rendered / package surface hashes captured before execution
* `literal_dvf_core_occurrence_count >= 0`
* `resolved_current_canonical_dvf_core_usage_count` is measured separately and not treated as a literal grep count

---

### Change 2

Purpose:

Seal successor vocabulary and retired-label allowance.

Files:

* write: `docs/dvf_3_3_dvf_system_naming_realignment_policy.md`
* write: `Iris/build/description/v2/staging/dvf_3_3_dvf_system_naming_realignment/phase1/*`

Implementation Notes:

* Define current canonical vocabulary:

```text
DVF System
DVF Body Compiler
DVF Body Compiler PASS (primary token, only if owner-ratified D1)
DVF System Body Compiler PASS (expanded alias, only if owner-ratified D2)
Iris Artifact Registry
Registry Authority PASS
Registry Runtime Compatibility PASS
Publish Boundary PASS
Legacy Combined DVF Governance Route PASS
```

* Define the relationship:

```text
DVF System responsibility ceiling
= facts / decisions / profile / body_plan -> rendered 3-3 body

DVF Body Compiler
= role-granularity name for the same body-production responsibility

DVF System
!= body production + Registry + Runtime + Publish
```

* Define retired vocabulary:

```text
DVF Core
DVF Core PASS
```

* Allowed retired usage:

```text
retired label: DVF Core
historical label: DVF Core
previous wording: DVF Core
legacy claim vocabulary: DVF Core PASS
historical claim vocabulary: DVF Core PASS
```

* Forbidden current claims:

```text
DVF System PASS
DVF = DVF Core + Iris Artifact Registry
Iris Artifact Registry is part of DVF System
Iris Artifact Registry is DVF submodule
DVF System includes responsibilities beyond body production
DVF System includes Iris Artifact Registry
DVF System includes Publish Boundary
DVF System includes Registry Authority
Legacy Combined DVF Governance Route PASS == DVF Body Compiler PASS
DVF Body Compiler PASS == Registry Authority PASS
DVF Body Compiler PASS == Registry Runtime Compatibility PASS
DVF Body Compiler PASS == Publish Boundary PASS
Runtime Payload Consumer Compatibility is DVF System closure
Public Text Quality is DVF System closure
DVF 시스템은 Iris Artifact Registry를 포함한다
Iris Artifact Registry는 DVF System 하위 구성요소다
DVF 시스템은 Registry를 포함한다
Runtime Payload Consumer Compatibility는 DVF System closure다
Public Text Quality는 DVF System 문제다
DVF Body Compiler PASS는 release readiness를 뜻한다
```

* Retired-token default-deny rule:

```text
Retired vocabulary in current prose is forbidden unless it matches an allowed retired / historical / previous wording / path / compatibility / quoted-prior-claim disposition class.
```

* Freeze sentence successor reading:

```text
current_route_required_validations.json
= legacy_combined_governance_route
!= DVF Body Compiler PASS authority
```

Validation:

* policy doc contains canonical / retired / forbidden / compatibility vocabulary
* bare `DVF System PASS` is forbidden in this plan and cannot be enabled by default
* old token to successor token mapping exists and is not a simple rename claim
* primary / expanded alias fields are absent from final claims unless D1 / D2 are owner-ratified
* `DVF System Naming Realignment PASS` is registered as a round-scoped naming claim, not a system-state claim

---

### Change 3

Purpose:

Map existing claim classes to successor terminology without rewriting historical authority.

Files:

* read: `docs/dvf_3_3_core_registry_boundary_claim_contract.md`
* read: `docs/dvf_3_3_core_registry_boundary_claim_boundary.md`
* write: `docs/dvf_3_3_dvf_system_naming_realignment_claim_boundary.md`
* write: `Iris/build/description/v2/staging/dvf_3_3_dvf_system_naming_realignment/phase2/*`

Implementation Notes:

* The existing `DVF Core PASS` claim class remains historical predecessor vocabulary.
* The successor body compiler meaning is:

```text
DVF Body Compiler PASS
= body compiler determinism
+ facts / decisions / profile / body_plan consumption
+ rendered 3-3 body shape
+ protected-output no-mutation inside body compiler scope
```

* `DVF Body Compiler PASS` may be emitted as the canonical token only when D1 is owner-ratified or owner-overridden.
* `DVF System Body Compiler PASS` may be emitted as an expanded alias only when D2 is owner-ratified or owner-overridden.
* Validator outputs must distinguish:

```text
primary_token
expanded_alias
owner_decision_id
owner_decision_state
```

* Meaning identity table must prove non-substitution:

```text
DVF Body Compiler PASS != Registry Authority PASS
DVF Body Compiler PASS != Registry Runtime Compatibility PASS
DVF Body Compiler PASS != Publish Boundary PASS
Legacy Combined DVF Governance Route PASS != DVF Body Compiler PASS
```

* `Iris Artifact Registry` remains Iris-side artifact lifecycle / authority / runtime-package identity pipeline, not a DVF System submodule.
* `DVF System` does not own Registry Authority, Registry Runtime Compatibility, Publish Boundary, release readiness, package readiness, public text acceptance, or semantic quality acceptance.
* Adjacent drift tokens such as `Registry Runtime Compatibility PASS` vs `Runtime Compatibility PASS` are recorded in `phase2/adjacent_token_drift_observation_report.json`. They are not normalized by this round unless explicitly covered by owner-ratified D1-D6 decisions.

Validation:

* predecessor claim contract hash is recorded
* successor claim boundary cites predecessor hash
* no predecessor claim class is deleted
* no Registry / Runtime / Publish responsibility is reattached to DVF System
* successor token fields are owner-ratified projections, not plan defaults

---

### Change 4

Purpose:

Realign top-level current prose while preserving sealed history.

Files:

* update candidate: `docs/ARCHITECTURE.md`
* update candidate: `docs/ROADMAP.md`
* append-only candidate: `docs/DECISIONS.md`
* write: `Iris/build/description/v2/staging/dvf_3_3_dvf_system_naming_realignment/phase3/*`

Implementation Notes:

* `ARCHITECTURE.md` current Iris DVF sections should replace current canonical `DVF Core` wording with `DVF System` / `DVF Body Compiler`.
* Claim vocabulary block should use `DVF Body Compiler PASS` or `DVF System Body Compiler PASS`, not `DVF Core PASS`, except as explicitly retired historical vocabulary.
* `ROADMAP.md` Iris summary should state the current vocabulary and keep detailed history out of the canonical summary.
* `DECISIONS.md` should receive a new additive decision family:

```text
Iris DVF 3-3 - DVF System naming realignment / DVF Core retired label
```

* Existing decision family text is not rewritten unless a separate owner-approved correction scope is opened.
* The additive successor entry must state:

```text
The prior "DVF Core / Registry / Publish boundary" current terminology
is retained as historical / predecessor claim vocabulary.

Its boundary split meaning remains valid,
but its current canonical label is superseded by
DVF System / DVF Body Compiler terminology.
```

* `DECISIONS.md` append entry must be owner-authored or owner-ratified under D4.
* `ROADMAP.md` current canonical summary must not be classified as historical merely because it is a top doc. Current summary blocks are patch candidates unless an explicit predecessor / historical disposition applies.
* Top-doc patching must include closeout-guard-compatible wording cleanup only inside this round's planned patch regions by default. This is not a goal change: it preserves the same non-claim meaning while rewriting ambiguous current prose into axis-qualified non-claim or Publish Boundary scope wording.
* The closeout-guard rule source is `docs/completion_vocabulary_separation_policy.md` at sha256 `7FE70E8003B89655EED9A94E27790ADE158E4C5B4966BD4A7F6298366A8AB82D`. A new rule may be used only if it is named in the policy section snapshot recorded by `phase0/top_doc_closeout_guard_pre_census.json`.
* Allowed cleanup forms are limited to:

```text
ambiguous current prose -> axis-qualified non-claim
release / Workshop / public text wording -> Publish Boundary scope wording
```

* Forbidden cleanup expansion:

```text
public text rewrite
semantic quality rewrite
release strategy rewrite
architecture section redesign
```

* If `phase0/top_doc_closeout_guard_pre_census.json` reports `closeout_guard_blocked_surface_count_before=0`, the Change 4 closeout-guard cleanup is a recorded no-op.
* If doc-wide scan finds preexisting closeout-guard surfaces outside this round's patch regions, tooling must not absorb them automatically. It must halt with `blocked_reason=preexisting_closeout_guard_surfaces` unless the owner ratifies either a separate prerequisite scope or explicit in-round inclusion.
* Disposition class exemptions apply before after-count evaluation. `sealed_historical`, `frozen_machine_token`, `historical_path_or_root`, `quoted_prior_claim`, and `predecessor_trace` are not unresolved blocked surfaces if their disposition proof is present. `closeout_guard_blocked_surface_count_after=0` means zero unresolved blocked surfaces after disposition, not zero literal occurrences.
* `phase3/top_doc_closeout_guard_compatibility_report.json` must record:

```text
closeout_guard_rule_source_path=docs/completion_vocabulary_separation_policy.md
closeout_guard_rule_source_sha256=7FE70E8003B89655EED9A94E27790ADE158E4C5B4966BD4A7F6298366A8AB82D
closeout_guard_rule_source_actual_sha256=<runtime sha256>
closeout_guard_rule_source_hash_mismatch=false
closeout_guard_scan_boundary=patch_region_default
closeout_guard_blocked_surface_count_before
closeout_guard_preexisting_out_of_patch_surface_count
closeout_guard_disposition_exempt_surface_count
closeout_guard_blocked_surface_count_after
public_text_workshop_release_terms_axis_qualified_for_patch_region=true
top_doc_closeout_guard_compatibility_status=PASS
```

* If a top-doc patch reprints an observed adjacent drift token such as `Runtime Compatibility PASS`, `phase3/top_doc_patch_plan.json` must carry reproduction provenance:

```text
adjacent_drift_reprint_detected=<true|false>
adjacent_drift_reprint_reason=<exact reason>
adjacent_drift_observation_report_ref=phase2/adjacent_token_drift_observation_report.json
```

Validation:

* `literal_dvf_core_occurrence_count` may be greater than 0
* `resolved_current_canonical_dvf_core_usage_count=0`
* `all_literal_dvf_core_occurrences_disposition_classified=true`
* `dvf_core_current_looking_predecessor_usage_classified=true`
* `successor_decision_family_supersedes_prior_current_label=true`
* allowed `retired label: DVF Core` / historical mentions remain
* `DECISIONS.md` append-only proof PASS
* no forbidden phrase such as `DVF = DVF Core + Iris Artifact Registry`
* no claim that Registry is a DVF System submodule
* `top_doc_closeout_guard_compatibility_status=PASS`
* `closeout_guard_rule_source_hash_mismatch=false`
* `closeout_guard_blocked_surface_count_after=0`
* `closeout_guard_preexisting_out_of_patch_surface_count=0` unless owner ratifies in-round inclusion or separate scope handling
* `top_doc_dirty_overlap_detected=false` before any top-doc mutation

---

### Change 5

Purpose:

Add lexical/token-level guard tooling for future current-route overclaims.

Files:

* write: `Iris/build/description/v2/tools/build/dvf_3_3_dvf_system_naming_realignment.py`
* write: `Iris/build/description/v2/tools/build/run_dvf_3_3_dvf_system_naming_realignment.py`
* write: `Iris/build/description/v2/tools/build/validate_dvf_3_3_dvf_system_naming_realignment.py`
* write: `Iris/build/description/v2/tests/test_dvf_3_3_dvf_system_naming_realignment.py`
* write: `Iris/build/description/v2/staging/dvf_3_3_dvf_system_naming_realignment/phase4/*`

Implementation Notes:

* Reuse the local pattern from the existing core/registry boundary closure and required-gate adoption tooling.
* Scanner class is `lexical_token_level`; semantic or paraphrase detection remains manual / independent review scope.
* Plain current-prose `DVF Core`, `DVF Core PASS`, `DVF 코어`, or equivalent retired-token usage fails unless it is classified as allowed retired / historical / previous wording / path / compatibility / quoted-prior usage.
* Exception classes must be explicit and hash-bound where needed:

```text
quoted_prior_claim
predecessor_trace
retirement_self_mention
historical_path_or_root
frozen_machine_token
machine_schema_compatibility
forbidden_example
negated_claim
```

* Negative fixtures must fail for:

```text
Current DVF System PASS is complete.
DVF Core validates rendered bodies.
DVF Core is the current body production system.
DVF System includes Iris Artifact Registry.
DVF System includes responsibilities beyond body production.
DVF System includes Publish Boundary.
Legacy Combined DVF Governance Route PASS equals DVF Body Compiler PASS.
DVF Body Compiler PASS proves runtime compatibility.
DVF Body Compiler PASS proves release readiness.
Runtime Payload Consumer Compatibility is DVF System closure.
Public Text Quality is DVF System closure.
DVF 시스템은 Iris Artifact Registry를 포함한다.
Iris Artifact Registry는 DVF System 하위 구성요소다.
DVF 시스템은 Registry를 포함한다.
Runtime Payload Consumer Compatibility는 DVF System closure다.
Public Text Quality는 DVF System 문제다.
DVF Body Compiler PASS는 release readiness를 뜻한다.
```

* Positive fixture must pass for the round-scoped naming claim:

```text
DVF System Naming Realignment PASS
= terminology / claim vocabulary governance-only closure

Expected:
PASS as round-scoped naming claim
not bare DVF System PASS
not system-state PASS
not release-state PASS
```

Validation:

* focused unittest PASS
* forbidden current claims fail
* retired-token current prose default-deny fixture fails
* Korean / mixed-language forbidden fixtures fail
* allowed retired-label references pass
* historical path references pass
* frozen machine tokens pass
* scan universe count > 0
* false positive exceptions are counted, not silently skipped

---

### Change 6

Purpose:

Decide enforcement depth and optionally adopt a current-route required gate.

Files:

* optional update: `Iris/_docs/round3/current_route_required_validations.json`
* optional update: `.gitignore`
* write: `Iris/build/description/v2/staging/dvf_3_3_dvf_system_naming_realignment/phase5/*`

Implementation Notes:

Two enforcement modes are allowed:

```text
Option A: doc-normative rule only
Option B: additive lexical scanner + current-route required-validation manifest consumption
```

* Enforcement mode is owner-reserved D5. Plan preference is not a decision.
* Option A closeout ceiling:

```text
dvf_system_naming_realignment_state=doc_normative_complete
required_gate_adopted=false
future_current_route_blocking_claimed=false
machine_gate_deferred=true
current_route_baseline_state=<phase0 recorded value>
current_route_baseline_dependency=waived
predecessor_required_gate_readpoint_freshness_status=<phase0 recorded value>
predecessor_required_gate_dependency=waived
option_b_current_route_test_design=<phase5 recorded value or not_evaluated>
option_b_current_route_test_design_dependency=waived
canonical_seal_allowed=true only if D6=doc_normative_canonical_seal_allowed; otherwise false
canonical_seal_scope=doc_normative_governance_only if canonical_seal_allowed=true; otherwise not_claimed
```

* Option B closeout ceiling:

```text
dvf_system_naming_realignment_state=required_gate_adopted_complete
required_gate_adopted=true
future_current_route_blocking_claimed=true
current_route_rerun_success=true
current_route_baseline_state=green
current_route_baseline_dependency=required
predecessor_required_gate_readpoint_freshness_status=PASS
predecessor_required_gate_dependency=required
option_b_current_route_test_design=closure_compatible_subprocess_or_bare_module_import
option_b_current_route_test_design_dependency=required
vcs_visibility_required_paths_tracked=true
canonical_seal_allowed=true only within governance-only naming boundary and only if D6=doc_normative_canonical_seal_allowed or D6=required_gate_only_canonical_seal
```

If Option B is too heavy, blocked by import closure, or not owner-ratified, executing Option A first is a valid successful closeout path. It must close as `doc_normative_complete`, with `required_gate_adopted=false`, `future_current_route_blocking_claimed=false`, and `machine_gate_deferred=true`.

Default implementation preference is Option B only if all of the following pass:

```text
current-route baseline precondition green
predecessor required-gate readpoint freshness PASS
focused test import closure PASS
current-route build closure PASS
new tooling/test paths VCS-visible
no active core closure config mutation needed
pre-adoption loadability PASS
manifest diff additive-only
existing required tests/artifacts removed count = 0
protected surface changed count = 0
```

Option B required-test design must be current-route import-closure compatible:

```text
required current-route test MUST NOT import new tooling as tools.build.*
required current-route test MAY use subprocess runner + evidence manifest validation
required current-route test MAY use bare module import only with tools_build_package_import_attempt_count=0
import closure probe MUST run before manifest patch
round3_active_core_closure.json expansion required => blocked, not auto-downgraded
```

If the Option B required current-route test uses a subprocess runner, the same current-route test must consume the emitted evidence manifest and validate at least these fields rather than trusting subprocess exit code alone:

```text
forbidden_current_claim_count=0
resolved_current_canonical_dvf_core_usage_count=0
protected_surface_changed_count=0
overclaim_scanner_class=lexical_token_level
```

`phase5/import_closure_compatible_test_design_report.json` must record:

```text
option_b_current_route_test_design=closure_compatible_subprocess_or_bare_module_import
tools_build_package_import_attempt_count=0
bare_tool_module_import_used=<true|false>
subprocess_runner_used=<true|false>
subprocess_evidence_manifest_fields_validated=<true|false|not_applicable>
subprocess_evidence_manifest_minimum_fields=forbidden_current_claim_count,resolved_current_canonical_dvf_core_usage_count,protected_surface_changed_count,overclaim_scanner_class
round3_active_core_closure_expansion_required=false
```

`phase5/vcs_visibility_required_path_report.json` must prove that every Option B required tool, test, documentation artifact, and manifest-required evidence path is either tracked or explicitly made visible by a narrow `.gitignore` allowlist before closeout.

If Option B requires expanding `round3_active_core_closure.json`, tooling must not auto-downgrade. It must halt with `blocked_reason=option_b_import_closure_infeasible` and require owner D5 re-ratification. If this is discovered before ratification, present Option A as the only viable mode.

Validation:

* selected enforcement mode recorded
* selected enforcement mode is owner-ratified D5 value
* current-route baseline precondition is green before Option B adoption
* preexisting current-route baseline failure is reported as prerequisite failure, not naming failure
* predecessor required-gate readpoint freshness is PASS before successor projection into Option B
* Option B required-test design avoids `tools.build.*` imports under current-route closure
* if `subprocess_runner_used=true`, `subprocess_evidence_manifest_fields_validated=true`
* `vcs_visibility_required_paths_tracked=true`
* Option B manifest patch is additive-only
* existing required gate meanings unchanged
* first current-route pass after adoption succeeds
* final docs are included in a second scan or second route pass before closeout
* if Option A, final report uses `doc_normative_complete` and sets `required_gate_adopted=false`, `future_current_route_blocking_claimed=false`, and `machine_gate_deferred=true`
* if Option B, final report uses `required_gate_adopted_complete` only after current-route consumption succeeds

---

### Change 7

Purpose:

Close the round with re-census, no-mutation proof, independent review input, and owner seal input.

Files:

* write: `docs/dvf_3_3_dvf_system_naming_realignment_closeout.md`
* write: `Iris/build/description/v2/staging/dvf_3_3_dvf_system_naming_realignment/phase6/*`
* optional owner-supplied input: `Iris/build/description/v2/owner_inputs/dvf_3_3_dvf_system_naming_realignment/owner_seals/current_session_owner_canonical_seal_record.json`

Implementation Notes:

* Re-run terminology census after planned edits.
* Compare pre/post disposition counts.
* Verify current canonical `DVF Core` usage is removed from current prose.
* Verify historical / retired / frozen usage remains classified.
* Produce final machine report with explicit non-claims.
* Independent review and owner seal are separate from machine PASS.
* Independent review report schema must include:

```text
reviewer_identity_class
reviewer_is_roadmap_coauthor
reviewer_is_plan_author
reviewer_is_prior_review_chain_participant
independent_review_gate_eligible
```

* Roadmap / plan co-author cannot satisfy `independent_review_gate`.
* Review chain artifacts may contribute plan-level review but cannot be silently promoted to independent review gate when structurally ineligible.
* Owner seal record is owner-supplied input. Tooling may verify, copy, hash, or reference the owner seal record, but must not synthesize it.
* If owner seal input is absent:

```text
owner_seal=not_claimed
canonical_closure=false
```

Validation:

* final forbidden claim scan PASS
* final protected source / rendered / Lua bridge / runtime / package mutation count = 0
* owner seal input is owner-supplied and present, or explicitly `not_claimed`
* independent review artifact is eligible and present, or explicitly `not_claimed`
* closeout claim remains governance-only

---

## 7. Validation Plan

### Automated Validation

Planned exact commands for execution:

```powershell
uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_dvf_system_naming_realignment.py --mode all
uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_dvf_system_naming_realignment.py --require-complete
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_dvf_system_naming_realignment.py"
```

If Option B required-gate adoption is selected:

```powershell
uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
```

Optional Lua syntax sanity check, because runtime Lua must remain untouched:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Additional automated checks:

* terminology census determinism
* scan universe minimum coverage
* disposition class schema validation
* owner decision queue validation
* owner decision ratification schema validation
* owner-ratified projection validation for D1-D6 final fields
* current-route baseline precondition validation before Option B
* predecessor required-gate readpoint freshness validation
* successor claim boundary hash binding
* predecessor claim contract hash binding
* predecessor / successor precedence validation for `DECISIONS.md`
* forbidden overclaim negative fixtures
* round-scoped naming claim positive fixture
* retired-token default-deny negative fixtures
* Korean / mixed-language negative fixtures
* allowed retired-label positive fixtures
* literal occurrence vs resolved current canonical usage validation
* top-doc baseline hash validation
* top-doc dirty-overlap fail-closed validation
* top-doc closeout-guard compatibility validation
* `DECISIONS.md` append-only proof
* `current_route_required_validations.json` additive-only diff, if mutated
* Option A / Option B closeout ceiling validation
* focused test import closure
* Option B import-closure-compatible test design validation
* VCS visibility check for new tools/tests/evidence
* VCS required path tracking validation for manifest-consumed artifacts
* independent reviewer eligibility validation
* owner seal source validation
* `EXECUTION_CONTRACT.md` checked-state validation
* protected source / rendered / Lua bridge / runtime chunk / package payload hash no-mutation
* final report non-claim field validation

### Manual Validation

* Review `docs/dvf_3_3_dvf_system_naming_realignment_policy.md` for clear canonical / retired / forbidden vocabulary.
* Review top-doc patches to ensure `DVF System` does not become a broad umbrella over Registry or Publish.
* Review scanner exceptions for historical / path / frozen-token false positives.
* Review successor PASS token decision:
  * D1 owner-ratified primary token, proposed default: `DVF Body Compiler PASS`
  * D2 owner-ratified expanded alias, proposed default: `DVF System Body Compiler PASS`
* Review legacy route label decision:
  * D3 owner-ratified current prose label, proposed default: `Legacy Combined DVF Governance Route PASS`
  * machine token preserved: `legacy_combined_governance_route`
* Review D4 predecessor / successor handling for `DECISIONS.md`.
* Review whether Option A or Option B enforcement is selected.
* Review D6 canonical seal eligibility.
* Review closeout wording for release/package/public-text overclaims.

### Validation Limits

This plan will not perform:

* no runtime equivalence validation
* no runtime payload compatibility closure
* no package safety validation
* no release readiness validation
* no Workshop readiness validation
* no B42 readiness validation
* no deployment validation
* no manual in-game QA
* no multiplayer validation
* no external mod compatibility sweep
* no public text quality acceptance
* no semantic quality acceptance
* no full clean-checkout historical byte reproducibility
* no Registry Authority PASS validation
* no Registry Runtime Compatibility PASS validation
* no Publish Boundary PASS validation
* no actual body compiler determinism re-run beyond this plan's governance checks

Lua syntax validation is only a no-regression sanity check. It is not runtime compatibility, package readiness, release readiness, or public-facing acceptance evidence.

---

## 8. Risk Surface Touch

### Authority Surface

Touched, governance-only.

The plan changes terminology / claim vocabulary authority. It does not move ownership of source facts, decisions, rendered output, runtime payload, package payload, release readiness, or public text acceptance.

Owner-ratified D1-D6 decisions are authority inputs. Tooling may validate those inputs but must not replace them with defaults.

### Runtime Behavior Surface

None.

Runtime Lua files, bridge-generated runtime chunks, UI behavior, tooltip behavior, and package runtime behavior are protected no-mutation surfaces.

### Compatibility Surface

No runtime compatibility change.

Machine compatibility is touched only if Option B adds a required-validation gate. Existing machine tokens and historical gate roles must remain compatibility aliases or historical surfaces, not breaking renames.

### Sealed Artifact Surface

Touched only additively.

Existing sealed decision bodies, historical closeout names, artifact paths, and evidence roots are not rewritten. New policy / claim boundary / evidence reports are additive successor artifacts.

`DECISIONS.md` may retain literal `DVF Core` occurrences as historical / predecessor text. Validation must use resolved current canonical usage, not literal zero-count.

### Public-Facing Output Surface

None.

No Iris public body text, tooltip text, wiki text, Workshop text, release note, package copy, or user-facing copy is changed by this plan.

---

## 9. Risk Analysis

### Architecture Risk

* `DVF System` could become a broader umbrella that reabsorbs Iris Artifact Registry or Publish Boundary.
* `DVF Body Compiler PASS` could be read as a simple rename of `DVF Core PASS` while inheriting old ambiguity.
* `DVF System PASS` could reintroduce a forbidden bare PASS claim.
* Plan defaults could be mistaken for owner-ratified decisions.
* Existing sealed history could be over-edited, breaking trace.
* Mitigation: successor policy, retired-label allowance matrix, meaning-identity table, forbidden claim scanner, D1-D6 owner ratification, and append-only DECISIONS treatment.

### Runtime Risk

* Runtime risk is low because runtime surfaces are out of scope.
* Main risk is accidental mutation during validation or generator execution.
* Mitigation: phase0 protected hash baseline, final protected hash recapture, and no-mutation fail-closed checks.

### Compatibility Risk

* Breaking rename of `dvf_core` machine fields, old paths, or gate role names could invalidate historical evidence or current route assumptions.
* Scanner false positives could block quoted or historical text.
* Literal `DVF Core` zero-count validation could force illegal sealed-history rewrite.
* Mitigation: compatibility alias class, historical/path/frozen-token dispositions, explicit exception classes, and positive fixtures.

### Regression Risk

* Top-doc sync could leave partial terminology drift.
* Pre-existing current-route baseline failures could be misattributed to this naming round.
* Required-gate adoption could fail import closure under `round3_active_core_closure.json`.
* New generated artifacts could remain ignored by `.gitignore`.
* A required current-route test could import new tooling through `tools.build.*` and fail only under closure enforcement.
* Scanner could pass with an incomplete scan universe.
* Option B could be overclaimed as future semantic enforcement when it is lexical/token-level only.
* Existing top-doc public-text / Workshop / release wording could fail closeout-guard scans even when the naming objective is otherwise correct.
* Top-doc rollback could be unverifiable without pre-edit hashes.
* Independent review or owner seal artifacts could be mistaken as satisfied by generated reports.
* Mitigation: current-route baseline precondition report, predecessor readpoint freshness report, current-route import probe, import-closure-compatible test design report, VCS visibility proof, required path tracking proof, mandatory scan universe minimum, top-doc closeout-guard compatibility report, top-doc baseline hashes, dirty-overlap guard, final re-census, reviewer eligibility fields, owner-supplied seal validation, and explicit `overclaim_scanner_class=lexical_token_level`.

---

## 10. Rollback Plan

Rollback is governance-scoped and additive-history aware.

1. If Option B was adopted, remove only this round's additive entries from `Iris/_docs/round3/current_route_required_validations.json`.
2. Remove or supersede only this round's scanner / runner / validator / focused test files.
3. Remove or supersede this round's docs:
   * `docs/dvf_3_3_dvf_system_naming_realignment_policy.md`
   * `docs/dvf_3_3_dvf_system_naming_realignment_claim_boundary.md`
   * `docs/dvf_3_3_dvf_system_naming_realignment_ledger_packet.md`
   * `docs/dvf_3_3_dvf_system_naming_realignment_closeout.md`
4. Remove only this round's narrow `.gitignore` allowlist entries, if added.
5. Revert `ARCHITECTURE.md` / `ROADMAP.md` terminology patches to the pre-round baseline hashes recorded in `phase0/top_doc_baseline_hashes.json` if the round fails before seal.
6. Do not delete sealed predecessor decision text. If `DECISIONS.md` already received an additive entry, supersede it with a correction entry rather than rewriting history.
7. Preserve predecessor core/registry boundary docs and required-gate adoption docs.
8. Re-run the focused validator and, if Option B touched the manifest, the current route runner.

Rollback does not mean `DVF Core` becomes current canonical terminology again. It means this naming realignment attempt was not adopted or must be superseded by a new scope.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Hub & Spoke / SPI boundaries remain preserved.
* Iris runtime remains 100% Lua.
* Runtime/build-time separation is mandatory.
* `DVF Core` retirement is terminology governance, not runtime or architecture expansion.
* `DVF System` is limited to 3-3 body production:

```text
facts / decisions / profile / body_plan -> rendered 3-3 body
```

* `DVF Body Compiler` is the role-granularity name for the same body-production responsibility, not a separate wider subsystem.
* `DVF System` does not include Registry Authority, Runtime Compatibility, Publish Boundary, release readiness, package readiness, public text acceptance, or semantic quality acceptance.
* Iris Artifact Registry remains separate from DVF System.
* Publish Boundary remains separate from DVF System and Iris Artifact Registry.
* Runtime Payload Consumer Compatibility remains Registry / Runtime Compatibility scope, not DVF System closure.
* Public Text Quality remains Publish Boundary scope, not DVF System closure.
* Current combined route remains preserved.
* Manifest physical split is forbidden in this scope.
* Current route runner rewrite is forbidden.
* Machine schema breaking rename is forbidden.
* Historical artifact path rename is forbidden.
* Sealed decision body rewrite is forbidden.
* `DECISIONS.md` changes are append-only unless a separate explicit correction scope is opened.
* `DECISIONS.md` prior literal `DVF Core` text may remain; successor precedence must resolve current canonical usage without rewriting sealed predecessor text.
* Source / rendered / Lua bridge / runtime chunk / package payload mutation is forbidden.
* Bare `DVF PASS` remains forbidden.
* Bare `DVF System PASS` is forbidden in this plan.
* `DVF Body Compiler PASS` cannot imply Registry Authority, Runtime Compatibility, Publish Boundary, package readiness, release readiness, or public text acceptance.
* Retired vocabulary in current prose is default-deny unless an allowed disposition class applies.
* Default proposed D1-D6 values do not count as owner decisions.
* Option B required-gate adoption must be additive-only and current-route import-closure compatible.
* If required-gate adoption is skipped, final state must not claim future current-route blocking.
* Scanner results are lexical/token-level only and do not replace manual / independent semantic review.
* Independent review, owner seal, and canonical seal are separate from machine PASS.
* Independent reviewer eligibility must be validated before any independent review gate claim.
* Owner seal record must be owner-supplied. Tooling must not synthesize owner seal records.
* Closeout prose must avoid bare `complete`; it must use an evidence-bounded `governance-only naming realignment` qualifier.

---

## 12. Expected Closeout State

Expected closeout target depends on owner-ratified D5 enforcement mode and D6 canonical seal eligibility.

The generic word `complete` is not used by itself. Closeout must use one of these evidence-bounded states:

```text
doc_normative_complete
required_gate_adopted_complete
blocked
```

D6 closeout projection must use one of these exact enum values:

```text
canonical_seal_deferred_this_round
doc_normative_canonical_seal_allowed
required_gate_only_canonical_seal
```

Expected final machine state:

```text
dvf_system_naming_realignment_state=<owner-ratified D5 projection>
terminology_retirement_mode=retirement_not_bulk_rename
current_canonical_body_system=DVF System
current_canonical_body_compiler=DVF Body Compiler
dvf_system_responsibility_ceiling=facts_decisions_profile_body_plan_to_rendered_3_3_body
dvf_body_compiler_relation=role_granularity_name_for_same_body_production_responsibility
dvf_body_compiler_pass_token_meaning_defined=true
dvf_body_compiler_pass_achievement_claimed=false
canonical_body_compiler_pass_token=<owner-ratified D1 value>
expanded_body_compiler_pass_token_allowed=<owner-ratified D2 value>
route_label=<owner-ratified D3 value>
decisions_append_precedence=<owner-ratified D4 value>
enforcement_mode=<owner-ratified D5 value>
canonical_seal_eligibility=<owner-ratified D6 value>
owner_required_decision_missing=false
bare_dvf_pass_allowed=false
bare_dvf_system_pass_allowed=false
literal_dvf_core_occurrence_count>=0
resolved_current_canonical_dvf_core_usage_count=0
all_literal_dvf_core_occurrences_disposition_classified=true
dvf_core_current_looking_predecessor_usage_classified=true
dvf_core_retired_or_historical_usage_classified=true
iris_artifact_registry_is_dvf_submodule=false
dvf_system_includes_registry_authority=false
dvf_system_includes_runtime_compatibility=false
dvf_system_includes_publish_boundary=false
legacy_combined_dvf_governance_route_pass_is_body_compiler_pass=false
registry_authority_pass_claimed=false
registry_runtime_compatibility_pass_claimed=false
publish_boundary_pass_claimed=false
runtime_payload_consumer_compatibility_closure_claimed=false
public_text_quality_acceptance_claimed=false
source_rendered_lua_runtime_package_mutation=false
protected_surface_changed_count=0
decisions_append_only_proof=PASS
successor_decision_family_supersedes_prior_current_label=true
top_doc_baseline_hashes_present=true
top_doc_dirty_overlap_detected=false
scan_universe_count>0
forbidden_current_claim_count=0
unclassifiable_blocker_count=0
retired_token_current_prose_default_deny=true
korean_mixed_language_fixture_status=PASS
dvf_system_naming_realignment_pass_positive_fixture_status=PASS
overclaim_scanner_class=lexical_token_level
execution_contract_checked=true
current_route_baseline_state=<green|required_prework|blocked>
current_route_baseline_dependency=<waived|required>
predecessor_required_gate_readpoint_freshness_status=<PASS|stale|blocked>
predecessor_required_gate_dependency=<waived|required>
top_doc_closeout_guard_compatibility_status=PASS
closeout_guard_rule_source_sha256=7FE70E8003B89655EED9A94E27790ADE158E4C5B4966BD4A7F6298366A8AB82D
closeout_guard_rule_source_actual_sha256=<runtime sha256>
closeout_guard_rule_source_hash_mismatch=false
closeout_guard_scan_boundary=patch_region_default
closeout_guard_blocked_surface_count_after=0
closeout_guard_preexisting_out_of_patch_surface_count=0 unless owner-ratified inclusion exists
vcs_visibility_required_paths_tracked=true
option_b_current_route_test_design=<closure_compatible_subprocess_or_bare_module_import|not_evaluated>
option_b_current_route_test_design_dependency=<waived|required>
round3_active_core_closure_expansion_required=false
independent_review_gate_eligible=<validated or not_claimed>
owner_seal_source=owner_supplied_or_not_claimed
canonical_seal_scope=<doc_normative_governance_only|required_gate_governance_only|not_claimed>
```

If Option A is owner-ratified and succeeds:

```text
dvf_system_naming_realignment_state=doc_normative_complete
required_gate_adopted=false
future_current_route_blocking_claimed=false
machine_gate_deferred=true
current_route_baseline_state=<phase0 recorded value>
current_route_baseline_dependency=waived
predecessor_required_gate_readpoint_freshness_status=<phase0 recorded value>
predecessor_required_gate_dependency=waived
option_b_current_route_test_design=<phase5 recorded value or not_evaluated>
option_b_current_route_test_design_dependency=waived
canonical_seal_allowed=true only if D6=doc_normative_canonical_seal_allowed; otherwise false
canonical_seal_scope=doc_normative_governance_only if canonical_seal_allowed=true; otherwise not_claimed
```

If Option B is owner-ratified and succeeds:

```text
dvf_system_naming_realignment_state=required_gate_adopted_complete
required_gate_adopted=true
future_current_route_blocking_claimed=true
current_route_rerun_success=true
current_route_baseline_state=green
current_route_baseline_dependency=required
predecessor_required_gate_readpoint_freshness_status=PASS
predecessor_required_gate_dependency=required
option_b_current_route_test_design=closure_compatible_subprocess_or_bare_module_import
option_b_current_route_test_design_dependency=required
vcs_visibility_required_paths_tracked=true
existing_required_test_removed_count=0
existing_required_artifact_removed_count=0
manifest_physical_split_performed=false
current_route_runner_rewrite_performed=false
canonical_seal_allowed=true only within governance-only naming boundary and only if D6=doc_normative_canonical_seal_allowed or D6=required_gate_only_canonical_seal
canonical_seal_scope=required_gate_governance_only if canonical_seal_allowed=true; otherwise not_claimed
```

If owner decisions are missing or validation cannot pass:

```text
dvf_system_naming_realignment_state=blocked
blocked=true
blocked_reason=<exact blocker>
owner_required_decision_missing=<true if owner decisions are missing; otherwise false>
full_execution_approved=false
required_gate_adoption_allowed=false
canonical_closure=false
```

Expected non-claims:

* DVF Body Compiler PASS token meaning defined.
* DVF Body Compiler PASS achievement not claimed.
* no Registry Authority PASS
* no Registry Runtime Compatibility PASS
* no Runtime Payload Consumer Compatibility closure
* no Publish Boundary PASS
* no public text acceptance
* no semantic quality acceptance
* no package readiness
* no release / Workshop / B42 / deployment readiness
* no manual QA
* no source / rendered / Lua bridge / runtime chunk / package payload mutation

Blocking conditions include:

```text
unclassifiable_blocker_count>0
forbidden_current_claim_count>0 after planned patches
resolved_current_canonical_dvf_core_usage_count>0 after planned patches
all_literal_dvf_core_occurrences_disposition_classified=false
bare_dvf_system_pass_allowed=true
iris_artifact_registry_is_dvf_submodule=true
dvf_system_includes_registry_authority=true
dvf_system_includes_publish_boundary=true
protected_surface_changed_count>0
decisions_append_only_proof!=PASS
top_doc_dirty_overlap_detected=true
top_doc_closeout_guard_compatibility_status!=PASS
closeout_guard_rule_source_hash_mismatch=true
blocked_reason=closeout_guard_rule_source_stale when closeout_guard_rule_source_hash_mismatch=true
closeout_guard_preexisting_out_of_patch_surface_count>0 without owner-ratified inclusion or separate scope
scan_universe_count=0
required_gate_adoption_claimed_without_current_route_consumption=true
current_route_import_closure_probe_failed=true
preexisting_current_route_baseline_failed=true when Option B selected
predecessor_required_gate_readpoint_freshness_status!=PASS when Option B selected
vcs_visibility_required_paths_tracked=false for required closeout paths
tools_build_package_import_attempt_count>0 when Option B selected
round3_active_core_closure_expansion_required=true when Option B selected
owner_required_decision_missing=true
owner_seal_synthesized_by_tooling=true
independent_review_gate_claimed_with_ineligible_reviewer=true
```
