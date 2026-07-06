# Implementation Plan

> Status: planned / roadmap-derived / codebase-inspected / synthesized-review-remediated / governance-only required-gate adoption
> 작성일: 2026-07-05
> 최근 수정: 2026-07-06
> Round candidate: `dvf_3_3_core_registry_boundary_required_gate_adoption`
> Roadmap input: `C:/Users/MW/.codex/attachments/2ca9bf40-0684-4e63-af74-039cc1b8ff56/pasted-text.txt`
> Review input: `C:/Users/MW/.codex/attachments/90fb5ad9-34d9-44c2-9022-f10ad59bb6f8/pasted-text.txt` / verdict `FAIL` / Required Revisions 1-8 incorporated
> Review input: `C:/Users/MW/.codex/attachments/d457bdc6-dc63-4fa4-8ded-7e0b3451c8dc/pasted-text.txt` / verdict `WARN` / sequencing fixes incorporated / two-pass current-route closure selected
> Review input: `C:/Users/MW/.codex/attachments/ff79c9a3-6614-4ed7-b6d0-dfd90749470b/pasted-text.txt` / verdict `PASS` / plan-level only / independent review gate remains blocked / non-critical implementation absorption items incorporated
> Template input: `docs/PLAN_TEMPLATE.md`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Primary predecessor: `dvf_3_3_core_registry_boundary_claim_contract_closure`
> Planned evidence root: `Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_required_gate_adoption/`

---

## 1. Objective

DVF Core / Iris Artifact Registry boundary claim contract를 live current-route required-validation gate로 채택한다.

선행 `dvf_3_3_core_registry_boundary_claim_contract_closure`는 governance-only machine contract로 닫혔지만, final report 기준 다음 값은 아직 닫히지 않았다.

```text
required_gate_adopted=false
future_current_route_blocking_claimed=false
```

이번 계획의 목적은 기존 claim 의미를 재정의하지 않고, 이미 봉인된 boundary claim contract를 `Iris/_docs/round3/current_route_required_validations.json`이 additive required gate로 소비하도록 만드는 것이다.

완료 후 목표 machine state:

```text
required_gate_adopted=true
future_current_route_blocking_claimed=true
legacy_combined_route_pass_is_dvf_core_pass=false
dvf_pass_standalone_current_claim_allowed=false
protected_surface_changed_count=0
source_rendered_lua_runtime_package_mutation=false
```

`future_current_route_blocking_claimed=true`는 replayed artifact 확인만으로는 주장할 수 없다. 이 값은 current-route 실행 시점마다 다음을 수행하는 required test가 live manifest에 채택된 경우에만 허용된다.

```text
scan universe live 재도출
forbidden claim live 재스캔
forbidden_overclaim_count > 0이면 fail-closed
```

Replay-only report validation은 보조 evidence일 뿐이며, replay-only 구성에서는 최종 report가 반드시 다음으로 내려가야 한다.

```text
required_gate_adopted=true
future_current_route_blocking_claimed=false
future_current_route_blocking_claim_denied_reason=replay_only_enforcement
```

Final docs sequencing decision:

```text
current_route_closure_mode=two_pass
future_current_route_blocking_scope=post_final_universe
```

첫 broad current route는 `pre_route_scan_universe`를 검증한다. Final report / closeout / walkthrough를 작성한 뒤 두 번째 broad current route를 실행하고, 최종 성공은 `post_final_current_route_rerun_success=true`일 때만 주장한다. 따라서 final docs overclaim도 current-route required gate가 검증하는 표면에 포함된다.

The two broad current-route commands are intentionally identical at the shell-command layer. Their semantic role is derived from phase state and must be recorded in each route result:

```text
first pass:
current_route_pass_sequence_id=first
current_route_scan_universe_mode=pre_route
current_route_scan_universe_mode_source=phase_state_derived
final_doc_scan_universe_enabled=false

second pass:
current_route_pass_sequence_id=second
current_route_scan_universe_mode=post_final
current_route_scan_universe_mode_source=phase_state_derived
final_doc_scan_universe_enabled=true
```

Codebase inspection read:

* Live required manifest: `Iris/_docs/round3/current_route_required_validations.json`
  * schema: `round3-current-route-required-validations-v1`
  * status: `PASS`
  * route: `current`
  * enforcement: `fail_closed`
  * current inspected denominator: `required_artifacts=93`, `required_tests=48`
* Current runner: `Iris/_docs/round3/round3_run_contract_tests.py`
  * taxonomy-selected current tests와 manifest `required_tests`를 union으로 실행한다.
  * `required_artifacts`의 JSON field checks를 fail-closed로 검증한다.
  * `--enforce-current-build-closure`는 `round3_active_core_closure.json`의 active core/tooling allowlist를 import guard로 사용한다.
* Active closure config: `Iris/_docs/round3/round3_active_core_closure.json`
  * current core modules: `12`
  * current-route allowed tooling modules: `export_dvf_3_3_lua_bridge` only
* Predecessor final report: `Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_claim_contract_closure/phase6/final_boundary_split_closure_report.json`
  * `claim_boundary_split_complete=true`
  * `required_gate_adopted=false`
  * `future_current_route_blocking_claimed=false`
  * `legacy_combined_route_pass_is_dvf_core_pass=false`
  * `dvf_pass_standalone_current_claim_allowed=false`
  * `protected_surface_changed_count=0`
  * `source_rendered_runtime_package_mutation_allowed=false`
* Predecessor claim authority doc: `docs/dvf_3_3_core_registry_boundary_claim_contract.md`
  * single claim meaning authority for DVF Core, Registry Authority, Registry Runtime Compatibility, Publish Boundary, and Legacy Combined Current Route claim classes.

---

## 2. Scope

이번 라운드는 governance-only required-gate adoption이다.

포함 범위:

* predecessor boundary claim contract closure 산출물의 live readpoint 재검증
* live `current_route_required_validations.json` denominator 재도출
* 채택할 required artifacts/tests의 stable field set 정의
* self-reference cycle 없는 required gate contract 작성
* forbidden overclaim scanner / negative fixture / allowed boundary fixture 작성
* current-route 실행 시점 live re-scan required test 작성
* claim scan universe mandatory surface set과 drift/reduction report 작성
* phase-tiered scan universe 작성: `pre_route_scan_universe`, `final_doc_scan_universe`
* pre-existing dirty target overlap guard 작성
* stable field host artifact / fixed phase / manifest-required eligibility mapping 작성
* pre-adoption loadability dry-run 작성
* live required manifest additive mutation
* manifest pre/post normalized diff report 작성
* phase0부터 post-route까지 protected source / rendered / Lua bridge / runtime chunk / package payload no-mutation proof
* post-route adopted required artifact VCS recensus
* focused runner / validator / unittest 작성
* two-pass broad current-route validation 수행
  * first pass: post-adoption / pre-final-doc route
  * second pass: final docs 작성 후 post-final route
* final closeout / claim boundary / ledger packet 작성
* canonical claim이 필요할 경우 independent review / owner seal / canonical seal 축을 별도로 분리

### Explicitly Out Of Scope

* 기존 boundary claim contract 의미 재정의
* Registry Authority PASS closure
* Registry Runtime Compatibility PASS closure
* Runtime Payload Consumer Compatibility closure
* Publish Boundary PASS closure
* Public Text Quality acceptance
* semantic quality acceptance
* package publication
* release / Workshop / B42 / deployment readiness
* manual in-game QA
* current route runner rewrite
* manifest physical split
* 기존 required tests / artifacts 제거, 재분류, predicate 의미 변경
* source facts / decisions / overlay support 변경
* rendered body text rewrite
* Lua bridge export 변경
* runtime chunk 변경
* package payload 변경
* broad `staging/**` unignore
* active core closure config나 tooling allowlist 확장

---

## 3. Non-Goals

이 계획은 다음을 해결하지 않는다.

* `DVF Core PASS` 자체를 새로 달성하지 않는다.
* `DVF PASS` 단독 current claim을 허용하지 않는다.
* `Legacy Combined Current Route PASS`를 `DVF Core PASS`로 읽지 않는다.
* `DVF Core PASS`를 runtime compatible, package safe, public accepted, release ready로 읽지 않는다.
* Registry / Runtime Compatibility / Publish Boundary 책임을 DVF Core closure로 재흡수하지 않는다.
* Runtime Payload Consumer Compatibility 문제나 Public Text Quality 문제를 DVF Core closure blocker로 라우팅하지 않는다.
* manifest adoption을 runtime writer authority로 취급하지 않는다.
* current-route PASS를 release readiness 또는 package readiness로 승격하지 않는다.
* staging evidence를 source / rendered / runtime / package current authority로 승격하지 않는다.
* independent review, owner seal, canonical seal을 machine adoption PASS와 혼동하지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 authority다.
* Iris는 100% Lua runtime module이며, 이번 Python 작업은 offline build/governance tooling이다.
* `docs/dvf_3_3_core_registry_boundary_claim_contract.md`가 claim meaning authority다.
* `docs/dvf_3_3_core_registry_boundary_claim_boundary.md`, ledger packet, closeout, walkthrough는 derivative summary로만 읽는다.
* Live manifest path는 `Iris/_docs/round3/current_route_required_validations.json`이다.
* Predecessor count `127 / 48 / 93 / 175` 등은 참고 readpoint이며 실행 시 live source에서 재도출한다.
* Live manifest의 기존 entries는 보존한다.
* Required gate adoption은 additive-only mutation으로 수행한다.
* Required gate adoption은 단일 live manifest mutation event로 수행한다.
* Current-route closure mode는 `two_pass`다.
* 새 required gate가 current-route에서 소비되려면 focused test가 current route runner에서 import 가능한 상태여야 한다.
* `round3_active_core_closure.json` mutation은 이번 라운드 범위가 아니다.
* 새 focused test가 active closure import guard 때문에 current route에서 실행될 수 없다면 adoption을 중단하고 별도 owner-decided tooling allowlist 라운드로 넘긴다.
* Pre-adoption loadability check는 live manifest mutation 전에 sandbox/override manifest 또는 dry-run으로 완료되어야 한다.
* `future_current_route_blocking_claimed=true`는 current-route 실행 시점 live re-scan required test가 채택되고 broad current route에서 소비될 때만 허용된다.
* `future_current_route_blocking_claimed=true`의 coverage scope는 `post_final_universe`다.
* Final report / closeout / walkthrough / owner-applied top-doc sync targets는 first pass current route의 `pre_route_scan_universe`에 넣지 않는다.
* Final docs는 final write 이후 second pass current route에서 `final_doc_scan_universe`로 live re-scan되어야 한다.
* Claim scan universe는 non-empty만으로 충분하지 않으며 mandatory minimum surface set을 만족해야 한다.
* Live manifest 또는 planned required target에 pre-existing dirty / untracked / ignored overlap이 있으면 fail-closed하거나 owner disposition을 요구한다.
* Manifest-required field는 첫 post-adoption route 실행 전에 host artifact에 존재하고 final value를 가져야 한다.
* Route result field는 manifest-required artifact predicate가 될 수 없고 final report 전용이다.
* Final no-mutation fields are final/post-route fields unless a post-final route rerun consumes them.
* Protected source / rendered / Lua bridge / runtime / package surfaces는 content hash 기준 no-mutation이어야 한다.
* Final `protected_surface_changed_count=0`은 phase0 baseline부터 post-route recapture까지의 전체 창 기준이다.
* `unknown`, `todo`, `tbd`, `unclear`는 통과 상태가 아니라 blocker다.
* Dirty worktree의 기존 변경은 되돌리지 않는다.
* Review metadata in this plan is provenance only. It is not an independent review gate, owner seal, or canonical seal claim.
* Plan-level PASS does not imply implementation evidence, independent review, owner seal, or canonical completion.
* Runner phase generation order must be declared and machine-recorded:

```text
runner --mode all generates phase artifacts in declared phase order
```

* Post-final report update is limited to an explicit machine-field set. Free-form final report text mutation after the second route is forbidden.

---

## 5. Repository Areas Affected

### Code

Planned offline governance tooling:

* `Iris/build/description/v2/tools/build/dvf_3_3_core_registry_boundary_required_gate_adoption.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_core_registry_boundary_required_gate_adoption.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_core_registry_boundary_required_gate_adoption.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_core_registry_boundary_required_gate_adoption.py`

Read-only consumed code/config:

* `Iris/_docs/round3/round3_run_contract_tests.py`
* `Iris/_docs/round3/round3_active_core_closure.json`
* `Iris/build/description/v2/tools/build/dvf_3_3_core_registry_boundary_claim_contract_closure.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_core_registry_boundary_claim_contract_closure.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_core_registry_boundary_claim_contract_closure.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_core_registry_boundary_claim_contract_closure.py`

No runtime Lua code change is planned.

### Docs

Direct plan artifact:

* `docs/dvf_3_3_core_registry_boundary_required_gate_adoption_plan.md`

Planned docs:

* `docs/dvf_3_3_core_registry_boundary_required_gate_adoption_contract.md`
* `docs/dvf_3_3_core_registry_boundary_required_gate_adoption_claim_boundary.md`
* `docs/dvf_3_3_core_registry_boundary_required_gate_adoption_ledger_packet.md`
* `docs/dvf_3_3_core_registry_boundary_required_gate_adoption_closeout.md`
* optional `docs/dvf_3_3_core_registry_boundary_required_gate_adoption_walkthrough.md`

Read-only context docs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/dvf_3_3_core_registry_boundary_claim_contract.md`
* `docs/dvf_3_3_core_registry_boundary_claim_boundary.md`
* `docs/dvf_3_3_core_registry_boundary_claim_contract_ledger_packet.md`
* `docs/dvf_3_3_core_registry_boundary_claim_contract_closure_closeout.md`
* `docs/dvf_3_3_core_registry_boundary_claim_contract_closure_walkthrough.md`

Optional additive top-doc sync candidates, owner-applied only:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

### Config

Planned mutation:

* `Iris/_docs/round3/current_route_required_validations.json`

Possible narrow visibility update if generated surfaces are ignored:

* `.gitignore`

Read-only config:

* `Iris/_docs/round3/round3_active_core_closure.json`
* `Iris/_docs/round3/round3_test_taxonomy.json`

### Generated Artifacts

Planned evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_required_gate_adoption/`

Expected generated artifacts include:

* `phase0_adoption_preflight_report.json`
* `phase0_predecessor_contract_consumption_report.json`
* `phase0_predecessor_rerun_root_override_report.json`
* `phase0_live_denominator_report.json`
* `phase0_vcs_census_report.json`
* `phase0_dirty_target_overlap_report.json`
* `phase0_gitignore_allowlist_diff_report.json`
* `phase0_roadmap_review_provenance_binding_report.json`
* `phase0_phase_execution_mapping_report.json`
* `phase1_required_gate_contract_schema.json`
* `phase1_required_gate_contract_definition_report.json`
* `phase1_per_artifact_adoption_disposition_queue.json`
* `phase1_field_host_phase_mapping.json`
* `phase1_predecessor_field_semantic_mapping_report.json`
* `phase2_claim_surface_scan_report.json`
* `phase2_scan_universe_derivation_report.json`
* `phase2_scan_universe_minimum_coverage_report.json`
* `phase2_pre_route_scan_universe_manifest.json`
* `phase2_final_doc_scan_universe_manifest.json`
* `phase2_negative_fixture_report.json`
* `phase2_allowed_boundary_fixture_report.json`
* `phase2_gate_tooling_report.json`
* `phase2_pre_adoption_loadability_report.json`
* `phase3_required_manifest_adoption_report.json`
* `phase3_required_manifest_diff_summary.json`
* `phase3_manifest_adoption_diff_report.json`
* `phase3_bootstrap_sufficiency_report.json`
* `phase4_protected_surface_no_mutation_report.json`
* `phase4_required_gate_vcs_preservation_report.json`
* `phase4_source_rendered_lua_runtime_package_hash_report.json`
* `phase5_post_route_protected_surface_recapture_report.json`
* `phase5_post_route_required_artifact_vcs_recensus_report.json`
* `phase5_current_route_required_gate_validation_result.json`
* `phase5_current_route_command_matrix_report.json`
* `phase5_pre_final_current_route_result.json`
* `phase5_current_route_failure_classification_report.json`, only on failure
* `phase6_final_doc_scan_report.json`
* `phase6_post_final_current_route_result.json`
* `phase6_post_final_protected_surface_recapture_report.json`
* `phase6_post_final_required_artifact_vcs_recensus_report.json`
* `phase6_post_final_report_update_contract.json`
* `phase6_plan_self_fingerprint_report.json`
* `final_boundary_required_gate_adoption_report.json`

---

## 6. Planned Changes

### Change 1

Purpose:

Establish a live preflight readpoint before any manifest mutation.

Files:

* read: `Iris/_docs/round3/current_route_required_validations.json`
* read: `Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_claim_contract_closure/phase6/final_boundary_split_closure_report.json`
* write: `Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_required_gate_adoption/phase0_*`

Implementation Notes:

* Recompute live required artifact/test counts from the live manifest.
* Emit generator-phase binding before phase execution proceeds. Required invariant:

```text
runner --mode all generates phase0~phaseN reports in declared phase order
phase_execution_mapping_status=PASS
undeclared_phase_output_count=0
phase_order_violation_count=0
```

* Verify predecessor final report fields directly:
  * `claim_boundary_split_complete=true`
  * `required_gate_adopted=false`
  * `future_current_route_blocking_claimed=false`
  * `legacy_combined_route_pass_is_dvf_core_pass=false`
  * `dvf_pass_standalone_current_claim_allowed=false`
  * protected surface no-mutation fields remain non-mutating.
* If predecessor inventory freshness is rederived, it must run in an isolated output root using:

```powershell
$env:DVF_LEGACY_COMBINED_ROUTE_AXIS_INVENTORY_ROOT = "Iris\build\description\v2\staging\dvf_3_3_core_registry_boundary_required_gate_adoption\phase0\predecessor_rerun"
```

* The default predecessor staging root must not receive freshness rerun output. Required observation fields:

```text
predecessor_rerun_root_override_supported=true
predecessor_rerun_output_root_observed=Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_required_gate_adoption/phase0/predecessor_rerun/
predecessor_default_staging_root_write_count=0
```

* If the predecessor generator ignores the override env var, closeout is blocked rather than falling back to the default predecessor staging root.
* Record predecessor docs and staging artifact hashes.
* Capture protected surface baseline before any generated report side effects.
* Record VCS state for planned docs, tool/test files, manifest, and evidence root.
* Add target dirty overlap guard before any mutation. Required fields:

```text
pre_existing_dirty_target_overlap_count=0
pre_existing_dirty_live_manifest=false
pre_existing_dirty_planned_required_artifact_count=0
pre_existing_untracked_required_target_count=0
pre_existing_ignored_required_target_count=0
owner_disposition_required_for_dirty_overlap=false
```

* Live manifest pre-existing dirty state is fail-closed.
* Planned required artifact path dirty / untracked / ignored state is fail-closed unless an owner disposition explicitly downgrades the artifact to non-required candidate evidence before adoption.
* New files under this round's evidence root are allowed during generation, but they must become Git-visible before being adopted as required artifacts.
* `.gitignore` mutation, if needed, must be an exact path or exact round-root negative exception. Broad `staging/**` unignore remains forbidden.
* If exact round-root `.gitignore` exception is used, final report must record:

```text
broad_staging_unignore=false
round_root_exception_only=true
gitignore_expected_round_local_rule_count=<derived_expected_count>
gitignore_added_rule_count=<derived_count>
gitignore_broad_unignore_rule_count=0
gitignore_round_local_rule_count=<derived_count>
```

* `.gitignore` allowance cannot be accepted by visual diff alone. Phase0 must emit an expected-rule manifest that enumerates every planned rule and computes:

```text
gitignore_expected_rule_manifest_status=PASS
gitignore_expected_round_local_rule_count=<derived_expected_count>
gitignore_added_rule_count=<same_count>
gitignore_round_local_rule_count=<same_count>
gitignore_added_rule_count_matches_expected=true
gitignore_broad_unignore_rule_count=0
```

* Any mismatch between expected and observed `.gitignore` count is fail-closed before live manifest adoption.

Validation:

* JSON schema/readability checks.
* `phase0_phase_execution_mapping_report.json` must bind runner mode, declared phase order, and generated report paths.
* `phase0_predecessor_rerun_root_override_report.json` must prove isolated rerun root support before predecessor freshness evidence is consumed.
* Live denominator report must mark counts as derived, not hard-coded.
* Any missing/stale predecessor required field blocks Change 2.
* `phase0_dirty_target_overlap_report.json` must satisfy all zero/false guard fields before Change 2.
* `.gitignore` diff report must show `gitignore_broad_unignore_rule_count=0`.
* `.gitignore` expected-rule manifest must show `gitignore_added_rule_count_matches_expected=true`.

---

### Change 2

Purpose:

Define the required gate contract without creating a self-referential manifest cycle.

Files:

* write: `docs/dvf_3_3_core_registry_boundary_required_gate_adoption_contract.md`
* write: `docs/dvf_3_3_core_registry_boundary_required_gate_adoption_claim_boundary.md`
* write: `docs/dvf_3_3_core_registry_boundary_required_gate_adoption_ledger_packet.md`
* write: `Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_required_gate_adoption/phase1_*`

Implementation Notes:

* Treat `docs/dvf_3_3_core_registry_boundary_claim_contract.md` as the existing claim meaning authority.
* The adoption contract defines which stable fields are required by current route.
* Required manifest checks must avoid requiring the final report's own complete claim before it can be generated.
* Candidate stable fields:

```text
required_gate_adopted=true
future_current_route_blocking_claimed=true
legacy_combined_route_pass_is_dvf_core_pass=false
dvf_pass_standalone_current_claim_allowed=false
protected_surface_changed_count=0
source_rendered_lua_runtime_package_mutation=false
predecessor_claim_contract_redefined=false
required_manifest_adoption_mode=additive_only
removed_required_artifact_count=0
removed_required_test_count=0
predicate_meaning_change_count=0
existing_entry_reclassified_count=0
```

* Per-file disposition chooses `presence`, `hash`, or `field` level adoption.
* Final report self-completion fields are checked by focused validator `--require-complete`, not by manifest self-reference.
* Add a field-host mapping table to the contract artifacts. Required columns:

```text
field
host_artifact
fixed_phase
manifest_required_allowed
```

* Minimum mapping rules:

```text
adoption fields -> phase3 adoption report -> manifest_required_allowed=true
scanner live-enforcement fields -> phase2/phase3 live scan reports -> manifest_required_allowed=true
route result fields -> phase5/final reports -> manifest_required_allowed=false
canonical / owner / independent review fields -> final/canonical reports -> manifest_required_allowed=false
```

No-mutation field host rules:

```text
pre_route_protected_surface_changed_count
host_artifact=phase4_protected_surface_no_mutation_report.json
fixed_phase=phase4
manifest_required_allowed=true

post_route_protected_surface_changed_count
host_artifact=phase5_post_route_protected_surface_recapture_report.json
fixed_phase=phase5_after_first_route
manifest_required_allowed=false

post_final_protected_surface_changed_count
host_artifact=phase6_post_final_protected_surface_recapture_report.json
fixed_phase=phase6_after_second_route
manifest_required_allowed=false

protected_surface_changed_count
host_artifact=final_boundary_required_gate_adoption_report.json
fixed_phase=final
manifest_required_allowed=false

source_rendered_lua_runtime_package_mutation
host_artifact=final_boundary_required_gate_adoption_report.json
fixed_phase=final
manifest_required_allowed=false
```

Because this plan selects two-pass current-route closure, final docs and final no-mutation summary are covered by the second route's live re-scan, not by first-route manifest artifact predicates.

* First post-adoption route cannot start until every `manifest_required_allowed=true` artifact exists and has its final phase value.
* Add predecessor field semantic mapping rather than renaming predecessor fields in place. Required mapping:

```text
predecessor.source_rendered_runtime_package_mutation_allowed=false
=> this_round.source_rendered_lua_runtime_package_mutation=false
```

* The mapping report must also record that predecessor field names are consumed as predecessor-origin fields and this round's names are target semantic fields.

Validation:

* Stable field schema validation.
* Per-artifact disposition validation.
* Self-reference cycle count must be `0`.
* `phase1_field_host_phase_mapping.json` must have no manifest-required route result fields.
* `phase1_field_host_phase_mapping.json` must mark final no-mutation summary fields as `manifest_required_allowed=false`.
* `phase1_predecessor_field_semantic_mapping_report.json` must bind predecessor field names to target semantic fields without mutating predecessor artifacts.

---

### Change 3

Purpose:

Implement claim misuse scanner and fixtures that fail closed for forbidden current-route overclaims.

Files:

* write: `Iris/build/description/v2/tools/build/dvf_3_3_core_registry_boundary_required_gate_adoption.py`
* write: `Iris/build/description/v2/tools/build/run_dvf_3_3_core_registry_boundary_required_gate_adoption.py`
* write: `Iris/build/description/v2/tools/build/validate_dvf_3_3_core_registry_boundary_required_gate_adoption.py`
* write: `Iris/build/description/v2/tests/test_dvf_3_3_core_registry_boundary_required_gate_adoption.py`
* write: `Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_required_gate_adoption/phase2_*`

Implementation Notes:

* Follow the existing runner/validator pattern from `dvf_3_3_core_registry_boundary_claim_contract_closure`.
* Scanner must fail closed for:
  * standalone current `DVF PASS`
  * `Legacy Combined Current Route PASS = DVF Core PASS`
  * `DVF Core PASS = runtime compatible`
  * `DVF Core PASS = package safe`
  * `DVF Core PASS = public accepted`
  * `DVF Core PASS = release ready`
  * Registry Authority / Runtime Compatibility / Publish Boundary responsibility attached to DVF Core
  * Runtime Payload Consumer Compatibility or Public Text Quality routed to DVF Core closure
* Scanner must distinguish normal boundary explanations, historical quotes, negated examples, and forbidden examples.
* At least one required test must perform live re-scan at current-route execution time. It must not only replay a previously generated `forbidden_overclaim_count=0` report.
* Required test behavior:

```text
current_route 실행 시점마다 scan universe live 재도출
forbidden claim live 재스캔
forbidden_overclaim_count > 0이면 fail-closed
```

* Artifact replay validation is allowed only as a supporting predicate.
* If implementation falls back to replay-only validation, final report must set:

```text
future_current_route_blocking_claimed=false
future_current_route_blocking_claim_denied_reason=replay_only_enforcement
```

* Scan universe must be derived, non-empty, phase-tiered, and minimum-coverage complete.
* `pre_route_scan_universe` covers surfaces that exist before the first post-adoption current route:

```text
live current_route_required_validations.json newly adopted gate entries
this round adoption contract / claim boundary / ledger packet
phase0~phase3 manifest-required artifacts
predecessor boundary claim contract closure final report
predecessor claim contract / claim boundary / ledger docs
existing DVF Core / Registry / Publish Boundary claim-bearing current-route governance docs
manifest-required artifacts classified as claim-bearing docs/evidence
```

* `final_doc_scan_universe` covers surfaces that are written after the first route:

```text
final_boundary_required_gate_adoption_report.json
docs/dvf_3_3_core_registry_boundary_required_gate_adoption_closeout.md
docs/dvf_3_3_core_registry_boundary_required_gate_adoption_walkthrough.md when generated
owner-applied top-doc sync targets when applied
phase6 final / post-final evidence reports
```

* First broad current route must scan `pre_route_scan_universe`.
* Second broad current route must scan `pre_route_scan_universe + final_doc_scan_universe`.
* Final docs missing before first route is not a failure; final docs missing before second route is fail-closed.
* This plan does not select the validator-only final docs option. Final docs overclaim is enforced by the second current-route pass.
* Required scan universe fields:

```text
claim_scan_minimum_universe_satisfied=true
claim_scan_universe_derivation_mode=explicit_rule_derived
claim_scan_required_surface_missing_count=0
claim_scan_excluded_path_without_reason_count=0
predecessor_scan_universe_reference=predecessor_claim_contract_closure_rule_v1
scan_universe_drift_recorded=true
scan_universe_reduction_without_reason_count=0
pre_route_scan_universe_missing_count=0
final_doc_scan_universe_missing_count=0
```

* Out-of-universe paths must be counted with exclusion reasons.
* Allowed boundary fixtures must include both English and Korean claim sentences so Korean governance docs are covered.
* Scanner exceptions cannot be accepted by prose. Every accepted exception must be represented as a hash-bound row with:

```text
exception_scope
source_path
line_hash
claim_text_hash
owner_adjudication_scope
owner_adjudication_does_not_generalize=true
```

* This round may carry only the already bounded predecessor non-claim false-positive adjudication. Any other scanner exception blocks adoption:

```text
unknown_claim_scanner_exception_count=0
hash_bound_false_positive_exception_count<=1
unhash_bound_scanner_exception_count=0
scanner_exception_prose_only_count=0
```

Validation:

* Focused unittest covers negative fixture failure and allowed statement non-failure.
* Validator rejects tampered report with forbidden overclaim count > 0.
* Scan universe count must be `> 0` and `claim_scan_minimum_universe_satisfied=true`.
* Live re-scan test must fail when a forbidden claim is injected into an in-universe temporary surface.
* Second-pass live re-scan must fail if final docs contain a forbidden claim.
* Validator rejects any scanner exception that is not hash-bound or is outside the single bounded predecessor false-positive scope.

---

### Change 4

Purpose:

Adopt the new required gate into the live current-route manifest by additive-only mutation.

Files:

* mutate: `Iris/_docs/round3/current_route_required_validations.json`
* write: `Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_required_gate_adoption/phase3_*`

Implementation Notes:

* Add new required artifacts/tests only.
* Do not remove existing required artifacts/tests.
* Do not rename, reclassify, or change predicate meaning of existing entries.
* Change 4 cannot start until `pre_adoption_loadability_passed=true`.
* Pre-adoption loadability must run with live manifest unchanged, using sandbox/override manifest or dry-run selection to prove that the new focused test imports and executes under `--enforce-current-build-closure`.
* Pre-adoption loadability must include an import-closure probe for the new focused test and adoption tooling:

```text
current_route_import_closure_probe_status=PASS
current_route_import_closure_probe_live_manifest_mutated=false
tools_build_package_import_attempt_count=0
bare_tool_module_import_used=true
build_closure_blocker_triggered_for_forbidden_fixture=true
```

* The focused test must follow the existing closure-test pattern: insert `Iris/build/description/v2/tools/build` on `sys.path` and import the round module as a bare module name. Importing `tools.build.<round_module>` from a current-route required test is forbidden because the current-route build-closure blocker intercepts that package prefix.
* If pre-adoption loadability fails, do not mutate live manifest. Emit blocked-state report:

```text
required_gate_adopted=false
future_current_route_blocking_claimed=false
pre_adoption_loadability_passed=false
blocked_reason=pre_adoption_loadability_failed
```

* Use a single writer phase for live manifest mutation.
* Preserve schema version `round3-current-route-required-validations-v1`.
* Add a round-specific role, expected shape:

```text
dvf_3_3_core_registry_boundary_required_gate_adoption_required_validation
```

* Required test entry should point to the focused unittest method(s) that prove gate behavior and manifest adoption.
* Required artifact entries should point to stable phase reports, not volatile final self-reference fields.
* Required test entry must include the live re-scan enforcement test. Replay-only tests cannot be the sole required test for this round.
* Bootstrap sufficiency must be proven before the first post-adoption route:

```text
all_manifest_required_artifacts_exist_before_post_adoption_route=true
all_manifest_required_artifacts_have_final_values_before_post_adoption_route=true
manifest_required_route_result_field_count=0
self_reference_cycle_count=0
```

Validation:

* `added_entries_count > 0`
* `removed_required_artifact_count=0`
* `removed_required_test_count=0`
* `modified_existing_entries=0`
* `existing_entry_reclassified_count=0`
* `predicate_meaning_change_count=0`
* live manifest JSON validity check.
* pre/post normalized diff report.
* `phase3_bootstrap_sufficiency_report.json` PASS before broad current route.
* `phase3_current_route_import_closure_probe_report.json` PASS before live manifest mutation.

---

### Change 5

Purpose:

Prove this round is governance-only and does not mutate protected runtime/source surfaces.

Files:

* read/hash: source facts, decisions, overlay support, rendered output, Lua bridge output, runtime chunks, package payload surfaces
* write: `Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_required_gate_adoption/phase4_*`

Implementation Notes:

* Open the no-mutation proof window at phase0 baseline and keep it open through post-route recapture.
* Separate generated staging evidence churn from protected source/runtime/package mutation.
* Required artifacts must be Git-visible when adopted.
* Broad staging unignore remains forbidden.
* Phase4 records pre-route state, not final state. Final no-mutation claim is not allowed until Change 6 post-route recapture passes.

Validation:

```text
pre_route_protected_surface_changed_count=0
required_gate_artifacts_present=true
no_broad_staging_unignore=true
pre_route_required_artifact_dirty_count=0
pre_route_required_artifact_untracked_count=0
pre_route_required_artifact_ignored_count=0
```

`protected_surface_changed_count` and `source_rendered_lua_runtime_package_mutation` are final summary fields. They are not phase4 manifest-required fields.

---

### Change 6

Purpose:

Run focused validation and the first broad current-route validation after live manifest adoption.

Files:

* read: `Iris/_docs/round3/round3_run_contract_tests.py`
* read: `Iris/_docs/round3/current_route_required_validations.json`
* write: `Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_required_gate_adoption/phase5_*`

Implementation Notes:

* Focused runner/validator/unittest must pass first.
* First broad current route must then pass with current build closure enforcement.
* The first broad current route must consume the live re-scan required test over `pre_route_scan_universe`.
* The first broad current-route result must identify the phase-derived pass mode:

```text
current_route_pass_sequence_id=first
current_route_scan_universe_mode=pre_route
current_route_scan_universe_mode_source=phase_state_derived
final_doc_scan_universe_enabled=false
```

* The first broad current route is necessary but not sufficient for `machine_required_gate_adoption_complete=true`.
* If the new required test cannot be loaded under the current closure import guard during pre-adoption dry-run, stop before live manifest mutation and record:

```text
required_gate_adopted=false
future_current_route_blocking_claimed=false
new_tooling_allowlist_expansion_required=true
allowlist_expansion_deferred_to_separate_owner_decided_round=true
```

* If the first post-adoption broad current route fails due loadability despite preflight, execute an automatic revert branch for only this round's manifest entries, then rerun current route to restore baseline. Required failure fields:

```text
post_adoption_failure_classification=<code>
auto_revert_executed_on_loadability_failure=true/false
post_revert_current_route_restored=true/false
```

* After first broad current route, recapture protected surfaces and adopted required artifact VCS state. These phase5 fields are post-first-route fields, not final summary fields:

```text
post_route_protected_surface_changed_count=0
post_route_required_artifact_dirty_count=0
post_route_required_artifact_untracked_count=0
post_route_required_artifact_ignored_count=0
pre_restore_protected_surface_changed_count=0
```

Validation:

* focused runner PASS
* focused validator `--require-complete` PASS
* focused unittest PASS
* first broad current route PASS
* first route result records `current_route_pass_sequence_id=first`
* first route result records `current_route_scan_universe_mode=pre_route`
* first route result records `final_doc_scan_universe_enabled=false`
* closure_enforced true
* required gate artifact consumed
* required gate test consumed
* pre-route live re-scan required test consumed
* post-route protected surface recapture PASS
* post-route required artifact VCS recensus PASS

---

### Change 7

Purpose:

Write final closeout, then run the second broad current-route validation over final docs.

Files:

* write: `Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_required_gate_adoption/final_boundary_required_gate_adoption_report.json`
* write: `docs/dvf_3_3_core_registry_boundary_required_gate_adoption_closeout.md`
* optional write: `docs/dvf_3_3_core_registry_boundary_required_gate_adoption_walkthrough.md`

Implementation Notes:

* Final report must bind manifest adoption diff, negative fixture report, protected no-mutation report, first current-route result, and post-final current-route result.
* Final report must bind live re-scan enforcement evidence separately from replayed artifact evidence.
* Final report / closeout / walkthrough must be written before the second broad current route.
* Second broad current route must live re-scan `pre_route_scan_universe + final_doc_scan_universe`.
* The second broad current-route result must identify the phase-derived pass mode:

```text
current_route_pass_sequence_id=second
current_route_scan_universe_mode=post_final
current_route_scan_universe_mode_source=phase_state_derived
final_doc_scan_universe_enabled=true
```

* If live re-scan was not consumed by the second broad current route, `future_current_route_blocking_claimed` must be `false`.
* Final no-mutation summary fields are fixed after the second route and post-final recapture:

```text
post_final_current_route_rerun_success=true
post_final_protected_surface_changed_count=0
protected_surface_changed_count=0
source_rendered_lua_runtime_package_mutation=false
```

* The final report may be updated after the second route only for the enumerated machine fields below. Free-form prose mutation after second route is forbidden:

```text
post_final_report_update_allowed_fields=[
  "post_final_current_route_rerun_success",
  "post_final_live_rescan_required_test_consumed",
  "post_final_protected_surface_changed_count",
  "post_final_required_artifact_dirty_count",
  "post_final_required_artifact_untracked_count",
  "post_final_required_artifact_ignored_count",
  "post_final_report_update_contract_status",
  "post_final_report_freeform_text_mutation_detected",
  "post_final_report_updated_field_count",
  "post_final_report_updated_field_set_matches_allowlist",
  "protected_surface_changed_count",
  "source_rendered_lua_runtime_package_mutation",
  "machine_required_gate_adoption_complete",
  "blocked",
  "blocked_reason",
  "blocked_phase"
]
post_final_report_freeform_text_mutation_allowed=false
post_final_report_freeform_text_mutation_detected=false
post_final_report_updated_field_count=<derived_count>
post_final_report_updated_field_set_matches_allowlist=true
```

* Final report must explicitly preserve non-claims:

```text
machine_required_gate_adoption_complete=true
canonical_complete_claimed=false
independent_review_claimed=false
owner_seal_claimed=false
canonical_seal_allowed=false
independent_review_gate_status=not_claimed
owner_seal_status=not_claimed
canonical_seal_status=not_claimed
registry_authority_pass_claimed=false
registry_runtime_compatibility_pass_claimed=false
publish_boundary_pass_claimed=false
release_readiness_claimed=false
manual_qa_claimed=false
runtime_payload_consumer_compatibility_closed=false
public_text_quality_acceptance_claimed=false
```

* If a known predecessor false-positive is owner-adjudicated by adopting this plan, the final report must bind the scope narrowly:

```text
owner_adjudication_scope=single_bounded_predecessor_non_claim_false_positive_row_only
owner_adjudication_does_not_generalize=true
```

* That adjudication cannot authorize suppress removal, claim vocabulary expansion, broad scanner exceptions, or any additional predecessor false-positive rows.
* Independent review / owner seal / canonical seal are separate axis. If not performed, final report must say `not_claimed`.
* Top-doc sync, if needed, should be additive and owner-applied; otherwise emit draft only.
* Add `legacy_combined_governance_route_preserved=true` to final report.
* Add final docs enforcement fields:

```text
current_route_closure_mode=two_pass
future_current_route_blocking_scope=post_final_universe
final_docs_overclaim_checked_by=second_current_route_live_rescan
first_current_route_pass_sequence_id=first
first_current_route_scan_universe_mode=pre_route
first_current_route_scan_universe_mode_source=phase_state_derived
first_final_doc_scan_universe_enabled=false
post_final_current_route_pass_sequence_id=second
post_final_current_route_scan_universe_mode=post_final
post_final_current_route_scan_universe_mode_source=phase_state_derived
post_final_doc_scan_universe_enabled=true
post_final_current_route_rerun_success=true
```

* Add implementation absorption fields:

```text
plan_level=PASS
execution_artifacts_present=true
implementation_evidence_status=produced
independent_review_gate=BLOCKED
phase_execution_mapping_status=PASS
post_final_report_update_contract_status=PASS
```

`implementation_evidence=not_yet_produced until execution artifacts exist` is a planning/review-stage statement only. It must not be copied into the execution final report after artifacts have been generated.

* Ledger packet must bind roadmap/review provenance through repo-durable copied path and SHA256, not only volatile attachment paths.
* Ledger packet must record the plan self-fingerprint at freeze time.
* If owner disposition downgrades a dirty planned required artifact to non-required candidate evidence, final report must name the replacement required host artifact and validate equivalent field coverage.
* Final report must reserve blocked-state fields in schema even on success:

```text
blocked=false
blocked_reason=null
blocked_phase=null
```

* The final validator must fail unless all execution-risk closure gates below are true:

```text
gitignore_added_rule_count_matches_expected=true
gitignore_broad_unignore_rule_count=0
pre_existing_dirty_target_overlap_count=0
pre_existing_dirty_live_manifest=false
unknown_claim_scanner_exception_count=0
unhash_bound_scanner_exception_count=0
hash_bound_false_positive_exception_count<=1
current_route_import_closure_probe_status=PASS
post_adoption_current_route_rerun_success=true
post_final_current_route_rerun_success=true
post_final_report_freeform_text_mutation_detected=false
post_final_report_updated_field_set_matches_allowlist=true
live_manifest_rollback_required=false
```

Validation:

* final require-complete validator PASS.
* no forbidden overclaim in final docs.
* second broad current route PASS.
* second route result records `current_route_pass_sequence_id=second`
* second route result records `current_route_scan_universe_mode=post_final`
* second route result records `final_doc_scan_universe_enabled=true`
* post-final live re-scan required test consumed.
* post-final report update contract PASS.
* post-final report update field set matches allowlist.
* post-final free-form text mutation detection is false.
* no top-doc mutation unless owner-applied state is present.
* final validator hard-fails if any execution-risk closure gate is missing, false, or weaker than the exact expected value.

---

## 7. Validation Plan

### Automated Validation

Planned exact commands:

```powershell
uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_core_registry_boundary_required_gate_adoption.py --mode all
uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_core_registry_boundary_required_gate_adoption.py --require-complete
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_core_registry_boundary_required_gate_adoption.py"
uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

The two identical current-route commands are intentional:

```text
first route = post-adoption / pre-final-doc universe
  current_route_pass_sequence_id=first
  current_route_scan_universe_mode=pre_route
  current_route_scan_universe_mode_source=phase_state_derived
  final_doc_scan_universe_enabled=false
second route = post-final-doc universe
  current_route_pass_sequence_id=second
  current_route_scan_universe_mode=post_final
  current_route_scan_universe_mode_source=phase_state_derived
  final_doc_scan_universe_enabled=true
```

Additional automated checks:

* live manifest denominator derivation
* predecessor contract field check
* predecessor field semantic mapping check
* phase execution mapping validation
* pre-existing dirty target overlap guard
* pre-adoption loadability dry-run with live manifest unchanged
* required artifact/test added-entry diff
* required artifact/test removed-entry count
* predicate meaning change count
* field-host-phase mapping validation
* bootstrap sufficiency validation before first post-adoption route
* scan universe derivation
* scan universe minimum coverage validation
* scan universe drift/reduction report
* pre-route scan universe validation
* final-doc scan universe validation
* first/second route pass sequence and scan universe mode validation
* current-route execution-time live re-scan validation
* negative fixture execution
* allowed boundary fixture execution
* Korean allowed/forbidden boundary fixture execution
* required artifact field checks
* protected no-mutation hash comparison from phase0 baseline through post-route recapture
* post-route adopted required artifact VCS recensus
* post-final current-route rerun validation
* post-final protected-surface recapture
* post-final final-doc overclaim live re-scan validation
* post-final report update allowed-field validation
* post-final report updated-field count and allowlist-set validation
* post-final final-report free-form text mutation detection
* post-adoption loadability failure auto-revert and route restoration validation, only if that failure path occurs
* `.gitignore` narrow visibility check if new generated evidence would otherwise be ignored
* `.gitignore` expected-rule manifest and count equality validation
* current-route import-closure probe for the new focused test and adoption tooling
* scanner exception hash-binding validation
* manifest diff axis check that new entries do not assign Registry / Publish responsibility to `dvf_core`
* final report non-claim field validation

### Manual Validation

* Review required gate contract for self-reference risks.
* Review scanner false-positive/false-negative fixture matrix.
* Review scan universe mandatory surface list and exclusion reasons.
* Review field-host-phase mapping for bootstrap cycles.
* Review generator-phase binding.
* Review post-final report update allowed-field list.
* Review manifest diff before accepting live manifest mutation.
* Review closeout wording for overclaim avoidance.
* Review optional top-doc sync draft before owner application.

### Validation Limits

This plan will not perform:

* no multiplayer validation
* no deployment validation
* no long-session runtime validation
* no in-game manual QA
* no package publication validation
* no Workshop readiness validation
* no public text quality validation
* no Registry Runtime Compatibility closure
* no Runtime Payload Consumer Compatibility closure
* no semantic quality acceptance
* no source/rendered/runtime regeneration parity beyond no-mutation proof
* no full clean-checkout required-evidence reproducibility
* no full historical byte reproducibility
* no external ecosystem compatibility sweep
* no semantic overclaim detection beyond explicit lexical/token claim classes

Lua syntax validation, if run, is a no-runtime-mutation sanity check only. It is not runtime compatibility, public text acceptance, or release readiness evidence.

---

## 8. Risk Surface Touch

### Authority Surface

Touched, governance-only.

The live current-route required-validation manifest is modified additively. New required artifacts/tests become current-route governance requirements, but they do not become source, rendered, runtime, Lua bridge, package, release, or public text authority.

The authority claim for `future_current_route_blocking_claimed=true` is limited to the configured live re-scan universe and lexical/token claim classes. It is not a general semantic overclaim detector.

### Runtime Behavior Surface

None.

Runtime Lua, Browser / Wiki / Tooltip behavior, runtime chunks, and Lua bridge output are not changed.

### Compatibility Surface

No direct runtime compatibility change.

Governance compatibility becomes stricter because future current-route claim misuse should fail closed.

### Sealed Artifact Surface

Touched.

New required gate adoption evidence is added under a new staging evidence root. Predecessor sealed artifacts are consumed read-only.

### Public-Facing Output Surface

None.

No public Iris text, tooltip text, wiki text, release note, Workshop page, or package copy is changed.

---

## 9. Risk Analysis

### Architecture Risk

* Required-gate adoption could accidentally redefine the predecessor claim contract.
* DVF Core could reabsorb Registry Authority, Runtime Compatibility, or Publish Boundary responsibility.
* Bare `DVF PASS` could reenter as a current claim.
* Required test could replay old reports rather than scanning future current-route claim surfaces.
* Mitigation: cite predecessor claim contract as meaning authority, add negative fixtures, require axis-qualified claim fields, and require current-route execution-time live re-scan before claiming future blocking.

### Runtime Risk

* Runtime risk is low because no runtime surface is intended.
* Main risk is accidental protected surface mutation while running generation/validation.
* Mitigation: phase0 baseline, post-route recapture, pre-restore capture, and fail-closed no-mutation field checks.

### Compatibility Risk

* Direct compatibility risk is low.
* Future current-route validations may fail earlier on forbidden claim language.
* Mitigation: allowed boundary fixture matrix for negated, quoted, historical, explanatory, and Korean-language statements.

### Regression Risk

* Live manifest mutation could remove or alter existing required entries.
* New focused test could be invisible to current route due active closure import guard.
* Self-referential final report field could make current route recursive.
* Scanner could pass vacuously with an empty universe.
* Scanner could pass with a non-empty but under-covered universe.
* Live manifest could already be dirty before adoption, weakening additive-only proof.
* Post-route side effects could dirty required artifacts after pre-route VCS checks pass.
* Final docs could be written after first route and escape current-route live re-scan if second route is skipped.
* Generated artifacts could remain ignored after manifest adoption.
* Mitigation: normalized manifest diff, pre-adoption loadability dry-run, dirty target overlap guard, stable-field host/phase mapping, phase-tiered scan minimum universe coverage, VCS visibility report, post-route recensus, and two-pass broad current-route rerun.

---

## 10. Rollback Plan

Rollback before canonical seal:

1. Remove only this round's additive entries from `Iris/_docs/round3/current_route_required_validations.json`.
2. Remove or supersede this round's runner / validator / focused unittest.
3. Remove or supersede this round's docs.
4. Remove or supersede this round's staging evidence root.
5. Remove only this round's `.gitignore` narrow allowlist entries, if added.
6. Re-run broad current route.

If `.gitignore` allowlist entries are reverted, rollback evidence must record:

```text
gitignore_added_rule_count=<original_round_count>
gitignore_reverted_rule_count=<same_count>
gitignore_broad_unignore_rule_count=0
gitignore_round_local_rule_count=0 after rollback
```

Automatic revert branch:

* If post-adoption route failure is classified as `loadability_failure`, revert only this round's manifest entries immediately.
* After revert, rerun:

```powershell
uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
```

* Required restoration fields:

```text
auto_revert_executed_on_loadability_failure=true
post_revert_current_route_restored=true
post_revert_removed_only_this_round_entries=true
post_revert_protected_surface_changed_count=0
```

Post-final failure branch:

* If second route fails because final docs contain forbidden claims, do not revert manifest automatically.
* Fix or supersede the final docs, rerun focused validator, then rerun second current route.
* If second route cannot be made PASS, final state is blocked:

```text
machine_required_gate_adoption_complete=false
post_final_current_route_rerun_success=false
blocked_phase=post_final_current_route
```

Rollback target state:

```text
claim_boundary_split_complete=true
required_gate_adopted=false
future_current_route_blocking_claimed=false
```

Rollback must not mutate:

```text
source facts
decisions
overlay support
rendered output
Lua bridge
runtime chunks
package payload
```

Rollback after canonical seal:

* Do not rewrite sealed history.
* Use additive supersession, owner-approved correction scope, or a separate correction round.
* Required-entry removal after canonical seal must itself be treated as a separate governed mutation.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Iris remains 100% Lua at runtime.
* Runtime/build-time separation is mandatory.
* DVF Core remains body compiler / body block composition scope.
* Iris Artifact Registry keeps artifact authority, evidence, required validation, seal, cutover, stale/predecessor guard, and runtime-package identity responsibilities.
* Publish Boundary remains separate from DVF Core and Registry success.
* `legacy_combined_governance_route` is preserved.
* Existing `current_route_required_validations.json` entries are preserved.
* Manifest mutation is additive-only.
* Runner `--mode all` must generate phase artifacts in declared phase order.
* Live manifest must not be pre-existing dirty before adoption.
* Planned required target dirty / untracked / ignored overlap must be zero or owner-dispositioned out of required adoption.
* Current route runner rewrite is forbidden.
* Manifest physical split is forbidden.
* Tooling allowlist expansion is out of scope.
* Pre-adoption loadability under current build closure is mandatory before live manifest mutation.
* New current-route required tests must use the bare-module tooling import pattern and must not import `tools.build.<round_module>`.
* Current-route import closure probe PASS is mandatory before live manifest mutation.
* Broad staging unignore is forbidden.
* `.gitignore` expected-rule count must match observed round-local count; otherwise adoption is blocked.
* Required field adoption must use stable machine/governance fields only.
* Required field adoption must have a field-host-phase mapping.
* Route result fields cannot be manifest-required predicates.
* Self-referential required gate cycles are forbidden.
* `PASS` vocabulary must remain axis-qualified.
* Claim scan universe must satisfy the mandatory minimum surface set and record drift/reduction.
* Claim scan universe must be phase-tiered into `pre_route_scan_universe` and `final_doc_scan_universe`.
* Claim scanner exceptions must be hash-bound. Prose-only exceptions and unknown exception rows are forbidden.
* `future_current_route_blocking_claimed=true` requires current-route execution-time live re-scan.
* `future_current_route_blocking_claimed=true` requires second-pass current-route live re-scan when the scope is `post_final_universe`.
* Replay-only gate validation cannot claim future current-route blocking.
* Protected source / rendered / Lua bridge / runtime / package mutation is forbidden.
* Protected no-mutation must be proven from phase0 baseline through post-route recapture.
* Final no-mutation summary fields must not be manifest-required first-route predicates.
* Adopted required artifacts must pass post-route VCS recensus.
* `machine_required_gate_adoption_complete=true` requires `post_final_current_route_rerun_success=true`.
* Post-final report updates are limited to enumerated machine fields.
* Post-final free-form report text mutation is forbidden.
* Plan-level PASS is not implementation PASS.
* Independent review gate remains blocked until a non-Claude independent review plus owner seal closes it.
* Machine adoption PASS does not imply independent review, owner seal, canonical seal, package readiness, release readiness, public text acceptance, manual QA, or runtime compatibility closure.

---

## 12. Expected Closeout State

Expected closeout target: `machine_required_gate_adoption_complete` for governance-only required-gate adoption.

Expected final state:

```text
machine_required_gate_adoption_complete=true
plan_level=PASS
execution_artifacts_present=true
implementation_evidence_status=produced
independent_review_gate=BLOCKED
current_route_closure_mode=two_pass
required_gate_adopted=true
future_current_route_blocking_claimed=true
future_current_route_blocking_scope=post_final_universe
first_current_route_pass_sequence_id=first
first_current_route_scan_universe_mode=pre_route
first_current_route_scan_universe_mode_source=phase_state_derived
first_final_doc_scan_universe_enabled=false
post_final_current_route_pass_sequence_id=second
post_final_current_route_scan_universe_mode=post_final
post_final_current_route_scan_universe_mode_source=phase_state_derived
post_final_doc_scan_universe_enabled=true
post_final_current_route_rerun_success=true
final_docs_overclaim_checked_by=second_current_route_live_rescan
legacy_combined_route_pass_is_dvf_core_pass=false
legacy_combined_governance_route_preserved=true
dvf_pass_standalone_current_claim_allowed=false
protected_surface_changed_count=0
post_route_protected_surface_changed_count=0
post_final_protected_surface_changed_count=0
pre_restore_protected_surface_changed_count=0
source_rendered_lua_runtime_package_mutation=false
pre_existing_dirty_target_overlap_count=0
pre_existing_dirty_live_manifest=false
pre_existing_dirty_planned_required_artifact_count=0
pre_existing_untracked_required_target_count=0
pre_existing_ignored_required_target_count=0
pre_adoption_loadability_passed=true
predecessor_rerun_root_override_supported=true
predecessor_rerun_output_root_observed=Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_required_gate_adoption/phase0/predecessor_rerun/
predecessor_default_staging_root_write_count=0
gitignore_expected_rule_manifest_status=PASS
gitignore_expected_round_local_rule_count=<derived_expected_count>
gitignore_added_rule_count=<derived_count>
gitignore_broad_unignore_rule_count=0
gitignore_round_local_rule_count=<derived_count>
gitignore_added_rule_count_matches_expected=true
removed_required_artifact_count=0
removed_required_test_count=0
predicate_meaning_change_count=0
existing_entry_reclassified_count=0
all_manifest_required_artifacts_exist_before_post_adoption_route=true
all_manifest_required_artifacts_have_final_values_before_post_adoption_route=true
manifest_required_route_result_field_count=0
self_reference_cycle_count=0
field_host_phase_mapping_status=PASS
phase_execution_mapping_status=PASS
forbidden_overclaim_count=0
allowed_boundary_statement_false_positive_count=0
unknown_claim_scanner_exception_count=0
hash_bound_false_positive_exception_count<=1
unhash_bound_scanner_exception_count=0
scanner_exception_prose_only_count=0
claim_scan_minimum_universe_satisfied=true
claim_scan_universe_derivation_mode=explicit_rule_derived
claim_scan_required_surface_missing_count=0
claim_scan_excluded_path_without_reason_count=0
predecessor_scan_universe_reference=predecessor_claim_contract_closure_rule_v1
scan_universe_drift_recorded=true
scan_universe_reduction_without_reason_count=0
pre_route_scan_universe_missing_count=0
final_doc_scan_universe_missing_count=0
live_rescan_required_test_consumed=true
post_final_live_rescan_required_test_consumed=true
current_route_import_closure_probe_status=PASS
current_route_import_closure_probe_live_manifest_mutated=false
tools_build_package_import_attempt_count=0
bare_tool_module_import_used=true
build_closure_blocker_triggered_for_forbidden_fixture=true
post_adoption_current_route_rerun_success=true
current_route_success=true
closure_enforced=true
live_manifest_rollback_required=false
post_route_required_artifact_dirty_count=0
post_route_required_artifact_untracked_count=0
post_route_required_artifact_ignored_count=0
post_final_report_update_contract_status=PASS
post_final_report_freeform_text_mutation_allowed=false
post_final_report_freeform_text_mutation_detected=false
post_final_report_updated_field_count=<derived_count>
post_final_report_updated_field_set_matches_allowlist=true
owner_adjudication_scope=single_bounded_predecessor_non_claim_false_positive_row_only
owner_adjudication_does_not_generalize=true
canonical_complete_claimed=false
independent_review_claimed=false
owner_seal_claimed=false
canonical_seal_allowed=false
independent_review_gate_status=not_claimed
owner_seal_status=not_claimed
canonical_seal_status=not_claimed
```

`future_current_route_blocking_claimed=true` is valid only when `live_rescan_required_test_consumed=true`, `post_final_live_rescan_required_test_consumed=true`, and `post_final_current_route_rerun_success=true`. If live re-scan is not consumed and the gate is replay-only, expected final state must be downgraded:

```text
required_gate_adopted=true
future_current_route_blocking_claimed=false
future_current_route_blocking_claim_denied_reason=replay_only_enforcement
machine_required_gate_adoption_complete=false
owner_redecision_required=true
```

Expected non-claims:

* no Registry Authority PASS
* no Registry Runtime Compatibility PASS
* no Runtime Payload Consumer Compatibility closure
* no Publish Boundary PASS
* no public text acceptance
* no semantic quality acceptance
* no package readiness
* no release / Workshop / B42 / deployment readiness
* no manual QA
* no source / rendered / Lua bridge / runtime / package mutation

Expected blocked state if import closure or manifest adoption cannot be safely performed:

```text
required_gate_adopted=false
future_current_route_blocking_claimed=false
machine_required_gate_adoption_complete=false
blocked=true
blocked_reason=<exact blocker>
blocked_phase=<phase>
```

Expected blocked conditions include:

```text
gitignore_expected_rule_count_mismatch
gitignore_broad_unignore_detected
pre_existing_dirty_live_manifest=true
pre_existing_dirty_target_overlap_count>0 without owner disposition
unknown_claim_scanner_exception_count>0
unhash_bound_scanner_exception_count>0
scanner_exception_prose_only_count>0
current_route_import_closure_probe_status!=PASS
pre_adoption_loadability_passed=false
claim_scan_minimum_universe_satisfied=false
claim_scan_required_surface_missing_count>0
field_host_phase_mapping_status!=PASS
self_reference_cycle_count>0
post_adoption_current_route_rerun_success=false
live_manifest_rollback_required=true
post_route_protected_surface_changed_count>0
post_final_protected_surface_changed_count>0
post_route_required_artifact_dirty_count>0
post_route_required_artifact_untracked_count>0
post_route_required_artifact_ignored_count>0
post_final_current_route_rerun_success=false
final_doc_scan_universe_missing_count>0
```

If canonical claim is required, machine adoption remains separate until these separate fields are satisfied:

```text
independent_review_gate_report=PASS
owner_canonical_seal_gate_report=PASS
canonical_seal_allowed=true
canonical_complete_claimed=true
```
