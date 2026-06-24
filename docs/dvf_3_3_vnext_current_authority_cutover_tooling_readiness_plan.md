# Implementation Plan

> Status: proposed tooling-readiness prerequisite plan / PASS-with-minor-revisions applied / no current cutover
> Roadmap input: `C:/Users/MW/.codex/attachments/b20d12d6-cdf8-40ec-add5-7c247d4a8fdd/pasted-text.txt` / sha256 `736F9E9B1912255908AE9AEA7A904253C5D4E39ADE2038DDAC2B062122689ACE` / non-authority synthesis reference
> Review input: `C:/Users/MW/.codex/attachments/f65aae50-5c84-4068-aa55-b8fd34dec967/pasted-text.txt` / sha256 `BBB68B358B254681784273EF7BA30094E60C2A7C1F8CCFEC1DE6B7E7311A4F6D` / WARN review reference
> Review input: `C:/Users/MW/.codex/attachments/d6c7368a-0d66-4b9d-a717-685f54fc5cb1/pasted-text.txt` / sha256 `12B9295D1065485AFCACF143D47FEF2D8241C079A56896CF5528359D5093BB33` / PASS-with-minor-revisions review reference
> Local feasibility inspection: 2026-06-17 Iris codebase readpoint / consumer materialization and runtime path failure guards applied
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Parent definition roadmap: `docs/dvf_3_3_vnext_current_authority_roadmap.md`
> Fixed downstream implementation plan: `docs/dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_plan.md`
> Cutover contract: `docs/dvf_3_3_vnext_cutover_contract.md`
> Top authority: `docs/Philosophy.md`

## 1. Objective

DVF 3-3 vNext current authority cutover를 실제로 수행하기 전에, 후속 cutover round가 요구하는 reusable command surface, guarded executor, rollback / snapshot evidence, row-level ledger, diff-to-ledger validation, command surface mapping validation을 먼저 구현하고 봉인한다.

이 계획은 successor current authority adoption 계획이 아니다. 목표는 후속 cutover Phase 0이 `command_surface_mapping.json`으로 직접 소비할 수 있는 도구와 계약을 준비하는 것이다.

The downstream implementation plan is treated as fixed. This readiness plan must therefore emit a Phase 0-compatible command mapping and handoff packet that the implementation plan can consume without schema reinterpretation, renamed validation families, or extra prerequisite planning.

완료 claim은 다음 범위로 제한한다.

```text
DVF 3-3 vNext current authority cutover tooling readiness is sealed.
This is not current authority adoption, live runtime replacement,
consumer migration completion, package readiness, or release readiness.
```

---

## 2. Scope

이 계획은 기존 vNext execution / regeneration / correction / current-route guard evidence를 current authority로 승격하지 않고, 그 evidence를 소비할 수 있는 실행 도구 표면을 staging / disposable / mirrored target에서 검증하는 선행 tooling readiness round다.

포함 범위:

* tooling readiness scope lock, shared command contract, mutation boundary 작성
* minimum schema contracts와 hard-fail predicates 작성
* command surface mapping schema와 validator 구현
* fixed downstream implementation plan 호환 command surface mapping export 구현
* fresh overlay support artifact generator 구현
* overlay input lineage와 fixture-as-authority negative guard 구현
* runtime chunk snapshot / candidate validation / atomic replace / stale chunk deletion / exact target verification / restore probe 도구 구현
* runtime chunk tool canonical path-safety / target-kind enforcement 구현
* 2105 consumer audit matrix 기반 actual consumer migration executor 구현
* consumer migration sandbox baseline / materialization / after-target authority handle 작성
* authority-role migration rule table 작성
* row-level before / after migration ledger generator 구현
* change-forbidden occurrence-level no-mutation 보호 구현
* actual diff-to-ledger validator 구현
* current cutover Phase 0 handoff manifest와 tool contract compatibility manifest 작성
* runtime cutover live command template 작성
* consumer migration reconciled input manifest 작성
* dual-zero, protected-surface no-mutation, current-route closure / allowlist cap 보존 확인
* existing current route green과 dedicated cutover-tooling route pass를 분리해 검증
* roadmap independent adversarial review / seal gate 확인
* final tooling readiness report, closeout, handoff packet, ledger update packet draft 작성

Primary execution evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/`

Plan artifact:

* `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_plan.md`

### Explicitly Out Of Scope

* successor current baseline identity final seal
* live current facts / decisions / rendered / runtime successor 전환
* live runtime chunk replacement
* 2105 consumer migration의 main repo / live 실행 완료 선언
* DECISIONS / ARCHITECTURE / ROADMAP에 current authority adopted 선언
* frozen 2105 복구 또는 current source authority 부활
* staging `accepted_overlay.jsonl`, bridge output, chunk output의 current evidence 직접 승격
* monolith export route의 current route 복귀
* audit matrix forbidden rows cleanup mutation
* 숫자 `2105`, `2084`, `21` 또는 vocabulary 문자열의 기계적 치환
* source-to-rendered chain을 우회한 runtime chunk-only copy cutover
* package readiness / release readiness / Workshop readiness / B42 readiness / deployment readiness 선언
* manual in-game validation
* Browser / Wiki / Tooltip behavior change
* semantic quality / public-facing quality acceptance
* quality exposure, publish policy, Layer4, ACQ_DOMINANT, Acquisition Lexical closed readpoint reopen
* current-route tooling allowlist 자동 확장 또는 current core 12 확장

---

## 3. Non-Goals

* cutover authorization을 만들지 않는다.
* successor baseline identity를 봉인하지 않는다.
* live deployable runtime authority를 successor chunk bundle로 교체하지 않는다.
* runtime chunks나 runtime-derived seed를 source authority로 승격하지 않는다.
* rendered-only, bridge-only, chunk-generation-only output을 current authority로 승격하지 않는다.
* old chunks와 successor chunks를 동시에 current authority로 두지 않는다.
* consumer migration dry-run evidence를 actual migration completion으로 읽지 않는다.
* consumer migration executor를 numeric / vocabulary replacement 도구로 만들지 않는다.
* current-route allowlist cap 1을 silent expansion하지 않는다.
* readiness PASS를 package / release / deployment readiness로 표현하지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 기준이다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 2026-06-17 current readpoint를 따른다.
* live deployable runtime authority는 여전히 `IrisLayer3DataChunks.lua + IrisLayer3DataChunks/Chunk###.lua` 단일 chunk bundle이다.
* monolith `IrisLayer3Data.lua`는 current / staging / runtime / package authority가 아니다.
* current source / facts / decisions / rendered의 기존 6-entry 파일은 full runtime authority input이 아니라 fixture / non-authority다.
* frozen `2105 / 2084 / 21`은 predecessor, comparison reference, migration input이며 current source authority 복구 대상이 아니다.
* vNext successor authority는 `source manifest -> facts -> decisions -> compose profile + body_plan -> rendered -> Lua bridge -> chunk manifest + chunk files` 체인으로만 성립한다.
* rejected delta correction round의 `cutover_input_usable=true`는 candidate predicate이며 cutover authorization이 아니다.
* 2105 Baseline Consumption Audit은 `raw 198815 / accepted 27869 / change required 311 / change forbidden 27558 / ambiguous 0` readpoint로 봉인되어 있다.
* consumer migration input은 `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase8/consumer_migration_matrix.jsonl`과 `phase8/consumer_migration_dry_run.json`이다.
* current core closure는 12 modules이고 current-route regeneration tooling allowlist는 `export_dvf_3_3_lua_bridge` 1개, cap 1이다.
* 본 round 도구를 current-route allowlist에 넣는 것은 자동이 아니라 별도 reviewed scope다.
* readiness round의 destructive validation은 mirrored target / disposable copy / staging working copy / sandbox에서만 수행한다.
* actual live runtime path는 mutation하지 않으며 필요한 경우 read-only exact-target probe만 허용한다.
* this round owns the schema and reference instance of `command_surface_mapping.json`; the later current authority cutover Phase 0 consumes it and may not silently reinterpret missing fields.
* downstream implementation Phase 0 expects command mapping rows with `validation_family`, `concrete_command_or_tool`, `expected_artifact`, and `blocking_condition`; this readiness round must emit those fields as mandatory compatibility fields in addition to its stricter readiness fields.
* runtime chunk cutover readiness must not mutate live runtime, but it must produce a guarded live command template that the downstream implementation Phase 4 can run only after its own Phase 0 snapshot, allowlist, and precondition gates pass.
* consumer migration readiness must reconcile every accepted audit row by explicit disposition. Rows with no actual text change are valid only as `no_op`, `historical_preserved`, `diagnostic_preserved`, `generated_no_mutation`, or `false_positive_no_mutation`; they must not be counted as migrated diffs.
* no-cutover consumer migration uses a labeled successor candidate target / parameterized authority handle, not live current authority adoption.
* default successor candidate lineage for overlay and after-target handles is the corrected candidate chain from `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/corrected_source_manifest.json` and `phase6/rendered/dvf_3_3_rendered.vnext_corrected.json`, with Phase 0 required to pin exact paths and fingerprints before any generation.
* local codebase inspection found actual live runtime data under `Iris/media/lua/client/Iris/Data` and package output under `Iris/build/package/Iris/media/lua/client/Iris/Data`; `Iris/Iris/media/...` must be treated as unresolved legacy-looking path unless it is explicitly materialized in Phase 0.
* local codebase inspection found `docs/2105_baseline_consumption_audit_plan.md` absent while the migration matrix contains change-required rows for it; Phase 3 must resolve, reconstruct, or block those rows before any actual migration completion claim.
* roadmap independent adversarial review / seal is a required complete-gate for this plan; without it, closeout cannot be `complete`.
* independent review seal is review evidence only, not authority adoption, not roadmap replacement, and not execution approval by itself.

---

## 5. Repository Areas Affected

### Code

Expected new or changed tooling surfaces:

* `Iris/build/description/v2/tools/build/generate_dvf_3_3_overlay_support_artifact.py`
* `Iris/build/description/v2/tools/build/manage_dvf_3_3_runtime_chunk_cutover.py`
* `Iris/build/description/v2/tools/build/apply_dvf_3_3_consumer_migration.py`
* `Iris/build/description/v2/tools/build/generate_dvf_3_3_row_level_migration_ledger.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_actual_diff_to_ledger.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_command_surface_mapping.py`

Expected new or changed focused tests:

* `Iris/build/description/v2/tests/test_dvf_3_3_cutover_tooling_readiness.py`
* Additional focused test files may be split by tool lane if keeping one test file becomes unclear.
* Phase 0 must record whether tests remain in one focused file or split by tool lane; either choice is acceptable if lane ownership remains explicit in the command mapping.

Protected current authority surfaces that must not be mutated by this readiness round:

* `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
* `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
* `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
* `Iris/build/description/v2/output/dvf_3_3_rendered.json`
* `Iris/build/description/v2/output/style_normalization_changes.jsonl`
* `Iris/build/description/v2/output/compose_requeue_candidates.jsonl`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`
* `Iris/build/package/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/build/package/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`
* `Iris/build/package/Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`
* `Iris/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`
* `Iris/Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`
* `Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua`
* `Iris/Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua`
* `media/lua/shared/Iris/IrisDvfBridgeData.lua`

The `changed_count == 0` verdict must cover the full set above plus any additional package-output equivalent path declared in Phase 0. The canonical observed package path is `Iris/build/package/Iris/media/lua/client/Iris/Data`. If a legacy-looking path such as `Iris/Iris/media/...` cannot be resolved, the closeout must report that as an unresolved path candidate and cannot treat it as canonical package coverage.

### Docs

Direct plan artifact:

* `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_plan.md`

Expected closeout and handoff docs:

* `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_closeout.md`
* `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_handoff_packet.md`
* `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_ledger_packet.md`

Read-only authority / input docs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/EXECUTION_CONTRACT.md`
* `docs/dvf_3_3_vnext_current_authority_roadmap.md`
* `docs/dvf_3_3_vnext_current_authority_plan.md`
* `docs/dvf_3_3_vnext_execution_plan.md`
* `docs/dvf_3_3_vnext_regeneration_parity_plan.md`
* `docs/dvf_3_3_vnext_delta_guard_current_route_integration_plan.md`
* `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_plan.md`
* `docs/dvf_3_3_vnext_cutover_contract.md`
* `docs/dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_plan.md`

### Config

No project configuration change is planned by default.

If exact command validation requires a dedicated test route or fixture path registration, the change must be listed in the command surface mapping and must not expand current core closure or current-route tooling allowlist silently.

### Generated Artifacts

All readiness evidence must be written under:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/`

Expected artifact families:

* `phase0/command_surface_mapping.json`
* `phase0/minimum_schema_contracts.json`
* `phase0/mutation_boundary.json`
* `phase0/protected_surface_set.json`
* `phase0/protected_surface_baseline_hashes.json`
* `phase0/tooling_readiness_scope_lock_report.json`
* `phase0/roadmap_independent_review_seal.md`
* `phase1/dvf_3_3_overlay_support.jsonl`
* `phase1/overlay_input_lineage_report.json`
* `phase1/overlay_support_manifest.json`
* `phase1/overlay_support_seal_report.json`
* `phase2/predecessor_runtime_snapshot_manifest.json`
* `phase2/path_safety_report.json`
* `phase2/candidate_bundle_validation_report.json`
* `phase2/atomic_cutover_mirror_apply_report.json`
* `phase2/exact_live_target_probe_report.json`
* `phase2/restore_probe_report.json`
* `phase3/sandbox_baseline_manifest.json`
* `phase3/consumer_migration_materialization_preflight_report.json`
* `phase3/missing_required_path_disposition_ledger.jsonl`
* `phase3/authority_role_migration_rules.json`
* `phase3/after_target_authority_handle.json`
* `phase3/consumer_migration_actual_report.json`
* `phase3/row_level_migration_ledger.jsonl`
* `phase3/change_forbidden_zero_mutation_report.json`
* `phase3/forbidden_occurrence_no_mutation_report.json`
* `phase4/actual_diff_snapshot.patch`
* `phase4/actual_diff_to_ledger_report.json`
* `phase4/diff_hunk_ledger_bijection_report.json`
* `phase4/protected_surface_no_mutation_verdict.json`
* `phase5/command_surface_mapping_validation_report.json`
* `phase5/exact_command_validation_report.json`
* `phase5/current_route_closure_report.json`
* `phase5/dedicated_cutover_tooling_route_report.json`
* `phase6/final_tooling_readiness_contract_report.json`
* `phase6/tooling_readiness_closeout.md`
* `phase6/handoff_packet_for_current_authority_cutover.md`
* `phase6/current_cutover_phase0_handoff_manifest.json`
* `phase6/command_surface_mapping.for_current_cutover.json`
* `phase6/tool_contract_compatibility_manifest.json`
* `phase6/runtime_cutover_live_command_template.json`
* `phase6/consumer_migration_reconciled_input_manifest.json`
* `phase6/ledger_update_packet.md` with first-line draft-only / not-applied wording
* `phase6/independent_review_seal.md`

---

## 6. Planned Changes

### Change 1 - Scope Lock, Shared Command Contract, and Mutation Boundary

Purpose:

후속 cutover가 소비할 command surface와 본 readiness round의 mutation boundary를 먼저 고정한다.

Files:

* `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_plan.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase0/*`

Implementation Notes:

* Roadmap input, template input, parent contract input의 path / sha256 / authority role을 기록한다.
* dry-run / apply / explicit mutation flag / read-only probe 의미를 도구 공통 계약으로 둔다.
* live runtime path denylist와 staging / disposable target allowlist를 분리한다.
* command surface mapping schema는 최소 필드와 hard-fail predicate를 `phase0/minimum_schema_contracts.json`에 고정한 뒤 생성한다.
* `freshness_inputs` for overlay, after-target, migration, and final command validation must include:
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/final_delta_disposition_guard_contract_report.json`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase11/final_rejected_delta_correction_reparity_report.json`
* protected live surface baseline hash를 phase 시작 시 캡처한다.
* `phase0/protected_surface_set.json`은 compose protected-output set 3종, live data / output / runtime, package output equivalents, stale-bridge forbidden paths, monolith forbidden paths를 모두 포함해야 한다.
* `phase0/roadmap_independent_review_seal.md`가 없으면 plan complete gate를 통과할 수 없다.
* independent review seal is review evidence only, not authority adoption, not roadmap replacement, and not execution approval by itself.

Minimum Schema Contracts:

* `command_surface_mapping.json` mandatory fields:
  * `command_id`
  * `validation_family`
  * `concrete_command_or_tool`
  * `tool_path`
  * `mode`
  * `required_args`
  * `forbidden_args`
  * `input_artifacts`
  * `output_artifacts`
  * `expected_artifact`
  * `expected_exit_code`
  * `blocking_condition`
  * `mutation_boundary`
  * `target_kind`
  * `freshness_inputs`
  * `schema_refs`
  * `claim_boundary`
  * `downstream_phase`
  * `downstream_artifact`
  * `readiness_artifact`
  * `compatibility_status`
* `row_level_migration_ledger.jsonl` mandatory fields:
  * `ledger_row_id`
  * `audit_row_id`
  * `source_matrix_path`
  * `path`
  * `before_anchor`
  * `after_anchor`
  * `before_authority_role`
  * `after_authority_role`
  * `after_authority_source`
  * `after_authority_candidate_status`
  * `migration_disposition`
  * `operation_kind`
  * `rule_id`
  * `evidence_anchor`
  * `diff_hunk_id`
  * `forbidden_row`
* `consumer_migration_materialization_preflight_report.json` mandatory fields:
  * `matrix_path`
  * `matrix_fingerprint`
  * `change_required_row_count`
  * `change_required_path_count`
  * `materialized_path_count`
  * `missing_required_path_count`
  * `missing_required_row_count`
  * `known_missing_paths`
  * `reconstruction_sources`
  * `blocked_rows`
  * `excluded_rows`
  * `verdict`
* `missing_required_path_disposition_ledger.jsonl` mandatory fields:
  * `audit_row_id`
  * `path`
  * `consumer_type`
  * `disposition`
  * `disposition_reason`
  * `source_evidence_path`
  * `source_evidence_fingerprint`
  * `review_required`
  * `eligible_for_actual_apply`
* `actual_diff_to_ledger_report.json` mandatory fields:
  * `diff_source`
  * `changed_paths`
  * `mapped_hunk_count`
  * `unmapped_hunk_count`
  * `orphan_ledger_count`
  * `forbidden_row_diff_count`
  * `protected_surface_diff_count`
  * `diff_hunk_ledger_bijection`
  * `verdict`
* `tool_contract_compatibility_manifest.json` mandatory fields:
  * `fixed_downstream_plan_path`
  * `fixed_downstream_plan_fingerprint`
  * `phase0_command_surface_mapping_path`
  * `downstream_required_validation_families`
  * `mapped_validation_families`
  * `unmapped_validation_families`
  * `readiness_to_downstream_artifact_map`
  * `runtime_cutover_contract`
  * `consumer_migration_contract`
  * `claim_boundary`
  * `verdict`
* `consumer_migration_reconciled_input_manifest.json` mandatory fields:
  * `source_matrix_path`
  * `source_matrix_fingerprint`
  * `accepted_row_count`
  * `change_required_row_count`
  * `change_forbidden_row_count`
  * `actual_apply_eligible_row_count`
  * `non_apply_reconciled_row_count`
  * `historical_preserved_row_count`
  * `diagnostic_preserved_row_count`
  * `no_op_row_count`
  * `blocked_row_count`
  * `missing_apply_eligible_row_count`
  * `row_disposition_ledger_path`
  * `actual_diff_ledger_path`
  * `downstream_phase5_consumption_note`
  * `verdict`
* `runtime_cutover_live_command_template.json` mandatory fields:
  * `tool_path`
  * `live_target_manifest_path`
  * `live_target_chunk_dir`
  * `required_downstream_phase0_inputs`
  * `required_precondition_reports`
  * `required_snapshot_manifest`
  * `required_apply_flags`
  * `forbidden_readiness_execution`
  * `validated_mirror_apply_report`
  * `restore_probe_report`
  * `claim_boundary`
* `final_tooling_readiness_contract_report.json` mandatory fields:
  * `status`
  * `phase_reports`
  * `exact_validation_commands`
  * `command_surface_mapping_report`
  * `current_cutover_phase0_handoff_manifest`
  * `tool_contract_compatibility_manifest`
  * `runtime_cutover_live_command_template`
  * `consumer_migration_reconciled_input_manifest`
  * `consumer_materialization_preflight_report`
  * `missing_required_path_disposition_report`
  * `protected_surface_no_mutation_verdict`
  * `dual_zero_report`
  * `existing_current_route_report`
  * `dedicated_tooling_route_report`
  * `closure_and_allowlist_report`
  * `independent_review_seal`
  * `template_execution_contract_compliance_review`
  * `claim_boundary`
  * `non_claims`
* hard-fail predicates:
  * missing mandatory field
  * unknown target kind
  * missing schema ref
  * stale freshness input
  * unapproved command
  * missing downstream implementation compatibility field
  * command mapping row without `validation_family`
  * command mapping row without `concrete_command_or_tool`
  * command mapping row without `expected_artifact`
  * command mapping row without `blocking_condition`
  * command mapping row whose `downstream_phase` is unknown or mismatched
  * readiness artifact that cannot be mapped to fixed downstream artifact
  * mapping surplus or missing count above 0
  * ledger row without `ledger_row_id`
  * ledger row without `rule_id`
  * ledger row with `forbidden_row=true` and mutation
  * change-required row without materialized file or sealed missing-path disposition
  * missing path disposition that silently drops a row from denominator accounting
  * rule match ambiguity for any mutation
  * hunk matched to multiple ledger rows without explicit split anchors
  * before-anchor or before-hash mismatch at executor input
  * diff hunk without ledger row
  * ledger row without actual diff
  * protected surface diff count above 0

Validation:

* schema lint
* required command presence check
* forbidden command absence check
* mutation allowlist / denylist self-test
* evidence root writability check
* protected surface read-only baseline hash capture
* minimum schema contract validation
* protected surface set coverage check against the expanded protected path set
* roadmap independent review / seal presence check

---

### Change 2 - Overlay Support Artifact Generator and Seal

Purpose:

fresh current overlay support artifact를 deterministic하게 생성하고, source authority가 아니라 compose support artifact임을 검증한다.

Files:

* `Iris/build/description/v2/tools/build/generate_dvf_3_3_overlay_support_artifact.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_cutover_tooling_readiness.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase1/*`

Implementation Notes:

* output role은 `compose_support_not_source_authority`로 강제한다.
* input manifest linkage와 rendered meta linkage를 필수로 검증한다.
* Phase 0은 overlay lineage를 `phase1/overlay_input_lineage_report.json`에 pin한다.
* default lineage input은 다음 corrected successor candidate surface다.
  * source manifest: `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/corrected_source_manifest.json`
  * facts: freshly materialized readiness-copy facts under `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase1/lineage/dvf_3_3_vnext_facts.jsonl`, generated from the pinned corrected source manifest
  * decisions: freshly materialized readiness-copy decisions under `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase1/lineage/dvf_3_3_vnext_decisions.jsonl`, generated from the pinned corrected source manifest
  * rendered candidate: `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase6/rendered/dvf_3_3_rendered.vnext_corrected.json`
  * bridge / chunk candidate: `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase6/bridge/`
* If Phase 0 selects a different successor candidate lineage, it must record exact source manifest path, facts path, decisions path, rendered path, sha256 / fingerprint, authority-status label, and reason in `overlay_input_lineage_report.json`.
* allowed authority-status labels are `successor_candidate_staging_only`, `compose_support_not_source_authority`, `non_authority_fixture`, and `rejected_as_authority`; generator input must not use `non_authority_fixture` as an accepted lineage.
* current 6-entry facts / decisions / rendered fixture files cannot be used as overlay authority lineage.
* `accepted_overlay.jsonl` from older staging rounds cannot be promoted directly; it may only be consumed as rejected predecessor evidence in a negative test.
* stale staging overlay direct promotion은 hard fail한다.
* single-writer guard와 deterministic rerun comparison을 포함한다.
* missing manifest, missing rendered meta, changed input fingerprint는 hard fail이다.

Validation:

* same input deterministic output hash equality
* byte-identical rerun comparison
* role field exact match
* input manifest fingerprint match
* rendered meta fingerprint match
* schema validation
* overlay input lineage authority-status validation
* successor candidate linkage validation
* fixture-as-authority negative test
* stale overlay direct promotion forbidden test
* no-inheritance negative test

---

### Change 3 - Runtime Chunk Cutover Tooling and Restore Probe

Purpose:

runtime chunk bundle을 snapshot, candidate validation, atomic replace, stale chunk deletion, exact target verification, restore probe까지 다룰 수 있는 도구를 구현한다. 본 라운드에서는 successor adoption을 수행하지 않는다.

Files:

* `Iris/build/description/v2/tools/build/manage_dvf_3_3_runtime_chunk_cutover.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_cutover_tooling_readiness.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase2/*`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/runtime_cutover_live_command_template.json`

Implementation Notes:

* predecessor snapshot manifest는 chunk manifest와 chunk file hash를 기록한다.
* candidate validation은 manifest schema, referenced file exactness, chunk count, chunk path containment를 확인한다.
* atomic replace and stale chunk deletion은 explicit apply flag와 approved path 없이는 실행되지 않는다.
* all target paths are compared using canonical resolved real paths.
* the canonical live runtime target is `Iris/media/lua/client/Iris/Data`; the canonical package output peer is `Iris/build/package/Iris/media/lua/client/Iris/Data`.
* `Iris/Iris/media/...` is not the observed canonical package output path in this readpoint; if Phase 0 cannot resolve it, the tool must classify it as unresolved path candidate rather than silently treating it as package coverage.
* symlink, junction, or reparse point in target path, chunk directory, manifest path, backup path, or restore path is a hard fail by default.
* relative path escape, case-insensitive collision, glob overreach, and path traversal are hard fails.
* target kinds are explicit: `live`, `mirrored`, `disposable`, `staging-copy`.
* In this readiness round, `--target-kind live` is executed only for read-only exact-target probe and snapshot hash read.
* The tool contract must nevertheless support a downstream implementation live-apply mode guarded by explicit apply flag, Phase 0 mutation allowlist, predecessor snapshot manifest, runtime switch precondition verdict, and approved canonical live target.
* `phase6/runtime_cutover_live_command_template.json` records the exact downstream Phase 4 command template and required Phase 0 / Phase 4 gate artifacts; the template is not executed by this readiness round.
* live apply attempted without the downstream gate artifacts must hard fail.
* destructive operation is allowed only for `--target-kind mirrored|disposable|staging-copy` plus explicit apply flag and approved canonical path.
* stale chunk deletion은 manifest-declared stale chunks only; directory sweep requires a dry-run diff report before apply.
* deleting chunk directory outside files, monolith files, stale bridge files, or unrelated Lua files is a hard fail.
* `atomic_cutover_mirror_apply_report.json` defines mirror apply evidence as real apply on a mirrored / disposable target: actual atomic replace, actual stale deletion, exact target verification, and actual restore probe.
* restore probe requires predecessor snapshot hash equality, not mere file existence.
* live path는 read-only exact-target probe만 허용한다.
* no monolith / no dual-current guard를 포함한다.

Validation:

* predecessor snapshot manifest hash validation
* candidate manifest and chunk path validation
* no monolith present
* no dual authority after mirror apply
* canonical live and package path readpoint validation
* unresolved legacy-looking path candidate disposition
* canonical path / symlink / junction / reparse point / path escape negative tests
* target-kind enforcement tests
* stale chunk deletion containment test
* exact target verification after mirrored replace
* restore from predecessor snapshot on mirrored / staging target
* predecessor snapshot hash equality after restore
* live mutation without explicit flag hard fail
* live apply template schema validation
* live apply without downstream Phase 0 allowlist hard fail
* live apply without predecessor snapshot manifest hard fail
* live apply without runtime switch precondition PASS hard fail
* apply mode against unapproved path hard fail
* Lua syntax validation for produced candidate / restored target where applicable

---

### Change 4 - Consumer Migration Executor and Row-Level Ledger

Purpose:

2105 consumer audit matrix의 change-required rows를 authority-role migration으로 적용할 수 있는 actual executor를 구현하고, change-forbidden occurrence mutation count 0을 증명한다.

Files:

* `Iris/build/description/v2/tools/build/apply_dvf_3_3_consumer_migration.py`
* `Iris/build/description/v2/tools/build/generate_dvf_3_3_row_level_migration_ledger.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_cutover_tooling_readiness.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase3/*`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/consumer_migration_reconciled_input_manifest.json`

Implementation Notes:

* audit matrix parser는 change-required / change-forbidden split을 강제한다.
* before sandbox creation, `phase3/consumer_migration_materialization_preflight_report.json` must prove every change-required row is either actual-apply eligible or reconciled by an implementation-compatible non-apply disposition.
* implementation-compatible row dispositions are `migrated_to_manifest_authority`, `historical_preserved`, `diagnostic_preserved`, `generated_no_mutation`, `false_positive_no_mutation`, `no_op`, and `blocked`.
* known local risk: `docs/2105_baseline_consumption_audit_plan.md` is absent at this readpoint while change-required rows reference it; current inspection shows those rows are `migration_disposition=no_change`, so the readiness route must reconcile them as `no_op` or `historical_preserved` non-apply rows with review evidence, not count them as actual migrated diffs.
* missing actual-apply-eligible rows are hard fail. Missing non-apply rows may pass only when they are reconciled with one of the implementation-compatible non-apply dispositions and disclosed in `phase6/consumer_migration_reconciled_input_manifest.json`.
* `phase3/missing_required_path_disposition_ledger.jsonl` records every missing path row with disposition `materialized_from_sealed_evidence`, `blocked_missing_source`, `excluded_non_live_historical_reference`, or `no_op_non_apply`; only `materialized_from_sealed_evidence` and existing materialized paths are eligible for actual apply.
* `phase6/consumer_migration_reconciled_input_manifest.json` is the downstream Phase 5 input bridge. It must reconcile executing-consumer `1062`, change-required `311`, and change-forbidden `27558` counts using the fixed implementation plan's disposition vocabulary.
* migration sandbox baseline is pinned in `phase3/sandbox_baseline_manifest.json`.
* sandbox baseline must include source snapshot identity, materialized path set, file hashes, audit matrix fingerprint, current route validation manifest fingerprint, and reproduction command.
* materialized path set must be derived from `consumer_migration_matrix.jsonl`; files outside the matrix path set cannot be changed unless they are explicitly listed as tool / test / doc support surface in `command_surface_mapping.json`.
* dry-run and apply mode must run against the same pinned sandbox baseline; `actual_diff_snapshot.patch` is always a diff from this baseline to the applied sandbox result.
* no-cutover after target is `phase3/after_target_authority_handle.json`, a labeled successor candidate / parameterized authority handle, not live current authority adoption.
* ledger rows must record `after_authority_source` and `after_authority_candidate_status`; accepted values include `successor_candidate_staging_only` and `parameterized_successor_authority_handle`.
* mutation rule은 `phase3/authority_role_migration_rules.json`의 authority-role migration table을 따른다.
* `authority_role_migration_rules.json` mandatory fields are `rule_id`, `input_consumer_type`, `input_current_authority_role`, `target_authority_role`, `target_authority_handle`, `allowed_migration_disposition`, `operation_kind`, `allowed_paths`, `forbidden_paths`, `before_pattern_policy`, `after_pattern_policy`, `required_before_context_hash`, `required_after_anchor_policy`, `numeric_replacement_allowed=false`, `legacy_vocabulary_reintroduction_allowed=false`, and `requires_evidence_anchor=true`.
* ledger rows must reference `rule_id`; executor-internal hidden migration policy is not sufficient evidence.
* executor must fail if a candidate mutation matches zero rules, more than one rule, a rule whose `consumer_type` does not match the row, or a rule whose path allowlist / denylist conflicts with the matrix.
* executor must fail if a proposed hunk overlaps any change-forbidden occurrence anchor, even when the same file also has change-required rows.
* executor must fail if the before-context hash or stable evidence anchor differs from the sandbox baseline.
* numeric-only replacement, legacy `active / silent` current vocabulary reintroduction, historical / diagnostic row promotion은 hard fail한다.
* apply mode는 staging / disposable / materialized copy에서만 검증한다.
* every changed file must have row-level before / after ledger rows.
* every ledger row must include authority source, migration disposition, implementation-compatible disposition, evidence anchor.
* `change-forbidden occurrence mutation count 0` uses denominator `27558` forbidden occurrences.
* forbidden occurrence no-mutation must be proved by line / anchor, including same-file required / forbidden coexistence cases.

Validation:

* change-required rows only mutation
* change-forbidden occurrence mutation count 0 / denominator 27558
* materialization preflight validation before sandbox apply
* missing path disposition ledger validation
* `docs/2105_baseline_consumption_audit_plan.md` known-missing path disposition validation
* consumer migration reconciled input manifest validation
* implementation-compatible disposition vocabulary validation
* missing actual-apply-eligible row count 0
* sandbox baseline reproducibility validation
* materialized path set validation
* dry-run and apply against the same pinned sandbox baseline
* after target authority handle validation
* authority-role migration rule table schema validation
* every ledger row references a valid `rule_id`
* every changed file has ledger rows
* every ledger row has before / after authority source
* every ledger row has candidate-status after authority source, migration disposition, implementation-compatible disposition, and evidence anchor
* same-file required / forbidden occurrence coexistence test
* forbidden occurrence line / anchor unchanged proof
* zero ambiguous rule matches
* before-context hash mismatch hard-fail test
* no hardcoded numeric-only replacement
* no legacy active / silent current vocabulary reintroduction
* dry-run and apply outputs structurally comparable
* apply mode requires explicit mutation flag

---

### Change 5 - Actual Diff-to-Ledger Validator

Purpose:

actual migration diff와 row-level migration ledger가 완전히 연결되는지 검증한다.

Files:

* `Iris/build/description/v2/tools/build/validate_dvf_3_3_actual_diff_to_ledger.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_cutover_tooling_readiness.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase4/*`

Implementation Notes:

* diff hunk parser는 changed path, hunk context, before / after snippets를 ledger anchor와 매칭한다.
* `diff_hunk_id <-> ledger_row_id` must be bijective for every actual mutation hunk.
* a hunk may not map to multiple ledger rows unless the ledger carries explicit split anchors and the validator emits a deterministic split mapping; otherwise it is ambiguous and hard fails.
* every ledger mutation row must have an actual diff hunk unless its migration disposition is explicitly non-apply / blocked and excluded from actual apply counts.
* every changed path must be present in the audit matrix materialized path set or in the command-surface support allowlist; support-surface changes may not be counted as consumer migration rows.
* before hash, before anchor, and baseline source identity must match the sandbox baseline used by the executor; line-number-only matching is insufficient.
* forbidden row diff means forbidden occurrence-level mutation, not just forbidden path mutation.
* protected surface mutation is evaluated against the expanded Phase 0 protected surface set.
* unmapped diff, orphan ledger row, forbidden occurrence diff, protected surface mutation은 hard fail이다.
* formatting-only drift가 나오면 ledger 없는 diff로 취급하며 closeout 전에 별도 adjudication을 요구한다.

Validation:

* every diff hunk maps to ledger row
* every ledger mutation has actual diff
* every changed path appears in audit matrix or allowed tool / test / doc surface
* `diff_hunk_id <-> ledger_row_id` bijection validation
* ambiguous hunk-to-ledger match count 0
* before hash / anchor mismatch count 0
* support-surface diff not counted as consumer migration
* zero forbidden occurrence diff
* zero protected current authority mutation
* no untracked runtime chunk mutation
* no monolith creation
* no stale bridge reintroduction
* unmapped diff count 0
* orphan ledger row count 0

---

### Change 6 - Command Surface Mapping Validator

Purpose:

모든 도구 command surface가 후속 cutover 계획 Phase 0의 `command_surface_mapping.json`에 직접 매핑 가능한지 검증한다.

This readiness round owns the schema and reference mapping instance. The later current authority cutover Phase 0 consumes this mapping and must not treat missing required fields as implementation discretion.

Files:

* `Iris/build/description/v2/tools/build/validate_dvf_3_3_command_surface_mapping.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_cutover_tooling_readiness.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase5/*`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/command_surface_mapping.for_current_cutover.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/tool_contract_compatibility_manifest.json`

Implementation Notes:

* mapping validator는 command name, args, mode, artifact, schema, fingerprint, exit code contract를 검증한다.
* mapping validator must emit both the readiness reference mapping at `phase0/command_surface_mapping.json` and the downstream implementation-compatible mapping at `phase6/command_surface_mapping.for_current_cutover.json`.
* `command_surface_mapping.for_current_cutover.json` must preserve all readiness safety fields and also include the fixed implementation Phase 0 fields: `validation_family`, `concrete_command_or_tool`, `expected_artifact`, and `blocking_condition`.
* `tool_contract_compatibility_manifest.json` must prove that downstream Phase 0 required validation families are all mapped to executable commands or explicit blocking conditions.
* downstream artifact names must be mapped explicitly. For example, readiness `phase3/row_level_migration_ledger.jsonl` maps to downstream Phase 5 consumer migration ledger input, and readiness `phase6/runtime_cutover_live_command_template.json` maps to downstream Phase 4 live runtime cutover command/tool.
* artifact presence만으로 pass하지 않고 schema / fingerprint freshness까지 확인한다.
* unapproved command, mapping missing, mapping surplus, stale evidence는 hard fail이다.
* dedicated tooling route는 current core module closure와 분리한다.
* validation wording separates `existing_current_route_remains_green` from `dedicated_cutover_tooling_route_passes`.
* new tools are not current-route allowlisted unless a separate reviewed scope approves that disposition.

Validation:

* all commands in mapping exist
* all commands return expected exit codes
* all commands produce declared artifacts
* all artifacts pass schema validation
* downstream implementation compatibility fields present
* downstream required validation family coverage complete
* readiness-to-downstream artifact map complete
* runtime cutover live command template present
* consumer migration reconciled input manifest present
* all fingerprints match expected inputs
* missing required artifact hard fails
* stale evidence hard fails
* unapproved command hard fails
* mapping missing count 0
* mapping surplus count 0
* current core module closure unchanged
* existing current route remains green
* dedicated tooling route pass

---

### Change 7 - Tooling Allowlist Disposition and Final Readiness Seal

Purpose:

도구들의 current-route 편입 여부를 별도 reviewed-scope 항목으로 분리하고, readiness round를 no-cutover claim boundary로 봉인한다.

Files:

* `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_closeout.md`
* `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_handoff_packet.md`
* `docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_ledger_packet.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase6/*`

Implementation Notes:

* allowlist disposition default is no automatic current-route allowlist expansion.
* current-route allowlist cap 1 and 12-module closure remain unchanged unless a separate reviewed scope approves otherwise.
* final report aggregates Phase 0-5 evidence, dual-zero, no-mutation verdict, exact command validation.
* final report separates `existing_current_route_remains_green`, `dedicated_cutover_tooling_route_passes`, and `new_tool_allowlist_disposition`.
* final report must include `fixed_downstream_plan_compatibility=PASS` before closeout can be `complete`.
* `phase6/current_cutover_phase0_handoff_manifest.json` must list the exact readiness artifacts to consume in the fixed implementation plan Phase 0.
* `phase6/command_surface_mapping.for_current_cutover.json` must be the recommended source for downstream `phase0/command_surface_mapping.json`.
* `phase6/tool_contract_compatibility_manifest.json` must state that fresh overlay generation, live runtime cutover, runtime restore probe, actual consumer migration executor, row-level ledger, actual diff-to-ledger validator, and command mapping validator are mapped to concrete commands.
* `phase6/runtime_cutover_live_command_template.json` must be present but marked not executed in readiness.
* `phase6/consumer_migration_reconciled_input_manifest.json` must be present and must report `blocked_row_count=0` and `missing_apply_eligible_row_count=0` for downstream compatibility.
* `ledger_update_packet.md` first line must state draft-only / not applied to DECISIONS, ARCHITECTURE, or ROADMAP.
* roadmap independent adversarial review / seal must be attached before `complete` closeout.
* independent review seal is review evidence only; it is not authority adoption, roadmap replacement, or execution approval by itself.
* closeout text must avoid current adoption, live runtime replacement, consumer migration completion, package readiness, and release readiness wording.

Validation:

* final report aggregates prior phase PASS
* exact command validation exit code 0
* dual-zero 재확인
* protected-surface no-mutation verdict `changed_count == 0`
* existing current route remains green
* dedicated cutover-tooling route passes
* 12-module closure unchanged
* allowlist cap 1 unchanged
* independent review / seal exists
* command surface mapping complete
* current cutover Phase 0 handoff manifest exists
* downstream command surface mapping exists
* tool contract compatibility manifest PASS
* fixed downstream plan compatibility PASS
* runtime cutover live command template exists and is not executed in readiness
* consumer migration reconciled input manifest has blocked row count 0
* consumer migration reconciled input manifest has missing apply-eligible row count 0
* handoff packet paths exist
* no current adoption wording
* no live runtime replacement wording
* no release readiness wording

---

## 7. Validation Plan

### Automated Validation

Execution-specific validation commands must be mapped in `phase0/command_surface_mapping.json` before any PASS closeout is written. Missing required tools block execution rather than being treated as pass.

Required automated validation families:

* Python unit tests for every new tool
* contract tests for dry-run / apply / explicit mutation flag behavior
* command-line exact invocation tests
* minimum schema mandatory field validation
* fixed downstream implementation plan compatibility validation
* downstream command surface mapping schema validation
* downstream required validation family coverage validation
* readiness-to-downstream artifact mapping validation
* corrected phase8 / phase11 freshness input validation
* overlay support determinism and fingerprint tests
* overlay input lineage authority-status tests
* runtime chunk snapshot / candidate validation / restore probe tests
* runtime chunk canonical path-safety and target-kind negative tests
* runtime cutover live command template validation
* runtime canonical live / package path readpoint tests
* unresolved legacy-looking runtime path disposition tests
* stale chunk deletion containment tests
* consumer migration materialization preflight tests
* known missing required path disposition tests for `docs/2105_baseline_consumption_audit_plan.md`
* consumer migration reconciled input manifest validation
* implementation-compatible row disposition vocabulary validation
* sandbox baseline reproducibility tests
* consumer migration dry-run / apply structural comparison tests
* authority-role migration rules validation
* authority-role rule ambiguity hard-fail tests
* before-context hash / anchor mismatch hard-fail tests
* after target authority handle validation
* occurrence-level forbidden no-mutation validation
* row-level ledger schema and completeness tests
* actual diff-to-ledger traceability tests
* diff hunk id to ledger row id bijection tests
* ambiguous hunk-to-ledger mapping hard-fail tests
* command surface mapping validation
* tool contract compatibility manifest validation
* protected-surface no-mutation hash comparison
* dual-zero validation with declared denominator for tooling evidence root
* existing current-route closure and allowlist cap validation
* dedicated cutover-tooling route validation
* Lua syntax validation for generated / candidate / restored chunk payloads where applicable

Expected exact validation routes:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_command_surface_mapping.py --mapping Iris\build\description\v2\staging\dvf_3_3_vnext_cutover_tooling_readiness\phase0\command_surface_mapping.json --evidence-root Iris\build\description\v2\staging\dvf_3_3_vnext_cutover_tooling_readiness
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

The exact command list may be refined in Phase 0, but the final closeout must report the exact commands that exited with code 0.

Current-route claims are split:

* `existing_current_route_remains_green`: proven only by `python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure` or a successor command with the same closure-enforcing semantics.
* `dedicated_cutover_tooling_route_passes`: proven by the mapped tooling validation commands under the readiness evidence root.
* `current_route_tooling_allowlist_unchanged`: proven by closure report showing 12 current core modules and allowlist cap 1.

Dual-zero denominator must be stated in the final report. It must cover the existing current-route guard denominator and the new readiness evidence root, including static forbidden current-surface hits, static unclassified residue, and dynamic forbidden reach.

### Manual Validation

Manual validation is limited to artifact review and claim-boundary inspection:

* phase reports exist at declared paths
* closeout wording does not imply current cutover or release readiness
* handoff packet lists only tooling readiness outputs
* live path operations are read-only probes only
* roadmap independent adversarial review / seal exists and is linked from final readiness report

No manual in-game validation is planned.

### Validation Limits

This plan will not validate:

* actual live successor current cutover
* live runtime mutation validation
* deployed runtime equivalence
* release readiness
* package release readiness
* Workshop readiness
* B42 readiness
* deployment readiness
* production deployment recovery
* real user environment rollback
* manual in-game validation
* long-session runtime validation
* multiplayer validation
* external ecosystem compatibility sweep
* public-facing behavior / semantic quality validation
* frozen 2105 byte-level recovery proof
* independent external verification of `PLAN_TEMPLATE.md` / `EXECUTION_CONTRACT.md` compliance, unless the independent review packet explicitly includes those files and records that check

---

## 8. Risk Surface Touch

### Authority Surface

Current source / runtime authority is not changed.

Additive tooling / evidence surface is added:

* shared command contract
* `command_surface_mapping.json` schema
* overlay support artifact role seal
* runtime cutover tool contract
* consumer migration executor contract
* row-level migration ledger schema
* actual diff-to-ledger validator contract
* final tooling readiness report

Official risk-surface wording for this plan:

```text
Current authority surface: no mutation.
Additive prerequisite tooling and evidence surface: yes.
```

### Runtime Behavior Surface

None.

Live runtime behavior, runtime Lua, packaged Lua, bridge payload, and runtime chunk payload are not changed by this readiness round. Runtime cutover destructive behavior is validated only against staging / mirrored / disposable target copies.

### Compatibility Surface

No user-facing compatibility behavior change.

Internal command contracts and generated evidence schemas are added for the later cutover round. These are not external mod APIs and must not be described as public compatibility guarantees.

### Sealed Artifact Surface

Sealed decision body and sealed predecessor evidence are not mutated.

New staging evidence is additive. Any ledger packet produced by this plan is a draft / handoff packet until a separate approved docs-canon update applies it.

### Public-Facing Output Surface

None.

Browser / Wiki / Tooltip behavior, user-visible item text, quality badges, recommendations, sorting, filtering, release claims, and public messaging remain unchanged.

---

## 9. Risk Analysis

### Architecture Risk

* Tooling may be misread as current authority adoption rather than prerequisite readiness.
* Command mapping may drift from actual CLI behavior.
* Adding tool contracts may accidentally expand current-route tooling allowlist or current core closure.
* Overlay support artifact may be interpreted as source / second authority if role metadata and linkage checks are weak.

### Runtime Risk

* Runtime cutover tooling could mutate live current runtime path if denylist / apply flag guards are weak.
* Stale chunk deletion could delete unrelated files if path containment is insufficient.
* Restore probe could be shallow and fail to prove real restore capability.
* Atomic replace mirror apply could leave dual-current state in staging if exact target verification is incomplete.

### Compatibility Risk

* Internal command contracts could be mistaken for public API surface.
* Consumer migration executor could alter historical / diagnostic references if audit matrix split enforcement is incomplete.
* Consumer migration executor could silently skip missing change-required paths and overclaim completion.
* Readiness command mapping could omit the fixed downstream implementation fields and block downstream Phase 0.
* Runtime cutover tool could pass mirror validation but fail to provide a downstream live command template.
* Consumer migration readiness could produce ledger evidence that does not match downstream Phase 5 disposition vocabulary.
* Package route and current route could drift if forbidden scan criteria are not shared.

### Regression Risk

* Consumer migration executor may degrade into hardcoded numeric / vocabulary replacement.
* Consumer migration rule matching may become ambiguous across consumer types, paths, or same-file required / forbidden occurrences.
* Row-level ledger may fail to explain all actual diffs.
* Missing baseline files may be auto-created without sealed source evidence.
* Formatter or newline churn may produce unmapped diffs.
* Protected current authority files may change without a matching approved cutover scope.
* Closeout wording may overclaim cutover, migration completion, or release readiness.

---

## 10. Rollback Plan

Rollback is limited to readiness round artifacts and tooling changes.

If validation fails:

* Revert or discard new tools, focused tests, docs, and staging evidence added by this readiness plan.
* Do not modify live facts / decisions / rendered / runtime chunk payloads as rollback.
* Do not mutate sealed decision bodies or sealed evidence.
* Treat generated staging evidence root as disposable containment.
* Preserve any failure reports needed to explain why readiness was not sealed.

Runtime cutover tool rollback capability is validated separately inside staging / mirrored target:

* predecessor snapshot manifest must exist before apply mode
* replace without snapshot must hard fail
* `atomic_cutover_mirror_apply_report.json` must come from real mirror apply on a mirrored / disposable target, not abstract dry-run modeling
* mirror apply must perform actual atomic replace, manifest-declared stale deletion, exact target verification, and actual restore probe
* restore probe must restore mirrored / staging target to predecessor manifest hashes
* stale chunk deletion must not touch files outside the allowed chunk directory
* failed exact target verification must leave restore evidence or block closeout

Because this round does not perform live successor adoption, rollback claim is limited to tool capability:

```text
The tooling can snapshot and restore a mirrored / staging target.
This is not proof that a live production successor cutover was performed or recovered.
```

---

## 11. Governance Constraints

* `Philosophy.md` remains the top authority.
* Hub & Spoke / SPI preservation remains unchanged.
* Runtime / build-time separation is preserved.
* Runtime Lua must not compose, repair, validate source, judge semantic quality, or judge publish policy.
* Source-to-runtime chain order must remain `source manifest -> facts -> decisions -> compose profile + body_plan -> rendered -> Lua bridge -> chunk manifest + chunk files`.
* `body_plan` remains compose profile implementation surface / alias label, not second authority.
* Live deployable authority remains chunk manifest + chunk files single bundle until a separate approved cutover.
* Monolith `IrisLayer3Data.lua` must not re-enter as current / staging / runtime / package authority.
* Old chunks and successor chunks must not both be current.
* Runtime-derived seed must not become source authority.
* Staging artifacts must not become current surface without validation and separate approved cutover scope.
* Legacy `active / silent` remains historical / diagnostic / import alias only.
* Current runtime vocabulary `adopted / unadopted` must not become quality-pass, publish_state, deletion, or suppression vocabulary.
* Consumer migration must be authority-role migration, not hardcoded numeric replacement.
* Consumer migration actual apply is forbidden until materialization preflight accounts for every change-required row.
* Missing actual-apply-eligible paths must be reconstructed from sealed evidence or block execution; silent row dropping is forbidden.
* Missing non-apply rows may be reconciled only with implementation-compatible dispositions and must not be counted as migrated diffs.
* `docs/2105_baseline_consumption_audit_plan.md` is a known missing required path at the local feasibility readpoint and must receive explicit Phase 3 disposition.
* Authority-role migration rules must match each mutation exactly once; zero-match and multi-match are hard failures.
* Before-context hash / stable evidence anchor mismatch is a hard failure.
* Change-forbidden rows mutation count must be 0.
* Dry-run evidence alone must not be claimed as actual migration completion.
* Rollback / snapshot evidence is required before live-like mutation command can be sealed.
* Atomic mirror apply must mean real apply on mirrored / disposable target, not abstract dry-run modeling.
* Runtime cutover paths must be canonical-resolved and must reject symlink / junction / reparse point targets unless a later reviewed scope explicitly changes that policy.
* Protected surface no-mutation boundary must remain intact.
* Protected surface set must cover compose protected-output set 3종, live data / output / runtime, package output equivalents, stale-bridge forbidden paths, and monolith forbidden paths.
* Current core closure must not expand beyond 12 modules through this plan.
* Current-route tooling allowlist cap 1 must not expand silently.
* New tools are not added to current-route allowlist without separate reviewed scope.
* Command surface mapping schema and reference mapping are owned by this readiness round; the later cutover round consumes them.
* Command surface mapping must be a superset of the fixed downstream implementation Phase 0 schema.
* Readiness complete requires `fixed_downstream_plan_compatibility=PASS`.
* Runtime live command template is a downstream handoff artifact only; this readiness round must not execute live runtime replacement.
* Consumer migration reconciled input manifest is a downstream handoff artifact and must use the fixed implementation plan's row disposition vocabulary.
* Consumer migration after-target authority is a labeled successor candidate / parameterized authority handle until a separate approved cutover adopts it.
* Change-forbidden no-mutation is occurrence-level, not path-level.
* Sealed decision body / sealed evidence mutation is forbidden; additive packet only.
* Dual-zero gate model remains in force.
* Unapproved delta ingress, fixture-as-authority, monolith fallback, staging direct promotion are fail-loud targets.

---

## 12. Expected Closeout State

Expected closeout target: `complete`, only if all planned tooling surfaces and required validation artifacts exist and the exact mapped validation commands exit with code 0.

Complete closeout means:

* tooling readiness roadmap and implementation plan are sealed
* shared tool contract and command contract are sealed
* minimum schema contracts are sealed and validated
* corrected phase8 / phase11 freshness inputs are present and current in command mapping validation
* overlay support generator exists and passes determinism / role / linkage validation
* overlay support lineage is pinned to a labeled successor candidate and rejects fixture-as-authority
* runtime chunk cutover / restore probe tool exists and passes staging / mirrored target validation
* runtime chunk tool path-safety and target-kind enforcement pass negative tests
* canonical live runtime path and canonical package output path are validated or unresolved path candidates are disclosed
* `atomic_cutover_mirror_apply_report.json` proves real mirror apply, stale deletion, exact verification, and restore
* consumer migration materialization preflight accounts for every change-required row before apply
* missing required path disposition ledger is complete, including the known `docs/2105_baseline_consumption_audit_plan.md` risk if still absent
* no missing / excluded / blocked change-required row is counted as actually migrated
* any remaining `blocked_missing_source` row makes closeout `partial`; any `excluded_non_live_historical_reference` row requires independent review evidence and must be disclosed as a migration coverage limit
* consumer migration sandbox baseline is pinned and reproducible
* after-target authority handle is labeled successor candidate / parameterized authority handle, not live current adoption
* `authority_role_migration_rules.json` is sealed and every ledger row references a valid `rule_id`
* every applied mutation matches exactly one authority-role migration rule
* consumer migration executor exists and can apply change-required rows in staging / disposable target
* change-forbidden occurrence mutation count is 0 with denominator 27558
* row-level migration ledger is generated and complete
* actual diff-to-ledger validator maps every actual diff hunk with hunk-id / ledger-row bijection
* actual diff-to-ledger validator reports ambiguous hunk mapping count 0 and before-anchor mismatch count 0
* command surface mapping validator passes
* `phase6/current_cutover_phase0_handoff_manifest.json` exists and maps readiness artifacts to fixed downstream Phase 0 inputs
* `phase6/command_surface_mapping.for_current_cutover.json` exists and contains both readiness safety fields and downstream implementation fields
* `phase6/tool_contract_compatibility_manifest.json` reports `fixed_downstream_plan_compatibility=PASS`
* `phase6/runtime_cutover_live_command_template.json` exists, references mirror validation evidence, and is marked not executed in readiness
* `phase6/consumer_migration_reconciled_input_manifest.json` exists with `blocked_row_count=0` and `missing_apply_eligible_row_count=0`
* protected current authority surface mutation count is 0 across the expanded protected surface set
* monolith re-entry count is 0
* stale bridge re-entry count is 0
* dual-current state count is 0
* dual-zero is reconfirmed
* existing current route remains green under closure-enforcing runner
* dedicated cutover-tooling route passes
* 12-module closure and allowlist cap 1 remain unchanged
* independent roadmap / plan review seal exists
* any limitation in independent `PLAN_TEMPLATE.md` / `EXECUTION_CONTRACT.md` verification is disclosed
* final tooling readiness contract report is PASS
* final claim boundary is tooling readiness only / no current cutover

If any planned tool exists but required validation is not run or does not exit 0, closeout state must be `implemented_only` or `partial`, not `complete`.

This closeout must not claim:

* cutover authorization
* successor current authority baseline adoption
* successor baseline identity final seal
* live runtime chunk replacement
* 2105 consumer migration live / main repo completion
* top ledger current authority adoption declaration
* full runtime equivalence
* full compatibility preservation
* package readiness
* release readiness
* Workshop readiness
* B42 readiness
* deployment readiness
* production validation
* manual in-game validation completion
* public-facing behavior change
* semantic / public-facing quality acceptance
* frozen 2105 recovery
* staging artifact current promotion
* current-route tooling allowlist automatic expansion
* current core 12 expansion
