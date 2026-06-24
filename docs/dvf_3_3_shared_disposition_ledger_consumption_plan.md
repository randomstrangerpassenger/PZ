# Implementation Plan

> Status: planned / roadmap-derived / WARN review revisions incorporated / candidate-only core / live-adoption branch hold / no-op default clarified / no execution performed
> 작성일: 2026-06-21
> Roadmap input: `C:/Users/MW/.codex/attachments/262a588b-b1f4-45a8-9488-7f916398beef/pasted-text.txt` / sha256 `56513E84F70C06465D617D5B602B2DD6C7FEEAC66C19B26D8BB6EEAE7F9B0A7F`
> Review input: `C:/Users/MW/.codex/attachments/8e79dfe3-0b09-4a8f-aee3-c61be3c216e7/pasted-text.txt` / sha256 `D980B7AB456331D76BA309158A9CACDF02D628896662899BFD23C91944158202`
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Execution contract input: `docs/EXECUTION_CONTRACT.md` / sha256 `A185BBD78EB849B0310D9AADC9102CB156B892513266FAC0EC7903EB3D3A9493`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Roadmap provenance tie-out: the roadmap bytes used for this plan are the exact attachment listed above; no separate sealed roadmap artifact was supplied as input for this plan revision.

---

## 1. Objective

DVF 3-3의 sealed terminal disposition / denominator 판단을 `manifest / tools / docs / tests / validators`가 같은 shared disposition consumption contract로 소비하도록 봉인한다.

이 계획의 핵심 목적은 다음이다.

```text
closed disposition and denominator evidence is not re-adjudicated.
all relevant downstream surfaces consume one shared contract or adapter-mediated route.
raw audit / readiness / sandbox / dry-run / historical artifacts do not become current execution authority.
predecessor 2105 / 2084 / 21 cannot re-enter as current debt.
divergent consumption fails loud instead of silently passing.
```

현재 닫힌 판단은 재판정하지 않는다. `1062` executing-consumer member-row denominator, terminal split `migrated=153 / no-op=268 / diagnostic-only=3 / historical-only=638`, readiness/execution split `153 = 109 live_mutation_eligible + 44 evidence_only + 0 blocked`, predecessor `2105 / 2084 / 21` baseline의 historical/comparison role은 이 계획의 입력 readpoint다.

이 계획은 current source / rendered / Lua bridge / runtime chunk / package payload를 변경하는 계획이 아니다. 최대 claim은 relevant downstream consumption surface가 같은 disposition contract를 소비하고, forbidden direct raw authority read / value divergence / predecessor re-entry가 fail-loud로 차단되었다는 것이다.

### 1.1 Shared Consumption Success Boundary

This plan is scoped to the first subproblem only: Shared Disposition Ledger Consumption.

Successful closeout means the relevant `manifest / tools / docs / tests / validators` surfaces either consume the same shared disposition contract / packet / adapter-mediated route, or are explicitly classified as non-executable provenance / docs-only references with matching claim boundary.

This plan does not close the separate Closeout / Reentry Guard Seal problem. It may produce inputs for that later round, but it must not claim that broad completion wording, current hard gate reentry, runtime authority reentry, or closeout taxonomy have been fully sealed.

### 1.2 Expected Blocker Mitigation Matrix

The known blockers for this first subproblem are execution/design blockers, not current evidence that the plan is impossible.

| Potential blocker | Mitigation in this plan | Closeout evidence |
|---|---|---|
| Numeric census noise from common tokens such as `21`, `44`, `109`, `153`, and `0` | Bounded path / co-occurrence / field-name / artifact-role / docs claim predicates; separate `raw_numeric_occurrence` from `role_bearing_disposition_occurrence` | `bounded_census_predicate.json`, `sealed_axis_token_set.json`, `zero_token_promotion_report.json` |
| False-negative census from missing sealed-axis values such as `27558`, `59`, `252`, `268`, `3`, `638`, `902`, `49`, `111`, and `0` | Full sealed-axis token set or explicit exclusion reasons | `sealed_axis_token_set.json`, full sealed-axis coverage report |
| Raw audit / readiness / sandbox / dry-run artifact read as current execution authority | Forbidden direct-read set, provenance-only role, negative fixtures, `RAW_AUTHORITY_READ = 0` | `forbidden_direct_read_set.json`, `raw_authority_read_report.json`, `direct_raw_read_negative_test_report.json` |
| Surface-specific `2105 / 2084 / 21` interpretation drift | Value resolution table, lifecycle role field, denominator axis field, predecessor re-entry detector | `value_resolution_table.json`, `value_divergence_report.json`, `predecessor_reentry_report.json` |
| Dual route where a consumer reads both shared packet and raw provenance as competing authorities | Dual-authority detector and adapter/no-op realignment rule | `no_dual_authority_read_report.json`, `DUAL_AUTHORITY_READ = 0` |
| Over-implementation when divergence is already zero | Phase 4 no-op default; adapter only for divergent executable consumers | `divergence_report.json`, `no_op_realignment_report.json` |
| Live required-validation adoption touching current-route closure or tooling cap | Artifact/report consumption route is the default adoption path; direct import of new shared tooling from current-route tests is forbidden; subprocess-only fallback remains secondary; adoption hold remains until closure count `12`, tooling cap `1`, and review evidence pass | `current_route_report_consumption_manifest.json`, `current_route_closure_allowlist_report.json`, adoption decision report |

For this plan, `complete_candidate_only` is the expected successful closeout if live adoption remains held. `complete_adopted` is allowed only if the additional closure / allowlist / review gates pass without widening current authority.

---

## 2. Scope

이 계획은 DVF 3-3 shared disposition ledger consumption seal round를 수행하기 위한 실행 계획이다.

포함 범위:

* scope lock / claim boundary / input provenance freeze
* `manifest / tools / docs / tests / validators` consumption census
* bounded census predicate definition for numeric / disposition / artifact path scanning
* full sealed-axis token role classification: `1062 / 311 / 163 / 153 / 148 / 109 / 44 / 2105 / 2084 / 21 / 27558 / 59 / 252 / 268 / 3 / 638 / 902 / 49 / 111 / 0`
* canonical consumption contract 또는 candidate packet 정의
* row identity, denominator axis, lifecycle role, artifact provenance field 정의
* forbidden direct-read set 정의
* divergence detector 작성
* divergent surface의 adapter-mediated route 또는 manifest route 정렬
* raw audit / readiness / sandbox / dry-run / diagnostic / historical artifact containment guard
* predecessor baseline current-debt re-entry guard
* docs claim boundary alignment
* current-route required-validation adoption candidate 작성, 단 live adoption은 별도 승인 gate로 분리
* current-route closure / tooling allowlist cap preservation evidence
* cross-surface matrix / row coverage / negative fixture validation
* negative fixture containment outside current-looking artifact paths
* independent review artifact hash report 및 owner adoption state 분리 기록

Primary execution evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/`

Direct plan artifact:

* `docs/dvf_3_3_shared_disposition_ledger_consumption_plan.md`

### Explicitly Out Of Scope

* Phase 4 live migration apply 실행
* live mutation completion 선언
* denominator / terminal disposition 재판정
* broad consumer universe 재정의
* source facts / decisions 수정
* rendered output 재생성
* Lua bridge 또는 runtime chunk 교체
* package payload 수정
* predecessor `2105 / 2084 / 21` byte-level recovery
* `active / silent` vocabulary 복귀
* raw audit ledger를 current authority로 승격
* readiness sandbox diff를 migration completion ledger로 승격
* live `current_route_required_validations.json` adoption before closure / allowlist / review gates are sealed
* public-facing text quality acceptance
* release / deployment / Workshop / B42 readiness 판단
* manual in-game QA, multiplayer validation, long-session runtime validation
* broad current-route source-overlay blocker 해결
* runtime payload state integrity residual seal 흡수

---

## 3. Non-Goals

이 계획은 다음을 해결하려 하지 않는다.

* DVF 3-3 current authority chain 재설계
* successor source / rendered / runtime authority 변경
* migration eligibility 재계산
* terminal disposition split 재산출
* readiness taxonomy 재해석
* sandbox output을 live completion evidence로 변환
* current-route tooling allowlist cap 확장
* current core closure 확장
* generated / staging / diagnostic / fixture artifact를 current authority로 승격
* Browser / Wiki / Tooltip runtime behavior 변경
* public require contract 또는 external mod compatibility contract 변경
* release packaging, Workshop upload, B42 deployment 판단

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 설계 권위다.
* DVF 3-3 current authority chain은 `source -> facts -> decisions -> rendered -> Lua bridge -> runtime chunks`로 유지한다.
* runtime은 sealed Lua payload를 표시할 뿐 source validation, compose, repair, semantic quality judgment, publish policy 판단을 수행하지 않는다.
* Denominator Governance와 Terminal Disposition Adjudication은 닫힌 readpoint다.
* `1062`는 executing-consumer member-row denominator이고, `311`, `163`, `153`, `109`, `44`, `148`, `2105`, `2084`, `21`은 count equality가 아니라 denominator axis / lifecycle role / row identity로만 연결한다.
* `153 migrated`는 terminal projection이며 live migration completion이 아니다.
* readiness / sandbox / dry-run artifacts는 pre-apply 또는 provenance evidence이며 current execution authority가 아니다.
* raw audit / raw migration matrix / dry-run output의 downstream direct entrypoint는 기존 sealed manifest route 또는 이번 계획의 shared consumption route를 통해서만 허용한다.
* live `Iris/_docs/round3/current_route_required_validations.json` 채택은 이 계획에서 author/owner decision gate 없이 수행하지 않는다.
* live-adoption branch is on hold until current-route closure, tooling allowlist cap, and review integration evidence are sealed.
* canonical packet 확정, candidate-only 유지, required-validation live adoption, independent review 기준은 실행 중 author/owner decision gate로 남긴다.
* `docs/EXECUTION_CONTRACT.md` checked / no conflict: this plan touches Sealed Artifact Surface and therefore uses explicit disclosure, evidence binding, validation ceiling, non-claims, and closeout discipline.
* Plan-local closeout substates such as `complete_candidate_only` and `complete_adopted` are reducible to `EXECUTION_CONTRACT.md` `complete` with a stated validation ceiling; they are not new ecosystem-wide closeout taxonomy.
* Independent review must be performed by a route that did not generate the reviewed artifacts before either `complete_candidate_only` or `complete_adopted` may be claimed.
* Commands listed as validation evidence must be existence-checked before execution and only exact commands that exit `0` can support PASS claims.
* Negative fixtures must live under `Iris/build/description/v2/tests/fixtures/negative/shared_disposition/` and must be excluded from current-looking artifact scans.
* 기존 작업 트리에는 많은 선행 변경이 존재할 수 있으므로, 이 계획의 실제 구현은 touched files를 명확히 한정하고 unrelated dirty state를 되돌리지 않는다.

---

## 5. Repository Areas Affected

### Code

* `Iris/build/description/v2/tools/build/dvf_3_3_shared_disposition_consumption_common.py`
* `Iris/build/description/v2/tools/build/generate_dvf_3_3_shared_disposition_packet.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_shared_disposition_consumption.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_shared_disposition_consumption.py`
* `Iris/build/description/v2/tools/build/write_dvf_3_3_shared_disposition_ledger_packet.py`
* Existing validator / generator routes that already consume denominator, terminal disposition, readiness, migration, or required-validation artifacts

### Docs

* `docs/dvf_3_3_shared_disposition_ledger_consumption_plan.md`
* `docs/dvf_3_3_shared_disposition_consumption_policy.md`
* `docs/dvf_3_3_shared_disposition_ledger_packet.md`
* `docs/dvf_3_3_shared_disposition_claim_boundary.md`
* `docs/DECISIONS.md` or `docs/DECISIONS.shared_disposition_consumption.patch.md`, if an additive decision packet is approved
* `docs/ROADMAP.md` or `docs/ROADMAP.shared_disposition_consumption.patch.md`, if an additive roadmap packet is approved

### Config

* `Iris/_docs/round3/current_route_required_validations.json`, candidate-only unless live adoption is explicitly approved
* `Iris/_docs/round3/current_route_required_validations.shared_disposition_candidate.json`, if candidate route is retained outside the live manifest
* Any local manifest that records current-route validator families, only when routed through an approved candidate/adoption state

### Generated Artifacts

* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase1/`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase2/`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase3/`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase4/`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase5/`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase6/`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase7/`

---

## 6. Planned Changes

### Change 1 - Scope Lock & Surface Census

Purpose:

이번 라운드를 shared disposition consumption seal로 고정하고, disposition / denominator / predecessor / readiness 값을 소비하는 모든 relevant surface를 열거한다.

Files:

* `Iris/build/description/v2/tools/build/run_dvf_3_3_shared_disposition_consumption.py`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase1/scope_lock.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase1/bounded_census_predicate.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase1/sealed_axis_token_set.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase1/zero_token_promotion_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase1/consumption_census_ledger.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase1/surface_inventory.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase1/unclassified_surface_report.json`

Implementation Notes:

* Do not perform unbounded repo-wide raw numeric grep as a consumption census.
* Define a DVF 3-3 relevant path allowlist before scanning, covering approved `docs/`, DVF 3-3 tools, tests, manifests, validator surfaces, and sealed staging evidence roots.
* Apply bounded predicates before an occurrence becomes a role-bearing census row:
  * co-occurrence with DVF 3-3 / disposition / denominator / readiness / migration vocabulary
  * field-name predicate such as `denominator`, `terminal_disposition`, `lifecycle_role`, `readiness`, `migration`, `current_route`, `predecessor`, `sealed_value_source`
  * artifact-role predicate such as manifest, validator input, tool default, test fixture, docs claim, sealed report, provenance reference
  * docs claim-boundary predicate for numeric tokens inside prose
* Separate `raw_numeric_occurrence` from `role_bearing_disposition_occurrence`; raw numeric noise cannot be used to satisfy or fail consumption closure unless promoted by the bounded predicates.
* Full sealed-axis token set includes `1062`, `311`, `163`, `153`, `148`, `109`, `44`, `2105`, `2084`, `21`, `27558`, `59`, `252`, `268`, `3`, `638`, `902`, `49`, `111`, and `0` when those tokens appear in role-bearing fields or claim-boundary prose.
* Because `0` is common but role-bearing for blocked / unknown / pending / forbidden counts, report its promoted count, excluded count, promoted ratio, excluded ratio, and top exclusion reasons separately in `zero_token_promotion_report.json`.
* If any sealed-axis token is excluded from role-bearing scan, record the exclusion reason in `sealed_axis_token_set.json`.
* Classify each occurrence by surface class: `manifest`, `tool`, `doc`, `test`, `validator`, `generated_report`, `staging_evidence`, `fixture`, `runtime`, `package`, `unknown`.
* Record artifact role separately from value role: `current_consumer`, `canonical_input`, `provenance_only`, `readiness_evidence`, `historical_trace`, `diagnostic_only`, `forbidden_direct_authority_candidate`.
* Do not infer divergence during census except for marking unclassified or raw-direct-read candidates.

Validation:

* Census output is deterministic.
* Bounded predicate output reports raw numeric count, promoted role-bearing count, excluded numeric count, and exclusion reason counts.
* `zero_token_promotion_report.json` records promoted / excluded `0` token ratios separately from other sealed-axis token coverage.
* Every role-bearing occurrence is classified or listed in `unclassified_surface_report.json`.
* Full sealed-axis token coverage is complete or exclusions are explicitly justified.
* Generated report references are not automatically treated as executable consumers.
* Runtime / package / source / rendered surfaces have changed_count `0`.

---

### Change 2 - Canonical Consumption Contract / Candidate Packet Definition

Purpose:

All downstream surfaces need a single contract for how to consume terminal disposition, denominator identity, readiness evidence, and raw provenance without flattening them into one number or one authority source.

Files:

* `Iris/build/description/v2/tools/build/generate_dvf_3_3_shared_disposition_packet.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_shared_disposition_consumption_common.py`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase2/shared_disposition_consumption_contract.md`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase2/shared_disposition_packet_schema.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase2/shared_disposition_packet.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase2/sealed_report_set.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase2/forbidden_direct_read_set.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase2/value_resolution_table.json`

Implementation Notes:

* Define explicit fields for `row_identity`, `terminal_disposition`, `denominator_axis`, `lifecycle_role`, `source_artifact_role`, `provenance_reference`, `readiness_reference`, `sealed_value_source`, and `artifact_hash`.
* Keep `1062`, `311`, `163`, `153`, `109`, `44`, `148`, `2105`, `2084`, `21` as role-bearing values, not substitute denominators.
* `sealed_value_source` must resolve only to the sealed report set, such as denominator final report, terminal final machine report, readiness final verdict/report, or reviewed ledger packet explicitly admitted by this plan.
* "Reviewed ledger packet explicitly admitted by this plan" is not a broad class. Every admitted ledger packet must be pinned in `sealed_report_set.json` with exact `path`, `hash`, and `role`; any unpinned packet is not a sealed value source.
* Raw audit, raw migration matrix, dry-run patch bundle, classified ledger, sandbox output, generated diagnostic report, and predecessor baseline trace cannot be `sealed_value_source`.
* Represent raw audit / readiness / sandbox / dry-run artifacts as provenance references or readiness references, not direct current execution authority.
* Any path that appears in both `sealed_report_set.json` and `forbidden_direct_read_set.json` is a hard schema failure.
* Record whether the packet is `candidate`, `review_pass`, `owner_adoption_pending`, or `adopted`.
* If author/owner does not approve canonical finalization during this round, keep the packet as candidate while still allowing detector validation against the candidate contract.

Validation:

* Schema validation passes.
* Required fields exist for every terminal row.
* Artifact hash references exist and are stable.
* `sealed_value_source` values are members of `sealed_report_set.json`.
* `sealed_report_set.json` pins every admitted sealed value source with exact path, hash, and role.
* Raw provenance paths are provenance-only or forbidden-direct-read references, not sealed value sources.
* Forbidden flattening checks reject count-only substitution.
* `2105 / 2084 / 21` resolution table cannot produce current-debt membership.

---

### Change 3 - Divergence Detection

Purpose:

Compare Phase 1 census against Phase 2 contract and report all cross-surface consumption divergence in a fail-loud, machine-readable form.

Files:

* `Iris/build/description/v2/tools/build/validate_dvf_3_3_shared_disposition_consumption.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_shared_disposition_consumption.py`
* `Iris/build/description/v2/tests/fixtures/negative/shared_disposition/`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase3/divergence_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase3/raw_authority_read_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase3/value_divergence_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase3/predecessor_reentry_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase3/negative_fixture_containment_report.json`

Implementation Notes:

* Implement at least these finding classes:
  * `RAW_AUTHORITY_READ`
  * `VALUE_DIVERGENCE`
  * `PREDECESSOR_REENTRY`
  * `LIFECYCLE_ROLE_MISMATCH`
  * `DENOMINATOR_AXIS_MISMATCH`
  * `UNCLASSIFIED_CONSUMPTION_SURFACE`
  * `DUAL_AUTHORITY_READ`
* Treat provenance-only references differently from executable consumer reads.
* Negative fixtures should include direct reads of raw audit, readiness sandbox, dry-run output, and predecessor baseline as current authority.
* Negative fixtures must live only under `Iris/build/description/v2/tests/fixtures/negative/shared_disposition/`.
* Current-looking artifact scans must exclude this negative fixture root by explicit path rule and must report that exclusion in `negative_fixture_containment_report.json`.
* Detector output must be reproducible from committed inputs and staged evidence roots.

Validation:

* Focused validator catches seeded forbidden raw direct-read fixtures.
* Focused unittest covers value divergence and predecessor re-entry.
* Divergence report includes zero/nonzero counts per finding class.
* Negative fixture containment report has leakage_count `0`.
* False-positive exclusions require explicit role and path evidence.

---

### Change 4 - Adapter / Manifest / Surface Realignment

Purpose:

If Phase 3 finds divergent executable consumers, realign them to consume the shared packet / contract or an adapter-mediated route. If Phase 3 `divergence_count` is `0`, Phase 4 closes as no-op evidence. Adapter implementation is required only for divergent executable consumers.

Files:

* `Iris/build/description/v2/tools/build/dvf_3_3_shared_disposition_consumption_common.py`
* Existing tools / validators / tests identified by Phase 1 as divergent
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase4/manifest_normalization_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase4/adapter_contract_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase4/no_op_realignment_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase4/no_dual_authority_read_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase4/realigned_surface_diff_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase4/protected_surface_no_mutation_report.json`

Implementation Notes:

* Default branch: if Phase 3 `divergence_count=0`, do not implement a new adapter and close Phase 4 with `no_op_realignment_report.json`.
* Adapter may load the packet, validate schema, check artifact hashes, join row identity, look up disposition, look up lifecycle role, and enforce denominator axis.
* Adapter implementation is justified only by one or more divergent executable consumers; docs-only wording drift or provenance-only references should be handled by docs / claim alignment, not new adapter code.
* Adapter must not re-adjudicate terminal disposition, reinterpret migrated/no-op, recalculate live eligibility, promote raw audit rows, or decide runtime mutation.
* Avoid dual-authority mode where a tool reads both canonical packet and raw provenance as competing authorities.
* Docs path references may remain as provenance descriptions, but executable consumers must resolve through the approved route.
* No source / rendered / Lua bridge / runtime / package mutation is allowed in this phase.

Validation:

* If Phase 3 `divergence_count=0`, `no_op_realignment_report.json` records adapter_required=false and no adapter unit tests are required for this phase.
* If adapter implementation is required, adapter unit tests pass.
* Manifest route tests pass.
* No dual-authority read report has violation_count `0`.
* Raw direct-read forbidden tests fail-loud on seeded violations.
* Protected surface no-mutation report has changed_count `0`.

---

### Change 5 - Required Validation / Guard Candidate Integration

Purpose:

Connect the shared disposition consumption contract to focused guard validation and, if explicitly approved, current-route required validation.

Files:

* `Iris/build/description/v2/tools/build/validate_dvf_3_3_shared_disposition_consumption.py`
* `Iris/_docs/round3/current_route_required_validations.shared_disposition_candidate.json`
* `Iris/_docs/round3/current_route_required_validations.json`, only if live adoption is separately approved
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase5/shared_disposition_consumption_validator_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase5/current_route_required_validation_candidate_patch.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase5/current_route_report_consumption_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase5/current_route_report_hash_attestation.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase5/current_route_closure_allowlist_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase5/current_route_integration_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase5/protected_surface_no_mutation_report.json`

Implementation Notes:

* Required guard classes:
  * packet/contract presence
  * schema validity
  * artifact hash match
  * terminal row coverage
  * terminal split sealed values
  * denominator axis mismatch
  * lifecycle role mismatch
  * forbidden direct-read
  * predecessor re-entry
  * claim boundary forbidden phrase
  * protected surface no-mutation
* Adoption states must be explicit: `candidate_only`, `review_pending`, `review_pass`, `owner_adoption_pending`, `adoption_hold_closure_or_allowlist_unsealed`, `adopted_to_required_validation`, `not_adopted_retained_candidate`.
* Current-route adoption path is artifact/report consumption by default:
  * focused shared disposition tooling runs outside the current-route test import graph;
  * it writes machine-readable reports under the round evidence root;
  * current-route required validation consumes only report status, schema version, input fingerprint, artifact hash, coverage counts, and invariant fields;
  * current-route tests must not directly import new `tools.build.dvf_3_3_shared_disposition_*` modules.
* Direct import of new shared disposition tooling by current-route tests is forbidden unless a separate reviewed closure / allowlist scope explicitly admits it.
* Subprocess-only guard must not be the default route. It is allowed only as a secondary fallback when artifact/report consumption cannot prove freshness; it still must not expand current core or tooling cap, and it must record command existence, exact command, exit code, stdout/stderr summary, output report hash, and the reason artifact/report freshness proof was insufficient.
* `adopted_to_required_validation` is forbidden until one of these is proven:
  * the shared disposition guard runs through the artifact/report consumption route and does not touch current core or current-route allowed tooling;
  * any required allowlist / closure change is split into a separate reviewed scope;
  * current-route closure evidence proves the validator is not counted as a current core module and does not expand the allowlist cap.
* Required closure invariants are current core closure count `12`, current-route allowed tooling modules max `1`, and no silent promotion of new shared disposition tools into current core.
* Broad current-route failures unrelated to this scope are recorded separately and cannot be used as reason to widen denominator or mutate current authority.

Validation:

* Focused validator passes.
* Focused unittest passes.
* Candidate manifest diff is reviewable and isolated.
* `current_route_report_consumption_manifest.json` lists every report consumed by current-route required validation, with status field, schema version, input fingerprint, hash, and exact invariant checks.
* `current_route_report_hash_attestation.json` proves the consumed reports are current relative to the focused shared disposition run.
* Current-route closure command exits with code `0` before any live adoption claim:
  `python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure`
* `current_route_closure_allowlist_report.json` proves current core closure count remains `12`, allowed tooling cap remains `1`, and new shared disposition tooling is not silently promoted into current core.
* If live adoption is approved after those gates, current-route required validation dry run exits with code `0`.
* If live adoption is not approved, candidate route remains retained and live manifest is unchanged.

---

### Change 6 - Docs / Ledger Packet / Claim Alignment

Purpose:

Make docs surfaces describe the same claim boundary as the machine-readable contract.

Files:

* `docs/dvf_3_3_shared_disposition_consumption_policy.md`
* `docs/dvf_3_3_shared_disposition_ledger_packet.md`
* `docs/dvf_3_3_shared_disposition_claim_boundary.md`
* `docs/DECISIONS.shared_disposition_consumption.patch.md`, if approved
* `docs/ROADMAP.shared_disposition_consumption.patch.md`, if approved
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase6/docs_claim_alignment_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase6/forbidden_claim_scan_report.json`

Implementation Notes:

* Docs must block these overclaims:
  * `153 migrated = live migration completed`
  * `109 live_mutation_eligible = already applied`
  * `163 sandbox mutation = live mutation evidence`
  * `311 change-required = terminal completion denominator`
  * `1062 executing consumers = source entries`
  * raw audit ledger = current execution authority
  * readiness execution artifact = current authority
  * dry-run patch bundle = live completion
  * historical / diagnostic row = current migration target
  * predecessor `2105 / 2084 / 21` = current debt
* DECISIONS / ROADMAP edits should be additive packets unless owner explicitly approves direct canonical document mutation.
* Keep detailed evidence in ledger packet or staging artifacts instead of bloating DECISIONS.

Validation:

* Docs forbidden claim scan has forbidden_claim_count `0`.
* Docs path role scan classifies raw/staging/historical references correctly.
* Ledger packet schema check passes.
* Plan/template section compliance is reviewed.

---

### Change 7 - Cross-Surface Consistency Validation & Adoption Decision

Purpose:

Close the round with machine-readable evidence that relevant surfaces consume the same disposition contract, then record review and owner adoption state separately.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase7/shared_consumption_surface_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase7/shared_consumption_consistency_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase7/row_coverage_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase7/direct_raw_read_negative_test_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase7/frozen_review_artifact_list.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase7/independent_review_artifact_hash_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase7/independent_review_minimum_standard.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase7/adoption_decision_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase7/final_shared_disposition_consumption_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_shared_disposition_ledger_consumption/phase7/final_claim_boundary_verdict.json`

Implementation Notes:

* Build a surface matrix comparing expected packet/contract hash with actual consumer hash or adapter route.
* Validate row-level sample lookups and full terminal row coverage.
* Run negative fixtures for direct raw artifact read.
* Record stale / historical / diagnostic containment.
* Record independent review status and owner adoption status as separate fields.
* A review pass cannot imply owner adoption; owner adoption cannot substitute for independent review.
* Owner must decide the review bar before closeout: either `artifact_generator_independent` review is sufficient, or a stricter `human_or_non_ai_reviewer` class is required. The decision must be recorded in `independent_review_minimum_standard.json`.
* Define independent review minimum standard before review:
  * frozen artifact list
  * hash coverage
  * reviewed artifact count
  * missing artifact count
  * packet schema re-check
  * surface matrix re-check
  * raw-direct negative fixture re-check
  * claim boundary verdict re-check
  * explicit reviewer identity / review source class
  * owner-approved review independence bar
* Independent adversarial review by a route that did not generate the reviewed artifacts is required before `complete_candidate_only` or `complete_adopted` closeout can be claimed.

Validation:

* Full surface matrix validator passes.
* Row coverage is complete or explicitly unresolved with blocker evidence.
* Direct raw read negative test report passes.
* Artifact hash stability check passes.
* Independent review report has reviewed_artifact_count and missing_artifact_count, and missing_artifact_count is `0` unless the final state is `partial` or `blocked`.
* Final report states one of the allowed plan-local closeout states.
* Final report repeats the non-claim that this plan does not close the separate Closeout / Reentry Guard Seal problem.

---

## 7. Validation Plan

### Automated Validation

Command provenance preflight:

* Verify each listed validation command path exists before using it as PASS evidence.
* Plan text does not by itself validate off-surface claims; execution must confirm command existence, exact command exit code `0`, `EXECUTION_CONTRACT.md` closeout-state reduction consistency, closure command behavior, current core closure count `12`, tooling cap `1`, and DVF tooling code / command path existence at execution time.
* As of this plan revision, the following existing command paths were checked as present:
  * `Iris/_docs/round3/round3_run_contract_tests.py`
  * `Iris/build/description/v2/tools/build/validate_consumer_universe_denominator_lock.py`
  * `Iris/build/description/v2/tools/build/validate_dvf_3_3_terminal_disposition_adjudication.py`
  * `Iris/build/description/v2/tools/build/validate_dvf_3_3_live_consumer_migration_execution.py`
* Planned commands that do not yet exist remain `unverified` and cannot be cited as PASS evidence until implemented and existence-checked.

Primary focused commands, once the planned tools exist:

* `uv run python Iris\build\description\v2\tools\build\run_dvf_3_3_shared_disposition_consumption.py --mode all`
* `uv run python Iris\build\description\v2\tools\build\validate_dvf_3_3_shared_disposition_consumption.py --require-complete`
* `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_shared_disposition_consumption.py"`

Current-route closure / tooling allowlist command:

* `python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure`

Expected current-route closure result:

* command exits with code `0`
* `closure_enforced=true`
* current core closure count remains `12`
* `current_route_allowed_tooling_modules` max remains `1`
* new shared disposition tools are not silently promoted into current core

Regression guard commands for already sealed predecessor surfaces:

* `uv run python Iris\build\description\v2\tools\build\validate_consumer_universe_denominator_lock.py --require-complete`
* `uv run python Iris\build\description\v2\tools\build\validate_dvf_3_3_terminal_disposition_adjudication.py --require-complete`
* `uv run python Iris\build\description\v2\tools\build\validate_dvf_3_3_live_consumer_migration_execution.py --require-complete`

Regression guard command meaning check:

* Before using `validate_dvf_3_3_live_consumer_migration_execution.py --require-complete` as evidence, confirm at execution time that `--require-complete` means pre-apply readiness / execution-evidence completeness.
* If `--require-complete` means or implies actual live migration completion, exclude that command from regression guard evidence for this plan and record the exclusion reason.
* This command can never be used by this plan to claim Phase 4 live apply, live mutation completion, release readiness, package readiness, Workshop readiness, B42 readiness, or deployment readiness.

Repository review commands:

* `git diff --stat`
* `git diff -- docs/dvf_3_3_shared_disposition_ledger_consumption_plan.md`
* `git diff -- Iris/build/description/v2/tools/build Iris/build/description/v2/tests Iris/_docs/round3 docs`

Execution contract self-check:

* Confirm `docs/EXECUTION_CONTRACT.md` remains applicable as disclosure / evidence / closeout discipline only.
* Record `validated`, `out_of_scope`, and `unvalidated_but_in_scope` validation ceiling in final closeout artifacts.
* Record non-claims for live apply, live completion, runtime behavior, release readiness, Workshop readiness, B42 readiness, and public-facing text quality.

Required machine-readable report checks:

* unclassified surface count is `0` or explicitly blocked.
* `RAW_AUTHORITY_READ = 0`
* `VALUE_DIVERGENCE = 0`
* `PREDECESSOR_REENTRY = 0`
* `LIFECYCLE_ROLE_MISMATCH = 0`
* `DENOMINATOR_AXIS_MISMATCH = 0`
* `DUAL_AUTHORITY_READ = 0`
* bounded census false-positive ceiling is reported.
* full sealed-axis false-negative coverage is complete or exclusions are justified.
* `0` token promoted / excluded ratio is reported separately.
* `sealed_value_source` is a member of the sealed report set.
* current-route adoption uses artifact/report consumption and has no direct import of new shared disposition tooling.
* report consumption manifest and report hash attestation are present for adopted validation.
* current-route closure / allowlist cap invariants are unchanged.
* negative fixture containment leakage_count is `0`.
* forbidden docs claim count is `0`
* protected source / rendered / Lua bridge / runtime / package changed_count is `0`

Do not claim validation passed unless the exact relevant command exits with code `0`. If `uv`, Python, or any required helper is unavailable, report that validation as blocked.

### Manual Validation

* Review Phase 1 census classification for false executable/provenance splits.
* Review Phase 2 packet/contract fields against DECISIONS current readpoint.
* Review Phase 3 divergence classes for false positives and false negatives.
* Review Phase 4 realignment diffs for accidental adjudication logic.
* Review candidate required-validation manifest diff before any live adoption.
* Review current-route report consumption manifest and hash attestation before any live adoption.
* Review that current-route tests do not directly import new shared disposition tooling.
* Review current-route closure / tooling allowlist evidence before any live adoption.
* Review `0` token promoted / excluded ratio for excessive noise or missing role-bearing zero counts.
* Review `validate_dvf_3_3_live_consumer_migration_execution.py --require-complete` semantics before treating it as regression evidence.
* Review negative fixture containment and current-looking scan exclusion evidence.
* Review docs claim boundary wording for overclaim risk.
* Review `EXECUTION_CONTRACT.md` validation ceiling and non-claim mapping before closeout.
* Review independent review hash report and adoption decision report as separate gates.

### Validation Limits

This plan will not validate:

* live Phase 4 apply execution
* live mutation correctness
* runtime equivalence
* source / rendered / runtime / package payload correctness
* in-game manual QA
* multiplayer validation
* long-session runtime validation
* package release readiness
* Workshop readiness
* B42 readiness
* public-facing text quality
* semantic quality acceptance
* external ecosystem compatibility sweep
* broad current-route source-overlay blocker resolution

---

## 8. Risk Surface Touch

### Authority Surface

Current source / rendered / Lua bridge / runtime / package authority is not changed.

This plan does create or seal a downstream disposition consumption contract. Whether that is classified as an Authority Surface impact or a sealed artifact consumption contract remains an explicit author/owner decision gate.

Default execution stance:

* Treat this as sealed artifact / validator consumption surface work.
* Do not mutate current authority chain.
* Do not claim new current source / runtime authority.

### Runtime Behavior Surface

None.

* Runtime Lua behavior is unchanged.
* Browser / Wiki / Tooltip behavior is unchanged.
* Lua bridge and runtime chunks are unchanged.
* Package payload is unchanged.

### Compatibility Surface

External compatibility surface: None expected.

Internal tooling compatibility surface: possible.

* CLI default input routes may be normalized.
* Validator manifest routes may change.
* Test fixtures may be redirected from raw artifacts to shared contract routes.
* Required-validation live adoption remains decision-gated.

### Sealed Artifact Surface

Read-only consumption impact.

The following sealed artifacts are referenced but not re-adjudicated:

* terminal disposition ledger / machine report
* denominator final report
* reconciled input manifest
* readiness authorization / execution evidence
* raw audit / raw migration matrix
* dry-run output
* historical / diagnostic artifacts
* predecessor baseline trace

### Public-Facing Output Surface

None.

* Public text, tooltip, Browser / Wiki display, Workshop page, and release notes are unchanged.
* Internal docs claim boundary may be aligned.

---

## 9. Risk Analysis

### Architecture Risk

* Adapter code could become a new adjudicator instead of a read-only consumption route.
* Canonical packet could flatten denominator axes into a single misleading count.
* Consumption contract could be overclaimed as source/runtime authority.
* Required-validation adoption could be confused with migration completion.
* Docs-only alignment could leave executable tool/test/validator surfaces divergent.

### Runtime Risk

* Direct runtime behavior risk is low because runtime surfaces are out of scope.
* Risk remains if implementation accidentally touches Lua bridge, runtime chunks, or package payload.
* No-mutation hash reports must verify protected runtime/package surfaces.

### Compatibility Risk

* Internal tools or tests may depend on raw fixture paths and break after route normalization.
* Current-route validation may surface unrelated broad failures.
* Candidate required-validation manifest may be mistaken for live adoption.
* External mod compatibility risk is low because no public require contract or runtime behavior changes are planned.

### Regression Risk

* Divergence detector false negatives could allow raw authority reads to remain.
* Divergence detector false positives could classify provenance-only references as executable direct reads.
* Predecessor `2105 / 2084 / 21` references could be over-cleaned from historical docs.
* Partial seal could align manifest/tooling while missing docs/tests or validators.
* Independent review and owner adoption state could be collapsed into one ambiguous status.

---

## 10. Rollback Plan

Rollback is tooling / manifest / docs / validator rollback, not live data rollback.

* Phase 1 census artifacts can be regenerated or discarded without changing current authority.
* Phase 2 contract / packet can be replaced by a revised candidate if schema or role modeling is wrong.
* Phase 3 detector changes can be reverted independently if false-positive or false-negative behavior is unacceptable.
* Phase 4 realignment must keep per-surface diffs small enough for individual revert.
* If adapter logic starts adjudicating values, remove that logic or revert the adapter to read-only lookup.
* If candidate required-validation integration breaks unrelated current-route validation, keep it candidate-only or focused-route-only.
* If live `current_route_required_validations.json` adoption was approved and later fails, revert only that manifest edit and retain the candidate patch/report.
* Docs policy / ledger packet / claim boundary changes can be reverted separately from code.
* Sealed denominator, terminal disposition, readiness evidence, source, rendered, Lua bridge, runtime chunks, and package payload are not rollback targets because this plan must not mutate them.

---

## 11. Governance Constraints

* Preserve `docs/Philosophy.md` compliance.
* Preserve Hub & Spoke / SPI boundaries.
* Preserve Iris as offline evidence/outcome/source producer plus runtime display consumer; do not turn runtime into a validator or adjudicator.
* Preserve DVF 3-3 current authority chain: `source -> facts -> decisions -> rendered -> Lua bridge -> runtime chunks`.
* Preserve runtime/build-time separation.
* Preserve existing authority ownership; do not bypass sealed current authority.
* Preserve additive amendment preference for DECISIONS / ROADMAP unless direct canonical edits are approved.
* Preserve minimal diff scope and do not revert unrelated dirty worktree changes.
* Preserve terminal disposition and denominator readpoints; do not reopen adjudication.
* Preserve distinction between terminal completion, readiness authorization, dry-run evidence, and live completion.
* Preserve `1062 / 311 / 163 / 153 / 109 / 44 / 148 / 2105 / 2084 / 21` as different denominator axes / lifecycle roles.
* Preserve raw audit / readiness / sandbox / dry-run artifacts as provenance or readiness evidence, not direct current execution authority.
* Preserve current-route tooling allowlist cap and current core closure.
* Preserve current core closure count `12` and current-route allowed tooling cap `1` unless a separate reviewed scope explicitly changes them.
* Preserve artifact/report consumption as the default current-route adoption path.
* Preserve subprocess-only guard as a secondary fallback only; it must not become the default current-route adoption route.
* Preserve the ban on direct current-route test imports of new shared disposition tooling unless a separate reviewed closure / allowlist scope explicitly admits it.
* Preserve candidate/adopted status distinction for required-validation manifest changes.
* Preserve live-adoption branch hold until closure / allowlist / independent review integration evidence is sealed.
* Preserve independent review status and owner adoption status as separate fields.
* Preserve `DUAL_AUTHORITY_READ = 0` as a closeout invariant.
* Preserve `sealed_value_source` as sealed-report-set-only; raw provenance cannot be sealed value source.
* Preserve `sealed_report_set.json` path / hash / role pinning for every admitted ledger packet.
* Preserve `EXECUTION_CONTRACT.md` disclosure, evidence, validation ceiling, non-claim, and closeout obligations.
* Preserve negative fixture containment outside current-looking artifact paths.

Open decision gates:

* Whether canonical packet is finalized in this round or retained as candidate set.
* Whether downstream consumption contract counts as Authority Surface impact.
* Whether internal tooling route change counts as Compatibility Surface impact.
* Whether live required-validation manifest adoption remains on hold or is split into a separate reviewed allowlist / closure scope.
* Whether subprocess-only fallback is needed despite artifact/report consumption, and if so whether its command provenance is sufficient.
* Whether the owner accepts `artifact_generator_independent` review as sufficient, or requires a stricter `human_or_non_ai_reviewer` source class for complete closeout.
* Whether the owner-approved independent review standard has been satisfied for complete closeout.
* Whether an explicit owner-approved exception is needed if someone proposes adapter implementation despite Phase 3 `divergence_count=0`.

---

## 12. Expected Closeout State

Expected closeout target: `complete_candidate_only`.

Plan-local closeout states:

* `complete_candidate_only`: focused shared disposition consumption guard closes, candidate required-validation route is retained, live `current_route_required_validations.json` is not adopted, and artifact-generator-independent review passes.
* `complete_adopted`: all `complete_candidate_only` conditions pass, live required-validation adoption is explicitly approved, current-route closure / allowlist cap evidence passes, and adoption is recorded without expanding current core or silently promoting tooling.
* `partial`: planned scope is only partly closed or one or more review / adoption / coverage gates remain unresolved.
* `blocked`: execution cannot continue without missing authority, evidence, dependency, reviewer, or closure / allowlist decision.

These are plan-local substates that reduce to `EXECUTION_CONTRACT.md` closeout states with an explicit validation ceiling; they do not create a new ecosystem-wide closeout taxonomy.

`complete_candidate_only` means:

* relevant `manifest / tools / docs / tests / validators` surfaces are inventoried.
* unclassified surfaces are `0` or explicitly blocked with follow-up state.
* shared disposition consumption contract or candidate packet exists and validates.
* terminal disposition ledger, denominator report, readiness evidence, raw provenance, and predecessor baseline roles are separated.
* forbidden direct authority consumers are `0`.
* `RAW_AUTHORITY_READ = 0`.
* `VALUE_DIVERGENCE = 0`.
* `PREDECESSOR_REENTRY = 0`.
* `DUAL_AUTHORITY_READ = 0`.
* denominator axis mismatch is `0`.
* lifecycle role mismatch is `0`.
* bounded census false-positive ceiling is reported.
* full sealed-axis false-negative coverage is complete or exclusions are justified.
* `0` token promoted / excluded ratio is reported separately.
* `sealed_value_source` values are members of the sealed report set.
* `sealed_report_set.json` pins every admitted sealed value source with exact path, hash, and role.
* terminal row coverage is complete.
* terminal split matches sealed values.
* relevant surfaces consume the same packet / contract / adapter-mediated route.
* raw audit / readiness sandbox / dry-run / staging / diagnostic artifacts do not re-enter as current execution authority.
* current-route closure / allowlist cap invariants are either unaffected or explicitly reported as candidate-only untouched.
* protected source / rendered / Lua bridge / runtime / package surface changed_count is `0`.
* docs forbidden claim scan is `0`.
* negative fixture containment leakage_count is `0`.
* current-route required-validation adoption state is explicitly recorded as candidate-only or retained candidate.
* live `current_route_required_validations.json` is unchanged.
* independent review minimum standard is materialized.
* owner-approved review independence bar is recorded in `independent_review_minimum_standard.json`.
* artifact-generator-independent review status is `review_pass`.
* independent review status and owner adoption state are recorded separately.
* final report repeats that this plan does not close the separate Closeout / Reentry Guard Seal problem.

`complete_adopted` additionally requires:

* current-route adoption uses artifact/report consumption, not direct import of new shared disposition tooling.
* `current_route_report_consumption_manifest.json` lists all adopted reports and invariant checks.
* `current_route_report_hash_attestation.json` proves adopted reports are current relative to the focused shared disposition run.
* owner adoption explicitly approves live required-validation adoption.
* `python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure` exits with code `0`.
* current core closure count remains `12`.
* current-route allowed tooling cap remains `1`.
* new shared disposition tools are not silently promoted into current core.
* adoption does not claim live migration execution, live mutation completion, release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game QA pass, or public-facing text quality acceptance.

If any of the following remain unresolved, expected closeout becomes `partial` or `blocked`:

* unclassified executable consumption surface
* unresolved raw direct-read consumer
* unresolved value divergence
* unresolved predecessor re-entry
* unresolved dual authority read
* missing terminal row coverage
* missing bounded census predicate or sealed-axis coverage evidence
* missing `0` token promoted / excluded ratio report
* `sealed_value_source` pointing to raw provenance
* negative fixture leakage into current-looking scans
* current-route adoption attempts direct import of new shared disposition tooling without separate reviewed closure / allowlist admission
* missing report consumption manifest or report hash attestation for adopted current-route validation
* protected source / rendered / Lua bridge / runtime / package mutation
* missing current-route closure / allowlist evidence for live adoption
* blocked or missing artifact-generator-independent review / owner adoption state evidence
