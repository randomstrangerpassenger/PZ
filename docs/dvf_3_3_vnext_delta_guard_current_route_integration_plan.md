# DVF 3-3 vNext Delta Guard Current Route Integration Plan

> 상태: planned / scope-lock candidate / second review pending
> 작성일: 2026-06-16
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Execution 기준: `docs/EXECUTION_CONTRACT.md`
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Roadmap input: `C:/Users/MW/.codex/attachments/91707d31-6fcb-4661-8f76-ad166fe85bbf/pasted-text.txt` / sha256 `8A279B68BD5CB2FA308EEA812A2C2231467F69D993743F4C64F9D510A4CCB856` / unsealed synthesized roadmap reference, preserved only as drafting input
> Review input: `C:/Users/MW/.codex/attachments/f915e4fd-957b-43f9-a27e-e24ac140276f/pasted-text.txt` / sha256 `0352EB18E0486CC5C7CABF74A69A4C07F600CD47438569DDBDD219F228D2A781` / WARN review reference
> Review input cycle 2: `C:/Users/MW/.codex/attachments/a8a20961-b141-4963-892a-cc7b5065f8bb/pasted-text.txt` / sha256 `294F8EE391B2592DF0848014C3F3D644C2B520B18F09DDD81A941A0A06EDC619` / WARN review reference
> Prior closeout input: `docs/dvf_3_3_vnext_delta_disposition_closeout.md`
> Prior sealed report input: `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_disposition_guard_seal/phase10/final_delta_disposition_guard_contract_report.json`

---

## 1. Objective

DVF 3-3 vNext delta disposition / guard seal evidence를 current validator / test / tool / package / export / compose route의 필수 fail-loud gate로 통합한다.

이번 계획의 완료 claim은 다음으로 제한한다.

```text
vNext delta disposition / guard seal evidence is integrated into the current
validator/test/tool/package/export/compose route as a fail-loud current-route
hard gate.
```

짧은 claim은 다음 하나만 허용한다.

```text
current route guard integrated
```

이 계획은 successor baseline cutover, live runtime chunk replacement, package readiness, release readiness를 선언하지 않는다. 이전 round의 상태는 다음 readpoint로만 소비한다.

* total delta: `2125`
* `text_ko 2071 + state 54 = 2125`
* approved: `2017`
* rejected: `108`
* deferred: `0`
* terminal: `complete_disposition_guard_sealed_cutover_input_blocked`
* `cutover_input_usable=false`

Execution choices:

* Phase 3/4 order token: **enforcement-first**.
* Gate design: **Hybrid gate**. Round 3 current taxonomy remains the current test identity route, while a separate required validation manifest is consumed by the current route runner as a hard gate.
* Taxonomy integration: **별도 current-route required validation manifest를 primary gate로 두고, Round 3 taxonomy / closure에는 addendum으로 반영한다.**
* Validation depth label: **heavy**. Positive pass와 negative fail-loud proof를 모두 요구한다.
* Compatibility label: **external compatibility surface none / internal build-package route impact only**.
* Shared guard authority framing: **existing guard surfaces keep their status-specific definition roles; the shared guard contract is an admission gate / aggregation surface that references those definitions and adds cross-route consistency checks.**
* Stale Bridge status: **Stale DVF Bridge Artifact Disposition remains implemented / review_pending unless separately sealed. This plan may reference its package intrusion criteria as subordinate implemented evidence, but must not claim it as an independently sealed authoritative definition owner.**
* Current closure discipline: **no new current core module and no tooling allowlist expansion by convenience**. Required validation may execute existing scripts / tests, but must not add a new `tools.build.*` import to the current taxonomy unless separately reviewed.

---

## 2. Scope

이 계획은 sealed disposition / guard evidence를 current route hard gate로 연결하는 실행 범위를 정의한다.

Primary evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/`

계획 문서:

* `docs/dvf_3_3_vnext_delta_guard_current_route_integration_plan.md`

Expected execution docs:

* `docs/dvf_3_3_vnext_delta_guard_current_route_integration_scope_lock.md`
* `docs/dvf_3_3_vnext_delta_guard_current_route_input_contract.md`
* `docs/dvf_3_3_vnext_delta_guard_shared_contract.md`
* `docs/dvf_3_3_vnext_delta_guard_current_route_integration_closeout.md`
* `docs/dvf_3_3_vnext_current_authority_handoff_packet.md`

포함 범위:

* prior disposition closeout과 final guard contract report를 read-only evidence input으로 binding
* parity report presence, disposition denominator coverage, approved manifest index-only contract를 current route hard gate로 연결
* 8개 forbidden condition을 shared guard contract / forbidden scan criteria로 정리
* shared guard contract와 Compose Entrypoint Guard Hardening / Lua Bridge Export Contract Realignment / Stale DVF Bridge Artifact Disposition surface의 status-aware authority 관계 선언
* current validator / test / tool route에 fail-loud enforcement wiring
* `Iris/_docs/round3/round3_run_contract_tests.py`가 current 실행 시 required validation manifest를 읽고, missing / skipped / failed required validation이면 non-zero exit로 실패하도록 wiring
* guard validation을 current route required validation으로 봉인
* package / export / compose route가 같은 forbidden scan criteria를 소비하도록 integration
* compose route guard target을 `compose_layer3_text.py`의 sealed `build_rendered()` write boundary와 reconcile
* positive clean-route validation과 intentional negative fixture fail-loud proof
* protected current surface no-mutation validation
* dual-zero 재확인
* parent problem handoff packet 작성: next-round allowed inputs, forbidden inputs, prerequisites, next-work list, and non-claims
* closeout과 ledger update packet 작성

### Explicitly Out Of Scope

* vNext successor baseline identity final seal
* live runtime chunk replacement
* current deployable authority switch
* approved delta 기반 cutover execution
* `cutover_input_usable=false` 변경
* rejected delta correction
* re-parity execution after correction
* predecessor / successor payload 재diff 또는 row input 재구성
* rendered text quality acceptance
* Browser / Wiki / Tooltip behavior change
* public-facing text mutation
* package readiness declaration
* release readiness declaration
* Workshop readiness declaration
* B42 readiness declaration
* manual in-game QA
* successor chunks current path placement
* staging artifact direct current promotion
* monolith export current fallback restoration
* 6-entry fixture current authority promotion
* approved manifest를 runtime payload, chunk bundle, release input, cutover authorization으로 재정의
* legacy `active / silent` vocabulary current writer / runtime vocabulary restoration
* architecture redesign
* unrelated refactor

---

## 3. Non-Goals

* guard evidence packet 존재만으로 current route integration 완료를 선언하지 않는다.
* focused guard test만 추가하고 official current completion gate 또는 equivalent required validation에 연결하지 않는 상태를 허용하지 않는다.
* package / export / compose route를 문서상으로만 언급하고 실제 preflight 실패 조건으로 만들지 않는 상태를 허용하지 않는다.
* approved manifest를 cutover input, successor payload, runtime payload, release input으로 표현하지 않는다.
* rejected `108` rows를 우회하거나 silent drop하지 않는다.
* old chunks와 successor chunks를 동시에 current authority로 두지 않는다.
* runtime Lua에서 validation, compose, repair, source validation, semantic quality judgment, publish policy 판단을 수행하지 않는다.
* `publish_state` predecessor-only legacy visibility disposition을 successor policy mutation으로 재개방하지 않는다.
* package route pass를 package readiness로 읽지 않는다.
* current route pass를 release readiness로 읽지 않는다.
* shared guard contract를 기존 guard surface를 대체하는 새 canonical authority로 만들지 않는다.

---

## 4. Assumptions

* 최상위 기준은 `docs/Philosophy.md`다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 Iris DVF 3-3 current readpoint를 따른다.
* `docs/EXECUTION_CONTRACT.md`의 disclosure, evidence, closeout discipline을 따른다.
* current deployable runtime authority는 existing runtime chunk manifest와 chunk files다.

```text
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua
```

* Existing runtime chunks are deployable runtime authority until a separate approved cutover.
* Existing runtime chunks are not source authority.
* Current `data/dvf_3_3_facts.jsonl`, `data/dvf_3_3_decisions.jsonl`, and `output/dvf_3_3_rendered.json` remain 6-entry fixture / non-authority surfaces.
* Prior delta disposition / guard seal evidence is read-only input. It must not be rewritten by this round.
* Existing guard surfaces retain status-specific definition roles for their owned surfaces:
  * Compose Entrypoint Guard Hardening owns the compose current write-boundary definition. The authoritative enforcement point is `compose_layer3_text.py::build_rendered()`. Its `surface_owner_status` is `sealed`.
  * Lua Bridge Export Contract Realignment owns the Lua bridge export / monolith fallback / deployable landing definition. Its `surface_owner_status` is `sealed`.
  * Stale DVF Bridge Artifact Disposition remains `implemented / review_pending / not sealed PASS` unless separately sealed. This plan may reference its package intrusion criteria as subordinate implemented evidence, but must not claim it as an independently sealed authoritative definition owner. Its `surface_owner_status` is `implemented_review_pending` and its `shared_contract_role` is `referenced_subordinate_package_guard_evidence`.
* The shared guard contract is an admission gate and aggregation surface, not a new canonical authority surface. It may reference the guard surfaces above, but must not duplicate their definitions as a competing source of truth.
* `guard_coverage_matrix.json` must record exactly one definition source for every forbidden condition, plus the status of that source.
* `guard_coverage_matrix.json` status fields are `sealed`, `implemented_review_pending`, and `subordinate_reference`.
* Stale Bridge rows in `guard_coverage_matrix.json` must use `surface_owner_status=implemented_review_pending`, `shared_contract_role=referenced_subordinate_package_guard_evidence`, and `dual_definition_verdict=no_competing_definition_but_not_independently_sealed`.
* The five non-structural forbidden conditions use the following planned definition sources unless execution evidence proves a more specific sealed source:
  * `parity-missing`: `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/runtime_parity_report.json` and the regeneration parity final contract report.
  * `disposition-coverage`: `docs/dvf_3_3_vnext_delta_disposition_policy.md`, `docs/dvf_3_3_vnext_delta_disposition_closeout.md`, and the final delta disposition guard contract report.
  * `rejected/deferred/unapproved-delta-inclusion`: `docs/dvf_3_3_vnext_delta_disposition_policy.md`, the approved manifest, and the final delta disposition guard contract report.
  * `dual-current`: `docs/dvf_3_3_vnext_cutover_contract.md`, `docs/dvf_3_3_vnext_current_authority_plan.md`, and the current authority readpoints in `docs/DECISIONS.md` / `docs/ROADMAP.md`.
  * `legacy-vocabulary`: `docs/dvf_3_3_vnext_guard_seal_contract.md`, `docs/dvf_3_3_vnext_delta_disposition_policy.md`, and the current vocabulary readpoints in `docs/DECISIONS.md`.
* Compose route guard integration must bind to `build_rendered()` in `Iris/build/description/v2/tools/build/compose_layer3_text.py`. If another file such as `compose_layer3_render.py` is involved during execution, the input contract must prove it reaches the same `build_rendered()` boundary; otherwise it is not a sufficient guard target.
* Required authoritative evidence inputs include:

```text
docs/dvf_3_3_vnext_delta_disposition_closeout.md
Iris/build/description/v2/staging/dvf_3_3_vnext_delta_disposition_guard_seal/phase10/final_delta_disposition_guard_contract_report.json
Iris/build/description/v2/staging/dvf_3_3_vnext_delta_disposition_guard_seal/phase9/approved_cutover_input_delta_manifest.json
Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/runtime_parity_report.json
Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/runtime_parity_deltas.jsonl
```

* Required evidence values are `approved=2017`, `rejected=108`, `deferred=0`, `total=2125`, `text_ko=2071`, `state=54`, and `cutover_input_usable=false`.
* Approved delta manifest is manifest/index-only. It is not rendered text, Lua bridge output, chunk payload, runtime authority, release input, or cutover authorization.
* Rejected rows block full successor candidate cutover-readiness until correction and re-parity, but they do not invalidate the prior disposition / guard seal closeout.
* Round 3 current route closure and tooling allowlist discipline remain binding. Guard integration must not expand current core module count or tooling allowlist cap by convenience.
* If any required input artifact, schema, tool, runner, or route contract is missing, validation is `blocked`, not `passed`.
* `docs/PLAN_TEMPLATE.md` and `docs/EXECUTION_CONTRACT.md` are provided as read-only review/contract surfaces for this plan. If a later closeout or review packet omits either file, template/contract conformance must be reported as author self-check only and not independently reviewed.

---

## 5. Repository Areas Affected

### Code

Expected or possible execution touch points:

* `Iris/_docs/round3/round3_run_contract_tests.py`
* `Iris/build/description/v2/tools/build/guard_dvf_3_3_vnext_output_paths.py`
* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_execution_contract.py`
* new shared guard contract / current-route integration tools under `Iris/build/description/v2/tools/build/`, only if they are executed by required validation or explicit tooling route and do not become unreviewed current taxonomy imports

### Tests

Expected or possible execution touch points:

* `Iris/build/description/v2/tests/test_dvf_3_3_vnext_delta_disposition_guard_seal.py`
* `Iris/build/description/v2/tests/test_package_layer3_chunks_only_contract.py`
* `Iris/build/description/v2/tests/test_lua_bridge_export_contract_realign.py`
* `Iris/build/description/v2/tests/test_compose_entrypoint_guard_hardening.py`
* new `Iris/build/description/v2/tests/test_dvf_3_3_vnext_delta_guard_current_route_integration.py`
* Round 3 current route contract taxonomy / required validation files under `Iris/_docs/round3/`

### Docs

Directly added by this planning step:

* `docs/dvf_3_3_vnext_delta_guard_current_route_integration_plan.md`

Expected execution docs:

* `docs/dvf_3_3_vnext_delta_guard_current_route_integration_scope_lock.md`
* `docs/dvf_3_3_vnext_delta_guard_current_route_input_contract.md`
* `docs/dvf_3_3_vnext_delta_guard_shared_contract.md`
* `docs/dvf_3_3_vnext_delta_guard_current_route_integration_closeout.md`

Read-only authority inputs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/EXECUTION_CONTRACT.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/dvf_3_3_vnext_delta_disposition_closeout.md`
* `docs/dvf_3_3_vnext_delta_disposition_guard_seal_plan.md`
* `docs/dvf_3_3_vnext_delta_disposition_policy.md`
* `docs/dvf_3_3_vnext_guard_seal_contract.md`

### Config

None expected directly.

If package / export / compose route configuration changes are required, the execution closeout must list the exact files and explain why route-level preflight could not consume the shared guard contract without config mutation.

### Generated Artifacts

All generated artifacts for this round must stay under:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/`

Expected artifact families:

* `phase1/input_contract_report.json`
* `phase1/input_fingerprint_report.json`
* `phase1/tool_path_existence_report.json`
* `phase1/no_touch_surface_manifest.json`
* `phase2/shared_guard_contract.json`
* `phase2/forbidden_scan_criteria.json`
* `phase2/guard_coverage_matrix.json`
* `phase2/guard_authority_reconciliation_report.json`
* `phase3/enforcement_wiring_report.json`
* `phase3/negative_fixture_validation_report.json`
* `phase4/current_route_required_validations.json`
* `phase4/round3_active_core_closure.delta_guard_addendum.json`
* `phase4/current_route_guard_integration_report.json`
* `phase5/package_export_compose_guard_report.json`
* `phase5/shared_criteria_drift_report.json`
* `phase5/compose_build_rendered_boundary_report.json`
* `phase6/current_route_regression_report.json`
* `phase6/package_route_report.json`
* `phase6/export_route_guard_report.json`
* `phase6/compose_route_guard_report.json`
* `phase6/lua_syntax_validation_report.txt`
* `phase6/protected_surface_no_mutation_verdict.json`
* `phase6/dual_zero_reconfirmation_report.json`
* `phase6/dynamic_forbidden_reach_report.json`
* `phase7/final_current_route_guard_integration_report.json`
* `phase7/parent_problem_handoff_report.json`
* `phase7/parent_problem_handoff_packet.md`
* `phase7/ledger_update_packet.md`
* `phase7/claim_boundary_lint_report.json`
* `phase7/executed_command_log.jsonl`

---

## 6. Planned Changes

### Change 1 - Phase 1 Scope Lock and Evidence Input Contract

Purpose:

이 라운드가 cutover가 아니라 current route guard integration임을 봉인하고, read-only로 소비할 evidence와 no-touch surface를 고정한다.

Files:

* `docs/dvf_3_3_vnext_delta_guard_current_route_integration_scope_lock.md`
* `docs/dvf_3_3_vnext_delta_guard_current_route_input_contract.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase1/input_contract_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase1/input_fingerprint_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase1/tool_path_existence_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase1/no_touch_surface_manifest.json`

Implementation Notes:

* Prior final report, approved manifest, parity report, runtime parity deltas, guard matrix, and dual-zero evidence are read-only inputs.
* Denominator requirements are `2125 = 2071 text_ko + 54 state` and `2017 approved + 108 rejected + 0 deferred = 2125`.
* `cutover_input_usable=false` must be preserved.
* The input contract records that approved manifest is index-only and may not be consumed as payload.
* Runtime chunks, Lua bridge output, facts, decisions, rendered output, and prior sealed evidence body are no-touch surfaces.
* Phase 1 must verify that required existing tools and paths resolve before any later PASS claim:
  * `Iris/build/description/v2/tools/build/guard_dvf_3_3_vnext_output_paths.py`
  * `Iris/build/description/v2/tools/build/validate_dvf_3_3_vnext_execution_contract.py`
  * `tools/check_lua_syntax.ps1`
  * `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/runtime_parity_deltas.jsonl`
  * `docs/PLAN_TEMPLATE.md`
  * `docs/EXECUTION_CONTRACT.md`
* Missing required paths close Phase 1 as `blocked`; they must not be reported as passed with a reduced validation set.
* `tool_path_existence_report.json` should record more than boolean existence where possible: `path`, `exists`, `kind`, `sha256` for files, `git_status` or tracked/untracked state when available, and `blocked_reason` when missing. Missing hash capture is not itself blocking if the path exists and the limitation is recorded.

Validation:

* input artifact presence validation
* input schema validation
* required tool / path existence validation
* required tool / path fingerprint capture, where available
* template / execution contract path validation
* denominator validation
* `cutover_input_usable=false` validation
* approved manifest index-only validation
* input fingerprint recording

---

### Change 2 - Phase 2 Shared Guard Contract and Forbidden Scan Criteria

Purpose:

8개 forbidden condition과 disposition evidence requirements를 route별 ad hoc rule이 아니라 shared guard contract로 고정하되, 기존 guard surface의 status-specific definition role을 중복 소유하지 않게 한다.

Files:

* `docs/dvf_3_3_vnext_delta_guard_shared_contract.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase2/shared_guard_contract.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase2/forbidden_scan_criteria.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase2/guard_coverage_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase2/guard_authority_reconciliation_report.json`

Implementation Notes:

The shared contract covers these forbidden conditions:

1. 6-entry fixture as current authority
2. monolith fallback re-entry
3. staging direct promotion
4. parity report missing
5. disposition coverage missing
6. rejected / deferred / unapproved delta inclusion
7. old + successor dual-current authority
8. legacy `active / silent` current-surface re-entry

The contract must distinguish current execution / package surfaces from docs, historical, diagnostic, and staging evidence references.

Authority reconciliation:

* `Compose Entrypoint Guard Hardening` remains authoritative for compose current write-boundary semantics, with `build_rendered()` as the sealed function-level boundary.
* `Lua Bridge Export Contract Realignment` remains authoritative for bridge export / monolith fallback / deployable landing semantics.
* `Stale DVF Bridge Artifact Disposition` remains implemented / review_pending unless separately sealed. This plan may reference its package intrusion criteria as subordinate implemented evidence, but must not claim it as an independently sealed authoritative definition owner.
* The shared guard contract references and aggregates those definitions for current-route admission. It must not restate the owned definitions in a way that creates a second authoritative definition.
* `guard_coverage_matrix.json` must include `forbidden_condition`, `surface_owner`, `surface_owner_status`, `authoritative_definition_source`, `shared_contract_role`, and `dual_definition_verdict`.
* Required `surface_owner_status` values are `sealed`, `implemented_review_pending`, or `subordinate_reference`.
* Required verdict for sealed / independently authoritative rows is `single_authority`.
* Required verdict for Stale Bridge rows before a separate seal is `no_competing_definition_but_not_independently_sealed`.
* Any `duplicate_authority`, `unknown_authority`, or `conflicting_authority` value blocks closeout.
* The non-structural guard rows must predeclare their `authoritative_definition_source` instead of relying on execution-time inference:
  * `parity-missing` -> regeneration parity report / final parity contract report.
  * `disposition-coverage` -> delta disposition policy / closeout / final guard contract report.
  * `rejected/deferred/unapproved-delta-inclusion` -> delta disposition policy / approved manifest / final guard contract report.
  * `dual-current` -> cutover contract / current authority plan / DECISIONS and ROADMAP current readpoints.
  * `legacy-vocabulary` -> guard seal contract / delta disposition policy / DECISIONS current vocabulary readpoints.

Validation:

* shared policy schema validation
* 8-guard coverage mapping
* guard surface status mapping validation
* Stale Bridge `implemented_review_pending` / subordinate evidence validation
* non-structural guard definition source validation
* dual-definition absence validation
* docs/reference mention non-violation validation
* historical / diagnostic / staging explicit non-current context validation
* intentional forbidden fixture fail-loud validation

---

### Change 3 - Phase 3 Enforcement Wiring First

Purpose:

Current validator / test / tool route가 shared guard contract를 실제 hard gate로 소비하게 한다.

Files:

* `Iris/_docs/round3/round3_run_contract_tests.py`
* `Iris/build/description/v2/tools/build/guard_dvf_3_3_vnext_output_paths.py`
* new current-route guard integration tool under `Iris/build/description/v2/tools/build/`
* `Iris/build/description/v2/tests/test_dvf_3_3_vnext_delta_guard_current_route_integration.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase3/enforcement_wiring_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase3/negative_fixture_validation_report.json`

Implementation Notes:

* Current route must fail if final disposition report is missing.
* Current route must fail if parity report is missing.
* Current route must fail if disposition coverage is incomplete.
* Current route must fail if approved manifest contains rejected / deferred / unapproved rows.
* Current route must fail if approved manifest contains payload body instead of index-only references.
* Current route must fail if fixture, monolith fallback, staging direct promotion, dual-current authority, or legacy vocabulary current-surface re-entry is detected.
* Negative fixtures must fail loud, not warn.
* All negative fixture injections must run under an isolated temp/staging synthetic fixture root.
* No negative fixture may write into protected current data/output/runtime/package source paths.
* If current-looking path simulation is required, it must be performed through a synthetic fixture tree or monkeypatched root resolver.
* Negative fixture reports must include a no-mutation assertion for protected current data/output/runtime/package source paths.

Validation:

* missing parity report fixture -> fail
* missing final disposition report fixture -> fail
* incomplete coverage fixture -> fail
* approved manifest containing rejected row fixture -> fail
* approved manifest containing payload body fixture -> fail
* 6-entry fixture current authority attempt -> fail
* monolith fallback re-entry fixture -> fail
* staging direct promotion fixture -> fail
* old + successor dual-current fixture -> fail
* legacy `active / silent` current writer/runtime fixture -> fail
* negative fixture root isolation validation
* protected current path no-write validation during negative fixtures
* clean current route fixture -> pass during execution

---

### Change 4 - Phase 4 Current Route Required Validation / Closure Integration

Purpose:

Guard validation이 standalone optional focused test로 남지 않도록 current route completion의 필수 조건으로 봉인한다.

Files:

* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/_docs/round3/round3_active_core_closure.delta_guard_addendum.json`
* `Iris/_docs/round3/round3_test_taxonomy.json`, only if taxonomy update is required and reviewed
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase4/current_route_guard_integration_report.json`

Implementation Notes:

* Primary gate is a required validation manifest consumed by the current route runner.
* `round3_run_contract_tests.py --class current` must load `current_route_required_validations.json` by default. A missing manifest, unreadable manifest, invalid schema, missing required artifact, missing required test id, skipped required validation, or failed required validation must make the current route return non-zero.
* The required validation manifest must include at minimum:
  * `test_dvf_3_3_vnext_delta_disposition_guard_seal.DvfVnextDeltaDispositionGuardSealTest.*`
  * package guard validation for `test_package_layer3_chunks_only_contract.PackageLayer3ChunksOnlyContractTest.*`
  * Lua bridge export guard validation for current chunk / protected destination / monolith fallback cases
  * compose `build_rendered()` boundary validation for protected write-boundary and fixture/staging rejection cases
  * required input artifact validation for final disposition report, approved manifest, parity report, and runtime parity deltas
* Required validation entries must record `id`, `kind`, `command_or_test_id`, `required=true`, `failure_policy=fail_current_route`, `expected_exit_code`, `evidence_output`, and `claim_id`.
* The delta disposition guard seal test is required validation for current completion, not an automatic current core module expansion. If execution chooses taxonomy promotion instead, it must prove no new `tools.build.*` import violates the active closure / tooling allowlist policy.
* Round 3 taxonomy / closure is updated by addendum only; no unreviewed current core module count expansion is allowed.
* Current-route tooling allowlist cap must remain intact. If a new helper is needed, the execution must prove it is tooling-route integration or required-validation execution and not current core expansion.
* Current route must fail if required guard validation is removed, skipped, or not discoverable.
* `--list` / route report output should expose required validation identities or a separate `required_validation_count` so reviewers can see that the delta guard and package guard are included in the official current completion path.

Validation:

* current route runner includes guard validation automatically
* guard validation removal / omission causes current route failure
* missing `current_route_required_validations.json` causes current route failure
* missing final disposition report, approved manifest, parity report, or runtime parity deltas causes current route failure
* delta guard seal test required-validation failure causes current route failure
* package guard required-validation failure causes current route failure
* closure report records guard integration
* closure_enforced remains true
* 12-module active build closure integrity preserved
* current-route tooling allowlist cap integrity preserved

---

### Change 5 - Phase 5 Package / Export / Compose Route Integration

Purpose:

Package, Lua bridge export, and compose/write route가 current route와 같은 forbidden scan criteria를 공유하게 한다.

Files:

* `Iris/tools/package_iris.ps1`, only if package preflight must be wired there
* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tools/build/guard_dvf_3_3_vnext_output_paths.py`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase5/package_export_compose_guard_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase5/shared_criteria_drift_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase5/compose_build_rendered_boundary_report.json`

Implementation Notes:

* Package / export / compose integration uses the shared guard contract as an admission / aggregation gate. It must not replace the existing route-specific guard owners or create a competing canonical authority.
* Package route must not silently delete or hide forbidden current-looking artifacts.
* Package guard completion cannot rely on diagnostic classification alone. The package guard test and package preflight must be included in required validation or otherwise promoted through an explicitly reviewed current/package completion gate.
* Export route must fail on monolith fallback, staging direct promotion, or approved-manifest-as-payload misuse.
* Compose route integration must bind to `compose_layer3_text.py::build_rendered()`, because that is the sealed compose current write-boundary.
* If execution finds that an external route calls `compose_layer3_render.py`, `compose_build_rendered_boundary_report.json` must prove that this route reaches the same `build_rendered()` boundary. If it does not, guarding `compose_layer3_render.py` is insufficient and the plan must retarget the guard to `build_rendered()`.
* Compose route must fail if `build_rendered()` current write boundary tries to consume 6-entry fixture as authority or promote staging rendered output.
* Route-specific reports must record either the shared criteria version / fingerprint they consumed or an equivalence fingerprint proving their existing route-specific guard matches the shared criteria for the forbidden condition it owns.
* Any route consuming a stale, missing, mismatched, or unproven shared guard contract fingerprint / equivalence fingerprint must fail route validation.
* Successor staging chunks must fail if present in package output or package source selection.
* Non-current staging chunks are allowed only outside package input/output surfaces and must be explicitly excluded from package assembly.

Validation:

* package route forbidden monolith present -> fail
* package route stale bridge / legacy 6-entry payload shape present -> fail
* package route successor staging chunks in package output -> fail
* package route successor staging chunks in package source selection -> fail
* non-current staging chunks outside package input/output and explicitly excluded from package assembly -> pass
* export route current/staging monolith export attempt -> fail
* export route approved manifest treated as payload -> fail
* compose route `build_rendered()` boundary binding proof -> pass
* compose route 6-entry fixture authority attempt through `build_rendered()` -> fail
* compose route staging rendered direct promotion through `build_rendered()` -> fail
* clean package / export / compose route -> pass during execution
* package guard present only as diagnostic and absent from required validation / package completion gate -> fail
* stale / missing / mismatched / unproven shared guard contract fingerprint or equivalence fingerprint -> fail
* shared criteria drift report shows no drift and no route consumes mismatched or unproven criteria

---

### Change 6 - Phase 6 Full-Route Validation and Dual-Zero Reconfirmation

Purpose:

Guard integration이 existing current route를 깨지 않으면서 forbidden state만 fail-loud로 차단하는지 확인한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase6/current_route_regression_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase6/package_route_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase6/export_route_guard_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase6/compose_route_guard_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase6/lua_syntax_validation_report.txt`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase6/protected_surface_no_mutation_verdict.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase6/dual_zero_reconfirmation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase6/dynamic_forbidden_reach_report.json`

Implementation Notes:

* Validation must include positive clean-route pass and negative fail-loud proof.
* Current route regression must be measured after required validation manifest enforcement is enabled. A pre-enforcement current route pass is baseline evidence only and cannot close this plan.
* Required validation must prove both the prior delta guard seal test and package route guard are included in the official completion path.
* Protected current facts / decisions / rendered output / runtime chunk surfaces must remain unchanged.
* Dual-zero means static forbidden current-surface hit count `0`, static unclassified residue count `0`, and dynamic forbidden reach count `0`.
* Allowed non-current historical / diagnostic / staging residue may exist only if classified non-current and unreachable from current route.
* Dynamic forbidden reach is measured by executing the current route runner, package guard, export guard, and compose `build_rendered()` guard against isolated synthetic forbidden fixtures. The input set must include at least fixture-as-authority, monolith fallback, staging direct promotion, missing parity, missing disposition, unapproved delta, dual-current authority, and legacy vocabulary cases. A forbidden candidate is counted as dynamic reach only if it passes preflight far enough to be admitted into a protected current writer, package assembly selection, export destination, or compose write sink. PASS requires each synthetic forbidden case to fail loud before protected sink admission, `dynamic_forbidden_reach_count=0`, and protected no-mutation unchanged.

Validation:

* Round 3 current route validation with required validation manifest enforced
* required validation manifest omission / required row omission failure validation
* package route validation, including package preflight or package guard test as a required completion gate
* export route guard validation
* compose route guard validation
* Lua syntax validation
* protected current surface no-mutation validation
* forbidden negative fixture validation
* dual-zero validation
* dynamic forbidden reach measurement validation

---

### Change 7 - Phase 7 Closeout and Ledger Packet

Purpose:

Completion claim을 `current route guard integrated`로 제한하고 additive closeout / ledger packet을 작성한다.

Files:

* `docs/dvf_3_3_vnext_delta_guard_current_route_integration_closeout.md`
* `docs/dvf_3_3_vnext_current_authority_handoff_packet.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase7/final_current_route_guard_integration_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase7/parent_problem_handoff_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase7/parent_problem_handoff_packet.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase7/ledger_update_packet.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase7/claim_boundary_lint_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/phase7/executed_command_log.jsonl`

Implementation Notes:

Closeout must say:

* delta disposition evidence is consumed by current route
* `round3_run_contract_tests.py --class current --enforce-current-build-closure` consumed `current_route_required_validations.json` and failed closed on missing / failed required validation
* delta disposition guard seal validation is included in the official current completion path
* guard validation is required for current route completion
* package guard validation is included in required validation or an explicitly reviewed package completion gate
* package / export / compose share forbidden scan criteria through direct consumption or recorded equivalence fingerprints
* fixture / monolith / staging direct promotion / parity-missing / disposition-missing / unapproved delta / dual-current / legacy vocabulary fail loud
* protected current surface no-mutation is preserved
* current route guard integrated
* parent problem handoff is prepared for `vNext Current Authority Implementation and 2105 Consumer Migration`
* parent handoff allowed inputs are limited to approved manifest as index-only reference, final disposition report, parity report / runtime parity deltas, guard coverage matrix, required validation manifest, and current route guard integration report
* parent handoff forbidden inputs include 6-entry fixture as current authority, monolith fallback, staging direct promotion, approved manifest as payload, rejected / unapproved delta inclusion, and dual-current old/successor chunks
* parent handoff next-work list is baseline manifest creation, facts / decisions / profile / overlay / input manifest reconstruction, full rendered authority regeneration, optional runtime chunk re-export / deployable authority reseal, and 2105 consumer migration ledger disposition

Closeout must not say:

* vNext successor baseline sealed
* cutover ready
* live runtime chunks replaced
* package ready
* release ready
* approved manifest is runtime payload
* rejected deltas are acceptable
* guard evidence alone was sufficient
* staging artifacts are current authority
* parent problem is solved
* current authority baseline manifest is created
* facts / decisions / profile / overlay / rendered authority has been regenerated
* 2105 consumer migration is complete

Validation:

* closeout claim lint
* parent problem handoff packet schema / claim-boundary validation
* ledger packet non-decision check
* artifact path reference check
* no-mutation boundary consistency check
* final integration report consistency check
* additive-only / prior seal immutability check

---

## 7. Validation Plan

### Automated Validation

Required command families, to be resolved into exact commands during execution:

```powershell
python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure
python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --list
python -B Iris/_docs/round3/round3_run_contract_tests.py --class historical
python -B Iris/_docs/round3/round3_run_contract_tests.py --class diagnostic
python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean -Zip
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

The first current-route command is a completion gate only after `current_route_required_validations.json` enforcement is enabled. A current-route pass before required-validation enforcement is baseline evidence, not closeout evidence.

Required validation areas:

* input artifact presence and schema validation
* required tool / path existence validation, including `guard_dvf_3_3_vnext_output_paths.py`, `validate_dvf_3_3_vnext_execution_contract.py`, `tools/check_lua_syntax.ps1`, and sealed `runtime_parity_deltas.jsonl`
* `docs/PLAN_TEMPLATE.md` / `docs/EXECUTION_CONTRACT.md` conformance check; if these files are not included in the execution review packet, closeout must say template/contract compliance was author self-check only
* input fingerprint recording
* disposition denominator validation
* approved manifest index-only validation
* shared guard contract schema validation
* shared guard contract status-aware reconciliation against Compose Entrypoint Guard Hardening, Lua Bridge Export Contract Realignment, and Stale DVF Bridge Artifact Disposition
* guard coverage matrix single-authority / implemented-review-pending validation
* 8-guard coverage validation
* current route required validation inclusion and fail-closed behavior
* `current_route_required_validations.json` schema, required row, required artifact, and required test id validation
* delta disposition guard seal test included in official current completion path
* package guard test or package preflight included in required validation / package completion gate
* negative fixture fail-loud proof
* negative fixture isolation and protected no-write proof
* package / export / compose route guard validation
* compose `build_rendered()` boundary binding validation
* stale / missing / mismatched shared guard fingerprint route-failure validation
* shared criteria drift validation as a failure gate, not advisory-only report
* protected current surface no-mutation validation
* dual-zero reconfirmation
* dynamic forbidden reach measurement with documented inputs, exercised routes, and `dynamic_forbidden_reach_count=0` verdict
* parent problem handoff validation, including allowed inputs, forbidden inputs, next-work list, and non-claim boundary for current authority implementation / 2105 migration
* closure / allowlist integrity validation
* claim boundary lint
* executed command log with working directory, command, exit code, artifact path, and validation claim id

If any required command exits non-zero, is unavailable, or cannot run because a required tool is missing, the corresponding validation is `blocked` or `failed`, not `passed`.

### Manual Validation

* scope lock review
* input contract review
* shared guard contract review
* guard authority/status reconciliation review
* forbidden scan false-positive review
* current route required validation manifest review
* closure addendum review
* compose `build_rendered()` binding review
* package / export / compose guard report review
* negative fixture matrix review
* dynamic forbidden reach report review
* closeout claim boundary review
* ledger packet review

### Validation Limits

This execution will not perform:

* no live runtime validation
* no long-session runtime validation
* no multiplayer validation
* no manual in-game QA
* no deployment validation
* no release readiness validation
* no Workshop readiness validation
* no B42 readiness validation
* no full external ecosystem compatibility sweep
* no successor baseline semantic quality review
* no rejected delta correction validation
* no re-parity after correction
* no live current chunk load validation
* no Browser / Tooltip / Wiki text review
* no public-facing description acceptance
* no frozen-2105 byte-level recovery proof

---

## 8. Risk Surface Touch

### Authority Surface

Touched in a limited way.

This plan does not replace current authority identity. It changes authority admission gates by requiring current route validation to consume prior disposition / guard evidence and reject forbidden authority pollution.

### Runtime Behavior Surface

Intended none.

Runtime Lua behavior, chunk payload, Lua bridge output, Browser behavior, Tooltip behavior, and Wiki behavior are not changed.

### Compatibility Surface

External compatibility surface: none expected.

Internal build / package route impact exists. Developer and packaging workflows may fail earlier when fixture, monolith, staging direct promotion, missing parity, missing disposition, unapproved delta, dual-current authority, or legacy vocabulary contamination appears.

### Sealed Artifact Surface

Touched as read-only input and additive evidence.

Prior delta disposition / guard seal evidence is consumed read-only. New evidence is additive under the new staging root. Previous sealed evidence body must not be rewritten.

### Public-Facing Output Surface

None.

No in-game text, README release claim, Workshop copy, Browser / Wiki / Tooltip UI, or user-facing behavior is changed by this round.

---

## 9. Risk Analysis

### Architecture Risk

* Guard evidence existence may be mistaken for current route integration.
* Approved manifest may be overread as cutover authorization or runtime payload.
* Rejected rows may be bypassed by treating approved rows as a full successor candidate.
* A shared guard contract may drift into a new authority instead of remaining an admission gate / aggregation surface.
* Shared guard contract wording may duplicate existing guard surfaces and create dual-definition authority.
* Stale DVF Bridge Artifact Disposition may be overclaimed as sealed PASS instead of implemented / review_pending subordinate evidence.
* Round 3 current closure / tooling allowlist may be expanded by convenience instead of reviewed scope.

### Runtime Risk

* Guard integration may accidentally copy staging artifacts into live runtime paths.
* Package route may include stale monolith or successor staging chunks even if current route tests pass.
* Export route may reintroduce monolith fallback as current output.
* Compose route may treat staging rendered output as current write input if it guards a surface other than `build_rendered()`.
* Runtime Lua may become a tempting place for validation or repair if build-time guard failures are not fail-loud.

### Compatibility Risk

* Shared scanner may false-positive on docs, historical, diagnostic, or staging references.
* Package / export / compose routes may consume subtly different forbidden criteria.
* A route may consume a stale or mismatched shared guard contract fingerprint unless mismatch is a failure condition.
* Current-route required validation may become an optional focused test if runner integration is incomplete.
* Tooling allowlist may become a bypass for current core closure.
* Internal package route failures may be mistaken for external runtime compatibility changes.

### Regression Risk

* Positive route may pass while negative forbidden fixtures do not fail.
* Closure report may claim guard integration while the runner can skip the guard.
* Negative fixture tests may accidentally write into protected current paths unless fixture roots are isolated.
* Protected no-mutation path set may omit a current payload file.
* Dual-zero may ignore static residue or dynamic reach if dynamic reach input / execution / verdict is not specified.
* Closeout wording may imply cutover, package readiness, release readiness, or successor baseline identity.

---

## 10. Rollback Plan

This execution must be build / validation layer only and no-live-mutation by design.

Rollback units:

* shared guard contract file
* guard authority reconciliation report
* current route runner integration
* current-route required validation manifest
* Round 3 closure addendum
* guard integration tests
* validator / test / tool preflight wiring
* package / export / compose preflight wiring
* generated staging evidence reports
* closeout / ledger packet

Rollback method:

1. Confirm protected current runtime / data / output surfaces did not change.
2. Revert current route runner integration and required validation manifest changes.
3. Revert package / export / compose route integration independently if only one route regresses.
4. Revert shared guard contract fingerprint consumption if mismatch handling blocks legitimate routes, then preserve the failed criteria report as blocked trace.
5. Preserve prior delta disposition / guard seal evidence and the existing guard-surface status records as historical read-only input.
6. Preserve new failed staging evidence as superseded or blocked trace if it was already generated.
7. If closeout was drafted but validation failed, change closeout to `blocked`, `partial`, or `implemented_only`; do not leave a success claim.

Rollback must not change:

* prior delta disposition result
* prior guard seal evidence
* rejected delta status
* `cutover_input_usable=false`
* approved manifest index-only status
* existing runtime chunk authority

Rollback terminal state returns to:

```text
disposition guard evidence complete / current-route integration pending
```

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Hub & Spoke / SPI boundaries remain untouched.
* Pulse / Core surface must not receive Iris DVF guard policy.
* Iris runtime remains render-only and must not compose, repair, source-validate, classify delta, judge quality, or decide publish policy.
* Runtime / build-time separation remains intact.
* Existing runtime chunks remain deployable runtime authority until separate approved cutover.
* Old chunks and successor chunks must not both be current authority.
* Current facts / decisions / rendered / runtime chunk payload mutation is forbidden unless a separate approved scope opens it.
* 6-entry fixture remains fixture / non-authority.
* Staging artifacts remain evidence, not deployable current authority.
* Approved manifest remains manifest/index-only and must not become payload.
* Rejected / deferred / unapproved rows must not enter current runtime / source / rendered / package / export / compose path.
* Prior sealed evidence is read-only input; additive reflection only.
* Compose Entrypoint Guard Hardening and Lua Bridge Export Contract Realignment retain authoritative ownership of their sealed surface definitions.
* Stale DVF Bridge Artifact Disposition remains implemented / review_pending unless separately sealed. It may be referenced as subordinate package-guard evidence, but must not be claimed as an independently sealed authoritative owner.
* The shared guard contract is an admission gate and aggregation surface, not a new canonical authority surface.
* `guard_coverage_matrix.json` must prove exactly one definition source per forbidden condition and record that source's `surface_owner_status`.
* Dual guard authority, unknown definition authority, conflicting definition authority, or stale bridge sealed-owner overclaim is a blocking condition.
* `publish_state` remains predecessor-only legacy visibility disposition / policy no-mutation.
* `active / silent` must not re-enter current writer / validator / runtime payload vocabulary.
* Guard failures must be fail-loud, not advisory.
* Any route consuming a stale, missing, or mismatched shared guard contract fingerprint must fail validation.
* Historical / diagnostic bypass must require explicit non-current context.
* Package / export / compose route must share forbidden scan criteria with current route.
* Compose route integration must bind to `compose_layer3_text.py::build_rendered()`. External compose helpers or validators are supplementary evidence only unless they prove they reach the same boundary.
* Negative fixtures must run only under isolated temp/staging synthetic roots or monkeypatched root resolvers; protected current paths must not be used for fixture injection.
* Guard integration must not expand Round 3 current core module closure or tooling allowlist cap by convenience.
* No generated staging evidence may be promoted by copy into current path.
* No release readiness, Workshop readiness, deployment readiness, manual in-game validation, runtime rollout, package release, public exposure, successor baseline identity final seal, or full runtime equivalence is implied.
* `COMMON-RELEASE-NONDECISION` and `COMMON-RUNTIME-SURFACE-NONMUTATION` markers are included by default in closeout / ledger packet.
* Dirty working tree safety applies: stage only files intentionally changed for this scope.

---

## 12. Expected Closeout State

Expected closeout target: `complete`, if all current route guard integration gates pass within the stated validation ceiling.

`complete` requires:

* input contract binds prior disposition closeout, final guard contract report, approved manifest, parity report, and runtime parity deltas.
* input fingerprints are recorded.
* required tool / path existence report is PASS for `guard_dvf_3_3_vnext_output_paths.py`, `validate_dvf_3_3_vnext_execution_contract.py`, `tools/check_lua_syntax.ps1`, `runtime_parity_deltas.jsonl`, `docs/PLAN_TEMPLATE.md`, and `docs/EXECUTION_CONTRACT.md`.
* denominator validation records `2125 = 2071 text_ko + 54 state`.
* disposition validation records `2017 approved + 108 rejected + 0 deferred = 2125`.
* `cutover_input_usable=false` is preserved.
* approved manifest index-only status is validated.
* shared guard contract covers all 8 forbidden conditions.
* shared guard contract is documented as an admission gate / aggregation surface, not as a replacement canonical authority.
* guard authority/status reconciliation proves Compose Entrypoint Guard Hardening and Lua Bridge Export Contract Realignment retain sealed owner status, while Stale DVF Bridge Artifact Disposition is recorded as `implemented_review_pending` / subordinate package-guard evidence unless separately sealed.
* guard coverage matrix records exactly one definition source per forbidden condition, its `surface_owner_status`, and no dual-definition conflict.
* Stale Bridge rows record `shared_contract_role=referenced_subordinate_package_guard_evidence` and `dual_definition_verdict=no_competing_definition_but_not_independently_sealed`.
* current validator / test / tool route consumes the shared guard contract as fail-loud hard gate.
* `round3_run_contract_tests.py` loads `current_route_required_validations.json` during current route execution and returns non-zero for missing / invalid / failed required validation.
* delta disposition guard seal validation is included in the official current completion path without expanding current core closure or tooling allowlist by convenience.
* guard validation is required for current route completion.
* required validation omission or missing input makes current route fail.
* package guard validation is included in required validation or an explicitly reviewed package completion gate; diagnostic-only presence is not sufficient for completion.
* package / export / compose route consumes the same forbidden scan criteria or records route-owner equivalence fingerprints against that criteria.
* stale, missing, mismatched, or unproven shared guard contract / equivalence fingerprint makes route validation fail.
* compose route integration is bound to `compose_layer3_text.py::build_rendered()` or proves any alternate route reaches that same sealed boundary.
* successor staging chunks fail if present in package output or package source selection, and are allowed only outside package input/output surfaces when explicitly excluded from package assembly.
* parent problem handoff packet is written and explicitly separates next-round allowed inputs, forbidden inputs, prerequisites, next-work list, and non-claims.
* parent problem handoff does not claim new current authority baseline creation, source-to-rendered regeneration, runtime chunk cutover, or 2105 consumer migration completion.
* positive clean route passes during execution.
* negative forbidden fixtures fail loud during execution.
* negative fixtures are isolated from protected current data/output/runtime/package source paths.
* protected current surface no-mutation verdict is PASS during execution.
* dual-zero records static forbidden current-surface hit `0`, static unclassified residue `0`, and dynamic forbidden reach `0`.
* dynamic forbidden reach report documents inputs, exercised routes, sink-admission criteria, and `dynamic_forbidden_reach_count=0`.
* Round 3 closure / tooling allowlist integrity is preserved.
* template / execution contract conformance is either independently reviewable from included `docs/PLAN_TEMPLATE.md` and `docs/EXECUTION_CONTRACT.md`, or explicitly limited as author self-check in closeout.
* final integration report is written.
* closeout is additive-only and does not rewrite previous sealed evidence.
* closeout includes `COMMON-RELEASE-NONDECISION` and `COMMON-RUNTIME-SURFACE-NONMUTATION`.
* closeout claim is limited to `current route guard integrated`.

Allowed alternate closeout states:

* `partial`: some route integration or evidence artifact exists, but one or more required phase, validation, or route binding is incomplete.
* `implemented_only`: code, docs, or tests exist, but required validation did not run.
* `blocked`: missing authority input, missing parity/disposition evidence, missing tooling, failed precondition, failed guard, protected current surface mutation, closure/allowlist integrity conflict, nondeterminism, or claim boundary conflict prevents safe completion.

No closeout state may claim:

* successor baseline identity final seal
* current cutover
* single-authority switch execution
* live runtime replacement
* live chunk replacement
* package readiness
* release readiness
* Workshop readiness
* deployment readiness
* production validation
* manual in-game validation
* full runtime equivalence
* full compatibility preservation
* public-facing behavior correctness
* public-facing text quality acceptance
* approved manifest runtime payload status
* rejected delta acceptability for cutover
* `cutover_input_usable` status change
