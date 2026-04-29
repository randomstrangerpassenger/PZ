# Iris DVF 3-3 Adapter / Native Body Plan Metadata Migration Round Plan

> 상태: Draft v0.3-synthesis  
> 기준일: 2026-04-25  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> authority input: `Adapter / Native Body Plan Metadata Migration Round - 최종 통합 로드맵` (2026-04-25 user-provided synthesis)  
> review input: `Verdict 통합 판정` FAIL feedback, `최종 통합 검토안 v0.2` PASS with Important feedback (2026-04-25)  
> 목적: readiness closeout에서 봉인된 active execution queue `2084` row의 persisted legacy `compose_profile` label을 native `body_plan` metadata로 이전하는 execution planning authority를 고정한다.  
> 실행 상태: planning authority only. 이 문서는 migration round를 열기 위한 계획이며, 같은 turn에서 decisions/source metadata, rendered text, Lua bridge, staged runtime artifact, resolver code, adapter code, top docs closeout state를 변경하지 않는다.

---

## 0. Round Identity

### 0-1. 공식명

```text
Adapter / Native Body Plan Metadata Migration Round
```

Trace:

```text
ROADMAP §27 Next의 Adapter / Native Body Plan Execution Round와 동일 라운드
```

### 0-2. 한 문장 scope lock

> 이번 round는 active rendered-preview execution queue `2084` row의 persisted legacy `compose_profile` label을 native `body_plan` metadata로 이전하되, rendered text, Lua runtime payload, resolver code, adapter code는 변경하지 않는 metadata-only execution round다.

### 0-3. Round 성격

| 항목 | 값 |
|---|---|
| round type | `metadata_only_execution` |
| execution scope | `active_rendered_preview_only` |
| input queue | `2084` |
| Queue A | `non_fallback_active_metadata_swap 2006` |
| Queue B | `fallback_dependent_active 78` |
| silent 21 | `deferred` |
| persistence target | `decisions/source metadata only` |
| rendered text mutation | 금지 |
| Lua-side rewrite | 금지 |
| resolver code modification | 금지 |
| adapter cleanup | 금지 |
| QA pass declaration | 금지 |
| expected closeout state | `closed_with_active_metadata_migration_only` |

### 0-4. Staging root

후속 execution round의 신규 산출물 root는 아래로 고정한다.

```text
Iris/build/description/v2/staging/compose_contract_migration/adapter_native_body_plan_metadata_migration_round/
```

권장 하위 디렉터리:

- `phase0_opening/`
- `phase1_reconciliation/`
- `phase2_migration_plan/`
- `phase3_baseline/`
- `phase4_dry_run/`
- `phase5_dry_run_verification/`
- `phase6_canonical_apply/`
- `phase7_post_apply_verification/`
- `phase8_review/`
- `phase9_closeout/`

---

## 1. Pre-Round Branch Seal

이번 round의 Phase 0는 아래 분기를 첫 번째 decision으로 봉인해야 한다.

| Branch | 의미 | 채택 조건 | 실패/보류 처리 |
|---|---|---|---|
| `A_manual_qa_first` | manual in-game validation QA round를 먼저 닫고 PASS state 위에서 migration round를 연다. | risk attribution을 가장 깨끗하게 유지해야 할 때 | QA pass 전 migration opening 보류 |
| `B_migration_first` | Phase 5/7 hard gate의 `rendered 0 delta + sealed staged Lua unchanged + workspace Lua unchanged vs Phase 3 baseline + staged/workspace parity pass`를 runtime surface 미변경의 실측 정당화로 삼는다. | metadata-only migration을 먼저 닫아도 된다고 명시적으로 판단할 때 | gate 실패 시 round fail, Branch A 또는 `runtime rebaseline opening`으로 escalate |

Phase 0 산출물 `qa_order_decision.md`는 반드시 아래 값을 하나만 가져야 한다.

```json
{
  "qa_order_branch": "A_manual_qa_first | B_migration_first",
  "manual_in_game_validation_status_after_round": "unchanged",
  "qa_pass_declaration_allowed": false
}
```

Branch B를 선택해도 manual QA pass를 선언하지 않는다. Closeout 문구는 계속 `Manual in-game validation status: unchanged`로 유지한다.

---

## 2. Governance Baseline

### 2-1. Adopted upstream state

이 round는 아래 current state를 재심하지 않는다.

- Readiness Round는 `closed_with_persisted_old_profile_and_legacy_fallback_inventory_ready`로 닫혔다.
- Active execution queue는 `2084` row로 sealed read한다.
- Queue A는 `non_fallback_active_metadata_swap 2006`이다.
- Queue B는 `fallback_dependent_active 78`이며 `mechanical_ready 78 / schema_gap 0`이다.
- Silent 21 row는 execution queue가 아니라 deferred inventory다.
- Current runtime/staged state는 `ready_for_in_game_validation`이다.
- Current sealed staged Lua hash target은 `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`이고, workspace Lua는 Phase 3 baseline 대비 unchanged 및 staged/workspace parity로 판정한다.
- `quality_baseline_v4`는 `strong 1316 / adequate 0 / weak 768`으로 frozen이다.
- Bridge availability는 `internal_only 617 / exposed 1467`로 frozen이다.

### 2-2. In scope

- Active 2084 decision/source row의 persisted legacy `compose_profile` metadata rewrite.
- Queue A 2006 row의 `target_native_profile` 기반 row-by-row rewrite.
- Queue B 78 row의 readiness-sealed `mechanical_ready target_native_profile` 기반 rewrite.
- Queue B fallback provenance를 canonical row가 아니라 migration manifest로 이동.
- Per-row trace와 single migration manifest 생성.
- Rendered text 0 delta, Lua hash unchanged, resolver source hash unchanged verification.
- Active scope에서 default path legacy fallback reach count를 0으로 만드는지 측정.

### 2-3. Out of scope

- Adapter removal.
- Resolver cleanup.
- Resolver code modification.
- Adapter code modification.
- Runtime Lua payload rewrite.
- `IrisLayer3Data.lua` update.
- Rendered text edit.
- Runtime baseline change.
- Silent 21 intake/cleanup.
- Manual in-game validation pass declaration.
- `quality_baseline_v4 -> v5` cutover.
- `ready_for_release`, deployed closeout 선언.

### 2-4. Hard invariants

```text
persistence target = decisions/source metadata only
rendered text = 0 delta vs sealed baseline
sealed_staged_lua_hash = 0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062
post_execution_staged_lua_hash == sealed_staged_lua_hash
post_execution_workspace_lua_hash == phase3_baseline_workspace_lua_hash
staged_workspace_lua_parity = pass
resolver source file hash = Phase 3 baseline 대비 unchanged
quality_baseline_v4 = strong 1316 / adequate 0 / weak 768 unchanged
bridge availability = internal_only 617 / exposed 1467 unchanged
runtime state = ready_for_in_game_validation unchanged
```

Lua hash measurement target paths:

```text
sealed_staged_lua_path = Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/IrisLayer3Data.body_plan_v2.2105.staged.lua
workspace_lua_path = Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua
```

### 2-5. Measurement definitions

`legacy_fallback_target_count`:

```text
decisions/source metadata 상에 legacy fallback target dependency가 남아 있는 active row 수.
category: static metadata residue count.
scope: active_rendered_preview_only.
post-migration hard gate: 0.
```

`default_path_legacy_fallback_reach_count`:

```text
default compose path 실행 중 실제 fallback branch에 도달한 횟수.
category: dynamic execution path reach count.
scope: active_rendered_preview_only.
post-migration hard gate: 0.
```

`default_adapter_dependency_count`:

```text
Interpretation A selected.
This is a derived closeout alias for default_path_legacy_fallback_reach_count.
It does not mean "all resolver adapter code invocations".
It means default path dependency on the legacy fallback branch.
hard gate: default_adapter_dependency_count == default_path_legacy_fallback_reach_count == 0.
```

`canonical_row_legacy_field_residue_count`:

```text
canonical row schema의 legacy field namespace를 enumerate하고,
post-migration active row에서 non-null occurrence count를 측정한다.
hard gate: 0.
```

### 2-6. Phase 5 dry-run dynamic gate mechanism

Phase 5 dry-run에서 `default_path_legacy_fallback_reach_count`를 측정하는 방식은 Option A로 봉인한다.

```text
dry_run_dynamic_gate_strategy = isolated_simulation_environment
canonical decisions/source metadata = unchanged
dry-run output tree = simulation input
default compose path = simulated against dry-run source tree
Lua/runtime artifact write = prohibited
```

이 방식은 dry-run output tree를 isolated simulation environment에 입력해 default path를 실행하고, canonical state는 그대로 둔다. Phase 5 dual-zero gate의 dynamic half는 이 simulation result로 판정한다. Simulation infra가 준비되지 않았거나 simulation report가 생성되지 않으면 Phase 5는 fail이며 Phase 6 canonical apply는 열 수 없다.

Implementation shape:

```text
isolated_simulation_environment =
  Python build pipeline 내부의 dry-run-only invocation mode
  또는 별도 sandbox script.

required invariants:
  canonical decisions/source metadata unchanged
  Lua/runtime artifact write prohibited
  resolver/adapter source write prohibited
  rendered text write prohibited
```

구체 구현은 Phase 4/5 implementation에서 선택할 수 있지만, 위 invariant를 만족하지 못하면 Option A simulation으로 인정하지 않는다.

옵션 B의 temporary canonical overlay는 금지한다. 옵션 C의 "Phase 5 static-only, Phase 7 dynamic-only"는 이 plan에서 채택하지 않는다.

### 2-7. Dual-zero independent gate interpretation

`legacy_fallback_target_count`와 `default_path_legacy_fallback_reach_count`는 동치가 아니다. 하나는 static metadata residue이고, 하나는 dynamic execution reach다. Phase 5 dry-run과 Phase 7 post-apply는 두 값을 독립적으로 측정하고 둘 다 0이어야 통과한다.

v0.1의 single-relationship 가정, 즉 두 카운트 동치와 동시 0 도달 표현을 dual-zero independent gate로 정밀화한다. 두 카운트는 독립적으로 측정하고 독립적으로 gate를 통과해야 한다.

Failure routing:

| Pattern | Count state | Interpretation | Action |
|---|---|---|---|
| A | `legacy_fallback_target_count > 0`, `default_path_legacy_fallback_reach_count = 0` | canonical source에 stray legacy field 잔존 | source metadata rewrite failure로 보고 migration 재실행 검토. Schema Extension Round 불필요 |
| B | `legacy_fallback_target_count = 0`, `default_path_legacy_fallback_reach_count > 0` | resolver가 다른 경로로 legacy fallback 도달 | diagnostic probe round로 먼저 routing. Probe가 hidden resolver dependency를 확인할 때만 Pattern B emergency Resolver Cleanup Round opening 허용 |
| C | both `> 0` | migration 미완료 또는 readiness target consumption failure | readiness sealed state 균열 의심. Schema Extension Round opening 검토 |

Schema Extension Round는 Pattern C, `phase2_plan_migration_hold_count > 0`, 또는 `phase4_dry_run_migration_hold_count > 0`에서만 강제 opening 후보가 된다. 이 경우 readiness closeout state의 retroactive restatement 함의를 governance trace에 기록해야 한다.

---

## 3. Phase 0 - Opening Decision / Pass Criteria Contract

### Purpose

라운드가 metadata-only migration execution임을 봉인하고 resolver cleanup, QA, Lua rebaseline, silent cleanup이 섞이지 않게 한다.

### Required Outputs

- `phase0_opening/opening_decision_reflection.md`
- `phase0_opening/pass_criteria_contract.json`
- `phase0_opening/qa_order_decision.md`
- `phase0_opening/scope_seal.md`

`pass_criteria_contract.json`은 아래 세 group을 분리한다.

```json
{
  "invariant_checks": {},
  "measurement_results": {},
  "status_seals": {}
}
```

### Exit Gate

```text
round_type = metadata_only_execution
execution_scope = active_rendered_preview_only
input_queue = 2084
queue_a_count = 2006
queue_b_count = 78
silent_21 = deferred
resolver_modification = prohibited
lua_rebaseline = prohibited
qa_order_branch = A_manual_qa_first or B_migration_first
legacy_fallback_target_count = static independent gate
default_path_legacy_fallback_reach_count = dynamic independent gate
default_adapter_dependency_count = derived alias of default_path_legacy_fallback_reach_count
canonical_row_legacy_field_residue_count gate defined
dry_run_gate_required_before_canonical_write = true
dry_run_dynamic_gate_strategy = isolated_simulation_environment
legacy_field_namespace_contract_required = true
```

---

## 4. Phase 1 - Input Reconciliation

### Purpose

Readiness round의 sealed 산출물을 execution 직전에 재검증한다.

### Required Checks

- Queue A `2006` row 전부의 `target_native_profile` 존재성/유효성 검증.
- Queue B `78` row 전부의 `mechanical_ready` 분류와 `target_native_profile` 매칭 검증.
- Silent 21 inventory를 read-only reference로 격리하고 write target에서 제외.
- Active 2084 row 모두의 현재 `compose_profile`이 legacy label인지 preflight 확인.
- Lua-side metadata label absence 확인: `IrisLayer3Data.lua`에 `compose_profile` 또는 legacy label이 직접 persist되지 않아야 한다.

### Required Outputs

- `phase1_reconciliation/active_queue_reconciliation_report.json`
- `phase1_reconciliation/silent_inventory_readonly_reference.json`
- `phase1_reconciliation/lua_metadata_absence_check.json`

### Exit Gate

```text
Queue A 2006 all target_native_profile present
Queue B 78 all mechanical_ready target_native_profile present
silent 21 isolated
Lua-side metadata label absence confirmed
active current compose_profile legacy preflight confirmed
```

### Failure Branches

| Failure | Interpretation | Action |
|---|---|---|
| `target_native_profile missing` | readiness artifact integrity crack | round fail |
| `mechanical_ready mismatch` | late schema_gap discovery and readiness sealed state crack | round fail + Schema Extension Round opening 권고 + readiness closeout restatement trace |
| Lua-side metadata label present | scope model crack | round fail + source/runtime boundary review |

---

## 5. Phase 2 - Migration Plan Lock

### Purpose

무엇을 어떻게 바꿀지 확정한다. 단순 문자열 치환은 금지한다.

### Queue A Rule

Queue A `non_fallback_active_metadata_swap 2006`은 이미 native target이 명확한 row다.

- `target_native_profile` 기반 row-by-row rewrite.
- old label compatibility mapping으로 역추론하지 않는다.
- legacy fallback 관련 필드가 canonical row에 남아 있지 않은지 확인한다.

### Queue B Rule

Queue B `fallback_dependent_active 78`은 readiness가 봉인한 `mechanical_ready target_native_profile`에 근거해 rewrite한다.

- fallback mapping으로 추정하지 않는다.
- readiness 산출물의 explicit target만 사용한다.
- canonical row에는 native metadata를 남긴다.
- fallback provenance는 migration manifest로 이동한다.

### Priority Rule

```text
1. readiness queue의 target_native_profile
2. body_plan section metadata
3. source/body role metadata
4. fallback_dependent_active의 mechanical_ready target
5. 불명확하면 migration hold
```

정상 readiness 기준은 `mechanical_ready 78 / schema_gap 0`이므로 automatic hold는 `0`이어야 한다.

`old label compatibility mapping`은 target 결정 authority가 아니다. 이 mapping은 post-hoc sanity check 또는 compatibility drift comparison에만 사용하며, row rewrite target을 결정하는 근거로 사용하면 manual guess violation이다.

### Legacy Field Namespace Contract

Phase 2는 dry-run 전에 legacy residue scan 대상을 별도 계약 산출물로 봉인해야 한다.

Required output:

```text
phase2_migration_plan/legacy_field_namespace_contract.json
```

Minimum contract shape:

```json
{
  "legacy_field_namespace_contract_version": "v1",
  "legacy_compose_profile_labels": [
    "interaction_tool",
    "interaction_component",
    "interaction_output"
  ],
  "legacy_dependency_fields": [
    "legacy_fallback_target"
  ],
  "legacy_profile_fields_to_scan": [
    "compose_profile",
    "legacy_compose_profile",
    "fallback_profile",
    "resolver_profile"
  ],
  "scan_scope": "active_rendered_preview_only",
  "hard_gate": "canonical_row_legacy_field_residue_count == 0"
}
```

실제 실행 시 field list는 current decisions/source schema를 기준으로 확정한다. 핵심 조건은 scan 대상 목록이 Phase 2에서 먼저 봉인되고, Phase 5/7이 그 계약 목록 전체를 읽어 `canonical_row_legacy_field_residue_count`를 측정해야 한다는 점이다. 실행자가 일부 field만 세고 0으로 닫는 것은 gate violation이다.

### Per-Row Trace Format

```json
{
  "item_id": "Base.X",
  "old_compose_profile": "interaction_tool",
  "new_native_profile": "tool_body",
  "source_queue": "fallback_dependent_active",
  "readiness_target_source": "mechanical_ready"
}
```

### Required Outputs

- `phase2_migration_plan/queue_a_swap_rule.md`
- `phase2_migration_plan/queue_b_rewrite_rule.md`
- `phase2_migration_plan/persistence_target_scope.md`
- `phase2_migration_plan/fallback_78_mechanical_ready_consumption_plan.json`
- `phase2_migration_plan/migration_hold_policy.json`
- `phase2_migration_plan/legacy_field_namespace_contract.json`

### Exit Gate

```text
Queue A 2006 all have target_native_profile
Queue B 78 all have mechanical_ready target_native_profile
schema_gap = 0
automatic migration hold = 0
manual guess = 0
Lua-side path is not included in write targets
legacy_field_namespace_contract sealed
```

### Failure Branch

```text
phase2_plan_migration_hold_count > 0:
  interpretation = readiness sealed state의 retroactive crack signal
  action = round fail + Schema Extension Round opening
  governance_trace = readiness closeout state restatement 함의 기록
```

`phase2_plan_migration_hold_count`는 plan lock 시점에 readiness queue와 target authority를 읽다가 hold가 발생한 row 수다. Phase 4의 `phase4_dry_run_migration_hold_count`와 별개로 측정한다.

---

## 6. Phase 3 - Baseline Capture

### Purpose

Migration 전 상태를 고정해 rollback과 drift attribution을 가능하게 한다.

### Required Hash Capture

- sealed staged Lua hash at `Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/IrisLayer3Data.body_plan_v2.2105.staged.lua`.
- workspace Lua hash at `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`.
- sealed rendered text artifact hash.
- resolver source file hash.
- quality baseline v4 snapshot.
- bridge availability snapshot.
- active queue manifest hash.

### Numeric Baseline

```text
row_count = 2105
active_count = 2084
silent_count = 21
active_old_profile_count = 2084
queue_a_count = 2006
queue_b_count = 78
```

### Required Outputs

- `phase3_baseline/baseline_hashes.json`
- `phase3_baseline/quality_and_bridge_snapshot.json`
- `phase3_baseline/pre_migration_numeric_baseline.json`
- `phase3_baseline/rollback_source_snapshot/`

### Exit Gate

```text
sealed staged Lua hash = 0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062
workspace Lua hash captured
staged_workspace_lua_parity captured
rendered text hash captured
resolver source file hash captured
rollback source snapshot created
```

### Failure Branch

Sealed Lua hash drift가 발견되면 round fail로 닫고 drift origin 분리 quarantine round를 연다.

---

## 7. Phase 4 - Dry-run Metadata Rewrite

### Purpose

Canonical decisions/source metadata에 write하기 전에 dry-run output tree를 만들고, 동일한 hard gate set을 dry-run 상태에서 먼저 통과시킨다.

Dry-run gate PASS 전 canonical decisions/source metadata write는 금지한다.

### Dry-run Rules

```text
single writer
single manifest schema
deterministic script
canonical write prohibited
no resolver code edit
no adapter code edit
no Lua-side artifact edit
no rendered text edit
```

### Required Work

- Queue A `2006` row dry-run swap 생성.
- Queue B `78` row dry-run mechanical_ready rewrite 생성.
- Queue A/B dry-run per-row trace 생성.
- Dry-run `migration_manifest.2084.dry_run.jsonl` 생성.
- Dry-run source tree가 canonical decisions/source metadata write target과 byte-level equivalent replacement 후보인지 기록.
- Executor script hash를 capture한다.

### Migration Manifest Schema

`migration_manifest.2084.*.jsonl`은 아래 schema를 따른다.

```json
{
  "manifest_schema_version": "adapter-native-body-plan-metadata-migration-manifest-v1",
  "item_id": "Base.X",
  "old_compose_profile": "interaction_tool",
  "new_native_profile": "tool_body",
  "source_queue": "fallback_dependent_active",
  "readiness_target_source": "mechanical_ready",
  "fallback_provenance_ref": "phase4_dry_run/queue_b_rewrite_trace.jsonl#...",
  "canonical_write_target": "decisions/source metadata",
  "row_order_key": "Base.X"
}
```

Deterministic reproducibility rules:

```text
row_order = deterministic by item_id, then source_queue
manifest_schema_version required on every row
trace row count must equal queue count
dry-run manifest and canonical manifest must have identical row_order_key sequence
executor script hash must be captured before dry-run and before canonical apply
```

### Required Outputs

- `phase4_dry_run/queue_a_swap_trace.dry_run.jsonl`
- `phase4_dry_run/queue_b_rewrite_trace.dry_run.jsonl`
- `phase4_dry_run/execution_summary.dry_run.json`
- `phase4_dry_run/migration_manifest.2084.dry_run.jsonl`
- `phase4_dry_run/migration_manifest_schema.json`
- `phase4_dry_run/dry_run_output_tree_manifest.json`
- `phase4_dry_run/executor_script_hash.json`

### Exit Gate

```text
dry_run_queue_a_trace_count = 2006
dry_run_queue_b_trace_count = 78
dry_run_manifest_count = 2084
phase4_dry_run_migration_hold_count = 0
canonical_write_performed = false
executor_script_hash captured
```

### Failure Branch

```text
phase4_dry_run_migration_hold_count > 0:
  interpretation = readiness sealed state의 retroactive crack signal
  action = round fail + Schema Extension Round opening
  governance_trace = readiness closeout state restatement 함의 기록
```

`phase4_dry_run_migration_hold_count`는 dry-run execution 중 실제 rewrite target을 산출하지 못한 row 수다. Phase 2의 `phase2_plan_migration_hold_count`와 별개로 측정한다.

---

## 8. Phase 5 - Dry-run Hard Gate Verification

### Purpose

Dry-run source tree에 대해 post-migration hard gate set을 먼저 실행한다. Phase 5가 PASS되지 않으면 Phase 6 canonical apply는 열 수 없다.

Phase 5의 Lua hash gate 의도는 dry-run이 Lua-side write를 하지 않았음을 검증하는 것이다.

### Dry-run Dynamic Measurement Mechanism

Phase 5 dynamic measurement는 Option A를 사용한다.

```text
mechanism = isolated_simulation_environment
input = phase4_dry_run/dry_run_output_tree_manifest.json
canonical decisions/source metadata = unchanged
canonical_write_performed = false
dynamic metric = default_path_legacy_fallback_reach_count
```

Dry-run output tree를 isolated simulation environment의 default compose path 입력으로 넣고 `default_path_legacy_fallback_reach_count`를 측정한다. Simulation은 canonical decisions/source metadata, rendered text, staged Lua, workspace Lua, resolver source, adapter source를 수정할 수 없다.

Simulation report가 없거나 simulation input이 Phase 4 dry-run output tree와 일치하지 않으면 Phase 5는 fail이다.

### Measurement Gates

```text
active_old_profile_count: 2084 -> 0
active_native_profile_count: 2084
legacy_fallback_target_count: 78 -> 0
default_path_legacy_fallback_reach_count: 0
default_adapter_dependency_count: 0
(derived alias of default_path_legacy_fallback_reach_count, not adapter removal)
canonical_row_legacy_field_residue_count: 0
native_profile_resolve_fail_count: 0
persisted_old_profile_count: 21
```

`persisted_old_profile_count = 21`은 silent 21만 남았다는 뜻이다. 이 round에서 `persisted_old_profile_count = 0`을 선언하면 안 된다.

### Dual-zero Independent Gate

```text
legacy_fallback_target_count == 0
default_path_legacy_fallback_reach_count == 0
```

두 카운트는 동치로 가정하지 않는다. 둘 다 독립적으로 측정하고 독립적으로 gate를 통과해야 한다.

### Invariant Gates

```text
rendered text vs sealed baseline: 0 delta
post_dry_run_staged_lua_hash == sealed_staged_lua_hash
post_dry_run_workspace_lua_hash == phase3_baseline_workspace_lua_hash
staged_workspace_lua_parity = pass
canonical_write_performed = false
resolver source file hash: Phase 3 baseline 대비 unchanged
quality_baseline_v4: strong 1316 / adequate 0 / weak 768 unchanged
bridge availability: internal_only 617 / exposed 1467 unchanged
runtime state: ready_for_in_game_validation unchanged
```

### Required Outputs

- `phase5_dry_run_verification/measurement_gates_report.json`
- `phase5_dry_run_verification/invariant_gates_report.json`
- `phase5_dry_run_verification/dual_zero_independent_gate_report.json`
- `phase5_dry_run_verification/default_adapter_dependency_report.json`
- `phase5_dry_run_verification/canonical_row_legacy_field_residue_report.json`
- `phase5_dry_run_verification/dry_run_default_path_simulation_report.json`
- `phase5_dry_run_verification/metadata_only_validation_report.json`

### Failure Branches

| Failure | Interpretation | Action |
|---|---|---|
| Pattern A: static `> 0`, dynamic `= 0` | source metadata rewrite or manifest consumption failure | round fail, migration 재실행 검토 |
| Pattern B: static `= 0`, dynamic `> 0` | resolver hidden dependency or instrumentation failure | round fail, diagnostic probe round first. Pattern B emergency Resolver Cleanup Round는 probe가 hidden resolver dependency를 확인한 뒤에만 허용 |
| Pattern C: both `> 0` | migration 미완료 또는 readiness target insufficiency | round fail, Schema Extension Round opening 검토 + readiness restatement trace |
| `canonical_row_legacy_field_residue_count > 0` | legacy field rename/residue risk | round fail, source rewrite plan 재작성 |
| rendered delta nonzero | metadata-only 성격 재심 필요 | round fail, canonical write 금지 |
| Lua hash changed | unexpected runtime payload drift | round fail, runtime rebaseline opening 필요 |
| resolver hash changed | resolver modification prohibition violated | round fail |

---

## 9. Phase 6 - Canonical Apply

### Purpose

Phase 5 dry-run hard gate PASS 후에만 canonical decisions/source metadata에 적용한다.

### Apply Rules

```text
Phase 5 PASS required
single writer
same manifest schema as dry-run
same executor script hash as dry-run
no resolver code edit
no adapter code edit
no Lua-side artifact edit
no rendered text edit
```

Dry-run과 canonical apply 사이 executor script hash가 바뀌면 round fail로 닫고 Phase 3/4부터 새 round execution을 다시 시작한다. Executor hash 변경은 justification으로 통과시킬 수 있는 예외가 아니라 deterministic script 봉인 위반이다.

### Required Work

- Queue A `2006` row canonical swap 적용.
- Queue B `78` row canonical mechanical_ready rewrite 적용.
- Canonical apply trace 생성.
- Canonical `migration_manifest.2084.jsonl` 생성.
- Dry-run manifest와 canonical manifest의 row order, target, count parity 확인.

### Required Outputs

- `phase6_canonical_apply/queue_a_swap_trace.jsonl`
- `phase6_canonical_apply/queue_b_rewrite_trace.jsonl`
- `phase6_canonical_apply/canonical_apply_summary.json`
- `phase6_canonical_apply/migration_manifest.2084.jsonl`
- `phase6_canonical_apply/executor_script_hash.json`
- `phase6_canonical_apply/dry_run_to_canonical_manifest_parity.json`

### Abort Rule

Canonical apply 도중 Lua-side write, resolver source write, adapter source write, rendered text write가 감지되면 즉시 abort하고 round fail로 닫는다.

---

## 10. Phase 7 - Post-Apply Verification and Migration Report

### Purpose

Canonical apply 이후 Phase 5와 동일한 hard gate set을 재실행하고, migration report를 작성한다.

Phase 7의 Lua hash gate 의도는 canonical apply가 Lua-side에 영향을 주지 않았음을 검증하는 것이다.

### Required Gate Set

Phase 7은 Phase 5의 모든 measurement gate, dual-zero independent gate, invariant gate, failure routing을 canonical source 상태에서 동일하게 재실행한다.

### Required Outputs

- `phase7_post_apply_verification/measurement_gates_report.json`
- `phase7_post_apply_verification/invariant_gates_report.json`
- `phase7_post_apply_verification/dual_zero_independent_gate_report.json`
- `phase7_post_apply_verification/default_adapter_dependency_report.json`
- `phase7_post_apply_verification/canonical_row_legacy_field_residue_report.json`
- `phase7_post_apply_verification/metadata_only_validation_report.json`
- `phase7_post_apply_verification/migration_report.json`

### Required Migration Report Fields

```json
{
  "overall_status": "pass | fail",
  "migration_status": "executed_verified | applied_pending_closeout",
  "closeout_status": "pending_review",
  "phase5_dry_run_status": "pass | fail",
  "phase7_post_apply_status": "pass | fail",
  "phase0_expected_value_crosscheck": "pass | fail",
  "qa_status": "unchanged"
}
```

`migration_status = ready`는 사용하지 않는다. `sealed`는 Phase 9 closeout 이후에만 사용한다.

Status usage:

```text
executed_verified:
  Phase 5 dry-run PASS + Phase 6 canonical apply complete + Phase 7 post-apply PASS.

applied_pending_closeout:
  canonical apply는 완료됐지만 Phase 7 post-apply verification, Phase 8 review,
  또는 Phase 9 closeout 중 하나가 아직 pending인 중간 상태.
```

### Failure Branch

`overall_status = fail`이면 Phase 8 review를 진행하되 round fail closeout으로 분기한다.

---

## 11. Phase 8 - Adversarial Review

### Purpose

겉으로 단순 metadata rewrite처럼 보여도 authority 상태를 오독할 수 있는 지점을 일부러 찌른다.

### Review Questions

```text
1. canonical row 안에 legacy label이 다른 필드명으로 남아 있는가?
2. legacy_fallback_target이 삭제된 게 아니라 이름만 바뀐 건 아닌가?
3. default compose path가 여전히 compatibility mapping을 암묵적으로 밟고 있지 않은가?
4. Queue B 78개가 readiness target이 아니라 문자열 mapping으로 처리된 건 아닌가?
5. legacy_field_namespace_contract가 current schema의 legacy field를 모두 enumerate했는가?
6. Phase 5/7 measurement가 contract 목록 전체를 읽었는가, 아니면 일부만 읽고 0으로 닫았는가?
7. Lua hash unchanged가 실제로 확인됐는가?
8. rendered 0 delta가 전체 active 2084에 대해 확인됐는가?
9. silent 21이 몰래 건드려졌는가?
10. resolver cleanup 성격의 code diff가 섞였는가?
11. QA status를 pass처럼 표현하지 않았는가?
12. ready_for_release나 deployed closeout 표현이 들어갔는가?
```

### Required Outputs

- `phase8_review/adversarial_review.md`
- `phase8_review/critical_findings.json`
- `phase8_review/scope_violation_check.json`
- `phase8_review/silent_21_untouched_attestation.json`
- `phase8_review/qa_status_unchanged_attestation.md`

### Exit Gate

```text
critical = 0
major unresolved = 0
scope violation = 0
silent touched = false
runtime rebaseline implied = false
```

---

## 12. Phase 9 - Closeout and Top-Doc Updates

### Purpose

Phase 5 dry-run verification, Phase 7 post-apply verification, Phase 8 adversarial review PASS를 기준으로 active metadata migration only closeout을 기록한다.

### Required Outputs

- `phase9_closeout/closeout_pass.json`
- `docs/Iris/Done/Walkthrough/iris-dvf-3-3-adapter-native-body-plan-metadata-migration-round-walkthrough.md`
- `docs/DECISIONS.md` addendum
- `docs/ROADMAP.md` §28 addendum
- `docs/ARCHITECTURE.md` 11-62 addendum

### Correct Closeout Wording

```text
Adapter / Native Body Plan Metadata Migration Round closed.

The active rendered-preview execution queue was consumed:
- Queue A non_fallback_active_metadata_swap: 2006
- Queue B fallback_dependent_active: 78

Active persisted old compose_profile labels were rewritten to native body_plan metadata.

Default compose execution no longer reaches legacy fallback targets
for active_rendered_preview_only scope.

Rendered output delta: 0
Sealed staged Lua hash: unchanged
Workspace Lua hash: unchanged vs Phase 3 baseline
Staged/workspace Lua parity: pass
Resolver code modification: none
Adapter cleanup: not performed
Silent metadata inventory 21: deferred
Manual in-game validation status: unchanged
Runtime state remains ready_for_in_game_validation
```

### Prohibited Wording

```text
adapter removed
resolver cleanup complete
runtime Lua rebaselined
IrisLayer3Data.lua updated
persisted_old_profile_count = 0
full old profile cleanup complete
ready_for_release
deployed closeout
manual QA pass
quality_baseline_v4 -> v5 cutover
```

### Final Completion Numbers

```text
active_old_profile_count: 2084 -> 0
active_native_profile_count: 2084
legacy_fallback_target_count: 78 -> 0
default_path_legacy_fallback_reach_count: 0
default_adapter_dependency_count: 0
(derived alias of default_path_legacy_fallback_reach_count, not adapter removal)
canonical_row_legacy_field_residue_count: 0
rendered_output_delta_count: 0
sealed_staged_lua_hash: unchanged
workspace_lua_hash: unchanged vs Phase 3 baseline
staged_workspace_lua_parity: pass
row_count: 2105
active_count: 2084
silent_count: 21
silent_old_profile_count: 21 deferred
```

### DECISIONS.md Addendum Template

```text
2026-04-25 — Adapter / Native Body Plan Metadata Migration Round closes active metadata migration only

상태: 채택 / 완료

결정:
active 2084 decision row의 persisted compose_profile을 native body_plan metadata로 이전했다.
Queue A 2006과 Queue B 78을 execution input으로 소비했다.
static legacy fallback target residue와 dynamic default path fallback reach는 active_rendered_preview_only scope에서 모두 0이 되었다.
이 migration은 decisions/source metadata rewrite이며 Lua-side rewrite가 아니다.

비결정:
adapter removal 아님 / resolver cleanup 아님
runtime rebaseline 아님 / manual in-game validation pass 아님
silent 21 full cleanup 아님
```

### ROADMAP.md §28 Template

```text
Done:
- active native metadata migration execution closed
- Queue A 2006 consumed / Queue B 78 consumed
- rendered output 0 delta / sealed staged Lua unchanged / workspace Lua unchanged vs Phase 3 baseline
- default_adapter_dependency_count 0 for active_rendered_preview_only
  (derived alias of default_path_legacy_fallback_reach_count, not adapter removal)

Next:
- manual in-game validation QA round
- optional resolver cleanup round
- optional silent 21 metadata intake/cleanup round

Hold:
- adapter removal 선언
- persisted_old_profile_count 0 선언
- runtime rebaseline / ready_for_release / deployed closeout
```

### ARCHITECTURE.md 11-62 Template

```text
11-62. Adapter / Native Body Plan Metadata Migration closes active source-shape debt

current read:
- active old profile count: 0
- active native profile count: 2084
- silent old profile count: 21 (deferred)
- default path legacy fallback reach: 0
- adapter dependency in default path: 0
  (derived alias of default_path_legacy_fallback_reach_count, not adapter removal)

boundary:
- compatibility adapter remains compose-internal (non-writer)
- resolver compatibility mapping remains for explicit diagnostic/compat path
- resolver cleanup is separate round
- runtime state remains ready_for_in_game_validation
```

---

## 13. Post-Round Follow-Up Rounds

이번 round closeout은 아래 후속 round를 가능하게 하지만 자동으로 열지 않는다. 각각 별도 opening decision이 필요하다.

| Follow-up | Trigger | Scope |
|---|---|---|
| Resolver Compatibility Mapping Cleanup Round | migration closeout 이후 optional, 또는 Pattern B emergency after diagnostic probe | adapter를 diagnostic-only 격리할지 완전 제거할지 결정 |
| Silent Metadata Intake / Cleanup Round | silent 21 처리 필요 시 | deferred silent row metadata migration/cleanup |
| Manual In-Game Validation QA Round | global pending | 실제 Project Zomboid runtime 표면 확인 |
| Schema Extension Round | Phase 5/7 Pattern C, `phase2_plan_migration_hold_count > 0`, 또는 `phase4_dry_run_migration_hold_count > 0` 발생 시 강제 opening | readiness `schema_gap 0` 균열 수리 및 readiness closeout restatement 검토 |

---

## 14. Full Gate Summary

```text
[Scope]
metadata-only = true
active-only = true
resolver-code-modification = false
lua-side-rewrite = false

[Input]
Queue A = 2006 consumed
Queue B = 78 consumed
silent 21 = deferred

[Migration]
active_old_profile_count = 0
active_native_profile_count = 2084
legacy_fallback_target_count = 0

[Default path]
default_path_legacy_fallback_reach_count = 0
default_adapter_dependency_count = 0
(derived alias of default_path_legacy_fallback_reach_count, not adapter removal)
native_profile_resolve_fail_count = 0
canonical_row_legacy_field_residue_count = 0

[Regression]
rendered_output_delta_count = 0
sealed_staged_lua_hash = unchanged
workspace_lua_hash = unchanged vs Phase 3 baseline
staged_workspace_lua_parity = pass
resolver_source_file_hash = unchanged
runtime_payload_delta_count = 0

[Status]
runtime state = ready_for_in_game_validation
manual QA status = unchanged
adapter cleanup = separate future round
resolver cleanup = separate future round
silent 21 cleanup = separate future round
```

---

## 15. Non-Negotiable Seal Lines

아래 네 항목 중 하나라도 깨지면 이 round는 `Adapter / Native Body Plan Metadata Migration Round`가 아니다.

```text
1. decisions/source metadata만 rewrite
2. active 2084만 처리
3. rendered/Lua unchanged
4. resolver code modification 금지
```
