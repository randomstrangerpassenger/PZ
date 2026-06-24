# Implementation Plan

> Status: planned / roadmap-derived / live-readiness pre-apply gate / no live mutation performed
> 작성일: 2026-06-20
> Roadmap input, provisional local paste: `C:/Users/MW/.codex/attachments/b7b91d43-12d5-45fc-8ba9-eb9e0569a3d9/pasted-text.txt` / sha256 `26ADB373C1557EDA9B75CB7D0FBE0411A14E8D7C68D6C71D94DB4AB4759FD9C4`
> Canonical roadmap input binding required before final readiness PASS / before `phase4_live_apply_allowed=true`: `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase0/canonical_roadmap_input.md` / sha256 recorded in `phase0/roadmap_input_binding.json`
> Baseline clarification: Iris is migrating the vNext Baseline into the consumer baseline path. This plan must not require restoration of the legacy 2105 baseline.
> Baseline boundary: this readiness plan records baseline context only when needed for live-readiness blocker classification. Shared disposition consumption and 2105 reentry guard closure belong to later rounds.
> Downstream compatibility target: `docs/dvf_3_3_live_consumer_migration_execution_plan.md` Section 1.1 / Phase 0-3 live-tooling readiness gate.
> Review input: `C:/Users/MW/.codex/attachments/87d412c8-9967-4bea-8337-15287ddd6c2e/pasted-text.txt` / sha256 `474966A3BB64F860A234540E7736F488F30BEE266792E23051E7F1627BDF1B65` / Final Synthesized Review WARN revisions incorporated
> Review input: `C:/Users/MW/.codex/attachments/67f73749-c53f-4fb7-89cd-6208a964e68a/pasted-text.txt` / sha256 `487E24542FB2D195D1C91DBE34E3AB610C6078C98D511C6774C7B357B53E0C94` / PASS-with-minor-revisions review incorporated / seal authorization remains WARN
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`

---

## 1. Objective

DVF 3-3 Terminal Disposition Adjudication의 `migrated=153` terminal projection을 live-readiness 관점에서 다시 판정하고, 후속 live execution round를 열 수 있는지 기계적으로 결정하는 pre-apply gate 체계를 구현한다.

이 계획의 목적은 live migration 실행이 아니다. 목적은 다음 상태를 산출하는 것이다.

```text
migrated=153 terminal projection을 input universe로 잠근다.
각 row를 live-readiness axis에서 live_mutation_eligible / evidence_only / blocked 중 하나로 판정한다.
live writer capability, consumer-only representability, hard-forbidden surface isolation, dirty target isolation, dry-run/apply equivalence, protected surface no-mutation을 gate로 검증한다.
Phase 9에서 pre_review_gate_pass / authorization_candidate를 산출한다.
Phase 10에서 independent_review_status == PASS 이후 final phase4_live_apply_allowed를 봉인한다.
이 round에서는 live mutation을 수행하지 않는다.
downstream live execution plan이 요구하는 `ready_for_phase4_live_apply` 또는 `blocked_before_live_apply` predecessor status를 산출한다.
```

`phase4_live_apply_allowed=true`는 후속 live execution round를 열 수 있다는 readiness verdict일 뿐, live migration completed, live mutation executed, current authority cutover, release readiness, Workshop readiness, B42 readiness를 의미하지 않는다. 혼동을 줄이기 위해 final report에는 `live_execution_round_apply_allowed` alias도 함께 기록한다.

Downstream compatibility는 다음으로 잠근다.

```text
이 계획은 docs/dvf_3_3_live_consumer_migration_execution_plan.md의 Section 1.1 선행과제 독립 실행 라운드다.
성공 상태는 ready_for_phase4_live_apply 또는 blocked_before_live_apply 중 하나다.
ready_for_phase4_live_apply는 Phase 4 live apply 실행이 아니라, Phase 4를 열 수 있는 pre-apply authorization evidence다.
blocked_before_live_apply는 계획 실패가 아니라, Phase 0-3 blocker를 machine-readable evidence로 닫는 정상 closeout이다.
```

Artifact naming은 이 계획에서 다음과 같이 잠근다.

* Plan: `docs/dvf_3_3_live_migration_readiness_execution_plan.md`
* Evidence root: `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/`
* Policy: `docs/dvf_3_3_live_migration_readiness_policy.md`
* Claim boundary: `docs/dvf_3_3_live_migration_readiness_claim_boundary.md`
* Ledger packet: `docs/dvf_3_3_live_migration_readiness_ledger_packet.md`

Partial live apply policy는 전역 strict rule로 잠근다.

```text
blocked > 0이면 phase4_live_apply_allowed=false다.
live_mutation_eligible subset은 후속 판단 자료로 남길 수 있지만,
그 subset만으로 partial live apply authorization을 열지 않는다.
single blocked row라도 전체 live execution round opening을 지연시킬 수 있음을 final report에 명시한다.
```

Independent review policy는 다음으로 잠근다.

```text
Claude-authored roadmap / artifact를 직접 입력으로 삼은 하위 review에서
Claude 단독 review는 independent review gate 충족으로 세지 않는다.
independent_review_status는 owner adoption status와 별도 필드로 유지한다.
phase4_live_apply_allowed=true는 independent_review_status == PASS일 때만 가능하다.
independent_review_status == pending은 실패는 아니지만 authorization PASS가 아니다.
```

---

## 2. Scope

이 계획은 `migrated=153` terminal projection만 live-readiness input universe로 소비하는 pre-apply readiness round다.

포함 범위:

* scope lock, claim boundary, no-live-mutation contract
* terminal `migrated=153` row extraction and input manifest
* `153`, `163`, `311`, `1062` denominator / lifecycle role separation
* terminal migrated rows와 readiness ledger, sandbox mutation ledger, actual diff-to-ledger evidence의 row identity reconciliation
* `153`이 sandbox mutation row set의 subset인지 row identity 기준으로 증명
* `(163 - 153)` exclusion reason recording
* per-row current live-surface state classification
* live target surface inventory and hard-forbidden classifier
* live writer capability contract and dormant dry-run mode
* consumer-only representability gate
* authority / runtime / package / generated / staging / diagnostic / historical dependency isolation
* dirty target isolation and pre-apply hash snapshot
* dry-run patch plan materialization
* isolated mirror apply equivalence validation
* row-level live-readiness disposition ledger
* Phase 9 pre-apply gate matrix, `pre_review_gate_pass`, and `authorization_candidate`
* Phase 10 final `phase4_live_apply_allowed` / `live_execution_round_apply_allowed` seal after independent review PASS
* no-live-mutation proof
* independent review handoff packet and artifact hash report
* canonical roadmap input path/hash binding
* sealed input provenance manifest with exact source artifact path/hash fields
* writer identity and same-operation-plan contract
* baseline / predecessor context recording for blocker classification
* handoff seeds for Shared Disposition Ledger Consumption and Closeout / Reentry Guard Seal
* live `current_route_required_validations.json` unchanged validation
* handoff packet non-claim fields
* downstream live consumer migration execution plan compatibility manifest
* `ready_for_phase4_live_apply` / `blocked_before_live_apply` predecessor status seal
* `no_live_work` verdict when all rows are evidence-only and no mutation work remains

Primary execution evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/`

Direct documentation artifacts:

* `docs/dvf_3_3_live_migration_readiness_execution_plan.md`
* `docs/dvf_3_3_live_migration_readiness_policy.md`
* `docs/dvf_3_3_live_migration_readiness_claim_boundary.md`
* `docs/dvf_3_3_live_migration_readiness_ledger_packet.md`

Downstream compatibility input:

* `docs/dvf_3_3_live_consumer_migration_execution_plan.md`

### Explicitly Out Of Scope

* live migration execution
* live target file mutation
* guarded live apply
* current authority cutover
* legacy 2105 baseline restoration
* Shared Disposition Ledger Consumption round completion
* Closeout / Reentry Guard Seal round completion
* runtime chunk replacement
* old chunk deletion
* source facts mutation
* decisions mutation
* rendered output mutation
* Lua bridge mutation
* package payload mutation
* live required-validation manifest adoption without separate approval
* release readiness
* package release readiness
* Workshop readiness
* B42 readiness
* deployment readiness
* manual in-game QA
* semantic quality acceptance
* public-facing text quality acceptance
* Browser / Wiki / Tooltip behavior change
* broad `1062` universe redisposition
* terminal disposition rewrite
* denominator lock rewrite
* no-op / diagnostic-only / historical-only row promotion
* architecture redesign
* unrelated refactor
* current-route tooling allowlist expansion

---

## 3. Non-Goals

* `migrated=153`을 live execution count로 해석하지 않는다.
* `migrated=153`을 live migration completion으로 선언하지 않는다.
* `163 sandbox mutation rows`를 live completion evidence로 승격하지 않는다.
* `153`과 `163`의 관계를 count equality로 치환하지 않는다.
* `163 actual_apply_eligible`와 `163 readiness sandbox mutation`을 같은 denominator로 취급하지 않는다.
* readiness sandbox executor를 live writer로 silent repointing하지 않는다.
* sandbox diff-to-ledger PASS를 live target mutation completion으로 읽지 않는다.
* generated / staging / diagnostic / historical artifact를 current authority로 승격하지 않는다.
* hard-forbidden source / rendered / runtime / package surface를 consumer-only target으로 열지 않는다.
* dirty target, unknown target class, ambiguous ownership, missing evidence를 fail-open 처리하지 않는다.
* candidate required-validation patch를 live manifest adoption으로 표현하지 않는다.
* final report를 release, deployment, Workshop, B42, semantic quality, public-facing text quality acceptance로 확대하지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 기준이다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 current readpoint를 따른다.
* DVF 3-3 current authority chain은 `source -> facts -> decisions -> rendered -> Lua bridge -> runtime chunks`로 유지한다.
* DVF/QG는 오프라인 생산 / 검문 체계이며 런타임 즉석 설명 생성 장치가 아니다.
* Runtime deployable authority는 monolith가 아니라 `IrisLayer3DataChunks.lua + IrisLayer3DataChunks/*.lua` 기준이다.
* `migrated=153`은 terminal projection input이며 live execution completion이 아니다.
* `1062`는 executing consumer universe denominator, `311`은 change-required audit subset, `163`은 readiness / sandbox actual mutation subset, `153`은 terminal migrated projection으로 읽는다.
* Terminal split은 read-only input으로 소비한다.

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

* Current-route required-validation patch는 `candidate_only` 상태이며 이 round에서 live manifest를 편집하거나 채택하지 않는다.
* Independent review와 owner adoption은 별도 상태 필드다.
* 이 round가 생성하는 staging evidence는 readiness evidence이며 current authority가 아니다.
* Local paste roadmap input은 plan drafting input일 뿐 canonical sealed roadmap input이 아니다. final readiness PASS 및 `phase4_live_apply_allowed=true` 전 Phase 0에서 canonical copy와 sha256을 `roadmap_input_binding.json`으로 고정해야 한다.
* Readiness tooling이 새로 추가되더라도 current route closure와 `current_route_allowed_tooling_modules` cap을 바꿀 수 없다.
* Iris baseline authority mode는 전환 중이다. 이 계획은 legacy 2105 baseline 복구를 요구하지 않는다.
* `CURRENT_FACTS 6 vs 2105` 형태의 실패는 legacy baseline을 되살릴 근거가 아니다. 이 readiness plan에서는 해당 상태를 broad current-route / baseline migration context로 기록하고, row-level expected-form derivation이나 consumer-only representability를 막는 경우에만 readiness blocker로 반영한다.
* Final readiness PASS는 legacy 2105 closure를 요구하지 않는다. 이 plan은 migrated=153 live-readiness gates를 평가하고, shared ledger / reentry guard 문제는 후속 라운드 seed로 남긴다.
* Baseline context가 live writer capability, target classification, expected migrated form, dirty target isolation, or dry-run/apply equivalence를 불확정하게 만들면 affected row 또는 global gate는 `blocked_by_external_baseline_context`로 fail-closed한다.
* Baseline context가 이미 봉인되어 있고 migrated=153 readiness gates에 영향을 주지 않으면 이 plan은 그 evidence를 provenance로만 기록한다.
* Downstream live execution plan compatibility vocabulary is fixed:
  * `live_mutation_eligible` maps to downstream `live_mutation_required`.
  * `evidence_only` maps to downstream `live_verified_already` when expected form already matches, or `excluded_non_live_target` when the row has positive non-live evidence.
  * `blocked` maps to downstream `live_blocked` or `live_ambiguous` with exact reason.
* Downstream predecessor status is fixed:
  * `ready_for_phase4_live_apply` requires all pre-apply gates PASS, frozen dry-run patch bundle exists, live writer capability is proven, hard-forbidden target count is `0`, dirty target overlap is absent or isolated, external gate status is explicit, and this plan's final authorization seal permits Phase 4 opening.
  * `blocked_before_live_apply` is emitted for any failed gate, unresolved external gate required by this plan, missing frozen patch bundle, missing live writer capability proof, or unresolved row status.
* The downstream execution plan must consume this round as predecessor evidence only. It must not count this round's sandbox/readiness evidence as live completion and must not rederive targets from mutable state if a frozen patch bundle was sealed.

---

## 5. Repository Areas Affected

### Code

Planned implementation may add or update focused offline tooling under these areas:

* `Iris/build/description/v2/tools/build/`
* `Iris/build/description/v2/tests/`

No runtime Lua, source authority, rendered authority, package payload, or live target mutation is planned in this readiness round.

### Docs

* `docs/dvf_3_3_live_migration_readiness_execution_plan.md`
* `docs/dvf_3_3_live_migration_readiness_policy.md`
* `docs/dvf_3_3_live_migration_readiness_claim_boundary.md`
* `docs/dvf_3_3_live_migration_readiness_ledger_packet.md`

### Config

* No live config mutation.
* Candidate-only required-validation patch may be generated at `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase9/candidate_required_validation_patch.json`.
* Live `Iris/_docs/round3/current_route_required_validations.json` is not edited in this plan.
* Live `Iris/_docs/round3/current_route_required_validations.json` pre-run sha256 is recorded in `phase0/external_baseline_context_snapshot.json` and must remain unchanged during this readiness round.
* If a successor required-validation manifest adoption or other authority/config mutation is needed for the vNext consumer baseline, that mutation belongs to a separate baseline-migration approval path. This readiness round may build candidate artifacts and consume already-sealed successor route evidence, but it may not adopt or mutate live authority/config by itself.

### Generated Artifacts

* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase0/`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase1/`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase2/`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase3/`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase4/`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase5/`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase6/`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase7/`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase8/`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase9/`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase0/roadmap_input_binding.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase0/sealed_input_provenance_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase0/external_baseline_context_snapshot.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase0/live_consumer_execution_compatibility_mapping.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase0/external_gate_requirements_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase4/writer_identity_contract.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase9/live_consumer_phase0_3_handoff_packet.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/external_baseline_context_verdict.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/pre_apply_authorization_evidence_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/downstream_predecessor_status.json`

---

## 6. Planned Changes

### Change 0 - Scope Lock / Claim Boundary Seal

Purpose:

Lock `migrated=153` as the only input universe and seal this round as live-readiness adjudication, not live execution.

Files:

* `docs/dvf_3_3_live_migration_readiness_policy.md`
* `docs/dvf_3_3_live_migration_readiness_claim_boundary.md`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase0/input_scope_lock.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase0/no_live_mutation_contract.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase0/reviewer_independence_note.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase0/canonical_roadmap_input.md`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase0/roadmap_input_binding.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase0/sealed_input_provenance_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase0/external_baseline_context_snapshot.json`

Implementation Notes:

* Define allowed input artifacts and excluded row classes.
* Separate `readiness_pass`, `phase4_live_apply_allowed`, and `live_completed`.
* Add explicit non-claims for source/rendered/runtime/package mutation and release readiness.
* Record independent review limitations when the input was authored by Claude or derived from Claude-authored material.
* Materialize the provisional roadmap paste into the canonical roadmap input artifact and record `roadmap_input_path`, `roadmap_input_sha256`, and `local_paste_input=false` after binding.
* Build a sealed input provenance manifest before Phase 1. It must include exact path, sha256, role, and read-only status for every source artifact used by row extraction, denominator reconciliation, subset proof, and diff-to-ledger proof.
* Build `live_consumer_execution_compatibility_mapping.json` before Phase 1. It must map each readiness artifact family to the downstream execution plan's Phase 0-3 expected artifacts, including scope lock, input binding, row identity crosswalk, migrated live-state classification, consumer-only representability, live writer capability probe, dirty target isolation, dry-run/apply equivalence, hard-forbidden surface verdict, and pre-apply gate report.
* Build `external_gate_requirements_manifest.json` using the downstream execution plan vocabulary: `satisfied`, `pending_external`, `blocked`, or `not_applicable_with_reason`. Pending gates must not be overread as authorization PASS.
* Record external baseline context before Phase 1. Allowed values are `not_relevant_to_migrated153_readiness`, `sealed_context_consumed`, `context_blocks_readiness`, or `unresolved_context_for_followup`.
* If context is relevant, record path, sha256, role, and reason for any consumed vNext / 2105 / current-route evidence. Do not require reconstruction of legacy 2105 facts.
* Do not create, repair, or adopt the baseline migration route as part of this readiness plan.
* If baseline context blocks migrated=153 expected-form derivation, target classification, or consumer-only representability, fail closed with `blocked_by_external_baseline_context` and keep authorization fields false.
* If baseline context is unrelated to migrated=153 readiness gates, record it only as follow-up seed for Shared Disposition Ledger Consumption or Closeout / Reentry Guard Seal.
* If canonical roadmap binding or sealed input provenance binding is missing, all later verdicts remain provisional and `phase4_live_apply_allowed=false`.
* Canonical roadmap binding is a final readiness PASS prerequisite, not a prerequisite for plan-text review status.

Validation:

* Input artifact existence check.
* `migrated` row count equals `153`.
* Non-migrated terminal rows are absent from the input manifest.
* Claim boundary lint rejects live completion wording.
* Pre-check confirms no live target mutation before the round begins.
* `roadmap_input_binding.json` records `local_paste_input=false` and sha256 for `phase0/canonical_roadmap_input.md`.
* `sealed_input_provenance_manifest.json` includes no missing path/hash fields.
* `live_consumer_execution_compatibility_mapping.json` covers every downstream Phase 0-3 required artifact family or gives an explicit blocked/not-applicable reason.
* `external_gate_requirements_manifest.json` uses only the allowed downstream gate states and does not convert `pending_external` to PASS.

---

### Change 1 - Row Identity Reconciliation / Denominator Lock

Purpose:

Join the `153` terminal migrated rows to readiness, sandbox mutation, and actual diff-to-ledger evidence by row identity rather than count equality.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase1/live_readiness_input_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase1/live_scope_reconciliation_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase1/migrated_to_sandbox_subset_proof.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase1/row_identity_join_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase1/orphan_duplicate_collision_report.json`

Implementation Notes:

* Extract only terminal `migrated` rows.
* Prove `153` is a row-identity subset of the relevant sandbox mutation evidence.
* Record explicit exclusion reasons for `(163 - 153)`.
* Reject unique path, source entry, runtime entry, semantic object, or accepted occurrence as denominator replacements.
* Reject count-only inference between different `163` denominator IDs.
* Consume only Phase 0 pinned read-only inputs for extraction and subset proof.
* Required sealed input provenance fields:
  * `terminal_disposition_final_report_path = Iris/build/description/v2/staging/dvf_3_3_terminal_disposition_adjudication/phase5/final_terminal_disposition_machine_report.json`
  * `terminal_disposition_final_report_sha256 = 1F2B07E8E16081E27748D57BA9B7EE888833D45B52C96900DB8F3897AA534CE9`
  * `denominator_lock_report_path = Iris/build/description/v2/staging/consumer_universe_denominator_lock/phase8/final_consumer_universe_denominator_lock_report.json`
  * `denominator_lock_report_sha256 = 2EBCB5C1B44CA140AE98935298F3C87B4FCB7AFCEE7ACA7C6042BD8891409945`
  * `row_disposition_ledger_for_readiness_path = Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase6/row_disposition_ledger.for_readiness.jsonl`
  * `row_disposition_ledger_for_readiness_sha256 = 8F2667EAFCF59A460FD292D45357667DC17E9FD3A4A6FB73C58D6610E347C094`
  * `consumer_migration_reconciled_input_manifest_path = Iris/build/description/v2/staging/dvf_3_3_vnext_consumer_migration_input_normalization/phase6/consumer_migration_reconciled_input_manifest.json`
  * `consumer_migration_reconciled_input_manifest_sha256 = 19D2435C0738BBF795D6CF180316468ADBE561FD703332AB1C6C53E4B3C16990`
  * `actual_diff_to_ledger_mapping_path = Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase4/actual_diff_to_ledger_report.json`
  * `actual_diff_to_ledger_mapping_sha256 = D9C1AEB99BCB55B4ED2452EBFFE3481E3BFAFCE03973C14EA17C98BE5DC6CD82`
  * `diff_hunk_ledger_bijection_path = Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness/phase4/diff_hunk_ledger_bijection_report.json`
  * `diff_hunk_ledger_bijection_sha256 = 51124650E1971871C1E59075888A0A191876BF22DECD59AC9EC060E5DA400758`

Validation:

* Migrated input count is exactly `153`.
* Every row has terminal migrated evidence.
* Every row has positive readiness / cutover evidence.
* Every admitted row maps to sandbox mutation evidence by row identity.
* No non-migrated row is admitted.
* No duplicate, orphan, or identity collision is silently accepted.
* Every consumed source artifact hash matches the Phase 0 provenance manifest.
* `(163 - 153)` exclusion reasons are repeated in final claim boundary inputs.

---

### Change 2 - Per-Row Current Live-Surface State Classification

Purpose:

Classify the current live target state for all 153 rows before any gate verdict or mutation eligibility is assigned.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase2/live_surface_state_ledger.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase2/live_surface_state_summary.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase2/state_unknown_inventory.json`

Implementation Notes:

* Resolve live target identifiers for each row.
* Record target present, missing, ambiguous, already-equivalent, mutation-needed, or state-unknown conditions.
* Do not assign final eligibility in this phase.
* Treat `state_unknown` as a first-class state that must fail closed later.

Validation:

* All 153 rows have exactly one state classification.
* `state_unknown` rows are explicit and feed later blocked disposition.
* Classifier output is deterministic.
* No live mutation occurs during classification.

---

### Change 3 - Live Target Surface Inventory / Hard-Forbidden Classifier

Purpose:

Inventory every live target candidate and block rows that overlap protected or hard-forbidden authority, runtime, package, staging, generated, diagnostic, historical, stale, monolith, or quarantine surfaces.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase3/live_target_surface_inventory.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase3/hard_forbidden_surface_policy.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase3/hard_forbidden_overlap_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase3/target_classification_ledger.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase3/static_reach_forbidden_surface_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase3/dry_run_dynamic_reach_forbidden_surface_report.json`

Implementation Notes:

* Define target path, target region, and target owner inventory.
* Apply protected current-output set and surface blocklists.
* Include source authority, rendered authority, runtime deployable authority, package peer, staging/generated/diagnostic/historical, stale bridge, monolith, and quarantine surfaces.
* Require both static reach and dry-run dynamic reach to report forbidden mutation `0` before eligibility can proceed.

Validation:

* Every row has target classification.
* Unknown target class is blocked.
* Protected surface overlap is blocked.
* Authority/runtime/package dependency is blocked.
* Static reach and dynamic reach reports are deterministic.

---

### Change 4 - Live Writer Capability / Consumer-Only Representability Gate

Purpose:

Define a live writer capability that is distinct from the sandbox executor and verify whether each row is representable as consumer-only mutation.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase4/live_writer_capability_contract.md`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase4/live_writer_capability_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase4/live_writer_dry_run_contract_test_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase4/consumer_only_representability_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase4/writer_dependency_isolation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase4/writer_capability_row_ledger.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase4/writer_identity_contract.json`

Implementation Notes:

* Define live writer command surface.
* Require dormant dry-run mode for this readiness round.
* Keep live write path unavailable for execution in this round.
* Block rows that require authority-derived regeneration, runtime/package/generated artifact dependency, or unsupported writer behavior.
* Ensure writer output target set equals allowed target set.
* Add writer identity fields to `writer_identity_contract.json` and to the Phase 9 handoff packet:
  * `writer_tool_path`
  * `writer_tool_hash`
  * `same_mutation_planner_hash`
  * `same_target_resolver_hash`
  * `same_patch_serializer_hash`
  * `same_row_to_operation_mapper_hash`
  * `same_operation_plan_hash`
  * `allowed_target_set_hash`
  * `expected_pre_apply_hash_manifest`
  * `required_next_round_activation_flag`
* `dry_run_mode` and `mirror_apply_mode` may differ only by sink.
* `live_apply_mode` remains disabled in this round.
* A future live execution round must consume the same operation plan contract and must not regenerate a different plan silently.

Validation:

* Every row has writer capability status.
* Writer unavailable rows are blocked.
* Consumer-only representation unavailable rows are blocked.
* Authority/runtime/package write attempt fails closed.
* Writer deterministic dry-run output hash is stable.
* Writer identity fields are non-empty and hash-verified.
* Dry-run planner, mirror apply planner, target resolver, patch serializer, row-to-operation mapper, operation plan, and allowed target set hashes are identical where required.
* `live_write_count = 0`.

---

### Change 5 - Dirty Target Isolation / Pre-Apply Workspace Gate

Purpose:

Verify that live target candidates are clean, owner-safe, and not overlapping untracked, ignored, modified, or unsafe inter-row target surfaces.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase5/pre_apply_target_hash_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase5/dirty_target_isolation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase5/untracked_ignored_overlap_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase5/inter_row_target_overlap_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase5/protected_surface_no_mutation_verdict.json`

Implementation Notes:

* Capture pre-apply hash snapshot for target files.
* Inspect modified, untracked, ignored, and generated target overlap.
* Detect unsafe inter-row target overlap.
* Block dirty target rows.
* Maintain protected surface no-mutation verdict.

Validation:

* All target files have pre-apply hashes.
* Dirty target overlap must be `0` for eligibility.
* Untracked target overlap must be `0` for eligibility.
* Unsafe inter-row overlap must be `0` for eligibility.
* Missing target is blocked unless explicit evidence-only reason applies.
* Protected current surface changed count remains `0`.

---

### Change 6 - Dry-Run Plan Materialization

Purpose:

Generate a no-live-write dry-run patch plan for candidate rows and separate mutation candidates from evidence-only rows.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase6/dry_run_operation_ledger.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase6/dry_run_patch_plan.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase6/dry_run_determinism_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase6/dry_run_no_live_mutation_verdict.json`

Implementation Notes:

* Produce row-level dry-run operations.
* Calculate expected before/after hashes.
* Calculate expected diff hunks.
* Map patch intent back to row evidence.
* Mark evidence-only rows separately and exclude them from mutation counts.
* Include `same_operation_plan_hash`, `allowed_target_set_hash`, and `expected_pre_apply_hash_manifest` from the writer identity contract.
* Treat regenerated or drifted dry-run operation plans as blocked rather than refreshing them silently.

Validation:

* Every candidate row has dry-run operation or explicit evidence-only reason.
* Dry-run target set equals allowed target set.
* Dry-run diff has no orphan hunks.
* Repeated dry-run output is deterministic.
* Repeated dry-run operation plan hash is stable.
* No live file changes after dry-run.

---

### Change 7 - Isolated Apply Equivalence Gate

Purpose:

Apply only inside an isolated mirror and prove dry-run patch output equals isolated actual apply output.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase7/isolated_apply_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase7/dry_run_apply_equivalence_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase7/actual_diff_to_readiness_ledger_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase7/isolated_apply_no_forbidden_mutation_verdict.json`

Implementation Notes:

* Create mirror from live target state.
* Verify mirror source hash equals live pre-apply hash.
* Run isolated apply executor only against the mirror.
* Compare dry-run expected diff to isolated actual diff.
* Revalidate row-level diff-to-ledger mapping.
* Block mismatch rows.
* Assert mirror apply consumes the same operation plan contract as dry-run and differs only by sink.
* Record whether the future live execution round is required to consume the frozen operation plan without replanning.

Validation:

* Mirror source hash equals live pre-apply hash.
* Isolated apply only touches allowed mirrored targets.
* Dry-run diff equals isolated apply diff.
* Dry-run and mirror apply share mutation planner, target resolver, patch serializer, row-to-operation mapper, operation plan, and allowed target set hashes.
* Mapped row count equals expected eligible mutation count.
* `unmapped_diff = 0`.
* `orphan_diff = 0`.
* `extra_target_mutation = 0`.
* Live protected surface changed count remains `0`.

---

### Change 8 - Row-Level Live Readiness Disposition

Purpose:

Assign exactly one final live-readiness disposition to every `migrated=153` row.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase8/live_readiness_row_disposition_ledger.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase8/live_readiness_disposition_summary.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase8/blocked_reason_inventory.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase8/evidence_only_reason_inventory.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase8/live_axis_vs_terminal_axis_boundary_note.md`

Implementation Notes:

* Valid final dispositions are `live_mutation_eligible`, `evidence_only`, and `blocked`.
* `live_mutation_eligible` requires all row gates to pass.
* `evidence_only` requires row-level evidence that live mutation is not needed.
* `blocked` requires machine-readable reason.
* Unknown, pending, conditional, ambiguous, missing evidence, and state unknown conditions fail closed into `blocked`.
* Keep live-readiness axis separate from terminal disposition axis.
* `evidence_only` is not terminal `no-op`. `evidence_only` means the row is in terminal `migrated=153` input but current live surface does not require a live mutation, with row-level proof.
* Blocked reason taxonomy uses a stable top-level `blocked_reason_code` plus freeform `blocked_reason_detail`; it does not create one-off top-level codes for every detail.

Validation:

* `live_mutation_eligible + evidence_only + blocked == 153`.
* Every row has exactly one final disposition.
* Every blocked row has blocked reason.
* Every evidence-only row has evidence-only reason.
* Every eligible row passes all gates.
* `unknown / pending / conditional / ambiguous == 0`.

---

### Change 9 - Pre-Review Gate Aggregation / Authorization Candidate

Purpose:

Aggregate gate results before independent review and produce a candidate verdict. Phase 9 does not seal final live execution round opening.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase9/pre_apply_gate_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase9/pre_review_gate_pass.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase9/live_apply_authorization_candidate.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase9/live_execution_handoff_packet.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase9/live_consumer_phase0_3_handoff_packet.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase9/candidate_required_validation_patch.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase9/draft_live_migration_readiness_report.json`

Implementation Notes:

* Build pre-apply gate matrix.
* Compute global PASS/FAIL.
* Compute `pre_review_gate_pass` and `authorization_candidate`.
* Compute a draft downstream predecessor status:
  * `ready_for_phase4_live_apply` only when `authorization_candidate=true`, frozen patch bundle evidence exists, live writer capability is proven, hard-forbidden target count is `0`, dirty target isolation PASS, and external gate status is explicit.
  * `blocked_before_live_apply` for any failed or pending required pre-apply gate.
* Keep `phase4_live_apply_allowed=false` and `live_execution_round_apply_allowed=false` until Phase 10 seals final authorization after `independent_review_status == PASS`.
* Record partial apply-ready subset only as evidence, not authorization.
* Keep candidate required-validation patch as candidate-only.
* Add mandatory handoff non-claim fields:
  * `live_mutation_executed = false`
  * `current_authority_cutover = false`
  * `required_validation_manifest_adopted = false`
  * `partial_live_apply_authorized = false`
  * `release_readiness = false`
  * `workshop_readiness = false`
  * `b42_readiness = false`
  * `deployment_readiness = false`
* If `live_mutation_eligible == 0` and `blocked == 0`, set `closeout_state = complete`, `verdict = no_live_work`, `reason = all rows evidence-only; no live mutation work remains`, `phase4_live_apply_allowed = false`, and `live_execution_round_apply_allowed = false`.
* If `blocked > 0`, set `partial_live_apply_authorized = false`, `phase4_live_apply_allowed = false`, and record that the all-or-nothing policy may delay the whole live execution round until residue is resolved.
* Repeat `(163 - 153)` exclusion summary in final report claim boundary so excluded sandbox rows cannot be reintroduced through handoff.
* `live_consumer_phase0_3_handoff_packet.json` must list downstream Phase 0-3 artifact names from `docs/dvf_3_3_live_consumer_migration_execution_plan.md`, the readiness artifact that satisfies each name, the artifact role, sha256, and whether the artifact is `satisfied`, `blocked`, or `not_applicable_with_reason`.

Validation:

Required global gates:

* input universe gate PASS
* row identity gate PASS
* live surface state classification complete
* hard-forbidden surface gate PASS
* writer capability gate PASS
* consumer-only representability gate PASS
* dirty target isolation gate PASS
* dry-run/apply equivalence gate PASS
* protected surface no-mutation gate PASS
* no live mutation gate PASS
* final disposition completeness gate PASS
* sealed input provenance gate PASS
* writer identity gate PASS
* external baseline context does not block migrated=153 readiness gates
* handoff non-claim gate PASS

Pre-review candidate rule:

```text
authorization_candidate = true
only if:
  live_mutation_eligible > 0
  blocked == 0
  all global gates == PASS
  protected_surface_changed_count == 0
  live_mutation_performed == false
```

If any condition fails:

```text
authorization_candidate = false
phase4_live_apply_allowed = false
live_execution_round_apply_allowed = false
blocked rows and gate failures must be recorded.
```

If all rows are evidence-only:

```text
if live_mutation_eligible == 0 and blocked == 0:
  closeout_state = complete
  verdict = no_live_work
  phase4_live_apply_allowed = false
  live_execution_round_apply_allowed = false
  reason = all rows evidence-only; no live mutation work remains
```

---

### Change 10 - Independent Review / No-Mutation Seal

Purpose:

Seal reproducibility and no-live-mutation evidence, and hand off to a genuinely independent reviewer when required.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/independent_review_artifact_hash_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/live_target_pre_post_hash_verdict.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/no_live_mutation_final_verdict.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/independent_review_handoff_packet.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/external_baseline_context_verdict.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/claim_boundary_lint_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/final_live_apply_authorization_verdict.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/final_live_migration_readiness_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/pre_apply_authorization_evidence_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/downstream_predecessor_status.json`
* `docs/dvf_3_3_live_migration_readiness_ledger_packet.md`

Implementation Notes:

* Hash final report and key artifacts.
* Hash row disposition ledger.
* Compare live target pre/post hash.
* Re-run protected surface no-mutation verdict.
* Run final claim boundary guard against final report, live execution handoff packet, independent review handoff packet, candidate required-validation patch, and ledger packet.
* Consume Phase 9 `authorization_candidate` and compute or seal final `phase4_live_apply_allowed` only after `independent_review_status == PASS`.
* Seal `downstream_predecessor_status.json` with exactly one of:
  * `ready_for_phase4_live_apply`
  * `blocked_before_live_apply`
* `ready_for_phase4_live_apply` requires `phase4_live_apply_allowed=true`, `live_execution_round_apply_allowed=true`, and a non-empty `pre_apply_authorization_evidence_manifest.json`.
* `blocked_before_live_apply` requires `phase4_live_apply_allowed=false` and at least one machine-readable `blocked_*` reason or explicit `no_live_work` closeout reason.
* `pre_apply_authorization_evidence_manifest.json` must include the frozen dry-run patch bundle identity, writer identity contract, live writer capability proof, row status ledgers, hard-forbidden surface verdict, dirty target isolation report, dry-run/apply equivalence report, and downstream Phase 0-3 handoff packet hash.
* Record independent review as PASS, FAIL, or pending.
* Do not treat self-review or Claude-only review of Claude-derived artifacts as independent review.
* Independent review actor fields must include `reviewer`, `reviewer_model_or_agent`, `input_dependency`, and `independence_basis`.
* `docs/dvf_3_3_live_migration_readiness_ledger_packet.md` must separate artifact inventory into:
  * `core_artifacts`
  * `supporting_artifacts`
  * `candidate_only_artifacts`
  * `non_authority_artifacts`
* Core artifacts must include final report, final authorization verdict, row disposition ledger, sealed input provenance manifest, external baseline context snapshot, writer identity contract, no-live-mutation verdict, external baseline context verdict, and independent review artifact hash report.
* Candidate-only artifacts must include the candidate required-validation patch and any handoff packet that is not independently sealed.
* Non-authority artifacts must explicitly include staging evidence and local/provisional paste inputs.
* Validate external baseline context only as a readiness dependency:
  * `context_state` is one of `not_relevant_to_migrated153_readiness`, `provenance_only`, `blocks_readiness`, or `followup_seeded`
  * legacy 2105 reconstruction is never required by this plan
  * shared disposition ledger consumption gaps are seeded for the Shared Disposition Ledger Consumption round
  * predecessor reentry guard gaps are seeded for the Closeout / Reentry Guard Seal round
  * baseline context can block this readiness plan only when it prevents migrated=153 expected-form derivation, target classification, consumer-only representability, dirty target isolation, or dry-run/apply equivalence

Validation:

* Stable artifact hash PASS.
* No live target mutation PASS.
* Protected surface changed count equals `0`.
* Claim boundary lint PASS across final report, handoff packets, candidate patch, and ledger packet.
* Row count consistency PASS.
* Independent review PASS is required for `phase4_live_apply_allowed=true`; pending must force `phase4_live_apply_allowed=false`.
* No self-certification of independence.
* Final authorization verdict PASS requires Phase 9 `authorization_candidate=true` and Phase 10 `independent_review_status=PASS`.
* Downstream predecessor status is `ready_for_phase4_live_apply` only when final authorization verdict PASS also holds.
* Downstream predecessor status is `blocked_before_live_apply` when any pre-apply gate fails, independent review is not `PASS`, or required external gate status is pending/blocked under this plan.
* Ledger packet artifact inventory has non-empty `core_artifacts`, `supporting_artifacts`, `candidate_only_artifacts`, and `non_authority_artifacts`.
* External baseline context verdict is present and either non-blocking for migrated=153 readiness or records exact `blocked_by_external_baseline_context` reasons.
* Live `Iris/_docs/round3/current_route_required_validations.json` sha256 remains equal to the pre-run hash recorded in `phase0/external_baseline_context_snapshot.json`.

---

## 7. Validation Plan

### Automated Validation

This round requires heavy validation. Planned automated validation includes:

* input artifact existence check
* canonical roadmap input hash validation
* sealed source artifact provenance validation
* input universe completeness check
* row identity join completeness check
* migrated subset proof
* denominator reconciliation
* live surface state classification completeness
* hard-forbidden surface classifier
* static reach forbidden surface scan
* dry-run dynamic reach forbidden surface scan
* live writer capability check
* writer identity equivalence validation
* dry-run / mirror apply same-code-path validation
* writer dry-run contract test
* consumer-only representability check
* dirty target isolation check
* untracked / ignored target overlap check
* inter-row target overlap check
* dry-run determinism check
* isolated apply equivalence check
* actual diff-to-readiness-ledger mapping check
* protected surface no-mutation check
* no live mutation check
* final disposition completeness check
* claim boundary lint
* independent artifact hash review
* independent review `PASS` hard gate validation
* downstream live consumer execution compatibility mapping validation
* downstream predecessor status validation
* pre-apply authorization evidence manifest completeness validation
* external baseline context snapshot validation
* external baseline context blocker classification
* current core module count unchanged validation
* `current_route_allowed_tooling_modules` cap unchanged validation
* live `Iris/_docs/round3/current_route_required_validations.json` unchanged validation
* readiness tooling not-imported-by-current-route validation
* candidate required-validation patch remains candidate-only validation

Expected validation commands must be made concrete during implementation and cannot be claimed as passed unless the exact relevant command exits with code `0`. Existing preferred commands remain:

* Python pipeline: `uv run python <script>`
* Lua syntax, if Lua surfaces are inspected: `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`

Every named validation check must have a machine-readable binding with:

```text
command
expected_artifact
expected_exit_code = 0
pass_condition
failure_condition
```

Required concrete validation binding seeds:

```text
check = external_baseline_context_validation
command = implementation-defined context classifier
expected_artifact = Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/external_baseline_context_verdict.json
expected_exit_code = 0
pass_condition = context_state recorded; legacy 2105 restoration not required; broad shared-ledger or reentry-guard gaps are emitted only as follow-up seeds; any context that affects migrated=153 expected-form derivation, target classification, consumer-only representability, dirty target isolation, or dry-run/apply equivalence is mapped to `blocked_by_external_baseline_context`
failure_condition = missing context snapshot, unclassified context dependency, hidden legacy 2105 restoration requirement, or baseline/context issue used to authorize live execution without row/global blocker evidence

check = sealed_input_provenance_validation
command = implementation-defined Python provenance validator
expected_artifact = Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase0/sealed_input_provenance_manifest.json
expected_exit_code = 0
pass_condition = every pinned path exists and every sha256 matches
failure_condition = missing path, missing hash, hash mismatch, or unpinned source artifact

check = downstream_compatibility_mapping_validation
command = implementation-defined downstream compatibility validator
expected_artifact = Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase0/live_consumer_execution_compatibility_mapping.json
expected_exit_code = 0
pass_condition = every required downstream Phase 0-3 artifact family is mapped to a readiness artifact, blocked reason, or not-applicable reason; artifact roles are read-only/predecessor evidence unless explicitly candidate-only; no readiness artifact is marked as live completion evidence
failure_condition = unmapped downstream artifact family, missing role, missing hash, sandbox/readiness evidence marked as live completion, or direct target rederivation allowed after frozen patch bundle seal

check = downstream_predecessor_status_validation
command = implementation-defined predecessor status validator
expected_artifact = Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/downstream_predecessor_status.json
expected_exit_code = 0
pass_condition = status is exactly ready_for_phase4_live_apply or blocked_before_live_apply; ready_for_phase4_live_apply implies phase4_live_apply_allowed true and complete pre_apply_authorization_evidence_manifest; blocked_before_live_apply implies phase4_live_apply_allowed false with machine-readable blocked reason or no_live_work reason
failure_condition = invalid status, authorization/status mismatch, missing blocked reason, missing evidence manifest for ready status, or live mutation executed in this readiness round

check = writer_identity_equivalence_validation
command = implementation-defined Python writer identity validator
expected_artifact = Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase4/writer_identity_contract.json
expected_exit_code = 0
pass_condition = dry_run_mode and mirror_apply_mode differ only by sink; same planner/resolver/serializer/mapper/operation-plan/target-set hashes
failure_condition = hash drift, replanning, sink leakage, or live_apply_mode enabled in this round

check = claim_boundary_lint
command = implementation-defined Python claim guard validator
expected_artifact = Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/phase10/claim_boundary_lint_report.json
expected_exit_code = 0
pass_condition = final report, handoff packets, candidate patch, and ledger packet contain required non-claim fields and no live completion/release/cutover claim
failure_condition = missing non-claim field or forbidden claim wording
```

### Manual Validation

Manual validation for this readiness round is inspection-only:

* review final live migration readiness report
* inspect blocked reason inventory
* inspect evidence-only reason inventory
* inspect live execution handoff packet
* verify no report wording claims live completion, release readiness, or current authority cutover
* verify independent review actor and status are explicit

### Validation Limits

This execution will not perform:

* live migration apply
* live target mutation
* runtime validation
* deployment validation
* package release validation
* Workshop validation
* B42 validation
* manual in-game QA
* long-session runtime validation
* multiplayer validation
* browser / wiki / tooltip behavior validation
* external ecosystem compatibility sweep
* public-facing text quality acceptance
* semantic quality re-adjudication
* current authority reconstruction
* legacy 2105 baseline restoration
* broad `1062` universe redisposition
* terminal disposition independent re-review beyond consumed inputs
* full runtime equivalence

---

## 8. Risk Surface Touch

### Authority Surface

None.

This plan does not mutate source facts, decisions, rendered output, runtime chunks, Lua bridge, or package payload. It creates staging readiness evidence only.

### Runtime Behavior Surface

None.

No runtime Lua, chunk manifest, chunk file, browser, wiki, tooltip, or package payload mutation is authorized.

### Compatibility Surface

Candidate-only.

The round may produce candidate command surface mapping or candidate required-validation patch artifacts. These artifacts are not live manifest adoption and do not change current-route validation requirements by themselves.
The live execution handoff packet is a readiness handoff only. It must carry explicit non-claim fields and cannot be consumed as live execution authorization unless `phase4_live_apply_allowed=true`, `live_execution_round_apply_allowed=true`, and `independent_review_status=PASS`.

### Sealed Artifact Surface

New staging evidence surface:

* `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/`

This staging evidence is not current authority. The canonical roadmap input, sealed input provenance manifest, external baseline context snapshot, writer identity contract, and external baseline context verdict are required before final readiness PASS and before `phase4_live_apply_allowed=true`.

New docs surface:

* `docs/dvf_3_3_live_migration_readiness_policy.md`
* `docs/dvf_3_3_live_migration_readiness_claim_boundary.md`
* `docs/dvf_3_3_live_migration_readiness_ledger_packet.md`

### Public-Facing Output Surface

None.

No user-facing text, UI, tooltip, browser behavior, release note, Workshop copy, or public documentation acceptance is in scope.

---

## 9. Risk Analysis

### Architecture Risk

* `migrated=153` may be overread as live completion.
* Sandbox mutation evidence may be promoted into live mutation evidence.
* `153`, `163`, `311`, and `1062` may be collapsed into one denominator.
* Generated, staging, diagnostic, historical, stale, package, runtime, or authority surfaces may be misclassified as consumer-only targets.
* Closed current readpoints may be reopened without new authority input.
* Legacy 2105 closure failures may be misread as a mandate to restore the old baseline instead of sealing the vNext consumer baseline route.
* Mixed legacy/vNext baseline artifacts may produce false confidence if their impact on migrated=153 readiness gates is not classified.
* Provisional local roadmap input may be mistaken for canonical sealed roadmap input.

### Runtime Risk

* Runtime risk is intended to remain none because this round performs no runtime mutation.
* Accidental writes to runtime chunk authority or Lua bridge must fail the round.
* Any live target mutation discovered during the round invalidates the readiness report.
* Live writer implementation work may accidentally enable a file sink; `live_apply_mode` must remain disabled.

### Compatibility Risk

* Candidate required-validation patch may be misread as live manifest adoption.
* Partial apply-ready subset may be misread as partial live execution authorization.
* Independent review pending may be misread as independent review pass.
* Package route PASS or current-route closure evidence may be overread as release readiness.
* New readiness tooling may accidentally enter the current route or expand the tooling allowlist cap.
* A legacy current-route validation failure may be overcorrected by restoring deprecated 2105 baseline artifacts.

### Regression Risk

* Row identity reconciliation may merge distinct rows that share target path.
* Target region granularity may be too broad and hide allowed/blocked row conflicts.
* Dirty target scan may miss ignored or untracked overlap.
* Dry-run output and isolated apply output may drift because of ordering, newline, formatting, or writer path differences.
* Evidence-only rows may be counted as mutation rows.
* Writer identity drift may make dry-run/mirror equivalence non-transferable to a future live execution round.

---

## 10. Rollback Plan

This round should not mutate live surfaces. Rollback is therefore artifact containment unless an accidental write is detected.

Normal containment:

* delete or archive `Iris/build/description/v2/staging/dvf_3_3_live_migration_readiness_execution/`
* discard candidate required-validation patch
* discard candidate live execution handoff packet
* mark final report invalid if independent review fails
* regenerate from the earliest invalid phase:
  * Phase 1 for row identity mismatch
  * Phase 2 for live surface state classifier error
  * Phase 3 for target classifier error
  * Phase 4-7 for writer or equivalence error
  * Phase 9 for verdict aggregation error

If unintended live mutation is detected:

* immediately close the round as `invalidated_due_to_live_mutation`
* identify changed files from pre-apply hash manifest
* restore using VCS or pre-run snapshot after explicit operator approval where required
* record the changed surface in the no-mutation verdict
* do not open live execution round from this readiness output

---

## 11. Governance Constraints

* Maintain `docs/Philosophy.md` compliance.
* Preserve Hub & Spoke module boundaries.
* Preserve Iris as 100% Lua runtime display module with offline evidence production.
* Preserve DVF current authority chain.
* Preserve baseline/reentry boundaries; do not force legacy 2105 restoration during vNext consumer baseline migration.
* Preserve runtime/build-time separation.
* Preserve source / facts / decisions / rendered / Lua bridge / runtime chunk authority ownership.
* Preserve current runtime deployable authority as chunk manifest plus chunk files, not monolith.
* Preserve FAIL-LOUD behavior.
* Preserve no silent fallback.
* No live mutation in this round.
* No runtime chunk replacement in this round.
* No source facts / decisions / rendered output mutation in this round.
* No Lua bridge mutation in this round.
* No package payload mutation in this round.
* No required-validation live manifest adoption without separate approval.
* No sandbox mutation evidence as live completion evidence.
* No terminal `migrated=153` as live execution count.
* No denominator mixing between `1062`, `311`, `163`, and `153`.
* No count-equality inference between `163 actual_apply_eligible` and `163 readiness sandbox mutation`.
* No generated / staging / diagnostic / historical artifact promotion to current authority.
* No legacy 2105 baseline restoration as a fix for vNext consumer baseline migration blockers.
* Consumer-only target is the only possible live writer target class.
* Dirty target is fail-closed.
* Hard-forbidden surface overlap is fail-closed.
* Dry-run/apply mismatch is fail-closed.
* Unknown / ambiguous / missing row evidence is blocked.
* Protected surface no-mutation evidence is required.
* Independent review cannot be replaced by self-certification.
* Independent review `pending` cannot authorize live execution round opening.
* `phase4_live_apply_allowed=true` requires `independent_review_status == PASS`.
* `live_mutation_eligible == 0` and `blocked == 0` must produce `verdict = no_live_work`, not live apply authorization.
* External baseline context, current core module count, tooling allowlist cap, and live required-validation manifest pre-run hash must be recorded without mutation during this readiness round.
* Live execution handoff packets must include non-claim fields for live mutation, current authority cutover, required-validation adoption, partial live apply, release, Workshop, B42, and deployment readiness.

---

## 12. Expected Closeout State

Expected closeout target: `complete`.

`complete` means:

* `migrated=153` input universe is locked.
* Row identity reconciliation is complete.
* Current live-surface state classification covers all 153 rows.
* Every row has exactly one live-readiness disposition.
* `live_mutation_eligible + evidence_only + blocked == 153`.
* Blocked rows, if any, have machine-readable blocked reasons.
* Evidence-only rows, if any, have explicit row-level evidence-only reasons.
* Canonical roadmap input path/hash is sealed and no longer depends on local paste identity.
* Source artifact provenance is pinned by exact path and sha256.
* Writer identity contract proves dry-run and mirror apply differ only by sink.
* External baseline context is classified as non-blocking provenance, migrated=153 readiness blocker, or follow-up seed for Shared Disposition Ledger Consumption / Closeout Reentry Guard Seal.
* Live `Iris/_docs/round3/current_route_required_validations.json` remains unchanged.
* Dry-run and isolated apply equivalence is validated for eligible mutation candidates.
* Protected surface changed count is `0`.
* Live mutation performed is `false`.
* Phase 9 computes `pre_review_gate_pass` and `authorization_candidate`.
* Phase 10 seals final `phase4_live_apply_allowed` and `live_execution_round_apply_allowed` after `independent_review_status == PASS`.
* Phase 10 seals `downstream_predecessor_status` as exactly `ready_for_phase4_live_apply` or `blocked_before_live_apply`.
* `pre_apply_authorization_evidence_manifest.json` exists and maps this readiness round to `docs/dvf_3_3_live_consumer_migration_execution_plan.md` Phase 0-3 inputs.
* Independent review handoff is produced.
* Independent review status is `PASS`, `FAIL`, or `pending`; only `PASS` can permit `phase4_live_apply_allowed=true`.
* Handoff packets contain the required non-claim fields.
* Ledger packet separates `core_artifacts`, `supporting_artifacts`, `candidate_only_artifacts`, and `non_authority_artifacts`.
* The final claim boundary does not assert live completion, current authority cutover, release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA pass, semantic quality completion, or public-facing text quality acceptance.

If `blocked > 0`, any global gate fails, or independent review is not `PASS`, the closeout may still be `complete` as a readiness adjudication, but the verdict must be:

```text
downstream_predecessor_status = blocked_before_live_apply
phase4_live_apply_allowed = false
live_execution_round_apply_allowed = false
```

If Phase 9 `authorization_candidate=true`, no blocked row exists, all global gates PASS, protected surface changed count is `0`, live mutation performed is `false`, independent review status is `PASS`, and `live_mutation_eligible > 0`, the verdict may be:

```text
downstream_predecessor_status = ready_for_phase4_live_apply
phase4_live_apply_allowed = true
live_execution_round_apply_allowed = true
```

That verdict only authorizes opening a separate live execution round. It does not execute live migration.

If all rows are evidence-only and no live mutation work remains, the verdict must be:

```text
closeout_state = complete
verdict = no_live_work
downstream_predecessor_status = blocked_before_live_apply
phase4_live_apply_allowed = false
live_execution_round_apply_allowed = false
reason = all rows evidence-only; no live mutation work remains
```
