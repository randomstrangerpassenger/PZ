# Iris DVF 3-3 Adapter / Native Body Plan Readiness Round Plan

> 상태: Draft v1.4-synthesis  
> 기준일: 2026-04-24  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> authority input: `Iris DVF 3-3 Adapter / Native Body Plan Readiness Round - 최종 통합 로드맵` (2026-04-24 user-provided synthesis)  
> 목적: persisted old 3-profile label, v2 resolver legacy fallback dependency, 78 fallback-dependent row의 execution readiness를 계측하고 후속 execution round가 소비할 active queue/checklist/definition artifact를 봉인하기 위한 planning authority를 고정한다. Silent 21 row는 이 round에서 execution queue가 아니라 inventory record로만 다룬다.  
> 실행 상태: planning authority only. 이 문서는 readiness round를 열기 위한 계획이며, 같은 turn에서 canonical artifact, rendered text, Lua bridge, staged runtime artifact, top docs closeout state를 변경하지 않는다.

---

## 0. Round Identity

### 0-1. 공식명

```text
Iris DVF 3-3 Adapter / Native Body Plan Readiness Round
```

내부 코드명:

```text
persisted_old_profile_and_legacy_fallback_inventory_readiness
```

### 0-2. 한 문장 scope lock

> 이번 round는 legacy 3-profile label과 v2 resolver fallback dependency를 줄이지 않고, 무엇이 남았는지와 다음 execution round가 어떤 순서로 제거해야 하는지를 observer-only readiness artifact로 봉인한다.

### 0-3. Round 성격

| 항목 | 값 |
|---|---|
| round type | `readiness_only` |
| writer role | `observer_only` |
| canonical artifact mutation | 금지 |
| rendered text mutation | 금지 |
| Lua bridge mutation | 금지 |
| in-game validation | 요구하지 않음 |
| legacy count reduction | 요구하지 않음 |
| 후속 execution round | 별도 opening decision 필요 |
| expected closeout state | `closed_with_persisted_old_profile_and_legacy_fallback_inventory_ready` |

이 계획에서 말하는 `artifact_mutation_allowed = false`는 sealed runtime/rendered/Lua/authority artifact 변경 금지를 뜻한다. Readiness round 자체의 신규 diagnostic/readiness artifact 생성은 아래 staging root 안에서만 허용한다.

```json
{
  "sealed_artifact_mutation_allowed": false,
  "diagnostic_readiness_artifact_creation_allowed": true,
  "diagnostic_artifact_root": "Iris/build/description/v2/staging/compose_contract_migration/adapter_native_body_plan_readiness_round/"
}
```

### 0-4. Staging root

후속 round 실행 시 신규 산출물 root는 아래로 고정한다.

```text
Iris/build/description/v2/staging/compose_contract_migration/adapter_native_body_plan_readiness_round/
```

권장 하위 디렉터리:

- `phase0_opening/`
- `phase1_inventory/`
- `phase2_definition/`
- `phase3_checklist/`
- `phase4_active_execution_queue/`
- `phase4_silent_inventory/`
- `phase4_summary/`
- `phase5_invariants/`
- `phase6_readiness_report/`
- `phase7_review/`
- `phase8_top_docs_update/`

---

## 1. Governance Baseline

### 1-1. Adopted upstream state

이 round는 아래 current state를 재심하지 않는다.

- `compose_profiles_v2.json + body_plan` is the default compose authority.
- Legacy `sentence_plan` access is explicit compatibility/diagnostic only after EDPAS.
- v2 resolver legacy label mapping remains present and is cleanup-round material.
- Current runtime/staged state remains `ready_for_in_game_validation`.
- Current baseline row count is `total 2105 / active 2084 / silent 21`.
- Current staged/workspace Lua hash target is `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`.
- `quality_baseline_v4` remains frozen as `strong 1316 / adequate 0 / weak 768`.
- Bridge availability remains `internal_only 617 / exposed 1467`.

### 1-2. In scope

- Count persisted old 3-profile labels in decisions rows.
- Count v2 resolver legacy mapping reach.
- Count rows whose rendered preview resolution source reaches `legacy_fallback_target`.
- Sub-classify the 78 fallback-dependent rows into:
  - `mechanical_ready`
  - `schema_gap`
- Seal active execution queues for a later execution round.
- Record silent 21 old-profile rows as inventory-only metadata records.
- Seal adapter removal checklist and resolver mode policy.
- Verify observer-only invariant preservation.
- Define new registration guard requirements.

### 1-3. Out of scope

- Removing `interaction_*` labels.
- Rewriting native 6-profile metadata.
- Removing or isolating the compatibility resolver fallback in code.
- Changing rendered text.
- Changing staged Lua or workspace Lua.
- Runtime QA / in-game validation.
- Cleaning up `sentence_plan` artifacts.
- Declaring deployed closeout or `ready_for_release`.
- Cutting over `quality_baseline_v4` to `quality_baseline_v5`.
- Adjusting publish split.

### 1-4. Status enum normalization

The roadmap requires free-text status seals to be avoided. This plan fixes the status enums as follows.

```text
new_registration_guard_status:
  undefined
  defined
  defined_and_dry_run_passed

adapter_removal_checklist_status:
  undefined
  defined
  sealed

execution_queue_status:
  undefined
  ready
  sealed

silent_metadata_inventory_status:
  undefined
  ready
  sealed
```

`execution_queue_status` semantics:

```json
{
  "undefined": "active execution queue artifacts have not been generated",
  "ready": "active execution queue artifacts are included in Phase 6 readiness report but have not passed Phase 7 review",
  "sealed": "active execution queue artifacts are included in closeout after Phase 7 review pass"
}
```

`silent_metadata_inventory_status` semantics:

```json
{
  "undefined": "silent metadata inventory artifact has not been generated",
  "ready": "silent metadata inventory artifact exists but has not passed Phase 7 review",
  "sealed": "silent metadata inventory artifact is included in Phase 6 report and Phase 7 review has passed"
}
```

The roadmap also uses `edpas_guard_verified_present` as a sample value for `new_registration_guard_status`. To avoid violating the enum rule, the readiness report should use:

```json
{
  "new_registration_guard_status": "defined_and_dry_run_passed",
  "new_registration_guard_evidence": "edpas_guard_verified_present"
}
```

If execution owners prefer `edpas_guard_verified_present` as the status value, Phase 0 must explicitly expand the enum before any Phase 6 report is sealed.

### 1-5. New registration guard dry-run policy

This round does not run a new default-mode guard dry-run. The `defined_and_dry_run_passed` status reuses already sealed EDPAS evidence.

```json
{
  "dry_run_policy": "edpas_evidence_reuse",
  "edpas_evidence_reference": [
    "unit_tests_299_pass",
    "design_review_guard_violations_0"
  ],
  "new_execution_required": false,
  "enum_value_semantics": {
    "undefined": "guard existence not verified",
    "defined": "guard presence verified in code path, no execution check",
    "defined_and_dry_run_passed": "guard presence verified plus EDPAS evidence confirms execution pass"
  }
}
```

### 1-6. Count field normalization

The roadmap labels Phase 5 as six preservation fields, but the table contains seven machine checks. This plan treats the table as authoritative and verifies all seven:

- `staged_lua_hash_unchanged`
- `workspace_lua_hash_unchanged`
- `runtime_state_unchanged`
- `additive_observer_lane_hashes_unchanged`
- `structural_reclassification_canonical_hashes_unchanged`
- `quality_baseline_v4_frozen`
- `internal_only_bridge_availability_unchanged`

### 1-7. Silent row scope decision

Silent rows are included in Phase 1 inventory and Phase 4 silent metadata inventory, but they are not sealed as execution input by this readiness round.

```json
{
  "silent_row_scope_decision": {
    "in_scope_for_this_readiness_round": "inventory_record_only",
    "execution_queue_seal_in_this_round": false,
    "persisted_old_profile_count_zero_target_applies_to": "active_only",
    "execution_round_silent_intake": "determined_at_execution_round_opening"
  }
}
```

---

## 2. Pre-Opening Gate

Round opening is blocked unless all gates pass.

| Gate | Check | Required value |
|---|---|---|
| G1 | runtime state | `ready_for_in_game_validation` |
| G2 | staged Lua hash | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |
| G3 | additive observer lane / structural reclassification sealed hash set | unchanged from 2026-04-24 sealed state |
| G4 | `quality_baseline_v4` split | `strong 1316 / adequate 0 / weak 768` |
| G5 | `internal_only` bridge availability | `internal_only 617 / exposed 1467` |
| G6 | EDPAS default-mode schema guard | present in code path |
| G7 | top-doc Hold scan | no Hold blocks this readiness round |
| G8 | row count baseline | `total 2105 / active 2084 / silent 21` |

G7 uses the following interpretation:

```json
{
  "top_doc_hold_scan": {
    "blocking_hold_categories": [
      "manual_in_game_validation_required_for_this_round",
      "deployed_closeout_required_before_this_round",
      "quality_baseline_cutover_required"
    ],
    "non_blocking_hold_categories": [
      "manual_in_game_validation_global_pending",
      "adapter_execution_round_pending",
      "sentence_plan_cleanup_pending"
    ]
  }
}
```

Gate failure terminal states:

- `blocked_by_runtime_state_drift`
- `blocked_by_lua_hash_drift`
- `blocked_by_observer_hash_drift`
- `blocked_by_quality_baseline_drift`
- `blocked_by_bridge_availability_drift`
- `blocked_by_missing_edpas_guard`
- `blocked_by_top_doc_hold`
- `blocked_by_row_count_drift`

---

## 3. Phase 0 - Opening Decision Sealing

### 3-1. Purpose

Seal the readiness-only design in `DECISIONS.md` before any inventory artifact is generated. The opening decision must state that only this readiness round is opened; the remaining execution/cleanup/QA problems still require separate openings.

### 3-2. Required opening decision content

The `DECISIONS.md` addendum must include:

- Pass criteria split into:
  - `invariant_checks`
  - `measurement_results`
  - `status_seals`
- The seven observer-only preservation checks from §1-6.
- Readiness-only character and separate future execution-round requirement.
- The fact that "six remaining problems" are not all opened by this decision; only this readiness round is opened.
- 78 fallback-dependent rows will be separated into:
  - native target exists / mechanical-ready
  - schema-gap
- Status enum values from §1-4.
- Dry-run semantics from §1-5.
- Silent inventory-only decision from §1-7.
- Readiness artifact path convention from §0-4.
- `artifact_mutation_allowed = false` meaning sealed runtime/rendered/Lua/authority artifacts are unchanged.
- Axis 4 resolver reach scope: `active_rendered_preview_only`.
- Resolver code modification ownership: execution round does not modify resolver code; cleanup round owns diagnostic isolation or removal.
- Schema-gap branch policy: if `fallback_schema_gap_count > 0`, full adapter-removal execution is blocked until schema extension round closes.
- `pass_criteria_contract.json` and Phase 6 readiness report must share the same schema identity.
- Phase 4 summary and Phase 6 readiness report must use shared count field names for `inventory_total`, `sealed_execution_queue_count`, and `silent_metadata_inventory_count`.

### 3-3. Required outputs

- `docs/DECISIONS.md` addendum
- `phase0_opening/opening_decision_reflection.md`
- `phase0_opening/pass_criteria_contract.json`

### 3-4. Gate

- Opening decision exists in `DECISIONS.md`.
- Planning §0 is re-cited in the opening reflection.
- `pass_criteria_contract.json` fixes the Phase 6 report schema version, required field set, and expected-vs-measured comparison rules.
- No execution phase starts before this gate passes.

---

## 4. Phase 1 - Inventory Measurement

### 4-1. Purpose

Measure three independent legacy source-shape axes over the sealed 2105-row baseline and write row-level inventory plus summary.

### 4-2. Inputs

- Canonical decisions artifact over 2105 rows.
- v2 resolver rendered preview artifact with `resolution_source`.
- Current default structural reclassification artifact:

```text
Iris/build/description/v2/staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/phase4_artifacts/body_plan_structural_reclassification.2105.jsonl
```

### 4-3. Axis definitions measured in this phase

Axis 2 - persisted source shape debt:

```text
compose_profile in {
  interaction_tool,
  interaction_component,
  interaction_output
}
```

Baseline expectation:

```json
{
  "persisted_old_profile_count": 2105,
  "active_old_profile_count": 2084,
  "silent_old_profile_count": 21
}
```

Axis 4 - compatibility resolver debt:

```text
rows where the v2 resolver applied legacy -> native compatibility mapping
```

Axis 4 scope is fixed to active rendered preview rows only.

```json
{
  "axis_4_resolver_reach_scope": "active_rendered_preview_only",
  "axis_4_expected_count": 2084,
  "silent_old_profile_resolver_reach": "not_measured_in_axis_4",
  "silent_old_profile_handling": "phase4_silent_metadata_inventory_record"
}
```

Baseline expectation: equals measured `active_old_profile_count`.

Axis 3 - true fallback dependency:

```text
resolution_source == "legacy_fallback_target"
```

Baseline expectation:

```json
{
  "legacy_fallback_target_count": 78
}
```

### 4-4. Fallback 78 subclassification

Each fallback-dependent row must receive one and only one subclass:

| subclass | definition |
|---|---|
| `mechanical_ready` | a valid native 6-profile target exists and execution can migrate by label/metadata swap without schema expansion |
| `schema_gap` | no current native 6-profile target exists; execution requires schema/profile decision before closure |

Summary field:

```json
{
  "fallback_78_subclass": {
    "mechanical_ready_count": "<measured>",
    "schema_gap_count": "<measured>"
  }
}
```

### 4-5. Resolution source enum

Phase 1 must record the `resolution_source` value exactly as emitted by the rendered preview and normalize it into the following validator enum:

```json
{
  "resolution_source_enum": [
    "body_plan_v2",
    "legacy_fallback_target",
    "pre_resolved",
    "cached",
    "diagnostic_lane",
    "unknown"
  ],
  "unknown_policy": "fail_unless_explicitly_justified_in_inventory_summary"
}
```

`legacy_fallback_target` is the only value that marks a row as true fallback-dependent.

### 4-6. Row-level inventory schema

Minimum row fields:

```json
{
  "full_type": "Base.Example",
  "row_state": "active",
  "persisted_compose_profile": "interaction_tool",
  "target_native_profile": "tool_body",
  "resolution_source": "body_plan_v2",
  "is_old_profile": true,
  "is_legacy_fallback_dependent": false,
  "fallback_subclass": null,
  "schema_gap_reason": null,
  "migration_class": "non_fallback_active_metadata_swap",
  "execution_queue": "non_fallback_active",
  "rendered_hash": "<hash>",
  "decision_row_hash": "<hash>"
}
```

Fallback-dependent row fields:

```json
{
  "is_legacy_fallback_dependent": true,
  "fallback_subclass": "mechanical_ready",
  "target_native_profile": "tool_body",
  "target_profile_status": "native_target_exists",
  "schema_gap_reason": null
}
```

For `fallback_subclass = "schema_gap"`, the row must instead use:

```json
{
  "fallback_subclass": "schema_gap",
  "target_native_profile": null,
  "target_profile_status": "schema_extension_required",
  "schema_gap_reason": "<required>"
}
```

Silent row inventory fields:

```json
{
  "row_state": "silent",
  "migration_class": "silent_metadata_inventory_only",
  "execution_queue": null,
  "proposed_target_native_profile": "tool_body",
  "target_native_profile": null,
  "execution_round_intake": "determined_at_execution_round_opening"
}
```

Silent rows use `proposed_target_native_profile` rather than `target_native_profile` because this readiness round records a mapping proposal only; it does not seal silent rows as execution input.

The example above is a single-case example. Phase 1 implementation follows `target_profile_resolution.silent_metadata_inventory.method` in §5-2 for each row's actual legacy label.

### 4-7. Outputs

```text
phase1_inventory/adapter_native_body_plan_readiness_inventory.2105.jsonl
phase1_inventory/adapter_native_body_plan_readiness_inventory.2105.summary.json
```

### 4-8. Gate

- `inventory_total == 2105`
- `active_count + silent_count == 2105`
- measured `persisted_old_profile_count == expected 2105`
- measured `active_old_profile_count == expected 2084`
- measured `silent_old_profile_count == expected 21`
- measured `legacy_fallback_target_count == expected 78`
- measured `non_fallback_active_metadata_swap_count + fallback_dependent_active_count == active_old_profile_count`
- measured `unresolved_profile_count == expected 0`
- `axis_2_active_count == axis_4_resolver_reached_count`
- `axis_4_resolver_reached_count == 2084`
- measured `fallback_mechanical_ready_count + fallback_schema_gap_count == legacy_fallback_target_count`
- no row has `resolution_source = "unknown"` unless the inventory summary carries an explicit fail/exception disposition

Axis 1, `sentence_plan` residue, is excluded from this inventory and reserved for a separate cleanup round.

---

## 5. Phase 2 - Legacy Source Shape Definition

### 5-1. Purpose

Define what counts as legacy. Phase 1 answers "how many"; Phase 2 answers "what exactly".

### 5-2. Required definitions

Persisted source shape debt:

```text
decisions.compose_profile in {
  interaction_tool,
  interaction_component,
  interaction_output
}
```

Mapping target:

```text
interaction_tool      -> tool_body
interaction_component -> material_body
interaction_output    -> output_body
```

Target native profile resolution:

```json
{
  "target_profile_resolution": {
    "non_fallback_active": {
      "method": "direct_legacy_profile_mapping",
      "target_native_profile": "derived_from_interaction_profile"
    },
    "fallback_mechanical_ready": {
      "method": "direct_legacy_profile_mapping_plus_fallback_subclass_validation",
      "target_native_profile": "derived_from_interaction_profile"
    },
    "fallback_schema_gap": {
      "method": "no_current_native_target",
      "target_native_profile": null,
      "target_profile_status": "schema_extension_required",
      "schema_gap_reason": "required"
    },
    "silent_metadata_inventory": {
      "method": "direct_legacy_profile_mapping_as_proposal_only",
      "proposed_target_native_profile": "derived_from_interaction_profile",
      "execution_target_status": "not_sealed_by_readiness_round"
    }
  }
}
```

`target_native_profile` is reserved for rows that the readiness round can place into a sealed active execution queue. `proposed_target_native_profile` is used for silent inventory rows because their execution intake is intentionally deferred to the execution round opening decision.

Compatibility resolver debt:

- Exact resolver file and mapping table or code block must be cited.
- Keys must match the old 3-profile label set above.
- Default path reach count is measured in Phase 1.

True fallback dependency:

- Diagnostic location is `resolution_source == "legacy_fallback_target"`.
- Current expected count is `78`.

Out-of-scope:

- `sentence_plan` artifact residue is not part of this round's legacy definition.
- EDPAS invariant must still verify that default mode does not execute `compose_profiles.json` `sentence_plan`.

### 5-3. Outputs

```text
phase2_definition/legacy_source_shape_definition.md
phase2_definition/legacy_profile_taxonomy.json
phase2_definition/resolver_dependency_taxonomy.json
```

`legacy_source_shape_definition.md` sealed hash must be referenced by the opening decision or by Phase 6 readiness report.

### 5-4. Gate

- Axis 2, Axis 3, Axis 4 definitions are disjoint and non-overlapping.
- Axis 1 exclusion is explicit.
- Resolver mapping reference is specific enough to be audited by file path and line/block identity.
- `legacy_profile_taxonomy.json` includes the target native profile resolution function above, including `schema_gap` null-target handling.

---

## 6. Phase 3 - Adapter Removal Checklist

### 6-1. Purpose

Turn adapter removal into measurable close criteria for the later execution round.

### 6-2. Resolver mode policy decision

Default recommendation:

```text
diagnostic-only isolation first; full removal reserved for explicit cleanup round
```

Rationale:

- EDPAS already reserves legacy access to explicit compatibility/diagnostic paths.
- This readiness round does not mutate resolver code.
- Execution round does not mutate resolver code; it only reduces data-level default path reach/dependency counts.
- Diagnostic-only isolation or complete removal is owned by a later resolver cleanup round after execution proves default path dependency count is zero.

### 6-3. Checklist minimum rows

| Item | Measurement method | Threshold | Pass timing |
|---|---|---|---|
| Axis 2 active close | active old-profile row count in canonical decisions | `== 0` | after execution round |
| Axis 2 total close | total old-profile row count in canonical decisions | deferred | execution round opening decides silent intake per §1-7 |
| Axis 4 close | default path legacy resolver reach count | `== 0` | after execution round |
| Axis 3 close | `resolution_source == legacy_fallback_target` count | `== 0` | after execution round |
| unresolved guard | `unresolved_profile_count` | `== 0` | after execution round |
| new registration guard | EDPAS/default-mode schema rejection path | present and dry-run passed | readiness closeout |
| runtime regression gate | rendered output delta after execution | `0 delta` | after execution round |
| Lua bridge validation | Lua bridge artifact hash | unchanged or re-validated | after execution round |

### 6-4. Gate spec

```json
{
  "readiness_round": {
    "persisted_old_profile_count_may_remain": true,
    "legacy_fallback_target_count_may_remain": true,
    "artifact_mutation_allowed": false,
    "overall_pass_condition": "active_execution_queues_and_silent_inventory_ready"
  },
  "execution_round": {
    "active_old_profile_count": 0,
    "legacy_fallback_target_count": 0,
    "adapter_default_dependency_count": 0,
    "default_path_legacy_fallback_reach_count": 0,
    "resolver_code_modification_allowed": false,
    "adapter_code_state_after_execution": "unchanged_from_readiness_closeout"
  },
  "resolver_cleanup_round": {
    "default_path_legacy_resolver_reachable": false,
    "diagnostic_mode_legacy_resolver_reachable": true,
    "adapter_status": "diagnostic_only_or_removed",
    "adapter_code_state_decision": "determined_at_cleanup_round_opening"
  }
}
```

### 6-5. Outputs

```text
phase3_checklist/adapter_removal_checklist.md
phase3_checklist/adapter_removal_gate_spec.json
phase3_checklist/legacy_resolver_mode_policy.md
```

### 6-6. Gate

- All checklist rows contain measurement method, threshold, output artifact, pass value.
- Gate spec is machine-readable JSON.
- Resolver mode policy explicitly chooses diagnostic-only isolation as the recommended cleanup-round next state unless Phase 0 records a different branch.
- Execution round gate does not require or permit resolver code modification.

---

## 7. Phase 4 - Active Execution Queues and Silent Inventory Record

### 7-1. Purpose

Seal active execution queues and record silent metadata inventory separately. Only Queue A and Queue B are sealed execution inputs by this readiness round. Silent 21 rows are inventory records only.

### 7-2. Queue A - Non-Fallback Active Metadata Swap

```json
{
  "queue_id": "non_fallback_active",
  "expected_count": 2006,
  "row_state": "active",
  "migration_class": "non_fallback_active_metadata_swap",
  "description": "old-label rows that do not fall through to legacy_fallback_target; native migration is expected to be a label/metadata swap"
}
```

Required row fields:

- `full_type`
- `persisted_compose_profile`
- `target_profile`
- `swap_method`
- `decision_row_hash`
- `rendered_hash`

Output:

```text
phase4_active_execution_queue/execution_queue_non_fallback_active.2006.jsonl
```

### 7-3. Queue B - Fallback-Dependent Active Migration

```json
{
  "queue_id": "fallback_dependent_active",
  "expected_count": 78,
  "row_state": "active",
  "migration_class": "fallback_dependent_active",
  "description": "rows where resolution_source == legacy_fallback_target"
}
```

Required row fields:

- `full_type`
- `persisted_compose_profile`
- `fallback_subclass`
- `target_profile` when `fallback_subclass == mechanical_ready`
- `schema_gap_reason` when `fallback_subclass == schema_gap`
- `decision_row_hash`
- `rendered_hash`

If any row in Queue B is subclassified as `schema_gap`, this queue is sealed as execution-readiness input only, not as an immediately executable migration queue.

Output:

```text
phase4_active_execution_queue/execution_queue_fallback_dependent_active.78.jsonl
```

### 7-4. Silent Metadata Inventory Record

```json
{
  "record_id": "silent_metadata_inventory",
  "expected_count": 21,
  "row_state": "silent",
  "inventory_class": "silent_metadata_inventory_only",
  "execution_queue_sealed": false,
  "execution_round_intake": "determined_at_execution_round_opening",
  "description": "silent rows stay silent; this readiness round records metadata mapping only and does not seal them as execution input"
}
```

Output:

```text
phase4_silent_inventory/silent_metadata_inventory.21.jsonl
```

### 7-5. Phase 4 summary

```json
{
  "queue_a_count": 2006,
  "queue_b_count": 78,
  "sealed_execution_queue_count": 2084,
  "silent_metadata_inventory_count": 21,
  "inventory_total": 2105,
  "active_total": 2084,
  "silent_total": 21,
  "schema_gap_count": "<Phase 1 measured>",
  "unresolved_count": 0
}
```

Output:

```text
phase4_summary/phase4_summary.json
```

### 7-6. Gate

- `queue_a_count + queue_b_count == active_old_profile_count`
- `queue_a_count + queue_b_count == 2084`
- `sealed_execution_queue_count == 2084`
- `silent_metadata_inventory_count == 21`
- `queue_a_count + queue_b_count + silent_metadata_inventory_count == 2105`
- `inventory_total == 2105`
- Active queue row ids are subsets of canonical decisions active row ids.
- Active queue row id intersection count is `0`.
- Silent inventory row ids are disjoint from active queue row ids.
- If schema-gap rows exist, `schema_gap_count` is exposed in summary and each row has `schema_gap_reason`.

---

## 8. Phase 5 - Observer-Only Invariant Preservation

### 8-1. Purpose

Prove that the readiness round did not mutate sealed runtime/rendered/Lua/canonical authority artifacts.

### 8-2. Required checks

| Field | Required value |
|---|---|
| `staged_lua_hash_unchanged` | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |
| `workspace_lua_hash_unchanged` | same as staged target |
| `runtime_state_unchanged` | `ready_for_in_game_validation` |
| `additive_observer_lane_hashes_unchanged` | 2026-04-24 signal preservation patch round sealed hash set |
| `structural_reclassification_canonical_hashes_unchanged` | 2026-04-24 convergence round sealed hash set |
| `quality_baseline_v4_frozen` | `strong 1316 / adequate 0 / weak 768` |
| `internal_only_bridge_availability_unchanged` | `internal_only 617 / exposed 1467` |

### 8-3. Output

```text
phase5_invariants/observer_invariant_preservation_report.json
```

### 8-4. Gate

- All seven checks pass.
- Any drift blocks Phase 6 pass and must be reported as `overall_status = fail`.

---

## 9. Phase 6 - Readiness Report Sealing

### 9-1. Purpose

Gather all phase outputs into the final read point for this readiness round.

### 9-2. JSON report shape

```json
{
  "round_type": "readiness_only",
  "artifact_mutation_allowed": false,
  "rendered_text_mutation_allowed": false,
  "lua_bridge_mutation_allowed": false,
  "in_game_validation_required": false,
  "legacy_count_reduction_required": false,
  "invariant_checks": {
    "row_count_expected": 2105,
    "active_count_expected": 2084,
    "silent_count_expected": 21,
    "legacy_fallback_target_expected": 78,
    "non_fallback_active_metadata_swap_expected": 2006,
    "fallback_dependent_active_expected": 78,
    "silent_metadata_inventory_expected": 21,
    "staged_lua_hash_unchanged": true,
    "workspace_lua_hash_unchanged": true,
    "runtime_state_unchanged": true,
    "additive_observer_lane_hashes_unchanged": true,
    "structural_reclassification_canonical_hashes_unchanged": true,
    "quality_baseline_v4_frozen": true,
    "internal_only_bridge_availability_unchanged": true
  },
  "measurement_results": {
    "inventory_total": "<Phase 1 measured>",
    "persisted_old_profile_count": "<Phase 1 measured>",
    "active_old_profile_count": "<Phase 1 measured>",
    "silent_old_profile_count": "<Phase 1 measured>",
    "resolver_reached_count": "<Phase 1 measured>",
    "legacy_fallback_target_count": "<Phase 1 measured>",
    "non_fallback_active_metadata_swap_count": "<Phase 1 measured>",
    "fallback_dependent_active_count": "<Phase 1 measured>",
    "fallback_mechanical_ready_count": "<Phase 1 measured>",
    "fallback_schema_gap_count": "<Phase 1 measured>",
    "silent_metadata_inventory_count": "<Phase 1 measured>",
    "sealed_execution_queue_count": "<Phase 4 measured>",
    "unresolved_profile_count": "<Phase 1 measured>"
  },
  "status_seals": {
    "legacy_source_shape_definition_status": "sealed",
    "adapter_removal_checklist_status": "sealed",
    "execution_queue_status": "ready",
    "silent_metadata_inventory_status": "ready",
    "new_registration_guard_status": "defined_and_dry_run_passed",
    "new_registration_guard_evidence": "edpas_guard_verified_present",
    "observer_invariant_preservation_status": "pass"
  },
  "overall_status": "pass"
}
```

### 9-3. Outputs

```text
phase6_readiness_report/adapter_native_body_plan_readiness_report.2105.json
phase6_readiness_report/adapter_native_body_plan_readiness_report.2105.md
```

### 9-4. Pass condition

- Every invariant check matches its required value.
- Internal measurement consistency holds:
  - `inventory_total == row_count_expected`
  - `active_old_profile_count + silent_old_profile_count == inventory_total`
  - `persisted_old_profile_count == row_count_expected`
  - `active_old_profile_count == active_count_expected`
  - `silent_old_profile_count == silent_count_expected`
  - `legacy_fallback_target_count == legacy_fallback_target_expected`
  - `non_fallback_active_metadata_swap_count + fallback_dependent_active_count == active_old_profile_count`
  - `sealed_execution_queue_count == active_old_profile_count`
  - `silent_metadata_inventory_count == silent_old_profile_count`
  - `fallback_mechanical_ready_count + fallback_schema_gap_count == legacy_fallback_target_count`
  - `unresolved_profile_count == 0`
- Status seals use allowed enum values or Phase 0 has explicitly expanded the enum.
- `artifact_mutation_allowed == false` remains true for sealed runtime/rendered/Lua/authority artifacts.

---

## 10. Phase 7 - Adversarial Review Gate

### 10-1. Purpose

Review the readiness round itself after Phase 0-6 artifacts are sealed.

### 10-2. Required format

```text
Good points
Critical issues (FAIL)
Important issues (conditional PASS)
Minor issues (PASS allowed)
PASS / FAIL verdict
```

### 10-3. Review focus

- Did the round accidentally reduce legacy counts?
- Did any sealed runtime/rendered/Lua artifact hash change?
- Did schema-gap rows get hidden inside active execution queues?
- Did status fields use free text instead of enums?
- Did Phase 6 report become the only final read point?
- Did the plan preserve separate openings for execution/schema-extension/cleanup/QA?

### 10-4. Output

No canonical artifact is required. The review record may be stored in:

```text
phase7_review/adapter_native_body_plan_readiness_adversarial_review.md
```

---

## 11. Phase 8 - Canonical Doc Update

### 11-1. Purpose

Reflect closeout only after Phase 6 pass and Phase 7 review pass.

### 11-2. Required updates

`docs/DECISIONS.md`:

```text
2026-XX-XX - Iris DVF 3-3 Adapter Removal Readiness Round closes as readiness closeout
```

Minimum content:

- closeout state `closed_with_persisted_old_profile_and_legacy_fallback_inventory_ready`
- `persisted_old_profile_count = 2105`
- `legacy_fallback_target_count = 78`
- schema-gap count disclosed
- active execution queue sealed
- silent metadata inventory sealed
- adapter removal checklist sealed
- new registration guard verified
- artifact hash status unchanged

`docs/ARCHITECTURE.md`:

```text
removal criterion sealed, execution round pending
```

This wording must be added as a new `11-61. Adapter removal criterion seal` section after current `11-60`, not by rewriting historical `11-53`. The new section should cite `11-53` as the existing adapter boundary and state that removal criteria are now sealed while execution round remains unopened. It must not imply that the adapter has already been removed.

`docs/ROADMAP.md`:

- Move this readiness round to `Done`.
- Add schema extension round as conditional `Next` before full execution when `fallback_schema_gap_count > 0`.
- Add execution round to Iris `Next`, with full execution blocked until schema-gap rows are resolved if any exist.
- Keep manual in-game validation QA as separate pending work.

### 11-3. Gate

- Top docs update happens only after Phase 6 `overall_status = pass` and Phase 7 review verdict pass.
- Top docs must not declare:
  - deployed closeout
  - ready for release
  - runtime QA pass
  - adapter removed
  - legacy count reduced

---

## 12. Dependency Graph

```text
Pre-opening gate
  -> Phase 0 opening decision
      -> Phase 1 inventory
      -> Phase 2 definition
          -> Phase 3 checklist
          -> Phase 4 active execution queues + silent inventory
      -> Phase 5 invariant verification
          -> Phase 6 readiness report
              -> Phase 7 adversarial review
                  -> Phase 8 top-doc update
```

Order rules:

- Phase 1 and Phase 2 may swap order after Phase 0.
- Phase 3 requires Phase 1 and Phase 2.
- Phase 4 requires Phase 1.
- Phase 5 may run in parallel with Phases 1-4 but must finish before Phase 6.
- Phase 6 is the only final read point for pass/fail.
- Phase 8 must not run before Phase 7 review verdict.

---

## 13. Closeout Contract

### 13-1. Closeout state

```text
closed_with_persisted_old_profile_and_legacy_fallback_inventory_ready
```

### 13-2. Closeout declaration

> 이번 round는 legacy count를 줄이지 않는다. 대신 legacy source shape를 정의하고, persisted old profile debt와 compatibility resolver debt를 분리하며, 78개 fallback-dependent row를 mechanical-ready / schema-gap으로 sub-classification하고, 후속 execution round가 소비할 active queue와 silent inventory record 및 adapter 제거 checklist를 봉인하며, observer-only invariant 보존을 기계 검증한다.

### 13-3. Closeout pass JSON

The values below are the expected closeout snapshot after Phase 6 measurements and Phase 7 review pass. Numeric values must be replaced by the actual Phase 6 measured values before closeout is sealed.

```json
{
  "persisted_old_profile_count": 2105,
  "legacy_fallback_target_count": 78,
  "execution_queue_status": "sealed",
  "sealed_execution_queue_count": 2084,
  "silent_metadata_inventory_status": "sealed",
  "silent_metadata_inventory_count": 21,
  "adapter_removal_checklist_status": "sealed",
  "new_registration_guard_status": "defined_and_dry_run_passed",
  "new_registration_guard_evidence": "edpas_guard_verified_present",
  "artifact_hash_status": "unchanged",
  "schema_gap_count_disclosed": true,
  "overall_status": "pass"
}
```

---

## 14. Follow-Up Rounds

This readiness round opens no follow-up automatically. Every downstream round requires a separate opening decision.

| Follow-up round | Precondition | Notes |
|---|---|---|
| Schema Extension Round | this readiness closeout and `fallback_schema_gap_count > 0` | required before full adapter-removal execution when schema-gap rows exist |
| Execution Round | this readiness closeout and (`fallback_schema_gap_count == 0` or schema extension round closeout) | migrate active queue A 2006 + active queue B 78 only; silent 21 intake is determined at execution round opening |
| Resolver Compatibility Mapping Cleanup Round | after execution round | EDPAS-reserved cleanup; full removal or diagnostic-only isolation can execute here |
| Manual In-Game Validation QA | after remaining release blockers close | this readiness round is hash-unchanged and does not replace QA |

Conditional precondition satisfaction does not auto-open a round. Even if `fallback_schema_gap_count > 0`, Schema Extension Round still requires an explicit separate opening decision before it can be started.

---

## 15. Planned Artifact Index

```text
# Phase 0
docs/DECISIONS.md addendum
phase0_opening/opening_decision_reflection.md
phase0_opening/pass_criteria_contract.json

# Phase 1
phase1_inventory/adapter_native_body_plan_readiness_inventory.2105.jsonl
phase1_inventory/adapter_native_body_plan_readiness_inventory.2105.summary.json

# Phase 2
phase2_definition/legacy_source_shape_definition.md
phase2_definition/legacy_profile_taxonomy.json
phase2_definition/resolver_dependency_taxonomy.json

# Phase 3
phase3_checklist/adapter_removal_checklist.md
phase3_checklist/adapter_removal_gate_spec.json
phase3_checklist/legacy_resolver_mode_policy.md

# Phase 4
phase4_active_execution_queue/execution_queue_non_fallback_active.2006.jsonl
phase4_active_execution_queue/execution_queue_fallback_dependent_active.78.jsonl
phase4_silent_inventory/silent_metadata_inventory.21.jsonl
phase4_summary/phase4_summary.json

# Phase 5
phase5_invariants/observer_invariant_preservation_report.json

# Phase 6
phase6_readiness_report/adapter_native_body_plan_readiness_report.2105.json
phase6_readiness_report/adapter_native_body_plan_readiness_report.2105.md

# Phase 7
phase7_review/adapter_native_body_plan_readiness_adversarial_review.md

# Phase 8
docs/DECISIONS.md closeout addendum
docs/ARCHITECTURE.md adapter boundary update
docs/ROADMAP.md done/next update
```
