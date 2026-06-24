# Implementation Plan

> Status: executed terminal-disposition adjudication plan / machine-complete evidence produced / independent review pending / no current-route adoption / no runtime-source-rendered-chunk mutation
> 작성일: 2026-06-19
> Roadmap input: `C:/Users/MW/.codex/attachments/1048c7e3-26a3-47ac-b566-5a4d1c00c1f7/pasted-text.txt` / sha256 `1F68EF5AAF824BB9A4BC2B697C7AC01F72EB04A83ED9BB258FA6F20E38B5F6A3` / non-authority synthesis reference
> Review input: `C:/Users/MW/.codex/attachments/05a29844-d747-43ce-b77a-54443fb6714b/pasted-text.txt` / sha256 `CB1901EE71319DE14B81B3639FE8EEE2F8DC9EECC30815BC4726DB3B36A350AC` / WARN required-revision synthesis, incorporated in this revision
> Review input R2: `C:/Users/MW/.codex/attachments/24dcd37d-a0af-478e-b461-ee08ab7a2b3a/pasted-text.txt` / sha256 `0B0520AD2A11DC20A9D77ABC5FA3E6BAB87D3F2ABC9610E3E5945AC047D5871C` / WARN near-PASS review, I-5 and recommended minor revisions incorporated
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Top authority: `docs/Philosophy.md`
> Current authority context: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`

---

## 1. Objective

Iris DVF 3-3 vNext Consumer Universe의 bound executing-consumer member-row population을 하나의 terminal disposition ledger로 귀속시키고, 성공 closeout 기준에서 `blocked_count = 0` 및 `conditional_count = 0`을 machine-checkable하게 증명한다.

이 계획은 migration을 다시 수행하는 계획이 아니다. 목표는 이미 존재하는 audit, normalization, readiness, cutover, runtime payload guard, denominator lock evidence를 read-only input으로 소비하여, Phase 1에서 새로 bind한 terminal universe의 모든 member를 다음 네 terminal disposition 중 하나로 판정하는 것이다.

* `migrated`
* `no-op`
* `diagnostic-only`
* `historical-only`

`canonical_complete` closeout claim은 다음 범위로 제한한다.

```text
Terminal Disposition Adjudication is complete:
every member in the bound consumer universe has a non-blocked terminal disposition,
with blocked_count = 0, conditional_count = 0, unknown_count = 0, and pending_count = 0,
under the defined denominator and claim boundary.
```

이 계획은 release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game QA, public-facing text quality acceptance, semantic quality completion, new current authority cutover, live runtime replacement, source facts / decisions / rendered output mutation, runtime payload policy mutation을 선언하지 않는다.

---

## 2. Scope

이 계획은 governance / adjudication / claim-boundary 라운드다. 실행은 staging 산출물, focused validator, docs closeout / ledger packet으로 제한한다.

Primary execution evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/`

Plan artifact:

* `docs/dvf_3_3_terminal_disposition_adjudication_plan.md`

포함 범위:

* read-only input inventory와 protected current authority surface snapshot
* executing-consumer member-row terminal adjudication denominator binding과 universe manifest 작성
* optional diagnostic roll-up conflict inventory 작성. 이 roll-up은 공식 completion denominator가 아니며, unique path 또는 semantic consumer object로 `1062`를 재해석하지 않는다.
* `2105`, `1062`, `311`, `163`, `148`, `252`, `59`, `27558`, `2084`, `21`의 role / axis / lifecycle 분리
* terminal disposition vocabulary와 sealed normalization vocabulary crosswalk 작성
* audit classification to terminal disposition crosswalk 작성
* `migrated_evidence_class` enum 작성
* `no-op`, `diagnostic-only`, `historical-only` positive reason enum 작성
* bound universe member별 evidence binding ledger 작성
* `conditional`, `blocked`, `unknown`, `pending`, unmatched residue inventory와 drain-down
* terminal disposition validator, focused unit tests, negative tests 작성
* denominator non-collapse, evidence completeness, terminal vocabulary exclusivity, protected surface no-mutation 검증
* optional current-route required-validation candidate patch 작성
* closeout report, claim-boundary check, ledger update packet 작성
* independent review / external gate status와 canonical promotion status 분리 기록

### Explicitly Out Of Scope

* vNext current authority cutover 재실행
* successor source manifest 재생성
* source facts / decisions / overlay support / rendered body 재작성
* runtime chunk payload 재생성 또는 live replacement
* Lua bridge export 계약 변경
* monolith `IrisLayer3Data.lua` runtime authority 복귀
* runtime enum, `publish_state`, `quality_state`, `runtime_state` 의미 변경
* Runtime Payload State Integrity branch 해소
* Denominator Lock 자체의 required-gate adoption
* current-route required validation adopted patch without explicit approval
* audit `classified_ledger.jsonl` 재산출 또는 mutation
* historical docs 전체 cleanup
* generated artifact 전체 재분류
* 2105 predecessor byte-level recovery
* Browser / Wiki / Tooltip behavior change
* public-facing wording, badge, sorting, filtering, hiding, recommendation, trust/confidence display
* package / Workshop / B42 / deployment readiness
* manual in-game QA, multiplayer validation, long-session runtime validation
* unrelated refactor or architecture redesign

---

## 3. Non-Goals

* `2105`를 consumer completion denominator로 사전 확정하지 않는다.
* `1062`, `311`, `163`, `148`, `252`, `59`를 같은 completion denominator로 collapse하지 않는다.
* `311`, `163`, `148`은 subset denominator이며 terminal adjudication completion denominator가 아니다.
* `2084 / 21`은 entry-axis counts이며 consumer-axis completion denominator가 아니다.
* subset evidence를 broad universe completion evidence로 승격하지 않는다.
* `actual_apply_eligible 163`을 live migration completion으로 over-count하지 않는다.
* readiness sandbox mutation을 `migrated` evidence로 직접 승격하지 않는다.
* `blocked`, `conditional`, `pending`, `review`, `unknown`, `deferred`, `needs_adjudication`을 terminal state로 허용하지 않는다.
* `conditional`을 `no-op`으로 default하지 않는다.
* unresolved rows를 `diagnostic-only` 또는 `historical-only`로 숨기지 않는다.
* migration evidence가 없다는 사실만으로 `no-op`, `diagnostic-only`, `historical-only`를 부여하지 않는다.
* sealed 7-value normalization vocabulary를 4-value vocabulary로 재정의하지 않는다.
* current-route validator/test/tool consumer와 live current authority consumer를 같은 surface로 취급하지 않는다.
* readiness sandbox mutation을 live migration evidence로 표현하지 않는다.
* machine PASS를 independent-review-complete canonical seal로 표현하지 않는다.
* tooling이 denominator / unit / roll-up decision을 추론해 author decision을 대체하지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 기준이다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 2026-06-19 current readpoint를 따른다.
* current source chain은 `dvf_3_3_input_manifest.json -> dvf_3_3_facts.jsonl -> dvf_3_3_decisions.jsonl -> dvf_3_3_overlay_support.jsonl`로 읽는다.
* live runtime deployable authority는 successor `IrisLayer3DataChunks.lua + IrisLayer3DataChunks/*.lua` 단일 chunk bundle이다.
* 2105 predecessor, 6-entry fixture, prior staging candidates, readiness artifacts는 current authority가 아니라 predecessor / comparison / migration / prerequisite trace다.
* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/classified_ledger.jsonl`, `change_required_index.md`, `change_forbidden_index.md`는 read-only audit input이다.
* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/executing_consumers.jsonl`와 `executing_consumer_impact.md`는 executing-consumer member-row universe binding의 read-only ground다.
* `executing_consumer_impact.md`는 executing-consumer member-row `1062` binding 시 required input이다. 부재 시 explicit allowed-absent policy가 없으면 universe binding은 `blocked`다.
* consumer migration input normalization의 durable downstream handoff는 `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase6/consumer_migration_reconciled_input_manifest.json`이다.
* normalization evidence의 `actual_apply_eligible 163 / no_op 148`은 downstream usability evidence이며 broad universe terminal completion evidence가 아니다.
* `docs/2105_baseline_consumption_audit_plan.md` missing-path rows는 non-apply / no-op reconciliation 대상이며 live checkout 복구나 migrated diff count 대상이 아니다.
* DVF 3-3 vNext current authority cutover evidence root는 `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_cutover/`다.
* Runtime Payload State Integrity evidence root는 `Iris/build/description/v2/staging/runtime_payload_state_integrity/`이며, this round does not reopen its branch decision.
* Consumer Universe Denominator Lock evidence root는 `Iris/build/description/v2/staging/consumer_universe_denominator_lock/`이며, `1062`, `311`, `163`, `148`, `27558`, `59`, `252`, `2105`, `2084`, `21`은 서로 다른 denominator / axis / lifecycle roles로 보존한다.
* `2105`는 runtime-entry/source/sealed successor entry count일 수 있으나 consumer completion denominator로 확정하지 않는다. Phase 1 binding 전에는 member adjudication을 시작하지 않는다.
* Plan-level universe decision: canonical terminal adjudication denominator is the executing-consumer member-row universe, grounded by the `1062` executing-consumer readpoint. The official unit is `executing_consumer_member_row`, not unique file path, semantic consumer object, runtime entry, source entry, accepted occurrence row, or readiness mutation row.
* The current repo-grounded `1062` readpoint is expected to join losslessly from `executing_consumers.jsonl` to `classified_ledger.jsonl`. The bound universe's internal predicate split is `49 yes / 111 conditional / 902 no == 1062`, while the global accepted-candidate change-required split remains `59 yes / 252 conditional == 311`.
* `59 / 252` are not the internal subset counts of the bound `1062` universe. They are Denominator Lock / accepted-candidate predicate-axis counts for the global `311` change-required subset.
* Denominator / unit / roll-up is an author-governance decision. Tooling may record, validate, and fail-loud on it, but may not infer or change it.
* A bound member row can be terminal only when that member row has positive evidence for exactly one terminal disposition. Any member row with `blocked`, `conditional`, `unknown`, `pending`, missing evidence, or incompatible terminal evidence blocks terminal closeout.
* Optional path-level or semantic-consumer roll-ups may show mixed terminal evidence and must remain diagnostic. No roll-up may hide unresolved member-row residue or replace the official `executing_consumer_member_row` denominator.
* final terminal vocabulary는 four-value projection이며, sealed source vocabulary는 source vocabulary로 보존한다.
* current-route required validation status는 `not_adopted`, `candidate_only`, `adopted` 중 하나로 기록한다.
* independent review / external gate status는 `review_pending`, `review_pass`, `review_failed` 중 하나로 기록한다.
* Claude-authored roadmap review or self-review is not independent verification for canonical promotion.
* `machine_complete_review_pending` is not canonical complete.
* For this Claude-authored-upstream round, `canonical_complete` requires machine PASS plus independent third-party review pass. Owner adoption may be recorded as an additional approval, but owner adoption does not replace the independent-review hard gate.
* `canonical_complete` implies `independent_review_status == review_pass`.
* Terminal member records use one common schema identity. Every generated ledger/report that carries terminal member records must include `schema_version` and `terminal_consumer_universe_id`.
* `dvf_3_3_terminal_disposition_adjudication_common.py` owns the row/member schema, identity resolver, and validation core. Generator scripts must import these surfaces instead of reimplementing identity resolution or schema checks.
* Denominator Lock, normalization, readiness, current-route, and runtime payload evidence may carry `review_pending` or round-local status. This transitive dependency status must be recorded in closeout and must not be promoted silently to adopted hard-gate authority.
* Dirty working tree가 있으면 이 계획의 의도된 파일과 무관한 변경은 보존한다.

---

## 5. Repository Areas Affected

### Code

Expected new tooling surfaces:

* `Iris/build/description/v2/tools/build/dvf_3_3_terminal_disposition_adjudication_common.py`
* `Iris/build/description/v2/tools/build/generate_dvf_3_3_terminal_disposition_universe.py`
* `Iris/build/description/v2/tools/build/generate_dvf_3_3_terminal_disposition_policy.py`
* `Iris/build/description/v2/tools/build/generate_dvf_3_3_terminal_disposition_ledger.py`
* `Iris/build/description/v2/tools/build/resolve_dvf_3_3_terminal_disposition_residues.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_terminal_disposition_adjudication.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_terminal_disposition_adjudication.py`

`dvf_3_3_terminal_disposition_adjudication_common.py` is the single implementation owner for:

* terminal member record schema and `schema_version`
* `terminal_consumer_universe_id` constants / binding helpers
* stable member / source-row identity resolver
* terminal disposition enum and reason enum definitions
* shared validation core used by generators, resolver, and validator

Generator scripts may produce many phase artifacts, but they must call the shared identity resolver and validation core instead of carrying local schema forks.

Expected new focused tests:

* `Iris/build/description/v2/tests/test_terminal_disposition_adjudication.py`

Protected current authority surfaces that must not be mutated:

* `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
* `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
* `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
* `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`
* `Iris/build/description/v2/output/dvf_3_3_rendered.json`
* `Iris/build/description/v2/output/style_normalization_changes.jsonl`
* `Iris/build/description/v2/output/compose_requeue_candidates.jsonl`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`
* `Iris/build/package/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/build/package/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`
* `Iris/build/package/Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`
* `Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua`

Protected generated/package peer paths may be allowed-absent only if the Phase 0 source input inventory marks them as `absent_at_baseline` with explicit role, hash-null policy, and expected producer. An `absent_at_baseline` path becoming present is a mutation unless produced by an explicitly scoped validation/package command recorded in the command log.

### Docs

Direct docs:

* `docs/dvf_3_3_terminal_disposition_adjudication_plan.md`
* `docs/dvf_3_3_terminal_disposition_adjudication_closeout.md`
* `docs/dvf_3_3_terminal_disposition_policy.md`
* `docs/dvf_3_3_terminal_disposition_claim_boundary.md`
* `docs/dvf_3_3_terminal_disposition_ledger_packet.md`

Authority docs updated only after execution evidence exists:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Read-only context docs:

* `docs/Philosophy.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/runtime_payload_state_integrity_plan.md`
* `docs/consumer_universe_denominator_lock_plan.md`
* `docs/dvf_3_3_vnext_consumer_migration_input_normalization_plan.md`
* `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_plan.md`

Read-only evidence inputs:

* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/executing_consumers.jsonl`
* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/executing_consumer_impact.md`
* `Iris/build/description/v2/staging/consumer_universe_denominator_lock/phase4/consumer_universe_denominator_registry.json`
* `Iris/build/description/v2/staging/consumer_universe_denominator_lock/phase4/consumer_universe_denominator_crosswalk.jsonl`
* `Iris/build/description/v2/staging/consumer_universe_denominator_lock/phase8/independent_review_status.json`

### Config

Expected unchanged by default:

* `pytest.ini`
* `Iris/_docs/round3/current_route_required_validations.json`

Optional candidate output only, unless explicit adoption is in scope:

* `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase5/current_route_required_validations.candidate_patch.json`
* `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase5/current_route_required_validation_adoption_approval.json`
* `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase5/current_route_required_validations.rollback_snapshot.json`
* `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase6/owner_confirmed_universe_binding.json`
* `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase6/owner_adoption_record.json`

### Generated Artifacts

All generated artifacts stay under:

* `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/`

Primary expected artifacts:

* `phase0/source_input_inventory.json`
* `phase0/protected_current_surface_baseline.json`
* `phase0/current_route_required_validations_baseline.json`
* `phase0/allowed_absent_path_policy.json`
* `phase0/terminal_member_common_schema.json`
* `phase0/identity_resolver_contract.json`
* `phase0/validation_core_contract.json`
* `phase0/scope_lock_report.json`
* `phase1/disposition_universe_binding.md`
* `phase1/universe_unit_author_decision.json`
* `phase1/occurrence_to_consumer_rollup_policy.json`
* `phase1/terminal_consumer_universe_manifest.json`
* `phase1/terminal_consumer_universe_denominator_report.json`
* `phase1/terminal_consumer_universe_scope_lock.md`
* `phase1/denominator_cross_reference.json`
* `phase2/terminal_disposition_policy.md`
* `phase2/terminal_disposition_crosswalk.md`
* `phase2/audit_classification_terminal_crosswalk.md`
* `phase2/audit_classification_terminal_crosswalk.json`
* `phase2/migrated_evidence_classes.json`
* `phase2/terminal_reason_enums.json`
* `phase2/terminal_disposition_schema.json`
* `phase2/terminal_disposition_allowed_values.json`
* `phase2/projection_function_spec.md`
* `phase3/terminal_disposition_ledger.jsonl`
* `phase3/terminal_disposition_evidence_binding_report.json`
* `phase3/terminal_disposition_counts.json`
* `phase3/terminal_disposition_unmatched_rows.json`
* `phase3/terminal_disposition_coverage_report.json`
* `phase4/blocked_conditional_initial_inventory.json`
* `phase4/conditional_resolution_ledger.jsonl`
* `phase4/blocked_conditional_resolution_ledger.jsonl`
* `phase4/blocked_conditional_drain_down_report.json`
* `phase4/blocked_conditional_zero_verdict.json`
* `phase4/predicate_vs_normalization_reconciliation_report.json`
* `phase5/final_terminal_disposition_machine_report.json`
* `phase5/common_schema_conformance_report.json`
* `phase5/identity_resolver_single_source_report.json`
* `phase5/validation_core_conformance_report.json`
* `phase5/protected_surface_no_mutation_verdict.json`
* `phase5/current_route_required_validations.candidate_patch.json`
* `phase6/final_terminal_disposition_report.json`
* `phase6/terminal_disposition_claim_boundary_check.json`
* `phase6/terminal_disposition_ledger_update_packet.md`
* `phase6/disposition_completeness_report.json`
* `phase6/owner_confirmed_universe_binding.json`
* `phase6/owner_adoption_record.json`
* `phase6/independent_review_status.json`

---

## 6. Planned Changes

### Change 0 - Source Input Inventory and Scope Lock

Purpose:

Freeze read-only input paths, protected current authority surfaces, and execution boundaries before any terminal universe binding or ledger generation.

Files:

* `Iris/build/description/v2/tools/build/dvf_3_3_terminal_disposition_adjudication_common.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_terminal_disposition_adjudication.py`
* `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase0/*`

Implementation Notes:

* Build a source input inventory with artifact role, path, existence, sha256, count expectations, freshness requirement, and read-only policy.
* Include audit, `executing_consumers.jsonl`, `executing_consumer_impact.md`, normalization, readiness, cutover, runtime payload guard, denominator lock, current-route validation, and rejected-delta correction inputs.
* Freeze the common terminal member record schema in `terminal_member_common_schema.json`.
* Freeze the single identity resolver contract in `identity_resolver_contract.json`.
* Freeze the validation core contract in `validation_core_contract.json`.
* Snapshot protected current authority surfaces before generating staging evidence.
* Snapshot `Iris/_docs/round3/current_route_required_validations.json` if adoption is in scope or if a candidate patch is emitted.
* Emit `allowed_absent_path_policy.json` for protected generated/package peer paths that are absent at baseline.
* Record upstream dependency status, including Denominator Lock, normalization, readiness, current-route, and runtime payload guard review/canonical status.
* Fail loud if a required evidence family is absent, ambiguous, or stale.
* Emit `scope_lock_report.json` with `runtime_mutation_allowed=false`, `source_mutation_allowed=false`, `rendered_mutation_allowed=false`, `chunk_mutation_allowed=false`.

Validation:

* Source inventory paths resolve or are marked with explicit allowed-absent policy.
* Common schema, identity resolver contract, and validation core contract are emitted before any member ledger generation.
* `executing_consumer_impact.md` resolves for executing-consumer member-row universe binding or the round blocks with explicit reason.
* Protected baseline captures every declared protected surface.
* Absent-at-baseline protected paths becoming present are flagged unless produced by an explicitly scoped validation/package command.
* Any attempted mutation outside staging fails the no-mutation check.

---

### Change 1 - Denominator Binding and Terminal Universe Scope Lock

Purpose:

Bind the exact adjudication denominator and prevent subset counts from being reused as completion claims.

Files:

* `Iris/build/description/v2/tools/build/generate_dvf_3_3_terminal_disposition_universe.py`
* `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase1/*`

Implementation Notes:

* Define `terminal_consumer_universe_id`.
* Record the plan-level author decision that the canonical terminal adjudication denominator is the `1062` executing-consumer member-row universe.
* Define the official universe unit as `executing_consumer_member_row`; reject unique path, semantic consumer object, source entry, runtime entry, accepted occurrence row, `311`, `163`, `148`, `59`, or `252` as silent substitute units.
* Resolve the "2105 consumer" expression against Denominator Lock terminology.
* Separate runtime-entry/source count, executing-consumer universe, accepted occurrence rows, change-required subset, readiness/sandbox mutation rows, no-op subset, diagnostic-only surfaces, and historical-only surfaces.
* State positively that `311`, `163`, and `148` are subset counts, while `2084 / 21` are entry-axis counts, not completion denominators.
* State positively that `59 / 252` are global `311` predicate-axis counts and not the internal split of the bound `1062` universe.
* Record the bound-universe predicate split as `49 yes / 111 conditional / 902 no == 1062` for the current repo-grounded readpoint.
* Use `executing_consumers.jsonl` rows as the official member rows and `classified_ledger.jsonl` rows as lossless joined classification evidence.
* Define optional deterministic roll-up diagnostics only for path/object summaries. Roll-up diagnostics cannot replace the official member-row denominator and cannot be a success denominator.
* Emit owner confirmation schema for universe binding with `denominator`, `unit`, `rollup_rule`, `accepted_claim_boundary`, `confirmer`, `timestamp`, and `relation_to_author_governance_decision` fields.
* Produce a universe manifest listing every member requiring terminal disposition.
* Stop Phase 2 if denominator binding is ambiguous, if author decision is absent, or if any official member row is unmatched against classification evidence.

Validation:

* Universe manifest count equals declared bound denominator.
* Every member has stable identity and maps to source evidence anchors.
* No member is included only by count equality.
* Every terminal disposition has positive member-row evidence.
* Optional path/object roll-up conflicts are reported but cannot hide member-row residues or redefine success.
* Owner-confirmed universe binding is validated as a claim-boundary artifact, not just a form file.
* Owner-confirmed universe binding includes all required fields: `denominator`, `unit`, `rollup_rule`, `accepted_claim_boundary`, `confirmer`, `timestamp`, and `relation_to_author_governance_decision`.
* Denominator substitution check rejects `2105`, `311`, `163`, `252`, or `59` as silent stand-ins for the bound denominator.
* Denominator unit substitution check rejects unique file path count, semantic consumer object count, source-entry count, runtime-entry count, and readiness mutation count as silent stand-ins for `executing_consumer_member_row`.

---

### Change 2 - Terminal Disposition Vocabulary and Crosswalk Seal

Purpose:

Seal the four-value terminal vocabulary and define its relationship to sealed normalization vocabulary without redefining source terms.

Files:

* `Iris/build/description/v2/tools/build/generate_dvf_3_3_terminal_disposition_policy.py`
* `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase2/*`
* `docs/dvf_3_3_terminal_disposition_policy.md`

Implementation Notes:

* Define allowed terminal dispositions: `migrated`, `no-op`, `diagnostic-only`, `historical-only`.
* Define disallowed final states: `blocked`, `conditional`, `pending`, `review`, `unknown`, `deferred`, `needs_adjudication`.
* Define `blocked` as transient processing/failure state only.
* Define `conditional` as transient predicate/reasoning state only.
* Require final reports to expose `blocked_count` and `conditional_count`.
* Require final reports to expose `unknown_count` and `pending_count`.
* Define `migrated_evidence_class` as a closed enum:
  * `prior_current_cutover_row_evidence`
  * `prior_cutover_authority_role_migration_evidence`
  * `adopted_current_route_authority_migration_evidence`
  * `live_authority_role_migration_ledger`
  * `explicitly_validated_current_successor_consumer_update`
* State that `actual_apply_eligible` and readiness sandbox mutation are insufficient by themselves for `migrated`.
* Define `terminal_reason_code` as a closed enum for non-migrated terminal classes:
  * `no-op`: `already_current_successor_contract`, `false_positive_no_mutation`, `generated_no_mutation`, `non_apply_missing_path`, `denominator_role_not_apply_target`, `preserved_reference_no_behavior_change`
  * `diagnostic-only`: `diagnostic_validator_surface`, `diagnostic_report_surface`, `non_authority_test_tool_diagnostic_path`
  * `historical-only`: `predecessor_trace`, `archive_or_done_doc`, `historical_fixture`, `staging_predecessor_evidence`, `generated_historical_trace`
* State that lack of migration evidence is never a positive terminal reason.
* Define additive 7-value-to-4-value crosswalk:
  * `actual_apply_eligible` can project to `migrated` only if terminal migration evidence exists.
  * `no_op`, `generated_no_mutation`, `false_positive_no_mutation` project to `no-op`.
  * `diagnostic_preserved` projects to `diagnostic-only`.
  * `historical_preserved` projects to `historical-only`.
  * `blocked` remains non-terminal.
* Define a separate additive audit-classification-to-terminal-disposition crosswalk for non-`311` broad-universe members. This crosswalk must not redefine sealed normalization vocabulary.
* Define audit-only positive evidence classes for bound member rows outside the normalization/readiness ledgers. A member row may use audit-only positive evidence only when it has Gate A/B classification, an executing route, a classified ledger join, and an allowed audit classification terminal reason.
* The current repo-grounded readpoint expects `902` bound member rows to be audit-only with respect to normalization/readiness ledgers. These rows must be terminalized through positive audit classification evidence, not by lack of migration evidence.
* Any audit classification not mapped by the audit classification terminal crosswalk remains `blocked` and prevents success closeout.

Validation:

* Terminal vocabulary validator rejects non-terminal final states.
* Projection is total, deterministic, and sealed-vocabulary-preserving.
* `migrated_evidence_class` is present and allowed for every `migrated` member.
* `terminal_reason_code` is present and allowed for every `no-op`, `diagnostic-only`, and `historical-only` member.
* Audit classification crosswalk covers broad-universe members outside the `311` normalization subset.
* Audit-only positive evidence covers expected non-normalization/readiness bound rows and records route class, classified disposition, migration disposition, and terminal reason.
* Unmapped audit classification fails validation and cannot be coerced into `no-op`, `diagnostic-only`, or `historical-only`.
* Members cannot be terminal without evidence class and reason.
* Lack of evidence remains `blocked`.
* Sealed normalization vocabulary input remains unchanged.

---

### Change 3 - Evidence Binding and Full-Universe Ledger Construction

Purpose:

Bind every member of the bound universe to evidence and assign exactly one terminal disposition or loud non-terminal `blocked` before drain-down.

Files:

* `Iris/build/description/v2/tools/build/generate_dvf_3_3_terminal_disposition_ledger.py`
* `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase3/*`

Implementation Notes:

* Read audit ledger, normalization artifacts, readiness sandbox ledger, cutover evidence, denominator lock evidence, runtime payload guard evidence, and current-route validation evidence as read-only input.
* For each member, emit stable identity, universe id, source predicate, source vocabulary disposition, projected terminal disposition, `migrated_evidence_class`, `terminal_reason_code`, evidence family, source artifact, source row identity / anchor, authority impact, mutation status, optional roll-up diagnostic summary, and reason fields.
* Every terminal member record emitted by any phase artifact must include `schema_version` and `terminal_consumer_universe_id`.
* Resolve stable member and source-row identities only through the shared identity resolver in `dvf_3_3_terminal_disposition_adjudication_common.py`.
* Distinguish live current authority consumer, validator/test/tool current-route consumer, diagnostic-only validator/test/tool consumer, historical/generated/staging/docs trace, false-positive/no-change member, already migrated member, and no-op member.
* Apply the audit classification crosswalk for broad-universe members outside the `311` normalization subset.
* Treat unmatched members as explicit failures, not omitted rows.

Validation:

* Every member in universe manifest appears exactly once in terminal ledger.
* Every member record conforms to the common schema version.
* Every member record carries `schema_version` and `terminal_consumer_universe_id`.
* Identity values are produced by the shared identity resolver.
* Coverage equals bound denominator exactly.
* Every `migrated` member has migration / cutover / current-route evidence.
* Every `migrated` member has allowed `migrated_evidence_class`.
* Every `no-op` member has a no-op reason enum.
* Every `diagnostic-only` member has diagnostic surface classification.
* Every `historical-only` member has historical / predecessor / staging / docs classification.
* Every non-migrated terminal member has allowed positive `terminal_reason_code`.
* No terminal member is assigned solely because migration evidence is absent.
* No member uses raw count equality as evidence.

---

### Change 4 - Conditional-Series Resolution and Blocked Drain-Down

Purpose:

Remove all final `conditional` residues and drain all `blocked`, `unknown`, `pending`, and unmatched residues before success closeout.

Files:

* `Iris/build/description/v2/tools/build/resolve_dvf_3_3_terminal_disposition_residues.py`
* `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase4/*`

Implementation Notes:

* Build initial inventory for conditional predicate rows/members, blocked rows/members, unknown/pending/unmatched residues.
* Classify residues by missing evidence anchor, moved path / relocated anchor, current-vs-diagnostic ambiguity, historical-vs-current ambiguity, migration evidence missing, no-op reason missing, duplicate row identity, denominator mismatch, or source/runtime mutation required.
* Resolve each residue into one of the four terminal dispositions where evidence allows.
* Keep any residue without positive terminal evidence as `blocked`; do not default to `no-op`, `diagnostic-only`, or `historical-only`.
* If resolution requires source/runtime mutation, stop and open a separate correction scope.
* Keep before/after trace for every drained row/member.
* Treat `blocked_count > 0` as valid incomplete readpoint, not success.

Validation:

* `conditional_count == 0` for success closeout.
* `blocked_count == 0` for success closeout.
* `unknown_count == 0` and `pending_count == 0`.
* Every drained row/member has before/after trace.
* Validator fails if a row/member was auto-drained without evidence.
* Validator fails if any terminal resolution uses lack of evidence as its reason.
* Predicate-axis `59 / 252` and normalization-axis `163 / 148` reconcile independently without substitution.
* Global numeric closure invariants hold: `59 + 252 == 311` and `163 + 148 == 311`.
* Bound-universe numeric closure invariant holds: `49 + 111 + 902 == 1062`.
* Validator fails if `59 / 252` are treated as the internal split of the bound `1062` universe.

---

### Change 5 - Terminal Disposition Validator and Guard Integration

Purpose:

Make terminal disposition closure machine-checkable and optionally consumable by current-route required validations.

Files:

* `Iris/build/description/v2/tools/build/validate_dvf_3_3_terminal_disposition_adjudication.py`
* `Iris/build/description/v2/tests/test_terminal_disposition_adjudication.py`
* `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase5/*`

Implementation Notes:

* Validate denominator exactness, universe unit decision, occurrence-to-consumer roll-up conflicts, coverage exactness, terminal vocabulary exclusivity, zero blocked/conditional/unknown/pending counts, evidence completeness, denominator non-collapse, `migrated_evidence_class`, terminal reason enums, audit classification crosswalk coverage, no-op reason completeness, diagnostic/historical positive classification, current-authority exclusion, protected current authority no-mutation, allowed-absent path policy, anchor staleness, common schema conformance, shared identity resolver use, validation core conformance, sealed vocabulary preservation, and additive-only artifact behavior.
* Emit `final_terminal_disposition_machine_report.json`.
* Emit `common_schema_conformance_report.json`, `identity_resolver_single_source_report.json`, and `validation_core_conformance_report.json`.
* Emit candidate patch for `current_route_required_validations.json` only as a separate candidate artifact.
* Keep required validation status explicit: `not_adopted`, `candidate_only`, or `adopted`.
* If status is `adopted`, require an explicit approval artifact and rollback snapshot.

Validation:

* Focused terminal disposition tests pass.
* Protected current authority surface shows no unintended mutation.
* Candidate required-validation patch schema validates if emitted.
* Candidate patch cannot be counted as adopted without explicit approval artifact.
* Adopted required-validation gate passes only if adoption is explicitly in scope.
* Historical and diagnostic routes remain separate.
* Every generated ledger/report that carries terminal member records includes `schema_version` and `terminal_consumer_universe_id`.
* Identity resolver implementation is single-source; local generator identity resolver forks fail validation.
* Phase artifacts may be many, but validation core remains one shared implementation.
* Negative tests include:
  * `test_consumer_rollup_rejects_mixed_child_residue`
  * `test_consumer_rollup_rejects_blocked_child_occurrence`
  * `test_consumer_rollup_rejects_missing_child_positive_reason`
  * `test_consumer_rollup_rejects_hidden_child_occurrence_residue`

---

### Change 6 - Closeout, Ledger Reflection, and Claim Boundary Seal

Purpose:

Close the round without overclaiming and without reopening prior seals.

Files:

* `docs/dvf_3_3_terminal_disposition_adjudication_closeout.md`
* `docs/dvf_3_3_terminal_disposition_claim_boundary.md`
* `docs/dvf_3_3_terminal_disposition_ledger_packet.md`
* `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase6/*`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Implementation Notes:

* Write final closeout report with exact terminal counts: bound universe, migrated, no-op, diagnostic-only, historical-only, blocked, conditional, unknown, pending.
* Require terminal count sum to equal bound universe count.
* Preserve predecessor trace without turning it into current authority.
* State that this closeout is additive to prior migration/cutover seals and not a reopening.
* Record required-validation adoption status separately from candidate patch status.
* Record independent review / external gate status.
* Record canonical promotion status separately from machine PASS.
* Use `machine_complete_review_pending` for machine PASS while independent third-party review pass or canonical promotion remains pending.
* Use `canonical_complete` only when machine PASS is paired with independent third-party review pass.
* Record owner adoption separately from independent review. Owner adoption may confirm universe binding or approve canonical promotion paperwork, but it does not waive or replace independent review for this round.
* Emit `owner_confirmed_universe_binding.json` with `denominator`, `unit`, `rollup_rule`, `accepted_claim_boundary`, `confirmer`, `timestamp`, and `relation_to_author_governance_decision`.
* Emit `owner_adoption_record.json` if owner adoption occurs; schema must keep `owner_adoption_status` separate from `independent_review_status`.
* Emit `independent_review_status.json` for this terminal disposition round. It must include `reviewed_artifacts`, `reviewed_hashes`, `reviewer_identity_or_label`, `verdict`, `timestamp`, and `claim_boundary_acknowledgement`.
* Record transitive dependency status for Denominator Lock, normalization, readiness, current-route, and runtime payload evidence, especially any `review_pending` state.
* Sync `DECISIONS.md`, `ARCHITECTURE.md`, and `ROADMAP.md` only after execution evidence exists and without claiming release readiness.

Validation:

* Final report machine status is PASS.
* Closeout claim-boundary checker passes.
* Ledger packet contains no runtime/source/rendered/package mutation claim.
* Required validation adoption state is explicit.
* Independent review status is explicit.
* Machine complete and canonical complete are not collapsed.
* `canonical_complete` implies `independent_review_status == review_pass`.
* Owner adoption status is recorded separately and cannot satisfy independent review.
* Owner-confirmed universe binding is present and validates the actual denominator/unit/roll-up/claim boundary for canonical closeout.
* Independent review status validates the reviewed artifact set and reviewed hashes for canonical closeout.
* Upstream dependency review/canonical status is explicit.
* Denominator claim guard or documented round-local equivalent passes.
* Additive-only verdict passes.

---

## 7. Validation Plan

### Automated Validation

Required commands must be recorded exactly in Phase 0. The planned default commands are:

* `uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_terminal_disposition_adjudication.py --mode generate`
* `uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_terminal_disposition_adjudication.py --require-complete`
* `uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_terminal_disposition_adjudication.py"`

If current-route adoption is explicitly in scope:

* `uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure`

If `uv` is unavailable, validation is blocked, not passed. Do not claim validation passed unless the exact relevant command exits with code 0.

Required invariants:

* `terminal_rows_total == bound_terminal_consumer_universe_count`
* `migrated_count + no_op_count + diagnostic_only_count + historical_only_count == terminal_rows_total`
* `blocked_count == 0`
* `conditional_count == 0`
* `unknown_count == 0`
* `pending_count == 0`
* `59 + 252 == 311` as global accepted-candidate predicate-axis closure
* `163 + 148 == 311`
* `49 + 111 + 902 == 1062` as bound executing-consumer member-row predicate-axis closure
* canonical terminal adjudication denominator is the `1062` executing-consumer member-row universe
* official terminal universe unit is `executing_consumer_member_row`
* unique file path count, semantic consumer object count, source-entry count, runtime-entry count, accepted occurrence count, readiness mutation count, `311`, `163`, `148`, `59`, and `252` cannot become the official completion denominator without a plan amendment
* every terminal disposition has positive member-row evidence
* no member-row residue is hidden by optional path/object roll-up diagnostics
* every member has exactly one terminal disposition
* every member has an evidence anchor
* every generated ledger/report carrying terminal member records includes `schema_version` and `terminal_consumer_universe_id`
* all terminal member records conform to one common schema version
* all stable member and source-row identities are resolved through the shared identity resolver
* validation core is single-source and reused by generators / resolver / validator
* every `migrated` member has allowed `migrated_evidence_class`
* every `no-op` member has allowed positive no-op reason
* every `diagnostic-only` member has allowed positive diagnostic reason and is excluded from current authority mutation
* every `historical-only` member has allowed positive historical reason and is excluded from current route hard gate
* no terminal disposition is assigned solely due to lack of migration evidence
* non-`311` broad-universe members are covered by audit classification terminal crosswalk
* expected audit-only bound member rows outside normalization/readiness ledgers are positively terminalized through Gate A/B classification, executing route evidence, classified ledger join, and allowed audit terminal reason
* unmapped audit classifications remain blocked and prevent success closeout
* `executing_consumer_impact.md` is present for executing-consumer member-row `1062` binding or universe binding blocks
* protected absent-at-baseline paths have explicit allowed-absent role and hash-null policy
* anchor staleness and relocated anchor checks pass
* candidate current-route validation patch is not counted as adopted without explicit approval artifact
* no denominator collapse
* no protected current authority mutation
* no monolith re-entry
* no legacy `active / silent` current vocabulary re-entry
* sealed normalization vocabulary is not redefined
* four-value projection is total and deterministic
* machine complete and canonical complete are separate fields
* if `closeout_state == canonical_complete`, `independent_review_status == review_pass`
* `independent_review_status.json` includes reviewed artifacts, reviewed hashes, reviewer identity or label, verdict, timestamp, and claim-boundary acknowledgement
* `owner_confirmed_universe_binding.json` includes denominator, unit, roll-up rule, accepted claim boundary, confirmer, timestamp, and relation to author-governance decision
* owner adoption is a separate field and does not replace independent review

### Manual Validation

* Inspect closeout wording for release/package/Workshop/manual-QA/semantic-quality overclaim.
* Inspect terminal policy and crosswalk for sealed-vocabulary preservation.
* Inspect denominator report for count-substitution or role collapse.
* Inspect current-route candidate/adopted status separation.
* Inspect independent review / external gate status.
* Review `git diff --stat` and `git diff` before closeout.

### Validation Limits

This execution does not require:

* multiplayer validation
* in-game manual QA
* long-session runtime validation
* external mod ecosystem compatibility sweep
* package release validation beyond an explicitly scoped current-route/package gate
* public-facing UI validation
* semantic text quality validation
* runtime parity remeasurement unless a separate correction scope is opened
* deployment validation
* Workshop validation
* B42 validation
* full historical artifact byte reproducibility
* full test discovery unless an exact full-discovery command is explicitly added to Phase 0

---

## 8. Risk Surface Touch

### Authority Surface

Limited / governance-only.

This round creates terminal disposition ledger / projection / completeness verdict authority. It must not mutate current source authority, rendered authority, runtime chunk authority, package authority, quality authority, publish authority, or runtime policy authority.

### Runtime Behavior Surface

None.

Runtime Lua behavior must not change. Browser / Wiki / Tooltip rendering must not change. Runtime chunks must not be regenerated by this round.

### Compatibility Surface

Limited to validation surface only.

If the terminal disposition validator is adopted into current-route required validation, it affects validation compatibility. It does not change runtime/API behavior.

### Sealed Artifact Surface

Additive-only.

Existing audit, normalization, readiness, cutover, runtime payload, denominator lock, and migration seal artifacts are read-only input. New artifacts are appended under the terminal disposition staging root and docs closeout surfaces.

### Public-Facing Output Surface

None.

No user-facing wording, tooltip text, browser display, wiki panel copy, recommendation, sorting, filtering, hiding, badge, trust/confidence display, or quality exposure change is authorized.

---

## 9. Risk Analysis

### Architecture Risk

* High: terminal adjudication may accidentally become a new authority migration route instead of a governance ledger.
* High: `2105` may be misread as consumer completion denominator despite Denominator Lock separation.
* High: tooling may infer universe unit / roll-up decision instead of enforcing the author decision.
* High: `1062` may be misread as unique file paths or semantic consumer objects instead of executing-consumer member rows.
* High: `59 / 252` may be misread as the internal split of the bound `1062` universe instead of global `311` predicate-axis counts.
* High: sealed 7-value normalization vocabulary may be silently redefined by the four-value projection.
* Medium: schema drift can occur if generators define local row/member schemas instead of importing the common schema.
* Medium: identity drift can occur if multiple generators reimplement identity resolution.
* Medium: `2084 / 21` entry-axis counts may be confused with consumer-axis completion counts.
* Medium: current-route required validation candidate patch may be confused with adopted validation.

### Runtime Risk

* Low if protected surface no-mutation guard is enforced.
* High if a blocked row is "fixed" by mutating current source/rendered/runtime surfaces inside this adjudication scope.
* Medium if generated chunks, bridge output, or package peer paths are touched during evidence gathering.

### Compatibility Risk

* Low for runtime/API compatibility because this round is governance-only.
* Medium for validation compatibility if current-route adoption is explicitly approved.
* Medium if historical/diagnostic tests are pulled into current route by a broad discovery pattern.

### Regression Risk

* High: subset evidence can be overextended to broad universe completion.
* High: non-`311` broad-universe members can be left without audit classification terminal crosswalk.
* High: expected audit-only bound members can be defaulted to terminal states without Gate A/B route and classified-ledger positive evidence.
* High: unmapped audit classifications can be accidentally terminalized instead of blocked.
* High: `actual_apply_eligible` or readiness sandbox mutation can be over-counted as `migrated`.
* High: unresolved rows can be hidden under `diagnostic-only`, `historical-only`, or `no-op`.
* High: member-row residue can be hidden by optional path/object roll-up diagnostics.
* Medium: moved paths or relocated anchors can break row identity.
* Medium: no-op reason enum can become too broad.
* Medium: absent generated/package paths can be misclassified as mutation or silently accepted after becoming present.
* Medium: owner adoption can be mistaken for independent review unless the status fields are kept separate.
* Medium: independent review can become too weak if reviewed artifacts and hashes are not recorded.
* Low: artifact naming drift, duplicated path traces, count summary ordering mismatch.

---

## 10. Rollback Plan

This is a staging / docs / validation governance round. Rollback is not live runtime rollback.

Rollback steps:

* Revert or remove new staging evidence under `Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/`.
* Revert new docs: closeout, policy, claim-boundary, ledger packet, and any authority-doc sync.
* Discard `current_route_required_validations.candidate_patch.json` if emitted.
* If `Iris/_docs/round3/current_route_required_validations.json` was explicitly adopted and then fails, revert it to `phase0/current_route_required_validations_baseline.json` or the explicit rollback snapshot emitted by Phase 5.
* Do not modify current source facts, decisions, overlay support, rendered output, runtime chunks, package chunks, or Lua bridge payload as rollback strategy.
* If protected current authority mutation is detected, fail the round, revert that mutation, and open a separate correction scope.
* If blocked or conditional residues remain, do not write success closeout. Preserve residue inventory as follow-up input only.
* If denominator binding or crosswalk is invalid, supersede with an additive correction entry. Do not silent-unseal prior artifacts.

Rollback-preservable debugging inputs:

* blocked/conditional inventory
* failed validation report
* unresolved row/member evidence
* denominator mismatch diagnostics
* crosswalk mismatch diagnostics

These are not current authority.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Preserve current authority chain and successor chunk authority.
* Keep runtime/build-time separation.
* Runtime Lua remains sealed payload renderer only.
* Do not give runtime Lua compose, repair, source validation, semantic quality judgment, or publish policy authority.
* Do not revive monolith `IrisLayer3Data.lua` as current runtime authority.
* Do not keep old chunks and successor chunks as dual current authority.
* Do not revive legacy `active / silent` as current writer / validator / runtime vocabulary.
* Do not interpret `adopted / unadopted` as quality-pass, publish policy, deletion, suppression, or UI visibility.
* Do not collapse `2105`, `1062`, `311`, `59`, `252`, `163`, `148`, `27558`, `2084`, `21` into one completion denominator.
* `blocked` and `conditional` are transient only and cannot be final success states.
* Candidate current-route validation patch and adopted current-route validation must remain separate.
* Existing audit / normalization / migration seal / denominator lock evidence is read-only input.
* This round is additive to prior seals and must not reopen or contradict them.
* Terminal universe unit and optional roll-up policy are author-governance decisions. Tooling must enforce `executing_consumer_member_row` as the official unit and must not infer a unique path or semantic consumer-object denominator.
* Row/member schema is single-source and versioned.
* Stable member and source-row identity resolution is single-source.
* Phase artifact count may grow, but validation core must remain one shared implementation.
* `migrated` requires allowed `migrated_evidence_class`; `actual_apply_eligible` and readiness sandbox mutation are not sufficient by themselves.
* `no-op`, `diagnostic-only`, and `historical-only` require positive terminal reason enums.
* Non-`311` broad-universe members require a separate audit classification terminal crosswalk.
* Audit-only bound members require Gate A/B classification, executing route evidence, classified-ledger join, and allowed audit terminal reason.
* `executing_consumer_impact.md` is required for executing-consumer member-row `1062` binding unless an explicit allowed-absent policy blocks or supersedes that route.
* Protected generated/package peer paths require allowed-absent policy if absent at baseline.
* Independent review / external gate status and canonical promotion status must be explicit.
* `machine_complete_review_pending` is not canonical complete.
* For this Claude-authored-upstream round, `canonical_complete` requires machine PASS plus independent third-party review pass.
* Owner adoption may be recorded separately but cannot replace independent review.
* `canonical_complete` implies `independent_review_status == review_pass`.
* Independent review status must record reviewed artifacts, reviewed hashes, reviewer identity or label, verdict, timestamp, and claim-boundary acknowledgement.
* Owner-confirmed universe binding must record denominator, unit, roll-up rule, accepted claim boundary, confirmer, timestamp, and relation to author-governance decision.
* No release readiness, package readiness, Workshop readiness, manual QA, B42 readiness, deployment readiness, or semantic quality completion claim is allowed.

---

## 12. Expected Closeout State

Expected execution closeout is one of:

* `canonical_complete`: allowed only if bound universe denominator is explicit, the official unit is `executing_consumer_member_row`, every member has exactly one positive evidence-backed terminal disposition, optional path/object roll-up diagnostics do not hide member-row residue, `blocked_count == 0`, `conditional_count == 0`, `unknown_count == 0`, `pending_count == 0`, validator commands exit 0, common schema / shared identity resolver / validation core conformance reports are PASS, protected surface no-mutation is PASS, claim-boundary check is PASS, `independent_review_status == review_pass`, independent review artifact set and hashes are recorded, and owner-confirmed universe binding is recorded. Owner adoption alone cannot satisfy this state.
* `machine_complete_review_pending`: allowed if machine validation passes but independent third-party review pass or canonical promotion remains pending. This state may claim machine-validated terminal disposition evidence, but not canonical completion.
* `partial`: required if any blocked, conditional, unknown, pending, unmatched official member row, denominator ambiguity, official-unit ambiguity, positive reason gap, migrated evidence gap, audit-only positive evidence gap, non-`311` crosswalk gap, allowed-absent policy gap, schema drift, identity resolver fork, validation core fork, independent review schema gap, owner binding schema gap, or evidence gap remains.
* `blocked`: required if success would require source/runtime/rendered/package mutation, prior seal reopen, missing required executing-consumer member-row input without allowed-absent policy, or denominator binding cannot be made from available evidence.

The expected first safe closeout target is `machine_complete_review_pending` unless independent third-party review is completed in the same execution round. A `canonical_complete` closeout must still avoid release/package/Workshop/manual-QA/semantic-quality claims.
