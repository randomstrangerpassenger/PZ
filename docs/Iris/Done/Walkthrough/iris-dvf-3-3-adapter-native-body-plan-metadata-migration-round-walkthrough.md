# Iris DVF 3-3 Adapter / Native Body Plan Metadata Migration Round Walkthrough

기준일: 2026-04-25
세션 결과: `closed_with_active_metadata_migration_only`

이 문서는 현재 세션에서 수행한 `Adapter / Native Body Plan Metadata Migration Round`의 실제 작업 흐름을 기록한다. 이 round는 active rendered-preview execution queue의 decisions/source metadata만 rewrite했고, Lua/runtime payload, resolver code, adapter cleanup, manual QA status는 건드리지 않았다.

## 1. Opening scope

이번 세션의 round identity는 아래처럼 봉인했다.

```text
Round name: Adapter / Native Body Plan Metadata Migration Round
Purpose: active 2084 decision row의 persisted legacy compose_profile labels를 native body_plan metadata로 이전
Primary target: decisions/source metadata
Not target: IrisLayer3Data.lua / rendered text / runtime Lua payload / resolver code / adapter code
Execution scope: active_rendered_preview_only
Silent 21: deferred
Manual QA status: unchanged
```

Pre-round QA ordering은 migration-first 분기인 Branch B로 진행했다. 이 선택은 rendered 0 delta와 Lua hash unchanged gate를 runtime surface unchanged의 실측 근거로 삼되, manual in-game validation PASS는 선언하지 않는다는 뜻이다.

## 2. v0.3 plan synthesis

사용자 검토 피드백을 받아 계획 문서를 v0.3으로 정리했다.

Plan artifact:

- `docs/Iris/Done/plan/iris-dvf-3-3-adapter-native-body-plan-metadata-migration-round-plan.md`

반영한 핵심 수정은 아래와 같다.

- `legacy_fallback_target_count`와 `default_path_legacy_fallback_reach_count`를 동치로 보지 않고 dual-zero independent gates로 분리했다.
- `default_adapter_dependency_count`는 `default_path_legacy_fallback_reach_count`의 derived alias로 봉인했다. adapter removal을 뜻하지 않는다.
- `canonical_row_legacy_field_residue_count == 0`을 hard gate로 추가했다.
- `legacy_field_namespace_contract.json`을 Phase 2 산출물로 추가하고, Phase 5/7 measurement가 contract 목록 전체를 읽도록 봉인했다.
- dry-run dynamic gate는 isolated simulation environment 방식으로 측정하도록 정했다.
- `phase2_plan_migration_hold_count`와 `phase4_dry_run_migration_hold_count`를 별개 카운트로 분리했다.
- `executed_verified`와 `applied_pending_closeout`의 사용 조건을 명시했다.
- Phase 8 review questions에 namespace contract 검증 질문을 추가했다.

## 3. Executor implementation

이번 세션에서 deterministic executor를 추가했다.

Script:

- `Iris/build/description/v2/tools/build/build_adapter_native_body_plan_metadata_migration.py`

입력 authority:

- Queue A 2006:
  - `Iris/build/description/v2/staging/compose_contract_migration/adapter_native_body_plan_readiness_round/phase4_active_execution_queue/execution_queue_non_fallback_active.2006.jsonl`
- Queue B 78:
  - `Iris/build/description/v2/staging/compose_contract_migration/adapter_native_body_plan_readiness_round/phase4_active_execution_queue/execution_queue_fallback_dependent_active.78.jsonl`
- Canonical source decisions:
  - `Iris/build/description/v2/staging/identity_fallback_source_expansion/phase6_subset_rollout/exec_subset_600_wrench_crowbar_b7_b8_b9/subset_overlay_decisions.jsonl`

Execution rule:

- Queue A는 readiness queue의 `target_native_profile`을 그대로 사용해 `compose_profile`을 native profile로 rewrite했다.
- Queue B는 readiness의 mechanical-ready target을 사용해 `compose_profile`을 rewrite했고, current resolver가 native metadata를 해석할 수 있도록 `selected_role` bridge를 함께 보존했다.
- Silent 21은 write target에서 제외했다.
- Resolver source, adapter code, Lua artifact는 수정하지 않았다.

### selected_role bridge namespace attestation

`selected_role` bridge 보존은 Queue B 78 row가 current resolver의 native metadata path로 해석되도록 유지한 native-side bridge다. 이 field는 legacy residue scan namespace에 포함되지 않는다.

`phase2_migration_plan/legacy_field_namespace_contract.json`의 `legacy_profile_fields_to_scan` 목록은 아래 네 개다.

```text
compose_profile
legacy_compose_profile
fallback_profile
resolver_profile
```

`legacy_dependency_fields` 목록은 아래 한 개다.

```text
legacy_fallback_target
```

따라서 `selected_role`은 `legacy_field_namespace_contract.json` 기준 legacy field가 아니다. Phase 5/7 residue reports는 위 contract 목록 전체를 읽었고 `canonical_row_legacy_field_residue_count = 0`을 산출했다.

Related reports:

- `phase5_dry_run_verification/canonical_row_legacy_field_residue_report.json`
- `phase7_post_apply_verification/canonical_row_legacy_field_residue_report.json`

Walkthrough addendum attestation for the Phase 8 review concern:

```text
selected_role bridge preservation is contract-compatible.
selected_role is not listed in legacy_profile_fields_to_scan or legacy_dependency_fields.
The Queue B rewrite used readiness mechanical-ready target_native_profile values, not old-label compatibility mapping.
```

Carry-forward obligation:

```text
selected_role_precedence: 288
selected_role_target: 894
```

These are not migration failures, but they remain primary observations for the future Resolver Compatibility Mapping Cleanup Round.

## 4. Baseline capture

Phase 3에서 migration 전 baseline을 고정했다.

Artifact:

- `Iris/build/description/v2/staging/compose_contract_migration/adapter_native_body_plan_metadata_migration_round/phase3_baseline/baseline_hashes.json`

Captured values:

```text
sealed staged Lua path:
Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/IrisLayer3Data.body_plan_v2.2105.staged.lua

sealed staged Lua hash:
0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062

workspace Lua path:
Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua

workspace Lua hash:
0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062

resolver source path:
Iris/build/description/v2/tools/build/compose_layer3_text.py

resolver source hash:
3471d14694e0e582db85bd35abb32705e4a1e774f994e0011637159a964da1ae

source decisions hash before apply:
e0d3c61512ecaa065acf35b08ddc94562b6e5bd405110e27ddfa6a137587453e

source decisions coverage:
row_count 2105 / active_count 2084 / silent_count 21
```

Rollback source snapshot:

- `Iris/build/description/v2/staging/compose_contract_migration/adapter_native_body_plan_metadata_migration_round/phase3_baseline/rollback_source_snapshot/subset_overlay_decisions.jsonl`

The `subset_overlay_decisions.jsonl` path covers the full current decision row set for this round: 2105 total rows, including all active 2084 rows and silent 21 rows. The migration write target remained active-only.

The staged Lua file and workspace Lua file are expected to be byte-identical at this closeout point. Their identical `0390272b...` SHA-256 values are the intended parity state, not an accidental single-file measurement.

The resolver invariant path sealed by this round is:

- `Iris/build/description/v2/tools/build/compose_layer3_text.py`

## 5. Dry-run execution

Canonical write 전에 dry-run output tree를 만들었다.

Command:

```powershell
python -B Iris\build\description\v2\tools\build\build_adapter_native_body_plan_metadata_migration.py --dry-run-only
```

Dry-run summary:

```text
canonical_write_performed: false
manifest_count: 2084
queue_a_trace_count: 2006
queue_b_trace_count: 78
migration_hold_count: 0
```

Key artifacts:

- `phase4_dry_run/dry_run_decisions.jsonl`
- `phase4_dry_run/migration_manifest.2084.dry_run.jsonl`
- `phase4_dry_run/queue_a_swap_trace.dry_run.jsonl`
- `phase4_dry_run/queue_b_rewrite_trace.dry_run.jsonl`
- `phase4_dry_run/executor_script_hash.json`
- `phase4_dry_run/migration_manifest_schema.json`

## 6. Dry-run hard gate verification

Phase 5는 dry-run output tree를 isolated simulation environment에 넣어 default compose path를 실행했다. Canonical decisions/source metadata는 이 단계에서 unchanged 상태를 유지했다.

Artifact:

- `phase5_dry_run_verification/dry_run_default_path_simulation_report.json`

Simulation report:

```text
mechanism: isolated_simulation_environment
canonical_decisions_source_metadata_unchanged: true
default_path_legacy_fallback_reach_count: 0
overall_status: pass
```

Phase 5 measurement gates:

```text
active_old_profile_count: 0
active_native_profile_count: 2084
legacy_fallback_target_count: 0
default_path_legacy_fallback_reach_count: 0
default_adapter_dependency_count: 0
canonical_row_legacy_field_residue_count: 0
native_profile_resolve_fail_count: 0
persisted_old_profile_count: 21
rendered_output_delta_count: 0
```

Phase 5 invariant gates confirmed that dry-run did not write Lua-side artifacts and did not modify resolver source.

## 7. Canonical apply

Dry-run hard gate PASS 이후에만 canonical decisions/source metadata를 적용했다.

Command:

```powershell
python -B Iris\build\description\v2\tools\build\build_adapter_native_body_plan_metadata_migration.py
```

Apply summary:

```text
canonical_write_performed: true
manifest_count: 2084
queue_a_trace_count: 2006
queue_b_trace_count: 78
migration_hold_count: 0
```

Dry-run to canonical manifest parity:

```text
overall_status: pass
count_match: true
row_order_match: true
target_match: true
```

Canonical apply artifacts:

- `phase6_canonical_apply/migration_manifest.2084.jsonl`
- `phase6_canonical_apply/queue_a_swap_trace.jsonl`
- `phase6_canonical_apply/queue_b_rewrite_trace.jsonl`
- `phase6_canonical_apply/execution_summary.json`
- `phase6_canonical_apply/dry_run_to_canonical_manifest_parity.json`
- `phase6_canonical_apply/executor_script_hash.json`

Executor script hash parity:

```text
dry-run executor sha256:
88c75055305382e3c12f1fb773177556bf3618c62c101274c22b90e9b7323b96

canonical apply executor sha256:
88c75055305382e3c12f1fb773177556bf3618c62c101274c22b90e9b7323b96

parity:
pass
```

The plan used the name `canonical_apply_summary.json`; the actual generated artifact is `phase6_canonical_apply/execution_summary.json`. This is a naming mismatch only. The actual artifact records the required apply summary fields: `canonical_write_performed`, `manifest_count`, Queue A/B trace counts, and `migration_hold_count`.

## 8. Post-apply verification

Phase 7에서 Phase 5와 같은 gate set을 canonical-applied state 위에서 다시 실행했다.

Artifact:

- `phase7_post_apply_verification/measurement_gates_report.json`
- `phase7_post_apply_verification/invariant_gates_report.json`
- `phase7_post_apply_verification/migration_report.json`

Post-apply measurement:

```text
active_old_profile_count: 0
active_native_profile_count: 2084
legacy_fallback_target_count: 0
default_path_legacy_fallback_reach_count: 0
default_adapter_dependency_count: 0
canonical_row_legacy_field_residue_count: 0
native_profile_resolve_fail_count: 0
persisted_old_profile_count: 21
silent_old_profile_count: 21
rendered_output_delta_count: 0
```

Post-apply resolution source distribution:

```text
identity_family_precedence: 720
identity_family_target: 46
identity_role_aligned: 136
selected_role_precedence: 288
selected_role_target: 894
```

Distribution source:

- `phase7_post_apply_verification/post_apply_rendered_preview.summary.json`

No active default path row reached `legacy_fallback_target`.

Post-apply invariant hashes:

```text
sealed_staged_lua_hash:
0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062

workspace_lua_hash:
0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062

resolver_source_file_hash:
3471d14694e0e582db85bd35abb32705e4a1e774f994e0011637159a964da1ae
```

Migration report:

```text
overall_status: pass
migration_status: executed_verified
closeout_status: pending_review
qa_status: unchanged
phase5_dry_run_status: pass
phase7_post_apply_status: pass
```

## 9. Plan-required output mapping

The generated artifact names are the actual audit surface for this session. The table below maps plan-required verification outputs to concrete files.

### Phase 5 dry-run verification

| Plan-required output | Actual artifact |
|---|---|
| `measurement_gates_report.json` | `phase5_dry_run_verification/measurement_gates_report.json` |
| `invariant_gates_report.json` | `phase5_dry_run_verification/invariant_gates_report.json` |
| `expected_relationship_crosscheck.json` / dual-zero crosscheck | `phase5_dry_run_verification/dual_zero_independent_gate_report.json` |
| `metadata_only_validation_report.json` | `phase5_dry_run_verification/metadata_only_validation_report.json` |
| dry-run dynamic default path simulation | `phase5_dry_run_verification/dry_run_default_path_simulation_report.json` |
| canonical row residue scan | `phase5_dry_run_verification/canonical_row_legacy_field_residue_report.json` |
| default adapter dependency alias report | `phase5_dry_run_verification/default_adapter_dependency_report.json` |

### Phase 7 post-apply verification

| Plan-required output | Actual artifact |
|---|---|
| `measurement_gates_report.json` | `phase7_post_apply_verification/measurement_gates_report.json` |
| `invariant_gates_report.json` | `phase7_post_apply_verification/invariant_gates_report.json` |
| `expected_relationship_crosscheck.json` / dual-zero crosscheck | `phase7_post_apply_verification/dual_zero_independent_gate_report.json` |
| `metadata_only_validation_report.json` | `phase7_post_apply_verification/metadata_only_validation_report.json` |
| canonical row residue scan | `phase7_post_apply_verification/canonical_row_legacy_field_residue_report.json` |
| default adapter dependency alias report | `phase7_post_apply_verification/default_adapter_dependency_report.json` |
| migration report | `phase7_post_apply_verification/migration_report.json` |

## 10. Adversarial review

Phase 8 review를 closeout 전에 실행했다.

Artifacts:

- `phase8_review/adversarial_review.md`
- `phase8_review/critical_findings.json`
- `phase8_review/scope_violation_check.json`
- `phase8_review/silent_21_untouched_attestation.json`
- `phase8_review/qa_status_unchanged_attestation.md`

Review hard results:

```text
critical: 0
major unresolved: 0
scope violation: 0
silent touched: false
runtime rebaseline implied: false
qa status unchanged: true
```

The review explicitly checked the new namespace contract path:

```text
legacy_field_namespace_contract가 current schema의 legacy field를 모두 enumerate했는가?
Phase 5/7 measurement가 contract 목록 전체를 읽었는가, 아니면 일부만 읽고 0으로 닫았는가?
```

The selected-role bridge attestation for the critical closeout review is:

```text
selected_role is not part of legacy_profile_fields_to_scan.
selected_role is not part of legacy_dependency_fields.
selected_role bridge preservation is contract-compatible.
Queue B 78 rewrite consumed readiness mechanical-ready target_native_profile values.
```

## 11. Closeout

Closeout was generated after Phase 5, Phase 7, and Phase 8 all passed.

Command:

```powershell
python -B Iris\build\description\v2\tools\build\build_adapter_native_body_plan_metadata_migration.py --closeout-only
```

Closeout artifact:

- `phase9_closeout/closeout_pass.json`

Closeout values:

```text
overall_status: pass
phase5_dry_run_status: pass
phase7_post_apply_status: pass
phase8_review_status: pass

active_old_profile_count: 0
active_native_profile_count: 2084
legacy_fallback_target_count: 0
default_path_legacy_fallback_reach_count: 0
default_adapter_dependency_count: 0
canonical_row_legacy_field_residue_count: 0
rendered_output_delta_count: 0
silent_old_profile_count: 21

resolver_code_modification: none
adapter_cleanup: not_performed
manual_in_game_validation_status: unchanged
runtime_state: ready_for_in_game_validation
```

## 12. Top-doc updates

이번 세션에서 closeout state를 top-doc에 반영했다.

- `docs/DECISIONS.md`
  - active metadata migration closeout decision added
  - explicit non-decisions: adapter removal, resolver cleanup, runtime rebaseline, manual QA pass, silent 21 cleanup
- `docs/ROADMAP.md`
  - Section 28 addendum added
  - Done/Next/Hold split updated
- `docs/ARCHITECTURE.md`
  - Section 11-62 added
  - active source-shape debt closeout read recorded

## 13. Verification commands

Round execution commands:

```powershell
python -B Iris\build\description\v2\tools\build\build_adapter_native_body_plan_metadata_migration.py --dry-run-only
python -B Iris\build\description\v2\tools\build\build_adapter_native_body_plan_metadata_migration.py
python -B Iris\build\description\v2\tools\build\build_adapter_native_body_plan_metadata_migration.py --closeout-only
```

Regression test command:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Regression test result:

```text
Ran 307 tests in 7.408s
OK
```

Regression test coverage note:

The 307-test suite is a general description v2 regression suite. It is not the authority source for the migration hard gates. The migration-specific gates are measured by the generated Phase 5/7 reports:

```text
rendered_output_delta_count -> measurement_gates_report.json
native_profile_resolve_fail_count -> measurement_gates_report.json
dual-zero independent gate -> dual_zero_independent_gate_report.json
namespace contract residue scan -> canonical_row_legacy_field_residue_report.json
Lua/resolver hash invariants -> invariant_gates_report.json
```

The test result is supporting regression evidence only.

## 14. Final boundary

This round is closed only as active metadata migration.

It did not:

- remove the adapter
- clean resolver compatibility mapping
- update or rebaseline `IrisLayer3Data.lua`
- declare manual in-game validation PASS
- clean silent 21 metadata
- declare `ready_for_release`
- declare deployed closeout

Remaining follow-up rounds still require separate opening decisions:

- Manual In-Game Validation QA Round
- Resolver Compatibility Mapping Cleanup Round
- Silent Metadata Intake / Cleanup Round
- Pattern B diagnostic probe round, only if future evidence requires it
