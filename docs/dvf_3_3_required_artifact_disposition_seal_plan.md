# Implementation Plan

> Status: planned / roadmap-derived / codebase-inspected / review WARN required revisions incorporated / second review WARN required revisions incorporated / success-probability revisions incorporated / conditional-pass review owner-gate incorporated / DVF 3-3 required artifact disposition seal / governance-only / no source-rendered-runtime-package mutation planned
> 작성일: 2026-06-30
> Roadmap input: `C:/Users/MW/.codex/attachments/29e883b6-daf0-401e-9287-381074821bc1/pasted-text.txt` / sha256 `7084ED87A47A5D5D104518AA818FC12D107C2D187A6C4EFD285B48D8A4A9EB2A`
> Review input: `C:/Users/MW/.codex/attachments/3d67b605-7390-4791-8a8c-9b1555efa74d/pasted-text.txt` / sha256 `82637D5C8FF7A0CD8FECDDF7A6D478C86FC9D38CB2945861A67EB69677B48084` / verdict `WARN` / required revisions incorporated
> Review input: `C:/Users/MW/.codex/attachments/72ea2acf-ee25-433b-9172-f9bf90a3f560/pasted-text.txt` / sha256 `720EE7971B8E2EF4628AFAD721D474B68E63D72CA6885910237EF46B70E6CB9B` / verdict `WARN` / required revisions incorporated
> Review input: `C:/Users/MW/.codex/attachments/6791f2ad-7401-48f4-8067-498d2eee58f2/pasted-text.txt` / sha256 `FA48281FA75A809CA467B1E499BA63733541FAB47A48C3C5888FFA7CCC97008B` / verdict `CONDITIONAL PASS` / owner auto-seal gate and schema source-of-truth revisions incorporated
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Direct plan artifact: `docs/dvf_3_3_required_artifact_disposition_seal_plan.md`
> Working round identifier: `dvf_3_3_required_artifact_disposition_seal`
> Primary evidence root target: `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/`
> Parent closure plan artifact: `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_plan.md`
> Parent round identifier: `dvf_3_3_current_route_authority_required_evidence_integrity_closure`
> Parent evidence root target: `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/`
> Existing predecessor surface: `docs/dvf_3_3_required_artifact_surface_preflight_census_plan.md`
> Existing predecessor evidence root: `Iris/build/description/v2/staging/dvf_3_3_required_artifact_surface_preflight_census/`

---

## 1. Objective

DVF 3-3 current route의 required artifact surface에 대해 dirty / ignored / tracked / untracked / missing / hashability 상태를 per-artifact disposition으로 봉인하는 실행 계획을 작성한다.

이 계획의 목적은 런타임 개선이 아니라 governance / evidence preservation 개선이다. `Iris/_docs/round3/current_route_required_validations.json`에서 required artifact denominator를 다시 도출하고, 각 artifact가 closure evidence로 보존되는 결과 family와 axis disposition token을 서로 섞지 않는 schema field로 봉인한다.

이 계획의 1차 성공 조건은 parent closure plan의 편의를 제공하는 것이 아니라 Required Artifact Disposition 문제 자체를 닫는 것이다. 따라서 이 계획은 execution readpoint에서 발견되는 dirty required artifact와 ignored required artifact를 추측 없이 전부 분류하고, 다음 문제 계약을 만족해야 한다.

Required Artifact Disposition problem closure contract:

* Roadmap premise `dirty required artifact 6`과 `ignored required artifact 19`는 입력 premise로 기록한다.
* Live execution recensus가 premise와 다르면 divergence를 봉인하되, 문제 해결 대상은 live current-route required artifact denominator에서 실제로 발견되는 dirty / ignored / untracked required surface다.
* `problem_closure_denominator`는 실제 closure blocker가 될 수 있는 dirty, active ignored, effectively ignored, untracked required artifact row다.
* `ignored_diagnostic_coverage_denominator`는 full `ignore_rule_match`-required population plus every `effectively_ignored` row다. 이 denominator는 과소보고를 막기 위한 coverage denominator이며, 모든 row가 closure blocker라는 뜻은 아니다.
* Dirty required artifact는 `axis=dirty` row로 전부 봉인하고, `axis_disposition`은 `owner_adopted_evidence_update`, `stale_local_mutation`, `regeneration_required`, `blocker`, `not_required_candidate` 중 하나의 계열로 귀결해야 한다.
* Dirty required artifact가 final recensus에서 content-dirty `0`이 되지 않으면 final `ready`가 아니라 `machine_pass_blocked=true` blocker가 되어야 한다.
* Ignored required artifact는 `axis=ignored` row로 전부 봉인하고, 보존 경로는 narrow tracking, tracked hash surrogate, explicit non-hash exception, manifest removal candidate, or blocker 중 하나로 귀결해야 한다.
* Tracked negative `.gitignore` exception row, 즉 `ignore_rule_match=true`, `ignore_rule_is_negative_exception=true`, `ignore_active=false`, `effectively_ignored=false`, `tracked=true`, `dirty=false`, `untracked=false`인 row는 owner-supplied auto-seal rule ratification record가 bound된 뒤에만 자동으로 `axis=ignored`, `axis_disposition=diagnostic_only_preserved_by_tracking`, `preservation_result=tracked_original_preservation`, `passability=passable`로 봉인할 수 있다. 비준 전에는 해당 class가 `auto_seal_rule_state=owner-ratification-pending`, `passability=owner_pending`으로 남으며 `SOLVED`나 `negative_exception_auto_disposition_count`에 포함될 수 없다.
* Ignored diagnostic coverage denominator의 어떤 row도 bare diagnostic으로 남을 수 없다. Final `ready`는 `bare_diagnostic_count=0`일 때만 가능하다.
* Current readpoint fast path is allowed when live recensus shows `dirty=0`, `untracked=0`, `active_ignore=0`, and `effectively_ignored=0`; in that path the problem can be `SOLVED` after every `ignore_rule_match` diagnostic row receives a rationale-bound automatic or explicit disposition, and any automatic passable disposition is covered by validated owner auto-seal rule ratification.
* 이 문제 계약이 닫히지 않으면 parent compatibility packet을 생성하더라도 이 계획은 `ready`가 아니다.

Preservation result family (`preservation_result`):

* `tracked_original_preservation`
* `tracked_hash_surrogate`
* `explicit_non_hash_exception`
* `none`

Axis disposition token (`axis_disposition`):

* `owner_adopted_evidence_update`
* `stale_local_mutation`
* `regeneration_required`
* `track_narrowly`
* `preservation_exception_requested`
* `manifest_removal_candidate`
* `diagnostic_only_preserved_by_tracking`
* `not_preservation_relevant_with_rationale`
* `not_required_candidate`
* `blocker`

`disposition_schema.json` is the single source of truth for `axis`, `axis_disposition`, `preservation_result`, and `passability`; Objective, policy, validator, and final report vocabulary must fail closed if they diverge from it. Schema must also carry `axis` as `dirty / ignored / untracked` and row-level `passability` as `passable / owner_pending / blocked / validation_failed`. Auto-seal rule ratification is a separate owner-reserved gate state, not a `passability` value.

현재 코드베이스에는 predecessor인 Required Artifact Surface Preflight Census가 이미 존재한다. 해당 라운드는 live manifest 기준 required artifact `93`개와 required test `48`개를 계량하고, current route `PASS / 127 tests / closure_enforced=true`와 별도로 VCS preservation surface를 확인하는 역할을 한다. 이 계획은 그 predecessor를 대체하지 않고, preflight census가 발견하거나 미래 readpoint에서 다시 발견할 수 있는 dirty / ignored surface를 추측 없이 disposition하는 후속 seal로 둔다.

이 계획 자체는 `dvf_3_3_current_route_authority_required_evidence_integrity_closure`의 선행 disposition lane이다. 따라서 closeout은 parent plan이 소비할 수 있는 `parent_closure_input_packet.json`과 compatibility contract를 남겨야 하며, parent plan의 Phase 0 / Phase 5 / Phase 7 rerun-bound validation을 대체하지 않는다. 이 계획의 `ready`는 parent가 required-surface disposition queue를 다시 검증할 수 있다는 뜻이지, parent `machine_pass_governance_only` 또는 canonical seal completion을 뜻하지 않는다.

이 계획은 review WARN의 required revisions를 다음 실행 불변식으로 반영한다.

* `owner_adopted_evidence_update`는 최종 PASS disposition이 아니라 중간 처분 상태다. Final `ready`는 final recensus에서 owner-adopted artifact의 content dirty가 0일 때만 가능하며, dirty가 남으면 blocker로 machine PASS를 막아야 한다.
* `preservation_result=tracked_hash_surrogate`는 final readpoint freshness를 증명해야 한다. Live original hash 또는 sealed recipe regenerated output hash가 surrogate-bound hash와 일치하지 않으면 해당 row는 `passability=passable`이 될 수 없다.
* 이 round가 새로 live manifest required artifact로 채택하는 docs / tool / test / evidence도 tracked / not effectively ignored / dirty-free이거나 같은 ledger에서 `tracked_hash_surrogate` 또는 `explicit_non_hash_exception` preservation result를 가져야 한다.
* Ignored coverage denominator는 full frozen `ignore_rule_match`-required population과 모든 `effectively_ignored` row의 union으로 고정한다. 보존 관련성이나 실행자가 고른 subset만 처분하고 PASS할 수 없다.
* Owner decision이 필요한 처분은 executor-generated self-certification으로 대체할 수 없다. Owner-supplied record, repo-relative path, sha256, owner identity / role binding이 없으면 `owner_pending`이다. 단, tracked negative `.gitignore` exception diagnostic row의 automatic preserved-by-tracking disposition은 per-artifact owner decision이 아니라 owner-reserved auto-seal rule ratification record를 요구한다. 그 rule 비준 전에는 해당 row class가 `owner-ratification-pending`으로 남는다.
* Canonical execution start is owner-gated when the run intends to use automatic tracked-negative-exception passability. Before `owner_rule_ratification_binding_status=PASS`, recensus and dry-run classification may execute, but `--require-complete` closeout must remain `OWNER_PENDING` and must not emit `ready` or `SOLVED`.
* Parent compatibility packet은 `parent_round_id=dvf_3_3_current_route_authority_required_evidence_integrity_closure`, `predecessor_round_id=dvf_3_3_required_artifact_disposition_seal`, readpoint id, current-route manifest sha256, required artifact denominator sha256, final recensus report sha256, terminal-state mapping, and `parent_rerun_required=true`를 포함해야 한다.

완료 후 허용되는 최대 machine claim은 다음으로 제한한다.

```text
DVF 3-3 required artifact disposition seal derived its artifact denominator
from the live current-route required-validation manifest, assigned exactly one
validated disposition to every dirty or ignored required artifact in scope,
proved owner-adopted dirty rows clean at final recensus or blocked them, proved
surrogate freshness at the final readpoint, verified self-preservation for any
new required artifact adopted by this round, covered the full ignored
diagnostic population without bare diagnostics, consumed only owner-supplied
path/hash/role-bound owner decisions and owner rule ratifications, propagated blockers fail-closed, and
produced governance-only parent-closure input reports.
```

이 claim은 source facts, rendered output, Lua bridge, runtime chunk, package payload, release readiness, manual QA, semantic quality completion, independent review PASS, owner seal, canonical seal을 뜻하지 않는다.

---

## 2. Scope

이 계획은 Iris DVF 3-3의 current-route required artifact disposition seal만 다룬다.

포함 범위:

* live `current_route_required_validations.json` 기반 required artifact denominator 재도출
* predecessor preflight census report intake
* stated `dirty 6 / ignored 19`와 execution recensus 결과 대조
* Required Artifact Disposition problem closure status
* `problem_closure_denominator`와 `ignored_diagnostic_coverage_denominator` 분리
* current-readpoint fast path for zero dirty / untracked / active ignored / effectively ignored required artifacts
* dirty content diff와 Windows stat / line-ending diagnostic 분리
* `ignore_rule_match`와 `effectively_ignored` 분리 유지
* full frozen `ignore_rule_match`-required population coverage
* stated `ignored 19`와 `ignore_rule_match`-required 축 비교
* `effectively_ignored` 별도 count 보고
* tracked negative `.gitignore` exception diagnostic row automatic disposition only after owner auto-seal rule ratification
* pre-ratification `owner-ratification-pending` state for auto-seal candidate rows
* dirty required artifact disposition schema
* ignored required artifact disposition schema
* dirty final count `0` or explicit machine-blocking dirty blocker
* every ignored required artifact row routed to tracking / surrogate / exception / manifest-removal-candidate / blocker
* four-field row schema: `axis`, `axis_disposition`, `preservation_result`, `passability`
* existing untracked required artifact precondition 또는 disposition routing
* surrogate binding schema
* explicit non-hash exception claim boundary
* owner-supplied path / sha256 / identity / role-bound decision record validation
* owner-supplied auto-seal rule ratification record validation
* owner adoption dirty-clean final recensus gate
* tracked hash surrogate final-readpoint freshness gate
* manifest removal candidate proposal
* new required artifact self-preservation gate
* blocker propagation rule
* negative fixture matrix
* final recensus
* claim boundary, ledger packet, parent closure input packet
* parent compatibility contract for `dvf_3_3_current_route_authority_required_evidence_integrity_closure`
* terminal state split: `ready`, `complete_with_blockers`, `machine_pass_blocked`, `owner_pending`, `validation_failed`

Primary evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/`

Owner input roots:

* `Iris/build/description/v2/owner_inputs/dvf_3_3_required_artifact_disposition_seal/owner_decision_records/`
* `Iris/build/description/v2/owner_inputs/dvf_3_3_required_artifact_disposition_seal/owner_rule_ratifications/`

The owner input roots are not executor-produced staging evidence. Staging reports may reference owner decision and owner rule-ratification records by repo-relative path and sha256, but must not treat a copied staging artifact as the owner-supplied source of authority.

Direct documentation artifact:

* `docs/dvf_3_3_required_artifact_disposition_seal_plan.md`

Expected execution docs:

* `docs/dvf_3_3_required_artifact_disposition_seal_policy.md`
* `docs/dvf_3_3_required_artifact_disposition_seal_claim_boundary.md`
* `docs/dvf_3_3_required_artifact_disposition_seal_ledger_packet.md`
* optional `docs/dvf_3_3_required_artifact_disposition_seal_closeout.md`

Read-only codebase inputs:

* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/_docs/round3/round3_run_contract_tests.py`
* `Iris/build/description/v2/tools/build/dvf_3_3_required_artifact_surface_preflight_census_common.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_required_artifact_surface_preflight_census.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_required_artifact_surface_preflight_census.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_required_artifact_surface_preflight_census.py`
* `Iris/build/description/v2/tools/build/dvf_vcs_tracking_policy.py`
* `.gitignore`

### Explicitly Out Of Scope

* source facts / decisions / overlay support mutation
* rendered output regeneration as writer authority
* Lua bridge export mutation
* runtime chunk replacement
* package payload mutation
* package readiness or Workshop readiness
* B42 / release / deployment readiness
* manual in-game QA
* semantic quality or public-facing text acceptance
* broad `Iris/build/description/v2/staging/**` unignore
* required artifact deletion without owner decision
* live manifest wholesale redesign
* closed readpoint reopening beyond this disposition scope
* predecessor / stale artifact deletion
* independent review PASS, owner seal PASS, or canonical seal allowed claim
* unrelated cleanup of the current dirty worktree

---

## 3. Non-Goals

이 계획은 required artifact disposition을 실행하기 위한 계획이지, DVF 3-3의 source / runtime authority를 다시 여는 계획이 아니다.

이 계획은 다음을 해결하지 않는다.

* current route `PASS`를 release readiness로 해석하지 않는다.
* tracked status를 authority status로 해석하지 않는다.
* ignored status를 삭제 가능성 또는 비중요성으로 해석하지 않는다.
* hash surrogate를 original artifact preservation과 동일한 claim으로 해석하지 않는다.
* stale surrogate hash를 current required evidence preservation으로 해석하지 않는다.
* explicit non-hash exception을 검증 면제권으로 쓰지 않는다.
* owner adoption을 dirty-state guard bypass로 쓰지 않는다.
* `dirty 6 / ignored 19`를 execution denominator로 고정하지 않는다.
* stated `ignored 19`를 `effectively_ignored`와 직접 비교해 ignored coverage를 닫았다고 주장하지 않는다.
* existing `semantic_verdict=ready / artifact_disposition_state=not_needed` predecessor closeout을 미래 execution readpoint의 대체 증명으로 쓰지 않는다.
* owner decision record를 executor가 생성하거나 self-certify하지 않는다.
* package probe, live migration execution, runtime deployability, public text acceptance를 검증하지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 설계 authority다.
* Iris는 100% Lua runtime mod이며, 이 계획의 변경은 offline build / governance tooling / docs에 한정한다.
* Current-route required-validation manifest는 `Iris/_docs/round3/current_route_required_validations.json`이다.
* Codebase inspection 기준 live manifest는 schema `round3-current-route-required-validations-v1`, route `current`, status `PASS`, required artifact count `93`, required test count `48`로 관찰됐다.
* Execution 시점에는 반드시 live manifest에서 denominator를 다시 계산한다. `93`과 `48`은 planning-time observation이지 substitute denominator가 아니다.
* `round3_run_contract_tests.py`의 `artifact_check_errors()`는 required artifact 존재, JSON parse, field equality를 검사한다. Git dirty / ignored / tracked state는 같은 runner의 기본 artifact field check가 아니다.
* Existing preflight census tooling은 `dirty`를 `git diff` / `git diff --cached` content diff 기준으로 계산하고, `ignore_rule_match`와 `effectively_ignored`를 분리한다.
* Existing preflight census tooling은 planning premise `dirty 6 / ignored 19`를 execution count와 비교해 readpoint drift로 기록하는 구조를 이미 가진다. 이 round에서는 `ignored 19` 비교 축을 `ignore_rule_match`-required population으로 교정하고, `effectively_ignored`는 별도 count로 보고한다.
* Existing top docs currently record the predecessor preflight census as `ready`, with post-resolution counts `missing=0`, `dirty=0`, `effectively_ignored=0`, `untracked=0`, `tracked=93`, `invalid_json=0`, `field_mismatch=0`, `vcs_query_error=0`.
* That predecessor ready state is an input and sanity check, not a replacement for this round's recensus.
* The current worktree is dirty with many pre-existing generated / staging / top-doc changes. This plan must not revert or normalize user-owned changes.
* `.gitignore` already contains narrow exceptions for the predecessor preflight census tooling, tests, and staging evidence root. This plan may propose new narrow exceptions only when a disposition row proves they are required.
* Git global ignore access may warn on this workstation. Git query errors and warnings must be recorded, not hidden.
* Roadmap inputs are AI-assisted staging / non-canonical planning inputs. Execution authority comes from repo-relative plan artifacts, live manifest recensus, validators, owner-supplied decision records, and final evidence packets.
* `owner_adopted_evidence_update` records why an owner accepts a content change, but final readiness still requires VCS-preserved clean content at final recensus.
* `preservation_result=tracked_hash_surrogate` is passable only if final-readpoint freshness is proven against the live original artifact hash or a regenerated output hash from a sealed recipe.
* Any new artifact this round proposes for live manifest adoption becomes part of the required-surface preservation problem and must pass self-preservation checks before final ready.
* Protected surface lists should be derived from existing predecessor guard constants where practical. If a static list is used, the execution report must say why and bind it to the same no-mutation claim boundary.
* Owner decision records are external inputs to this round. The executor may read, hash, validate, and consume them, but must not generate them as proof of owner decision.
* Independent review is blocked by default unless a non-roadmap-author, artifact-bound review record exists.

---

## 5. Repository Areas Affected

### Code

Expected future execution surfaces:

* `Iris/build/description/v2/tools/build/dvf_3_3_required_artifact_disposition_seal_common.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_required_artifact_disposition_seal.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_required_artifact_disposition_seal.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_required_artifact_disposition_seal.py`

Expected reuse / read-only reference surfaces:

* `Iris/build/description/v2/tools/build/dvf_3_3_required_artifact_surface_preflight_census_common.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_required_artifact_surface_preflight_census.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_required_artifact_surface_preflight_census.py`
* `Iris/_docs/round3/round3_run_contract_tests.py`
* `Iris/build/description/v2/tools/build/dvf_vcs_tracking_policy.py`

No runtime Lua mutation is planned.

### Docs

Direct planning doc:

* `docs/dvf_3_3_required_artifact_disposition_seal_plan.md`

Expected execution docs:

* `docs/dvf_3_3_required_artifact_disposition_seal_policy.md`
* `docs/dvf_3_3_required_artifact_disposition_seal_claim_boundary.md`
* `docs/dvf_3_3_required_artifact_disposition_seal_ledger_packet.md`
* optional `docs/dvf_3_3_required_artifact_disposition_seal_closeout.md`

Read-only related docs:

* `docs/dvf_3_3_required_artifact_surface_preflight_census_plan.md`
* `docs/dvf_3_3_required_artifact_surface_preflight_census_claim_boundary.md`
* `docs/dvf_3_3_required_artifact_surface_preflight_census_ledger_packet.md`
* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_plan.md`
* `docs/dvf_vcs_tracking_policy.md`

### Config

Possible future config surface:

* `.gitignore`, only for narrow required artifact or surrogate preservation exceptions approved by a disposition row.

Broad staging unignore remains out of scope.

### Generated Artifacts

Expected future evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/`

Expected phase subroots:

* `phase0_readpoint_freeze/`
* `phase1_policy_schema/`
* `phase2_dirty_disposition/`
* `phase3_ignored_disposition/`
* `phase4_manifest_guard_integration/`
* `phase5_fail_closed_validation/`
* `phase6_closeout_claim_boundary/`

Parent-consumable closeout artifacts:

* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase6_closeout_claim_boundary/parent_closure_input_packet.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase6_closeout_claim_boundary/parent_compatibility_contract.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase6_closeout_claim_boundary/parent_terminal_state_mapping.json`

Separate owner input subroot:

* `Iris/build/description/v2/owner_inputs/dvf_3_3_required_artifact_disposition_seal/owner_decision_records/`
* `Iris/build/description/v2/owner_inputs/dvf_3_3_required_artifact_disposition_seal/owner_rule_ratifications/`

Generated artifacts are governance evidence outputs, not runtime payloads. Owner-supplied decision records and owner rule-ratification records are inputs, not generated artifacts; executor-produced staging outputs may contain only validation reports, path/hash references, VCS preservation status, and consumption status for those records.

---

## 6. Planned Changes

### Change 1 - Required Surface Re-census and Readpoint Freeze

Purpose:

Derive the live required artifact denominator and freeze the execution readpoint before any disposition.

Files:

* `Iris/build/description/v2/tools/build/run_dvf_3_3_required_artifact_disposition_seal.py`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase0_readpoint_freeze/*`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase0_readpoint_freeze/protected_surface_derivation_report.json`

Implementation Notes:

* Load `Iris/_docs/round3/current_route_required_validations.json`.
* Record manifest schema, route, status, hash, required artifact count, required test count.
* Reuse predecessor preflight census VCS tuple logic from `Iris/build/description/v2/tools/build/dvf_3_3_required_artifact_surface_preflight_census_common.py`; this is mandatory unless Phase 0 records a fail-loud incompatibility reason.
* Record Git status, Git version, ignore source state, and global ignore warning/error state.
* Recompute required artifact VCS state using content diff for dirty.
* Keep `git status` line-ending/stat signals as diagnostics.
* Compare measured dirty count to the roadmap premise `dirty 6`.
* Compare measured `ignore_rule_match`-required count to the roadmap premise `ignored 19`.
* Report `effectively_ignored` as a separate closure-blocking count; do not use it as the stated-19 divergence axis.
* Freeze `problem_closure_denominator` as dirty, active ignored, effectively ignored, and untracked required artifact rows.
* Freeze `ignored_diagnostic_coverage_denominator` as the union of full `ignore_rule_match`-required population and all `effectively_ignored` rows.
* If `dirty_required_artifact_count=0`, `untracked_required_artifact_count=0`, `active_ignore_required_artifact_count=0`, and `effectively_ignored_required_artifact_count=0`, enter `current_readpoint_fast_path_status=ELIGIBLE`.
* Freeze existing untracked required artifacts as either `untracked_required_artifact_count=0` or a required disposition population. Untracked required artifacts cannot be silently ignored just because they are not dirty or ignored.
* If counts diverge, record divergence as execution readpoint fact. Do not silently adopt roadmap counts.
* Record protected surface baseline hashes for source, rendered, Lua bridge, runtime chunks, package-adjacent forbidden surfaces, and live manifest.
* Record `protected_surface_derivation_report.json` that explains how protected source / rendered authority / Lua bridge / runtime / package surfaces were derived and how generated evidence artifacts are excluded from protected rendered authority.

Validation:

* Manifest denominator is derived from live manifest.
* Required artifact paths are repo-relative and path-normalized.
* `dirty` uses content diff only.
* `ignore_rule_match` and `effectively_ignored` remain separate.
* `problem_closure_denominator` equals dirty union active ignored union effectively ignored union untracked required artifact rows.
* `ignored_diagnostic_coverage_denominator` equals full `ignore_rule_match`-required population union `effectively_ignored`.
* stated `ignored 19` divergence is computed against `ignore_rule_match`-required, not `effectively_ignored`.
* Current-readpoint fast path is allowed only with zero dirty / untracked / active ignored / effectively ignored required artifacts.
* Existing untracked required artifacts either count `0` or enter a disposition/blocker route.
* Output root is disjoint from measured required artifact paths.
* Protected surface baseline report exists.
* Protected surface derivation report exists and separates generated evidence artifacts from protected rendered authority.

---

### Change 2 - Disposition Policy, Schema, and Predicate Seal

Purpose:

Define exactly which schema fields can pass, block, or require owner decision without mixing preservation result family and axis disposition token.

Files:

* `docs/dvf_3_3_required_artifact_disposition_seal_policy.md`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase1_policy_schema/disposition_schema.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase1_policy_schema/disposition_passability_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase1_policy_schema/disposition_classification_contract.md`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase1_policy_schema/auto_seal_rule_ratification_validation_report.json`
* `Iris/build/description/v2/owner_inputs/dvf_3_3_required_artifact_disposition_seal/owner_rule_ratifications/`

Implementation Notes:

* Each artifact row must have four separate fields: `axis`, `axis_disposition`, `preservation_result`, and `passability`.
* `disposition_schema.json` is the canonical source of truth for allowed values. The policy markdown, Objective summary, validators, ledgers, and final reports must be checked against it; enum mismatch is a validation failure, not a warning.
* `axis` allowed values are `dirty`, `ignored`, and `untracked`.
* `axis_disposition` allowed values include `owner_adopted_evidence_update`, `regeneration_required`, `manifest_removal_candidate`, `not_required_candidate`, `track_narrowly`, `preservation_exception_requested`, `diagnostic_only_preserved_by_tracking`, `not_preservation_relevant_with_rationale`, `stale_local_mutation`, and `blocker`.
* `preservation_result` allowed values are `tracked_original_preservation`, `tracked_hash_surrogate`, `explicit_non_hash_exception`, and `none`.
* `passability` allowed values are `passable`, `owner_pending`, `blocked`, and `validation_failed`.
* Each artifact row must have exactly one final `axis_disposition`, one `preservation_result`, and one `passability` per active `axis`.
* `blocker` axis disposition or `blocked` passability must prevent machine PASS.
* `manifest_removal_candidate` is only a proposal until owner approval and consumer scan are present.
* Manifest removal proposal rows must record source axis and source `axis_disposition`: dirty `not_required_candidate`, ignored `manifest_removal_candidate`, untracked `not_required_candidate`, or explicit owner request.
* `owner_adopted_evidence_update` is an intermediate `axis_disposition`. It is passable only after final recensus proves content dirty is 0 for the adopted artifact. If content dirty remains, the row passability is `blocked`.
* `tracked_hash_surrogate` is a `preservation_result`, not an `axis_disposition`; it must bind original path, surrogate path, source hash, generation recipe, validation command, claim boundary, and final-readpoint freshness predicate.
* `explicit_non_hash_exception` is a `preservation_result`, not an `axis_disposition`; it must bind reason, scope, owner decision state, and narrowed claim boundary.
* Owner-required row combinations include `axis_disposition=owner_adopted_evidence_update`, `preservation_result=explicit_non_hash_exception`, owner-approved `axis_disposition=manifest_removal_candidate`, and the owner-reserved auto-seal rule ratification needed before any automatic preserved-by-tracking row can become passable.
* Per-artifact owner decision is not required for `axis_disposition=diagnostic_only_preserved_by_tracking` only after an owner-supplied auto-seal rule ratification record validates. Before that record validates, candidate rows remain `auto_seal_rule_state=owner-ratification-pending` and `passability=owner_pending`.
* The automatic tracked-negative-exception row combination is `axis=ignored`, `axis_disposition=diagnostic_only_preserved_by_tracking`, `preservation_result=tracked_original_preservation`, `passability=passable`, with a rationale binding to the `.gitignore` negative exception source and current VCS tuple, and with `auto_seal_rule_ratification_status=ratified`.
* Owner-required disposition rows are valid only with owner-supplied records that bind repo-relative path, sha256, owner identity, owner role, decision token, decision timestamp or sequence id, and artifact role. Executor-generated owner records are invalid.
* Owner-supplied auto-seal rule ratification records are valid only under `Iris/build/description/v2/owner_inputs/dvf_3_3_required_artifact_disposition_seal/owner_rule_ratifications/`, and must bind rule id, predicate version, owner identity, owner role, decision token, timestamp or sequence id, and the schema hash they ratify. Executor-generated rule ratification records are invalid.
* `regeneration_required` cannot target protected source / rendered / Lua bridge / runtime / package surfaces. Any intersection with protected surfaces becomes `passability=blocked` or `owner_pending` outside this plan.
* `regeneration_required` can be passable only for generated evidence artifacts whose boundary is proven by `protected_surface_derivation_report.json`; ambiguity between generated evidence and protected rendered authority blocks passability.
* A policy row cannot turn tracked status into authority status.

Validation:

* Schema validation.
* Enum coverage validation.
* Objective / policy / schema enum source-of-truth validation.
* Mutual exclusivity validation.
* Field separation validation for `axis`, `axis_disposition`, `preservation_result`, and `passability`.
* Combination validation so `tracked_hash_surrogate` and `explicit_non_hash_exception` cannot appear as `axis_disposition` values.
* Automatic tracked-negative-exception combination validation.
* Auto-seal rule ratification validation rejects automatic passable rows when the owner rule-ratification record is missing, path/hash mismatched, schema-hash mismatched, identity-missing, or executor-generated.
* Owner decision scope validation rejects per-artifact owner-required expansion to diagnostic preserved-by-tracking rows after the owner rule-ratification gate is satisfied.
* Passability matrix validation.
* Protected surface derivation report validation before any `regeneration_required` row is passable.
* Negative fixture for unknown disposition.
* Negative fixture for missing surrogate binding.
* Negative fixture for stale surrogate freshness.
* Negative fixture for owner-adopted dirty row that remains content-dirty.
* Negative fixture for exception without claim boundary.
* Negative fixture for owner-required disposition with executor-generated or missing owner record.
* Negative fixture for untracked required artifact without disposition route.

---

### Change 3 - Dirty Required Artifact Disposition

Purpose:

Assign a final dirty-axis disposition to every recensus-detected dirty required artifact.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase2_dirty_disposition/dirty_required_artifact_disposition_ledger.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase2_dirty_disposition/dirty_required_artifact_diff_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase2_dirty_disposition/owner_adopted_update_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase2_dirty_disposition/regeneration_required_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase2_dirty_disposition/dirty_blocker_report.json`

Implementation Notes:

* Confirm each dirty path is still present in the live manifest.
* Distinguish content diff from stat / line-ending / timestamp diagnostic.
* If dirty content is intended evidence update, require owner adoption and post-adoption clean recensus.
* Owner adoption must come from an owner-supplied record bound to repo-relative path, current/adopted sha256, owner identity, owner role, and decision token. The executor may not create this record as a substitute for owner input.
* `owner_adopted_evidence_update` is not a final PASS disposition by itself. It becomes passable only when final recensus shows `git diff` and `git diff --cached` content dirty count for that artifact is 0 after the adopted baseline is VCS-preserved.
* If owner adoption exists but final content dirty remains nonzero, the row must be reported as `owner_adopted_dirty_not_preserved` and final machine PASS is blocked.
* If dirty content is generated output drift, require deterministic regeneration recipe and output match.
* If dirty content is stale local mutation, keep PASS blocked until revert, adoption, or owner decision.
* If the artifact is not actually required, move it only to `not_required_candidate`; do not remove from manifest in this phase.
* A dirty path cannot pass by annotation alone.

Validation:

* Dirty ledger coverage equals dirty working population.
* Every dirty row has one disposition.
* `owner_adopted_evidence_update` has owner decision record and post-adoption hash.
* Owner decision record validation is mandatory, not manual/optional.
* `owner_adoption_dirty_clean_status=PASS` only when final recensus content dirty is 0 for adopted rows.
* A fixture with owner adoption but remaining content dirty fails closed.
* `regeneration_required` has deterministic command and input identity.
* `regeneration_required_protected_surface_intersection_count=0`.
* Any remaining dirty blocker prevents PASS.

---

### Change 4 - Ignored Required Artifact Disposition

Purpose:

Assign a final ignored-axis disposition to the full frozen ignored coverage denominator.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase3_ignored_disposition/ignored_required_artifact_disposition_ledger.jsonl`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase3_ignored_disposition/ignored_rule_match_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase3_ignored_disposition/effectively_ignored_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase3_ignored_disposition/ignored_diagnostic_coverage_denominator_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase3_ignored_disposition/problem_closure_denominator_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase3_ignored_disposition/negative_exception_auto_disposition_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase3_ignored_disposition/bare_diagnostic_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase3_ignored_disposition/untracked_required_artifact_disposition_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase3_ignored_disposition/narrow_tracking_exception_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase3_ignored_disposition/hash_surrogate_binding_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase3_ignored_disposition/non_hash_exception_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase3_ignored_disposition/ignored_blocker_report.json`

Implementation Notes:

* Keep `ignore_rule_match` diagnostic separate from `effectively_ignored` blocker.
* Preserve the distinction between `tracked_but_ignore_matched` and `untracked_ignored`.
* The problem closure denominator is dirty, active ignored, effectively ignored, and untracked required artifact rows.
* The ignored diagnostic coverage denominator is the full frozen `ignore_rule_match`-required population plus every `effectively_ignored` row. It cannot be reduced to an executor-selected subset.
* Every row in the diagnostic coverage denominator needs a disposition row, including rows that appear preservation-irrelevant. Such rows use a sealed rationale-bound disposition such as `diagnostic_only_preserved_by_tracking` or `not_preservation_relevant_with_rationale`; bare diagnostic with no disposition is forbidden.
* Generate automatic passable disposition rows for tracked negative `.gitignore` exception diagnostics only when the owner auto-seal rule ratification record validates and all of the following row predicates hold: `tracked=true`, `ignore_rule_match=true`, `ignore_rule_is_negative_exception=true`, `ignore_active=false`, `effectively_ignored=false`, `dirty=false`, and `untracked=false`.
* Without validated owner rule ratification, otherwise matching negative exception candidate rows stay `auto_seal_rule_state=owner-ratification-pending`, `passability=owner_pending`; they count as disposition candidates but not as automatic passable rows.
* Automatic negative exception rows use `axis=ignored`, `axis_disposition=diagnostic_only_preserved_by_tracking`, `preservation_result=tracked_original_preservation`, `passability=passable`, and `auto_seal_rule_ratification_status=ratified`.
* Automatic negative exception rows must bind the `.gitignore` source line or pattern, the current VCS tuple, the owner rule-ratification record path/hash, and the artifact path/hash; they are not per-artifact owner decisions and cannot approve deletion or manifest removal.
* `bare_diagnostic_count` must be computed over the full ignored diagnostic coverage denominator and must be `0` for final `ready`.
* Existing `untracked` required artifacts that are not dirty or ignored still require a valid `axis_disposition` / `preservation_result` combination, such as `track_narrowly` + `tracked_original_preservation`, `regeneration_required` + `tracked_hash_surrogate`, `preservation_exception_requested` + `explicit_non_hash_exception`, `not_required_candidate` + `none`, or `blocker` + `none`.
* Prefer `axis_disposition=track_narrowly` and `preservation_result=tracked_original_preservation` when original required evidence must survive clean checkout.
* Use `preservation_result=tracked_hash_surrogate` only for volatile generated evidence where source binding and regeneration recipe are stronger than tracking raw output.
* `preservation_result=tracked_hash_surrogate` is passable only when `surrogate_freshness_status=PASS`.
* `surrogate_freshness_status=PASS` requires either final recensus live original content hash equals the surrogate-bound hash, or the artifact is absent from clean checkout by design and the sealed generation recipe regenerates output whose hash equals the surrogate-bound hash.
* If neither freshness path can be proven, downgrade the row to `axis_disposition=blocker` or reroute to `axis_disposition=preservation_exception_requested` with `preservation_result=explicit_non_hash_exception` and a narrowed claim boundary.
* If recipe regeneration is attempted but byte-deterministic output does not match the surrogate-bound hash, record `surrogate_regeneration_mismatch_count` and make the row non-passable unless it is separately rerouted to explicit non-hash exception with owner-supplied decision.
* Use `preservation_result=explicit_non_hash_exception` only with narrowed claim boundary.
* Do not add broad staging root unignore.
* If no safe disposition exists, emit `blocker`.

Validation:

* Ignored ledger coverage equals the full frozen ignored diagnostic coverage denominator.
* Problem closure denominator is reported separately from diagnostic coverage denominator.
* Every ignored row has one disposition.
* `bare_diagnostic_count=0` over the full ignored diagnostic coverage denominator.
* Automatic tracked-negative-exception rows are passable only with a validated owner rule-ratification record and with all predicate fields present and true/false as specified.
* No automatic tracked-negative-exception row requires per-artifact owner decision, surrogate, or manifest removal approval after owner rule ratification.
* Missing owner rule ratification keeps candidate rows `owner-ratification-pending` and prevents `required_artifact_disposition_problem_status=SOLVED`.
* `ignore_rule_match_required_count` is reported separately from `effectively_ignored_required_artifact_count`.
* Existing untracked required artifact count is `0` or every untracked row has one disposition.
* Narrow tracking proof uses exact path or narrow file family only.
* Surrogate binding has original path, surrogate path, hash, generation recipe, validation command, and claim boundary.
* Surrogate freshness report proves final-readpoint live original hash or regenerated output hash matches the surrogate-bound hash.
* A stale surrogate hash negative fixture fails closed.
* Exception rows have reason, owner/scope, and claim boundary.
* Broad staging unignore scan returns zero.
* Any remaining ignored blocker prevents PASS.

---

### Change 5 - Conditional Manifest Removal and Guard Integration

Purpose:

Integrate disposition results into the governance chain without weakening live manifest semantics.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase4_manifest_guard_integration/manifest_removal_proposal.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase4_manifest_guard_integration/live_manifest_disposition_integration_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase4_manifest_guard_integration/manifest_diff_scope_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase4_manifest_guard_integration/blocker_propagation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase4_manifest_guard_integration/new_required_artifact_preservation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase4_manifest_guard_integration/owner_decision_record_validation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase4_manifest_guard_integration/owner_input_record_vcs_preservation_report.json`
* optional candidate patch for `Iris/_docs/round3/current_route_required_validations.json`

Implementation Notes:

* Manifest removal candidates are proposals, not automatic removals.
* Any live manifest mutation must be additive or owner-approved, and existing required artifact/test removal count must be `0` unless the owner explicitly seals the removal.
* Owner-approved removal requires owner-supplied path / sha256 / identity / role-bound record. Without that record, the row remains `owner_pending`.
* Owner decision records are consumed from `Iris/build/description/v2/owner_inputs/dvf_3_3_required_artifact_disposition_seal/owner_decision_records/`; `phase4_manifest_guard_integration/owner_decision_record_validation_report.json` records validation results and path/hash bindings only.
* Any owner input record referenced by final report or parent compatibility packet must have VCS preservation status reported as tracked, not effectively ignored, and clean at the final readpoint, unless the report explicitly marks the record as external owner input that must be supplied again for parent revalidation.
* `owner_input_record_vcs_preservation_report.json` records tracked / ignored / effectively ignored / dirty / untracked status for every referenced owner decision or owner rule-ratification record. This report is executor-produced validation evidence, not the owner authority record itself.
* Staging must not contain the authoritative owner decision source record. If a copied or executor-produced staging record is the only available owner record, owner binding fails and the affected rows stay `owner_pending`.
* Owner-rejected removal candidates must be rerouted to a valid `axis_disposition` / `preservation_result` combination such as `axis_disposition=blocker`, `axis_disposition=track_narrowly` with `preservation_result=tracked_original_preservation`, `axis_disposition=regeneration_required` with `preservation_result=tracked_hash_surrogate`, or `axis_disposition=preservation_exception_requested` with `preservation_result=explicit_non_hash_exception`; they cannot remain passable removal candidates.
* Candidate manifest and live manifest must stay separate.
* Disposition blockers must be visible to runner / validator and must not be converted into PASS.
* If this round introduces new final reports as required artifacts, avoid self-reference cycles.
* If this round proposes any new docs / tool / test / evidence as live manifest required artifacts, each new required artifact must be tracked, not effectively ignored, and dirty-free at final recensus.
* If a new required artifact is intentionally not tracked, it must have a surrogate or explicit non-hash exception row in this same disposition ledger.
* Required artifact adoption must not broad-unignore the evidence root.
* Generated staging evidence not adopted as required artifact stays outside durable preservation claims.

Validation:

* Manifest removal proposal validation.
* Owner decision record validation is mandatory for any owner-required disposition.
* Live manifest diff scope validation.
* Existing required artifact/test unintended removal count is `0`.
* Candidate/live manifest separation validation.
* Blocker propagation validation.
* Self-reference cycle check.
* `new_required_artifact_preservation_status` validation.
* New required artifact tracked / not effectively ignored / dirty-free validation, or surrogate / exception coverage validation.

---

### Change 6 - Negative Fixture and Fail-Closed Validation

Purpose:

Prove that invalid disposition states fail closed.

Files:

* `Iris/build/description/v2/tools/build/validate_dvf_3_3_required_artifact_disposition_seal.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_required_artifact_disposition_seal.py`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase5_fail_closed_validation/negative_fixture_matrix.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase5_fail_closed_validation/fail_closed_validation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase5_fail_closed_validation/protected_surface_no_mutation_report.json`

Implementation Notes:

* Negative fixtures must be isolated from live required artifacts and Git state.
* Fixture cases include dirty content, staged dirty, owner-adopted dirty row that remains content-dirty, missing surrogate binding, stale surrogate freshness, untracked surrogate, exception without claim boundary, owner-required disposition with missing / executor-generated / path-mismatched / sha-mismatched / identity-missing owner record, missing / executor-generated / schema-hash-mismatched owner auto-seal rule ratification record, full ignored denominator row left as bare diagnostic, untracked required artifact without disposition, new required artifact untracked or effectively ignored, manifest removal dependency break, skipped disposition, Git global ignore warning misclassified as actual ignored state, near-miss auto-seal predicates, and blocker present.
* Near-miss auto-seal fixtures must cover at least `ignore_active=true`, `dirty=true`, `untracked=true`, and non-negative ignore rows. These fixtures must not emit `diagnostic_only_preserved_by_tracking / tracked_original_preservation / passable`; they must route to `owner_pending`, `blocked`, or another explicit non-passable disposition.
* Validator `--require-complete` must reject unresolved blocker, missing disposition, bare diagnostic, and owner-pending PASS claims.
* Current-route regression remains separate from disposition validator.
* Protected source / rendered / Lua bridge / runtime / package surfaces must remain unchanged.

Validation:

* Focused unittest passes.
* Validator `--require-complete` passes.
* Negative fixture matrix passes.
* Protected surface no-mutation report has changed count `0`.
* Owner-adopted dirty bypass negative fixture fails closed.
* Stale surrogate freshness negative fixture fails closed.
* New required artifact self-preservation negative fixture fails closed.
* Git global ignore warning negative fixture remains diagnostic-only.
* Full ignored coverage denominator negative fixture fails closed.
* Owner decision record binding negative fixtures fail closed.
* Auto-seal owner rule-ratification negative fixtures fail closed.
* Near-miss auto-seal negative fixtures fail closed.
* Untracked required artifact routing negative fixture fails closed.
* Current route still passes, or any failure is classified without hiding it.

---

### Change 7 - Final Re-census, Closeout, and Claim Boundary

Purpose:

Close the round with a final readpoint, final disposition state, and parent-consumable reports.

Files:

* `docs/dvf_3_3_required_artifact_disposition_seal_claim_boundary.md`
* `docs/dvf_3_3_required_artifact_disposition_seal_ledger_packet.md`
* optional `docs/dvf_3_3_required_artifact_disposition_seal_closeout.md`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase6_closeout_claim_boundary/final_required_artifact_disposition_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase6_closeout_claim_boundary/final_recensus_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase6_closeout_claim_boundary/closure_readiness_verdict.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase6_closeout_claim_boundary/owner_input_record_vcs_preservation_report.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase6_closeout_claim_boundary/parent_closure_input_packet.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase6_closeout_claim_boundary/parent_compatibility_contract.json`
* `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/phase6_closeout_claim_boundary/parent_terminal_state_mapping.json`

Implementation Notes:

* Final report must include `required_artifact_disposition_problem_status`, `current_readpoint_fast_path_status`, `fast_path_used`, `dirty_axis_verdict`, `ignored_axis_verdict`, `artifact_disposition_state`, `blocker_count`, `surrogate_freshness_status`, `new_required_artifact_preservation_status`, `auto_seal_rule_ratification_status`, `owner_input_record_vcs_preservation_status`, and `no_guess_entry_ready`.
* `required_artifact_disposition_problem_status` allowed values are `SOLVED`, `SOLVED_WITH_MACHINE_BLOCKERS`, `OWNER_PENDING`, and `VALIDATION_FAILED`.
* `current_readpoint_fast_path_status` allowed values are `ELIGIBLE`, `NOT_ELIGIBLE`, and `NOT_USED`.
* `auto_seal_rule_ratification_status` allowed values are `ratified`, `owner-ratification-pending`, `not_applicable`, and `invalid`.
* `SOLVED` requires dirty required artifact final content-dirty count `0`, every ignored required artifact row routed to a preservation/disposition outcome, `bare_diagnostic_count=0`, and no unresolved owner-required row.
* `fast_path_used=true` is valid only when `current_readpoint_fast_path_status=ELIGIBLE`, final recensus has `dirty_required_artifact_count=0`, `untracked_required_artifact_count=0`, `active_ignore_required_artifact_count=0`, and `effectively_ignored_required_artifact_count=0`, every `ignore_rule_match` diagnostic row has a rationale-bound disposition, `bare_diagnostic_count=0`, and `owner_rule_ratification_binding_status=PASS`.
* `SOLVED` may use the current readpoint fast path only when the full `fast_path_used=true` predicate above is satisfied.
* `SOLVED_WITH_MACHINE_BLOCKERS` is acceptable for this predecessor only when every dirty / ignored / untracked required artifact row is classified and one or more rows intentionally block machine PASS. It must co-occur with `machine_pass_blocked=true`.
* `OWNER_PENDING` is acceptable only when every non-owner row is classified and the remaining unresolved rows require owner-supplied decision records or owner auto-seal rule ratification.
* `dirty_axis_verdict` allowed values are `ready_clean`, `owner_pending`, and `blocked_dirty_not_preserved`.
* `ignored_axis_verdict` allowed values are `ready_preserved`, `owner_pending`, and `blocked_not_preserved`.
* Final report must include `problem_closure_denominator_count`, `ignored_diagnostic_coverage_denominator_count`, `ignore_rule_match_required_count`, `active_ignore_required_artifact_count`, `effectively_ignored_required_artifact_count`, `negative_exception_auto_disposition_count`, `bare_diagnostic_count`, `untracked_required_artifact_count`, `owner_decision_record_binding_status`, `owner_rule_ratification_binding_status`, `owner_input_record_tracked_count`, `owner_input_record_effectively_ignored_count`, `owner_input_record_dirty_count`, `regeneration_required_protected_surface_intersection_count`, `protected_surface_derivation_status`, `surrogate_regeneration_mismatch_count`, and `machine_pass_blocked`.
* Terminal state must distinguish `ready`, `complete_with_blockers`, `machine_pass_blocked`, `owner_pending`, and `validation_failed`.
* `complete_with_blockers` is a classification-complete terminal state only. It is invalid unless the same final report sets `machine_pass_blocked=true`, `ready=false`, and lists the blocker rows that prevent machine PASS.
* `docs/dvf_3_3_required_artifact_disposition_seal_ledger_packet.md` must repeat that `complete_with_blockers` means classification-complete, not closeout-complete, and must show `machine_pass_blocked=true`, `ready=false`, and the blocking rows next to the term every time it is summarized.
* `ready` requires final recensus and zero unresolved blockers.
* `ready` requires `required_artifact_disposition_problem_status=SOLVED`.
* `ready` requires `owner_adoption_dirty_clean_status=PASS` for every owner-adopted dirty row.
* `ready` requires `surrogate_freshness_status=PASS` for every passable surrogate row.
* `ready` requires `new_required_artifact_preservation_status=PASS` for every new artifact adopted into the live required manifest by this round.
* `ready` requires `bare_diagnostic_count=0`.
* `ready` requires `owner_decision_record_binding_status=PASS` for all owner-required disposition rows.
* `ready` requires `owner_rule_ratification_binding_status=PASS` when any automatic tracked-negative-exception disposition row is counted as passable.
* `ready` requires `owner_input_record_vcs_preservation_status=PASS` for every owner input record referenced by final report or parent compatibility packet.
* `ready` requires current-route regression validation PASS; current-route regression failure must produce `validation_failed` or `machine_pass_blocked`, not `ready`.
* `owner_pending` is not PASS.
* Claim boundary must separate hash-preserved, surrogate-backed, and explicit exception counts.
* Independent review gate remains `BLOCKED` unless an artifact-bound independent review is present.
* Owner seal and canonical seal remain separate axes.
* Parent closure input is advisory unless consumed at the same readpoint.
* `parent_compatibility_contract.json` must bind `parent_round_id=dvf_3_3_current_route_authority_required_evidence_integrity_closure`, `predecessor_round_id=dvf_3_3_required_artifact_disposition_seal`, readpoint id, current-route manifest sha256, required artifact denominator sha256, final recensus report sha256, disposition ledger sha256, owner decision validation report sha256 when present, owner rule-ratification validation report sha256 when auto-seal is used, owner input record VCS preservation report sha256 when owner inputs are referenced, protected surface derivation report sha256, and `parent_rerun_required=true`.
* `parent_terminal_state_mapping.json` must map this round's terminal state to the parent plan:
  * `ready` maps to `parent_required_surface_disposition_ready_for_rerun`, not parent machine PASS.
  * `complete_with_blockers` with `machine_pass_blocked=true` maps to parent `blocked_with_required_surface_disposition_packet / no-authority-mutation`.
  * `owner_pending` maps to parent `blocked_with_required_surface_disposition_packet / owner_adjudication_required`.
  * `validation_failed` maps to parent `blocked / no-authority-mutation`.
* Parent machine PASS remains unavailable until parent Phase 0 / Phase 5 VCS checks and Phase 7 current-route validation rerun at the compatible readpoint.

Validation:

* Final validator `--require-complete`.
* Final report schema validation.
* Final recensus reproducibility.
* Required Artifact Disposition problem status validation.
* Current readpoint fast path validation, if used, requires `fast_path_used=true`, `bare_diagnostic_count=0`, `owner_rule_ratification_binding_status=PASS`, and every `ignore_rule_match` diagnostic row rationale-bound in the same final report.
* Dirty required artifact final content-dirty count is `0` or all remaining dirty rows have explicit machine-blocking disposition.
* Every ignored required artifact row has a tracking / surrogate / exception / manifest-removal-candidate / blocker route.
* Every ignored diagnostic coverage row has a rationale-bound disposition.
* Negative exception automatic disposition count matches rows satisfying the tracked clean negative-exception predicate and only counts rows covered by validated owner auto-seal rule ratification.
* Owner-adopted dirty rows are content-clean at final recensus.
* Surrogate freshness status is PASS or the row is non-passable.
* New required artifact preservation status is PASS or final ready is blocked.
* `regeneration_required_protected_surface_intersection_count=0`.
* `protected_surface_derivation_status=PASS`.
* Surrogate regeneration mismatch count is 0 for passable surrogate rows, or affected rows are non-passable / owner-pending.
* Full ignored coverage denominator has no bare diagnostic rows.
* Owner decision records are owner-supplied inputs under `Iris/build/description/v2/owner_inputs/dvf_3_3_required_artifact_disposition_seal/owner_decision_records/` and bound to repo-relative path, sha256, identity, role, and decision token; staging validation reports may only reference them.
* Owner auto-seal rule ratification records are owner-supplied inputs under `Iris/build/description/v2/owner_inputs/dvf_3_3_required_artifact_disposition_seal/owner_rule_ratifications/` and bound to rule id, predicate version, schema hash, identity, role, and decision token; staging validation reports may only reference them.
* Owner input record VCS preservation validation proves every referenced owner decision or rule-ratification record is tracked, not ignored, not effectively ignored, not untracked, and clean at the final readpoint, or marks the final state non-ready and parent-revalidation-required.
* Existing untracked required artifacts are zero or fully dispositioned.
* Claim boundary validation.
* Parent input packet path/hash binding.
* Parent compatibility contract validates parent round id, predecessor round id, readpoint id, manifest hash, denominator hash, final recensus hash, disposition ledger hash, owner rule-ratification validation report hash when applicable, owner input record VCS preservation report hash when applicable, terminal-state mapping, and `parent_rerun_required=true`.
* Parent terminal mapping rejects any predecessor `ready` packet that claims parent `machine_pass_governance_only` directly.
* No release, package, runtime, semantic quality, or public-facing text acceptance claim exists.

---

## 7. Validation Plan

### Automated Validation

Expected commands for future execution:

```powershell
uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_required_artifact_disposition_seal.py --mode all
```

```powershell
uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_required_artifact_disposition_seal.py --require-complete
```

```powershell
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_required_artifact_disposition_seal.py"
```

Predecessor compatibility check:

```powershell
uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_required_artifact_surface_preflight_census.py --mode standard
```

Current-route regression check:

```powershell
uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
```

Existing VCS policy guard:

```powershell
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_vcs_tracking_policy.py"
```

Lua syntax validation is not required if execution touches no Lua files. If any Lua file is touched, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

### Manual Validation

Mandatory manual review should inspect:

* Phase 0 recensus denominator
* stated-vs-measured dirty / `ignore_rule_match` divergence
* `problem_closure_denominator` vs `ignored_diagnostic_coverage_denominator`
* current-readpoint fast path eligibility, if claimed, including `fast_path_used=true`, `bare_diagnostic_count=0`, and `owner_rule_ratification_binding_status=PASS`
* tracked negative `.gitignore` exception automatic disposition rows and owner rule-ratification binding
* owner input record VCS preservation status for every referenced owner decision or owner rule-ratification record
* near-miss auto-seal negative fixture coverage
* ignored diagnostic coverage `bare_diagnostic_count`
* owner decision record binding
* existing untracked required artifact routing
* dirty disposition ledger
* ignored disposition ledger
* surrogate binding rows
* surrogate freshness rows
* explicit non-hash exception rows
* owner-adopted dirty clean proof
* manifest removal proposal
* new required artifact preservation report
* blocker propagation report
* terminal state split
* broad unignore scan
* final claim boundary
* parent closure input packet

Optional manual review may inspect:

* non-adopted generated staging evidence naming
* final report readability of `ready` / `complete_with_blockers` / `machine_pass_blocked` / `owner_pending` / `validation_failed` verdicts, including `machine_pass_blocked=true` when `complete_with_blockers`
* manifest removal proposal source-axis readability

Manual in-game validation is not part of this plan.

### Validation Limits

This execution will not validate:

* no runtime behavior validation
* no multiplayer validation
* no long-session runtime validation
* no manual in-game QA
* no package readiness validation
* no Workshop validation
* no B42 readiness validation
* no deployment validation
* no semantic quality completion
* no public-facing text acceptance
* no live migration execution validation
* no source/rendered/runtime/package mutation validation beyond no-mutation proof
* no full historical byte reproducibility
* no clean-checkout full required-evidence reproducibility proof
* no independent review completion
* no owner seal or canonical seal

---

## 8. Risk Surface Touch

### Authority Surface

Validation/governance surface impact only.

This plan may add disposition policy docs, validator tooling, focused tests, and staging evidence. It does not mutate source facts, decisions, overlay support, rendered output, Lua bridge output, runtime chunks, or package payloads as authority surfaces.

If any new disposition seal artifact is adopted into the live required-validation manifest, that artifact's VCS preservation is part of this plan's authority surface and must be closed by `new_required_artifact_preservation_status=PASS`.

Owner decision and owner rule-ratification authority remain owner-supplied only. The executor cannot create owner decision records for owner adoption, explicit non-hash exception, or manifest removal approval, and cannot create the owner ratification record that permits automatic tracked-negative-exception passability.

### Runtime Behavior Surface

None.

Runtime Lua, Browser, Wiki, Tooltip, package payload, and runtime chunks remain unchanged.

### Compatibility Surface

Low.

Runtime compatibility should not change. Tooling may become stricter about dirty / ignored required artifacts and may reveal blockers that current field-level validation does not catch.

### Sealed Artifact Surface

Governance evidence impact only.

Existing sealed predecessor docs and reports are read-only inputs. New disposition seal artifacts are additive unless an owner-approved manifest adoption diff is opened.

New sealed artifact candidates are not self-validating. Required artifact adoption of this round's own docs / tools / tests / evidence requires tracked / not effectively ignored / dirty-free status or a valid same-ledger preservation result such as `tracked_hash_surrogate` or `explicit_non_hash_exception`.

### Public-Facing Output Surface

None.

No README, Workshop text, UI text, or public Iris description changes are planned.

---

## 9. Risk Analysis

### Architecture Risk

* The disposition seal could be mistaken for source/runtime authority. Mitigation: every report must state governance-only and no writer authority.
* The live manifest denominator could be substituted by roadmap counts. Mitigation: denominator must be rederived from live manifest.
* Reimplementing VCS tuple logic could diverge from the proven preflight census. Mitigation: reuse `dvf_3_3_required_artifact_surface_preflight_census_common.py` VCS tuple logic unless a fail-loud incompatibility is recorded.
* Predecessor `ready` could be overread as future readpoint proof. Mitigation: final execution recensus is mandatory.
* Manifest removal candidate could become a blocker escape hatch. Mitigation: owner verdict, consumer scan, and negative validation are required.
* Ignored artifacts could drop out through a subset denominator. Mitigation: full frozen ignored diagnostic coverage denominator, separate problem closure denominator, and `bare_diagnostic_count=0`.
* Negative `.gitignore` exception diagnostics could be over-routed to owner pending after the owner has ratified the benign auto-seal rule. Mitigation: tracked clean negative-exception rows have an automatic preserved-by-tracking disposition that is passable without per-artifact owner decision only after owner rule ratification.
* Auto-seal could bypass owner-reserved authority if executed before rule ratification. Mitigation: validated owner rule-ratification record is required before any automatic negative-exception row becomes passable; missing ratification leaves rows `owner-ratification-pending`.
* Auto-seal predicate implementation could be too broad. Mitigation: near-miss fixtures for `ignore_active=true`, `dirty=true`, `untracked=true`, and non-negative ignore fail closed.
* Current-readpoint fast path could hide diagnostic coverage gaps. Mitigation: fast path requires zero dirty / untracked / active ignored / effectively ignored required artifacts plus complete ignored diagnostic coverage with `bare_diagnostic_count=0`, `owner_rule_ratification_binding_status=PASS`, and every `ignore_rule_match` diagnostic row rationale-bound.
* Schema terms could re-mix axis route and preservation result. Mitigation: validate separate `axis`, `axis_disposition`, `preservation_result`, and `passability` fields and reject preservation result tokens used as axis disposition tokens.
* Owner adoption could become a dirty-state bypass. Mitigation: owner-adopted rows are intermediate until final content-dirty recensus is 0.
* Owner authority could leak to executor self-certification. Mitigation: owner-supplied path / sha256 / identity / role-bound records are mandatory and executor-generated records fail validation.
* Owner-supplied records could be confused with executor-produced staging evidence. Mitigation: authoritative owner records live under `Iris/build/description/v2/owner_inputs/...`; staging stores only validation reports and path/hash references.
* Owner input records referenced by final reports could become non-replayable if they are untracked or ignored. Mitigation: final report must include owner input record VCS preservation status and parent compatibility must bind the preservation report hash.
* `complete_with_blockers` could be misread as closeout complete. Mitigation: final report and ledger packet must pair it with `machine_pass_blocked=true`, `ready=false`, explicit blocker rows, and the phrase classification-complete, not closeout-complete.
* Generated evidence regeneration could be confused with protected rendered authority mutation. Mitigation: protected surface derivation report is mandatory before any `regeneration_required` row can be passable.
* A tracked hash surrogate could represent a stale readpoint. Mitigation: final-readpoint live-original or regenerated-output hash freshness is mandatory.
* New required artifacts could recreate the same preservation gap. Mitigation: self-preservation gate covers new required docs / tools / tests / evidence.

### Runtime Risk

* Direct runtime risk is low because runtime surfaces are not touched.
* Accidental generation or export could mutate protected output. Mitigation: protected surface baseline and final no-mutation hash checks.

### Compatibility Risk

* Runtime compatibility risk is low.
* Validation compatibility risk is medium because stricter preservation checks may block a route that still passes field-level current-route validation.

### Regression Risk

* Existing dirty worktree state may be confused with round-owned mutation.
* Git ignore warnings may be misinterpreted as ignored evidence state.
* stated `ignored 19` may be compared to the wrong axis. It must compare against `ignore_rule_match`-required, not `effectively_ignored`.
* `tracked_but_ignore_matched` may be incorrectly merged with `untracked_ignored`.
* Existing untracked required artifacts may bypass dirty/ignored routes unless explicitly dispositioned.
* Surrogate evidence may be overclaimed as original preservation.
* Owner-adopted evidence may remain content-dirty if validator treats owner record as sufficient.
* Surrogate evidence may become stale if final-readpoint freshness is not checked.
* New required artifact adoption may leave this round's own evidence untracked, ignored, or dirty.
* Owner-required decisions may be represented by executor-generated records if binding validation is weak.
* Normal blocker propagation may be confused with validation failure if terminal states are not split.
* New focused tests may accidentally enter current-route closure without manifest adoption.

---

## 10. Rollback Plan

Rollback is governance-only.

If validation fails or the plan is rejected:

* Revert or remove `docs/dvf_3_3_required_artifact_disposition_seal_plan.md`.
* Revert any future disposition seal tooling and focused tests.
* Discard generated evidence under `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/`.
* Do not discard owner-supplied input records under `Iris/build/description/v2/owner_inputs/dvf_3_3_required_artifact_disposition_seal/` unless the owner separately requests it.
* Revert any owner-approved manifest adoption patch if the adoption itself is rejected.
* Revert any narrow `.gitignore` exception introduced by this round if its disposition row is rejected.
* If owner adoption is rejected or final dirty-clean proof fails, downgrade affected rows to blocker rather than preserving the owner-adopted label as passable.
* If surrogate freshness fails, downgrade the row to blocker or explicit non-hash exception with narrowed claim boundary.
* If new required artifact self-preservation fails, remove the adoption proposal or block final ready.
* If owner decision record binding fails, downgrade the affected rows to `owner_pending` or blocker.
* If ignored diagnostic coverage denominator has bare diagnostics, block final ready and keep the report as `validation_failed` or `machine_pass_blocked`.
* Do not revert unrelated dirty worktree changes.
* Do not restore, delete, regenerate, or rewrite source / rendered / Lua bridge / runtime / package artifacts as rollback for this plan.
* Preserve failed evidence only as diagnostic trace if it clearly says FAIL / blocked and makes no PASS claim.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Hub & Spoke boundary remains unchanged.
* Iris remains 100% Lua at runtime.
* Runtime/build-time separation must remain intact.
* Required-validation manifest entries are governance gates, not writer authority.
* Live required artifact denominator must be derived from the live manifest.
* `dirty` must use content diff, not Windows stat / timestamp diagnostics.
* `ignore_rule_match` and `effectively_ignored` must remain separate.
* stated `ignored 19` divergence must use `ignore_rule_match`-required count; `effectively_ignored` is a separate blocker count.
* Problem closure denominator is dirty union active ignored union effectively ignored union untracked required artifact rows.
* Ignored diagnostic coverage denominator is `ignore_rule_match`-required union `effectively_ignored`.
* No row in the ignored diagnostic coverage denominator may remain as bare diagnostic.
* Existing untracked required artifacts require zero count or explicit disposition routing.
* Broad staging root unignore is forbidden.
* Tracking status is not authority status.
* Ignored status is not deletion approval.
* Hash surrogate is not original artifact preservation.
* Schema must keep `axis`, `axis_disposition`, `preservation_result`, and `passability` separate.
* `tracked_hash_surrogate` and `explicit_non_hash_exception` are `preservation_result` values, not `axis_disposition` values.
* Explicit non-hash exception must narrow the claim boundary.
* Dirty required artifacts cannot PASS without adoption, regeneration proof, revert, or blocker routing.
* Owner adoption cannot bypass dirty-state guard; adopted dirty rows require final content-dirty count 0.
* Owner-required decisions require owner-supplied repo-relative path / sha256 / identity / role-bound records; executor-generated owner decision records are invalid.
* Tracked clean negative `.gitignore` exception diagnostic rows do not require per-artifact owner decision when automatically disposed as preserved-by-tracking, but automatic passability requires a validated owner auto-seal rule ratification record.
* Authoritative owner decision records live outside executor-produced staging evidence; staging may only report validation and path/hash binding.
* Authoritative owner rule-ratification records live outside executor-produced staging evidence; staging may only report validation and path/hash binding.
* Any owner input record referenced by final or parent-consumable reports must have tracked / not ignored / not effectively ignored / clean VCS preservation status reported, or final `ready` is blocked.
* Tracked hash surrogate rows require final-readpoint freshness proof.
* `regeneration_required` passability requires protected surface derivation proof and zero protected-surface intersection.
* New artifacts adopted into the live required manifest require tracked / not effectively ignored / dirty-free proof or same-ledger `preservation_result=tracked_hash_surrogate` or `preservation_result=explicit_non_hash_exception`.
* Manifest removal candidates require owner decision and consumer scan.
* Blockers must prevent machine PASS.
* `complete_with_blockers` must always co-occur with `machine_pass_blocked=true` and `ready=false`.
* `complete_with_blockers` must be described in ledger packets as classification-complete, not closeout-complete.
* Existing sealed bodies are read-only unless separately reopened.
* Source / rendered / Lua bridge / runtime / package mutation remains forbidden.
* Independent review, owner seal, and canonical seal remain separate axes.
* Release / package / Workshop / B42 / deployment readiness remain non-claims.
* Existing dirty user changes must not be reverted.

---

## 12. Expected Closeout State

Expected closeout for this planning artifact:

* `plan_document_complete`

Expected closeout for future execution:

* `ready / required_artifact_disposition_problem_status=SOLVED / parent_required_surface_disposition_ready_for_rerun / governance_only / independent_review_gate=BLOCKED` when dirty required artifact final content-dirty count is `0`, every ignored required artifact row has a sealed tracking / surrogate / exception / manifest-removal-candidate / blocker route, ignored diagnostic coverage has `bare_diagnostic_count=0`, tracked clean negative `.gitignore` exception rows are automatically or explicitly disposed as preserved-by-tracking only with validated owner auto-seal rule ratification when automatic passability is used, owner-required decisions have bound owner-supplied records, final recensus has no unresolved blocker, current-route regression passes, protected derivation and no-mutation pass, validators pass, and the parent compatibility contract is hash-bound. This still requires parent Phase 0 / Phase 5 / Phase 7 rerun before parent `machine_pass_governance_only`.
* `complete_with_blockers / required_artifact_disposition_problem_status=SOLVED_WITH_MACHINE_BLOCKERS / machine_pass_blocked=true / blocked_with_required_surface_disposition_packet / governance_only` when every dirty / ignored / untracked required artifact row is classified and blockers are intentionally propagated to stop machine PASS. This state solves the disposition classification problem but is not closeout complete and cannot be reported without `ready=false`.
* `owner_pending / required_artifact_disposition_problem_status=OWNER_PENDING / blocked_with_required_surface_disposition_packet / owner_adjudication_required / governance_only` when one or more rows require owner-supplied decision records, owner auto-seal rule ratification, owner seal, manifest removal approval, or authority mutation outside this plan.
* `validation_failed / required_artifact_disposition_problem_status=VALIDATION_FAILED / blocked / no_authority_mutation` when recensus, disposition validation, blocker propagation, current-route regression, owner record binding, owner input record VCS preservation, ignored diagnostic coverage, untracked routing, parent compatibility contract, or protected no-mutation checks fail unexpectedly.

The expected execution closeout is not bare `complete`. Canonical completion requires machine PASS, artifact-bound independent review PASS, owner seal, and final sign-off as separate bound axes.
