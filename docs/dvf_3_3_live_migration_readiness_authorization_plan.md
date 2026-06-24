# Implementation Plan

> Status: planned / roadmap-derived / pre-apply authorization plan / no live mutation performed
> 작성일: 2026-06-20
> Roadmap input: `C:/Users/MW/.codex/attachments/cc9cd507-845f-458e-9cab-a941f743a537/pasted-text.txt` / sha256 `C0A9A230A8EEBBC56AC298879F8AA25F5AA291F9C811C068C14D8D0E9B89A24E`
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Execution contract input: `docs/EXECUTION_CONTRACT.md` / sha256 `A185BBD78EB849B0310D9AADC9102CB156B892513266FAC0EC7903EB3D3A9493`
> Compatibility target: `docs/dvf_3_3_live_migration_readiness_execution_plan.md` / sha256 `3B1D1D9C4481FD8CE3755314E33589E10FEEFB9789C06C01FD82B0B38D4897F0`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`

---

## 1. Objective

DVF 3-3 `migrated=153` terminal projection에 대해 live apply를 열 수 있는지 기계적으로 판정하는 pre-apply authorization evidence chain을 만든다.

이 계획은 live migration execution 계획이 아니다. 목표는 `docs/dvf_3_3_live_migration_readiness_execution_plan.md`가 소비할 수 있는 다음 final verdict 중 하나를 산출하는 것이다.

```text
phase4_live_apply_allowed=true
live_execution_round_apply_allowed=true
downstream_predecessor_status=ready_for_phase4_live_apply
authorization_plan_alias=ready_for_live_execution_round
```

또는

```text
phase4_live_apply_allowed=false
live_execution_round_apply_allowed=false
downstream_predecessor_status=blocked_before_live_apply
blocked_* reason / row / evidence artifact
```

또는 모든 row가 already-satisfied evidence-only 상태라면:

```text
verdict=no_live_work
phase4_live_apply_allowed=false
live_execution_round_apply_allowed=false
downstream_predecessor_status=blocked_before_live_apply
blocker_kind=no_live_mutation_work_remaining
reason=all rows evidence-only; no live mutation work remains
```

이번 round는 authorization packet을 만드는 것이며, live mutation 결과물을 만드는 것이 아니다. `phase4_live_apply_allowed=true`와 `live_execution_round_apply_allowed=true`는 후속 live execution round를 열 수 있다는 뜻으로만 읽고, live apply 실행, live migration completion, current authority cutover, runtime/package/source mutation, release readiness를 의미하지 않는다.

Final authorization semantics use two distinct tokens. The row-accounting / mechanical gate token is not the final authorization token.

```text
internal_authorization_gates_pass iff:
- total_authorization_rows == 153
- blocked_row_count == 0
- unknown_row_count == 0
- pending_row_count == 0
- conditional_row_count == 0
- every row terminal_class is one of:
  - live_mutation_eligible
  - evidence_only
- `live_apply_candidate` is retained only as an authorization-plan alias for `live_mutation_eligible`
- `evidence_only_no_live_apply_needed` is retained only as an authorization-plan alias for `evidence_only`
- every live_mutation_eligible row has complete dry-run / future-live / mirror evidence
- every evidence_only row has explicit no-patch proof
```

`internal_authorization_gates_pass` is necessary but not sufficient for `phase4_live_apply_allowed=true`.

```text
phase4_live_apply_allowed=true iff:
- internal_authorization_gates_pass == true
- live_mutation_eligible_count > 0
- every Change 10 full PASS condition is satisfied
- review_gate_pass == true
- review_gate_kind in {ordinary_independent_review, external_gate}
- reviewed_artifact_hash_coverage == complete
- protected-surface no-mutation passes
- live baseline capture and mirror seed hash match pass
- external_baseline_context_state in {not_relevant_to_migrated153_readiness, sealed_context_consumed}
- dual-163 reconciliation passes
- static no-unclassified residue passes
- dynamic no-live-reach residue passes
- downstream_predecessor_status == ready_for_phase4_live_apply
```

`review_gate_pass` is true only when either ordinary independent review is PASS, or the fallback explicit external gate is PASS with the same artifact-hash, coverage, and independence requirements.

```text
review_gate_pass == true iff:
- ordinary_independent_review_status == PASS
  OR
- external_gate_status == PASS with required schema
```

If any `blocked_*` row exists, final verdict must be:

```text
phase4_live_apply_allowed=false
live_execution_round_apply_allowed=false
downstream_predecessor_status=blocked_before_live_apply
```

If `internal_authorization_gates_pass=true` but independent review / external gate is pending:

```text
closeout_state=implemented_only
phase4_live_apply_allowed=true is forbidden
live_execution_round_apply_allowed=true is forbidden
downstream_predecessor_status=blocked_before_live_apply
```

Plan-local roadmap conflict resolution:

* Phase count: synthesized 10 authorization phases를 유지하되, execution-plan compatibility를 위해 Phase 0 provenance / compatibility preflight를 추가한다.
* Gate order: **surface-first**를 채택한다. hard-forbidden / dirty / dependency / representability blocker를 먼저 닫고, writer capability와 dry-run / mirror proof는 그 이후에 수행한다.
* Equivalence split: dry-run vs future live input equivalence와 mirror apply equivalence를 별도 validation unit으로 분리한다.
* Dependency gate: Authority / Runtime / Package Dependency Gate를 Consumer-Only Representability와 독립 phase로 둔다.
* Independent review / external gate: ordinary independent review를 기본값으로 둔다. External gate는 fallback이며, 사용할 경우 independent review와 같은 hash / coverage / independence schema를 만족해야 한다. Review / external gate pending 상태는 실패가 아니지만 authorization PASS가 아니다.
* Terminal class vocabulary: execution-plan canonical values are `live_mutation_eligible`, `evidence_only`, and `blocked`. Authorization-plan aliases `live_apply_candidate`, `evidence_only_no_live_apply_needed`, and exact `blocked_*` reasons may appear only with the canonical mapping.
* PASS packet: `ready_for_phase4_live_apply_packet.json`은 모든 gate가 PASS이고 `review_gate_pass=true`일 때만 생성한다. `ready_for_live_execution_round_packet.json`은 compatibility alias일 뿐이다.
* Downstream predecessor status: final output must be exactly `ready_for_phase4_live_apply` or `blocked_before_live_apply`.
* No-live-work status: if `live_mutation_eligible_count == 0` and `blocked_row_count == 0`, emit `verdict=no_live_work`, `blocker_kind=no_live_mutation_work_remaining`, keep both apply-allowed booleans false, and do not create a PASS packet.
* Dual-zero residue: final authorization validation에 static no-unclassified residue와 dynamic no-live-reach residue를 포함한다.
* Closeout state: `EXECUTION_CONTRACT.md`의 allowed closeout states만 사용한다. 좁은 완료 claim은 새 state가 아니라 `complete` + `authorization_verdict_complete` claim label + validation ceiling으로 표현한다. `authorization_verdict_complete` is a claim label, not a closeout state.

Plan artifact:

* `docs/dvf_3_3_live_migration_readiness_authorization_plan.md`

Primary evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_authorization/`

Execution-plan compatibility root:

* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/`

When this plan is implemented together with `docs/dvf_3_3_live_migration_readiness_execution_plan.md`, that execution-plan root is canonical for shared evidence. Shared evidence canonical writer is the execution-plan root. Authorization-root artifacts are plan-local, references, mirrors, or derived compatibility mappings only. Final reports must include a compatibility manifest mapping every authorization artifact to the execution-plan artifact family or an explicit not-applicable reason.

---

## 2. Scope

이 계획은 `migrated=153` rows만 authorization scope로 소비하는 pre-apply authorization round다.

포함 범위:

* `migrated=153` authorization scope lock
* terminal disposition / readiness / sandbox evidence row identity crosswalk
* `153`과 두 개의 `163` axis의 row-level relationship 검증
* `actual_apply_eligible (163)`와 `readiness sandbox mutation (163)`의 denominator axis 분리
* input normalization drift detection
* sandbox evidence / diff-to-ledger reconciliation
* hard-forbidden surface classification
* dirty target isolation
* current live target baseline read-only capture
* authority / runtime / package dependency classification
* consumer-only representability classification
* live writer capability proof without apply
* dry-run patch bundle generation
* dry-run vs future live input equivalence proof
* mirror apply equivalence proof on isolated mirror target only
* Phase 9 `pre_review_gate_pass` / `authorization_candidate` seal
* final binary authorization verdict
* `live_execution_round_apply_allowed` alias
* `ready_for_phase4_live_apply` / `blocked_before_live_apply` predecessor status seal
* `no_live_work` verdict when all rows are evidence-only and no mutation work remains
* exact blocked reason index
* independent review handoff packet
* external gate schema, if used
* canonical roadmap input path / sha256 binding
* sealed input provenance manifest
* external baseline context snapshot and blocker classification
* downstream live-readiness execution compatibility mapping
* final claim boundary

### Explicitly Out Of Scope

* actual Phase 4 live apply
* live migration execution
* source facts / decisions / rendered / Lua bridge / runtime chunk / package mutation
* current authority cutover reopen
* successor baseline regeneration
* frozen 2105 predecessor recovery
* legacy 2105 baseline restoration as a prerequisite for readiness PASS
* Terminal Disposition or Denominator Lock readjudication
* `migrated=153` outside broad universe redisposition
* `no-op`, `diagnostic-only`, `historical-only` row promotion
* required-validation manifest live adoption
* live `current_route_required_validations.json` mutation
* manual in-game validation
* release / package / Workshop / B42 readiness declaration
* semantic quality improvement
* public-facing text quality acceptance
* architecture redesign
* unrelated refactor
* monolith / legacy bridge / stale quarantine fallback restoration
* staging / diagnostic / generated evidence current-authority promotion

---

## 3. Non-Goals

* `migrated=153`을 live execution count로 해석하지 않는다.
* `migrated=153`을 live migration completion으로 선언하지 않는다.
* `163 sandbox mutation rows`를 live completion evidence로 승격하지 않는다.
* `153`과 `163`의 관계를 count equality로 치환하지 않는다.
* `actual_apply_eligible (163)`와 `readiness sandbox mutation (163)`을 같은 denominator axis로 collapse하지 않는다.
* sandbox mutation membership만으로 row를 `live_mutation_eligible`로 승격하지 않는다.
* dry-run patch bundle을 live mutation evidence로 세지 않는다.
* mirror apply result를 live current surface mutation으로 세지 않는다.
* current source / rendered / runtime / package authority surface를 authorization target으로 열지 않는다.
* unknown / ambiguous / unmapped / orphan diff를 silent pass하지 않는다.
* hard-forbidden surface를 automatic repair나 silent skip으로 넘기지 않는다.
* dirty target overlap을 warning-only로 통과시키지 않는다.
* required-validation candidate patch를 live required-validation adoption으로 표현하지 않는다.
* final authorization report를 deployment, Workshop, B42, release, semantic quality, public text acceptance 근거로 쓰지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 기준이다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 current Iris / DVF readpoint를 따른다.
* DVF 3-3 current authority chain은 `source -> facts -> decisions -> rendered -> Lua bridge -> runtime chunks`로 유지한다.
* DVF/QG는 오프라인 생산 / 검문 체계이며, runtime 즉석 설명 생성 장치가 아니다.
* current runtime deployable authority는 monolith나 legacy bridge가 아니라 current chunk manifest + chunk files 기준이다.
* Denominator roles are not interchangeable:
  * `1062`: executing consumer universe
  * `311`: readiness change-required audit subset
  * `actual_apply_eligible (163)`: apply-relevant eligibility axis
  * `readiness sandbox mutation (163)`: sandbox/readiness mutation evidence axis
  * `153`: terminal migrated projection and this plan's authorization scope
* Terminal split is read-only input:

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

* `migrated=153` is not automatically a live mutation target count.
* A row can become `live_mutation_eligible` only if all pre-apply gates prove that it is grounded in `actual_apply_eligible (163)` membership, consumer-only representable, not dirty, not hard-forbidden, not authority/runtime/package dependent, and covered by dry-run/future-live/mirror equivalence evidence. `readiness sandbox mutation (163)` membership alone cannot promote a row to `live_mutation_eligible`.
* `live_apply_candidate` is a plan-local alias for `live_mutation_eligible`; new machine artifacts must emit the execution-plan canonical value.
* `actual_apply_eligible (163)` and `readiness sandbox mutation (163)` must be reconciled by row identity before candidate promotion.
* `evidence_only` rows are valid authorization terminal rows but cannot enter a patch bundle. `evidence_only_no_live_apply_needed` is a plan-local alias only. Evidence-only classification is defined by desired-state vs current live-state read-only comparison plus explicit no-patch proof.
* Any unsupported row shape, path class, dependency class, identity drift, input drift, diff drift, writer gap, dry-run mismatch, or mirror divergence becomes exact `blocked_*`.
* Candidate required-validation evidence remains candidate-only unless a separate approval explicitly adopts it.
* The local roadmap attachment is a drafting input. Phase 0 must bind or copy it under the evidence root and record whether the input is a sealed owner artifact, draft roadmap, or model-authored synthesis. A draft / non-sealed input can guide tooling work but cannot by itself satisfy independent review or final `phase4_live_apply_allowed=true`.
* Canonical roadmap input binding is required before final authorization PASS. Missing binding or missing sealed provenance keeps `phase4_live_apply_allowed=false`.
* Current live target baseline must be captured read-only before dry-run or mirror proof. Mirror seed must match the captured live baseline hash, and the PASS packet must embed baseline hash and drift invalidation conditions.
* Authorization PASS is point-in-time. Any live target drift after baseline capture invalidates the PASS packet unless a successor authorization round revalidates the baseline.
* Dirty working tree changes outside this plan are preserved and never overwritten by authorization tooling.
* Baseline context is recorded for blocker classification only. This plan must not require legacy 2105 baseline restoration. If baseline context blocks migrated=153 expected-form derivation, target classification, consumer-only representability, dirty target isolation, or dry-run/apply equivalence, the affected row or global gate becomes `blocked_by_external_baseline_context`.
* External baseline context final PASS states are limited to `not_relevant_to_migrated153_readiness` and `sealed_context_consumed`.
* `context_blocks_readiness` forces exact `blocked_by_external_baseline_context` evidence.
* `unresolved_context_for_followup` forces `phase4_live_apply_allowed=false` even if no row-level blocker has been materialized yet.
* Independent review and author adoption are separate states. Ordinary independent review is the default completion gate. Explicit external gate is a fallback only, and if used it must satisfy the same schema:
  * declared review / gate artifact path
  * reviewed artifact hash list
  * reviewer / source identity
  * reviewer is not roadmap author, plan author, or execution author
  * complete Phase 1-10 final artifact coverage
  * mismatch, missing hash, partial review, or unclear independence means not PASS
  * author adoption alone cannot satisfy this gate
* Authorization-level `blocked_*` rows do not reopen, revise, or contradict the sealed Terminal Disposition split where `blocked=0`; they are a separate pre-apply authorization axis.
* Downstream execution-plan compatibility vocabulary is fixed:
  * `live_mutation_eligible` maps to downstream `live_mutation_required`.
  * `evidence_only` maps to downstream `live_verified_already` when expected form already matches, or `excluded_non_live_target` when the row has positive non-live evidence.
  * `blocked_*` maps to downstream `live_blocked` or `live_ambiguous` with exact reason.
* Downstream predecessor status is fixed:
  * `ready_for_phase4_live_apply` requires all pre-apply gates PASS, frozen dry-run patch bundle exists, live writer capability is proven, hard-forbidden target count is `0`, dirty target overlap is absent or isolated, review gate status is explicit PASS, external baseline context is non-blocking, and this plan's final authorization seal permits Phase 4 opening.
  * `blocked_before_live_apply` is emitted for any failed gate, missing frozen patch bundle, missing live writer capability proof, unresolved row status, `review_gate_pass=false`, review gate pending, or `no_live_work`.
* The downstream execution plan must consume this round as predecessor evidence only. It must not count this round's sandbox/readiness evidence as live completion and must not rederive targets from mutable state if a frozen patch bundle was sealed.
* `EXECUTION_CONTRACT.md` compliance is required for closeout disclosure, evidence, validation ceiling, allowed closeout state, and non-claim language. Bound vocabulary check is:
  * closeout states: `complete`, `partial`, `implemented_only`, `blocked`
  * `authorization_verdict_complete`: plan-local claim label only, not a closeout state

---

## 5. Repository Areas Affected

### Code

Planned implementation may add or update focused offline tooling under:

* `Iris/build/description/v2/tools/build/`
* `Iris/build/description/v2/tests/`

Expected tooling families include:

* authorization scope materializer
* row identity crosswalk validator
* input normalization drift validator
* sandbox diff-to-ledger reconciler
* surface classifier
* dirty target isolation validator
* authority/runtime/package dependency classifier
* consumer-only representability validator
* no-write live writer capability probe
* dry-run patch bundle generator
* dry-run / future-live equivalence validator
* mirror apply equivalence validator
* final authorization report validator

No runtime Lua, source authority, rendered authority, package payload, live target, or current required-validation manifest mutation is planned by this authorization round.

### Docs

* `docs/dvf_3_3_live_migration_readiness_authorization_plan.md`
* `docs/dvf_3_3_live_migration_readiness_execution_plan.md` as compatibility target
* Optional execution docs produced by the later round:
  * `docs/dvf_3_3_live_migration_readiness_authorization_claim_boundary.md`
  * `docs/dvf_3_3_live_migration_readiness_authorization_ledger_packet.md`
  * `docs/dvf_3_3_live_migration_readiness_authorization_closeout.md`
  * `docs/dvf_3_3_live_migration_readiness_policy.md`
  * `docs/dvf_3_3_live_migration_readiness_claim_boundary.md`
  * `docs/dvf_3_3_live_migration_readiness_ledger_packet.md`

### Config

* No live config mutation.
* No live required-validation manifest adoption.
* Live `Iris/_docs/round3/current_route_required_validations.json` must remain unchanged if inspected or snapshotted.
* Candidate validation or adoption evidence may be written only under the staging evidence root.

### Generated Artifacts

Primary generated artifact root:

* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_authorization/`

Expected subdirectories:

* `phase0_execution_compatibility/`
* `phase1_scope_identity/`
* `phase2_input_drift/`
* `phase3_sandbox_reconciliation/`
* `phase4_surface_classification/`
* `phase5_baseline_dirty/`
* `phase6_dependency_gate/`
* `phase7_representability/`
* `phase8_writer_capability/`
* `phase9_equivalence/`
* `phase10_final_authorization/`

Execution-plan compatibility artifacts:

* `phase0_execution_compatibility/roadmap_input_binding.json`
* `phase0_execution_compatibility/sealed_input_provenance_manifest.json`
* `phase0_execution_compatibility/external_baseline_context_snapshot.json`
* `phase0_execution_compatibility/live_consumer_execution_compatibility_mapping.json`
* `phase0_execution_compatibility/external_gate_requirements_manifest.json`
* `phase8_writer_capability/live_writer_capability_contract.json`
* `phase9_equivalence/pre_review_gate_report.json`
* `phase10_final_authorization/live_consumer_phase0_3_handoff_packet.json`
* `phase10_final_authorization/pre_apply_authorization_evidence_manifest.json`
* `phase10_final_authorization/downstream_predecessor_status.json`

---

## 6. Planned Changes

### Change 0 - Execution-Plan Compatibility / Provenance Preflight

Purpose:

Bind this authorization plan to `docs/dvf_3_3_live_migration_readiness_execution_plan.md` and create the provenance / compatibility artifacts that downstream readiness execution tooling can consume without reinterpreting sandbox evidence as live completion.

Files:

* `Iris/build/description/v2/tools/build/*compatibility*`
* `Iris/build/description/v2/tests/*compatibility*`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_authorization/phase0_execution_compatibility/`

Implementation Notes:

* Record `docs/dvf_3_3_live_migration_readiness_execution_plan.md` path and sha256.
* Record `execution_plan_review_status` with value in `{sealed, reviewed, draft, unknown}`. Unless status is `sealed` or `reviewed`, final `phase4_live_apply_allowed=true` is forbidden.
* Bind or copy the roadmap input under the evidence root as `canonical_roadmap_input.md` and record `roadmap_input_binding.json`.
* Record `sealed_input_provenance_manifest.json` with exact path and sha256 for every consumed source artifact.
* Write `live_consumer_execution_compatibility_mapping.json` mapping authorization artifacts to the execution plan's Phase 0-3 predecessor families.
* Write `external_gate_requirements_manifest.json` with values limited to `satisfied`, `pending_external`, `blocked`, or `not_applicable_with_reason`.
* Record `external_baseline_context_snapshot.json` before row-level gates. Allowed context states are `not_relevant_to_migrated153_readiness`, `sealed_context_consumed`, `context_blocks_readiness`, or `unresolved_context_for_followup`.
* Treat `context_blocks_readiness` as `blocked_by_external_baseline_context`.
* Treat `unresolved_context_for_followup` as a final PASS blocker: `phase4_live_apply_allowed=false` and `downstream_predecessor_status=blocked_before_live_apply`.
* Allow final PASS only when `external_baseline_context_state` is `not_relevant_to_migrated153_readiness` or `sealed_context_consumed`.
* Snapshot live `Iris/_docs/round3/current_route_required_validations.json` if present and require unchanged hash at final seal.
* Define execution-compatible terminal class mapping:
  * `live_apply_candidate` -> `live_mutation_eligible`
  * `evidence_only_no_live_apply_needed` -> `evidence_only`
  * exact `blocked_*` -> `blocked`
* Define execution-compatible final status mapping:
  * PASS -> `ready_for_phase4_live_apply`
  * any blocker / review pending / no-live-work -> `blocked_before_live_apply`
* Missing canonical roadmap binding, missing sealed provenance, or unmapped downstream compatibility family keeps `phase4_live_apply_allowed=false`.
* Missing, draft, or unknown execution plan review status keeps `phase4_live_apply_allowed=false`.

Validation:

* compatibility target path exists
* compatibility target sha256 matches recorded hash
* execution plan review status is recorded and is one of `sealed`, `reviewed`, `draft`, or `unknown`
* final PASS requires execution plan review status in `{sealed, reviewed}`
* canonical roadmap input exists and sha256 matches
* sealed provenance manifest has no missing path or hash
* every required downstream predecessor family is mapped or explicitly not applicable
* execution vocabulary contains no unmapped authorization-only terminal class
* external baseline context is classified
* final PASS requires external baseline context state in `{not_relevant_to_migrated153_readiness, sealed_context_consumed}`
* `context_blocks_readiness` forces `blocked_by_external_baseline_context`
* `unresolved_context_for_followup` forces `phase4_live_apply_allowed=false`
* required-validation manifest hash is unchanged if snapshotted

Expected Deliverables:

* `canonical_roadmap_input.md`
* `roadmap_input_binding.json`
* `sealed_input_provenance_manifest.json`
* `execution_plan_compatibility_status.json`
* `external_baseline_context_snapshot.json`
* `live_consumer_execution_compatibility_mapping.json`
* `external_gate_requirements_manifest.json`
* compatibility / provenance tests

---

### Change 1 - Authorization Scope / Row Identity Lock

Purpose:

Lock `migrated=153` as the only authorization scope and bind it to terminal disposition, actual-apply eligibility, readiness, and sandbox evidence by row identity.

Files:

* `Iris/build/description/v2/tools/build/*authorization_scope*`
* `Iris/build/description/v2/tests/*authorization_scope*`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_authorization/phase1_scope_identity/`

Implementation Notes:

* Materialize the `migrated=153` row list.
* Assign stable row identity fields:
  * executing consumer member row id
  * terminal disposition
  * actual_apply_eligible_row_id_163
  * readiness row id
  * readiness_sandbox_mutation_row_id_163
  * consumer path
  * target surface kind
  * source ledger ref
  * expected patch identity
* Consume the Phase 0 roadmap binding and sealed provenance manifest; do not rebind source identity in Phase 1.
* Verify `actual_apply_eligible (163)` and `readiness sandbox mutation (163)` are linked by row identity, not count equality.
* Verify `153` is linked to each `163` axis by row identity, not by count equality.
* Record `163 - 153` residual rows as `intentionally_out_of_scope` in the reconciliation report.
* Ground `live_mutation_eligible` promotion in `actual_apply_eligible_row_id_163`; sandbox mutation membership alone is never enough.
* Write `command_surface_mapping.for_authorization.json` with every planned command surface, owner tool, expected input, expected output, no-live-mutation status, and blocking condition.
* Write `authorization_validation_command_matrix.json` with command, expected artifact, blocking condition, expected exit code, and exit code source for every validation command.
* Fail loud if any broad `1062` row enters authorization scope without terminal `migrated` identity.

Validation:

* `153 / 153` mapped
* unmapped row = 0
* duplicate row = 0
* extra readiness row in authorization scope = 0
* broad `1062` universe contamination = 0
* `actual_apply_eligible (163)` mapped independently from `readiness sandbox mutation (163)`
* `actual_apply_eligible (163)` vs `readiness sandbox mutation (163)` row-identity reconciliation pass
* sandbox-only membership `live_mutation_eligible` promotion = 0
* `163 - 153` residual rows recorded as `intentionally_out_of_scope`
* command surface mapping content schema valid
* validation command matrix content schema valid
* validation command matrix includes command / expected artifact / blocking condition / exit code source
* row identity hash deterministic

Expected Deliverables:

* `authorization_scope_manifest.json`
* `migrated_153_row_crosswalk.jsonl`
* `153_163_reconciliation_report.json`
* `dual_163_axis_reconciliation_report.json`
* Phase 0 `roadmap_input_binding.json` consumed, not regenerated
* Phase 0 `canonical_roadmap_input.md` consumed, not regenerated
* `command_surface_mapping.for_authorization.json`
* `authorization_validation_command_matrix.json`
* row identity / crosswalk integrity test

---

### Change 2 - Input Normalization Drift Gate

Purpose:

Verify terminal disposition, readiness / sandbox ledger, and future live input are looking at the same normalized row universe.

Files:

* `Iris/build/description/v2/tools/build/*input_normalization*`
* `Iris/build/description/v2/tests/*input_normalization*`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_authorization/phase2_input_drift/`

Implementation Notes:

* Rejoin terminal migrated rows with reconciled input manifest.
* Fix normalized row shape and canonical path rules.
* Compute row-level input fingerprints.
* Compare prior readiness input and current authorization input.
* Terminalize drift rows as `blocked_input_drift` or `blocked_input_normalization_drift`.

Validation:

* input row count = 153
* terminal row join coverage = 153 / 153
* readiness evidence join coverage = 153 / 153
* normalized path canonicalization deterministic
* fingerprint stable
* drift rows are 0 or exact blocked rows

Expected Deliverables:

* `input_normalization_contract.md`
* `normalized_authorization_input.jsonl`
* `input_drift_report.json`
* `blocked_input_drift_rows.jsonl`
* input drift validator

---

### Change 3 - Sandbox Evidence / Diff-to-Ledger Reconciliation

Purpose:

Map existing sandbox / readiness mutation evidence exactly onto the final authorization row identity and close diff-to-ledger drift.

Files:

* `Iris/build/description/v2/tools/build/*sandbox*`
* `Iris/build/description/v2/tools/build/*diff_to_ledger*`
* `Iris/build/description/v2/tests/*sandbox*`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_authorization/phase3_sandbox_reconciliation/`

Implementation Notes:

* Project sandbox mutation evidence to the `migrated=153` scope.
* Remap sandbox actual diff to row-level authorization ledger.
* Verify expected diff, actual diff, target file, and patch hunk identity.
* Block orphan diff, unmapped diff, and duplicate ownership.
* Preserve the `sandbox_not_live_completion` claim boundary on every evidence record.

Validation:

* migrated rows mapped to sandbox evidence = 153 / 153
* orphan sandbox diff = 0
* unmapped expected diff = 0
* duplicate patch ownership = 0
* actual diff-to-ledger pass
* sandbox evidence claim boundary present

Expected Deliverables:

* `sandbox_evidence_repair_report.json`
* `sandbox_diff_to_authorization_ledger.jsonl`
* `sandbox_orphan_diff_report.json`
* `sandbox_claim_boundary.md`
* diff-to-ledger reconciliation validator

---

### Change 4 - Hard-Forbidden Surface Classification

Purpose:

Classify every target path before writer proof so forbidden current-authority and package surfaces cannot enter live input.

Files:

* `Iris/build/description/v2/tools/build/*surface_classification*`
* `Iris/build/description/v2/tests/*surface_classification*`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_authorization/phase4_surface_classification/`

Implementation Notes:

Hard-forbidden categories include:

* current source facts
* current decisions
* current rendered output
* protected current-output set
* Lua bridge current authority
* runtime chunk manifest
* runtime chunk files
* package peer
* monolith runtime output
* legacy bridge artifact
* stale quarantine artifact
* diagnostic-only artifact
* historical reproduction artifact
* current-route required-validation manifest live file

Rows mapped to hard-forbidden surfaces become `blocked_hard_forbidden_surface`.

Validation:

* all 153 target paths classified
* unclassified target path = 0
* classification deterministic
* protected current authority changed_count = 0
* forbidden rows excluded from future live apply input

Expected Deliverables:

* `surface_classification_policy.md`
* `hard_forbidden_surface_classification.jsonl`
* `surface_classification_report.json`
* `blocked_hard_forbidden_surface_rows.jsonl`
* path classifier tests

---

### Change 5 - Live Baseline Capture / Dirty Target Isolation Gate

Purpose:

Capture the current live target baseline read-only and prevent future live apply from overwriting dirty target files or baseline-mismatched target content.

Files:

* `Iris/build/description/v2/tools/build/*dirty_target*`
* `Iris/build/description/v2/tests/*dirty_target*`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_authorization/phase5_baseline_dirty/`

Implementation Notes:

* Capture current live target baseline read-only before dry-run or mirror proof.
* Compute target path baseline hashes from captured live target content.
* Inspect git status, filesystem snapshot, and expected target hash.
* Include ignored/generated target paths in the filesystem snapshot, not only git status.
* Compute authorization target vs dirty file overlap.
* Terminalize overlap rows as `blocked_dirty_target_overlap`.
* Keep unrelated dirty files as evidence / warnings only.
* Treat protected surface dirty state as hard fail.
* Define authorization staleness: any target drift after baseline capture invalidates PASS packet unless revalidated by a successor authorization run.

Validation:

* current live target baseline captured read-only
* target dirty overlap count = 0 for allow path
* protected surface dirty count = 0
* missing target baseline either expected or blocked
* target hash matches captured live baseline
* captured live baseline hash is available to dry-run and mirror phases
* dirty target rows excluded from live apply input
* ignored/generated target dirty state included in snapshot
* baseline drift invalidation rule recorded

Expected Deliverables:

* `live_target_baseline_capture.jsonl`
* `dirty_target_isolation_policy.md`
* `authorization_staleness_policy.md`
* `dirty_target_overlap_report.json`
* `target_baseline_hashes.jsonl`
* `blocked_dirty_target_overlap_rows.jsonl`
* dirty target validator

---

### Change 6 - Authority / Runtime / Package Dependency Gate

Purpose:

Verify that candidate consumer migration rows do not depend on current authority, runtime deployable, package peer, or required-validation live manifest mutation.

Files:

* `Iris/build/description/v2/tools/build/*dependency*`
* `Iris/build/description/v2/tests/*dependency*`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_authorization/phase6_dependency_gate/`

Implementation Notes:

* Build row-level desired-state dependency graph.
* Detect source facts / decisions / rendered / Lua bridge / runtime chunk / package peer dependency.
* Block rows with exact axis-specific reason:
  * `blocked_authority_dependency`
  * `blocked_runtime_dependency`
  * `blocked_package_dependency`
  * `blocked_authority_runtime_package_dependency`
* Treat required-validation live adoption need as blocker unless separately approved outside this plan.
* Scan package route for current-looking stale artifact and monolith re-entry.

Validation:

* authority dependency rows classified
* runtime dependency rows classified
* package dependency rows classified
* current authority changed_count = 0
* runtime chunk changed_count = 0
* package peer changed_count = 0
* monolith forbidden scan pass
* stale bridge forbidden scan pass

Expected Deliverables:

* `authority_runtime_package_dependency_policy.md`
* `authority_runtime_package_dependency_report.json`
* `blocked_authority_dependency_rows.jsonl`
* `blocked_runtime_dependency_rows.jsonl`
* `blocked_package_dependency_rows.jsonl`
* package / runtime forbidden-surface scan

---

### Change 7 - Consumer-Only Representability Gate

Purpose:

Determine whether each migrated row can be completed as a consumer-only mutation, evidence-only result, or exact blocked state.

Files:

* `Iris/build/description/v2/tools/build/*representability*`
* `Iris/build/description/v2/tests/*representability*`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_authorization/phase7_representability/`

Implementation Notes:

* Convert row desired state into the consumer representation model.
* Distinguish consumer target from source authority, generated evidence, runtime payload, and package peer.
* Keep only consumer-only rows as `live_mutation_eligible`.
* Terminalize rows requiring no mutation as `evidence_only` only when desired-state vs captured current-live-state read-only comparison proves no patch is needed.
* Emit compatibility alias fields only as secondary fields:
  * `authorization_alias=live_apply_candidate` for `live_mutation_eligible`
  * `authorization_alias=evidence_only_no_live_apply_needed` for `evidence_only`
* Emit explicit no-patch proof for every evidence-only row.
* Terminalize non-representable rows as `blocked_not_consumer_only_representable`.

Validation:

* all 153 rows assigned one representability class
* consumer-only rows have target path, patch hash, baseline hash
* evidence-only rows have desired-state vs captured current-live-state proof
* evidence-only rows have explicit no-patch proof
* evidence-only rows have no patch bundle entry
* non-representable rows blocked with reason
* unknown representability rows = 0

Expected Deliverables:

* `consumer_only_representability_policy.md`
* `consumer_only_representability_report.json`
* `live_mutation_eligible_rows.jsonl`
* `evidence_only_rows.jsonl`
* `evidence_only_no_patch_proof.jsonl`
* `blocked_not_consumer_only_representable_rows.jsonl`
* representability validator

---

### Change 8 - Live Writer Capability Contract Without Apply

Purpose:

Prove that the live writer can support required safety contracts without touching live targets.

Files:

* `Iris/build/description/v2/tools/build/*writer*`
* `Iris/build/description/v2/tests/*writer*`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_authorization/phase8_writer_capability/`

Implementation Notes:

Writer capability must prove:

* `no_write_preflight`
* `dry_run_plan`
* `mirror_apply_only`
* `live_apply_disabled`
* same-operation-plan writer identity contract: dry-run and mirror apply differ only by sink
* normalized live input load
* target path resolution
* hard-forbidden surface refusal
* dirty target refusal
* expected baseline hash verification
* patch bundle generation
* row-level ledger emission
* actual diff-to-ledger validation hook
* atomic write plan generation
* restore plan generation
* no-write mode no-mutation guarantee

Unsupported rows become `blocked_writer_capability_unproven` or a more specific `blocked_live_writer_capability_*` reason.

Validation:

* no-write preflight changed_count = 0
* protected surface changed_count = 0
* writer supports all required row shapes or blocks unsupported rows
* writer refuses forbidden rows
* writer refuses dirty rows
* writer version / policy version recorded
* planner / resolver / serializer / mapper / operation-plan / target-set hashes recorded
* live apply command remains disabled

Expected Deliverables:

* `live_writer_capability_contract.md`
* `live_writer_capability_contract.json`
* `live_writer_no_write_preflight_report.json`
* `writer_supported_row_shapes.json`
* `writer_refusal_matrix.jsonl`
* `blocked_writer_capability_unproven_rows.jsonl`
* writer capability tests

---

### Change 9 - Pre-Review Equivalence Gates: 9A Dry-Run / Future Live Input, 9B Mirror Apply

Purpose:

Prove two separate equivalence axes without live mutation, then seal the pre-review candidate state consumed by the execution plan: dry-run patch bundle vs future live input, and mirror apply result vs row-level ledger.

Files:

* `Iris/build/description/v2/tools/build/*dry_run*`
* `Iris/build/description/v2/tools/build/*mirror*`
* `Iris/build/description/v2/tests/*equivalence*`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_authorization/phase9_equivalence/`

Implementation Notes:

Phase 9A - dry-run / future-live input equivalence:

* Generate dry-run patch bundle only from `live_mutation_eligible` rows.
* Generate future live apply input manifest from the dry-run bundle.
* Compare row set, ordering, target path, baseline hash, patch hash, writer version, policy version, and expected diff hash.
* Block live input not derived from the dry-run bundle.
* Use captured live target baseline hashes from Phase 5 as the only baseline identity.
* Freeze the dry-run bundle hash and future live input manifest hash for downstream consumption.

Phase 9B - mirror apply equivalence:

* Apply bundle only to an isolated mirror target.
* Seed mirror target from captured current live target baseline.
* Verify mirror seed hash equals captured live baseline hash before applying any patch.
* Compare mirror actual diff to row-level ledger.
* Run mirror restore probe.

Phase 9C - pre-review gate:

* Compute `pre_review_gate_pass`.
* Compute `authorization_candidate`.
* Emit `live_consumer_phase0_3_handoff_packet.json` with non-claim fields.
* Keep `phase4_live_apply_allowed=false` until Phase 10 `review_gate_pass=true`.
* If all rows are `evidence_only` and no patch bundle row exists, set `authorization_candidate=false` and emit `verdict=no_live_work` candidate data for Phase 10.

Validation:

9A validation:

* dry-run row count matches authorized candidate row count
* future live input row count matches dry-run row count
* row set hash equal
* patch bundle hash equal
* expected diff hash equal
* target baseline hash equals captured live baseline hash
* writer / policy version equal
* frozen dry-run bundle hash recorded
* future live input manifest is derived from frozen dry-run bundle

9B validation:

* mirror seed hash equals captured live baseline hash
* mirror apply pass
* mirror actual diff-to-ledger pass
* unmapped diff = 0
* orphan diff = 0
* protected surface changed_count = 0
* mirror restore probe pass

9C validation:

* `pre_review_gate_pass=true` only if every internal pre-review gate passes
* `authorization_candidate=true` only if `pre_review_gate_pass=true`, `live_mutation_eligible_count > 0`, and `blocked_row_count == 0`
* `phase4_live_apply_allowed` remains false before Phase 10 review seal
* handoff packet contains non-claim fields for live mutation, current authority cutover, release, Workshop, B42, deployment, and required-validation adoption
* no-live-work candidate is represented without creating a PASS packet

Expected Deliverables:

* `dry_run_patch_bundle_manifest.json`
* `future_live_apply_input_manifest.json`
* `dry_run_live_input_equivalence_report.json`
* `blocked_dry_run_live_input_mismatch_rows.jsonl`
* `mirror_target_manifest.json`
* `mirror_seed_baseline_match_report.json`
* `mirror_apply_equivalence_report.json`
* `mirror_actual_diff_to_ledger_report.json`
* `mirror_restore_probe_report.json`
* `blocked_dry_run_mirror_divergence_rows.jsonl`
* `pre_review_gate_report.json`
* `authorization_candidate_report.json`
* `live_consumer_phase0_3_handoff_packet.json`

---

### Change 10 - Final Authorization Seal

Purpose:

Combine Phase 0-9 results into the execution-plan compatible final seal and handoff packet for a separate live execution round.

Files:

* `Iris/build/description/v2/tools/build/*authorization_report*`
* `Iris/build/description/v2/tests/*authorization_report*`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_authorization/phase10_final_authorization/`
* Optional docs:
  * `docs/dvf_3_3_live_migration_readiness_authorization_claim_boundary.md`
  * `docs/dvf_3_3_live_migration_readiness_authorization_ledger_packet.md`

Implementation Notes:

* Fix final verdict schema.
* Classify all 153 rows into exactly one execution-compatible terminal class.
* Record PASS / FAIL conditions.
* Link every blocked row to exact reason and evidence artifact.
* Generate live execution handoff only when all gates pass and `review_gate_pass=true`.
* Keep live apply command disabled.
* Include independent review / external gate state and certification ceiling.
* Embed captured baseline hashes and drift invalidation conditions in the handoff / PASS packet.
* Ensure `authorization-level blocked_*` is reported as a pre-apply axis and not as a Terminal Disposition rewrite.
* Seal `live_execution_round_apply_allowed` as an alias that exactly equals `phase4_live_apply_allowed`.
* Seal `downstream_predecessor_status` as exactly `ready_for_phase4_live_apply` or `blocked_before_live_apply`.
* Seal `pre_apply_authorization_evidence_manifest.json` for the readiness execution plan.
* Seal `external_baseline_context_verdict.json`; do not require legacy 2105 restoration unless it directly blocks migrated=153 readiness gates.
* If all rows are `evidence_only` and no mutation remains, emit `verdict=no_live_work`, `blocker_kind=no_live_mutation_work_remaining`, keep apply-allowed booleans false, and set `downstream_predecessor_status=blocked_before_live_apply`.

PASS requires:

* total authorization row count = 153
* blocked_row_count = 0
* unknown_row_count = 0
* pending_row_count = 0
* conditional_row_count = 0
* every row terminal class is either `live_mutation_eligible` or `evidence_only`
* `live_mutation_eligible_count > 0`
* input scope locked
* Phase 0 compatibility / provenance binding complete
* row identity complete
* dual-`163` axis reconciliation complete
* input drift absent
* sandbox evidence reconciled
* diff-to-ledger reconciled
* hard-forbidden rows absent from live input
* dirty target overlap absent from live input
* writer capability proven
* dry-run / future live input equivalent
* dry-run / mirror apply equivalent
* mirror actual diff-to-ledger pass
* authority/runtime/package dependency absent from live input
* consumer-only representability pass
* every live_mutation_eligible row has complete dry-run / future-live / mirror evidence
* every evidence_only row has explicit no-patch proof
* protected surface no-mutation pass
* current live baseline captured read-only
* mirror seed baseline hash equals captured live baseline hash
* PASS packet embeds baseline hash and drift invalidation conditions
* review_gate_pass = true
* review_gate_kind in `{ordinary_independent_review, external_gate}`
* reviewed_artifact_hash_coverage = complete
* external_baseline_context_state in `{not_relevant_to_migrated153_readiness, sealed_context_consumed}`
* execution_plan_review_status in `{sealed, reviewed}`
* Phase 9 `authorization_candidate=true`
* `pre_apply_authorization_evidence_manifest.json` complete
* `downstream_predecessor_status=ready_for_phase4_live_apply`
* live `current_route_required_validations.json` hash unchanged if snapshotted

External gate PASS, if used instead of ordinary independent review, requires:

* declared gate artifact path
* reviewed artifact hash list
* reviewer / source identity
* reviewer is not roadmap author, plan author, or execution author
* complete Phase 1-10 final artifact coverage
* mismatch / missing hash / partial review / unclear independence = not PASS
* author adoption alone is not sufficient

Ordinary independent review PASS requires:

* `ordinary_independent_review_status=PASS`
* declared review artifact path
* reviewed artifact hash list
* reviewer / source identity
* reviewer is not roadmap author, plan author, or execution author
* complete Phase 0-10 final artifact coverage
* mismatch / missing hash / partial review / unclear independence = not PASS

Validation:

* final report schema valid
* final row accounting sums to 153
* blocked_row_count = 0 required for `phase4_live_apply_allowed=true`
* any blocked row forces `phase4_live_apply_allowed=false`
* `live_execution_round_apply_allowed` equals `phase4_live_apply_allowed`
* `downstream_predecessor_status=ready_for_phase4_live_apply` requires `phase4_live_apply_allowed=true`
* `downstream_predecessor_status=blocked_before_live_apply` requires `phase4_live_apply_allowed=false`
* `no_live_work` requires `phase4_live_apply_allowed=false`, `live_execution_round_apply_allowed=false`, `blocked_before_live_apply`, and `blocker_kind=no_live_mutation_work_remaining`
* unclassified row = 0
* blocked rows have exact reason
* live mutation eligible rows have complete dry-run and mirror evidence
* evidence-only rows have explicit no-patch proof
* captured baseline hash included in handoff packet
* drift invalidation condition included in handoff packet
* review gate schema valid
* external gate PASS can satisfy `review_gate_pass` without ordinary independent review PASS when the external gate schema is complete
* `phase4_live_apply_allowed=true` requires `review_gate_pass=true`, `review_gate_kind` in `{ordinary_independent_review, external_gate}`, and complete reviewed artifact hash coverage
* final claim boundary embedded
* protected surface no-mutation verdict pass
* static no-unclassified residue pass
* dynamic no-live-reach residue pass
* external baseline context verdict is present
* `phase4_live_apply_allowed=true` requires external baseline context state in `{not_relevant_to_migrated153_readiness, sealed_context_consumed}`
* `unresolved_context_for_followup` forces `phase4_live_apply_allowed=false`
* `context_blocks_readiness` forces `blocked_by_external_baseline_context`
* execution plan review status is present and final PASS requires `{sealed, reviewed}`
* pre-apply authorization evidence manifest complete
* required-validation manifest unchanged verdict present if Phase 0 snapshotted it

Expected Deliverables:

* `final_live_migration_readiness_authorization_report.json`
* `final_live_migration_readiness_report.json` compatibility alias
* `live_execution_authorization_handoff_packet.json`
* `live_consumer_phase0_3_handoff_packet.json` compatibility alias
* `phase4_live_apply_allowed_verdict.md`
* `authorization_claim_boundary.md`
* `blocked_reason_index.jsonl`
* `external_gate_schema_report.json`
* `authorization_baseline_staleness_report.json`
* `external_baseline_context_verdict.json`
* `pre_apply_authorization_evidence_manifest.json`
* `downstream_predecessor_status.json`
* `ready_for_phase4_live_apply_packet.json` only if all gates pass and `review_gate_pass=true`
* `ready_for_live_execution_round_packet.json` compatibility alias only if all gates pass and `review_gate_pass=true`
* final focused tests

---

## 7. Validation Plan

### Automated Validation

This round requires heavy validation.

Planned automated validation includes:

* template section coverage check against `docs/PLAN_TEMPLATE.md`
* `EXECUTION_CONTRACT.md` compliance / disclosure / closeout-state check
* `EXECUTION_CONTRACT.md` allowed closeout state vocabulary check: `complete`, `partial`, `implemented_only`, `blocked`
* `authorization_verdict_complete` verified as claim label only, not closeout state
* roadmap input path / sha256 binding
* sealed input provenance validation
* execution-plan compatibility mapping validation
* external baseline context validation
* external baseline context nonblocking state validation
* live required-validation manifest unchanged validation if snapshotted
* `command_surface_mapping.for_authorization.json` validation
* `authorization_validation_command_matrix.json` content validation: command, expected artifact, blocking condition, expected exit code, and exit code source
* row identity / crosswalk integrity tests
* denominator non-substitution tests for `1062`, `311`, `actual_apply_eligible (163)`, `readiness sandbox mutation (163)`, `153`
* dual-`163` row-identity reconciliation validator
* sandbox-only membership cannot promote `live_mutation_eligible`
* `163 - 153` residual rows recorded as `intentionally_out_of_scope`
* input normalization deterministic tests
* input drift validator
* sandbox diff-to-ledger reconciliation validator
* surface classification tests
* current live target baseline read-only capture validator
* dirty target validator
* ignored/generated target filesystem snapshot validator
* authority/runtime/package dependency scan
* consumer-only representability validator
* evidence-only explicit no-patch proof validator
* writer no-write capability tests
* writer identity equivalence validator
* writer forbidden / dirty refusal tests
* dry-run / future live input equivalence validator
* frozen dry-run bundle hash validation
* mirror apply equivalence validator
* mirror seed vs captured live baseline hash validator
* mirror actual diff-to-ledger validator
* mirror restore probe validator
* Phase 9 `pre_review_gate_pass` / `authorization_candidate` validator
* downstream predecessor status validator
* no-live-work verdict validator
* final authorization schema validation
* final row accounting validation
* `internal_authorization_gates_pass` schema and predicate validation
* `review_gate_pass` schema and predicate validation
* `blocked_row_count == 0` validator for `phase4_live_apply_allowed=true`
* `phase4_true_requires_no_blocked_rows`
* `phase4_false_when_any_blocked_row`
* `phase4_true_requires_review_gate_pass`
* `external_gate_pass_can_satisfy_review_gate_without_independent_review`
* `phase4_true_requires_review_gate_kind_and_complete_hash_coverage`
* `internal_gates_pass_review_pending_forces_implemented_only`
* `live_execution_round_apply_allowed_equals_phase4_live_apply_allowed`
* `ready_for_phase4_live_apply_requires_phase4_true`
* `blocked_before_live_apply_requires_phase4_false`
* `phase4_true_requires_external_baseline_context_state_nonblocking`
* `unresolved_external_baseline_context_forces_phase4_false`
* `context_blocks_readiness_forces_blocked_by_external_baseline_context`
* `no_live_work_requires_no_live_mutation_work_remaining_blocker_kind`
* `execution_plan_review_status_required_for_phase4_true`
* `external_gate_schema_valid`
* `external_gate_artifact_hash_match`
* baseline drift invalidation validator
* protected surface no-mutation validation
* static no-unclassified residue validation
* dynamic no-live-reach residue validation
* Lua syntax check only if Lua files are touched: `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`
* Python unit tests for changed offline tooling

Exact command surfaces must be resolved in Phase 1 before execution closeout claims PASS. Do not claim validation passed unless the exact relevant command exits with code 0.

### Manual Validation

Manual validation is limited to:

* final report readability inspection
* blocked reason index spot check
* independent review / external gate packet inspection
* generated claim boundary inspection
* git diff inspection for no unintended runtime/source/package mutations

### Validation Limits

The following validation is not performed by this plan:

* no live migration apply
* no live runtime mutation validation
* no source facts mutation validation
* no decisions mutation validation
* no rendered output mutation validation
* no runtime chunk replacement validation
* no package peer mutation validation
* no multiplayer validation
* no deployment validation
* no Workshop / B42 / release validation
* no manual in-game QA
* no semantic quality validation
* no public-facing text quality validation
* no full external ecosystem compatibility sweep
* no full runtime equivalence
* no current authority cutover validation

---

## 8. Risk Surface Touch

### Authority Surface

No direct mutation. Existing authority artifacts are read-only inputs. Newly created authorization evidence under staging is not current authority.

### Runtime Behavior Surface

None. Runtime Lua, Browser, Wiki, Tooltip behavior, runtime chunks, and Lua bridge files are not changed.

### Compatibility Surface

No direct compatibility mutation. Consumer target path, import route, dependency, target file hash, and package peer overlap are inspected as pre-apply risk surfaces.

### Sealed Artifact Surface

Existing sealed authority and terminal disposition evidence are read-only inputs. New artifacts are additive authorization evidence.

### Public-Facing Output Surface

None. No user-facing text, UI, tooltip, wiki, package, release, or public description is changed.

---

## 9. Risk Analysis

### Architecture Risk

* Risk: authorization evidence could be misread as current authority mutation.
* Mitigation: every staging artifact and final report must embed the claim boundary that this is pre-apply authorization only.

### Runtime Risk

* Risk: writer capability proof accidentally reaches live targets.
* Mitigation: require `live_apply_disabled`, no-write preflight, mirror-only apply, changed_count = 0, protected surface changed_count = 0.

### Compatibility Risk

* Risk: consumer-only candidate could hide authority/runtime/package dependency.
* Mitigation: dependency gate is independent and runs before writer proof.
* Risk: mirror PASS could be transferred from a stale baseline to live applicability.
* Mitigation: capture live target baseline read-only, seed mirror from that baseline, and invalidate PASS on post-capture drift.

### Regression Risk

* Risk: row identity drift mutates or authorizes the wrong consumer target.
* Mitigation: stable row identity hash, deterministic crosswalk, duplicate/unmapped/orphan diff blockers.
* Risk: dual-`163` axes collapse into a single denominator because counts match.
* Mitigation: keep `actual_apply_eligible_row_id_163` and `readiness_sandbox_mutation_row_id_163` separate and reconcile them by row identity.

### Claim Risk

* Risk: `phase4_live_apply_allowed=true` is overclaimed as release readiness or live completion.
* Mitigation: final verdict and handoff packet must include explicit non-claims and no-live-mutation proof.
* Risk: `phase4_live_apply_allowed=true` is declared after excluding blocked rows from live input.
* Mitigation: `blocked_row_count == 0` is required globally across all 153 authorization rows.

### False Block Risk

* Risk: conservative classification reduces candidate rows.
* Mitigation: exact blocked reasons are preserved as evidence. `phase4_live_apply_allowed=false` is a valid authorization result, not a plan failure.

---

## 10. Rollback Plan

This authorization round does not perform live mutation, so rollback is containment-focused.

* Live source / rendered / runtime / package files are not changed.
* Mirror apply output is deleted or restored using the mirror restore probe.
* Staging evidence and new tooling can be reverted by branch-level revert.
* If final verdict is false, do not rewrite evidence to force PASS. Preserve `phase4_live_apply_allowed=false` and exact `blocked_*` records.
* If input drift is found, record it as fail-loud evidence instead of mutating the input to match.
* If writer capability is unproven, do not partially use the writer.
* If protected surface changed_count is nonzero, stop immediately and record contamination evidence.
* Follow-up live execution remains blocked until a separate plan consumes a PASS authorization packet.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* `docs/EXECUTION_CONTRACT.md` disclosure, evidence, validation ceiling, closeout-state, and non-claim rules are mandatory.
* Hub & Spoke boundaries remain unchanged.
* Iris remains 100% Lua at runtime; offline tooling does not authorize runtime JVM/Lua mixing.
* Runtime / build-time separation must remain intact.
* Current authority ownership must not be bypassed.
* `source -> facts -> decisions -> rendered -> Lua bridge -> runtime chunks` authority chain must not be redefined.
* `1062`, `311`, `actual_apply_eligible (163)`, `readiness sandbox mutation (163)`, and `153` denominators must not be collapsed.
* `actual_apply_eligible (163)` and `readiness sandbox mutation (163)` are distinct denominator axes even if counts match.
* `153` and each `163` axis relation is row identity only, not count equality.
* `live_mutation_eligible` promotion must be grounded in `actual_apply_eligible (163)` membership; sandbox mutation membership alone is insufficient.
* `163 - 153` residual rows are recorded as `intentionally_out_of_scope`, not silently dropped.
* Sandbox / readiness mutation is not live completion.
* No source facts / decisions / rendered / runtime chunk / package mutation.
* Protected current-output set is no-mutation.
* Monolith runtime fallback / legacy bridge fallback / stale bridge fallback must not return.
* Unknown / ambiguous / unmapped / orphan diff must fail loud.
* Hard-forbidden surface must not be repaired or silently skipped.
* Dirty target overlap is an authorization blocker.
* Captured live target baseline is point-in-time evidence; later drift invalidates PASS packet.
* Consumer-only representability is required for `live_mutation_eligible` rows.
* `blocked_row_count == 0` across all 153 authorization rows is required for `phase4_live_apply_allowed=true`.
* `live_execution_round_apply_allowed` must always equal `phase4_live_apply_allowed`.
* `downstream_predecessor_status` must be exactly `ready_for_phase4_live_apply` or `blocked_before_live_apply`.
* `ready_for_phase4_live_apply` requires `phase4_live_apply_allowed=true`; `blocked_before_live_apply` requires `phase4_live_apply_allowed=false`.
* `verdict=no_live_work` requires both apply-allowed booleans false, `downstream_predecessor_status=blocked_before_live_apply`, and `blocker_kind=no_live_mutation_work_remaining`.
* Authorization-level `blocked_*` does not reopen, revise, or contradict sealed Terminal Disposition `blocked=0`.
* `review_gate_pass` with declared artifact path, reviewed hash list, reviewer/source independence, and Phase 0-10 coverage is required for `phase4_live_apply_allowed=true`.
* `review_gate_pass` may be satisfied by ordinary independent review PASS or by external gate PASS with the same required schema.
* Ordinary independent review is the default review gate. Explicit external gate is fallback only.
* `phase4_live_apply_allowed=true` must not require `ordinary_independent_review_status=PASS` when a complete external gate PASS satisfies `review_gate_pass`.
* Author adoption alone cannot satisfy the independent review / external gate requirement.
* `external_baseline_context_state` must be `not_relevant_to_migrated153_readiness` or `sealed_context_consumed` for `phase4_live_apply_allowed=true`.
* `unresolved_context_for_followup` and `context_blocks_readiness` must force `phase4_live_apply_allowed=false`.
* Shared evidence canonical writer is the execution-plan root; authorization-root artifacts are plan-local, references, mirrors, or derived compatibility mappings only.
* No new verdict token / alias / report-name expansion is allowed after this Cycle 4 alignment without a new review round.
* Release / Workshop / B42 / deployment readiness must not be claimed.
* Manual in-game QA, semantic quality, and public-facing text acceptance are outside this scope.

---

## 12. Expected Closeout State

Expected closeout target:

```text
complete
```

`complete` is used only in the `EXECUTION_CONTRACT.md` sense: the governing plan's stated completion condition is met within the declared validation ceiling. The narrow formal claim label is:

```text
authorization_verdict_complete
```

`complete` with `authorization_verdict_complete` means this plan's execution produced one of the valid final authorization terminals:

```text
complete means authorization_verdict_complete only.
complete does not mean live migration completed.
```

```text
phase4_live_apply_allowed=true
live_execution_round_apply_allowed=true
downstream_predecessor_status=ready_for_phase4_live_apply
authorization_plan_alias=ready_for_live_execution_round
```

or:

```text
phase4_live_apply_allowed=false
live_execution_round_apply_allowed=false
downstream_predecessor_status=blocked_before_live_apply
blocked_* reason / row / evidence artifact
```

or:

```text
verdict=no_live_work
phase4_live_apply_allowed=false
live_execution_round_apply_allowed=false
downstream_predecessor_status=blocked_before_live_apply
blocker_kind=no_live_mutation_work_remaining
reason=all rows evidence-only; no live mutation work remains
```

If `internal_authorization_gates_pass=true` but `review_gate_pass=false` or pending, closeout must not claim full authorization PASS. This includes both ordinary independent review pending and external gate pending. The `EXECUTION_CONTRACT.md` closeout state should be:

```text
implemented_only
```

with non-claim text stating `sealed authorization PASS not achieved / review gate pending or failed`, and with:

```text
phase4_live_apply_allowed=false
live_execution_round_apply_allowed=false
downstream_predecessor_status=blocked_before_live_apply
```

If tooling, inputs, or source evidence are missing, closeout should be:

```text
blocked
```

with exact blocker reason and evidence path.

This plan's closeout never means live apply completed, runtime changed, source authority changed, package changed, release readiness achieved, Workshop readiness achieved, or manual in-game QA completed.
