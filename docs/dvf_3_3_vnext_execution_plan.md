# DVF 3-3 vNext Execution Plan

> Status: proposed execution plan / WARN rev.2 revisions applied
> Parent roadmap: `docs/dvf_3_3_vnext_current_authority_roadmap.md`
> Parent governance plan: `docs/dvf_3_3_vnext_current_authority_plan.md`
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> External synthesis input: `C:/Users/MW/.codex/attachments/d1be0404-320e-497c-a6bd-c9d214e3a34c/pasted-text.txt` / sha256 `B2D1425CD09E3002568E7834E3AE0721AD56056DECE339D1E9D1C2A208320F92` / non-authority drafting reference
> Review input: `C:/Users/MW/.codex/attachments/c5bb8eff-9b71-4cc5-803b-b8543f43ec99/pasted-text.txt` / sha256 `133EBBC993496A31AD2674D2988C86E3771F6DFB943AEC6AA8C6D676EE0B624C` / non-authority review reference
> Review input rev.2: `C:/Users/MW/.codex/attachments/3a0c24f6-400b-454c-9d60-2a620186eb76/pasted-text.txt` / sha256 `2EAF442D65A358A2ACFBBDAE7644A45F14C18F9D809A747229D53C2ED22F882F` / non-authority review reference
> Top authority: `docs/Philosophy.md`

## 1. Objective

DVF 3-3 vNext successor authority chain을 구현자가 그대로 따라 실행할 수 있는 staging-safe implementation command contract로 봉인한다.

이 계획은 첨부된 synthesized roadmap의 핵심 scope 판정을 다음처럼 고정한다.

* 이번 계획은 방향성 문서가 아니라 `implementation_plan_sealed_for_execution`을 목표로 한다.
* 계획은 input path, output path, generation command, validation command, consumer migration scope, failure condition, rollback / blocked condition을 phase별로 봉인한다.
* 후속 실행은 이 계획의 command contract를 따라 isolated staging root에서 `staging execution evidence production`을 수행한다.
* 단, canon docs, live data, live output, runtime Lua payload, package artifact는 변경하지 않는다.
* 후속 실행 산출물은 adversarial review와 별도 cutover 판단의 입력이지 current authority, release readiness, runtime cutover가 아니다.

목표 chain은 다음 순서를 유지한다.

```text
source manifest
-> facts
-> decisions
-> compose profile + body_plan
-> rendered
-> Lua bridge
-> chunk manifest + chunk files
```

실행 중 command surface가 staging-safe로 확인되지 않으면 해당 phase는 추정 실행하지 않고 `blocked_tooling_unverified`로 닫는다. 어떤 generation / export command도 resolved output path pre-flight guard와 protected surface before hash capture 없이 실행할 수 없다.

---

## 2. Scope

이 계획은 DVF 3-3 vNext successor candidate를 live path 밖에서 생성, 검증, 비교, dry-run할 수 있도록 phase별 command contract를 봉인하는 구현 계획이다.

Primary staging root:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/`

계획 문서:

* `docs/dvf_3_3_vnext_execution_plan.md`

포함 범위:

* Phase 0 command / input / protected surface lock
* command contract table and wrapper/tool closure requirement
* protected output path pre-flight abort guard
* protected surface before / after / diff / no-mutation verdict
* source universe manifest 생성 또는 blocked 상태 기록
* source input attempt order and blocked state classification
* accepted source 기반 facts / decisions 생성 또는 blocked 상태 기록
* compose profile + body_plan binding fingerprint
* rendered regeneration into staging only
* Lua bridge and chunk candidate export into staging only
* isolated staging Lua module-load harness
* source-to-runtime self-consistency report
* predecessor-to-successor delta classification
* 2105 audit 기반 consumer migration matrix and dry-run
* validator / test / tool route separation report
* cutover precondition and staging rollback boundary
* staging-only ledger reflection packet

### Explicitly Out Of Scope

* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua` 변경
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua` 변경
* `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua` 변경
* `Iris/build/description/v2/data/dvf_3_3_facts.jsonl` 변경
* `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl` 변경
* `Iris/build/description/v2/output/dvf_3_3_rendered.json` 변경
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` 직접 mutation
* source reconstruction completion 선언
* successor sealed baseline identity 봉인
* runtime cutover
* consumer migration execution
* package / release / Workshop / B42 readiness 선언
* manual in-game validation
* Browser / Wiki / Tooltip behavior change
* quality exposure change
* Layer4 / ACQ_DOMINANT / Acquisition Lexical / Resolver / Silent 21 reopen
* `active / silent` repo-wide 기계 삭제
* `2105 / 2084 / 21` 숫자 기계 치환
* predecessor byte-level recovery

---

## 3. Non-Goals

* vNext baseline을 current authority로 승격하지 않는다.
* runtime-derived seed를 source authority로 승격하지 않는다.
* runtime chunks를 source authority로 읽지 않는다.
* current 6-entry facts / decisions / rendered fixture를 full authority input으로 쓰지 않는다.
* rendered-only, bridge-only, chunk-generation-only output을 current authority로 승격하지 않는다.
* old chunks와 successor chunks를 동시에 current로 두지 않는다.
* consumer migration dry-run을 실제 mutation으로 바꾸지 않는다.
* `change_required_index.md`를 executable instruction으로 직접 취급하지 않는다.
* historical / diagnostic / docs-only row를 current hard gate로 승격하지 않는다.
* `active / silent`를 current writer / validator / runtime payload vocabulary로 되살리지 않는다.
* `adopted / unadopted`를 quality, publish, deletion, suppression 의미로 확장하지 않는다.
* package pass나 smoke pass를 release readiness로 읽지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 기준이다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 current DVF 3-3 vNext readpoint를 따른다.
* `docs/dvf_3_3_vnext_current_authority_plan.md`는 definition-only governance plan으로 이미 존재한다.
* `docs/dvf_3_3_vnext_current_authority_roadmap.md`는 definition-only successor authority roadmap으로 이미 봉인되어 있다.
* 이번 계획은 그 다음 단계인 execution plan이다.
* current deployable runtime authority는 existing `IrisLayer3DataChunks.lua` manifest와 chunk files다.
* existing runtime chunks는 predecessor comparison reference이지만 source authority가 아니다.
* runtime-derived seed는 `derived-from-runtime-chunks` provenance를 가진 non-authority bootstrap material로만 사용할 수 있다.
* `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`은 current partial readpoint input이며 vNext successor source manifest 그 자체가 아니다.
* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/`는 migration input이다.
* command는 실제 repo에서 staging-safe input / output flags가 확인된 경우에만 execution contract로 쓴다.
* `compose_layer3_text.py`는 explicit `--facts-path`, `--decisions-path`, `--profiles-path`, `--output-path`, `--overlay-path`, `--style-log-path`가 있으므로 staging output 후보로 볼 수 있다.
* `export_dvf_3_3_lua_bridge.py`는 explicit `--rendered-path`, `--lua-output-path`, `--report-path`, `--chunk-output-dir`, `--chunk-manifest-path`, `--chunk-module-prefix`가 있으나, 기본값은 live Lua path이므로 반드시 explicit staging paths와 protected-surface hash guard를 함께 사용한다.
* command가 default live path를 쓰거나 staging output을 보장하지 못하면 실행하지 않고 wrapper/tool update 대상으로 분리한다.

---

## 5. Repository Areas Affected

### Code

This plan implements vNext-specific staging tooling through Change 0 and runs it.

This plan does not modify existing tools, default current-route behavior, live data / output / runtime payload, or canon docs.

Possible existing tool touch points, only if a staging-safety gap is proven and separately approved:

* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/build/description/v2/tools/build/validate_interaction_cluster_rendered.py`
* `Iris/build/description/v2/tools/build/validate_interaction_cluster_phase_d_runtime.py`

Required command-contract tooling to implement or verify before execution:

* `Iris/build/description/v2/tools/build/hash_dvf_3_3_vnext_protected_surface.py`
* `Iris/build/description/v2/tools/build/guard_dvf_3_3_vnext_output_paths.py`
* `Iris/build/description/v2/tools/build/write_dvf_3_3_vnext_phase0_contract_inputs.py`
* `Iris/build/description/v2/tools/build/extract_dvf_3_3_vnext_runtime_seed.py`
* `Iris/build/description/v2/tools/build/build_dvf_3_3_vnext_source_manifest.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_source_manifest.py`
* `Iris/build/description/v2/tools/build/build_dvf_3_3_vnext_facts_decisions.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_facts_decisions.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_compose_binding.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_lua_load_harness.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_self_consistency.py`
* `Iris/build/description/v2/tools/build/classify_dvf_3_3_vnext_delta.py`
* `Iris/build/description/v2/tools/build/build_dvf_3_3_vnext_consumer_migration_matrix.py`
* `Iris/build/description/v2/tools/build/dry_run_dvf_3_3_vnext_consumer_migration.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_execution_contract.py`
* `Iris/build/description/v2/tools/build/write_dvf_3_3_vnext_ledger_packet.py`

Any such code change must be justified by a staging-safety gap and must not change default current route behavior without separate approval.

### Docs

Directly added:

* `docs/dvf_3_3_vnext_execution_plan.md`

Read-only authority inputs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/dvf_3_3_vnext_current_authority_plan.md`
* `docs/dvf_3_3_vnext_current_authority_roadmap.md`
* `docs/dvf_3_3_vnext_authority_scope_lock.md`
* `docs/dvf_3_3_vnext_source_authority_conditions.md`
* `docs/dvf_3_3_vnext_runtime_seed_disposition.md`
* `docs/dvf_3_3_vnext_regeneration_requirements.md`
* `docs/dvf_3_3_vnext_consumer_migration_principles.md`
* `docs/dvf_3_3_vnext_cutover_contract.md`
* `docs/dvf_3_3_vnext_ledger_update_packet.md`

Staging-only documentation outputs:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/EXECUTION_CONTRACT.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/cutover_preconditions.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/rollback_boundary.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/ledger_update_packet.md`

### Config

None directly.

Follow-up execution may read:

* `Iris/build/description/v2/data/compose_profiles_v2.json`
* `Iris/build/description/v2/data/compose_profile_identity_hint_rules.json`
* `Iris/build/description/v2/data/compose_profile_conflict_precedence_rules.json`

### Generated Artifacts

All generated artifacts must stay under:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/`

Expected staging artifact families:

* `phase0/input_readpoint.json`
* `phase0/command_surface_inventory.json`
* `phase0/implementation_command_contract.md`
* `phase0/tooling_closure_report.json`
* `phase0/template_and_input_anchor.json`
* `phase0/protected_surface_set.json`
* `phase0/protected_surface_hashes.before.json`
* `phase0/output_path_preflight_guard.json`
* `phase0/guard_negative_self_test.json`
* `phase0/tool_behavior_self_test_report.json`
* `phase0/tooling_unverified.md`
* `phase1/output_path_preflight_guard.json`
* `phase1/source_input_attempt_order.md`
* `phase1/source_universe_manifest.schema.json`
* `phase1/source_universe_manifest.json`
* `phase1/source_manifest.validation.json`
* `phase1/source_manifest.fingerprint.json`
* `phase1/source_blocked_state.md`
* `phase2/output_path_preflight_guard.json`
* `phase2/dvf_3_3_vnext_facts.jsonl`
* `phase2/dvf_3_3_vnext_decisions.jsonl`
* `phase2/facts_decisions.validation.json`
* `phase2/facts_decisions.hashes.json`
* `phase3/output_path_preflight_guard.json`
* `phase3/compose_binding_manifest.json`
* `phase3/compose_profile_fingerprint.json`
* `phase3/overlay_disposition.md`
* `phase4/output_path_preflight_guard.json`
* `phase4/dvf_3_3_vnext_rendered.json`
* `phase4/rendered.validation.json`
* `phase4/rendered.determinism.json`
* `phase4/rendered.hash.json`
* `phase4/style_baseline_conformance.json`
* `phase5/output_path_preflight_guard.json`
* `phase5/IrisLayer3Data.lua`
* `phase5/IrisLayer3DataChunks.lua`
* `phase5/IrisLayer3DataChunks/*.lua`
* `phase5/lua_bridge_export_report.json`
* `phase5/chunk_hashes.json`
* `phase5/staging_lua_load_harness_report.json`
* `phase5/staging_loaded_module_paths.json`
* `phase5/live_module_leak_report.json`
* `phase6/output_path_preflight_guard.json`
* `phase6/source_to_runtime_self_consistency.json`
* `phase6/authority_chain_fingerprint.json`
* `phase7/output_path_preflight_guard.json`
* `phase7/predecessor_successor_delta.jsonl`
* `phase7/delta_summary.json`
* `phase7/explained_delta_metrics.json`
* `phase8/output_path_preflight_guard.json`
* `phase8/migration_input_manifest.json`
* `phase8/consumer_migration_matrix.jsonl`
* `phase8/consumer_migration_dry_run.json`
* `phase8/consumer_hashes.before.json`
* `phase8/consumer_hashes.after.json`
* `phase8/consumer_hash_diff.json`
* `phase8/forbidden_touch_report.json`
* `phase9/output_path_preflight_guard.json`
* `phase9/validator_test_tool_contract.md`
* `phase9/current_route_regression_report.json`
* `phase10/output_path_preflight_guard.json`
* `phase10/cutover_preconditions.md`
* `phase10/rollback_boundary.md`
* `phase10/protected_surface_hashes.after.json`
* `phase10/protected_surface_hash_diff.json`
* `phase10/protected_surface_no_mutation_verdict.json`
* `phase11/output_path_preflight_guard.json`
* `phase11/ledger_update_packet.md`

### Implementation Command Contract

This section is the execution contract layer. A phase is executable only when its command exists, resolves outputs under the staging root, and has a validation command. If a command does not exist, the plan does not guess; the corresponding wrapper/tool must be implemented under `Iris/build/description/v2/tools/build/` before execution or the phase closes with the listed blocked state.

Common variables:

* `ROOT`: `Iris/build/description/v2/staging/dvf_3_3_vnext_execution`
* `PROTECTED_SET`: `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase0/protected_surface_set.json`
* `COMMAND_CONTRACT`: `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase0/implementation_command_contract.md`

Common pre-flight command before every generation/export/write-capable command:

The output must be phase-local. Replace `<phaseN>` with the phase currently being executed. Writing a Phase 1-11 pre-flight report into `phase0/` is forbidden.

```powershell
python -B Iris\build\description\v2\tools\build\guard_dvf_3_3_vnext_output_paths.py --command-contract Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase0\implementation_command_contract.md --protected-surface Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase0\protected_surface_set.json --phase <phaseN> --output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\<phaseN>\output_path_preflight_guard.json
```

#### Phase 0 Command Contract

Purpose: lock inputs, protected surfaces, and command availability.

Inputs:

* `docs/PLAN_TEMPLATE.md`
* `docs/dvf_3_3_vnext_current_authority_roadmap.md`
* `docs/dvf_3_3_vnext_current_authority_plan.md`
* `docs/dvf_3_3_vnext_source_authority_conditions.md`
* `docs/dvf_3_3_vnext_cutover_contract.md`
* external synthesis / review attachments listed in the header

Outputs:

* `phase0/input_readpoint.json`
* `phase0/template_and_input_anchor.json`
* `phase0/protected_surface_set.json`
* `phase0/output_path_preflight_guard.json`
* `phase0/protected_surface_hashes.before.json`
* `phase0/implementation_command_contract.md`
* `phase0/tooling_closure_report.json`
* `phase0/guard_negative_self_test.json`
* `phase0/tool_behavior_self_test_report.json`

Generation commands:

```powershell
python -B Iris\build\description\v2\tools\build\write_dvf_3_3_vnext_phase0_contract_inputs.py --execution-root Iris\build\description\v2\staging\dvf_3_3_vnext_execution --plan docs\dvf_3_3_vnext_execution_plan.md --template docs\PLAN_TEMPLATE.md --source-authority-conditions docs\dvf_3_3_vnext_source_authority_conditions.md --cutover-contract docs\dvf_3_3_vnext_cutover_contract.md --input-readpoint-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase0\input_readpoint.json --template-anchor-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase0\template_and_input_anchor.json --protected-surface-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase0\protected_surface_set.json --command-contract-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase0\implementation_command_contract.md
```

```powershell
python -B Iris\build\description\v2\tools\build\hash_dvf_3_3_vnext_protected_surface.py --surface Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase0\protected_surface_set.json --output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase0\protected_surface_hashes.before.json
```

```powershell
python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_vnext_execution_contract.py --execution-root Iris\build\description\v2\staging\dvf_3_3_vnext_execution --output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase0\tooling_closure_report.json
```

```powershell
python -B Iris\build\description\v2\tools\build\guard_dvf_3_3_vnext_output_paths.py --command-contract Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase0\implementation_command_contract.md --protected-surface Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase0\protected_surface_set.json --phase phase0 --known-protected-output Iris\media\lua\client\Iris\Data\IrisLayer3DataChunks.lua --expect-fail --output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase0\guard_negative_self_test.json
```

Validation command:

```powershell
python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_vnext_execution_contract.py --execution-root Iris\build\description\v2\staging\dvf_3_3_vnext_execution --require-phase phase0 --tool-state-enum implemented_new,verified_existing,missing_to_implement,unsafe_live_default,blocked_requires_design --self-test-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase0\tool_behavior_self_test_report.json --output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase0\tooling_closure_report.json
```

Writes allowed: `phase0/` only.

Protected writes forbidden: all protected surface paths.

Blocked state: `blocked_tooling_unverified`.

#### Phase 1 Command Contract

Purpose: create or block the vNext source manifest.

Inputs:

* `docs/dvf_3_3_vnext_source_authority_conditions.md`
* `Iris/build/description/v2/data/dvf_3_3_input_manifest.json` as partial readpoint input only
* live runtime chunks as non-authority seed input only

Outputs:

* `phase1/output_path_preflight_guard.json`
* `phase1/runtime_derived_seed.jsonl`
* `phase1/source_universe_manifest.schema.json`
* `phase1/source_universe_manifest.json`
* `phase1/source_manifest.validation.json`
* `phase1/source_manifest.fingerprint.json`
* `phase1/source_input_attempt_order.md`
* `phase1/source_blocked_state.md`

Generation commands:

```powershell
python -B Iris\build\description\v2\tools\build\extract_dvf_3_3_vnext_runtime_seed.py --runtime-manifest Iris\media\lua\client\Iris\Data\IrisLayer3DataChunks.lua --runtime-chunk-dir Iris\media\lua\client\Iris\Data\IrisLayer3DataChunks --output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase1\runtime_derived_seed.jsonl --provenance derived-from-runtime-chunks
```

```powershell
python -B Iris\build\description\v2\tools\build\build_dvf_3_3_vnext_source_manifest.py --source-conditions docs\dvf_3_3_vnext_source_authority_conditions.md --partial-input-manifest Iris\build\description\v2\data\dvf_3_3_input_manifest.json --runtime-seed Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase1\runtime_derived_seed.jsonl --schema-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase1\source_universe_manifest.schema.json --output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase1\source_universe_manifest.json --attempt-order-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase1\source_input_attempt_order.md --blocked-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase1\source_blocked_state.md
```

Validation command:

```powershell
python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_vnext_source_manifest.py --schema Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase1\source_universe_manifest.schema.json --manifest Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase1\source_universe_manifest.json --source-conditions docs\dvf_3_3_vnext_source_authority_conditions.md --fingerprint-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase1\source_manifest.fingerprint.json --report-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase1\source_manifest.validation.json
```

Writes allowed: `phase1/` only.

Protected writes forbidden: all protected surface paths.

Success criteria: accepted source rows satisfy `docs/dvf_3_3_vnext_source_authority_conditions.md`; runtime-derived seed rows are not accepted authority rows.

Blocked states: `blocked_source_universe_unavailable`, `blocked_source_manifest_generator_unavailable`, `blocked_source_manifest_schema_unverified`, `blocked_runtime_seed_only_no_authority_source`.

#### Phase 2 Command Contract

Purpose: generate facts and decisions from accepted source rows.

Inputs:

* `phase1/source_universe_manifest.json`

Outputs:

* `phase2/output_path_preflight_guard.json`
* `phase2/dvf_3_3_vnext_facts.jsonl`
* `phase2/dvf_3_3_vnext_decisions.jsonl`
* `phase2/facts_decisions.validation.json`
* `phase2/facts_decisions.hashes.json`

Generation command:

```powershell
python -B Iris\build\description\v2\tools\build\build_dvf_3_3_vnext_facts_decisions.py --source-manifest Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase1\source_universe_manifest.json --facts-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase2\dvf_3_3_vnext_facts.jsonl --decisions-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase2\dvf_3_3_vnext_decisions.jsonl --hash-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase2\facts_decisions.hashes.json
```

Validation command:

```powershell
python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_vnext_facts_decisions.py --source-manifest Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase1\source_universe_manifest.json --facts Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase2\dvf_3_3_vnext_facts.jsonl --decisions Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase2\dvf_3_3_vnext_decisions.jsonl --report-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase2\facts_decisions.validation.json
```

Writes allowed: `phase2/` only.

Protected writes forbidden: all protected surface paths.

Blocked states: `blocked_source_universe_unavailable`, `blocked_source_manifest_generator_unavailable`, `blocked_tooling_unverified`.

#### Phase 3 Command Contract

Purpose: seal compose profile, body_plan, and overlay disposition for this vNext run.

Inputs:

* `Iris/build/description/v2/data/compose_profiles_v2.json`
* `Iris/build/description/v2/data/compose_profile_identity_hint_rules.json`
* `Iris/build/description/v2/data/compose_profile_conflict_precedence_rules.json`
* optional accepted overlay, if Phase 0 proves non-fixture full input

Outputs:

* `phase3/output_path_preflight_guard.json`
* `phase3/compose_binding_manifest.json`
* `phase3/compose_profile_fingerprint.json`
* `phase3/overlay_disposition.md`

Generation / validation command:

```powershell
python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_vnext_compose_binding.py --profiles Iris\build\description\v2\data\compose_profiles_v2.json --identity-rules Iris\build\description\v2\data\compose_profile_identity_hint_rules.json --precedence-rules Iris\build\description\v2\data\compose_profile_conflict_precedence_rules.json --binding-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase3\compose_binding_manifest.json --fingerprint-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase3\compose_profile_fingerprint.json --overlay-disposition-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase3\overlay_disposition.md
```

Writes allowed: `phase3/` only.

Protected writes forbidden: all protected surface paths.

Blocked state: `blocked_tooling_unverified`.

#### Phase 4 Command Contract

Purpose: generate rendered output under staging.

Inputs:

* `phase2/dvf_3_3_vnext_facts.jsonl`
* `phase2/dvf_3_3_vnext_decisions.jsonl`
* `Iris/build/description/v2/data/compose_profiles_v2.json`
* `Iris/build/description/v2/data/compose_profile_identity_hint_rules.json`
* `Iris/build/description/v2/data/compose_profile_conflict_precedence_rules.json`

Outputs:

* `phase4/output_path_preflight_guard.json`
* `phase4/dvf_3_3_vnext_rendered.json`
* `phase4/style_normalization_changes.jsonl`
* `phase4/rendered.validation.json`
* `phase4/rendered.determinism.json`
* `phase4/rendered.hash.json`
* `phase4/style_baseline_conformance.json`

Generation command:

```powershell
python -B Iris\build\description\v2\tools\build\compose_layer3_text.py --mode default --facts-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase2\dvf_3_3_vnext_facts.jsonl --decisions-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase2\dvf_3_3_vnext_decisions.jsonl --profiles-path Iris\build\description\v2\data\compose_profiles_v2.json --identity-rules-path Iris\build\description\v2\data\compose_profile_identity_hint_rules.json --precedence-rules-path Iris\build\description\v2\data\compose_profile_conflict_precedence_rules.json --output-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase4\dvf_3_3_vnext_rendered.json --style-log-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase4\style_normalization_changes.jsonl
```

If Phase 3 accepts a non-fixture overlay, the only allowed alternate generation command appends:

```powershell
--overlay-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase3\accepted_overlay.jsonl
```

Validation commands:

```powershell
python -B Iris\build\description\v2\tools\build\validate_interaction_cluster_rendered.py --decisions-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase2\dvf_3_3_vnext_decisions.jsonl --rendered-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase4\dvf_3_3_vnext_rendered.json --report-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase4\rendered.validation.json
```

```powershell
python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_vnext_execution_contract.py --execution-root Iris\build\description\v2\staging\dvf_3_3_vnext_execution --require-phase phase4 --output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase4\rendered.determinism.json
```

Writes allowed: `phase4/` only.

Protected writes forbidden: all protected surface paths.

Blocked state: `blocked_tooling_unverified`.

#### Phase 5 Command Contract

Purpose: export staging Lua bridge and chunks.

Inputs:

* `phase4/dvf_3_3_vnext_rendered.json`

Outputs:

* `phase5/output_path_preflight_guard.json`
* `phase5/IrisLayer3Data.lua`
* `phase5/IrisLayer3DataChunks.lua`
* `phase5/IrisLayer3DataChunks/*.lua`
* `phase5/lua_bridge_export_report.json`
* `phase5/chunk_hashes.json`
* `phase5/staging_lua_load_harness_report.json`
* `phase5/staging_loaded_module_paths.json`
* `phase5/live_module_leak_report.json`

Generation command:

```powershell
python -B Iris\build\description\v2\tools\build\export_dvf_3_3_lua_bridge.py --rendered-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase4\dvf_3_3_vnext_rendered.json --lua-output-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\IrisLayer3Data.lua --report-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\lua_bridge_export_report.json --chunk-output-dir Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\IrisLayer3DataChunks --chunk-manifest-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\IrisLayer3DataChunks.lua --chunk-module-prefix Iris/Data/IrisLayer3DataChunks
```

Validation commands:

```powershell
python -B Iris\build\description\v2\tools\build\validate_interaction_cluster_phase_d_runtime.py --rendered-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase4\dvf_3_3_vnext_rendered.json --bridge-report-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\lua_bridge_export_report.json --layer3-data-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\IrisLayer3Data.lua --layer3-chunk-manifest-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\IrisLayer3DataChunks.lua --layer3-chunk-dir Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\IrisLayer3DataChunks --output-path Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\runtime_bridge_validation_report.json
```

```powershell
python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_vnext_lua_load_harness.py --staging-data-root Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5 --live-data-root Iris\media\lua\client\Iris\Data --report-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\staging_lua_load_harness_report.json --loaded-paths-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\staging_loaded_module_paths.json --leak-report-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\live_module_leak_report.json
```

Writes allowed: `phase5/` only.

Protected writes forbidden: all protected surface paths.

Blocked state: `blocked_tooling_unverified`.

#### Phase 6 Command Contract

Purpose: validate source-to-runtime self-consistency.

Inputs:

* Phase 1-5 outputs

Outputs:

* `phase6/output_path_preflight_guard.json`
* `phase6/source_to_runtime_self_consistency.json`
* `phase6/authority_chain_fingerprint.json`

Validation command:

```powershell
python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_vnext_self_consistency.py --source-manifest Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase1\source_universe_manifest.json --facts Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase2\dvf_3_3_vnext_facts.jsonl --decisions Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase2\dvf_3_3_vnext_decisions.jsonl --compose-binding Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase3\compose_binding_manifest.json --rendered Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase4\dvf_3_3_vnext_rendered.json --bridge-report Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\lua_bridge_export_report.json --chunk-manifest Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\IrisLayer3DataChunks.lua --chunk-dir Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\IrisLayer3DataChunks --lua-load-report Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\staging_lua_load_harness_report.json --report-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase6\source_to_runtime_self_consistency.json --fingerprint-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase6\authority_chain_fingerprint.json
```

Writes allowed: `phase6/` only.

Protected writes forbidden: all protected surface paths.

Blocked state: `partial_blocked_some_phases_incomplete`.

#### Phase 7 Command Contract

Purpose: classify predecessor-successor delta.

Inputs:

* live predecessor runtime chunks as read-only comparison reference
* Phase 5 staging successor chunks

Outputs:

* `phase7/output_path_preflight_guard.json`
* `phase7/predecessor_successor_delta.jsonl`
* `phase7/delta_summary.json`
* `phase7/unexplained_delta_report.md`
* `phase7/explained_delta_metrics.json`

Validation command:

```powershell
python -B Iris\build\description\v2\tools\build\classify_dvf_3_3_vnext_delta.py --predecessor-manifest Iris\media\lua\client\Iris\Data\IrisLayer3DataChunks.lua --predecessor-chunk-dir Iris\media\lua\client\Iris\Data\IrisLayer3DataChunks --successor-manifest Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\IrisLayer3DataChunks.lua --successor-chunk-dir Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase5\IrisLayer3DataChunks --source-manifest Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase1\source_universe_manifest.json --facts Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase2\dvf_3_3_vnext_facts.jsonl --decisions Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase2\dvf_3_3_vnext_decisions.jsonl --compose-binding Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase3\compose_binding_manifest.json --rendered Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase4\dvf_3_3_vnext_rendered.json --output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase7\predecessor_successor_delta.jsonl --summary-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase7\delta_summary.json --unexplained-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase7\unexplained_delta_report.md --metrics-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase7\explained_delta_metrics.json
```

Writes allowed: `phase7/` only.

Protected writes forbidden: all protected surface paths.

Success criteria: `unexplained_delta_count == 0`.

Blocked state: `partial_blocked_some_phases_incomplete`.

#### Phase 8 Command Contract

Purpose: build consumer migration matrix and dry-run without mutation.

Inputs:

* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/classified_ledger.jsonl`
* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/change_required_index.md`
* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/change_forbidden_index.md`
* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/executing_consumer_impact.md`

Outputs:

* `phase8/output_path_preflight_guard.json`
* `phase8/migration_input_manifest.json`
* `phase8/consumer_migration_matrix.jsonl`
* `phase8/consumer_migration_dry_run.json`
* `phase8/consumer_hashes.before.json`
* `phase8/consumer_hashes.after.json`
* `phase8/consumer_hash_diff.json`
* `phase8/forbidden_touch_report.json`
* `phase8/migration_blockers.md`

Generation commands:

```powershell
python -B Iris\build\description\v2\tools\build\build_dvf_3_3_vnext_consumer_migration_matrix.py --classified-ledger Iris\build\description\v2\staging\2105_baseline_consumption_audit\classified_ledger.jsonl --change-required Iris\build\description\v2\staging\2105_baseline_consumption_audit\change_required_index.md --change-forbidden Iris\build\description\v2\staging\2105_baseline_consumption_audit\change_forbidden_index.md --executing-impact Iris\build\description\v2\staging\2105_baseline_consumption_audit\executing_consumer_impact.md --input-manifest-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase8\migration_input_manifest.json --matrix-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase8\consumer_migration_matrix.jsonl --expected-change-required 311 --expected-change-forbidden 27558
```

```powershell
python -B Iris\build\description\v2\tools\build\dry_run_dvf_3_3_vnext_consumer_migration.py --matrix Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase8\consumer_migration_matrix.jsonl --dry-run-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase8\consumer_migration_dry_run.json --consumer-before-hashes Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase8\consumer_hashes.before.json --consumer-after-hashes Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase8\consumer_hashes.after.json --consumer-hash-diff Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase8\consumer_hash_diff.json --forbidden-touch-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase8\forbidden_touch_report.json --blockers-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase8\migration_blockers.md
```

Writes allowed: `phase8/` only.

Protected writes forbidden: all protected surface paths and all consumer files.

Blocked state: `partial_blocked_some_phases_incomplete`.

#### Phase 9 Command Contract

Purpose: run current route regression and vNext contract validation.

Inputs:

* Phase 0-8 outputs

Outputs:

* `phase9/output_path_preflight_guard.json`
* `phase9/validator_test_tool_contract.md`
* `phase9/current_route_regression_report.json`
* `phase9/vnext_route_validation_report.json`
* `phase9/tool_change_list.md`

Validation commands:

```powershell
python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
```

```powershell
python -B Iris\build\description\v2\tools\validate_legacy_active_silent_current_surface_guard.py
```

```powershell
python -B Iris\build\description\v2\tools\validate_layer4_absorption_current_surface_guard.py
```

```powershell
python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_vnext_execution_contract.py --execution-root Iris\build\description\v2\staging\dvf_3_3_vnext_execution --require-phase all --output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase9\vnext_route_validation_report.json
```

Writes allowed: `phase9/` only.

Protected writes forbidden: all protected surface paths.

Blocked state: `partial_blocked_some_phases_incomplete`.

#### Phase 10 Command Contract

Purpose: seal cutover preconditions and protected no-mutation verdict.

Inputs:

* Phase 0-9 outputs
* `docs/dvf_3_3_vnext_cutover_contract.md`

Outputs:

* `phase10/output_path_preflight_guard.json`
* `phase10/cutover_preconditions.md`
* `phase10/rollback_boundary.md`
* `phase10/protected_surface_hashes.after.json`
* `phase10/protected_surface_hash_diff.json`
* `phase10/protected_surface_no_mutation_verdict.json`

Generation / validation commands:

```powershell
python -B Iris\build\description\v2\tools\build\hash_dvf_3_3_vnext_protected_surface.py --surface Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase0\protected_surface_set.json --output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase10\protected_surface_hashes.after.json --compare Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase0\protected_surface_hashes.before.json --diff-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase10\protected_surface_hash_diff.json --verdict-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase10\protected_surface_no_mutation_verdict.json
```

```powershell
python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_vnext_execution_contract.py --execution-root Iris\build\description\v2\staging\dvf_3_3_vnext_execution --require-phase phase10 --cutover-contract docs\dvf_3_3_vnext_cutover_contract.md --output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase10\cutover_preconditions.md
```

Writes allowed: `phase10/` only.

Protected writes forbidden: all protected surface paths.

Success criteria: `protected_surface_hash_diff.changed_count == 0`.

Blocked / failed state: `failed_protected_surface_mutation`.

#### Phase 11 Command Contract

Purpose: prepare non-binding ledger reflection packet.

Inputs:

* Phase 0-10 outputs

Outputs:

* `phase11/output_path_preflight_guard.json`
* `phase11/ledger_update_packet.md`
* `phase11/proposed_decisions_entry.md`
* `phase11/proposed_architecture_patch.md`
* `phase11/proposed_roadmap_patch.md`

Generation command:

```powershell
python -B Iris\build\description\v2\tools\build\write_dvf_3_3_vnext_ledger_packet.py --execution-root Iris\build\description\v2\staging\dvf_3_3_vnext_execution --packet-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase11\ledger_update_packet.md --decisions-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase11\proposed_decisions_entry.md --architecture-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase11\proposed_architecture_patch.md --roadmap-output Iris\build\description\v2\staging\dvf_3_3_vnext_execution\phase11\proposed_roadmap_patch.md
```

Writes allowed: `phase11/` only.

Protected writes forbidden: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`.

Blocked state: `partial_blocked_some_phases_incomplete`.

---

## 6. Planned Changes

### Change 0 - Command Contract Tooling Closure

Purpose:

이 계획을 `implementation_plan_sealed_for_execution` 상태로 만들기 위해 phase별 wrapper / validator / guard command를 구현 또는 존재 확인한다.

Files:

* `Iris/build/description/v2/tools/build/hash_dvf_3_3_vnext_protected_surface.py`
* `Iris/build/description/v2/tools/build/guard_dvf_3_3_vnext_output_paths.py`
* `Iris/build/description/v2/tools/build/write_dvf_3_3_vnext_phase0_contract_inputs.py`
* `Iris/build/description/v2/tools/build/extract_dvf_3_3_vnext_runtime_seed.py`
* `Iris/build/description/v2/tools/build/build_dvf_3_3_vnext_source_manifest.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_source_manifest.py`
* `Iris/build/description/v2/tools/build/build_dvf_3_3_vnext_facts_decisions.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_facts_decisions.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_compose_binding.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_lua_load_harness.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_self_consistency.py`
* `Iris/build/description/v2/tools/build/classify_dvf_3_3_vnext_delta.py`
* `Iris/build/description/v2/tools/build/build_dvf_3_3_vnext_consumer_migration_matrix.py`
* `Iris/build/description/v2/tools/build/dry_run_dvf_3_3_vnext_consumer_migration.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_execution_contract.py`
* `Iris/build/description/v2/tools/build/write_dvf_3_3_vnext_ledger_packet.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase0/implementation_command_contract.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase0/tooling_closure_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase0/guard_negative_self_test.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase0/tool_behavior_self_test_report.json`

Implementation Notes:

* each wrapper must support explicit input / output arguments and must not default to live runtime, live data, live output, or canon docs.
* every write-capable wrapper must expose output paths in a form consumable by `guard_dvf_3_3_vnext_output_paths.py`.
* existing tools may be reused only if their exact command line is listed in the command contract and their resolved output paths are staging-safe.
* missing wrappers are not execution blockers after this Change is implemented; they are implementation tasks of this plan.
* if any wrapper cannot be implemented without changing current route behavior, stop and close as `blocked_tooling_unverified`.
* `tooling_closure_report.json` must use per-tool state enum:
  * `implemented_new`
  * `verified_existing`
  * `missing_to_implement`
  * `unsafe_live_default`
  * `blocked_requires_design`
* guard negative self-test is mandatory:
  * known protected output path input
  * guard returns non-zero / fail
  * wrapper or orchestration halts
  * no generation / export command runs after guard failure
* guard fail or resolved protected write target detected means the wrapper refuses execution and orchestration halts on non-zero.
* behavioral self-tests are mandatory for safety / judgment tools:
  * `dry_run_dvf_3_3_vnext_consumer_migration.py` is read-only by construction and is checked by independent before / after consumer-file hash diff.
  * `validate_dvf_3_3_vnext_self_consistency.py` must fail a known-bad fixture.
  * `classify_dvf_3_3_vnext_delta.py` must fail an unexplained-delta fixture.
  * forbidden-touch / no-mutation validation must not rely only on tool self-report.

Validation:

* `validate_dvf_3_3_vnext_execution_contract.py --require-phase phase0` passes.
* all command contract commands exist.
* all write-capable commands have explicit staging output paths.
* no command resolves a protected path as write target.
* `guard_negative_self_test.json` records expected failure on a protected output path.
* `tool_behavior_self_test_report.json` records known-bad fixture failures and dry-run no-mutation independent diff.
* no tool remains `missing_to_implement`, `unsafe_live_default`, or `blocked_requires_design` for PASS.

---

### Change 1 - Phase 0 Scope Lock / Input Readpoint / Command Surface Lock

Purpose:

후속 phase가 fixture, runtime chunks, audit summary, unverified command를 authority로 오독하지 못하도록 입력 지위와 command surface를 잠근다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/EXECUTION_CONTRACT.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase0/input_readpoint.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase0/command_surface_inventory.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase0/template_and_input_anchor.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase0/protected_surface_set.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase0/protected_surface_hashes.before.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase0/output_path_preflight_guard.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase0/tooling_unverified.md`

Implementation Notes:

* `vNext-CAB`를 pre-cutover program label로만 기록한다.
* current 6-entry facts / decisions / rendered는 fixture / non-authority로 기록한다.
* current runtime chunks는 deployable authority and comparison reference로 기록한다.
* runtime-derived seed는 non-authority bootstrap으로 기록한다.
* `2105_baseline_consumption_audit` 산출물은 migration input으로만 기록한다.
* `PLAN_TEMPLATE.md`, external synthesis input, review input의 path / sha256 / authority role을 `template_and_input_anchor.json`에 기록한다.
* `compose_layer3_text.py`, `export_dvf_3_3_lua_bridge.py`, rendered validator, runtime bridge validator의 input / output flag를 inventory한다.
* protected surface set을 먼저 정의한다.
  * live runtime chunks: `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`, `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`
  * live runtime facade / loader: `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua` when present or generated by the bridge exporter
  * live description data: `Iris/build/description/v2/data/`
  * live description output: `Iris/build/description/v2/output/`
  * canon docs: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
* protected surface set is intentionally broad for this round. Hashing `data/` and `output/` may be expensive, but safety takes precedence over hash cost.
* protected surface narrowing for performance requires a separate approved plan and cannot be introduced inside this execution round.
* live protected paths의 before hash를 먼저 캡처한다.
* any generation / export command must resolve all output paths before execution.
* resolved output path inside protected surface set means abort before write.
* default output path invocation is forbidden unless every resolved output path is proven staging-safe.
* staging-safe output을 보장하지 못하는 command는 실행 금지하고 `tooling_unverified`에 기록한다.

Validation:

* `PLAN_TEMPLATE.md` exists and hash is recorded.
* external synthesis and review inputs are labeled non-authority references.
* protected surface hash capture exists.
* protected surface set includes live runtime chunks, live runtime facade / loader if applicable, live data, live output, and canon docs.
* output path pre-flight guard exists.
* live path write targets are absent from execution command contract.
* unverified commands are marked blocked, not guessed.
* no source authority is assigned to runtime chunks or runtime-derived seed.

---

### Change 2 - Phase 1 Source Universe Manifest

Purpose:

successor authority 후보의 첫 upstream input인 source universe manifest를 staging에서 생성하거나 blocked 상태로 닫는다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase1/source_universe_manifest.schema.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase1/source_universe_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase1/source_manifest.validation.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase1/source_manifest.fingerprint.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase1/source_input_attempt_order.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase1/source_blocked_state.md`

Implementation Notes:

* source input attempt order is fixed:
  1. existing validated source-universe artifact, only if explicitly sealed for vNext
  2. generated source universe from approved non-runtime source inputs
  3. runtime-derived seed as non-authority bootstrap only, never accepted source authority
  4. if no authority source exists, close Phase 1 as `blocked_source_universe_unavailable`
* `approved non-runtime source inputs` means inputs satisfying `docs/dvf_3_3_vnext_source_authority_conditions.md`.
* Phase 1 acceptance must record which source authority condition each accepted input satisfies.
* source row identity, provenance, authority status, seed lineage, accepted / rejected / hold status를 분리한다.
* runtime-derived rows가 포함될 경우 `derived-from-runtime-chunks` provenance와 `authority_role: non_authority_bootstrap_seed`를 요구한다.
* accepted source row만 facts / decisions generation input이 될 수 있다.
* source count가 predecessor 2105와 다르다는 이유만으로 자동 실패 또는 자동 통과 처리하지 않는다.
* current `dvf_3_3_input_manifest.json`은 partial readpoint input으로만 읽고 vNext manifest identity로 재사용하지 않는다.
* allowed Phase 1 blocked states:
  * `blocked_source_universe_unavailable`
  * `blocked_source_manifest_generator_unavailable`
  * `blocked_source_manifest_schema_unverified`
  * `blocked_runtime_seed_only_no_authority_source`

Validation:

* source input attempt order is recorded.
* source authority condition mapping is recorded for every accepted input.
* schema validation PASS.
* duplicate source key count is 0.
* authority source rows derived only from runtime chunks count is 0.
* accepted source count and fingerprint captured.
* fixture paths are excluded from production manifest authority.
* runtime-derived seed-only source universe cannot pass as authority source.
* blocked state is one of the allowed Phase 1 blocked states.

---

### Change 3 - Phase 2 Facts / Decisions Generation

Purpose:

accepted source universe에서 facts와 decisions를 분리 생성하거나 generation blocker를 fail-loud로 기록한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase2/dvf_3_3_vnext_facts.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase2/dvf_3_3_vnext_decisions.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase2/facts_decisions.validation.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase2/facts_decisions.hashes.json`

Implementation Notes:

* facts는 accepted source-derived facts만 담는다.
* decisions는 composition, null reason, disposition, body_plan decision을 담는다.
* decisions generator or validator는 rendered output을 입력으로 삼지 않는다.
* legacy `active / silent`는 current writer vocabulary로 들어오지 못한다.
* `adopted / unadopted`는 runtime availability vocabulary로만 유지하고 quality / publish / deletion / suppression 의미로 확장하지 않는다.
* Phase 1이 blocked면 Phase 2는 generation을 시도하지 않고 upstream blocked state를 인용한다.
* facts / decisions generator가 없으면 phase result는 `blocked_source_manifest_generator_unavailable` or `blocked_tooling_unverified`로 닫는다.
* runtime-derived seed-only universe에서 facts / decisions를 authority output으로 생성하는 것은 금지한다.

Validation:

* accepted source count to facts / decisions key parity PASS or explicit hold reason exists.
* facts JSONL schema PASS.
* decisions JSONL schema PASS.
* legacy current vocabulary guard PASS.
* deterministic hash repeat PASS.
* downstream-to-upstream circular validation absent.

---

### Change 4 - Phase 3 Compose Profile / Body Plan Binding

Purpose:

facts / decisions를 어떤 compose profile과 body_plan implementation surface로 조합할지 고정한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase3/compose_binding_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase3/compose_profile_fingerprint.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase3/overlay_disposition.md`

Implementation Notes:

* `compose_profiles_v2.json + body_plan`은 implementation surface and alias label로만 둔다.
* `body_plan`은 second authority가 아니다.
* compose profile hash, identity rule hash, precedence rule hash를 rendered identity input fingerprint에 포함한다.
* overlay input이 실제 full input surface로 확인되면 subordinate input으로 fingerprint에 포함한다.
* overlay가 fixture-only 또는 unavailable이면 `overlay_disposition.md`에 명시하고 authority input에서 제외한다.
* selected_role / body_plan / slot sequence / required_any 규칙을 validator 대상으로 유지한다.

Validation:

* compose profile schema PASS.
* identity and precedence rule fingerprints captured.
* overlay status classified.
* required slot validation PASS.
* selected_role resolver trace PASS.
* legacy adapter default path absence PASS.

---

### Change 5 - Phase 4 Rendered Regeneration

Purpose:

facts / decisions / compose profile / body_plan에서 rendered output을 staging에 결정론적으로 생성한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase4/dvf_3_3_vnext_rendered.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase4/rendered.validation.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase4/rendered.determinism.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase4/rendered.hash.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase4/style_normalization_changes.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase4/style_baseline_conformance.json`

Implementation Notes:

* current `Iris/build/description/v2/output/dvf_3_3_rendered.json`은 덮어쓰지 않는다.
* `compose_layer3_text.py`는 explicit staging output args로만 사용한다.
* rendered output은 source manifest fingerprint, facts hash, decisions hash, compose profile hash를 trace해야 한다.
* rendered validator는 schema, count, key parity, body/state consistency, no legacy current vocabulary, no unexpected null을 확인한다.
* rendered validation must include style-baseline conformance if style linter / normalizer surfaces are active.
* style linter / normalizer may report style drift but must not mutate source authority, facts, decisions, or rendered authority in-place.
* style-baseline version and linter / normalizer command identity must be recorded when applicable.
* expected style-baseline closeout is current `v4` conformance PASS; `v5` remains deferred unless separately approved.
* while style linter / normalizer surfaces are active, `not_applicable` is not an acceptable PASS closeout.
* `not_applicable` is allowed only if Phase 0 proves the style linter / normalizer surfaces are inactive for this route and records the reason.
* predecessor byte-level parity는 success criterion이 아니다.

Validation:

* rendered schema PASS.
* accepted source universe to rendered key parity PASS.
* decisions to rendered key parity PASS.
* body/state validation PASS.
* legacy current vocabulary count 0.
* style-baseline conformance PASS. `not_applicable` is valid only when Phase 0 proves inactive style surfaces.
* deterministic repeated output hash PASS.
* canonical output path hash unchanged.

---

### Change 6 - Phase 5 Lua Bridge Export / Chunk Candidate Generation

Purpose:

rendered output에서 Lua bridge payload와 successor chunk candidate를 staging에만 export한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase5/IrisLayer3Data.lua`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase5/IrisLayer3DataChunks.lua`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase5/IrisLayer3DataChunks/*.lua`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase5/lua_bridge_export_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase5/chunk_hashes.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase5/staging_lua_load_harness_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase5/staging_loaded_module_paths.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase5/live_module_leak_report.json`

Implementation Notes:

* `export_dvf_3_3_lua_bridge.py`는 explicit staging paths가 모두 제공될 때만 사용한다.
* required explicit args include `--rendered-path`, `--lua-output-path`, `--report-path`, `--chunk-output-dir`, `--chunk-manifest-path`.
* default live Lua output path usage is forbidden in this plan.
* resolved output path pre-flight guard must run before export.
* any resolved output under the protected surface set aborts before write.
* `IrisLayer3Data.lua` is treated as a runtime facade / loader surface when generated or present. The live file is protected; the staging file is only a candidate.
* chunk manifest and chunk files are successor candidate only.
* staged chunk module prefix must preserve the runtime require contract for validation while the files remain outside live runtime paths.
* staging Lua load validation must run in an isolated module-load harness.
* the harness must:
  * set `package.path` / module prefix to the staging candidate only
  * fail if any `Iris/media/lua/client/Iris/Data` live path is loaded
  * clear or isolate require / module cache between runs
  * report loaded module paths
* live deployable runtime path is untouched before cutover.
* monolith / chunk dual current is forbidden.

Validation:

* output path pre-flight guard PASS.
* rendered to bridge key parity PASS.
* bridge to chunk key parity PASS.
* chunk manifest to chunk files consistency PASS.
* isolated staging Lua load harness PASS.
* live module leak count is 0.
* loaded module paths report exists.
* missing chunk count 0.
* orphan chunk count 0.
* live runtime path protected hashes unchanged.
* per-chunk hashes captured.

---

### Change 7 - Phase 6 Source-to-Runtime Self-Consistency

Purpose:

successor chain이 source manifest부터 chunk files까지 단방향으로 일관되는지 검증한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase6/source_to_runtime_self_consistency.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase6/authority_chain_fingerprint.json`

Implementation Notes:

* source manifest, facts, decisions, compose binding, rendered, bridge, chunks의 key universe를 단계별로 비교한다.
* downstream output으로 upstream input을 정당화하지 않는다.
* authority chain fingerprint는 각 단계의 count, content hash, schema hash, command identity를 포함한다.
* Phase 5 isolated Lua load harness result is part of the runtime-side consistency evidence.
* self-consistency cannot pass if staging Lua candidate loaded any live runtime data module.
* predecessor byte-level parity는 여기서 success criterion으로 사용하지 않는다.

Validation:

* source to facts key parity PASS.
* facts to decisions key parity PASS.
* decisions to rendered key parity PASS.
* rendered to bridge key parity PASS.
* bridge to chunks key parity PASS.
* isolated staging Lua load harness PASS.
* live module leak report PASS.
* authority chain fingerprint generated.
* self-consistency PASS.

---

### Change 8 - Phase 7 Predecessor to Successor Delta Classification

Purpose:

predecessor runtime chunks와 successor candidate chunks 사이의 delta를 분류하고 unexplained delta를 fail-loud 처리한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase7/predecessor_successor_delta.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase7/delta_summary.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase7/unexplained_delta_report.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase7/explained_delta_metrics.json`

Implementation Notes:

* predecessor chunks are read-only comparison reference.
* successor chunks are staging candidate only.
* minimum delta taxonomy:
  * `identical`
  * `intentional_successor_delta`
  * `source_gap`
  * `schema_gap`
  * `compose_delta`
  * `validation_failure`
  * `migration_required`
  * `unexplained`
* `unexplained` is allowed as an intermediate classification but must be 0 for successful closeout.
* numeric replacement and vocabulary replacement cannot be used as explanation by themselves.
* `intentional_successor_delta`, `source_gap`, `schema_gap`, and `compose_delta` require trace evidence:
  * source manifest row reference
  * facts / decisions row reference where applicable
  * compose binding reference where applicable
  * rendered diff reference
  * validator acceptance reference
* delta summary must include `explained_delta_count`, `explained_delta_ratio`, and `unexplained_delta_count`.
* delta classification is cutover input, not cutover approval.

Validation:

* predecessor-successor delta classified.
* unexplained delta count equals 0 for complete closeout.
* predecessor chunks read-only hash unchanged.
* each non-identical delta has source, schema, compose, validation, or migration rationale with trace references.
* explained delta metrics are recorded.

---

### Change 9 - Phase 8 Consumer Migration Matrix / Dry-Run

Purpose:

2105 Baseline Consumption Audit 결과를 기준으로 migration 대상과 금지 대상을 분리하고 dry-run한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase8/consumer_migration_matrix.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase8/consumer_migration_dry_run.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase8/consumer_hashes.before.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase8/consumer_hashes.after.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase8/consumer_hash_diff.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase8/forbidden_touch_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase8/migration_blockers.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase8/migration_input_manifest.json`

Implementation Notes:

* Primary machine-readable input is `classified_ledger.jsonl`.
* `change_required_index.md` is a derived summary only.
* `change_forbidden_index.md` rows are not promoted to mutation targets.
* `executing_consumer_impact.md` is included as migration input for execution-reach context.
* Phase 8 input manifest must include:
  * `Iris/build/description/v2/staging/2105_baseline_consumption_audit/classified_ledger.jsonl`
  * `Iris/build/description/v2/staging/2105_baseline_consumption_audit/change_required_index.md`
  * `Iris/build/description/v2/staging/2105_baseline_consumption_audit/change_forbidden_index.md`
  * `Iris/build/description/v2/staging/2105_baseline_consumption_audit/executing_consumer_impact.md`
* current hard gate / validator / test / tool / runtime consumer rows are separated from historical / diagnostic / false-positive / no-op rows.
* migration means authority-role migration, not numeric or vocabulary replacement.
* dry-run must produce no file mutation.
* migration matrix must reconcile against the sealed audit counts:
  * `change_required` total is 311
  * `change_forbidden` total is 27558
* count reconciliation is drift detection only; these counts do not create source authority or successor baseline identity.
* Phase 8 dry-run claims projected static current-surface residue only.
* dynamic execution reach zero is deferred to a later migration execution phase unless a separate staging projected-copy reach analysis method is approved.
* this phase may report `dynamic_execution_reach_deferred: true`, but it must not claim dynamic reach count 0.
* cutover preconditions must require reopening dynamic execution reach validation in a later migration execution plan or approved projected-copy reach analysis.

Validation:

* migration matrix row classification complete.
* migration matrix count reconciliation PASS:
  * matrix `change_required` count == 311
  * matrix `change_forbidden` count == 27558
* ambiguous rows count 0 or explicit blocker list exists.
* forbidden changes count 0.
* dry-run writes no files.
* `consumer_hash_diff.changed_count == 0`.
* current hard gate rows assigned.
* historical / diagnostic / docs-only rows preserved.
* projected static current-surface residue is 0 for PASS; otherwise emit an explicit blocker state.
* dynamic reach zero is not claimed by this dry-run.

---

### Change 10 - Phase 9 Validator / Test / Tool Contract Update Plan

Purpose:

vNext route에 필요한 validator / test / tool 변경 목록을 current route와 분리한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase9/validator_test_tool_contract.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase9/current_route_regression_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase9/vnext_route_validation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase9/tool_change_list.md`

Implementation Notes:

* current route and vNext route remain separate.
* historical / diagnostic route must not be silently folded into current blocker state.
* default current contract route remains:

```powershell
python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
```

* default pytest route remains current route plus root active pytest coverage unless a separate test-contract update changes it:

```powershell
python -B -m pytest -q
```

* package validation is artifact integrity check only and is not release readiness:

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean -Zip
```

* guard token validators remain separate hard guards for current vocabulary / forbidden surface consumption.
* any new vNext validator must reject circular validation.

Validation:

* current route PASS.
* vNext authority route PASS or route contract sealed as blocked.
* historical / diagnostic route separation maintained.
* circular validation absence PASS.
* legacy active/silent current-surface guard PASS.
* Layer4 unauthorized consumption guard PASS.

---

### Change 11 - Phase 10 Cutover Preconditions / Rollback Boundary

Purpose:

후속 cutover가 가능하려면 어떤 evidence가 필요하고 어떤 상태에서는 cutover가 금지되는지 봉인한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase10/cutover_preconditions.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase10/rollback_boundary.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase10/protected_surface_hashes.after.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase10/protected_surface_hash_diff.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase10/protected_surface_no_mutation_verdict.json`

Implementation Notes:

* this execution plan is staging-only.
* `cutover_preconditions.md` is subordinate to `docs/dvf_3_3_vnext_cutover_contract.md`.
* if `cutover_preconditions.md` conflicts with the sealed cutover contract, the sealed cutover contract prevails.
* rollback for this plan is staging artifact discard.
* live runtime rollback snapshot / restore command is not part of this plan.
* future cutover requires separate approval and protected live snapshot before mutation.
* cutover forbidden states include missing source manifest, failed facts / decisions validation, failed rendered determinism, failed bridge / chunk parity, unexplained delta, failed migration dry-run, deferred dynamic execution reach validation, forbidden row touch, current route regression, missing ledger reflection.
* because Phase 8 defers dynamic reach zero, a later migration execution plan or approved projected-copy reach analysis must close that deferral before cutover.
* old deployable runtime chunks stay current until single-authority switch.
* final protected surface hashes are captured after all staging execution.
* `protected_surface_hash_diff.changed_count == 0` is required for any PASS closeout.
* if protected surface mutation is detected, closeout state is `failed_protected_surface_mutation`.

Validation:

* source manifest validation PASS listed as cutover precondition.
* facts / decisions validation PASS listed as cutover precondition.
* rendered determinism PASS listed as cutover precondition.
* bridge / chunk validation PASS listed as cutover precondition.
* unexplained delta 0 listed as cutover precondition.
* migration dry-run PASS listed as cutover precondition.
* dynamic execution reach validation closed before cutover.
* staging rollback rule documented.
* protected surface after hashes exist.
* protected surface diff exists.
* protected surface no-mutation verdict PASS.
* `protected_surface_hash_diff.changed_count == 0`.
* no future live restore command is presented as current execution command.

---

### Change 12 - Phase 11 Ledger Reflection Packet

Purpose:

후속 review / ledger update가 소비할 staging-only reflection packet을 준비한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase11/ledger_update_packet.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase11/proposed_decisions_entry.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase11/proposed_architecture_patch.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase11/proposed_roadmap_patch.md`

Implementation Notes:

* packet records plan status as one of:
  * `implementation_plan_sealed_for_execution`
  * `staging_evidence_produced_for_adversarial_review`
  * `blocked_tooling_unverified`
  * `partial_blocked_some_phases_incomplete`
  * `failed_protected_surface_mutation`
* packet does not mutate `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md`.
* proposed DECISIONS / ARCHITECTURE / ROADMAP patches are non-binding draft output.
* packet must not claim baseline identity sealing unless cutover evidence exists.
* packet must not claim runtime cutover or release readiness.
* evidence paths, counts, hashes, and blocked states are trace anchors only.

Validation:

* packet does not claim baseline creation unless actual evidence exists.
* packet does not claim runtime cutover.
* packet does not claim release readiness.
* evidence paths are traceable.
* non-decision boundary preserved.
* canon docs remain unchanged by this phase.

---

## 7. Validation Plan

### Automated Validation

Plan-document validation:

* template section presence check against `docs/PLAN_TEMPLATE.md`
* `PLAN_TEMPLATE.md` existence and sha256 anchor check
* synthesis input and review input non-authority anchor check
* command contract completeness check for every phase
* phase-local pre-flight output path check for every phase
* Phase 0 bootstrap artifact writer command check
* exact input / output path presence check for every phase
* generation / validation command presence check for every phase
* allowed writes / protected writes / blocked state presence check for every phase
* obsolete no-code-change claim absence check
* forbidden claim scan
* no live path mutation claim scan
* no current authority / release readiness overclaim scan
* path accounting check for staging-only generated artifacts

Execution validation, performed only during the follow-up execution of this plan:

* source manifest schema validation
* source input attempt order validation
* source blocked state taxonomy validation
* duplicate source key validation
* runtime-derived seed non-authority validation
* output path pre-flight abort guard validation before each generation / export command
* guard negative self-test validation
* guard halt semantics validation
* protected surface before / after / diff validation
* `protected_surface_hash_diff.changed_count == 0` gate
* facts schema validation
* decisions schema validation
* facts / decisions determinism hash validation
* compose profile / body_plan binding validation
* rendered schema validation
* style-baseline conformance validation where applicable
* rendered determinism validation
* rendered to bridge parity validation
* bridge to chunk parity validation
* isolated staging Lua load harness validation
* live module leak validation
* chunk manifest / chunk file consistency validation
* source-to-runtime self-consistency validation
* self-consistency known-bad fixture FAIL validation
* predecessor-successor delta classification validation
* delta classifier unexplained-delta fixture FAIL validation
* explained delta traceability validation
* explained delta count / ratio validation
* unexplained delta count gate
* consumer migration matrix classification validation
* consumer migration dry-run no-mutation validation
* dry-run independent before / after consumer-file hash diff validation
* tooling closure state enum validation
* projected static current-surface residue validation
* current route regression validation
* guard token validation

Known current route command:

```powershell
python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
```

Known default pytest route:

```powershell
python -B -m pytest -q
```

Known package integrity route, not release readiness:

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean -Zip
```

Suggested guard routes:

```powershell
python -B Iris\build\description\v2\tools\validate_legacy_active_silent_current_surface_guard.py
python -B Iris\build\description\v2\tools\validate_layer4_absorption_current_surface_guard.py
```

### Manual Validation

* authority vocabulary review
* source / runtime role separation review
* `vNext-CAB` label and actual sealed baseline identity separation review
* runtime-derived seed provenance review
* command-surface honesty review
* Phase 0 bootstrap ordering review
* protected surface set review
* output path pre-flight guard review
* guard halt semantics review
* tooling closure enum review
* new safety / judgment tool behavioral self-test review
* staging output path review
* isolated Lua load harness review
* consumer migration matrix review
* dynamic execution reach deferral review
* delta classification review
* delta traceability review
* `cutover_preconditions.md` subordinate-status review
* ledger packet claim boundary review
* rollback boundary review

### Validation Limits

This plan will not perform or claim:

* runtime cutover validation
* manual in-game validation
* Workshop validation
* B42 validation
* release validation
* long-session runtime validation
* multiplayer validation
* external ecosystem compatibility sweep
* Browser / Wiki / Tooltip behavior validation
* semantic quality completion validation
* Layer4 / ACQ_DOMINANT / Acquisition Lexical reopen validation
* predecessor byte-level full recovery validation

---

## 8. Risk Surface Touch

### Authority Surface

Staging candidate authority only.

This plan may produce source-to-runtime successor evidence for review. It does not grant current authority to any successor artifact.

### Runtime Behavior Surface

None intended.

Live runtime Lua files and public require paths must remain unchanged. Staging Lua candidates are not deployed.

### Compatibility Surface

Dry-run only.

Consumer migration matrix may identify future changes, but actual consumer mutation is out of scope.

### Sealed Artifact Surface

Additive plan document plus staging artifacts only.

Existing sealed docs and runtime payloads are not directly modified by this plan.

### Public-Facing Output Surface

None.

No Browser, Wiki, Tooltip, README, Workshop, release note, or package-facing output is changed.

---

## 9. Risk Analysis

### Architecture Risk

* Staging evidence may be overread as sealed baseline identity.
* `vNext-CAB` may be mistaken for actual current baseline identity.
* Runtime chunks may be treated as source authority.
* Runtime-derived seed may be treated as recovered source.
* `body_plan` may be promoted into a second authority.
* Partial outputs may be promoted independently.

### Runtime Risk

* Export tooling defaults may write live Lua paths if explicit staging args are omitted.
* Guard tooling may report a protected path without halting execution if halt semantics are not enforced.
* Staged chunk manifest may be copied into runtime path before cutover.
* Old and successor chunks may coexist as current deployable authorities.
* Package validation may be overread as deployment readiness.

### Compatibility Risk

* Consumer migration dry-run may become accidental mutation.
* Historical / diagnostic rows may be edited as if current hard gates.
* Numeric replacement may be used instead of authority-role migration.
* `active / silent` historical references may be incorrectly treated as repo-wide delete targets.

### Regression Risk

* Current route tests may be contaminated with vNext staging outputs.
* Phase-local write policy may be violated if pre-flight reports are written to the wrong phase directory.
* New validator existence may be mistaken for validator correctness without known-bad fixture tests.
* Rendered validators may back-propagate decisions into upstream generation.
* Delta taxonomy may hide unexplained drift.
* Guard token validators may be weakened to pass staging output.
* Core docs may be updated with staging claims before review.

---

## 10. Rollback Plan

This execution plan is staging-first and no-cutover.

Rollback rules:

* If Phase 0 fails, stop and keep `blocked_tooling_unverified`.
* If any phase fails before live mutation, discard the phase staging directory.
* If generated artifacts are incomplete, mark the phase as blocked and do not promote partial outputs.
* If protected live surface hashes change unexpectedly, stop immediately and mark closeout as `failed_protected_surface_mutation`.
* If protected surface mutation is detected:
  * identify the changed protected files from `protected_surface_hash_diff.json`
  * do not continue generation / export / validation
  * restore named protected files only through explicit VCS restore or another user-approved recovery procedure
  * rerun protected surface after/diff validation
  * keep the failed mutation report as evidence
* If a tool writes live paths because explicit staging paths were omitted, treat it as execution failure and do not continue.
* If consumer migration dry-run mutates files, revert only those dry-run mutations after identifying them, then mark the dry-run tooling unsafe.
* If ledger packet overclaims cutover or readiness, rewrite the packet before review.
* If actual cutover is needed later, open a separate cutover plan with live snapshot / restore procedure.

For this plan, normal rollback is deleting or ignoring:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/`

The current runtime chunks remain the deployable authority until a separate approved single-authority cutover.

---

## 11. Governance Constraints

* `Philosophy.md` compliance is mandatory.
* Iris runtime remains render-only and must not compose, repair, validate source, judge semantic quality, or decide publish policy.
* Runtime / build-time separation must remain intact.
* All vNext generation is offline.
* A direction-only plan is not a valid closeout for this problem.
* `implementation_plan_sealed_for_execution` requires exact input paths, output paths, generation commands, validation commands, consumer migration scope, failure conditions, rollback conditions, and blocked states.
* Change 0 implements and runs vNext-specific staging tooling; it must not modify existing tools or default current-route behavior without separate approval.
* Every generation / export command requires resolved output path pre-flight guard.
* Pre-flight guard output must be phase-local as `phaseN/output_path_preflight_guard.json`.
* Any resolved output path inside the protected surface set must abort before write.
* Guard failure is not report-only; wrapper execution refuses to continue and orchestration halts on non-zero.
* New safety / judgment tools must prove failure behavior with known-bad fixtures before their PASS/FAIL output can support follow-up execution.
* Protected surface before / after / diff evidence is mandatory for PASS closeout.
* `protected_surface_hash_diff.changed_count` must be 0 for PASS closeout.
* Source authority and runtime payload authority must remain distinct.
* Runtime chunks are comparison reference, not source authority.
* Runtime-derived seed is non-authority bootstrap only.
* Seed-derived artifacts require provenance.
* `body_plan` remains compose profile implementation surface / alias label, not second authority.
* `active / silent` remains historical / diagnostic / import alias vocabulary only.
* Current runtime vocabulary remains `adopted / unadopted`.
* `adopted / unadopted` must not become quality, publish, deletion, or suppression vocabulary.
* Browser / Wiki / Tooltip must not expose quality state as badge, sorting, filtering, hiding, recommendation, trust, or confidence display.
* 2105 audit output is migration input, not migration approval.
* Consumer migration must be authority-role migration, not numeric or vocabulary replacement.
* Phase 8 dry-run may claim projected static residue only; dynamic execution reach zero requires a separate migration execution phase or approved projected-copy reach method.
* Old chunks and successor chunks cannot both be current.
* Rendered-only, bridge-only, chunk-generation-only, smoke-only, migration-draft-only, or reflection-only output cannot become current authority.
* FAIL-LOUD must be preserved for source absence, basis-unavailable, parity failure, unexplained delta, forbidden row touch, and blocked tooling.
* `cutover_preconditions.md` is subordinate to `docs/dvf_3_3_vnext_cutover_contract.md`; the sealed cutover contract prevails on conflict.
* External synthesis and review inputs are non-authority references unless separately promoted by an approved docs-canon step.
* DECISIONS / ARCHITECTURE / ROADMAP mutation requires a separate approved reflection application.
* Release readiness, Workshop readiness, B42 readiness, manual in-game validation, runtime rollout, package deployment, and public exposure are not implied.

---

## 12. Expected Closeout State

Expected plan closeout: `implementation_plan_sealed_for_execution`

Acceptable plan blocked closeout: `blocked_tooling_unverified`

Follow-up execution terminal closeouts:

* `staging_evidence_produced_for_adversarial_review`
* `partial_blocked_some_phases_incomplete`
* `failed_protected_surface_mutation`

`implementation_plan_sealed_for_execution` means:

* every phase has explicit authority inputs, exact input paths, exact output paths, generation command, validation command, allowed writes, protected writes, success criteria, and blocked state.
* required wrapper / validator / guard tool paths are listed as implementation tasks or verified existing commands.
* Phase 0 bootstrap writer command is defined.
* every phase has phase-local `output_path_preflight_guard.json`.
* guard negative self-test and safety / judgment tool behavioral self-tests are required before follow-up execution.
* `tooling_closure_report.json` uses the required tool state enum.
* source manifest schema, runtime seed handling, facts / decisions generation, profile / overlay handling, rendered generation, runtime export, consumer migration, validator / test strategy, ledger packet, rollback, and blocked conditions are all fixed in this plan.
* implementation can begin by executing Change 0 and then following the phase command contract.
* this closeout does not mean staging evidence has already been produced.

`staging_evidence_produced_for_adversarial_review` means:

* source manifest candidate, facts, decisions, compose binding, rendered output, Lua bridge, chunk candidates, isolated Lua load harness report, self-consistency report, delta classification, consumer migration dry-run, validator route report, cutover precondition note, rollback boundary, protected surface after/diff verdict, and ledger packet exist under isolated staging.
* protected live runtime, runtime facade / loader if applicable, live data, live output, and canon docs remain unchanged.
* `protected_surface_hash_diff.changed_count == 0`.
* live module leak count is 0.
* unexplained delta is 0.
* forbidden consumer mutation is 0.
* projected static current-surface residue is 0.
* current route remains green.
* generated evidence is ready for review.

It does not mean:

* successor current authority exists.
* actual sealed baseline identity is approved.
* runtime cutover happened.
* consumer migration executed.
* package or release readiness exists.
* Workshop or B42 readiness exists.
* manual in-game QA passed.
* public Browser / Wiki / Tooltip behavior changed.

`blocked_tooling_unverified` means:

* Phase 0 found that required generation, export, validation, or dry-run commands cannot be executed safely into staging with the current tool surface.
* required evidence is limited to Phase 0 input readpoint, command surface inventory, protected before / after / diff if any command was probed, and `tooling_unverified.md`.
* Phase 1-11 output existence is not required.
* no guessed command or live-path default was used to manufacture evidence.
* follow-up work must first add or verify staging-safe tooling before reopening execution.

`partial_blocked_some_phases_incomplete` means:

* Phase 0 passed and at least one later phase produced valid staging evidence.
* one or more later phases blocked with an allowed blocked state.
* partial evidence is not review-ready successor authority evidence.
* this warning sentence must remain in any closeout or ledger packet that mentions `partial_blocked_some_phases_incomplete`.
* partial output must not be promoted to current authority, sealed baseline identity, or cutover input without a follow-up completion plan.

`failed_protected_surface_mutation` means:

* protected surface after/diff detected a changed protected file or a command wrote to a protected output path.
* execution stops immediately.
* changed protected files require explicit VCS restore or another user-approved recovery procedure.
* this state cannot be converted into PASS by deleting the report; recovery and rerun evidence must be preserved.
