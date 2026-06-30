# Implementation Plan

> Status: revised plan / roadmap-derived / codebase-inspected / final-review WARN required revisions incorporated / Cycle 2 top-doc sync-state fix incorporated / required-artifact-disposition predecessor compatibility incorporated / DVF 3-3 current-route authority and required-evidence integrity closure / governance-only / no source-rendered-runtime-package mutation planned / execution readiness requires re-review
> 작성일: 2026-06-29
> Roadmap input: `C:/Users/MW/.codex/attachments/4f46d21f-f28f-403e-b0a5-854bee5438cc/pasted-text.txt` / sha256 `A73FE26F706F8DA962D10A2CFF12CDBC10E501C14260EDB2ABD00FA4E20DA8DD` / lines `604`
> Feedback input: `C:/Users/MW/.codex/attachments/df1ff22d-61d0-4b13-ba48-49b3b3b7321d/pasted-text.txt` / sha256 `447F394C11E09186C76CB6BFD7159018C5D558B97D0315AE6EA7CB244BC30CDE` / lines `277` / verdict `WARN` / required revisions incorporated
> Feedback input: `C:/Users/MW/.codex/attachments/2a880a91-2cb1-467a-9ca0-a8daff6640a4/pasted-text.txt` / sha256 `D24BD78FE50321F0363121DBF58FE2712B3B9A3285DE295EF016F68EAE030905` / lines `203` / verdict `WARN / PASS branch` / top-doc sync-state revision incorporated
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Top authority: `docs/Philosophy.md`
> Current ecosystem readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Direct plan artifact: `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_plan.md`
> Compatible predecessor preflight artifact: `docs/dvf_3_3_required_artifact_surface_preflight_census_plan.md`
> Compatible predecessor disposition artifact: `docs/dvf_3_3_required_artifact_disposition_seal_plan.md`
> Compatible predecessor disposition evidence root: `Iris/build/description/v2/staging/dvf_3_3_required_artifact_disposition_seal/`
> Working round identifier: `dvf_3_3_current_route_authority_required_evidence_integrity_closure`
> Primary evidence root target: `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/`
> Phase granularity decision for this plan: 9-phase split. This keeps package-guard probing and final seal/review state separate from baseline inventory, integrity hardening, and integrated route validation.
> Independent review gate: `independent_review_gate=BLOCKED` until a non-Claude / non-roadmap-author artifact-bound review is present.
> Canonical seal boundary: machine PASS is not independent review PASS, owner seal, release readiness, or canonical seal completion.

---

## 1. Objective

DVF 3-3 current route의 기존 `PASS / closure_enforced=true` 계열 판정을 더 강한 governance-only closure로 재봉인하기 위한 실행 계획을 작성한다.

이 계획의 목적은 runtime 기능을 추가하거나 Iris 데이터를 다시 쓰는 것이 아니다. 현재 route가 소비하는 authority reference, required artifact, deterministic rebuild evidence, tool inventory, VCS state, top-doc readpoint가 같은 checkout과 같은 readpoint에서 정렬되어 있는지 fail-closed로 증명하는 것이다.

This plan is allowed to solve governance-surface blockers that prevent that proof, including missing/stale authority references, required-artifact identity/freshness gaps, timestamp drift classification, tool/VCS inventory mismatch, and dirty/ignored required-surface disposition. A blocked preflight state is therefore not a terminal instruction to abandon the problem; it is a routing state that prevents false PASS while the plan moves into disposition, owner adjudication, or rerun-bound remediation.

완료 후 허용되는 최대 machine claim은 다음으로 제한한다.

```text
DVF 3-3 current route / authority / required-evidence integrity closure has
governance-only machine evidence that current authority references, required
artifact identity/freshness, deterministic rebuild, tool/VCS inventory,
dirty-state rejection, top-doc sync draft/apply state, current-route validation, and Lua syntax
validation were checked at the same readpoint.

This does not open source writer authority, rendered regeneration, Lua bridge
mutation, runtime chunk replacement, package payload mutation, release
readiness, Workshop readiness, manual QA, public-facing text acceptance,
semantic quality completion, independent review completion, or canonical seal
completion.
```

이 계획은 다음 보류 항목을 실행 계획 레벨에서 이렇게 처리한다.

* Round identifier는 `dvf_3_3_current_route_authority_required_evidence_integrity_closure`를 working identifier로 선택한다. Owner가 실행 전 다른 이름을 확정하면 문서와 artifact root를 일괄 대체한다.
* Phase granularity는 9-phase split으로 선택한다.
* Independent review 상태 토큰은 기본값을 `independent_review_gate=BLOCKED`로 둔다. `canonical_review_pending`은 이 BLOCKED 상태의 하위 sub-state일 뿐이며, 대체 표현이 아니다.
* Independent review gate 해제 조건은 non-Claude 및 non-roadmap-author reviewer가 생성한 artifact-bound review record다. Machine PASS, owner approval, owner seal, or this plan text cannot satisfy this gate.
* `preflight_blocked_required_dirty_surface` is a closure-entry blocker, not a prohibition on remediation. It blocks seal progression until the required surface is dispositioned and the relevant preflight / VCS checks are rerun at a bound readpoint.
* `dvf_3_3_required_artifact_disposition_seal` is a compatible predecessor lane for that required-surface disposition. Its `parent_closure_input_packet.json` may clear the disposition queue only when parent Phase 0 / Phase 5 accept the same readpoint, manifest hash, denominator hash, final recensus hash, and rerun binding. It never substitutes for this parent plan's final current-route PASS, independent review, owner seal, or canonical seal gates.
* Optional isolated package guard probe는 기본적으로 보류한다. 별도 owner 승인 없이는 protected package surface no-mutation proof까지만 수행하며, isolated package guard probe와 package readiness는 모두 non-claim이다.
* Owner seal / token sign-off는 final canonical seal claim의 별도 축이다.
* Top-doc sync claim은 `top_doc_sync_state`로만 표현한다.
  * `top_doc_sync_state=draft_prepared_owner_application_pending`
  * `top_doc_sync_state=owner_applied_and_validated`
  * `top_doc_sync_state=not_claimed`
* Owner-applied top-doc update가 없으면 `top-doc sync PASS` 또는 `top_doc_sync_state=owner_applied_and_validated` claim은 금지한다.

---

## 2. Scope

이 계획은 Iris DVF 3-3 current route를 둘러싼 governance / validation surface만 다룬다.

포함 범위:

* current route baseline census
* authority manifest와 top-doc canonical reference inventory
* authority manifest role adoption report
* candidate-to-live required manifest adoption sequence validation
* required current artifact identity / freshness / producer / consumer manifest
* dirty required artifact fail-closed policy
* pre-existing dirty required artifact intersection blocker
* required dirty / ignored / untracked surface disposition lane and rerun gate
* optional predecessor required artifact surface preflight resolution handoff intake, if generated at the same readpoint
* optional predecessor required artifact disposition seal packet intake, if generated at the same readpoint and mapped to this parent round
* deterministic rebuild output의 stable hash / field drift 판정
* tool inventory, active closure count, current-route tooling allowlist reconciliation
* tracked / ignored / dirty required surface 검사
* top-doc claim boundary draft preparation
* `top_doc_sync_state` validation
* sealed ledger additive draft generation and owner-applied seal boundary
* wrapper failure propagation fixture
* ambiguous reference-role fail-loud / owner adjudication path
* non-hash exception deterministic identity floor
* hardened current route 재실행
* Lua syntax validation 재실행
* protected source / rendered / Lua bridge / runtime / package no-mutation proof
* owner-gated isolated package guard probe separation
* roadmap provenance repo-relative path + hash rebinding
* change-number to phase-root mapping manifest
* final machine seal bundle, review artifact manifest, owner / independent-review boundary 기록

Primary evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/`

Direct documentation artifact:

* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_plan.md`

Expected execution docs:

* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_claim_boundary.md`
* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_ledger_packet.md`
* optional `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_closeout.md`

Read-only authority / context inputs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/EXECUTION_CONTRACT.md`
* `docs/PLAN_TEMPLATE.md`
* `docs/dvf_3_3_current_route_required_validation_evidence_freshness_reseal_plan.md`
* `docs/dvf_3_3_required_artifact_surface_preflight_census_plan.md`
* `docs/dvf_3_3_required_artifact_disposition_seal_plan.md`
* `docs/dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal_plan.md`
* `docs/dvf_3_3_predecessor_stale_artifact_reentry_guard_plan.md`
* `docs/dvf_3_3_durable_current_authority_surface_alignment_plan.md`

### Explicitly Out Of Scope

* source facts / decisions / overlay_support mutation
* rendered output regeneration as writer authority
* Lua bridge export mutation
* runtime chunk replacement
* package payload mutation
* package publication
* package readiness claim
* isolated package guard probe without explicit owner approval
* Workshop publication
* release / B42 / deployment readiness declaration
* manual in-game QA
* public-facing text quality acceptance
* semantic quality completion
* live migration execution
* predecessor / stale artifact deletion
* old monolith runtime path or legacy bridge fallback restoration
* current route core module count expansion by convenience
* broad staging root unignore
* full historical artifact byte reproducibility
* full clean-checkout historical archive reproducibility
* full clean-checkout required-evidence reproducibility 전면 봉인
* DVF architecture redesign
* unrelated refactor
* direct sealed ledger body rewrite by Codex execution

---

## 3. Non-Goals

이 계획은 다음을 해결하지 않는다.

* Existing `PASS`를 release readiness나 canonical seal로 재해석하지 않는다.
* Required artifact 존재 여부만으로 current evidence integrity를 인정하지 않는다.
* Timestamp-bearing evidence를 무조건 hash 대상에 넣지 않는다.
* Non-hash exception을 우회로 넓히지 않는다. 각 exception은 artifact role, deterministic identity floor, and substitute validation condition을 가져야 한다.
* Tracked status를 authority status로 읽지 않는다.
* Ignored status를 deletable status로 읽지 않는다.
* Historical / diagnostic / fixture mention을 current canonical reference로 승격하지 않는다.
* `2105 / 2084 / 21` predecessor vocabulary를 current hard gate나 runtime deployable authority로 되살리지 않는다.
* `active / silent`, `adopted / unadopted`, `quality_state`, `publish_state`, `runtime_state` vocabulary를 새 의미로 확장하지 않는다.
* Owner approval, owner seal, or machine PASS를 independent review로 대체하지 않는다.
* Current-route runner output을 wrapper가 PASS로 보정하거나 재해석하지 않는다.
* Ambiguous reference role을 자동 분류하거나 silent pass하지 않는다.
* Pre-existing dirty required artifact를 `outside this plan`이라는 이유로 PASS시키지 않는다.

---

## 4. Assumptions

* `docs/Philosophy.md`가 최상위 설계 authority다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 current readpoint를 따른다.
* Iris는 100% Lua runtime module이며, 이 계획의 변경은 offline build / governance tooling / docs surface에 한정한다.
* Runtime / build-time separation은 유지한다.
* Codebase inspection 기준으로 `Iris/_docs/round3/round3_run_contract_tests.py`는 taxonomy-selected current tests와 `Iris/_docs/round3/current_route_required_validations.json`의 required tests를 union으로 실행한다.
* 같은 runner는 required artifact 존재와 JSON field equality / one_of checks를 검사하지만, 현재 구조만으로는 artifact hash, freshness, producer/consumer identity, dirty-state rejection을 충분히 봉인하지 않는다.
* Planning-time inspection 기준으로 `Iris/_docs/round3/current_route_required_validations.json`은 schema `round3-current-route-required-validations-v1`, required artifact count `93`, required test count `48`, generated_at `2026-06-17T16:28:41.744038+00:00`로 관찰됐다. 실행 시점에는 이 값을 재계산하고, 이 숫자를 sacred count로 고정하지 않는다.
* `Iris/_docs/round3/round3_active_core_closure.json`은 current closure count `12`와 current-route tooling allowlist `1`개, `export_dvf_3_3_lua_bridge`만을 허용하는 정책을 가진다.
* 새 integrity tooling은 current core module이 아니다. 현재 route에서 직접 import하지 않고 subprocess wrapper / focused unittest / required-validation helper surface로 격리한다.
* `Iris/_docs/authority/iris_current_authority_manifest.json`은 Phase 1 validation 전까지 `candidate machine-readable authority index / inventory input`으로만 읽는다. It is a validation target, not a new authority layer.
* `iris_current_authority_manifest.json` may gain a role-qualified current authority index role only after Phase 1/2 validation and a top-doc sync-state report produce an adoption report. Even then, it does not replace source facts, decisions, rendered output, runtime authority, or top docs.
* Current route required-validation manifest entry는 governance gate이며 source / rendered / Lua bridge / runtime / package writer authority가 아니다.
* Generated staging evidence는 `.gitignore`상 많은 root가 명시적으로 ignore / unignore되어 있다. 새 root의 preservation strategy는 broad staging unignore가 아니라 minimum tracked artifact plus hash-manifest surrogate를 기본으로 한다.
* Dirty working tree changes outside this plan must be preserved. Planning-time `git status --short` shows many pre-existing modified staging artifacts unrelated to this document; execution must distinguish pre-existing dirty state from round-owned mutation.
* If any pre-existing dirty path intersects with a required current artifact, Phase 0 must stop seal progression with `preflight_blocked_required_dirty_surface` and enter required-surface disposition mode. It must not be passed through as a preservation exception or machine PASS input.
* Optional package guard probe는 package readiness가 아니다. 별도 승인 없이는 package publication, package payload mutation, package output adoption을 열지 않는다.
* Protected package surface no-mutation hashing and isolated package guard probing are separate checks. The former is required; the latter is owner-gated and optional.
* `docs/EXECUTION_CONTRACT.md` and `docs/PLAN_TEMPLATE.md` compliance must be checked as part of plan and execution validation. If either authority input is missing or not applicable in a future checkout, Phase 0 records a fail-loud rationale.
* The external attachment path for the roadmap is planning provenance only. Execution evidence must bind the adopted plan by repo-relative path plus sha256, not by an ephemeral local attachment path.
* Top-doc synchronization has three allowed states: `draft_prepared_owner_application_pending`, `owner_applied_and_validated`, and `not_claimed`. Draft preparation is not top-doc sync completion.
* `top_doc_sync_state=not_claimed` is valid, but execution should prefer at least `draft_prepared_owner_application_pending` unless Phase 0 records an explicit reason to omit top-doc draft generation.
* Canonical seal requires machine evidence, non-Claude / non-roadmap-author independent review binding, owner seal, and final token sign-off as separate axes.

---

## 5. Repository Areas Affected

### Code

Expected new offline tooling surfaces:

* `Iris/build/description/v2/tools/build/dvf_3_3_current_route_authority_required_evidence_integrity_closure.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py`

Read-mostly existing surfaces:

* `Iris/_docs/round3/round3_run_contract_tests.py`
* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/_docs/round3/round3_active_core_closure.json`
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/_docs/authority/iris_current_authority_manifest.json`
* `Iris/build/description/v2/tools/build/INVENTORY.md`
* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/tools/package_iris.ps1`

Direct edits to `Iris/_docs/round3/round3_run_contract_tests.py` are allowed only if wrapper integration cannot expose required fail-closed output or if a narrow harness/evidence-write defect is proven. A wrapper must not reinterpret runner failures as success.

No runtime Lua source mutation is planned.

### Docs

Direct docs mutation in this planning task:

* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_plan.md`

Expected future execution docs:

* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_claim_boundary.md`
* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_ledger_packet.md`
* optional `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_closeout.md`

Expected staged top-doc synchronization drafts from future execution:

* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_roadmap_update_draft.md`
* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_decisions_update_draft.md`
* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_architecture_update_draft.md`

Codex execution must not directly rewrite existing sealed `DECISIONS.md` / `ARCHITECTURE.md` bodies in this round. The default path is staged additive draft generation plus owner-applied single-writer ledger seal. If the owner explicitly authorizes direct top-doc editing in a later execution, that execution must add a sealed-body immutability / additive-only diff guard and prove existing sealed entry body byte-modification count `0`.

### Config

Possible additive allowlist / preservation edits:

* `.gitignore`, only if new tools/tests or minimum tracked evidence surrogates need explicit tracking.

Broad staging root unignore is out of scope.

### Generated Artifacts

Primary future evidence root:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/`

Expected phase subroots:

* `phase0/` for scope lock and baseline census
* `phase1/` for authority reference inventory
* `phase2/` for candidate required artifact identity manifest
* `phase3/` for sandbox validation, live additive adoption diff, integrity gate, and negative fixtures
* `phase4/` for deterministic rebuild and drift disposition
* `phase5/` for tool inventory / VCS / closure count reconciliation
* `phase6/` for top-doc draft preparation, `top_doc_sync_state`, and claim-boundary scans
* `phase7/` for integrated current route and Lua syntax validation
* `phase8/` for final machine seal bundle and review gate records
* `phase_change_mapping_manifest.json` for the explicit Change 1~9 to phase0~phase8 mapping

Generated artifacts are evidence outputs, not runtime payloads.

---

## 6. Planned Changes

### Change 1 - Scope Lock / Baseline Census

Purpose:

Freeze the execution boundary before any manifest or docs synchronization work.

Files:

* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_claim_boundary.md`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/phase0/*`

Implementation Notes:

* Record current route command, manifest hash, runner hash, active closure hash, top-doc hashes, authority manifest hash, and git dirty-state.
* Record that release / package / public text / manual QA / live migration are non-claims.
* Capture baseline current route result without treating an old count as final truth.
* Capture pre-existing dirty files separately from round-owned outputs.
* If a predecessor required artifact surface preflight packet exists, consume its early blocker input for diagnosis and its resolved input for parent entry when available. Parent Phase 0 still recomputes the dirty required artifact intersection at the same checkout readpoint.
* If predecessor packet readpoint, manifest hash, or required artifact denominator differs from parent Phase 0 recomputation, fail loud and treat the predecessor packet as advisory only.
* If a predecessor required artifact disposition seal packet exists, consume it only as `required_surface_disposition_predecessor_packet`. It must bind `predecessor_round_id=dvf_3_3_required_artifact_disposition_seal`, `parent_round_id=dvf_3_3_current_route_authority_required_evidence_integrity_closure`, readpoint id, manifest sha256, required artifact denominator sha256, final recensus report sha256, and `parent_rerun_required=true`.
* A predecessor disposition terminal state of `ready` means only that the parent may continue to Phase 0 / Phase 5 rerun validation. A predecessor terminal state of `complete_with_blockers`, `machine_pass_blocked`, `owner_pending`, or `validation_failed` keeps parent seal progression blocked and maps to `blocked_with_required_surface_disposition_packet` or `blocked / no-authority-mutation`.
* Intersect pre-existing dirty files with the current required artifact set. Any overlap blocks seal progression as `preflight_blocked_required_dirty_surface` and emits a disposition queue instead of abandoning the closure problem.
* Required-surface disposition mode may classify each blocker as owner-intended artifact update, generated evidence drift, ignore/tracking policy mismatch, stale required artifact, missing authority reference, or unrelated checkout drift. It must not mutate source/rendered/runtime/package surfaces without a later approved action.
* After disposition actions are completed or owner-adjudicated, rerun Phase 0 and Phase 5 VCS checks before any Phase 7 current-route PASS can be claimed.
* Verify `tools/check_lua_syntax.ps1`, `docs/EXECUTION_CONTRACT.md`, and `docs/PLAN_TEMPLATE.md` path existence or record a fail-loud not-applicable rationale.
* Generate a mapping manifest that binds Change 1~9 to phase0~phase8 evidence roots and blocks off-by-one interpretation.
* Record this plan artifact as the repo-relative roadmap consumption surface with sha256.

Validation:

* Scope lock report has no source/rendered/runtime/package mutation claim.
* Baseline census is read-only.
* Protected surface pre-hash report exists.
* Pre-existing dirty required artifact intersection count is 0, or a required-surface disposition queue exists and seal progression is explicitly held.
* Any consumed predecessor census packet matches the parent readpoint, manifest hash, and required artifact denominator, or is explicitly rejected as advisory-only.
* Any consumed predecessor disposition seal packet matches parent readpoint, manifest hash, denominator hash, final recensus hash, parent round id, and terminal-state mapping, or is explicitly rejected as advisory-only.
* Required authority input path validation is PASS or explicitly blocked.
* Change-to-phase mapping manifest exists.
* Repo-relative plan artifact hash binding exists.

---

### Change 2 - Canonical Authority Reference Inventory

Purpose:

Inventory top docs, authority manifest, runner configs, current route manifest, closeouts, and DVF contract docs so references can be role-qualified instead of stale current claims.

Files:

* `Iris/_docs/authority/iris_current_authority_manifest.json`
* `docs/DECISIONS.md`, read-only input for this change
* `docs/ARCHITECTURE.md`, read-only input for this change
* `docs/ROADMAP.md`, read-only input for this change
* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/phase1/*`

Implementation Notes:

* Classify references as `current canonical`, `current required gate`, `governance-only current`, `historical trace`, `diagnostic fixture`, `predecessor trace`, `stale invalid`, or `missing invalid`.
* Treat missing/stale invalid canonical references as final PASS blockers.
* Preserve historical/provenance mentions when role-qualified.
* Treat `iris_current_authority_manifest.json` as candidate authority index / inventory input until validation and adoption report exist.
* Route ambiguous reference roles to fail-loud / owner adjudication. Do not auto-classify them.
* Generate additive supersession entry drafts rather than editing sealed ledger bodies.

Validation:

* Missing canonical authority reference count is 0.
* Stale canonical authority reference count is 0.
* Ambiguous canonical reference role count is 0, or execution is blocked for owner adjudication.
* Authority manifest role adoption report exists before any current index claim.
* False-positive allowlist exists for quoted, negated, historical, or provenance-only references.

---

### Change 3 - Required Artifact Identity Manifest

Purpose:

Upgrade required current artifacts from existence/field-check records to identity-bound artifacts.

Files:

* sandbox candidate manifest under `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/phase2/`
* `Iris/_docs/round3/current_route_required_validations.json`, live adoption target only after candidate validation
* `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/phase2/*`

Implementation Notes:

* Define schema fields for path, role, authority class, producer, consumer, required fields, hash mode, freshness mode, normalization rule, exception class, exception justification, dirty-state policy, and required tracked/not ignored policy.
* Supported hash modes are full sha256, normalized content sha256, field-bound identity hash, generated bundle hash, and non-hash exception.
* Non-hash exceptions require explicit alternative checks and a deterministic identity floor such as size + schema + field-set, producer-recorded content signature, or another artifact-role-specific stable signature.
* Non-hash exceptions must declare a class ceiling, allowed artifact role list, and substitute validation conditions. If execution cannot justify all three, machine PASS is blocked.
* The final machine report must bind each non-hash exception class ceiling together with its allowed role list and substitute validation condition; a numeric ceiling alone is not sufficient evidence.
* Generate the identity manifest first as a sandbox/staging candidate. Live manifest mutation is not allowed in this change.
* Avoid self-reference cycles in final reports and review bundles.

Validation:

* Manifest schema validation.
* Hash-mode validation.
* Non-hash exception validation.
* Non-hash exception artifact role list and deterministic identity floor validation.
* Non-hash exception class ceiling, allowed role list, and substitute validation condition validation.
* Self-reference cycle detection.
* Producer/consumer resolution.
* Candidate manifest validation before live adoption.

---

### Change 4 - Required Evidence Integrity Gate

Purpose:

Make current route fail closed on stale content, missing freshness, hash mismatch, dirty required artifact, skipped required test, and candidate manifest substitution.

Files:

* `Iris/build/description/v2/tools/build/dvf_3_3_current_route_authority_required_evidence_integrity_closure.py`
* `Iris/build/description/v2/tools/build/run_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py`
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/phase3/*`

Implementation Notes:

* Prefer a wrapper / validator around `round3_run_contract_tests.py`.
* The wrapper may augment runner output with manifest hash, artifact identity, freshness, git dirty-state, protected mutation, and claim-boundary evidence.
* The wrapper must preserve runner exit code and required validation failure semantics.
* Candidate-to-live sequence is fixed: candidate generation -> sandbox focused validator and negative fixtures -> additive live manifest adoption diff -> live manifest hash pinning -> final current route rerun.
* Final current route consumes the live `Iris/_docs/round3/current_route_required_validations.json` only. Official wrapper candidate override is forbidden; candidate override is allowed only inside sandbox fixture tests.
* Negative fixtures must use sandbox copies, not live manifest or sealed evidence roots.

Validation:

* Dirty required artifact fail-closed fixture.
* Stale required artifact fail-closed fixture.
* Hash mismatch fail-closed fixture.
* Missing freshness fail-closed fixture.
* Candidate manifest substitution fail-closed fixture.
* Synthetic runner non-zero / required-FAIL propagation fixture proving wrapper result is FAIL.
* Current-route recursion guard fixture.
* Live additive adoption diff validation.
* Existing live required artifact removal count `0` and required test removal count `0`.
* Existing live required artifact/test modification count `0`, except additive identity/freshness metadata under the approved adoption diff.
* Live manifest hash pinning report.

---

### Change 5 - Deterministic Evidence Rebuild / Drift Disposition

Purpose:

Prove that required governance evidence can be regenerated without meaningless timestamp/hash drift, or classify unstable fields as explicit exceptions.

Files:

* `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/phase4/*`

Implementation Notes:

* Rebuild into sandbox / staging sinks only.
* Run at least two rebuilds.
* Normalize or exclude only declared non-semantic fields, such as generated timestamps, run-local temp paths, host-local absolute paths, unordered JSON object keys, allowed platform separators, and allowed line ending differences.
* Enumerate the non-semantic field allowlist per evidence artifact before normalization.
* Semantic fields must not be hidden by normalization.

Validation:

* Run A / Run B normalized hash parity.
* Raw drift classification.
* Timestamp drift disposition.
* Per-artifact non-semantic field allowlist report.
* Semantic field drift count is 0.
* No live mutation report.

---

### Change 6 - Tool Inventory / VCS / Closure Count Reconciliation

Purpose:

Ensure current-route tool inventory, active closure count, tooling allowlist, and tracked/ignored/dirty required surface match the actual checkout.

Files:

* `Iris/_docs/round3/round3_active_core_closure.json`
* `Iris/build/description/v2/tools/build/INVENTORY.md`
* `Iris/_docs/round3/current_route_required_validations.json`
* `.gitignore`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/phase5/*`

Implementation Notes:

* Recompute active current core modules from import graph.
* Recompute current-route tooling allowlist.
* Keep regeneration tooling separate from current core modules.
* Classify new tools as current required validation helper, regeneration tooling, historical reproduction, diagnostic advisory, fixture, or archive/delete eligible.
* Required path checks cover missing, ignored, untracked, dirty without exception, top-doc required reference dirty, current route runner dirty, and current-required manifest dirty.
* If predecessor preflight VCS outputs exist, reconcile dirty / ignored / tracked / untracked / field-pass / hash-candidate / non-hash-candidate counts against parent recomputation. Prefer post-resolution predecessor outputs when present, but predecessor outputs cannot override parent fail-closed checks.
* If predecessor disposition seal outputs exist, reconcile `axis`, `axis_disposition`, `preservation_result`, `passability`, `machine_pass_blocked`, `bare_diagnostic_count`, owner decision binding, protected surface derivation status, and final recensus hashes against parent recomputation. Prefer compatible predecessor disposition rows as the parent disposition ledger input, but they cannot override parent VCS / current-route / protected no-mutation checks.
* Pre-existing dirty required artifact overlap is a seal-progression blocker, not a preservation exception and not an instruction to leave the problem unsolved.
* Generate a required-surface disposition ledger for every dirty, ignored, untracked, missing, stale, or hash-ineligible required artifact that prevents closure.
* Each disposition row must choose one owner-reviewable path: accept as intentional required artifact update with hash/freshness rebinding, move to generated evidence drift remediation, adjust ignore/tracking policy with minimum-scope diff, classify as non-hash exception with deterministic substitute checks, reject as unrelated checkout drift, or escalate for owner adjudication.
* Dirty exceptions target final count `0` for machine PASS. Any remaining dirty required exception holds seal progression as `blocked / no-authority-mutation`; it does not mean the remediation plan must stop.
* A predecessor disposition `ready` state still requires parent Phase 5 VCS required surface PASS and parent Phase 7 current-route PASS before this plan may claim `machine_pass_governance_only`.
* A predecessor disposition `complete_with_blockers`, `machine_pass_blocked`, `owner_pending`, or `validation_failed` state must surface as parent `blocked_with_required_surface_disposition_packet` or `blocked / no-authority-mutation`; it must not be normalized into PASS.
* After any accepted disposition action, rerun the required-surface census and parent VCS surface report before current-route PASS can be used as closure evidence.
* Do not broaden staging unignore as a convenience fix.

Validation:

* Active closure count report.
* Tooling allowlist report.
* Current/historical/diagnostic route split validation.
* Unexpected tool reentry scan.
* VCS required surface report.
* Predecessor census VCS surface reconciliation report, if predecessor outputs are consumed.
* Predecessor required artifact disposition seal reconciliation report, if disposition outputs are consumed.
* Required-surface disposition ledger and rerun binding report, if any blocker was found.
* Pre-existing dirty required surface blocker report.
* Broad staging unignore guard.

---

### Change 7 - Top-Doc Sync / Claim Boundary Reconciliation

Purpose:

Prepare additive top-doc synchronization drafts and record the top-doc sync state so `ROADMAP.md`, `DECISIONS.md`, `ARCHITECTURE.md`, and supporting DVF docs can be aligned by the owner without unguarded sealed-body edits.

Files:

* `docs/ROADMAP.md`, read-only input unless owner separately authorizes direct edit
* `docs/DECISIONS.md`, read-only input unless owner separately authorizes direct edit
* `docs/ARCHITECTURE.md`, read-only input unless owner separately authorizes direct edit
* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_roadmap_update_draft.md`
* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_decisions_update_draft.md`
* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_architecture_update_draft.md`
* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_claim_boundary.md`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/phase6/*`

Implementation Notes:

* Generate top-doc update drafts only after validator evidence exists.
* Actual sealed ledger application is owner single-writer work outside this Codex execution by default.
* If direct editing is explicitly authorized later, run a sealed-body immutability / additive-only diff guard and prove existing sealed entry body byte-modification count `0`.
* Write `top_doc_sync_state=draft_prepared_owner_application_pending` when Codex execution only prepares update drafts.
* Write `top_doc_sync_state=owner_applied_and_validated` only when owner-applied top-doc changes are present, additive-only diff guard passes, and the final current-route readpoint binds those applied docs.
* Write `top_doc_sync_state=not_claimed` if no top-doc draft or owner-applied validation is included in the machine packet. This is valid but non-preferred; execution should prefer `draft_prepared_owner_application_pending` for traceability unless Phase 0 records an explicit omission rationale.
* In `draft_prepared_owner_application_pending`, final machine reports may claim draft preparation and claim-boundary checking, but must not claim `top-doc sync PASS`.
* Separate these claims:
  * current-route validation PASS
  * Lua syntax PASS
  * required artifact identity/freshness PASS
  * deterministic rebuild PASS
  * VCS required surface PASS
  * canonical authority reference sync PASS
  * top-doc sync state checked
  * governance-only machine seal
  * release readiness non-claim
* Preserve stale predecessor, stale bridge, monolith, fixture, and rollback snapshot mentions only with historical / diagnostic / fixture / provenance roles.
* Forbid standalone `complete` without owning axis and review state.

Validation:

* Top-doc reference sync scan.
* Overclaim scan.
* Non-claim boundary scan.
* Stale predecessor doc reentry scan.
* Closeout cross-problem regression scan.
* Additive draft scan.
* `top_doc_sync_state` validation.
* Final report `top-doc sync PASS` prohibition when state is `draft_prepared_owner_application_pending` or `not_claimed`.
* Sealed-body immutability guard, if direct top-doc editing is owner-authorized.

---

### Change 8 - Integrated Current Route / Lua Syntax / Protected Surface Proof

Purpose:

Rerun the hardened current route and Lua syntax checks at the final readpoint.

Files:

* `Iris/_docs/round3/round3_run_contract_tests.py`
* `Iris/_docs/round3/current_route_required_validations.json`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/phase7/*`

Implementation Notes:

* Run full current route with closure enforcement.
* Run Lua syntax validation at the same readpoint.
* Record final current route count from execution output, not from roadmap baseline.
* Carry the `top_doc_sync_state` from Phase 6 into the Phase 7 validation result.
* If `top_doc_sync_state=owner_applied_and_validated`, bind owner-applied doc hashes and additive-only diff report into the same readpoint before final current-route rerun.
* Confirm protected source / rendered / Lua bridge / runtime / package mutation count is 0.
* Confirm protected package surface no-mutation by hashing protected package inputs separately from generated package outputs.
* Optional isolated package guard probe remains disabled unless owner explicitly opens it. If opened, it writes only to an explicit isolated output root and remains non-readiness evidence.
* Optional package probe artifacts must use names that contain `isolated_package_guard_evidence` or an equivalent `isolated_guard_evidence` token, not `package_readiness`, `package_release`, or `publication`.

Validation:

* Full current route PASS.
* `closure_enforced=true`.
* Required validation success.
* Lua syntax PASS.
* Protected surface no-mutation PASS.
* Protected package surface no-mutation PASS.
* `top_doc_sync_state` is present and one of the three allowed values.
* Optional isolated package guard evidence PASS only if separately authorized.

---

### Change 9 - Final Machine Seal Bundle / Review Gate / Ledger Packet

Purpose:

Bundle the machine evidence without claiming independent review, owner seal, release readiness, or canonical seal completion.

Files:

* `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_ledger_packet.md`
* optional `docs/dvf_3_3_current_route_authority_required_evidence_integrity_closure_closeout.md`
* `Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/phase8/*`

Implementation Notes:

* Generate final machine report.
* Generate primary review artifact manifest.
* Generate final artifact hash bundle.
* Include `phase_change_mapping_manifest.json` in the primary review artifact manifest. Missing this manifest blocks machine PASS because the review packet loses Change-to-phase traceability.
* Run no-new-defect self-scan.
* Require final report to read and emit `top_doc_sync_state`.
* If `top_doc_sync_state=draft_prepared_owner_application_pending`, final machine claim must use that exact state and must not say `top-doc sync PASS`.
* If `top_doc_sync_state=owner_applied_and_validated`, final machine claim must include owner-applied doc hashes, additive-only diff validation, and post-application current-route rerun binding.
* If an optional isolated package guard probe is owner-opened, record output root, artifact retention policy, package zip hash disposition, and non-readiness claim boundary in Phase 8. Artifact names must identify the result as isolated guard evidence, not package readiness.
* Bind non-hash exception class ceilings in the final machine report with allowed artifact roles and substitute validation conditions.
* Record `required_artifact_disposition_predecessor_state` when a disposition seal packet was consumed, including predecessor terminal state, `machine_pass_blocked`, readpoint compatibility, denominator compatibility, owner-pending count, blocker count, and parent rerun status.
* Parent `machine_pass_governance_only` requires either no required-surface disposition blocker at Phase 0 / Phase 5, or a consumed predecessor disposition packet with terminal state `ready`, `machine_pass_blocked=false`, `bare_diagnostic_count=0`, compatible readpoint / denominator hashes, and parent rerun-bound VCS / current-route validation PASS.
* Record independent review and owner seal as separate axes.
* Record `independent_review_gate=BLOCKED` unless a non-Claude / non-roadmap-author artifact-bound review is present.
* `canonical_review_pending` may appear only as a sub-state under `independent_review_gate=BLOCKED`.
* Keep canonical seal blocked until artifact-bound independent review, owner seal, and final token sign-off exist.

Validation:

* Final machine report validation.
* Required artifact disposition predecessor state validation, if a predecessor packet was consumed.
* Primary review artifact hash validation.
* Primary review artifact manifest includes `phase_change_mapping_manifest.json`.
* Self-hash cycle guard.
* No-new-defect self-scan.
* Final non-hash exception ceiling / role / substitute-condition binding validation.
* `top_doc_sync_state` claim validation.
* Independent review gate validation with default BLOCKED state.
* Independent review binding validation, if applicable.
* Owner seal binding validation, if applicable.
* Final claim boundary validation.

---

## 7. Validation Plan

### Automated Validation

Expected commands for future execution:

* `uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --out Iris/build/description/v2/staging/dvf_3_3_current_route_authority_required_evidence_integrity_closure/phase7/full_current_route_validation_result.json`
* `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`
* `uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py --mode all`
* `uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py --require-complete`
* `uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py"`

Additional automated checks:

* authority reference inventory validation
* required artifact identity manifest schema validation
* non-hash exception validation
* non-hash exception artifact role list and deterministic identity floor validation
* non-hash exception class ceiling / allowed role list / substitute validation condition validation
* hash self-reference cycle guard
* dirty required artifact negative fixture
* pre-existing dirty required artifact intersection blocker
* deterministic rebuild A/B parity
* per-artifact non-semantic field allowlist validation
* semantic field drift report
* tool inventory / closure count report
* tracked / ignored / dirty required surface report
* manifest candidate-to-live adoption sequence validation
* live manifest existing required artifact/test removal count `0`
* live manifest existing required artifact/test modification count `0` outside approved additive metadata
* wrapper failure propagation fixture
* ambiguous reference-role fail-loud / owner adjudication report
* sealed-body additive-only draft validation
* roadmap provenance repo-relative path + hash validation
* change-to-phase mapping validation
* `top_doc_sync_state` validation
* final report `top-doc sync PASS` prohibition in draft or not-claimed states
* top-doc overclaim and non-claim scan
* protected source / rendered / Lua bridge / runtime / package no-mutation report
* protected package surface no-mutation report separated from optional isolated package guard probe
* optional isolated package guard evidence artifact naming validation, if opened
* primary review artifact manifest includes `phase_change_mapping_manifest.json`

### Manual Validation

* Review top-doc drafts and `top_doc_sync_state` for claim boundary accuracy.
* Review non-hash exception justifications.
* Review false-positive allowlist entries for historical/provenance mentions.
* Review ambiguous reference-role adjudication records.
* Review final ledger packet to ensure machine PASS, independent review, owner seal, and canonical seal remain separate.

### Validation Limits

This execution will not perform:

* no multiplayer validation
* no long-session runtime validation
* no manual in-game validation
* no deployment validation
* no Workshop validation
* no B42 readiness validation
* no package publication validation
* no public-facing text acceptance validation
* no semantic quality completion validation
* no full release checklist
* no live migration execution
* no source/rendered/runtime/package mutation validation beyond no-mutation proof
* no full historical byte reproducibility
* no full clean-checkout historical archive reproducibility
* no full clean-checkout required-evidence reproducibility 전면 봉인
* no public-facing behavior regression sweep
* no external ecosystem compatibility sweep

---

## 8. Risk Surface Touch

### Authority Surface

Validation/governance surface impact only.

This plan may update authority-reference inventories, candidate required-validation manifests, live manifest additive adoption diffs, top-doc update drafts, claim-boundary drafts, and governance evidence packets. It must not mutate source facts, decisions, overlay_support, rendered output, Lua bridge output, runtime chunks, or package payloads as writer authority. It also must not treat `iris_current_authority_manifest.json` as a new authority layer before validation and role-qualified adoption.

### Runtime Behavior Surface

None.

Runtime Lua behavior, Browser / Wiki / Tooltip display policy, runtime renderer, and runtime chunks remain unchanged.

### Compatibility Surface

Low.

External runtime compatibility should not change. Tooling and validation command behavior may become stricter, especially around required artifact identity, freshness, dirty-state, and stale references.

### Sealed Artifact Surface

Governance evidence impact only.

Required artifact identity/freshness manifests and deterministic rebuild evidence may be added. Existing sealed bodies must not be rewritten by Codex execution in this round. Additive top-doc update drafts are allowed; actual ledger application is owner single-writer work unless a later owner-approved execution adds sealed-body immutability guards.

### Public-Facing Output Surface

None.

Top-doc sync-state tracking is governance documentation, not public-facing text acceptance, README release copy, Workshop text, or packaging announcement. Draft-prepared state is not top-doc sync completion.

---

## 9. Risk Analysis

### Architecture Risk

* Wrapper integration could accidentally become a second current-route authority instead of a verifier around the runner.
* `iris_current_authority_manifest.json` could be overread as a new authority layer instead of candidate inventory input.
* Convenience expansion of `current_route_allowed_tooling_modules` could bypass the 12-module current closure.
* Top-doc draft sync could overclaim canonical seal or release readiness before review evidence exists.
* Unguarded sealed ledger edits could violate additive-only authority ownership.
* Stale/historical references could be deleted instead of role-qualified, losing provenance.

### Runtime Risk

* Runtime risk is low because runtime Lua, rendered payload, bridge payload, chunks, and package payloads are not mutation targets.
* The main runtime-adjacent risk is accidental writer invocation during deterministic rebuild or package probe. This must be blocked by sandbox output roots and no-mutation hashing.

### Compatibility Risk

* Runtime compatibility risk is low.
* Validation compatibility risk is medium because stricter identity/freshness checks may reveal existing stale or dirty required evidence and flip current route to FAIL until resolved.

### Regression Risk

* Current-route count changes could be misread as regression if tests are added by manifest adoption. The final count must be recorded from execution output and compared by role, not treated as a sacred baseline.
* Timestamp normalization may hide semantic drift if exception rules are too broad.
* Non-hash exceptions may weaken the integrity closure if class ceiling, allowed role list, and substitute validation condition are not reported together.
* `top_doc_sync_state=draft_prepared_owner_application_pending` could be overread as owner-applied top-doc sync completion if final reports do not use the exact state token.
* Git dirty-state handling may confuse pre-existing unrelated user changes with round-owned mutation, or incorrectly allow a pre-existing dirty required artifact to PASS.
* Package guard probe, if opened, could be misread as package readiness unless artifact names explicitly say isolated package guard evidence.

---

## 10. Rollback Plan

Rollback is governance-hardening rollback, not runtime recovery.

If validation fails or unexpected regressions appear:

1. Stop before top-doc draft generation or top-doc sync-state claim if Phase 0-5 evidence does not support the claim.
2. Discard unadopted top-doc update drafts first.
3. Revert live `current_route_required_validations.json` adoption changes.
4. Revert wrapper / validator / focused test changes.
5. Preserve failed evidence as historical diagnostic trace only if it does not claim PASS.
6. Discard sandbox deterministic rebuild outputs if they are not adopted.
7. Keep protected source / rendered / Lua bridge / runtime / package surfaces unchanged.
8. If blockers remain unresolved after disposition, close the closure claim as `blocked / no-authority-mutation` rather than weakening fail-closed checks.

If integrity gates reveal a large dirty/stale required surface, seal progression should stop at census, disposition ledger, or partial machine packet state. The round may continue in remediation planning / owner-adjudication mode, but it must not convert stale evidence into non-hash exceptions to force a PASS.

If a pre-existing dirty path intersects with a required current artifact, execution enters `preflight_blocked_required_dirty_surface` and no live manifest adoption or top-doc draft sync proceeds until the dirty surface is dispositioned and the relevant preflight checks are rerun.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance.
* Hub & Spoke boundary preservation.
* Iris remains 100% Lua at runtime.
* Runtime/build-time separation.
* Additive amendment preference.
* Sealed ledger body edits are out of Codex execution scope by default; top-doc changes are staged as additive drafts for owner single-writer application.
* Minimal diff preservation.
* Existing dirty worktree changes outside this plan must be preserved.
* Source facts / decisions / overlay_support writer authority must not be bypassed.
* Rendered / Lua bridge / runtime chunk / package payload authority must not be mutated.
* Required-validation manifest entries are governance gates, not writer authorities.
* Current route core closure remains 12 modules unless a separate reviewed scope changes it.
* Current-route tooling allowlist remains narrow and is not a convenience bypass.
* Historical / diagnostic / fixture / predecessor references must stay role-qualified.
* Deterministic rebuild uses sandbox / staging sinks.
* Dirty required artifacts fail closed. Pre-existing dirty required artifact overlap blocks preflight; remaining dirty required exceptions prevent machine PASS.
* Ambiguous reference roles fail loud and route to owner adjudication.
* Non-hash exceptions require artifact role lists and deterministic identity floors.
* Non-hash exception final report entries must bind class ceiling, allowed role list, and substitute validation condition together.
* Optional package guard probe artifacts must be named as isolated guard evidence, not readiness evidence.
* `top_doc_sync_state=not_claimed` is valid but non-preferred; execution should prefer `draft_prepared_owner_application_pending` unless an explicit omission rationale is recorded.
* `phase_change_mapping_manifest.json` must be included in the primary review artifact manifest; omission blocks machine PASS.
* Completion-bearing claims remain axis-qualified.
* `independent_review_gate=BLOCKED` is the default review state until non-Claude / non-roadmap-author artifact-bound review exists.
* Machine PASS, independent review PASS, owner seal, and canonical seal are separate states.
* Release readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, semantic quality completion, public-facing text acceptance, package publication, and live migration remain non-claims.

---

## 12. Expected Closeout State

Expected closeout for this planning artifact:

* `plan_document_complete`

Expected closeout for a future execution of this plan:

* `machine_pass_governance_only / top_doc_sync_state=draft_prepared_owner_application_pending / independent_review_gate=BLOCKED / canonical_review_pending` if machine validation passes, top-doc drafts are prepared, and no owner-applied top-doc validation or artifact-bound non-Claude / non-roadmap-author independent review exists.
* `machine_pass_governance_only / top_doc_sync_state=owner_applied_and_validated / independent_review_gate=BLOCKED / canonical_review_pending` if machine validation passes after owner-applied top-doc changes are hash-bound, additive-only validated, and rerun-bound, but no artifact-bound non-Claude / non-roadmap-author independent review exists.
* `machine_pass_governance_only / top_doc_sync_state=not_claimed / independent_review_gate=BLOCKED / canonical_review_pending` if machine validation passes and the round intentionally omits top-doc draft preparation and owner-applied validation from the machine packet.
* `blocked_with_required_surface_disposition_packet / no-authority-mutation` if dirty / ignored / untracked / stale required surface is found, disposition evidence is produced, but owner-approved remediation or rerun-bound clean evidence is not complete yet. A consumed `dvf_3_3_required_artifact_disposition_seal` packet with `complete_with_blockers`, `machine_pass_blocked`, or unresolved blocker maps here.
* `blocked_with_required_surface_disposition_packet / owner_adjudication_required` if a consumed `dvf_3_3_required_artifact_disposition_seal` packet is `owner_pending`.
* `blocked / no-authority-mutation` if required artifact integrity, deterministic rebuild, VCS required surface, `top_doc_sync_state` validation, current route, Lua syntax, or protected no-mutation checks fail.
* `canonical_seal_allowed` only if machine PASS, artifact-bound independent review PASS, owner seal, and final token sign-off are all present and bound to the same readpoint.

The expected execution closeout is not unconditional `complete` because canonical seal is intentionally gated by independent review and owner-controlled final seal decisions. Bare `complete` is not a valid closeout token for this round. In `draft_prepared_owner_application_pending` and `not_claimed` states, `top-doc sync PASS` is explicitly forbidden. `blocked_with_required_surface_disposition_packet` is a successful diagnostic/remediation handoff state, not a claim that the DVF current-route / authority / seal closure problem should remain unresolved.
