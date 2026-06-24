# Implementation Plan

> Status: proposed current-authority implementation and 2105 consumer migration plan / WARN review revisions and codebase feasibility amendments applied
> Roadmap input: `C:/Users/MW/.codex/attachments/7c6c3a19-5422-4a36-9782-2a9eb09c7c9e/pasted-text.txt` / sha256 `8512A5526A089574C7CA49DE8FA8C3ED7CA126E0872A27BCC60C3DD99FEA01C5` / non-authority synthesis reference
> Review input: `C:/Users/MW/.codex/attachments/cc6b9950-272a-4dd9-b470-9e31cc6c35f0/pasted-text.txt` / sha256 `4B95E30122FE1C9CB2B27C375A8F6E7F352BE7E9E54B90719E45EBC79CD69C36` / non-authority review reference
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Parent definition plan: `docs/dvf_3_3_vnext_current_authority_plan.md`
> Parent execution plan: `docs/dvf_3_3_vnext_execution_plan.md`
> Handoff input: `docs/dvf_3_3_vnext_current_authority_handoff_packet.md`
> Top authority: `docs/Philosophy.md`

## 1. Objective

DVF 3-3 vNext successor candidate를 live current authority baseline으로 실제 승격하고, frozen `2105 / 2084 / 21` predecessor를 소비하던 validator / test / tool / consumer surface를 baseline-manifest-driven authority role로 이관한다.

이 계획은 frozen 2105 byte-level recovery가 아니다. 목표는 다음 current authority chain을 같은 successor baseline identity로 봉인하는 것이다.

```text
source manifest
-> facts
-> decisions
-> compose profile + body_plan
-> rendered output
-> Lua bridge
-> chunk manifest + chunk files
-> validator / test / tool / consumer expectations
-> DECISIONS / ARCHITECTURE / ROADMAP additive ledger reflection
```

이 계획의 실행 완료가 의미하는 것은 successor current authority baseline cutover와 2105 consumer migration completion이다. 이 계획의 실행 완료가 release readiness, package release readiness, Workshop readiness, B42 readiness, manual in-game validation, semantic quality completion, or public-facing text quality acceptance를 의미하지 않는다.

---

## 2. Scope

이 계획은 `docs/dvf_3_3_vnext_execution_plan.md`와 후속 regeneration / correction / current-route guard evidence가 이미 만든 staging candidate를 live current authority surface로 승격하는 후속 execution plan이다.

포함 범위:

* cutover scope lock, input freeze, evidence freshness re-verification
* successor baseline identity candidate pre-seal
* current source surface promotion
* current rendered authority regeneration
* Lua bridge / runtime chunk fresh export
* live runtime deployable authority single-authority switch
* 2105 audit 기반 actual consumer migration
* validator / test / tool re-baselining
* current route / package route / export route / compose route validation
* predecessor 2105 / 6-entry fixture / staging evidence reseal
* pre-ledger final end-to-end chain validation
* independent adversarial review before ledger seal
* DECISIONS / ARCHITECTURE / ROADMAP additive ledger adoption after final-chain PASS
* post-ledger closeout, claim boundary, and rollback recipe seal

Primary execution evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_cutover/`

Plan artifact:

* `docs/dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_plan.md`

### Explicitly Out Of Scope

* frozen 2105 byte-level recovery
* predecessor runtime byte-for-byte equivalence
* `2105 / 2084 / 21` 숫자 기계 치환
* historical / diagnostic / docs-only row를 current migration 대상으로 승격
* `active / silent` current vocabulary 재도입
* `adopted / unadopted` quality / publish / deletion / suppression 의미 부여
* monolith runtime authority 복귀
* runtime Lua JSON parser 도입
* runtime Lua compose / repair / source validation 도입
* Browser / Wiki / Tooltip UI 정책 변경
* quality_state / publish_state UI exposure
* Layer4 / ACQ_DOMINANT / Acquisition Lexical reopen
* public release / Workshop / package release readiness 선언
* manual in-game QA completion 선언
* multiplayer validation
* long-session runtime validation
* external mod ecosystem compatibility sweep
* unrelated refactor
* architecture redesign outside the DVF 3-3 authority chain

---

## 3. Non-Goals

* frozen 2105를 복구된 source로 표현하지 않는다.
* runtime chunks를 source authority로 승격하지 않는다.
* runtime-derived seed를 source authority, fact authority, decision authority, rendered authority로 소비하지 않는다.
* current 6-entry facts / decisions / rendered fixture를 full current authority input으로 남기지 않는다.
* staging rendered / staging Lua / staging chunks를 검증 없이 current path로 복사하지 않는다.
* source-to-rendered chain 없이 runtime chunks만 교체하지 않는다.
* rendered-only, bridge-only, chunk-generation-only, migration-draft-only output을 current authority로 승격하지 않는다.
* old chunks와 successor chunks를 동시에 current deployable authority로 두지 않는다.
* consumer migration을 hardcoded count replacement로 처리하지 않는다.
* docs ledger update만으로 cutover 완료를 주장하지 않는다.
* package route PASS를 release readiness로 읽지 않는다.
* final cutover contract를 public-facing text quality acceptance로 읽지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 기준이다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 2026-06-17 current readpoint를 따른다.
* `docs/dvf_3_3_vnext_current_authority_plan.md`는 definition-only governance plan으로 봉인되어 있다.
* `docs/dvf_3_3_vnext_current_authority_roadmap.md`는 definition-only successor roadmap으로 봉인되어 있다.
* `docs/dvf_3_3_vnext_execution_plan.md`는 staging-only execution contract이며, live cutover approval이 아니다.
* `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/phase11/final_execution_contract_report.json`은 `status=PASS` readpoint로 존재한다.
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase7/final_contract_report.json`은 `status=PASS` and `closeout_state=complete` readpoint로 존재한다.
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/runtime_parity_report.json`은 successor-predecessor delta input이다.
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/final_delta_disposition_guard_contract_report.json`은 corrected cutover input predicate다.
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase11/final_rejected_delta_correction_reparity_report.json`은 `cutover_input_usable=true`, `parent_problem_unlock=true`, `not_cutover_authorization=true` readpoint로 존재한다.
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase7/final_current_route_guard_integration_report.json`은 current route guard integration input이다.
* `Iris/_docs/round3/current_route_required_validations.json` remains the current-route required validation manifest and must require corrected evidence freshness.
* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/` is read-only migration input.
* current runtime deployable authority before this plan is still the predecessor `IrisLayer3DataChunks.lua + IrisLayer3DataChunks/*.lua` bundle.
* source authority and runtime deployable authority are distinct and must be sealed separately.

Plan-local resolution of roadmap conflict items:

* Post-ledger failure is handled by additive correction / successor round, not silent un-seal. Any prior readpoint restoration after ledger seal requires a new additive correction or rollback plan.
* Final seal uses the extended hash set where available: source manifest, facts, decisions, sealed overlay support metadata, compose profile/body_plan binding, rendered hash, Lua bridge report, chunk manifest, chunk files, consumer migration result, and ledger reflection.
* Public-facing surface is described as payload text replacement through sealed Layer3 data; UI policy, quality exposure, recommendation, sorting, filtering, and release claims remain unchanged.
* Final end-to-end chain validation PASS is required before independent review and before ledger final seal.
* Independent adversarial review is a required gate before ledger final seal, and it must be performed by a reviewer independent from the plan author and roadmap synthesis reference.
* Phase 1 is candidate / pre-seal only. Final current baseline identity is sealed in the ledger adoption phase after all evidence exists.
* Source promotion uses Option A: canonical current paths are replaced with successor full source files. Redirect mode is not allowed in this plan.
* The cutover now explicitly acknowledges the body-plan v2 minimal overlay support surface discovered in vNext staging. It must be regenerated fresh from successor current facts, sealed as compose support metadata, linked from the current input manifest, and consumed through an explicit compose `--overlay-path`. It is not source authority and must not become a second current authority.

---

## 5. Repository Areas Affected

### Code

Current source / output / runtime surfaces expected to change during execution:

* `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
* `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
* `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
* `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`
* `Iris/build/description/v2/output/dvf_3_3_rendered.json`
* `Iris/build/description/v2/output/style_normalization_changes.jsonl`
* `Iris/build/description/v2/output/compose_requeue_candidates.jsonl`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`

Consumer / validator / tool surfaces expected to change only where 2105 audit and migration matrix classify them as actual current hard gate consumers:

* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/_docs/round3/round3_run_contract_tests.py`
* `Iris/build/description/v2/tests/*.py`
* `Iris/build/description/v2/tools/**/*.py`
* `Iris/tools/package_iris.ps1`, only if package forbidden scan criteria require successor boundary alignment

Preserved surfaces:

* `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua` must not re-enter as current runtime authority.
* `media/lua/shared/Iris/IrisDvfBridgeData.lua` must not re-enter as current bridge fallback or package allowlist.

### Docs

Direct plan artifact:

* `docs/dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_plan.md`

Read-only authority inputs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/dvf_3_3_vnext_current_authority_plan.md`
* `docs/dvf_3_3_vnext_current_authority_roadmap.md`
* `docs/dvf_3_3_vnext_execution_plan.md`
* `docs/dvf_3_3_vnext_regeneration_parity_plan.md`
* `docs/dvf_3_3_vnext_delta_disposition_policy.md`
* `docs/dvf_3_3_vnext_delta_guard_current_route_integration_plan.md`
* `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_plan.md`
* `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_closeout.md`
* `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_ledger_packet.md`
* `docs/dvf_3_3_vnext_current_authority_handoff_packet.md`

Canon docs mutated only in Phase 9 after evidence and review gates pass:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Closeout / ledger artifacts produced by this plan:

* `docs/dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_closeout.md`
* `docs/dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_ledger_packet.md`

### Config

No project configuration change is planned by default.

If validation reveals that test discovery or package route config still encodes predecessor current authority expectations, the affected config file must be listed in the Phase 5 consumer migration execution ledger before mutation.

### Generated Artifacts

All execution evidence must be written under:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_cutover/`

Expected artifact families:

* `phase0/cutover_scope_lock.md`
* `phase0/cutover_input_manifest.json`
* `phase0/evidence_freshness_report.json`
* `phase0/command_surface_mapping.json`
* `phase0/mutation_allowlist.json`
* `phase0/mutation_denylist.json`
* `phase0/protected_surface_hashes.before.json`
* `phase0/rollback_snapshot_manifest.json`
* `phase0/current_surface_vcs_representation_report.json`
* `phase1/successor_baseline_manifest.candidate.json`
* `phase1/baseline_identity_definition_report.json`
* `phase1/overlay_support_surface_disposition.json`
* `phase1/overlay_support_surface_manifest.json`
* `phase1/accepted_overlay_support_surface.jsonl`
* `phase1/seal_precondition_ledger.json`
* `phase2/source_promotion_report.json`
* `phase2/source_promotion_selected_path_report.json`
* `phase2/source_manifest_fingerprint.json`
* `phase2/facts_decisions_schema_validation.json`
* `phase2/fixture_disposition_report.json`
* `phase3/rendered_regeneration_report.json`
* `phase3/rendered_determinism_report.json`
* `phase3/rendered_hash_seal.json`
* `phase3/source_to_rendered_consistency_report.json`
* `phase3/protected_side_output_semantics_report.json`
* `phase3/publish_state_no_direct_emit_report.json`
* `phase4/lua_bridge_export_report.json`
* `phase4/live_runtime_cutover_tooling_verdict.json`
* `phase4/runtime_chunk_cutover_execution_plan.json`
* `phase4/runtime_switch_precondition_verdict.json`
* `phase4/chunk_manifest_fingerprint.json`
* `phase4/chunk_file_hash_index.json`
* `phase4/runtime_atomic_replace_report.json`
* `phase4/runtime_single_authority_cutover_report.json`
* `phase4/runtime_restore_probe_report.json`
* `phase4/predecessor_runtime_snapshot_report.json`
* `phase5/consumer_migration_executor_verdict.json`
* `phase5/consumer_migration_execution_ledger.json`
* `phase5/consumer_migration_actual_change_manifest.json`
* `phase5/consumer_migration_actual_diff_report.json`
* `phase5/executing_consumer_disposition_reconciliation.json`
* `phase5/hardcoded_current_readpoint_removal_report.json`
* `phase5/forbidden_change_no_mutation_report.json`
* `phase5/manifest_driven_consumer_validation_report.json`
* `phase6/current_route_regression_report.json`
* `phase6/package_route_report.json`
* `phase6/export_route_report.json`
* `phase6/compose_route_report.json`
* `phase6/route_owner_equivalence_report.json`
* `phase6/validation_summary.md`
* `phase7/predecessor_preservation_report.json`
* `phase7/fixture_disposition_report.json`
* `phase7/staging_evidence_disposition_report.json`
* `phase7/current_looking_artifact_scan_report.json`
* `phase8/pre_ledger_final_chain_validation_report.json`
* `phase8/pre_ledger_atomic_restore_readiness_report.json`
* `phase8/independent_adversarial_review_report.md`
* `phase9/final_baseline_identity_report.json`
* `phase9/decisions_update_packet.md`
* `phase9/architecture_update_packet.md`
* `phase9/roadmap_update_packet.md`
* `phase9/ledger_consistency_check.json`
* `phase10/final_current_authority_cutover_report.json`
* `phase10/final_validation_summary.md`
* `phase10/final_claim_boundary_statement.md`
* `phase10/protected_surface_hashes.after.json`
* `phase10/protected_surface_hash_diff.json`
* `phase10/rollback_restoration_recipe.md`

---

## 6. Planned Changes

### Phase 0 - Cutover Scope Lock / Input Freeze / Re-verification

Purpose:

Actual cutover가 참조할 corrected evidence, mutation boundary, command surface, rollback snapshot을 잠근다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_cutover/phase0/*`
* read-only input evidence listed in Section 4

Implementation Notes:

* corrected re-parity, corrected disposition, current-route guard integration, and 2105 audit evidence freshness를 재확인한다.
* old blocked disposition evidence와 corrected evidence를 혼용하지 않는다.
* `cutover_input_usable=true` and `parent_problem_unlock=true` are candidate predicates, not cutover authorization.
* mutation allowlist and denylist must be materialized before any write.
* `command_surface_mapping.json` maps every automated validation family in Section 7 to an actual command or tool; any missing required tool blocks execution.
* each `command_surface_mapping.json` row must include `validation_family`, `concrete_command_or_tool`, `expected_artifact`, and `blocking_condition`.
* command mapping must include a fresh-overlay generation / validation command, a current compose command with explicit sealed overlay path, a live runtime chunk cutover command or approved atomic replacement tool, a runtime restore probe command, and an actual consumer migration executor. If any of these are absent, Phase 0 closes as `blocked_required_execution_tool_missing`.
* the existing Lua bridge exporter may be mapped only for quarantined staging bundle generation unless it is changed and revalidated to allow current live chunk writes. It must not be mapped as the direct live runtime cutover tool while its protected-path guard refuses current chunk manifest and chunk directory targets.
* the existing consumer migration dry-run tool may be mapped as a precondition validator only. It must not be mapped as the actual Phase 5 migration executor because dry-run evidence with `mutation_performed=false` cannot satisfy current consumer migration completion.
* `current_surface_vcs_representation_report.json` classifies every current source / output / runtime / consumer mutation target as `tracked_required`, `ignored_reproducible`, `generated_evidence`, or `runtime_deployable`.
* all current source / output / runtime / consumer / ledger mutation candidates must have predecessor snapshot and SHA256 before mutation.
* post-ledger rollback semantics, final seal evidence granularity, public-facing output wording, independent review gate, and Phase 1 pre-seal wording are frozen according to Section 4 before execution proceeds.

Validation:

* required input artifact existence check
* corrected evidence freshness check
* stale blocked evidence exclusion check
* mutation allowlist / denylist validation
* command surface mapping completeness check
* VCS representation / tracking status validation
* protected surface before hash capture
* rollback snapshot manifest completeness check
* no cutover authorization claim scan

---

### Phase 1 - Successor Baseline Identity Candidate / Pre-seal

Purpose:

successor baseline identity candidate를 final seal 전 evidence slots와 함께 정의한다.

Files:

* `phase1/successor_baseline_manifest.candidate.json`
* `phase1/baseline_identity_definition_report.json`
* `phase1/source_lineage_note.md`
* `phase1/predecessor_relation_note.md`
* `phase1/overlay_support_surface_disposition.json`
* `phase1/overlay_support_surface_manifest.json`
* `phase1/accepted_overlay_support_surface.jsonl`
* `phase1/seal_precondition_ledger.json`

Implementation Notes:

* Phase 1 output is candidate / pre-seal only.
* identity is name-first, count-later. Count `2105` is not the identity.
* source manifest fingerprint, facts hash, decisions hash, profile/body_plan fingerprint, rendered hash, Lua bridge report hash, chunk manifest fingerprint, chunk file hash index, consumer migration result, and ledger reflection slots are defined.
* `overlay_support_surface_disposition.json` must state `sealed_compose_support_surface`, not `no_standalone_overlay_current_surface`.
* `accepted_overlay_support_surface.jsonl` is regenerated from successor current facts during this execution and is promoted to `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl` only as compose support metadata.
* `overlay_support_surface_manifest.json` must include source facts hash, generated overlay hash, row count, role label `compose_support_not_source_authority`, input manifest linkage, rendered meta linkage, stale rejection check, and not-second-authority guard.
* Direct consumption of prior staging `phase3/accepted_overlay.jsonl` or legacy body-role fixture overlay is forbidden for current rendered regeneration. If the fresh support artifact cannot be generated and sealed, Phase 1 closes as `blocked_overlay_surface_unsealed`.
* corrected staging lineage is restated as successor input lineage, not as staging direct promotion.
* runtime-derived seed and predecessor chunks remain non-source authority.

Validation:

* baseline manifest schema validation
* key set validation
* source lineage validation
* no runtime-derived-source-authority violation scan
* no fixture-as-source-authority violation scan
* fingerprint determinism check
* overlay / support surface disposition check
* fresh overlay support artifact hash and rendered meta linkage check
* stale staging overlay rejection check
* precondition slot completeness check

---

### Phase 2 - Current Source Surface Promotion

Purpose:

current facts / decisions / input manifest를 successor full source authority와 일치시키고 6-entry fixture를 current authority input에서 분리한다.

Files:

* `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
* `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
* `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
* `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`
* `phase2/source_promotion_report.json`
* `phase2/source_promotion_selected_path_report.json`
* `phase2/fixture_disposition_report.json`

Implementation Notes:

* canonical current path replacement is the only approved source promotion mode.
* `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`, `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`, and `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl` are replaced with successor full source files as one baseline unit.
* redirect to another full authority path is not allowed by this plan.
* compose profile, body_plan binding, and sealed overlay support metadata are connected to the current baseline.
* `Iris/build/description/v2/data/dvf_3_3_input_manifest.json` must list `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl` with role `compose_support_not_source_authority` and the Phase 1 fingerprint.
* current compose must pass an explicit `--overlay-path Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl` or update the guarded default path to the same sealed support artifact. Falling back to the existing staging default overlay path is forbidden.
* 6-entry fixture is preserved only as fixture / test / historical / diagnostic non-authority where needed.
* legacy `active / silent` trace remains predecessor metadata only.
* no blanket `silent -> active` remap is allowed.

Validation:

* full source count validation
* facts / decisions schema validation
* current path no-fixture validation
* selected source promotion path validation
* legacy vocabulary current-surface guard
* source manifest fingerprint validation
* deterministic reload validation
* explicit current overlay path validation
* input manifest overlay support linkage validation
* control set and corrected alignment key validation

---

### Phase 3 - Current Rendered Authority Regeneration

Purpose:

current `output/dvf_3_3_rendered.json`을 successor source manifest에서 fresh regeneration한다.

Files:

* `Iris/build/description/v2/output/dvf_3_3_rendered.json`
* `Iris/build/description/v2/output/style_normalization_changes.jsonl`
* `Iris/build/description/v2/output/compose_requeue_candidates.jsonl`
* `phase3/rendered_regeneration_report.json`
* `phase3/rendered_determinism_report.json`
* `phase3/rendered_hash_seal.json`
* `phase3/protected_side_output_semantics_report.json`
* `phase3/publish_state_no_direct_emit_report.json`

Implementation Notes:

* compose route must use `compose_context=current`, `profile_class=v2_current`, and current data input.
* compose route must consume `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl` through an explicit sealed overlay path or a revalidated guarded default pointing to the same file.
* staging rendered files must not be copied directly into current output path.
* rendered meta must record the sealed overlay support path and SHA256. A rendered meta reference to prior staging `phase3/accepted_overlay.jsonl`, legacy body-role fixture overlay, or any unsealed overlay path blocks Phase 3.
* legacy / diagnostic / partial / ambiguous profile must not write current-looking output.
* rendered-only promotion is forbidden; rendered hash must link back to source manifest and decisions.
* protected side outputs follow the closed current-output contract.
* `style_normalization_changes.jsonl` and `compose_requeue_candidates.jsonl` may mutate only as deterministic side outputs of current rendered regeneration; they are not source authority and must be included in mutation allowlist and rollback snapshot.
* successor rendered output must not directly emit `publish_state`; B-branch / policy no-mutation carry-forward remains intact.

Validation:

* compose current write-boundary guard
* rendered schema validation
* rendered warning / hard fail check
* rendered determinism validation
* rendered hash validation
* profile / body_plan binding validation
* sealed overlay support consumption and rendered meta linkage validation
* no staging direct promotion validation
* source-to-rendered consistency report
* protected side-output semantics validation
* publish_state no-direct-emit / no-policy-mutation check

---

### Phase 4 - Lua Bridge / Runtime Chunk Re-export / Single-authority Cutover

Purpose:

successor rendered authority에서 Lua bridge and runtime chunk bundle을 fresh export하고 live deployable runtime authority를 successor chunk bundle로 단일 전환한다.

Files:

* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`
* `phase4/lua_bridge_export_report.json`
* `phase4/live_runtime_cutover_tooling_verdict.json`
* `phase4/runtime_chunk_cutover_execution_plan.json`
* `phase4/runtime_switch_precondition_verdict.json`
* `phase4/chunk_manifest_fingerprint.json`
* `phase4/chunk_file_hash_index.json`
* `phase4/runtime_atomic_replace_report.json`
* `phase4/runtime_single_authority_cutover_report.json`
* `phase4/runtime_restore_probe_report.json`
* `phase4/predecessor_runtime_snapshot_report.json`

Implementation Notes:

* export must read current rendered authority, not staging-only rendered output.
* bridge export and live runtime cutover are two separate operations. The exporter may write only to a quarantined candidate bundle unless its protected-path guard is intentionally changed and validated for current cutover.
* `live_runtime_cutover_tooling_verdict.json` must name the exact cutover command/tool, expected inputs, expected live targets, and rollback probe. If no approved live cutover tool exists, Phase 4 closes as `blocked_runtime_cutover_tool_missing` before any live runtime mutation.
* `runtime_chunk_cutover_execution_plan.json` must describe the atomic unit: predecessor snapshot, candidate manifest, candidate chunk directory, target manifest, target chunk directory, file delete/replace order, extra stale chunk deletion rule, and restore command.
* predecessor chunks are snapshotted before replacement.
* `runtime_switch_precondition_verdict.json` is the single blocking gate for live runtime switch.
* live runtime switch is allowed only when rendered determinism, rendered-to-Lua consistency, Lua syntax, chunk manifest validation, predecessor snapshot, old/new dual-current absence, monolith re-entry absence, stale bridge fallback absence, public require contract, and package forbidden scan preconditions all PASS.
* if the precondition verdict is not PASS, the live switch is not attempted and Phase 4 closes as `blocked_runtime_switch_precondition_failed`.
* live runtime path is switched as one bundle: manifest + all chunk files. Partial copy, manual file-by-file promotion without a report, or leaving extra predecessor chunk files under the current chunk directory is forbidden.
* `runtime_atomic_replace_report.json` must prove the post-switch live target contains exactly the successor chunk manifest plus the successor chunk files referenced by that manifest, with no predecessor-only extras.
* `runtime_restore_probe_report.json` must prove the predecessor runtime bundle can be restored from the Phase 0 / Phase 4 snapshot before ledger seal if any later gate fails.
* old chunks and successor chunks must not both be current.
* monolith output must not be generated or packaged as current runtime authority.
* package allowlist must not reintroduce stale bridge artifact.
* chunk manifest fingerprint is linked into the baseline identity evidence.

Validation:

* rendered-to-Lua bridge consistency validation
* Lua syntax validation
* chunk manifest schema validation
* chunk coverage validation
* chunk file hash index validation
* public require contract validation
* live runtime cutover tool availability validation
* atomic runtime replacement exact-target validation
* runtime restore probe validation
* old/new dual-current absence scan
* monolith re-entry absence scan
* stale bridge fallback absence scan
* package route forbidden scan
* runtime switch precondition verdict PASS

---

### Phase 5 - 2105 Consumer Migration Execution

Purpose:

2105 audit의 migration-required consumers를 hardcoded predecessor current readpoint에서 successor baseline manifest / sealed authority metadata consumption으로 이관한다.

Files:

* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/change_required_index.md`
* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/change_forbidden_index.md`
* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/classified_ledger.jsonl`
* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/executing_consumer_impact.md`
* current validators / tests / tools classified as actual current hard gate consumers
* `phase5/consumer_migration_executor_verdict.json`
* `phase5/consumer_migration_execution_ledger.json`
* `phase5/consumer_migration_actual_change_manifest.json`
* `phase5/consumer_migration_actual_diff_report.json`
* `phase5/executing_consumer_disposition_reconciliation.json`
* `phase5/hardcoded_current_readpoint_removal_report.json`
* `phase5/forbidden_change_no_mutation_report.json`

Implementation Notes:

* migration is authority-role migration, not numeric replacement.
* Phase 5 must use an actual migration executor or an explicitly approved scripted patch process that emits row-level evidence. The dry-run tool is only a precondition and cannot close Phase 5 because it does not mutate files.
* `consumer_migration_executor_verdict.json` must name the command/tool, input matrix, mutation allowlist, expected changed files, and blocking condition. If the executor is missing or cannot emit row-level evidence, Phase 5 closes as `blocked_consumer_migration_executor_missing`.
* accepted change-required rows are applied only when classified as current hard gate consumers.
* historical-reference, diagnostic-only, generated, false-positive, no-op, and change-forbidden rows remain unchanged unless a separate approved correction narrows a row.
* tools and tests should read current baseline identity from manifest / sealed authority metadata where possible.
* `2105` literal is not forbidden by value alone. Manifest-derived successor `entry_count=2105` is allowed when provenance points to sealed baseline metadata.
* hardcoded predecessor readpoint `2105` is forbidden only when it functions as a current authority gate, expectation, fixture authority, or validator threshold independent of sealed baseline metadata.
* `2084 / 21` is predecessor-specific split vocabulary and must not remain as current authority split unless explicitly labeled historical / diagnostic.
* `active / silent` historical references are not repo-wide delete targets.
* `change_forbidden` rows must remain mutation count 0.
* `executing_consumer_disposition_reconciliation.json` reconciles executing-consumer `1062`, change-required `311`, and change-forbidden `27558` counts with row-level dispositions.
* every `consumer_migration_execution_ledger.json` row must include `before_authority_source`, `after_authority_source`, `migration_disposition`, `evidence_anchor`, `hardcoded_literal_removed_or_manifest_derived`, and `change_forbidden_no_mutation`.
* `consumer_migration_actual_change_manifest.json` lists every mutated file, every row-level reason for mutation, and every unchanged row-level disposition. It must distinguish `migrated_to_manifest_authority`, `historical_preserved`, `diagnostic_preserved`, `generated_no_mutation`, `false_positive_no_mutation`, `no_op`, and `blocked`.
* `consumer_migration_actual_diff_report.json` must prove that each actual text change corresponds to an accepted change-required row and no change corresponds to a change-forbidden row.
* `dynamic_execution_reach_deferred=true` from dry-run input is not a completion claim. Phase 5 must either run an executing-consumer route check after mutation or carry an explicit `dynamic_reach_deferred_residual_risk` entry into Phase 8 independent review and Phase 10 claim boundary.

Validation:

* consumer migration executor availability validation
* consumer migration execution report
* actual mutation manifest validation
* actual diff-to-ledger traceability validation
* accepted candidate / required row reconciliation
* change_required all-addressed check
* change_forbidden zero-mutation check
* authority-source-based hardcoded current readpoint scan
* sealed-manifest-derived `2105` allowance check
* predecessor-specific `2084 / 21` split current-surface scan
* no legacy `active / silent` current consumer scan
* manifest-driven consumer behavior check
* executing consumer disposition total reconciliation
* dry-run vs actual migration diff report
* static forbidden current surface hit count == 0
* static unclassified residue count == 0
* dynamic forbidden reach count == 0

---

### Phase 6 - Current Route / Package Route / Export Route / Tool Re-baselining

Purpose:

cutover 후 current route와 package / export / compose route, validators, tests, and tools가 successor baseline 기준으로 fail-loud 통과하는지 검증하고 required validation manifest를 정렬한다.

Files:

* `Iris/_docs/round3/current_route_required_validations.json`
* current route runner and tests affected by migration
* package / export / compose validation reports under `phase6/`

Implementation Notes:

* required validations must consume cutover evidence and corrected evidence freshness.
* stale staging-only PASS must not satisfy live cutover validation.
* package route must not include old chunks and successor chunks together.
* package mixed predecessor/successor scan is owned by Phase 6 for package artifacts; Phase 4 owns live runtime path dual-current prevention.
* current core closure remains 12 modules.
* current-route tooling allowlist cap remains 1.
* historical and diagnostic routes must keep predecessor reference capability.

Validation:

* current route regression
* current route closure enforcement
* required validation manifest success
* v2 unittest discovery
* historical route
* diagnostic route
* package route
* export route
* compose route
* Lua syntax
* static forbidden current surface hit count == 0
* static unclassified residue count == 0
* dynamic forbidden reach count == 0
* route-owner equivalence fingerprint
* protected surface mutation diff matches allowlist

---

### Phase 7 - Historical 2105 / Fixture / Staging Evidence Reseal

Purpose:

cutover 후 predecessor 2105, 6-entry fixture, staging evidence, and old runtime chunks의 non-current 지위를 재봉인한다.

Files:

* `phase7/predecessor_preservation_report.json`
* `phase7/fixture_disposition_report.json`
* `phase7/staging_evidence_disposition_report.json`
* `phase7/historical_diagnostic_reference_index.md`
* `phase7/current_looking_artifact_scan_report.json`

Implementation Notes:

* frozen 2105 is predecessor / comparison reference / migration input historical state.
* old runtime chunks are predecessor runtime snapshot or hash-indexed preservation, not fallback runtime authority.
* 6-entry fixture is non-current.
* staging evidence is not live source of truth after cutover.
* historical Done documents must not be rewritten as current baseline docs.
* current-looking historical artifacts are scanned and dispositioned.

Validation:

* predecessor reference scan
* fixture-as-authority guard
* staging direct promotion guard
* current-looking historical artifact scan
* old chunk fallback scan
* monolith fallback scan
* stale bridge artifact scan

---

### Phase 8 - Pre-ledger Final Chain Validation / Independent Review Gate

Purpose:

ledger seal 전에 live source / rendered / runtime / consumer state가 하나의 successor baseline chain으로 PASS인지 검증하고, 독립 adversarial review를 수행한다.

Files:

* `phase8/pre_ledger_final_chain_validation_report.json`
* `phase8/pre_ledger_atomic_restore_readiness_report.json`
* `phase8/independent_adversarial_review_report.md`

Implementation Notes:

* this phase is the point where final end-to-end chain PASS is established before ledger seal.
* final chain validation connects manifest-to-source, sealed overlay support metadata, source-to-rendered, rendered-to-Lua, Lua-to-runtime chunks, consumer migration, current route, package/export/compose routes, and protected-surface diff.
* `pre_ledger_atomic_restore_readiness_report.json` verifies that source facts / decisions / input manifest / overlay support artifact, rendered output + protected side outputs, runtime chunk manifest + chunk files, migrated consumers, and required validation manifest can be restored atomically from Phase 0 snapshots if review or validation fails.
* independent review must be performed by a reviewer who did not author this plan and is not the roadmap synthesis reference.
* independent review checklist must include stale evidence, source/runtime mismatch, forbidden row mutation, old/new dual authority, ledger overclaim, release-readiness overclaim, and public quality overclaim.
* `independent_adversarial_review_report.md` must use an itemized PASS / FAIL table for each checklist item and must not collapse the review into a single summary PASS sentence.
* if final chain validation or independent review fails, Phase 8 closes as blocked and Phase 0 snapshots are used for atomic pre-ledger restore. Ledger adoption is not attempted.

Validation:

* pre-ledger final chain PASS
* atomic restore readiness PASS
* independent adversarial review PASS
* reviewer independence check
* stale evidence check
* source/runtime mismatch check
* forbidden row mutation check
* old/new dual authority check
* ledger overclaim check
* release-readiness overclaim check
* public quality overclaim check

---

### Phase 9 - Ledger Adoption / Baseline Identity Final Seal

Purpose:

pre-ledger final chain validation and independent review have passed, then successor baseline identity is additively adopted as current authority in top ledger docs.

Files:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `phase9/final_baseline_identity_report.json`
* `phase9/decisions_update_packet.md`
* `phase9/architecture_update_packet.md`
* `phase9/roadmap_update_packet.md`
* `phase9/ledger_consistency_check.json`

Implementation Notes:

* ledger adoption is last-mile canon reflection and must not precede Phase 8 `pre_ledger_final_chain_validation_report.json` PASS and `independent_adversarial_review_report.md` PASS.
* updates are additive. Historical closeouts and predecessor traces are preserved.
* baseline identity seal includes extended evidence slots where available.
* DECISIONS records successor current readpoint and predecessor relation.
* ARCHITECTURE records current source-to-runtime authority chain.
* ROADMAP moves parent problem only to the validated state reached by this execution.
* release / package / Workshop / B42 readiness non-decision is explicit.

Validation:

* Phase 8 final chain PASS consumed as required input
* Phase 8 independent review PASS consumed as required input
* seal precondition ledger completeness check
* baseline manifest seal integrity
* ledger consistency check
* current readpoint wording check
* non-decision boundary check
* predecessor trace preservation check
* additive-only canon diff review
* no release readiness claim scan
* no public-facing quality exposure claim scan

---

### Phase 10 - Post-ledger Closeout / Claim Boundary / Rollback Recipe Seal

Purpose:

sealed ledger 상태에서 final closeout, claim boundary, rollback / correction boundary를 닫는다.

Files:

* `phase10/final_current_authority_cutover_report.json`
* `phase10/final_validation_summary.md`
* `phase10/rollback_restoration_recipe.md`
* `phase10/final_claim_boundary_statement.md`
* `phase10/protected_surface_hashes.after.json`
* `phase10/protected_surface_hash_diff.json`
* `docs/dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_closeout.md`
* `docs/dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_ledger_packet.md`

Implementation Notes:

* final verdict is one of `PASS`, `FAIL`, or `BLOCKED`.
* final chain validation is not first performed here; Phase 10 consumes Phase 8 final-chain PASS and Phase 9 ledger seal as required inputs.
* rollback restoration recipe is preserved even on PASS.
* post-ledger defects are corrected through additive correction / successor round; silent un-seal is forbidden.
* final claim boundary must stay inside validated scope.
* if any required evidence is missing or stale, closeout is `BLOCKED`, not partial success.

Validation:

* Phase 8 final chain PASS consumed
* Phase 9 ledger consistency PASS consumed
* protected surface diff against allowlist
* package verification
* current route
* historical / diagnostic route preservation
* rollback recipe validation
* final claim boundary scan

---

## 7. Validation Plan

### Automated Validation

Required validation families:

* input artifact existence and freshness validation
* mutation allowlist / denylist validation
* protected surface before / after / diff validation
* rollback snapshot completeness validation
* successor baseline manifest schema validation
* source manifest fingerprint validation
* overlay support artifact generation / fingerprint / manifest linkage / stale rejection validation
* facts schema validation
* decisions schema validation
* fact-to-decision traceability validation
* compose profile / body_plan binding validation
* rendered schema validation
* rendered determinism validation
* rendered hash validation
* rendered-to-bridge consistency validation
* bridge-to-chunk consistency validation
* chunk manifest and chunk file hash validation
* live runtime cutover tool availability validation
* atomic runtime replacement exact-target validation
* runtime restore probe validation
* Lua syntax validation
* current route regression
* historical route preservation
* diagnostic route preservation
* package route validation
* export route validation
* compose route validation
* consumer migration executor availability validation
* consumer migration completeness validation
* actual migration diff-to-ledger traceability validation
* change-forbidden zero mutation validation
* authority-source-based hardcoded predecessor current gate scan
* sealed-manifest-derived `2105` allowance validation
* predecessor-specific `2084 / 21` split current-surface validation
* no current `active / silent` writer / validator / runtime payload scan
* publish_state no-direct-emit / B-branch policy no-mutation validation
* overlay / support surface disposition validation
* current surface VCS representation validation
* pre-ledger final-chain PASS validation
* atomic pre-ledger restore readiness validation
* independent reviewer independence validation
* fixture-as-authority guard
* monolith re-entry guard
* stale bridge fallback guard
* old/new dual-current authority guard
* current-route tooling allowlist cap validation
* current core 12 closure validation
* ledger consistency validation
* final claim boundary validation

Known validation commands that must remain exact when claimed:

```powershell
python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
```

```powershell
python -B -m pytest -q
```

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean -Zip
```

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Execution-specific validation commands must be mapped in Phase 0 `command_surface_mapping.json` before any PASS closeout is written. Missing required tools block execution rather than being treated as pass.

### Manual Validation

* authority vocabulary review
* source / runtime role separation review
* mutation allowlist review
* predecessor snapshot review
* consumer migration row-by-row sampling
* historical / diagnostic row preservation review
* independent adversarial review before ledger seal
* reviewer independence review
* public-facing claim boundary review
* rollback restoration recipe review
* rollback restoration dry-run or hash-restore simulation review
* DECISIONS / ARCHITECTURE / ROADMAP additive diff review

### Validation Limits

This plan will not validate or claim:

* multiplayer validation
* long-session runtime validation
* full manual in-game QA
* Workshop readiness
* release readiness
* package release readiness
* deployment readiness
* B42 readiness
* public-facing text quality acceptance
* tooltip completion
* semantic quality completion
* external mod ecosystem compatibility sweep
* full historical artifact byte reproducibility
* predecessor byte-for-byte recovery
* full runtime equivalence with predecessor chunks

---

## 8. Risk Surface Touch

### Authority Surface

Changed.

This plan intentionally touches current source manifest, facts, decisions, compose binding reference, rendered output, Lua bridge export, runtime chunk manifest, runtime chunk files, validator / test / tool authority inputs, and top ledger current readpoint.

### Runtime Behavior Surface

Changed in sealed data payload only.

Runtime Lua logic and UI behavior policy should not change. The runtime Layer3 payload loaded by Iris changes from predecessor chunk bundle to successor chunk bundle.

### Compatibility Surface

Changed.

Validators, tests, tools, and current-route gates must stop treating hardcoded `2105 / 2084 / 21` as current authority and must consume sealed baseline metadata instead. Historical and diagnostic routes must preserve predecessor references.

Manifest-derived `entry_count=2105` is allowed when its authority source is the sealed successor baseline. Predecessor-specific hardcoded `2105`, `2084`, and `21` current gates remain forbidden.

### Sealed Artifact Surface

Changed additively.

New sealed baseline evidence, migration execution evidence, and ledger reflection artifacts are produced. Existing historical sealed artifacts are preserved as predecessor trace.

### Public-Facing Output Surface

Changed at payload text level, not at UI policy level.

Layer3 body payload may change for successor entries. Browser / Wiki / Tooltip layout, sorting, filtering, quality badges, trust/confidence display, recommendation behavior, and publish policy exposure remain out of scope.

---

## 9. Risk Analysis

### Architecture Risk

* source-to-rendered chain may be bypassed by runtime chunk-only replacement.
* baseline candidate may be overread as final sealed current identity before ledger adoption.
* `body_plan` may be treated as a second authority.
* stale staging overlay may be consumed as current support evidence.
* overlay support metadata may accidentally become source authority or a second current authority.
* staging evidence may be directly promoted without live current regeneration.
* ledger update may run ahead of implementation evidence.
* post-ledger rollback may be attempted as silent unseal rather than additive correction.

### Runtime Risk

* old chunks and successor chunks may coexist in live runtime path or package artifact.
* monolith bridge or stale bridge artifact may re-enter fallback / package path.
* a staging-only bridge exporter may be incorrectly treated as the live runtime cutover tool.
* Lua syntax may pass while chunk manifest points at stale or missing chunk files.
* public require contract may change accidentally.
* runtime data payload change may be overclaimed as UI behavior or quality improvement.

### Compatibility Risk

* hardcoded predecessor `2105 / 2084 / 21` current gates may remain in validators or tests.
* legitimate successor `entry_count=2105` may be falsely flagged unless scans inspect authority source.
* change-forbidden audit rows may be accidentally modified.
* historical / diagnostic references may be edited as if current hard gate consumers.
* numeric replacement may hide authority-role migration failure.
* consumer migration may stop at dry-run evidence without actual mutation.
* current-route tooling allowlist may creep beyond cap 1.
* current core closure may expand beyond 12 modules.

### Regression Risk

* rendered regeneration may be non-deterministic.
* facts and decisions hashes may not match final baseline manifest.
* package route may include a mixed predecessor / successor bundle.
* current route may reuse stale staging-only pass evidence.
* protected surface diff may include unapproved files.
* `adopted / unadopted` may be overloaded with quality or publish meaning.
* claim boundary may drift into release readiness, manual QA, or semantic quality completion.

---

## 10. Rollback Plan

Rollback must operate on the baseline unit, not on runtime chunks alone.

Before any mutation:

* capture predecessor source / output / runtime / consumer / ledger snapshots.
* capture SHA256 for every mutation-allowed path.
* write `phase0/rollback_snapshot_manifest.json`.
* verify snapshots are restorable before mutation by restoration dry-run where safe, or by hash-restore simulation when actual restore would mutate live state.

Before ledger adoption:

* if source promotion fails, restore source files and rerun current route.
* if rendered regeneration fails, restore output files and protected side outputs, then rerun current route.
* if runtime switch precondition fails, do not switch live chunks; leave predecessor runtime authority in place and close Phase 4 as blocked.
* if runtime chunk export or syntax validation fails after mutation, restore predecessor chunk manifest + chunk files as one bundle and rerun Lua syntax + package route.
* if consumer migration fails, restore migrated consumers and required validation manifest together, then rerun current route and forbidden scans.
* if Phase 8 final-chain validation fails or independent review fails after live mutation, atomically restore source facts / decisions / input manifest / overlay support artifact, rendered output + protected side outputs, runtime chunk manifest + chunk files, migrated consumers, and required validation manifest from Phase 0 snapshots. Then rerun protected-surface hash diff, stale overlay rejection, old/new dual-current absence scan, package route, Lua syntax, and current route.
* failed successor artifacts remain staged evidence and must not be deleted to hide failure.

After ledger adoption:

* do not silently un-seal the ledger.
* open an additive correction / successor round if a defect is found.
* prior current readpoint restoration after ledger seal requires a new additive rollback or correction plan that records the supersession relation. It cannot be performed as an unrecorded restore inside this plan.

Rollback validation:

* protected surface hash diff after restore
* stale overlay rejection after restore
* restoration dry-run or hash-restore simulation report
* current route regression
* Lua syntax validation after restore
* package route forbidden scan
* old/new dual-current absence scan
* ledger claim boundary review

---

## 11. Governance Constraints

* `Philosophy.md` compliance is mandatory.
* Hub & Spoke / SPI structure must remain intact.
* Iris runtime remains 100% Lua and render-only.
* Runtime / build-time separation must remain intact.
* runtime Lua must not compose, repair, validate source, judge semantic quality, or decide publish policy.
* source authority and runtime deployable authority must remain distinct.
* runtime chunks are deployable runtime authority, not source authority.
* runtime-derived seed is non-authority bootstrap only.
* staging artifact direct current promotion is forbidden.
* monolith current re-entry is forbidden.
* old chunks and successor chunks cannot both be current.
* 6-entry fixture-as-authority is forbidden.
* legacy `active / silent` remains historical / diagnostic / import alias only.
* current runtime vocabulary remains `adopted / unadopted`.
* `adopted / unadopted` must not become quality, publish, deletion, or suppression vocabulary.
* Browser / Wiki / Tooltip must not expose quality state as badge, sorting, filtering, hiding, recommendation, trust, or confidence display.
* successor rendered / bridge / runtime payload must not directly emit `publish_state`; B-branch / policy no-mutation carry-forward remains intact.
* consumer migration must be authority-role migration, not numeric replacement.
* `2105` scanning must distinguish sealed-manifest-derived successor count from hardcoded predecessor readpoint.
* canonical current source paths are replaced as one baseline unit; redirect promotion is not allowed by this plan.
* sealed overlay support metadata is allowed only as `compose_support_not_source_authority`; it must have concrete path, role, fingerprint, input manifest linkage, rendered consumption linkage, stale rejection, and not-second-authority guard.
* `change_required_index.md` is migration input, not automatic execution instruction.
* change-forbidden rows require mutation count 0.
* current core closure remains 12 modules.
* current-route tooling allowlist cap remains 1.
* final end-to-end chain PASS and independent review PASS must precede ledger seal.
* pre-ledger gate failure requires atomic restore from Phase 0 snapshots before any ledger adoption.
* FAIL-LOUD must be preserved for missing source, stale evidence, parity failure, unexplained delta, forbidden row touch, protected surface drift, and blocked tooling.
* DECISIONS / ARCHITECTURE / ROADMAP changes must be additive.
* release readiness, Workshop readiness, B42 readiness, manual in-game validation, runtime rollout beyond local payload replacement, package deployment, and public exposure are not implied.

---

## 12. Expected Closeout State

Expected plan closeout: `current_authority_implementation_2105_consumer_migration_plan_sealed`

Expected execution closeout after the follow-up implementation completes all gates: `complete_current_authority_cutover_and_consumer_migration`

Acceptable execution blocked states:

* `blocked_missing_corrected_evidence`
* `blocked_stale_required_validation_manifest`
* `blocked_unresolved_rollback_semantics`
* `blocked_command_surface_unmapped`
* `blocked_required_execution_tool_missing`
* `blocked_vcs_representation_unclassified`
* `blocked_overlay_surface_unsealed`
* `blocked_source_promotion_validation_failed`
* `blocked_source_promotion_redirect_attempted`
* `blocked_rendered_regeneration_failed`
* `blocked_publish_state_direct_emit_detected`
* `blocked_runtime_switch_precondition_failed`
* `blocked_runtime_cutover_tool_missing`
* `blocked_runtime_chunk_cutover_failed`
* `blocked_consumer_migration_executor_missing`
* `blocked_consumer_migration_incomplete`
* `blocked_current_route_regression`
* `blocked_pre_ledger_final_chain_validation_failed`
* `blocked_independent_review_failed`
* `blocked_independent_review_failed_after_mutation_restored`
* `failed_protected_surface_unapproved_mutation`

`complete_current_authority_cutover_and_consumer_migration` means:

* successor baseline identity is sealed through source manifest, facts, decisions, sealed overlay support metadata, compose binding, rendered hash, Lua bridge report, chunk manifest, chunk files, consumer migration result, and ledger reflection evidence.
* current facts / decisions / overlay support artifact / rendered / runtime chunk bundle are successor baseline current surfaces.
* runtime deployable authority is single successor chunk bundle.
* canonical current source paths were replaced as one baseline unit, not redirected.
* predecessor 2105 remains predecessor / comparison reference / historical migration input.
* 6-entry fixture remains non-current.
* 2105 current hard gate consumers have migrated to baseline manifest / sealed authority metadata.
* manifest-derived `entry_count=2105` is distinguished from hardcoded predecessor readpoint usage.
* change-forbidden rows remain unmodified.
* publish_state B-branch / policy no-mutation carry-forward is preserved.
* independent review PASS and pre-ledger final-chain PASS preceded ledger seal.
* current route, package route, export route, compose route, Lua syntax, historical route, and diagnostic route pass within their defined scope.
* DECISIONS / ARCHITECTURE / ROADMAP reflect the successor current readpoint additively.
* final claim boundary excludes release readiness, Workshop readiness, B42 readiness, manual in-game QA, semantic quality completion, public-facing quality acceptance, multiplayer validation, long-session runtime validation, and external mod compatibility completion.
