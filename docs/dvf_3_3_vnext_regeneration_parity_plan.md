# DVF 3-3 vNext Regeneration Parity Plan

> 상태: planned / scope-lock candidate / WARN review revisions applied / fresh-full-rerun success path locked / field-resolution contingency locked
> 작성일: 2026-06-15
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Roadmap input: `C:/Users/MW/.codex/attachments/ddf2074c-4825-402a-b965-d0ea61f8eea8/pasted-text.txt` / sha256 `2379C192AEEDD94E14770726B578F23B8ED8A3168E45CDBF3FCE6063C907DD53` / unsealed roadmap drafting input
> Review input: `C:/Users/MW/.codex/attachments/24d12468-afaa-4bc1-aae2-bb4a69c790c2/pasted-text.txt` / sha256 `8BFA75A6B22A20271E50EF7CA6174E1016EAF475F3AD071A0C94A42EF4969045` / WARN review reference
> Related governance: `docs/dvf_3_3_vnext_current_authority_plan.md`, `docs/dvf_3_3_vnext_regeneration_requirements.md`, `docs/dvf_3_3_vnext_cutover_contract.md`, `docs/dvf_3_3_vnext_runtime_seed_disposition.md`

---

## 1. Objective

DVF 3-3 vNext successor candidate가 source-to-runtime regeneration chain을 staging에서 결정론적으로 통과할 수 있는지 검증하고, regenerated successor chunk bundle과 existing predecessor runtime chunk bundle 사이의 `key / state / text_ko / publish_state` field-level delta를 공식 report로 측정한다.

목표 chain은 다음이다.

```text
source manifest
-> facts
-> decisions
-> compose profile + body_plan
-> rendered
-> Lua bridge
-> chunk manifest + chunk files
```

이 계획의 완료 claim은 단일하게 `fresh_full_rerun`으로 고정한다.

```text
vNext successor candidate가 validated input에서 rendered -> Lua bridge -> chunk bundle까지 staging에서 결정론적으로 재생성되었고,
predecessor runtime chunk bundle과의 key / state / text_ko / publish_state delta가 official report로 측정되었다.
```

Sealed prior artifact reuse는 complete 경로가 아니다. 필요하면 diagnostic / non-complete 참고 경로로만 기록할 수 있으며, 이 문제의 성공 조건인 새 vNext baseline input 기반 regeneration을 대체하지 못한다.

이 계획은 frozen 2105 recovery plan, live runtime cutover plan, package/release readiness plan이 아니다.

---

## 2. Scope

이 계획은 DVF 3-3 vNext successor candidate의 regeneration evidence와 predecessor runtime parity evidence를 staging-only 산출물로 생성하는 실행 범위를 정의한다.

Primary staging evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/`

계획 문서:

* `docs/dvf_3_3_vnext_regeneration_parity_plan.md`

포함 범위:

* scope lock과 protected current surface baseline
* input lineage verdict and fresh-full-rerun gate
* field reality preflight and resolution contract
* parity field comparator contract
* runtime parity report minimum schema contract
* volatile metadata canonicalization policy
* vNext input manifest / precondition gate
* full rendered candidate regeneration into explicit staging path
* Lua bridge and chunk bundle candidate regeneration into explicit staging path
* predecessor runtime chunk bundle read-only parsing
* normalized predecessor/successor parity comparison
* field-level delta report generation
* determinism rerun and protected-surface no-mutation validation
* current route regression / bridge export contract / package forbidden scan validation
* closeout, ledger packet, follow-up input handoff

### Explicitly Out Of Scope

* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua` 변경
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua` 변경
* `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua` 생성 또는 복귀
* `Iris/build/description/v2/data/dvf_3_3_facts.jsonl` 변경
* `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl` 변경
* `Iris/build/description/v2/output/dvf_3_3_rendered.json` 변경
* live runtime chunk replacement
* successor baseline cutover
* canonical rendered output promotion
* successor baseline identity 최종 봉인
* package / Workshop / public release readiness 선언
* manual in-game validation
* Browser / Wiki / Tooltip behavior change
* quality exposure 변경
* `quality_state` / `publish_state` / `runtime_state` 정책 변경
* consumer migration execution
* 2105 Baseline Consumption Audit의 `change_required` rows를 즉시 mutation instruction으로 사용하는 것
* Layer4 / ACQ_DOMINANT / Acquisition Lexical / Resolver / Silent 21 / Structural Signal readpoint 재개방
* source universe reconstruction 또는 source expansion
* architecture redesign
* unrelated refactor
* optimization outside target area

---

## 3. Non-Goals

* frozen `2105 / 2084 / 21` baseline을 current input에서 복구했다고 주장하지 않는다.
* predecessor runtime bundle과 byte-for-byte parity를 완료 조건으로 삼지 않는다.
* delta count가 `0`이어야 성공이라고 정의하지 않는다.
* delta가 존재한다는 이유만으로 regression이라고 단정하지 않는다.
* runtime chunks나 runtime-derived seed를 source authority로 승격하지 않는다.
* current 6-entry facts / decisions / rendered fixture를 full vNext input으로 쓰지 않는다.
* rendered-only, bridge-only, chunk-generation-only, parity-report-only output을 current authority로 승격하지 않는다.
* old chunks와 successor chunks를 동시에 current authority로 두지 않는다.
* monolith `IrisLayer3Data.lua`를 current / staging / runtime / package authority로 되살리지 않는다.
* stale `IrisDvfBridgeData.lua` payload를 current-looking fallback으로 재유입하지 않는다.
* `active / silent`를 current runtime vocabulary로 되살리지 않는다.
* `adopted / unadopted`를 quality-pass, deletion, suppression, publish visibility 의미로 확장하지 않는다.
* runtime-side repair / compose / validation을 도입하지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 기준이다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 Iris DVF 3-3 current readpoint를 따른다.
* current deployable runtime authority는 existing chunk manifest와 chunk files다.
* existing runtime chunks는 cutover 전까지 deployable runtime authority이자 read-only comparison reference다.
* existing runtime chunks는 source authority가 아니다.
* vNext regenerated rendered / Lua bridge / chunk bundle은 staging successor candidate evidence이며 current runtime authority가 아니다.
* `docs/dvf_3_3_vnext_regeneration_requirements.md`의 regeneration chain과 delta classification rule을 따른다.
* `docs/dvf_3_3_vnext_cutover_contract.md`의 no-premature-cutover, no-dual-current, partial-promotion 금지 원칙을 따른다.
* runtime-derived seed를 사용할 경우 `docs/dvf_3_3_vnext_runtime_seed_disposition.md`의 provenance와 non-authority 조건을 유지한다.
* `body_plan`은 compose profile implementation surface / alias label이며 second authority가 아니다.
* `publish_state`는 visibility contract로 비교하되, 이 라운드에서 policy를 변경하지 않는다.
* parser failure, duplicate key, invalid enum, missing required field, nondeterministic output은 fail-loud 처리한다.
* Phase 0 `input_lineage_verdict.json`은 `fresh_full_rerun` 또는 `blocked` 중 하나로만 닫는다.
* `input_lineage_verdict.input_mode == blocked`이면 Phase 2 이후 regeneration 단계에 진입하지 않는다.
* predecessor execution plan Phase 0-11 staging output은 historical / diagnostic / comparison input으로만 읽을 수 있으며, complete closeout의 input lineage를 대체하지 못한다.
* sealed prior artifact reuse는 complete 경로가 아니며, 발견되면 `partial_prior_artifact_revalidation_only` 또는 `blocked_input_lineage`로 닫는다.
* predecessor / successor `state` / `publish_state` 비교 방식은 Phase 0 `field_reality_preflight_report.json`, `parity_field_contract.json`, `parity_field_resolution_contract.json`으로 먼저 닫는다.
* Field resolution mode는 field별로 `direct_payload`, `governed_derived`, `legacy_predecessor_only_visibility`, `blocked_unresolved` 중 하나로 봉인한다.
* `direct_payload`는 양측 payload field가 존재하고 enum universe가 동일하거나 explicit mapping table이 있을 때만 허용한다.
* `governed_derived`는 missing runtime payload field를 accepted facts / decisions / rendered lineage에서 key별로 결정론적으로 복원할 수 있고 source fingerprint가 report에 남을 때만 허용한다.
* `legacy_predecessor_only_visibility`는 predecessor `publish_state`처럼 legacy runtime payload에는 존재하지만 successor candidate에는 의도적으로 export하지 않는 visibility field에만 허용한다. 이 경우 report는 equivalence가 아니라 predecessor legacy visibility disposition과 successor intentional absence를 분리해 표시한다.
* 한쪽에 `state` 또는 `publish_state` 비교 축이 구조적으로 없더라도 Phase 0 resolution contract가 `governed_derived` 또는 `legacy_predecessor_only_visibility`로 닫으면 complete 경로를 유지할 수 있다.
* resolution mode가 `blocked_unresolved`이거나 필요한 derived source / mapping table / intentional-absence rationale이 없으면 fail-loud 처리하고 delta count `0`으로 침묵 처리하지 않는다.
* runtime-derived-seed-only input은 complete closeout을 허용하지 않는다. 해당 경우는 `blocked_precondition_seed_only`로 닫는다.
* seed-derived material이 포함되더라도 accepted source verification과 provenance carry-forward가 없는 row가 있으면 complete closeout을 허용하지 않는다.
* validation depth label은 `heavy`로 고정한다.

---

## 5. Repository Areas Affected

### Code

Directly changed by this planning step:

* None.

Expected or possible execution touch points, only if staging-safe tooling gaps are proven and separately accepted inside the execution scope:

* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/build/description/v2/tools/build/_dvf_3_3_vnext_common.py`
* `Iris/build/description/v2/tools/build/guard_dvf_3_3_vnext_output_paths.py`
* `Iris/build/description/v2/tools/build/hash_dvf_3_3_vnext_protected_surface.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_execution_contract.py`
* new parity parser / normalizer / report tools under `Iris/build/description/v2/tools/build/`

### Docs

Directly added:

* `docs/dvf_3_3_vnext_regeneration_parity_plan.md`

Read-only authority inputs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/EXECUTION_CONTRACT.md`
* `docs/dvf_3_3_vnext_current_authority_plan.md`
* `docs/dvf_3_3_vnext_current_authority_roadmap.md`
* `docs/dvf_3_3_vnext_regeneration_requirements.md`
* `docs/dvf_3_3_vnext_cutover_contract.md`
* `docs/dvf_3_3_vnext_runtime_seed_disposition.md`
* `docs/dvf_3_3_vnext_source_authority_conditions.md`
* `docs/dvf_3_3_vnext_consumer_migration_principles.md`

Expected execution docs / packet outputs:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase0/scope_lock.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase7/closeout.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase7/ledger_update_packet.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase7/followup_input_index.md`
* optional draft packets for later `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md` reflection

### Config

None directly.

Execution may read, but must not mutate unless separately justified:

* `Iris/build/description/v2/data/compose_profiles_v2.json`
* `Iris/build/description/v2/data/compose_profile_identity_hint_rules.json`
* `Iris/build/description/v2/data/compose_profile_conflict_precedence_rules.json`

### Generated Artifacts

All generated artifacts must stay under:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/`

Expected artifact families:

* `phase0/protected_surface_baseline.json`
* `phase0/allowed_inputs.json`
* `phase0/forbidden_surface_scan.json`
* `phase0/input_lineage_verdict.json`
* `phase0/field_reality_preflight_report.json`
* `phase0/parity_field_contract.json`
* `phase0/parity_field_resolution_contract.json`
* `phase0/runtime_parity_report_schema_contract.json`
* `phase0/determinism_canonicalization_policy.json`
* `phase0/exact_command_route_matrix.json`
* `phase0/exact_command_route_matrix.md`
* `phase1/input_manifest_verdict.json`
* `phase1/input_manifest_fingerprint.json`
* `phase1/facts_decisions_schema_report.json`
* `phase1/vocabulary_guard_report.json`
* `phase2/rendered/dvf_3_3_rendered.vnext.json`
* `phase2/rendered_validation_report.json`
* `phase2/rendered_hashes.json`
* `phase2/compose_context_verdict.json`
* `phase2/rendered_candidate_origin.json`
* `phase3/chunks/IrisLayer3DataChunks.lua`
* `phase3/chunks/IrisLayer3DataChunks/*.lua`
* `phase3/bridge_report.json`
* `phase3/chunk_manifest_fingerprint.json`
* `phase3/chunk_file_hashes.json`
* `phase3/lua_syntax_report.json`
* `phase3/chunk_candidate_origin.json`
* `phase4/predecessor_runtime_snapshot.json`
* `phase4/predecessor_runtime_snapshot.jsonl`
* `phase4/predecessor_parse_report.json`
* `phase4/predecessor_hash_inventory.json`
* `phase4/predecessor_field_coverage.json`
* `phase4/predecessor_state_publish_state_vocabulary_report.json`
* `phase5/runtime_parity_report.json`
* `phase5/runtime_parity_report.md`
* `phase5/runtime_parity_deltas.jsonl`
* `phase5/missing_keys.txt`
* `phase5/additional_keys.txt`
* `phase5/text_ko_delta_summary.md`
* `phase5/state_delta_summary.md`
* `phase5/publish_state_delta_summary.md`
* `phase5/field_resolution_delta_summary.md`
* `phase6/determinism_report.json`
* `phase6/protected_surface_no_mutation_verdict.json`
* `phase6/current_route_regression_report.json`
* `phase6/bridge_export_contract_report.json`
* `phase6/package_forbidden_scan_report.json`
* `phase6/legacy_active_silent_guard_report.json`
* `phase6/layer4_current_surface_guard_report.json`
* `phase7/final_contract_report.json`

---

## 6. Planned Changes

### Change 1 - Phase 0 Scope Lock and Protected Surface Baseline

Purpose:

Regeneration + predecessor parity evidence round임을 봉인하고 live cutover, runtime mutation, package readiness로 오독되는 경로를 닫는다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase0/scope_lock.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase0/protected_surface_baseline.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase0/allowed_inputs.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase0/forbidden_surface_scan.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase0/input_lineage_verdict.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase0/field_reality_preflight_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase0/parity_field_contract.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase0/parity_field_resolution_contract.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase0/runtime_parity_report_schema_contract.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase0/determinism_canonicalization_policy.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase0/exact_command_route_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase0/exact_command_route_matrix.md`

Implementation Notes:

* staging evidence root를 확정한다.
* protected current surface 목록을 확정한다.
* predecessor runtime reference path와 vNext input manifest path를 확정한다.
* current output / runtime / package path write 금지선을 확정한다.
* allowed tooling list와 expected report schema 초안을 기록한다.
* `exact_command_route_matrix.json`과 `.md`에 Phase 1-7에서 실행할 실제 command route를 명령 단위로 봉인한다.
* command matrix는 최소한 `phase`, `route_role`, `cwd`, `command`, `inputs`, `outputs`, `protected_preflight_required`, `expected_exit_code`, `blocked_if_missing`, `validation_artifact`, `notes`를 포함한다.
* command matrix의 `route_role`은 `fresh_full_rerun` 또는 `common_validation` 중 하나로 둔다.
* exact command route가 없는 required validation / generation / parser / report command는 추정 실행하지 않고 `blocked_tooling_unverified`로 닫는다.
* Phase 0 이후 실행자는 suggested command를 임의 구성하지 않고 command matrix에 봉인된 route만 사용한다.
* determinism command는 same selected input으로 rendered / bridge / chunk generation을 재실행하고 canonicalized hash를 비교하는 `fresh_full_rerun` route만 허용한다.
* predecessor execution plan Phase 0-11 staging output은 `input_lineage_verdict.json`에서 `prior_artifact_reuse_allowed=false`로 고정한다.
* `input_lineage_verdict.json`은 최소한 `input_mode`, `selected_input_manifest`, `source_manifest_fingerprint`, `facts_fingerprint`, `decisions_fingerprint`, `profile_fingerprint`, `overlay_fingerprint`, `prior_artifact_reuse_allowed`, `rejected_prior_artifact_reuse_source`, `claim_boundary`, `blocked_reason`을 포함한다.
* `input_mode` 허용값은 `fresh_full_rerun`, `blocked`다.
* `claim_boundary` 허용값은 `fresh_regeneration`이다.

Minimum `input_lineage_verdict.json` shape:

```json
{
  "input_mode": "fresh_full_rerun | blocked",
  "selected_input_manifest": null,
  "source_manifest_fingerprint": null,
  "facts_fingerprint": null,
  "decisions_fingerprint": null,
  "profile_fingerprint": null,
  "overlay_fingerprint": null,
  "prior_artifact_reuse_allowed": false,
  "rejected_prior_artifact_reuse_source": null,
  "claim_boundary": "fresh_regeneration",
  "blocked_reason": null
}
```

* prior staging artifact revalidation이 필요한 경우에도 complete 경로가 아니며, 별도 diagnostic / non-complete output으로만 기록한다.
* `field_reality_preflight_report.json`은 predecessor runtime chunks, fresh successor rendered candidate schema expectation, Lua bridge export shape, facts / decisions lineage에서 `key`, `text_ko`, `state`, `publish_state`의 실제 존재 위치를 기록한다.
* `parity_field_contract.json`을 작성해 `key`, `text_ko`, `state`, `publish_state`, missing/empty/null policy, legacy alias policy를 Phase 4-5 전에 고정한다.
* `parity_field_resolution_contract.json`은 field별 resolution mode, direct payload path, derived source path, mapping table path, intentional absence rationale, complete-allowed 여부를 고정한다.
* `state` / `publish_state` exact comparison은 resolution mode가 `direct_payload`이고 양측 enum universe가 동일한 경우에만 허용한다. enum universe가 다르면 explicit mapping table을 mandatory로 둔다.
* 한쪽에 비교 축이 구조적으로 없으면 즉시 차단하지 않고 `governed_derived` 또는 `legacy_predecessor_only_visibility`로 해소 가능한지 먼저 판정한다.
* 해소 불가능하면 `blocked_unresolved`로 fail-loud 처리한다.

Minimum `parity_field_contract.json` shape:

```json
{
  "key": {
    "comparison": "exact"
  },
  "text_ko": {
    "comparison": "normalized_and_raw",
    "normalization_allowed": ["lua_escape_decode", "line_ending_normalization"],
    "normalization_forbidden": ["semantic_rewrite", "josa_repair", "whitespace_collapse_that_changes_rendered_text"]
  },
  "state": {
    "comparison": "exact | explicit_mapping | derived_disposition",
    "mapping_table_path": null,
    "enum_universe_verdict": "same | different | not_comparable",
    "resolution_contract_path": "phase0/parity_field_resolution_contract.json"
  },
  "publish_state": {
    "comparison": "exact | explicit_mapping | legacy_visibility_disposition",
    "mapping_table_path": null,
    "enum_universe_verdict": "same | different | not_comparable",
    "resolution_contract_path": "phase0/parity_field_resolution_contract.json"
  },
  "missing_empty_null_policy": "separate_categories",
  "legacy_active_silent_policy": "historical_alias_not_current_vocabulary"
}
```

Minimum `parity_field_resolution_contract.json` shape:

```json
{
  "fields": {
    "key": {
      "resolution_mode": "direct_payload",
      "complete_allowed": true
    },
    "text_ko": {
      "resolution_mode": "direct_payload",
      "complete_allowed": true
    },
    "state": {
      "resolution_mode": "direct_payload | explicit_mapping | governed_derived | blocked_unresolved",
      "predecessor_source_path": null,
      "vnext_source_path": null,
      "derived_source_fingerprint": null,
      "mapping_table_path": null,
      "complete_allowed": "true | false",
      "blocked_reason": null
    },
    "publish_state": {
      "resolution_mode": "direct_payload | explicit_mapping | legacy_predecessor_only_visibility | blocked_unresolved",
      "predecessor_source_path": null,
      "vnext_source_path": null,
      "intentional_absence_rationale": null,
      "mapping_table_path": null,
      "complete_allowed": "true | false",
      "blocked_reason": null
    }
  },
  "blocked_fields": []
}
```

* `runtime_parity_report_schema_contract.json`에 `report_type`, `claim_boundary`, predecessor/vNext authority role, key parity, field parity, validation counts를 필수 top-level field로 고정한다.
* `determinism_canonicalization_policy.json`에 timestamp, absolute path, generated_at 등 volatile metadata를 hash 대상에서 제외하거나 canonicalize하는 규칙을 기록한다.
* 최소 protected surface는 canonical rendered output, style normalization output, compose requeue output, current facts / decisions fixture, live runtime chunk path, package output equivalent, stale bridge forbidden path, monolith forbidden path를 포함한다.
* monolith / stale bridge / current-looking fallback surface를 pre-scan한다.

Validation:

* protected surface baseline hash snapshot 생성
* staging root outside-current-path 확인
* monolith / stale bridge forbidden path pre-scan
* input lineage verdict schema check
* field reality preflight schema and coverage check
* parity field contract schema check
* parity field resolution contract schema check
* no `blocked_unresolved` field if complete path is expected
* runtime parity report schema contract check
* determinism canonicalization policy check
* exact command route matrix schema check
* exact command route matrix fresh-full-rerun route coverage check
* no cutover / no live mutation / no release readiness wording scan

---

### Change 2 - Phase 1 vNext Input Manifest / Precondition Gate

Purpose:

vNext facts / decisions / profile / overlay / input manifest가 이번 regeneration 라운드의 유효 입력인지 확인한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase1/input_manifest_verdict.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase1/input_manifest_fingerprint.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase1/facts_decisions_schema_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase1/vocabulary_guard_report.json`

Implementation Notes:

* input manifest 존재 여부와 fingerprint를 확인한다.
* `phase0/input_lineage_verdict.json`의 `input_mode != blocked`를 Phase 1 pass 전제에 포함한다.
* facts / decisions / profile / overlay path를 해석한다.
* expected entry universe, required field coverage, duplicate key, invalid enum을 측정한다.
* current 6-entry fixture와 full vNext input 혼동을 차단한다.
* runtime-derived seed가 source authority로 승격되지 않았는지 검증한다.
* source provenance가 `runtime-derived-seed-only`라면 `blocked_precondition_seed_only`로 기록하고 complete closeout을 금지한다.
* seed-derived material이 포함되더라도 accepted source verification과 provenance carry-forward가 없는 row가 있으면 blocked로 기록한다.

Validation:

* manifest schema validation
* facts / decisions row count validation
* required key uniqueness validation
* profile / body_plan binding validation
* invalid current vocabulary scan
* seed-only provenance blocked check
* input lineage non-blocked check
* precondition gate report: `PASS` 또는 `BLOCKED-with-reason`

---

### Change 3 - Phase 2 Full Rendered Candidate Regeneration

Purpose:

Phase 0에서 봉인된 fresh vNext input manifest에서 full rendered authority candidate를 explicit staging path에 결정론적으로 생성한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase2/rendered/dvf_3_3_rendered.vnext.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase2/rendered_validation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase2/rendered_hashes.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase2/compose_context_verdict.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase2/current_output_no_mutation_precheck.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase2/rendered_candidate_origin.json`

Implementation Notes:

* Phase 2 진입 조건은 `phase0/input_lineage_verdict.json`의 `input_mode == fresh_full_rerun`이다.
* vNext input manifest에서 rendered candidate를 새로 생성한다.
* `rendered_candidate_origin.json`에 `artifact_origin=fresh_full_rerun`과 `claim_boundary=fresh_regeneration`을 기록한다.
* prior staging rendered artifact 재검증은 complete 경로가 아니며 Phase 2 대체 입력으로 사용할 수 없다.
* `compose_layer3_text` current compose contract를 사용한다.
* `build_rendered()` shared guard를 통과한다.
* `compose_context=staging` 또는 동등한 non-current context를 명시한다.
* current-equivalent output write를 금지한다.
* style / requeue side-output도 explicit staging path에만 기록한다.
* rendered hash와 entry count를 기록한다.

Validation:

* compose guard 통과
* rendered schema validation
* rendered validator hard fail / warn count 기록
* duplicate key fail-loud
* current output no-mutation hash diff
* rendered candidate origin claim-boundary check
* second-run rendered hash determinism check 준비 또는 수행

---

### Change 4 - Phase 3 Lua Bridge and Chunk Bundle Candidate Regeneration

Purpose:

Phase 2 rendered candidate에서 Lua bridge와 chunk bundle candidate를 staging에 재생성한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase3/chunks/IrisLayer3DataChunks.lua`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase3/chunks/IrisLayer3DataChunks/*.lua`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase3/bridge_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase3/chunk_manifest_fingerprint.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase3/chunk_file_hashes.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase3/lua_syntax_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase3/monolith_forbidden_scan.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase3/chunk_candidate_origin.json`

Implementation Notes:

* Phase 3 진입 조건은 `phase0/input_lineage_verdict.json`의 `input_mode == fresh_full_rerun`이다.
* Phase 2 rendered candidate에서 Lua bridge와 chunk bundle candidate를 새로 export한다.
* `chunk_candidate_origin.json`에 `artifact_origin=fresh_full_rerun`과 `claim_boundary=fresh_regeneration`을 기록한다.
* prior staging bridge / chunk artifact 재검증은 complete 경로가 아니며 Phase 3 대체 입력으로 사용할 수 없다.
* chunk-authority exporter route를 사용한다.
* exporter default path는 live Lua path일 수 있으므로 explicit staging output root를 강제한다.
* bridge report가 chunk authority 기준인지 확인한다.
* monolith export는 사용하지 않거나 explicit diagnostic / historical side-output으로만 격리한다.
* live runtime path write를 금지한다.

Validation:

* bridge export contract validation
* bridge report schema validation
* chunk manifest schema validation
* chunk file count validation
* chunk manifest loadability scan
* Lua syntax validation
* live runtime path no-mutation hash diff
* monolith / stale bridge forbidden scan
* chunk candidate origin claim-boundary check

---

### Change 5 - Phase 4 Predecessor Runtime Snapshot Extraction

Purpose:

기존 deployable runtime chunk bundle을 read-only comparison reference로 파싱한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase4/predecessor_runtime_snapshot.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase4/predecessor_runtime_snapshot.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase4/predecessor_parse_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase4/predecessor_hash_inventory.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase4/predecessor_field_coverage.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase4/predecessor_state_publish_state_vocabulary_report.json`

Implementation Notes:

* existing runtime chunk manifest path를 확인한다.
* referenced chunk files를 read-only로 파싱한다.
* predecessor normalized snapshot을 생성한다.
* predecessor entry count, key uniqueness, required field coverage를 기록한다.
* `key / state / text_ko / publish_state` 필드를 추출한다.
* predecessor payload의 `state` / `publish_state` 실제 필드 존재 여부와 enum universe를 `predecessor_state_publish_state_vocabulary_report.json`에 기록한다.
* `state` / `publish_state`가 predecessor runtime payload에 없으면 absence를 field reality로 기록하고 Phase 5 resolution engine에 전달한다.
* Phase 4 invalid enum report는 Phase 0 `parity_field_contract.json`과 같은 판정 기준을 사용한다.
* `state` 또는 `publish_state` field absence는 delta `0`이 아니라 `field_absent_requires_resolution` candidate로 기록한다.
* raw payload hash inventory를 기록한다.

Validation:

* predecessor manifest exists
* all referenced chunks exist
* parser completeness check
* duplicate key check
* required field coverage check
* invalid enum report
* `state` / `publish_state` field-reality and enum-universe check
* field absence forwarded to Phase 5 resolution check
* parity field contract conformance check
* raw hash inventory
* no write access check

---

### Change 6 - Phase 5 Normalized Parity Engine and Delta Report

Purpose:

vNext regenerated chunk candidate와 predecessor runtime snapshot 사이의 `key / state / text_ko / publish_state` parity를 공식 측정한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/runtime_parity_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/runtime_parity_report.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/runtime_parity_deltas.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/missing_keys.txt`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/additional_keys.txt`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/text_ko_delta_summary.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/state_delta_summary.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/publish_state_delta_summary.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/field_resolution_delta_summary.md`

Implementation Notes:

* predecessor snapshot과 vNext snapshot을 동일 normalized record schema로 변환한다.
* Phase 5 진입 전 `phase0/field_reality_preflight_report.json`, `phase0/parity_field_contract.json`, `phase0/parity_field_resolution_contract.json`, `phase4/predecessor_state_publish_state_vocabulary_report.json`이 모두 존재해야 한다.
* key set comparison을 수행한다.
* missing key / additional key 목록을 생성한다.
* matching key에 대해 field-level comparison을 수행한다.
* `state`, `text_ko`, `publish_state` delta를 분리한다.
* null / missing / empty / changed distinction을 유지한다.
* normalized record는 field별 `field_presence`, `field_source`, `resolution_mode`, `derived_source_fingerprint`, `comparison_claim`을 포함한다.
* raw text diff와 normalized text diff를 분리한다.
* parity report는 recovery / equivalence verdict가 아니라 successor-predecessor delta measurement로 라벨링한다.
* `text_ko` normalization은 `lua_escape_decode`, `line_ending_normalization` 같은 representation normalization만 허용한다.
* `semantic_rewrite`, `josa_repair`, rendered text 의미를 바꾸는 whitespace collapse는 금지한다.
* `direct_payload` field는 양측 enum universe가 동일한 경우에만 exact comparison을 허용한다.
* enum universe가 다르면 `parity_field_contract.json`의 explicit mapping table을 mandatory로 사용한다.
* `governed_derived` field는 accepted facts / decisions / rendered lineage에서 key별 값을 결정론적으로 derive하고, direct runtime payload equality로 주장하지 않는다.
* `legacy_predecessor_only_visibility` field는 predecessor legacy visibility payload와 successor intentional absence / non-export rationale을 report한다. 이 mode는 release visibility policy 변경이나 equality proof가 아니다.
* `blocked_unresolved` field가 하나라도 있으면 Phase 5는 complete report를 생성하지 않고 `blocked_parity_field_contract`로 닫는다.
* 한쪽에 비교 축이 구조적으로 없는 경우에도 resolution mode와 source disposition을 기록하고, delta count `0`으로 침묵 처리하지 않는다.
* sample diff는 최소한 missing key, additional key, `text_ko` changed, `state` changed, `publish_state` changed, null / empty / missing category를 포함한다.

Runtime parity report minimum top-level contract:

```json
{
  "report_type": "vnext_successor_predecessor_runtime_delta_measurement",
  "claim_boundary": "fresh_regeneration",
  "predecessor": {
    "entry_count": 0,
    "source": "existing_runtime_chunk_bundle",
    "authority_role": "deployable_runtime_authority_until_cutover_and_comparison_reference"
  },
  "vnext": {
    "entry_count": 0,
    "source": "staging_regenerated_successor_candidate",
    "authority_role": "successor_candidate_evidence_not_live_runtime_authority"
  },
  "key_parity": {
    "matching_key_count": 0,
    "missing_in_vnext_count": 0,
    "additional_in_vnext_count": 0
  },
  "field_parity": {
    "exact_match_count": 0,
    "text_ko_delta_count": 0,
    "state_delta_count": 0,
    "publish_state_delta_count": 0,
    "not_comparable_count": 0
  },
  "field_resolution": {
    "key": {
      "resolution_mode": "direct_payload",
      "comparison_claim": "exact_key_set_comparison"
    },
    "text_ko": {
      "resolution_mode": "direct_payload",
      "comparison_claim": "raw_and_normalized_text_delta"
    },
    "state": {
      "resolution_mode": "direct_payload | governed_derived",
      "comparison_claim": "runtime_payload_delta | governed_derived_disposition",
      "blocked_reason": null
    },
    "publish_state": {
      "resolution_mode": "direct_payload | explicit_mapping | legacy_predecessor_only_visibility",
      "comparison_claim": "runtime_payload_delta | legacy_visibility_disposition",
      "blocked_reason": null
    }
  },
  "validation": {
    "schema_valid": true,
    "duplicate_key_count": 0,
    "invalid_enum_count": 0,
    "parser_error_count": 0,
    "not_comparable_count": 0
  }
}
```

Validation:

* parity report schema validation
* total count consistency check
* `predecessor_count = matching + missing_in_vnext`
* `vnext_count = matching + additional_in_vnext`
* per-field delta count consistency
* invalid state / publish_state enum fail-loud
* `state` / `publish_state` comparator contract check
* field resolution contract conformance check
* no `blocked_unresolved` field in complete report
* `not_comparable` / unresolved field fail-loud check
* duplicate key fail-loud
* delta detail row count consistency
* sample diff rendering sanity check by required sample category
* predecessor read-only 확인
* report가 delta-measurement로 명시 라벨됨

---

### Change 7 - Phase 6 Determinism, Regression, and No-Mutation Validation

Purpose:

regeneration output이 결정론적이고, current protected surface가 변경되지 않았으며, current route guard가 회귀하지 않았음을 확인한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase6/determinism_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase6/protected_surface_no_mutation_verdict.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase6/current_route_regression_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase6/bridge_export_contract_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase6/package_forbidden_scan_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase6/legacy_active_silent_guard_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase6/layer4_current_surface_guard_report.json`

Implementation Notes:

* Phase 6은 Phase 0 `exact_command_route_matrix.json`에 봉인된 `fresh_full_rerun` determinism route만 실행한다.
* Phase 2-3 generation commands를 same selected input으로 재실행하고 rendered hash, bridge report hash, chunk manifest fingerprint, chunk file hashes를 비교한다.
* prior staging artifact revalidation은 complete determinism route가 아니며 determinism PASS 근거로 사용할 수 없다.
* rendered hash, bridge report hash, chunk manifest fingerprint, chunk file hashes를 비교한다.
* `phase0/determinism_canonicalization_policy.json`에 따라 timestamp, absolute path, generated_at, machine-local temp path 같은 volatile metadata를 hash 대상에서 제외하거나 canonicalize한다.
* volatile field가 canonicalization policy 없이 report hash를 흔들면 determinism PASS를 금지한다.
* parity report regeneration stability를 확인한다.
* protected current surface hash diff를 확인한다.
* current route regression과 bridge export contract를 실행한다.
* package forbidden scan, legacy vocabulary guard, Layer4 current-surface guard를 실행한다.

Validation:

* determinism rerun PASS
* fresh-full-rerun determinism command route PASS
* volatile metadata canonicalization PASS
* protected surface no-mutation PASS
* current route regression PASS
* bridge export contract PASS
* package forbidden scan PASS
* Lua syntax PASS
* legacy active/silent current-surface guard PASS
* layer4 current-surface guard PASS
* parity report schema PASS

---

### Change 8 - Phase 7 Closeout, Ledger Packet, and Next-Round Input Handoff

Purpose:

이번 라운드의 결과를 vNext successor와 predecessor runtime의 delta 측정으로 봉인하고, 후속 cutover / consumer migration / release validation과 구분한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase7/closeout.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase7/ledger_update_packet.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase7/followup_input_index.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase7/claim_boundary_checklist.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase7/final_contract_report.json`

Implementation Notes:

* closeout을 작성한다.
* `input_lineage_verdict.json`의 `input_mode`와 `claim_boundary`를 closeout headline에 반영한다.
* complete closeout headline은 `fresh_full_rerun / fresh_regeneration`만 허용한다.
* prior artifact reuse / revalidation이 실행되었으면 complete가 아니라 `partial_prior_artifact_revalidation_only` 또는 blocked closeout으로 닫는다.
* runtime-derived-seed-only input이면 complete closeout을 금지하고 `blocked_precondition_seed_only`로 닫는다.
* parity report 요약, successor candidate fingerprint, protected no-mutation verdict를 반영한다.
* claim boundary와 non-decision을 명시한다.
* `COMMON-RELEASE-NONDECISION`과 `COMMON-RUNTIME-SURFACE-NONMUTATION` marker를 ledger packet과 closeout에 기본 포함한다.
* marker를 생략하려면 Phase 7에서 별도 `marker_omission_reason`을 fail-loud로 기록하고, release/cutover/runtime mutation 오독 방지 문구가 동등하게 존재함을 증명해야 한다.
* unresolved delta disposition 필요 여부를 표시한다.
* 후속 round input 목록을 작성한다.
* ledger update packet과 ROADMAP / DECISIONS / ARCHITECTURE 반영 후보 문구를 작성한다.
* live cutover를 열지 않았다는 점을 명시한다.

Validation:

* closeout claim boundary review
* input lineage verdict reflected in closeout
* seed-derived provenance disposition reflected in closeout
* COMMON marker inclusion check
* non-decision checklist 확인
* artifact path existence check
* report schema check
* protected no-mutation verdict attached
* successor candidate fingerprint attached
* follow-up input path completeness check
* recovery / cutover / release claim 없음 확인

---

## 7. Validation Plan

### Automated Validation

Validation depth: `heavy`.

Plan-stage validation:

* `docs/PLAN_TEMPLATE.md` section coverage check
* referenced authority docs path existence check
* roadmap input hash recorded
* review input hash recorded
* exact command route matrix required artifact check
* exact command route matrix actual command-unit coverage check
* fresh-full-rerun determinism command route check
* input lineage verdict schema requirement check
* parity field contract schema requirement check
* protected surface mandatory list check
* runtime parity report minimum schema contract check
* volatile metadata canonicalization policy check
* forbidden current authority / cutover / release claim scan
* protected live path mutation wording scan
* staging evidence root consistency scan

Execution validation:

* vNext input manifest schema validation
* facts / decisions schema validation
* profile / body_plan binding validation
* rendered schema validation
* rendered determinism validation
* bridge export contract validation
* chunk manifest schema validation
* chunk file count and loadability scan
* Lua syntax validation
* predecessor runtime parser completeness check
* predecessor `state` / `publish_state` field-reality and enum-universe validation
* `state` / `publish_state` direct-vs-derived-vs-legacy-visibility resolution gate
* `blocked_unresolved` / `not_comparable` fail-loud validation
* normalized parity report schema validation
* field resolution summary consistency checks
* field-level delta count consistency checks
* protected current surface no-mutation check
* current route regression
* package forbidden scan
* legacy `active / silent` current-surface guard
* Layer4 current-surface guard
* final contract report validation

Exact command routes must be resolved during Phase 0 as `phase0/exact_command_route_matrix.json` and `phase0/exact_command_route_matrix.md`. If any required tool, required command, required input path, staging output flag, or protected preflight command is missing, validation is `blocked`, not `passed`.

### Manual Validation

* scope lock review
* input lineage verdict review for fresh full rerun vs blocked
* parity field contract review for `state` / `publish_state` mapping
* parity field resolution contract review for `state` / `publish_state` absence handling
* seed-derived provenance disposition review
* parity report sample diff sanity inspection
* closeout claim boundary review
* non-decision wording review
* follow-up input index review

### Validation Limits

This plan and its execution will not perform:

* no multiplayer validation
* no deployment validation
* no cutover validation
* no long-session runtime validation
* no manual in-game validation
* no Workshop validation
* no external ecosystem compatibility sweep
* no package release readiness
* no Browser / Wiki / Tooltip behavior validation
* no consumer migration execution
* no live runtime replacement
* no byte-for-byte predecessor equivalence
* no full runtime equivalence claim
* no quality exposure validation
* no release checklist completion

---

## 8. Risk Surface Touch

### Authority Surface

Staging successor candidate evidence only.

This plan does not change current authority. Existing runtime chunks remain deployable runtime authority until a separate approved cutover. vNext rendered / Lua bridge / chunks generated by this plan are successor candidate evidence, not current authority.

### Runtime Behavior Surface

None.

Runtime Lua is not changed. Live chunk payload is not replaced. Browser / Wiki / Tooltip behavior is not changed.

### Compatibility Surface

No direct compatibility mutation.

The parity report may become input to later consumer migration, but it does not execute consumer migration and does not update validators, runtime consumers, or package surfaces by itself.

### Sealed Artifact Surface

Additive staging evidence only.

Protected current data / output / runtime / package surfaces must remain unchanged. Existing sealed artifacts are read as authority inputs or comparison references, not rewritten.

### Public-Facing Output Surface

None.

Public-facing copy, UI, tooltip text, release note, Workshop description, and package readiness language are unchanged.

---

## 9. Risk Analysis

### Architecture Risk

* vNext regenerated candidate may be described as current runtime authority before cutover.
* Delta measurement may be misframed as frozen 2105 recovery.
* predecessor execution plan Phase 0-11 staging output and validated 2-4 input may be confused as competing authorities.
* Runtime-derived seed may be treated as source authority.

### Runtime Risk

* A command default may write to live runtime or canonical output path.
* Old chunks and successor chunks may both appear on current-looking surface.
* Monolith or stale bridge artifact may re-enter fallback or package reachability.
* Lua escaping or chunk formatting parser errors may create false deltas.

### Compatibility Risk

* `state` / `publish_state` mapping errors may inflate or hide deltas.
* `state` / `publish_state` field absence may be overclaimed as equality unless resolution mode and comparison claim are explicit.
* `legacy_predecessor_only_visibility` may be misread as a successor publish policy decision unless labeled as predecessor legacy visibility disposition only.
* Parity report may be read as migration execution approval.
* Current route tooling allowlist may be misread as a convenience bypass.
* `adopted / unadopted` may be overread as quality or publish policy mutation.

### Regression Risk

* Regeneration order or chunk split order may be nondeterministic.
* Volatile metadata may make report hashes unstable.
* Normalization may hide meaningful `text_ko` deltas.
* Raw Lua representation differences may be overreported as text deltas.
* Protected current surface hash capture may miss a live path if the protected set is incomplete.

---

## 10. Rollback Plan

This execution is staging-only. Rollback is primarily evidence root isolation and disposal.

If any generated candidate is written outside `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/`, the candidate is invalid as authority evidence and the round must stop. If a protected current surface hash diff is detected, the round fails with `current path write violation`; the affected file must be restored through the appropriate VCS or baseline procedure before the round can be retried.

If `input_lineage_verdict.input_mode == blocked` or Phase 1 precondition gate is `BLOCKED`, the round closes without parity claim.

If selected input is runtime-derived-seed-only, the round closes as `blocked_precondition_seed_only`; no caveat-pass complete closeout is allowed.

If `parity_field_resolution_contract.json` records `blocked_unresolved` for `state` or `publish_state`, or if a required mapping table / derived source fingerprint / intentional-absence rationale is absent, the round closes as comparator-blocked and does not publish headline delta counts for that field.

If predecessor parsing fails, chunk export success is insufficient; the round closes as incomplete and does not claim successor-predecessor delta measurement.

If determinism rerun fails, generated candidate artifacts cannot be sealed as successor evidence. The closeout records `nondeterministic_candidate` and routes a follow-up to isolate the nondeterminism source.

If parity report exists but claim boundary is ambiguous, closeout is blocked until the boundary is corrected.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance 유지.
* Hub & Spoke / SPI 원칙 유지.
* Iris runtime render-only boundary 유지.
* runtime/build-time separation 유지.
* vNext regeneration은 staging evidence root에서만 수행.
* Phase 0 `exact_command_route_matrix.json`과 `.md` 없이는 Phase 1 이후 실행 금지.
* exact command route matrix에 없는 command를 실행자가 임의 구성하지 않음.
* required command / tool / staging output flag / protected preflight가 없으면 `blocked_tooling_unverified`로 닫고 PASS를 주장하지 않음.
* Phase 0 `input_lineage_verdict.json` 없이는 Phase 2 이후 실행 금지.
* complete closeout은 `fresh_full_rerun / fresh_regeneration`만 허용.
* sealed prior artifact reuse / revalidation을 complete 경로로 사용하지 않음.
* fresh-full-rerun determinism command route를 Phase 0에서 실제 command로 봉인함.
* Phase 0 `parity_field_contract.json` 없이는 Phase 4-5 parity 측정 금지.
* Phase 0 `field_reality_preflight_report.json`과 `parity_field_resolution_contract.json` 없이는 Phase 4-5 parity 측정 금지.
* `state` / `publish_state` enum universe가 다를 때 explicit mapping table 없이 exact comparison 금지.
* field absence는 `direct_payload`, `governed_derived`, `legacy_predecessor_only_visibility`, `blocked_unresolved` 중 하나로 명시하고 delta count `0`으로 침묵 처리하지 않음.
* `legacy_predecessor_only_visibility`는 successor equality, release visibility policy, runtime cutover decision으로 해석하지 않음.
* runtime-derived-seed-only input을 complete closeout으로 봉인하지 않음.
* validation depth는 `heavy`로 유지.
* 별도 승인 없이 live data / output / runtime chunk payload 변경 금지.
* existing old chunks와 successor chunks를 동시에 current authority로 두지 않음.
* rendered-only, bridge-only, chunk-generation-only, parity-report-only output을 current authority로 승격하지 않음.
* runtime-derived seed를 source authority로 승격하지 않음.
* `body_plan`을 second authority로 취급하지 않음.
* monolith `IrisLayer3Data.lua`를 current / staging / runtime / package authority로 되살리지 않음.
* stale `IrisDvfBridgeData.lua` payload를 current-looking fallback으로 재유입하지 않음.
* `active / silent`를 current runtime vocabulary로 되살리지 않음.
* `adopted / unadopted`를 quality-pass, deletion, suppression, publish visibility 의미로 오독하지 않음.
* `publish_state`는 visibility contract로 비교하되 이 라운드에서 policy를 변경하지 않음.
* parser failure, duplicate key, invalid enum, missing required field, nondeterministic output은 fail-loud 처리.
* VCS tracking status를 authority policy로 오독하지 않음.
* `COMMON-RELEASE-NONDECISION`과 `COMMON-RUNTIME-SURFACE-NONMUTATION` marker는 Phase 7 ledger packet과 closeout에 기본 포함함.

---

## 12. Expected Closeout State

Expected closeout target: `complete`, if all Phase 0-7 gates pass.

`complete` means:

* `phase0/input_lineage_verdict.json` exists and records `input_mode != blocked`.
* `phase0/exact_command_route_matrix.json` and `.md` exist and close required Phase 1-7 routes as actual command units.
* `input_mode == fresh_full_rerun`.
* `claim_boundary == fresh_regeneration`.
* vNext input manifest is validated and full rendered candidate is generated into explicit staging path.
* Sealed prior artifact reuse / revalidation is absent from complete closeout.
* Runtime-derived-seed-only input is absent from complete closeout.
* Any seed-derived material has accepted source verification and provenance carry-forward.
* `phase0/field_reality_preflight_report.json`, `phase0/parity_field_contract.json`, `phase0/parity_field_resolution_contract.json` exist and all comparator / resolution requirements pass.
* `state` / `publish_state` are resolved by allowed mode: direct payload comparison, explicit mapping, governed derived disposition, or legacy predecessor-only visibility disposition.
* rendered validation and rendered hash recording pass.
* Lua bridge and chunk bundle candidate are generated into staging path from the fresh rendered candidate.
* predecessor runtime chunk bundle is parsed read-only.
* predecessor `state` / `publish_state` field reality and enum universe are recorded.
* predecessor and vNext snapshots are normalized into a shared record shape.
* `key / state / text_ko / publish_state` parity report is generated.
* runtime parity report includes field-level resolution mode and comparison claim, so missing `state` / `publish_state` cannot be mistaken for exact equality.
* runtime parity report includes required top-level schema fields: `report_type`, `claim_boundary`, predecessor/vNext authority role, key parity, field parity, validation counts.
* duplicate key, invalid enum, parser failure, missing required field are fail-loud.
* `blocked_unresolved` / `not_comparable` is fail-loud and not hidden as delta `0`.
* determinism rerun passes.
* fresh-full-rerun determinism route passes according to Phase 0 command matrix.
* volatile metadata canonicalization passes.
* protected current surface no-mutation verdict is `PASS`.
* current route regression passes.
* monolith / stale bridge forbidden surface scan passes.
* closeout frames the result as successor-predecessor delta measurement, not frozen 2105 recovery proof.
* closeout and ledger packet include `COMMON-RELEASE-NONDECISION` and `COMMON-RUNTIME-SURFACE-NONMUTATION` markers by default.
* follow-up cutover / consumer migration / release validation remain separate rounds.

Allowed non-complete closeouts:

* `blocked_precondition`: Phase 1 cannot identify valid full input.
* `blocked_precondition_seed_only`: selected input is runtime-derived-seed-only.
* `blocked_input_lineage`: Phase 0 cannot choose `fresh_full_rerun`.
* `partial_prior_artifact_revalidation_only`: execution can only revalidate sealed prior artifacts and cannot perform fresh full rerun.
* `blocked_parity_field_contract`: `state` / `publish_state` comparator / resolution contract is absent, unresolved, or requires missing mapping table / derived source fingerprint / intentional-absence rationale.
* `blocked_tooling_unverified`: required generation, export, parse, validation tooling, exact command route, staging output flag, or protected preflight cannot be verified.
* `partial_regeneration_only`: rendered / bridge / chunk candidate exists but predecessor parsing or parity report is incomplete.
* `partial_parity_only`: parity report exists but determinism or protected no-mutation validation fails.
* `failed_current_path_write_violation`: protected current surface changed.
* `failed_nondeterministic_candidate`: deterministic regeneration does not hold.

No closeout state may claim release readiness, package readiness, runtime cutover, successor baseline identity final sealing, or manual in-game validation completion.
