# Implementation Plan

> Status: planned / roadmap-derived / WARN review revisions incorporated / PASS-with-minor-revisions review incorporated / failure-mitigation controls incorporated / live consumer migration execution evidence seal plan / no execution performed
> 작성일: 2026-06-19
> Roadmap input: `C:/Users/MW/.codex/attachments/7dbd6fba-0c90-4346-8393-b478a25128ef/pasted-text.txt` / sha256 `B2C00398644619DCA32C16D634B3B97A8D8F71E3316DC194184060ABB2CEC6B9`
> Review input: `C:/Users/MW/.codex/attachments/b6d5c088-4f9d-4d84-8048-33de1abe9f6a/pasted-text.txt` / sha256 `DCD9DF8EB62DA88C9C40751C753B07A72F60E929ED1684D2CF69FF02BE1AC327` / WARN revisions incorporated
> Final review input: `C:/Users/MW/.codex/attachments/af990c6c-b5ee-425a-8a73-02845af95bd9/pasted-text.txt` / sha256 `F2FCF546423853B68B83914E9486CC12487B3861A6096ABF8EB870B8ECDD680F` / PASS with minor revisions incorporated
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Execution contract input: `docs/EXECUTION_CONTRACT.md` / sha256 `A185BBD78EB849B0310D9AADC9102CB156B892513266FAC0EC7903EB3D3A9493`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`

---

## 1. Objective

DVF 3-3 Terminal Disposition Adjudication의 `migrated=153` terminal projection을 live current consumer surface 기준으로 재검증하고, 필요한 row에만 guarded live mutation을 수행한 뒤, readiness / sandbox evidence와 분리된 live completion evidence로 봉인한다.

이 계획의 핵심 목적은 다음이다.

```text
terminal migrated consumer rows를 live current surface 기준으로 재검증한다.
already-live row와 mutation-required row를 분리한다.
authorized live mutation target만 실제 변경한다.
actual live diff와 row-level live ledger를 1:1로 검증한다.
sandbox/readiness evidence를 live completion evidence로 세지 않는다.
```

이 계획은 current authority cutover를 다시 여는 계획이 아니다. `source -> facts -> decisions -> compose -> rendered -> Lua bridge -> chunk runtime data` authority chain은 재정의하지 않는다.

이 계획의 완료가 release readiness, package release readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game QA, semantic quality completion, public-facing text quality acceptance를 의미하지 않는다.

### 1.1 Predecessor Problem Definition - Live Tooling Readiness

현재 해결해야 할 1차 문제는 live mutation 자체가 아니라, live mutation을 안전하게 수행할 수 있는 실행 도구와 검증 경계가 아직 증명되지 않았다는 점이다.

문제 정의:

```text
DVF 3-3 live consumer migration은 roadmap을 먼저 만들고,
그 roadmap에 기반한 실행 계획을 세운 뒤,
그 계획에 필요한 tooling / validator / evidence artifact를 구현하여 해결해야 하는 문제다.

현재 선행과제는 이 전체 문제의 first implementation problem이다:
live writer, row eligibility, dry-run/apply equivalence, dirty target isolation,
consumer-only representability, and external completion gates가 Phase 4 live apply 전에
기계적으로 PASS / BLOCK 판정을 낼 수 있어야 한다.
```

이 선행과제는 다음 이유로 독립 문제로 취급한다.

* 현재 코드베이스에는 readiness / sandbox executor evidence가 있으나, live mutation executor capability는 별도 증명 대상이다.
* `migrated=153` terminal projection은 live mutation target count가 아니라 live-state 재검증 input이다.
* `sandbox mutation=163`은 readiness evidence이며, live completion evidence로 승격할 수 없다.
* terminal `migrated=153` row identity는 sandbox mutation rows의 subset일 수 있으나, subset 관계만으로 hard-forbidden surface mutation을 승인할 수 없다.
* dirty target overlap, expected-form drift, and authority-surface dependency는 Phase 4에서 발견되면 늦으므로 Phase 0-3에서 fail-closed로 판정해야 한다.

해결 방식은 다음 순서를 따른다.

1. Roadmap: live execution readiness 문제를 별도 roadmap item으로 고정하고, sandbox/readiness evidence와 live completion evidence의 claim boundary를 분리한다.
2. Plan: 이 문서를 실행 계획으로 사용하되, Phase 0-3을 live-tooling readiness implementation gate로 먼저 수행한다.
3. Implementation: live writer capability probe, row identity reconciliation, representability validator, frozen patch-bundle dry-run, dirty target isolation, and focused validator suite를 구현하거나 기존 도구가 그 요건을 충족함을 증명한다.

이 선행과제의 성공 상태는 둘 중 하나다.

* `ready_for_phase4_live_apply`: Phase 0-3 gates all PASS, frozen patch bundle exists, live writer capability is proven, no hard-forbidden target remains, and external gate status is explicit.
* `blocked_before_live_apply`: one or more Phase 0-3 blockers are recorded with machine-readable evidence, no live surface mutation is performed, and a successor roadmap / plan / implementation item is opened for the blocker class.

따라서 이 계획은 first execution에서 Phase 4 live apply를 보장하지 않는다. Phase 0-3에서 blocked state로 종료되는 것은 계획 실패가 아니라, live completion overclaim을 막는 정상 결과다.

---

## 2. Scope

이 계획은 live consumer migration execution / evidence seal round를 수행하기 위한 실행 계획이다.

포함 범위:

* scope lock / claim boundary / input provenance freeze
* terminal migrated row input binding
* denominator role separation: `1062`, `311`, `163`, `153`, `148`, `2105`, `2084`, `21`
* row identity crosswalk and `migrated153` vs `sandbox163` reconciliation
* live current consumer surface snapshot
* migrated row live-state classification
* live target derivation
* dry-run live diff and pre-apply hard-forbidden authority-surface safety gate
* guarded live apply, only if Phase 3 gates pass
* actual live diff-to-ledger validation
* sandbox/live evidence separation validation
* static and build-time execution-reach graph dual-zero residue gate
* focused live migration validator and current-route integration boundary
* required-validation manifest adoption status recording
* failure-mode mitigation preflights for authority-surface dependency, row identity drift, expected-form drift, live writer readiness, dry-run/apply equivalence, dirty target overlap, and external gate readiness
* independent review / explicit external gate packet
* final claim boundary, closeout, and ledger packet

Primary execution evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_live_consumer_migration_execution/`

Direct plan artifact:

* `docs/dvf_3_3_live_consumer_migration_execution_plan.md`

### Explicitly Out Of Scope

* successor current authority redesign
* vNext current authority implementation / 2105 consumer migration reopen
* frozen 2105 predecessor recovery
* current source / rendered / runtime authority model change
* monolith runtime fallback restoration
* runtime-side compose, repair, source validation, semantic quality judgment, or publish policy judgment
* Browser / Wiki / Tooltip UI policy change
* `quality_state`, `publish_state`, or `runtime_state` vocabulary redefinition
* no-op / diagnostic-only / historical-only / false-positive row promotion to live mutation target
* broad consumer universe expansion beyond terminal `migrated=153`
* closed readpoint reopen without new authority input
* broad current-route source-overlay blocker fix
* required-validation manifest live adoption without explicit in-scope approval
* source facts / decisions / rendered output / Lua bridge / runtime chunk / package authority surface mutation
* package release readiness, Workshop readiness, deployment readiness, B42 readiness, manual in-game QA, semantic quality completion, public-facing text quality acceptance
* unrelated refactor

---

## 3. Non-Goals

* `migrated=153`을 live mutation count로 해석하지 않는다.
* `migrated=153`을 live completion count로 선해석하지 않는다.
* `163` sandbox mutation rows를 live completion evidence로 세지 않는다.
* `311`, `163`, `153`, `1062` count equality나 subset 추정만으로 row identity를 대체하지 않는다.
* readiness sandbox diff-to-ledger PASS를 live current surface 반영 증거로 사용하지 않는다.
* generated / staging / diagnostic / fixture artifact를 current authority로 승격하지 않는다.
* source facts, decisions, rendered output, runtime chunk authority, Lua bridge authority, package authority를 이 round에서 재정의하지 않는다.
* source facts / decisions / rendered output / Lua bridge / runtime chunk / package authority surfaces를 row-level allowlist로 열지 않는다.
* sandbox executor를 live writer로 silent repointing하지 않는다.
* package route PASS를 package release readiness로 읽지 않는다.
* final closeout을 release readiness나 public exposure로 표현하지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 기준이다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 2026-06-19 current readpoint를 따른다.
* DVF 3-3 current runtime deployable authority는 monolith가 아니라 `IrisLayer3DataChunks.lua` plus `IrisLayer3DataChunks/*.lua` chunk bundle이다.
* Terminal Disposition Adjudication split은 live mutation completion이 아니라 terminal projection input이다.
* Terminal disposition split read:

```text
migrated        = 153
no-op           = 268
diagnostic-only = 3
historical-only = 638
blocked         = 0
conditional     = 0
unknown         = 0
pending         = 0
total           = 1062
```

* `migrated=153` is the live-scope denominator, not the live mutation target count.
* live mutation target must satisfy all conditions below:

```text
terminal_disposition == migrated
AND live_surface_role is writable current consumer surface
AND expected migrated form is known
AND current live content does not already match expected form
AND row is not historical / diagnostic / generated / no-op / false-positive
AND target file is a writable live consumer surface
AND target file is not a hard-forbidden authority surface
```

* Plan-local status vocabulary is fixed as:

```text
live_verified_already
live_mutation_required
live_applied
live_blocked
live_ambiguous
excluded_non_live_target
```

* External vocabulary aliases may be recorded for provenance, but machine artifacts in this plan should use the plan-local vocabulary.
* `excluded_non_live_target` remains a distinct terminal state. It is not silently absorbed into `live_blocked` or `live_ambiguous`.
* `migrated153` vs `sandbox163` reconciliation resolves by row identity and set-difference disposition:

```text
which_163:
  The plan must identify whether the 163 set is actual_apply_eligible, readiness sandbox mutation, or both.
  If both exist, those two 163 sets must also be reconciled by row identity.

migrated153_minus_sandbox163:
  Each row must be assigned to a positive non-sandbox evidence class.
  If no positive evidence class exists, the row becomes live_ambiguous and blocks Phase 3+ mutation.

sandbox163_minus_migrated153:
  Each row must be recorded under its non-migrated terminal disposition.
  These rows are forbidden-for-live-mutation in this round.

resolved:
  Every set-difference row receives exactly one disposition and no row is silently dropped.
```

* Expected migrated form is rederived in Phase 2 from fixed current sealed authority vocabulary input, fixed current runtime chunk identity input, and a documented expected-form derivation oracle. Sandbox/readiness-era expected form is provenance only.
* Source facts / decisions / rendered output / Lua bridge / runtime chunk / package authority surfaces are hard-forbidden mutation surfaces in this round. No row-level allowlist in this plan may authorize them. If such mutation is required, this round stops and a separate approved correction / authority-surface migration plan is required.
* Phase 6 success is conservatively scoped as `focused live migration validator PASS + current-route scope/result recorded + pre-existing blocker loud preservation`. A broad current-route PASS is stronger evidence if available, but it is not allowed to hide unrelated pre-existing blockers.
* Required-validation manifest mutation defaults to `candidate_only`. It may become `adopted_in_scope` only when an external author-approval token or separate decision record is present, guarded diff is recorded, and manifest validation passes. This plan text is not itself approval.
* `candidate_only` is an absent-normal approval-token state. In that state, `required_validation_author_approval_token.json` is not required, and `required_validation_adoption_status.json` must record `approval_token_present=false` and `adoption_status=candidate_only`.
* Independent review may be a non-author adversarial review or an explicit external gate, but it must disclose reviewer independence, reviewed artifact hash set, review scope, and certification ceiling.
* Completion seal remains gated by independent review or explicit external gate, upstream roadmap seal status, and `EXECUTION_CONTRACT.md` applicability / compliance confirmation.
* Any unresolved `live_blocked` or `live_ambiguous` row blocks complete live completion seal unless a separate approved adjudication resolves it.
* `docs/runtime_payload_state_integrity_closeout.md` is provenance input only. Runtime Payload State Integrity Residual Seal remains separately gated unless its own complete seal exists, and no `live_mutation_required` row may depend on an open runtime-payload residual branch.
* The roadmap's reach-residue gate is implemented in this plan as `build_time_execution_reach_graph_residue`. It is not runtime execution, manual in-game QA, long-session validation, or full runtime equivalence. Phase 0 must fix the graph source, command, oracle, and false-positive disposition before this gate can pass.
* New writer / validator tooling must pass positive and negative fixture self-validation before Phase 4 live apply. A tool introduced in this round cannot create a self-referential PASS without fixture evidence.
* Dirty working tree state is part of the evidence boundary. Phase 0 must write a baseline of pre-existing dirty files, and later phases must prove live apply did not consume or overwrite unrelated dirty changes.
* Dirty working tree changes outside this plan are preserved.
* Failure mitigation is front-loaded:
  * authority-surface dependency must be detected before live target derivation and either converted to a consumer-only representable target or split into a separate correction plan seed.
  * row identity drift gets one deterministic resolution ladder before blocking; fuzzy or inferred identity repair is forbidden.
  * expected-form drift is adjudicated by current sealed authority inputs, not sandbox-era forms.
  * live writer capability must be probed before Phase 3; missing live writer is a pre-apply blocker, not a Phase 4 surprise.
  * dry-run/apply equivalence must be proven on fixture or copied target material before live apply.
  * dirty target overlap must be isolated before Phase 3; overlapping dirty files cannot be live-mutated silently.
  * external seal gates must be inventoried before mutation so implementation success is not confused with completion seal.

---

## 5. Repository Areas Affected

### Code

Expected or candidate tooling surfaces, only if the execution round lacks required validators / writers:

* `Iris/build/description/v2/tools/build/validate_dvf_3_3_actual_diff_to_ledger.py`
* `Iris/build/description/v2/tools/build/apply_dvf_3_3_consumer_migration.py`
* `Iris/build/description/v2/tools/build/generate_dvf_3_3_row_level_migration_ledger.py`
* `Iris/build/description/v2/tools/build/validate_consumer_universe_claim_guard.py`
* `Iris/build/description/v2/tests/test_terminal_disposition_adjudication.py`
* `Iris/build/description/v2/tests/test_consumer_universe_denominator_lock.py`

New tooling may be added under the same `tools/build` and `tests` families if Phase 0 proves a required command is missing. Any new tool must be mapped in `phase0/command_surface_mapping.json` before execution claims can rely on it.

Any live writer must be distinct from sandbox / readiness executors unless Phase 0 proves the tool has an explicit live mode, hard-forbidden authority-surface protection, restore-packet support, and self-validation fixtures. Silent path repointing of a sandbox executor is forbidden.

Live mutation targets are not predeclared by filename in this plan. They must be derived from Phase 1 row identity crosswalk and Phase 2 live-state classification, then materialized in Phase 3 path allowlist before any write.

### Docs

Direct plan artifact:

* `docs/dvf_3_3_live_consumer_migration_execution_plan.md`

Expected execution docs:

* `docs/dvf_3_3_live_consumer_migration_claim_boundary.md`
* `docs/dvf_3_3_live_consumer_migration_ledger_packet.md`
* `docs/dvf_3_3_live_consumer_migration_execution_closeout.md`
* `docs/DECISIONS.live_migration_execution.patch.md`
* `docs/ROADMAP.live_migration_execution.patch.md`

Read-only authority inputs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/EXECUTION_CONTRACT.md`
* `docs/consumer_universe_denominator_lock_closeout.md`
* `docs/dvf_3_3_terminal_disposition_adjudication_closeout.md`
* `docs/dvf_3_3_terminal_disposition_claim_boundary.md`
* `docs/dvf_3_3_terminal_disposition_ledger_packet.md`
* `docs/dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_closeout.md`
* `docs/dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_ledger_packet.md`
* `docs/runtime_payload_state_integrity_closeout.md` - provenance only, not residual-seal complete proof

Canonical docs may be updated only after final evidence and review gates pass, and only as additive ledger reflection:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

### Config

Candidate-only by default:

* `Iris/_docs/round3/current_route_required_validations.json`

Live mutation of this manifest is allowed only if Phase 6 records `adopted_in_scope` and the diff is protected by the required-validation adoption gate.

`adopted_in_scope` additionally requires an external author-approval token or separate decision record. Without that artifact, Phase 6 output remains `candidate_only`.

For `candidate_only`, the author approval token file is intentionally absent-normal. `phase6/required_validation_adoption_status.json` must record:

```json
{
  "approval_token_present": false,
  "adoption_status": "candidate_only"
}
```

### Generated Artifacts

All execution evidence must be written under:

* `Iris/build/description/v2/staging/dvf_3_3_live_consumer_migration_execution/`

Expected artifact families:

* `phase0/scope_lock.json`
* `phase0/claim_boundary.freeze.md`
* `phase0/live_migration_input_binding.json`
* `phase0/input_artifact_fingerprint_manifest.json`
* `phase0/live_surface_allowlist.json`
* `phase0/authority_surface_gate_policy.json`
* `phase0/command_surface_mapping.json`
* `phase0/working_tree_baseline.json`
* `phase0/pre_existing_dirty_diff_manifest.json`
* `phase0/execution_contract_applicability_report.json`
* `phase0/hard_forbidden_authority_surface_manifest.json`
* `phase0/surface_boundary_schema_examples.json`
* `phase0/authority_surface_dependency_preflight.json`
* `phase0/live_writer_capability_probe_report.json`
* `phase0/dirty_target_overlap_report.json`
* `phase0/external_gate_requirements_manifest.json`
* `phase0/build_time_execution_reach_graph_definition.json`
* `phase0/new_tool_self_validation_plan.json`
* `phase1/input_freshness_report.json`
* `phase1/artifact_role_binding_ledger.jsonl`
* `phase1/row_identity_crosswalk.jsonl`
* `phase1/row_identity_resolution_ladder_report.json`
* `phase1/unresolved_identity_worklist.jsonl`
* `phase1/which_163_source_report.json`
* `phase1/migrated153_vs_sandbox163_reconciliation_report.json`
* `phase1/reconciliation_set_difference_disposition.json`
* `phase2/migrated_live_state_classification_ledger.jsonl`
* `phase2/current_sealed_authority_vocabulary_input.json`
* `phase2/current_runtime_chunk_identity_input.json`
* `phase2/expected_form_derivation_oracle.json`
* `phase2/expected_form_drift_adjudication_report.json`
* `phase2/consumer_only_representability_report.json`
* `phase2/authority_surface_correction_seed_packet.md`
* `phase2/expected_migrated_form_rederivation_report.json`
* `phase2/runtime_payload_residual_dependency_report.json`
* `phase2/live_target_derivation_summary.json`
* `phase3/new_writer_validator_fixture_report.json`
* `phase3/live_surface_snapshot.before.json`
* `phase3/dry_run_apply_equivalence_probe_report.json`
* `phase3/dirty_target_isolation_report.json`
* `phase3/live_dry_run_diff.json`
* `phase3/live_dry_run_to_ledger_report.json`
* `phase3/hard_forbidden_authority_surface_pre_apply_verdict.json`
* `phase4/live_apply_ledger.jsonl`
* `phase4/live_apply_file_diff_manifest.json`
* `phase4/live_surface_snapshot.after.json`
* `phase4/restore_packet.json`
* `phase5/live_actual_diff_to_ledger_report.json`
* `phase5/live_completion_ledger.jsonl`
* `phase5/sandbox_live_separation_report.json`
* `phase5/static_residue_report.json`
* `phase5/build_time_execution_reach_graph_residue_report.json`
* `phase5/live_migration_completion_report.json`
* `phase6/focused_live_migration_validation_report.json`
* `phase6/current_route_validation_report.json`
* `phase6/required_validation_manifest.candidate_patch.json`
* `phase6/required_validation_adoption_status.json`
* `phase6/required_validation_author_approval_token.json` - required only when `adoption_status == adopted_in_scope`
* `phase6/pre_existing_current_route_blocker_report.json`
* `phase7/independent_review_artifact_hash_manifest.json`
* `phase7/independent_review_artifact_hash_report.json`
* `phase7/review_scope_manifest.json`
* `phase7/upstream_roadmap_seal_status.json`
* `phase7/completion_external_gate_readiness_report.json`
* `phase7/independent_review_request_packet.md`
* `phase7/review_findings.jsonl`
* `phase7/owner_adoption_status.json`
* `phase8/final_live_migration_execution_report.json`

---

## 6. Planned Changes

### Change 1 - Phase 0 Scope Lock / Claim Boundary / Provenance Freeze

Purpose:

이번 round가 current authority cutover 재개방이 아니라 terminal `migrated=153` row의 live reflection / execution evidence seal임을 고정한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_live_consumer_migration_execution/phase0/*`
* read-only input docs and evidence listed in Section 5

Implementation Notes:

* denominator role table을 작성한다.
* read-only input artifact list and SHA256 manifest를 작성한다.
* hard-forbidden authority surface manifest와 writable live consumer surface allowlist를 분리해서 작성한다.
* `surface_boundary_schema_examples.json`에 최소 3분류 예시를 기록한다.
  * `consumer_surface_examples`: writable live consumer surface로 분류 가능한 예시와 필수 판정 필드
  * `hard_forbidden_authority_surface_examples`: source facts, decisions, rendered output, Lua bridge, runtime chunk, package authority surface 예시
  * `ambiguous_surface_disposition`: consumer/authority 경계가 불명확할 때 `live_ambiguous` 또는 `revised_plan_needed`로 멈추는 규칙
* `authority_surface_dependency_preflight.json`을 작성한다. 각 candidate path는 `consumer_only_representable`, `authority_surface_dependent`, `ambiguous_surface`, or `not_in_scope` 중 하나로 분류한다.
* `authority_surface_dependent` row가 있으면 Phase 2에서 consumer-only 대체 가능성을 한 번 판정하고, 불가하면 `authority_surface_correction_seed_packet.md`로 별도 scope seed를 남긴다. 이 row는 live apply target이 될 수 없다.
* working tree baseline and pre-existing dirty diff manifest를 작성한다.
* `dirty_target_overlap_report.json`을 작성해 pre-existing dirty files와 잠재 live target path overlap을 계산한다. overlap row는 Phase 3 전 isolation 또는 explicit block이 필요하다.
* `EXECUTION_CONTRACT.md` applicability report를 작성한다. 적용 가능하면 read-only contract input으로 소비하고, 적용 불가한 항목은 `not_applicable_with_reason`으로 기록한다.
* `build_time_execution_reach_graph_definition.json`에 graph source, command, oracle, false-positive disposition, and certification ceiling을 고정한다.
* `live_writer_capability_probe_report.json`을 작성한다. live writer는 explicit live mode, hard-forbidden surface protection, restore-packet support, dirty-target refusal, and self-validation hook을 갖춰야 한다.
* new writer / validator self-validation plan을 작성한다.
* `external_gate_requirements_manifest.json`을 작성해 independent review, upstream roadmap seal, and execution-contract applicability gate의 required / pending / not-applicable 상태를 실행 전부터 분리한다.
* sandbox / readiness executor를 live writer로 silent repointing하지 않음을 command mapping에서 증명한다.
* `readiness evidence != live completion evidence` claim rule을 고정한다.
* Phase 0 before-state 기준 live mutation count가 `0`임을 확인한다.
* every required validation family must map to a concrete command, tool, or explicit blocked status in `command_surface_mapping.json`.

Validation:

* scope validator
* claim boundary validator
* input artifact existence and fingerprint check
* hard-forbidden authority surface manifest check
* writable live consumer surface allowlist check
* surface boundary schema examples check
* authority surface dependency preflight check
* live writer capability probe check
* dirty target overlap check
* external gate requirements inventory check
* working tree baseline capture
* execution contract applicability check
* build-time execution-reach graph definition check
* new tool self-validation plan check
* live writer / sandbox executor separation check
* mutation-0 check
* command surface mapping completeness check

---

### Change 2 - Phase 1 Input Binding / Evidence Freshness / Row Identity Crosswalk

Purpose:

Terminal Disposition, Denominator Governance, readiness tooling, current cutover evidence를 live execution input으로 묶되 lifecycle role을 분리한다.

Files:

* `phase1/input_freshness_report.json`
* `phase1/artifact_role_binding_ledger.jsonl`
* `phase1/row_identity_crosswalk.jsonl`
* `phase1/which_163_source_report.json`
* `phase1/migrated153_vs_sandbox163_reconciliation_report.json`
* `phase1/reconciliation_set_difference_disposition.json`
* `phase1/input_rejection_report.json`

Implementation Notes:

* terminal disposition ledger and final report are read-only input.
* readiness row disposition and sandbox mutation evidence are provenance only.
* row identity key normalization is required before any target derivation.
* `row_identity_resolution_ladder_report.json` must attempt deterministic identity resolution in this order: canonical row id, terminal ledger key, current live surface anchor, normalized evidence tuple. Each step must record matched / unmatched counts.
* fuzzy matching, display-string matching, or count-balancing identity repair is forbidden.
* rows still unmatched after the ladder are written to `unresolved_identity_worklist.jsonl` and block mutation derivation.
* `migrated=153` and `sandbox=163` membership relation must be reconciled by row identity, not count equality.
* `which_163_source_report.json` must identify whether `163` means `actual_apply_eligible`, readiness sandbox mutation rows, or both.
* if both 163 sets exist, they must be reconciled with each other by row identity before comparison with `migrated=153`.
* `migrated153_minus_sandbox163` rows must receive a positive non-sandbox evidence class. Rows without such class become `live_ambiguous` and block mutation.
* `sandbox163_minus_migrated153` rows must receive their non-migrated terminal disposition and be marked `forbidden_for_live_mutation`.
* reconciliation is `resolved` only when every set-difference row receives exactly one disposition and no row is silently dropped.
* raw dry-run or audit matrix artifacts must not become executable instruction without role binding.

Validation:

* required input artifact hash check
* artifact lifecycle role check
* row identity crosswalk validation
* deterministic row identity resolution ladder validation
* unresolved identity worklist empty check
* `which_163` source validation
* set-difference disposition completeness validator
* `migrated153_minus_sandbox163` positive evidence class validator
* `sandbox163_minus_migrated153` forbidden-for-live-mutation validator
* no raw dry-run direct execution check
* no staging artifact current promotion check
* unresolved row identity mismatch blocks Phase 2 mutation derivation

---

### Change 3 - Phase 2 Migrated Row Projection / Live-State Classification

Purpose:

terminal `migrated=153` row 전체를 live current consumer surface 기준 상태로 분류한다.

Files:

* `phase2/migrated_live_state_classification_ledger.jsonl`
* `phase2/live_verified_already_ledger.jsonl`
* `phase2/live_mutation_required_ledger.jsonl`
* `phase2/live_blocked_ledger.jsonl`
* `phase2/live_ambiguous_ledger.jsonl`
* `phase2/excluded_non_live_target_ledger.jsonl`
* `phase2/current_sealed_authority_vocabulary_input.json`
* `phase2/current_runtime_chunk_identity_input.json`
* `phase2/expected_form_derivation_oracle.json`
* `phase2/expected_form_drift_adjudication_report.json`
* `phase2/consumer_only_representability_report.json`
* `phase2/authority_surface_correction_seed_packet.md`
* `phase2/expected_migrated_form_rederivation_report.json`
* `phase2/runtime_payload_residual_dependency_report.json`
* `phase2/live_target_derivation_summary.json`

Implementation Notes:

* every terminal migrated row must receive exactly one plan-local live status.
* already matching live surface rows are recorded as `live_verified_already` and are not mutated.
* `live_verified_already` rows must include `no_diff=true` and `expected_form_match=true`; `positive_provenance` should be populated when available and may be `null` only when those two checks carry the match.
* expected migrated form must be rederived from `current_sealed_authority_vocabulary_input.json`, `current_runtime_chunk_identity_input.json`, and `expected_form_derivation_oracle.json`. Sandbox/readiness-era expected forms are provenance only.
* if sandbox/readiness-era expected form differs from current rederived expected form, `expected_form_drift_adjudication_report.json` records both forms, the current-authority winning form, and whether the row remains consumer-only representable.
* `consumer_only_representability_report.json` must prove every `live_mutation_required` row can be changed only through writable live consumer surface files. If not, the row is removed from live apply eligibility and written to `authority_surface_correction_seed_packet.md`.
* no `live_mutation_required` row may depend on an open Runtime Payload State Integrity Residual Seal branch. If a row depends on that open branch, classify it as `live_ambiguous` or split a successor plan.
* only `live_mutation_required` rows can proceed to Phase 3 dry-run target derivation.
* `live_blocked`, `live_ambiguous`, and `excluded_non_live_target` are fail-loud disposition buckets, not silent zeroes.
* no-op / diagnostic-only / historical-only rows must not enter mutation target derivation.

Validation:

* migrated-only projection validator
* live-state classification coverage validator
* unclassified row count == `0`
* non-migrated mutation target count == `0`
* already-live no-mutation intent validator
* `live_verified_already` positive provenance / no-diff / expected-form-match validator
* current sealed authority vocabulary input validator
* current runtime chunk identity input validator
* expected-form derivation oracle validator
* expected-form drift adjudication validator
* consumer-only representability validator
* authority-surface correction seed validator, when needed
* expected migrated form current-authority rederivation validator
* runtime payload residual dependency validator
* blocked / ambiguous unresolved target gate

---

### Change 4 - Phase 3 Live Dry-Run Diff / Pre-Apply Safety Gate

Purpose:

실제 live mutation 전에 예상 diff가 `live_mutation_required` ledger와 1:1로 매핑되는지 검증한다.

Files:

* `phase3/live_surface_snapshot.before.json`
* `phase3/new_writer_validator_fixture_report.json`
* `phase3/dry_run_apply_equivalence_probe_report.json`
* `phase3/dirty_target_isolation_report.json`
* `phase3/live_dry_run_diff.json`
* `phase3/live_dry_run_to_ledger_report.json`
* `phase3/hard_forbidden_authority_surface_pre_apply_verdict.json`
* `phase3/pre_apply_gate_report.json`

Implementation Notes:

* before snapshot is mandatory.
* Phase 0 working tree baseline must be consumed so pre-existing dirty changes do not become live apply evidence.
* `dirty_target_isolation_report.json` must prove no live target overlaps pre-existing dirty file content. If overlap exists, Phase 3 must either isolate the target into an explicit patch from the captured baseline or block with `blocked_dirty_target_overlap`.
* if any writer or validator is new or materially changed in this round, `new_writer_validator_fixture_report.json` must PASS before Phase 4.
* minimum negative fixtures are orphan diff, unmapped row, non-migrated mutation, hard-forbidden authority surface mutation, sandbox/live evidence mix-up, already-live row rewrite, and invalid rollback packet.
* `dry_run_apply_equivalence_probe_report.json` must prove the live writer applies the same patch bundle that the dry-run validator approved, using fixture or copied target material. Phase 4 must not recompute targets from mutable state.
* dry-run applies only `live_mutation_required` rows.
* dry-run must produce no orphan diff and no hard-forbidden authority surface mutation.
* path allowlist must be materialized before Phase 4.
* if dry-run exposes anchor drift, stale replacement form, hard-forbidden authority surface mutation, or blocked target, Phase 4 must not run.

Validation:

* dry-run diff-to-ledger validator
* new writer / validator positive and negative fixture suite
* dry-run/apply equivalence probe validator
* dirty target isolation validator
* orphan diff validator
* unmapped row validator
* hard-forbidden authority surface mutation validator
* touched-file isolation against dirty baseline validator
* change-forbidden surface validator
* path allowlist validator
* static residue preliminary validator

---

### Change 5 - Phase 4 Guarded Live Apply

Purpose:

Phase 3 gate를 통과한 live mutation target만 실제 live consumer surface에 반영한다.

Files:

* `phase4/live_apply_ledger.jsonl`
* `phase4/live_apply_file_diff_manifest.json`
* `phase4/live_surface_snapshot.after.json`
* `phase4/restore_packet.json`
* `phase4/apply_integrity_report.json`

Implementation Notes:

* apply is single-writer.
* live writer must be explicitly identified as live-capable. A sandbox executor cannot be used for live apply by changing paths silently.
* apply must be atomic or patch-bundle controlled.
* Phase 4 consumes the frozen patch bundle approved by Phase 3. It must not regenerate row targets, expected forms, or path allowlists during live apply.
* changed file list must be exactly tied to Phase 3 allowlist.
* restore packet must be generated before complete claim.
* source facts / decisions / rendered output / Lua bridge / runtime chunk / package authority surfaces are hard-forbidden mutation surfaces in this round. No row-level allowlist can authorize those surfaces.
* if a live mutation appears to require one of those hard-forbidden surfaces, Phase 4 stops and the closeout becomes `revised_plan_needed` or a separate correction / authority-surface migration plan is opened.

Validation:

* atomic apply completion check
* changed file list check
* apply ledger completeness check
* frozen patch bundle identity check
* no extra file mutation check
* hard-forbidden authority surface changed_count == `0`
* dirty baseline isolation check
* live writer / sandbox executor separation check
* restore packet validity check

---

### Change 6 - Phase 5 Actual Live Completion Evidence / Dual-Zero Gate

Purpose:

actual live diff와 live apply ledger가 정확히 일치하고, sandbox/readiness evidence와 분리된 live completion evidence로 봉인 가능한지 검증한다.

Files:

* `phase5/live_actual_diff_to_ledger_report.json`
* `phase5/live_completion_ledger.jsonl`
* `phase5/sandbox_live_separation_report.json`
* `phase5/non_migrated_no_mutation_verdict.json`
* `phase5/hard_forbidden_authority_surface_no_mutation_verdict.json`
* `phase5/static_residue_report.json`
* `phase5/build_time_execution_reach_graph_residue_report.json`
* `phase5/live_migration_completion_report.json`

Implementation Notes:

* before / after snapshot comparison is authoritative.
* actual diff must map to live apply ledger rows.
* sandbox diff must not be reused as live diff.
* already-live rows must have no live mutation diff.
* no-op / diagnostic-only / historical-only rows must have no mutation.
* `build_time_execution_reach_graph_residue_report.json` is a build-time reference/reachability graph gate, not runtime execution proof.
* graph source, command, oracle, and false-positive disposition must match Phase 0 `build_time_execution_reach_graph_definition.json`.
* dual-zero gate requires both:

```text
static residue within live migrated-scope legacy reference == 0
build_time_execution_reach_graph_residue == 0
```

Validation:

* actual live diff-to-ledger validator
* migrated-only mutation validator
* no-op / diagnostic / historical no-mutation validator
* sandbox/live evidence separation validator
* row identity completeness validator
* already-live no-diff validator
* static residue validator
* build-time execution-reach graph residue validator
* hard-forbidden authority surface no-mutation validator

---

### Change 7 - Phase 6 Current Route / Required Validation Integration

Purpose:

live completion evidence가 focused validator와 current-route required validation boundary에서 재사용 가능한 형태로 닫히도록 한다.

Files:

* `phase6/focused_live_migration_validation_report.json`
* `phase6/current_route_validation_report.json`
* `phase6/required_validation_manifest.candidate_patch.json`
* `phase6/required_validation_adoption_status.json`
* `phase6/required_validation_author_approval_token.json` - required only when `adoption_status == adopted_in_scope`
* `phase6/current_core_closure_guard_report.json`
* `phase6/tooling_allowlist_guard_report.json`
* `phase6/pre_existing_current_route_blocker_report.json`

Implementation Notes:

* focused live migration validator PASS is mandatory for complete execution seal.
* current-route validation command and scope must be recorded exactly.
* if broad current-route has a pre-existing blocker, this plan records it loudly and does not relabel it as live migration failure or success.
* required-validation manifest patch is `candidate_only` unless an external author-approval token or separate decision record exists and is copied into `required_validation_author_approval_token.json`.
* if `adoption_status == candidate_only`, `required_validation_author_approval_token.json` is not required and `required_validation_adoption_status.json` must record `approval_token_present=false`.
* if `adoption_status == adopted_in_scope`, `required_validation_author_approval_token.json` is required and must reference an external author-approval token or separate decision record.
* if `required_validation_author_approval_token.json` is missing or invalid while `adoption_status == adopted_in_scope`, adoption is forbidden even if the plan text says adoption is desirable.
* current core closure and tooling allowlist cap must not be expanded to make this round pass.

Validation:

* focused live migration validator
* current route contract or scoped current-route validation
* current core closure enforcement
* tooling allowlist cap check
* required-validation candidate/live distinction check
* required-validation approval-token absent-normal validator
* required-validation external approval token validator
* pre-existing blocker preservation check

---

### Change 8 - Phase 7 Independent Review / Artifact Hash Seal

Purpose:

live execution evidence를 독립 검토 가능하게 봉인한다.

Files:

* `phase7/independent_review_artifact_hash_manifest.json`
* `phase7/independent_review_artifact_hash_report.json`
* `phase7/review_scope_manifest.json`
* `phase7/upstream_roadmap_seal_status.json`
* `phase7/review_findings.jsonl`
* `phase7/owner_adoption_status.json`

Implementation Notes:

* review packet must include exact artifact list and hashes.
* stable artifact hash mismatch remains hard-fail.
* owner adoption and independent review status are separate.
* `upstream_roadmap_seal_status.json` records whether the source roadmap has independent review / seal, explicit external gate status, or a certification ceiling. It does not by itself approve live mutation.
* `completion_external_gate_readiness_report.json` records each completion seal gate as `satisfied`, `pending_external`, `blocked`, or `not_applicable_with_reason` before final closeout.
* `independent_review_request_packet.md` is prepared even if the review is not complete, so completion can proceed without rediscovering review scope.
* review must check claim boundary, evidence role separation, live completion claim, sandbox/live separation, hard-forbidden authority surface mutation, release-readiness overclaim, and current-authority-recutover overclaim.

Validation:

* independent review artifact hash validator
* claim boundary validator
* evidence role separation validator
* stable artifact hash mismatch hard-fail
* owner adoption / independent review status separation check
* upstream roadmap seal status check
* completion external gate readiness check
* independent review request packet completeness check

---

### Change 9 - Phase 8 Closeout / Decision Ledger Packet

Purpose:

live migration execution의 final state를 closeout, claim boundary, and ledger packet으로 봉인한다.

Files:

* `phase8/final_live_migration_execution_report.json`
* `docs/dvf_3_3_live_consumer_migration_execution_closeout.md`
* `docs/dvf_3_3_live_consumer_migration_ledger_packet.md`
* `docs/dvf_3_3_live_consumer_migration_claim_boundary.md`
* `docs/DECISIONS.live_migration_execution.patch.md`
* `docs/ROADMAP.live_migration_execution.patch.md`

Implementation Notes:

* final report must separate `live_applied`, `live_verified_already`, `excluded_non_live_target`, `live_blocked`, and `live_ambiguous` counts.
* closeout must explicitly state that sandbox mutation is not counted as live completion.
* closeout must not claim current authority recutover.
* closeout must not claim release, package, Workshop, B42, deployment, manual QA, semantic quality, or public text readiness.
* follow-up, if any, must be classified as correction, rollback, required-validation adoption, or explicit external gate.

Validation:

* closeout report schema validation
* claim boundary validation
* DECISIONS patch candidate validation
* ROADMAP patch candidate validation
* no release-readiness claim validator
* no current-authority-recutover claim validator

---

## 7. Validation Plan

### Automated Validation

Do not claim validation passed unless the exact relevant command exits with code 0.

Required validation families:

* input artifact role validation
* input fingerprint / hash validation
* execution contract applicability validation
* dirty working tree baseline validation
* dirty target overlap and isolation validation
* surface boundary schema examples validation
* authority surface dependency preflight validation
* live writer capability probe validation
* external gate requirements inventory validation
* row identity crosswalk validation
* deterministic row identity resolution ladder validation
* unresolved identity worklist empty validation
* `migrated153` vs `sandbox163` reconciliation validation
* `which_163` source validation
* reconciliation set-difference disposition completeness validation
* terminal migrated projection validation
* current sealed authority vocabulary input validation
* current runtime chunk identity input validation
* expected-form derivation oracle validation
* expected-form drift adjudication validation
* consumer-only representability validation
* expected migrated form current-authority rederivation validation
* `live_verified_already` positive provenance / no-diff / expected-form-match validation
* runtime payload residual dependency validation
* live-state classification coverage validation
* live target derivation validation
* new writer / validator positive and negative fixture validation
* live writer / sandbox executor separation validation
* dry-run/apply equivalence validation
* frozen patch bundle identity validation
* live dry-run diff-to-ledger validation
* guarded apply validation
* actual live diff-to-ledger validation
* already-live no-diff validation
* non-migrated no-mutation validation
* hard-forbidden authority surface no-mutation validation
* touched-file isolation validation
* static residue validation
* build-time execution-reach graph residue validation
* focused live migration validation
* required-validation manifest adoption status validation
* required-validation approval-token absent-normal validation
* required-validation external approval token validation
* independent review hash validation
* upstream roadmap seal status validation
* completion external gate readiness validation
* independent review request packet validation
* final claim boundary validation

Known exact command candidates:

```powershell
python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
```

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean -Zip
```

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Execution-specific validators must be pinned in Phase 0 `command_surface_mapping.json` before any PASS claim. Missing tools block execution instead of being treated as pass.

Package route may be used as no-regression evidence. It does not imply package release readiness.

### Manual Validation

* mutation allowlist review
* hard-forbidden authority surface policy review
* row identity crosswalk sampling
* reconciliation set-difference disposition review
* surface boundary examples review
* live-state status vocabulary review
* current sealed authority vocabulary input review
* current runtime chunk identity input review
* expected-form derivation oracle review
* expected migrated form rederivation review
* `live_verified_already` provenance field review
* `migrated=153` vs `sandbox=163` membership relation review
* actual diff-to-ledger sampling
* already-live no-diff review
* dirty working tree baseline review
* dirty target overlap review
* authority surface dependency preflight review
* consumer-only representability review
* deterministic row identity resolution ladder review
* new writer / validator fixture review
* live writer capability probe review
* dry-run/apply equivalence review
* frozen patch bundle review
* build-time execution-reach graph definition review
* blocked / ambiguous row disposition review
* required-validation adoption status review
* approval-token absent-normal review
* independent review scope and reviewer independence review
* upstream roadmap seal status review
* completion external gate readiness review
* final claim boundary review
* DECISIONS / ROADMAP patch candidate review

### Validation Limits

This plan will not validate or claim:

* full external ecosystem compatibility sweep
* multiplayer validation
* long-session runtime validation
* manual in-game QA
* deployment validation
* Workshop readiness validation
* package release readiness validation
* B42 readiness validation
* semantic quality acceptance
* public-facing behavior validation
* full text quality review
* full runtime equivalence
* full compatibility preservation
* dynamic runtime execution-reach validation
* broad current-route source-overlay blocker resolution, unless a separate exact current-route command passes and the blocker is in scope

---

## 8. Risk Surface Touch

### Authority Surface

Limited / guarded.

This plan may touch approved migrated consumer rows and produce row-level live completion evidence. It must not redefine or mutate source facts, decisions, rendered output, Lua bridge authority, runtime chunk authority, or package authority.

Hard-forbidden mutation surfaces:

```text
source facts
decisions
rendered output
Lua bridge
runtime chunks
package authority surfaces
```

No row-level allowlist in this plan may authorize those surfaces. If one of those surfaces must change, this plan stops and a separate approved correction / authority-surface migration plan is required.

### Runtime Behavior Surface

None intended.

If a migrated consumer reference is runtime-reachable, correcting that reference may affect the runtime data path. That does not authorize runtime-side compose, repair, source validation, semantic quality judgment, renderer policy change, or UI exposure change.

### Compatibility Surface

Limited.

No public require contract mutation is planned. This plan does not run a full external ecosystem compatibility sweep and does not claim full external compatibility preservation.

### Sealed Artifact Surface

Changed additively.

New live migration evidence, review packets, closeout, and ledger packet are created. Existing terminal / denominator / readiness / cutover artifacts are consumed as read-only predecessor evidence.

### Public-Facing Output Surface

None.

This plan does not change Browser / Wiki / Tooltip display, sorting, filtering, quality badges, recommendation behavior, confidence display, public release notes, or Workshop upload.

---

## 9. Risk Analysis

### Architecture Risk

* `migrated=153` may be overread as live mutation completion.
* readiness / sandbox evidence may be counted as live completion evidence.
* row identity mismatch may be hidden by count equality.
* `migrated153` / `sandbox163` set-difference rows may pass without disposition.
* closeout may imply current authority recutover.
* required-validation manifest adoption may occur without explicit approval.
* independent review pending may be presented as sealed PASS.
* runtime payload residual seal provenance may be overread as complete residual seal.

### Runtime Risk

* live mutation may try to touch runtime chunk / bridge / source / rendered / package authority surfaces, which must hard-fail this plan.
* already-live rows may be rewritten unnecessarily.
* stale replacement forms may drift anchors.
* runtime-reachable reference correction may be overclaimed as UI or behavior policy improvement.
* build-time execution-reach graph residue may be misread as runtime validation.

### Compatibility Risk

* public require contract may change accidentally.
* old vocabulary alias support may leak from historical / diagnostic route into current route.
* current-route tooling allowlist or core closure count may be expanded to force a pass.
* package route PASS may be read as package readiness.
* sandbox executor may be silently repointed into a live writer path.

### Regression Risk

* actual live diff may not match dry-run diff.
* hard-forbidden authority surface diff or unrelated dirty-file diff may appear in changed output.
* generated / staging / diagnostic files may enter live mutation target set.
* `live_blocked` or `live_ambiguous` rows may be collapsed into silent zero.
* new writer / validator tooling may self-validate without negative fixture sensitivity.
* dirty working tree changes may pollute before/after diff interpretation.
* dual-zero may pass static residue but fail build-time execution-reach graph residue, or vice versa.

---

## 10. Rollback Plan

Before Phase 4, no live surface mutation is allowed. Phase 0 through Phase 3 failures produce failed preflight reports, blocked mismatch ledgers, live ambiguous ledgers, and no-mutation verdicts only.

Phase 0 must capture:

* `phase0/working_tree_baseline.json`
* `phase0/pre_existing_dirty_diff_manifest.json`
* hashes or equivalent identity records for all intended mutation candidates

Rollback must preserve unrelated pre-existing dirty files and must not normalize, delete, or overwrite them.

If Phase 0 or Phase 3 detects dirty target overlap, rollback planning must include either:

* an isolated patch generated from captured baseline content, or
* a blocked state before live apply.

Phase 4 live apply requires:

* `phase3/live_surface_snapshot.before.json`
* `phase4/restore_packet.json`
* `phase4/live_apply_file_diff_manifest.json`
* `phase4/live_apply_ledger.jsonl`

If Phase 5 or later validation fails after mutation, one of these paths must be taken:

* automatic restore from pre-apply snapshot or restore packet
* manual rollback procedure generated from mutation file list and row ledger
* correction scope split when the mutation is valid but validator expectation is wrong

If a hard-forbidden authority surface is touched, rollback is mandatory and the plan cannot close as complete. The only allowed follow-up is `revised_plan_needed`, `rolled_back_after_failed_live_apply`, or a separate approved correction / authority-surface migration plan.

If Phase 4 output differs from the Phase 3 frozen patch bundle, rollback is mandatory and the plan closes as `rolled_back_after_apply_equivalence_failure` or `blocked_dry_run_apply_equivalence_failed`.

Rollback completion requires:

```text
before snapshot and restored state hash match
post-rollback diff == 0
failed apply ledger preserved
failed live completion claim not emitted
final report state = rolled_back or blocked_before_live_apply
```

If `live_blocked` or `live_ambiguous` rows remain, canonical complete seal is blocked and the residual rows become a successor adjudication scope.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Hub & Spoke / SPI boundaries remain unchanged.
* Iris runtime remains Lua-only render surface, not runtime analysis / repair / policy engine.
* Runtime / build-time separation must be preserved.
* Source / rendered / runtime chunk / package authority ownership must be preserved.
* Source facts / decisions / rendered output / Lua bridge / runtime chunk / package authority surfaces are hard-forbidden mutation surfaces in this round.
* No row-level allowlist may authorize hard-forbidden authority surface mutation.
* Authority-surface-dependent rows must be removed from live apply eligibility and split into a separate correction seed packet.
* Current runtime deployable authority remains chunk manifest plus chunk files.
* Monolith fallback remains forbidden.
* Staging / generated / diagnostic / fixture artifacts must not become current authority.
* Sandbox / readiness evidence must not become live completion evidence.
* Historical / diagnostic / no-op / false-positive rows must not become live mutation target.
* Terminal `migrated=153` projection must not become automatic live mutation count.
* Row identity mapping has priority over count equality.
* `migrated153` / `sandbox163` set-difference rows must receive explicit disposition before Phase 2 mutation derivation.
* Row identity repair must follow a deterministic resolution ladder; fuzzy matching and count-balancing are forbidden.
* Protected current authority surface guard must remain fail-loud.
* Live mutation requires snapshot before apply and actual diff-to-ledger validation after apply.
* Rollback must be possible for all live mutations.
* No public require contract mutation is planned; full external compatibility preservation is not claimed.
* Required-validation manifest adoption defaults to `candidate_only`.
* `adopted_in_scope` requires an external author-approval token or separate decision record; this plan text is not approval.
* Live writer and sandbox executor must be separated unless a tool has explicit live mode, hard-forbidden surface protection, restore support, and self-validation fixture PASS.
* Live writer capability must be probed before Phase 3.
* Any new writer or validator must pass positive and negative fixture self-validation before Phase 4.
* Dry-run/apply equivalence must be proven before Phase 4, and Phase 4 must consume the frozen Phase 3 patch bundle.
* `build_time_execution_reach_graph_residue` is not runtime execution validation.
* Runtime Payload State Integrity Residual Seal provenance must not be consumed as complete residual seal unless its own complete seal exists.
* Current core closure and tooling allowlist caps must not be widened to pass this round.
* DECISIONS / ARCHITECTURE / ROADMAP updates, if performed, must be additive and claim-bounded.
* Release readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA completion, semantic quality completion, and public-facing text quality acceptance are not implied.

---

## 12. Expected Closeout State

Expected plan closeout:

```text
live_consumer_migration_execution_plan_sealed
```

Expected execution closeout after implementation:

```text
complete_live_consumer_migration_execution_evidence_seal
```

This complete state is allowed only if:

* all terminal `migrated=153` rows are classified into exactly one live terminal state.
* Phase 0 surface boundary examples exist for consumer surfaces, hard-forbidden authority surfaces, and ambiguous surface disposition.
* authority surface dependency preflight proves all live targets are consumer-only representable.
* `which_163` source is identified and, if multiple 163 sets exist, reconciled by row identity.
* row identity resolution ladder has no unresolved identity worklist.
* every `migrated153_minus_sandbox163` row has a positive non-sandbox evidence class or is classified `live_ambiguous`.
* every `sandbox163_minus_migrated153` row has a non-migrated terminal disposition and is forbidden for live mutation.
* reconciliation set-difference disposition is complete.
* unclassified row count is `0`.
* expected migrated forms are rederived from fixed current sealed authority vocabulary input, fixed current runtime chunk identity input, and expected-form derivation oracle.
* expected-form drift, if present, is adjudicated in favor of current sealed authority inputs and remains consumer-only representable.
* no `live_mutation_required` row depends on an open runtime-payload residual branch.
* `live_mutation_required` target set is row-identity locked.
* live mutation target exactly matches `live_mutation_required`.
* `live_verified_already` rows have `no_diff=true`, `expected_form_match=true`, and `positive_provenance` populated when available.
* no-op / diagnostic-only / historical-only / generated / false-positive row mutation count is `0`.
* actual live diff-to-ledger mapping PASS.
* unmapped live diff count is `0`.
* orphan live mutation count is `0`.
* non-migrated mutation count is `0`.
* hard-forbidden authority surface mutation count is `0`.
* source facts / decisions / rendered output / Lua bridge / runtime chunk / package authority surface changed count is `0`.
* no row-level allowlist authorized hard-forbidden authority surface mutation.
* working tree baseline proves unrelated dirty changes were not touched or consumed.
* dirty target overlap is absent or isolated before live apply.
* sandbox/readiness evidence `311/163` is excluded from live completion counts.
* static residue count is `0`.
* build-time execution-reach graph residue count is `0`, with graph definition fixed in Phase 0.
* any new writer / validator positive and negative fixture suite PASS preceded Phase 4.
* live writer capability probe PASS preceded Phase 3.
* live writer was not a silently repointed sandbox executor.
* dry-run/apply equivalence probe PASS preceded Phase 4.
* Phase 4 consumed the frozen Phase 3 patch bundle without regenerating targets.
* focused live migration validator PASS.
* current-route validation scope and result are recorded exactly.
* tooling allowlist and current core closure remain unchanged.
* required-validation adoption status is `candidate_only` with `approval_token_present=false`, or `adopted_in_scope` with external author-approval token / separate decision record.
* independent review or explicit external gate is satisfied and artifact hashes are sealed.
* upstream roadmap seal status and `EXECUTION_CONTRACT.md` applicability / compliance confirmation are recorded before completion seal.
* completion external gate readiness report records all completion seal gates as satisfied, pending external, blocked, or not applicable with reason.
* final report separates `live_applied`, `live_verified_already`, `excluded_non_live_target`, `live_blocked`, and `live_ambiguous` counts.
* rollback packet exists and validates.
* final claim boundary rejects release / package / Workshop / deployment / B42 / manual QA / semantic quality / public text readiness claims.

Acceptable blocked or partial execution states:

* `blocked_input_artifact_missing`
* `blocked_input_freshness_failed`
* `blocked_row_identity_mismatch`
* `blocked_row_identity_resolution_failed`
* `blocked_reconciliation_set_difference_unresolved`
* `blocked_authority_surface_dependency`
* `blocked_consumer_only_representability_failed`
* `blocked_expected_form_rederivation_failed`
* `blocked_expected_form_drift_unadjudicated`
* `blocked_runtime_payload_residual_dependency`
* `blocked_unclassified_migrated_rows`
* `blocked_live_ambiguous_rows`
* `blocked_live_mismatch_rows`
* `blocked_new_tool_self_validation_failed`
* `blocked_dirty_worktree_isolation_failed`
* `blocked_dirty_target_overlap`
* `blocked_dry_run_diff_unmapped`
* `blocked_dry_run_apply_equivalence_failed`
* `blocked_hard_forbidden_authority_surface_pre_apply`
* `blocked_hard_forbidden_authority_surface_touch`
* `blocked_live_writer_not_separated_from_sandbox_executor`
* `blocked_required_execution_tool_missing`
* `blocked_live_writer_capability_probe_failed`
* `blocked_live_apply_failed`
* `blocked_actual_diff_to_ledger_failed`
* `blocked_dual_zero_failed`
* `blocked_build_time_execution_reach_graph_failed`
* `blocked_focused_validator_failed`
* `blocked_current_route_scope_unclear`
* `blocked_required_validation_adoption_unapproved`
* `blocked_required_validation_approval_token_state_invalid`
* `blocked_surface_boundary_examples_missing`
* `blocked_expected_form_input_unpinned`
* `blocked_upstream_roadmap_seal_pending`
* `blocked_execution_contract_applicability_unconfirmed`
* `blocked_completion_external_gate_not_ready`
* `blocked_independent_review_failed`
* `independent_review_pending_external_gate`
* `rolled_back_after_failed_live_apply`
* `rolled_back_after_apply_equivalence_failure`
* `revised_plan_needed`

If actual live mutation count is `0`, that is not failure. The valid complete claim becomes:

```text
live reflection verified / no live mutation required
```

and not:

```text
live mutation completed
```
