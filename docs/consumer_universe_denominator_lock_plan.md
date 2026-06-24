# Consumer Universe Denominator Lock Plan

> Status: planned / roadmap-derived / WARN review revisions incorporated / Cycle 2 PASS minor revisions incorporated / denominator governance only / no consumer migration execution / no cutover execution / no runtime mutation / independent review and required-gate adoption separated before canonical seal
> 작성일: 2026-06-19
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Roadmap input: `C:/Users/MW/.codex/attachments/efb4ca6f-9904-4cb7-8e0f-634d9ee55762/pasted-text.txt` / sha256 `AEA543790E4AA2B2CBA29389B0EE1EA299D392B5A0B2D78FA44EB77CD691E0F2`
> Review input: `C:/Users/MW/.codex/attachments/e23185a7-f4dd-4960-aa04-eaaad0d5f0fd/pasted-text.txt` / sha256 `E537A6245D8B9035E807340096FBD1C6EBA2BBB3DB0824141BA8EA984BC8E517` / WARN revisions basis
> Review input cycle 2: `C:/Users/MW/.codex/attachments/63f4f43f-f640-464c-aa0b-a0baeb8f7a09/pasted-text.txt` / sha256 `47F75D83C641397DECD6BD37433AA4D5976A69CD77EA7A46DFF2638D3665C2F0` / PASS with minor revisions basis
> Roadmap chain-of-custody: attachment text is the current normalized roadmap source for this plan; Phase 0 must emit canonicalization and path-resolution evidence before implementation claims
> Evidence root target: `Iris/build/description/v2/staging/consumer_universe_denominator_lock/`

---

## 1. Objective

DVF 3-3 vNext consumer migration / cutover 계열에서 함께 유통되는 `1062`, `311`, `163`, `148`, `27558`, `59`, `252`, `2105`, `2084`, `21` 등의 수치를 하나의 completion denominator처럼 오독하지 못하도록 denominator identity, axis, subset relationship, allowed claim, forbidden claim, and ledger read order를 봉인한다.

이 계획은 migration 실행 계획이나 cutover 실행 계획이 아니다. 목표는 새 migration을 수행하는 것이 아니라, 기존 audit / normalization / readiness / current-route evidence를 read-only input으로 소비해 다음 governance artifact를 만드는 것이다.

* denominator inventory
* denominator registry
* denominator crosswalk
* denominator relation graph
* claim vocabulary and claim boundary contract
* claim guard fixtures and report
* current-route validation integration candidate report or staging patch
* ledger reflection packet
* external independent review input manifest and review status packet
* final denominator lock closeout

완료 claim은 다음 범위로 제한한다.

```text
Candidate-only maximum claim:
Consumer universe denominator roles, subset relationships, axis boundaries, and completion claim boundaries
are generated, validated, and staged. Denominator misuse is guarded in generated staging evidence.
If sandbox validation is not run, the current-route output is only a schema-validated candidate patch.
If sandbox validation is run and restored, candidate current-route validation may be claimed for that sandbox only.

Future closeout blocking is not claimed until the required current-route validation gate is adopted.

This is not consumer migration execution, current authority cutover, runtime payload replacement,
source/rendered/runtime/package mutation, release readiness, or Workshop readiness.
Canonical seal requires independent review and an explicit required-gate adoption status.
```

Closeout blocking state contract:

* `candidate_guard_claim_allowed=true` means this round generated registry / crosswalk / relation / claim-guard evidence that can detect denominator misuse when the generated validator or candidate patch is explicitly run. It does not bind future closeout tooling by itself.
* `future_closeout_blocking_claim_allowed=false` means future disposition / migration / closeout reports are not yet guaranteed to fail through the current-route required validation path. In this state, final wording must say `generated / validated / staged`, not `future closeouts cannot`.
* `future_closeout_blocking_claim_allowed=true` is allowed only after `required_gate_adoption_status=adopted_required_gate`, the adopted required validation manifest is validated by the current-route runner, and the adopted gate is included in the closeout evidence.
* If the round ends candidate-only, the unresolved follow-up is required-gate adoption, not denominator identity definition.

---

## 2. Scope

이 계획은 read-only provenance input에서 population count를 수집하고, 각 count의 denominator identity와 claim boundary를 staging evidence로 고정한다.

포함 범위:

* denominator governance scope lock 작성
* input artifact manifest and hash / timestamp / role capture
* protected current authority surface precheck and final no-mutation verdict
* `198815`, `27869`, `21174`, `6695`, `1062`, `311`, `59`, `252`, `163 actual_apply_eligible`, `163 sandbox mutation rows`, `148`, `125`, `27558`, `2105`, `2084`, `21`, and zero-count guard populations such as missing apply-eligible rows population inventory
* source artifact / source field / owning round / read status 기록
* count별 axis, row-unit, source granularity, registry inclusion classification
* parent / child / peer / disjoint / different-axis / asserted-equality relationship binding
* `163 actual_apply_eligible`와 `163 sandbox mutation rows`의 숫자 일치와 row-key identity proof 분리
* `59`와 `252`의 source grounding 실패 시 각각 독립 non-LOCKED terminal status 기록
* `2105`, `2084`, `21`의 독립 runtime-context denominator entry와 `2084 + 21 == 2105` arithmetic validation
* all inventoried counts as registry entries or `registry_inclusion=inventory_only` records with forbidden claim coverage
* canonical registry and crosswalk 생성
* claim vocabulary / allowed claim verbs / forbidden claim verbs 작성
* positive and negative claim guard fixture 작성
* current-route required validation integration candidate 작성
* `candidate_guard_claim_allowed`와 `future_closeout_blocking_claim_allowed` 분리
* documentation ledger packet and closeout 작성
* external independent review gate 작성

Primary execution evidence root:

* `Iris/build/description/v2/staging/consumer_universe_denominator_lock/`

Plan artifact:

* `docs/consumer_universe_denominator_lock_plan.md`

Read-only input families:

* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/`
* `Iris/_docs/round3/current_route_required_validations.json`

Registry format decision:

* canonical denominator registry and relation graph use `.json`.
* row-like inventory, crosswalk, and fixture ledgers use `.jsonl` where one record per denominator / claim / relationship is clearer.
* Phase 4 emits `registry_format_decision.json` so this mixed format is explicit and reviewable.

### Explicitly Out Of Scope

* 2105 audit full re-run
* sealed count recalculation or correction
* current authority cutover execution
* live consumer migration execution
* runtime chunk replacement
* source facts / decisions mutation
* rendered output regeneration
* Lua bridge mutation
* package output mutation
* `IrisLayer3Data.lua` monolith restoration
* old chunks and successor chunks as dual current authority
* raw `consumer_migration_matrix.jsonl` or dry-run output as direct executor input
* `change_required_index.md` or `change_set.md` as executable instruction authority
* readiness sandbox diff as live migration completion
* `active / silent` legacy vocabulary restoration
* `adopted / unadopted` expansion into quality, publish, deletion, or suppression meaning
* `59` or `252` LOCKED denominator claim before source grounding
* immediate required-gate adoption into `Iris/_docs/round3/current_route_required_validations.json` without separate approval or independent review
* future closeout blocking claim while current-route integration remains candidate-only
* self-generated independent review report or placeholder review artifact
* release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game validation, semantic quality completion, or public-facing text quality acceptance

---

## 3. Non-Goals

* `311`을 `311 migrated rows`로 표현하지 않는다.
* `1062`를 applied migration denominator로 사용하지 않는다.
* `163 sandbox mutation rows`를 live consumer migration completion으로 승격하지 않는다.
* `163 actual_apply_eligible`와 `163 sandbox mutation rows`를 숫자 일치만으로 같은 denominator로 취급하지 않는다.
* `59` 또는 `252`를 source artifact / source field 없이 terminal migration disposition으로 쓰지 않는다.
* `148 no_op`를 migrated diff denominator에 포함하지 않는다.
* `27558 change-forbidden`을 no-op 또는 handled migration denominator로 축소하지 않는다.
* `198815`, `27869`, `21174`, `6695` 같은 inventory-only 후보를 denominator ID 없이 completion claim에 쓰지 않는다.
* candidate current-route patch를 adopted required gate처럼 표현하지 않는다.
* claim guard를 historical prose cleanup 도구로 만들지 않는다.
* denominator lock을 runtime feature, UI feature, Browser / Wiki / Tooltip policy, 또는 public-facing quality signal로 만들지 않는다.
* machine PASS를 independent review PASS나 canonical seal로 표현하지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 기준이다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 Iris DVF 3-3 readpoint와 non-claim boundary를 따른다.
* `2105 Baseline Consumption Audit`은 read-only migration-input readpoint다.
* 2105 audit에서 알려진 주요 counts는 `raw occurrence rows=198815`, `accepted candidate rows=27869`, `executing consumer count=1062`, `change required count=311`, `change forbidden count=27558`, `ambiguous-needs-adjudication=0`으로 읽는다.
* consumer migration input normalization에서 알려진 주요 counts는 `total normalized rows=311`, `actual_apply_eligible=163`, `no_op=148`, `missing path rows=125`, `missing apply-eligible rows=0`, `authority-role migration rule seed rows=163`, `complete claim allowed=false`로 읽는다.
* tooling readiness에서 알려진 주요 counts는 `row-level migration ledger=311`, `sandbox mutation rows=163`, `non-apply reconciled rows=148`, `actual diff-to-ledger mapped=163`, `unmapped=0`, `orphan=0`, `change-forbidden occurrence denominator=27558`, `change-forbidden mutation=0`으로 읽는다.
* 위 counts는 Phase 1 source location에서 artifact / field / read status로 다시 binding되어야 한다. 문서 prose만으로 LOCKED denominator가 되지 않는다.
* `59`와 `252`는 source located 전까지 각각 `UNLOCATED_REFERENT_PENDING`이며 completion claim 근거로 사용할 수 없다. Located 이후에도 source predicate가 모호하면 해당 entry만 `AMBIGUOUS_REFERENT`, count나 parent relation이 불일치하면 해당 entry만 `INCONSISTENT_REFERENT`로 둔다.
* `2105`, `2084`, `21`은 각각 독립 scalar-value registry entry여야 하며, combined `2105/2084/21` entry는 금지한다.
* `163 actual_apply_eligible`와 `163 sandbox mutation rows`의 equality-style relationship은 row-key 1:1 identity mapping이 `MATCHED`일 때만 LOCKED될 수 있다. Count equality only는 `COUNT_EQUAL_ONLY`로 기록하고 LOCKED relationship을 금지한다.
* every count must include `source_granularity=aggregate_count | row_enumerated | derived_count | unknown`. Aggregate-only counts cannot prove subset or row identity relationships without row-enumerated supporting evidence.
* `source_granularity=unknown` cannot support LOCKED status or completion claims.
* 모든 inventoried count는 registry에 들어가거나 `registry_inclusion=inventory_only`로 기록되어야 하며, `inventory_only` count에도 forbidden claim verbs와 claim guard coverage가 필요하다.
* current-route validation integration은 candidate patch / report를 만드는 범위다. required gate 편입은 independent review 또는 별도 author approval 전까지 보류한다.
* `candidate_guard_claim_allowed` means generated staging evidence and candidate validation can catch misuse; `future_closeout_blocking_claim_allowed` requires actual required-gate adoption.
* current-route closure count and tooling allowlist must not be expanded by this round's tools/tests. New tools/tests must be round-local unless a separate current-route adoption decision says otherwise.
* Independent review report is external input, not a generated artifact of this round. Tooling may record an external review manifest, but it must not materialize placeholder review content.
* If any generator is introduced, regenerate-twice fingerprint comparison is a mandatory deterministic gate.
* `freshness_marker` is input-derived and deterministic. Allowed sources are source artifact sha256, sealed artifact date from input, input manifest digest, or canonical path resolution digest.
* Run-specific values such as execution timestamp, local temp path, PID, elapsed time, or command invocation ID must live under `execution_metadata` and must be excluded from canonical artifact fingerprints.
* Phase 0 must emit canonical path resolution and roadmap input chain-of-custody reports before implementation evidence can claim source binding.
* Additional input families, including rejected-delta correction/re-parity artifacts, are `provenance_context` unless Phase 0 marks a specific file as `required`.
* runtime Lua remains a sealed payload renderer and does not compose, repair, validate source, normalize state, decide publish policy, or judge semantic quality.
* protected current authority surfaces must have `changed_count == 0`.
* If any assumed count drifts during source location, the round closes `blocked` or `revised_plan_needed`, not forced pass.
* Dirty working tree changes outside this plan are preserved.

---

## 5. Repository Areas Affected

### Code

Expected new build-time tooling surfaces, only during later implementation:

* `Iris/build/description/v2/tools/build/consumer_universe_denominator_lock_common.py`
* `Iris/build/description/v2/tools/build/generate_consumer_universe_denominator_lock_artifacts.py`
* `Iris/build/description/v2/tools/build/validate_consumer_universe_denominator_lock.py`
* `Iris/build/description/v2/tools/build/validate_consumer_universe_claim_guard.py`

Expected focused tests:

* `Iris/build/description/v2/tests/test_consumer_universe_denominator_lock.py`

These tools and tests are a round-local family. They must not be added to current-route core closure or current-route tooling allowlist unless Phase 6 records an approved adoption decision.

Runtime Lua, source facts, decisions, rendered output, chunk files, and package output are read-only surfaces in this plan.

### Docs

Direct plan artifact:

* `docs/consumer_universe_denominator_lock_plan.md`

Expected later docs:

* `docs/consumer_universe_denominator_lock_closeout.md`
* `docs/consumer_universe_denominator_lock_ledger_packet.md`

Read-only authority / context docs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ROADMAP.md`
* `docs/ARCHITECTURE.md` only if the implementation changes architecture wording; otherwise this remains no-op.
* `docs/PLAN_TEMPLATE.md`
* `docs/dvf_3_3_vnext_consumer_migration_input_normalization_plan.md`
* `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_plan.md`
* `docs/dvf_3_3_vnext_cutover_contract.md`

Canonical docs reflection targets, after validated implementation:

* `docs/DECISIONS.md`
* `docs/ROADMAP.md`
* `docs/ARCHITECTURE.md` only if implementation changes architecture wording; otherwise no-op

### Config

Expected direct mutation: none.

Candidate staging patch / report only:

* `Iris/_docs/round3/current_route_required_validations.json`

This plan does not directly edit the required validation manifest. Phase 6 emits a candidate patch and adoption report. Direct required-gate adoption requires separate approval or independent review clearance.

### Generated Artifacts

All generated artifacts stay under:

* `Iris/build/description/v2/staging/consumer_universe_denominator_lock/`

Expected artifact families:

* `phase0/scope_lock.md`
* `phase0/input_artifact_manifest.json`
* `phase0/input_artifact_hash_report.json`
* `phase0/canonical_path_resolution_report.json`
* `phase0/roadmap_input_chain_of_custody_report.json`
* `phase0/protected_surface_precheck.json`
* `phase0/no_runtime_mutation_boundary.json`
* `phase1/population_inventory.jsonl`
* `phase1/unlocated_report.md`
* `phase1/unsealed_count_referent_report.json`
* `phase1/source_location_report.json`
* `phase2/axis_classified_inventory.jsonl`
* `phase2/ambiguous_axis_report.md`
* `phase2/denominator_inventory_review.md`
* `phase3/relationship_bound_inventory.jsonl`
* `phase3/denominator_relation_graph.json`
* `phase3/arithmetic_consistency_report.json`
* `phase3/cross_ledger_row_identity_mapping.jsonl`
* `phase3/row_identity_match_report.json`
* `phase3/inconsistency_report.md`
* `phase4/registry_format_decision.json`
* `phase4/consumer_universe_denominator_registry.json`
* `phase4/consumer_universe_denominator_crosswalk.jsonl`
* `phase4/registry_schema_report.json`
* `phase4/denominator_crosswalk_validation_report.json`
* `phase4/inventory_only_guard_coverage_report.json`
* `phase5/claim_vocabulary.json`
* `phase5/claim_boundary_contract.md`
* `phase5/claim_guard_contract.json`
* `phase5/claim_guard_positive_fixtures.jsonl`
* `phase5/claim_guard_negative_fixtures.jsonl`
* `phase5/claim_guard_inventory_only_catch_all_report.json`
* `phase5/claim_guard_test_report.json`
* `phase6/current_route_required_validation_patch.json`
* `phase6/current_route_denominator_validation_report.json`
* `phase6/current_route_candidate_patch_sandbox_apply_restore_report.json`
* `phase6/current_route_closure_allowlist_regression_report.json`
* `phase6/protected_surface_no_mutation_verdict.json`
* `phase7/consumer_universe_denominator_lock_ledger_packet.md`
* `phase7/consumer_universe_denominator_lock_closeout.md`
* `phase7/documentation_claim_boundary_review.md`
* `phase8/external_independent_review_input_manifest.json`
* `phase8/independent_review_status.json`
* `phase8/final_consumer_universe_denominator_lock_report.json`
* `phase8/final_consumer_universe_denominator_lock_closeout.md`

---

## 6. Planned Changes

Common tool contract for all changes:

* All tools must read from explicit path allowlists emitted in Phase 0.
* All denominator records must include `denominator_id`, scalar `value`, `axis`, `row_unit`, `source_granularity`, `source_artifact`, `source_field`, `owning_round`, `registry_inclusion`, `authority_role`, `inclusion_predicate`, `exclusion_predicate`, `allowed_claim_verbs`, `forbidden_claim_verbs`, `completion_meaning`, `non_completion_boundary`, deterministic `freshness_marker`, and `status`.
* `freshness_marker` must be derived only from source artifact sha256, sealed artifact date from input, input manifest digest, or canonical path resolution digest. It must not contain generation time, run ID, local temp path, or other run-specific values.
* `authority_role` must be `claim_boundary_governance_only`; registry entries cannot become source authority, runtime authority, package authority, or cutover authority.
* All crosswalk records that relate audit / normalization / readiness rows must include `row_identity_key`, `audit_row_id`, `normalization_row_id`, `readiness_row_id`, `source_path`, `source_line_or_anchor`, `anchor_digest`, `identity_match_status`, and `identity_match_basis`.
* `identity_match_status` is one of `MATCHED`, `PARTIAL`, `UNMATCHED`, or `NOT_APPLICABLE`.
* `identity_match_basis` is one of `exact_id`, `relocated_anchor`, `path_line_digest`, `manifest_mapping`, `non_apply`, or `not_applicable`.
* All validation reports must emit `machine_contract_status`, `governance_closeout_status`, `complete_claim_allowed`, `canonical_seal_allowed`, `required_gate_adoption_status`, `candidate_guard_claim_allowed`, `future_closeout_blocking_claim_allowed`, and `independent_review_required`.
* Unknown status, missing source, stale source, ambiguous axis, or unsupported completion claim must fail loud.
* No tool may write source facts, decisions, rendered output, runtime Lua, runtime chunks, Lua bridge payload, or package output.

### Change 1 - Phase 0 Scope Lock and Input Artifact Freeze

Purpose:

Fix this round as denominator governance and freeze all read-only input artifacts before any denominator claim is made.

Files:

* `docs/consumer_universe_denominator_lock_plan.md`
* `Iris/build/description/v2/staging/consumer_universe_denominator_lock/phase0/*`

Implementation Notes:

* Create `scope_lock.md` stating this is not consumer migration execution, not cutover, and not runtime mutation.
* Build `input_artifact_manifest.json` from the 2105 audit, normalization, readiness, current-route integration, rejected-delta correction, and required-validation surfaces.
* Build `canonical_path_resolution_report.json` that resolves every configured repo-relative and absolute input path, and records `required`, `optional`, `allowed_absent`, or `blocked_missing`.
* Build `roadmap_input_chain_of_custody_report.json` that records the attachment hash, line-ending normalization rule, any canonical `.md` companion status, and the exact normalized bytes used for implementation planning.
* Include at minimum the following verified read-only inputs when present:
  * `Iris/build/description/v2/staging/2105_baseline_consumption_audit/classified_ledger.jsonl`
  * `Iris/build/description/v2/staging/2105_baseline_consumption_audit/change_required_index.md`
  * `Iris/build/description/v2/staging/2105_baseline_consumption_audit/change_forbidden_index.md`
  * `Iris/build/description/v2/staging/2105_baseline_consumption_audit/executing_consumers.jsonl`
  * `Iris/build/description/v2/staging/2105_baseline_consumption_audit/raw_occurrences.jsonl`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase6/consumer_migration_reconciled_input_manifest.json`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase6/row_disposition_ledger.for_readiness.jsonl`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase4/authority_role_migration_rule_seed.jsonl`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase2/missing_required_path_disposition_ledger.readiness_schema_preview.jsonl`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase5/downstream_command_surface_compatibility_manifest.json`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase3/row_level_migration_ledger.jsonl`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase4/actual_diff_to_ledger_report.json`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/consumer_migration_reconciled_input_manifest.json`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/command_surface_mapping.for_current_cutover.json`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/final_tooling_readiness_contract_report.json`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase7/final_current_route_guard_integration_report.json`
  * `Iris/_docs/round3/current_route_required_validations.json`
* Record missing optional inputs as `allowed_absent` or `blocked_missing`; do not synthesize counts.
* Mark rejected-delta correction / re-parity files as `provenance_context` unless the plan explicitly promotes a single file to `required`.
* Capture protected surface hashes before generating denominator artifacts.

Validation:

* all required input artifacts exist or have explicit blocked disposition.
* all input artifacts have path, role, sha256, timestamp, and read-only status.
* canonical path resolution has no unresolved required input.
* roadmap input chain-of-custody records the normalized source and hash rule.
* no output is written outside the dedicated staging root and plan doc.
* protected surface precheck records `changed_count == 0`.

---

### Change 2 - Phase 1 and Phase 2 Population Inventory / Axis Classification

Purpose:

Locate every population count, bind it to source artifact / source field, and classify its axis before any denominator is locked.

Files:

* `Iris/build/description/v2/staging/consumer_universe_denominator_lock/phase1/*`
* `Iris/build/description/v2/staging/consumer_universe_denominator_lock/phase2/*`

Implementation Notes:

* Generate `population_inventory.jsonl` for all roadmap counts:
  * `198815`
  * `27869`
  * `21174`
  * `6695`
  * `1062`
  * `311`
  * `59`
  * `252`
  * `163 actual_apply_eligible`
  * `163 sandbox mutation rows`
  * `148`
  * `125`
  * `27558`
  * `2105`
  * `2084`
  * `21`
  * `0 missing_apply_eligible_rows`
  * `0 ambiguous_needs_adjudication`
  * `0 change_forbidden_mutation`
  * `0 actual_diff_unmapped`
  * `0 actual_diff_orphan`
* Each record includes raw value, asserted label, source artifact, source field, sealed round, read status, limitation, source granularity, and registry inclusion.
* `source_granularity` is required for every record:
  * `aggregate_count`
  * `row_enumerated`
  * `derived_count`
  * `unknown`
* `registry_inclusion` is required for every record:
  * `anchor`
  * `inventory_only`
* Classify each located value into exactly one axis:
  * `consumer`
  * `occurrence_row`
  * `runtime_entry`
  * `validation_artifact`
  * `UNKNOWN`
  * `AMBIGUOUS`
* Expected starting classifications:
  * `1062` -> `consumer`
  * `198815`, `27869`, `311`, `27558`, `163`, `148`, `125` -> `occurrence_row`
  * `2105`, `2084`, `21` -> `runtime_entry`
  * current-route required count -> `validation_artifact`
* `59` and `252` may only become LOCKED independently after source location, source field, parent denominator, and predicate are validated for each scalar entry.
* Unlocated counts stay non-LOCKED with `UNLOCATED_REFERENT_PENDING`.
* Aggregate-only counts cannot prove subset, row identity, or migrated-diff completion without row-enumerated support.
* Every `inventory_only` record must still receive forbidden claim verbs and claim guard coverage.

Validation:

* all roadmap counts are either located or explicitly non-LOCKED.
* no located population has more than one axis.
* every population has `source_granularity` and `registry_inclusion`.
* `source_granularity=unknown` entries remain non-LOCKED and cannot support completion claims.
* every `inventory_only` population has forbidden claim verbs.
* no `UNKNOWN`, `AMBIGUOUS`, or unlocated population can support completion claim.
* consumer axis and occurrence-row axis cannot substitute for each other.

---

### Change 3 - Phase 3 Relationship / Containment Binding

Purpose:

Bind denominator relationships without inferring semantic identity from count equality alone.

Files:

* `Iris/build/description/v2/staging/consumer_universe_denominator_lock/phase3/*`

Implementation Notes:

* Create relation labels:
  * `is_universe`
  * `subset_of`
  * `derived_from`
  * `disjoint_from`
  * `peer_axis_of`
  * `different_axis_projection_of`
  * `asserted_equal_to`
  * `mapped_to`
  * `not_completion_of`
  * `negative_guard_for`
* Expected relationship assertions:
  * `311` is the change-required occurrence subset.
  * `163 actual_apply_eligible` is a subset of `311`.
  * `148 no_op` is a subset of `311`.
  * `163 + 148 == 311` must be validated arithmetically.
  * `27558` is the change-forbidden protection denominator with expected mutation count `0`.
  * `163 sandbox mutation rows` is readiness sandbox evidence and not live migration completion.
  * `1062` is broad executing consumer universe and not applied migration denominator.
  * `2105`, `2084`, and `21` are runtime baseline context entries and not migration denominators.
  * `2084 + 21 == 2105` must be validated arithmetically if all three entries are LOCKED.
  * `59` and `252` relations are recorded independently only after source grounding.
* `163 sandbox mutation rows == 163 actual_apply_eligible` may be recorded only as a relationship with row-key identity evidence, never as automatic denominator identity.
* Cross-ledger row identity mapping must emit one record per candidate row with:
  * `row_identity_key`
  * `audit_row_id`
  * `normalization_row_id`
  * `readiness_row_id`
  * `source_path`
  * `source_line_or_anchor`
  * `anchor_digest`
  * `identity_match_status`
  * `identity_match_basis`
* `DEN-NORMALIZED-APPLY-ELIGIBLE` to `DEN-READINESS-SANDBOX-MUTATION` can become `asserted_equal_to` or `mapped_to` only if all applicable identity records are `MATCHED`.
* `actual_diff_to_ledger mapped 163 / unmapped 0 / orphan 0` is readiness relation proof only when accompanied by row-key identity mapping.
* Count equality without row identity is recorded as `COUNT_EQUAL_ONLY` and cannot LOCK the relation.
* `PARTIAL` identity rows make the target relation non-LOCKED and must surface in `inconsistency_report.md`; they cannot be silently dropped or treated as partial success.
* `UNMATCHED` identity rows make the target relation non-LOCKED and must surface in `inconsistency_report.md`; they cannot be silently dropped or treated as no-op.
* `NOT_APPLICABLE` is valid only for non-apply rows or relationships that do not claim row identity.

Validation:

* subset count is less than or equal to parent count.
* `actual_apply_eligible + no_op == 311`.
* `2084 + 21 == 2105` if runtime entries are LOCKED.
* `change-forbidden mutation count == 0`.
* `DEN-NORMALIZED-APPLY-ELIGIBLE` to `DEN-READINESS-SANDBOX-MUTATION` relation requires identity match status `MATCHED`.
* any `PARTIAL` or `UNMATCHED` identity row blocks relation LOCKED status and appears in `inconsistency_report.md`.
* count-only equality emits `COUNT_EQUAL_ONLY` and leaves relationship non-LOCKED.
* every relationship has source evidence or remains non-LOCKED.
* relationship graph rejects count-only equivalence as semantic identity.

---

### Change 4 - Phase 4 Denominator Registry and Crosswalk

Purpose:

Create the canonical co-tracking artifact for denominator identity and claim boundaries.

Files:

* `Iris/build/description/v2/staging/consumer_universe_denominator_lock/phase4/*`

Implementation Notes:

* Emit `registry_format_decision.json`.
* Emit `consumer_universe_denominator_registry.json`.
* Emit `consumer_universe_denominator_crosswalk.jsonl`.
* Required named anchors use scalar values only:
  * `DEN-BROAD-CONSUMER-UNIVERSE` = `1062`
  * `DEN-CHANGE-REQUIRED-OCCURRENCE` = `311`
  * `DEN-NORMALIZED-APPLY-ELIGIBLE` = `163`
  * `DEN-READINESS-SANDBOX-MUTATION` = `163`
  * `DEN-NO-OP-RECONCILED` = `148`
  * `DEN-CHANGE-FORBIDDEN-PROTECTION` = `27558`
  * `DEN-RUNTIME-BASELINE-TOTAL` = `2105`
  * `DEN-RUNTIME-ADOPTED` = `2084`
  * `DEN-RUNTIME-UNADOPTED` = `21`
  * `DEN-REBASELINE-CHANGE-NEEDED` = `59`, only if located; otherwise non-LOCKED
  * `DEN-REBASELINE-CONDITIONAL` = `252`, only if located; otherwise non-LOCKED
* Every inventoried count must appear in the registry either as `registry_inclusion=anchor` or `registry_inclusion=inventory_only`.
* `registry_inclusion=inventory_only` entries are not named anchors, but they retain forbidden claim verbs and are covered by the claim guard.
* `value` is a single scalar per entry; packed values such as `59/252` and `2105/2084/21` are schema failures.
* Registry status vocabulary:
  * `LOCKED`
  * `UNLOCATED_REFERENT_PENDING`
  * `AMBIGUOUS_REFERENT`
  * `INCONSISTENT_REFERENT`
  * `SOURCE_STALE`
  * `COUNT_EQUAL_ONLY`
  * `REVIEW_PENDING`
  * `BLOCKED`

Validation:

* registry schema validation passes.
* every registry entry is traceable to Phase 1-3 output.
* every named anchor exists.
* every inventoried count has a registry entry or `inventory_only` entry.
* all registry values are scalar.
* `source_granularity` and `registry_inclusion` are present for every entry.
* entries with `source_granularity=unknown` are non-LOCKED.
* non-LOCKED entries cannot support completion claim.
* registry and crosswalk have matching denominator IDs.

---

### Change 5 - Phase 5 Claim Vocabulary, Claim Boundary, and Guard Fixtures

Purpose:

Define allowed and forbidden claim verbs per denominator and make denominator misuse fail-loud.

Files:

* `Iris/build/description/v2/staging/consumer_universe_denominator_lock/phase5/*`

Implementation Notes:

* Claim vocabulary includes:
  * `audited`
  * `classified`
  * `reconciled`
  * `normalized`
  * `apply_eligible`
  * `sandbox_mutated`
  * `diff_mapped`
  * `live_migrated`
  * `forbidden_mutation_zero`
* Every completion claim must include denominator ID.
* If a count appears in a completion claim but is not mapped to a LOCKED denominator ID, the claim fails.
* `registry_inclusion=inventory_only` counts must have forbidden claim verbs and are rejected as completion denominators unless a later revision promotes them to LOCKED anchors with source grounding.
* Negative fixtures include:
  * `311 rows migrated` without qualifier -> fail
  * `163 sandbox mutation rows means consumer migration complete` -> fail
  * `1062 consumers complete because 163 rows mutated` -> fail
  * `conditional 252 no longer matters because 163 applied` -> fail
  * `change-forbidden 27558 handled because no-op 148 exists` -> fail
  * `2105 runtime baseline proves migration completion` -> fail
  * `27869 accepted candidates complete` without LOCKED denominator ID -> fail
  * `198815 raw occurrence rows prove migration completion` -> fail
  * `21174 / 6695 subset complete` without source-grounded denominator role -> fail
* Positive fixtures include:
  * `311 change-required rows reconciled into 163 apply-eligible / 148 no-op` -> pass
  * `163 sandbox mutation rows mapped to ledger in readiness` -> pass
  * `27558 change-forbidden occurrences had 0 mutations` -> pass
  * `1062 broad executing consumers classified/dispositioned` -> pass only if source supports the exact claim
* Guard must inspect target docs / reports selected by Phase 5, not the whole historical repo by default. Historical prose scans are advisory unless the target is a closeout or ledger packet for this round.
* Guard output must separate:
  * `candidate_guard_claim_allowed`
  * `future_closeout_blocking_claim_allowed`

Validation:

* all positive fixtures pass.
* all negative fixtures fail.
* denominator ID missing from completion claim fails.
* inventoried count completion claim without LOCKED denominator ID fails.
* `registry_inclusion=inventory_only` completion claim fails.
* `status != LOCKED` denominator used as completion evidence fails.
* sandbox/readiness denominator used as live migration completion hard fails.
* broad audit denominator used as applied migration denominator hard fails.
* candidate-only guard report sets `candidate_guard_claim_allowed=true` and `future_closeout_blocking_claim_allowed=false`.

---

### Change 6 - Phase 6 Current Route Validation Integration Candidate

Purpose:

Connect denominator lock evidence to current-route validation as a candidate gate without silently changing required route authority.

Files:

* `Iris/build/description/v2/staging/consumer_universe_denominator_lock/phase6/*`
* `Iris/_docs/round3/current_route_required_validations.json` - candidate patch target only

Implementation Notes:

* Emit `current_route_required_validation_patch.json` but do not apply it directly.
* Emit `current_route_denominator_validation_report.json` with adoption status:
  * `candidate_patch_generated`
  * `independent_review_required`
  * `required_gate_adoption_pending`
* Allowed `required_gate_adoption_status` values:
  * `not_attempted`
  * `candidate_patch_generated`
  * `sandbox_validated_not_adopted`
  * `adoption_pending_author_approval`
  * `adopted_required_gate`
  * `adoption_rejected`
  * `blocked`
* Emit machine fields:
  * `required_gate_adoption_status`
  * `candidate_current_route_validation_status`
  * `candidate_guard_claim_allowed`
  * `future_closeout_blocking_claim_allowed`
* Allowed `candidate_current_route_validation_status` values:
  * `not_attempted`
  * `patch_schema_validated`
  * `sandbox_validated_and_restored`
  * `sandbox_failed`
  * `restore_failed`
* Candidate-only state must set:
  * `required_gate_adoption_status=candidate_patch_generated`
  * `candidate_current_route_validation_status=patch_schema_validated` unless sandbox apply / restore has run successfully
  * `candidate_guard_claim_allowed=true`
  * `future_closeout_blocking_claim_allowed=false`
* Only `required_gate_adoption_status=adopted_required_gate` may set `future_closeout_blocking_claim_allowed=true`.
* Enforcement state matrix:
  * `not_attempted`: no candidate patch and no future closeout blocking claim.
  * `candidate_patch_generated`: generated guard artifacts and schema-valid candidate patch only; no future closeout blocking claim.
  * `sandbox_validated_not_adopted`: sandbox proof exists and was restored; still no future closeout blocking claim.
  * `adoption_pending_author_approval`: adoption is waiting for explicit approval; no future closeout blocking claim.
  * `adopted_required_gate`: required validation gate is actually adopted and current-route validated; future closeout blocking may be claimed.
  * `adoption_rejected` or `blocked`: final claim is limited to generated evidence or blocked disposition.
* Candidate required artifacts:
  * denominator registry
  * denominator crosswalk
  * relation graph
  * claim guard report
  * protected no-mutation verdict
* Candidate fail conditions:
  * required denominator artifact missing
  * denominator count drift without successor scope
  * invalid completion claim
  * sandbox/readiness denominator used as live completion
  * broad audit denominator used as applied migration denominator
  * non-LOCKED denominator used as completion evidence
* If sandbox application is tested, apply the candidate patch to a temporary copy or snapshot, run the candidate validation, restore the original file, and emit `current_route_candidate_patch_sandbox_apply_restore_report.json`.
* Emit `current_route_closure_allowlist_regression_report.json` proving this round's tools/tests did not expand current-route core closure or current-route tooling allowlist without approval.

Validation:

* candidate patch is syntactically valid JSON.
* report says whether direct adoption is blocked, pending, or separately approved.
* `required_gate_adoption_status`, `candidate_current_route_validation_status`, `candidate_guard_claim_allowed`, and `future_closeout_blocking_claim_allowed` are present and consistent.
* protected current authority surface remains unchanged.
* current-route regression can pass with valid denominator artifacts when the candidate is applied in a sandbox; if sandbox is not run, the claim is limited to patch schema validation.
* removing a required denominator artifact makes the candidate validation fail in sandbox.
* sandbox apply / restore report proves `Iris/_docs/round3/current_route_required_validations.json` was restored.
* closure / allowlist regression proves no unauthorized expansion.

---

### Change 7 - Phase 7 Ledger Reflection and Documentation Closeout

Purpose:

Write closeout and ledger packet language without reopening closed readpoints or implying migration execution.

Files:

* `docs/consumer_universe_denominator_lock_closeout.md`
* `docs/consumer_universe_denominator_lock_ledger_packet.md`
* `Iris/build/description/v2/staging/consumer_universe_denominator_lock/phase7/*`

Implementation Notes:

* Closeout labels this as governance / validation closeout only.
* Ledger packet states:
  * broad consumer universe denominator locked or explicitly non-LOCKED.
  * cutover/migration subset denominator locked or explicitly non-LOCKED.
  * readiness/sandbox subset denominator locked or explicitly non-LOCKED.
  * forbidden mutation denominator locked.
  * denominator misuse fail-loud guard generated in staging / candidate validation.
  * future closeout blocking remains unclaimed until required-gate adoption status is adopted.
* Documentation claim review must reject:
  * migration execution claim
  * cutover completion claim
  * runtime/package/source/rendered mutation claim
  * release readiness claim
  * public-facing text quality claim
* Canonical docs update is allowed only after validated implementation and review. Until then this phase emits packet(s), not silent top-doc mutation.

Validation:

* ledger packet claim boundary review passes.
* no runtime/data/output mutation check passes.
* no release-readiness claim check passes.
* no closed-readpoint reopen check passes.
* closeout includes independent review status and completion ceiling.
* candidate-only closeout uses the limited claim:

```text
Denominator roles and claim boundaries are generated, validated, and staged.
Future closeout blocking is claimed only after the required current-route gate is actually adopted.
```

---

### Change 8 - Phase 8 Independent Review Gate and Final Closeout

Purpose:

Prevent self-asserted denominator governance artifacts from becoming canonical seal without review.

Files:

* `Iris/build/description/v2/staging/consumer_universe_denominator_lock/phase8/*`
* `docs/consumer_universe_denominator_lock_closeout.md`

Implementation Notes:

* Independent review report is an external input. This round may emit `external_independent_review_input_manifest.json`, but must not generate placeholder review content or count self-authored review text as independent.
* The external independent review manifest must record:
  * `review_state`
  * `external_review_input`
  * `materialized_by_this_round=false`
  * `review_report_path`
  * `review_report_sha256`
  * `reviewer_not_plan_author`
  * `reviewer_not_executor`
  * `reviewer_conflict_disclosure`
* `review_state=pending` is allowed for machine-PASS-before-review. In pending state, `review_report_path` and `review_report_sha256` may be null, but `materialized_by_this_round=false` is still required.
* `review_state=complete` is required for governance completion. In complete state, `review_report_path`, `review_report_sha256`, reviewer identity fields, and conflict disclosure are mandatory.
* Independent review must inspect:
  * every count has unique denominator role.
  * `59` and `252` source artifacts are independently identified or explicitly non-LOCKED.
  * `2105`, `2084`, and `21` are independent scalar runtime-context entries.
  * `311` cannot become `311 applied`.
  * `163 sandbox mutation` cannot become live completion.
  * `163 actual_apply_eligible` to `163 sandbox mutation` row-key mapping is `MATCHED` or relation remains non-LOCKED.
  * `1062` cannot become cutover/migration completion.
  * `27558` remains mutation-zero protection denominator.
  * no-op rows are excluded from migrated diff denominator.
  * inventory-only counts are covered by catch-all guard.
  * current-route candidate fails loudly on bad denominator claims.
  * registry regeneration is deterministic by regenerate-twice fingerprint comparison.
* Review result vocabulary:
  * `PASS`
  * `PASS_WITH_NOTES`
  * `BLOCKED_REFERENT_GAP`
  * `FAIL`
* `BLOCKED_REFERENT_GAP` is allowed only when ungrounded values are excluded from completion claims.

Validation:

* external independent review input manifest exists.
* independent review report is not materialized by this round.
* pending review state permits null path/hash before governance completion.
* complete review state requires path/hash and reviewer fields.
* reviewer independence fields are present:
  * `reviewer_not_plan_author`
  * `reviewer_not_executor`
  * `review_scope`
  * `certification_ceiling`
  * `reviewer_conflict_disclosure`
  * `plan_template_checked`
* final report status matches review result.
* complete claim allowed predicate is false without `PASS` or `PASS_WITH_NOTES`.
* ungrounded values are non-LOCKED when review returns `BLOCKED_REFERENT_GAP`.

---

## 7. Validation Plan

### Automated Validation

Do not claim validation passed unless the exact relevant command exits with code 0.

Expected commands after implementation:

```powershell
python -B Iris\build\description\v2\tools\build\generate_consumer_universe_denominator_lock_artifacts.py
python -B Iris\build\description\v2\tools\build\validate_consumer_universe_denominator_lock.py
python -B Iris\build\description\v2\tools\build\validate_consumer_universe_claim_guard.py
python -B -m unittest Iris.build.description.v2.tests.test_consumer_universe_denominator_lock
python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Required automated gates:

* input artifact existence and role validation
* input artifact hash / timestamp validation
* canonical path resolution validation
* roadmap input chain-of-custody validation
* protected surface precheck and final no-mutation verdict
* population source-location validation
* source-field completeness validation
* source granularity validation
* deterministic freshness marker validation
* registry inclusion validation
* axis classification validation
* row-key 1:1 identity correspondence validation for `DEN-NORMALIZED-APPLY-ELIGIBLE` and `DEN-READINESS-SANDBOX-MUTATION`
* relationship graph validation
* arithmetic consistency validation
* `2084 + 21 == 2105` runtime-context arithmetic validation
* registry schema validation
* scalar-only registry value validation
* registry / crosswalk denominator ID parity validation
* all inventoried counts registry or inventory-only coverage validation
* non-LOCKED completion claim rejection
* inventory-only count catch-all guard validation
* positive / negative claim guard fixture validation
* current-route candidate patch JSON validation
* candidate current-route sandbox apply / validate / restore validation if adoption is tested
* candidate current-route claim wording validation based on `candidate_current_route_validation_status`
* current-route closure / tooling allowlist unchanged regression
* documentation claim-boundary scan
* external independent review input-origin validation
* external review pending vs complete state validation
* independent review status validation
* regenerate-twice canonical artifact fingerprint comparison for every generated registry / crosswalk / relation / claim-guard output

If any command or required tool is missing, validation is blocked, not passed.

### Manual Validation

* Review Phase 0 input artifact manifest and blocked/allowed-absent dispositions.
* Review every unlocated population count, especially independent `59` and `252` entries.
* Review axis classification for `1062`, `311`, `163`, `148`, `27558`, `2105`, `2084`, and `21`.
* Review source granularity for aggregate-only values before accepting any subset relationship.
* Review relation graph so count equality does not imply denominator identity.
* Review cross-ledger row identity mapping for `163 actual_apply_eligible` and `163 sandbox mutation rows`.
* Review all `registry_inclusion=inventory_only` entries and forbidden claim verbs.
* Review claim guard negative fixtures for false negatives.
* Review claim guard positive fixtures for over-narrow matching.
* Review current-route candidate patch and confirm adoption state remains pending unless separately approved.
* Review current-route candidate patch sandbox restore report.
* Review current-route closure / allowlist regression report.
* Review ledger packet wording for no-migration, no-cutover, no-release, and no-runtime-mutation boundaries.
* Review external independent review input manifest and certification ceiling.

### Validation Limits

This plan will not validate:

* live consumer migration execution
* current authority cutover
* runtime chunk replacement
* source facts / decisions mutation
* rendered output regeneration
* Lua bridge mutation
* package output mutation
* package release readiness
* Workshop readiness
* deployment readiness
* B42 readiness
* manual in-game validation
* multiplayer validation
* long-session runtime validation
* external mod compatibility sweep
* semantic quality validation
* public-facing text quality review
* full `198815` row re-audit unless denominator referent drift is found

---

## 8. Risk Surface Touch

### Authority Surface

Touched, limited to denominator governance / validation authority.

This round creates denominator identity, relation, and claim-boundary artifacts. It does not change source authority, rendered authority, runtime authority, package authority, or current cutover authority.

### Runtime Behavior Surface

None.

Runtime Lua remains a sealed payload renderer. No runtime chunk, Lua bridge, Browser / Wiki / Tooltip behavior, or package output changes are in scope.

### Compatibility Surface

Low runtime compatibility impact. Moderate build-time governance impact.

Future migration / readiness / closeout tooling may need denominator IDs or registry lookup to make completion claims. That is intentional fail-loud governance behavior, not runtime compatibility behavior.

### Sealed Artifact Surface

Existing sealed artifacts are read-only inputs.

New artifacts are additive under `Iris/build/description/v2/staging/consumer_universe_denominator_lock/`. Existing audit, normalization, readiness, current-route, and rejected-delta evidence is not rewritten.

### Public-Facing Output Surface

None.

No tooltip, browser text, wiki text, badge, sorting, filtering, hiding, recommendation, trust, confidence, quality display, release note, or Workshop-facing output is changed.

---

## 9. Risk Analysis

### Architecture Risk

* Denominator registry may be over-read as source authority.
* Candidate current-route patch may be mistaken for approved required-gate adoption.
* `59` or `252` may be locked without sufficient source grounding.
* packed denominator entries may hide independent status, so scalar-only registry validation is required.
* `163` equality may collapse two different denominators.
* row identity mapping may be weakened into count-only equality.
* inventory-only counts may remain outside claim guard coverage.
* machine PASS may be mistaken for canonical seal.
* ledger wording may reopen closed readpoints.

### Runtime Risk

* Direct runtime risk is low because runtime surfaces are out of scope.
* Indirect risk exists if a misleading closeout causes a later operator to treat denominator lock as cutover authorization.
* No-mutation verification must include runtime Lua, bridge payload, chunks, rendered output, and package output where applicable.

### Compatibility Risk

* Claim guard may false-positive on historical prose if scan targets are too broad.
* Claim guard may false-negative if it only matches exact phrases.
* Current-route candidate may conflict with tooling allowlist / closure cap if adopted without review.
* Current-route candidate patch may leave the real manifest dirty unless sandbox restore is validated.
* Future closeout tools may fail until they emit denominator IDs.

### Regression Risk

* Source artifacts may drift or be renamed.
* Count-only reconciliation may pass while row identity differs.
* Crosswalk and registry may drift if generated by separate logic.
* Review may find that `59` or `252` cannot be sourced; final state must then exclude those values from completion claims independently.
* Generator output may drift without regenerate-twice fingerprint comparison.
* Independent review artifact may be accidentally self-generated without external-origin checks.
* Protected no-mutation verdict may fail if support tooling touches current surfaces.

---

## 10. Rollback Plan

Rollback is limited to additive governance / validation artifacts.

If validation fails:

* Mark the phase report `FAIL`, `BLOCKED_REFERENT_GAP`, `BLOCKED`, or `REVISED_PLAN_NEEDED`.
* Do not mutate sealed inputs to make counts match.
* Delete, archive, or supersede only the dedicated staging root:
  * `Iris/build/description/v2/staging/consumer_universe_denominator_lock/`
* Revert only new tools / tests / docs introduced by this plan.
* Remove or discard `phase6/current_route_required_validation_patch.json` if the candidate gate is wrong.
* If a required-gate adoption was separately approved and then fails, revert only that manifest change and preserve the failure report.
* If sandbox apply / restore fails, stop before closeout and restore `Iris/_docs/round3/current_route_required_validations.json` from the recorded snapshot.
* If row identity mapping is count-only, downgrade the relationship to `COUNT_EQUAL_ONLY` and keep it non-LOCKED.
* If a packed denominator entry is emitted, mark registry schema validation `FAIL`.
* If an independent review report was generated by this round, invalidate it and return to `review_pending`.
* If ledger wording is wrong, supersede it with an additive correction packet rather than rewriting predecessor evidence.
* Runtime chunks, source facts, source decisions, rendered output, Lua bridge payload, package output, and existing sealed evidence must not be changed as rollback for this plan.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Runtime / build-time separation must remain intact.
* FAIL-LOUD behavior is required for missing source, ambiguous axis, stale artifact, unsupported claim, and denominator substitution.
* Existing sealed readpoints are immutable provenance inputs.
* Additive amendment / supersession is preferred over silent history rewrite.
* Current authority ownership must not be bypassed.
* Raw audit and dry-run artifacts are provenance, not direct executor input.
* `change_required 311` is not `311 migrated`.
* `1062` broad consumers are not applied migration denominator.
* `163 sandbox mutation rows` are not live migration completion.
* `163 actual_apply_eligible` and `163 sandbox mutation rows` must remain distinct denominator IDs.
* Any equality or mapped relationship between those `163` populations requires row-key identity proof with `identity_match_status=MATCHED`.
* `148 no_op` must not enter migrated diff denominator.
* `27558` remains mutation-zero protection denominator.
* `59` and `252` cannot be LOCKED without independent source grounding.
* `2105`, `2084`, and `21` must be independent scalar runtime-context entries and must not become migration completion evidence.
* Every registry `value` must be a single scalar.
* All inventoried counts must have registry coverage as `anchor` or `inventory_only`.
* `inventory_only` counts must be forbidden as completion denominators.
* Aggregate-only counts cannot prove row-level subset or identity relationships.
* Denominator registry cannot authorize source/rendered/runtime/package mutation.
* Candidate current-route gate adoption requires independent review or separate author approval.
* Candidate guard and adopted required-gate enforcement must remain separate:
  * `candidate_guard_claim_allowed`
  * `future_closeout_blocking_claim_allowed`
* Machine PASS and governance complete must remain separate.
* Independent review is required for canonical seal, and the review report must be external input with `materialized_by_this_round=false`.
* Regenerate-twice fingerprint comparison is mandatory for generated denominator artifacts.
* Complete closeout must not claim release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA completion, or public-facing text quality acceptance.

---

## 12. Expected Closeout State

Expected closeout before independent review:

```json
{
  "machine_contract_status": "PASS",
  "governance_closeout_status": "review_pending",
  "complete_claim_allowed": false,
  "canonical_seal_allowed": false,
  "required_gate_adoption_status": "candidate_patch_generated",
  "candidate_current_route_validation_status": "patch_schema_validated",
  "candidate_guard_claim_allowed": true,
  "future_closeout_blocking_claim_allowed": false,
  "runtime_mutation_allowed": false
}
```

Expected closeout after independent review:

* `governance_closeout_status=complete` only if independent review returns `PASS` or `PASS_WITH_NOTES`.
* `complete_claim_allowed=true` only when all LOCKED denominator entries pass source, axis, relationship, registry, crosswalk, claim guard, no-mutation, and documentation boundary validation.
* `future_closeout_blocking_claim_allowed=true` only when required-gate adoption is actually applied and validated.
* `candidate_guard_claim_allowed=true` without adopted required gate is not enough to claim future closeout blocking.
* `BLOCKED_REFERENT_GAP` may close the round only if ungrounded values, especially `59` or `252`, are explicitly non-LOCKED and excluded from completion claims.

Machine PASS means:

* all major population counts are inventoried.
* every count is located or explicitly non-LOCKED.
* every inventoried count is represented as `registry_inclusion=anchor` or `registry_inclusion=inventory_only`.
* every `inventory_only` count has forbidden claim verbs and catch-all guard coverage.
* every LOCKED entry has scalar `value`, `source_granularity`, and source field.
* no LOCKED entry has `source_granularity=unknown`.
* every `freshness_marker` is input-derived and deterministic.
* run-specific fields are excluded from canonical artifact fingerprints.
* `1062` has a broad consumer denominator role.
* `311` has a change-required occurrence denominator role and cannot mean `migrated`.
* `163 actual_apply_eligible` is distinct from `163 sandbox mutation rows`.
* `163 actual_apply_eligible` to `163 sandbox mutation rows` relation is LOCKED only when row identity mapping is `MATCHED`; count-only equality remains non-LOCKED.
* `148 no_op` is excluded from migrated diff denominator.
* `27558 change-forbidden` is locked as mutation-zero protection denominator.
* `59` and `252` are independently source-grounded or non-LOCKED.
* `2105`, `2084`, and `21` are independent runtime baseline context entries and not migration completion.
* `actual_apply_eligible + no_op == 311` is validated or inconsistency is surfaced.
* `2084 + 21 == 2105` is validated when runtime entries are LOCKED.
* sandbox/readiness equality has evidence and is not inferred from numeric equality alone.
* candidate guard can reject migration / cutover / readiness completion without denominator ID in generated staging evidence when explicitly run.
* future closeout blocking is not claimed unless required-gate adoption status is actually adopted.
* non-LOCKED denominator cannot support completion claim.
* synthetic bad denominator completion claims fail.
* current-route validation either passes with denominator artifacts in sandbox or required-gate adoption remains explicitly pending.
* candidate current-route wording matches `candidate_current_route_validation_status`.
* current-route candidate patch sandbox apply / restore passes when tested.
* current-route closure / allowlist regression passes.
* regenerate-twice fingerprint comparison passes.
* external independent review input manifest may be `review_state=pending` for machine PASS.
* external independent review input manifest is `review_state=complete` with path/sha when governance completion is claimed.
* protected current authority surface remains unchanged.
* no runtime Lua behavior changes.
* no source facts / decisions / rendered output mutation.
* no runtime chunk mutation.
* no package output mutation.
* ledger packet states this is denominator governance, not migration execution.

Blocked closeout examples:

* required input artifact missing without allowed-absent disposition.
* source field for a LOCKED denominator cannot be located.
* source count differs from asserted count without successor scope.
* `59` or `252` is used as completion evidence while unlocated.
* `311` is claimed as migrated.
* `163 sandbox mutation rows` is claimed as live migration completion.
* `163 actual_apply_eligible` to `163 sandbox mutation rows` is LOCKED by count equality only.
* `1062` is claimed as applied migration completion.
* `27558` loses mutation-zero protection boundary.
* `2105/2084/21` appears as a packed registry value.
* `59/252` appears as a packed registry value.
* an inventory-only count is used as completion denominator.
* non-LOCKED denominator supports completion claim.
* current-route patch is applied without approval.
* candidate-only state claims future closeout blocking.
* candidate-only state claims sandbox validation while `candidate_current_route_validation_status=patch_schema_validated`.
* independent review report is materialized by this round.
* regenerate-twice fingerprint comparison is absent.
* `freshness_marker` contains generation time, run ID, temp path, or other run-specific values.
* protected no-mutation verdict fails.
* independent review is absent but closeout claims canonical seal.

Candidate-only maximum final claim:

```text
Denominator roles and claim boundaries are generated, validated, and staged.
Denominator misuse is guarded in generated staging evidence.
If candidate_current_route_validation_status=patch_schema_validated, the current-route artifact is only a schema-validated candidate patch.
If candidate_current_route_validation_status=sandbox_validated_and_restored, candidate current-route validation is completed for that sandbox.
Future closeout blocking is not claimed until the required current-route gate is actually adopted.
```

Adopted-gate maximum final claim, allowed only after required-gate adoption validation:

```text
Consumer universe denominator roles, subset relationships, axis boundaries, and completion claim boundaries
have been locked or explicitly marked non-LOCKED, and denominator misuse is fail-loud guarded by the adopted
current-route required validation gate.
```

Neither final claim authorizes consumer migration execution, current authority cutover, runtime chunk replacement, source authority mutation, rendered output mutation, Lua bridge mutation, package output mutation, release readiness, Workshop readiness, or public-facing behavior acceptance.
