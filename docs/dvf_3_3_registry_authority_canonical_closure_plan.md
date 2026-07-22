# Implementation Plan

> Status: implementation-authorized / retry-semantics-corrected / cycle-id-attempt-id-separated / write-once-attempt-evidence / failure-laundering-prohibited / entry-deadlock-removed / protected-denominator-and-freshness-closed / external-review-source-recomputed / fixed-review-path-allowlist / candidate-specific-D6-required / real-current-write-disabled / attempt-0005-review-required / execution-blocked-before-WP
> 작성일: 2026-07-10
> Round candidate: dvf_3_3_registry_authority_canonical_closure
> Roadmap input: C:/Users/MW/.codex/attachments/8d0d9746-0c56-482c-a7ed-e5aca9fedebf/pasted-text.txt / consumed_roadmap_hash=sha256:17C41198E4D35A15743FD6C9F869CA545C5363A3A32EB005DB1E94BC16530ECD / 1482 lines
> Roadmap canonical authority: owner-approved repo-local payload / sha256:17C41198E4D35A15743FD6C9F869CA545C5363A3A32EB005DB1E94BC16530ECD
> Phase 3 attempt-0001 reviewed bundle: sha256:908862D0E58D9B96FA9F77B01F0204A2AE4E9C4C2111E1AEFE938EC46A306E8F / verdict FAIL / Critical 1 / Important 3 / superseded but byte-preserved
> Phase 3 attempt-0002 reviewed bundle: sha256:8A77019F38EFA265BA2A34767A53FE3EBCCF85CA28910BECDF86F9617E4D0EF3 / verdict FAIL / Critical 1 / Important 1 / superseded but byte-preserved
> Phase 3 attempt-0003 bundle: sha256:F92DD854BB0785AE581E815B7DEBED1F5426A7578D9842829F443BAA2712D11A / superseded before final review after primary fixed-path audit / byte-preserved
> Phase 3 attempt-0004 bundle: sha256:EBC2A1831A3F10ED295FA9C72D64160F25827AFB8879DFC6B325F65E4665B47D / superseded before final review after retry-semantics correction / byte-preserved
> Execution entry status: blocked until attempt-0005-entry receives fresh external reviews with Critical=0 and Important=0
> Template input: docs/PLAN_TEMPLATE.md / sha256 38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1
> Top authority: docs/Philosophy.md / sha256 938C52E9090C36AF00DAC18B64905E12A4F2390AC238A26121A63A14F81F44B2
> Planning readpoints: docs/DECISIONS.md / sha256 E57C4D3BC21BB2DFA10791E41EF7440358C3DAF66D11AD05A06E8158090C40D3; docs/ARCHITECTURE.md / sha256 8B2CA298EF75FE1C85C7E44B81E6536EE6343E0FC5227F662142398EE1636C89; docs/ROADMAP.md / sha256 9D3A74DA7B54FD6392FD44F5D7A2ED1ABA35CA29AB83D3EB914CD64AAC6C0A12
> Execution obligations: docs/EXECUTION_CONTRACT.md / sha256 A185BBD78EB849B0310D9AADC9102CB156B892513266FAC0EC7903EB3D3A9493
> Direct plan artifact: docs/dvf_3_3_registry_authority_canonical_closure_plan.md
> Cycle evidence root: Iris/build/description/v2/staging/dvf_3_3_registry_authority_canonical_closure/
> Attempt evidence root contract: Iris/build/description/v2/staging/dvf_3_3_registry_authority_canonical_closure/attempts/<attempt_id>/ (write-once; never reused or overwritten)
> Maximum future execution claim: Registry Authority Closure = canonical_complete
> Review boundary: machine PASS, independent review PASS, owner seal, and canonical seal are separate non-substitutable axes
> Execution authorization: 현재 사용자는 이 revised implementation round와 Codex Reviewer 사용을 승인했다. 테스트는 Section 7의 명시된 command boundary에서만 실행한다. candidate-specific required-gate adoption, top-doc 반영, independent review verdict, owner seal, canonical seal은 각각 명시된 외부 입력/검증 경계를 통과해야 한다.

---

## 1. Objective

Legacy Combined DVF Governance Route 아래 분산되어 있는 current authority, artifact role, required-validation, seal/cutover, stale/predecessor guard 증거를 현재 checkout 기준으로 다시 계수·결속하여 Iris Artifact Registry가 소유하는 독립된 Registry Authority Closure readpoint로 봉인하기 위한 실행 계획을 정의한다.

이 계획은 새 Registry 구현 계획이 아니다. 기존 source, rendered, exporter, runtime chunk, package guard, current-route validation, stale guard를 재사용하여 다음 책임 경계를 하나의 검증 가능한 parent closure로 수렴시키는 계획이다.

    DVF System
    = facts / decisions / profile / body_plan
      -> rendered 3-3 body

    Iris Artifact Registry
    = artifact role / lifecycle / authority
      / runtime-package identity pipeline

    Legacy Combined DVF Governance Route
    = historical polluted governance surface

실행이 성공했을 때 허용되는 최대 claim은 다음으로 제한한다.

    Registry Authority Closure
    = canonical_complete

    Registry Authority PASS
    = artifact role classification complete
    + single current identity chain
    + required-validation ownership/freshness complete
    + seal/cutover contract complete
    + stale/predecessor reentry guard complete

이 최대 claim은 DVF Body Compiler PASS, Registry Runtime Compatibility PASS, Runtime Payload Consumer Compatibility closure, Publish Boundary PASS, package publication, release/Workshop/B42/deployment readiness, manual in-game QA 또는 public text acceptance를 뜻하지 않는다.

### Codebase Inspection Summary

계획 작성 시점의 실제 코드베이스에서 확인한 기준은 다음과 같다. 수치는 planning readpoint일 뿐 실행 시 sacred count로 사용하지 않는다.

* Iris/_docs/round3/current_route_required_validations.json은 required=true, enforcement=fail_closed이며 required artifact 112개, required test 52개, non-claim 33개를 담고 있다.
* Iris/_docs/round3/round3_run_contract_tests.py는 taxonomy-selected test와 live required test를 합쳐 실행하고, required artifact 존재 및 field equals/one_of 조건을 fail-closed로 검사한다.
* planning-time taxonomy current 99개와 required test 52개의 distinct union은 131개다. 저장된 131-test PASS는 predecessor evidence이며 새 closure의 final evidence가 아니다.
* Iris/_docs/round3/round3_active_core_closure.json은 current build core 12개를 closure_rows로 보존하고, current-route tooling allowlist는 export_dvf_3_3_lua_bridge 1개만 허용한다.
* Iris/build/description/v2/data/dvf_3_3_input_manifest.json은 facts, decisions, overlay_support 각 2105 row와 current runtime chunk manifest/directory를 successor current source authority로 가리킨다.
* Iris/build/description/v2/output/dvf_3_3_rendered.json, Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua, Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua가 현재 rendered/runtime identity 조사 대상이다.
* Iris/_docs/authority/iris_current_authority_manifest.json은 2026-06-10 Round 1의 coarse classification manifest다. 이 계획에서는 predecessor inventory input으로만 소비하며, Registry closure를 대신하는 fresh census로 간주하지 않는다.
* 기존 required-evidence integrity, freshness, durable-surface, stale-reentry, runtime-payload, boundary-claim tooling과 focused tests가 이미 존재한다. 새 구현은 이를 subprocess/read-only predecessor input으로 재사용하고 동일 기능을 재작성하지 않는다.
* Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py의 기본 route는 staging + chunk이며, current/staging monolith export를 거부하고 chunk bundle validation을 제공한다.
* Iris/build/description/v2/tools/build/manage_dvf_3_3_runtime_chunk_cutover.py는 validate와 copy/delete/replace 기반 snapshot/apply/restore 경로를 제공한다. 이 계획은 read-only --validate-candidate만 사용하고 mutating modes는 열지 않는다.
* Iris/tools/package_iris.ps1은 custom OutputRoot를 지원하고 monolith 및 stale IrisDvfBridgeData.lua를 package에서 fail-loud로 거부한다.
* Iris/media/lua/client/Iris/Data/layer3_renderer.lua는 public runtime require를 Iris/Data/IrisLayer3DataChunks로 유지한다. 이 계획은 이 contract를 변경하지 않는다.
* compose_layer3_text.py의 default/no-explicit-output entrypoint는 compose_context=current와 live rendered output을 자동 선택하지만 Registry authorization/receipt를 검사하지 않으며, imported build_rendered current-path 호출도 같은 인증이 없다. 계약적 금지만으로는 fail-closed가 아니므로 이 계획은 body generation semantics를 보존한 채 shared write-contract/CLI current protected-path guard만 좁게 harden한다. 또한 current context는 일반 staging output class를 거부하므로 WP-3 proof는 compose_context=staging과 exact current-input hash binding을 사용해야 한다.
* planning-time Python scan에는 build_rendered( text match가 106개 있어 광범위한 caller churn 위험이 있다. 따라서 새 receipt parameter는 default=None으로 뒤에 추가하고, resolved target이 실제 CLOSED_CURRENT_PROTECTED_PATHS일 때만 강제한다. 모든 callsite는 inventory하되 ordinary staging/diagnostic caller의 의미나 출력은 바꾸지 않는다.
* 별도 persisted compiler receipt artifact는 현재 없고 rendered.meta가 embedded compiler trace/receipt 역할로 input/entry hashes를 보유한다. 새 Registry sidecar는 compiler semantics를 바꾸는 산출물이 아니며 compiler receipt, Registry seal, authority source로 부르지 않는다.
* dvf_3_3_input_manifest.json의 compose_authority.body_plan_alias와 실제 compose code를 대조한 결과, current body_plan input authority는 별도 7번째 파일이 아니라 compose_profiles_v2.json의 schema_version/section_names/profiles/render_rules에 내재한다. per-entry body_plan instance는 compose_layer3_item.py가 생성하여 rendered entries[*].body_plan에 기록한다. WP-3는 이 Case A를 실행 시 재검증하고 양쪽 hash coverage를 명시한다.
* 일부 predecessor governance tool의 protected path가 존재하지 않는 Iris/Iris/media/... 중복-root를 가리킨다. 새 round는 실제 runtime path 존재를 단언하고 이 predecessor PASS를 runtime no-mutation의 대용물로 쓰지 않는다.
* tracked Iris/_docs/round3/round3_contract_manifest.json은 planning-time JSON parse가 실패하는 current-looking governance artifact다. 현재 reference scan에서는 round3_generate_evidence.py가 producer이고 dvf_3_3_current_source_authority_drift_verification.py의 상수 선언은 실제 read가 없으며 current required route의 live consumer는 확인되지 않았다. WP-2는 diagnostic-only/no-reentry를 proposed disposition으로 재검증한다.
* live required test 중 completion-vocabulary gate test는 gitignored/untracked 877-line tools/build implementation을 sys.path bare-import한다. round3_run_contract_tests.py의 BuildClosureBlocker는 tools.build.* qualified import만 차단하므로 이 경로가 closure를 우회한다. WP-4는 subprocess-only refactor와 narrow runner preflight hardening으로 이 우회를 제거한다.
* 같은 test의 setUpClass는 stored phase9/current-route/fixture reports가 PASS이면 fresh execution을 생략하고, 없으면 machine-pass runner가 current route를 다시 호출하여 동일 test에 INNER_CURRENT_ROUTE 우회를 건다. WP-4는 이 조기 반환/재귀를 제거하고 docs/current-route write가 없는 isolated fixture-check subprocess로 required assertion을 재구성한다.
* 계획이 재사용하는 기존 도구 18개와 adjacent test 12개는 모두 존재하고 tracked/not-ignored다. current input 6개 hash/cardinality, rendered raw hash, runtime 11 chunks, isolated package projection은 predecessor binding과 일치한다. 이는 재사용 가능성 근거이지 final fresh PASS가 아니다.
* 새 round의 tool, test, staging evidence, owner-input path는 현재 .gitignore에 기본적으로 가려진다. Fixture visibility는 실행 시 exact path로 recensus하며 가려졌다고 선결론 내리지 않는다. 실행은 broad unignore가 아니라 필요한 exact path만 보존해야 한다.
* tools/check_lua_syntax.ps1는 Get-Command luac로 외부 실행 파일을 해석하고, luac가 없거나 대상 Lua 파일이 0개이면 exit 2로 실패한다. 따라서 Lua syntax adjacent check의 환경 capability를 Phase 0에서 미리 고정하고, 실행 중 자동 설치하지 않는다.
* planning-time git status에는 modified 99개와 이 plan 1개 untracked가 있으며 required artifact 112개 중 11개와 docs/ARCHITECTURE.md, docs/DECISIONS.md, docs/ROADMAP.md가 dirty다. 세 top-doc diff는 Registry/DVF boundary와 직접 겹친다. 이 계획은 이를 되돌리거나 자기 변경으로 흡수하지 않고, owner-approved commit 기반 전용 clean worktree 전에는 실행하지 않는다.

---

## 2. Scope

이 계획은 roadmap Phase 3의 pre-implementation review부터 Phase 5의 final validation/review/owner seal까지를 실행 가능한 파일·검증 단위로 구체화한다.

포함 범위:

* roadmap/plan provenance, owner-reserved decision register, plan fingerprint, owner-approved implementation-plan hash binding
* pre-existing dirty worktree disposition, bounded Entry-scaffold owner-approved commit, external empty-status checkpoint 기반 전용 execution worktree
* Responsibility Boundary Review
* Authority/Evidence Integrity Review
* Adversarial/Failure-Mode Review
* DVF/Registry handoff contract
* current-checkout Registry-relevant artifact surface census
* artifact role classification
* source -> rendered -> bridge receipt -> runtime chunks -> isolated package projection identity binding
* required-validation ownership, denominator recensus, freshness reseal
* candidate-to-current promotion, seal/cutover, rollback/historical preservation contract
* stale/predecessor/current-looking/package fallback reentry guard
* Registry Authority claim contract와 axis-qualified vocabulary guard
* conditional additive live required-validation gate adoption; implemented_only/partial/blocked에서는 선택 가능하지만 Registry Authority Closure = canonical_complete에는 필수
* focused positive/negative tests
* narrow VCS visibility/preservation updates
* protected source/rendered/Lua bridge/runtime/package no-mutation proof
* final current-checkout rerun, artifact/validation hash binding
* independent closeout review input과 reviewer eligibility 검증
* owner decision/owner seal input 검증
* additive top-doc update draft와 owner-applied sync 검증
* final closeout 및 correction-only reopening rule

### Explicitly Out Of Scope

* DVF Body Compiler 본문 생성 로직 변경
* body_plan semantics 변경
* input facts/decisions/overlay 의미 재판정
* rendered body content 수정 또는 live regeneration
* Lua bridge live export
* runtime chunk 교체
* live package payload 교체
* current route runner 전면 재작성; bare-import closure 우회를 막는 narrow dependency preflight hardening은 포함
* current_route_required_validations.json 물리 분해
* round3 active core 12개 확대
* current-route tooling allowlist를 편의상 확대
* old monolith 또는 stale bridge fallback 복구
* historical/staging/fixture artifact 삭제 또는 대량 rename
* Registry Runtime Compatibility Closure
* runtime consumer 동작/equivalence 보증
* Publish Boundary Closure
* public text/semantic quality acceptance
* package publication 또는 release/Workshop/B42/deployment readiness
* manual in-game QA, multiplayer, long-session runtime validation
* Phase 4 Live Migration Execution
* closed readpoint 재개방
* ACQ_DOMINANT, FUNCTION_NARROW, Layer4, Acquisition Lexical follow-up
* external mod compatibility sweep
* full historical byte reproducibility
* tooling이 owner decision, independent review PASS, owner seal을 생성하는 것

---

## 3. Non-Goals

이 계획은 다음을 시도하지 않는다.

* Legacy Combined DVF Governance Route PASS를 Registry Authority PASS로 재명명하지 않는다.
* DVF output을 Registry adoption 전부터 current artifact로 취급하지 않는다.
* DVF compiler trace/receipt를 Registry seal로 취급하지 않는다.
* Iris Artifact Registry를 DVF System의 내부 하위 구성요소로 만들지 않는다.
* Registry가 3-3 body를 생성하거나 DVF가 current selector/promoter/sealer가 되게 하지 않는다.
* count equality를 authority identity 또는 freshness 증거로 사용하지 않는다.
* stored PASS를 final fresh evidence로 재사용하지 않는다.
* generated staging evidence를 required manifest 채택 없이 durable evidence로 승격하지 않는다.
* tracked 상태를 authority 상태로, ignored 상태를 삭제 가능 상태로 읽지 않는다.
* planning-time 112/52, 2105, 11 등의 관찰값을 실행 시 고정 denominator로 사용하지 않는다.
* current package snapshot 또는 isolated package probe를 package publication/readiness로 읽지 않는다.
* machine PASS, owner approval, owner seal, independent review를 서로 대체하지 않는다.
* 기존 dirty 변경을 자동 정리하거나 baseline으로 조용히 흡수하지 않는다.
* current route failure를 wrapper가 PASS로 보정하거나 재해석하지 않는다.

---

## 4. Assumptions

### Repository and Authority Assumptions

* docs/Philosophy.md가 최상위 authority다.
* docs/DECISIONS.md, docs/ARCHITECTURE.md, docs/ROADMAP.md의 current readpoint와 docs/EXECUTION_CONTRACT.md의 heavy-execution 규율을 따른다.
* Iris runtime은 100% Lua이며, 이 계획의 Python/PowerShell 작업은 offline governance/build validation에 한정한다.
* Runtime/build-time separation과 FAIL-LOUD 원칙을 유지한다.
* current source/rendered/runtime artifact는 계획 시점에 존재하지만, 실행 시작 시 path, hash, cardinality, VCS state를 다시 계산한다.
* current_route_required_validations.json의 planning-time 112/52는 stale-safe observation이다. final denominator는 실행 시 live manifest recensus 결과다.
* iris_current_authority_manifest.json은 coarse predecessor manifest이며, 새 Registry census의 input이지 결과 authority가 아니다.
* existing predecessor reports는 source seed/provenance로만 사용하며, final PASS predicate는 live recensus와 fresh rerun에서만 만든다.
* 새 round tooling은 current build core가 아니다. current route test가 이를 import하지 않도록 focused test는 subprocess boundary를 사용한다.
* bare tools/build import가 BuildClosureBlocker를 우회하는 live evidence가 확인됐으므로 round3_run_contract_tests.py의 narrow pre-execution dependency guard hardening은 이 계획 범위에 포함한다. test selection/result semantics와 active-core/tooling allowlist는 변경하지 않는다.
* live runtime, source, rendered, package source는 read-only protected surface다.
* isolated package probe는 round evidence root 아래로 resolve된 OutputRoot에서만 허용한다. containment check 전에는 -Clean을 실행하지 않는다.
* execution이 top-doc을 직접 편집하려면 pre-existing dirty overlap을 owner가 먼저 disposition하고 additive-only diff guard를 통과해야 한다. 이 계획은 Option B를 채택하여 final top-doc application을 owner seal 뒤 post_external_gate 안에서 수행한다.
* DECISIONS.md의 기존 sealed body는 immutable이며, 새 decision은 owner-authored 또는 owner-ratified append로만 추가한다.
* owner-approved implementation plan은 repo-relative path, raw SHA-256, approved roadmap hash, bounded Entry bootstrap scaffold manifest, clean-worktree checkpoint, execution base commit, approval identity/time을 외부 input과 phase0 materialization에 결속한다. plan/roadmap/checkpoint/base drift와 pre-Entry scaffold drift는 approval을 즉시 stale로 만들며, post-Entry plan-mapped implementation transition은 별도 before/after hash evidence가 필요하다.
* execution은 현재 dirty checkout에서 시작하지 않는다. Owner가 채택한 기존 변경과 이 plan/roadmap 및 bounded Entry scaffold를 포함하는 approved commit을 먼저 지정하고, 그 commit에서 만든 dedicated worktree의 empty-status checkpoint를 승인한다. 현재 checkout의 uncommitted 변경은 자동 stash/reset/commit하지 않는다.
* final closeout은 machine evidence, eligible independent review, owner seal, canonical seal을 별도 축으로 가진다.

### Owner-Reserved Decisions

다음 항목은 이 plan이 제안값을 제공할 수 있지만 owner 결정을 선점하지 않는다.

| ID | Decision | Proposed default | Complete closeout requirement |
|---|---|---|---|
| D0 | Durable approved roadmap payload | docs/dvf_3_3_registry_authority_canonical_closure_roadmap.md materialized from the attached draft | owner-approved repo-local path+hash; approved/consumed hash parity 또는 no-material-effect diff-scope approval |
| D1 | Round identifier | dvf_3_3_registry_authority_canonical_closure | owner_ratified 또는 owner_overridden |
| D2 | Evidence root | cycle root Iris/build/description/v2/staging/dvf_3_3_registry_authority_canonical_closure/ plus registered write-once attempts/<attempt_id>/ | owner_ratified cycle root and exact attempt root |
| D3 | Final vocabulary | Registry Authority Closure / Registry Authority PASS | owner_ratified 또는 owner_overridden |
| D4 | Per-artifact disposition authority | live recensus; malformed round3_contract_manifest.json은 no-live-consumer가 재증명되면 diagnostic-only/no-reentry | ambiguous/unclassified 0, damaged manifest outcome evidence-bound |
| D5 | Independent reviewer designation | pending | eligible reviewer 지정 및 PASS |
| D6 | Required-gate adoption | entry-time mandatory-adoption policy plus post-candidate exact one-use authorization | canonical_complete이면 candidate/base/diff hashes를 결속한 별도 owner authorization 후 adopted and rerun-bound; non-canonical outcome에만 optional |
| D7 | Top-doc application | Option B: owner seal 뒤 post_external_gate에서 additive DECISIONS/ROADMAP/ARCHITECTURE update | owner_applied_and_validated_post_external |
| D8 | Owner/canonical seal | pending external owner input | PASS |
| D9 | Branch/worktree/attempt selection | owner-approved bounded Entry-scaffold commit 기반 dedicated clean worktree and new attempt_id; current dirty checkout execution 금지 | base commit/path/branch/attempt ratified, byte-identical clean checkpoint, initial dirty count 0, predecessor failure records preserved |
| D10 | Implementation plan approval | external owner approval over this repo-local plan path/hash, bounded Entry bootstrap scaffold manifest/hash, clean-checkpoint hash, attempt-registration hash/root, execution base commit, and approved roadmap hash | approved plan/scaffold/checkpoint/attempt/base parity; byte-identical phase0 materialization |

owner decision 상태는 proposed_default, owner_ratified, owner_overridden, missing 중 하나로 기록한다. D0-D10 중 closeout에 필요한 항목이 proposed_default 또는 missing이면 canonical_complete를 주장하지 않는다. Required-gate adoption is optional only for implemented_only, partial, or blocked outcomes. It is mandatory for Registry Authority Closure = canonical_complete.

### Execution Entry Gate

다음 체크리스트가 모두 PASS이고 revised plan의 새 Phase 3 review에서 Critical/Important가 0이 되기 전에는 WP-1을 시작하지 않는다.

* D0 owner-approved repo-local roadmap path/hash present
* D0 approved_payload_hash equals this header's consumed_roadmap_hash, or an owner-authored diff-scope approval proves no material plan effect
* D1 round identifier owner_ratified 또는 owner_overridden
* D2 evidence root owner_ratified 또는 owner_overridden
* D3 final vocabulary owner_ratified 또는 owner_overridden
* D5 eligible independent reviewer designation present
* D6 required-gate adoption policy present; exact candidate authorization은 gate-candidate 이후 별도 외부 input으로만 허용
* D7 Option B post-owner-seal top-doc application policy present
* D8 external owner/canonical seal path reserved
* D9 owner-approved scaffold-bearing base commit/branch, dedicated worktree, and new attempt_id/root selected; byte-identical clean checkpoint records initial dirty count = 0 and attempt registration preserves every predecessor failure record
* D10 external implementation-plan approval present and byte-identically materialized
* D10 approved_plan_hash equals the exact plan bytes being executed and binds the D0 approved roadmap hash plus D9 clean-checkpoint and attempt-registration hashes
* D10 approved bootstrap scaffold manifest/hash equals the bounded Entry scaffold in the execution base. 구현 성공 capability는 preflight와 byte-identical Phase 3 review materialization뿐이고 validator success capability는 require-preflight, require-preimplementation-reviews, require-execution-entry뿐이다. WP, current/protected write, gate adoption, owner/reviewer verdict authoring, machine/final/canonical producer capability는 0이며 post-checkpoint unapproved delta count = 0
* original dirty checkout preserved; execution-worktree dirty protected/required/planned-mutation overlap = 0
* pre-implementation Critical_count = 0
* pre-implementation Important_count = 0
* tools/check_lua_syntax.ps1 exists and its SHA-256 is recorded
* Get-Command luac resolves one executable; resolved path/version/hash and a non-empty intended Lua input set are recorded

D4의 per-artifact disposition은 WP-2 live census 결과에 의존하므로 entry-time 완료값이 아니라 승인된 disposition rule로만 고정한다. round3_contract_manifest.json은 producer-only/unused-constant/no-current-consumer가 모두 재증명될 때에만 diagnostic, current_reentry_allowed=false, package_reentry_allowed=false로 닫는다. 실제 read가 하나라도 나오면 이 default는 무효이며 correction blocker다. 이후 ambiguous/unclassified가 하나라도 남으면 fail-closed한다.

### Closeout State Assumptions

* gate adoption 전 dry-run/tooling 결과는 implementation evidence이며 canonical Registry Authority Closure가 아니다.
* independent review external input은 plan/roadmap/implementation author와 독립된 reviewer identity와 reviewed artifact hashes를 가져야 한다. phase5 copy는 이 외부 입력의 byte-identical, hash-verified materialization이어야 한다.
* roadmap co-draft author인 Claude review는 final independent closeout review로 사용할 수 없다.
* owner seal은 independent review를 대체하지 않는다.
* final execution 후 unvalidated_but_in_scope가 비어 있지 않으면 closeout은 complete가 될 수 없다.

---

## 5. Repository Areas Affected

### Code

Planned new offline governance tooling:

* Iris/build/description/v2/tools/build/dvf_3_3_registry_authority_canonical_closure.py
* Iris/build/description/v2/tools/build/run_dvf_3_3_registry_authority_canonical_closure.py
* Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_authority_canonical_closure.py
* Iris/build/description/v2/tests/test_dvf_3_3_registry_authority_canonical_closure.py
* Iris/build/description/v2/tests/fixtures/dvf_3_3_registry_authority_canonical_closure/

Planned narrow existing guard/dependency edits:

* Iris/build/description/v2/tools/build/compose_layer3_text.py - shared write-contract plus CLI current protected-path authorization guard only; rendering/body_plan semantics unchanged
* Iris/_docs/round3/round3_run_contract_tests.py - pre-load bare-import/dependency preservation guard only; selection/result semantics unchanged
* Iris/build/description/v2/tests/test_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py - remove sys.path bare import and use subprocess-only validation
* Iris/build/description/v2/tools/build/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py
* Iris/build/description/v2/tools/build/run_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py
* Iris/build/description/v2/tools/build/validate_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py
* Iris/build/description/v2/tests/fixtures/negative/completion_vocabulary_external_gate/
* Iris/build/description/v2/tests/fixtures/positive/completion_vocabulary_external_gate/

Read-only or subprocess-reused existing tooling:

* Iris/build/description/v2/tools/build/dvf_3_3_current_route_authority_required_evidence_integrity_closure.py
* Iris/build/description/v2/tools/build/run_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py
* Iris/build/description/v2/tools/build/validate_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py
* Iris/build/description/v2/tools/build/dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py
* Iris/build/description/v2/tools/build/dvf_3_3_required_artifact_surface_preflight_census_common.py
* Iris/build/description/v2/tools/build/dvf_3_3_required_artifact_disposition_seal_common.py
* Iris/build/description/v2/tools/build/dvf_3_3_predecessor_stale_artifact_reentry_guard_common.py
* Iris/build/description/v2/tools/build/run_dvf_3_3_predecessor_stale_artifact_reentry_guard.py
* Iris/build/description/v2/tools/build/validate_dvf_3_3_predecessor_stale_artifact_reentry_guard.py
* Iris/build/description/v2/tools/build/runtime_payload_state_integrity.py
* Iris/build/description/v2/tools/build/runtime_payload_state_integrity_residual_seal.py
* Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py
* Iris/build/description/v2/tools/build/manage_dvf_3_3_runtime_chunk_cutover.py
* Iris/build/description/v2/tools/build/dvf_3_3_core_registry_boundary_claim_contract_closure.py
* Iris/build/description/v2/tools/build/dvf_3_3_core_registry_boundary_required_gate_adoption.py
* Iris/build/description/v2/tools/build/dvf_3_3_dvf_system_naming_realignment.py
* Iris/tools/package_iris.ps1

Protected runtime code/data, read-only:

* Iris/media/lua/client/Iris/Data/layer3_renderer.lua
* Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua
* Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua
* Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua
* Iris/media/lua/client/Iris/Util/IrisModuleBootstrap.lua
* Iris/media/lua/client/Iris/Util/IrisRequire.lua

Protected generated/current-like data, read-only:

* Iris/build/description/v2/output/dvf_3_3_rendered.json
* Iris/build/description/v2/output/style_normalization_changes.jsonl
* Iris/build/description/v2/output/compose_requeue_candidates.jsonl
* Iris/build/package/**

### Docs

Direct mutation in this planning task:

* docs/dvf_3_3_registry_authority_canonical_closure_plan.md

Planned execution docs:

* docs/dvf_3_3_registry_authority_canonical_closure_roadmap.md
* docs/dvf_registry_handoff_contract.md
* docs/registry_authority_protected_surface_policy.md
* docs/registry_authority_seal_cutover_contract.md
* docs/stale_predecessor_reentry_guard_policy.md
* docs/registry_authority_claim_contract.md
* docs/dvf_3_3_registry_authority_canonical_closure_claim_boundary.md
* docs/dvf_3_3_registry_authority_canonical_closure_ledger_packet.md
* docs/dvf_3_3_registry_authority_canonical_closure_closeout.md

The repo-local roadmap, implementation plan, bounded Entry bootstrap scaffold manifest, and clean-worktree checkpoint are owner-approved immutable execution inputs, not artifacts this planning task silently approves. Their path/hashes/base commit must be bound by D0/D9/D10 and external approvals before Phase 3 or any WP begins.

Planned post-owner-seal owner-application drafts, generated only inside Option B post_external_gate:

* docs/dvf_3_3_registry_authority_canonical_closure_decisions_update_draft.md
* docs/dvf_3_3_registry_authority_canonical_closure_architecture_update_draft.md
* docs/dvf_3_3_registry_authority_canonical_closure_roadmap_update_draft.md

Read-only authority/context docs:

* docs/Philosophy.md
* docs/DECISIONS.md
* docs/ARCHITECTURE.md
* docs/ROADMAP.md
* docs/EXECUTION_CONTRACT.md
* docs/PLAN_TEMPLATE.md
* docs/dvf_3_3_core_registry_boundary_claim_contract.md
* docs/dvf_3_3_core_registry_boundary_required_gate_adoption_contract.md
* docs/dvf_3_3_dvf_system_naming_realignment_policy.md
* docs/dvf_3_3_predecessor_stale_artifact_reentry_policy.md
* docs/dvf_3_3_vnext_cutover_contract.md
* docs/dvf_3_3_vnext_current_authority_handoff_packet.md
* docs/predecessor_reentry_guard_policy.md
* docs/dvf_vcs_tracking_policy.md
* docs/runtime_payload_shape_contract.md

### Config

Potential narrow additive edits:

* Iris/_docs/round3/current_route_required_validations.json
* .gitignore

Read-only config/authority inputs:

* Iris/_docs/round3/round3_active_core_closure.json
* Iris/_docs/round3/round3_test_taxonomy.json
* Iris/_docs/round3/round3_contract_manifest.json
* Iris/_docs/authority/iris_current_authority_manifest.json
* Iris/build/description/v2/data/dvf_3_3_input_manifest.json

No round3 active-core expansion and no broad staging unignore are planned.

Owner/reviewer-provided external inputs:

* Iris/build/description/v2/owner_inputs/dvf_3_3_registry_authority_canonical_closure/worktree_checkpoints/current_session_clean_worktree_checkpoint_record.json
* Iris/build/description/v2/owner_inputs/dvf_3_3_registry_authority_canonical_closure/owner_decisions/current_session_owner_decision_record.json
* Iris/build/description/v2/owner_inputs/dvf_3_3_registry_authority_canonical_closure/plan_approvals/current_session_implementation_plan_approval_record.json
* Iris/build/description/v2/owner_inputs/dvf_3_3_registry_authority_canonical_closure/preimplementation_reviews/current_session_responsibility_boundary_review.md
* Iris/build/description/v2/owner_inputs/dvf_3_3_registry_authority_canonical_closure/preimplementation_reviews/current_session_authority_evidence_integrity_review.md
* Iris/build/description/v2/owner_inputs/dvf_3_3_registry_authority_canonical_closure/preimplementation_reviews/current_session_adversarial_failure_mode_review.md
* Iris/build/description/v2/owner_inputs/dvf_3_3_registry_authority_canonical_closure/reviewer_designations/current_session_independent_reviewer_designation.json
* Iris/build/description/v2/owner_inputs/dvf_3_3_registry_authority_canonical_closure/attempt_registrations/current_session_attempt_record.json
* Iris/build/description/v2/owner_inputs/dvf_3_3_registry_authority_canonical_closure/gate_adoptions/current_session_required_gate_adoption_authorization_record.json
* Iris/build/description/v2/owner_inputs/dvf_3_3_registry_authority_canonical_closure/independent_reviews/current_session_independent_closeout_review.md
* Iris/build/description/v2/owner_inputs/dvf_3_3_registry_authority_canonical_closure/owner_seals/current_session_owner_canonical_seal_record.json

### Generated Artifacts

Cycle evidence root and immutable bootstrap location:

* Iris/build/description/v2/staging/dvf_3_3_registry_authority_canonical_closure/

Every execution attempt writes only below its registered immutable root:

* Iris/build/description/v2/staging/dvf_3_3_registry_authority_canonical_closure/attempts/<attempt_id>/

The phase0/* through phase5/* paths below are relative to that attempt root unless explicitly identified as the cycle-level tracked bootstrap manifest. An existing attempt root or claim-bearing output is never overwritten; retry uses a new attempt_id and new root while preserving predecessor failure records.

Phase 0 / plan binding:

* phase0/registry_authority_plan_traceability_matrix.json
* phase0/registry_authority_evidence_root_manifest.json
* phase0/roadmap_approval_record.json
* phase0/roadmap_scope_boundary_record.json
* phase0/roadmap_provenance_record.json
* phase0/implementation_plan_fingerprint_report.json
* phase0/bootstrap_scaffold_hash_manifest.json
* phase0/implementation_plan_approval_record.json
* phase0/attempt_registration_record.json
* phase0/implementation_plan_approval_validation_report.json
* phase0/owner_reserved_decision_register.json
* phase0/current_checkout_baseline.json
* phase0/dirty_overlap_report.json
* phase0/clean_worktree_checkpoint_record.json
* phase0/worktree_isolation_report.json
* phase0/protected_surface_policy.json
* phase0/protected_surface_hashes.before.json
* phase0/protected_surface_plan_mapping_report.json
* phase0/vcs_visibility_preflight.json
* phase0/evidence_root_preservation_policy.json
* phase0/lua_syntax_environment_preflight.json
* phase0/preflight_report.json
* attempt_failures/<mode>.json (conditional, exclusive-create exception record)

Phase 3 / pre-implementation review:

* phase3/responsibility_boundary_review.md
* phase3/authority_evidence_integrity_review.md
* phase3/adversarial_failure_mode_review.md
* phase3/preimplementation_review_input_manifest.json
* phase3/preimplementation_review_materialization_report.json
* phase3/consolidated_review.md
* phase3/carry_forward_findings_table.json
* phase3/pre_implementation_blocker_resolution_report.json
* phase3/blocker_zero_record.json

Phase 4 / work packages:

* phase4/wp1_dvf_registry_handoff_validation_report.json
* phase4/wp1_candidate_artifact_consumption_guard_report.json
* phase4/wp1_current_writer_authorization_guard_report.json
* phase4/wp1_current_writer_callsite_inventory.json
* phase4/wp2_current_checkout_artifact_surface_census.json
* phase4/wp2_required_validation_manifest_recensus.json
* phase4/wp2_required_artifact_vcs_surface_report.json
* phase4/wp2_artifact_role_classification_ledger.jsonl
* phase4/wp2_artifact_role_classification_summary.md
* phase4/wp2_forbidden_current_looking_surface_report.json
* phase4/wp2_candidate_current_boundary_report.json
* phase4/wp2_round3_contract_manifest_consumer_graph.json
* phase4/wp2_round3_contract_manifest_disposition_report.json
* phase4/wp3_current_identity_chain_manifest.json
* phase4/wp3_current_identity_chain_hash_report.json
* phase4/wp3_registry_observation_receipt.json
* phase4/wp3_dual_authority_scan_report.json
* phase4/wp3_predecessor_relation_map.json
* phase4/wp3/bridge_candidate/
* phase4/wp3/package_probe/
* phase4/wp4_required_validation_ownership_report.json
* phase4/wp4_required_evidence_freshness_report.json
* phase4/wp4_durable_vs_generated_evidence_report.json
* phase4/wp4_fresh_execution_manifest.json
* phase4/wp4_required_test_dependency_closure_report.json
* phase4/wp4_bare_import_guard_validation_report.json
* phase4/wp5_candidate_to_current_promotion_contract.json
* phase4/wp5_seal_receipt_schema.json
* phase4/wp5_registry_current_write_authorization_receipt_schema.json
* phase4/wp5_registry_current_write_authorization_guard_report.json
* phase4/wp5/fixture_receipts/
* phase4/wp5_cutover_precondition_report.json
* phase4/wp5_cutover_postcondition_report.json
* phase4/wp5_rollback_reentry_guard_report.json
* phase4/wp6_stale_current_looking_path_scan_report.json
* phase4/wp6_package_fallback_forbidden_scan_report.json
* phase4/wp6_required_manifest_reentry_report.json
* phase4/wp6_docs_current_authority_claim_scan_report.json
* phase4/wp7_registry_authority_claim_scan_report.json
* phase4/wp7_registry_authority_required_gate_contract_report.json
* phase4/wp7_required_gate_adoption_authorization_record.json
* phase4/wp7_required_validation_additive_gate_record.json
* phase4/implementation_scope_report.json
* phase4/protected_surface_no_mutation_report.json
* phase4/registry_authority_tooling_validation_report.json
* phase4/focused_test_result_report.json
* phase4/wp_completion_summary.md

Phase 5 / final validation and seal:

* phase5/implementation_freeze_manifest.json
* phase5/final_current_checkout_validation_report.json
* phase5/final_command_matrix_report.json
* phase5/final_validation_failure_attribution_report.json
* phase5/final_validation_hash_binding_report.json
* phase5/final_registry_blocker_report.json
* phase5/protected_surface_hashes.after.json
* phase5/protected_surface_no_mutation_report.json
* phase5/current_route_validation_result.json
* phase5/package_probe/
* phase5/post_external_required_consumer_manifest.json
* phase5/final_registry_authority_machine_report.json
* phase5/independent_closeout_review.md
* phase5/independent_review_artifact_hash_report.json
* phase5/owner_seal_input_manifest.json
* phase5/owner_canonical_seal_record.json
* phase5/owner_canonical_seal_record_validation_report.json
* phase5/top_doc_application_order_report.json
* phase5/top_doc_sync_state.json
* phase5/post_external_current_route_validation_result.json
* phase5/post_external_consumer_coverage_report.json
* phase5/post_external_gate_validation_report.json
* phase5/final_registry_authority_closure_report.json
* phase5/final_artifact_hash_manifest.json
* phase5/terminal_hash_seal.json

Roadmap deliverable mapping:

* The owner creates current_session_clean_worktree_checkpoint_record.json only after the scaffold-bearing worktree reports empty git status. It binds the base commit, worktree identity/path, exact status command/output digest, timestamp, and bootstrap scaffold manifest hash. phase0/clean_worktree_checkpoint_record.json is a byte-identical materialization.
* The owner authors the implementation-plan approval only at Iris/build/description/v2/owner_inputs/dvf_3_3_registry_authority_canonical_closure/plan_approvals/current_session_implementation_plan_approval_record.json.
* phase0/implementation_plan_approval_record.json is a byte-identical, hash-verified materialization of that external input. Tooling may copy/validate it but may not approve the plan, alter approved_plan_hash/approved_scaffold_hash/approved_clean_checkpoint_hash, or substitute current hashes after approval.
* The three Phase 3 reviewers author only their reserved preimplementation_reviews inputs after preflight publishes the reviewed-bundle hash. The phase3 review files are byte-identical materializations; tooling may consolidate findings mechanically but cannot author, improve, default, or suppress a review verdict/finding.
* The eligible independent reviewer authors the final review only at Iris/build/description/v2/owner_inputs/dvf_3_3_registry_authority_canonical_closure/independent_reviews/current_session_independent_closeout_review.md.
* phase5/independent_closeout_review.md is a byte-identical, hash-verified materialization of that external reviewer input. Tooling may copy and validate it but may not author, default, summarize, rewrite, or alter its body, findings, or verdict fields.
* phase5/independent_review_artifact_hash_report.json records both paths, both raw SHA-256 values, byte length, byte_identity=true, reviewer designation identity, and reviewed bundle hash.
* The owner authors the canonical seal at the external owner-input path.
* phase5/owner_canonical_seal_record.json is a byte-identical, hash-verified materialization of that external input; tooling may copy and validate it but may not author, default, or alter its decision fields.

Mandatory tracked implementation dependency set:

* Iris/build/description/v2/tools/build/dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py
* Iris/build/description/v2/tools/build/run_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py
* Iris/build/description/v2/tools/build/validate_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py
* Iris/build/description/v2/tests/test_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py
* every exact positive/negative fixture path enumerated by phase4/wp4_required_test_dependency_closure_report.json

Each item must be tracked and not ignored/effectively ignored. The fixture report is an enumeration check, not authority to unignore a directory wildcard; .gitignore changes name every admitted file exactly.

Mandatory selective-tracked closeout set:

* docs/dvf_3_3_registry_authority_canonical_closure_roadmap.md
* docs/dvf_3_3_registry_authority_canonical_closure_plan.md
* phase0/roadmap_approval_record.json
* phase0/bootstrap_scaffold_hash_manifest.json
* phase0/clean_worktree_checkpoint_record.json
* phase0/implementation_plan_approval_record.json
* phase3/responsibility_boundary_review.md
* phase3/authority_evidence_integrity_review.md
* phase3/adversarial_failure_mode_review.md
* phase3/preimplementation_review_materialization_report.json
* phase5/implementation_freeze_manifest.json
* phase5/final_validation_hash_binding_report.json
* phase5/final_command_matrix_report.json
* phase5/final_validation_failure_attribution_report.json
* phase5/final_registry_authority_machine_report.json
* phase5/independent_closeout_review.md
* phase5/independent_review_artifact_hash_report.json
* phase5/owner_canonical_seal_record.json
* phase5/post_external_gate_validation_report.json
* phase5/post_external_current_route_validation_result.json
* phase5/post_external_required_consumer_manifest.json
* phase5/post_external_consumer_coverage_report.json
* phase5/top_doc_application_order_report.json
* phase5/top_doc_sync_state.json
* phase5/final_registry_authority_closure_report.json
* docs/dvf_3_3_registry_authority_canonical_closure_ledger_packet.md
* docs/dvf_3_3_registry_authority_canonical_closure_closeout.md
* phase5/final_artifact_hash_manifest.json
* phase5/terminal_hash_seal.json

These claim-bearing closeout artifacts use docs/dvf_vcs_tracking_policy.md selective-tracked-closeout-evidence treatment. Their durability is separate from live required-manifest adoption: exact .gitignore visibility and git ls-files preservation are required even when they are intentionally not added to current_route_required_validations.json.

Generated evidence is not source, rendered, runtime, package, public, or release authority by file existence alone.

---

## 6. Planned Changes

### Roadmap-to-Plan Traceability

| Roadmap unit | Plan change | Primary output |
|---|---|---|
| Phase 1 roadmap approval | D0 / Change 0 entry gate | repo-local approved roadmap + approval/scope records |
| Phase 2 roadmap-derived plan | D9/D10 / current plan artifact / bounded Entry bootstrap / Change 0 binding | owner-approved plan/scaffold/checkpoint/base hashes + byte-identical records + fingerprint + traceability/evidence-root manifests |
| Phase 3 reviews | Change 0 | phase3 blocker-zero evidence |
| WP-1 | Change 1 | DVF/Registry handoff contract |
| WP-2 | Change 2 | live census and role ledger |
| WP-3 | Change 3 | single identity chain manifest |
| WP-4 | Change 4 | required-validation freshness reseal |
| WP-5 | Change 5 | seal/cutover contract |
| WP-6 | Change 6 | stale/predecessor guard |
| WP-7 | Change 7 | Registry claim contract and conditional live gate, mandatory for canonical_complete |
| Phase 5 closeout | Change 8 | final validation/review/owner seal |

### Synthesized Review Revision Closure

| Review revision | Selected resolution | Plan readpoint |
|---|---|---|
| R1 current-regeneration exception | Option B: no exception; entrypoint rejects unauthenticated current writes and only a one-use WP-5 receipt can pass the parity-gated candidate-first route | Change 1, Change 5 |
| R2 required-gate ambiguity | conditional across outcomes, mandatory for canonical_complete | Scope, D6, Change 7, Section 12 |
| R3 external independent review path | reserved reviewer input + byte-identical phase5 materialization | Section 5, Change 8, Validation step 11 |
| R4 roadmap hash mismatch | fail closed, re-derive, rerun Phase 3; narrow no-material-effect owner exception only | D0, Change 0 |
| R5 body_plan binding | current Case A physical location plus input-plan/output-instance hash coverage; Case B fallback or blocker | Codebase summary, Change 3 |
| R6 top-doc/seal DAG | Option B: owner seal first, post_external top-doc application/affected-consumer rerun, terminal binding last | D7, Change 8, Validation steps 12-13 |
| R7 execution entry checklist | one fail-closed gate before WP-1 | Section 4, Change 0, Validation step 2 |
| R8 validation triage | blocking and adjacent matrices separated | Section 7 |
| R9 lexical/fixture hardening | closeout_state token, rendered.meta role, unconditional Lua syntax, expanded forbidden meanings, receipt non-claims | Changes 1/7, Sections 7/12 |
| Follow-up operator-risk hardening | remove all mode; require WP-attributed failure reports; preflight luac capability; freeze post_external consumer denominator | Change 0, Change 8, Section 7 |
| RAC-M6 finalize producer order | finalize produces final closure report, ledger packet, and closeout before final artifact manifest and terminal seal | Change 8, Validation step 13 |
| RAC-M7 owner wait marker | explicit STOP/RESUME marker and no-write owner-application predicate before post-external reruns | Validation step 12 |
| Success-probability hardening | Registry-authenticated shared writer, D9/D10 scaffold/checkpoint approval, valid WP-3 staging compose, fresh no-recursion completion fixture-check, bare-import closure repair, diagnostic-only malformed manifest disposition | Changes 0/1/2/3/4/5, Section 7 |

This table records plan revision coverage only. It does not convert the attached FAIL review into PASS; a fresh cycle-2 review must validate these resolutions before execution.

### Change 0 - Execution Scaffold, Provenance, Review, and Blocker-Zero Gate

Purpose:

Freeze the plan-derived execution boundary, provide only the minimum non-circular review-materialization/Entry-validation bridge, prove that bridge cannot execute a WP or claim completion, capture the live dirty/protected baseline, and complete the three roadmap-mandated pre-implementation reviews before WP execution.

Files:

* new common/runner/validator/focused-test files listed in Section 5
* phase0/* and phase3/* evidence
* owner decision, implementation-plan approval, reviewer designation, and worktree-isolation input paths
* .gitignore exact-path visibility rules

Implementation Notes:

* Runner modes are limited to preflight, materialize-preimplementation-reviews, implementation, wp1, wp2, wp3, wp4, wp5, wp6, wp7, gate-candidate, adopt-gate, final-rerun, materialize-independent-review, materialize-owner-seal, prepare-top-docs, post-external, and finalize. Do not implement all mode. --mode all and any unlisted stage-aggregating alias must exit nonzero before writes, external-input reads, gate adoption, or finalization; a negative fixture proves zero mutation/evidence emission.
* preflight mode may create census/provenance evidence but must set canonical_closure_claimed=false and owner_seal_claimed=false.
* Resolve the clean-worktree/review/Entry dependency explicitly: before D10, the only new executable change allowed into the proposed execution-base commit is a bounded Entry scaffold consisting of the new common/runner/validator/focused-test files. Its only runner success modes are preflight and materialize-preimplementation-reviews; its only validator success requirements are require-preflight, require-preimplementation-reviews, and require-execution-entry. The materializer may only parse/validate/copy the three reserved review inputs byte-for-byte and emit mechanical counts/provenance under phase3. The Entry validator is read-only and may only return the checklist result. Every WP, implementation, gate-candidate/adoption, current/protected writer, machine/final/canonical producer, owner/reviewer verdict authoring, and post-external mode remains not_implemented nonzero. The same commit contains the final plan/roadmap bytes and only the exact .gitignore visibility rules needed for the scaffold and reserved external inputs. No WP logic, compose/current-runner hardening, broad unignore, gate adoption logic, or final producer is allowed in this bootstrap.
* Before creating the base commit, derive and commit phase0/bootstrap_scaffold_hash_manifest.json from the closed scaffold path set. It hashes only scaffold paths/bytes and AST/command capabilities, excludes its own bytes and the not-yet-created commit hash to avoid self-reference, and is immutable after commit. D10 approves this manifest hash and the resulting base commit together with the plan hash; Entry recomputes the manifest in memory and compares without overwriting it. Any bootstrap byte or capability change between approval and successful Execution Entry invalidates D10 and requires a fresh clean base, owner approval, and Phase 3 review. After Entry, only plan-mapped implementation transitions are legal; bind their before/after hashes in phase4/implementation_scope_report.json and the final freeze rather than rewriting the approved bootstrap baseline.
* Materialize and owner-approve the roadmap at docs/dvf_3_3_registry_authority_canonical_closure_roadmap.md, then bind its repo-relative path and SHA-256 together with the adopted plan path/hash. The attachment path remains provenance only and must not become an execution dependency.
* Before any WP/domain implementation beyond the bounded Entry scaffold, materialize the externally authored current_session_implementation_plan_approval_record.json byte-for-byte into phase0/implementation_plan_approval_record.json. Validate that it names the repo-local plan path, binds the exact plan SHA-256, entry-time bootstrap scaffold manifest, clean-worktree checkpoint hash, and approved roadmap hash consumed by the runner, identifies the owner and approval time, and approves the execution base commit. Any plan/roadmap/checkpoint/base change, or any pre-Entry scaffold byte/capability change, makes the approval stale and forces owner reapproval plus a fresh Phase 3 review before any wp* mode.
* Materialize registry_authority_plan_traceability_matrix.json and registry_authority_evidence_root_manifest.json before WP execution; every roadmap deliverable must map to one planned producer and one validation consumer.
* Require a roadmap_approval_record and roadmap_scope_boundary_record that bind the repo-local roadmap payload before implementation. The current request authorizes this plan document, not a synthetic owner approval record.
* Compare roadmap_approval_record.approved_payload_hash with this plan header's consumed_roadmap_hash. A mismatch fails closed, requires re-deriving the plan from the approved roadmap, and requires a fresh Phase 3 review. The sole exception is an owner-authored diff-scope approval that binds both hashes, the canonical diff SHA-256, every changed section/hunk, and a per-hunk no-material-effect rationale. Wildcards, whole-document approval, unexplained changes, and phrases equivalent to “all changes are non-material” are invalid. Any hunk touching objective, scope/out-of-scope, WP deliverables, authority ownership, required gates, validation denominator/ceiling, closeout vocabulary, top-doc policy, or seal DAG makes the exception ineligible and forces re-derivation/re-review.
* Preserve the original dirty checkout's file bytes as provenance. In an explicit owner-controlled action outside this runner, the owner must disposition the accepted changes, create the exact accepted commit without discarding unresolved bytes, and designate that commit as the execution base; the runner must never stash, reset, clean, commit, or copy working-tree changes on the owner's behalf.
* Record every original dirty path/hash as accepted_into_execution_base, excluded_but_preserved_in_original_checkout, or blocker in dirty_overlap_report.json. Required/protected/planned-mutation and top-doc Registry/DVF-overlap paths require an exact owner disposition; wildcard or repository-wide acceptance is invalid. The execution base tree hash must match every accepted row, while excluded rows remain only in the original checkout and cannot leak into evidence.
* Create a dedicated worktree from the owner-approved execution base commit and run every mutation and validation command in Section 7 there. Capture the original checkout path/status hash, execution worktree path, base commit, branch/worktree identity, git status --porcelain=v1, required/protected intersections, and top-doc baseline hashes in worktree_isolation_report.json.
* Require the dedicated execution worktree created from the scaffold-bearing base commit to have zero modified, deleted, renamed, or untracked paths and zero ignored planned-output paths at an owner-recorded clean checkpoint. current_session_clean_worktree_checkpoint_record.json binds the empty status output, command, base HEAD, worktree identity/path, timestamp, and scaffold manifest hash; tooling may validate/materialize but never author or backdate it.
* After that clean checkpoint and before preflight, only the exact reserved external owner/reviewer input files named in Section 5 may be introduced. D10 lists each present input path/hash and binds the clean-checkpoint hash. Preflight rejects any code/docs/config/evidence delta, unlisted input, ignored input, or changed checkpoint/approval hash before its own evidence writes. Later gates recompute expected round-owned deltas separately; the planning observation of 99 modified paths is provenance only, never an execution predicate.
* Resolve every path before hashing or writing. Evidence writes must remain under the ratified evidence root.
* Separate cycle_id from attempt_id. cycle_id remains dvf_3_3_registry_authority_canonical_closure; each execution uses an owner-registered attempt_id matching attempt-NNNN-lowercase-label and the exact root cycle_root/attempts/<attempt_id>/. Preflight rejects a missing/mismatched registration, path traversal, a reused attempt root, or any existing attempt output before writes.
* A pre-adoption retry is legal only with a new attempt_id and new output root while protected_mutation_count=0, live_gate_adopted=false, and top_docs_applied=false. The registration lists every predecessor attempt, its preserved failure/archive path, and the canonical tree SHA-256 of that archive. Preflight and Entry recompute every predecessor tree hash and require its terminal preflight report or write-once preflight exception record. The tool must not delete, truncate, replace, rename-away, or rewrite a predecessor failure record.
* All attempt claim-bearing outputs are exclusive-create/write-once. A failed or partial attempt remains immutable evidence; it may be superseded by a later attempt but never converted in place from FAIL to PASS. preflight_report.json and preimplementation_review_materialization_report.json are their modes' terminal outputs and are written only after every preceding mode output succeeds. Before Entry, the runner records an otherwise-unmaterialized mode exception once under attempt_failures/<mode>.json; it never rewrites that record and never appends one after the mode's terminal output already exists. materialize-preimplementation-reviews prechecks its entire output set and refuses a same-attempt rerun if any target already exists.
* Receipt nonce consumption is scoped to one attempt and never reset. A consumed nonce cannot be retried; a later legal attempt requires a newly authorized receipt and nonce. Candidate/fixture generation failures may discard or supersede only the candidate/fixture inside their attempt, then continue only in a new attempt root.
* Use one closed plan-mapped protected/identity-bearing denominator resolver for preflight, Entry, implementation freeze, final no-mutation, and reviewed-bundle hashing. It includes the six DVF current inputs, compose_profiles_v2.json, compose_profile_identity_hint_rules.json, compose_profile_conflict_precedence_rules.json, dvf_3_3_rendered.json, style_normalization_changes.jsonl, compose_requeue_candidates.jsonl, layer3_renderer.lua, IrisWikiSections.lua, IrisModuleBootstrap.lua, IrisRequire.lua, the verified runtime chunk manifest/directory, and Iris/build/package. Build runtime paths from _dvf_3_3_vnext_common.RUNTIME_CHUNK_MANIFEST, RUNTIME_CHUNK_DIR, RUNTIME_MONOLITH or equally verified actual repo-root paths. Emit one explicit row per exact file/directory and require set equality with this plan-mapped denominator; assert required members exist and reject omissions, extras, and duplicate-root forms such as Iris/Iris/media/....
* Record exact .gitignore visibility for tool, test, fixture, owner input, and minimum durable evidence paths.
* Do not broad-unignore Iris/build/description/v2/staging/** or tools/build/**.
* Add exact-path visibility rules for the existing completion-vocabulary main/runner/validator trio, the existing focused test, and only the positive/negative fixtures that the refactored test actually consumes. Prove each selected path is tracked and not ignored/effectively ignored; a directory wildcard or broad tools/build/** exception is invalid.
* Preflight Lua capability before WP execution: hash tools/check_lua_syntax.ps1, resolve exactly one luac executable, record its resolved path/version/file hash, and prove the intended roots contain at least one Lua file. A missing/ambiguous checker or later capability drift is environment_blocked; the runner must not download or install a replacement.
* Materialize the three review inputs independently. Tooling may validate review schemas and findings but must not author PASS verdicts.
* Reserve three external preimplementation review paths in Section 5. preflight emits only their hash-bound review bundle/criteria; then execution stops. materialize-preimplementation-reviews copies each supplied review byte-for-byte into phase3, records author/path/hash/byte identity, and fails if a review is absent, self-generated by the runner, based on a different plan/scaffold/base bundle, or authored before that bundle hash existed.
* Each Phase 3 review records designated scope, author identity, relation to the plan/scaffold implementer, reviewed-bundle hash, verdict, and typed findings. The plan/scaffold implementer may supply factual responses but cannot be the sole verdict author for all three reviews; one identity covering multiple review scopes requires explicit owner designation and may not be reported as three independent reviewers.
* require-preimplementation-reviews and require-execution-entry must freshly parse the three fixed external review source paths on every invocation, recompute schema/bundle/identity/verdict/finding counts and byte identity against their fixed materialized targets, and compare the recomputed projection with the mechanical phase3 reports. blocker_zero_record.json, consolidated_review.md, carry_forward_findings_table.json, and every other ignored/generated projection are diagnostic consistency outputs, never verdict/count authority. A forged or stale derived PASS cannot override an external FAIL or malformed source review.
* Execution Entry constructs its allowed post-checkpoint status map only from compile-time fixed reserved paths plus D10-validated preflight inputs. It never imports a path or target from an ignored/generated materialization report. Stored source_path/target_path fields must equal the fixed scope mapping, and an extra path remains forbidden even when its bytes duplicate a valid review.
* Consolidate Critical, Important, Minor findings. Critical/Important must be zero; every Minor needs owner_resolved or owner_accepted disposition.
* require-execution-entry must freshly recompute every plan-mapped protected/identity-bearing row and aggregate, require byte equality with phase0/protected_surface_hashes.before.json and hash equality with the reviewed bundle, and reject missing/drifted members. Git status is not a substitute because protected output/package paths may be ignored.
* require-execution-entry likewise freshly recomputes the Lua checker/luac/version/hash/input-set report and requires equality with both the Phase 0 bytes and reviewed-bundle lua_environment_hash. An ignored Phase 0 report cannot authorize capability drift.
* A roadmap/plan/execution author is not eligible as final independent reviewer.
* Enforce the Execution Entry Gate checklist in Section 4 as a single fail-closed predicate before any wp* mode. The validator must report every failed checklist row rather than short-circuiting after the first.
* Every command-result row must carry validation_class, wp_owner, command_id, exact argv, input/output paths, exit_code, failure_category, first_failing_predicate, stderr/stdout digest, and blocked_downstream command IDs. final_validation_failure_attribution_report.json groups failures by preimplementation_review, WP-1..WP-7, adjacent regression, external review, owner seal, post_external, and finalize; a single undifferentiated overall failure is invalid.
* On a blocking failure, stop dependent commands but still write the command row and attribution summary, then exit nonzero. Mark unexecuted dependents as not_run_due_to with the originating WP/command ID; never relabel them PASS or silently omit them.

Validation:

* plan-only claim additions = 0
* pre_entry_non_scaffold_implementation_path_count = 0
* bootstrap_scaffold_success_modes = [preflight, materialize-preimplementation-reviews]
* bootstrap_scaffold_validator_success_requirements = [require-preflight, require-preimplementation-reviews, require-execution-entry]
* bootstrap_scaffold_non_entry_mode_success_count = 0
* bootstrap_scaffold_claim_or_finalization_capability_count = 0
* cycle_id_attempt_id_separation = true
* same_attempt_claim_output_overwrite_count = 0
* predecessor_failure_record_deletion_or_rewrite_count = 0
* attempt_registration_materialization_byte_identity = true
* uncaptured_pre_entry_mode_exception_count = 0
* pre_adoption_new_attempt_retry_allowed = true
* protected_surface_plan_denominator_set_equality = true
* entry_fresh_protected_surface_rows_equal_preflight_rows = true
* entry_fresh_protected_surface_hash_equals_reviewed_bundle_hash = true
* entry_fresh_lua_environment_hash_equals_reviewed_bundle_hash = true
* entry_external_review_sources_freshly_reparsed = true
* derived_blocker_zero_used_as_authority_count = 0
* forged_derived_pass_external_fail_bypass_count = 0
* generated_review_path_used_as_entry_allowlist_count = 0
* duplicate_review_bytes_at_unreserved_path_allowed_count = 0
* pre_implementation_blocker_count = 0
* Critical_count = 0
* Important_count = 0
* preimplementation_review_materialization_byte_identity = true
* preimplementation_review_wrong_bundle_count = 0
* tool_authored_preimplementation_review_verdict_count = 0
* all_phase3_verdicts_solely_authored_by_plan_scaffold_implementer = false
* false_phase3_reviewer_independence_claim_count = 0
* self_generated_pass_as_independent_review_count = 0
* unresolved owner-reserved execution-entry decision = 0
* approved_roadmap_hash_matches_consumed_roadmap_hash = true, or valid_no_material_effect_diff_scope_approval = true
* broad_or_wildcard_roadmap_diff_scope_approval_count = 0
* implementation_plan_approval_materialization_byte_identity = true
* approved_plan_hash_matches_execution_plan_hash = true
* approved_bootstrap_scaffold_hash_matches_entry_scaffold_hash = true
* clean_worktree_checkpoint_materialization_byte_identity = true
* approved_clean_checkpoint_hash_matches_materialized_checkpoint_hash = true
* approved_execution_base_commit_matches_entry_worktree_head = true
* execution_worktree_initial_dirty_count = 0
* preflight_start_unapproved_delta_count = 0
* post_checkpoint_code_docs_config_delta_count = 0
* runner_original_checkout_content_mutation_count = 0
* unexplained_or_broad_dirty_path_disposition_count = 0
* accepted_dirty_path_execution_base_hash_mismatch_count = 0
* excluded_dirty_path_execution_leak_count = 0
* unsupported_all_mode_rejected_without_writes = true
* unattributed_validation_failure_count = 0
* lua_syntax_environment_preflight_status = PASS
* dirty protected/required overlap = 0
* evidence root containment = PASS
* scaffold cannot emit Registry Authority PASS or canonical_complete

---

### Change 1 - WP-1 DVF / Registry Handoff Contract

Purpose:

Fix the boundary between DVF inputs/outputs and Registry candidate/current adoption so neither system reabsorbs the other system's responsibility.

Files:

* docs/dvf_registry_handoff_contract.md
* phase4/wp1_dvf_registry_handoff_validation_report.json
* phase4/wp1_candidate_artifact_consumption_guard_report.json
* positive/negative handoff fixtures

Implementation Notes:

The contract must encode:

    DVF input
    = contract-valid facts / decisions / profile / body_plan

    DVF output
    = rendered 3-3 body + rendered.meta

    compiler trace / receipt in the current form
    = rendered.meta embedded in the rendered artifact

    separate persisted compiler receipt artifact
    = absent in the current implementation

    Registry observation receipt
    = read-only sidecar over rendered.meta and bound hashes
    != compiler receipt
    != Registry seal
    != authority source

    DVF output before Registry adoption
    = candidate artifact

    Registry adoption
    = candidate -> current promotion
      only through Registry Authority contract

* Preserve compose_layer3_text.py body-generation and body_plan resolution semantics, but make one narrow write-contract hardening change: every resolved real CLOSED_CURRENT_PROTECTED_PATHS target is unconditionally rejected in this governance-only closure, before directory creation or writes, even when a receipt is supplied. Enforce this in the shared enforce_compose_write_contract/build_rendered boundary as well as main(), so an imported direct call cannot bypass the CLI. Validation must prove identical staged output bytes for identical inputs before and after this guard change.
* Add the explicit CLI option --registry-current-write-authorization-receipt and a default-None propagated function parameter only for contained fixture-contract validation. Receipt absence remains legal for staging, diagnostic, historical, and contained current-equivalent fixture sinks. No receipt accepted by this round can authorize any real CLOSED_CURRENT_PROTECTED_PATHS member. Key the decision on all resolved target paths, not compose_context or basename alone.
* The existing default/no-arg compose_context=current path must therefore fail nonzero before directory creation or writes when no authorization receipt is supplied. A prose prohibition or caller convention is insufficient. WP-3 uses compose_context=staging, supplies every current input explicitly, and binds those hashes to the live input manifest; its isolated staging proof must not require a current-write receipt.
* Define a closed, versioned fixture_only receipt schema containing round/schema ID, exact one-use allowed output paths, six input path/hash bindings, normalized body_plan authority hash, isolated candidate raw/canonical entries hashes, pre-write fixture hashes, expected post-write fixture hashes, WP-5 fixture-decision hash, issue time, expiry, nonce, and the contained receipt-consumption state path. Bind the receipt itself by SHA-256 in the Registry evidence root. An owner-authorization field or production/live flag is forbidden in receipts issued by this closure.
* Validate a fixture receipt before any fixture target/output filesystem mutation, then rehash all input/target preimages immediately before exclusive nonce consumption. The full allowed target set must resolve under one contained phase4/wp5 fixture transaction root. Missing, malformed, forged, stale, replayed, wrong-path, wrong-input, wrong-candidate, wrong-preimage, non-fixture, or real-path receipts fail closed with zero protected-path mutations. This fixture seam is evidence for guard semantics only; it is not an operational authorization mechanism.
* Inventory every compose_layer3_text.py callsite. Migrate ordinary candidate and proof invocations to explicit non-current sinks. The permitted real current-protected callsite count in this closure is zero. Any future Registry-controlled current write requires a separately reviewed operational-cutover plan that defines an enforceable Registry-owned lock or equivalent exclusive state transition across the full target set, revalidates preimages while holding it, writes contained temporary outputs, and specifies atomic replacement/rollback semantics and their platform limits.
* WP-5 must (1) prove the six pinned current inputs and body_plan authority coverage match the adopted current input manifest, (2) render to an isolated candidate sink, and (3) prove raw/canonical entry and body_plan identity parity with the adopted current rendered artifact. It records that production receipt issuance and live invocation are disabled. Any delta leaves output candidate-only.
* Add negative fixtures for no-arg/default current writes, drifted source, forged/stale/replayed receipts, mismatched paths/hashes, and receipt reuse. Each must be rejected before current-path mutation. Add positive isolated-fixture coverage for explicit staging output and a valid one-use Registry receipt without touching the real protected surface.
* Exercise the positive receipt/write path through a subprocess-only test harness that substitutes CLOSED_CURRENT_PROTECTED_PATHS in process with contained phase4/wp5 fixture paths and uses fixture_only=true. Production CLI/config/environment must expose no protected-set override; a fixture receipt or substituted fixture set can never authorize the real constants. This test seam is not a legal production callsite.
* Require every ordinary DVF candidate output to use an explicit non-current output sink/context. Do not invoke the no-arg current writer to create a candidate.
* Create only a registry_observation_receipt sidecar over rendered.meta and current input/output hashes. Its schema must repeat compiler_receipt=false, registry_seal=false, and authority_source=false. It is not a compiler-produced receipt, a new compiler output authority, or a Registry seal.
* Registry validates artifact role/identity and promotion conditions; it does not generate the body.
* Scan code/docs/config for direct candidate-as-current consumption and DVF-owned selector/promoter/sealer claims.
* Historical and negated claims remain allowed only when role-qualified.

Validation:

* dvf_current_artifact_selector_claim_count = 0
* registry_body_generation_claim_count = 0
* candidate_direct_current_consumption_count = 0
* current_regeneration_exception_count = 0
* current_protected_path_write_invocation_outside_registry_wp5_count = 0
* raw_no_arg_current_protected_write_rejected = true
* direct_build_rendered_current_protected_write_without_receipt_rejected = true
* registry_authorization_receipt_required_for_current_protected_write = true
* invalid_or_replayed_receipt_protected_mutation_count = 0
* receipt_input_and_target_preimage_revalidation_immediately_before_claim = true
* receipt_nonce_claim_precedes_target_write = true
* failed_receipt_nonce_reuse_allowed = false
* current_writer_legal_real_path_callsite_count = 0
* production_current_protected_set_override_surface_count = 0
* production_real_path_receipt_acceptance_count = 0
* current_write_operational_cutover_deferred = true
* entrypoint_guard_body_semantics_delta_count = 0
* staging_identity_proof_requires_current_write_authorization = false
* drifted_source_current_context_attempt_rejected = true
* drifted_source_fixture_current_path_mutation_count = 0
* compiler_trace_misread_as_seal_count = 0
* registry_observation_receipt_misread_as_compiler_receipt_count = 0
* registry_observation_receipt_misread_as_authority_source_count = 0
* handoff contract has no Runtime Compatibility or Publish Boundary claim

---

### Change 2 - WP-2 Current-Checkout Census and Artifact Role Classification

Purpose:

Build a fresh, deterministic Registry-relevant universe from the current checkout and classify every member with an explicit role.

Files:

* phase4/wp2_* census/ledger/reports
* Iris/_docs/authority/iris_current_authority_manifest.json as read-only predecessor input
* Iris/build/description/v2/data/dvf_3_3_input_manifest.json as current source seed
* current_route_required_validations.json as live required seed
* existing stale/runtime/package guard inventories as read-only predecessor seeds

Implementation Notes:

* Do not use a stored file list or fixed count as the scan universe.
* Build the universe from live required artifact paths, current input manifest paths, authority manifest exact/glob entries, runtime chunk manifest modules, exporter/package protected paths, referenced predecessor relations, and current-checkout filename/path scans for DVF/Layer3/bridge/chunk artifacts.
* Include Iris/_docs/round3/round3_contract_manifest.json in the scan seed. If it remains malformed, determine its actual live consumers and classify it with evidence; a current/required consumer makes the damage a blocker, while an unconsumed historical/diagnostic disposition requires an explicit exclusion rationale.

  The disposition outcome table is closed:

  | Observed outcome | Required role/disposition | Closeout effect |
  |---|---|---|
  | Parsed and proven current/required consumer input | current or required, with schema/consumer validation | parse/schema damage is a blocker until a separately authorized correction and fresh rerun |
  | Malformed and any current/required consumer exists | forbidden-current-looking plus damaged-required evidence | fail-closed blocker; no exclusion or downgrade allowed |
  | Malformed, no current/required consumer, historical/diagnostic provenance proven | historical or diagnostic with exact consumer-search evidence and explicit exclusion rationale | allowed only with current_reentry_allowed=false and package_reentry_allowed=false |
  | Misleading current-looking path/name with no legitimate consumer role | forbidden-current-looking or quarantine | reentry-denial evidence required; any current claim is a blocker |
  | Consumer/role cannot be proven | ambiguous | fail-closed blocker; unclassified/ambiguous count cannot be waived |

* Planning-time inspection selects a concrete proposed default for Iris/_docs/round3/round3_contract_manifest.json: diagnostic-only, current_reentry_allowed=false, and package_reentry_allowed=false. The observed producer is round3_generate_evidence.py; dvf_3_3_current_source_authority_drift_verification.py contains only an unused path constant; no live current-route or required-artifact consumer was found.
* Execution must re-prove that default from a repository-wide read/import/subprocess/config/reference graph, not inherit the planning observation. When producer-only provenance, the unused verifier constant, and zero current/required consumers all remain true, preserve the malformed bytes unchanged, record their hash and parse failure, classify the file diagnostic, and exclude it from every authority/current/package input denominator.
* Do not opportunistically repair or reparse the malformed payload in this closure. If even one live consumer is found, invalidate the diagnostic default and block before WP-3; correction then requires an explicit owner-authorized correction artifact, a fresh census, and rerunning every affected consumer. Absence of a proven consumer graph is ambiguous, not diagnostic.
* Resolve glob results at execution time, sort by normalized repo-relative path, and record the scan rule that admitted each artifact.
* Do not use rg --files alone for the census because ignored surfaces would be omitted. Use fd -HI or an equivalent hidden+ignored filesystem walk together with Git tracked/untracked/ignored/dirty queries.
* Role vocabulary is limited to current, candidate, staging, fixture, historical, diagnostic, quarantine, and forbidden-current-looking.
* Each ledger row must include path, role, authority_axis, hash, cardinality, producer, consumer, predecessor_relation, current_reentry_allowed, package_reentry_allowed, required_validation_status.
* Exact-path classification outranks glob classification. Conflicting exact roles are blockers, not automatic precedence.
* Resolve the known broad-glob conflict where iris_current_authority_manifest.json classifies output/** as reproduction while the successor chain treats the exact rendered JSON as current rendered identity. Record exact-path authority role and lifecycle/VCS treatment without turning the broad reproduction glob into a second authority.
* Hash regular files. For directories, record a sorted child path/hash Merkle-style digest without following out-of-repo links.
* Record tracked/untracked/ignored/effectively-ignored/dirty/missing state separately from authority role.
* A path not relevant to Registry may be excluded only with a recorded exclusion rule. A relevant path without a role is a blocker.
* Preserve historical/staging/fixture artifacts; classification does not authorize deletion.
* A second deterministic census comparison is valid only when HEAD, normalized git dirty set, required manifest bytes, and every protected surface hash are unchanged between runs. Otherwise invalidate the comparison, recapture the baseline, and run both censuses again.

Validation:

* artifact_surface_census_status = PASS
* artifact_role_classification_complete = true
* ambiguous_role_count = 0
* unclassified_role_count = 0
* duplicate_path_role_conflict_count = 0
* forbidden_current_looking_violation_count = 0
* candidate_current_confusion_count = 0
* round3_contract_manifest_role = diagnostic
* round3_contract_manifest_live_current_or_required_consumer_count = 0
* round3_contract_manifest_current_reentry_allowed = false
* round3_contract_manifest_package_reentry_allowed = false
* round3_contract_manifest_bytes_mutated = false
* stored_pass_reused_as_fresh_evidence = false
* second deterministic census has identical normalized ledger hash under same HEAD, same dirty set, and unchanged required/protected surfaces

---

### Change 3 - WP-3 Single Current Identity Chain Binding

Purpose:

Bind one Registry identity chain from current source through rendered/runtime identity and an isolated package projection, while preserving the fact that package publication is outside this closure.

Files:

* phase4/wp3_* manifests/reports
* phase4/wp3/bridge_candidate/
* phase4/wp3/package_probe/
* current source/rendered/runtime files listed in Section 5
* export_dvf_3_3_lua_bridge.py
* manage_dvf_3_3_runtime_chunk_cutover.py
* Iris/tools/package_iris.ps1

Implementation Notes:

* Validate the current input manifest against live facts/decisions/overlay paths, cardinalities, and SHA-256 values.
* Define current source identity as the input manifest plus its six pinned inputs: facts, decisions, overlay_support, compose_profiles_v2.json, compose_profile_identity_hint_rules.json, and compose_profile_conflict_precedence_rules.json.
* Record body_plan_authority_physical_location explicitly. Codebase inspection selects Case A at this readpoint: the body_plan input-plan authority is embedded in the full compose_profiles_v2.json payload, specifically schema_version, section_names, profiles.* required_sections/optional_sections/section_order/minimum sets, and render_rules; it is not a separate seventh source file. Bind the whole raw file SHA-256 and a normalized hash of those named sections rather than hashing an informal label.
* Also bind the produced per-entry body_plan instance at dvf_3_3_rendered.json entries[*].body_plan, including resolved_profile, emitted_sections, emitted_section_names, and missing_required_sections, through both the canonical entries hash and raw rendered artifact hash. Record that facts/decisions/overlay plus profile/identity/precedence inputs participate in resolution and section content.
* Revalidate this Case A predicate against dvf_3_3_input_manifest.json compose_authority.body_plan_alias, compose_layer3_body_profile.py, compose_layer3_item.py, and the live profile JSON at execution time. If body_plan has become a separate artifact, select Case B: add its path/hash to the input manifest, pinned input set, direct-compose arguments, and receipt. If neither Case A nor Case B is proven, fail closed; source_rendered_identity_match and single_current_identity_chain must remain false.
* Validate rendered entry identity and rendered metadata against the current source/overlay identity.
* Freshly execute the existing drift-verifier direct-compose pattern through the new WP-3 runner with compose_context=staging: pass all six current source inputs explicitly, write every compose output under phase4/wp3/direct_compose, and compare canonical rendered entries/key identity with the live rendered artifact. Do not use compose_context=current with a staging path; the live guard correctly rejects that output-class combination.
* Before invocation, prove the six explicit input paths/hashes equal dvf_3_3_input_manifest.json; this replaces the current-context input-path assertion without granting a protected write. The direct-compose proof must include context=staging, exact command, six input path/hash bindings, manifest parity, process exit code, output hashes, canonical entries hash, and live parity result. Metadata inspection alone cannot satisfy source_rendered_identity_match.

  Planned direct-compose command:

       uv run python -B Iris/build/description/v2/tools/build/compose_layer3_text.py --compose-context staging --facts-path Iris/build/description/v2/data/dvf_3_3_facts.jsonl --decisions-path Iris/build/description/v2/data/dvf_3_3_decisions.jsonl --profiles-path Iris/build/description/v2/data/compose_profiles_v2.json --overlay-path Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl --identity-rules-path Iris/build/description/v2/data/compose_profile_identity_hint_rules.json --precedence-rules-path Iris/build/description/v2/data/compose_profile_conflict_precedence_rules.json --output-path Iris/build/description/v2/staging/dvf_3_3_registry_authority_canonical_closure/phase4/wp3/direct_compose/dvf_3_3_rendered.json --style-log-path Iris/build/description/v2/staging/dvf_3_3_registry_authority_canonical_closure/phase4/wp3/direct_compose/style_normalization_changes.jsonl --requeue-candidates-path Iris/build/description/v2/staging/dvf_3_3_registry_authority_canonical_closure/phase4/wp3/direct_compose/compose_requeue_candidates.jsonl
* Iris has no separate live current monolith bridge authority. Define bridge identity as the deterministic exporter contract plus a staging candidate receipt that maps the rendered hash to the chunk manifest/chunk set.
* Run the exporter only into phase4/wp3/bridge_candidate with bridge-context staging and format chunk.
* Compare candidate manifest modules and chunk bytes/hashes with the live runtime bundle. Any mismatch is a Registry blocker; do not repair live runtime in this round.
* Record the domain and algorithm for every digest: raw file SHA-256, normalized JSON/content hash, row-key set hash, and ordered bundle hash are distinct and must not be compared as interchangeable values.
* Parse IrisLayer3DataChunks.lua to derive the live chunk set. Do not hardcode Chunk001..Chunk011 or chunk count 11.
* Scan for dual current authority, live monolith, stale bridge, predecessor chunk, and implicit fallback paths.
* Run Iris/tools/package_iris.ps1 only with an OutputRoot that has been resolved and proven to be inside phase4/wp3/package_probe. Use -Clean only after containment proof.
* Do not use -Zip, publish, copy to Iris/build/package, or adopt the probe as package authority.
* Compare the isolated package projection's Layer3 chunk manifest/chunks with the live runtime bundle by relative path and SHA-256.
* runtime_package_identity_match proves package payload identity projection only. It does not prove package readiness, publication, installability, or runtime behavior.
* Keep public runtime require contract unchanged.

Validation:

* single_current_identity_chain = true
* dual_authority_count = 0
* ambiguous_current_authority_count = 0
* body_plan_authority_physical_location = embedded_compose_profiles_v2
* body_plan_input_plan_hash_coverage = complete
* rendered_entry_body_plan_hash_coverage = complete
* direct_compose_context = staging
* direct_compose_current_input_manifest_hash_parity = true
* current_context_with_staging_output_invocation_count = 0
* source_rendered_identity_match = true
* rendered_bridge_identity_match = true
* bridge_runtime_identity_match = true
* runtime_package_identity_match = true
* live monolith/current stale bridge count = 0
* package probe output containment = PASS
* protected source/rendered/runtime/package-source mutation = 0
* deterministic bridge candidate rerun hash parity = true

---

### Change 4 - WP-4 Required-Validation Ownership and Freshness Reseal

Purpose:

Rebind Registry Authority required artifacts/tests to the live manifest and current checkout, separate durable evidence from generated evidence, and prohibit stored PASS reuse.

Files:

* phase4/wp4_* reports/manifests
* current_route_required_validations.json
* existing required-evidence/freshness/durable/VCS tooling and reports
* .gitignore exact preservation entries

Implementation Notes:

* Recompute required artifact/test/non-claim denominators from the live manifest. Do not copy planning-time 112/52 or any predecessor 93/48, 102/51, or other count.
* Separate path existence, JSON/schema/field semantics, producer identity, consumer identity, freshness, hash binding, and VCS preservation checks.
* Build a recursive required-test dependency closure covering Python imports, sys.path-injected bare imports, subprocess command targets, fixtures, and referenced schemas. Resolve each import to its actual file before test execution and record exists/tracked/not-ignored/hash state for every dependency.
* Close the known bypass as a required implementation, not an optional disposition: refactor test_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py to remove its sys.path insertion and bare import of dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py. Remove the setUpClass stored-final-PASS early return and the INNER_CURRENT_ROUTE/machine-pass recursion from the required-test path; a selected current-route test must execute fresh assertions every time.
* Add a narrow fixture-check mode to the preserved completion-vocabulary run/validate entrypoints. It requires explicit --root and --fixture-root paths, resolves both into a contained test-temp root/exact tracked fixture set, reads no stored phase9 PASS, calls neither write_docs nor round3_run_contract_tests.py, and writes only its isolated fixture report. Make --mode explicit rather than defaulting this preserved runner to all. The required test invokes only fixture-check through subprocess and asserts runner/validator machine reports, exit codes, input hashes, freshness nonce, cleanup, and no repository mutation.
* Legacy explicit all/machine-pass behavior in that predecessor runner is not current evidence for this closure and must never be invoked by the refactored required test or the new closure runner. fixture-check proves vocabulary/negative-fixture semantics only; it cannot emit canonical/external/owner completion claims. Any future retirement of legacy aggregate modes remains a separately reviewed predecessor compatibility change.
* Selectively preserve the completion-vocabulary main, run, and validate scripts plus the focused test and its exact fixtures. All must be tracked and not ignored/effectively ignored before gate adoption. Do not add the main script, its run/validate wrappers, or any new Registry tool to the active current core or current tooling allowlist.
* Narrowly harden Iris/_docs/round3/round3_run_contract_tests.py under --enforce-current-build-closure: before loading a selected test, account for its literal sys.path additions and resolve bare/qualified imports into tools/build. Reject any resolved dependency that is absent, untracked, ignored, outside the preserved closure, or introduced as an active-core dependency. This guard must run before importing the selected module or executing its setup code.
* Extend BuildClosureBlocker (or an equivalently narrow pre-import resolver) so tools.build.*, bare module names resolved under tools/build, aliases, and from-import forms share one closure predicate. A violation reports unqualified_tools_build_import_bypass with the selected test and resolved target path; it may not be converted into skip, warning, or adjacent-only status.
* Add negative fixtures for sys.path + bare import, aliased bare import, missing/untracked/ignored target, and import-time write side effects. Each must be rejected before the fixture's sentinel write. Add a positive fixture proving a tracked subprocess target remains legal without expanding the active-core/tooling allowlists.
* Rerun the complete live current-route selection after the refactor and runner hardening. The planning-time selection of 131 tests is evidence only; the execution report must bind the freshly selected denominator and show every selected test executed with no stored PASS substitution.
* Apply the same track, subprocess-refactor, or fail-closed rule to every additional dependency found by live recensus; no discovered bare import receives a one-off waiver.
* For each Registry-required evidence row, bind producer command, input hashes, output hash, consumer/gate, and fresh execution timestamp or content-addressed equivalent.
* A stored predecessor report may be consumed only as provenance. Final PASS requires a current-run receipt or a justified immutable-input revalidation bound to current hashes.
* Detect tests/runners that skip production when a stored final PASS exists. Such a test is regression evidence only unless the round forces a fresh isolated output or revalidates immutable content against current input hashes.
* generated staging output becomes durable only if the live required manifest adopts it and .gitignore/VCS preservation is explicit.
* Required durable paths must be present, tracked, and not ignored/effectively ignored.
* Timestamp-only churn must be normalized only through an existing approved normalization rule; do not silently drop semantic fields.
* Do not treat the live manifest generated_at value as freshness identity; it predates later additive rows. Freshness is content/input/producer/consumer hash-bound.
* Prepare an additive gate candidate after WP-1 through WP-7 machine inputs are stable.
* Avoid a self-reference cycle: the live manifest may require the phase4 Registry gate contract report and focused test, but must not require a phase5 final closure report whose production depends on that same current-route run.
* Keep the existing manifest container as legacy_combined_governance_route; this plan adds a Registry-axis gate and does not transfer manifest ownership.

Validation:

* required_manifest_current_checkout_bound = true
* required_artifact_denominator_matches_manifest = true
* required_test_denominator_matches_manifest = true
* required artifact existence/semantic check separation = true
* stored_pass_reuse_count = 0
* generated_staging_as_durable_evidence_count = 0
* dirty/untracked/ignored/missing required artifact count = 0
* required_test_dependency_unpreserved_count = 0
* selected_test_unqualified_tools_build_import_count = 0
* build_closure_bypass_fixture_preimport_rejection = true
* build_closure_bypass_fixture_sentinel_write_count = 0
* active_core_or_tooling_allowlist_expansion_count = 0
* completion_vocabulary_required_test_execution_mode = subprocess_fixture_check
* completion_vocabulary_stored_pass_early_return_count = 0
* completion_vocabulary_current_route_recursion_count = 0
* completion_vocabulary_fixture_check_repository_mutation_count = 0
* completion_vocabulary_fixture_check_completion_claim_count = 0
* completion_vocabulary_runner_implicit_all_default_allowed = false
* fresh_current_route_selected_test_execution_coverage = 1.0
* required_evidence_freshness_status = PASS
* candidate manifest override rejected
* current live manifest not yet changed until Change 7 adoption gate

---

### Change 5 - WP-5 Candidate Promotion and Seal/Cutover Contract

Purpose:

Define the only legal candidate-to-current promotion path, seal identity/receipt, cutover pre/postconditions, and rollback/historical preservation behavior without executing a live cutover.

Files:

* docs/registry_authority_seal_cutover_contract.md
* phase4/wp5_* contracts/reports
* staging-copy fixtures under phase4/wp5/
* manage_dvf_3_3_runtime_chunk_cutover.py as subprocess-reused tooling

Implementation Notes:

* Define candidate identity as a closed set of source/rendered/export receipt/runtime candidate/package projection hashes.
* Define promotion preconditions: role classification complete, no ambiguous/dual authority, fresh required evidence, candidate/live expected identity relation, protected dirty overlap zero, stale guard PASS, review input complete.
* Define the candidate-first promotion contract but keep its real current-context execution leg disabled. No free-standing current-regeneration exception exists, and this governance-only closure has no legal real current-protected writer callsite.
* Define WP-5 as the only fixture receipt issuer/consumer for contained guard tests. compose_layer3_text.py only verifies/consumes the fixture receipt and cannot issue it. Production/live receipt issuance is absent, and any future enablement requires the separately reviewed serialized operational cutover described in Change 1.
* Bind each fixture receipt nonce to an exclusive consumption marker under the verified evidence root. The marker is never cleared for retry; retry requires a new fixture receipt over freshly recaptured fixture preimages. Receipt/marker creation outside the evidence root or after a fixture target write is a contract violation.
* Positive tests use fixture_only=true receipts whose allowed roots are contained under phase4/wp5; the guard must reject every receipt against real protected paths. Record live_current_write_authorization_receipt_issued=false and production_real_path_receipt_acceptance_count=0.
* A precondition or postcondition delta keeps all delta bytes candidate-only and forbids current promotion outside this WP-5 seal/cutover contract. The contract must reject drifted-source current-context attempts before any live current-path write.
* Define seal receipt fields from roadmap-approved vocabulary only. Owner identity/sign-off fields must come from owner input, never generated defaults.
* Define cutover postconditions: one current identity, no partial current state, no live monolith, no old/new dual current, predecessor relation recorded, rollback snapshot historical-only.
* Validate candidate shape with manage_dvf_3_3_runtime_chunk_cutover.py --validate-candidate only.
* Do not invoke --snapshot, --apply, or --restore, even against a staging copy. Those modes perform copy/delete/replace mutations and are outside this governance-only closure.
* Prove that the contract/postcondition evaluator rejects partial and dual-current states, and that rollback artifacts remain historical-only, using static positive/negative fixtures and read-only state inspection.
* Do not claim that the existing sequential copy/delete cutover implementation is atomic. Operational atomic-apply verification belongs to a separate safe implementation/runtime-compatibility or live-migration scope.
* Never pass a live Iris media/data path to any mutating cutover mode in this round.
* A failed precondition leaves the candidate unadopted and current authority unchanged.
* A rollback snapshot cannot automatically reenter current authority.

Validation:

* candidate_promotion_contract_complete = true
* seal_identity_defined = true
* seal_receipt_schema_valid = true
* partial_cutover_allowed = false
* partial_state_rejected_by_contract = true
* dual_current_state_rejected_by_contract = true
* rollback_current_reentry_count = 0
* atomic_apply_verified = false / out_of_scope
* live_apply_executed = false
* live_repo_mutated = false
* current_context_real_path_route_enabled = false
* registry_fixture_write_receipt_issuer_count = 1
* registry_production_write_receipt_issuer_count = 0
* live_current_write_authorization_receipt_issued = false
* fixture_receipt_real_protected_path_authorization_count = 0
* drifted_source_current_context_promotion_allowed = false
* owner fields not tool-generated

---

### Change 6 - WP-6 Stale / Predecessor Reentry Guard

Purpose:

Prove that historical, diagnostic, fixture, quarantine, old monolith, stale bridge, predecessor chunk, rollback snapshot, current-looking stale path, and package fallback artifacts cannot reenter any current Registry surface.

Files:

* docs/stale_predecessor_reentry_guard_policy.md
* phase4/wp6_* reports
* existing predecessor-stale guard tooling/tests/fixtures
* new round-specific positive/negative fixtures where existing coverage is insufficient

Implementation Notes:

* Reuse existing stale guard classification and docs-claim scanner behavior through subprocess or stable read-only inputs.
* Guard current source, rendered, exporter/bridge, runtime, package, required manifest, and docs current-authority claim surfaces.
* Scan package source, isolated package projection, and any existing Iris/build/package snapshot without modifying them.
* Extend beyond the predecessor guard's fixed known roots: use the fresh WP-2 role ledger, current checkout tracked/untracked/ignored/dirty paths, and producer/consumer/readpoint references as the scan universe.
* Scan raw execution/read graphs for direct predecessor reads; do not accept a hardcoded zero report.
* Inspect ZIP entries and payload hash/content markers when an existing or isolated archive is present, so a renamed stale payload cannot evade filename-only checks.
* Distinguish actual current-authority overclaim from negation, quoted prior claim, and role-qualified historical/provenance mention.
* Include Korean, English, and mixed-language fixtures.
* Include dedicated negative fixtures for bare Registry PASS, Registry Authority PASS equated with Runtime Compatibility or Publish Boundary, and Registry Authority Closure equated with release readiness.
* Default deny unrecognized current-looking paths.
* Preserve quarantine/history; guard adoption does not authorize deletion.
* Any stale artifact found on a current path is a blocker and must be handled by a new correction scope, not silently relabeled.

Validation:

* stale_source_reentry_violation_count = 0
* stale_rendered_reentry_violation_count = 0
* stale_runtime_reentry_violation_count = 0
* stale_package_reentry_violation_count = 0
* current_looking_stale_path_count = 0
* package_fallback_forbidden_hit_count = 0
* required_manifest_predecessor_reentry_count = 0
* docs_current_authority_overclaim_count = 0
* historical/negated/quoted positive fixtures remain allowed

---

### Change 7 - WP-7 Registry Authority Claim Contract and Additive Required Gate

Purpose:

Fix the allowed and forbidden meanings of Registry Authority PASS and, after owner ratification and all WP checks, adopt a narrow fail-closed gate in the existing live current-route manifest.

Files:

* docs/registry_authority_claim_contract.md
* docs/dvf_3_3_registry_authority_canonical_closure_claim_boundary.md
* phase4/wp7_* reports
* current_route_required_validations.json
* .gitignore
* focused test and fixtures

Implementation Notes:

Allowed claim:

    Registry Authority PASS
    = artifact role classification complete
    + single current identity chain
    + required-validation ownership/freshness complete
    + seal/cutover contract complete
    + stale/predecessor reentry guard complete

Forbidden claims:

    Registry PASS
    DVF PASS
    DVF System PASS
    Legacy Combined DVF Governance Route PASS == Registry Authority PASS
    Registry Authority PASS == Registry Runtime Compatibility PASS
    Registry Authority PASS == Publish Boundary PASS
    Registry Authority PASS == input facts factual approval
    Registry Authority PASS == semantic quality approval
    Registry Authority PASS == runtime consumer behavior guarantee
    Registry Authority PASS == package publication readiness
    Registry Authority PASS == public text acceptance
    Registry Authority PASS == manual QA complete
    Registry Authority Closure == release readiness

* Use axis-qualified completion vocabulary throughout machine and docs surfaces.
* Scanner is lexical/contract validation, not semantic quality or public text acceptance.
* Focused current-route test must launch the new runner/validator as a subprocess; it must not import the new tool through current build closure.
* Keep round3_active_core_closure.json and its current tooling allowlist unchanged.
* Generate phase4/wp7_registry_authority_required_gate_contract_report.json before adoption. It is an immutable, non-self-referential machine contract report and must not contain a live-adoption or canonical-seal claim.
* Add only that minimum phase4 gate contract report and the subprocess-based focused test needed to block future overclaim/reentry/freshness regression.
* Do not add the phase5 self-dependent final closure report to the live manifest.
* Produce a candidate manifest patch and validate it against a copy before requesting adoption authority. Entry-time D6 ratifies only the mandatory-adoption policy; it is not authorization for an unknown future diff. The owner must then author current_session_required_gate_adoption_authorization_record.json at the reserved gate_adoptions path. That one-use record binds owner identity/time, decision=adopt_exact_candidate_once, allowed target path, candidate artifact path/hash, base live-manifest hash, canonical additive diff hash, and the gate contract report path/hash. It is intentionally downstream of Phase 3 and does not rewrite D0-D10 or the reviewed bundle.
* adopt-gate must validate and byte-identically materialize that record as phase4/wp7_required_gate_adoption_authorization_record.json, rehash the live base, candidate, canonical diff, and contract immediately before writing, and require exact parity. Any absent/stale/replayed/wrong-target/wrong-hash record fails before mutation. Successful adoption consumes the authorization once and records its hash in wp7_required_validation_additive_gate_record.json.
* Required-gate adoption is conditional across execution outcomes: it may remain unapplied only when the final outcome is implemented_only, partial, or blocked. It is mandatory, freshly rerun-bound, and non-waivable for Registry Authority Closure = canonical_complete.
* Manifest removal/modification of predecessor required rows is forbidden.
* Add exact .gitignore rules only for the new tool/test/fixture and the minimum required evidence adopted by the live manifest.
* Run current route after live adoption. A failure propagates as failure.
* required_gate_adopted=true is a governance-gate fact, not Registry Authority canonical closure by itself.

Validation:

* registry_authority_claim_contract_complete = true
* forbidden_claim_hit_count = 0
* axis_qualified_completion_vocabulary_enforced = true
* live manifest diff is additive-only
* candidate_specific_gate_adoption_authorization_valid = true
* generic_D6_policy_used_as_candidate_authorization_count = 0
* gate_adoption_authorization_materialization_byte_identity = true
* gate_adoption_authorization_replay_count = 0
* predecessor required artifact/test removal count = 0
* round3 active core count unchanged
* current-route tooling allowlist unchanged
* current route PASS after adoption
* canonical_complete_without_required_gate_adoption_allowed = false
* gate does not claim Runtime Compatibility, Publish Boundary, package/release readiness, or public acceptance

---

### Change 8 - Final Rerun, Independent Review, Owner Seal, and Closeout

Purpose:

After the last implementation/config change, rerun every required validation, bind claim-bearing artifacts and validation results by hash, obtain eligible external independent review and owner seal, then apply and validate the final top-doc trace under the selected Option B DAG before closing the Registry parent problem.

Files:

* phase5/* final validation/review/seal artifacts
* closeout/ledger/top-doc draft docs
* owner input records
* final protected/VCS recensus

Implementation Notes:

* Freeze the implementation tree after Change 7 and record its path/hash manifest. Under selected Option B, mutable top docs docs/DECISIONS.md, docs/ARCHITECTURE.md, docs/ROADMAP.md and the three post-external D7 update drafts are excluded from the implementation freeze; the freeze binds top-doc baseline hashes, allowed draft paths, and the D7 application policy instead. No other frozen implementation/config path may change after this point.
* Rerun census, role classification, identity binding, freshness, seal/cutover fixtures, stale guard, claim guard, every WP focused test, gate-candidate validation, post-adoption current route, VCS checks, protected-surface checks, package identity probe, and the adjacent regression matrix from scratch.
* Produce final_command_matrix_report.json and final_validation_failure_attribution_report.json even on failure. Preserve WP/phase ownership for every failed or skipped command, and forbid an aggregate PASS/FAIL that cannot identify the originating WP and first failing predicate.
* final-rerun produces and freezes post_external_required_consumer_manifest.json before the machine report as the immutable denominator of all top-doc-dependent reruns. Each row binds command_id, WP owner, exact argv, required input surface, expected output path, and blocking status; the machine report, independent review bundle, and owner seal input manifest bind its hash. post-external is the sole producer of the corresponding coverage report.
* Do not reuse earlier PASS output as the final result.
* Bind each claim-bearing artifact and validation report by repo-relative path + SHA-256.
* Select review Option B and use this acyclic seal order:

      implementation tree + top-doc baseline hashes + D7 policy
      -> implementation_freeze_manifest (mutable top docs excluded)
      -> final fresh validations + final_validation_hash_binding_report
         + final command/failure-attribution reports
         + post_external_required_consumer_manifest
      -> final_registry_authority_machine_report
      -> external independent review input
      -> byte-identical phase5 independent review materialization
      -> external owner seal input
      -> byte-identical owner_canonical_seal_record
      -> owner-applied final top-doc append
      -> post_external_consumer_coverage_report
      -> post_external_gate_validation_report
      -> finalize: final_registry_authority_closure_report
      -> finalize: docs/dvf_3_3_registry_authority_canonical_closure_ledger_packet.md
      -> finalize: docs/dvf_3_3_registry_authority_canonical_closure_closeout.md
      -> finalize: final_artifact_hash_manifest
      -> terminal_hash_seal

* final_artifact_hash_manifest excludes itself and the not-yet-created terminal_hash_seal; terminal_hash_seal binds the final artifact manifest hash and excludes only itself. Both record those rules. The terminal seal thereby binds every prior claim-bearing artifact plus the final owner-applied top-doc hashes; no claim-bearing file or bound top doc may change afterward except through correction-only reopening.
* Generate the machine closure report before independent review. It may claim machine_pass_governance_only but must keep canonical_seal_allowed=false until external gates validate.
* Independent reviewer must author the review only at the reserved external independent_reviews path and bind reviewer identity/scope, reviewed artifact manifest hash, rerun result hashes, findings, and verdict. phase5/independent_closeout_review.md must be byte-identical to that input; tooling may copy/validate but may not author, default, summarize, or alter it.
* Owner seal input manifest must bind the machine report, independent review artifact, post_external required-consumer manifest, top-doc baseline hashes, allowed D7 target/draft paths, and the selected Option B policy. It intentionally cannot bind not-yet-applied final top-doc hashes; terminal_hash_seal binds those after post_external validation. Tooling validates but does not author the owner seal.
* Materialize phase5/owner_canonical_seal_record.json byte-for-byte from the validated external owner input and record both hashes.
* final Registry Authority canonical claim requires machine PASS, independent review PASS, owner seal PASS, owner-ratified vocabulary, required gate adoption, top-doc sync, and zero blockers as separate axes.
* Apply final top-doc content only after the owner seal materialization validates. Tooling may prepare a draft from already validated machine/review/owner facts, but it cannot apply the draft or invent a verdict; the owner must author or ratify and apply it.
* Post-external top-doc application is additive only. Existing sealed DECISIONS body byte changes must be zero. The append records the validated final verdict trace and stable round/closeout paths without predicting the not-yet-created terminal hash.
* After top-doc application, rerun every consumer whose input universe includes top docs: dirty/additive diff guards, sealed-body immutability, WP-6 docs authority-claim scan, WP-7 vocabulary/non-claim scan, required current route, VCS preservation, and final top-doc hashes. Any failure blocks finalization; the owner seal is not a waiver.
* --require-post-external must compare the immutable required-consumer manifest and coverage report one-to-one, require every blocking row to have a fresh post-application receipt with exit_code=0, prove each receipt binds the applied top-doc hashes, and reject missing, duplicated, stale, reordered-to-bypass, or not_run rows. finalize must refuse to run unless this predicate passes; --require-terminal-seal --no-write recomputes it rather than trusting the stored PASS.
* Because top docs are dirty at planning time, execution must recapture overlap and stop rather than overwrite concurrent/user changes.
* final_registry_authority_closure_report.json must reference, not redefine, each sealed axis.
* finalize is the sole producer mode for phase5/final_registry_authority_closure_report.json, docs/dvf_3_3_registry_authority_canonical_closure_ledger_packet.md, and docs/dvf_3_3_registry_authority_canonical_closure_closeout.md. It creates them in that order after post_external PASS, then creates final_artifact_hash_manifest.json over those artifacts, and creates terminal_hash_seal.json last. The ledger packet and closeout must exist, be selectively tracked, and be hash-bound before terminal seal creation.
* Run --require-final-inputs before top-doc preparation, then --require-post-external after owner application and the affected-consumer rerun. Only then may finalize generate the ordered artifacts above. A final --require-terminal-seal --no-write check is the last command and may not mutate the sealed DAG.
* Exact-unignore and git ls-files validation of the mandatory selective-tracked closeout set is required independently of live-manifest adoption.
* Set successor_registry_authority_round_required=false only when unresolved/deferred/pending/blocker counts are all zero.
* Reopening after canonical closeout is correction-only and requires new evidence.

Validation:

* final_validation_rerun_after_last_implementation_change = true
* final_rerun_wp_focused_test_coverage = complete
* final_rerun_gate_candidate_validation_coverage = complete
* final_rerun_post_adoption_current_route_coverage = complete
* final_validation_failure_attribution_status = PASS
* unattributed_failure_count = 0
* stored_pass_reused_for_final_completion = false
* final_artifact_hash_bound = true
* final_validation_result_hash_bound = true
* current_route_validation_status = PASS
* protected_surface_mutation_count = 0
* registry_blocker_count = 0
* independent_closeout_review_status = PASS
* independent_review_external_materialization_byte_identity = true
* reviewed_artifact_hash_coverage = complete
* mandatory_selective_tracked_closeout_unpreserved_count = 0
* owner_seal_status = PASS
* canonical_seal_status = PASS
* canonical_seal_allowed = true
* top_doc_dag_option = post_owner_seal_application
* top_doc_sync_state = owner_applied_and_validated_post_external
* post_external_top_doc_affected_consumer_rerun_status = PASS
* post_external_required_consumer_denominator_frozen = true
* post_external_required_consumer_manifest_producer_mode = final-rerun
* post_external_consumer_coverage_report_producer_mode = post-external
* post_external_required_consumer_missing_or_stale_count = 0
* post_external_stored_pass_trusted_without_recompute = false
* final_registry_authority_closure_report_producer_mode = finalize
* ledger_packet_producer_mode = finalize
* closeout_producer_mode = finalize
* ledger_packet_and_closeout_precede_terminal_hash_seal = true
* unresolved/deferred/pending Registry required item count = 0
* successor_registry_authority_round_required = false
* terminal_hash_seal_status = PASS

---

## 7. Validation Plan

### Automated Validation

The future execution command order is part of the contract. Every command below runs from the repository root of the D9 owner-approved dedicated clean execution worktree; running the matrix from the original dirty checkout is invalid evidence.

Before command 1, the bounded Entry scaffold, final roadmap/plan, and owner-accepted pre-existing state are committed without any WP/current-writer/gate-adoption/finalization implementation. The scaffold implements only preflight, byte-identical Phase 3 review materialization, and the three read-only Entry validators listed in steps 1-2. The owner designates that commit, creates the dedicated worktree, records its empty status in the external clean-worktree checkpoint, registers a new attempt_id/root with predecessor failure preservation, then authors D10 over the exact plan/scaffold/checkpoint/attempt/roadmap hashes and base commit. Only the exact reserved external inputs may be placed in the worktree after that checkpoint. These are owner actions, not runner automation. Preflight must reject any other post-checkpoint delta, reused attempt_id, or existing attempt output before writing evidence.

### Validation Triage

| Class | Commands/predicates | Effect |
|---|---|---|
| Blocking validation | D10 plan/base-commit approval and clean-worktree isolation; Execution Entry Gate; current-checkout recensus including malformed-manifest consumer disposition; authenticated current-writer guard; required-test dependency/bare-import closure; WP-1..WP-7 focused validation; body_plan location/coverage; gate-candidate and additive adoption; required current route; exact package identity projection; protected no-mutation; VCS preservation; final hash binding; external independent review/owner seal materialization; post-external top-doc validation | Any failure forbids canonical_complete. No stored result or owner seal may waive it. |
| Adjacent regression validation | Related historical guard/authority/freshness/runtime/package tests in step 6 and unconditional Lua syntax check | Run and record separately so their role is not confused with a closure predicate. A failure that intersects a protected/required surface becomes blocking; a proven unrelated pre-existing failure must be explicitly dispositioned and may not be reported as PASS. |

The exact package probe identity predicate is blocking because this closure claims a runtime-package identity pipeline. Broader package readiness/publication behavior remains outside scope. Lua syntax runs unconditionally as adjacent no-mutation reinforcement; it is not runtime behavior proof. Its script/luac/input-set capability is therefore checked at Execution Entry rather than discovered late: missing or changed capability is environment_blocked, and provisioning luac is an explicit operator prerequisite outside this runner.

Every validation report uses the same attribution vocabulary: preimplementation_review, wp1 through wp7, adjacent_regression, independent_review, owner_seal, post_external, and finalize. final_command_matrix_report.json contains one row per expected command; final_validation_failure_attribution_report.json groups failed and not-run rows by that owner. report_status=PASS is forbidden when unattributed_failure_count or missing_expected_command_count is nonzero.

1. Scaffold/preflight:

       uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --mode preflight
       uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --require-preflight

   Preflight now publishes the immutable reviewed-bundle hash and stops:

       [STOP — THREE EXTERNAL PREIMPLEMENTATION REVIEWS REQUIRED; THIS IS NOT A SHELL COMMAND]
       The designated reviewers author the responsibility-boundary, authority/evidence-integrity, and adversarial/failure-mode reviews only at their three reserved input paths.
       [RESUME ONLY AFTER ALL THREE REVIEWS BIND THE PUBLISHED BUNDLE HASH]

2. Materialize the three reviews and validate the Execution Entry Gate. This must confirm byte-identical review/checkpoint/D10 materializations, plan/entry-scaffold/checkpoint/base-commit parity, no unapproved post-checkpoint delta, clean-worktree isolation, Critical=0 and Important=0 in the fresh consolidated Phase 3 review, and resolved/hashed tools/check_lua_syntax.ps1 plus luac and its non-empty input set before any WP mode:

       uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --mode materialize-preimplementation-reviews
       uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --require-preimplementation-reviews
       uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --require-execution-entry

3. Focused test before implementation:

       uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_registry_authority_canonical_closure.py"

4. WP implementation only; this mode must not adopt the live gate or emit final/machine/canonical closure:

       uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --mode implementation

5. Implementation validation:

       uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --require-implementation

6. Preliminary adjacent regression matrix:

       uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_current_route_authority_required_evidence_integrity_closure.py"
       uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py"
       uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_predecessor_stale_artifact_reentry_guard.py"
       uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_runtime_payload_state_integrity.py"
       uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_lua_bridge_export_contract_realign.py"
       uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_layer3_data_chunking_contract.py"
       uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_package_layer3_chunks_only_contract.py"
       uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_current_authority_source_path_guard.py"
       uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_compose_entrypoint_guard_hardening.py"
       uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_vnext_current_authority_chain_successor_readpoint_seal.py"
       uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_core_registry_boundary_claim_contract_closure.py"
       uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_dvf_system_naming_realignment.py"
       uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py"

7. Preliminary isolated package identity probe, only after runner containment proof:

       powershell -ExecutionPolicy Bypass -File ./Iris/tools/package_iris.ps1 -OutputRoot ./Iris/build/description/v2/staging/dvf_3_3_registry_authority_canonical_closure/attempts/<attempt_id>/phase4/wp3/package_probe -Clean

8. Build and validate the non-self-referential gate candidate:

       uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --mode gate-candidate
       uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --require-gate-candidate

9. After gate-candidate validation, stop for the candidate-specific external D6 authorization. The owner-authored record must bind the exact candidate/base/diff/contract hashes; the entry-time generic D6 policy value is insufficient. Only then apply the additive gate and run the current route immediately:

       [STOP — EXACT REQUIRED-GATE CANDIDATE AUTHORIZATION REQUIRED; THIS IS NOT A SHELL COMMAND]
       The owner authors only Iris/build/description/v2/owner_inputs/dvf_3_3_registry_authority_canonical_closure/gate_adoptions/current_session_required_gate_adoption_authorization_record.json.
       [RESUME ONLY AFTER THE RECORD BINDS THE VALIDATED CANDIDATE/BASE/DIFF/CONTRACT HASHES]

       uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --mode adopt-gate

       uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --out Iris/build/description/v2/staging/dvf_3_3_registry_authority_canonical_closure/attempts/<attempt_id>/phase4/wp7_post_adoption_current_route_validation_result.json

10. After the last code/config mutation, create the implementation freeze with actual top docs excluded under Option B. The final-rerun mode must execute WP-1..WP-7 focused checks, both gate-candidate commands from step 8, the post-adoption/current-route check, every exact adjacent-test command from step 6, deterministic census under its same-state predicate, and the protected/VCS checks into fresh phase5 evidence. Missing command-matrix rows are blocking:

       uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --mode final-rerun
       uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --require-gate-candidate
       powershell -ExecutionPolicy Bypass -File ./Iris/tools/package_iris.ps1 -OutputRoot ./Iris/build/description/v2/staging/dvf_3_3_registry_authority_canonical_closure/attempts/<attempt_id>/phase5/package_probe -Clean
       uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --out Iris/build/description/v2/staging/dvf_3_3_registry_authority_canonical_closure/attempts/<attempt_id>/phase5/current_route_validation_result.json
       uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_registry_authority_canonical_closure.py"
       powershell -ExecutionPolicy Bypass -File ./tools/check_lua_syntax.ps1
       uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --require-machine-complete

11. Obtain and materialize the external independent review, then obtain and materialize the external owner seal. The reviewer writes only the reserved independent_reviews input; the owner writes only the reserved owner_seals input. Materialization must be byte-identical and no tool may synthesize, summarize, default, or alter either verdict:

       uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --mode materialize-independent-review
       uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --require-independent-review
       uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --mode materialize-owner-seal
       uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --require-final-inputs

12. Only after owner seal validation, prepare the final additive top-doc draft from already validated facts, obtain owner authorship/ratification and application, then rerun all top-doc-dependent consumers inside post_external_gate:

       uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --mode prepare-top-docs
       [STOP — OWNER ACTION REQUIRED; THIS IS NOT A SHELL COMMAND]
       Owner authors/ratifies and applies the three additive top-doc drafts.
       [RESUME ONLY AFTER OWNER APPLICATION IS PRESENT IN THE WORKTREE]
       uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --require-top-doc-owner-application --no-write
       uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --out Iris/build/description/v2/staging/dvf_3_3_registry_authority_canonical_closure/attempts/<attempt_id>/phase5/post_external_current_route_validation_result.json
       uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --mode post-external
       uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --require-post-external

13. Finalize the closure DAG. finalize must produce final_registry_authority_closure_report.json, ledger packet, closeout, final_artifact_hash_manifest.json, and terminal_hash_seal.json in that order; then perform a read-only terminal verification:

       uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --mode finalize
       uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_authority_canonical_closure.py --attempt-id <attempt_id> --require-terminal-seal --no-write

Additional machine checks:

* jq parse/schema checks for all JSON/JSONL contract artifacts
* --mode all and unlisted stage-aggregating aliases rejected with nonzero exit and zero writes
* expected command matrix complete and every failure/not-run row attributed to one WP/phase owner
* deterministic census rerun only under same HEAD, same normalized dirty set, and unchanged required/protected surfaces; otherwise recapture and restart both runs
* git check-ignore -v for every new durable path
* git ls-files and git status --porcelain=v1 VCS preservation recensus
* byte-identical clean-checkpoint/implementation-plan approval materialization, exact approved plan/entry-scaffold/checkpoint hash parity, and approved base-commit/entry-worktree HEAD parity
* execution-worktree checkpoint cleanliness, post-checkpoint external-input-only delta, and original dirty-checkout no-tool-mutation proof
* one-to-one original dirty-path disposition, accepted-row tree-hash parity, and excluded-row no-leak proof with no broad waiver
* pre/post SHA-256 comparison for protected source/rendered/Lua/runtime/package-source surfaces
* exact set equality between the plan-mapped protected/identity-bearing denominator and preflight/Entry/final no-mutation rows
* additive-only diff scan for current_route_required_validations.json
* candidate-specific gate-adoption authorization byte identity, base/candidate/diff/contract hash parity, allowed target, and one-use consumption
* additive-only/sealed-body immutability scan for DECISIONS.md
* exact current core/tooling allowlist comparison
* completion-vocabulary fresh subprocess fixture-check, no stored-PASS/recursive route, explicit-mode/no-repository-write, dependency closure, and exact selective-tracking proof
* current-route pre-import negative fixtures for sys.path/bare/aliased tools/build imports, including zero sentinel writes
* no-arg/default current writer, any receipt against a real protected path, invalid/replayed fixture receipt, fixture-receipt/live-path, and staging-output guard fixtures with zero real protected mutations
* WP-3 staging-context direct-compose current-input manifest parity; current-context plus ordinary staging path remains rejected
* round3_contract_manifest.json producer/consumer graph, diagnostic exclusion, no-reentry fields, malformed-byte hash, and no-mutation proof
* approved roadmap payload hash versus consumed_roadmap_hash comparison, including strict diff-scope approval validation
* roadmap diff-scope approval has exact diff hash/hunks, no wildcard/broad waiver, and no material-contract hunk
* body_plan physical authority location and input/output hash-coverage predicate
* byte identity, reviewed-bundle hash, author provenance, and no-tool-authored-verdict checks for all three Phase 3 review materializations
* fresh external review-source reparse/count recomputation and negative forged blocker-zero/stored-projection bypass fixtures
* Entry-time fresh protected-row/hash parity against Phase 0 and the reviewed bundle, including ignored output/package drift fixtures
* byte identity and hash validation for external independent review and owner seal materializations
* Option B top-doc ordering check: application after owner seal, immutable required-consumer denominator, one-to-one fresh post-external coverage, final top-doc hashes bound by terminal_hash_seal, and post-seal claim-bearing mutation count 0
* Lua checker script/luac path/version/hash/input-set parity with Phase 0 environment preflight
* negative fixtures for dual authority, candidate-as-current, unauthenticated/drifted-source current-context attempts, forged/stale/replayed current-write receipts, bare-import closure bypass, stale reentry, partial cutover, stored PASS reuse, self-reference, owner/reviewer substitution, and forbidden claim aliases

No validation is reported as PASS unless the exact command exits with code 0.

### Manual Validation

* Review a sample from every artifact role and every scan-admission rule.
* Inspect every ambiguous/excluded candidate and confirm the final count is zero.
* Confirm the clean-checkpoint and D10 external bytes equal their Phase 0 materializations, D10 binds the exact executed plan/entry-scaffold/checkpoint hashes and worktree base commit, and approval was authored after the final plan and entry-scaffold baseline were fixed.
* Confirm the scaffold-bearing worktree was clean at the owner checkpoint, only exact reserved external inputs appeared before preflight, every command ran there, and the original dirty checkout was neither normalized nor mutated by tooling.
* Confirm each Phase 3 review was externally authored after the preflight bundle hash existed, binds that exact bundle, is byte-identically materialized, and contributes every finding unchanged to the consolidated blocker table.
* Inspect every original dirty-path disposition: accepted rows match the execution-base tree, excluded rows remain outside execution, and no wildcard/broad owner acceptance exists.
* Confirm package probe OutputRoot containment before -Clean execution.
* Inspect live-vs-candidate chunk identity and package projection reports.
* Confirm WP-3 used compose_context=staging, all six explicit inputs matched the current input manifest, and no current-context/staging-path bypass was introduced.
* Confirm current body_plan Case A: compose_profiles_v2.json plan-spec coverage and rendered entries[*].body_plan instance coverage; if repository shape changed, require Case B binding or block.
* Inspect required-manifest diff for additions only and absence of final-report self-reference.
* Inspect .gitignore diff for exact-path preservation and absence of broad unignore.
* Inspect final command/failure-attribution reports and confirm every failed/not-run row identifies one WP/phase owner and first failing predicate.
* Confirm round3_active_core_closure.json and tooling allowlist are unchanged.
* Inspect the completion-vocabulary test/runner and current-route loader to confirm the known bare-import, stored-PASS early return, implicit all default, and recursive current-route path were removed from required execution; verify fixture-check is contained/fresh and all subprocess targets/fixtures are selectively tracked.
* Inspect the compose entrypoint guard and WP-5 receipt contract to confirm a no-arg/default current-path call cannot write, every real-path receipt is rejected, fixture receipts cannot authorize real protected paths, and operational current-write enablement is deferred to a separately reviewed serialized cutover.
* Confirm the D6 post-candidate authorization record is externally owner-authored, byte-identically materialized, and binds the exact candidate/base/diff/contract hashes and one allowed target before adopt-gate.
* Confirm round3_contract_manifest.json remains byte-identical, has a proven zero-consumer graph, is diagnostic-only, and is excluded from authority/current/package input denominators; otherwise require blocker status.
* Inspect Korean/English/mixed-language claim fixtures for false positive/negative behavior.
* Confirm Option B ordering: owner seal validated before top-doc application, top-doc changes additive, affected consumers rerun afterward, and terminal seal binds final hashes without overwriting pre-existing dirty work.
* Confirm the post_external required-consumer manifest was frozen before machine review and has exact one-to-one fresh coverage after owner application.
* Confirm independent reviewer eligibility, reserved external input path, byte-identical phase5 materialization, scope, artifact hash coverage, and verdict.
* Confirm owner decision and seal records are externally supplied and hash-bound.
* Confirm approved roadmap hash equals consumed_roadmap_hash or inspect the exact owner no-material-effect diff-scope approval, including diff hash, every hunk, and absence of wildcard/material-contract changes.
* Confirm ledger packet and closeout report producer_mode=finalize and both hashes precede terminal_hash_seal.
* Confirm the Phase 0 Lua capability record and final luac/script/input-set identity match.
* Confirm final non-claims are present in machine report, owner seal input, closeout, and top-doc update.

### Validation Limits

Validated by this plan when closeout_state=complete:

* Registry artifact census and role classification
* current identity chain binding
* required-validation ownership/freshness
* candidate/promotion/seal/cutover contract
* stale/predecessor reentry guard
* claim vocabulary boundary
* VCS preservation
* protected-surface no-mutation
* governance current-route regression
* independent review/owner seal/hash binding

Out of scope:

* runtime consumer behavior/equivalence
* manual in-game, multiplayer, long-session validation
* package publication/install/deployment validation
* release/Workshop/B42 readiness
* public text/semantic quality acceptance
* Registry Runtime Compatibility Closure
* Publish Boundary Closure
* operational/live cutover atomicity and apply/restore behavior
* external ecosystem compatibility sweep
* full historical byte reproducibility

Unvalidated but in scope:

* Must be empty for closeout_state=complete.
* If non-empty, record each item and use partial, implemented_only, or blocked. Do not claim Registry Authority Closure canonical_complete.

---

## 8. Risk Surface Touch

### Authority Surface

Touched.

This execution establishes the Registry Authority Closure readpoint, artifact role ownership, identity-chain binding, required-validation ownership/freshness, promotion/seal/cutover contract, stale guard, and claim boundary. It must not move DVF System, Registry Runtime Compatibility, or Publish Boundary responsibilities.

### Runtime Behavior Surface

None intended.

Runtime Lua and current chunks are read-only validation inputs. Any runtime mutation is a fail-closed scope violation.

### Compatibility Surface

None intended.

Public require contract, external format, SPI/API, runtime consumer contract, and package format remain unchanged. Isolated package probing validates identity only.

### Sealed Artifact Surface

Touched.

The round adds governance contracts, required-gate evidence, review/hash/owner seal artifacts, and additive top-doc entries. Existing sealed artifacts remain immutable historical/predecessor inputs.

### Public-Facing Output Surface

None.

Browser/Wiki/Tooltip output, public text, release notes, Workshop/package publication, and user-visible runtime behavior are not changed or accepted.

---

## 9. Risk Analysis

### Architecture Risk

* Registry responsibilities may be reabsorbed into DVF System.
* Registry Authority PASS may be confused with Runtime Compatibility or Publish Boundary PASS.
* A combined current-route manifest may be mistaken for meaning authority.
* New tooling may accidentally become a current build core dependency.
* A required test may import an ignored tools/build module through a sys.path bare-import bypass and appear preserved when it is not.
* An aggregate orchestration mode could cross owner/reviewer gates or obscure the actual failing WP.
* A package identity projection may be mistaken for package authority/readiness.

Mitigation:

* handoff/claim contracts, no closure-stage all/aggregate mode, WP-attributed command reports, subprocess-only completion-vocabulary integration, pre-import bare-module resolution, selectively tracked dependency closure, unchanged active-core/tooling allowlists, explicit non-claims, and independent boundary review.

### Runtime Risk

* A misconfigured exporter, cutover fixture, or package probe could write to live paths.
* The observed default current writer could be misread as an authorized regeneration exception and bypass candidate promotion.
* A forged, stale, or replayed authorization receipt could widen a protected write.
* -Clean on an unverified OutputRoot could remove unintended generated output.
* Stale bridge/monolith data could reenter runtime/package paths.

Mitigation:

* resolved-path containment checks, staging-only bridge output, no live apply, plan-complete protected hashes, unconditional real-current-path rejection, contained fixture-only receipts, no-arg/forged/replay/real-path negative fixtures, and stale/package fail-closed scans.

### Compatibility Risk

* The plan could silently change public require or package selection behavior.
* Existing package scripts could be modified under the guise of identity validation.

Mitigation:

* package/exporter/runtime code is read-only, public contract is hashed, and compatibility claims are excluded.

### Regression Risk

* Live manifest denominator may drift during execution.
* Stored PASS or stale inventory may be reused.
* New required artifacts may remain ignored/untracked.
* Final validation may be invalidated by a later doc/config change.
* Claim scanner may misclassify quoted/negated/historical wording.
* Final report may enter a self-reference hash cycle.
* Pre-existing top-doc/staging changes may be overwritten or absorbed.
* A dirty checkout or an owner-unapproved base commit may make otherwise passing evidence irreproducible.
* A post-approval plan edit, pre-Entry scaffold drift, or fabricated clean checkpoint may silently change the execution contract.
* A Phase 3 review may be self-generated, stale, or bound to a different plan/scaffold bundle.
* The malformed round3 contract manifest may be repaired or reintroduced without proving its consumer role.
* Approved roadmap drift, unbound body_plan authority, or a self-generated independent review could create a false closure.
* A missing post_external consumer row or late Lua environment failure could make terminal diagnosis ambiguous.

Mitigation:

* dedicated owner-approved scaffold-bearing worktree, external empty-status checkpoint, byte-identical plan/scaffold/checkpoint approval, explicit Phase 3 STOP/materialization with exact bundle binding, stale-on-any-bound-change rule, same-state deterministic recensus, malformed-manifest zero-consumer graph/no-reentry disposition, WP-attributed failures, frozen post_external consumer denominator with exact coverage, early Lua capability preflight, final implementation rerun, Option B post-owner-seal top-doc application plus affected-consumer rerun, minimum VCS preservation, multilingual fixtures, self-reference exclusion rule, roadmap-hash parity, explicit body_plan coverage, and byte-identical external independent review materialization.

---

## 10. Rollback Plan

Rollback is governance-scoped containment, not destructive cleanup.

The governing retry rule is:

> 같은 cycle의 새 attempt는 허용하되, 같은 attempt의 claim-bearing 산출물 덮어쓰기, 실패 이력 삭제, receipt 재사용은 금지한다.

| State | Same-cycle retry | Required boundary |
|---|---|---|
| gate 채택 전, protected mutation 없음 | 허용 | 새 attempt_id, 새 attempt output root, 이전 실패 기록 보존 |
| candidate/fixture 생성 실패 | 허용 | candidate 폐기 또는 supersede, 새 attempt_id와 새 nonce 사용 |
| receipt nonce 소비 후 | 동일 attempt 재시도 금지 | 새 receipt, 새 nonce, 새 attempt 필요 |
| live gate 채택 또는 top-doc 반영 후 | 단순 재시도 금지 | additive correction/supersession 기록과 affected consumer 재실행 |
| plan/roadmap/base/checkpoint/scaffold 변경 후 | 기존 attempt 증거 재사용 금지 | 새 clean checkpoint, 새 attempt registration, D10 재승인, 필요한 fresh review |

1. Before live required-gate adoption, supersede or remove only unsealed round-owned candidate/fixture/draft bytes inside the active attempt and leave every protected source/rendered/runtime/package surface untouched. Attempt logs, failure JSON, materialized reviews, command receipts, and other claim-bearing outputs are never removed or rewritten.
2. Verify every candidate/fixture cleanup target resolves inside the active attempt root before deletion. The attempt root itself and predecessor attempt roots are immutable audit records and are never recursive-cleanup targets.
3. Remove only the round-specific exact .gitignore entries when their corresponding artifacts are removed. Do not alter unrelated ignore rules.
4. If a candidate manifest patch fails, record the failure, discard or supersede only that candidate, keep the live manifest unchanged, and use a new attempt_id for another candidate.
5. After a live required gate has been adopted, silent removal is forbidden. Use an additive correction/supersession record, preserve predecessor trace, and rerun the current route.
6. Before owner application, top-doc drafts may be superseded. After the Option B post-external append, owner-applied DECISIONS entries are never deleted; append a correction entry and reopen only through the correction contract.
7. Stale/predecessor/quarantine artifacts are not deleted as rollback. Their current-reentry prohibition remains.
8. Isolated bridge/package/cutover fixtures may be regenerated or removed only inside their verified attempt root before claim sealing; retry uses a new attempt_id and preserves the failed attempt record.
9. Restore no old monolith, stale bridge, predecessor chunks, or rollback snapshot as current authority.
10. Preserve the original dirty checkout byte-for-byte. Abandoning or removing a failed dedicated worktree must not reset, clean, stash, commit, or merge the original checkout automatically.
11. A plan/roadmap/checkpoint/base change or pre-Entry scaffold drift invalidates D10 and every downstream artifact of that attempt; preserve that attempt, establish a new clean checkpoint and attempt registration, reapprove, and rerun in a new attempt root rather than patching recorded hashes. A post-Entry implementation rollback keeps the approved scaffold baseline immutable and records a new before/after implementation diff in the new attempt.
12. Preserve the malformed round3 contract manifest bytes during rollback. Its diagnostic/no-reentry disposition remains in force unless a separately authorized correction proves and repairs a live consumer.
13. Revoke unused fixture receipt nonces after a failed attempt. Once a nonce is consumed, the same attempt may not retry that action; a new attempt requires a newly issued receipt and nonce. Never reuse a receipt or treat a fixture receipt as recovery or real-current-path authorization.
14. If protected surface mutation, dual current state, partial cutover, stored PASS reuse, stale promotion, unpreserved dependency, or non-Registry blocker is detected, stop with partial/blocked and document the evidence.
15. A failed Registry closure does not return Registry responsibility to DVF System.

Rollback success conditions:

* protected source/rendered/Lua/runtime/package-source mutation = 0
* current route remains at its pre-round state or is additively corrected
* no dual current authority
* no stale/predecessor promotion
* round failure and ceiling documented
* cycle_id and attempt_id separately recorded
* predecessor attempt failure records preserved and hash-addressable
* same-attempt claim-bearing overwrite count 0
* original dirty checkout preserved and runner mutation count 0
* no authorization receipt replay or real-path fixture authorization

---

## 11. Governance Constraints

* Philosophy.md compliance is mandatory.
* Hub & Spoke and Iris module-role boundaries remain unchanged.
* DVF System responsibility ceiling ends at approved facts/decisions/profile/body_plan -> rendered 3-3 body.
* Iris Artifact Registry owns artifact role/lifecycle/authority and runtime-package identity pipeline.
* Registry Runtime Compatibility and Publish Boundary remain separate.
* Runtime/build-time separation is mandatory.
* Runtime Lua does not validate source or regenerate descriptions.
* Source facts/decisions/overlay, rendered content, live bridge/runtime chunks, and live package payload are protected read-only surfaces.
* No free-standing current-regeneration exception exists. compose_layer3_text.py must reject every resolved real current-protected output before writes in this closure, regardless of receipt. Any future legal regeneration requires a separately reviewed Registry operational-cutover scope with candidate-first parity, exact owner authorization, full-target serialization, under-lock preimage revalidation, and explicit atomic-replacement/rollback limits.
* Existing infrastructure is reused before new infrastructure is added.
* run_dvf_3_3_registry_authority_canonical_closure.py --mode all and equivalent closure-stage aggregate aliases are forbidden; each owner/reviewer/post_external transition is an explicit operator-visible boundary. The pre-existing round3_run_contract_tests.py --class all taxonomy selector is not a closure-stage mode, is never used for current authority evidence here, and its selection semantics remain unchanged.
* The preserved completion-vocabulary predecessor runner requires an explicit mode; its legacy all/machine-pass modes are never invoked or accepted as fresh evidence by this closure. The required test uses only contained fixture-check and cannot recurse into the current route.
* current-route runner failures propagate unchanged.
* current route remains a legacy combined governance container; manifest ownership is not transferred.
* active core 12 and tooling allowlist 1 are not expanded by convenience.
* Required-test dependency closure resolves sys.path bare imports before module load; an ignored/untracked tools/build dependency or import-time side effect is a blocking closure violation.
* No fixed scan universe or stored denominator is authoritative.
* Count equality is not identity.
* Stored PASS is predecessor evidence, not fresh completion evidence.
* Generated staging evidence is not durable unless explicitly adopted and preserved.
* Tracked is not authority; ignored is not deletable.
* Broad staging/tools/tests unignore is forbidden.
* Execution occurs only in the D9 owner-approved bounded Entry-scaffold commit-based dedicated worktree, proven clean by an external checkpoint; after that checkpoint only exact reserved external inputs may precede preflight. Tooling does not normalize the original dirty checkout.
* The D10 externally authored approval must bind the exact plan, entry-time bootstrap scaffold, clean-checkpoint, roadmap hashes, and execution base commit. Plan/roadmap/checkpoint/base drift always invalidates approval; bootstrap drift invalidates Entry, while post-Entry plan-mapped implementation changes must retain the approved baseline and bind before/after hashes through implementation/freeze evidence.
* round3_contract_manifest.json is diagnostic/no-reentry only while its zero live-consumer graph is freshly proven; its malformed bytes are not silently repaired or consumed.
* Dirty required/protected overlap is fail-closed.
* Existing sealed decision bodies are immutable.
* DECISIONS updates are owner-authored/ratified additive entries only.
* Owner seal and independent review are separate and non-substitutable.
* The three Phase 3 review verdicts are external, exact-bundle-bound inputs; tooling may byte-copy and mechanically consolidate them but cannot author or rewrite findings/verdicts.
* Tooling cannot generate owner decisions, independent review PASS, or owner seal; independent review and owner seal phase5 artifacts must be byte-identical materializations of their reserved external inputs.
* Option B is authoritative for top docs: final application occurs after owner seal, top-doc-dependent consumers rerun in post_external_gate, and terminal_hash_seal binds the resulting hashes. No post-terminal claim-bearing append is permitted.
* finalize is the only producer for the final closure report, ledger packet, and closeout; all three precede the final artifact manifest and terminal hash seal.
* The final review universe is hash-bound by repo-relative path.
* Machine PASS cannot claim canonical seal before external gates pass.
* Registry Authority PASS is axis-qualified and cannot be shortened to Registry PASS.
* Registry Authority PASS does not imply DVF Body Compiler PASS, Runtime Compatibility, Publish Boundary, package/release readiness, public acceptance, or manual QA.
* Historical, diagnostic, fixture, quarantine, and predecessor artifacts remain non-current unless a future explicit correction contract adopts them.
* Post-closeout reopening is correction-only and requires new authority drift, identity mismatch, required omission/freshness violation, seal/cutover error, stale reentry, new artifact class, or explicit authority-contract change.

---

## 12. Expected Closeout State

Expected execution closeout target:

    closeout_state=complete

The closeout_state=complete token is allowed only inside this plan's validation ceiling and only when all of the following are true:

* wp_completion_state=complete for WP-1 through WP-7
* approved roadmap/consumed roadmap hash predicate PASS
* byte-identical clean-checkpoint/D10 materializations with approved plan/entry-scaffold/checkpoint hashes and approved base commit=entry worktree HEAD, plus final implementation before/after hash binding
* dedicated execution worktree checkpoint cleanliness PASS, post-checkpoint unapproved delta count 0, and runner original-checkout content mutation count 0
* all three Phase 3 reviews externally authored, exact-bundle-bound, byte-identically materialized, and consolidated with Critical/Important count 0
* fresh current-checkout census/identity/freshness/guard validation PASS
* final validation command matrix complete with unattributed failure count 0
* unconditional real current-protected writer rejection and WP-5 contained fixture receipt guard PASS with real protected mutation count 0
* completion-vocabulary fresh contained fixture-check/no stored-PASS recursion/selective tracking and current-route bare-import pre-load guard PASS without active-core/tooling allowlist expansion
* malformed round3 contract manifest diagnostic-only/zero-live-consumer/no-reentry predicate PASS with bytes unchanged
* body_plan physical authority location and input/output hash coverage PASS
* live additive required gate adopted and current route rerun PASS; this is mandatory and non-waivable for canonical_complete
* protected mutation count 0
* Registry blocker/unresolved/deferred/pending count 0
* eligible external independent review PASS with byte-identical phase5 materialization and complete hash coverage
* owner decisions ratified
* owner seal PASS
* Option B top-doc sync owner_applied_and_validated_post_external after owner seal
* post_external required-consumer denominator/coverage exact match and terminal no-write recomputation PASS
* Lua checker capability matches the Phase 0 preflight record
* finalize-produced ledger packet and closeout exist, are selectively tracked, and precede terminal seal
* canonical seal PASS
* successor Registry Authority round not required

Allowed final claim:

    Registry Authority Closure
    = canonical_complete

    Registry Authority PASS
    = artifact role classification complete
    + single current identity chain
    + required-validation ownership/freshness complete
    + seal/cutover contract complete
    + stale/predecessor reentry guard complete

Required non-claims:

* no DVF Body Compiler PASS achievement claim
* no input facts factual approval claim
* no Registry Runtime Compatibility PASS
* no Runtime Payload Consumer Compatibility closure
* no Publish Boundary PASS
* no runtime behavior/equivalence guarantee
* no package publication/readiness
* no release/Workshop/B42/deployment readiness
* no manual in-game QA
* no public text acceptance or semantic quality approval
* no full historical byte reproducibility

Required-gate adoption is optional only for implemented_only, partial, or blocked outcomes. If implementation is present but required_validation_state is not complete, use implemented_only. If only part of the planned scope is satisfied, use partial. If owner authority, independent reviewer, required evidence, dirty-overlap disposition, or an external dependency prevents progress, use blocked. None of these states may claim Registry Authority Closure canonical_complete.
