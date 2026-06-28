# Implementation Plan

> Status: revised plan / roadmap-derived / codebase-inspected / Cycle 1 WARN feedback incorporated / Cycle 2 WARN PASS-near feedback incorporated / success-probability hardening incorporated / N12 plan-text freeze incorporated / successor readpoint vocabulary and evidence-role seal / governance-only / execution readiness requires re-review
> 작성일: 2026-06-28
> Roadmap input: `C:/Users/MW/.codex/attachments/5c39b2e7-1365-4a10-afdc-e639799b6c9f/pasted-text.txt` / sha256 `A42B3B00C5B3F196E43542681C680000C401A4D1C2FB5834049EF0E8EFD46CB8` / lines `584`
> Feedback input: `C:/Users/MW/.codex/attachments/72f9d5bd-81fa-441d-b337-842a4e42aec0/pasted-text.txt` / sha256 `BD35584CE795010FCECEDE34F1ABDFF226B9C74CE92866E6E1FD136C6EB8D96F` / lines `450` / verdict `WARN` / required revisions incorporated
> Feedback input: `C:/Users/MW/.codex/attachments/d351e5f2-362a-49b7-bae3-23a45f16aecb/pasted-text.txt` / sha256 `2B7E41B50B06C2ED724506CF8F80D31D934AF9F642CBF1B3B3F3A2EA347B6D8E` / lines `312` / verdict `WARN - PASS near` / C6-C8 and N6-N7 required revisions incorporated
> Inline feedback: N12 post-convergence plan-text freeze advisory incorporated / further advisory soft spots route to execution validators, not plan expansion
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Direct plan artifact: `docs/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal_plan.md`
> Primary evidence root target: `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/`

---

## 1. Objective

DVF 3-3 vNext successor current authority chain에서 같은 literal `2105`가 서로 다른 의미 축으로 재사용되는 문제를 봉인한다.

이 계획의 목적은 source / rendered / Lua bridge / runtime chunk / package chain을 새로 쓰는 것이 아니라, successor readpoint vocabulary와 evidence role binding을 governance-only로 분리하는 것이다. 이 라운드의 `2105` vocabulary axis set은 닫힌 4축으로 시작하며, 추가 축 후보가 발견되면 silent expansion이 아니라 `blocked_axis_set_incomplete` / manual review로 처리한다.

* successor current row identity
* predecessor historical trace
* migration / consumer denominator
* runtime deployable entry count

현재 Iris 코드베이스 기준으로 successor source chain은 이미 `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`에서 `successor_current_source_authority`로 선언되어 있고, `facts / decisions / overlay_support`는 모두 `2105`행이다. Runtime authority도 monolith가 아니라 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`와 `IrisLayer3DataChunks/*.lua` bundle로 고정되어 있으며, 현재 readpoint는 `2105` entries / `11` chunks다.

따라서 이번 계획의 최대 claim은 다음으로 제한한다.

```text
DVF 3-3 vNext successor current authority chain readpoint vocabulary and
evidence role binding are governance-sealed or governance-ready according to
the resolved review status. 2105 axis misuse and predecessor 2105 / 2084 / 21
reentry are fail-closed. Protected source / rendered / Lua bridge / runtime /
package surfaces are not mutated.
```

이 계획은 canonical seal 가능 여부를 자동 확정하지 않는다. Non-Claude / non-author independent review, owner decision, owner seal, package scope selection, canonical round identifier, axis token final strings는 실행 전 또는 final seal 전 별도 판정이 필요한 gate로 둔다.

Feedback 반영 후에도 이 plan artifact 자체는 execution readiness PASS가 아니다. Cycle 2 feedback 기준으로 PASS 근접 상태까지 보강하되, 실행 전에는 revised plan review가 필요하며, independent-review gate는 `BLOCKED`, canonical seal은 non-Claude / non-author independent review 전까지 `not_allowed`로 유지한다.

N12 반영 후 이 plan text는 동결한다. 이후 발견되는 non-blocking soft spot은 더 정교한 계획 문안이나 새 artifact/field/enum 추가로 흡수하지 않고, 실제 실행 tooling / validator / fail-loud evidence report가 드러내는 문제로 처리한다. Plan 재개정은 실행 중 기존 계약으로 표현할 수 없는 hard blocker가 확인되어 `revised_plan_needed`로 닫을 때만 허용한다.

---

## 2. Scope

이 계획은 DVF 3-3 vNext successor readpoint의 vocabulary, occurrence axis taxonomy, source/rendered/runtime/package binding evidence, evidence role taxonomy, predecessor reentry guard, live required-validation manifest additive adoption, final governance packet을 다룬다.

포함 범위:

* `2105 / 2084 / 21` occurrence inventory
* source / rendered / runtime / package / docs / tools / tests / manifest / evidence report surface coverage
* successor readpoint closed four-axis taxonomy and exhaustiveness proof
* per-occurrence axis map
* scan root / exclusion root manifest and deterministic corpus lock
* count/hash and row-key identity or key-set hash binding
* row-key definition and cross-surface correspondence mapping
* source `item_id` uniqueness and intra-source key-set equality validation
* `item_id` to rendered/runtime/package key transform rule
* count equality alone cannot prove identity rule
* vNext / rejected-delta / cutover / drift / adoption / freshness / durable-surface evidence role taxonomy, separate from the 4 `2105` axes
* predecessor `2105 / 2084 / 21` reentry fail-closed guard
* current-route active core closure / tooling allowlist impact validation
* live `Iris/_docs/round3/current_route_required_validations.json` additive governance adoption
* current checkout readiness preflight before evidence generation
* frozen report field contract before tool/test implementation
* candidate manifest patch before live required-validation manifest mutation
* Phase 6 / Phase 7 artifact dependency sequencing and recursion avoidance
* two-stage VCS preservation proof gate for tools/tests/docs/evidence plus live manifest diff
* post-adoption required-test execution inventory to block no-op adoption
* protected package surface vs generated package scan output boundary
* package peer scan canonical minimum proof separated from package payload preservation
* final governance packet, review boundary, owner-reserved decision capture
* row-key/package claim ceiling matrix
* plan-text freeze boundary after N12 advisory incorporation
* DECISIONS / ROADMAP update draft generation only after claim boundary is explicit; canonical update candidates are produced only after final seal state is resolved

Primary execution evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/`

Direct documentation artifacts:

* `docs/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal_plan.md`
* `docs/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal_claim_boundary.md`
* `docs/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal_ledger_packet.md`

Candidate support docs:

* `docs/predecessor_reentry_guard_policy.md`
* `docs/completion_vocabulary_separation_policy.md`

### Explicitly Out Of Scope

* successor current authority cutover re-execution
* source facts / decisions / overlay_support mutation
* rendered output regeneration mutation
* Lua bridge export mutation
* runtime chunk replacement
* package payload mutation
* live migration execution
* terminal disposition re-adjudication
* denominator redefinition
* shared disposition ledger re-adoption
* current-route baseline / source-overlay repair reopen
* predecessor residue cleanup
* old predecessor byte-level recovery
* `IrisLayer3Data.lua` monolith reintroduction
* legacy `active / silent` current vocabulary revival
* public-facing text quality acceptance
* semantic quality completion
* Browser / Wiki / Tooltip behavior change
* manual in-game QA
* release / package / Workshop / B42 / deployment readiness declaration
* full historical byte reproducibility proof
* full clean-checkout required-evidence reproducibility proof
* Claude self-review or author self-review as independent review
* unrelated refactor

---

## 3. Non-Goals

이 계획은 다음을 해결하지 않는다.

* `2105` 값을 제거하거나 다른 숫자로 바꾸지 않는다.
* sealed successor `2105 entries` 자체를 재판정하지 않는다.
* predecessor `2105 / 2084 / 21` trace를 삭제하지 않는다. 허용 context에 historical / comparison / migration provenance로 보존한다.
* `adopted / unadopted`를 quality-pass, publish, deletion, suppression 의미로 확장하지 않는다.
* `active / silent`를 current runtime vocabulary로 되살리지 않는다.
* current-route manifest adoption을 source writer, rendered writer, runtime writer, package writer로 취급하지 않는다.
* package peer binding 범위를 무리하게 확장하지 않는다. Package peer가 in-scope로 선택되지 않으면 explicit out-of-scope note와 forbidden legacy scan으로 제한한다.
* count equality를 row-key identity 증명으로 사용하지 않는다.
* machine PASS, plan-level PASS, owner approval, owner seal을 independent review로 대체하지 않는다.
* final report를 release readiness, package readiness, Workshop readiness, deployment readiness, manual QA, semantic quality, public-facing text acceptance로 표현하지 않는다.
* N12 이후 advisory soft spot을 이유로 plan text, artifact list, field list, closeout enum을 계속 확장하지 않는다. 추가 발견 사항은 실행 validator와 fail-loud report에서 드러내고, 기존 계약으로 표현 불가능한 hard blocker만 `revised_plan_needed`로 처리한다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 설계 authority다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 current readpoint를 따른다.
* Iris는 100% Lua runtime module이며, 이번 계획은 offline build / governance tooling만 다룬다.
* Runtime / build-time separation은 유지된다.
* `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`은 schema `dvf-3-3-input-manifest-v1`, status `current_authority`, authority role `successor_current_source_authority`다.
* Current source chain은 다음 파일이다.
  * `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
  * `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
  * `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
  * `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`
* Codebase inspection 기준으로 `facts`, `decisions`, `overlay_support`는 각각 `2105`행이다.
* `Iris/build/description/v2/output/dvf_3_3_rendered.json`은 존재하며 `meta.stats.total=2105`, sha256 `4EBDB0B6C381FB07D8A61517133C7F61483D979563FC9C0E6EBBB8F2359FA50D`로 관찰됐다.
* `Iris/build/description/v2/output/dvf_3_3_rendered.json`은 PowerShell `ConvertFrom-Json`에서 duplicate key 오류를 낼 수 있다. Row-key / key-set 검증 tooling은 duplicate-key-aware parser를 사용하고, key collision을 조용히 collapse하지 않아야 한다.
* Runtime deployable authority는 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`와 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`다.
* Current runtime chunk manifest는 `-- Total runtime entries: 2105`, `-- Chunks: 11 x <= 200`을 명시한다.
* 현재 runtime chunk file set은 `Chunk001.lua` through `Chunk011.lua`지만, guard는 이 count를 하드코딩하지 않고 `IrisLayer3DataChunks.lua`에서 derive해야 한다.
* `Iris/tools/package_iris.ps1`는 `media\lua\client\Iris\Data\IrisLayer3Data.lua` monolith와 stale `IrisDvfBridgeData.lua` package output을 forbidden surface로 검사한다.
* Package peer surface는 `Iris/build/package/Iris/media/lua/client/Iris/Data`가 존재할 때 scan 대상이 될 수 있다. Package build나 package readiness는 이 계획의 기본 요구가 아니다.
* Protected package payload inputs are the source package inputs copied by `Iris/tools/package_iris.ps1`, including `Iris/Iris/mod.info`, optional `Iris/Iris/poster.png`, and `Iris/Iris/media/**`.
* Generated package peer scan outputs are the default `Iris/build/package/Iris/**`, `Iris/build/package/Iris.package_manifest.sha256.json`, `Iris/build/package/Iris.zip`, or an explicitly declared `package_iris.ps1 -OutputRoot` equivalent. Writes there are allowed only inside the declared generated output root, must be inventoried separately, and are excluded from protected package payload mutation counts.
* `Iris/_docs/round3/current_route_required_validations.json`은 schema `round3-current-route-required-validations-v1`, status `PASS`, required artifact count `75`, required test count `40`으로 관찰됐다.
* `Iris/_docs/round3/round3_run_contract_tests.py`는 taxonomy-selected current tests와 live required manifest tests를 union으로 실행하며, required artifact field mismatch를 fail-closed 처리한다.
* Current route closure enforcement는 `Iris/_docs/round3/round3_active_core_closure.json`과 `current_route_allowed_tooling_modules`를 통해 이루어진다.
* Current active core closure is currently `12` modules. The current-route tooling allowlist currently has cap `1` and contains `export_dvf_3_3_lua_bridge` only. New successor-readpoint tools are not current core modules and must not be inserted into `current_route_allowed_tooling_modules` as a convenience bypass.
* If current-route import of new tooling is required, it requires a separate additive closure impact report that proves active core `12` remains unchanged, tooling allowlist cap is not violated, and the new tool is consumed only through required-validation wrapper / focused unittest surface.
* Existing related governance roots already exist for closeout reentry, completion vocabulary split, current source authority drift verification, evidence freshness reseal, durable surface alignment, runtime payload integrity, and live migration readiness. This round must consume them by role, not reopen them.
* Seal-vs-prerequisite classification is not one of the four `2105` axes. It is a separate evidence role taxonomy handled in Phase 4, and Phase 2 must point to Phase 4 instead of redefining evidence roles as axis values.
* Facts / decisions / overlay_support row identity is keyed by `item_id`. Each source file must prove `distinct item_id count == row count == 2105` at execution readpoint. Duplicate source keys block row-key identity.
* The current source-chain relation is expected to be `facts.item_id key-set == decisions.item_id key-set == overlay_support.item_id key-set`. If a future plan treats overlay_support as sparse, that plan must explicitly supersede this equality rule and define subset semantics; this round defaults to equality.
* Rendered and runtime chunk entries are keyed by full type keys such as `Base.223Box`. For the current DVF 3-3 vNext source chain, the key transform rule is identity: `source.item_id == rendered entry key == runtime Lua table key`. Package peer keys, if in-scope, use the same identity transform against package Lua table keys.
* Cross-surface matching is a key correspondence proof, not authority equality proof.
* Rendered and runtime surfaces are non-writer / correspondence-only evidence in this round. They may support chain binding but cannot become source authority.
* Lua bridge is export-contract evidence only unless a concrete candidate bridge artifact is explicitly named and classified. It is not a separate row-key identity node by default.
* Phase 6 current-route manifest adoption may require only Phase 0 through Phase 6 stable machine/governance artifacts. Phase 7 final report, independent review artifact, and owner seal record must be validated by the wrapper validator / final seal validator, not by self-referential current-route manifest checks.
* Existing required artifact/test/check removal or modification count must be `0` as a hard fail-closed assertion. Violation is terminal for this round, not a soft warning.
* Existing sealed body rewrite count must be `0` as a hard gate.
* Clean-checkout required-evidence reproducibility remains a non-claim. Execution assumes current required evidence is available in the working checkout or explicitly records missing evidence as blocked / deferred.
* VCS preservation is a closeout ceiling gate: related tool/test/docs/evidence paths and the live required-validation manifest diff must be proven tracked or staged / commit-bound, not ignored, and included in the same VCS boundary for canonical closeout preservation. If not, closeout is limited to noncanonical / machine packet state.
* Codebase inspection shows generated staging evidence under `Iris/build/description/v2/staging/*` and package outputs under `Iris/build/package/*` are ignored by `.gitignore`. Canonical-ready preservation must therefore use a minimum tracked path set plus tracked hash-manifest surrogates for ignored generated evidence, instead of requiring every generated output byte to become tracked.
* Planning-time live manifest counts `75` required artifacts and `40` required tests are observations only. Execution must recompute baseline counts from execution HEAD before additive diff and no-op adoption checks.
* Dirty working tree changes outside this plan must be preserved.

---

## 5. Repository Areas Affected

### Code

Expected new offline tooling surfaces:

* `Iris/build/description/v2/tools/build/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal.py`

Read-only current route and existing guard surfaces:

* `Iris/_docs/round3/round3_run_contract_tests.py`
* `Iris/_docs/round3/round3_active_core_closure.json`
* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/build/description/v2/tools/build/runtime_payload_state_integrity.py`
* `Iris/build/description/v2/tools/build/runtime_payload_state_integrity_residual_seal.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_durable_current_authority_surface_alignment.py`
* `Iris/tools/package_iris.ps1`

No runtime Lua source mutation is planned.

### Docs

Direct plan artifact:

* `docs/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal_plan.md`

Expected execution docs:

* `docs/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal_claim_boundary.md`
* `docs/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal_ledger_packet.md`
* `docs/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal_decisions_update_draft.md`
* `docs/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal_roadmap_update_draft.md`

Read-only authority inputs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/dvf_3_3_vnext_current_authority_implementation_2105_consumer_migration_plan.md`
* `docs/dvf_3_3_closeout_reentry_guard_seal_plan.md`
* `docs/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split_plan.md`
* `docs/dvf_3_3_durable_current_authority_surface_alignment_plan.md`
* `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_plan.md`

### Config

Candidate live governance config surface:

* `Iris/_docs/round3/current_route_required_validations.json`

Manifest adoption must be additive-only. Existing required artifacts, required tests, and existing check predicates must not be removed or modified by this round. Removal/modification count greater than `0` is a terminal fail-closed condition for this round.

### Generated Artifacts

All generated evidence should be written under:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/`

Expected artifact families:

* `phase0/roadmap_input_binding.json`
* `phase0/feedback_input_binding.json`
* `phase0/owner_reserved_decision_matrix.json`
* `phase0/report_field_contract.json`
* `phase0/preflight_current_checkout_readiness_report.json`
* `phase1/axis_occurrence_inventory.jsonl`
* `phase1/scan_root_manifest.json`
* `phase1/fingerprint_manifest.json`
* `phase1/surface_coverage_report.json`
* `phase1/protected_no_mutation_report.json`
* `phase1/package_surface_boundary_manifest.json`
* `phase2/successor_readpoint_axis_taxonomy.md`
* `phase2/axis_exhaustiveness_report.json`
* `phase2/axis_token_reconciliation_report.json`
* `phase2/axis_token_non_supersession_report.json`
* `phase2/occurrence_axis_map.json`
* `phase2/successor_readpoint_axis_policy.json`
* `phase2/successor_readpoint_claim_boundary.md`
* `phase2/banned_unqualified_claim_patterns.json`
* `phase3/current_chain_count_hash_report.json`
* `phase3/chain_rowkey_identity_report.json`
* `phase3/count_vs_rowkey_divergence_report.json`
* `phase3/source_rendered_runtime_package_binding.json`
* `phase3/rowkey_definition.json`
* `phase3/source_item_id_uniqueness_report.json`
* `phase3/intra_source_keyset_equality_report.json`
* `phase3/key_transform_rule_report.json`
* `phase3/cross_surface_key_correspondence_report.json`
* `phase3/rendered_runtime_correspondence_only_report.json`
* `phase3/rowkey_package_claim_matrix.json`
* `phase3/chunk_membership_report.json`
* `phase3/package_peer_scan_canonical_minimum.json`
* `phase3/package_peer_scan_report.json` or `phase3/package_out_of_scope_note.md`
* `phase4/evidence_role_taxonomy_report.json`
* `phase4/evidence_class_ledger.md`
* `phase4/seal_vs_prerequisite_map.json`
* `phase4/prerequisite_candidate_disposition_report.json`
* `phase4/direct_authority_read_scan.json`
* `phase5/predecessor_reentry_axis_guard_report.json`
* `phase5/allowed_predecessor_context_report.json`
* `phase5/forbidden_predecessor_context_report.json`
* `phase5/claim_scan_inventory.json`
* `phase5/no_axis_misuse_report.json`
* `phase6/live_required_manifest_adoption_report.json`
* `phase6/current_route_required_validation_candidate_patch.json`
* `phase6/manifest_additive_diff_report.json`
* `phase6/vcs_preservation_preflight_report.json`
* `phase6/canonical_preservation_minimum_set.json`
* `phase6/vcs_preservation_gate_report.json`
* `phase6/post_adoption_required_test_execution_report.json`
* `phase6/current_route_executed_test_inventory.json`
* `phase6/current_route_tooling_closure_impact_report.json`
* `phase6/guard_negative_fixture_report.json`
* `phase6/current_route_validation_result.json`
* `phase6/recursion_avoidance_validation_report.json`
* `phase6/artifact_dependency_graph.json`
* `phase7/final_successor_readpoint_governance_seal_report.json`
* `phase7/validation_report.require_complete.json`
* `phase7/primary_review_artifact_manifest.json`
* `phase7/independent_review_artifact_hash_report.json`
* `phase7/owner_seal_record.json`
* `phase7/ledger_packet.json`

---

## 6. Planned Changes

### Change 0 - Roadmap Provenance and Owner-Reserved Decision Preflight

Purpose:

Bind the transient roadmap input to stable execution provenance and record unresolved decisions before generating authority artifacts.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase0/roadmap_input_binding.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase0/feedback_input_binding.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase0/owner_reserved_decision_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase0/report_field_contract.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase0/preflight_current_checkout_readiness_report.json`

Implementation Notes:

* Record roadmap attachment path, sha256, line count, capture time, and direct plan artifact path.
* Record feedback attachment paths, sha256 values, line counts, verdicts, blocking issues, and required revision incorporation status for both Cycle 1 and Cycle 2 reviews.
* Record candidate round identifier `dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal` as working identifier.
* Keep final canonical round identifier owner-reserved until explicitly sealed.
* Record unresolved decision axes:
  * canonical seal closeout state
  * package peer binding in-scope vs out-of-scope
  * final axis token strings
  * independent-review gate status
  * owner decision / owner seal status
* Default safe execution posture is `machine_governance_packet_possible / canonical_seal_blocked_until_independent_review_and_owner_seal`.
* Owner may select a lower / noncanonical closeout class, but owner decision cannot convert missing independent review into canonical seal allowance.
* `report_field_contract.json` freezes report file names, schema versions, status enum values, required field names, and final report field aliases before implementation. Validators and tests must consume this contract instead of duplicating field strings ad hoc.
* `preflight_current_checkout_readiness_report.json` must check already-observable high-risk assumptions before Phase 1:
  * source facts / decisions / overlay row count, distinct `item_id` count, duplicate count, and key-set equality;
  * rendered entry count, duplicate-aware rendered key count, and source-rendered key-set equality;
  * runtime chunk manifest / chunk file count, runtime key count, and source-runtime key-set equality;
  * package peer existence, package key count, forbidden monolith absence, stale bridge absence, and source-package key-set equality when package output exists;
  * current-route manifest status, required artifact/test counts from execution HEAD, active core `12`, allowlist cap `1`;
  * ignored path inventory for staging evidence and package generated output.
* Preflight failure does not mutate later phases. It either blocks early or explicitly lowers package/canonical scope before expensive evidence generation.

Validation:

* Roadmap input binding includes sha256 `A42B3B00C5B3F196E43542681C680000C401A4D1C2FB5834049EF0E8EFD46CB8` and line count `584`.
* Feedback input binding includes Cycle 1 sha256 `BD35584CE795010FCECEDE34F1ABDFF226B9C74CE92866E6E1FD136C6EB8D96F`, line count `450`, verdict `WARN`, and required revision checklist.
* Feedback input binding includes Cycle 2 sha256 `2B7E41B50B06C2ED724506CF8F80D31D934AF9F642CBF1B3B3F3A2EA347B6D8E`, line count `312`, verdict `WARN - PASS near`, and C6-C8 / N6-N7 required revision checklist.
* Owner-reserved decision matrix exists before Phase 2 taxonomy finalization.
* Report field contract exists before any phase-specific validator/test is considered complete.
* Current checkout readiness preflight records observed counts and key-set diffs; all hard assumptions PASS or the plan closes with an early blocked state.
* Final report cannot claim canonical seal if unresolved owner-reserved fields remain.

---

### Change 1 - Occurrence Inventory / Fingerprint Preflight

Purpose:

Collect every relevant `2105 / 2084 / 21` occurrence across current and current-looking surfaces, with enough fingerprint evidence to distinguish source identity, predecessor trace, denominator, and runtime entry count.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase1/axis_occurrence_inventory.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase1/scan_root_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase1/fingerprint_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase1/surface_coverage_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase1/protected_no_mutation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase1/package_surface_boundary_manifest.json`

Implementation Notes:

* Create `scan_root_manifest.json` before occurrence classification. The occurrence inventory is invalid without this bounded corpus manifest.
* `scan_root_manifest.json` must include included roots, excluded roots, generated-current-round evidence exclusion rule, historical archive inclusion mode, staging final report inclusion mode, package peer inclusion mode, duplicate path handling, symlink handling, generated copy handling, and docs/staging dedup rules.
* Scan at least docs, tests, tools, source data, rendered output, runtime chunk manifest, runtime chunks, package peer if in-scope, current-route manifest, and staging final reports, as bounded by `scan_root_manifest.json`.
* Record path, line or object path, surface family, lifecycle role, source authority role, occurrence value, surrounding context, inferred axis candidate, and ambiguity status.
* Build fingerprint manifest for current source chain, rendered output, runtime chunk manifest, chunk files, package peer if in-scope, current-route manifest, and referenced predecessor evidence roots.
* Rendered JSON parsing must preserve duplicate-key observations. Do not rely on PowerShell `ConvertFrom-Json` for row-key identity.
* `package_surface_boundary_manifest.json` must classify:
  * protected package payload input roots: `Iris/Iris/mod.info`, optional `Iris/Iris/poster.png`, `Iris/Iris/media/**`;
  * generated package peer scan output roots: default `Iris/build/package/Iris/**`, `Iris/build/package/Iris.package_manifest.sha256.json`, `Iris/build/package/Iris.zip`, or explicit `package_iris.ps1 -OutputRoot` equivalent;
  * forbidden generated package surfaces: package monolith `media/lua/client/Iris/Data/IrisLayer3Data.lua` and stale `IrisDvfBridgeData.lua`.
* `protected_no_mutation_report.json` must not count declared generated package peer scan output writes as protected package payload mutation, but must still hash and inventory them in package scan evidence.
* Protected source / rendered / Lua bridge / runtime / package mutation count must remain `0`.

Validation:

* Surface coverage report includes all required surface families.
* `scan_root_manifest.json` validation PASS.
* Re-running the inventory against the same manifest produces the same file universe and occurrence count, except for explicitly excluded current-round generated evidence.
* Missing required surface family count is `0`, unless package peer is explicitly out-of-scope.
* Fingerprint manifest includes source chain hashes from `dvf_3_3_input_manifest.json`.
* Package surface boundary manifest PASS, with no ambiguous path classified as both protected package payload and generated package scan output.
* Protected mutation count is `0`.

---

### Change 2 - Closed Four-Axis Taxonomy / Successor Readpoint Vocabulary Split

Purpose:

Define the closed successor readpoint axis set and classify each occurrence into exactly one axis or a fail-loud terminal value.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase2/successor_readpoint_axis_taxonomy.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase2/axis_exhaustiveness_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase2/axis_token_reconciliation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase2/axis_token_non_supersession_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase2/occurrence_axis_map.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase2/successor_readpoint_axis_policy.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase2/successor_readpoint_claim_boundary.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase2/banned_unqualified_claim_patterns.json`

Implementation Notes:

* The `2105` axis set is exactly four axes for this round:
  * `successor_current_row_identity`
  * `predecessor_historical_trace`
  * `migration_consumer_denominator`
  * `runtime_deployable_entry_count`
* Final token strings remain owner-reserved until sealed.
* If a fifth axis candidate is discovered, the taxonomy does not expand silently. The round records `blocked_axis_set_incomplete` or `manual_review_required` and cannot claim complete axis closure.
* `axis_exhaustiveness_report.json` must prove that every in-corpus occurrence is covered by one of the four axes or a fail-loud terminal state, and that every terminal state is counted.
* `axis_token_reconciliation_report.json` must map new axis labels to existing sealed tokens. Existing sealed tokens such as `successor_current_source_authority` remain canonical when they already name an authority role; new axis labels are subordinate classification labels unless owner explicitly seals a supersession.
* `axis_token_non_supersession_report.json` must expose stable fields: `this_round_maps_tokens_only=true`, `sealed_token_supersession_claim=false`, `owner_supersession_plan_present=false`, and `sealed_tokens_replaced=[]`.
* Seal-vs-prerequisite is not a fifth axis. It is the separate Phase 4 evidence role taxonomy.
* Each axis must define allowed surfaces, allowed evidence roots, forbidden inference, and required binding evidence.
* `2105 PASS`, standalone `complete`, standalone `current seal`, and unqualified `2105 current` are banned unless axis-qualified.
* Any occurrence that could plausibly belong to multiple axes must be `manual_review_required` or `blocked_ambiguous_axis`, not silently assigned.

Validation:

* Every occurrence is exactly one of the four axes or a fail-loud terminal value.
* `unclassified_count=0`, or final report records a blocked state.
* `axis_exhaustiveness_report.json` PASS.
* `axis_token_reconciliation_report.json` PASS.
* `axis_token_non_supersession_report.json` PASS and confirms this round maps tokens but does not supersede sealed tokens.
* Mutual exclusivity check PASS.
* Banned unqualified claim scan PASS.
* Final token string sign-off is present before canonical seal.

---

### Change 3 - Count + Row-Key / Count-Hash Chain Binding

Purpose:

Bind source / rendered / Lua bridge / runtime chunk / package peer chain through fresh count/hash and row-key or key-set identity evidence.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase3/current_chain_count_hash_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase3/rowkey_definition.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase3/source_item_id_uniqueness_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase3/intra_source_keyset_equality_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase3/key_transform_rule_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase3/chain_rowkey_identity_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase3/count_vs_rowkey_divergence_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase3/cross_surface_key_correspondence_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase3/rendered_runtime_correspondence_only_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase3/rowkey_package_claim_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase3/source_rendered_runtime_package_binding.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase3/chunk_membership_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase3/package_peer_scan_canonical_minimum.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase3/package_peer_scan_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase3/package_out_of_scope_note.md`

Implementation Notes:

* Source chain binding must include:
  * `dvf_3_3_input_manifest.json`
  * `dvf_3_3_facts.jsonl`
  * `dvf_3_3_decisions.jsonl`
  * `dvf_3_3_overlay_support.jsonl`
* `rowkey_definition.json` must define the canonical source row key as `item_id` for `facts`, `decisions`, and `overlay_support`. `decisions.facts_ref` may be a consistency field but cannot replace `item_id` as the row key.
* `source_item_id_uniqueness_report.json` must prove for each source JSONL file:
  * `row_count == 2105`
  * `distinct_item_id_count == row_count`
  * `duplicate_item_id_count == 0`
* Source duplicate-key handling must be symmetric with rendered duplicate-key handling. Source duplicates are not inventory-only; they block `rowkey_identity_status=pass`.
* `intra_source_keyset_equality_report.json` must prove `facts.item_id key-set == decisions.item_id key-set == overlay_support.item_id key-set`.
* Any facts / decisions / overlay_support missing / extra key count greater than `0` is fail-loud and maps to `blocked_rowkey_identity_unproven`.
* Rendered row key is the rendered entry key / full type key. Runtime row key is the Lua table key in chunk files. Package row key, if in-scope, is the package peer Lua table key.
* `key_transform_rule_report.json` must define the current transform as identity:
  * `item_id -> rendered key`: identity string equality
  * `item_id -> runtime key`: identity string equality
  * `item_id -> package key`: identity string equality when package peer is in-scope
* If a non-identity transform is discovered, the report must record join input, source field, module prefix source, and validation rule, then block canonical seal until a revised plan accepts that transform.
* Cross-surface correspondence is `source item_id` -> `rendered full type key` -> `runtime Lua table key` -> optional `package Lua table key`, using the transform rule above.
* Rendered / runtime / package comparison is correspondence evidence only. It does not make rendered, runtime, or package surfaces source authority.
* Rendered binding must include `Iris/build/description/v2/output/dvf_3_3_rendered.json`, `meta.stats.total`, entries hash, and duplicate-key inventory.
* Duplicate rendered keys are not silently collapsed. The duplicate-key policy is:
  * if duplicate keys affect key-set identity or cross-surface correspondence, `rowkey_identity_status=limited` or `blocked`;
  * if duplicate keys are explainable parser collisions with preserved distinct source keys, record them in inventory and keep rendered comparison correspondence-only;
  * duplicate count `0` is not assumed without duplicate-aware parsing evidence.
* Runtime binding must derive chunk membership from `IrisLayer3DataChunks.lua`, not hardcoded `Chunk001` through `Chunk011`.
* Lua bridge authority must be described as bridge/export contract evidence only; no export mutation is planned. It is not a row-key correspondence node unless an explicit candidate bridge artifact is separately classified.
* Package binding branch:
  * if package peer is in-scope, scan package data dir for chunk manifest, chunk files, and forbidden legacy monolith/stale bridge surfaces.
  * if package peer is out-of-scope, write explicit note and keep package readiness out of claim.
* `package_peer_scan_canonical_minimum.json` separates package scan proof from package payload preservation. For full-chain canonical-ready status, it must include:
  * package chunk manifest hash and package chunk key-set hash;
  * package chunk file membership derived from the package manifest, not a hardcoded chunk list;
  * source/runtime/package key-set equality;
  * forbidden `IrisLayer3Data.lua` monolith absence;
  * stale `IrisDvfBridgeData.lua` absence;
  * generated package output root classification from `package_surface_boundary_manifest.json`;
  * explicit `package_zip_preservation_required_for_canonical=false` unless owner later chooses package zip preservation as a separate release/package readiness scope.
* Package zip or full generated package directory preservation is not required for this governance seal unless separately selected. The canonical minimum is scan evidence plus key/hash/forbidden-surface proof, not package release readiness.
* Count equality alone is insufficient. Report must include key-set hash or row-key diff where technically possible.
* If row-key identity is technically limited for any surface, record `rowkey_identity_status=limited` and restrict canonical seal claims through `rowkey_package_claim_matrix.json`.
* Any component-level "allowed limitation" in row-key or cross-surface correspondence must be translated by `rowkey_package_claim_matrix.json` into a lower claim ceiling for full-chain canonical closeout. Full-chain canonical closeout requires no unresolved allowed limitation.

Validation:

* `current_chain_count_hash_report.json` PASS.
* `rowkey_definition.json` PASS.
* `source_item_id_uniqueness_report.json` PASS with duplicate source key count `0`.
* `intra_source_keyset_equality_report.json` PASS with facts / decisions / overlay_support key-set mismatch count `0`.
* `key_transform_rule_report.json` PASS and declares identity transform, or records blocked non-identity transform state.
* `chain_rowkey_identity_report.json` PASS or explicit limitation with blocked/noncanonical seal state.
* `cross_surface_key_correspondence_report.json` PASS or `limited` with claim ceiling.
* `rendered_runtime_correspondence_only_report.json` confirms non-writer / correspondence-only status.
* `rowkey_package_claim_matrix.json` defines allowed closeout classes for every rowkey/package status combination and demotes any allowed limitation to `limited` / noncanonical for full-chain claims.
* Missing / extra key count is `0` for in-scope comparable surfaces.
* Duplicate rendered key collision is reported, not silently collapsed.
* Chunk manifest membership matches actual chunk files.
* Package branch is exactly one of `in_scope_scanned` or `out_of_scope_noted`.
* If package branch is `in_scope_scanned`, `package_peer_scan_canonical_minimum.json` PASS and zip/full package preservation non-claim is explicit.

---

### Change 4 - Evidence Role Taxonomy / Seal vs Prerequisite Split

Purpose:

Classify vNext / rejected-delta / cutover / drift / adoption / freshness / durable-surface evidence by role, so prerequisite and staging evidence cannot become current authority by implication. This is a separate evidence-classification problem, not a fifth `2105` axis.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase4/evidence_role_taxonomy_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase4/evidence_class_ledger.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase4/seal_vs_prerequisite_map.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase4/prerequisite_candidate_disposition_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase4/direct_authority_read_scan.json`

Implementation Notes:

* Minimum evidence roles:
  * `sealed_current_authority`
  * `prerequisite_evidence`
  * `candidate_evidence`
  * `staging_evidence`
  * `historical_trace`
  * `governance_required_gate`
  * `pre_apply_readiness`
  * `non_authority_fixture`
* Existing roots such as closeout reentry guard, completion vocabulary split, drift verification, evidence freshness reseal, durable surface alignment, runtime payload integrity, and live migration readiness must be classified by role.
* `seal_vs_prerequisite_map.json` must state explicitly that Phase 4 consumes the Phase 2 axis map but does not add a new axis token.
* Prerequisite / candidate evidence cannot be direct current authority unless another current readpoint explicitly seals it.
* Raw audit / readiness / dry-run / predecessor artifact direct execution authority reads are forbidden.

Validation:

* Evidence role taxonomy report PASS.
* Seal-vs-prerequisite scope alignment PASS.
* `candidate_promoted_to_current_authority_count=0`.
* `prerequisite_direct_execution_authority_count=0`.
* `staging_as_current_authority_count=0`.
* `raw_audit_as_execution_authority_count=0`.

---

### Change 5 - Predecessor Reentry Axis Guard

Purpose:

Block predecessor `2105 / 2084 / 21` from reentering as current hard gate, runtime authority, package authority, current debt, or release readiness.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase5/predecessor_reentry_axis_guard_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase5/allowed_predecessor_context_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase5/forbidden_predecessor_context_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase5/claim_scan_inventory.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase5/no_axis_misuse_report.json`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal.py`

Implementation Notes:

* Allowed predecessor contexts:
  * historical predecessor trace
  * frozen comparison baseline
  * migration provenance
  * terminal disposition provenance
  * diagnostic fixture trace
* Forbidden contexts:
  * current hard gate
  * current runtime authority
  * package authority
  * release readiness
  * current debt
  * required migration target expansion
  * old chunks fallback
  * monolith fallback
  * raw predecessor artifact direct execution authority
* Negative fixtures must include successor `2105` and predecessor `2105` same-value ambiguity to prevent numeric-only false positives.

Validation:

* Predecessor reentry report PASS.
* `predecessor_current_hard_gate_count=0`.
* `predecessor_runtime_authority_count=0`.
* `predecessor_package_authority_count=0`.
* `predecessor_current_debt_count=0`.
* `old_chunks_or_monolith_fallback_count=0`.
* Historical trace preservation count is recorded separately.

---

### Change 6 - Live Required-Validation Manifest Additive Adoption

Purpose:

Make successor readpoint axis misuse and predecessor reentry fail-closed in future current-route closeouts through additive live manifest adoption.

Files:

* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase6/live_required_manifest_adoption_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase6/current_route_required_validation_candidate_patch.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase6/manifest_additive_diff_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase6/vcs_preservation_preflight_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase6/canonical_preservation_minimum_set.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase6/vcs_preservation_gate_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase6/post_adoption_required_test_execution_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase6/current_route_executed_test_inventory.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase6/current_route_tooling_closure_impact_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase6/guard_negative_fixture_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase6/current_route_validation_result.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase6/recursion_avoidance_validation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase6/artifact_dependency_graph.json`

Implementation Notes:

* Current manifest baseline observed at planning time only:
  * schema `round3-current-route-required-validations-v1`
  * status `PASS`
  * required artifacts `75`
  * required tests `40`
* Execution must recompute pre-adoption required artifact/test counts from execution HEAD before generating `current_route_required_validation_candidate_patch.json`; the planning-time `75/40` values are not hardcoded expected counts.
* `current_route_required_validation_candidate_patch.json` is generated and validated before any live manifest mutation. It must list only added required artifacts/tests/check predicates and must include no remove/replace operations.
* `manifest_additive_diff_report.json` compares execution-HEAD manifest, candidate patch, and final manifest. It must record pre-adoption count, candidate post-adoption expected count, final post-adoption count, added artifact count, added test count, removed count `0`, modified count `0`, and duplicate count `0`.
* Adoption sequence is candidate patch -> additive diff validation -> no-op adoption check planning -> live manifest write -> current-route execution inventory. Direct live manifest mutation before candidate patch validation is blocked.
* Adoption must add new required artifacts/tests/checks without removing or modifying existing ones. Removal or modification count greater than `0` is terminal fail for this round.
* Phase 6 manifest required checks may consume only Phase 0 through Phase 6 stable machine/governance artifacts.
* Phase 7 final report, independent review artifact, owner seal record, and canonical seal fields are not current-route manifest self-requirements. They are checked by `validate --require-complete` and final seal wrapper validation.
* `artifact_dependency_graph.json` must show that Phase 6 required artifacts do not depend on Phase 7 final artifacts.
* `recursion_avoidance_validation_report.json` must consume the artifact dependency graph and prove no self-referential hash or final-artifact requirement cycle exists.
* `current_route_tooling_closure_impact_report.json` must prove the new tools are not current core modules, active core count remains `12`, current-route tooling allowlist cap `1` is not bypassed, and any required allowlist change is explicitly separate reviewed scope.
* `post_adoption_required_test_execution_report.json` must prove this adoption is not a no-op:
  * either `post_adoption_executed_test_count == pre_adoption_executed_test_count + new_required_test_count`;
  * or every named new required test is present in `current_route_executed_test_inventory.json` with executed state and not skipped / missing / failed.
* Missing, skipped, or absent new required tests map to `blocked_no_op_manifest_adoption`.
* `vcs_preservation_preflight_report.json` must classify all related tool/test/docs/evidence/live-manifest/package-generated paths before the final gate:
  * `tracked_or_force_stage_candidate_paths`;
  * `canonical_preservation_minimum_candidates`;
  * `ignored_but_hash_preserved_local_evidence_paths`;
  * `generated_package_scan_output_paths`;
  * `noncanonical_local_only_evidence_paths`;
  * `blocked_ambiguous_preservation_paths`.
* `canonical_preservation_minimum_set.json` must define the smallest path set needed for canonical-ready governance preservation: source plan/docs, new tool modules, new tests, live manifest diff, candidate patch, final validator outputs, field contract, and hash manifests for ignored generated evidence. Generated package zip/full directory is excluded unless separately selected.
* `vcs_preservation_gate_report.json` must prove the canonical minimum set is preserved in the same VCS boundary, not merely intended to be preserved. For canonical closeout, each minimum-set path must be either already tracked or explicitly staged / commit-bound, must not be ignored by VCS unless paired with a tracked hash-manifest surrogate, and must be listed in the preservation proof with its status.
* If `package_iris.ps1 -Clean` is used for a package peer scan, any generated package directory or zip under the declared generated output root is a generated package peer scan artifact, not live package payload mutation and not package readiness.
* Generated package peer scan outputs must be inventoried separately from protected no-mutation surfaces. Writes outside the declared generated output root or writes to protected package payload inputs remain protected mutation failures.
* Current-route manifest adoption is governance-only and not writer authority.

Validation:

* Manifest additive diff report PASS.
* Candidate manifest patch PASS before live manifest mutation.
* Existing required artifact/test removals `0`.
* Existing required artifact/test modifications `0`.
* Existing sealed body rewrite count `0`.
* Post-adoption expected artifact/test counts equal pre-adoption counts plus added counts.
* New required test execution inventory proves all newly added tests were selected and executed in current-route validation.
* VCS preservation preflight PASS with ambiguous preservation path count `0`.
* Canonical preservation minimum set PASS and does not require ignored generated package zip/full directory preservation.
* VCS preservation gate PASS proves minimum-set tool/test/docs/evidence/live-manifest paths are tracked or staged / commit-bound, not ignored unless covered by tracked hash-manifest surrogate, and in one VCS boundary; otherwise final closeout is noncanonical / machine-packet-only.
* Generated package peer scan output inventory PASS when package peer is in-scope; no generated output path is ambiguous with a protected package payload input.
* Current-route tooling closure impact report PASS.
* Active core `12` unchanged.
* Current-route allowed tooling modules remain within cap, or the round is blocked pending separate reviewed closure scope.
* Duplicate entries `0`.
* Artifact dependency graph PASS.
* Phase 6 does not require Phase 7 final report / independent review / owner seal artifacts.
* Current-route validation PASS.
* Closure enforced true.
* Negative fixture matrix PASS.
* Protected source / rendered / Lua / runtime / package mutation `0`.

---

### Change 7 - Final Governance Seal Packet / Review Boundary

Purpose:

Separate machine contract result, artifact binding, independent-review state, owner decision, owner seal, and canonical seal status in the final packet.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase7/final_successor_readpoint_governance_seal_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase7/validation_report.require_complete.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase7/primary_review_artifact_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase7/independent_review_artifact_hash_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase7/owner_seal_record.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal/phase7/ledger_packet.json`
* `docs/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal_claim_boundary.md`
* `docs/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal_ledger_packet.md`

Implementation Notes:

* Final report minimum fields:
  * `machine_contract_status`
  * `report_field_contract_status`
  * `preflight_current_checkout_readiness_status`
  * `successor_readpoint_axis_state`
  * `axis_misuse_count`
  * `predecessor_reentry_count`
  * `axis_token_non_supersession_status`
  * `count_hash_binding_status`
  * `rowkey_identity_status`
  * `source_item_id_uniqueness_status`
  * `intra_source_keyset_status`
  * `key_transform_rule_status`
  * `package_scope_status`
  * `package_peer_scan_canonical_minimum_status`
  * `full_source_rendered_runtime_package_binding_claim`
  * `claim_ceiling_matrix_status`
  * `evidence_role_taxonomy_status`
  * `manifest_additive_only`
  * `candidate_manifest_patch_status`
  * `vcs_preservation_status`
  * `vcs_preservation_preflight_status`
  * `canonical_preservation_minimum_set_status`
  * `vcs_preservation_proof_status`
  * `package_surface_boundary_status`
  * `post_adoption_required_test_execution_status`
  * `protected_mutation_changed_count`
  * `current_route_tooling_closure_status`
  * `phase6_phase7_dependency_graph_status`
  * `independent_review_status`
  * `owner_decision_status`
  * `owner_seal_status`
  * `canonical_seal_status`
  * `canonical_seal_allowed`
* `rowkey_identity_status` enum is `pass|limited|blocked`.
* `rowkey_identity_status=pass` requires source `item_id` uniqueness PASS, facts/decisions/overlay_support key-set equality PASS, transform rule PASS, and cross-surface correspondence PASS with no unresolved limitation that affects full-chain canonical claims.
* If a component report contains an "allowed limitation", the final report must either resolve it to PASS before full-chain canonical closeout or set `rowkey_identity_status=limited`; `rowkey_package_claim_matrix.json` is the controlling source for that demotion.
* `package_scope_status` enum is `in_scope_scanned|out_of_scope_noted|unresolved`.
* `independent_review_status` enum treats `blocked` / `BLOCKED` as a first-class terminal-for-canonical-seal state, not as absence to be coerced into owner approval.
* `full_source_rendered_runtime_package_binding_claim` is `true` only when row-key identity passes for all in-scope surfaces and package scope is `in_scope_scanned`.
* `canonical_seal_allowed=true` for the full roadmap scope requires report field contract PASS, checkout preflight PASS, `rowkey_identity_status=pass`, no unresolved allowed limitation in the claim ceiling matrix, source `item_id` uniqueness PASS, intra-source key-set equality PASS, identity key transform PASS, `package_scope_status=in_scope_scanned`, package surface boundary PASS, package peer scan canonical minimum PASS, candidate manifest patch PASS, Phase 6 / Phase 7 dependency graph PASS, no-op adoption guard PASS, VCS preservation preflight PASS, canonical preservation minimum set PASS, VCS preservation proof PASS, current-route tooling closure status PASS, protected mutation changed count `0`, non-Claude / non-author independent review PASS, owner decision, owner seal, and final token sign-off.
* `package_scope_status=out_of_scope_noted` can support only a lower / noncanonical source-rendered-runtime governance packet unless owner later approves a narrower canonical scope as a separate plan.
* Branch-specific success criteria must be recorded for at least:
  * `full_chain_canonical_candidate`
  * `source_rendered_runtime_only_noncanonical`
  * `machine_packet_review_blocked`
  * `package_scope_unresolved_blocked`
* If non-Claude / non-author independent review is absent, final report must keep `canonical_seal_allowed=false`.
* Owner may approve a lower / noncanonical closeout class such as `machine_governance_packet_complete`, but owner decision cannot transform missing independent review into canonical seal allowance.
* If owner decision / owner seal is absent, final report must keep owner axis `pending` or `blocked`.
* If package scope is unresolved, final report must not claim full source/rendered/runtime/package chain binding.
* DECISIONS / ROADMAP update drafts must preserve non-claims and remain draft-only until final seal status is resolved.

Validation:

* Focused runner PASS.
* Focused validator `--require-complete` PASS.
* Focused unittest PASS.
* Current-route required validation PASS.
* Report field contract PASS and final report field names match the contract.
* Current checkout readiness preflight PASS.
* Primary review artifact manifest completeness PASS.
* Hash-sealed bundle completeness PASS.
* Self-referential hash cycle count `0`.
* Claim ceiling matrix PASS for rowkey/package status combinations.
* Source key uniqueness and intra-source key-set equality PASS.
* Candidate manifest patch PASS and precedes live manifest mutation.
* No-op adoption guard PASS.
* VCS preservation preflight PASS.
* Canonical preservation minimum set PASS.
* VCS preservation proof PASS or canonical seal disallowed.
* Package surface boundary PASS if package peer is in-scope.
* Package peer scan canonical minimum PASS if package peer is in-scope.
* Independent-review missing fixture produces `canonical_seal_allowed=false`.
* Canonical seal status reflects independent-review / owner-reserved decision state.

---

## 7. Validation Plan

### Automated Validation

Do not claim validation passed unless the exact relevant command exits with code `0`.

Expected command candidates:

```powershell
uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal.py --mode all
```

```powershell
uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal.py --require-complete
```

```powershell
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal.py"
```

```powershell
uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure --out Iris\build\description\v2\staging\dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal\phase6\current_route_validation_result.json
```

Conditional package scan, only if package peer is selected in-scope:

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean
```

Required automated validation families:

* roadmap provenance binding
* feedback provenance binding and WARN required-revision checklist
* owner-reserved decision matrix validation
* report field contract validation
* current checkout readiness preflight validation
* current-route tooling allowlist / active closure impact validation
* active core `12` unchanged validation
* tooling allowlist cap validation
* bounded scan root manifest validation
* surface coverage completeness
* occurrence inventory schema validation
* axis closure / exhaustiveness validation
* axis token reconciliation with existing sealed tokens
* axis token non-supersession stable field validation
* duplicate-key-aware rendered key inventory
* closed four-axis taxonomy validation
* per-occurrence mutual exclusivity validation
* axis-confusion negative fixtures
* banned unqualified claim scan
* seal-vs-prerequisite separate-scope validation
* source chain count/hash validation
* source `item_id` uniqueness validation
* source duplicate-key handling validation
* facts / decisions / overlay_support key-set equality validation
* rendered count/hash validation
* row-key definition validation
* `item_id` to rendered/runtime/package key transform validation
* cross-surface key correspondence validation
* row-key or key-set identity validation
* rendered non-writer / correspondence-only validation
* chunk manifest membership derivation from `IrisLayer3DataChunks.lua`
* package branch validation
* package peer scan canonical minimum validation
* protected package surface vs generated package scan output boundary validation
* rowkey limited / package out-of-scope claim matrix validation
* evidence role taxonomy validation
* prerequisite / candidate direct-authority read rejection
* predecessor reentry guard validation
* old chunk / monolith fallback scan
* manifest additive diff validation
* candidate manifest patch validation before live manifest mutation
* manifest execution-HEAD baseline count recomputation
* post-adoption expected required artifact/test count validation
* no-op adoption prevention through named new required test execution inventory
* VCS preservation preflight validation
* canonical preservation minimum set validation
* VCS preservation proof validation for tracked / not-ignored / staged-or-commit-bound paths or tracked hash-manifest surrogates
* existing sealed body rewrite count validation
* negative fixture matrix
* Phase 6 / Phase 7 artifact dependency graph validation
* recursion avoidance validation
* protected source / rendered / Lua bridge / runtime / package no-mutation
* final report schema validation
* canonical seal disallow validation when independent review is missing
* independent review / owner seal boundary validation
* current-route required-validation runner regression

### Manual Validation

Manual validation is governance / artifact inspection only:

* inspect roadmap provenance and sha256
* inspect feedback provenance and required revision incorporation
* inspect owner-reserved decision matrix
* inspect report field contract
* inspect current checkout readiness preflight report
* inspect current-route tooling closure impact report
* inspect scan root manifest and exclusion/dedup rules
* inspect axis taxonomy and token names
* inspect axis exhaustiveness, token reconciliation, and token non-supersession reports
* inspect ambiguous occurrence disposition
* inspect rendered duplicate-key handling
* inspect row-key definitions, cross-surface correspondence, and row-key identity limitations
* inspect source `item_id` uniqueness and intra-source key-set equality reports
* inspect key transform rule report
* inspect package scope decision and package surface boundary manifest
* inspect package peer scan canonical minimum report
* inspect rowkey/package claim ceiling matrix
* inspect evidence role taxonomy
* inspect predecessor allowed / forbidden context tables
* inspect live manifest additive diff
* inspect candidate manifest patch and live mutation ordering
* inspect post-adoption executed test inventory
* inspect VCS preservation preflight, canonical minimum set, and final preservation proof report
* inspect current-route validation result
* inspect final report non-claims
* inspect independent review and owner seal records if present

Manual validation does not mean in-game validation.

### Validation Limits

This plan will not validate:

* live migration execution
* source mutation correctness
* rendered regeneration correctness
* Lua bridge export correctness
* runtime chunk replacement correctness
* runtime behavior equivalence
* multiplayer validation
* long-session runtime validation
* external ecosystem compatibility sweep
* package release readiness
* Workshop readiness
* B42 readiness
* deployment readiness
* manual in-game QA
* public-facing text quality
* semantic quality completion
* full historical byte reproducibility
* full clean-checkout required-evidence reproducibility
* actual package publication

---

## 8. Risk Surface Touch

### Authority Surface

Touched / governance-only.

This plan adds vocabulary, evidence-role, and required-validation governance surface. It does not create or replace source authority, rendered authority, Lua bridge authority, runtime authority, package authority, or release authority.

### Runtime Behavior Surface

None planned.

Runtime Lua, Browser, Wiki, Tooltip, layer3 renderer behavior, runtime chunk payloads, and package payloads must remain unchanged.

### Compatibility Surface

Medium internal workflow risk.

Current-route validation may become stricter. Existing docs/tests/tools that used unqualified `2105`, `complete`, `PASS`, or predecessor counts in mixed contexts may fail new guards unless classified as historical / predecessor / prerequisite.

### Sealed Artifact Surface

Additive only.

Existing sealed artifacts are read-only inputs. New staging artifacts and final governance packets may be produced under the new evidence root. Historical evidence must not be rewritten.

### Public-Facing Output Surface

None.

No user-facing text, release claim, README marketing claim, Workshop text, tooltip, Browser, or Wiki output mutation is planned.

---

## 9. Risk Analysis

### Architecture Risk

* The four-axis taxonomy can accidentally become a new source authority layer. Mitigation: keep taxonomy governance-only and bind source authority back to existing manifest paths.
* The axis set can become open-ended again if additional axis candidates are accepted silently. Mitigation: exactly four axes for this round; extra axis candidates block completion.
* New axis labels can overload existing sealed tokens. Mitigation: keep existing sealed authority tokens canonical and record axis labels as subordinate classification labels unless owner seals supersession.
* Axis token supersession is out of scope for this round unless a separate owner-approved plan opens it. This round maps tokens; it does not supersede sealed tokens by itself, and the implementation report must restate non-supersession in stable machine fields.
* Count equality can be mistaken for row-key identity. Mitigation: require row-key or key-set evidence and explicit count-vs-identity report.
* Source-side duplicate `item_id` or source key-set mismatch can make row-key proof hollow. Mitigation: source uniqueness and intra-source key-set equality are hard validation gates.
* Evidence role taxonomy can reopen sealed predecessor rounds. Mitigation: classify existing roots by role without re-adjudicating their closed claims.
* Live manifest adoption can be overread as writer authority. Mitigation: final report and manifest adoption report must state governance-only non-writer status.
* VCS preservation can be overclaimed as intent. Mitigation: require tracked / not-ignored / staged-or-commit-bound path proof for all related tool/test/docs/evidence/live-manifest changes before canonical closeout.
* VCS preservation can fail late because generated staging and package outputs are ignored. Mitigation: run VCS preservation preflight early, define a canonical minimum set, and preserve ignored generated evidence through tracked hash-manifest surrogates instead of requiring every generated byte to be tracked.
* Report/test/schema field drift can break an otherwise valid round. Mitigation: freeze `report_field_contract.json` in Phase 0 and require validators/tests/final report to consume that contract.

### Runtime Risk

* Runtime risk should remain none because no runtime mutation is planned.
* Accidental exporter/package execution could write runtime or package surfaces. Mitigation: protected no-mutation reports before and after execution.
* Monolith fallback could reappear through convenience export paths. Mitigation: explicit scan for `IrisLayer3Data.lua` and stale bridge surfaces.

### Compatibility Risk

* Duplicate keys in rendered JSON can make naive JSON parsers fail or silently collapse key identity. Mitigation: use duplicate-aware parsing and record duplicate-key inventory.
* Package peer may be absent or stale. Mitigation: branch package binding as in-scope scanned or explicit out-of-scope.
* Package zip/full generated directory preservation can be confused with package scan proof. Mitigation: `package_peer_scan_canonical_minimum.json` makes key/hash/forbidden-surface scan evidence canonical-ready while keeping package zip preservation out of scope unless separately selected.
* Existing current-route required manifest has many adopted gates. Mitigation: additive-only diff and no predicate modification.
* New tools can collide with current-route active closure or tooling allowlist. Mitigation: closure impact report must prove active core `12` unchanged and no allowlist cap bypass.
* Phase 6 manifest adoption can self-require Phase 7 final artifacts. Mitigation: artifact dependency graph and wrapper-only Phase 7 validation.
* Historical trace can create false positives in predecessor reentry scan. Mitigation: allowed predecessor context table and negative fixtures for same-value successor/predecessor `2105`.

### Regression Risk

* A future closeout may emit `2105 PASS` without axis. Mitigation: banned unqualified claim patterns and current-route required validation.
* Predecessor `2084 / 21` may reenter through current debt or unadopted vocabulary. Mitigation: direct current debt and runtime authority scans.
* Package route may accidentally be described as readiness. Mitigation: package scan report must separate forbidden legacy scan from package readiness.
* Generated package peer scan outputs can be mistaken for live package payload mutation, or can hide real payload mutation if boundaries are vague. Mitigation: define protected package payload inputs and generated package scan output roots in `package_surface_boundary_manifest.json`, then inventory generated outputs separately.
* Final machine PASS can be mistaken for canonical seal. Mitigation: independent review, owner decision, owner seal, and canonical seal status fields stay separate.
* Row-key limited, component-level allowed limitation, or package out-of-scope states may be overclaimed. Mitigation: rowkey/package claim ceiling matrix demotes any unresolved allowed limitation to `limited` / noncanonical for full-chain claims and controls `canonical_seal_allowed`.
* No-op manifest adoption can pass without executing new guards. Mitigation: post-adoption executed test inventory must prove new required tests ran.
* Live manifest mutation can happen before a candidate patch is validated. Mitigation: require candidate patch -> additive diff -> no-op adoption planning -> live mutation -> current-route inventory ordering.
* Post-convergence plan expansion can accumulate regression risk through new constants, artifacts, fields, and closeout enums. Mitigation: freeze plan text after N12 and move additional advisory findings into execution validators / fail-loud reports instead of expanding the plan.

---

## 10. Rollback Plan

Rollback is governance/tooling rollback, not runtime rollback.

Before manifest adoption:

* discard or quarantine the new evidence root
* remove candidate tooling and tests for this round
* keep historical evidence untouched
* keep source / rendered / runtime / package surfaces unchanged

After manifest adoption:

* revert only this round's additive entries from `Iris/_docs/round3/current_route_required_validations.json`
* revert candidate tooling/tests/docs as one rollback unit if validators are overbroad
* preserve failed evidence as historical / diagnostic trace
* do not lower fail-closed behavior to advisory-only without a separate plan

If protected source / rendered / Lua bridge / runtime / package mutation is detected:

* stop the round
* record changed files in protected no-mutation report
* restore accidental mutation only with explicit approval where required
* close as blocked or rolled back
* do not emit successor readpoint seal completion

If axis taxonomy proves insufficient:

* do not rewrite sealed predecessor docs
* add a supersession or correction artifact under the evidence root
* keep canonical seal blocked until revised taxonomy validates

If independent review or owner seal is missing:

* preserve machine artifacts as partial / governance-ready
* keep `canonical_seal_allowed=false`
* do not update DECISIONS / ROADMAP as canonical complete

If additive-only is violated:

* stop the round
* record removed / modified existing required entries and sealed body rewrite count
* revert the manifest or sealed-body mutation as the rollback unit
* close as `blocked_additive_only_violation`

If report field contract or current checkout preflight fails:

* stop before phase-specific evidence generation or live manifest mutation
* record failed contract field / failed checkout assumption
* revise the plan or lower the claim scope before continuing
* close as `blocked_report_field_contract_incomplete` or `blocked_current_checkout_preflight_failed`

If candidate manifest patch validation fails:

* do not mutate `Iris/_docs/round3/current_route_required_validations.json`
* record invalid add/remove/modify/duplicate operation in `manifest_additive_diff_report.json`
* revise candidate patch before current-route execution
* close as `blocked_candidate_manifest_patch_invalid`

If Phase 6 / Phase 7 dependency graph shows a self-reference:

* remove Phase 7 final artifacts from current-route required manifest candidates
* keep Phase 7 validation in wrapper / complete validator only
* close as blocked until dependency graph validation passes

If source row-key validation fails:

* stop before row-key identity PASS claim
* record duplicate source keys or intra-source key-set mismatch
* close as `blocked_source_rowkey_integrity_failed` or `blocked_intra_source_keyset_mismatch`

If post-adoption required tests are not executed:

* stop before required-validation gate adoption closeout
* record missing / skipped / unselected new required tests
* close as `blocked_no_op_manifest_adoption`

If VCS preservation is not satisfied:

* preserve machine artifacts as noncanonical evidence
* record whether failure is preflight ambiguity, missing canonical minimum path, ignored path without tracked hash surrogate, or not-staged path
* keep `canonical_seal_allowed=false`
* close as `machine_governance_packet_complete`, `blocked_vcs_preservation_preflight_failed`, `blocked_canonical_preservation_minimum_unmet`, or `blocked_vcs_preservation_unmet`

If package surface boundary is ambiguous or generated output escapes the declared root:

* stop package peer scan claim
* record ambiguous / escaped paths in `package_surface_boundary_manifest.json`
* keep protected package mutation status blocked until reviewed
* close as `blocked_package_surface_boundary_unresolved` or lower to package out-of-scope noncanonical closeout

If package peer scan canonical minimum fails:

* keep package peer out of full-chain canonical claim
* record missing package key/hash/forbidden-surface proof in `package_peer_scan_canonical_minimum.json`
* lower to source-rendered-runtime noncanonical governance packet or close as `blocked_package_peer_scan_canonical_minimum_unmet`

---

## 11. Governance Constraints

* Preserve `docs/Philosophy.md` compliance.
* Preserve Hub & Spoke / SPI boundaries.
* Preserve Iris runtime as Lua-only display surface, not runtime validation / repair / policy engine.
* Preserve runtime / build-time separation.
* No source facts / decisions / overlay_support mutation.
* No rendered output mutation.
* No Lua bridge export mutation.
* No runtime chunk mutation.
* No package payload mutation.
* Protected package payload inputs and generated package peer scan outputs must be path-separated. Generated package scan writes are allowed only under the declared generated output root and never count as package readiness.
* No `IrisLayer3Data.lua` monolith revival.
* No stale `IrisDvfBridgeData.lua` revival.
* `active / silent` remains historical / diagnostic / import alias only.
* `adopted / unadopted` remains current runtime vocabulary only, not quality / publish / deletion / suppression vocabulary.
* `2105` must be axis-qualified when used in current claims.
* Count equality cannot substitute for row-key identity.
* Source `item_id` uniqueness is mandatory. Each source JSONL file must prove `distinct item_id count == row count == 2105`.
* Facts / decisions / overlay_support key sets must be equal for this round.
* `item_id` to rendered/runtime/package key transform must be explicit and validated.
* Any row-key "allowed limitation" must lower full-chain canonical claim status to `limited` / noncanonical unless resolved to PASS before final closeout.
* Duplicate rendered keys must be detected or explicitly accounted for.
* Axis token reports must state that this round maps tokens and does not supersede sealed tokens unless a separate owner-approved supersession plan exists.
* Predecessor `2105 / 2084 / 21` may appear only in allowed historical / comparison / migration / terminal provenance contexts.
* Raw audit / readiness / dry-run / predecessor artifact may not become direct execution authority.
* Required-validation manifest adoption is additive-only and governance-only.
* Live required-validation manifest mutation must be preceded by a validated candidate patch.
* Existing required artifacts/tests/check predicates must not be removed or modified.
* Existing required artifact/test/check predicate removal or modification count greater than `0` is terminal fail for this round.
* Existing sealed body rewrite count greater than `0` is terminal fail for this round.
* Missing or ambiguous evidence fails closed.
* Phase 0 report field contract must be the source of truth for report/test/final field names.
* Current checkout preflight must pass, or the plan must lower scope before producing later PASS claims.
* Package peer scope must be explicitly selected or explicitly out-of-scope.
* Package peer canonical-ready scan proof requires `package_peer_scan_canonical_minimum.json`; package zip/full directory preservation is not package readiness and is not required unless separately selected.
* Row-key identity status and package scope status must be reflected in a claim ceiling matrix before any final closeout claim.
* Plan text is frozen after N12 incorporation. Do not add new artifacts, final fields, closeout enums, or validation families for advisory post-convergence concerns unless execution proves the existing contract cannot represent the failure.
* Machine PASS does not replace independent review.
* Owner decision and owner seal do not replace independent review.
* Non-Claude / non-author independent review is required for canonical seal. Owner may choose a lower / noncanonical closeout class, but cannot convert missing independent review into `canonical_seal_allowed=true`.
* Owner-reserved fields must remain blocked or pending until captured.
* Current-route manifest Phase 6 requirements must not require Phase 7 final report, independent review artifact, owner seal artifact, or canonical seal fields.
* New tooling must not be treated as current core. Active core `12` and tooling allowlist cap must remain intact unless a separate reviewed closure scope explicitly changes them.
* New required tests added to the live manifest must be proven executed in the current-route run; manifest presence alone is not adoption completion.
* VCS preservation of the canonical minimum set is required for canonical closeout preservation. It must be proven with tracked / not-ignored / staged-or-commit-bound path status, or tracked hash-manifest surrogates for ignored generated evidence; if not satisfied, closeout is noncanonical.
* Final reports and docs must not claim release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, semantic quality completion, or public-facing text acceptance.
* Dirty worktree changes outside this plan must be preserved.

---

## 12. Expected Closeout State

Expected plan artifact closeout:

```text
successor_readpoint_seal_plan_revised / WARN_feedback_incorporated / plan_text_frozen / re_review_required
```

Expected execution closeout is conditional.

If report field contract, current checkout preflight, occurrence inventory, bounded scan corpus, closed four-axis taxonomy, axis exhaustiveness, token reconciliation, axis token non-supersession, count/hash binding, source `item_id` uniqueness, intra-source key-set equality, explicit key transform validation, row-key/key-set evidence with no unresolved allowed limitation, cross-surface correspondence, package surface boundary, package peer scan canonical minimum, evidence role taxonomy, predecessor reentry guard, tooling closure impact, Phase 6 / Phase 7 dependency graph, candidate manifest patch, manifest additive adoption, post-adoption required test execution, VCS preservation preflight, canonical preservation minimum set, VCS preservation proof, focused validation, current-route validation, protected no-mutation, non-Claude / non-author independent review, owner decision, owner seal, package-scope decision, claim ceiling matrix, and final token sign-off all pass:

```text
successor_readpoint_governance_seal_complete
canonical_seal_allowed=true
```

If machine validation passes but independent review, owner seal, package-scope decision, or final token sign-off is missing:

```text
machine_governance_packet_complete
canonical_seal_allowed=false
canonical_seal_status=blocked_or_pending
```

Allowed alternate closeout states:

* `implemented_only`
* `blocked_report_field_contract_incomplete`
* `blocked_current_checkout_preflight_failed`
* `blocked_occurrence_inventory_incomplete`
* `blocked_scan_root_manifest_incomplete`
* `blocked_axis_taxonomy_incomplete`
* `blocked_axis_exhaustiveness_unproven`
* `blocked_axis_token_reconciliation_incomplete`
* `blocked_axis_token_non_supersession_unproven`
* `blocked_ambiguous_axis_occurrence`
* `blocked_rowkey_identity_unproven`
* `blocked_source_rowkey_integrity_failed`
* `blocked_intra_source_keyset_mismatch`
* `blocked_key_transform_rule_undefined`
* `blocked_rowkey_identity_limited_for_canonical_seal`
* `blocked_duplicate_key_handling_incomplete`
* `blocked_cross_surface_correspondence_unproven`
* `blocked_evidence_role_taxonomy_incomplete`
* `blocked_predecessor_reentry_detected`
* `blocked_additive_only_violation`
* `blocked_candidate_manifest_patch_invalid`
* `blocked_current_route_tooling_closure_unresolved`
* `blocked_phase6_phase7_dependency_cycle`
* `blocked_no_op_manifest_adoption`
* `blocked_vcs_preservation_preflight_failed`
* `blocked_canonical_preservation_minimum_unmet`
* `blocked_vcs_preservation_unmet`
* `blocked_manifest_adoption_unapproved`
* `blocked_current_route_validation_failed`
* `blocked_package_scope_unresolved`
* `blocked_package_out_of_scope_for_full_chain_claim`
* `blocked_package_surface_boundary_unresolved`
* `blocked_package_peer_scan_canonical_minimum_unmet`
* `blocked_independent_review_pending`
* `blocked_owner_seal_pending`
* `blocked_no_mutation_violation`
* `revised_plan_needed`

This closeout never means source mutation, rendered regeneration, Lua bridge export, runtime chunk replacement, package payload mutation, live migration execution, package readiness, release readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game QA, semantic quality completion, public-facing text acceptance, full runtime equivalence, full compatibility preservation, full clean-checkout required-evidence reproducibility, or full historical byte reproducibility.
