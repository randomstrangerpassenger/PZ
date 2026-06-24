# Runtime Payload State Integrity Plan

> Status: planned / scope-lock candidate / final synthesized reviews consumed / plan-text terminal / codebase inspection correction incorporated / Phase 0-1 execution ready / final certification gates pending / branch decision pending / no runtime mutation
> 작성일: 2026-06-18
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Roadmap input: `C:/Users/MW/.codex/attachments/945bbd5e-6bd1-4273-b9f3-b7dea57bd6eb/pasted-text.txt` / sha256 `9638D0BEC015D0AAD494CA6DB57C2B81EEE73147163AEACB580670AAB4EAB2D8` / unsealed roadmap reference, consumed only as drafting input
> Review input: `C:/Users/MW/.codex/attachments/9a44a462-c689-495b-b425-2dd1054a1403/pasted-text.txt` / sha256 `F753099B7A52A19D6AD324C8E96D5C4BB82AEA20E2E532CD4A340B7F2990F714` / WARN review reference, C1-C2 and I1-I8/M1-M3 incorporated
> Final synthesized review input: `C:/Users/MW/.codex/attachments/5bae4efe-8cf3-463c-a12f-0840170bdc4d/pasted-text.txt` / sha256 `103E45542582B54AF9FCC495C300AABE223D4440304417714F8187FA3CEC7D51` / WARN certification reference, no required plan revisions, optional N1-N3 and certification ceiling notes incorporated
> Final synthesized review input R2: `C:/Users/MW/.codex/attachments/1d723db0-c103-4570-82e9-c5981700b130/pasted-text.txt` / sha256 `103E45542582B54AF9FCC495C300AABE223D4440304417714F8187FA3CEC7D51` / PASS plan-text and WARN final-certification reference, no required revisions, execution sequence confirmed
> Codebase inspection input: 2026-06-18 read-only inspection found live current / package / candidate runtime chunks already have 21 `unadopted` rows with `text_ko = nil` and no `publish_state`, while the two `unadopted + exposed + non-nil text_ko` rows are present in predecessor rollback snapshot payload only. Phase 0 must verify or supersede this observation with machine-readable evidence.

---

## 1. Objective

Current DVF runtime chunk payload에서 `source` / `runtime_state` / `adoption_state`, `publish_state`, `text_ko` value state의 책임 경계를 전수 audit하고, `unadopted` payload의 allowed shape를 current-compatible contract로 봉인한다.

이 계획은 `unadopted + non-nil text_ko`, `unadopted + publish_state = exposed`, `unadopted + exposed + non-nil text_ko` 조합을 사전 결론 없이 evidence-first로 판정한다. `text_ko = nil` / JSON `null` / missing text는 non-nil display text와 분리한다. 선택 branch는 Phase 2 decision gate에서만 확정한다.

현재 codebase inspection 기준으로 문제의 두 row는 live current violation이 아니라 predecessor rollback snapshot residue로 보인다. 따라서 Phase 0이 이를 재확인하면 이 round의 주된 해결은 live data mutation이 아니라 current shape 봉인, stale predecessor residue 재유입 방지, validator / current-route guard integration이다.

성공 closeout claim은 다음 범위로 제한한다.

```text
Runtime payload state shape is sealed.
unadopted / publish_state / text_ko value combinations are explicitly classified.
validator and current route consume the same payload shape contract.
runtime remains a sealed payload renderer.
```

이 계획은 release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game QA, public-facing Korean text quality acceptance, full compatibility preservation, or cutover reopen을 선언하지 않는다.

Execution gating:

* Plan-text readiness is treated as terminal by the final synthesized reviews; no additional required plan revisions are pending.
* Phase 0 read-only inventory may start.
* Phase 1 evidence characterization may start only to resolve field identity and `publish_state` authority / anomaly status.
* Phase 2 branch selection, Phase 3 matrix seal, Phase 4 validator/current-route seal, Branch A correction, and Branch B contract closeout are blocked until C2 `publish_state` axis authority / residue / anomaly status is resolved in evidence and the required revision gates are represented in artifacts.
* Final seal is additionally blocked until C1 independent review is satisfied by a reviewer independent of the roadmap authorship chain.
* Final seal certification remains WARN until Phase 0/1 evidence, author-reserved branch decision, independent Phase 7 review, and template / execution-contract certification ceiling are closed or explicitly disclosed.
* The next review loop should consume the Phase 0-1 evidence packet, not recertify plan text, unless new scope or new evidence invalidates this plan.
* Claude-authored roadmap review is not independent verification for final seal.

---

## 2. Scope

이 계획은 current runtime chunk bundle의 payload state shape를 inventory하고, current-looking package / candidate surface와 predecessor rollback / historical surface를 분리하며, branch decision, machine-readable matrix, validator / current-route guard, branch-specific alignment, runtime consumer regression, independent review, closeout / ledger 문서화를 수행하는 실행 범위를 정의한다.

Primary execution evidence root:

* `Iris/build/description/v2/staging/runtime_payload_state_integrity/`

Plan artifact:

* `docs/runtime_payload_state_integrity_plan.md`

Expected execution docs:

* `docs/runtime_payload_state_integrity_scope_lock.md`
* `docs/runtime_payload_state_policy.md`
* `docs/runtime_payload_shape_contract.md`
* `docs/runtime_payload_state_integrity_closeout.md`
* `docs/runtime_payload_state_integrity_ledger_packet.md`
* `docs/dvf_contract_current_reseal_payload_state_addendum.md` - subordinate staging draft to be folded into the Phase 0 identified canonical current contract surface

포함 범위:

* current runtime payload inventory and protected baseline capture
* 21-row `unadopted` population audit
* problem row key-level identification, surface-role classification, and provenance audit
* field identity confirmation for `source` / `runtime_state` / `adoption_state`
* successor runtime payload `publish_state` presence / authority / anomaly determination
* `source/runtime_state/adoption_state x publish_state x text_ko value state` combination matrix, with axes collapsed / split / diagnostic-only according to field and publish-state authority resolution
* Branch A `FORBID` and Branch B `ALLOW + REDEFINE` comparison
* author-reserved branch decision; tool output is evidence input only
* selected branch decision and rejected branch predecessor trace
* allowed / forbidden / diagnostic_only / legacy_only / anomaly / impossible matrix seal
* payload shape validator and negative fixture implementation
* current route required validation guard integration, unless Phase 0 proves an existing required validation already consumes the same contract
* package route scope resolution; if skipped, closeout must record `package surface untouched / unguarded` rationale
* predecessor rollback snapshot residue disposition and current-surface re-entry guard
* Branch A data alignment / regeneration path, if selected
* Branch A sealed cutover lineage / additive correction trace, if selected
* Branch B strict no-mutation / redefinition path, if selected
* Branch B display resolution parity verification
* Browser / Wiki / Tooltip / renderer consumer scan for policy-boundary regressions
* independent review before final seal by a reviewer who did not author the roadmap this plan derives from
* review finding ID to plan response mapping in ledger / closeout packet
* additive authority-doc update draft after execution evidence exists

### Explicitly Out Of Scope

* release readiness
* package release readiness
* Workshop readiness
* B42 readiness
* deployment readiness
* manual in-game validation
* full runtime equivalence proof
* full compatibility preservation
* external mod ecosystem compatibility sweep
* full public-facing Korean text quality acceptance
* semantic quality completion
* DVF semantic quality rejudgment for all 2105 rows
* frozen 2105 byte-level recovery
* current cutover reopen
* successor baseline identity reseal
* old chunks / successor chunks dual-current authority
* Layer4 / ACQ_DOMINANT / Acquisition Lexical reopen
* `quality_state` UI exposure
* legacy `active / silent` vocabulary restoration
* monolith bridge restoration
* source authority redesign
* renderer-side publish policy checker
* runtime-side source validation / compose / repair
* unrelated refactor

---

## 3. Non-Goals

* Branch A or Branch B를 Phase 0 전에 사전 확정하지 않는다.
* `unadopted`를 quality-pass, deletion, suppression, hidden, or publish-state 신호로 silent 승격하지 않는다.
* `publish_state`와 `quality_state`를 섞지 않는다.
* renderer가 `source` 또는 `runtime_state`를 보고 표시 정책을 판단하도록 바꾸지 않는다.
* 2084 adopted row의 본문 내용을 변경하지 않는다.
* 21개 `unadopted` population 중 2개 problem row만 보고 전체 조합을 봉인하지 않는다.
* current / staging / historical payload surface를 혼동한 validator를 만들지 않는다.
* predecessor rollback snapshot residue를 live current violation처럼 직접 수정하지 않는다.
* `text_ko = nil`, JSON `null`, or missing text를 non-nil display text로 오판하지 않는다.
* direct runtime chunk edit로 source authority chain을 우회하지 않는다.
* Branch B 선택 시 문서만 수정하고 validator allow rule을 누락하지 않는다.
* Branch A 선택 시 data correction 없이 forbidden rule만 넣지 않는다.
* tool / Codex / validator output만으로 Branch A 또는 Branch B를 자동 선택하지 않는다.
* `publish_state`가 authoritative successor field인지, predecessor-derived legacy visibility residue인지 판정하기 전에 matrix나 validator를 봉인하지 않는다.
* Claude-authored roadmap review를 Phase 7 independent review로 계상하지 않는다.
* closeout에서 release / package / Workshop / public exposure readiness를 암시하지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 기준이다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 Iris DVF 3-3 current readpoint를 따른다.
* current runtime authority는 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`와 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua` 단일 chunk bundle이다.
* current runtime baseline은 `2105 rows / adopted 2084 / unadopted 21`로 읽는다.
* 2026-06-18 read-only codebase inspection은 live current, package peer, current-authority candidate chunks에서 `publish_state` row count 0, `unadopted` 21 rows, `unadopted text_ko = nil` 21 rows, `unadopted non-nil text_ko` 0 rows를 관찰했다. 동일 inspection은 predecessor `phase0/rollback_snapshot_payload`에서 `Base.WeldingMask`와 `farming.WateredCanFull`의 `unadopted + exposed + non-nil text_ko` residue를 관찰했다. Phase 0 machine-readable inventory가 이 observation을 검증하거나 supersede한다.
* monolith `IrisLayer3Data.lua`는 current runtime authority로 복귀하지 않는다.
* runtime Lua는 sealed payload를 렌더링만 하며 compose, repair, source validation, semantic quality judgment, publish policy 판단을 수행하지 않는다.
* legacy `active / silent`는 historical / diagnostic / import alias로만 남으며 current writer / validator / runtime vocabulary로 재도입하지 않는다.
* `adopted / unadopted`는 current runtime vocabulary이지만, quality-pass, publish_state, deletion, suppression 의미로 승격하지 않는다.
* `quality_state`는 UI visibility에 관여하지 않고 Browser / Wiki / Tooltip에 badge, sorting, filtering, hiding, recommendation, trust / confidence 표시로 소비되지 않는다.
* `publish_state` visibility authority와 `source/runtime_state/adoption_state` lineage authority는 분리해서 검토한다.
* `text_ko` axis는 boolean presence가 아니라 `missing`, `null_or_nil`, `non_nil_string`으로 분해한다. Lua source text에 `["text_ko"] = nil`이 있더라도 runtime display body는 없는 것으로 판정한다.
* successor runtime chunk payload의 per-row `publish_state`가 authoritative successor field인지, predecessor-derived legacy visibility residue인지, sealed contract 대비 anomaly인지 여부는 Phase 0-1 evidence로 확정하기 전까지 미정이다.
* `source`와 `runtime_state`가 같은 축인지, 별도 field identity인지 여부는 Phase 0-1에서 증거로 확정한다.
* Phase 2 Branch A / Branch B selection is an author-reserved project decision by the project author / maintainer; tool output, validator output, and Codex analysis are evidence inputs only.
* Phase 7 independent reviewer must be independent of the roadmap authorship chain for this plan. Claude-authored review artifacts do not satisfy independent verification.
* `docs/dvf_contract_current_reseal_payload_state_addendum.md` is a subordinate staging draft that must be folded into the canonical current contract surface identified in Phase 0. If the canonical `dvf_contract_current_reseal` surface is missing or renamed, Phase 0 must record the canonical target or block final seal.
* Roadmap / review input fingerprints are trace metadata. If later copy / paste / encoding changes produce hash mismatch, the mismatch is carried forward in the ledger note instead of silently replacing the input trace.
* Branch A는 affected current row count가 nonzero일 때 user-facing output delta가 발생할 수 있으므로 heavy validation이 필요하다. Affected current row count가 0이면 Branch A는 reseal / guard-only heavy validation으로 축소된다.
* Branch B는 runtime content mutation이 없더라도 contract / validator / consumer interpretation이 바뀌므로 standard-heavy validation이 필요하다.
* dirty working tree가 있으면 이 계획의 의도된 파일과 무관한 변경은 보존한다.

---

## 5. Repository Areas Affected

### Code

Expected new or changed build-time tooling, only after Phase 0 command-surface resolution:

* `Iris/build/description/v2/tools/build/` - runtime payload inventory, matrix, validator, report, and route-guard helper surfaces
* `Iris/build/description/v2/tests/` - focused payload shape validator, negative fixture, current-route integration, consumer-boundary tests
* `Iris/_docs/round3/round3_run_contract_tests.py` - reviewed wiring target if the existing closure-enforcing current route does not already consume the selected payload shape contract

Read-only or inspection-only runtime surfaces:

* `Iris/media/lua/client/Iris/` - renderer / Browser / Wiki / Tooltip consumer boundary scan
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`

### Docs

Direct plan artifact:

* `docs/runtime_payload_state_integrity_plan.md`

Expected closeout / policy docs:

* `docs/runtime_payload_state_integrity_scope_lock.md`
* `docs/runtime_payload_state_policy.md`
* `docs/runtime_payload_shape_contract.md`
* `docs/runtime_payload_state_integrity_closeout.md`
* `docs/runtime_payload_state_integrity_ledger_packet.md`
* `docs/dvf_contract_current_reseal_payload_state_addendum.md` - subordinate staging draft, not a permanent parallel authority surface

Authority docs touched only after execution closeout evidence exists:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Read-only inputs:

* `docs/Philosophy.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/EXECUTION_CONTRACT.md`
* existing DVF 3-3 vNext plan / closeout / ledger documents referenced by Phase 0

### Config

* `Iris/_docs/round3/current_route_required_validations.json` - selected branch validator must be consumed by current route required validation unless Phase 0 proves an existing required validation already consumes the same contract.

### Generated Artifacts

All execution evidence must be written under:

* `Iris/build/description/v2/staging/runtime_payload_state_integrity/`

Expected artifact families:

* `phase0/runtime_payload_state_inventory.json`
* `phase0/unadopted_payload_rows.jsonl`
* `phase0/field_identity_resolution.json`
* `phase0/publish_state_authority_resolution.json`
* `phase0/surface_role_classification.json`
* `phase0/rollback_snapshot_residue_scan.json`
* `phase0/payload_state_combination_matrix.preview.md`
* `phase0/protected_surface_baseline_hashes.json`
* `phase0/current_contract_surface_resolution.md`
* `phase0/input_fingerprint_carry_forward.md`
* `phase0/package_route_scope_resolution.md`
* `phase0/scope_lock.md`
* `phase1/runtime_payload_state_evidence_inventory.md`
* `phase1/unadopted_provenance_audit.jsonl`
* `phase1/affected_payload_rows.md`
* `phase1/renderer_read_behavior_trace.md`
* `phase1/publish_state_anomaly_determination.md`
* `phase2/payload_shape_branch_decision.md`
* `phase2/unadopted_payload_row_disposition.jsonl`
* `phase2/author_reserved_branch_decision_record.md`
* `phase3/runtime_payload_shape_matrix.json`
* `phase3/runtime_payload_shape_matrix.md`
* `phase3/payload_shape_axis_definition.md`
* `phase3/renderer_responsibility_boundary.md`
* `phase3/validator_responsibility_boundary.md`
* `phase4/payload_shape_validation_report.json`
* `phase4/current_route_payload_state_guard_report.json`
* `phase4/equivalent_required_validation_evidence.json` - only if no new current-route required validation is added
* `phase4/dual_zero_payload_shape_guard_report.json`
* `phase5a/` - Branch A correction / regeneration evidence, only if selected
* `phase5a/sealed_cutover_additive_correction_lineage.md` - Branch A only
* `phase5b/` - Branch B redefinition / no-mutation evidence, only if selected
* `phase5b/display_resolution_parity_report.json`
* `phase6/runtime_consumer_impact_report.md`
* `phase7/independent_review.md`
* `phase7/review_finding_resolution_map.md`
* `phase7/template_execution_contract_certification_ceiling.md`
* `phase7/package_route_scope_rationale.md`
* `phase7/runtime_payload_state_integrity_closeout.md`
* `phase7/runtime_payload_state_integrity_ledger_packet.md`

Protected current authority surfaces that must not be mutated without the selected branch and explicit phase authorization:

* `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
* `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
* `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
* `Iris/build/description/v2/output/dvf_3_3_rendered.json`
* `Iris/build/description/v2/output/style_normalization_changes.jsonl`
* `Iris/build/description/v2/output/compose_requeue_candidates.jsonl`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`

Forbidden current-looking / monolith re-entry surfaces:

* `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`

---

## 6. Planned Changes

### Change 1 - Phase 0 Scope Lock / Baseline Capture

Purpose:

현재 runtime payload 상태와 변경 금지선을 고정한다.

Files:

* `Iris/build/description/v2/staging/runtime_payload_state_integrity/phase0/*`
* `docs/runtime_payload_state_integrity_scope_lock.md`

Implementation Notes:

* current runtime chunk bundle 전체에서 key, state field identity, `publish_state`, `text_ko` value state, chunk path, rendered path를 추출한다.
* `text_ko`는 `missing`, `null_or_nil`, `non_nil_string`으로 분해해 기록한다. `null_or_nil`은 display body 없음으로 취급한다.
* 21개 `unadopted` row를 전수 분리한다.
* problem row 2건을 key-level로 식별하되, 먼저 live current, package peer, current-authority candidate, predecessor rollback snapshot, diagnostic / historical staging 중 어느 surface role에서만 재현되는지 확정한다.
* `surface_role_classification.json`을 작성해 current / current-looking surface와 historical / rollback / diagnostic surface를 fail-loud로 분리한다.
* `rollback_snapshot_residue_scan.json`을 작성해 predecessor rollback snapshot의 forbidden-looking residue가 current route나 package route의 current input으로 재소비될 수 있는지 판정한다.
* `field_identity_resolution.json`을 작성한다. Required fields:
  * `observed_in_runtime`
  * `observed_in_rendered`
  * `observed_in_source`
  * `canonical_axis`
  * `alias_of`
  * `current_contract_role`
  * `matrix_axis_role`
* `publish_state_authority_resolution.json`을 작성해 successor runtime chunk payload가 per-row `publish_state`를 실제로 보유하는지, authoritative successor field인지, predecessor-derived legacy visibility residue인지, sealed contract 대비 anomaly인지 판정한다.
* source / rendered / runtime chain의 current authority 파일을 재확인한다.
* protected surface baseline hash snapshot을 만든다.
* `docs/dvf_contract_current_reseal_payload_state_addendum.md`가 접힐 canonical current contract surface를 확인한다. `docs/dvf_contract_current_reseal.md`가 absent이면 absent 상태와 대체 canonical target을 기록하거나 final seal blocker로 둔다.
* roadmap / review input fingerprint가 후속 copy / paste / encoding change로 달라질 경우 carry-forward ledger note에 남긴다.
* `package_route_scope_resolution.md`를 작성해 payload state guard가 package/current-looking surface 재유입 방지까지 관여하는지 판정한다. 관여하면 package route validation은 expected route로 둔다. 생략할 경우 `package surface untouched / unguarded` rationale과 closeout carry-forward 조건을 기록한다.
* Phase 0은 read-only이며 runtime / rendered / source mutation을 하지 않는다.

Validation:

* inventory total row count equals current runtime entry count.
* 21 `unadopted` rows are enumerated.
* unknown source/runtime enum count is 0 or explicitly blocked.
* field identity resolution exists and each candidate field has `matrix_axis_role`.
* publish_state authority resolution exists and blocks Phase 2+ if unresolved.
* active/silent current-surface hit count is 0.
* protected baseline snapshot exists.
* current contract surface resolution exists.
* package route scope resolution exists.
* surface role classification exists and does not classify predecessor rollback snapshot as live current.
* rollback snapshot residue scan exists and records current re-entry risk.
* `text_ko = nil` / JSON `null` is not counted as non-nil display text.
* no-mutation verdict exists.

---

### Change 2 - Phase 1 Evidence Characterization / Provenance Audit

Purpose:

문제 row와 전체 `unadopted` population의 provenance와 observed shape를 확정한다.

Files:

* `Iris/build/description/v2/staging/runtime_payload_state_integrity/phase1/*`

Implementation Notes:

* problem row의 key, surface role, chunk path, rendered path, source path를 확인한다.
* non-nil `text_ko`가 compose, fallback, normalization, source-backed path, or predecessor snapshot path 중 어디에서 생성됐는지 추적한다.
* `unadopted + non-nil text_ko`, `unadopted + exposed`, `unadopted + exposed + non-nil text_ko` 발생 수를 surface role별로 확정한다.
* problem row의 `publish_state = "exposed"`가 current sealed contract 대비 allowed field인지, predecessor rollback residue인지, anomaly인지 판정한다.
* Phase 0 observation이 유지되어 affected current row count가 0이면 Phase 5A data correction target은 `none`으로 두고, stale rollback residue disposition과 re-entry guard를 필수 산출물로 둔다.
* Phase 0 `publish_state_authority_resolution.json`이 unresolved이면 Phase 1은 그 해소 목적의 read-only evidence만 생산하고 Phase 2로 넘어가지 않는다.
* renderer가 실제 표시 판단에 사용하는 field를 trace한다.
* `source`, `runtime_state`, `adoption_state`의 field identity와 axis semantics를 분리한다.
* renderer가 `publish_state`를 보지 않고 non-nil text value만 표시 body로 쓰는 경우, Branch A에서 `publish_state` 조정만으로 correction complete claim을 할 수 없음을 기록한다.

Validation:

* 21-row audit complete.
* affected row count is explicit by surface role.
* renderer read-behavior trace matches code path.
* publish_state authority / anomaly determination is resolved or Phase 2+ remains blocked.
* source/rendered/runtime/current-looking/historical surface cross-check exists.
* affected current row count is explicit, including 0 if the problem rows are predecessor-only.
* no-mutation verdict remains true.

---

### Change 3 - Phase 2 Allowed-Shape Contract Decision Gate

Purpose:

`unadopted` payload의 allowed shape와 forbidden shape를 selected branch로 봉인한다.

Files:

* `docs/runtime_payload_state_policy.md`
* `Iris/build/description/v2/staging/runtime_payload_state_integrity/phase2/*`

Implementation Notes:

* Branch A `FORBID`: `unadopted`는 current runtime display payload를 가질 수 없다는 contract로 평가한다. Phase 0-1이 affected current row count 0을 증명하면 Branch A는 data-correction branch가 아니라 reseal / guard-only branch로 실행된다.
* Branch B `ALLOW + REDEFINE`: `unadopted`는 visibility가 아니라 adoption lineage / runtime vocabulary axis라는 contract로 평가한다.
* 판정 기준은 current sealed decisions, provenance, legacy `silent` 재유입 위험, `publish_state` visibility authority, data mutation / public-facing delta, docs-validator 동일 contract 소비 가능성이다.
* Branch selection is author-reserved. Codex, tools, inventory reports, validators, and review packets provide evidence only and may not auto-select Branch A or Branch B.
* `publish_state`가 authoritative successor field가 아니거나 anomaly로 판정되면 Branch A/B comparison은 해당 axis를 visibility axis로 쓰지 않고, diagnostic / residue / anomaly disposition을 먼저 반영한다.
* row-level `publish_state` 보정이 sealed `publish_state` no-mutation / predecessor-only disposition과 정합되는지 판정한다.
* selected branch와 rejected branch를 모두 기록한다.
* row-level disposition을 `unadopted` population 전체와 predecessor-only problem rows에 부여한다.

Validation:

* selected branch has no unresolved contradiction with current decisions.
* non-selected branch assumptions are recorded.
* affected rows have explicit row-level disposition by current / predecessor-only role.
* branch decision does not silently change publish policy.
* author-reserved branch decision record exists before Phase 3.
* publish_state axis premise is resolved before branch selection.
* no source / rendered / runtime mutation occurs before branch authorization.

---

### Change 4 - Phase 3 Payload Shape Contract Seal

Purpose:

선택 branch를 machine-readable matrix와 responsibility boundary로 봉인한다.

Files:

* `docs/runtime_payload_shape_contract.md`
* `docs/dvf_contract_current_reseal_payload_state_addendum.md`
* `Iris/build/description/v2/staging/runtime_payload_state_integrity/phase3/*`

Implementation Notes:

* `source/runtime_state/adoption_state x publish_state x text_ko value state` matrix를 작성한다.
* matrix construction rule은 Phase 0 `field_identity_resolution.json`과 `publish_state_authority_resolution.json`을 따른다. Field identity가 단일 축으로 판정되면 first dimension을 collapse하고, 별도 축이면 split한다.
* `publish_state`가 authoritative successor field가 아니라 predecessor-derived residue 또는 anomaly로 판정되면 matrix에서 authoritative visibility axis로 쓰지 않고 `diagnostic_only` / `legacy_only` / `anomaly` role로 한정한다.
* `all 2105 rows classified` claim은 Phase 0-1에서 확정된 axis definition에 대해서만 적용한다.
* 각 조합을 `allowed`, `forbidden`, `diagnostic_only`, `legacy_only`, `anomaly`, `impossible` 중 하나로 분류한다.
* all observed combinations를 matrix에 포함한다.
* renderer responsibility boundary와 validator responsibility boundary를 문서화한다.
* `quality_state` no-exposure, active/silent rejection, monolith non-reentry를 재봉인한다.

Validation:

* all current 2105 rows are classified.
* axis definition report exists and matches Phase 0-1 determinations.
* unclassified combination count is 0.
* forbidden combinations have explicit fail reason.
* allowed combinations do not create unnecessary warning.
* quality_state UI no-exposure remains enforced.

---

### Change 5 - Phase 4 Validator / Guard Implementation

Purpose:

payload shape contract를 fail-loud build-time validator와 current-route guard로 구현한다.

Files:

* `Iris/build/description/v2/tools/build/` - exact validator path to be resolved in Phase 0
* `Iris/build/description/v2/tests/` - focused validator and negative fixture tests
* `Iris/_docs/round3/current_route_required_validations.json` - selected branch validator must be wired as a required current-route validation unless `equivalent_required_validation_evidence.json` proves an existing required validation already consumes the same contract
* `Iris/build/description/v2/staging/runtime_payload_state_integrity/phase4/*`

Implementation Notes:

* matrix check를 payload shape validator에 추가한다.
* selected branch에 따라 `unadopted + exposed + non-nil text_ko`의 pass/fail을 구현한다.
* validator는 `text_ko = nil` / JSON `null` / missing text를 non-nil display text와 구분한다.
* forbidden combination negative fixtures를 추가한다.
* selected branch validator는 current route required validation에 편입한다. 직접 추가하지 않는 경우 `equivalent_required_validation_evidence.json`이 동일 contract 소비를 증명해야 한다.
* current-looking runtime / package / staging / historical surface 분류를 fail-loud로 구분한다.
* predecessor rollback snapshot residue는 current violation으로 오탐하지 않되, current route / package route 재유입 가능성이 있으면 fail-loud로 막는다.
* payload shape guard는 selected current/current-looking surfaces에 대해 dual-zero gate를 보고해야 한다: `static_forbidden_current_count == 0`, `static_unclassified_current_count == 0`, `dynamic_forbidden_reach_count == 0`. Historical / predecessor residue count는 별도 `predecessor_residue_count`로 보고한다.
* package route와 Lua syntax route가 forbidden current-looking payload를 놓치지 않는지 확인한다.

Validation:

* focused validator unit tests pass.
* negative forbidden-combination fixture fails loud.
* current route passes with required validation manifest or equivalent required validation evidence.
* current-surface dual-zero payload shape guard passes.
* predecessor residue count is explicit and not current-route-consumable.
* package route passes, if package-surface guard is in scope.
* Lua syntax passes.
* historical / diagnostic fixtures are not misclassified as current violations.

---

### Change 6 - Phase 5A FORBID Data Alignment / Regeneration

Purpose:

Phase 2에서 Branch A가 선택된 경우, forbidden current `unadopted` display payload를 source authority chain에서 교정하거나, affected current row count가 0이면 reseal / guard-only path로 봉인한다.

Files:

* `Iris/build/description/v2/data/dvf_3_3_input_manifest.json` - only if selected correction requires it
* `Iris/build/description/v2/data/dvf_3_3_facts.jsonl` - only if selected correction requires it
* `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl` - only if selected correction requires it
* `Iris/build/description/v2/output/*` - regenerated only through approved chain
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua` - only through approved regeneration / single-authority path
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua` - only through approved regeneration / single-authority path
* `Iris/build/description/v2/staging/runtime_payload_state_integrity/phase5a/*`

Implementation Notes:

* affected current row를 source authority chain에서만 교정한다.
* Phase 0-1이 problem rows를 predecessor rollback snapshot residue로만 판정하고 current / package / candidate surface가 이미 `unadopted + text_ko nil/null + no publish_state` shape이면 live source / rendered / runtime mutation을 수행하지 않는다. 이 경우 `phase5a/noop_reseal_disposition.md`를 작성하고 validator / current-route / package re-entry guard로만 closeout한다.
* current / current-looking surface에 forbidden row가 있으면 `publish_state`를 non-exposed 계열로 조정하거나 `text_ko`를 null/nil로 제거하는 방식 중 selected contract와 source authority에 맞는 방식을 사용한다.
* correction method는 Phase 1 renderer read-behavior trace에 종속된다. Renderer가 `publish_state`를 표시 판단에 사용하지 않으면 `publish_state` 조정만으로 correction complete claim을 할 수 없다.
* renderer가 `publish_state == "internal_only"`만 제한적으로 차단하고 그 외에는 non-nil `text_ko`를 반환하는 경우, Branch A의 안정적 forbidden shape는 `unadopted + non-nil display text 없음`이다.
* row-level `publish_state` 보정이 필요한 경우, sealed `publish_state` no-mutation / predecessor-only disposition과의 정합성 판정을 Phase 2/3 evidence로 먼저 통과해야 한다.
* Branch A는 sealed cutover lineage에 대한 additive correction plan으로 기록한다. `sealed_cutover_additive_correction_lineage.md`는 어떤 sealed decision/readpoint를 predecessor로 소비했고, 어떤 correction이 additive supersession인지, current cutover reopen이 아님을 명시한다.
* rendered output, Lua bridge, chunk manifest, chunk files는 regeneration chain으로만 생성한다.
* public-facing behavior delta가 있으면 row-level로 기록한다.
* direct chunk edit는 금지한다.

Validation:

* source-rendered-runtime key parity passes.
* determinism passes.
* `unexpected_protected_surface_changed_count == 0`.
* `expected_changed_rows == affected_current_row_disposition rows`.
* intended-only protected surface diff exists.
* if affected current row count is 0, intended-only protected surface diff is explicitly empty and `noop_reseal_disposition.md` exists.
* payload shape validator passes.
* no active/silent current surface.
* no monolith re-entry.
* current route, package route, Lua syntax pass.
* affected current entry public-facing delta is explicitly recorded, or explicitly empty for reseal / guard-only Branch A.
* sealed cutover additive correction lineage exists and does not claim cutover reopen.

---

### Change 7 - Phase 5B ALLOW + REDEFINE Contract Alignment

Purpose:

Phase 2에서 Branch B가 선택된 경우, `unadopted`를 visibility와 분리된 lineage / runtime vocabulary로 명문화하고 existing runtime behavior를 validator와 contract에 맞춘다.

Files:

* `docs/runtime_payload_state_policy.md`
* `docs/runtime_payload_shape_contract.md`
* `Iris/build/description/v2/tools/build/` - validator allow / forbid rule
* `Iris/build/description/v2/tests/` - focused tests
* `Iris/build/description/v2/staging/runtime_payload_state_integrity/phase5b/*`

Implementation Notes:

* `unadopted != hidden`, `unadopted != silent`, `unadopted != quality fail`, `unadopted != deletion`, `unadopted != suppression`를 contract에 명시한다.
* visibility는 renderer read contract가 소유한다는 boundary를 명시한다: `publish_state = internal_only`는 `getText()`에서 suppress되고, 그 외에는 non-nil `text_ko`가 display body가 된다.
* Branch B가 `unadopted + exposed + non-nil text_ko`를 allowed로 재정의하려면 그것이 current/current-looking surface에서 허용되는지, predecessor-only residue에서만 허용되는지 surface role별로 명시한다.
* problem row는 allowed row disposition 또는 predecessor-only residue disposition으로 닫는다.
* enum / field rename은 immediate scope가 아니라 follow-up migration / backlog로만 기록한다.
* Branch B는 strict byte-unchanged branch다. Metadata diff도 live chunk payload에 허용하지 않는다.
* metadata diff가 필요하다고 판정되면 Branch B closeout이 아니라 source-authority-chain regeneration + single-authority switch가 필요한 별도 selected execution path로 재분류한다.
* `display_resolution_parity_report.json`을 작성한다. 최소 대상은 21개 current `unadopted` row이며, 권장 대상은 2105 전체 key의 before/after rendered text resolution hash다.

Validation:

* runtime payload byte-unchanged.
* display resolution parity passes for all 21 current `unadopted` rows; 2105-key parity is expected unless Phase 0 scopes a narrower verified target.
* renderer behavior trace matches contract.
* selected allowed shape passes validator.
* forbidden combinations fail loud.
* current route, package route, Lua syntax pass.
* no quality_state UI exposure.
* no active/silent alias route.

---

### Change 8 - Phase 6 Runtime Consumer Regression

Purpose:

runtime consumer가 selected payload state contract를 오독하지 않는지 확인한다.

Files:

* `Iris/media/lua/client/Iris/` - read-only scan and focused regression target
* `Iris/build/description/v2/tests/` - consumer-boundary tests if needed
* `Iris/build/description/v2/staging/runtime_payload_state_integrity/phase6/*`

Implementation Notes:

* renderer가 `source` / `runtime_state` policy branch를 갖지 않는지 확인한다.
* Browser / Wiki / Tooltip이 `quality_state`를 표시, 정렬, 필터, 숨김, 추천, 신뢰도 표시로 소비하지 않는지 확인한다.
* `publish_state` visibility route가 selected contract와 일치하는지 확인한다.
* `unadopted`를 legacy `silent`처럼 읽는 consumer / validator / test route를 검색한다.

Validation:

* runtime consumer scan exists.
* Browser / Wiki / Tooltip focused regression passes or is explicitly blocked.
* quality no-exposure guard passes.
* publish_state visibility route check passes.
* no runtime source-policy branch.
* no active/silent alias route.

---

### Change 9 - Phase 7 Independent Review / Ledger / Documentation Closeout

Purpose:

selected branch와 산출물을 final seal 전에 독립 검토하고 current docs에 additive로 반영한다.

Files:

* `Iris/build/description/v2/staging/runtime_payload_state_integrity/phase7/*`
* `docs/runtime_payload_state_integrity_closeout.md`
* `docs/runtime_payload_state_integrity_ledger_packet.md`
* `docs/DECISIONS.md` - additive update only after accepted closeout
* `docs/ARCHITECTURE.md` - additive update only after accepted closeout
* `docs/ROADMAP.md` - additive update only after accepted closeout

Implementation Notes:

* independent adversarial review를 수행한다.
* independent reviewer는 이 plan이 파생된 roadmap의 저작자 또는 동일 review chain의 author가 아니어야 한다.
* Claude-authored roadmap / review artifact는 Phase 7 independent verification으로 계상하지 않는다.
* final seal 전 별도 independent reviewer의 review artifact가 필요하다.
* selected branch, rejected branch, matrix, validator evidence, row disposition을 closeout에 연결한다.
* `review_finding_resolution_map.md`를 작성해 review cycle별 finding ID, plan 반영 위치, remaining gate, closeout status를 고정한다. Final synthesized review R2의 `required_revisions=none` verdict와 `next_review_target=phase0_1_evidence_packet`도 기록한다.
* `template_execution_contract_certification_ceiling.md`를 작성해 `PLAN_TEMPLATE.md`와 `EXECUTION_CONTRACT.md`가 final reviewer surface에 포함됐는지, template / execution contract certification이 PASS인지, 아니면 certification ceiling으로 남는지 기록한다.
* package route를 실행하지 않는 경우 `package_route_scope_rationale.md`에 `package surface untouched / unguarded` 근거를 기록한다. Payload guard가 package/current-looking surface 재유입 방지까지 관여하면 package route를 생략하지 않는다.
* authority docs는 실행 evidence가 PASS 또는 honest blocked terminal을 가진 뒤 additive로만 갱신한다.
* release readiness가 아님을 명시한다.
* future reopen criteria를 남긴다.

Validation:

* independent review PASS by a reviewer independent of the roadmap authorship chain, or blocking issue resolved by a later independent review.
* docs wording is consistent with selected branch.
* rejected branch predecessor trace exists.
* claim boundary includes no release / package / Workshop / manual QA readiness.
* artifact paths are recorded.
* review finding resolution map exists.
* template / execution contract certification ceiling is closed or explicitly disclosed.
* package route execution or skip rationale is recorded.
* current decision ledger wording is internally consistent.

---

## 7. Validation Plan

### Automated Validation

Execution-specific validation commands must be resolved in Phase 0. Do not claim validation passed unless the exact command exits with code 0.

Required automated validation families:

* payload state inventory validation
* 21-row `unadopted` population audit validation
* `field_identity_resolution.json` schema validation
* successor `publish_state` presence / authority / anomaly determination validation
* payload shape matrix coverage validation
* payload axis definition validation against field identity and publish-state authority resolution
* focused payload shape validator unit test
* negative forbidden-combination fixture test
* current route contract test
* current route required validation integration or `equivalent_required_validation_evidence.json` validation
* current-surface dual-zero payload shape guard validation: `static_forbidden_current_count == 0`, `static_unclassified_current_count == 0`, `dynamic_forbidden_reach_count == 0`, with `predecessor_residue_count` reported separately
* package route validation, if package surface is touched or guarded
* package route skip-rationale validation, if package route is not executed
* Lua syntax validation
* source-rendered-runtime key parity
* protected surface diff / no-mutation validation
* active/silent forbidden scan
* quality_state no-exposure scan
* renderer source-policy branch absence scan
* runtime consumer scan
* strict byte-unchanged verdict, Branch B
* display resolution parity report, Branch B: minimum 21 current `unadopted` rows, recommended 2105 keys
* intended-only public-facing delta confirmation, Branch A, or explicit empty delta if Branch A is reseal / guard-only
* Branch A renderer-read-behavior-dependent correction method validation
* Branch A protected diff validation: `unexpected_protected_surface_changed_count == 0`, `expected_changed_rows == affected_current_row_disposition rows`
* Branch A sealed cutover additive correction lineage validation, if selected
* independent review artifact existence check
* review finding resolution map validation
* template / execution contract certification ceiling validation

Expected exact validation route candidates:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

If package route validation is in scope:

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean -Zip
```

The payload-state validator command path is intentionally unresolved in this plan and must be pinned by Phase 0 command-surface resolution.

### Manual Validation

* review Branch A / Branch B decision evidence before sealing selected branch
* confirm Branch A / Branch B selection was made by the project author / maintainer, not auto-selected by Codex or tools
* review 21-row `unadopted` audit and row-level disposition
* review `publish_state` authority / anomaly determination before matrix seal
* review payload shape matrix wording and validator boundary
* review Branch A public-facing delta, if selected and affected current row count is nonzero
* review Branch B strict no-mutation / display parity / redefinition wording, if selected
* review independent review findings and reviewer independence before closeout
* review `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md` additive wording before authority-doc sync

Manual validation does not include in-game QA, release QA, Workshop validation, B42 validation, multiplayer validation, long-session runtime validation, external ecosystem compatibility sweep, or full public-facing text quality acceptance.

### Validation Limits

This plan will not validate:

* full manual in-game QA
* long-session runtime validation
* multiplayer validation
* Workshop readiness
* B42 readiness
* deployment readiness
* external mod ecosystem compatibility sweep
* release package approval
* semantic quality completion
* full 2105 text review completion
* full runtime equivalence
* frozen 2105 byte-level recovery
* current cutover authorization
* successor baseline identity final seal

---

## 8. Risk Surface Touch

### Authority Surface

Touched.

This round seals a runtime payload shape contract and may add validator / current-route authority over that contract. It does not automatically replace current source authority or cutover authority.

The `publish_state` axis is not treated as authoritative until Phase 0-1 determines whether successor runtime chunks carry it as a current contract field, predecessor-derived residue, or anomaly.

### Runtime Behavior Surface

Conditional.

Branch A may change currently visible affected entry text or exposure only if Phase 0-1 finds forbidden current/current-looking rows. If problem rows are predecessor-only residue, Branch A is expected to be reseal / guard-only with empty public-facing delta. Branch B should preserve existing runtime behavior and make the contract explicit. Branch B preservation requires display resolution parity, not only byte unchanged evidence. In both branches, renderer must remain render-only.

### Compatibility Surface

Conditional.

Branch B may reveal internal consumer misunderstanding if any consumer treated `unadopted` as hidden. Branch A may create public-facing behavior delta only for affected current rows; predecessor-only residue must close as guard / quarantine evidence, not live data mutation. External mod compatibility sweep is out of scope.

### Sealed Artifact Surface

Touched.

New sealed or additive artifacts may include payload shape contract, matrix, validator report, current-route guard evidence, runtime consumer impact report, closeout, and ledger packet. Existing sealed artifacts are read-only unless a selected branch explicitly authorizes regeneration through the source authority chain. The payload-state addendum is a subordinate staging draft until folded into the canonical current contract surface identified by Phase 0.

### Public-Facing Output Surface

Conditional.

Branch A can alter affected current row visibility or displayed text only when current forbidden rows exist. Branch B is expected to preserve public-facing output. Neither branch adds quality badges, confidence labels, recommendation, comparison, or public release messaging.

---

## 9. Risk Analysis

### Architecture Risk

* Branch selection may happen before evidence inventory is complete.
* docs and validator may encode different semantics.
* `unadopted` may be accidentally revived as legacy `silent`.
* `publish_state` visibility authority and source/runtime lineage authority may be mixed.
* `publish_state` may be sealed as a matrix axis before authority / residue / anomaly status is resolved.
* renderer may gain policy judgment responsibility.
* direct chunk edit may bypass source authority chain.
* selected contract may reopen cutover-sealed surfaces without explicit authorization.
* Phase 2 branch selection may be treated as tool-selected instead of author-reserved.
* Claude-authored review artifacts may be miscounted as independent verification.

### Runtime Risk

* Branch A may remove or hide currently displayed text without explicit public-facing delta record, or may mutate live current despite affected current row count 0.
* Branch A may choose a correction method that the renderer does not actually read.
* Branch B may leave ambiguous naming without validator and docs reinforcement.
* Branch B may overclaim behavior preservation without display resolution parity.
* Branch B may use metadata diff as a no-mutation bypass.
* validator may over-fit to two known rows instead of the full 21-row population.
* runtime consumer may interpret `unadopted` inconsistently across Browser / Wiki / Tooltip.
* Lua runtime may be changed to compensate for a build-time contract issue.

### Compatibility Risk

* internal consumers may have relied on an undocumented `unadopted == hidden` assumption.
* package route and current route may diverge on forbidden current-looking payload detection.
* package route may be skipped without recording why package surface is untouched / unguarded.
* generated / staging / historical payloads may be misclassified as current violations.
* enum / field rename may expand the scope into consumer migration if not deferred.

### Regression Risk

* affected row count may be larger than the initial two problem rows, or may be zero for live current if the two rows are predecessor-only residue.
* `text_ko` provenance may remain ambiguous.
* `quality_state` no-exposure may weaken during consumer regression changes.
* active/silent current vocabulary may re-enter through tests, fixtures, generated artifacts, or import aliases.
* monolith runtime may re-enter as a convenient inspection or package fallback.
* closeout wording may overclaim release readiness or public text quality completion.

---

## 10. Rollback Plan

Rollback is additive-evidence and authority-chain based, not direct runtime patch revert.

* Phase 0 baseline hash snapshot is the rollback reference.
* Phase 0-1 inventory / characterization are read-only and have no runtime rollback target.
* Phase 2 branch decision is additive and can be superseded only by an explicit later decision.
* Branch A data alignment must be revertible through source/rendered/Lua bridge/chunk regeneration or a recorded baseline restore, not direct chunk edits.
* Branch A rollback must record the public-facing delta and rollback reason when affected current row count is nonzero; reseal / guard-only Branch A rollback must record guard invalidation reason instead.
* Branch B docs / validator changes can be reverted or superseded if consumer confusion or display parity failure appears, with the policy decision reopened additively.
* Branch B may not roll forward with metadata diff. If metadata diff is required, rollback Branch B closeout and reopen as source-authority-chain regeneration / single-authority execution.
* If validator or current-route integration is wrong, remove or correct the guard through a blocked / invalid guard assumption closeout and correction plan.
* If an existing current-route validation was incorrectly treated as equivalent, invalidate `equivalent_required_validation_evidence.json` and wire the selected branch validator as a required validation before closeout.
* If protected surface mutation is detected outside selected branch authorization, fail close and restore from the baseline / source authority chain.
* Failed evidence is quarantined under the staging root and must not be silently consumed by current route.
* No rollback path may claim release readiness, deployment readiness, or public runtime recovery.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance must be preserved.
* Hub & Spoke / SPI boundaries remain unchanged.
* Iris remains a Lua runtime display layer and must not become a runtime analysis / repair / policy engine.
* Runtime / build-time separation must be preserved.
* Runtime Lua must not compose, repair, validate source, judge semantic quality, or judge publish policy.
* Current runtime authority remains chunk manifest + chunk files single bundle unless a separate approved cutover changes it.
* Monolith `IrisLayer3Data.lua` must not re-enter current runtime / package / workspace authority.
* Direct chunk payload edit is forbidden.
* Data correction must go through the source authority chain and regeneration chain.
* `adopted / unadopted` must not become quality-pass, publish_state, deletion, or suppression vocabulary unless explicitly selected branch contract and matrix say so.
* `active / silent` must not return as current writer / validator / runtime vocabulary.
* `quality_state` must not be exposed in UI or consumed as visibility, sorting, filtering, recommendation, trust, or confidence signal.
* `publish_state` and `quality_state` must remain separate axes.
* `publish_state` matrix role must be derived from Phase 0-1 authority / residue / anomaly determination, not assumed.
* The selected branch must be reflected consistently in docs, validator, and current-route guard.
* Phase 2 branch selection is author-reserved by the project author / maintainer; tools and Codex do not select the branch.
* The rejected branch must remain as predecessor trace.
* Current-route guard must fail closed / fail loud and must consume the selected branch contract unless equivalent required validation evidence proves the contract is already consumed.
* Payload shape guard must report `static_forbidden_current_count == 0`, `static_unclassified_current_count == 0`, and `dynamic_forbidden_reach_count == 0`, with predecessor residue counted separately.
* Branch B is strict byte-unchanged; metadata diff is not allowed under Branch B closeout.
* Branch B requires display resolution parity for at least the 21 current `unadopted` rows.
* Branch A correction method must be justified by renderer read-behavior evidence.
* Independent final review must be performed by a reviewer independent of the roadmap authorship chain; Claude-authored roadmap review does not satisfy this gate.
* Payload shape addendum is subordinate until folded into the canonical current contract surface identified by Phase 0.
* Review finding IDs must be mapped in closeout / ledger to avoid losing which WARN-cycle findings were resolved, carried forward, or gated.
* Template / execution contract certification ceiling must be disclosed if the final reviewer surface does not include `PLAN_TEMPLATE.md` and `EXECUTION_CONTRACT.md`.
* Package route may be skipped only with explicit package surface untouched / unguarded rationale.
* Sealed decision body and sealed evidence are mutated only through additive docs updates and approved source-authority execution paths.
* This round must not declare release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA completion, or public-facing text quality acceptance.

---

## 12. Expected Closeout State

Expected closeout target: `complete` only if one branch is selected by the project author / maintainer, implemented, validated, independently reviewed by a reviewer independent of the roadmap authorship chain, and reflected in closeout / ledger artifacts.

Complete closeout requires:

* `field_identity_resolution.json` exists and resolves matrix axis roles
* `publish_state_authority_resolution.json` exists and resolves whether `publish_state` is authoritative successor field, predecessor-derived residue, or anomaly
* all 2105 current payload rows are classified by payload shape matrix according to the resolved axis definition
* all 21 `unadopted` rows are audited
* `unadopted + text_ko nil/null/missing` allowed / forbidden status is explicit
* `unadopted + non-nil text_ko` allowed / forbidden status is explicit
* `unadopted + exposed` allowed / forbidden status is explicit
* `unadopted + exposed + non-nil text_ko` allowed / forbidden status is explicit
* problem rows have row-level disposition and surface role disposition
* Phase 2 branch decision has an author-reserved decision record
* selected branch is reflected consistently in docs, validator, and current route guard
* current route required validation consumes the selected branch validator, or `equivalent_required_validation_evidence.json` proves an existing required validation consumes the same contract
* rejected branch is preserved as predecessor trace
* forbidden combinations fail loud
* allowed combinations pass without unnecessary warning
* current-surface dual-zero payload shape guard passes: `static_forbidden_current_count == 0`, `static_unclassified_current_count == 0`, `dynamic_forbidden_reach_count == 0`, with predecessor residue count reported separately
* renderer does not perform source/runtime_state policy judgment
* `quality_state` is not exposed or consumed as UI visibility signal
* `active / silent` does not re-enter current writer / runtime / validator surface
* current runtime authority remains chunk bundle single authority
* monolith re-entry count is 0
* source-rendered-runtime parity is preserved or expected-only Branch A delta is recorded
* current route, package route if applicable, and Lua syntax validation pass with exact commands
* if package route is skipped, `package_route_scope_rationale.md` records `package surface untouched / unguarded` and explains why payload state guard does not touch package/current-looking surface
* Branch A, if selected, records intended-only public-facing delta or explicit empty delta for reseal / guard-only execution, renderer-read-behavior-dependent correction method, `unexpected_protected_surface_changed_count == 0`, and `expected_changed_rows == affected_current_row_disposition rows`
* Branch A, if selected, records sealed cutover additive correction lineage without claiming current cutover reopen
* Branch B, if selected, records strict runtime payload byte-unchanged and display resolution parity for at least the 21 current `unadopted` rows
* independent review is complete and is not satisfied by Claude-authored roadmap / review artifacts
* payload shape addendum has a recorded canonical current contract fold-in target or final seal remains blocked
* review finding resolution map exists and records finding ID, plan response, status, and carry-forward gate
* template / execution contract certification ceiling is PASS or explicitly disclosed as a final certification limit
* closeout and ledger packet include claim boundary

If `publish_state` authority / anomaly status is unresolved, closeout state must be `blocked` or `partial`, not `complete`.

If branch decision is blocked by insufficient provenance or missing author-reserved decision, closeout state must be `blocked` or `partial`, not `complete`.

If implementation exists but required validation is missing or fails, closeout state must be `implemented_only` or `partial`, not `complete`.

If independent review is performed by a reviewer from the roadmap authorship chain, closeout state must not be `complete`.

This closeout must not claim:

* release readiness
* package readiness
* Workshop readiness
* B42 readiness
* deployment readiness
* manual in-game QA completion
* external compatibility guarantee
* full runtime equivalence
* semantic quality completion
* full 2105 text review completion
* Browser / Wiki / Tooltip policy redesign
* frozen 2105 recovery
* current cutover reopen or successor baseline identity final seal
