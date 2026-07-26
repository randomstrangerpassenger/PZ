# DVF 3-3 Food Semantic Facts Authority Reconstruction — Implementation Plan

> 상태: owner-ratified / cross-plan-synchronized-v1 / preimplementation-plan-review-required / implementation-entry-blocked
> 작성일: 2026-07-26
> 최종 수정일: 2026-07-27
> Round ID: `dvf_3_3_food_semantic_facts_authority_reconstruction`
> Historical design source input: `C:/Users/MW/.codex/attachments/982ec766-f8aa-4c0b-83f6-9c081f8b2ad0/pasted-text.txt` [non-normative provenance only; live presence not required]
> Historical design source SHA-256 / logical line count: `016e621b39ff175ac9fa7b4a671631ba03eae6569652077c715c586fc3e87394` / `3057`
> Normative requirements artifact: `docs/dvf_3_3_food_semantic_facts_authority_reconstruction_implementation_plan.md` / `Appendix A — Normative Design Requirements Snapshot`
> Normative requirements snapshot SHA-256 / logical line count: `443b7f1e2f821ee86d2850cf6c0ecc8ead304ef62a857e6659387475ee1af83e` / `60`
> Normative requirements synthesis author: `Codex planning synthesis from the owner-provided problem definition and accepted planning-review dispositions`
> Normative requirements owner ratification status: `ratified_owner_directive`
> Ratification approver identity / approval time / ratified snapshot SHA-256: `repository_owner` / `2026-07-27T07:53:49.4755918+09:00` / `443b7f1e2f821ee86d2850cf6c0ecc8ead304ef62a857e6659387475ee1af83e`
> Roadmap ceremony owner directive: `separate_roadmap_required=false`; this plan must not create or require a roadmap artifact
> This revision writes: this successor plan only; predecessor draft is currently restored to its exact bound identity and no policy/schema/binding/generated artifact is created
> Template input: `docs/PLAN_TEMPLATE.md`
> Template SHA-256: `38d70d4d624733db4d24f047e0b737a47c75522a967c84f06fe5aabc5ebd9ba1`
> Top authority: `docs/Philosophy.md`
> Planning readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/EXECUTION_CONTRACT.md`
> Preserved predecessor plan: `docs/dvf_3_3_facts_authority_enrichment_plan.md`
> Preserved predecessor SHA-256 / line count: `61f9235e8ed3787f8388859f383d44727a2f088fb277a1d46cd1dcc78a3b5ee7` / `234`
> Predecessor episode: `scenario_b_overwritten_then_restored`; Cycle 1 authoring temporarily replaced the predecessor path, then restored it from the prior exact read record and verified it against the repo-relative routing-correction bound SHA-256; this boundary episode must remain explicit
> Overwritten successor identity at predecessor path: SHA-256 `e800a937bacf5eaea0d3841f524961720603d17ffb640846c48e25f3b73b0834` / logical line count `1426` / observed 2026-07-26
> Restore identity verifier: `Iris/_docs/round3/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/facts_authority_routing_correction_attempt_0014.json` / planning SHA-256 `267ce42750539f35e212e74353edc59f54f1f2b3b187aa570705352697f89c46` / bound predecessor SHA-256 at line 72
> Direct plan artifact: `docs/dvf_3_3_food_semantic_facts_authority_reconstruction_implementation_plan.md`
> Attempt root contract: `Iris/build/description/v2/staging/dvf_3_3_food_semantic_facts_authority/attempts/<attempt-id>/`
> Cross-plan synchronization targets: `docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md`, `docs/dvf_3_3_registry_authority_canonical_closure_plan.md`
> Cross-plan synchronization contracts: `dvf3_3_food_semantic_facts_authority__naturalization_phase2_sync_v1`, `dvf3_3_food_semantic_facts_authority__registry_successor_sync_v1`
> Current implementation entry: repository-relative requirements snapshot materialization/presence/tracking과 owner ratification, counterpart plans의 presence/read-only stance, fresh pre-implementation plan review PASS, protected-surface non-overlap, required tool availability와 Section 4 entry predicate가 모두 충족된 뒤에만 implementation build를 시작할 수 있다. Change 0 exit가 실제 reciprocal/boundary binding을 생산하며 별도 roadmap artifact는 요구하지 않는다. Planning-stage requirements ratification을 제외한 semantic/adoption owner decision·approval과 post-implementation external review는 implementation-complete bundle 뒤에만 시작한다.
> Post-implementation authority entry: implementation-complete bundle이 봉인된 뒤 owner가 D1/D5~D16과 semantic artifacts를 직접 승인하고 post-implementation external implementation review가 PASS해야 authority execution으로 진행할 수 있다. Sealed non-current successor가 생성된 뒤에만 terminal independent closeout review, owner final seal과 terminal hash seal을 순서대로 수행한다. D2는 owner-selectable route가 아닌 retired mandatory contract다. Current adoption은 별도 Registry-owned operational-cutover 계획만 소유한다.
> Maximum future claim: post-implementation owner approval에서 D1로 확정한 food semantic facts/source authority claim token에 한정한다.

이 문서는 현재 exact identity로 복구된 짧은 predecessor draft의 evidence, 317-row 범위, Layer 4 비승격 경계, candidate-first 원칙을 보존하면서 사용자 제공 설계 요구사항을 `PLAN_TEMPLATE.md` 구조로 구체화한 successor implementation plan이다. Predecessor path는 protected no-mutation evidence이며 이 successor의 실행 권위를 공유하지 않는다. Cycle 1의 temporary overwrite/restore episode를 “항상 byte-preserved였다”라고 세탁하지 않는다. 이 successor plan 자체가 유일한 durable implementation-planning artifact이며 별도 roadmap materialization을 요구하지 않는다.

이 문서는 `설계 요구사항 → 계획 → 계획 검토 → 구현` 순서를 따른다. 계획 검토 전에는 implementation build를 시작하지 않는다. 검토를 통과한 implementation build도 current facts 변경, authority-bearing candidate 채택, official Naturalization retry 또는 Publish Boundary 재시도를 승인하지 않는다. 이 round의 authority execution은 sealed non-current successor와 no-render compatibility handoff까지이며, current adoption과 official Naturalization retry는 각각 별도 Registry cutover와 fresh Naturalization attempt가 소유한다.

## 0. Normative Lifecycle and Cross-Plan Synchronization

이 절은 implementation entry, Registry successor 처리, Naturalization Phase 2 handoff에 관한 이 문서의 규범적 동기화 절이다. 뒤 절의 문구가 이 절과 충돌하면 이 절이 우선한다.

### 0.1 Canonical lifecycle

실행 순서는 다음으로 고정한다.

```text
requirements artifact materialization/presence/tracking
-> requirements artifact owner ratification
-> counterpart plan presence/read-only preflight
-> plan-level finding closure and fresh pre-implementation plan review PASS
-> attempt-local Change 0 requirements/cross-plan binding verification
-> Changes 1-7 feasibility kernel
-> [kernel PASS only] Changes 8-13 implementation build
-> implementation-complete bundle
-> semantic owner decisions and approvals
-> post-implementation external implementation review
-> authority execution
-> sealed non-current successor
-> terminal independent closeout review
-> owner final seal
-> terminal hash seal
-> separately reviewed Registry operational cutover
-> new Naturalization attempt Phase 0, with Phase 2 source inventory reseal
-> Naturalization Phase 3 through Phase 8
-> fresh Publish Boundary official attempt
```

Kernel BLOCKED이면 lifecycle은 Change 7에서 종료하며 Changes 8~13, implementation-complete bundle, owner/review stage로 진행하지 않는다. 실패 bundle을 보존한 새 attempt만 허용한다.

계획 검토는 implementation-complete bundle review나 terminal independent review로 대체할 수 없다. Pre-implementation review에서 Open Critical 또는 Open Important가 하나라도 남으면 implementation entry는 차단된다.

```text
post_implementation_external_review != terminal_independent_review
post_implementation_external_review_terminal_gate_credit = 0
```

### 0.2 Facts Authority to Naturalization contract

`dvf3_3_food_semantic_facts_authority__naturalization_phase2_sync_v1`은 다음 producer/consumer 경계를 가진다.

| Contract role | Owner | Required behavior |
|---|---|---|
| producer | Food Semantic Facts Authority round | successor facts, successor input manifest, food semantic schema, proposition-licensing contract와 exact hashes를 봉인한다. |
| compatibility consumer | Naturalization actual Phase 2 inventory path | sealed non-current successor를 explicit override로 읽는 no-render probe만 허용한다. |
| official consumer | fresh Naturalization attempt | Registry adoption receipt로 current facts/manifest가 successor와 같아진 뒤 Phase 0부터 새 attempt를 열고 Phase 2에서 source inventory를 재봉인한다. |

Facts round Change 12의 no-render PASS는 compatibility evidence일 뿐 official Naturalization attempt, candidate 생성, Phase 4~8 실행 또는 Publish handoff가 아니다. Sealed non-current successor만 존재하는 동안 `official_naturalization_retry_allowed=false`이며, Phase 4~8은 금지된다.

Naturalization이 소비해야 하는 exact identity set은 다음 네 개다.

```text
successor facts SHA-256
successor input-manifest SHA-256
approved food-semantic schema SHA-256
approved proposition-licensing contract SHA-256
```

하나라도 selected successor binding과 다르면 stale input으로 거부한다. `attempt-0014-remediation`은 immutable predecessor evidence이며 재개하거나 수정하지 않는다.

Naturalization counterpart plan은 read-only synchronization readpoint다.

```text
naturalization_plan_path = docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md
naturalization_plan_planning_sha256 = 11ed7682a07a6dfd41f516f80a1a708b09f20814c5971f493b74f7c9a44908a4
naturalization_sync_mutation_allowed = false
naturalization_counterpart_contract_present = true
naturalization_counterpart_contract_anchor = "Food Semantic Facts Authority → Naturalization Phase 2 synchronization"
```

Change 0은 위 plan을 수정하지 않고 execution-time fresh SHA-256, counterpart contract token, producer/consumer four-identity projection과 forbidden-action set을 `cross_plan_sync_binding.json`에 기록한다. Planning hash drift, counterpart token 부재 또는 byte-equivalent projection 불일치는 `facts_naturalization_sync_reciprocal=false`로 fail-loud 종료한다. 자동 patch, in-place correction 또는 다른 plan의 mutation으로 PASS를 만들지 않으며 수정이 필요하면 별도의 owner-authorized planning round로 보낸다.

### 0.3 Facts Authority to Registry contract

`dvf3_3_food_semantic_facts_authority__registry_successor_sync_v1`은 기존 `docs/dvf_3_3_registry_authority_canonical_closure_plan.md`의 candidate/current, promotion, seal/cutover, stale-reentry 경계를 소비한다. 기존 Registry 계획은 이 동기화를 위해 수정하지 않는다.

```text
registry_plan_path = docs/dvf_3_3_registry_authority_canonical_closure_plan.md
registry_plan_planning_sha256 = 0de824e9b471895689b5089d71bfe4a79d3526dc96f0268f681a9b9d65aa7cfb
registry_sync_mutation_allowed = false
```

이 round가 직접 허용하는 terminal successor action은 sealed non-current successor 생성까지다. 이 문서 안의 Branch B가 in-round authority execution 경로다. Branch A tooling과 atomicity fixture는 future Registry cutover proposal일 수 있지만, 이 계획은 current facts나 current input manifest를 직접 변경하지 않는다.

```text
facts_round_current_write_count = 0
facts_round_registry_promotion_count = 0
sealed_successor_receipt_required = true
registry_operational_cutover_plan_required = true
```

실제 candidate-to-current promotion은 별도 Registry-owned operational-cutover 계획이 exact successor/base/diff/contract hashes를 검토·승인한 뒤에만 실행할 수 있다. Owner decision D9만으로 Registry promotion authority를 만들 수 없다.

### 0.4 Publish Boundary non-synchronization

이 round는 Publish Boundary policy, detector, threshold, waiver 또는 evaluation-subject schema를 변경하지 않는다. Publish Boundary와 직접 교차 계약을 추가하지 않으며 Publish counterpart plan path/hash를 Change 0 input으로 소비하지 않는다. Publish Boundary는 Registry adoption 뒤 새 Naturalization attempt가 만든 fresh Phase 8 handoff만 기존 `dvf3_3_korean_naturalization__publish_boundary_sync_v1`로 소비한다.

### 0.5 Implementation entry predicates

다음 atomic predicate가 모두 true여야 implementation build를 시작할 수 있다.

```text
requirements_artifact_materialized = true
requirements_artifact_present_at_entry = true
requirements_artifact_tracked = true
requirements_artifact_git_blob_identity_bound = true
requirements_artifact_owner_ratified = true
requirements_ratification_approver_identity_present = true
requirements_ratification_approval_time_present = true
requirements_ratified_snapshot_sha256_match = true
preimplementation_review_bound_to_ratified_snapshot_sha256 = true
naturalization_counterpart_present_at_entry = true
registry_counterpart_present_at_entry = true
cross_plan_mutation_allowed = false
publish_direct_sync_required = false
preimplementation_plan_review = PASS
open_critical_count = 0
open_important_count = 0
```

여기서 `preimplementation_plan_review`는 설계 요구사항·계획 사이클의 구현 전 계획 품질 검토다. 구현 결과를 대상으로 하는 owner 승인, 외부 리뷰 또는 terminal independent review가 아니며 그 어떤 승인·리뷰 token도 선소비하지 않는다.

`requirements_artifact_owner_ratified`는 Appendix A의 planning requirements authority만 승인하는 entry-time ratification이다. D1/D5~D16 semantic/adoption decision이나 구현 결과 승인이 아니며 implementation 중 consumed owner-decision count에 포함하지 않는다. Ratification은 이 plan header의 approver identity, approval time, exact snapshot SHA-256 세 필드가 `not_ratified`가 아닌 값으로 채워지고 hash가 재계산될 때만 true다. 이 개정 시점의 header 상태는 `ratified_owner_directive`이며 fresh pre-implementation plan review PASS 전까지 implementation entry는 계속 차단된다.

이 gate 전에는 attempt root, implementation code, schema candidate, writer candidate 또는 generated implementation evidence를 만들지 않는다.

---

## 1. Objective

DVF 3-3의 식품 317건이 하나의 승인 의미 조건으로 수렴하는 상류 부채를 Iris 책임 경계 안에서 종결할 수 있도록, Classification / Rule, Evidence Allowlist, lineage, closed food semantic schema, automatic mapping, curated approval, candidate writer, Registry successor handling, Naturalization Phase 2 handoff를 각각 독립된 권위와 검증 단위로 구현한다.

현재 문제는 다음과 같이 읽는다.

```text
current food facts 317 rows
= identity_hint "식품"
+ primary_use 1종
+ item_subtype 0건

DVF Body Compiler
= 승인된 facts만 소비

따라서 compiler-only 자연화
!= 승인되지 않은 식품 의미 차이 생성
```

성공 경로는 다음과 같다.

```text
allowlisted source
-> reproducible Classification / Rule signal
-> approved signal-to-fact mapping
   또는 explicit curated approval
-> closed food semantic facts
-> attempt-local candidate facts
-> Registry-controlled adoption 또는 sealed successor handoff
-> Naturalization Phase 2 no-render acceptance
```

책임 상한은 다음과 같이 고정한다.

```text
Iris Classification / Rule
= allowlisted source를 deterministic signal로 변환

Food Semantic Facts Authority
= automatic lineage와 curated approval을 closed fact로 승인

Iris Artifact Registry
= candidate/current lifecycle, identity, promotion, seal

DVF System / DVF Body Compiler
= approved facts / decisions / profile / body_plan
  -> rendered 3-3 body

Publish Boundary
= public text와 공개 수용성 판정
```

### Codebase Inspection Summary

계획 작성 시점의 실제 checkout에서 다음을 확인했다. 이 수치는 planning readpoint이며 실행 시 fresh census로 다시 봉인한다.

* `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`과 current input manifest는 facts/decisions 각각 2,105행을 current source authority로 가리킨다.
* preserved `attempt-0014-remediation` cause analysis의 대상 317건은 current facts에서도 정확히 `identity_hint="식품"`, `selected_cluster="food_consumption"`, `primary_use` 1종이며 `item_subtype` non-null 행이 0건이다.
* preserved baseline은 repeated-skeleton hit 450건을 compiler-remediable 133건과 facts-authority-blocked 317건으로 분리하며, 대상 semantic condition digest는 `3707352bc4e8363e712ffc383a0ecdb2d5f1d8cfd74ff54a15531485f934738e`다.
* `Iris/build/phase2_rules/rule_executor.py`는 고정 순서로 8개 `phase2_rules/rules/*_rules.py` 모듈을 import하지만 현재 checkout에는 해당 directory와 modules가 없다. 해당 경로의 tracked Git history도 planning scan에서 발견되지 않았고 상위 `Iris/build/*`는 기본 ignore 대상이므로, “원본 Rule 복구 가능” 또는 “영구 소실” 어느 쪽도 census 없이 주장할 수 없다.
* `Iris/_docs/iris-evidence-allowlist.md`는 제목에서 v0.4, 본문 변경 이력에서 v0.5를 latest로 표시하지만 `Iris/build/phase0_validation/allowlist.py`의 machine contract는 `version="0.3"`이다.
* `Iris/output/tags_by_fulltype.json`은 대상 317건을 모두 덮지만 Rule/source/operation lineage를 보유하지 않는다. 대상 안에서 8개 tag-set이 관찰되고 최대 group은 202건이므로 diagnostic input일 뿐 semantic facts authority가 아니다.
* `Iris/input/items_itemscript.json`은 대상 317건을 모두 포함하지만 `Base.LemonGrass`와 `Base.Lemongrass` 같은 exact case-sensitive identity를 보존해야 하므로 Windows PowerShell의 case-insensitive object materialization을 authoritative consumer로 사용하지 않는다.
* `Iris/build/description/v2/data/upstream_usecases_by_fulltype.json`의 Layer 4 surface는 대상 316/317을 덮고 `Base.Lemongrass` 1건이 없다. 이 surface는 interaction evidence이며 automatic Layer 3 food fact input이 아니다.
* Naturalization Phase 2는 현재 `identity_hint`, `primary_use`, `secondary_use`, `special_context`, `processing_hint`, `acquisition_hint`, `limitation_hint`, `notes`만 source proposition으로 등록한다. 새 structured food semantics가 실제 Phase 2에서 소비되려면 승인된 proposition-licensing contract와 명시적 adapter가 필요하다.
* `Iris/_docs/round3/round3_active_core_closure.json`은 current core 12개와 current-route tooling allowlist 1개(`export_dvf_3_3_lua_bridge`)를 봉인한다. 새 food semantic writer는 편의상 이 12+1 표면에 추가하지 않는다.
* planning-time live required-validation manifest는 fail-closed이며 required artifact 149개, required test 56개를 포함한다. 이 수치는 Section 6 Change 1 denominator reconciliation table의 서로 다른 role로 다시 분리하며, 실행 시 fresh count를 계산하고 success sacred count로 고정하지 않는다.
* 현재 worktree에는 Naturalization/Publish 관련 사용자 변경과 staging evidence 변경이 존재한다. 구현은 이를 되돌리거나 흡수하지 않고 mechanically verified clean commit 또는 exact non-overlap isolated worktree에서만 시작한다. 이 검증은 owner approval token이 아니다.

---

## 2. Scope

다음 범위를 포함한다.

* user-provided design requirements, byte-preserved predecessor draft와 본 successor 계획의 path/hash/line-count traceability 및 owner decision register
* 식품 317건 exact FullType/member set과 predecessor evidence의 fresh read-only census
* Classification / Rule authority의 R1 history/recovery census, R2 reproducible-subset diagnostic census와 유일한 executable 경로인 R3 official successor
* Evidence Allowlist 0.3/0.4/0.5 divergence와 source field/operation admissibility 봉인
* automatic signal의 intermediate provenance와 모든 final automatic fact의 proposition-level lineage
* writer authority contract와 hard-forbidden sink
* closed food semantic vocabulary, 조합 규칙, proposition licensing, amendment governance
* approved signal-to-fact mapping과 automatic coverage
* automatic residual을 위한 curated authority, approval ledger, reconciliation
* 317/317 terminal semantic disposition과 unsupported-fact zero proof
* attempt-local deterministic food semantic facts writer와 candidate-only 산출물
* Branch B sealed non-current successor handoff, Registry cutover request와 future Branch A proposal의 divergence/claim ceiling
* 실제 Naturalization Phase 2 consumer의 no-render/isolated acceptance projection
* Branch G2 explicit deferral, future Registry G1 adoption request와 terminal-state 제한
* independent closeout review, owner seal, terminal hash binding

### Explicitly Out Of Scope

* Naturalization candidate body 생성 또는 승격
* Naturalization Phase 4~8 실행
* `Iris/build/description/v2/output/dvf_3_3_rendered.json` 재생성 또는 변경
* Lua bridge export
* `IrisLayer3DataChunks.lua` 또는 runtime chunk 변경
* package payload 생성, 교체, publication
* Browser / Tooltip / Wiki 표시 변경
* Publish Boundary 재시도
* public text acceptance 또는 semantic quality acceptance
* repeated-skeleton detector, canonical threshold(계획 작성 시 관찰값 104), ratio, waiver 정책 변경
* Recipe 또는 Right-click QG 정책 변경
* Layer 4를 automatic Layer 3 fact writer로 승격
* DVF System / DVF Body Compiler를 source classifier 또는 facts authority로 확장
* Iris Artifact Registry를 semantic adjudicator로 확장
* 식품 317건 밖의 전체 taxonomy/schema 재설계
* external mod semantic import 체계
* current-route runner 전면 재작성
* current core 12개 또는 tooling allowlist 1개 편의상 확대
* predecessor facts, old generated tags, old allowlist, failed attempt 또는 sealed evidence 삭제/재작성
* release, Workshop, B42, deployment, multiplayer, manual in-game readiness

---

## 3. Non-Goals

이 계획은 다음을 해결하려 하지 않는다.

* 식품 ontology의 영구적 완전성
* 모든 식품 fact의 automatic derivation
* 사람이 읽는 최종 한국어 문장의 자연스러움
* 317건을 반드시 일정 개수의 taxonomy partition으로 나누는 것
* current generated tags를 사후 lineage로 세탁하는 것
* `DisplayName`, `Description`, `DisplayCategory`, item ID, hash, 난수로 의미를 추론하는 것
* `unknown_food`, `generic_food`, `other_food` 같은 임시 bucket으로 coverage를 채우는 것
* automatic signal 부재를 negative fact로 해석하는 것
* human review 자체를 evidence provenance로 간주하는 것
* Registry receipt로 semantic approval을 대체하는 것
* machine PASS로 independent review 또는 owner seal을 대체하는 것
* `maximum_same_skeleton_group <= bound_threshold_value`를 Publish Boundary PASS 또는 public text acceptance로 확대하는 것

---

## 4. Assumptions

### Repository and Authority Assumptions

* `Philosophy.md`의 Iris 경계, 특히 근거 없는 추론·권장·비교 금지와 runtime 표시 전용 원칙이 최상위다.
* current source authority는 `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`이 가리키는 2,105행 facts/decisions chain이다.
* 이 round는 current source authority를 직접 변경하지 않는다. Current adoption은 별도 Registry-owned operational-cutover 계획의 책임이다.
* `attempt-0014-remediation`과 facts-authority routing correction은 immutable predecessor evidence다.
* old `tags_by_fulltype.json`, Layer 4 use cases, missing Rule 경로와 allowlist predecessor versions는 census/diagnostic/recovery input일 뿐 자동 authority가 아니다.
* target denominator는 count만이 아니라 exact FullType set과 case-sensitive identity로 봉인한다.
* current facts를 직접 수동 편집하지 않는다. curated approval도 writer input ledger를 통해서만 candidate에 반영한다.
* 모든 claim-bearing attempt는 새 `attempt_id`와 새 출력 root를 사용하며 같은 attempt의 FAIL/PASS 산출물을 덮어쓰지 않는다.
* plan/code/input/schema/approval identity가 바뀌면 영향 phase를 새 attempt에서 다시 실행한다.
* implementation은 user-owned dirty changes와 겹치지 않는 mechanically verified base에서 수행한다.
* exact Naturalization 317과 facts target 317의 case-sensitive set identity binding은 필수이며 count equality로 대체하지 않는다.
* final automatic fact authority는 `fact_field + fact_value + signal_to_fact_mapping_id + source/rule/allowlist lineage`를 필수로 가진다. Row/tag lineage는 intermediate signal provenance일 뿐 terminal fact authority가 아니다.
* downstream repetition threshold는 canonical policy/detector artifact가 소유하며 이 계획의 관찰값이 second authority가 되지 않는다.
* `logical line count`는 UTF-8 text를 읽고 CRLF/CR을 LF로 정규화한 뒤 terminal newline이 만드는 빈 segment를 제외한 textual line 수다. Final line은 terminal LF가 없어도 1개 line으로 센다. Normative requirements snapshot, predecessor와 successor plan identity에 같은 정의를 적용한다.

### Post-Implementation Owner Decisions and Reviews

아래 표의 semantic/adoption owner decision·approval과 post-implementation authority review는 implementation build의 entry·progress·completion predicate가 아니다. §0.5의 requirements ratification과 pre-implementation plan review만 planning-stage entry predicate다. 구현자는 reviewed plan이 허용한 option, proposal, validator와 exact evidence bundle만 구현하며 선택·승인·claim을 하지 않는다. `implementation_complete_bundle_sealed = true`가 봉인된 뒤에만 owner가 exact bundle hash를 대상으로 직접 승인 또는 거절하고 post-implementation external implementation review를 시작한다. Terminal independent closeout review는 authority execution이 sealed non-current successor와 final review input을 생산한 뒤에만 시작한다.

Post-implementation approval은 같은 attempt의 구현 산출물을 소급 수정하지 않는다. Owner는 exact implementation-complete bundle을 승인 또는 거절할 수 있으며, option·schema·mapping·cap·review denominator·branch 조건을 바꾸려면 기존 bundle을 보존하고 새 implementation attempt를 생성한다.

| ID | Post-implementation 결정 | 실행 영향 | Required Before |
|---|---|---|---|
| D1 | 최종 claim token C1 또는 C2 | terminal claim vocabulary | implementation-complete bundle 및 external review PASS 뒤, Phase 13 claim 전 |
| D5 | Layer 4를 curated human review context로 허용할지 | curated reviewed source set | implementation-complete bundle 뒤, Phase 8 authority execution 전 |
| D6 | bulk 금지, bounded batch 허용 여부와 batch 조건 | curation execution workflow | implementation-complete bundle 뒤, Phase 8 authority execution 전 |
| D7 | pre-result-sealed proposed item/proposition curation cap을 승인 또는 거절할지 | automatic coverage 부족 시 item/proposition 양축 routing | implementation-complete bundle 뒤, Phase 7 authority execution 전 |
| D8 | implementation이 산출한 automatic row human-review denominator를 승인 또는 거절할지 | final semantic review denominator | implementation-complete bundle 뒤, Phase 9 authority execution 전 |
| D9 | Branch B sealed handoff 승인과 future Registry cutover request 발행 여부 | successor handoff 범위; 이 round의 current mutation 권한은 만들지 않음 | implementation-complete bundle 및 external review PASS 뒤, Phase 11 authority action 전 |
| D10 | pre-result-sealed `minimum_meaningful_partition >= 4` criterion을 승인할지 | Phase 12 acceptance claim | implementation-complete bundle 뒤, Phase 12 authority acceptance 전 |
| D11 | G2 explicit deferral과 future Registry G1 adoption-request 발행 여부 | 이 round는 live manifest를 변경하지 않음 | implementation-complete bundle 및 external review PASS 뒤, Phase 13 authority action 전 |
| D12 | future Registry promotion 이후 correction successor의 owner와 operational route | future cutover request에 포함할 predecessor-reentry 없는 correction contract | implementation-complete bundle 뒤, future Registry cutover request 발행 전 |
| D13 | independent reviewer eligibility I1 또는 I2 | closeout eligibility | sealed non-current successor 및 final review input 봉인 뒤, terminal independent review 시작 전 |
| D14 | 12+1 tooling cap 비확장 proof를 formal artifact로 채택할지 | required validation evidence | implementation-complete bundle 뒤, authority execution 전 |
| D15 | top-doc update와 freshness reseal의 실행 범위 | post-closeout docs/validation | implementation-complete bundle 및 external review PASS 뒤, Phase 13 authority action 전 |
| D16 | reviewed plan이 허용한 Naturalization adapter/no-render candidate를 tooling owner가 채택할 수 있는지와 exact symbol 범위 | cross-axis compatibility tooling adoption scope, baseline/no-impact proof; official retry authority는 아님 | implementation-complete bundle 뒤, Phase 12 compatibility execution 전 |

Implementation build는 Phase 6 `schema_satisfiability_report.json`만 사용해 `proposed_curation_item_cap`과 `proposed_curation_proposition_cap`을 Phase 7 dry-run 결과 전에 봉인한다. D7은 구현 완료 뒤 그 exact proposal을 승인 또는 거절하는 decision이다. Owner가 cap을 바꾸면 동일 attempt를 계속하지 않고 새 implementation attempt에서 새 Phase 6 basis와 pre-result proposal을 봉인한다.

Implementation build는 D8의 proposed automatic-row review denominator도 row-level semantic review 결과 전에 봉인한다. Post-implementation owner는 exact denominator를 승인 또는 거절할 수만 있으며 변경 시 새 implementation attempt가 필요하다.

기존 D2/D3/D4 identifier는 owner-selectable option에서 폐기한다.

```text
D2 status      = retired_mandatory_contract
D2 replacement = R3 official successor is the only executable Rule authority route
D3 status      = retired_mandatory_contract
D3 replacement = final automatic fact proposition-level lineage mandatory
D4 status      = retired_mandatory_contract
D4 replacement = exact case-sensitive 317 set-identity binding mandatory
```

Owner decision ledger는 D2/D3/D4 row를 삭제하지 않고 `status=retired_mandatory_contract`와 replacement contract path/hash를 기록한다.

D1 option 정의:

```text
C1
= claim token "Food Semantic Facts Authority Successor Handoff"
+ terminal value "sealed_successor_handoff_complete"

C2
= owner가 명명한 facts/source-authority axis-qualified claim token과 terminal value
```

C2의 이름은 바꿀 수 있지만 C1보다 넓은 semantic, current-authority, Registry, DVF Body Compiler, Publish, runtime 또는 release scope를 주장할 수 없다. 이 plan은 `canonical_complete`를 발행하지 않는다.

D13 option 정의:

```text
I1
= requirements, plan, review, implementation, curation, owner-decision chain에 참여하지 않은 reviewer

I2
= non-Claude reviewer
+ I1과 동일한 전 체인 불참 조건을 별도로 machine-check
```

현재 requirements/plan/review chain에 참여한 ChatGPT, Claude와 종합 검토 참여자는 I1/I2 모두에 부적격하다.

Post-implementation D16 approval은 implementation이 산출한 candidate scope에 대해 최소한 다음을 봉인한다.

```text
tooling owner
allowed files and symbols
adapter + no-render mode only인지 여부
existing Phase 4–8 behavior mutation prohibition
attempt-0014 baseline validator semantics preservation
```

Owner decision은 implementation-complete bundle 봉인 뒤 다음 machine-readable record로 고정한다.

`Iris/build/description/v2/owner_inputs/dvf_3_3_food_semantic_facts_authority/owner_reserved_decisions.json`

이 파일은 최소한 decision ID, selected option, rationale, approver identity, approval time, bound plan SHA-256과 bound implementation-complete bundle SHA-256을 포함한다. Implementation build 중에는 생성·소비하지 않으며 미결 값을 implicit default로 해석하지 않는다.

Post-implementation external implementation review는 다음 record로 고정한다.

`Iris/build/description/v2/staging/dvf_3_3_food_semantic_facts_authority/attempts/<attempt-id>/post_implementation_reviews/external_implementation_review.json`

이 reviewer는 implementation author가 아니어야 하며 exact implementation-complete bundle SHA-256 일치를 직접 검증한다. Plan/review chain 참여 여부만으로 부적격하게 만들지는 않지만, 이 review의 PASS는 terminal independent gate credit이 0이다.

### Execution Entry Gate

Gate producer와 consumer를 pre-implementation plan review, implementation entry, implementation completion, post-implementation owner/review, authority execution의 다섯 단계로 분리한다. 같은 predicate를 서로 다른 단계의 PASS로 재사용하지 않는다.

```text
requirements_artifact_materialized = true
requirements_artifact_present_at_entry = true
requirements_artifact_tracked = true
requirements_artifact_git_blob_identity_bound = true
requirements_artifact_owner_ratified = true
requirements_ratification_approver_identity_present = true
requirements_ratification_approval_time_present = true
requirements_ratified_snapshot_sha256_match = true
preimplementation_review_bound_to_ratified_snapshot_sha256 = true
naturalization_counterpart_present_at_entry = true
registry_counterpart_present_at_entry = true
cross_plan_mutation_allowed = false
preimplementation_plan_review = PASS
open_critical_count = 0
open_important_count = 0
```

Implementation build entry는 owner decision, owner approval 또는 외부 review를 요구하지 않는다.

```text
successor_plan_identity_known = true
bootstrap_no_protected_mutation_contract_active = true
bootstrap_execution_base_clean_or_nonoverlap = true
bootstrap_required_tools_available = true
owner_decision_consumed_count = 0
owner_approval_consumed_count = 0
external_review_consumed_count = 0
```

Change 0 exit PASS는 Change 0의 mechanical Validation block에 열거된 모든 atomic predicate의 conjunction이다. Change 1 entry는 그 full exit PASS를 소비하고, 아래 5개 binding predicate를 진단 가능한 gating subset으로 다시 확인한다. 이 subset만의 PASS는 full Change 0 exit PASS를 대체하지 않는다.

```text
change0_exit_pass = true
requirements_plan_binding_verified_at_exit = true
change0_predecessor_plan_identity_verified = true
change0_successor_plan_identity_verified = true
change0_routing_ambiguity_count = 0
change0_protected_surface_policy_materialized = true
```

Implementation build의 Change 2+는 Change 1 evidence/baseline binding과 machine-detectable implementation blocker-zero만 요구한다. Review finding과 owner decision은 이 gate의 입력이 아니다.

```text
implementation_machine_blocker_count = 0
protected_surface_overlap_count = 0
implementation_execution_base_verified = true
change1_predecessor_evidence_hashes_bound = true
change1_protected_current_baseline_captured = true
change1_exact_317_identity_bound = true
owner_decision_consumed_count = 0
owner_approval_consumed_count = 0
external_review_consumed_count = 0
```

Implementation completion은 `feasibility_kernel_state=PASS`를 선행 조건으로 D1/D5~D16 option-capable code, D2/D3/D4 retired contracts, schemas/proposals, validators, fixtures, dry-run reports와 post-implementation review bundle을 exact hash로 봉인하지만 authority claim이나 current mutation을 만들지 않는다. Kernel BLOCKED bundle은 implementation completion이 아니다.

```text
feasibility_kernel_state = PASS
changes_8_through_13_implementation_complete = true
implementation_build_complete = true
implementation_option_matrix_complete = true
implementation_machine_validation = PASS
implementation_complete_bundle_sealed = true
authority_claim_emitted_count = 0
current_facts_manifest_mutation_count = 0
owner_decision_consumed_count = 0
owner_approval_consumed_count = 0
external_review_consumed_count = 0
```

Owner semantic/adoption decision, semantic approval과 plan-level external finding resolution은 위 implementation-complete bundle 뒤에만 시작한다. Post-implementation external implementation review는 owner가 exact review target을 승인한 뒤 수행하고, terminal independent closeout review는 authority execution과 sealed non-current successor 뒤에만 수행한다. Open Critical/Important finding은 실제 수정 또는 reviewer가 resolved로 판정한 대체 수정 없이는 authority execution gate에서 0으로 셀 수 없고 owner risk acceptance로 우회할 수 없다. Minor는 resolved 또는 explicit owner-accepted bounded disposition이어야 한다.

Plan-level finding-resolution reviewer는 원 finding 제기자를 포함한 requirements/plan/review chain 참여자일 수 있다. Eligibility는 reviewer identity와 review-chain role, exact implementation-complete bundle SHA-256, finding별 correction/disposition evidence를 기록하는 것으로 정의한다. 이 reviewer의 `resolved` 판정은 plan/implementation finding count만 닫으며 terminal `independent_review_gate`에는 기여하지 않는다. D13의 I1/I2 terminal independent reviewer eligibility와 credit은 별도 token이다.

```text
implementation_complete_bundle_sealed = true
post_implementation_owner_decisions_complete = true
post_implementation_semantic_approval = PASS
post_implementation_external_review = PASS
post_implementation_external_reviewer_is_implementation_author = false
post_implementation_external_reviewed_bundle_sha256_match = true
post_implementation_external_review_terminal_gate_credit = 0
owner_approval_bound_to_implementation_bundle_sha256 = true
plan_level_finding_resolution_reviewer_bound = true
plan_level_resolution_independent_gate_credit = 0
open Important = 0
open Critical = 0
open Critical/Important finding의 owner risk acceptance = forbidden
Minor = resolved or explicit owner-accepted bounded disposition
authority_execution_authorized = true
```

별도 roadmap artifact의 존재나 materialization은 implementation entry predicate가 아니다. 현재 implementation entry는 이 plan 내부 normative requirements snapshot의 materialization/presence/tracking과 owner ratification, counterpart plans의 presence/read-only stance, fresh pre-implementation plan review, protected-surface non-overlap 및 required tool availability만 소비한다. Requirements-to-plan traceability, Naturalization reciprocity와 Registry boundary binding은 entry가 아니라 Change 0 exit가 생산한다.

다음은 entry 허용이 아니다.

```text
plan file exists
design requirements are detailed
machine census passes
candidate output directory exists
owner discussed a preferred option
external reviewer is scheduled
```

### Environment Assumptions

* Windows PowerShell을 command shell로 사용한다.
* Python validation은 repository 정책에 따라 `uv run python -B`를 우선한다.
* JSON exact-key 처리는 canonical Python loader 또는 `jq`를 사용하며 PowerShell `ConvertFrom-Json`을 authoritative route로 사용하지 않는다.
* test tooling이 없거나 exact command가 nonzero이면 validation은 blocked/failed로 기록하며 PASS로 주장하지 않는다.

---

## 5. Repository Areas Affected

아래 경로는 계획된 최대 표면이다. Implementation build는 공통 standalone code와 option-capable candidate patch를 만들 수 있지만, branch 또는 owner decision 조건이 붙은 기존 current 경로는 post-implementation 승인 전에는 수정하지 않는다.

### Code

신규 standalone implementation 후보:

* `Iris/build/description/v2/tools/build/dvf_3_3_food_semantic_facts_authority.py`
  * 아래 package만 호출하는 thin phase-subcommand orchestrator
  * business logic, schema interpretation 또는 writer logic을 중복하지 않는 candidate-only CLI
* `Iris/build/description/v2/tools/build/dvf_3_3_food_semantic/`
  * `contracts.py` — shared typed records, canonical JSON/JSONL serialization, digest contract
  * `census_rules.py` — Change 1 census와 Change 2 R1/R2 diagnostics 및 R3 successor execution
  * `lineage_allowlist.py` — Change 3~4 allowed operation과 proposition-level lineage
  * `schema_feasibility.py` — Change 6~7 closed schema, mapping projection, dual-cap feasibility kernel
  * `curation_workflow.py` — Change 8~9 batch/checkpoint/rework와 coverage reconciliation
  * `candidate_writer.py` — Change 5·10~11 candidate-only writer, sink guard와 successor seal
  * `naturalization_handoff.py` — Change 12 frozen proposition-inventory interface와 candidate patch generation
  * `closeout.py` — Change 13 claim/non-claim scan, bundle manifest와 closeout validation
* `Iris/build/description/v2/tests/test_dvf_3_3_food_semantic_kernel.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_food_semantic_curation_writer.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_food_semantic_handoff.py`
* `Iris/build/description/v2/tests/test_dvf_3_3_food_semantic_closeout.py`
* `Iris/build/description/v2/tests/fixtures/dvf_3_3_food_semantic_facts_authority/`

위 package modules는 하나의 standalone food-semantic CLI 내부 구현이며 current core 12개나 allowed tooling 1개를 늘리지 않는다. Phase module은 앞 phase의 declared artifact schema만 소비하고 sibling module의 private function 또는 mutable global state를 직접 호출하지 않는다.

실제 consumer handoff에 필요한 bounded 변경 [post-implementation D16 adoption only]:

* `Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py` [post-implementation D16 only]
  * 승인된 food semantic proposition adapter
  * no-render Phase 2 acceptance mode
* `Iris/build/description/v2/tools/build/validate_dvf_3_3_korean_prose_naturalization.py` [post-implementation D16 only]
* `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_acceptance_gate.py` [post-implementation D16 only]
* `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_semantic_preservation.py` [post-implementation D16 only]

Implementation은 위 current files를 수정하지 않고 attempt root에 exact candidate patch, affected-symbol manifest와 fixtures를 생성한다. Post-implementation D16이 이 변경을 허용하면 exact candidate patch만 채택한다. 거절되면 대체 근사 consumer로 PASS를 만들지 않고 Change 12를 blocked로 닫는다.

R1/R2 diagnostic census에서만 읽는 조사 또는 복구 후보:

* `Iris/build/phase2_rules/rules/__init__.py`
* `Iris/build/phase2_rules/rules/tool_rules.py`
* `Iris/build/phase2_rules/rules/combat_rules.py`
* `Iris/build/phase2_rules/rules/consumable_rules.py`
* `Iris/build/phase2_rules/rules/resource_rules.py`
* `Iris/build/phase2_rules/rules/literature_rules.py`
* `Iris/build/phase2_rules/rules/wearable_rules.py`
* `Iris/build/phase2_rules/rules/furniture_rules.py`
* `Iris/build/phase2_rules/rules/vehicle_rules.py`

R3에서는 위 missing predecessor path를 fabricated recovery로 채우지 않고 standalone successor registry를 사용한다.

### Docs

* `docs/dvf_3_3_facts_authority_enrichment_plan.md` [byte-preserved predecessor; no mutation]
* `docs/dvf_3_3_food_semantic_facts_authority_reconstruction_implementation_plan.md` [this successor]
* `docs/dvf_3_3_food_semantic_authority_policy.md` [신규]
* `docs/dvf_3_3_food_semantic_schema.md` [신규]
* `docs/dvf_3_3_food_semantic_claim_boundary.md` [신규]
* `docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md` [read-only synchronization verification; mutation forbidden]
* `docs/dvf_3_3_registry_authority_canonical_closure_plan.md` [read-only boundary verification; mutation forbidden]
* `Iris/_docs/round3/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/facts_authority_implementation_plan_successor_binding.json` [신규 additive routing supersession]
* `Iris/_docs/authority/food_semantic/README.md` [신규 durable navigation]
* `docs/DECISIONS.md` [D15와 approved closeout 범위에서만 additive]
* `docs/ARCHITECTURE.md` [D15와 approved architecture readpoint 범위에서만 additive]
* `docs/ROADMAP.md` [D15와 approved current-state 범위에서만 additive]

기존 `Iris/_docs/iris-evidence-allowlist.md`의 predecessor 문구는 재작성하지 않는다. successor identity는 별도 durable contract로 추가한다.

### Config

Durable authority contract 후보:

* `Iris/_docs/authority/food_semantic/rule_registry.json`
* `Iris/_docs/authority/food_semantic/evidence_allowlist_contract.json`
* `Iris/_docs/authority/food_semantic/forbidden_inference_registry.json`
* `Iris/_docs/authority/food_semantic/food_semantic_schema.json`
* `Iris/_docs/authority/food_semantic/signal_to_fact_mappings.json`
* `Iris/_docs/authority/food_semantic/curation_policy.json`
* `Iris/_docs/authority/food_semantic/proposition_licensing_contract.json`
* `Iris/_docs/authority/food_semantic/food_semantic_proposition_inventory.schema.json`
* `Iris/_docs/authority/food_semantic/authority_manifest.json`

Future Registry operational-cutover targets; read-only/proposal-only in this plan:

* `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
* `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
* `Iris/_docs/round3/current_route_required_validations.json`
* targeted `.gitignore` negative exceptions proposed for future G1 required artifacts

`Iris/_docs/round3/round3_active_core_closure.json`은 formal D14 proof 대상일 수 있으나 편의상 변경하거나 allowlist를 확대하지 않는다.

### Generated Artifacts

Attempt-local root:

`Iris/build/description/v2/staging/dvf_3_3_food_semantic_facts_authority/attempts/<attempt-id>/`

필수 phase roots:

```text
phase0_plan_and_decisions/
phase1_census/
phase2_rule_authority/
phase3_allowlist/
phase4_lineage/
phase5_writer_contract/
phase6_schema/
phase7_automatic_mapping/
phase8_curation/
phase9_coverage/
phase10_candidate/
phase11_successor/
phase12_phase2_handoff/
phase13_closeout/
```

Owner input root:

`Iris/build/description/v2/owner_inputs/dvf_3_3_food_semantic_facts_authority/`

Protected no-mutation set for the entire plan:

* current facts, decisions, overlay, profile, body_plan inputs
* current rendered output
* Lua bridge outputs
* runtime chunk manifest and chunks
* package payload and package manifest
* predecessor attempts and sealed evidence
* `docs/dvf_3_3_facts_authority_enrichment_plan.md` exact predecessor bytes
* `docs/dvf_3_3_food_semantic_facts_authority_reconstruction_implementation_plan.md` Appendix A normative requirements snapshot bytes/identity and successor-plan traceability evidence
* Naturalization and Registry counterpart plan bytes consumed by read-only synchronization

Facts, input manifest, required-validation manifest와 `.gitignore`도 이 plan에서는 변경하지 않는다. Future Registry operational-cutover가 별도 검토 후 exact target을 소유한다.

---

## 6. Planned Changes

### Requirements-to-Plan Traceability

| Requirements Phase | Planned Change | Primary Exit |
|---|---|---|
| 0 | Change 0 | mechanical requirements/plan traceability and implementation entry |
| 1 | Change 1 | exact 317 and protected baseline |
| 2 | Change 2 | R1/R2 diagnostic disposition and deterministic R3 successor |
| 3 | Change 3 | canonical allowlist proposal and validator |
| 4 | Change 4 | adopted-granularity lineage 100% |
| 5 | Change 5 | candidate-only writer contract |
| 6 | Change 6 | closed semantic schema proposal and validator |
| 7 | Change 7 | automatic mapping proposal and dry-run feasibility |
| Feasibility kernel checkpoint | Changes 0~7 | R3/schema/mapping/curation-workload feasibility PASS |
| 8 | Change 8 | curation workflow, packets and approval validators |
| 9 | Change 9 | 317/317, blocked/unsupported 0 |
| 10 | Change 10 | deterministic writer implementation and non-authoritative dry run |
| 11 | Change 11 | successor seal/cutover-request tooling and non-authoritative fixtures |
| 12 | Change 12 | frozen Phase 2 proposition interface, candidate patch and no-render fixtures |
| 13 | Change 13 | required-gate/closeout tooling, claim scan and reviewer-eligibility fixtures |
| Implementation completion checkpoint | all Changes | implementation-complete bundle; no owner/review token consumed |
| Post-implementation authority checkpoint | approved actions | owner decisions/approval, external review, authority execution and terminal review |

#### Appendix A Required-Authority-Outcome Traceability

위 표는 phase-indexed execution traceability이고, 아래 표는 Appendix A의 `required authority outcomes`를 outcome-indexed로 전건 매핑한다. `requirements_to_plan_traceability = complete`는 두 표를 모두 소비하며, 아래 12개 outcome 중 누락·중복·빈 evidence binding이 하나라도 있으면 false다.

| Outcome ID | Appendix A required authority outcome | Planned Change | Required evidence or exit |
|---|---|---|---|
| O-01 | R3 official successor만 executable Rule route이며 R1/R2는 diagnostic-only | Changes 0, 2 | D2 retirement provenance와 `approved_rule_route = R3`, selected Rule identity, R3 semantic approval |
| O-02 | Evidence Allowlist document heading/history/machine identity를 하나의 canonical version으로 reconciliation | Changes 1, 3 | three-way census와 `document_machine_identity_match = true` |
| O-03 | allowed source fields와 operations를 machine-readable/version-bound로 봉인 | Change 3 | allowed field/operation registries, canonical allowlist SHA-256, unclassified field/operation count 0 |
| O-04 | 모든 automatic proposition에 source/Rule/allowlist/mapping lineage 제공 | Changes 4, 7, 10 | `candidate_fact_proposition_lineage_coverage = 100%`, missing lineage count 0 |
| O-05 | 모든 curated proposition에 reviewed value/rationale/approval 제공 | Change 8 | curated approval ledger와 `curated_approval_missing_count = 0` |
| O-06 | exact 317 전건에 automatic 또는 curated terminal semantic disposition 제공 | Changes 1, 9 | exact member-set binding과 coverage reconciliation 317/317, gap/double count 0 |
| O-07 | unsupported fact, arbitrary inference와 Layer 4 automatic promotion count 0 | Changes 7~9 | `unsupported_fact_count = 0`, `arbitrary_inference_count = 0`, `layer4_auto_promotion_count = 0` |
| O-08 | non-target facts row byte identity 보존 | Changes 1, 10 | protected baseline과 `non_target_row_byte_mismatch_count = 0` |
| O-09 | successor facts와 input manifest를 predecessor/current와 구분 | Changes 10, 11 | successor facts/manifest identity reports, non-current Branch B seal과 `candidate_current_identity_confusion = 0` |
| O-10 | actual Naturalization Phase 2가 selected successor facts/manifest/schema/license exact identities 소비 | Change 12 | actual consumer receipt와 four-SHA equality predicates |
| O-11 | approved facts가 actual Phase 2 consumer에서 meaningful semantic partition 형성 | Change 12 | licensed-proposition partition definition, `meaningless_partition_count = 0`, D10 승인 시 `minimum_meaningful_partition >= 4` |
| O-12 | same-skeleton group이 canonical policy/detector bound를 넘지 않으며 이 값은 upstream schema gate가 아님 | Changes 6, 12 | schema diagnostic gate credit 0, threshold identity binding과 `maximum_same_skeleton_group <= bound_threshold_value` |

Change 0~7 feasibility kernel이 PASS한 뒤에만 Change 8~13의 code/schema/report generator/validator/fixture 구현을 시작한다. 표의 `approved`, `authority`, `acceptance`, `adoption`, `closeout`은 implementation completion checkpoint 뒤 authority execution state이며 implementation completion state와 동일하지 않다.

### Feasibility-First Implementation Cut

Change 0~7은 전체 후속 구현 전에 실행되는 독립 feasibility kernel이다. 이 kernel은 owner decision·approval, 외부 review, curated authority 또는 current mutation을 소비하지 않고 R3 successor, closed schema, automatic mapping과 예상 curation workload가 실제 구현 가능한 모양인지 검증한다.

```text
feasibility_kernel_changes_0_through_7_complete = true
r3_successor_registry_implementation_complete = true
r3_determinism_validation = PASS
r1_r2_member_disposition_complete = true
closed_schema_validator = PASS
schema_has_meaningful_distinctions = true
schema_combination_rules_satisfiable = true
schema_threshold_driven_token_count = 0
automatic_mapping_conflict_count = 0
exact_317_automatic_or_curation_route_count = 317
unrouted_target_count = 0
predicted_required_curation_items <= proposed_curation_item_cap
predicted_required_curation_propositions <= proposed_curation_proposition_cap
feasibility_authority_claim_emitted_count = 0
```

`schema_expressible_meaningful_profile_count`는 `schema_satisfiability_report.json`에 숫자로 기록할 수 있지만 diagnostic-only이며 feasibility kernel gate credit은 0이다. Kernel은 schema가 의미 차이를 갖고 조합 규칙이 satisfiable하며 threshold-driven token이 없는지만 차단 조건으로 소비한다. 최소 partition 4와 동일 골격 상한은 taxonomy/schema 설계 입력이 아니며, D10이 exact proposal을 승인한 경우 approved facts를 actual Phase 2 consumer에 투영하는 Change 12에서만 acceptance criterion으로 검사한다.

```text
feasibility_kernel_state = PASS
does_not_imply
food_semantic_schema_semantic_approval = PASS
```

Kernel PASS는 R3/schema/mapping/curation workload의 mechanical·structural feasibility만 뜻한다. Owner semantic preread는 implementation 이전에 수행하거나 gate credit으로 소비하지 않는다. Owner가 implementation-complete bundle의 schema axis, vocabulary, combination rule 또는 proposition licensing을 거절하면 현재 bundle은 `rejected_postimplementation_schema`로 append-only 보존하고 Changes 6~13 output 전부를 non-authoritative로 유지한다. 같은 attempt를 수정하지 않으며 새 attempt가 Change 0부터 시작해 affected Changes 6~13을 다시 생성한다.

위 conjunction이 PASS이면 `feasibility_kernel_state=PASS`를 봉인하고 Change 8~13 구현을 시작한다. 하나라도 실패하면 다음 state로 fail-loud 종료한다.

```text
feasibility_kernel_state = BLOCKED
food_semantic_facts_authority_implementation_state = blocked_feasibility_kernel
changes_8_through_13_started = false
implementation_complete_bundle_sealed = false
```

BLOCKED kernel은 실패 원인, exact input/code/schema hashes, 예상 automatic/curation denominator와 재시작 조건을 `feasibility_kernel_bundle.json`에 봉인한다. 같은 attempt에서 schema, mapping 또는 cap을 상향 조정하지 않는다. 수정은 새 attempt에서 Change 0부터 다시 실행한다.

### Review Finding Disposition

기존 finding은 plan text에 반영됐지만 이번 synchronization 이후 exact plan hash에 대한 pre-implementation review를 다시 수행해야 한다. Open Critical/Important는 implementation build를 차단한다. Implementation-complete bundle external review와 terminal independent review는 별도 후속 review다.

| Finding | Plan-text disposition | Re-review state |
|---|---|---|
| R-1 | predecessor exact bytes restored, successor 별도 path, protected identity, overwrite episode non-laundering | pending |
| R-2 | owner directive에 따라 별도 roadmap은 제거하되 Appendix A normative requirements snapshot과 tracked plan Git blob으로 durable retrievability 확보 | reflected; pending re-review |
| R-3 | D16, Naturalization tooling owner, baseline/no-impact proof | pending |
| R-4 | Branch B divergence, future Registry cutover request와 freshness report | pending pre-implementation re-review |
| R-5 | B sealed-successor terminal과 future Registry A/G1 non-claim 분리 | pending pre-implementation re-review |
| R-6 | exact 317 set과 proposition-level lineage 의무화 | pending |
| R-7 | post-promotion correction-only | pending |
| R-8 | denominator role/delta reconciliation | pending |
| R-9 | threshold authority/no-relaxation binding | pending |
| R-10 | meaningful partition 정의와 detector-positive fixture | pending |
| R-11 | read-only/mutating entry gate 분리 | pending |
| R-12 | non-target byte identity와 derived denominator | pending |
| R-13 | Phase 7 curation feasibility gate | pending |
| R-14 | G1 tracked/not-ignored targeted VCS disposition | pending |
| R-15 | R1/R2 diagnostic member의 R3 또는 curated lane 전건 disposition | pending |
| R-16 | fixture vocabulary non-authority disclaimer | pending |
| R-17 | axis-qualified completion states | pending |
| R-18 | proof 결과 전 decision timing | pending |
| R-19 | forbidden field/operation 기반 arbitrary inference 정의 | pending |
| R-20 | D8 exact manual-review denominator | pending |
| R-21 | H1 round identity | pending |

Cycle 2 재검토 finding disposition:

| Finding | Plan-text disposition | Re-review state |
|---|---|---|
| I-1 | Change 0 requirements/plan traceability, implementation entry/exit, Change 1 exit predicate를 분리 | pending post-implementation review |
| I-2 | G-A strict blocker-zero를 post-implementation authority gate에 적용; OPEN Important owner-waiver 금지 | pending post-implementation review |
| I-3 | selected Phase 11 successor와 Phase 12 consumed facts/manifest/schema/license SHA equality | pending |
| I-4 | policy/detector path/hash/value reconciliation과 mismatch classification | pending |
| I-5 | item/proposition curation cap 양축 정의 | pending |
| I-6 | Branch A `current_authority_defect_declared` first-class state | pending |
| I-7 | Scenario B temporary overwrite/restore episode와 recovery source ceiling 명시 | pending |
| M-1 | C1/C2/I1/I2 option 정의 | pending |
| M-2 | 33 non-claims를 독립 claim-ceiling denominator로 분리 | pending |
| M-3 | D3/D4 `retired_mandatory_contract` ledger record | pending |
| M-4 | materialized/present/binding-verified predicate 분리 | pending |
| M-5 | logical line count 정규화 정의 | pending |
| M-6 | 149/56 관찰값을 Change 1 reconciliation에 결속 | pending |

Cycle 3 재검토 finding disposition:

| Finding | Plan-text disposition | Re-review state |
|---|---|---|
| P-1 | owner-waiver 금지를 open Critical/Important로 한정하고 Minor bounded disposition과 정합화 | pending |
| P-2 | Phase 6 projection 기반 D7 cap proposal을 Phase 7 dry-run 전 봉인하고 owner accept/reject는 implementation 뒤로 이동 | pending post-implementation review |
| P-3 | Change 0 full exit PASS와 Change 1의 5-predicate 진단 subset을 구분; Important blocker는 post-implementation authority gate에 고정 | pending post-implementation review |
| P-4 | plan-level finding resolver eligibility와 independent gate 무기여를 명시 | pending |
| P-5 | live manifest non-claim enumeration을 Change 13 final scan에 exact binding | pending |
| P-6 | evidence 부족 시 침묵과 bounded curated manual override의 철학적 경계를 명시 | pending |

Cycle 4 종합 재검토 finding disposition:

| Finding | Plan-text disposition | Re-review state |
|---|---|---|
| C-1 | Appendix A normative requirements snapshot을 이 repo-relative plan에 내장하고 독립 hash/line count 결속; historical attachment는 non-normative | reflected; pending re-review |
| I-1 | Naturalization counterpart plan을 exact path/hash/contract-anchor read-only verification으로 고정하고 mutation 금지 | reflected; pending re-review |
| I-2 | kernel PASS의 mechanical/structural ceiling과 schema owner rejection blast radius/new-attempt routing 명시 | reflected; pending re-review |
| I-3 | D12를 future Registry cutover request 발행 전 correction-contract decision으로 재범위화 | reflected; pending re-review |
| I-4 | existing selected-successor 4-SHA equality/non-current fixtures에 actual Phase 2 consumer receipt를 추가 | reflected; pending re-review |
| I-5 | requirements artifact materialization, entry presence와 Change 0 exit binding predicate를 분리 | reflected; pending re-review |
| I-6 | owner risk acceptance의 Critical/Important gate credit 0 규칙이 §4/§11에 존재함을 재확인 | closed by existing text; pending re-review |
| M-1 | in-round evidence condition을 successor facts/manifest `sealed`로 한정 | reflected; pending re-review |
| M-2 | C1/C2와 I1/I2 allowed semantics/claim ceiling이 §4에 정의됐음을 재확인 | closed by existing text; pending re-review |

Cycle 5 최종 종합 검토 및 S-1 후속 finding disposition:

| Finding | Plan-text disposition | Re-review state |
|---|---|---|
| I-1 | §0.1을 owner approval → external implementation review → authority execution → sealed successor → terminal independent closeout → owner final seal → terminal hash seal 순서로 통일하고 review token을 분리 | reflected; pending fresh re-review |
| I-2 | `schema_expressible_meaningful_profile_count >= 4`를 kernel blocker에서 제거하고 meaningful distinction/satisfiable combination/no threshold-driven token만 kernel gate로 유지; 4-partition 검사는 D10 승인 시 Change 12로 한정 | reflected; pending fresh re-review |
| I-3 | Appendix A author/ratification metadata, entry predicates와 fidelity 요구사항을 추가하고 owner의 2026-07-27 구현 진행 지시를 `ratified_owner_directive`로 기록 | reflected; owner ratification recorded, pending fresh re-review |
| M-1 | implementation target을 proposal technical/structural feasibility PASS로 낮추고 business feasibility claim을 금지 | reflected; pending fresh re-review |
| M-2 | external implementation reviewer의 non-author, exact bundle-hash match, terminal-credit 0 predicate 추가 | reflected; pending fresh re-review |
| M-3 | Publish 계획을 Change 0 direct input에서 제거하고 §0.4의 non-synchronization boundary만 유지 | reflected; pending fresh re-review |
| S-1 | Appendix A required-authority-outcome 12건을 outcome-indexed Change/evidence mapping으로 추가하고 Change 0 completeness predicate에 결속 | reflected; pending fresh re-review |

### Change 0 — Mechanical Plan Binding, Option Matrix and Implementation Entry Freeze

Purpose:

사용자 제공 설계 요구사항과 successor plan의 범위를 hash로 결속하고 reciprocal cross-plan synchronization과 pre-implementation plan review를 검증한 뒤, implementation entry와 post-implementation authority execution 권한을 분리한다. 별도 roadmap 파일은 생성하거나 소비하지 않는다.

Files:

* 이 plan의 normative requirements snapshot과 본 successor plan identity
* currently restored predecessor plan and explicit temporary overwrite/restore episode
* `docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md`
* `docs/dvf_3_3_registry_authority_canonical_closure_plan.md`
* `owner_reserved_decisions.schema.json` and unselected option matrix
* `phase0_plan_and_decisions/requirements_plan_traceability.json`
* `phase0_plan_and_decisions/review_finding_disposition.json`
* `phase0_plan_and_decisions/predecessor_overwrite_restore_episode.json`
* additive facts-authority implementation-plan successor binding
* `phase0_plan_and_decisions/cross_plan_sync_binding.json`
* `phase0_plan_and_decisions/preimplementation_plan_review_binding.json`
* `phase0_plan_and_decisions/protected_surface_policy.json`
* `phase0_plan_and_decisions/post_implementation_review_bundle_schema.json`
* `phase0_plan_and_decisions/implementation_entry_gate.json`

Implementation Notes:

* predecessor draft와 successor implementation plan은 서로 다른 durable path를 사용한다. Predecessor exact bytes, SHA-256, line count를 protected surface와 evidence manifest에 포함한다.
* predecessor overwrite episode는 Scenario B다. Cycle 1 plan authoring 중 predecessor path가 successor content로 임시 교체됐고, prior exact session read record에서 복구한 뒤 repo-relative routing correction의 expected SHA-256과 대조했다.
* episode record는 overwritten successor identity, occurrence time/readpoint, `restore_source_kind=session_read_record`, `restore_source_commit_or_blob_available=false`, routing-correction verifier path/hash, restored path/hash/logical-line-count, `boundary_violation_preserved=true`를 기록한다. Commit/blob recovery였다고 과대 주장하지 않는다.
* immutable routing correction의 predecessor plan binding은 재작성하지 않는다. 별도 additive successor binding이 predecessor path/hash와 successor path/hash를 함께 결속하고 routing ambiguity를 0으로 만든다.
* reviewed design requirements와 successor plan에 없는 scope, claim, current mutation을 추가하지 않는다.
* `cross_plan_sync_binding.json`은 Naturalization/Registry counterpart 각각의 repo-relative path, planning SHA-256, execution SHA-256, contract token/anchor, producer projection SHA-256, consumer projection SHA-256, mutation-allowed=false와 exact match verdict를 기록한다.
* Responsibility Boundary, Authority/Evidence Integrity, Adversarial/Failure-Mode pre-implementation plan review의 exact reviewed plan hash, ratified requirements snapshot SHA-256, verdict, finding counts와 finding-disposition identity를 결속한다. Owner ratification 뒤의 exact plan Git blob을 fresh review하지 않으면 PASS가 아니다. Implementation-complete bundle review와 terminal independent review는 별도 후속 축이다.
* pre-implementation plan review의 Open Critical/Important는 Change 0 진입 전에 0이어야 한다. Minor finding은 exact reviewer-recorded bounded disposition이 있을 때만 carry할 수 있으며 owner approval token을 소비하지 않는다.
* Change 0 bootstrap entry는 이 계획 header와 Appendix A에 기록된 normative requirements snapshot materialization/presence와 current successor-plan identity만 소비한다. Historical source attachment path의 live 존재는 요구하지 않는다. Change 0 exit는 requirements-to-plan traceability binding을 생산하고, Change 1 exit는 predecessor evidence/current baseline/exact 317 binding을 생산한다.
* `requirements_artifact_materialized`는 repo-relative plan path와 Appendix marker가 존재함을 뜻하고, `requirements_artifact_tracked`는 reviewed commit/tree에서 해당 path가 Git blob으로 조회됨을 뜻한다. Untracked working-tree copy나 machine-local attachment는 entry credit 0이다. Change 0은 plan Git blob ID, requirements snapshot SHA-256/line count와 reviewed commit identity를 함께 결속한다.
* `requirements_plan_traceability.json`은 historical design source path/hash/line count를 provenance-only input으로 보존하고 `normative_authority_transition=owner_directed_embedded_requirements_snapshot`을 기록한다. Appendix A가 historical attachment의 byte-exact copy라고 주장하지 않으며, snapshot normalization은 marker-excluded UTF-8 LF/exactly-one-terminal-LF 규칙으로 재계산한다.
* 같은 traceability artifact는 O-01~O-12 각각의 Appendix A normalized line identity, mapped Change ID, required evidence/exit token과 coverage verdict를 기록한다. Count equality만으로 PASS하지 않으며 missing/duplicate outcome ID 또는 빈 evidence binding은 `requirements_outcome_traceability=complete`를 금지한다.
* Appendix A는 planning synthesis이므로 owner ratification 전에는 canonical requirements authority credit이 0이다. Change 0은 plan header의 non-placeholder approver identity, approval time, ratified snapshot SHA-256를 재계산해 Appendix marker scope와 일치시킨다. 이 ratification은 implementation 결과의 semantic/adoption approval이 아니며 D1/D5~D16 owner-decision token을 선소비하지 않는다.
* Evidence Allowlist document/machine identity reconciliation과 downstream meaningful semantic partition formation은 owner-provided problem definition의 required closure outcomes로 Appendix A와 traceability matrix에 각각 독립 row를 가진다.
* Appendix A의 R3 sole-executable requirement는 원 문제 정의의 literal이 아니라 planning-chain D2 retirement disposition에서 파생됐다. Owner ratification은 이 provenance를 포함한 exact snapshot을 승인해야 하며 R1/R2는 diagnostic-only ceiling을 유지한다.
* G-A strict blocker-zero는 implementation build가 아니라 post-implementation authority execution에 적용한다. OPEN Critical/Important는 owner risk acceptance로 우회하지 않는다.
* planning-time dirty worktree를 clean으로 만들기 위해 user changes를 reset/delete하지 않는다. Mechanically verified clean commit 또는 isolated worktree를 사용한다.

Implementation Validation:

```text
requirements_artifact_materialized = true
requirements_artifact_present_at_entry = true
requirements_artifact_tracked = true
requirements_artifact_git_blob_identity_bound = true
requirements_artifact_owner_ratified = true
requirements_ratification_approver_identity_present = true
requirements_ratification_approval_time_present = true
requirements_ratified_snapshot_sha256_match = true
preimplementation_review_bound_to_ratified_snapshot_sha256 = true
requirements_snapshot_sha256_match = true
requirements_snapshot_logical_line_count_match = true
requirements_to_plan_traceability = complete
appendix_required_authority_outcome_count = 12
appendix_required_authority_outcome_traceability_count = 12
appendix_required_authority_outcome_unmapped_count = 0
appendix_required_authority_outcome_duplicate_id_count = 0
requirements_outcome_traceability = complete
requirements_plan_binding_verified_at_exit = true
facts_naturalization_sync_reciprocal = true
naturalization_counterpart_contract_present = true
naturalization_counterpart_projection_byte_equivalent = true
naturalization_plan_mutation_count = 0
facts_registry_boundary_binding = true
registry_plan_mutation_count = 0
publish_direct_sync_required = false
preimplementation_plan_review = PASS
preimplementation_open_critical_count = 0
preimplementation_open_important_count = 0
change0_predecessor_plan_identity_verified = true
change0_successor_plan_identity_verified = true
change0_routing_ambiguity_count = 0
change0_protected_surface_policy_materialized = true
predecessor_overwrite_restore_episode_recorded = true
predecessor_restore_hash_matches_bound_identity = true
predecessor_boundary_violation_preserved = true
predecessor_restore_source_overclaim_count = 0
plan_only_new_claim_count = 0
owner_decision_option_matrix = complete
read_only_no_mutation_contract = true
semantic_owner_decision_consumed_count = 0
postimplementation_owner_approval_consumed_count = 0
postimplementation_external_review_consumed_count = 0
```

위 atomic predicate가 모두 true일 때만 `change0_exit_pass = true`다. Pre-implementation plan review는 Change 0의 필수 선행 조건이다. Owner decision·approval, implementation-complete bundle review, terminal reviewer eligibility와 final owner seal은 §4의 post-implementation authority execution 요건으로 분리하며 Change 0 또는 implementation build가 소비하지 않는다.

---

### Change 1 — Current Checkout Census and Exact Identity Binding

Purpose:

317 target universe, current facts/manifest, item-script source, generated tags, Layer 4, Rule path, allowlist versions, writer capability, predecessor evidence를 current checkout에서 read-only로 재계수한다.

Files:

* existing sources listed in Section 1
* `phase1_census/target_food_universe_manifest.json`
* `phase1_census/current_facts_identity_report.json`
* `phase1_census/rule_module_census.json`
* `phase1_census/allowlist_identity_census.json`
* `phase1_census/generated_tag_role_report.json`
* `phase1_census/layer4_signal_role_report.json`
* `phase1_census/writer_capability_census.json`
* `phase1_census/predecessor_evidence_manifest.json`
* `phase1_census/protected_surface_hashes_before.json`
* `phase1_census/set_identity_report.json`
* `phase1_census/required_validation_denominator_reconciliation.json`
* `phase1_census/live_non_claim_enumeration.json`

Implementation Notes:

* exact Unicode/code-point identity와 case-sensitive FullType를 보존한다.
* `Base.LemonGrass`/`Base.Lemongrass`를 병합하지 않는다.
* count equality를 set identity로 대체하지 않는다.
* current, predecessor, diagnostic, Layer 4, staging, sealed role을 path별로 분류한다.
* generated tags의 317 coverage는 authority 증거가 아니다.
* Layer 4 singleton은 누락/비누락 사실만 기록하며 semantic value를 채우지 않는다.
* exact Naturalization target 317과 facts target 317의 case-sensitive member-set equality를 의무적으로 증명한다.
* required-validation count를 하나의 denominator로 합치지 않는다. 최소 reconciliation table은 다음 planning readpoint를 역할별로 분리하고 execution-time current value/delta를 다시 계산한다.

| Observed count | Role | Source readpoint | Consumption |
|---:|---|---|---|
| 149 artifacts | live required-artifact denominator | `Iris/_docs/round3/current_route_required_validations.json` | G1 required-artifact adoption, presence and VCS enforcement |
| 56 tests | live required-test denominator | `Iris/_docs/round3/current_route_required_validations.json` | G1/current-route required test enforcement; artifact denominator가 아님 |
| 33 non-claims | planning-readpoint live claim-ceiling enumeration | `Iris/_docs/round3/current_route_required_validations.json` | Change 13 final claim/non-claim vocabulary scan의 exact input; artifact/test denominator가 아님 |
| 93 artifacts / 48 tests | historical required-artifact preflight roles | sealed preflight report and `docs/DECISIONS.md` trace | predecessor comparison only |
| 56 artifacts / 37 tests | historical durable-surface roles | `docs/DECISIONS.md` durable readpoint trace | durable-surface history only |
| 127 tests | historical parent current-route total | `docs/DECISIONS.md` parent validation trace | route-level test total, not a manifest artifact/test denominator |

실행 artifact는 각 row에 `count`, `role`, `source_artifact`, `predecessor_value`, `current_value`, `delta`, `delta_explanation`, `consumption_phase`를 기록한다.

`live_non_claim_enumeration.json`은 execution-time live manifest에서 non-claim member를 재열거하고 source path/hash, canonical member set, observed count, enumeration SHA-256을 봉인한다. Planning readpoint의 33은 관찰값이며, 설명된 delta 없이 고정 상수나 claim authority로 사용하지 않는다. Change 13은 이 exact enumeration identity를 소비해야 한다.

Implementation Validation:

```text
target_member_count = 317
naturalization_facts_exact_set_identity = true
duplicate_identity_count = 0
missing_identity_count = 0
relevant_surface_unclassified_count = 0
protected_surface_changed_count = 0
predecessor_evidence_hash_bound = true
change1_predecessor_evidence_hashes_bound = true
change1_protected_current_baseline_captured = true
change1_exact_317_identity_bound = true
unexplained_denominator_delta_count = 0
denominator_role_substitution_count = 0
non_claim_role_substitution_count = 0
live_manifest_non_claim_enumeration_bound = true
live_manifest_non_claim_enumeration_sha256_bound = true
change1_live_non_claim_enumeration_sha256 = sha256(phase1_census/live_non_claim_enumeration.json)
```

---

### Change 2 — Classification / Rule Authority Reconstruction

Purpose:

R1 history/recovery census와 R2 reproducible-subset diagnostic census를 수행하되, generated signal을 재생산하는 executable Rule authority는 R3 official successor registry 하나로 고정한다. R1/R2 조사 결과는 R3 source/rule design에 참고할 수 있지만 recovery equivalence나 authority route를 만들지 않는다.

Files:

* existing `phase2_rules` modules [R1/R2 read-only diagnostic inputs]
* recovered Rule paths [R1/R2 diagnostic evidence only]
* `Iris/_docs/authority/food_semantic/rule_registry.json` [R3 executable successor registry]
* `phase2_rule_authority/recovery_attempt_log.jsonl`
* `phase2_rule_authority/rule_dependency_manifest.json`
* `phase2_rule_authority/rule_execution_order_manifest.json`
* `phase2_rule_authority/rule_reproducibility_report.json`
* `phase2_rule_authority/predecessor_rule_disposition.json`
* `phase2_rule_authority/provenance_gap_record.json`

Implementation Notes:

* R1은 canonical source, history, producer identity가 증명된 byte/content만 historical recovery evidence로 기록한다. 발견된 파일도 executable route로 복원하지 않고 R3 divergence input으로만 사용한다.
* R2는 재현 가능한 Rule/row와 provenance gap을 진단해 residual report를 만든다. R2 output은 authority candidate, Phase 2 terminal exit 또는 fallback execution route가 될 수 없다.
* 모든 R1/R2 recovered/reproducible member는 R3 successor Rule 또는 non-automatic/curated lane으로 전건 disposition한다. 누락된 disposition은 R3 feasibility FAIL이다.
* R3 implementation output은 predecessor equivalence를 주장하지 않는 유일한 executable official-successor registry proposal이다. Post-implementation semantic approval은 R3의 exact content를 승인 또는 거절할 수 있지만 다른 Rule route를 선택하지 않는다.
* successor registry proposal의 각 Rule은 `rule_id`, `rule_version`, `registry_version`, source family/field, normalization operations, output signal, dependency set, execution order, determinism contract를 가진다.
* arbitrary Python callback이나 hidden environment dependency를 registry 계약으로 허용하지 않는다.
* fixed order를 machine manifest로 기록하고 input ordering을 바꿔도 canonical output이 동일한지 검사한다.
* Rule determinism fixture는 최소 두 `PYTHONHASHSEED`, fixed locale variants와 reversed filesystem traversal order에서도 byte-identical signal/lineage output을 요구한다.

Implementation Validation:

```text
unregistered_rule_count = 0
undefined_dependency_count = 0
hidden_dependency_count = 0
same_input_same_signal_output = true
execution_order_deterministic = true
historical_equivalence_overclaim = 0
historical_equivalence_overclaim_token_scan_bound = true
rule_residual_undispositioned_count = 0
failure_evidence_deleted_count = 0
r3_successor_registry_implementation_complete = true
rule_executable_route = R3
r1_authority_execution_count = 0
r2_authority_execution_count = 0
r1_r2_member_disposition_complete = true
d2_retired_mandatory_contract_recorded = true
```

Post-Implementation Authority Gate:

```text
approved_rule_route = R3
selected_rule_route_identity_bound = true
r3_successor_registry_semantic_approval = PASS
```

---

### Change 3 — Evidence Allowlist Identity and Allowed Surface Seal

Purpose:

문서 0.4/history 0.5/machine 0.3 divergence를 content 기준으로 비교하고 food semantic automatic lane이 사용할 source field와 operation의 단일-identity proposal 및 validators를 구현한다. Canonical authority 채택은 post-implementation owner semantic approval이 수행한다.

Files:

* predecessor allowlist doc/machine files
* `Iris/_docs/authority/food_semantic/evidence_allowlist_contract.json`
* `Iris/_docs/authority/food_semantic/forbidden_inference_registry.json`
* `phase3_allowlist/three_way_divergence_report.json`
* `phase3_allowlist/version_impact_census.json`
* `phase3_allowlist/allowed_source_field_registry.json`
* `phase3_allowlist/allowed_operation_registry.json`
* `phase3_allowlist/forbidden_operation_registry.json`
* `phase3_allowlist/allowlist_identity_binding_report.json`
* `phase3_allowlist/predecessor_version_disposition.json`

Implementation Notes:

* version number의 크기만으로 canonical을 선택하지 않는다.
* identity reconciliation과 new allowlist expansion을 분리한다.
* `DisplayName`, `Description`, `DisplayCategory`, Java decompile, unbounded contains, numeric threshold inference, item ID/hash/random partition을 forbidden으로 고정한다.
* exact token membership과 field existence도 semantic fact mapping 권한을 자동 획득하지 않는다.
* 기존 predecessor allowlist를 in-place rewrite하지 않고 successor contract를 additive하게 추가한다.
* contract path와 canonical content hash를 Rule registry, lineage, mapping이 동일하게 참조한다.
* forbidden registry는 automatic fact가 읽거나 적용할 수 없는 source field와 operation을 machine-readable하게 열거한다. `arbitrary inference`는 이 forbidden source field 또는 forbidden operation을 경유해 생성된 fact로 조작적으로 정의한다.

Implementation Validation:

```text
allowlist_reconciliation_proposal_exists = true
proposed_document_machine_identity_match = true
unclassified_divergence_count = 0
forbidden_source_field_unclassified_count = 0
forbidden_operation_unclassified_count = 0
unclassified_field_count = 0
unclassified_operation_count = 0
forbidden_operation_execution_count = 0
signal_fact_conflation_count = 0
allowlist_owner_approval_consumed_during_implementation = false
```

Post-Implementation Authority Validation:

```text
allowlist_owner_approval = present
canonical_allowlist_identity_exists = true
document_machine_identity_match = true
approved_allowlist_sha256 = implementation_proposed_allowlist_sha256
```

---

### Change 4 — Lineage Contract and Successor Signal Regeneration

Purpose:

모든 candidate automatic signal과 proposed final automatic fact proposition을 source artifact와 field/value까지 추적할 수 있게 하고 old generated tags와 successor output의 차이를 설명한다. Adopted authority claim은 post-implementation approval 뒤에만 가능하다.

Files:

* `Iris/_docs/authority/food_semantic/authority_manifest.json`
* `phase4_lineage/lineage_schema.json`
* `phase4_lineage/successor_signals.jsonl`
* `phase4_lineage/lineage_ledger.jsonl`
* `phase4_lineage/lineage_completeness_report.json`
* `phase4_lineage/lineage_conflict_report.json`
* `phase4_lineage/legacy_successor_divergence_report.json`
* `phase4_lineage/old_generated_tag_disposition.json`

Implementation Notes:

Intermediate signal provenance는 다음을 가진다.

```text
item_identity
source_family
source_artifact path/hash
source_item_locator
source_field
source_value 또는 value hash
normalization operation chain
allowlist identity
rule identity
rule output signal
writer attempt identity
```

Final automatic fact lineage는 선택사항 없이 다음을 추가한다.

```text
fact_field
fact_value
signal_to_fact_mapping_id
mapping_version
fact proposition identity
```

Row/tag lineage는 signal provenance를 보조할 수 있지만 terminal semantic proposition authority를 충족하지 않는다.

Old generated tags에 사후 추정 lineage를 붙이지 않는다. 새 source에서 새 Rule을 실행한 successor signal만 automatic lane 후보가 된다.

Implementation Validation:

```text
candidate_signal_lineage_coverage = 100%
candidate_fact_proposition_lineage_coverage = 100%
missing_source_locator_count = 0
missing_rule_identity_count = 0
missing_allowlist_identity_count = 0
missing_fact_field_value_mapping_lineage_count = 0
retroactive_invented_lineage = 0
same_input_same_lineage_output = true
unexplained_divergence_count = 0
adopted_authority_claim_emitted_during_implementation_count = 0
```

Post-Implementation Authority Validation:

```text
adopted_signal_lineage_coverage = 100%
adopted_fact_proposition_lineage_coverage = 100%
```

---

### Change 5 — Scoped Writer Authority Contract

Purpose:

candidate generation 전에 writer의 input, target subset, output, sink, forbidden surface와 failure preservation을 executable contract로 고정한다.

Files:

* standalone authority tool
* `phase5_writer_contract/scoped_writer_contract.json`
* `phase5_writer_contract/writer_input_allowlist.json`
* `phase5_writer_contract/writer_output_allowlist.json`
* `phase5_writer_contract/hard_forbidden_surface_contract.json`
* `phase5_writer_contract/writer_negative_fixture_results.json`
* `phase5_writer_contract/single_writer_authority_report.json`
* `phase5_writer_contract/tooling_allowlist_relation_report.json` [D14]

Implementation Notes:

```text
scope = food_semantic_facts_only
context = attempt_local
authority = candidate_only
target = exact target manifest
live current write = false
```

Writer는 semantic inference, approval, Registry promotion, validation waiver를 수행하지 않는다. 승인된 schema, automatic ledger, curated ledger, target manifest, predecessor facts만 join한다.

Candidate writer는 explicit output root를 필수로 받고 resolved target이 current facts, rendered, Lua, runtime, package 또는 predecessor attempt 아래이면 write 전에 nonzero로 거부한다.

새 writer는 current core 12개나 allowed tooling 1개에 추가하지 않는다. G1 required test가 필요하면 test가 writer module을 current process에 import하지 않고 standalone validator/report를 subprocess/read-only 방식으로 소비한다.

Implementation Validation:

```text
writer_current_sink_count = 0
writer_unapproved_input_count = 0
out_of_scope_row_write_blocked = true
out_of_scope_field_write_blocked = true
live_sink_request_blocked = true
single_writer_authority = true
```

---

### Change 6 — Food Semantic Schema and Proposition Authority

Purpose:

식품의 실제 role/state 차이를 closed vocabulary로 표현하고 각 fact가 DVF consumer에 허용하는 proposition을 명시한다.

Files:

* `docs/dvf_3_3_food_semantic_schema.md`
* `Iris/_docs/authority/food_semantic/food_semantic_schema.json`
* `Iris/_docs/authority/food_semantic/proposition_licensing_contract.json`
* `phase6_schema/combination_rule_matrix.json`
* `phase6_schema/schema_examples_and_counterexamples.json`
* `phase6_schema/schema_satisfiability_report.json`
* `phase6_schema/schema_review_record.json`
* `phase6_schema/schema_owner_approval.json` [post-implementation]

Implementation Notes:

* identity와 semantics를 분리한다.
* 단일 `item_subtype`에 모든 의미를 과적재하지 않는다.
* 검토 축은 direct consumption, beverage/solid form, preparation requirement, culinary role, intermediate/prepared state, preservation form, ingredient origin, meal/snack/component role다. 이 목록 자체는 승인 vocabulary가 아니다.
* 각 token은 exact meaning, allowed/forbidden combinations, required evidence, automatic eligibility, curated requirement, licensed/forbidden propositions를 정의한다.
* fact representation은 structured assertion을 사용하고 vocabulary 밖 free text를 값으로 허용하지 않는다.
* multi-role food는 한 개의 강제 class가 아니라 승인된 orthogonal assertions로 표현할 수 있다.
* 104와 4는 token 생성 입력이 아니다.
* `unknown`, `generic`, `other` bucket을 completion shortcut으로 두지 않는다.
* positive fixture의 family 이름은 test shape일 뿐 승인 vocabulary나 owner token을 선점하지 않는다. `seasoning`, `condiment`, `prepared dish` 같은 예시는 schema approval 전에는 비권위 placeholder다.
* `schema_satisfiability_report.json`은 각 축·값에 대해 automatic-eligible projection과 curation-required projection을 분리해 제공한다. 이 pre-Phase 7 projection이 D7 cap의 유일한 workload 정보 기반이다.
* `schema_expressible_meaningful_profile_count`는 reportable diagnostic이며 값이 4 이상인지 여부는 Change 6 exit나 feasibility kernel을 통과시키지 않는다. Downstream minimum partition은 D10 승인 뒤 Change 12 actual consumer 결과만 판정한다.

Implementation Validation:

```text
closed_vocabulary = true
field_definition_complete = true
combination_rules_complete = true
proposition_licensing_complete = true
ambiguous_token_count = 0
threshold_driven_token_count = 0
schema_has_meaningful_distinctions = true
schema_combination_rules_satisfiable = true
schema_threshold_driven_token_count = 0
schema_expressible_meaningful_profile_count_recorded = true
schema_expressible_meaningful_profile_count_kernel_gate_credit = 0
free_text_escape_count = 0
unknown_token_count = 0
schema_satisfiability_automatic_curation_projection_complete = true
schema_owner_approval_consumed_during_implementation = false
```

Post-Implementation Authority Validation:

```text
schema_owner_approval = present
approved_schema_sha256 = implementation_proposed_schema_sha256
approved_proposition_license_sha256 = implementation_proposed_proposition_license_sha256
```

Implementation은 exact schema/licensing proposal, fixtures, satisfiability report와 approval input bundle을 봉인한다.

---

### Change 7 — Signal-to-Fact Mapping and Automatic Coverage

Purpose:

재현 가능한 signal 중 어떤 것이 어떤 semantic fact를 정당하게 license할 수 있는지 mapping proposal, validator와 dry-run coverage를 구현한다. Mapping 승인은 implementation completion 뒤 owner semantic approval이 수행한다.

Files:

* `Iris/_docs/authority/food_semantic/signal_to_fact_mappings.json`
* `phase7_automatic_mapping/automatic_food_fact_ledger.jsonl`
* `phase7_automatic_mapping/automatic_coverage_report.json`
* `phase7_automatic_mapping/partial_resolution_report.json`
* `phase7_automatic_mapping/curation_required_queue.jsonl`
* `phase7_automatic_mapping/automatic_conflict_report.json`
* `phase7_automatic_mapping/residual_set_reason_codes.json`
* `phase7_automatic_mapping/curation_feasibility_report.json`
* `phase7_automatic_mapping/feasibility_kernel_bundle.json`

Implementation Notes:

각 mapping은 다음을 가진다.

```text
mapping_id
input_signal
required_source_lineage
output_fact_axis/value
preconditions
conflict_conditions
non_claims
mapping_version
approval_status
```

Implementation은 Phase 7 잔여 dry-run 결과를 산출하기 전에 proposed cap을 봉인한다. `schema_satisfiability_report.json`의 bound identity만을 정보 기반으로 소비하며, `automatic_coverage_report.json`, `partial_resolution_report.json`, `curation_required_queue.jsonl`, `residual_set_reason_codes.json`, `curation_feasibility_report.json`을 포함한 Phase 7 결과는 proposed cap 선택 또는 상향의 입력이 될 수 없다. D7 owner decision은 implementation completion 뒤 exact proposed cap을 승인 또는 거절한다.

Signal absence는 negative fact가 아니다. Generated tag 이름과 semantic token이 비슷해도 mapping approval 없이 치환하지 않는다. Layer 4 signal은 automatic input으로 등록하지 않는다.

Phase 7 dry-run은 proposed item cap과 proposition cap을 서로 다른 denominator로 비교한다. Post-implementation authority execution은 D7에서 승인된 동일 cap을 사용한다. Multi-role item의 여러 orthogonal assertions 때문에 두 cap을 모두 봉인하며 하나를 다른 하나로 대체하지 않는다.

```text
predicted_required_curation_items
<= proposed_curation_item_cap

predicted_required_curation_propositions
<= proposed_curation_proposition_cap
```

Feasibility report는 item count, proposition count, average propositions per item, maximum propositions per item, axis distribution을 포함한다. 어느 한 proposed cap이라도 초과하거나 R3/schema/mapping/routing kernel predicate가 실패하면 `feasibility_kernel_state=BLOCKED`를 봉인하고 Change 8~13 구현을 시작하지 않는다. 이 결과는 implementation-complete bundle이 아니라 원인과 재시작 조건을 보존한 feasibility-kernel bundle이다. 이 attempt에서 cap을 재결정하거나 상향하지 않는다. Schema/mapping 수정 또는 cap 변경은 새 attempt를 요구한다. Unsupported fact, generic bucket, implicit bulk approval로 계속 진행하지 않는다.

Implementation Validation:

```text
mapping_proposal_schema_valid = true
mapping_approval_consumed_during_implementation = false
authority_mapping_execution_count_during_implementation = 0
absence_as_negative_fact_count = 0
layer4_automatic_promotion_count = 0
automatic_lineage_missing_count = 0
invented_proposition_count = 0
unresolved_conflict_without_disposition = 0
predicted_required_curation_items <= proposed_curation_item_cap
predicted_required_curation_propositions <= proposed_curation_proposition_cap
curation_item_cap_unit_bound = true
curation_proposition_cap_unit_bound = true
curation_cap_basis_schema_satisfiability_sha256_bound = true
curation_cap_sealed_before_phase7_result = true
curation_feasibility_report_dimensions_complete = true
feasibility_kernel_state = PASS
changes_8_through_13_allowed = true
```

Post-Implementation Authority Validation:

```text
D7_owner_cap_decision = accepted_exact_proposal
approved_mapping_only = true
unapproved_mapping_execution_count = 0
authority_curation_item_cap = proposed_curation_item_cap
authority_curation_proposition_cap = proposed_curation_proposition_cap
```

---

### Change 8 — Curated Food Facts Authority

Purpose:

automatic evidence로 닫히지 않은 대상을 위한 curation workflow, exact packets, ledger schema와 validators를 구현한다. Explicit human approval과 curated authority 성립은 implementation completion 뒤에 수행하며 automatic provenance로 세탁하지 않는다.

Files:

* `docs/dvf_3_3_food_semantic_authority_policy.md`
* `Iris/_docs/authority/food_semantic/curation_policy.json`
* unapproved curation proposal packets and owner-input packet schema [implementation]
* owner-input approved curation packets [post-implementation]
* `phase8_curation/curated_fact_ledger.jsonl` [post-implementation authority execution]
* `phase8_curation/semantic_authority_approval_ledger.jsonl` [post-implementation]
* `phase8_curation/curation_work_queue.jsonl`
* `phase8_curation/curation_batch_manifest.jsonl`
* `phase8_curation/curation_event_ledger.jsonl`
* `phase8_curation/curation_checkpoint.json`
* `phase8_curation/curation_rework_queue.jsonl`
* `phase8_curation/curation_completion_report.json`
* `phase8_curation/automatic_curated_reconciliation_report.json`
* `phase8_curation/curation_consistency_report.json`

Implementation Notes:

각 curated proposition은 item identity, axis/value, `authority_class=curated`, curator identity, reviewed source set, rationale, schema identity, approval record, semantic approver, approval state를 가진다.

Implementation은 D5~D8의 모든 허용 option을 disabled-by-default로 지원하고 unapproved curation packets를 생성한다. Post-implementation owner decision 뒤 선택된 option만 authority execution에 사용한다. Layer 4 review context가 허용돼도 automatic lineage로 기록하지 않는다. Bulk/batch 허용 시 각 member의 exact fact/value와 rationale applicability를 machine-expanded member ledger로 남기며 anonymous or implicit approval을 금지한다.

Curator는 current facts를 편집하지 않는다. schema vocabulary에 없는 값은 schema amendment route로 돌린다.

`curation_work_queue.jsonl`은 case-sensitive FullType, axis, proposition ID 순 canonical ordering을 사용한다. 각 batch ID는 schema SHA-256, queue SHA-256과 exact ordered member set의 digest로 결정하며 batch size나 member set이 바뀌면 새 batch ID를 발급한다. Batch 승인 UI나 packet은 묶음 표시를 허용하더라도 authority ledger에는 모든 member의 exact value, rationale applicability와 approval event를 개별 row로 확장한다.

`curation_event_ledger.jsonl`은 `queued`, `review_started`, `accepted`, `rejected`, `needs_rework`, `superseded` event를 append-only로 기록한다. Rejected 또는 out-of-schema proposition은 삭제하거나 완료로 세지 않고 `curation_rework_queue.jsonl`로 이동한다. `curation_checkpoint.json`은 마지막 fully committed batch ID, event-ledger SHA-256, accepted/rejected/rework counts와 next canonical cursor를 결속한다.

Resume은 checkpoint 이전 batch를 재적용하지 않고 next canonical cursor에서 시작한다. 동일 packet을 반복 제출해도 proposition/approval event가 중복되지 않아야 하며 crash-before-commit과 crash-after-ledger-before-checkpoint fixtures를 모두 통과해야 한다. Checkpoint나 ledger hash가 맞지 않으면 자동 복구나 skip 없이 fail-loud로 중단한다.

Change 8 workflow implementation은 owner decision을 요구하지 않지만 `feasibility_kernel_state=PASS`를 반드시 소비한다. Kernel BLOCKED 상태에서 curation workflow 구현을 계속해 실패를 뒤로 미루지 않는다. Change 8 authority execution은 D5~D8 승인과 Change 7의 approved-cap predicate가 모두 PASS일 때만 허용한다. Curated approval missing/invalid detector는 최소 하나의 missing approver, missing rationale, out-of-schema value fixture를 nonzero로 탐지한 뒤 approved curated ledger에서 0을 보고해야 한다.

Post-Implementation Authority Validation:

```text
curated_approval_missing_count = 0
curated_schema_violation_count = 0
automatic_curated_conflict_count = 0
unsupported_fact_count = 0
authority_class_separation = true
curation_policy_conformance = true
curation_item_cap_respected = true
curation_proposition_cap_respected = true
curated_approval_negative_fixture_hit_count > 0
curation_rework_unresolved_count = 0
curation_duplicate_approval_event_count = 0
curation_checkpoint_hash_match = true
```

위 block은 post-implementation authority execution validation이다. Implementation completion은 대신 다음을 요구한다.

```text
curation_workflow_option_implementations_complete = true
unapproved_curation_packet_generation_complete = true
curated_approval_detector_fixture_pass = true
curation_batch_exact_member_expansion_fixture_pass = true
curation_resume_idempotence_fixture_pass = true
curation_crash_boundary_fixtures_pass = true
curation_rejection_rework_fixture_pass = true
curated_authority_emitted_during_implementation_count = 0
```

---

### Change 9 — Full 317 Coverage and Unsupported-Fact Zero Closure

Purpose:

317건 전부가 automatic 또는 curated authority로 terminal disposition되며 blocked, unsupported, arbitrary inference가 0임을 증명한다.

Implementation build는 coverage/reconciliation/zero detectors와 fixtures를 완성하고 unapproved dry-run corpus에 실행한다. `317/317 semantic disposition complete`와 authority PASS는 post-implementation owner approval을 소비한 authority execution에서만 주장한다.

Files:

* `phase9_coverage/full_317_semantic_disposition.jsonl`
* `phase9_coverage/coverage_reconciliation_report.json`
* `phase9_coverage/unsupported_fact_zero_report.json`
* `phase9_coverage/arbitrary_inference_zero_report.json`
* `phase9_coverage/forbidden_inference_registry_binding.json`
* `phase9_coverage/layer4_non_promotion_report.json`
* `phase9_coverage/singleton_disposition_closure.json`
* `phase9_coverage/semantic_consistency_report.json`
* detector-positive negative fixture reports

Implementation Notes:

* automatic/curated double count를 금지한다.
* `Base.Lemongrass` singleton을 별도 disposition한다.
* D8에 따른 automatic-row review denominator를 적용한다.
* zero detector는 최소 하나의 fixture violation을 nonzero로 탐지한 뒤 clean corpus에서 0을 보고해야 한다.
* `arbitrary_inference_count`는 Change 3의 forbidden field/operation registry에 결속하고 registry의 각 금지 항목을 detector-positive fixture로 검증한다.
* 317 completion을 2,105 universe completion으로 확대하지 않는다.

Post-Implementation Authority Validation:

```text
target_semantic_disposition_count = 317
blocked_count = 0
double_count = 0
coverage_gap = 0
unsupported_fact_count = 0
arbitrary_inference_count = 0
forbidden_inference_registry_bound = true
layer4_auto_promotion_count = 0
per_item_disposition_missing = 0
```

위 block은 post-implementation authority execution validation이다. Implementation completion은 `phase9_validator_implementation_complete = true`, `detector_positive_fixtures_pass = true`, `authority_coverage_claim_emitted_count = 0`을 요구한다.

---

### Change 10 — Attempt-Local Candidate Facts Generation

Purpose:

승인된 automatic/curated ledgers와 schema만 소비하여 target 317행만 의미적으로 달라지는 successor facts candidate와 candidate manifest를 결정론적으로 생성한다.

Implementation build는 writer, input/sink guards, deterministic fixtures와 non-authoritative dry-run을 완성한다. Approved ledgers를 소비하는 claim-bearing candidate invocation은 post-implementation owner approval과 authority execution gate 이후에만 수행한다.

Files:

* standalone authority tool
* `phase10_candidate/writer_attempt_manifest.json`
* `phase10_candidate/candidate_successor_facts.jsonl`
* `phase10_candidate/candidate_successor_input_manifest.json`
* `phase10_candidate/candidate_diff_report.json`
* `phase10_candidate/candidate_determinism_report.json`
* `phase10_candidate/candidate_lineage_bundle.jsonl`
* `phase10_candidate/candidate_validation_report.json`

Implementation Notes:

* current facts 2,105 row order와 exact key set을 보존한다.
* non-target denominator는 `current exact universe count - exact target set count`로 execution-time census에서 유도한다. `1,788`을 writer 또는 validator literal로 고정하지 않는다.
* 모든 non-target row는 raw line bytes가 byte-identical해야 한다. 재직렬화가 불가피하면 canonical equality로 자동 fallback하지 않고 owner-reviewed blocker로 남긴다.
* target 행에는 approved structured food semantic assertions와 authority references만 추가/갱신한다.
* existing approved proposition을 삭제하거나 modality/qualifier를 강화하지 않는다.
* candidate manifest는 predecessor/current hash, schema, Rule, allowlist, mapping, curated ledger, lineage, candidate facts identity를 결속한다.
* 동일 input identity로 두 isolated output root에서 생성한 candidate bytes와 ledgers가 같아야 한다.
* 실패 attempt를 overwrite하지 않는다.

Post-Implementation Authority Validation:

```text
writer_current_sink_count = 0
writer_unapproved_fact_count = 0
non_target_row_change_count = 0
non_target_row_byte_mismatch_count = 0
non_target_denominator_derived_from_bound_sets = true
candidate_same_input_same_output = true
candidate_lineage_coverage = 100%
failed_attempt_overwrite_count = 0
candidate_current_identity_confusion = 0
```

Implementation completion은 `candidate_writer_implementation_complete = true`, `non_authoritative_dry_run = PASS`, `authority_bearing_candidate_emitted_during_implementation_count = 0`을 별도로 요구한다. 위 candidate authority predicate는 post-implementation authorized invocation이 소유한다.

---

### Change 11 — Successor Facts Handling and Adoption Boundary

Purpose:

Post-implementation owner semantic approval과 external review를 마친 authority-bearing candidate를 sealed non-current successor로 봉인하고, future Registry operational-cutover가 소비할 exact request를 만든다. Semantic approval과 Registry promotion을 분리하며 이 round에서는 current promotion을 실행하지 않는다.

Files:

공통:

* `phase11_successor/pre_successor_review.json`
* `phase11_successor/successor_authorization.json`
* `phase11_successor/candidate_to_successor_identity_manifest.json`
* `phase11_successor/successor_facts_identity_report.json`
* `phase11_successor/successor_manifest_identity_report.json`
* `phase11_successor/selected_successor_input_binding.json`
* `phase11_successor/predecessor_disposition_report.json`
* `phase11_successor/protected_surface_hashes_after.json`
* `phase11_successor/declared_divergence_report.json`
* `phase11_successor/freshness_impact_report.json`

Future Registry Branch A proposal only:

* `phase11_successor/registry_cutover_request.json`
* `phase11_successor/registry_candidate_diff_manifest.json`
* atomic promotion/rollback negative fixtures

In-round Branch B:

* sealed successor facts/manifest under attempt root
* `phase11_successor/sealed_successor_receipt.json`

Implementation Notes:

Branch A current promotion은 이 계획의 실행 범위가 아니다. Implementation은 Registry-owned operational-cutover 계획이 검토할 candidate diff, atomicity contract와 negative fixture proposal까지만 만들 수 있다. `registry_adoption_receipt.json`은 이 round가 생성하지 않으며 D9/D12 또는 owner approval만으로 current writer 권한을 만들 수 없다. Partial promotion, dual current, predecessor fallback, candidate direct runtime consumption, rendered regeneration, Lua/runtime/package mutation을 금지한다.

Future Registry cutover request의 divergence report는 최소한 다음을 기록한다.

```text
current successor facts identity
current successor input manifest identity
unchanged rendered/runtime payload가 참조하는 predecessor facts identity
affected row count
allowed divergence scope
resolution owner and scope
required-validation freshness impact
```

이는 promotion이 수행될 경우 생길 current source와 unchanged rendered/runtime 사이의 예상 authority-chain divergence다. 이 round에서는 live divergence를 만들지 않으며 선언만으로 freshness나 downstream closure가 복원됐다고 주장하지 않는다.

Branch B는 current를 변경하지 않고 successor identity, non-current status, candidate와 current 사이의 non-current divergence 및 freshness impact를 명시한다.

D12 correction-only contract proposal을 Registry cutover request에 포함한다. D12는 이 plan에 존재하지 않는 Phase 11 promotion을 gate하지 않으며, request가 future Registry plan으로 전달되기 전에 correction owner/route를 결속하는 데만 사용한다. 실제 promotion과 correction successor 운용은 별도 Registry-owned operational-cutover 계획이 소유하며 predecessor restoration은 허용하지 않는다.

`selected_successor_input_binding.json`은 selected branch, successor facts SHA-256, successor input-manifest SHA-256, approved food-semantic schema SHA-256, approved proposition-licensing contract SHA-256을 봉인하며 Change 12가 소비할 유일한 input identity다.

Future Registry promotion 뒤 defect가 발견됐을 때 필요한 `current_authority_defect_declared` schema proposal은 다음 최소 필드를 가진다. 이 plan의 terminal state로 발행하지 않는다.

```text
defect identity
affected rows and propositions
defect discovery evidence
correction successor unavailable reason
current source/rendered divergence update
required gate status
owner-scoped correction round route
```

실제 Registry cutover에서 이 state가 발생하면 `canonical_complete`, `adopted_but_required_gate_deferred`, `sealed_successor_handoff_complete`를 모두 금지한다. In-round Branch B에는 적용하지 않는다.

Post-Implementation Authority Validation:

공통:

```text
candidate_semantic_review = PASS
authorization = present
dual_current = 0
current_identity_ambiguity = 0
rendered_lua_runtime_package_change = 0
undeclared_divergence_count = 0
freshness_impact_declared = true
selected_successor_facts_sha256_bound = true
selected_successor_manifest_sha256_bound = true
selected_successor_schema_sha256_bound = true
selected_successor_proposition_license_sha256_bound = true
```

Future Registry Branch A proposal:

```text
registry_cutover_request_complete = true
registry_candidate_diff_manifest_bound = true
atomic_promotion_fixture_pass = true
current_facts_mutation_count = 0
current_manifest_mutation_count = 0
registry_adoption_receipt_emitted_count = 0
```

In-round Branch B:

```text
predecessor_hash_unchanged = true
successor_identity_sealed = true
non_current_candidate_divergence_declared = true
current_adoption = false
```

---

### Change 12 — Naturalization Phase 2 Handoff and Semantic Partition Validation

Purpose:

실제 Naturalization Phase 2 consumer가 승인된 structured facts와 proposition licensing을 소비하며 compiler invention 없이 meaningful partition을 형성할 수 있는지 no-render/isolated mode에서 검증한다.

Files:

* bounded Naturalization runner/validator/test files from Section 5
* `Iris/_docs/authority/food_semantic/food_semantic_proposition_inventory.schema.json`
* `phase12_phase2_handoff/phase2_handoff_contract.json`
* `phase12_phase2_handoff/frozen_proposition_interface_fixture.jsonl`
* `phase12_phase2_handoff/naturalization_candidate_patch_manifest.json`
* `phase12_phase2_handoff/actual_phase2_consumed_input_receipt.json`
* `phase12_phase2_handoff/consumed_input_identity_report.json`
* `phase12_phase2_handoff/phase2_handoff_acceptance_report.json`
* `phase12_phase2_handoff/semantic_partition_report.json`
* `phase12_phase2_handoff/skeleton_group_report.json`
* `phase12_phase2_handoff/proposition_consumption_report.json`
* `phase12_phase2_handoff/forbidden_dispersion_report.json`
* `phase12_phase2_handoff/naturalization_tooling_authorization_binding.json`
* `phase12_phase2_handoff/attempt_0014_baseline_reproduction_report.json`
* `phase12_phase2_handoff/existing_phase4_to_8_no_impact_report.json`
* `phase12_phase2_handoff/meaningful_partition_definition.json`
* `phase12_phase2_handoff/meaningless_partition_detector_fixture_report.json`
* `phase12_phase2_handoff/threshold_authority_binding.json`
* `phase12_phase2_handoff/no_relaxation_attestation.json`
* `phase12_phase2_handoff/downstream_resume_packet.json`

Implementation Notes:

* Implementation build는 Naturalization tooling 변경 후보와 adapter/no-render fixtures를 isolated patch로 완성할 수 있지만 current tooling에 채택하거나 Change 12 authority PASS를 주장하지 않는다.
* Implementation completion 뒤 D16 owner authorization이 없으면 candidate tooling을 채택하거나 authoritative Change 12를 실행하지 않는다. D16이 거부되면 `naturalization_consumer_handoff_state=blocked_d16_not_authorized`로 닫고 다른 consumer나 approximate harness로 우회하지 않는다.
* `dvf_3_3_food_semantic/naturalization_handoff.py`는 implementation 중 current Naturalization runner/validator를 import하거나 호출하지 않는다. Frozen proposition interface와 saved baseline fixtures만 소비해 adapter payload, exact affected-symbol manifest와 candidate patch를 생성한다.
* Frozen proposition record는 최소 `item_id`, `proposition_id`, `fact_axis`, `fact_value`, `authority_class`, `source_or_approval_lineage_id`, `schema_sha256`, `proposition_license_sha256`를 가진다. Field 추가는 additive schema revision만 허용하며 기존 field 의미를 바꾸지 않는다.
* Candidate patch manifest는 변경할 exact symbol, preimage SHA-256, replacement SHA-256와 금지 symbol set을 봉인한다. D16 뒤 적용 시 manifest 밖의 symbol 또는 preimage mismatch가 하나라도 있으면 patch를 거부한다.
* acceptance harness를 별도 근사 구현하지 않고 actual Phase 2 source proposition inventory path를 사용한다.
* Actual Phase 2 consumer는 open/read가 성공한 exact facts, manifest, schema, proposition-license path/hash와 `explicit_non_current_input_override`, `current_facts_read_count`를 `actual_phase2_consumed_input_receipt.json`에 직접 기록한다. `consumed_input_identity_report.json`은 이 receipt와 Change 11 selected binding을 비교하는 파생 report이며 receipt 없이 자체 선언으로 PASS를 만들 수 없다.
* adapter는 facts row의 approved structured assertions와 bound proposition-licensing contract만 읽는다.
* schema token 자체를 문장으로 추측하지 않는다.
* current rendered output이나 Naturalization candidate를 쓰지 않는 explicit `no-render`/isolated output mode를 사용한다.
* item ID/hash/random/order/synonym-only dispersion을 금지한다.
* failure routing은 schema omission, mapping loss, curation omission, consumer projection loss 순으로 수행한다.
* 기존 `attempt-0014-remediation`의 450/133/317 cause-analysis baseline을 변경 전/후 동일 입력으로 재현하거나, 변경 symbol이 그 baseline path에 영향을 주지 않는다는 call-graph/fixture proof를 남긴다.
* existing Phase 4~8 runner modes와 validator semantics는 frozen fixtures에서 behavior change 0을 증명한다.
* meaningful partition은 승인 schema axis/value 조합에 대응하고, 서로 다른 partition 사이에 최소 하나의 licensed proposition 차이가 있을 때만 성립한다.
* sort order, file position, row index, output path와 기타 비의미 key로 만든 partition은 detector-positive negative fixture에서 nonzero를 내야 한다.
* Phase 12는 Change 11 `selected_successor_input_binding.json`의 exact identities만 소비한다. 이 round는 Branch B sealed non-current successor만 explicit override로 읽는다. Future Registry cutover 뒤의 adopted current successor 검증은 새 Naturalization attempt가 별도로 수행한다.
* Branch B에서는 `explicit_non_current_input_override=true`, `current_facts_read_count=0`이어야 하며 predecessor/다른 candidate를 주입한 fixture가 nonzero로 실패해야 한다.
* 이 계획 안에서는 Branch B만 실행 가능하므로 Phase 12는 compatibility no-render probe로만 닫힌다. `official_naturalization_retry_allowed=false`, `naturalization_phase4_to_8_execution_count=0`이어야 한다.
* Future Registry cutover가 successor facts/manifest를 current로 채택한 뒤에는 이 attempt의 Phase 12 결과를 official retry로 재사용하지 않는다. 새 Naturalization attempt를 Phase 0부터 열고, Registry adoption receipt와 current successor identity를 결속한 뒤 Phase 2 source inventory를 새로 봉인한다.
* Naturalization reciprocal consumer 계약은 `docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md`의 `dvf3_3_food_semantic_facts_authority__naturalization_phase2_sync_v1`과 execution-time byte-equivalent projection이어야 한다.
* detector와 threshold는 변경하지 않는다. Threshold binding은 policy path/hash/ratio/resolved value와 actual detector path/hash/resolved ratio/value를 각각 기록한다. Detector가 policy를 직접 소비하면 `detector_value_source=bound_policy`도 기록한다.
* policy/detector가 불일치하면 `policy_lag`, `detector_lag`, `genuine_fork` 중 정확히 하나로 분류한다. Canonical identity reconciliation 전에는 Change 12 PASS를 주장하지 않으며 plan literal을 fallback authority로 사용하지 않는다.

Post-Implementation Authority Validation:

```text
phase2_handoff_schema_compatible = true
actual_phase2_consumed_input_receipt_present = true
actual_phase2_consumed_input_receipt_producer = naturalization_actual_phase2_consumer
actual_phase2_consumed_input_receipt_sha256_bound = true
phase2_consumed_facts_sha256 = selected_successor_facts_sha256
phase2_consumed_manifest_sha256 = selected_successor_manifest_sha256
phase2_consumed_schema_sha256 = approved_food_semantic_schema_sha256
phase2_consumed_proposition_license_sha256 = approved_proposition_licensing_contract_sha256
phase2_required_fact_missing_count = 0
compiler_invented_proposition_count = 0
id_hash_random_partition_count = 0
meaningless_partition_count = 0
meaningless_partition_negative_fixture_hit_count > 0
D10_owner_partition_criterion = accepted_exact_proposal
minimum_meaningful_partition >= 4
threshold_source_identity_bound = true
threshold_source_value_unchanged = true
threshold_policy_detector_identity_match = true
threshold_authority_unclassified_mismatch_count = 0
detector_modification_count = 0
waiver_added_count = 0
maximum_same_skeleton_group <= bound_threshold_value
attempt_0014_baseline_reproduced = true
  또는 changed_path_has_no_effect_on_attempt_0014 = proven
existing_phase4_to_8_behavior_change_count = 0
naturalization_candidate_promoted = false
publish_boundary_retried = false
official_naturalization_retry_allowed = false
naturalization_phase4_to_8_execution_count = 0
reciprocal_naturalization_contract_match = true
frozen_proposition_interface_schema_match = true
candidate_patch_out_of_scope_symbol_count = 0
candidate_patch_preimage_mismatch_count = 0
```

Branch B additional validation:

```text
explicit_non_current_input_override = true
current_facts_read_count = 0
wrong_predecessor_input_fixture_hit > 0
wrong_candidate_input_fixture_hit > 0
```

Implementation은 partition dry-run 결과 전에 `proposed_minimum_meaningful_partition >= 4` criterion을 봉인한다. 이 proposal과 `schema_expressible_meaningful_profile_count` diagnostic은 feasibility kernel gate credit이 0이다. D10은 implementation completion 뒤 exact proposal을 승인 또는 거절하며 동일 attempt에서 criterion을 바꿀 수 없다. 승인된 경우에만 approved facts와 actual Phase 2 consumer 결과를 대상으로 authority execution에서 `minimum_meaningful_partition >= 4`를 검사한다. 관찰된 bound threshold가 현재 readpoint에서 104일 수 있지만 authority는 threshold binding artifact가 소유한다.

---

### Change 13 — Required Gate Candidate, Independent Closeout and Owner Seal

Purpose:

Implementation-complete bundle에 대한 owner semantic/adoption approval과 post-implementation external implementation review가 PASS하고 authority execution이 sealed non-current successor를 만든 뒤, D11의 in-round G2와 future G1 proposal, D1/D13/D15를 적용해 final machine evidence, terminal independent closeout review, owner seal, terminal hash를 서로 대체 불가능한 순서로 봉인한다. Live required-gate adoption은 실행하지 않고 Registry cutover request에 포함한다.

Files:

* `docs/dvf_3_3_food_semantic_claim_boundary.md`
* `phase13_closeout/final_machine_report.json`
* `phase13_closeout/final_artifact_manifest.json`
* `phase13_closeout/independent_reviewer_eligibility_report.json`
* `phase13_closeout/independent_closeout_review.json`
* `phase13_closeout/owner_seal.json`
* `phase13_closeout/terminal_branch_disposition.json`
* `phase13_closeout/final_claim_non_claim_vocabulary_scan.json`
* `phase13_closeout/sealed_successor_closeout.json` [B + G2 only]
* `phase13_closeout/terminal_hash_seal.json`
* required gate contract/adoption candidate and Registry request [future G1]
* required gate deferred/freshness impact record [G2]
* `phase13_closeout/required_artifact_vcs_disposition.json` [G1]
* approved top-doc additive updates [D15]

Implementation Notes:

* Future G1 candidate는 food semantic required artifacts/tests의 additive manifest diff만 제안한다. Existing entries를 제거/수정하거나 live manifest를 변경하지 않으며 duplicate test/artifact row를 금지한다.
* Future G1 required test proposal은 new writer를 current build closure에 import하는 우회면이 되지 않아야 한다.
* Future G1의 각 required artifact proposal은 exact targeted negative exception만 사용할 수 있다. 실제 tracking/unignore/adoption은 Registry cutover 계획이 검토한다. Broad staging unignore는 금지한다.
* G2는 adopted source authority의 required manifest/freshness reseal을 별도 Registry scope로 남기므로 canonical completion을 주장할 수 없다.
* Branch B는 current authority를 바꾸지 않는 sealed successor handoff다. Live required-gate adoption도 Registry-owned current mutation이므로 이 round에서는 G2 explicit deferral과 exact cutover request만 허용한다.
* final claim/non-claim vocabulary scan은 Change 1의 `live_non_claim_enumeration.json` path/hash, exact canonical member set, count를 입력으로 결속한다. Live manifest non-claim 전건의 scan disposition이 없거나 forbidden claim emission이 하나라도 있으면 closeout은 FAIL이다.
* Post-implementation external implementation review와 terminal independent closeout review는 별도 artifact/token이다. External reviewer는 implementation author가 아니고 reviewed implementation-complete bundle hash가 일치해야 하지만, 그 PASS의 terminal independent gate credit은 0이다.
* independent reviewer eligibility를 machine-check한 뒤 review를 수행한다.
* 이 계획의 원 검토자와 종합 검토 참여자는 terminal independent reviewer로 부적격하다. Eligibility report는 requirements/plan/review/implementation/owner 체인에 참여하지 않은 reviewer만 허용한다.
* Terminal independent review는 `sealed_successor_handoff_complete=true`와 final artifact manifest가 봉인되기 전에는 시작할 수 없다.
* Terminal reviewer bundle은 reviewed repository commit, 이 plan repo-relative path, plan Git blob ID, Appendix A marker/version, normative requirements snapshot SHA-256/line count를 포함한다. Reviewer는 machine-local attachment 없이 repository artifact만으로 requirements scope를 재계산해야 하며 불일치나 missing blob은 eligibility가 아니라 review input failure로 닫는다.
* owner seal은 review PASS와 exact final artifact manifest hash를 소비한다.
* top-doc이 바뀌면 영향 검증을 다시 실행하고 그 결과를 terminal seal에 포함한다.
* terminal seal 뒤 claim-bearing artifact가 바뀌면 기존 seal을 수정하지 않고 새 correction attempt를 연다.

Post-Implementation Authority Validation:

```text
implementation_complete_bundle_sha256_bound = true
post_implementation_owner_decisions_complete = true
post_implementation_semantic_approval = PASS
post_implementation_external_review = PASS
post_implementation_external_reviewer_is_implementation_author = false
post_implementation_external_reviewed_bundle_sha256_match = true
post_implementation_external_review_terminal_gate_credit = 0
sealed_successor_handoff_complete = true
final_machine_validation = PASS
final_non_claim_scan_input_sha256 = change1_live_non_claim_enumeration_sha256
final_non_claim_scan_denominator_identity_match = true
missing_live_non_claim_scan_disposition_count = 0
forbidden_non_claim_emission_count = 0
independent_reviewer_eligible = true
independent_reviewer_requirements_snapshot_retrievable = true
independent_reviewer_requirements_snapshot_hash_match = true
independent_review = PASS
owner_seal = PASS
terminal_hash_binding = PASS
post_terminal_claim_bearing_change = 0
```

Future Registry G1 proposal only:

```text
required_gate_candidate_complete = true
required_gate_adoption_request_complete = true
live_required_manifest_mutation_count = 0
```

In-round G2:

```text
required_gate_deferred_explicitly = true
freshness_impact_declared = true
```

이 plan의 허용 terminal state:

```text
B + G2
-> food_semantic_facts_authority_closeout = sealed_successor_handoff_complete
-> current_authority_reconstruction_complete = false
-> canonical_complete = forbidden

future A + G1
-> separate Registry-owned operational-cutover plan required
-> no terminal state emitted by this plan
```

---

## 7. Validation Plan

Validation depth는 `heavy`다. Authority Surface와 Sealed Artifact Surface를 직접 다루기 때문이다.

### Automated Validation

#### Planned focused commands

Implementation build에서 standalone implementation/test가 존재하고 tracked/visible한 상태에서 다음을 실행한다. 이 command는 owner decision이나 external review를 소비하지 않는다.

```powershell
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_food_semantic_*.py"
```

다음 두 command는 post-implementation D16 approval로 exact candidate patch가 채택된 뒤 실행한다. Implementation completion을 차단하지 않는다.

```powershell
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_korean_prose_acceptance_gate.py"
```

```powershell
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_korean_prose_semantic_preservation.py"
```

G1인 경우 final tracked/config/doc 변경 뒤 live current route를 실행한다.

```powershell
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --out Iris/build/description/v2/staging/dvf_3_3_food_semantic_facts_authority/attempts/<attempt-id>/phase13_closeout/current_route_validation_result.json
```

Post-implementation authorized 변경과 branch action 뒤 최종 repository regression은 다음 exact command가 exit 0일 때만 authority closeout PASS로 기록한다.

```powershell
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py"
```

#### Implementation completion machine checks

* repo-relative normative requirements snapshot tracked Git blob, marker/version, SHA-256/logical-line-count와 plan/predecessor binding
* exact 317 census와 protected baseline
* Change 0~7 feasibility kernel PASS와 R3 sole-executable-route proof
* D1/D5~D16 option matrix, D2/D3/D4 retired-mandatory records, proposed artifacts와 disabled-by-default option implementations
* Rule route, allowlist, lineage, writer, schema, mapping, curation, coverage, candidate, adoption, Phase 2, closeout tooling implementation
* thin CLI/private phase-module ownership과 declared-artifact-only dependency 검사
* schema/mapping/cap/denominator/partition proposals와 pre-result seal
* detector-positive fixtures, curation batch/resume/rework/crash fixtures와 non-authoritative dry runs
* current facts/manifest, rendered/Lua/runtime/package protected hashes unchanged
* `owner_decision_consumed_count = 0`
* `owner_approval_consumed_count = 0`
* `external_review_consumed_count = 0`
* `authority_claim_emitted_count = 0`
* `implementation_complete_bundle_sealed = true`

#### Post-implementation authority and closeout machine checks

* JSON/JSONL schema와 exact-key parse
* Change 0 requirements/plan traceability, implementation entry/exit binding, Change 1 evidence-baseline predicate separation
* Change 0에서 검증한 normative requirements snapshot과 predecessor/successor plan path/hash/logical-line-count binding
* Naturalization/Registry counterpart plan read-only fresh hash와 mutation count 0
* predecessor temporary overwrite/restore episode와 recovery-source ceiling preservation
* strict open Critical/Important 0, OPEN Important owner-waiver rejection
* approved Rule route R3 고정과 R1/R2 authority execution 0
* source, target, Rule, allowlist, schema, mapping, approval, candidate hash binding
* Naturalization target 317과 facts target 317 exact member-set identity
* Rule order/input permutation determinism
* intermediate signal provenance와 final fact proposition-level lineage completeness
* required-validation denominator role/delta reconciliation
* automatic/curated authority class separation
* item/proposition curation cap 양축과 curated-approval detector-positive fixtures
* candidate two-root byte determinism
* non-target byte-identical parity와 derived denominator
* hard-forbidden writer sink rejection before write
* failed attempt write-once preservation
* detector-positive negative fixtures
* Layer 4 automatic promotion 0
* display-only inference 0
* item-ID/hash/random dispersion 0
* Branch B non-current identity/divergence와 future Registry cutover proposal completeness
* future Registry post-promotion defect-state schema proposal
* rendered/Lua/runtime/package protected hashes unchanged
* actual Naturalization Phase 2 path를 사용한 no-render compatibility acceptance
* Phase 11 selected successor와 Phase 12 consumed facts/manifest/schema/license SHA equality
* attempt-0014 baseline reproduction 또는 no-effect proof
* existing Naturalization Phase 4~8 behavior-change 0
* threshold policy/detector identity match, mismatch classification과 no-relaxation attestation
* meaningful partition definition과 detector-positive non-semantic fixtures
* future G1 required-artifact candidate diff와 live manifest no-mutation proof
* Change 1에서 봉인한 live manifest non-claim exact enumeration을 입력으로 소비하는 final claim/non-claim vocabulary scan
* D3/D4 retired mandatory record와 planning-readpoint 33 non-claims의 claim-ceiling role preservation
* independent reviewer eligibility
* terminal hash seal

#### Positive fixtures

아래 family 이름은 test shape이며 승인 schema vocabulary나 owner token이 아니다.

* directly edible fruit
* raw cooking ingredient
* animal-origin raw ingredient
* plant-origin raw ingredient
* seasoning
* condiment
* beverage
* prepared dish
* meal component
* dough/intermediate product
* frozen, dried, canned/preserved food
* multi-role food
* `Base.LemonGrass`/`Base.Lemongrass` exact identity pair

#### Negative fixtures

* untracked/missing normative requirements plan blob 또는 Appendix snapshot hash mismatch
* Naturalization/Registry counterpart contract missing, hash drift 또는 plan mutation
* DisplayName/Description/DisplayCategory-only inference
* Layer 4 direct promotion
* unregistered/unversioned Rule
* R1/R2 diagnostic output의 authority execution 또는 fallback 사용
* allowlist identity mismatch
* missing source locator or approval
* missing/invalid curated approver, rationale or schema value
* free-text schema value
* absence-as-negative fact
* item ID/hash/random partition
* sort order/file position/row index/output path partition
* same-attempt overwrite
* feasibility kernel FAIL 뒤 Change 8~13 시작 또는 implementation-complete 주장
* feasibility kernel PASS를 semantic schema approval로 확대
* thin CLI business-logic duplication 또는 sibling private-module import
* duplicate curation packet replay
* checkpoint/event-ledger hash mismatch
* rejected curation proposition의 rework queue 누락
* current writer sink
* non-target mutation
* dual current
* predecessor fallback [A]
* undeclared divergence [A/B]
* Phase 12 predecessor/wrong-candidate input [B]
* actual Phase 2 consumed-input receipt missing 또는 self-declared comparison report only
* Naturalization candidate patch의 out-of-scope symbol 또는 preimage mismatch
* threshold policy/detector mismatch without disposition
* item-cap PASS/proposition-cap FAIL 및 그 역방향
* unrecoverable current-authority defect를 success state로 분류
* OPEN Important owner-waiver
* predecessor restore episode omission 또는 commit/blob source overclaim
* required-gate row replacement/removal [G1]
* tooling allowlist convenience expansion

### Manual Validation

아래 semantic/adoption manual validation과 post-implementation owner decision·approval은 `implementation_complete_bundle_sealed = true` 뒤에 수행한다. Post-implementation external implementation review는 owner가 exact bundle을 승인한 뒤 수행하고, terminal independent closeout review는 authority execution이 sealed non-current successor와 final artifact manifest를 봉인한 뒤 수행한다. §0.5의 requirements owner ratification과 fresh pre-implementation plan review는 별도의 planning-stage implementation entry gate다.

* owner review of schema exact meanings, examples, counterexamples, combination rules and proposition licensing
* D7 pre-result-sealed proposed item/proposition cap과 predicted workload distribution의 accept/reject review
* row-level or owner-approved bounded-batch curated review according to D5~D8
* automatic/curated conflict adjudication
* implementation dry-run 결과 전에 봉인된 D8 proposed exact denominator 전체에 대한 target semantic consistency review와 accept/reject
* Branch B successor status와 future Registry cutover request/divergence review
* independent reviewer eligibility and closeout review
* owner review of final claim token and non-claims

Manual review는 machine validation을 대신하지 않으며 machine PASS도 semantic approval을 대신하지 않는다.

### Validation Limits

이번 execution에서 검증하지 않는다.

* feasibility kernel PASS의 semantic schema owner approval
* Naturalization Phase 4~8
* 최종 Korean prose 품질
* Publish Boundary PASS
* Browser / Tooltip / Wiki 표시
* runtime Lua behavior
* runtime payload compatibility 재종결
* package publication
* release / Workshop / B42 / deployment readiness
* manual in-game QA
* multiplayer
* external mod compatibility
* 전체 food ontology의 영구 완전성

계획 작성 시 관찰된 `104`는 Phase 2 handoff threshold의 current readpoint 값일 뿐이다. Acceptance는 canonical policy/detector identity에서 파생한 `bound_threshold_value`와 비교하며 public text acceptance가 아니다.

---

## 8. Risk Surface Touch

### Authority Surface

중대한 변경 있음.

* Classification / Rule authority
* Evidence Allowlist authority
* lineage authority
* food semantic schema/proposition authority
* automatic mapping authority
* curated facts authority
* scoped writer authority
* successor facts source authority
* D16이 허용하는 범위에서의 Naturalization consumer tooling owner authority
* threshold policy/detector reconciliation authority
* item/proposition curation-cap authority

Semantic value approval은 Food Semantic Facts Authority, artifact lifecycle은 Iris Artifact Registry, body generation은 DVF Body Compiler, public acceptance는 Publish Boundary가 소유한다.

### Runtime Behavior Surface

직접 변경 없음.

Runtime Lua, renderer, Browser, Tooltip, Wiki, chunks, package를 변경하지 않는다. Current source facts/manifest도 이 plan에서는 변경하지 않는다.

### Compatibility Surface

source-consumer compatibility 영향 있음.

* structured successor facts와 Naturalization Phase 2
* proposition licensing과 source proposition inventory
* existing attempt-0014 baseline validator semantics
* existing Naturalization Phase 4~8 behavior
* candidate/current manifest schema
* exact 317 identity와 existing 2,105 universe
* selected Phase 11 successor와 exact Phase 12 consumed input

Registry Runtime Compatibility closure는 다시 열지 않는다.

### Sealed Artifact Surface

additive sealed successor와 future Registry current-mutation proposal이 있다. 이 plan 자체의 current mutation은 없다.

Predecessor facts, currently restored predecessor plan, normative requirements snapshot, generated tags, allowlist versions, failed attempts, Registry evidence를 재작성하지 않는다. Historical source attachment는 protected execution input이 아니다. Predecessor plan의 temporary overwrite/restore episode도 additive evidence로 보존한다. Branch B는 predecessor bytes를 유지하고 non-current divergence를 선언한다. Future Registry cutover request는 예상 divergence와 required adoption receipt schema만 제안한다.

### Public-Facing Output Surface

직접 변경 없음.

Public body, Tooltip, Browser, Wiki, package, release claim을 변경하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

* Classification, semantic approval, Registry promotion, DVF consumption, Publish acceptance가 하나의 PASS로 합쳐질 수 있다.
* missing Rule을 이름만 같은 새 코드로 복구하고 historical equivalence를 과대 주장할 수 있다.
* Registry가 semantic adjudication을 흡수하거나 DVF compiler가 source inference를 수행할 수 있다.
* Layer 4 interaction evidence가 automatic Layer 3 fact로 승격될 수 있다.
* schema token이 104 상한을 맞추기 위한 taxonomy로 설계될 수 있다.
* current core/tooling closure를 새 writer가 우회할 수 있다.
* cross-axis Naturalization tooling이 owner authorization 없이 변경될 수 있다.
* OPEN Important가 owner risk acceptance만으로 post-implementation authority gate를 통과할 수 있다.
* Change 0 entry가 자기 exit predicate를 요구할 수 있다.
* feasibility kernel 실패 뒤 후속 tooling을 계속 구현해 실패 원인을 뒤로 미룰 수 있다.

완화:

* authority class와 owner를 artifact마다 명시
* R1/R2 diagnostic-only disposition, R3 sole-executable-route와 equivalence non-claim
* closed schema + proposition licensing
* candidate-only writer와 current sink 0
* actual Phase 2 no-render consumer projection
* 12+1 비확장 및 subprocess/read-only gate
* D16 tooling owner/symbol scope와 attempt-0014/Phase 4~8 no-impact proof
* G-A strict blocker-zero authority gate와 requirements materialization/entry presence/Change 0 exit-binding predicate 분리
* Changes 0~7 kernel PASS가 Changes 8~13과 implementation-complete bundle의 mandatory dominator

### Runtime Risk

* future Registry current facts 변경이 후행 compose/export 도구에 예상치 못한 영향을 줄 수 있다.
* future current source와 unchanged rendered/runtime 사이 divergence가 숨겨질 수 있다.
* future Registry cutover가 no-render acceptance 범위를 넘어 runtime regeneration으로 확장될 수 있다.
* future promoted authority defect에 correction successor가 없어 current defect가 고착될 수 있다.

완화:

* 이 plan은 Branch B만 실행하고 Branch A는 separate Registry plan으로 격리
* rendered/Lua/runtime/package hash no-mutation gate
* Branch B non-current divergence와 future Registry cutover 예상 divergence/freshness impact report
* Naturalization Phase 2 isolated output only
* runtime/package command를 plan allowlist에 포함하지 않음
* `current_authority_defect_declared` fail-loud state와 owner-scoped correction routing

### Compatibility Risk

* structured facts schema를 기존 consumer가 무시할 수 있다.
* case-insensitive tooling이 exact FullType 두 개를 병합할 수 있다.
* new manifest fields가 existing validators와 충돌할 수 있다.
* proposition licensing adapter가 facts보다 넓은 의미를 생성할 수 있다.
* Naturalization validator 변경이 predecessor baseline 또는 Phase 4~8 behavior를 바꿀 수 있다.
* Phase 12가 selected successor가 아닌 predecessor/다른 candidate를 읽을 수 있다.
* threshold policy와 detector-resolved value가 갈라질 수 있다.
* moving Naturalization runner private API에 adapter가 직접 결합할 수 있다.

완화:

* actual consumer adapter와 focused tests
* canonical Python/jq exact-key handling
* additive manifest extension과 existing-field preservation
* proposition-by-proposition lineage/licensing
* case-variant fixture
* D16 authorization, baseline reproduction/no-effect proof, frozen Phase 4~8 fixtures
* selected-successor/consumed-input four-hash equality와 wrong-input fixtures
* threshold policy/detector path/hash/value equality와 mismatch classification
* frozen proposition interface, no-current-import adapter module과 exact candidate-patch symbol manifest

### Regression Risk

* target 317 밖 row의 byte mutation
* existing approved proposition deletion/strengthening
* old generated tags에 invented lineage 부여
* automatic/curated conflict 숨김
* curation fatigue와 batch overreach
* failure artifact overwrite
* current required manifest의 existing entry 수정/삭제
* top-doc 변경 후 affected validation 미실행
* denominator role substitution 또는 unexplained historical/current delta
* threshold literal drift, detector 변경 또는 waiver 추가
* curation cap 초과 뒤 implicit/generic fallback
* item cap과 proposition cap 단위 혼용
* predecessor overwrite/restore episode 누락 또는 recovery source 과대 주장

완화:

* non-target byte-identical mandatory parity
* before/after proposition diff
* old artifact diagnostic-only disposition
* per-item terminal ledger
* D5~D8 curation policy
* write-once attempt root
* additive-only G1 diff
* final mutation 뒤 validation rerun과 terminal seal
* denominator reconciliation, threshold binding/no-relaxation, Phase 7 feasibility gate
* item/proposition dual-cap validation과 overwrite/restore episode validator
* canonical curation batch membership, append-only event ledger, hash-bound checkpoint, idempotent resume와 rejection/rework closure

---

## 10. Rollback Plan

### Before Current Mutation

Implementation build 전체는 Change 11~13 tooling facets를 포함해 attempt-local 또는 durable additive proposal/contract만 생성하며 current facts/manifest를 변경하지 않는다. Post-implementation Branch B authority execution도 current를 변경하지 않는다.

실패 시:

```text
terminal FAIL 보존
candidate 비채택
current facts/manifest 유지
새 attempt identity에서 correction
```

실패 artifact를 삭제하거나 같은 attempt의 PASS로 교체하지 않는다.

Change 0~7 feasibility kernel이 BLOCKED이면 Change 8~13 directory를 만들거나 placeholder PASS를 기록하지 않는다. `feasibility_kernel_bundle.json`과 completed phase outputs만 보존하고, schema/mapping/cap 또는 R3 Rule을 수정한 새 attempt를 Change 0부터 연다. BLOCKED kernel을 implementation-complete bundle로 승격하거나 owner approval로 우회하지 않는다.

Kernel PASS 뒤 implementation-complete bundle이 생성됐더라도 owner가 schema proposal을 거절하면 bundle과 Changes 6~13 outputs를 `rejected_postimplementation_schema` evidence로 보존한다. Changes 6~13 artifact를 같은 attempt에서 고치거나 승인 상태로 바꾸지 않으며, 새 attempt가 Change 0부터 prerequisite identities를 재검증한 뒤 affected outputs를 재생성한다.

### Future Registry Atomic Adoption Failure Contract

별도 Registry operational-cutover 계획은 허용 상태를 다음 둘로 제한해야 한다.

```text
predecessor current intact
또는
successor current fully adopted
```

Partial current 또는 dual current가 보이면 adoption을 FAIL로 닫고 protected hash/receipt로 실제 상태를 판정한다.

### Future Registry Post-Promotion Defect

Future successful current adoption 뒤에는 predecessor restoration을 허용하지 않는다. Registry operational-cutover 계획이 지정한 owner와 route에서 다음 correction-only 절차만 사용한다.

```text
new correction attempt
-> corrected candidate
-> affected-row and full required revalidation
-> new correction successor adoption
```

Predecessor current reentry는 0이어야 한다. 기존 sealed decision/attempt와 failed successor는 historical evidence로 보존한다.

Correction successor를 즉시 생산할 수 없으면 rollback이나 predecessor restoration을 가장하지 않고 다음 state로 fail-loud 전환한다.

```text
food_semantic_facts_authority_closeout = current_authority_defect_declared
current_authority_defect_record = present
required_gate_status = recorded
current_source_rendered_divergence = updated
owner_scoped_correction_round = routed
predecessor_current_reentry = 0
```

이 state는 success terminal state가 아니며 correction successor가 새 attempt에서 채택되고 전체 required validation을 다시 통과하기 전까지 유지한다.

### Branch B Defect

Successor가 current가 아니면 adoption하지 않는 것으로 rollback한다.

```text
successor artifact 보존
handoff status superseded
current authority 유지
새 successor attempt에서 correction
```

### Downstream Acceptance Failure

104 상한 또는 meaningful partition validation 실패는 evidence 삭제 사유가 아니다.

허용 routing:

* schema omission review
* mapping loss review
* curation omission review
* consumer projection loss review
* round open 유지

금지 routing:

* threshold/detector 완화
* waiver 추가
* item ID/hash/random 분산
* unsupported fact 삭제로 수치 맞춤

### Required Gate / Top-Doc Rollback

Future G1/D15 candidate는 owner seal 전 supersede할 수 있다. 이 plan은 live required manifest나 `.gitignore`를 변경하지 않는다. Registry cutover 계획이 채택한 sealed entry는 삭제하지 않고 additive correction으로 대체하며 broad unignore로 rollback하지 않는다.

---

## 11. Governance Constraints

* `Philosophy.md` compliance
* Iris는 근거 기반 위키이며 해석·권장·비교를 생성하지 않는다.
* Runtime Lua는 표시만 담당한다.
* Recipe와 Right-click은 동급 Source지만 Layer 4 interaction information은 automatic food semantic facts authority가 아니다.
* Automatic classification은 allowlisted declaration을 누적하는 indexing이며 자유 의미 추론기가 아니다.
* DVF System / DVF Body Compiler 책임은 approved facts/decisions/profile/body_plan에서 rendered body를 만드는 데 한정한다.
* Iris Artifact Registry는 semantic value를 판정하지 않는다.
* Publish Boundary는 facts writer가 아니다.
* current source, rendered, Lua, runtime, package authority를 혼합하지 않는다.
* bare `DVF PASS`와 bare `DVF System PASS`를 사용하지 않는다.
* `Registry Authority PASS`, `Registry Runtime Compatibility PASS`, `DVF Body Compiler PASS`, `Publish Boundary PASS`, Legacy Combined route PASS는 서로 대체하지 않는다.
* candidate-first, exact-subset-bound, no-direct-current-edit
* additive historical preservation
* failure laundering 금지
* count equality를 identity equality로 대체하지 않음
* exact Naturalization/facts 317 set binding 의무
* final automatic fact proposition-level lineage 의무
* provenance 없는 generated tags 승격 금지
* DisplayName/Description/DisplayCategory inference 금지
* Layer 4 automatic promotion 금지
* item ID/hash/random/synonym-only dispersion 금지
* closed vocabulary와 schema amendment governance
* automatic/curated authority class 분리
* `Philosophy.md` 적용 경계: 증거가 부족한 semantic 축은 침묵하고, 반복적으로 필요한 예외만 bounded curated manual override로 봉인한다. Curated authority는 모든 미확정 축이나 317건 전체를 채우는 포괄 waiver가 아니다.
* implementation build entry는 pre-implementation plan review PASS만 소비함
* implementation entry/progress/completion은 owner decision·approval, post-implementation external review 또는 terminal independent review를 소비하지 않음
* implementation-complete bundle 전에는 authority claim, owner decision consumption, current facts/manifest mutation을 모두 금지
* owner decision과 semantic approval은 implementation completion 뒤, external implementation review는 exact approved bundle 뒤, terminal independent review와 owner final seal은 sealed successor 뒤 별도 authority/closeout stage에서만 수행
* semantic approval, Registry promotion, independent review, owner seal 분리
* current core 12개와 tooling allowlist 1개를 편의상 확대하지 않음
* protected current/rendered/Lua/runtime/package no-mutation
* top-doc update는 owner-approved additive 범위에서만 수행
* validation exit 0 없이 PASS 주장 금지
* validation ceiling과 non-claims 명시
* cross-axis Naturalization tooling은 D16 owner authorization과 bounded symbol scope 안에서만 변경
* current source/rendered divergence를 branch별로 선언하고 freshness impact를 숨기지 않음
* successful promotion 이후 predecessor current restoration 금지
* threshold authority는 canonical policy/detector binding이 소유하며 detector/waiver 완화 금지
* current required artifact는 tracked/not-ignored여야 하며 broad staging unignore 금지
* OPEN Critical/Important finding은 owner risk acceptance만으로 post-implementation authority execution gate를 통과할 수 없음
* requirements/plan traceability, implementation bootstrap presence, Change 0 binding verification, Change 1 evidence/baseline binding을 서로 다른 predicate로 유지
* selected Phase 11 successor와 Phase 12 consumed facts/manifest/schema/license exact identity 일치
* item/proposition curation cap을 서로 대체하지 않음
* predecessor overwrite/restore episode와 non-durable recovery-source ceiling을 삭제하거나 세탁하지 않음
* `current_authority_defect_declared`를 success terminal state로 확대하지 않음

---

## 12. Expected Closeout State

### Plan State

이 문서의 작성 상태는 `food_semantic_facts_authority_plan_state=cross_plan_synchronized_proposed / separate_roadmap_required=false / preimplementation_plan_review_required=true / implementation_entry_owner_approval_required=false / implementation_entry_blocked=true / post_implementation_owner_approval_required=true / post_implementation_re_review_required=true`다.

다음을 의미한다.

```text
design requirements translated to path-level successor plan
separate roadmap artifact not required
normative requirements snapshot embedded; repository tracking/adoption pending
predecessor draft currently restored at exact identity; temporary overwrite/restore episode disclosed
Cycle 1 review findings R-1 through R-21 reflected
Cycle 2 review findings I-1 through I-7 and M-1 through M-6 reflected
Cycle 3 review findings P-1 through P-6 reflected
Cycle 4 synthesis findings C-1, I-1 through I-6 and M-1 through M-2 reflected
Cycle 5 synthesis findings I-1 through I-3 and M-1 through M-3 plus S-1 follow-up reflected
Facts/Naturalization Phase 2 reciprocal contract synchronized
Facts/Registry boundary synchronized without mutating the reviewed Registry plan
Publish Boundary direct synchronization not required
requirements artifact owner ratification recorded
fresh pre-implementation plan review pending against the ratified exact plan blob
codebase gaps reflected
R3 fixed as sole executable Rule authority route; R1/R2 diagnostic only
Changes 0-7 feasibility kernel gates Changes 8-13 implementation
curation batch/checkpoint/rework contract defined
Naturalization frozen proposition interface and isolated candidate patch boundary defined
post-implementation owner option matrix exposed
phase dependencies defined
validation and rollback defined
implementation not started
current facts unchanged
naturalization not resumed
Publish Boundary not retried
```

### Implementation Target

Pre-implementation plan review PASS 뒤에만 Implementation은 다음 상태까지 진행한다. Implementation entry·progress·completion에서 owner decision·approval과 external/independent review의 consumed count는 모두 0이어야 한다.

Change 0~7 kernel이 BLOCKED이면 다음 상태에서 멈추며 아래 full implementation target을 주장하지 않는다.

```text
food_semantic_facts_authority_implementation_state = blocked_feasibility_kernel
feasibility_kernel_bundle_sealed = true
changes_8_through_13_started = false
implementation_complete_bundle_sealed = false
owner_decision_consumed_count = 0
owner_approval_consumed_count = 0
external_review_consumed_count = 0
```

Kernel PASS일 때만 full implementation target은 다음이다.

```text
mechanical requirements/plan/predecessor binding complete
exact 317 and protected baseline bound
all D1/D5-D16 option implementations, D2/D3/D4 retired records and proposal artifacts complete
Rule/allowlist/lineage/writer/schema/mapping/curation/coverage tooling complete
candidate, adoption, Phase 2 and closeout tooling complete
machine fixtures PASS; non-authoritative dry-run reports complete
proposal_technical_feasibility = PASS
proposal_structural_feasibility = PASS
business_feasibility_claimed = false
implementation-complete review bundle sealed
semantic owner decision consumed count = 0
postimplementation owner approval consumed count = 0
postimplementation external review consumed count = 0
authority claim emitted count = 0
current facts/manifest mutation count = 0
```

Implementation-complete bundle이 봉인된 뒤에만 다음 순서를 시작한다.

```text
owner decisions and semantic approvals required to bind the review target
-> post-implementation external implementation review
-> remaining D1/D9/D11/D15 branch, action and claim decisions
-> authorized authority execution and candidate generation
-> Branch B sealed successor action and future Registry cutover request
-> terminal independent closeout review
-> owner final seal
-> terminal hash seal
```

Owner는 동일 implementation attempt의 exact proposal을 승인 또는 거절한다. Option, cap, criterion, denominator, schema 또는 mapping을 변경하면 기존 bundle은 거절 상태로 보존하고 새 implementation attempt를 생성한다. D2/D3/D4는 owner option이 아니라 mandatory contract다. Claim은 D1에서 승인한 axis-qualified token에만 한정한다.

### Post-Implementation Authority Target

공통 evidence conditions:

```text
Rule authority resolved
Allowlist identity aligned
final automatic fact proposition lineage complete
food semantic schema approved
automatic mapping approved
curated authority disposition complete
317/317 semantic disposition complete
unsupported/arbitrary inference 0
scoped writer sealed
successor facts/manifest sealed
minimum meaningful partition >= 4 under D10-approved downstream criterion
Phase 12 consumed facts/manifest/schema/license identities equal selected Phase 11 successor binding
Naturalization Phase 2 no-render compatibility handoff PASS
official Naturalization retry deferred until Registry adoption
threshold policy/detector identity match
maximum same-skeleton group <= bound threshold from canonical policy/detector
attempt-0014 baseline reproduced or no-effect proven
existing Phase 4-8 behavior change 0
independent review PASS
owner seal PASS
terminal hash seal PASS
```

이 plan의 terminal state는 Branch B sealed successor handoff로 제한한다. Branch A와 G1/G2 조합은 future Registry operational-cutover 계획의 상태이며 이 plan이 발행하지 않는다.

```text
B + G2
-> food_semantic_facts_authority_closeout = sealed_successor_handoff_complete
-> current_authority_reconstruction_complete = false
-> canonical_complete = false

future Registry cutover
-> separate reviewed operational-cutover plan required
-> this plan emits no Registry adoption or current-authority terminal claim
```

Normative requirements artifact가 tracked reviewed Git blob이 아니면 implementation build state는 `blocked_requirements_artifact_not_durable`다. 그 조건은 충족했지만 pre-implementation plan review PASS가 없으면 `blocked_preimplementation_review`다. Implementation-complete bundle 뒤 필요한 semantic/adoption owner decision·approval이나 post-implementation review가 없으면 `food_semantic_facts_authority_authority_execution_state=blocked_pending_owner_or_review`를 사용한다. Bare `complete` token은 사용하지 않는다.

### Final Non-Claims

성공하더라도 다음을 선언하지 않는다.

* DVF Body Compiler PASS
* DVF System Body Compiler PASS
* Registry Authority PASS 재달성
* Registry Runtime Compatibility PASS
* Publish Boundary PASS
* Naturalization Phase 4~8 completion
* public text acceptance
* semantic quality acceptance
* Korean prose quality completion
* runtime equivalence 또는 runtime payload compatibility
* Lua bridge/runtime chunk/package mutation completion
* package/release/Workshop/B42/deployment readiness
* manual in-game QA
* external mod semantic support
* 전체 Iris food ontology 완성

`maximum_same_skeleton_group <= bound_threshold_value`는 승인된 새 semantic facts가 Naturalization Phase 2 consumer projection에서 canonical detector/policy의 동일 골격 수용 기준을 만족할 수 있음을 뜻할 뿐이다. 계획 작성 시 관찰된 104는 reportable readpoint value이지 별도 authority가 아니다.

---

## Appendix A — Normative Design Requirements Snapshot

이 appendix는 implementation entry와 terminal independent review가 공통으로 재검증하는 repository-retrievable 최상위 requirements artifact다. 아래 marker 내부의 UTF-8 text만 hash scope이며 marker line은 제외한다. CRLF/CR은 LF로 정규화하고 exactly one terminal LF를 부여한 bytes의 SHA-256과 logical line count를 header에 기록한다. Historical attachment의 live 존재는 요구하지 않는다.

<!-- BEGIN NORMATIVE DESIGN REQUIREMENTS SNAPSHOT v1 -->
```text
problem_status = formally_defined
problem_class = upstream_authority_and_semantic_data_debt
implementation_ready_at_plan_authoring = false

target_universe = exact case-sensitive 317 food FullType members
current_authorized_semantic_condition_count = 1
current_largest_authorized_partition = 317
downstream_observed_same-skeleton_limit = canonical policy/detector binding

objective:
reconstruct Classification/Rule, Evidence Allowlist, row/proposition lineage,
closed food semantic schema, curated facts authority, candidate-only writer,
sealed non-current successor facts/manifest and Naturalization Phase 2 handoff
without inventing facts or mutating current authority in this round.

required authority outcomes:
R3 official successor is the sole executable Rule route.
R3-only route origin is the planning-chain D2 retirement disposition;
R1 and R2 remain diagnostic-only and owner ratification binds this provenance.
Evidence Allowlist document heading, document history and machine-contract identities
are reconciled to one canonical version before authority execution.
Allowed source fields and operations are machine-readable and version-bound.
Every automatic proposition has source/rule/allowlist/mapping lineage.
Every curated proposition has explicit reviewed value, rationale and approval.
All 317 members receive automatic or curated terminal semantic disposition.
Unsupported fact, arbitrary inference and Layer 4 automatic promotion counts are zero.
Non-target facts rows remain byte-identical.
Successor facts and successor input manifest are distinct from predecessor/current.
Naturalization Phase 2 consumes the selected successor facts, manifest, schema
and proposition-license exact identities through a no-render compatibility probe.
Approved facts form meaningful semantic partitions in the actual Phase 2 consumer,
and no same-skeleton group exceeds the canonical policy/detector bound.
Minimum partition and same-skeleton values are downstream validation only;
they do not create schema tokens or gate upstream schema feasibility.

implementation constraints:
Owner decisions, approvals and external/independent reviews are not consumed
during implementation entry, progress or completion.
Changes 0-7 feasibility kernel must PASS before Changes 8-13 start.
Kernel PASS is mechanical/structural feasibility only and is not semantic approval.
Current facts, current input manifest, required-validation manifest, rendered output,
Lua, runtime chunks, package payload and predecessor sealed evidence are not mutated.
Failed or blocked attempts are append-only evidence and are never rewritten as PASS.
No item ID, hash, random, row order or synonym-only semantic dispersion is allowed.
No detector, threshold or waiver relaxation is allowed.

scope boundary:
This round may seal a non-current successor and future Registry cutover request.
This round does not perform Registry promotion or current facts adoption.
This round does not run an official Naturalization retry or Naturalization Phase 4-8.
This round does not retry Publish Boundary or change runtime/package behavior.
Maximum in-round terminal state is sealed_successor_handoff_complete.
canonical_complete and current_authority_reconstruction_complete are forbidden claims.

owner workflow directive:
A separate roadmap artifact is not required and must not gate implementation.
This repository-relative appendix plus the successor plan is the durable requirements surface.
Owner semantic/adoption decisions begin only after implementation-complete bundle sealing.
```
<!-- END NORMATIVE DESIGN REQUIREMENTS SNAPSHOT v1 -->
