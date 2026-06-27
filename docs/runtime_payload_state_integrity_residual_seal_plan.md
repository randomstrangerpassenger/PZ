# Runtime Payload State Integrity Residual Seal Plan

> Status: planned / review revisions incorporated / bounded / governance-only / no runtime mutation / final seal blocked until author selection and external review
> 작성일: 2026-06-27
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Roadmap input sha256: `9EC36A2286BD4CFACCDE270C82B44520D5AEC47B477433B966C9CB60B0653E4E`
> Review input cycle 1 sha256: `64EFAD7EFE19C53D197CEDE86DEFC6751427C7868CD7460B458250E671575D4A`
> Review input cycle 2 sha256: `E65F23F2DFACFE5C97A374DF79A5A14A5A5E98EEFBC29784A45CC7D92394CF4D`
> Existing guard tool: `Iris/build/description/v2/tools/build/runtime_payload_state_integrity.py`
> Existing guard test: `Iris/build/description/v2/tests/test_runtime_payload_state_integrity.py`
> Existing evidence root: `Iris/build/description/v2/staging/runtime_payload_state_integrity/`

---

## 1. Objective

`Runtime Payload State Integrity Residual Seal`을 구현 변경 라운드가 아니라 final governance seal 라운드로 실행한다.

현재 코드베이스 기준으로 runtime payload shape guard는 이미 `runtime_payload_state_integrity.py`와 required-validation manifest에 연결되어 있다. 해당 guard는 live current runtime, package peer runtime, candidate bridge runtime을 current-like surface로 읽고, predecessor rollback snapshot을 historical surface로 분리한다. 또한 current runtime `2105` rows, current `unadopted` `21` rows, current-like `publish_state` row `0`, current-like forbidden/unclassified row `0`, predecessor residue `2`건을 다룬다.

이 계획의 목적은 그 guard PASS를 final residual seal PASS로 과대 해석하지 않고, 남은 `pending_author_selection`과 `blocked_external_gate`를 닫기 위한 author decision, no-mutation verification, independent review, final claim boundary, optional current-route governance adoption 절차를 문서화하는 것이다.

이 계획 자체는 independent-review gate를 충족하지 않는다. Phase 1-3 inventory / redrive / residue confinement 준비는 가능하지만, `canonical_residual_seal_allowed=true`는 author-owned seal-closing decision과 비-self independent/external review PASS 전까지 금지한다.

완료 claim은 다음 범위로 제한한다.

```text
Runtime Payload State Integrity Residual Seal is complete only when payload shape guard PASS, author-owned policy confirmation, predecessor residue historical-only disposition, protected-surface no-mutation evidence, guard predicate freeze evidence, and independent/external review PASS are all present.
```

---

## 2. Scope

이 계획은 runtime payload guard completion과 residual final seal completion을 분리하고, residual seal에 필요한 governance evidence와 문서/검증 연결을 정리한다.

포함 범위:

* existing payload shape guard readpoint 재확인
* `pending_author_selection` / `blocked_external_gate` inventory
* current-compatible `unadopted + text_ko` 금지 정책 confirmation
* current-compatible `unadopted + publish_state` 금지 정책 confirmation
* predecessor rollback residue 2건의 historical-only disposition
* `current_like_denominator ∩ predecessor_residue = ∅` disjointness 증명
* protected no-mutation surface manifest 작성
* source / rendered / Lua bridge / runtime chunk / package payload no-mutation verification
* existing guard predicate freeze 및 guard tool/test hash coverage
* author decision admissibility schema 작성
* independent / external review admissibility schema 작성
* final residual seal report와 claim boundary 작성
* optional current-route governance adoption decision rule 작성
* optional additive ledger / roadmap / architecture packet 작성

### Explicitly Out Of Scope

* runtime payload row 수정
* source facts / decisions / overlay mutation
* rendered output regeneration
* Lua bridge export mutation
* runtime chunk replacement
* package payload mutation
* predecessor residue cleanup mutation
* `unadopted` row 삭제 또는 `adopted` 전환
* `publish_state`, `quality_state`, `runtime_state` 의미 확장
* Browser / Wiki / Tooltip behavior change
* renderer policy change
* live migration execution
* current authority cutover reopen
* current-route rebuild / regeneration
* package / release / Workshop / B42 / deployment readiness 선언
* manual in-game QA 또는 public-facing text acceptance
* full clean-checkout required-evidence reproducibility
* full historical artifact byte reproducibility

---

## 3. Non-Goals

* payload shape guard PASS만으로 final residual seal PASS를 선언하지 않는다.
* current-route required validation PASS를 independent review PASS로 취급하지 않는다.
* author-reserved decision을 Codex, validator, reviewer가 대신 선택하지 않는다.
* option space가 공집합이거나 비열거 상태일 때 Codex / reviewer / validator가 새 option을 만들지 않는다.
* `unadopted + text_ko` 금지를 deletion, suppression, quality fail, publish suppression으로 해석하지 않는다.
* predecessor rollback residue를 current debt, cleanup target, runtime mutation 근거로 재개방하지 않는다.
* governance-only seal을 release readiness, manual QA completion, semantic quality completion으로 포장하지 않는다.
* existing sealed decision body를 직접 수정하지 않는다. 필요한 경우 additive supersession 또는 packet으로만 보강한다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 기준이다.
* Iris는 100% Lua runtime 표시 모드이며, runtime은 sealed payload를 렌더링만 한다.
* DVF production path와 runtime display path는 분리되어야 한다.
* current runtime authority는 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`와 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua` chunk bundle이다.
* monolith `IrisLayer3Data.lua`는 current runtime authority로 복귀하지 않는다.
* current guard implementation은 `Iris/build/description/v2/tools/build/runtime_payload_state_integrity.py`에 존재한다.
* current focused test는 `Iris/build/description/v2/tests/test_runtime_payload_state_integrity.py`에 존재한다.
* live `Iris/_docs/round3/current_route_required_validations.json`은 runtime payload state integrity artifacts/tests를 required validation으로 소비한다.
* current-compatible payload shape readpoint는 `2105` rows / `21` unadopted rows / current-like `publish_state` rows `0` / current-like forbidden or unclassified rows `0`이다.
* current `unadopted` rows의 renderer-visible `text_ko`는 missing 또는 explicit nil이어야 한다.
* predecessor rollback snapshot의 `unadopted + exposed + non_nil text_ko` residue 2건은 historical-only residue다.
* predecessor residue 2건과 current-like denominator `2105 / 21`은 lifecycle role이 다르며 disjoint해야 한다.
* `adopted / unadopted`는 current runtime vocabulary이며 quality-pass, publish_state, deletion, suppression 의미가 아니다.
* legacy `active / silent`는 historical / diagnostic / import alias로만 남는다.
* self-review 또는 same-authorship-chain review는 independent / external review gate를 충족하지 않는다.
* no-mutation baseline은 Phase 1 input fingerprint와 같은 protected manifest pre-hash snapshot을 Phase 5에서 post-hash와 비교하는 방식으로 고정한다.
* dirty working tree의 unrelated changes는 보존한다.

---

## 5. Repository Areas Affected

### Code

Read-only / frozen predicate guard surface:

* `Iris/build/description/v2/tools/build/runtime_payload_state_integrity.py`
* `Iris/build/description/v2/tests/test_runtime_payload_state_integrity.py`

기존 guard 변경 허용 범위:

* 별도 wrapper tool 추가
* 기존 tool에 additive report output만 추가

기존 guard 변경 금지 범위:

* PASS / FAIL predicate 변경
* denominator 변경
* expected counts 변경
* current-like surface selection 변경

새 residual seal 전용 tooling/test가 필요할 경우에만 추가:

* `Iris/build/description/v2/tools/build/runtime_payload_state_integrity_residual_seal.py`
* `Iris/build/description/v2/tests/test_runtime_payload_state_integrity_residual_seal.py`

Read-only runtime surfaces:

* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`
* `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`

### Docs

Direct plan artifact:

* `docs/runtime_payload_state_integrity_residual_seal_plan.md`

Expected residual docs:

* `docs/runtime_payload_state_integrity_residual_claim_boundary.md`
* `docs/runtime_payload_state_integrity_residual_ledger_packet.md`
* `docs/runtime_payload_state_integrity_author_decision.md`

Read-only / predecessor docs:

* `docs/runtime_payload_state_integrity_plan.md`
* `docs/runtime_payload_state_integrity_scope_lock.md`
* `docs/runtime_payload_state_policy.md`
* `docs/runtime_payload_shape_contract.md`
* `docs/runtime_payload_state_integrity_closeout.md`
* `docs/runtime_payload_state_integrity_ledger_packet.md`

Canonical paths if direct write is separately authorized, subject to canonical path pinning in the current checkout:

* `docs/Philosophy.md` - read-only top authority
* `docs/DECISIONS.md` - optional additive canonical target
* `docs/ARCHITECTURE.md` - optional additive canonical target
* `docs/ROADMAP.md` - optional additive canonical target

### Config

* `Iris/_docs/round3/current_route_required_validations.json`

This file is an optional additive governance adoption target only. It is not a runtime writer.

### Generated Artifacts

Preferred new evidence root:

* `Iris/build/description/v2/staging/runtime_payload_state_integrity_residual_seal/`

Existing guard evidence consumed read-only:

* `Iris/build/description/v2/staging/runtime_payload_state_integrity/`

Expected generated artifact families:

* `phase1/scope_separation_and_no_mutation_declaration.json`
* `phase1/input_fingerprint_manifest.json`
* `phase1/protected_surface_manifest.json`
* `phase1/blocker_inventory.json`
* `phase1/runtime_payload_existing_gate_consumption_report.json`
* `phase2/shape_guard_readpoint_reverification_report.json`
* `phase2/current_looking_forbidden_scan_report.json`
* `phase2/guard_predicate_diff_scope_report.json`
* `phase2/denominator_disjointness_report.json`
* `phase3/residual_historical_only_confinement_report.json`
* `phase3/predecessor_residue_non_reentry_report.json`
* `phase4/author_reserved_selection_option_enumeration.json`
* `phase4/author_reserved_selection_decision_record.json`
* `phase4/policy_consistency_report.json`
* `phase5/no_mutation_report.json`
* `phase5/artifact_hash_report.json`
* `phase5/primary_review_artifact_manifest.json`
* `phase6/independent_review_artifact_hash_report.json`
* `phase6/external_independent_review_report.json`
* `phase6/external_review_gate_report.json`
* `phase7/final_runtime_payload_residual_seal_report.json`
* `phase8/current_route_governance_adoption_report.json`

`artifact_hash_report.json` is the internal pre-review hash manifest. `independent_review_artifact_hash_report.json` is the reviewer-side comparison report and must not be treated as equivalent to review PASS by mere existence.

---

## 6. Planned Changes

### Change 1 - Scope Separation and Residual Blocker Inventory

Purpose:

payload shape guard completion과 residual final seal completion을 분리하고, blocker가 implementation blocker가 아니라 governance blocker인지 확인한다.

Files:

* `Iris/build/description/v2/staging/runtime_payload_state_integrity_residual_seal/phase1/*`

Implementation Notes:

* `payload_shape_guard_status`와 `residual_seal_status`를 별도 machine field로 기록한다.
* existing evidence root와 live required-validation manifest가 runtime payload guard를 어떻게 소비하는지 inventory한다.
* `pending_author_selection`, `blocked_external_gate` marker를 live blocker / stale marker / author-reserved blocker / external-review blocker로 분류한다.
* `input_fingerprint_manifest.json`을 작성하고 roadmap / review input은 content SHA로 기록한다.
* `protected_surface_manifest.json`을 Phase 5 이전에 작성한다.
* no-mutation pre-hash baseline은 이 Phase 1 input fingerprint와 같은 protected manifest snapshot으로 고정한다.

`protected_surface_manifest.json` minimum path families:

* current source chain
* rendered output
* Lua bridge output
* runtime chunk manifest
* manifest-derived runtime chunk files 전체
* package peer runtime payload manifest / chunks
* candidate bridge runtime payload manifest / chunks
* stale monolith / legacy bridge current-looking reentry scan 대상
* current-route required-validation manifest

`protected_surface_manifest.json` entry schema:

* `path`
* `path_source_kind`
* `surface_class`
* `authority_role`
* `expected_mutation_allowed`
* `pre_hash`
* `post_hash`
* `exists_status`
* `missing_allowed`
* `reason`
* `package_peer_source` - required for package peer runtime payload entries

`expected_mutation_allowed=true` is allowed only for the Phase 8 current-route required-validation manifest additive adoption carve-out. It is forbidden for source, rendered, Lua bridge, runtime chunk, package payload, candidate bridge, stale monolith, and legacy bridge authority surfaces.

Validation:

* blocker inventory completeness check
* existing runtime payload artifact presence check
* current-route required validation consumption check
* input fingerprint reproducibility check
* protected surface manifest schema validation
* no-mutation precheck

---

### Change 2 - Shape Guard Read-Only Reverification and Predicate Freeze

Purpose:

기존 guard PASS가 현재 checkout에서도 read-only로 성립함을 재확인하되, guard predicate 자체는 frozen으로 둔다.

Files:

* `Iris/build/description/v2/staging/runtime_payload_state_integrity_residual_seal/phase2/*`
* `Iris/build/description/v2/tools/build/runtime_payload_state_integrity.py` - frozen predicate surface
* `Iris/build/description/v2/tests/test_runtime_payload_state_integrity.py` - frozen expected-count surface

Implementation Notes:

* existing guard를 재실행하거나 기존 PASS evidence를 redrive한다.
* `2105` rows, `21` unadopted rows, current-like `publish_state` rows `0`, current-like forbidden/unclassified rows `0`을 재확인한다.
* current-like `unadopted` rows의 renderer-visible `text_ko` absent 상태를 확인한다.
* live current runtime, package peer, candidate bridge를 current-like denominator로 유지한다.
* `guard_predicate_diff_scope_report.json`을 작성한다.
* 허용되는 변경은 wrapper tool 또는 additive report output뿐이다.
* PASS / FAIL predicate, denominator, expected counts, current-like surface selection 변경은 금지한다.
* `runtime_payload_state_integrity.py`와 `test_runtime_payload_state_integrity.py`의 hash를 artifact hash manifest에 포함한다.
* 산출물은 freshness evidence이며 source/runtime/package authority가 아니다.

Validation:

* deterministic redrive
* no-write execution check
* current-looking forbidden scan
* package/current-looking compatibility scan
* guard predicate drift check
* existing focused test expected counts 유지 확인
* guard tool/test hash coverage check
* validation CLI existence check

---

### Change 3 - Predecessor Residue Historical-Only Confinement

Purpose:

predecessor rollback residue 2건이 historical-only이며 current-route reentry count가 0이고 current-like denominator와 disjoint임을 봉인한다.

Files:

* `Iris/build/description/v2/staging/runtime_payload_state_integrity_residual_seal/phase3/*`

Implementation Notes:

* predecessor rollback snapshot의 `unadopted + exposed + non_nil text_ko` residue 2건을 재확인한다.
* residue가 live current runtime, package peer, candidate bridge, rendered output, Lua bridge, current-route required artifact로 재유입되지 않았음을 스캔한다.
* `current_like_denominator ∩ predecessor_residue = ∅`를 증명한다.
* `residue_in_current_denominator_count=0`을 machine field로 기록한다.
* residue `2`와 denominator `2105 / 21`은 서로 다른 lifecycle role임을 report에 남긴다.
* residue를 cleanup target, current debt, runtime mutation 근거로 해석하지 않는 disposition을 기록한다.
* residue 자체는 이동/삭제/수정하지 않는다.

Validation:

* residue inventory check
* current-route reentry count check
* historical-only classification check
* predecessor residue non-reentry check
* denominator disjointness check
* `residue_in_current_denominator_count == 0`

---

### Change 4 - Author-Reserved Selection and Payload Policy Confirmation

Purpose:

`pending_author_selection`을 author-owned decision으로 해소하고, seal-closing option이 선택될 경우 payload shape policy를 확정한다.

Files:

* `docs/runtime_payload_state_integrity_author_decision.md`
* `Iris/build/description/v2/staging/runtime_payload_state_integrity_residual_seal/phase4/*`

Implementation Notes:

* code/evidence marker가 요구하는 author option space를 enumerate한다.
* `enumerable_option_space_present=false`이면 Phase 4는 halt한다.
* option space가 공집합이거나 비열거 상태이면 `pending_author_selection`을 유지하고, Codex / reviewer / validator는 새 option을 만들 수 없다.
* 비열거 / 공집합 상태는 first-class blocked state로 기록한다.
* author selection은 author-owned decision record로만 기록한다.
* seal-closing decision이 선택될 경우 다음을 policy confirmation으로 기록한다.
  * current-compatible `unadopted + text_ko` 금지
  * current-compatible `unadopted + publish_state` 금지
  * `unadopted` row display body는 missing 또는 explicit nil
  * predecessor rollback residue 2건은 historical-only
* author가 seal-closing option을 선택하지 않으면 canonical residual seal은 보류한다.

`author_reserved_selection_decision_record.json` required fields:

* `decision_owner`
* `decision_owner_role`
* `selected_option_id`
* `selected_option_is_seal_closing`
* `decision_source`
* `decision_timestamp`
* `decision_readpoint`
* `not_generated_by_executor`
* `not_inferred_by_validator`
* `policy_confirmations`

Validation:

* option enumeration evidence consistency check
* non-enumerable option space halt validation
* author decision required-field validation
* author ownership check
* policy / guard / shape contract consistency check
* forbidden interpretation scan

---

### Change 5 - No-Mutation and Artifact Integrity Verification

Purpose:

이번 residual seal이 source / rendered / Lua bridge / runtime chunks / package payload 변경 없이 닫히는 governance-only round임을 증명한다.

Files:

* `Iris/build/description/v2/staging/runtime_payload_state_integrity_residual_seal/phase5/*`

Implementation Notes:

* Phase 1 `protected_surface_manifest.json`의 `pre_hash`를 baseline으로 사용한다.
* Phase 5는 같은 manifest path set에 대해 `post_hash`를 채우고 pre/post hash를 비교한다.
* protected manifest 밖의 surface를 no-mutation evidence로 암묵 소비하지 않는다.
* `expected_mutation_allowed=true` entry가 있으면 Phase 8 manifest additive adoption carve-out인지 검증하고, 그 외 surface에서는 fail-closed 처리한다.
* mutation changed count가 0임을 기록한다.
* `runtime_payload_state_integrity.py`, `test_runtime_payload_state_integrity.py`, 새 wrapper/tool/test가 있으면 모두 `artifact_hash_report.json`에 포함한다.
* generated staging evidence가 current authority가 아님을 명시한다.
* Phase 8 adoption으로 `current_route_required_validations.json`이 additive 변경되는 경우에는 expected additive diff로 따로 분리한다.

Validation:

* protected surface manifest validation
* no-mutation report
* pre/post hash comparison
* artifact hash coverage check
* changed count `0` check
* Phase 1 input fingerprint baseline equality check

---

### Change 6 - Independent / External Review Gate

Purpose:

author decision과 residual disposition을 independent / external review로 봉인한다.

Files:

* `Iris/build/description/v2/staging/runtime_payload_state_integrity_residual_seal/phase6/*`

Implementation Notes:

* Phase 1-5 evidence packet을 review bundle로 구성한다.
* reviewer identity, review kind, self-review 여부를 machine-readable하게 기록한다.
* self-review는 forbidden으로 처리한다.
* Claude-authored 또는 same-authorship-chain review는 complete seal의 independent review로 세지 않는다.
* review report exists만으로 review PASS를 주장하지 않는다.
* review PASS일 때만 final canonical residual seal을 허용한다.

`external_independent_review_report.json` required fields:

* `reviewer_identity`
* `reviewer_kind`
* `review_independence_basis`
* `not_self_review`
* `not_same_authorship_chain`
* `same_authorship_chain_basis`
* `reviewed_artifact_manifest_hash`
* `primary_review_artifact_count`
* `missing_count`
* `hash_mismatch_count`
* `comparison_exempt_count`
* `comparison_exemptions`
* `review_verdict`
* `canonical_residual_seal_allowed`

Each `comparison_exemptions` item must include `path`, `exempt_reason`, and `reviewer_accepted`. `comparison_exempt_count` is not a blanket escape hatch and cannot substitute for hash coverage.

Validation:

* primary review artifact completeness
* frozen hash comparison
* missing artifact count `0`
* reviewer identity / review kind field check
* self-review forbidden check
* same-authorship-chain review forbidden check
* review gate pass check
* independent review hash report versus internal artifact hash report separation check

---

### Change 7 - Final Residual Seal Report

Purpose:

payload shape guard 완료와 residual seal 완료를 분리한 상태로 canonical closeout을 작성한다.

Files:

* `docs/runtime_payload_state_integrity_residual_claim_boundary.md`
* `docs/runtime_payload_state_integrity_residual_ledger_packet.md`
* `Iris/build/description/v2/staging/runtime_payload_state_integrity_residual_seal/phase7/*`

Implementation Notes:

* Phase 7 may emit a blocked final report while author or external gates remain open.
* PASS final report and `canonical_residual_seal_allowed=true` are forbidden until Phase 4 and Phase 6 gates pass.
* final report에 다음 axis를 분리 기록한다.
  * `payload_shape_guard_status`
  * `guard_predicate_freeze_status`
  * `author_decision_status`
  * `independent_external_review_status`
  * `predecessor_residue_disposition`
  * `residue_in_current_denominator_count`
  * `runtime_mutation_changed_count`
  * `source_rendered_bridge_package_mutation_changed_count`
  * `blocked_external_gate`
  * `pending_author_selection`
  * `governance_adoption_status`
  * `review_traceability_chain`
  * `canonical_residual_seal_allowed`
* final report traceability order is fixed as `artifact_hash_report.json -> primary_review_artifact_manifest.json -> independent_review_artifact_hash_report.json -> external_review_gate_report.json`.
* bare `complete` claim을 금지하고 complete의 대상을 residual seal로 한정한다.
* release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, semantic quality, public-facing text acceptance를 non-claim으로 유지한다.

Validation:

* final report schema validation
* claim boundary scan
* no bare `complete` claim scan
* non-claim field presence check
* final report traceability check
* `canonical_residual_seal_allowed=false` unless Phase 4 and Phase 6 gates are PASS

---

### Change 8 - Current-Route Governance Adoption and Documentation Update

Purpose:

residual seal을 current-route governance chain에서 재현 가능하게 소비하되 runtime writer로 오독되지 않게 한다.

Files:

* `Iris/_docs/round3/current_route_required_validations.json` - optional additive target
* `docs/DECISIONS.md` - optional additive canonical target
* `docs/ARCHITECTURE.md` - optional additive canonical target
* `docs/ROADMAP.md` - optional additive canonical target
* `Iris/build/description/v2/staging/runtime_payload_state_integrity_residual_seal/phase8/*`

Implementation Notes:

* required-validation manifest adoption은 optional / conditional이다.
* adoption decision rule은 `governance_adoption_status`로 기록한다.
* allowed values: `adopted_required_gate`, `not_required_traceable`, `blocked`.
* `adopted_required_gate`는 existing guard가 final residual seal report를 required artifact/test로 추적하지 못하고, duplicate-free additive entry가 필요한 경우에만 허용한다.
* `not_required_traceable`은 existing required validation과 residual evidence path가 충분히 traceable하며 새 manifest entry가 중복인 경우 사용한다.
* `blocked`은 duplicate risk, schema mismatch, missing evidence, non-additive diff, canonical path ambiguity가 있는 경우 사용한다.
* adoption이 필요하면 additive-only, duplicate-free, non-writer로만 추가한다.
* existing runtime payload guard entries를 제거하거나 약화하지 않는다.
* DECISIONS / ROADMAP / ARCHITECTURE 반영은 기존 sealed entry 수정이 아니라 staging draft 후 author seal 이후 additive supersession 또는 update packet으로 처리한다.
* canonical write를 행사할 경우 `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` 실제 path를 pin하고 검증한다.
* broad current-route rebuild / regeneration은 열지 않고 validation만 실행한다.

Validation:

* adoption decision rule validation
* additive-only diff check
* existing sealed entry diff `0`
* required artifact/test duplicate check
* canonical path pinning check if canonical docs are written
* package peer `path_source_kind` / `package_peer_source` validation
* current-route validation
* focused residual seal claim-boundary test
* docs claim scan

---

## 7. Validation Plan

### Automated Validation

Do not claim validation passed unless the exact command exits with code 0.

Primary current guard validation:

```powershell
uv run python -B Iris\build\description\v2\tools\build\runtime_payload_state_integrity.py --mode validate
uv run python -B -m unittest Iris.build.description.v2.tests.test_runtime_payload_state_integrity
```

Current-route required validation:

```powershell
uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
```

Lua syntax validation is regression safety, not a final residual seal sufficiency condition:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Conditional residual seal validation, if a dedicated wrapper/tool/test is added:

```powershell
uv run python -B Iris\build\description\v2\tools\build\runtime_payload_state_integrity_residual_seal.py --mode all
uv run python -B Iris\build\description\v2\tools\build\runtime_payload_state_integrity_residual_seal.py --mode validate
uv run python -B -m unittest Iris.build.description.v2.tests.test_runtime_payload_state_integrity_residual_seal
```

Supplemental regression, if the scope expands:

```powershell
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Package build is not a substitute for package peer payload scan. If package regression is explicitly opened:

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean -Zip
```

Required validation areas:

* validation CLI existence check
* protected surface manifest schema validation
* guard predicate drift validation
* guard tool/test artifact hash coverage
* author decision schema validation
* independent review admissibility validation
* option enumeration 공집합 / 비열거 halt validation
* `current_like_denominator ∩ predecessor_residue = ∅` validation
* optional manifest adoption decision validation
* package peer payload target enumeration validation
* roadmap / review provenance SHA validation
* canonical path validation if direct canonical write is authorized
* package peer `path_source_kind` / `package_peer_source` validation
* comparison exemption `exempt_reason` validation
* final report traceability order validation

Negative fixture / fail-closed cases:

* missing author decision
* self-review
* same-authorship-chain review
* guard predicate drift
* duplicate manifest adoption
* non-enumerable option space
* residue included in current denominator

### Manual Validation

* author reviews option enumeration and records selection.
* author confirms the selected option is seal-closing before final seal is claimed.
* reviewer confirms predecessor residue 2건 are historical-only and not current debt.
* reviewer confirms `unadopted` remains runtime vocabulary, not quality / publish / deletion / suppression vocabulary.
* reviewer confirms no runtime/source/rendered/bridge/package mutation occurred.
* independent reviewer confirms complete seal or leaves `blocked_external_gate` explicit.

### Validation Limits

This plan will not perform:

* multiplayer validation
* deployment validation
* long-session runtime validation
* manual in-game QA
* Workshop validation
* B42 compatibility sweep
* external ecosystem compatibility sweep
* public-facing text quality review
* semantic quality review
* full runtime equivalence
* full package equivalence
* full clean-checkout required-evidence reproducibility
* full historical artifact byte reproducibility
* live migration execution

---

## 8. Risk Surface Touch

### Authority Surface

Touched, governance-only.

This plan can seal residual governance authority for payload shape policy and predecessor residue disposition. It does not change source authority, rendered authority, Lua bridge authority, runtime authority, or package authority.

### Runtime Behavior Surface

None.

Runtime Lua remains a sealed payload renderer. Runtime display behavior, Browser, Wiki, Tooltip, sorting, filtering, and quality visibility are unchanged.

### Compatibility Surface

None by default.

Fail-loud checks may catch future current-looking reentry of predecessor residue. That is validation behavior, not compatibility policy expansion.

### Sealed Artifact Surface

Touched.

New residual seal artifacts, author decision record, review report, final seal report, claim boundary, ledger packet, and optional current-route adoption report may be created. Final seal remains blocked unless protected-surface manifest, guard predicate freeze, author schema, review schema, option enumeration, and denominator disjointness are all satisfied.

### Public-Facing Output Surface

None.

No public-facing Korean text, tooltip text, Browser copy, Workshop copy, release note, badge, recommendation, or quality display is changed.

---

## 9. Risk Analysis

### Architecture Risk

* final seal may be confused with runtime payload mutation completion.
* author decision may be bypassed by tooling or review text.
* independent review may be replaced with self-review.
* current-route required validation may be treated as writer authority.
* predecessor residue may be reclassified as current debt.
* guard predicate freeze may be weakened by additive report work that changes denominator semantics.

### Runtime Risk

* runtime chunks may be modified to satisfy a governance seal.
* renderer code may be given source / quality / publish policy responsibility.
* current-like scans may accidentally include historical rollback residue in the denominator.
* field absence, explicit nil, and non-nil text may be collapsed incorrectly.

### Compatibility Risk

* manifest adoption may duplicate existing runtime payload state integrity required entries.
* package peer scan may be skipped and replaced with unrelated package build evidence.
* stale monolith or legacy bridge surface may be mistaken for current authority.

### Regression Risk

* current row counts may drift and be force-fit instead of fail-loud.
* no-mutation evidence may be incomplete because the protected surface manifest is incomplete.
* guard tool/test changes may be left outside artifact hash coverage.
* docs may overclaim release/package/manual QA readiness.
* `complete` may be used without qualifying the completed target.

---

## 10. Rollback Plan

Rollback is artifact-level and additive-doc-level.

* If Phase 1 blocker inventory or protected surface manifest is incomplete, stop before final seal and keep `pending_author_selection` / `blocked_external_gate` explicit.
* If Phase 2 guard redrive drifts from expected counts or guard predicate freeze fails, fail loud and open a separate correction roadmap.
* If Phase 3 finds current-route residue reentry or denominator overlap, stop residual seal and open a mutation investigation plan.
* If Phase 4 option space is not enumerable, stop and keep `pending_author_selection`.
* If Phase 4 author decision is absent or not seal-closing, final seal remains blocked.
* If Phase 5 changed count is nonzero or protected-surface coverage is incomplete, stop and investigate protected-surface mutation.
* If Phase 6 review is missing, self-authored, same-authorship-chain, or hash-incomplete, keep `blocked_external_gate`.
* If Phase 8 manifest adoption is wrong, revert or supersede only the additive manifest entry.
* If a sealed docs entry is wrong after closeout, do not rewrite history; add a superseding correction packet.

No rollback path may mutate runtime chunks, Lua bridge, rendered output, source facts/decisions, package payload, or predecessor residue itself under this plan.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Hub & Spoke / SPI boundaries remain unchanged.
* Iris runtime remains Lua-only display surface, not runtime analysis / repair / policy engine.
* Runtime / build-time separation must be preserved.
* Runtime Lua must not compose, repair, validate source, normalize state, judge semantic quality, or judge publish policy.
* Source facts / decisions / rendered output / Lua bridge / runtime chunks / package payload mutation is forbidden.
* `adopted / unadopted` must not become quality-pass, publish_state, deletion, suppression, visibility, recommendation, trust, or confidence vocabulary.
* Legacy `active / silent` must not return as current writer / validator / runtime vocabulary.
* `publish_state` must not be reintroduced as current runtime policy.
* `quality_state` must not be exposed in UI.
* predecessor rollback residue must remain historical evidence only.
* `current_like_denominator ∩ predecessor_residue = ∅` must be proven before complete residual seal.
* FAIL-LOUD behavior must be preserved.
* non-enumerable option space must halt Phase 4.
* single-writer authority per surface must be preserved.
* current-route required-validation manifest is governance gate, not runtime writer.
* required-validation adoption, if any, must be additive-only, duplicate-free, and non-writer.
* `expected_mutation_allowed=true` is allowed only for the Phase 8 manifest additive adoption carve-out.
* existing guard predicate, denominator, expected counts, and current-like surface selection are frozen.
* self-review or same-authorship-chain review cannot satisfy independent / external review.
* complete residual seal requires author-owned seal-closing decision and independent / external review PASS.
* final claim boundary must keep release readiness, package readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, semantic quality, and public-facing text acceptance out of scope.

---

## 12. Expected Closeout State

Expected closeout target is conditional.

`complete_residual_seal` is allowed only when all conditions below are true:

* payload shape guard readpoint is PASS.
* existing guard predicate freeze is PASS.
* current runtime row count is `2105`.
* current `unadopted` row count is `21`.
* current-like `publish_state` row count is `0`.
* current-like forbidden or unclassified state row count is `0`.
* current-like `unadopted` rows have no renderer-visible `text_ko`.
* predecessor rollback residue count is `2`.
* predecessor residue current-route reentry count is `0`.
* `residue_in_current_denominator_count == 0`.
* `current_like_denominator ∩ predecessor_residue = ∅`.
* protected surface manifest exists and covers required path families.
* protected surface manifest package peer entries include `path_source_kind` and `package_peer_source`.
* any `expected_mutation_allowed=true` entry is limited to Phase 8 manifest additive adoption.
* no-mutation pre-hash baseline equals Phase 1 input fingerprint baseline.
* source / rendered / Lua bridge / runtime / package changed count is `0`.
* guard tool/test and any residual wrapper/tool/test are included in artifact hash coverage.
* `enumerable_option_space_present == true`.
* author-owned decision record includes all required fields.
* author-owned decision confirms current-compatible `unadopted + text_ko` and `unadopted + publish_state` forbidden policy.
* author-owned decision confirms predecessor residue historical-only disposition.
* author-owned decision has `selected_option_is_seal_closing == true`.
* independent / external review report includes all required fields.
* independent / external review metadata includes `same_authorship_chain_basis`.
* independent / external review PASS is present.
* `not_self_review == true`.
* `not_same_authorship_chain == true`.
* reviewed artifact hash coverage is complete.
* any comparison exemption includes per-item `exempt_reason` and `reviewer_accepted=true`.
* final report traceability order is `artifact_hash_report.json -> primary_review_artifact_manifest.json -> independent_review_artifact_hash_report.json -> external_review_gate_report.json`.
* final report sets `canonical_residual_seal_allowed=true`.
* current-route validation passes.
* `governance_adoption_status` is `adopted_required_gate` or `not_required_traceable`.
* optional manifest/docs adoption is additive-only and does not weaken existing runtime payload guard entries.
* claim boundary preserves all non-claims.

If author decision is missing, expected closeout is `pending_author_selection`, not complete.

If option space is non-enumerable or empty, expected closeout is `pending_author_selection` with Phase 4 halt, not complete.

If independent review is missing, self-authored, or same-authorship-chain, expected closeout is `blocked_external_gate`, not complete.

If no-mutation verification fails or protected surface manifest is incomplete, expected closeout is `blocked`.

If guard counts drift or predicate freeze fails, expected closeout is `revised_plan_needed` or `blocked`.

If predecessor residue overlaps current-like denominator, expected closeout is `blocked`.

If optional current-route manifest adoption is not necessary, the plan may close without manifest mutation as long as final residual seal evidence and claim boundary remain traceable through `governance_adoption_status=not_required_traceable`.
