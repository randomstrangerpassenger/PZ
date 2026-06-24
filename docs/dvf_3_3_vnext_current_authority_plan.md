# Implementation Plan

## 1. Objective

`DVF 3-3 vNext Current Authority Plan`을 definition-only governance plan으로 봉인한다.

이 계획의 목적은 frozen `2105 / 2084 / 21` baseline을 복구하는 것이 아니라, 해당 predecessor가 맡고 있던 current authority 역할을 대체할 successor authority model의 scope, vocabulary, artifact boundary, validation expectation, cutover rule, consumer migration principle, ledger reflection boundary를 정의하는 것이다.

이 계획은 successor baseline을 실제 생성하거나 current authority로 승격하는 실행 계획이 아니다. 이 계획 완료 자체는 source / facts / decisions / rendered / Lua bridge / chunk payload 생성, runtime cutover, package readiness, release readiness를 의미하지 않는다.

---

## 2. Scope

이 계획은 DVF 3-3 vNext current authority를 열기 전에 필요한 정의 / 계약 / governance 범위만 다룬다.

포함 범위:

* frozen 2105를 recovery 대상이 아니라 predecessor / comparison / migration input으로 읽는 원칙
* `vNext-CAB` label과 actual sealed baseline identity의 분리
* runtime chunks와 runtime-derived seed의 non-source-authority 지위
* source / facts / decisions / compose profile / body_plan / rendered / runtime authority 성립 조건
* source-to-rendered-to-runtime regeneration이 후속 execution plan의 필수 조건이라는 점
* old runtime chunks와 successor runtime 사이의 delta / parity classification criteria
* `2105 Baseline Consumption Audit` 기반 consumer migration principle
* no-premature-cutover / no-dual-current / single-authority switch 원칙
* DECISIONS / ARCHITECTURE / ROADMAP 직접 mutation이 아니라 reflection draft packet 작성 범위

### Explicitly Out Of Scope

* frozen 2105 byte-level recovery
* 새 baseline 실제 생성
* source manifest instance 생성
* vNext facts / decisions JSONL instance 생성
* vNext rendered output 생성
* Lua bridge export 실행
* chunk manifest / chunk files 생성 또는 교체
* rendered-runtime parity report 실제 산출
* intentional delta ledger 실제 산출
* consumer migration 실제 실행
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` 직접 수정
* current authority cutover
* runtime rollout
* package build
* Workshop / release readiness 선언
* B42 readiness 선언
* manual in-game validation
* Browser / Wiki / Tooltip behavior 변경
* quality exposure 변경
* Layer4 / ACQ_DOMINANT / Acquisition Lexical reopen
* closed readpoint 재판정

---

## 3. Non-Goals

* `2105`를 복구된 것처럼 표현하지 않는다.
* `2105` 숫자를 새 숫자로 단순 치환하지 않는다.
* runtime chunks를 source authority로 승격하지 않는다.
* runtime-derived seed를 recovered source 또는 source-of-truth로 사용하지 않는다.
* current 6-entry facts / decisions / rendered fixture를 full authority로 승격하지 않는다.
* `active / silent` vocabulary를 current writer / validator / runtime vocabulary로 되살리지 않는다.
* `adopted / unadopted`를 quality-pass, publish_state, deletion, suppression 의미로 승격하지 않는다.
* chunks-only authority를 선언하지 않는다.
* rendered output 생성만으로 current authority promotion을 선언하지 않는다.
* chunk generation success만으로 runtime authority cutover를 선언하지 않는다.
* partial output을 current authority로 승격하지 않는다.
* old chunks와 successor chunks가 동시에 current인 dual-authority 상태를 만들지 않는다.
* reflection packet 작성을 core docs mutation 권한으로 해석하지 않는다.

---

## 4. Assumptions

* `Philosophy.md`가 최상위 기준이다.
* `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`의 current Iris / DVF readpoint가 이 계획의 상위 맥락이다.
* current DVF 3-3 authority model은 `facts -> decisions -> compose -> rendered -> Lua bridge -> chunk manifest + chunk files`로 읽는다.
* current deployable runtime authority는 existing chunk manifest + chunk files다.
* runtime chunks는 deployable runtime authority이자 comparison reference지만 source authority는 아니다.
* runtime-derived seed는 non-authority bootstrap seed로만 취급한다.
* current 6-entry facts / decisions / rendered files는 fixture / non-authority다.
* Layer3 current authority reconstruction은 partial readpoint로 닫혀 있으며, 현재 checkout에는 sealed full body-plan v2 source path에서 current runtime chunk text를 결정론적으로 재생성할 full input set이 없다.
* `2105 Baseline Consumption Audit`는 후속 migration input으로만 소비한다.
* sealed artifacts와 sealed decisions는 직접 mutate하지 않고 additive supersession / additive direction artifact로만 보정한다.
* FAIL-LOUD 원칙을 유지한다. source 부재, basis-unavailable, parity 미달, unexplained delta, blocked terminal state는 silent fallback하지 않는다.

---

## 5. Repository Areas Affected

### Code

* None in this plan.

### Docs

Direct plan artifact:

* `docs/dvf_3_3_vnext_current_authority_plan.md`

Direct follow-up direction / contract artifacts this plan may authorize drafting:

* `docs/dvf_3_3_vnext_authority_scope_lock.md`
* `docs/dvf_3_3_vnext_cutover_contract.md`
* `docs/dvf_3_3_vnext_source_authority_conditions.md`
* `docs/dvf_3_3_vnext_runtime_seed_disposition.md`
* `docs/dvf_3_3_vnext_regeneration_requirements.md`
* `docs/dvf_3_3_vnext_consumer_migration_principles.md`
* `docs/dvf_3_3_vnext_ledger_update_packet.md`
* `docs/decisions_vnext_entry_draft.md`
* `docs/architecture_vnext_patch_draft.md`
* `docs/roadmap_vnext_patch_draft.md`

Read-only authority inputs:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/dvf_3_3_vnext_current_authority_roadmap.md`
* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/change_required_index.md`
* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/change_forbidden_index.md`
* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/classified_ledger.jsonl`
* `Iris/build/description/v2/staging/2105_baseline_consumption_audit/executing_consumer_impact.md`

Canon targets not directly modified by this plan:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Actual mutation of those canon targets requires a separate approved reflection application or a follow-up closeout step.

### Config

* None in this plan.

### Generated Artifacts

None directly in this plan.

The following are follow-up execution-plan artifact families, not direct outputs of this plan:

* `dvf_3_3_vnext_input_manifest.json`
* `dvf_3_3_vnext_facts.jsonl`
* `dvf_3_3_vnext_decisions.jsonl`
* `compose_profiles_vnext.json`
* `dvf_3_3_vnext_rendered.json`
* `rendered_runtime_parity.json`
* `vnext_parity_matrix.json`
* `intentional_delta_ledger.jsonl`
* `chunk_generation_result.md`
* `lua_bridge_export_result.md`

---

## 6. Planned Changes

### Change 1 - Scope Lock / Successor Identity

Purpose:

이 계획이 frozen 2105 recovery가 아니라 successor authority model definition plan임을 봉인한다.

Files:

* `docs/dvf_3_3_vnext_authority_scope_lock.md`

Implementation Notes:

* `vNext-CAB`를 cutover 전까지 program / roadmap / authority-model label로 정의한다.
* actual current baseline identity는 후속 regeneration 산출물의 sealed count, manifest fingerprint, rendered hash, chunk manifest fingerprint가 나온 뒤 별도 cutover artifact에서만 봉인한다고 명시한다.
* scope-lock 문서에서 `successor`, `predecessor`, `comparison reference`, `migration input`, `seed candidate`, `current authority`, `deployable runtime authority`, `source authority` 용어를 명문화한다.
* successor relation은 recovery가 아니라 successor / supersession relation으로 둔다.
* number substitution, chunks-only authority, recovery disguise를 금지한다.

Validation:

* identity wording scan
* forbidden claim scan
* `vNext-CAB` label usage review
* baseline identity placeholder check

---

### Change 2 - Runtime-Derived Seed Status

Purpose:

runtime-derived seed의 지위를 non-authority bootstrap으로 제한한다.

Files:

* `docs/dvf_3_3_vnext_runtime_seed_disposition.md`

Implementation Notes:

* seed는 `provenance: derived-from-runtime-chunks`를 가진 non-authority bootstrap으로 정의한다.
* seed-derived artifact는 provenance 없이 생성하지 않는다.
* seed row는 source / facts / decisions validation 전까지 current fact가 될 수 없다고 명시한다.
* existing chunks는 deployable runtime authority + comparison reference로만 유지한다.

Validation:

* seed provenance rule review
* source authority non-promotion scan
* runtime chunks role wording review

---

### Change 3 - Source Authority Conditions

Purpose:

successor source authority의 성립 조건을 정의한다.

Files:

* `docs/dvf_3_3_vnext_source_authority_conditions.md`

Implementation Notes:

* source authority는 fixture / staging / derived-only 상태로 성립하지 않는다고 정의한다.
* source absence / unresolved / basis-unavailable / blocked 상태를 fail-loud terminal state로 표현한다.
* source universe manifest는 후속 execution plan 산출물이며, 이 계획은 schema / contract requirement만 정의한다.
* `genuine-zero`는 단순 부재 alias가 아니라 관측 가능한 source universe 안에서 해당 row가 진짜 0임을 증명한 경우에만 허용되는 terminal state로 좁혀 정의한다.

Validation:

* source authority wording review
* planned-only artifact scan
* basis-unavailable / blocked terminal state review
* `genuine-zero` proof-condition review

---

### Change 4 - Facts / Decisions / Profile / Rendered Authority Contract

Purpose:

facts / decisions / compose profile / body_plan / rendered authority가 어떤 조건으로 성립하는지 정의한다.

Files:

* `docs/dvf_3_3_vnext_regeneration_requirements.md`

Implementation Notes:

* shared requirements 문서 안에 `input authority requirements`와 `rendered authority requirements` 섹션을 분리한다.
* facts와 decisions의 책임을 분리한다.
* body_plan은 second authority가 아니라 compose profile 구현 표면 / alias label로 둔다.
* rendered validator output이 decisions에 역류하지 않도록 한다.
* rendered output actual generation은 후속 execution plan으로 유보한다.
* `confirmed / genuine-zero / basis-unavailable / blocked` terminal state를 정의한다.
* advisory style / structural signal / quality signal은 hard gate로 승격하지 않는다.
* shared requirements 문서가 비대해지면 Change 4 contract는 별도 input/rendered authority contract 문서로 분리할 수 있다.

Validation:

* facts / decisions boundary review
* body_plan authority wording scan
* no-rendered-input-to-decisions guard
* terminal state wording review
* advisory-to-hard-gate scan

---

### Change 5 - Runtime Regeneration Requirements

Purpose:

`rendered -> Lua bridge -> chunk manifest + chunk files` 재생성 요구사항을 후속 execution plan의 조건으로 정의한다.

Files:

* `docs/dvf_3_3_vnext_regeneration_requirements.md`

Implementation Notes:

* shared requirements 문서 안에 `runtime regeneration requirements` 섹션을 둔다.
* runtime regeneration은 이 계획의 직접 실행이 아님을 명시한다.
* successor parity 기준은 2105-byte parity가 아니라 successor source <-> successor runtime self-consistency로 정의한다.
* chunk generation success가 current cutover를 의미하지 않는다고 명시한다.
* generated chunk load smoke는 후속 execution validation이며 release readiness가 아니라고 명시한다.
* monolith / chunks dual deployment 금지를 유지한다.

Validation:

* runtime mutation forbidden scan
* self-consistency parity wording review
* no-premature-cutover wording review
* no-monolith-dual-deploy guard wording review

---

### Change 6 - Delta / Parity Classification Criteria

Purpose:

old runtime chunks와 successor generated runtime 사이의 차이를 분류하는 기준을 정의한다.

Files:

* `docs/dvf_3_3_vnext_regeneration_requirements.md`

Implementation Notes:

* shared requirements 문서 안에 `parity / delta classification requirements` 섹션을 둔다.
* actual parity matrix / delta ledger 산출은 후속 execution plan으로 유보한다.
* 이 계획은 classification criteria만 정의한다.
* delta category는 다음으로 둔다.
  * `intentional_successor_delta`
  * `source_gap`
  * `schema_gap`
  * `compose_delta`
  * `validation_failure`
  * `migration_required`
* unexplained delta는 fail-loud 대상이라고 정의한다.

Validation:

* delta category wording review
* unexplained delta gate wording review
* planned-only parity artifact scan

---

### Change 7 - Consumer Migration Principles

Purpose:

`2105 Baseline Consumption Audit`를 migration input으로 소비하는 원칙을 정의한다.

Files:

* `docs/dvf_3_3_vnext_consumer_migration_principles.md`

Implementation Notes:

* `change_required_index.md`, `change_forbidden_index.md`, `classified_ledger.jsonl`, `executing_consumer_impact.md`는 read-only migration input으로 둔다.
* current hard gate / validator / test / tool / runtime consumer를 구분한다.
* docs-only historical reference는 current hard gate로 승격하지 않는다.
* migration은 숫자 치환이 아니라 authority role 변경으로만 수행한다.
* actual consumer migration은 후속 execution plan에서 수행한다.
* `active / silent` 원시 occurrence scan은 historical / diagnostic alias를 violation으로 자동 판정하지 않고, current writer / validator / runtime payload surface 재유입만 violation으로 본다.

Validation:

* audit-ledger consumption boundary review
* forbidden rows unchanged rule review
* numeric substitution forbidden scan
* Korean forbidden wording scan
* current-surface-only `active / silent` violation review

---

### Change 8 - Cutover Contract

Purpose:

successor 기준선이 current authority가 되는 조건과 cutover 전후 authority rule을 정의한다.

Files:

* `docs/dvf_3_3_vnext_cutover_contract.md`

Implementation Notes:

* cutover 전 existing chunks는 current deployable runtime authority로 유지한다.
* cutover는 별도 approved execution / reflection step 이후에만 가능하다.
* partial promotion을 금지한다.
* source / facts / decisions / profile / rendered / bridge / chunks / consumer migration / ledger packet이 모두 통과해야 current promotion이 가능하다고 정의한다.
* rollback은 frozen 2105 recovery가 아니라 pre-cutover current chunks 유지로 표현한다.

Validation:

* no-dual-current scan
* no-partial-promotion scan
* rollback language review
* cutover checklist wording review

---

### Change 9 - Ledger Reflection Packet

Purpose:

DECISIONS / ARCHITECTURE / ROADMAP 반영을 위한 draft packet을 작성한다.

Files:

* `docs/dvf_3_3_vnext_ledger_update_packet.md`
* `docs/decisions_vnext_entry_draft.md`
* `docs/architecture_vnext_patch_draft.md`
* `docs/roadmap_vnext_patch_draft.md`

Implementation Notes:

* DECISIONS.md에 직접 쓰지 않고 `decisions_vnext_entry_draft.md`를 작성한다.
* ARCHITECTURE.md에 직접 쓰지 않고 `architecture_vnext_patch_draft.md`를 작성한다.
* ROADMAP.md에 직접 쓰지 않고 `roadmap_vnext_patch_draft.md`를 작성한다.
* 미실행 항목은 ROADMAP draft에서 Done으로 선반영하지 않는다.
* core docs mutation은 별도 approved reflection application으로 유보한다.
* closeout report가 DECISIONS를 대체하지 않는다고 명시한다.

Validation:

* core-doc mutation guard
* draft-only wording review
* Done / Doing / Next / Hold mapping review
* ledger claim boundary scan

---

## 7. Validation Plan

### Automated Validation

Plan-stage validation:

* heading / template section check for this plan
* forbidden claim scan for English and Korean wording
* `vNext-CAB` label usage scan
* direct core-doc mutation guard for `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
* planned-only artifact scan to ensure execution artifacts are not described as direct outputs
* no-premature-cutover / no-dual-current wording scan

Suggested search patterns:

* `2105 recovery|2105 복구|복구 성공|recovered source|복구된 source`
* `숫자 치환|단순 치환|numeric substitution`
* `chunks-only|chunks only|청크만|runtime-only authority`
* `current로 승격|current authority 성립|cutover 완료`
* `release readiness|Workshop readiness|B42 readiness|배포 준비|릴리즈 준비`
* `active / silent|active/silent`

`active / silent` findings are only violations when they re-enter current writer / validator / runtime payload vocabulary. Historical / diagnostic / import alias references are allowed when labeled as such.

Follow-up execution validation, not performed by this plan:

* source manifest schema validation
* facts schema validation
* decisions schema validation
* profile / body_plan consistency validation
* rendered schema validation
* rendered determinism validation
* deterministic rebuild validation
* rendered-to-bridge parity validation
* bridge-to-chunk validation
* runtime chunk parity validation
* generated chunk load smoke
* consumer migration dry-run
* intentional delta classification
* unexplained delta count gate

### Manual Validation

* scope consistency review
* definition-only boundary review
* authority vocabulary review
* `vNext-CAB` label and actual sealed baseline identity separation review
* seed non-authority rule review
* runtime chunks non-source rule review
* core-doc mutation guard review
* draft-only ledger reflection boundary review
* rollback wording review
* FAIL-LOUD terminal state review

### Validation Limits

This plan will not validate:

* full source reconstruction
* actual source manifest generation
* actual rendered generation
* actual Lua bridge export
* actual chunk generation
* actual runtime parity
* full runtime equivalence
* in-game manual QA
* long-session runtime behavior
* multiplayer behavior
* external compatibility sweep
* package / release validation
* Workshop readiness
* B42 readiness
* public-facing UI behavior
* semantic quality completion

---

## 8. Risk Surface Touch

### Authority Surface

Planning / governance level only.

This plan defines conditions for successor current authority but does not grant current authority to any successor artifact.

### Runtime Behavior Surface

None.

This plan does not mutate runtime Lua, bridge payload, manifest, chunk files, or public require contract.

### Compatibility Surface

None directly.

Follow-up consumer migration may affect validators, tools, tests, and runtime consumers. This plan only defines audit-ledger-based migration principles.

### Sealed Artifact Surface

Additive direction artifact only.

Existing sealed artifacts and core docs are not directly mutated. Reflection material is draft-only until a separate approved reflection application or follow-up closeout step.

### Public-Facing Output Surface

None.

Browser / Wiki / Tooltip behavior, public UI, quality exposure, recommendation, sorting, filtering, hiding, trust/confidence display are unchanged.

---

## 9. Risk Analysis

### Architecture Risk

* Definition-only plan and execution / regeneration plan may be mixed.
* `vNext-CAB` label may be mistaken for actual sealed baseline identity.
* Runtime chunks may be treated as source authority.
* Runtime-derived seed may be treated as recovered source.
* Source / facts / decisions / rendered / runtime layers may be partially promoted.

### Runtime Risk

* Regeneration requirement may be read as runtime mutation approval.
* Chunk generation success may be mistaken for current cutover.
* Old and new chunks may accidentally coexist as current deployable authorities.
* Rollback may be described as 2105 recovery instead of pre-cutover current chunk retention.

### Compatibility Risk

* Current hard gate consumers and historical / diagnostic consumers may be mixed.
* Docs-only historical references may be over-edited as if they were runtime consumers.
* `active / silent` may leak back into current writer / validator / runtime vocabulary.
* Numeric replacement may be used instead of authority-role migration.

### Regression Risk

* Facts and decisions responsibility may blur.
* body_plan may become an accidental second authority.
* Rendered validator outputs may feed backward into decisions.
* Advisory style / structural signal / quality signal may become a hard gate.
* `adopted / unadopted` may be overloaded with quality, publish, deletion, or suppression meaning.
* ROADMAP draft may mark unexecuted work as Done.

---

## 10. Rollback Plan

This plan performs document / authority-claim work only, so rollback is claim-level.

* Before sealing, discard the draft or rewrite the affected section.
* After sealing, do not mutate sealed body directly; add an additive supersession entry or successor plan.
* If `vNext-CAB` is used as actual baseline identity, add an identity-boundary correction.
* If seed is consumed as source authority, discard seed disposition output and rewrite seed provenance constraints.
* If planned-only artifacts are mistaken for direct outputs, reclassify file accounting and planned changes.
* If core docs are directly modified under this plan, stop and move the change into a separate reflection application.
* If follow-up regeneration fails, successor artifacts remain staging-only and cutover is forbidden.
* If parity / regeneration is unreachable, record `basis-unavailable` or `blocked` terminal state.
* Rollback is always pre-cutover current chunks retention, not frozen 2105 recovery.

---

## 11. Governance Constraints

* `Philosophy.md` compliance is mandatory.
* This is a definition / governance plan, not an execution / regeneration plan.
* Iris remains 100% Lua at runtime; DVF production remains offline.
* Runtime / build-time separation must remain intact.
* Runtime must render sealed payload and must not compose, repair, validate source, judge semantic quality, or decide publish policy.
* `vNext-CAB` is a program / roadmap / authority-model label before cutover, not the actual sealed current baseline identity.
* Actual current baseline identity is sealed only after follow-up regeneration outputs provide count / fingerprint / rendered hash / chunk manifest fingerprint.
* Runtime chunks are deployable runtime authority and comparison reference, not source authority.
* Runtime-derived seed is non-authority bootstrap only.
* Seed-derived artifacts require provenance.
* FAIL-LOUD must be preserved for source absence, basis-unavailable, parity failure, unexplained delta, and blocked states.
* Current runtime vocabulary remains `adopted / unadopted`.
* Legacy `active / silent` remains historical / diagnostic / import alias only.
* `adopted / unadopted` must not become quality-pass, publish_state, deletion, or suppression vocabulary.
* Browser / Wiki / Tooltip must not consume quality state as badge, sorting, filtering, hiding, recommendation, trust/confidence display.
* Monolith / chunks dual deployment remains forbidden.
* Sealed decisions must be updated by additive supersession, not direct mutation.
* DECISIONS / ARCHITECTURE / ROADMAP reflection is draft-packet only in this plan.
* Release readiness, Workshop readiness, package readiness, B42 readiness, manual in-game QA, runtime rollout, and public exposure are not implied by this plan.

---

## 12. Expected Closeout State

Expected closeout: `partial_governance_plan_sealed`

Acceptable alternate label: `scope_locked_plan_only`

This closeout means the successor current authority definition / governance plan is sealed. It does not mean successor current authority exists, source reconstruction is complete, rendered output has been promoted, Lua bridge payload has changed, runtime chunks have changed, consumer migration has executed, or release readiness has been reached.

The maximum acceptable claim is:

DVF 3-3 acknowledges frozen 2105 as predecessor / comparison / migration input, does not attempt recovery, defines `vNext-CAB` as a pre-cutover program / authority-model label, keeps actual sealed baseline identity deferred until regeneration outputs exist, limits runtime-derived seed to non-authority bootstrap status, defines source-to-runtime regeneration and audit-ledger-based migration as follow-up execution requirements, and forbids current authority cutover before a separate approved execution / reflection step.
