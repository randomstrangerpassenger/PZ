# DVF 3-3 vNext Rejected Delta Correction / Re-Parity Seal Plan

> 상태: planned / scope-lock candidate / synthesized roadmap consumed / WARN review revisions applied / R2 PASS review recommendations applied / R3 WARN revisions applied / Iris codebase feasibility notes applied / parent unlock candidate boundary applied
> 작성일: 2026-06-16
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Execution 기준: `docs/EXECUTION_CONTRACT.md`
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Roadmap input: `C:/Users/MW/.codex/attachments/9b11d70c-cad1-467e-951a-92c4a5f03ec9/pasted-text.txt` / sha256 `2E4EF0D238E23A1515EFBA7B83604F616B9E0243F50FE6EA00EDFAC7DAE13ADB` / unsealed synthesized roadmap reference, preserved only as drafting input
> Review input: `C:/Users/MW/.codex/attachments/a27f80e3-cd71-4004-a9c1-aa2a35e6c741/pasted-text.txt` / sha256 `24454560FCA7EC352F2679A94620A1FCB1CF0D533844A3B231FEC53F599E5B9C` / WARN final review reference, R1-R9 incorporated
> Review input R2: `C:/Users/MW/.codex/attachments/64ce85df-3633-40fd-b8f3-1bb38401de9a/pasted-text.txt` / sha256 `47F7B59856015EE49B6E94555B657A8CFB3CF1AA1FF018E64567DF0D47DFB309` / PASS final review reference, N1-N3 incorporated
> Review input R3: `C:/Users/MW/.codex/attachments/6edef041-0b42-4a51-9599-5ecd2b2caa75/pasted-text.txt` / sha256 `5A18509A1135AD1A6BC3E827A5BF50162FBFAB1987621C9050DF50332092E7F0` / WARN final review reference, R-A through R-C incorporated
> Prior evidence input: `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/`
> Prior parity input: `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/`
> Prior disposition input: `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_disposition_guard_seal/`
> Prior current-route gate input: `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_guard_current_route_integration/`

---

## 1. Objective

DVF 3-3 vNext successor candidate의 blocked readpoint인 `2125 total / 2017 approved / 0 deferred / 108 rejected` 상태를 본 correction/re-parity round에서 분해하고, corrected successor candidate를 staging-only로 fresh regeneration한 뒤 predecessor runtime 대비 re-parity와 re-disposition을 다시 봉인한다.

이 계획은 parent problem `2-4 vNext Current Authority Implementation and 2105 Consumer Migration`의 선행 hard gate다. 이 선행 문제는 successful terminal로 닫힐 때만 parent prerequisite unlock을 제공한다. rejected / deferred / scope exclusion / unresolved policy candidate / failed correction이 남으면 parent prerequisite unlock으로 표현하지 않는다.

이 계획의 successful terminal은 parent prerequisite unlock에 필요한 correction/re-parity 성공 terminal로 제한한다.

```text
rejected delta correction / re-parity sealed; cutover_input_usable=true candidate established
```

`cutover_input_usable=true`가 산출되더라도 이는 이 라운드가 계산한 candidate / recommended value일 뿐이다. current cutover authorization, successor baseline identity final seal, live runtime replacement authorization으로 읽지 않는다.

성공 closeout은 `rejected=0`, `deferred=0`, `scope_exclusion=0`, `unresolved_policy_candidate=0`, `cutover_input_usable=true`, `parent_problem_unlock=true`를 모두 요구한다.

non-success terminal은 다음으로 제한한다.

```text
unsuccessful_attempt_sealed;
cutover_input_usable=false;
parent_problem_unlock=false;
prior blocked readpoint remains authoritative;
failed evidence quarantined
```

이 non-success terminal은 successful closeout이 아니며 parent prerequisite unlock도 아니다. rejected / deferred / scope exclusion / unresolved policy candidate / failed correction 상태가 남으면 Phase 2 / Phase 4 / Phase 5로 되돌려 재작업할 수 있지만, 재작업으로 해소할 수 없는 evidence-insufficient / blocked / out-of-scope root cause / policy decision unavailable 상태는 위 terminal로 정직하게 봉인한다.

`parent_problem_unlock=true` means only that this prerequisite gate is satisfied for the next parent-scope round as this correction round's candidate / recommended gate result. Until an independent post-execution adversarial review accepts the evidence, it is not a self-sealed canonical unlock. It is not parent problem completion, consumer migration execution, or cutover authorization.

현재 blocked readpoint는 다음 사실을 전제로 소비한다.

* total delta: `2125`
* text axis: `text_ko 2071`
* state axis: `state 54`
* disposition result: `approved 2017 / deferred 0 / rejected 108`
* rejected decomposition: 54 key의 `state` delta 54건 + 같은 54 key의 `text_ko` delta 54건
* terminal: `complete_disposition_guard_sealed_cutover_input_blocked`
* `cutover_input_usable=false`

이 계획은 current cutover, live runtime chunk replacement, old chunks replacement, package readiness, release readiness, Workshop readiness, deployment readiness, manual in-game validation, parent problem `2-4 vNext Current Authority Implementation and 2105 Consumer Migration` 완료를 선언하지 않는다.

---

## 2. Scope

이 계획은 rejected 54 key를 key-bundle 단위로 판정하고, 오류로 판정된 successor generation input만 correction한 뒤, corrected candidate의 regeneration / re-parity / re-disposition / current-route verification / consumer migration dry-run impact를 staging evidence로 봉인하는 실행 범위를 정의한다.

Primary staging evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/`

계획 문서:

* `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_plan.md`

Expected execution docs:

* `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_scope_lock.md`
* `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_input_contract.md`
* `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_closeout.md`
* `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_ledger_packet.md`

포함 범위:

* sealed prior evidence root와 실제 artifact surface 대조
* prior final report, prior parity deltas, prior disposition ledger, prior approved manifest, current-route required validation evidence fingerprint
* rejected 108 rows를 54 key bundle로 재구성하는 inventory
* 54 key의 `state` axis primary adjudication
* `text_ko` axis dependent disposition
* correction patch manifest와 non-correction isolation
* source / decision / derivation 오류로 판정된 key의 successor generation input correction
* intended policy mutation / predecessor maintain / deferred 후보의 라운드 내 최종 처분
* `predecessor_maintain` key의 실현 메커니즘 선택과 검증
* authorized successor generation input surface allowlist
* corrected successor candidate fresh regeneration
* corrected rendered / Lua bridge / chunk candidate staging generation
* predecessor runtime chunk bundle read-only re-parity measurement
* re-parity result 기반 re-disposition seal
* prior approved 2017 output-level reconciliation
* `publish_state` B-branch persistence check
* sealed 8 guard matrix named set reconfirmation
* `cutover_input_usable` 재평가
* current route required validation freshness check, package/export/compose route guard, Lua syntax validation, protected no-mutation validation
* parent problem unlock gate 판정: successful terminal만 unlock 허용, non-success terminal은 unlock 없이 blocked evidence 봉인
* 2105 consumer migration impact dry-run
* successful closeout 또는 unsuccessful attempt closeout과 additive ledger packet 작성

### Explicitly Out Of Scope

* current cutover
* live runtime chunk replacement
* old chunks replacement
* single-authority switch execution
* package readiness declaration
* release readiness declaration
* Workshop readiness declaration
* deployment readiness declaration
* manual in-game validation
* Browser / Wiki / Tooltip behavior change
* public-facing text quality acceptance
* `quality_state`, `publish_state`, `runtime_state` redesign
* unresolved `publish_state` policy mutation 후보를 successful terminal에 포함하는 것
* unresolved intended policy mutation 후보를 successful terminal에 포함하는 것
* full 2105 consumer migration execution
* full 2-4 consumer migration execution
* successor baseline identity final seal
* frozen 2105 byte-level recovery proof
* full runtime equivalence proof
* external mod compatibility sweep
* external ecosystem compatibility claim
* legacy `active / silent` vocabulary restoration
* body_plan, compose profile, Evidence DSL, allowlist, Layer4, ACQ_DOMINANT, Acquisition Lexical, Resolver, Silent 21, Structural Signal readpoint 재개방
* monolith export current fallback restoration
* stale bridge current fallback restoration
* approved manifest를 runtime payload, chunk payload, cutover authorization, release input으로 재정의
* 일부만 적용하는 successor authority baseline 또는 일부 cutover 모델 도입
* architecture redesign
* unrelated refactor

---

## 3. Non-Goals

* 108 rejected delta를 단순히 approved로 바꾸지 않는다.
* `state` delta 원인 판정 없이 같은 key의 `text_ko` delta만 승인하지 않는다.
* unresolved policy mutation 후보를 successful terminal로 둔갑시키지 않는다.
* rejected / deferred / scope exclusion / unresolved policy candidate / failed correction을 parent prerequisite unlock으로 재포장하지 않는다.
* predecessor maintain 대상을 successor cutover input mutation으로 표현하지 않는다.
* deferred 대상을 successful closeout에 남기지 않는다.
* rejected / unapproved delta를 current runtime / source / rendered path에 주입하지 않는다.
* `cutover_input_usable=false` 상태에서 full successor candidate를 cutover-bound current authority baseline으로 표현하지 않는다.
* runtime chunks나 runtime-derived seed를 source authority로 승격하지 않는다.
* current 6-entry facts / decisions / rendered fixture를 full current authority input으로 승격하지 않는다.
* rendered-only, bridge-only, chunk-generation-only output을 current authority로 승격하지 않는다.
* old chunks와 successor chunks를 동시에 current authority로 두지 않는다.
* runtime-side compose / repair / validation / semantic quality judgment를 도입하지 않는다.
* Browser / Wiki / Tooltip 표시 정책으로 데이터 계약이나 disposition 결과를 보정하지 않는다.
* text_ko 의미 품질 acceptance, 추천, 비교, 조건부 요약, 품질 badge, trust/confidence UI를 열지 않는다.
* stale generated artifact를 corrected fresh regeneration result로 재사용하지 않는다.
* VCS tracking status를 authority status로 해석하지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 기준이다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 Iris DVF 3-3 current readpoint를 따른다.
* prior delta disposition / guard seal evidence는 read-only input이다.
* prior current-route integration seal은 current-route hard-gate readpoint로 유지한다.
* prior approved manifest는 manifest/index-only surface이며 runtime payload나 cutover authorization이 아니다.
* `108 rejected`는 108개의 독립 문제로 보지 않고, 54 key의 state/text coupled bundle로 본다.
* `state` axis가 primary adjudication axis이며, `text_ko` axis runtime eligibility는 state axis disposition에 종속된다.
* Iris codebase inspection 기준, prior rejected `state` 54건은 모두 `predecessor=adopted`, `vnext=unadopted` 방향이며 source decision pattern은 `state=silent`, `reason_code=MISSING_PRIMARY_USE`, `merge_case=cluster_absent_keep_existing`, `hard_fail_codes=role_fallback_too_hollow`로 동일하다.
* Iris codebase inspection 기준, source decisions에는 rejected 54개 외에도 `silent` non-rejected control set 21개가 있으므로 global `silent -> active` 전환은 금지한다. correction은 predecessor-adopted rejected 54-key allowlist로만 제한한다.
* Iris codebase inspection 기준, existing regeneration runner는 fixed live input manifest를 읽고 existing disposition guard builder는 blocked readpoint terminal을 전제로 하므로, corrected success round는 corrected input manifest/root parameterization과 corrected disposition success contract를 명시적으로 구현하거나 wrapper로 분리해야 한다.
* correction은 predecessor byte-level recovery가 아니라 successor source-to-runtime self-consistency 복원이다.
* `predecessor_maintain`은 label만으로 닫지 않는다. 성공 closeout 기준의 실현 방식은 `predecessor_equivalent_alignment`뿐이다. `successor_baseline_scope_exclusion`이 발견되면 successful closeout하지 않고 Phase 2/4로 되돌려 재해결하거나 non-success terminal로 봉인한다.
* predecessor runtime chunk bundle은 deployable current authority로 유지하되, 이 라운드에서는 comparison reference로만 읽는다.
* successor corrected candidate는 cutover 전까지 staging-only evidence다.
* Phase 0에서 실제 artifact filename, command invocation, staging root 내부 layout을 repository surface와 대조해 확정한다.
* 계획 본문에 적힌 command는 known candidate 또는 expected validation route이며, Phase 0 command-surface resolution이 최종 실행 기준이다.
* dirty working tree가 있으면 이 라운드의 의도된 파일만 분리해 다룬다.

---

## 5. Repository Areas Affected

### Code

* `Iris/build/description/v2/tools/build/` - correction / regeneration / parity / disposition helper가 실제로 필요할 때만 Phase 0 승인 후 변경
* `Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_regeneration_parity.py` - corrected input manifest/root를 읽을 수 있도록 parameterization 또는 corrected-round wrapper가 필요할 때만 변경
* `Iris/build/description/v2/tools/build/build_dvf_3_3_vnext_delta_disposition_guard_seal.py` - blocked-only prior terminal과 `rejected > 0` 전제를 corrected success terminal과 분리해야 할 때만 변경 또는 corrected-round builder로 대체
* `Iris/build/description/v2/tools/build/_dvf_3_3_vnext_common.py` - state normalization / source manifest loading contract를 직접 변경해야 할 때만 변경하며, global vocabulary remap은 금지
* `Iris/_docs/round3/round3_run_contract_tests.py` - Phase 9에서 current-route required validation wiring 갱신이 필요할 때만 변경

### Tests

* `Iris/build/description/v2/tests/` - rejected correction, re-parity, re-disposition, route guard regression tests가 필요할 때만 추가 또는 갱신

### Docs

* `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_plan.md`
* `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_scope_lock.md`
* `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_input_contract.md`
* `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_closeout.md`
* `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_ledger_packet.md`
* `docs/DECISIONS.md` - execution closeout 후 additive ledger update가 승인될 때만
* `docs/ARCHITECTURE.md` - execution closeout 후 current readpoint reflection이 필요할 때만
* `docs/ROADMAP.md` - execution closeout 후 next gate 반영이 필요할 때만

### Config

* `Iris/_docs/round3/current_route_required_validations.json` - Phase 9에서 새 re-disposition evidence를 current-route hard gate로 소비해야 할 때만 갱신

### Generated Artifacts

* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase0/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase1/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase2/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase3/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase4/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase6/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase7/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase9/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase10/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase11/`

Protected deployable current authority surfaces that must not be mutated without separate approval:

* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`

Protected current output surfaces that must not be mutated without separate approval:

* `Iris/build/description/v2/output/dvf_3_3_rendered.json`
* `Iris/build/description/v2/output/style_normalization_changes.jsonl`
* `Iris/build/description/v2/output/compose_requeue_candidates.jsonl`

Forbidden current-looking / monolith re-entry surfaces:

* `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`

---

## 6. Planned Changes

### Change 1 - Phase 0 Scope Lock, Evidence Intake, Fingerprint, and Command-Surface Resolution

Purpose:

* 라운드의 입력, 금지선, evidence root, command surface, output claim boundary를 고정한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase0/scope_lock.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase0/input_evidence_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase0/input_fingerprint_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase0/command_surface_resolution.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase0/codebase_feasibility_findings.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase0/corrected_round_tool_gap_resolution.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase0/authorized_successor_generation_input_surface_allowlist.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase0/sealed_guard_matrix_named_set.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase0/determinism_method.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase0/cutover_input_usability_predicate_schema.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase0/rejected_bundle_index.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase0/intake_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase0/no_mutation_precheck.json`

Implementation Notes:

* prior disposition, parity, approved manifest, current-route integration report를 read-only input으로 binding한다.
* 문제 정의에 나온 artifact 이름과 실제 sealed evidence root의 rejected-delta surface를 대조한다.
* line count, SHA256, denominator, rationale count를 capture한다.
* 108 rejected rows를 54 key bundle로 재구성하는 기준을 고정한다.
* regeneration / parity / disposition / guard / package / Lua syntax validation에 사용할 command invocation을 실제 repo surface 기준으로 확정한다.
* codebase feasibility finding을 Phase 0 evidence로 봉인한다: rejected `state` 54건의 direction은 모두 `adopted -> unadopted`, source decision pattern은 모두 `silent / MISSING_PRIMARY_USE / cluster_absent_keep_existing / role_fallback_too_hollow`, same-key `text_ko` 54건은 state-axis dependent blocked row다.
* corrected-round tool gap을 Phase 0에서 해결한다. Existing regeneration runner가 fixed live input manifest를 읽으면 corrected source manifest/root를 읽는 parameter 또는 wrapper 없이는 Phase 6으로 진행하지 않는다.
* Existing disposition guard builder가 prior blocked terminal, fixed prior counts, `rejected > 0`, `cutover_input_usable=false`를 전제로 하면 corrected-round re-disposition builder 또는 parameterized mode를 마련하기 전에는 Phase 8로 진행하지 않는다.
* correction이 쓸 수 있는 authorized successor generation input surface allowlist를 봉인한다.
* 8 guard matrix를 다음 sealed named set으로 binding한다: `fixture-as-authority`, `monolith re-entry`, `staging direct promotion`, `parity-missing`, `disposition coverage`, `unapproved delta`, `single-authority`, `legacy vocabulary`.
* determinism method는 기본적으로 동일 input double-run 후 rendered / bridge / chunk manifest / chunk files hash 비교로 고정한다. 다른 방법을 쓰려면 Phase 0에서 명시 사유와 동등성 근거를 남긴다.
* `cutover_input_usable` predicate schema를 Phase 0에서 정의하고, Phase 8/11은 이 schema를 따른다.
* `cutover_input_usability_predicate_schema.json`은 terminal별 predicate를 정의한다.
  * successful terminal: `rejected=0`, `deferred=0`, `scope_exclusion=0`, `unresolved_policy_candidate=0`, `cutover_input_usable=true`, `parent_problem_unlock=true`
  * non-success terminal: `cutover_input_usable=false`, `parent_problem_unlock=false`, prior blocked readpoint authoritative, failed evidence quarantined
* `successor_baseline_scope_exclusion`은 cutover-input exclusion으로 count하며, final count는 `0`이어야 한다.
* parent problem unlock predicate는 successful terminal과 동일하게 둔다. rejected / deferred / scope exclusion / unresolved policy candidate / failed correction evidence가 남으면 parent problem unlock은 `false`다.
* Phase 0 결과 없이 후속 phase가 fabricated path나 fabricated command를 사용하지 못하게 한다.

Validation:

* input artifact existence check
* line count / SHA256 fingerprint capture
* rejected row count check
* rejected rationale count check
* 54 key bundle bijection check
* sealed `2125 / 2017 / 0 / 108` 재확인
* dual-zero 출발값 재확인
* authorized successor generation input surface allowlist exists and is closed
* 8 guard matrix named set matches sealed names exactly
* determinism method selected before generation
* cutover usability predicate schema exists before re-disposition
* successful terminal predicate requires `rejected=0`
* successful closeout predicate requires `deferred=0`
* successful closeout predicate requires `scope_exclusion=0`
* successful closeout predicate requires `unresolved_policy_candidate=0`
* non-success terminal predicate requires `cutover_input_usable=false`
* non-success terminal predicate requires `parent_problem_unlock=false`
* non-success terminal predicate requires failed evidence quarantine
* `successor_baseline_scope_exclusion` is counted as cutover-input exclusion and final count is `0`
* parent problem unlock predicate is defined and fail-closed
* codebase feasibility findings captured and reconciled with prior evidence
* corrected-round regeneration input manifest/root parameterization or wrapper resolved
* corrected-round disposition success contract exists and is separated from prior blocked-only seal builder
* protected current surface no-mutation precheck

---

### Change 2 - Phase 1 Rejected 54-Key Bundle Inventory

Purpose:

* 108 rejected row를 54개 key 단위의 adjudication 가능한 inventory로 바꾼다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase1/rejected_54_key_inventory.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase1/rejected_54_key_inventory.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase1/state_text_pairing_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase1/silent_non_rejected_control_set.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase1/source_decision_pattern_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase1/inventory_validation_report.json`

Implementation Notes:

* 각 key에 대해 predecessor state, successor state, state delta rationale, predecessor text, successor text, text delta rationale, source / facts / decisions / derivation references를 한 row로 묶는다.
* `state` delta를 primary axis로 표시하고, 같은 key의 `text_ko` delta는 dependent axis로 표시한다.
* rejected 54 key와 rejected가 아닌 `silent` control set 21 key를 분리해 기록한다. Control set은 correction target이 아니며 unchanged sentinel로 사용한다.
* rejected 54 key의 source decision pattern이 `state=silent`, `reason_code=MISSING_PRIMARY_USE`, `merge_case=cluster_absent_keep_existing`, `hard_fail_codes=role_fallback_too_hollow`, `use_source=role_fallback`인지 검증한다.
* policy mutation 의심, predecessor maintain 의심, deferred 의심, correction 의심을 preliminary hint로만 남긴다.
* preliminary hint는 최종 disposition이 아니다.

Validation:

* 108 rejected rows to 54 key bundles exact mapping
* each bundle has one state rejected row and one text_ko rejected row
* no orphan rejected row
* no duplicate key bundle
* rejected 54 key allowlist and silent non-rejected control set are disjoint
* source decision pattern uniformity check for rejected 54 keys
* source reference presence check
* inventory schema validation

---

### Change 3 - Phase 2 State Axis Cause Adjudication

Purpose:

* 각 rejected key의 governed `state` delta를 먼저 판정한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase2/state_axis_adjudication_ledger.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase2/state_axis_adjudication_summary.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase2/source_decision_derivation_error_index.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase2/intended_policy_mutation_index.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase2/predecessor_maintain_index.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase2/predecessor_maintain_mechanism_ledger.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase2/deferred_index.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase2/state_adjudication_validation_report.json`

Implementation Notes:

* 각 key를 우선 다음 중 하나로 분류한다.
  * `source_decision_derivation_error`
  * `intended_policy_mutation`
  * `predecessor_maintain`
  * `deferred`
* `deferred`는 successful terminal class가 아니라 재판정 또는 non-success terminal 요구 상태다. successful Phase 2 completion 전에는 `source_decision_derivation_error`, `intended_policy_mutation`, `predecessor_maintain` 중 하나로 해소되어야 하며, 해소할 수 없으면 `unsuccessful_attempt_sealed` 입력으로 남긴다.
* source / decision / derivation 오류는 correction 대상이 된다.
* Phase 1 uniform pattern은 adjudication shortcut이 아니라 evidence input이다. 각 key는 동일 pattern을 공유하더라도 key별로 predecessor-adopted 상태 유지가 source decision derivation correction인지, predecessor maintain alignment인지, policy no-mutation alignment인지 명시해야 한다.
* `state_axis_adjudication_summary.md`는 각 key마다 선택된 classification뿐 아니라 왜 나머지 3개 classification이 아닌지도 짧게 기록한다.
* intended policy mutation은 이 correction / re-parity round에서 successor generation input에 채택하지 않는다.
  * `policy_mutation_rejected_no_mutation_alignment`: successor generation input에는 policy mutation을 반영하지 않고 predecessor-equivalent state로 정렬한다.
  * `policy_mutation_blocked_requires_separate_policy_surface`: no-mutation alignment가 불가능하거나 reviewer objection / evidence gap이 있으면 non-success terminal 입력으로 봉인한다.
* unresolved policy mutation candidate는 successful closeout failure이며 parent prerequisite unlock으로 표현하지 않는다.
* predecessor maintain은 successor cutover input에서 governed state mutation을 반영하지 않는 대상으로 기록하되, key별 실현 방식은 `predecessor_equivalent_alignment`만 성공 경로로 허용한다.
* `predecessor_maintain` 실현 방식은 다음으로 고정한다.
  * `predecessor_equivalent_alignment`: predecessor-equivalent state로 정렬하는 tracked patch를 만들고 `rationale=predecessor_maintain`로 error-correction과 구분한다.
* `successor_baseline_scope_exclusion`은 최종 성공 경로가 아니다. 발견되면 successful closeout하지 않고 Phase 2/4로 돌아가 predecessor-equivalent alignment로 재해결하거나 non-success terminal 입력으로 봉인한다.
* 실현 방식이 선택되지 않은 `predecessor_maintain` row는 Phase 2 validation failure다.
* `state` axis 판정 없이 `text_ko` axis를 승인하지 않는다.
* rejected 54 key 밖의 `silent` non-rejected control set을 active/adopted로 끌어올리는 판정은 금지한다.

Validation:

* 54 state delta adjudication coverage 100%
* exactly one terminal class per key
* summary records not-chosen alternatives for each key
* correction class has source / decision / derivation evidence pointer
* policy mutation class has no successor-adoption path in this round: rejected no-mutation alignment or blocked non-success terminal only
* successful terminal requires unresolved policy mutation candidate count is `0`
* predecessor maintain class has explicit mechanism: `predecessor_equivalent_alignment`
* predecessor maintain class has predecessor-state preservation note and downstream realization expectation
* no classification changes the silent non-rejected control set
* successful terminal requires deferred final count is `0`
* successful terminal requires scope exclusion final count is `0`
* adjudication ledger schema validation

---

### Change 4 - Phase 3 Text Axis Dependent Disposition

Purpose:

* 같은 key의 `text_ko` delta를 state axis disposition에 종속시켜 재판정한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase3/text_axis_dependent_disposition_ledger.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase3/text_axis_reeligibility_summary.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase3/text_axis_blocked_by_state_index.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase3/text_axis_validation_report.json`

Implementation Notes:

* state axis가 correction 대상이면 text delta를 candidate correction 후 re-disposition 대상으로 둔다.
* state axis가 `policy_mutation_rejected_no_mutation_alignment`이면 text delta는 predecessor-equivalent alignment의 dependent delta로 처리한다.
* state axis가 `policy_mutation_blocked_requires_separate_policy_surface`이면 text delta도 blocked dependent row로 남기고 successful runtime eligibility를 부여하지 않는다.
* state axis가 predecessor maintain이면 text delta는 predecessor maintain 또는 excluded successor mutation으로 묶는다.
* state axis가 deferred이면 text delta도 임시 deferred dependent row로 유지하되, Phase 2 재판정이 끝나기 전 successful closeout으로 갈 수 없다.
* 이 phase의 text result는 preliminary dependent disposition이며, 최종 runtime eligibility는 Phase 8 re-disposition에서만 확정한다.

Validation:

* 54 text_ko delta dependent disposition coverage 100%
* no text_ko approval without resolved state axis
* no text_ko runtime_eligible final mark in Phase 3
* state/text class consistency check
* predecessor maintain text handling matches selected state mechanism
* dependent ledger schema validation

---

### Change 5 - Phase 4 Correction Plan, Patch Manifest, and Non-Correction Isolation

Purpose:

* correction, policy no-mutation alignment, predecessor-maintain alignment 대상을 single-writer manifest로 만들고, unresolved policy / deferred / scope exclusion을 successful closeout 전에 제거하거나 non-success terminal 입력으로 격리한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase4/correction_patch_manifest.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase4/predecessor_maintain_realization_plan.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase4/correction_plan.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase4/non_correction_isolation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase4/blocked_policy_mutation_index.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase4/predecessor_maintain_application_index.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase4/temporary_deferred_resolution_index.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase4/patch_manifest_validation_report.json`

Implementation Notes:

* patch manifest row는 key, axis, source input path, old value, new value, adjudication reason, operation type, expected downstream effect를 포함한다.
* correction 대상은 Phase 2 `source_decision_derivation_error` class로 제한한다.
* patch manifest target key는 Phase 1 rejected 54-key allowlist의 subset이어야 한다. `silent` non-rejected control set 21 key는 patch manifest에 포함할 수 없다.
* global `silent -> active`, global `silent -> adopted`, global state vocabulary remap은 correction plan으로 허용하지 않는다.
* `predecessor_equivalent_alignment`로 선택된 `predecessor_maintain` key는 `operation_type=predecessor_maintain_alignment`, `rationale=predecessor_maintain`로 tracked patch manifest에 포함할 수 있다. 이 row는 error-correction row와 분리 집계한다.
* `successor_baseline_scope_exclusion`으로 선택된 row는 successful Phase 4 manifest로 넘어가지 않는다. 발견되면 invalidated / provisional evidence로만 기록하고 Phase 2로 되돌려 `predecessor_equivalent_alignment` 또는 explicit policy decision으로 재해결한다.
* `policy_mutation_rejected_no_mutation_alignment` row는 `operation_type=policy_no_mutation_alignment`로 predecessor-equivalent state에 정렬한다.
* `policy_mutation_blocked_requires_separate_policy_surface` row는 correction patch manifest에 포함하지 않고 `blocked_policy_mutation_index.md`와 non-success terminal evidence로 격리한다.
* predecessor maintain 대상은 `predecessor_maintain_realization_plan.jsonl`에서 selected mechanism, expected candidate effect, Phase 7/8 validation predicate를 가진다.
* deferred 대상은 successful manifest로 넘어갈 수 없으며, Phase 4 전에 correction / policy no-mutation alignment / predecessor maintain 중 하나로 재판정하거나 non-success terminal evidence로 격리한다.
* correction plan은 current runtime/output path가 아니라 authorized successor generation input surface만 대상으로 한다.

Validation:

* correction patch manifest only includes `source_decision_derivation_error`, `policy_no_mutation_alignment`, and explicitly tracked `predecessor_maintain_alignment` rows
* no `approved_policy_mutation` row in correction patch manifest
* no unresolved policy mutation row in correction patch manifest
* no deferred row in correction patch manifest
* no predecessor maintain row creates untracked successor mutation
* every predecessor maintain row has selected realization mechanism
* scope-excluded predecessor maintain rows are absent from final successful manifest because they must be reworked before closeout and final `scope_exclusion_count` must be `0`
* final unresolved policy candidate count is `0`
* final deferred count is `0`
* expected affected key count matches Phase 2 / Phase 3 ledgers
* patch target keys are subset of rejected 54-key allowlist
* silent non-rejected control set unchanged predicate exists
* no global state vocabulary remap operation exists
* protected current surface no-mutation precheck

---

### Change 6 - Phase 5 Successor Input Correction Implementation

Purpose:

* Phase 4 patch manifest에 따라 authorized successor generation input만 수정한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/corrected_input_snapshot/`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/source_input_correction_changeset.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/correction_application_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/predecessor_maintain_realization_application_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/correction_provenance.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/corrected_source_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/corrected_input_fingerprint.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/protected_surface_no_mutation_verdict.json`

Implementation Notes:

* Phase 0에서 확정된 authorized source / decision / derivation input surface에만 적용한다.
* authorized successor generation input surface allowlist 밖의 파일은 수정하지 않는다.
* current facts / decisions / rendered output / runtime chunk deployable authority는 직접 수정하지 않는다.
* corrected source manifest는 live `dvf_3_3_input_manifest.json`를 덮어쓰지 않는 staging-local manifest로 생성한다.
* source decision snapshot은 rejected 54-key allowlist에 대한 tracked row-level correction만 포함하고, silent non-rejected control set은 byte/content unchanged로 검증한다.
* `predecessor_equivalent_alignment` row는 Phase 4 manifest와 정확히 일치하는 tracked change로 적용한다.
* `successor_baseline_scope_exclusion` row는 successful Phase 5 input이 아니다. 발견되면 source value를 몰래 바꾸지 않고 invalidated / provisional evidence로만 격리한 뒤 Phase 2/4로 되돌려 재해결한다.
* correction 전후 fingerprint와 changeset을 보존한다.
* corrected input snapshot은 fresh regeneration의 유일한 input으로 사용한다.
* existing runner가 fixed input manifest를 읽는 상태라면 Phase 5는 corrected runner parameter/wrapper contract file을 생성하고 Phase 6은 그 contract만 사용한다.
* failed correction attempt는 quarantine 대상이며, 성공 evidence로 섞지 않는다.

Validation:

* patch manifest to applied changes bijection check
* authorized input surface allowlist enforcement
* corrected input schema validation
* corrected source manifest fingerprint update
* live input manifest no-overwrite check
* rejected 54-key-only mutation check
* silent non-rejected control set unchanged check
* corrected runner parameter/wrapper contract exists
* correction provenance completeness check
* predecessor maintain selected mechanism application check
* no untracked predecessor maintain state drift
* no unexpected key mutation check
* newly eligible text_ko no interpretation / recommendation / comparison check
* protected current surface no-mutation verdict

---

### Change 7 - Phase 6 Fresh Regeneration of Corrected Successor Candidate

Purpose:

* corrected input에서 rendered authority candidate, Lua bridge, chunk candidate를 fresh regeneration한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase6/rendered/dvf_3_3_rendered.vnext_corrected.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase6/bridge/IrisLayer3DataChunks.lua`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase6/bridge/IrisLayer3DataChunks/*.lua`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase6/bridge_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase6/regeneration_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase6/determinism_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase6/lua_syntax_report.json`

Implementation Notes:

* corrected source manifest를 기준으로 facts / decisions / rendered candidate를 재생성한다.
* generation command는 Phase 5 corrected source manifest/root를 명시적으로 입력으로 받아야 한다. Fixed live input manifest를 암묵적으로 읽는 invocation은 invalid다.
* corrected-round wrapper를 쓰는 경우 wrapper는 source manifest path, output root, prior runtime comparison root, no-live-output-write predicate를 report에 기록한다.
* current compose profile + body_plan contract를 사용한다.
* Lua bridge exporter는 current chunk authority contract로 staging chunk manifest + chunk files를 생성한다.
* monolith output은 생성하지 않거나 explicit diagnostic / historical side-output으로만 허용한다.
* generated candidate lineage는 `fresh_corrected_regeneration`으로 기록한다.
* determinism은 Phase 0에서 확정한 method를 따른다. 기본 method는 same input double-run hash compare이며, rendered / bridge / chunk manifest / chunk files가 모두 비교 대상이다.
* live payload와 existing chunks는 변경하지 않는다.

Validation:

* rendered schema validation
* rendered hard_fail / warn validation
* rendered / bridge / chunk double-run hash determinism check
* generation report proves corrected source manifest/root was used
* no fixed live input manifest fallback check
* Lua bridge report validation
* chunk manifest validation
* Lua syntax validation
* monolith / stale bridge forbidden scan
* protected current surface no-mutation check

---

### Change 8 - Phase 7 Re-Parity Measurement

Purpose:

* corrected successor candidate와 predecessor runtime을 다시 parity 측정한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase7/runtime_parity_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase7/runtime_parity_deltas.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase7/parity_delta_summary.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase7/prior_vs_corrected_delta_comparison.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase7/prior_approved_2017_output_reconciliation.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase7/predecessor_maintain_realization_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase7/publish_state_b_branch_persistence_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase7/parity_validation_report.json`

Implementation Notes:

* predecessor runtime chunk bundle은 deployable authority이자 comparison reference로만 읽는다.
* corrected successor candidate를 field-level로 비교한다.
* 비교 축은 최소 `key`, `text_ko`, `state`, `publish_state predecessor-only legacy visibility disposition`을 포함한다.
* prior parity report와 delta count 변화를 비교한다.
* prior approved 2017 key set을 resolve하고 regenerated output이 unchanged인지 확인한다. 변경이 있으면 모든 changed row를 enumerate하고 Phase 8 re-disposition input으로 넘긴다.
* `predecessor_maintain` key는 Phase 4 selected mechanism대로 실제 candidate에 반영됐는지 확인한다. divergent state 잔존과 untracked input 변경은 둘 다 failure다.
* `publish_state`는 predecessor-only legacy visibility disposition / B-branch로 유지되는지 확인한다. correction으로 신규 in-scope publish_state classification row가 생기면 failure다.
* remaining deltas를 axis-expanded inventory로 만든다.
* re-parity report는 frozen 2105 recovery proof나 full runtime equivalence proof가 아니다.

Validation:

* predecessor count `2105`
* successor count `2105`, 또는 변경이 있다면 explicit exclusion / predecessor-maintain 근거 필요
* missing / additional key count check
* field-level delta count check
* determinism check
* parity denominator consistency check
* parity row schema validation
* prior vs corrected delta comparison
* prior approved 2017 output-level reconciliation
* predecessor maintain candidate-realization validation
* publish_state B-branch persistence check

---

### Change 9 - Phase 8 Re-Disposition Seal

Purpose:

* re-parity 결과 기준으로 delta disposition을 다시 봉인한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/delta_disposition_ledger.corrected.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/delta_disposition_summary.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/approved_cutover_input_delta_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/rejected_remaining_index.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/deferred_remaining_index.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/prior_approved_2017_output_reconciliation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/phase3_to_phase8_text_disposition_reconciliation.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/predecessor_maintain_final_realization_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/publish_state_b_branch_persistence_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/cutover_input_usability_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/parent_problem_unlock_gate_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/non_success_terminal_candidate_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/failed_evidence_quarantine_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/final_delta_disposition_guard_contract_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase8/re_disposition_validation_report.json`

Implementation Notes:

* Phase 7 `runtime_parity_deltas.jsonl`만 disposition input으로 사용한다.
* re-disposition command는 corrected-round disposition contract를 사용한다. Prior blocked seal builder의 fixed `rejected > 0`, fixed `state_delta_count=54`, fixed `cutover_input_usable=false` predicate를 그대로 통과 조건으로 쓰면 invalid다.
* corrected success projection은 state deltas가 `0`으로 제거되고 same-key `text_ko` dependent blocked rows가 regenerated delta result에서 approved/runtime-eligible로 재판정되는지 검증하는 것이다. 실제 denominator는 Phase 7 parity result에서 계산하며 prior `2125`를 고정값으로 강제하지 않는다.
* 모든 in-scope delta를 `approved / deferred / rejected` 중 하나로 닫는다.
* correction으로 사라진 delta, predecessor-maintained delta, policy no-mutation alignment, blocked policy mutation candidate, deferred candidate를 구분한다.
* Phase 7에서 enumerated된 prior approved 2017 output drift가 있으면 모두 Phase 8에서 재처분한다. silent approved-set output drift는 허용하지 않는다.
* Phase 3 preliminary text disposition과 regenerated `text_ko` delta를 대조하고, divergence는 모두 enumerate / re-disposition한다.
* `predecessor_maintain` key는 선택된 mechanism대로 final realization을 통과해야 한다.
* `publish_state`는 predecessor-only B-branch를 유지해야 하며, new in-scope publish_state classification rows는 `0`이어야 한다.
* approved rows만 `runtime_eligible=true`로 표시한다.
* approved manifest는 계속 manifest/index-only로 생성한다.
* `cutover_input_usable`을 Phase 0 predicate schema와 새 disposition 결과로 재평가한다.
* `successor_baseline_scope_exclusion` count가 1 이상이면 Phase 2/4로 되돌아가 재해결하거나 non-success terminal 입력으로 봉인한다.
* `cutover_input_usable=true`가 산출되더라도 candidate / recommended value일 뿐 current cutover authorization, successor baseline identity final seal, live runtime replacement authorization이 아니다.
* remaining rejected / deferred / scope exclusion / unresolved policy candidate가 있으면 parent unlock successful closeout으로 가지 않는다. 재작업 가능하면 Phase 2/4/5로 돌아가고, 재작업 불가능하면 `unsuccessful_attempt_sealed` candidate를 생성한다.
* parent problem unlock gate는 successful closeout에서 반드시 `true`이고, non-success terminal에서는 반드시 `false`다.
* `parent_problem_unlock=true` means only that this prerequisite gate is satisfied for the next parent-scope round as this correction round's candidate / recommended gate result. Until an independent post-execution adversarial review accepts the evidence, it is not a self-sealed canonical unlock. It is not parent problem completion, consumer migration execution, or cutover authorization.

Validation:

* disposition coverage 100%
* approved / deferred / rejected sum equals in-scope delta denominator
* in-scope denominator derived from corrected Phase 7 parity result, not hardcoded prior total
* no prior blocked-only `rejected > 0` predicate in corrected success path
* corrected state_delta_count is `0` for successful terminal
* prior 54 state rejected keys reconcile as corrected / no-mutation aligned / predecessor-equivalent realized, not silently approved
* runtime_eligible only for approved rows
* no rejected / deferred row in approved manifest
* approved manifest index-only predicate
* cutover usability predicate check
* scope_exclusion count is `0`
* rejected count is `0`
* deferred count is `0`
* unresolved policy candidate count is `0`
* parent problem unlock gate check
* parent problem unlock candidate / recommended boundary check pending independent post-execution adversarial review
* non-success terminal validation when success predicates fail
* non-success terminal requires `cutover_input_usable=false`
* non-success terminal requires `parent_problem_unlock=false`
* non-success terminal requires prior blocked readpoint remains authoritative
* non-success terminal requires failed evidence quarantine manifest
* prior rejected row reconciliation check
* prior approved 2017 output-level reconciliation
* phase3-to-phase8 text disposition reconciliation
* predecessor maintain final realization validation
* publish_state B-branch persistence check
* newly eligible text_ko no interpretation / recommendation / comparison check
* dual-zero reconfirmation
* sealed 8 guard matrix named set reconfirmation

---

### Change 10 - Phase 9 Guard and Route Integration Verification

Purpose:

* 새 disposition evidence가 current route, package/export/compose route, Lua validation에서 fail-loud로 소비되는지 확인한다.

Files:

* `Iris/_docs/round3/current_route_required_validations.json` - 새 re-disposition evidence를 참조하거나 resolve했음을 증명해야 하며, old evidence-only pass는 허용하지 않음
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase9/current_route_required_validation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase9/required_validation_manifest_freshness_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase9/package_export_compose_route_equivalence_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase9/route_owner_equivalence_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase9/dual_zero_reconfirmation.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase9/current_route_regression_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase9/package_route_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase9/lua_syntax_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase9/protected_surface_no_mutation_verdict.json`

Implementation Notes:

* current route required validation manifest가 새 re-disposition evidence를 참조하거나 resolve하도록 확인하거나 갱신한다.
* stale prior disposition final report reference는 historical input으로 명시 보존된 경우에만 허용한다.
* Phase 8 final disposition report, Phase 8 approved manifest index-only predicate, Phase 8 cutover usability report가 참조 또는 resolve되어야 한다.
* old evidence-only pass는 실패로 처리한다.
* required artifact checks를 새 final report / approved manifest / cutover usability report 기준으로 수행한다.
* package/export/compose route-owner equivalence fingerprint를 재확인한다.
* rejected / unapproved delta ingress negative case를 유지한다.
* protected no-mutation boundary를 재검증한다.
* compose write boundary와 shared guard가 유지되는지 확인한다.
* current core closure와 current-route tooling allowlist cap을 convenience로 확장하지 않는다.

Validation:

* current route required validations pass
* required validation manifest freshness check
* no stale prior disposition final report reference unless explicitly preserved as historical input
* Phase 8 final disposition report referenced or resolved
* Phase 8 approved manifest index-only predicate referenced or resolved
* Phase 8 cutover usability report referenced or resolved
* no old evidence-only pass accepted
* current core closure unchanged
* current-route tooling allowlist cap unchanged
* package/export/compose route-owner equivalence pass
* forbidden scan criteria shared
* dual-zero reconfirmation
* Lua syntax validation
* protected no-mutation verdict
* historical / diagnostic route remains separated
* v2 unittest discovery remains valid

---

### Change 11 - Phase 10 Consumer Migration Impact Recheck

Purpose:

* corrected disposition이 2105 consumer migration input에 주는 영향을 dry-run으로 재확인한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase10/consumer_migration_impact_matrix.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase10/consumer_migration_dry_run.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase10/blocked_policy_candidate_impact.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase10/migration_validation_report.json`

Implementation Notes:

* prior 2105 Baseline Consumption Audit의 change-required rows를 read-only input으로 사용한다.
* correction-only rows, policy no-mutation alignment rows, migration-required rows를 구분한다.
* blocked policy mutation candidate가 consumer migration에 미치는 영향은 별도 matrix로 분리하되, successor input 반영이나 policy approval로 표현하지 않는다.
* 2105 consumer migration 실행은 parent problem 범위이므로 수행하지 않고 dry-run만 한다.
* numeric replacement나 vocabulary 치환을 authority migration으로 취급하지 않는다.
* current hard gate row 변경은 후속 scope가 필요하다고 남긴다.

Validation:

* migration input source check
* dry-run only check
* `mutation_performed=false`
* `forbidden_changes_count=0`
* blocked policy candidate impact rows explicitly isolated
* current hard gate change proposals require later scope

---

### Change 12 - Phase 11 Ledger Packet and Closeout

Purpose:

* correction / re-parity / re-disposition 결과를 ledger 반영 가능한 packet으로 정리한다.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase11/final_rejected_delta_correction_reparity_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase11/closeout_report.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase11/ledger_update_packet.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase11/claim_boundary_check.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase11/parent_problem_unlock_gate_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase11/unsuccessful_attempt_report.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase11/blocking_cause_index.md`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase11/failed_evidence_quarantine_manifest.json`
* `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase11/final_validation_summary.md`
* `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_closeout.md`
* `docs/dvf_3_3_vnext_rejected_delta_correction_reparity_ledger_packet.md`

Implementation Notes:

* successful final claim을 `rejected delta correction / re-parity sealed; cutover_input_usable=true candidate established`로 제한한다.
* non-success final claim은 `unsuccessful_attempt_sealed; cutover_input_usable=false; parent_problem_unlock=false; prior blocked readpoint remains authoritative; failed evidence quarantined`로 제한한다.
* successful terminal에서는 remaining rejected / deferred / scope exclusion / unresolved policy candidate가 없음을 명시한다.
* non-success terminal에서는 remaining rejected / deferred / scope exclusion / unresolved policy candidate / failed correction 중 무엇이 blocking cause인지 명시한다.
* `cutover_input_usable` 최종 값을 새 disposition 결과 기준으로 선언한다.
* `cutover_input_usable=true`가 산출되면 candidate / recommended value임을 명시하고, current cutover authorization, successor baseline identity final seal, live runtime replacement authorization이 아님을 반복한다.
* Phase 11 ledger packet과 closeout 첫 문단에 다음 문장을 포함한다: `This value is a correction-round usability predicate result, not a cutover authorization.`
* parent problem unlock 여부를 별도 필드로 선언한다. successful closeout에서는 반드시 `parent_problem_unlock=true`이고 non-success terminal에서는 반드시 `parent_problem_unlock=false`다.
* Phase 11 ledger packet과 closeout에 다음 문장을 포함한다: `parent_problem_unlock=true means only that this prerequisite gate is satisfied for the next parent-scope round as this correction round's candidate / recommended gate result. Until an independent post-execution adversarial review accepts the evidence, it is not a self-sealed canonical unlock. It is not parent problem completion, consumer migration execution, or cutover authorization.`
* successor baseline identity final seal 여부는 선언하지 않는다.
* current cutover, live runtime replacement, package readiness, release readiness는 명시적으로 non-decision으로 둔다.
* DECISIONS / ARCHITECTURE / ROADMAP 반영 초안을 additive ledger packet으로 작성한다.
* sealed body 재작성 없이 후속 반영 가능한 packet만 제공한다.

Validation:

* final report claim boundary check
* required deliverables existence check
* no contradiction with current-route guard
* no current surface mutation
* cutover usability predicate trace
* `cutover_input_usable=true` candidate boundary check
* parent problem unlock gate check
* parent problem unlock candidate / recommended boundary check pending independent post-execution adversarial review
* successful terminal no remaining rejected / deferred / scope exclusion / unresolved policy candidate check
* non-success terminal parent_problem_unlock=false check
* non-success terminal cutover_input_usable=false check
* non-success terminal prior blocked readpoint remains authoritative check
* failed evidence quarantine manifest check
* ledger first paragraph includes correction-round usability predicate / not cutover authorization sentence
* ledger packet consistency check
* additive-only update check

---

## 7. Validation Plan

### Automated Validation

Phase 0에서 실제 command surface를 확정한다. 현 문서 기준 known candidate validation route는 다음이다.

* `python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure`
* `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py"`
* `powershell -ExecutionPolicy Bypass -File ./Iris/tools/package_iris.ps1 -Clean -Zip`
* `powershell -ExecutionPolicy Bypass -File ./tools/check_lua_syntax.ps1`

Phase-specific validation categories:

* input artifact existence and SHA256 fingerprint validation
* authorized successor generation input surface allowlist validation
* sealed 8 guard matrix named set validation
* rejected row count and 54-key bundle bijection validation
* rejected 54-key allowlist / silent non-rejected control set disjoint validation
* state axis adjudication coverage validation
* text axis dependent disposition validation
* predecessor maintain mechanism and realization validation
* correction patch manifest schema and class-boundary validation
* correction patch target subset-of-rejected-54 validation
* no global `silent -> active` / `silent -> adopted` vocabulary remap validation
* silent non-rejected control set unchanged validation
* corrected source manifest fingerprint validation
* corrected runner parameter/wrapper contract validation
* corrected generation report proves staging-local corrected manifest/root was used
* rendered schema / hard_fail / warn validation
* rendered / bridge / chunk double-run hash determinism validation
* Lua bridge export contract validation
* chunk manifest and chunk file validation
* predecessor runtime parity validation
* prior approved 2017 output-level reconciliation validation
* publish_state B-branch persistence validation
* Phase 3 preliminary text disposition to Phase 8 final disposition reconciliation
* re-disposition coverage validation
* corrected re-disposition contract validation: no blocked-only hardcoded `rejected > 0` predicate, no hardcoded prior denominator, successful terminal permits `rejected=0`
* approved manifest index-only predicate validation
* cutover input usability predicate validation
* scope_exclusion final count `0` validation
* parent problem unlock gate validation
* parent problem unlock candidate / recommended boundary validation pending independent post-execution adversarial review
* current route required validation freshness validation
* current route regression validation
* package/export/compose route guard validation
* protected current surface no-mutation validation
* dual-zero reconfirmation
* sealed 8 guard matrix named set reconfirmation
* consumer migration dry-run validation

### Manual Validation

* review Phase 2 state axis adjudication rationale for all 54 keys
* review Phase 2 not-chosen alternative rationale for each key
* review Phase 3 text axis dependent disposition for state/text coupling errors
* review Phase 4 correction patch manifest before applying correction
* review Phase 8 `cutover_input_usable` predicate trace before closeout
* review Phase 11 claim boundary and non-decision language before ledger packet use

Manual validation does not include in-game QA, release QA, Workshop validation, Browser / Wiki / Tooltip behavior validation, or public-facing text quality acceptance.

### Validation Limits

* no live runtime replacement validation
* no current cutover validation
* no single-authority switch execution validation
* no manual in-game validation
* no Workshop validation
* no release readiness validation
* no deployment validation
* no long-session runtime validation
* no multiplayer validation
* no external ecosystem compatibility sweep
* no public-facing copy quality acceptance
* no Browser / Wiki / Tooltip behavior validation
* no full 2-4 consumer migration execution validation
* no full runtime equivalence validation
* no frozen 2105 byte-level recovery validation
* no package readiness validation beyond package route guard execution

---

## 8. Risk Surface Touch

### Authority Surface

Touched.

* successor generation input 일부가 수정될 수 있다.
* 수정 대상은 source / decision / derivation 오류로 판정된 key에 한정한다.
* delta disposition, runtime eligibility, approved manifest index-only predicate, cutover input usability predicate를 새 evidence 기준으로 재평가한다.
* successor baseline identity final seal과 current cutover authority는 만지지 않는다.

### Runtime Behavior Surface

Direct runtime mutation 없음.

* live runtime chunks는 변경하지 않는다.
* runtime Lua는 새 판단을 수행하지 않는다.
* Browser / Wiki / Tooltip 동작 변경은 이 라운드의 목표가 아니다.
* corrected successor candidate는 staging evidence로만 생성한다.

### Compatibility Surface

Direct external compatibility mutation 없음.

* policy mutation approval은 이 라운드에서 수행하지 않는다. blocked policy candidate는 successor input 반영 없이 non-success evidence 또는 별도 policy surface input으로만 기록한다.
* consumer migration execution은 수행하지 않는다.
* legacy / historical / diagnostic route는 current correction 대상이 아니다.

### Sealed Artifact Surface

Existing sealed artifacts: read-only / unchanged.

New staging evidence: generated and later sealed as additive evidence.

* rejected 54-key inventory
* state-axis adjudication ledger
* text-axis dependent disposition ledger
* correction patch manifest
* corrected input snapshot
* regenerated rendered candidate
* regenerated Lua bridge candidate
* regenerated chunk candidate
* re-parity report
* re-disposition ledger
* cutover input usability report
* current route validation report
* consumer migration dry-run report
* final closeout report
* ledger update packet

### Public-Facing Output Surface

Direct public-facing mutation 없음.

* user-facing text candidate가 바뀌더라도 이 라운드에서는 staging evidence로만 검증한다.
* public-facing description quality acceptance, release note, Workshop page, public rollout wording은 scope 밖이다.

---

## 9. Risk Analysis

### Architecture Risk

* source-to-runtime authority chain을 깨고 rendered-only / bridge-only / chunk-only correction을 수행할 위험이 있다.
* approved manifest를 runtime payload나 cutover authorization처럼 오해할 위험이 있다.
* current-route guard를 correction round 편의에 맞춰 약화할 위험이 있다.
* current-route tooling allowlist가 convenience로 확장될 위험이 있다.
* sealed predecessor evidence와 corrected evidence가 섞여 authority readpoint가 흐려질 위험이 있다.
* `predecessor_maintain` label이 실제 candidate realization 없이 봉인될 위험이 있다.
* `cutover_input_usable=true` candidate가 cutover authorization처럼 오해될 위험이 있다.
* corrected regeneration이 staging-local corrected manifest가 아니라 fixed live input manifest를 암묵적으로 읽어 성공 evidence를 위조할 위험이 있다.
* corrected re-disposition이 prior blocked-only guard builder의 hardcoded terminal을 재사용해 `rejected=0` success contract를 표현하지 못할 위험이 있다.

### Runtime Risk

* staging successor chunks를 live runtime authority처럼 취급할 위험이 있다.
* old chunks와 successor chunks를 동시에 current authority로 둘 위험이 있다.
* runtime Lua에 compose / repair / validation 책임을 열 위험이 있다.
* protected current runtime chunk path가 correction 과정에서 실수로 변경될 위험이 있다.

### Compatibility Risk

* intended policy mutation을 untracked correction으로 위장해 consumer migration impact를 누락할 위험이 있다.
* policy mutation impact dry-run이 full consumer migration approval처럼 읽힐 위험이 있다.
* predecessor maintain과 deferred를 혼동해 후속 migration input이 오염될 위험이 있다.
* `publish_state` predecessor-only B-branch가 correction side-effect로 흔들릴 위험이 있다.
* legacy `active / silent` vocabulary가 current writer / runtime vocabulary로 되살아날 위험이 있다.

### Regression Risk

* `state` delta 원인 판정 없이 `text_ko` delta를 승인할 위험이 있다.
* corrected input patch가 예상 외 key에 영향을 줄 위험이 있다.
* global `silent -> active` 또는 `silent -> adopted` 변경으로 rejected 54 key 밖의 silent non-rejected control set 21 key가 오염될 위험이 있다.
* prior approved 2017 set의 regenerated output이 silent 변경될 위험이 있다.
* non-deterministic regeneration 또는 re-parity가 발생할 위험이 있다.
* remaining rejected / deferred가 있는데 `cutover_input_usable=true`로 봉인할 위험이 있다.
* current route required validation manifest가 old evidence를 계속 참조할 위험이 있다.
* package/export/compose route가 서로 다른 forbidden scan criteria를 사용할 위험이 있다.
* generated staging evidence가 ignored 상태라는 이유로 검토 불가능해질 위험이 있다.

---

## 10. Rollback Plan

이 라운드는 live runtime mutation을 수행하지 않으므로 rollback은 protected current surface 보존과 staging evidence invalidation을 기본으로 한다.

* current runtime chunks는 변경하지 않는다.
* current facts / decisions / rendered output은 직접 변경하지 않는다.
* staging root 단위로 correction evidence를 폐기하거나 재생성할 수 있게 한다.
* successor source input correction은 single-writer changeset으로 관리하고, 수정 전후 fingerprint를 보존한다.
* Phase 5 이후 correction input이 잘못됐다고 판정되면 corrected input snapshot과 derived rendered / bridge / chunks를 전부 invalidated 상태로 표시하고 Phase 2/4/5로 되돌아간다.
* `predecessor_maintain` selected mechanism이 실제 candidate에 반영되지 않으면 successful closeout하지 않고 Phase 2/4/5로 되돌아가거나 non-success terminal로 봉인한다.
* prior approved 2017 output-level reconciliation에서 silent drift가 발견되면 drift rows를 Phase 8 re-disposition input으로 보내거나 Phase 2/4/5로 되돌아간다.
* `publish_state` B-branch persistence check가 실패하면 correction evidence를 cutover input으로 소비하지 않는다.
* Phase 8 re-disposition이 실패하면 prior disposition seal을 current blocked readpoint로 유지하되, successful closeout을 하지 않고 새 evidence를 invalidated attempt로 격리한 뒤 재작업하거나 `unsuccessful_attempt_sealed`로 봉인한다.
* current route validation manifest가 잘못 갱신되었으면 이전 integration seal 기준으로 되돌리고, 새 correction evidence는 required validation input으로 소비하지 않는다.
* protected surface mutation이 감지되면 라운드를 fail-close하고 mutation diff를 revert한다.
* 판정 불가 / 정합 실패 / determinism 실패가 발생하면 무리하게 `rejected=0`을 만들지 않고, 같은 라운드 안에서 재판정 또는 correction을 반복하거나 `unsuccessful_attempt_sealed`로 봉인한다.
* 실패 상태는 새 prerequisite 정의로 넘기지 않고, 이 라운드의 invalidated attempt / retry evidence로만 관리한다.
* 실패 상태는 rollback / invalidated attempt로 기록할 수 있고, successful closeout이 아닌 non-success terminal로만 선언할 수 있다.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance를 유지한다.
* Iris는 JVM+Lua 혼용 없이 100% Lua runtime 표시 계층으로 유지한다.
* DVF 3-3 successor authority chain은 `source manifest -> facts -> decisions -> compose profile + body_plan -> rendered -> Lua bridge -> chunk manifest + chunk files`로만 성립한다.
* `body_plan`은 compose profile alias이며 second authority가 아니다.
* predecessor runtime chunks는 comparison reference / migration input으로만 읽는다.
* runtime-derived seed와 runtime chunks는 source authority가 아니다.
* runtime은 compose / repair / source validation / semantic quality judgment / publish policy 판단을 수행하지 않는다.
* successor staging output은 cutover 전까지 current runtime authority가 아니다.
* existing predecessor chunks는 후속 cutover 전까지 deployable runtime authority다.
* old chunks와 successor chunks를 동시에 current authority로 둘 수 없다.
* cutover는 별도 승인된 single-authority switch로만 가능하다.
* approved delta manifest는 manifest/index-only로 유지한다.
* approved manifest를 runtime payload, chunk payload, cutover authorization, release input처럼 표현하지 않는다.
* `cutover_input_usable=true`가 산출되더라도 candidate / recommended value일 뿐이며 current cutover authorization, successor baseline identity final seal, live runtime replacement authorization이 아니다.
* `cutover_input_usable=true candidate established` terminal은 `rejected=0`, `deferred=0`, `scope_exclusion=0`, `unresolved_policy_candidate=0`, `parent_problem_unlock=true`일 때만 허용된다.
* `successor_baseline_scope_exclusion`은 cutover-input exclusion으로 count한다.
* parent problem `2-4 vNext Current Authority Implementation and 2105 Consumer Migration` unlock은 이 단일 successful terminal에서만 허용된다.
* remaining rejected / deferred / scope exclusion / unresolved policy candidate / failed correction 상태는 successful closeout으로 표현하지 않는다. 남는 경우 `unsuccessful_attempt_sealed` non-success terminal로만 봉인한다.
* rejected / unapproved delta를 current runtime / source / rendered path에 넣지 않는다.
* `state` delta 원인 판정 없이 `text_ko` delta만 승인하지 않는다.
* `predecessor_maintain`은 `predecessor_equivalent_alignment` 실현 메커니즘 없이는 successful sealed disposition이 될 수 없다.
* global `silent -> active` 또는 `silent -> adopted` vocabulary remap은 금지한다. Correction은 rejected 54-key allowlist의 tracked row-level change로만 수행한다.
* rejected 54-key 밖의 silent non-rejected control set은 unchanged sentinel로 유지한다.
* prior approved 2017 output drift는 silent accepted state가 될 수 없고, unchanged 증명 또는 enumerate + re-disposition을 거쳐야 한다.
* `publish_state` axis는 predecessor-only legacy visibility disposition으로 유지하며, 이번 라운드에서 숨김 삭제나 policy mutation으로 재해석하지 않는다.
* correction 이후 new in-scope `publish_state` classification rows는 `0`이어야 한다.
* current 6-entry facts / decisions / rendered fixture는 full current authority input으로 승격하지 않는다.
* monolith export, stale bridge, staging direct promotion, package-only snapshot, parity-missing promotion은 계속 fail-loud 대상이다.
* 8 guard matrix는 `fixture-as-authority`, `monolith re-entry`, `staging direct promotion`, `parity-missing`, `disposition coverage`, `unapproved delta`, `single-authority`, `legacy vocabulary` named set으로만 reconfirm한다.
* current-route tooling allowlist는 convenience bypass가 아니다.
* VCS tracking status는 authority status가 아니다.
* 선행 sealed decision은 read-only input으로 소비하며, 본 라운드 결과는 additive supersession / ledger packet으로만 반영한다.
* Pulse / Hub & Spoke 구조는 건드리지 않는다.
* 이 라운드는 parent problem `2-4 vNext Current Authority Implementation and 2105 Consumer Migration` 전체 완료를 선언하지 않는다.

---

## 12. Expected Closeout State

Expected closeout target: complete with either successful prerequisite unlock or honest non-success attempt seal.

There is only one successful closeout terminal:

```text
rejected delta correction / re-parity sealed; cutover_input_usable=true candidate established
```

This terminal is not current cutover authorization, not successor baseline identity final seal, and not live runtime replacement authorization.

This terminal additionally requires `rejected=0`, `deferred=0`, `scope_exclusion=0`, `unresolved_policy_candidate=0`, `cutover_input_usable=true`, and `parent_problem_unlock=true`.

There is also one non-success terminal:

```text
unsuccessful_attempt_sealed;
cutover_input_usable=false;
parent_problem_unlock=false;
prior blocked readpoint remains authoritative;
failed evidence quarantined
```

This terminal is not a successful closeout, not parent prerequisite unlock, not parent problem completion, not consumer migration execution, and not cutover authorization. It exists only to preserve FAIL-LOUD finite evidence handling when rejected / deferred / scope exclusion / unresolved policy candidate / failed correction cannot be honestly resolved inside this correction round.

`parent_problem_unlock=true` means only that this prerequisite gate is satisfied for the next parent-scope round as this correction round's candidate / recommended gate result. Until an independent post-execution adversarial review accepts the evidence, it is not a self-sealed canonical unlock. It is not parent problem completion, consumer migration execution, or cutover authorization.

Successful closeout 조건:

* rejected 54 key가 모두 classification coverage를 가진다.
* 각 key는 correction / policy no-mutation alignment / predecessor maintain 중 하나로 성공 처분된다.
* `state` axis disposition 없이 `text_ko` axis가 승인되지 않는다.
* source / decision / derivation 오류는 successor generation input에서 수정된다.
* policy mutation candidate는 successful path에서 `policy_mutation_rejected_no_mutation_alignment`로만 닫힌다. successor adoption이 필요하면 `policy_mutation_blocked_requires_separate_policy_surface`로 non-success terminal에 기록한다.
* predecessor maintain 대상은 `predecessor_equivalent_alignment` mechanism을 갖고, Phase 7/8에서 실제 candidate realization을 통과한다.
* deferred final count는 `0`이다.
* scope exclusion final count는 `0`이다.
* unresolved policy candidate count는 `0`이다.
* corrected successor candidate가 fresh regeneration된다.
* corrected regeneration은 staging-local corrected source manifest/root를 명시적으로 입력으로 사용하며 fixed live input manifest fallback을 쓰지 않는다.
* corrected rendered / Lua bridge / chunk candidate가 deterministic하게 생성된다.
* predecessor runtime과 corrected successor candidate의 re-parity report가 생성된다.
* prior approved 2017 set은 unchanged로 증명되거나, 변경 row가 전부 enumerate되어 re-disposition된다.
* Phase 3 preliminary text disposition과 Phase 8 final regenerated text disposition의 divergence가 전부 enumerate / re-disposition된다.
* `publish_state`는 predecessor-only B-branch를 유지하고 new in-scope publish_state classification rows는 `0`이다.
* re-disposition ledger가 새 parity result 기준으로 100% coverage를 가진다.
* corrected re-disposition은 prior blocked-only builder의 hardcoded `rejected > 0`, prior fixed denominator, `cutover_input_usable=false` predicate를 success path로 재사용하지 않는다.
* approved manifest는 manifest/index-only predicate를 계속 통과한다.
* current route required validations가 새 evidence 기준으로 통과한다.
* current-route required validation manifest freshness check가 통과하고 old evidence-only pass가 거부된다.
* `cutover_input_usable=true candidate established`가 선언되는 경우 `rejected=0`, `deferred=0`, `scope_exclusion=0`, `unresolved_policy_candidate=0`이 모두 증명된다.
* parent problem unlock gate는 `true`로 봉인되지만, independent post-execution adversarial review 전에는 candidate / recommended gate result이며 self-sealed canonical unlock이 아니다.
* package/export/compose route guard가 통과한다.
* Lua syntax validation이 통과한다.
* protected current surface no-mutation verdict가 통과한다.
* consumer migration impact는 dry-run / identification 수준으로만 분리된다.
* successful final closeout claim은 `rejected delta correction / re-parity sealed; cutover_input_usable=true candidate established`로 제한된다.

Non-success terminal 조건:

* `cutover_input_usable=false`로 봉인된다.
* `parent_problem_unlock=false`로 봉인된다.
* prior blocked readpoint remains authoritative를 명시한다.
* failed / blocked evidence quarantine manifest를 가진다.
* rejected / deferred / scope exclusion / unresolved policy candidate / failed correction 중 blocking cause를 기록한다.
* approved manifest를 runtime payload, cutover authorization, release input으로 표현하지 않는다.
* current cutover, successor baseline identity final seal, live runtime replacement, parent 2-4 completion을 선언하지 않는다.

이 closeout이 complete여도 다음은 선언하지 않는다.

* parent 2-4 completion
* successor baseline identity final seal
* current cutover
* live runtime chunk replacement
* old chunks replacement
* single-authority switch execution
* package readiness
* release readiness
* Workshop readiness
* deployment readiness
* manual in-game validation pass
* public-facing text quality acceptance
* Browser / Wiki / Tooltip behavior change
* full runtime equivalence
* frozen 2105 byte-level recovery
* consumer migration execution
* policy mutation approval and full consumer migration execution
