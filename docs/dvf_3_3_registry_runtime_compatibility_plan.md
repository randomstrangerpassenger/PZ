# Implementation Plan

> Status: Cycle 5 final-review WARN incorporated / governance-bootstrap-allowed / Gate A pending / no implementation PASS / no compatibility PASS
> 작성일: 2026-07-25
> Round candidate: `dvf_3_3_registry_runtime_compatibility`
> Roadmap input: `C:/Users/MW/.codex/attachments/d2bde82b-a66a-448b-8097-be54301e0475/pasted-text.txt`
> Original roadmap attachment SHA-256: `CBEF54897015C75FD9212489BA46A50882C8F9D4BE9F3639DBB34A866DE49DCC`
> Previous review input: `C:/Users/MW/.codex/attachments/8d76fbc0-a738-440f-9dbd-7de24937fcf0/pasted-text.txt` / SHA-256 `70B9356FDF2B7A8D98411BAC372DBEB4168F74F201ABEC0980ED8C75E2C771FA`
> Cycle 2 review input: `C:/Users/MW/.codex/attachments/df57dd43-25ae-4247-b141-0a044dc5723c/pasted-text.txt`
> Cycle 2 review SHA-256: `9B92656F324581681544F33E4150ADC14BB10355969BCEE4A4A79B371C19C783`
> Cycle 2 reviewed-plan SHA-256: `E0C5DED5C4892FF3B4633FA7AA85A40E18E55AC744371AC5C0B85398E500D3A4`
> Cycle 3 review input: `C:/Users/MW/.codex/attachments/19903be3-c2c3-4ffa-8994-e5077ed11b8e/pasted-text.txt`
> Cycle 3 review SHA-256: `0ED4E7C3438BFD0009C541B6A5F012A867B5D77B3BB1F4352C5AE5126BBD9320`
> Cycle 3 reviewed-plan SHA-256: `50D3C8FCA2BE868567376A80C50636892A8A5F5821A536FA2AAA35AE73BD5F69`
> Cycle 4 review input: `C:/Users/MW/.codex/attachments/22372f25-e78d-4c29-8753-886821b3e935/pasted-text.txt`
> Cycle 4 review SHA-256: `6910D636FE49E24A73DC40AB4B71D34E1CA0629BECEDF7BE45D91FBA3A4FB963`
> Cycle 4 reviewed-plan SHA-256: `EC9218504A51F918C2E0BCF16D6F0E5B6596435A27F7A00DA7BEEADFE4AD06CD`
> Cycle 5 review input: `C:/Users/MW/.codex/attachments/d23d58fd-a37a-4507-8e1b-6f39ae31e0e2/pasted-text.txt`
> Cycle 5 review SHA-256: `BBBA8421C86C449950C0E2BFE750F2A54F7EC097662C5031AB87A0A5C409B9CC`
> Cycle 5 reviewed-plan SHA-256: `818E2D1544B545CB55D9620B89DBBDB89DB06172C29CBCB2E3A0146069EB6742`
> Cycle 5 final incremental review input: `C:/Users/MW/.codex/attachments/d3559565-94a1-45d7-a0a7-e1226193ed90/pasted-text.txt`
> Cycle 5 final incremental review SHA-256: `130EFC7CEEF1657C1982EE231BDDDE737DE1D7D1EA7B4DD163F4791280AA7D4A`
> Cycle 5 final incremental review reviewed-plan SHA-256: `20806FC55C4CF4080F2A4AD38BB209D108A3190E831051644167C5B774B9586F`
> Superseded plan SHA-256: `2BCECA07EEAA77FE928453F2AD414B762519BB91D7823D9973B5FC22E716F6BE`
> Future execution provenance: roadmap materialization과 plan fingerprint는 Change 0에서 생성하며 planning 단계 산출물로 미리 만들지 않는다.
> Template input: `docs/PLAN_TEMPLATE.md`
> Execution obligations: `docs/EXECUTION_CONTRACT.md`
> Closed predecessor: Registry Authority canonical closure `attempt-0038-practical` / integrated `main` commit `63357b7afb879f89c4f43df67ad0d39a060561fb`
> Expected validation depth: `heavy`
> Maximum future claim: `Registry Runtime Compatibility PASS`

이 문서는 Cycle 1~5 feedback disposition과 Cycle 5 final incremental review의 WARN hardening을 반영한 구현 계획이며 구현 결과나 PASS 증거가 아니다. final incremental review verdict는 `WARN`, open Critical `0`, open implementation blocker `0`, `governance_bootstrap_allowed=true`다. 따라서 추가 plan-level review 없이 Gate A로 진행할 수 있지만, Gate A/B/C의 실제 predicate가 충족되기 전에는 각각의 후속 mutation이나 PASS를 주장하지 않는다. architecture boundary, evidence DAG, claim ceiling이 실질적으로 바뀌면 새 plan-level review를 요구한다.

---

## 0. Review Revision and Implementation Entry Gate

### 0.1 Cycle 1 Carry-Forward Disposition

| ID | Review requirement | Revised disposition | Implementation gate |
|---|---|---|---|
| A-1 | repo-local roadmap와 roadmap/plan fingerprint | future execution Change 0에서 roadmap/review를 repo-local materialization하고 외부 fingerprint report로 plan을 결속한다 | fingerprint mismatch 시 block |
| A-2 | execution baseline disposition | owner-bound baseline record와 clean selected worktree를 필수화한다 | missing/dirty/overlap unresolved 시 block |
| A-3 | attempt-scoped evidence root | `attempts/attempt-NNNN/phase0..phase5`를 사용하고 failed attempt를 보존한다 | attempt reuse 시 block |
| A-4 | C-6 timing | Phase 0A census 후 Phase 0B branch 판정 전에 role disposition을 요구한다 | C-6 missing 시 Branch C |
| A-5 | alias comparison universe | alias contribution은 diagnostic regression으로만 계량하고 네 surface의 exact universe equality를 유지한다 | new alias-emitted key 시 fail |
| A-6 | package binding normalization | logical manifest/chunk binding과 ZIP transport metadata를 분리한다 | logical binding mismatch 시 fail |
| A-7 | durable evidence classification | durable/supporting/temp/diagnostic class와 live-manifest eligibility를 고정한다 | attempt-local artifact 직접 채택 시 block |
| A-8 | actual Lua harness contract | exact executable/version/path/package.path/stdout/exit contract를 고정한다 | missing Lua 또는 parse failure 시 block |
| A-9 | C-4 route enum | 각 route의 command/dependency/producer/fallback/report/authority를 정의한다 | eligible route 미선택 시 Phase 3 block |
| A-10 | terminology/reporting | axis-qualified terminal token, role fields, Windows receipt, failure stage를 고정한다 | bare completion token 시 fail |
| B-1 | required-validation self-cycle | pre-adoption과 post-adoption/final governance DAG를 분리한다 | cycle edge 발견 시 block |
| B-2 | tooling allowlist | allowlist/core closure를 수정하지 않고 standalone subprocess를 사용한다 | allowlist diff가 1줄이라도 있으면 block |
| B-3 | identity/comparator order | strict UTF-8 decoded code-point exact + `ascii_lower_v1`을 이 plan contract로 제안·고정한다 | re-review/owner ratification 전 block |
| B-4 | C-3 typed mismatch routing | technical failure는 machine fail이며 owner override를 금지한다 | waiver count가 1 이상이면 fail |
| B-5 | package guard | `package_iris.ps1` 내부 guard를 무조건 실행한다. C-5는 adoption topology만 선택한다 | guard bypass 가능 시 fail |
| B-6 | pre-implementation blocker-zero | production mutation 전 machine-readable blocker-zero report를 요구한다 | open blocker가 1 이상이면 block |
| B-7 | reviewer eligibility | roadmap/plan/implementation author·coauthor·owner signer와 다른 reviewer만 허용한다 | owner waiver 불가 |

### 0.2 Cycle 2 Finding Adjudication

| ID | Cycle 2 finding | Codebase/contract adjudication | Revised plan result |
|---|---|---|---|
| A-1 | candidate validation mechanism | `round3_run_contract_tests.py`에 `--required-validations`가 실제 존재한다 | exact flag preflight와 candidate probe command를 고정 |
| A-2 | allowlist contract scope | `DECISIONS.md`와 runner는 `tools.build` import closure로 정의한다 | `import_closure_only`를 기록하고 authority drift 시 separate-scope block |
| A-3 | candidate probe vs official current route | candidate override는 official live route가 아니다 | `candidate_manifest_route_probe`로 명명하고 official PASS는 post-adoption에만 허용 |
| A-4 | C-6 role multiplicity | two-member bounded disposition만 이 round에서 허용한다 | group별 `1 reference + 1 exception`, overlap/unassigned 0 |
| A-5 | verdict vocabulary | template vocabulary는 `PASS/WARN/FAIL`이다 | 새 token을 제거하고 WARN 진입 조건을 별도 predicate로 표현 |
| A-6 | C-1/C-2 owner binding | plan 승인 단일 record role로 고정한다 | selected `plan_approvals/approval-<approval-id>.json`이 plan fingerprint와 C-1/C-2를 hash-bind |
| A-7 | Windows report/parity | roadmap 10개 측정치와 rerun parity가 필요하다 | direct fields와 normalized/record/key/payload hash parity를 필수화 |
| A-8 | C-6 vocabulary/C-5 confirmation | 강화·재명명 사실의 owner 인지가 필요하다 | old/new mapping과 C-5 강화 acknowledgement를 plan approval에 포함 |
| B-1 | candidate policy bootstrap | Phase 2~4가 durable policy를 조기 참조하면 순환한다 | attempt-local candidate context를 명시하고 Phase 5 complete promotion 후 canonical-durable context를 재검증 |
| B-2 | alias exact-key invariant | current alias declaration은 new-key success를 정당화하지 않는다 | source=rendered=runtime=package exact sets, applied new alias key 0 |
| B-3 | Phase 0B ordering | final Branch A가 Review 2보다 앞서면 안 된다 | Phase 0A eligibility → Review 2 ratification → Phase 0B final branch |
| B-4 | attempt allocation | naming convention만으로 no-reuse를 강제할 수 없다 | named-mutex reservation, append-only events, immutable terminal records 추가 |
| B-5 | format-specific decode | raw token과 decoded exact identity를 분리해야 한다 | JSON/Lua adapter schema와 escaped-key fixtures 추가 |
| B-6 | jq rejection wording | case-variant key와 identical duplicate를 구분해야 한다 | case variants는 distinct, default object duplicate는 last-wins, `--stream`은 미채택으로 명시 |
| B-7 | Lua accepted version | version receipt만으로 부족하다 | accepted `{5.1.x, 5.4.x}`, unsupported-version failure, Kahlua/PZ equivalence non-claim 추가 |

### 0.3 Cycle 3 Finding Adjudication

| ID | Cycle 3 finding | Revised disposition | Gate |
|---|---|---|---|
| B-1 | exporter analyzer invocation | exporter direct import를 금지하고 exact tracked validator subprocess만 허용한다 | exporter import graph 또는 child receipt 위반 시 block |
| B-2 | candidate hash-binding DAG | leaf artifact reciprocal hash를 금지하고 external `candidate_contract_binding_manifest.json`으로 결속한다 | cycle edge 또는 bundle mismatch 시 block |
| B-3 | attempt evidence durability | mutable canonical index를 폐기하고 append-only event ledger + immutable per-attempt terminal records를 authority로 둔다 | prior event mutation/deletion/hash-chain break 시 block |
| B-4 | durable promotion completeness | Cycle 3의 여섯 role에 Cycle 4 toolchain 2 role, Cycle 5 owner/review authority 3 role을 추가한다 | final eleven-role source/destination 1:1 parity 실패 시 block |
| B-5 | Windows surface inputs | four-surface paths/hashes와 package attempt/binding을 `windows_surface_inputs.json`으로 명시한다 | missing/stale input 시 Phase 3 block |
| B-6 | policy lifecycle vocabulary | policy context와 required-gate state를 분리한다 | ambiguous `adopted` token 사용 시 fail |
| B-7 | lock recovery | Windows named mutex 하나만 canonical mechanism으로 사용한다 | timeout/recovery recensus 실패 시 allocation block |
| A-1 | non-adopted package route | candidate/canonical-durable probe만 허용하고 normal package finalization은 live gate adoption 전 차단한다 | premature finalization 시 fail |
| A-2 | undispositioned two-member collision | dedicated failure code/stage fixture를 추가한다 | fixture mismatch 시 fail |
| A-3 | Lua evidence role | executed version과 offline reconstruction ceiling을 final report에 기록한다 | cross-version/Kahlua overclaim 시 fail |
| A-4 | formal claim token | bare `Runtime Compatibility PASS` current claim을 금지한다 | claim scan count가 1 이상이면 fail |
| I-3 | Windows A/C choice | A를 canonical route, C를 required transport regression으로 고정한다 | owner route-selection ceremony 없음 |

### 0.4 Cycle 4 Finding Adjudication

| ID | Cycle 4 finding | Codebase/contract adjudication | Revised plan result |
|---|---|---|---|
| C4-1 | roadmap fixture coverage | roadmap Fixture 1 ordinary positive와 Fixture 6 Windows cardinality-loss injection이 기존 class 목록에 명시적으로 대응되지 않았다 | roadmap 1~10 exact traceability table, expected code/stage/first predicate, unresolved count 0 추가 |
| C4-2 | exporter/package invocation migration | exporter library는 다수 tool/test가 import하고 package default command도 current repository contract에 남아 있어 migration을 가정할 수 없다 | repository-wide inventory/migration matrix와 post-adoption canonical default route, unknown/unmigrated count 0 추가 |
| C4-3 | implementation toolchain freshness | protected data freshness만으로 evidence producer/test bytes의 불변성을 증명할 수 없다 | toolchain manifest, checkpoint freshness reports, durable/live/final binding 추가 |
| C4-4 | pre-entry durable-ledger bootstrap | planned ledger paths는 planning checkout에서 unignored지만 아직 tracked durable root로 materialize되지 않았다 | owner-approved governance-only bootstrap commit과 two-stage entry gate 추가 |
| I4-1 | event append transaction | record/event/shared-ledger partial state의 recovery/block 규칙이 부족했다 | exact write/flush/append order와 partial-state matrix 추가 |
| I4-2/N-ii | cross-worktree/branch prefix | named mutex만으로 서로 다른 branch의 tracked prefix divergence를 막지 못한다 | owner-approved single integration branch와 three-prefix equality 추가 |
| I4-3 | attempt-specific bundle ID | attempt-local source path가 content identity에 들어갔다 | canonical destination filename/role 기반 content-addressed ID로 수정 |
| I4-4 | roadmap OR → plan AND | package guard와 live gate를 모두 요구하는 강화가 owner field로 충분히 드러나지 않았다 | exact approval booleans와 hash binding 추가 |
| I4-5 | bridge preflight boundary | pre-generation preflight가 post-generation four-surface equality까지 증명하는 것처럼 읽혔다 | explicit bridge input manifest와 rendered/policy-only preflight, post-generation four-surface validator 분리 |
| N-i | C-4 route transition approval | owner-selected A/C에서 fixed A + required C로의 전환 binding이 부족했다 | plan approval exact acknowledgement 추가 |
| M4-1 | route evidence strength | same producer를 두 algorithm proof로 오해할 수 있다 | `algorithm_proof_count=1`, `transport_conformance_count=2` 고정 |
| M4-2 | PUC Lua vocabulary | offline validation ceiling의 runtime vocabulary가 불완전했다 | PUC Lua/runtime-not-executed fields 추가 |

### 0.5 Cycle 5 Finding Adjudication

| ID | Cycle 5 finding | Revised disposition | Gate |
|---|---|---|---|
| C5-1 | Gate B executor bootstrap cycle | Option A를 고정해 round-local bootstrap-only executor, test, manifest, validation report를 Gate A commit에 포함한다 | reviewed executor 외 reservation 또는 manual/ad hoc path가 있으면 block |
| C5-2 | owner/review authority bytes not durable | plan approval, collision owner disposition, Phase 0/Review 2 contract review 3 role을 candidate/durable contract에 추가한다 | clean checkout에서 record/schema/hash/decision/eligibility 불일치 시 fail |
| C5-3 | final closeout bytes disposable | final governance artifacts를 tracked per-attempt `closeout/` packet으로 atomic publish/commit한 뒤 terminal transaction을 실행한다 | closeout commit 전 terminal event 또는 missing content 시 block |
| I5-1 | bundle lifecycle authority | append-only durable lifecycle ledger와 immutable event records를 추가한다 | local lifecycle report만 존재하면 block |
| I5-2 | closeout/terminal ordering | closeout packet commit → terminal record/event → terminal commit → shared prefix 순서를 고정한다 | ordering mismatch 시 block |
| I5-3 | bootstrap executor provenance | bootstrap contract가 executor/test hashes를 결속하고 Phase 1 toolchain manifest가 provenance를 import한다 | executor drift 또는 unbound execution 시 block |
| I5-4 | live manifest final binding | pre/post live manifest hashes, selected bundle id/manifest, adopted row identity를 final artifacts에 직접 결속한다 | required field missing/mismatch 시 fail |
| I5-5 | dirty docs inventory baseline | invocation authority는 owner-approved clean baseline만 사용하고 original dirty docs는 preservation-only comparison으로 분리한다 | dirty text가 authority denominator에 들어가면 block |
| M5-1 | cross-version Lua claim | `cross_version_parity_claimed=false`를 명시한다 | unexecuted parity claim 시 fail |
| M5-2 | governance scope | executor/ledger/lifecycle/closeout packet을 이 round namespace에만 제한한다 | cross-round/general framework화 시 separate-scope block |
| N5-1 | content reuse vs lifecycle | invalidated/superseded bundle의 automatic content reuse/revalidation을 금지한다 | terminal lifecycle bundle reuse 시 block |

### 0.6 Cycle 5 Final Incremental Review WARN Disposition

| ID | Review warning/status | Adopted disposition | Gate |
|---|---|---|---|
| FR5-0 | `WARN`, Critical 0, implementation blocker 0 | review bytes/hash와 reviewed-plan hash를 provenance에 고정하고 `governance_bootstrap_allowed=true`를 인정한다 | Gate A may proceed; implementation PASS는 아님 |
| FR5-W1 | fixed `current_*` owner/review record paths | 세 authority record를 record-id 기반 immutable versioned namespace로 바꾸고 candidate/durable/live route가 선택된 exact versioned path/hash를 직접 소비한다 | alias/current pointer, ambiguous active head, broken successor chain이면 block |
| FR5-W2 | reservation 전 nonterminal attempt metric 부재 | bootstrap executor가 event ledger를 재생해 `nonterminal_attempt_count`와 `open_attempt_ids[]`를 계산하고 count `0`일 때만 새 ID를 reserve한다 | open attempt가 하나라도 있으면 new reservation block |
| FR5-R | 추가 plan revision/re-review 불필요 | 두 warning을 이 계획의 필수 Gate A hardening으로 채택한다. 해당 hardening의 실제 구현/test/owner approval은 Gate A evidence로 검증한다 | 책임 경계/DAG/claim ceiling 변경 때만 plan-level re-review |
| FR5-E | final independent review eligibility | 이 final plan reviewer는 roadmap/이전 plan review 참여로 final closeout independent reviewer에 부적격임을 고정한다 | 동일 identity가 Review 6을 수행하면 block |

### 0.7 Review-Adjudicated Fixed Contracts

이 개정본의 재검토와 owner approval은 다음 계약을 일괄 ratify한다. 구현자가 실행 중 다른 값을 고를 수 없다.

1. `exact_runtime_identity_v1`
   - input bytes를 strict UTF-8로 decode한 Unicode code-point sequence다.
   - Unicode normalization, locale mapping, case folding을 적용하지 않는다.
   - raw UTF-8 bytes와 byte hash는 provenance/diagnostic field로 함께 보존하지만 equality authority는 decoded code-point sequence다.
   - invalid UTF-8은 `failure_code=invalid_utf8`로 fail-closed한다.
2. `consumer_comparison_identity_ascii_lower_v1`
   - ASCII `A`~`Z`만 `a`~`z`로 변환한다.
   - 현재 조사된 2,105개 key는 planning observation 기준 모두 ASCII지만 이 수치를 상수로 쓰지 않는다.
   - non-ASCII key가 하나라도 나타나면 locale-aware lower나 Unicode casefold로 자동 확장하지 않고 `failure_code=unsupported_comparator_domain`으로 차단한다.
3. C-3는 owner waiver가 아니다.
   - planning count drift는 fresh recensus로 흡수할 수 있는 observation이다.
   - exact key-set mismatch, exact duplicate, collision-member drift, payload divergence, missing surface/dependency, unauthorized collision은 typed machine failure다.
4. package guard는 unconditional이다.
   - C-5는 live required-validation adoption topology만 선택한다.
   - package guard 자체를 OFF, warning-only, opt-in으로 바꾸는 enum은 없다.
5. independent review eligibility는 fixed contract다.
   - owner는 조건을 만족하는 reviewer를 지정할 수만 있고 eligibility 기준을 완화할 수 없다.
6. four-surface exact-key invariant는 fixed contract다.
   - `source_exact_key_set = rendered_exact_key_set = runtime_exact_key_set = package_exact_key_set`이어야 한다.
   - `applied_new_alias_key_count`, `unexpected_emission_count`, `alias_induced_comparison_collision_increase`는 모두 `0`이어야 한다.
7. candidate/canonical-durable policy context는 explicit contract다.
   - Phase 1~4는 attempt-local candidate policy/disposition을 explicit path로만 소비한다.
   - Phase 5 durable promotion 뒤 canonical-durable context는 selected immutable durable bundle path 외 입력을 거부한다.
8. attempt allocation은 evidence contract다.
   - atomic reservation이 성공한 ID만 사용하며 pre-Phase 0 failure와 partial attempt도 ID를 소비한다.
   - reservation/terminal event와 immutable durable terminal record가 없으면 claim-bearing phase를 시작하지 않는다.
9. candidate binding은 acyclic contract다.
    - policy/exclusion/disposition과 plan approval/owner disposition/Review 2 authority records는 허용된 단방향 authority/review edges 외 reciprocal final hash, bundle manifest hash, 자기 final hash를 포함하지 않는다.
    - external binding manifest가 정확히 six leaf path/role/schema/version/byte count/SHA-256을 결속한다.
10. policy lifecycle과 gate lifecycle은 별도 축이다.
    - `policy_context`는 `candidate` 또는 `canonical_durable`만 허용한다.
    - `required_gate_state`는 `not_adopted` 또는 `live_gate_adopted`다.
11. existing invocation은 census와 migration 없이 파손할 수 없다.
    - exporter CLI/library와 package CLI의 omitted compatibility arguments는 live gate adoption 뒤에만 live manifest가 결속한 selected durable bundle로 결정론적으로 resolve한다.
    - adoption 전 omission, partial override, ambiguous historical route는 fail-closed하며 executable caller의 `unknown`/`unmigrated` count는 모두 `0`이어야 한다.
12. claim-affecting implementation toolchain은 evidence와 byte-bind한다.
    - fixed root roles와 transitive project-local dependency closure의 path/hash/byte count/tracked/not-ignored 상태를 manifest로 봉인한다.
    - Phase 2 evidence 전부터 final machine report 전까지 지정 checkpoint의 drift count는 `0`이어야 한다.
13. durable attempt authority는 governance-only bootstrap과 single integration branch를 요구한다.
    - first attempt 전에 empty event ledger와 bootstrap contract를 별도 owner-approved commit으로 tracked/unignored 상태로 만든다.
    - attempt는 owner-approved integration branch의 canonical event prefix에서만 실행하며 retroactive durable materialization을 금지한다.
14. Windows A/C는 하나의 algorithm과 두 transport conformance 증거다.
    - Route A는 canonical transport, Route C는 required regression이며 `algorithm_proof_count=1`, `transport_conformance_count=2`다.
15. Gate B는 reviewed bootstrap-only executor만 수행한다.
    - executor/test/contract/validation report는 Gate A commit에서 hash-bound되고 compatibility source inspection이나 PASS claim을 수행하지 않는다.
    - manual/ad hoc reservation, 다른 script substitution, executor 변경 뒤 bootstrap re-approval 생략은 금지한다.
16. owner-bound exception authority bytes는 durable contract의 일부다.
    - plan approval, collision owner disposition, Phase 0/Review 2 contract review의 실제 bytes를 candidate binding, versioned bundle, live required route가 직접 검증한다.
17. canonical closeout authority는 local phase5가 아니라 tracked per-attempt closeout packet이다.
    - final machine/review/owner seal/final report/terminal seal bytes와 supporting post-adoption result를 durable commit한 뒤에만 terminal event를 append한다.
18. bundle lifecycle은 append-only durable authority다.
    - bundle directory를 rewrite하지 않고 lifecycle event ledger/record로 adoption, invalidation, supersession을 기록한다.
    - `invalidated` 또는 `superseded`인 existing content-addressed bundle은 이 scope에서 자동 revalidation/reuse하지 않는다.
19. owner/review authority record는 versioned immutable namespace만 사용한다.
    - `current_*` file이나 mutable pointer 없이 owner-selected exact record-id path/hash를 pre-entry, candidate binding, durable bundle, live route가 직접 결속한다.
    - successor는 prior bytes를 바꾸지 않고 predecessor path/hash와 supersession reason을 가진 새 record로만 추가한다.
20. 새 attempt reservation은 열린 attempt가 없을 때만 허용한다.
    - bootstrap executor가 canonical event ledger에서 reservation-minus-terminal 상태를 계산해 `nonterminal_attempt_count == 0`과 `open_attempt_ids == []`를 증명한다.
    - clean worktree/prefix parity가 참이어도 open attempt가 있으면 새 ID를 열지 않는다.

### 0.8 Pre-Implementation Blocker-Zero Predicate

다음 predicate가 모두 참일 때만 `implementation_entry_allowed=true`다.

```text
repo_local_roadmap_materialized
and repo_local_review_materialized
and current_plan_fingerprint_matches
and roadmap_plan_traceability_complete
and revised_plan_review_verdict in {PASS, WARN}
and revised_plan_review_open_critical_count == 0
and revised_plan_review_open_implementation_blocker_count == 0
and (revised_plan_review_verdict == PASS
     or all_review_warnings_owner_dispositioned == true)
and owner_plan_approval_matches_fingerprints
and preentry_executor_contract_complete == true
and bootstrap_executor_contract_reviewed == true
and bootstrap_executor_test_status == PASS
and bootstrap_executor_hash_matches == true
and bootstrap_executor_scope_violation_count == 0
and ad_hoc_or_manual_reservation_count == 0
and reservation_preflight_nonterminal_attempt_count == 0
and reservation_preflight_open_attempt_ids == []
and governance_bootstrap_commit_owner_approved == true
and preentry_required_path_ignored_count == 0
and preentry_required_path_untracked_count == 0
and retroactive_attempt_materialization_count == 0
and selected_execution_branch == owner_approved_integration_branch
and selected_worktree_event_prefix == approved_canonical_event_prefix
and approved_canonical_event_prefix == shared_reservation_ledger_committed_prefix
and execution_baseline_disposition == approved_clean_worktree
and target_overlap_unresolved_count == 0
and tooling_allowlist_mutation_planned_count == 0
and allowlist_contract_scope == import_closure_only
and required_validations_override_flag_verified == true
```

필수 pre-entry artifact:

- `roadmap_input_materialization_report.json`
- `implementation_plan_fingerprint_report.json`
- `roadmap_plan_traceability_matrix.json`
- `revised_plan_review_report.json`
- selected `plan_approvals/approval-<approval-id>.json`
- `execution_contract_check_report.json`
- `allowlist_contract_scope_report.json`
- `execution_baseline_disposition.json`
- `bootstrap_tool_manifest.json`
- `bootstrap_executor_validation_report.json`
- `governance_ledger_bootstrap_report.json`
- `attempt_reservation_receipt.json`
- `preimplementation_gate_report.json`

entry는 세 gate다.

1. Gate A는 final plan review의 `governance_bootstrap_allowed=true`를 소비해 round-local bootstrap executor/contract/test/validation report와 ledger bootstrap files를 candidate로 준비·검토한다. 그 exact hashes와 warning dispositions를 selected versioned owner approval record가 승인한 뒤 이 governance-only set만 별도 bootstrap commit으로 만든다.
2. owner가 그 bootstrap commit을 새 execution baseline과 canonical integration branch로 승인한 뒤 Gate B는 그 committed executor만 사용해 prefix parity, committed attempt reservation, `implementation_entry_allowed=true`를 판정한다. 이 상태는 신규 compatibility tooling/tests 작성만 허용하고 existing exporter/package/live config mutation은 아직 금지한다.
3. Gate C는 reserved attempt 안에서 신규 tooling이 owner-approved clean baseline을 대상으로 invocation inventory/migration plan과 read-only dependency checks를 생성한 뒤 판정한다. 다음 predicate가 모두 참일 때만 `production_integration_allowed=true`로 existing exporter/package/tests/config integration을 시작한다.

```text
implementation_entry_allowed == true
and invocation_inventory_authority_baseline == owner_approved_clean_baseline
and invocation_inventory_unknown_count == 0
and invocation_migration_plan_unresolved_count == 0
and dirty_original_docs_consumed_as_authority_count == 0
and preintegration_tool_scope_violation_count == 0
```

production mutation 뒤에 만든 pre-entry report, 수동 reservation, 이미 시작된 attempt를 소급 materialize해 Gate A/B를 충족할 수 없다. inventory가 실패하면 신규 attempt tooling과 failure evidence만 보존하고 existing exporter/package/live config는 수정하지 않는다.

`preimplementation_gate_report.json`은 각 predicate, input path/hash, reviewer identity/provenance, selected versioned owner record path/hash, bootstrap commit, selected integration branch/baseline HEAD/worktree, three-prefix hashes, `reservation_preflight_nonterminal_attempt_count`, `reservation_preflight_open_attempt_ids[]`, open blocker counts를 가진다.

Gate B의 `preentry_required_path_*_count` denominator는 selected versioned plan contract approval record, bootstrap executor/test/tool manifest/validation report/contract, attempt/lifecycle ledgers, current attempt reservation record/event commit이다. reservation commit이 tracked 상태가 되고 three-prefix parity가 복구된 뒤에만 count를 계산하므로 dynamic record를 Phase 0 뒤 사후 tracking하는 경로는 없다. `approved_canonical_event_prefix`는 owner-approved starting prefix에 contract-valid exact-one event를 적용해 reservation commit이 확정한 expected next prefix이며, previous-prefix hash와 derivation을 gate report에 함께 기록한다.

---

## 1. Objective

이미 봉인된 Iris Artifact Registry의 current authority chain을 변경하지 않고, consumer가 Registry key를 서로 다른 comparison semantics로 읽더라도 exact runtime identity와 payload binding이 손실되지 않음을 lossless evidence로 검증하고 future drift를 fail-closed하는 구현 계획을 정의한다.

대상 chain:

```text
current source
-> rendered artifact
-> Lua bridge export
-> runtime chunk manifest/chunks
-> actual Lua reconstruction
-> isolated package projection
-> Windows lossless inspection projection
```

두 identity 축을 명시적으로 분리한다.

```text
exact_runtime_identity_v1
= strict UTF-8 decoded code-point sequence

consumer_comparison_identity_ascii_lower_v1
= ASCII A-Z only lowercase transform used for collision analysis
```

comparison identity는 runtime lookup, alias resolution, source correction, canonical winner 선정에 사용하지 않는다. comparison identity가 같아도 exact key와 각 key의 payload binding은 별도 record로 유지한다.

### Codebase Inspection Summary

계획 작성 시점의 실제 checkout에서 다음을 확인했다. 모두 planning observation이며 실행 상수나 PASS 증거가 아니다.

- facts, decisions, overlay, rendered artifact, runtime chunks, 현재 isolated package projection은 각각 2,105개의 exact key를 보유한다.
- source/rendered/runtime/package exact key-set symmetric difference와 exact duplicate count는 planning-time 기준 0이다.
- 조사된 2,105개 key의 non-ASCII key count는 0이다.
- `Base.LemonGrass`와 `Base.Lemongrass`는 source, rendered, runtime `Chunk005.lua`, isolated package에 별도 exact key로 존재한다.
- 두 key는 comparison collision group을 만들지만 현재 payload 관찰만으로 owner disposition이나 final equivalence를 대신하지 않는다.
- PowerShell `5.1.26100.8894`의 `ConvertFrom-Json`은 current rendered object의 case-variant properties를 거부한다.
- `export_dvf_3_3_lua_bridge.py`는 rendered object를 `json.load()`로 dictionary materialize하므로 pre-materialization duplicate evidence가 없다.
- exporter의 chunk validation은 missing/orphan/exact duplicate를 검사하지만 comparison collision, owner exception, payload binding, actual Lua overwrite를 검사하지 않는다.
- runtime manifest는 chunk entry를 `data[fullType] = entry`로 병합한다. Python parser만으로 actual Lua table cardinality를 증명할 수 없다.
- exporter에는 `Base.CanOpener -> Base.TinOpener` alias declaration이 있으나 planning-time source에는 target `Base.TinOpener`가 이미 존재하고 source `Base.CanOpener`가 없어 new key를 적용하지 않는다. 이 round의 success invariant는 alias-added key `0`이다.
- `package_iris.ps1`은 isolated `OutputRoot`와 forbidden/stale file guard를 제공하지만 registry compatibility guard를 무조건 호출하지 않는다.
- `round3_run_contract_tests.py`는 live required tests/artifacts와 field predicate를 fail-closed로 실행하며 line 440에 candidate manifest를 지정할 수 있는 `--required-validations` option이 존재한다.
- `DECISIONS.md`는 `current_route_allowed_tooling_modules`를 regeneration tooling **import allowlist**로 정의하고 runner도 `tools.build.*` import만 검사한다. 현재 contract scope는 `import_closure_only`다.
- `round3_active_core_closure.json`은 current core 12개와 tooling allowlist 1개 `export_dvf_3_3_lua_bridge`를 분리하며, allowlist expansion은 별도 reviewed scope를 요구한다.
- planning environment의 resolved `lua`/`luac`는 `5.4.8`이지만 이는 future execution receipt나 Kahlua/PZ equivalence 증거가 아니다.
- exporter는 CLI entrypoint뿐 아니라 `tools.build.export_dvf_3_3_lua_bridge` 또는 bare module로 여러 build tool과 tests에서 직접 import된다. package script path와 `-Clean -Zip` command도 current tooling/tests/docs에 남아 있으므로 새 required arguments를 기존 caller가 이미 충족한다고 가정할 수 없다.
- `Iris/_docs/round3/`에는 tracked files가 이미 있고 planned `registry_runtime_compatibility` paths는 planning checkout의 `git check-ignore --no-index`에서 ignored로 판정되지 않았지만, exact ledger/bootstrap files는 아직 존재하거나 tracked되지 않는다. first attempt 전 governance-only bootstrap commit이 필요하다.
- current branch는 planning observation 기준 `main`이지만 future attempt branch는 owner approval record와 canonical prefix synchronization으로 다시 판정하며 이 값을 hard-code하지 않는다.
- 현재 `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md`에는 사용자 소유 미커밋 변경이 있다. 실행은 이 변경을 되돌리거나 이 round 변경으로 흡수하지 않는다.

---

## 2. Scope

포함 범위:

- repo-local roadmap/review materialization과 plan fingerprint/traceability
- clean execution baseline 및 user-owned dirty change preservation
- round-local reviewed bootstrap-only executor, governance-only durable-ledger bootstrap, single integration branch, transactional attempt-scoped immutable evidence lifecycle
- exporter/package repository-wide invocation census, migration, post-adoption canonical default compatibility
- claim-affecting implementation toolchain manifest와 checkpoint freshness
- versioned owner/review authority records, append-only bundle lifecycle authority, tracked per-attempt final closeout packet
- source/rendered/runtime/isolated package의 fresh lossless census
- strict exact identity와 ASCII-only comparator contract
- four-surface exact-key equality와 existing alias declaration의 no-new-key regression
- collision group별 machine integrity 검사와 owner-bound/hash-bound role disposition
- surface-specific ordered record adapter와 standalone canonical analyzer
- explicit identity-field exclusion manifest와 edge-specific payload binding
- bridge pre-materialization, chunk generation, cross-chunk, merge, post-serialization, runtime reconstruction guard
- unconditional isolated package projection guard와 package child exit propagation
- PowerShell 5.1 lossless record projection과 round-trip inspection
- roadmap fixture 10종 및 existing exact-duplicate/stale bridge/monolith/predecessor guard regression
- actual Lua table merge cardinality/overwrite 검증
- deterministic rerun, cross-phase freshness, protected no-mutation
- additive live required-validation adoption candidate와 owner C-5 topology 결정
- independent review, owner seal, terminal hash seal, axis-qualified closeout
- required tool/test/durable evidence에 한정한 exact-path VCS visibility

### Explicitly Out Of Scope

- Registry Authority closure 재수행 또는 `attempt-0038-practical` 수정
- source key rename, 삭제, 병합, spelling correction
- `Base.LemonGrass`와 `Base.Lemongrass` 중 runtime winner를 구현자가 선택
- source facts/decisions/overlay 또는 rendered text 의미 변경
- runtime-side case normalization, case alias, lookup fallback 추가
- live runtime chunk payload replacement 또는 monolith 복구
- tooling allowlist/current core 확대
- allowlist expansion을 우회하는 direct import
- package publication, Workshop upload, release/B42/deployment readiness
- Browser, Tooltip, Wiki, public text, semantic quality
- manual in-game QA, multiplayer, long-running session
- external mod ecosystem 전체 sweep
- 모든 JSON parser/PowerShell/OS consumer의 일반 compatibility 보장
- Pulse Core 또는 다른 Pulse spoke 변경

---

## 3. Non-Goals

- case-insensitive consumer를 위해 exact key를 하나로 축소하지 않는다.
- comparison identity를 alias/source-normalization framework로 확장하지 않는다.
- collision member의 item 의미가 동일하다고 판결하지 않는다.
- sealed `2105` observation을 새 hard-coded success condition으로 만들지 않는다.
- Windows projection/sidecar를 authority artifact로 승격하지 않는다.
- package guard PASS를 package publication 또는 release readiness로 읽지 않는다.
- fixture의 단순 non-zero exit만으로 negative test를 통과시키지 않는다. expected failure code와 failure stage가 모두 일치해야 한다.
- pre-adoption report를 final machine report, independent review, owner seal, terminal seal과 동일시하지 않는다.
- plan-document revision completion을 implementation completion으로 표현하지 않는다.

---

## 4. Assumptions

### Repository and Authority Assumptions

- `docs/Philosophy.md`가 최상위 기준이다.
- current source authority는 `dvf_3_3_input_manifest.json`이 가리키는 facts/decisions/overlay chain이다.
- current rendered inspection input은 `Iris/build/description/v2/output/dvf_3_3_rendered.json`이다.
- current runtime inspection input은 `IrisLayer3DataChunks.lua`와 그 manifest가 참조하는 chunk files다.
- package surface는 `package_iris.ps1 -OutputRoot <fresh-isolated-root>`가 새로 만든 copy만 사용한다.
- Registry Authority canonical closure는 닫힌 predecessor이며 이 round는 compatibility axis만 연다.
- Phase 0은 source/readpoint를 변경하지 않고 fresh isolated output만 쓴다.
- Branch A에서만 Phase 1 이후 production integration을 진행한다.
- count, chunk count, collision count, hash는 매 attempt에서 재파생한다.

### Execution Baseline Contract

owner input `execution_baseline_disposition.json`의 최소 fields:

- `schema_version`
- `round_id`
- `baseline_head`
- `baseline_head_approval`
- `original_worktree_path`
- `original_dirty_path_inventory[]`
- `target_path_inventory[]`
- `target_overlap_paths[]`
- `selected_execution_worktree`
- `selected_worktree_head`
- `selected_worktree_clean`
- `protected_surface_hashes`
- `user_owned_change_preservation`
- `top_doc_application_mode`
- `disposition`
- `owner_identity`
- `owner_timestamp`
- `record_sha256`

규칙:

- selected execution worktree는 owner-approved `baseline_head`에 고정되고 production target path 기준 clean이어야 한다.
- original worktree의 사용자 변경은 그대로 보존한다. `reset`, `checkout --`, silent stash를 사용하지 않는다.
- target overlap이 있으면 `approved_clean_worktree`가 확정될 때까지 implementation을 차단한다.
- top-doc user changes가 original worktree에 남아 있으면 implementation Changes 0~6은 clean worktree에서 진행할 수 있으나 final top-doc application은 `owner_application_pending`으로 분리한다.
- protected source/rendered/runtime/package baseline hash는 Phase 0 전에 고정하고 매 phase freshness check에 사용한다.
- execution baseline record는 `owner_approved_integration_branch`, `governance_bootstrap_commit`, bootstrap executor/test/tool-manifest/contract/validation-report hashes, resolved bootstrap Python/Git hashes, `approved_canonical_event_prefix_sha256`, `shared_reservation_ledger_committed_prefix_sha256`를 포함한다.
- attempt는 지정 integration branch의 전용 clean worktree에서만 시작한다. 다른 branch/worktree의 sequential attempt, detached HEAD, unmerged event prefix는 named mutex를 획득했더라도 block한다.

### Surface Projection and Alias Regression

- source record는 facts/decisions/overlay row를 exact `item_id`로 결속한 ordered tuple이다.
- rendered record는 raw JSON property pair의 exact key, raw key bytes hash, full payload를 함께 보존한다.
- runtime record는 raw chunk assignment stream과 exporter-declared runtime payload projection을 함께 가진다.
- package record는 isolated package manifest/chunks를 같은 runtime projection으로 읽는다.
- cross-surface equality는 edge-specific projection/hash contract를 사용한다.
- exact-key success universe는 하나뿐이며 source, rendered, runtime, package가 모두 같은 decoded exact key-set을 가져야 한다.
- alias declaration은 current exporter behavior를 관찰하는 diagnostic regression input일 뿐 equality universe나 future alias framework를 정의하지 않는다.
- target이 authority universe에 이미 존재하는 declaration은 `existing_target_no_new_key`로 기록할 수 있지만 새 key를 만들 수 없다.
- authority universe 밖 alias target 또는 실제 alias-added key는 `compatibility_blocked_alias_identity_expansion_requires_separate_scope`로 종료한다.
- alias metrics는 `declared_alias_count`, `existing_target_no_new_key_count`, `applied_new_alias_key_count`, `unexpected_emission_count`, `alias_induced_comparison_collision_increase`다.
- PASS에는 마지막 세 count가 모두 `0`이어야 한다.

### Decision and Gate Register

| ID | Fixed/owner choice | Timing | Missing/invalid result |
|---|---|---|---|
| C-1 | `decoded_codepoint_exact_v1` fixed by approved plan | pre-entry | implementation block |
| C-2 | `ascii_lower_v1` fixed by approved plan | pre-entry | implementation block |
| C-3 | typed mismatch routing; technical owner override forbidden | Phase 0A | machine fail |
| C-4 | Route A `windows_uv_python` fixed canonical; Route C required transport regression; Route B rejected | pre-entry approval + Review 3 verification / Phase 3 | acknowledgement missing or either A/C failure blocks |
| C-5 | `live_additive_required_gate` 또는 `blocked_no_live_adoption`; package guard는 두 경우 모두 mandatory | Review 5 | canonical closeout block if not adopted |
| C-6 | exactly one reference role + one exception role per two-member group; resolution power 없음 | Phase 0A proposal → Review 2 ratification → Phase 0B | Branch C |
| C-7 | fixed reviewer eligibility; owner assigns only eligible identity | pre-entry/Review 6 | review block |
| C-8 | execution baseline/worktree disposition | pre-entry | implementation block |

선택된 `plan_approvals/approval-<approval-id>.json`은 C-1/C-2의 유일한 owner approval unit이다. 이 record는 roadmap hash, current plan fingerprint, `decoded_codepoint_exact_v1`, `ascii_lower_v1`, C-6 old/new vocabulary mapping과 다음 exact fields를 직접 hash-bind한다.

```text
c4_route_model_transition_acknowledged = true
c4_route_a_fixed_canonical = true
c4_route_c_required_transport_regression = true
roadmap_or_condition_superseded_by_plan_and_condition = true
package_guard_and_live_required_gate_both_mandatory_for_closeout = true
owner_explicitly_approved = true
final_plan_review_verdict = WARN
final_plan_review_open_critical_count = 0
final_plan_review_open_implementation_blocker_count = 0
final_plan_review_reviewer_closeout_eligible = false
fr5_warning_1_disposition = adopted_during_implementation
fr5_warning_2_disposition = adopted_during_implementation
```

이 record는 Gate A candidate의 bootstrap executor/test/tool manifest/ledger contract/validation report exact paths/hashes와 allowed responsibility version도 결속한다. Phase 1 policy와 invalidation matrix는 이 approval record hash를 소비하며 별도 암묵 owner record로 C-1/C-2/C-4/C-5 강화나 bootstrap executor 승인을 대체하지 않는다.

owner/review authority source의 exact paths:

```text
Iris/build/description/v2/owner_inputs/dvf_3_3_registry_runtime_compatibility/
  plan_approvals/approval-<approval-id>.json
  collision_dispositions/disposition-<disposition-id>.json
  reviews/phase0-contract-review-<review-id>.json
```

세 record는 candidate 생성 전에 tracked/not-ignored, strict schema-valid, exclusive-create immutable이어야 한다. 공통 fields는 `schema_version`, `round_id`, role-specific `record_id`, `record_role`, owner/reviewer identity와 eligibility/provenance, timestamp, selected decision/verdict, target plan/policy/exclusion/disposition/input hashes, rationale, `record_state=issued`, optional predecessor record path/hash/id와 supersession reason이다. `record_id`는 lowercase `[a-z0-9][a-z0-9-]{7,63}`이고 path separator나 `current` token을 허용하지 않으며 filename의 id와 내부 `record_id`가 일치해야 한다. 자기 final hash를 record 안에 넣지 않고 candidate binding manifest와 downstream receipts가 exact versioned path/bytes/hash를 결속한다.

선택된 `collision_dispositions/disposition-<disposition-id>.json`은 collision group/member hashes, C-6 role assignment, no-resolution-power flags를 직접 가진다. 선택된 `reviews/phase0-contract-review-<review-id>.json`은 Review 2 scope, reviewer eligibility, reviewed policy/exclusion/disposition/owner-record paths/hashes, verdict `PASS`, findings 0을 가진다. owner/reviewer record는 technical failure, failed command, hash drift, missing dependency, reviewer ineligibility를 waive할 수 없다.

`current_*` alias와 mutable selector file은 만들지 않는다. plan approval은 owner-approved pre-entry input manifest, collision disposition과 Review 2 record는 Phase 0B branch record가 선택한 exact versioned path/hash만 소비한다. successor는 prior record를 rewrite하지 않고 새 tracked record가 predecessor path/hash/id와 reason을 가리키는 방식만 허용한다. selection baseline에서 role별 predecessor graph를 전부 검증해 selected record가 unique chain head인지 확인한다. selector가 missing/multiple이거나 selected record가 stale head이거나 chain break/fork/cycle/duplicate `record_id`가 있으면 Branch C다.

### C-6 Role Contract

collision member record의 role metadata:

- `role`은 `contract_reference_member` 또는 `bounded_compatibility_exception_member`
- `runtime_resolution_priority = "none"`
- `alias_target = false`
- `lookup_fallback = false`
- `source_mutation_authority = false`
- `runtime_mutation_authority = false`

각 collision group은 이 round에서 정확히 두 member만 허용하며 다음 multiplicity를 모두 만족해야 한다.

```text
member_count = 2
contract_reference_member_count = 1
bounded_compatibility_exception_member_count = 1
role_overlap_count = 0
unassigned_member_count = 0
```

old/new vocabulary trace:

| Roadmap vocabulary | Revised contract vocabulary | Runtime resolution authority |
|---|---|---|
| `canonical_exact_key` | `contract_reference_member` | none |
| `exception_exact_key` | `bounded_compatibility_exception_member` | none |

`contract_reference_member`는 documentation/comparison anchor일 뿐 runtime canonical winner가 아니다. two-member 조건을 벗어나거나 member set/hash/payload가 변하면 기존 role record는 자동 invalidation되고 Phase 0B Branch A를 허용하지 않는다.

### Typed Mismatch Routing

| Failure type | Machine result | Branch | Owner override |
|---|---|---|---|
| planning observation count drift only, all fresh invariants intact | recensus / continue | A eligible | not needed |
| exact duplicate within any surface | FAIL | B handoff or C block | forbidden |
| any source/rendered/runtime/package exact key-set mismatch | FAIL | B handoff | forbidden |
| collision member set/count drift after disposition | FAIL / policy invalidated | C until new disposition | forbidden |
| payload divergence outside exclusions | FAIL | B handoff | forbidden |
| missing surface or required dependency | BLOCKED | C | forbidden |
| new unauthorized comparison collision | FAIL | C until disposition | forbidden |
| any alias-added new key, undeclared emission, or alias cycle | FAIL | separate-scope block or B/C | forbidden |
| hash/freshness drift during attempt | attempt invalid | new attempt | forbidden |

Branch B terminal token은 `compatibility_blocked_authority_correction_handoff_ready`다. 이 상태는 `partial`, compatibility progress, source correction approval을 뜻하지 않는다.

### Environment Assumptions

- Windows canonical execution은 PowerShell 5.1에서 검증한다.
- repository Python command는 `uv run python`을 사용한다.
- actual Lua merge에는 resolved `lua` executable이, syntax validation에는 `tools/check_lua_syntax.ps1`이 요구하는 `luac`가 필요하다.
- accepted offline harness major/minor는 `5.1.x` 또는 `5.4.x`다. 다른 version은 `unsupported_lua_version`으로 차단하고 자동 호환으로 간주하지 않는다.
- missing dependency는 fallback parsing 없이 actionable failure와 non-zero exit를 만든다.
- offline PUC Lua harness PASS는 Kahlua 또는 Project Zomboid full runtime equivalence를 뜻하지 않는다.

---

## 5. Repository Areas Affected

### Code

신규 standalone tooling:

- `Iris/build/description/v2/tools/build/dvf_3_3_registry_runtime_compatibility.py`
- `Iris/build/description/v2/tools/build/run_dvf_3_3_registry_runtime_compatibility.py`
- `Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_runtime_compatibility.py`
- `Iris/build/description/v2/tools/build/export_registry_runtime_records.py`
- `Iris/tools/inspect_registry_runtime_compatibility.ps1`

Gate A round-local governance tooling:

- `Iris/_docs/round3/registry_runtime_compatibility/bootstrap/reserve_registry_runtime_compatibility_attempt.py`
- `Iris/_docs/round3/registry_runtime_compatibility/bootstrap/test_reserve_registry_runtime_compatibility_attempt.py`
- `Iris/_docs/round3/registry_runtime_compatibility/bootstrap/bootstrap_tool_manifest.json`
- `Iris/_docs/round3/registry_runtime_compatibility/bootstrap/bootstrap_executor_validation_report.json`

bootstrap executor는 `round_id=dvf_3_3_registry_runtime_compatibility`와 이 문서에 고정된 ledger/shared-ledger namespace만 허용한다. 다른 round, Registry 전역 attempt framework, compatibility analyzer, source/rendered/runtime/package surface를 import·inspect·modify하지 않는다.

신규 tests/fixtures:

- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_contract.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_bridge.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_chunks.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_windows.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_fixtures.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_current.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_package.py`
- `Iris/build/description/v2/tests/fixtures/registry_runtime_compatibility/lua_merge_harness.lua`
- roadmap fixture files under the same fixture root

수정:

- `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
- `Iris/tools/package_iris.ps1`
- inventory가 `executable_current` 또는 `test_current`로 분류한 exporter/package caller와 adjacent regression tests

required test id `test_dvf_3_3_registry_runtime_compatibility_current.RegistryRuntimeCompatibilityCurrentRouteTest.test_required_gate_runs_standalone_subprocess`, package wrapper, bridge exporter는 analyzer module을 direct import하지 않는다. required unittest와 exporter는 resolved current Python으로 tracked validator path를 child process 실행하고 receipt/result를 parse한다. common algorithm은 standalone analyzer 한 곳에만 있고 unittest/exporter/PowerShell/Lua wrapper는 orchestration/transport/harness 역할만 가진다.

### Docs

- `docs/dvf_3_3_registry_runtime_compatibility_plan.md`
- future policy/claim-boundary/ledger/closeout documents
- final evidence 뒤 필요한 경우 `docs/DECISIONS.md`, `docs/ROADMAP.md` additive draft

`docs/ARCHITECTURE.md`의 현재 boundary를 재정의하지 않는다. top-doc 적용은 user-owned changes와 별도 owner step이다.

### Config

- 신규 required tool/test/artifact가 broad rule에 가려질 때 그 exact path에 한정한 `.gitignore` exceptions; planning checkout에서는 planned durable root가 unignored이므로 그 root를 위한 불필요한 ignore diff를 만들지 않는다
- `Iris/_docs/round3/current_route_required_validations.json`
- `Iris/_docs/round3/registry_runtime_compatibility/ledger_bootstrap_contract.json`
- `Iris/_docs/round3/registry_runtime_compatibility/bundle_lifecycle_events.jsonl`
- immutable lifecycle event records under `Iris/_docs/round3/registry_runtime_compatibility/bundle_lifecycle/`
- immutable durable bundle files under `Iris/_docs/round3/registry_runtime_compatibility/bundles/<bundle-id>/`
- append-only `Iris/_docs/round3/registry_runtime_compatibility/attempt_events.jsonl`
- immutable per-attempt records under `Iris/_docs/round3/registry_runtime_compatibility/attempts/attempt-NNNN/`
- immutable final governance packets under `Iris/_docs/round3/registry_runtime_compatibility/attempts/attempt-NNNN/closeout/`
- owner input records under `Iris/build/description/v2/owner_inputs/dvf_3_3_registry_runtime_compatibility/`

`Iris/_docs/round3/round3_active_core_closure.json`은 read-only protected config다. current core list와 `current_route_allowed_tooling_modules`를 모두 변경하지 않는다. allowlist expansion이 필요하다고 판명되면 live adoption을 차단하고 별도 reviewed scope로 이관한다.

### Generated Artifacts and Evidence Classes

Attempt root:

```text
Iris/build/description/v2/staging/
  dvf_3_3_registry_runtime_compatibility/
    attempts/
      attempt-0001/
        phase0/
        phase1/
        phase2/
        phase3/
        phase4/
        phase5/
```

attempt id는 `attempt-` + zero-padded 4-digit monotonic integer다. first attempt 이전 bootstrap과 allocation contract:

1. Gate A는 owner-approved governance-only bootstrap worktree에서 다음 exact files를 만들고 검증한다.

```text
Iris/build/description/v2/owner_inputs/dvf_3_3_registry_runtime_compatibility/
  plan_approvals/approval-<approval-id>.json

Iris/_docs/round3/registry_runtime_compatibility/
  ledger_bootstrap_contract.json
  attempt_events.jsonl                         # zero-byte
  bundle_lifecycle_events.jsonl                # zero-byte
  bootstrap/
    reserve_registry_runtime_compatibility_attempt.py
    test_reserve_registry_runtime_compatibility_attempt.py
    bootstrap_tool_manifest.json
    bootstrap_executor_validation_report.json
```

이 files와 future baseline에서 실제로 필요할 때만 그 exact paths의 `.gitignore` exceptions를 별도 bootstrap commit으로 commit하고 owner가 이 commit을 새 execution baseline으로 승인한다. plan approval record 외 owner disposition/Review 2 record, production compatibility tooling/test, source inspection, attempt evidence, bundle, live config를 같은 commit에 섞지 않는다.

`bootstrap_tool_manifest.json`은 executor/test의 normalized repository path, role, schema version, SHA-256, byte count, standard-library-only dependency rule, allowed round id/root, resolved bootstrap Python path/version/hash, resolved Git executable path/version/hash를 결속하며 자기 hash를 포함하지 않는다. `ledger_bootstrap_contract.json`은 manifest hash, exact CLI schema, mutex name derivation, ledger/shared-ledger paths, event/record schemas, permitted Git paths/commit message prefix, partial-state matrix version을 결속한다.

Gate A는 candidate executor/test/manifest/contract bytes를 먼저 고정하고 test file을 resolved bootstrap Python의 isolated mode로 실행해 command/stdout/stderr/exit/executor-test-contract hashes를 `bootstrap_executor_validation_report.json`에 기록한다. positive reservation, concurrent reservation, wrong branch/prefix, record/event partial states, manual/substituted executor, cross-round/root escape, open attempt blocks second reservation, terminal completion permits next reservation, clean worktree with open attempt still blocks fixtures가 모두 expected stage/code와 일치해야 한다. Gate A review 뒤 versioned owner plan approval record가 이 exact candidate/report hashes와 두 FR5 warning의 `adopted_during_implementation` disposition을 승인한 다음 한 commit으로 bootstrap한다. Gate B는 committed test/hash를 다시 검증한다. executor/test/contract/report bytes가 review 뒤 바뀌면 기존 approval을 재사용하지 않고 새 Gate A review/bootstrap commit/owner re-baseline을 요구한다.

Gate B exact invocation:

```powershell
<bootstrap-python> -I -B Iris/_docs/round3/registry_runtime_compatibility/bootstrap/reserve_registry_runtime_compatibility_attempt.py reserve --contract Iris/_docs/round3/registry_runtime_compatibility/ledger_bootstrap_contract.json --preentry-input-manifest <owner-approved-preentry-input-manifest> --repo-root <selected-worktree-root> --expected-branch <owner-approved-integration-branch> --expected-starting-prefix <owner-approved-prefix-sha256> --reservation-receipt <local-reservation-receipt> --gate-report <local-preimplementation-gate-report>
```

executor responsibility는 named mutex, git-common-dir/branch/prefix census, canonical event-ledger replay, nonterminal attempt census, reservation record/event transaction, exact reservation commit, shared ledger committed-prefix update, local attempt-root exclusive-create, partial-state reconciliation, reservation receipt와 Gate B predicate report로 제한한다. compatibility census, source/rendered/runtime/package read, exporter/package modification, candidate generation, required-validation adoption, PASS claim은 code-level denylist와 tests로 금지한다. shell command composition, alternate executor, manual Git/PowerShell reservation은 허용하지 않는다.

2. `git rev-parse --path-format=absolute --git-common-dir` 결과를 hash한 repository coordination key를 만든다.
3. canonical lock은 Windows named mutex `IrisRegistryRuntimeCompatibility-<coordination-key>` 하나로 고정한다. lockfile fallback은 없다.
4. mutex wait timeout은 60초다. timeout은 `attempt_lock_timeout`; owner/manual stale override는 허용하지 않는다.
5. lock 안에서 selected worktree가 owner-approved integration branch의 tip이며 clean인지, tracked event prefix가 approved canonical prefix와 같은지, shared ledger의 last committed prefix가 같은지 다시 검사한다. canonical `attempt_events.jsonl`을 replay해 valid reservation에서 valid terminal을 뺀 `nonterminal_attempt_count`와 sorted `open_attempt_ids[]`를 계산한다. count가 `0`이고 ids가 empty일 때만 진행하며 clean worktree/prefix parity가 참이어도 open attempt가 하나 이상이면 `open_attempt_exists`로 새 reservation을 차단한다. fetch/network 추정을 사용하지 않으며 local approved ref가 불일치하면 block한다.
6. abandoned mutex가 반환되면 OS가 lock을 회수한 뒤 `abandoned_mutex_recovery_receipt.json`을 만들고 durable events/records, shared ledger, existing local roots, integration-branch prefix를 전부 recensus한다. recensus 불일치 시 allocation을 차단한다.
7. nonterminal census가 `0`임을 gate report에 고정한 뒤 모든 surface에 없는 next integer를 선택하고 reservation record bytes와 next event line bytes를 local transaction staging에 먼저 render해 schema, prior-prefix hash, record hash를 검증한다.
8. canonical `reservation_record.json`을 exclusive-create하고 file contents와 directory metadata를 flush한 뒤, `attempt_events.jsonl`을 exclusive append handle로 열어 정확히 한 line을 append하고 durable flush한다. 기존 prefix bytes는 바꾸지 않는다.
9. ledger를 다시 읽어 `old_prefix + exact_one_event`, record hash, event hash chain을 검증한 뒤 exact record/ledger paths만 stage하여 owner-approved integration branch에 reservation commit을 만든다. Phase 0은 이 commit이 성공하기 전에 시작하지 않는다.
10. reservation commit/hash와 committed event prefix를 shared reservation ledger에 exclusive append/flush하고 local attempt root를 exclusive-create한 뒤 `attempt_reservation_receipt.json`을 기록한다. receipt와 Gate B report는 `reservation_preflight_nonterminal_attempt_count=0`, `reservation_preflight_open_attempt_ids=[]`, replayed prefix/hash, census timestamp를 직접 포함한다.
11. lock/event/record/VCS/shared-ledger/root write 중 하나라도 실패하면 아래 partial-state matrix로 reconcile하고, 성공적으로 sealed reservation이 아니면 `attempt_allocation_failure`로 implementation을 차단한다.

shared reservation ledger의 exact local path는 `<git-common-dir>/iris_registry_runtime_compatibility/attempt_reservations.jsonl`이다. 이 파일은 concurrent local worktree coordination용 비권위 surface이며 PASS evidence가 아니다. named mutex는 process 종료 시 OS가 해제하므로 stale lockfile 삭제 절차가 없다.

canonical history:

```text
Iris/_docs/round3/registry_runtime_compatibility/
  ledger_bootstrap_contract.json
  attempt_events.jsonl
  bundle_lifecycle_events.jsonl
  bootstrap/
    reserve_registry_runtime_compatibility_attempt.py
    test_reserve_registry_runtime_compatibility_attempt.py
    bootstrap_tool_manifest.json
    bootstrap_executor_validation_report.json
  bundle_lifecycle/
    event-NNNN-<bundle-id>-<state>.json
  attempts/attempt-NNNN/
    reservation_record.json
    terminal_record.json
    evidence_manifest.json
    failure_summary.json       # failed/invalid/abandoned only
    closeout/                  # successful canonical closeout only
      post_adoption_current_route_result.json
      live_gate_package_finalization_result.json
      final_machine_report.json
      independent_review_gate_report.json
      owner_canonical_seal_gate_report.json
      final_registry_runtime_compatibility_report.json
      final_claim_scan_report.json
      closeout_content_manifest.json
      terminal_hash_seal.json
      durable_closeout_packet_manifest.json
```

- `attempt_events.jsonl`은 reservation event와 terminal event를 별도 line으로 append한다.
- 각 event는 `event_sequence`, `attempt_id`, `event_type`, `record_path`, `record_sha256`, `previous_event_sha256`를 가진다.
- successful `terminal` event는 추가로 `durable_closeout_packet_commit`, `durable_closeout_packet_manifest_path`, `durable_closeout_packet_manifest_sha256`, `terminal_hash_seal_path`, `terminal_hash_seal_sha256`를 필수로 가진다. failed/invalid/abandoned terminal은 해당 필드를 `not_applicable` reason과 함께 명시한다.
- 기존 prefix line의 수정/삭제/재정렬을 금지하고 hash-chain과 baseline prefix hash를 검증한다.
- `reservation_record.json`, `terminal_record.json`, `evidence_manifest.json`, optional `failure_summary.json`은 exclusive-create immutable files다.
- terminal enum은 `failed_pre_phase0`, `failed`, `invalid`, `abandoned`, `complete`다. attempt당 reservation 1개와 terminal 1개만 허용한다.
- abandoned-mutex recensus에서 valid reservation event/record는 있으나 terminal이 없는 exactly-one attempt만 machine-generated `abandoned` terminal record와 terminal event로 닫을 수 있다. reservation/event mismatch나 둘 이상의 orphan attempt는 자동 복구하지 않고 block한다.
- normal `reserve` preflight에서 `nonterminal_attempt_count=1`이면 해당 `open_attempt_ids[0]`을 resume하거나 plan-defined terminal transaction으로 먼저 닫아야 하며 새 ID를 할당하지 않는다. `reserve` command가 편의를 위해 terminal을 합성하지 않는다. count가 `2` 이상이면 `multiple_nonterminal_attempts`로 hard block하고 owner/manual waiver를 금지한다.
- terminal commit과 shared-prefix update가 완료된 뒤 mutex 안에서 ledger를 다시 replay해 prior open ID가 terminal임을 확인해야 다음 reservation이 가능하다.
- mutable `attempt_index.json`은 authority가 아니다. 필요하면 event ledger에서 재생성하는 diagnostic projection으로만 생성하며 required artifact가 될 수 없다.
- pre-Phase 0 failure와 partial execution도 할당된 ID를 소비한다.
- claim-bearing file write는 overwrite가 아닌 exclusive-create만 허용한다.
- reservation과 terminal append는 각각 `record render → exclusive-create/flush → exact-one event append/flush → prefix validation → exact VCS commit → shared-ledger committed-prefix append` 순서를 사용한다.
- terminal transaction 중간 실패도 같은 partial-state 규칙을 적용하며 prior prefix나 immutable record를 삭제해 retry하지 않는다.
- bootstrap executor path/hash/contract hash는 reservation record와 event에 포함하고 Phase 1 implementation toolchain manifest가 `bootstrap_executor_provenance` role로 같은 hashes를 import한다. 사후 manifest 기록이 Gate B provenance를 대체하지 않는다.

Partial-state matrix:

| Observed state under mutex | Required action | Result |
|---|---|---|
| record exists / event missing | record가 expected next ID/prefix/schema/hash와 일치할 때만 그 pre-existing record를 가리키는 event를 append하고 즉시 `failed_pre_phase0` terminal transaction으로 닫는다 | no record reconstruction; ID consumed |
| event exists / record missing | record를 사후 재구성하지 않는다 | `event_record_missing` block |
| record+event exist / reservation commit missing | exact bytes가 approved prefix의 one-event extension이면 그 same bytes를 recovery commit하고 즉시 `failed_pre_phase0`로 닫는다 | retroactive materialization count 0 |
| shared ledger committed row exists / durable record 또는 event missing | shared row로 durable history를 만들지 않는다 | `shared_durable_divergence` block |
| durable reservation commit exists / shared ledger row missing | durable commit/prefix에서 non-authority shared row를 catch up하고 attempt를 `abandoned`로 닫는다 | canonical bytes unchanged |
| local root exists / reservation record missing | root를 attempt authority로 승격하거나 ID를 재사용하지 않는다 | `orphan_local_attempt_root` block |
| one valid reservation without terminal | existing attempt를 resume하거나 별도 terminal transaction으로 먼저 닫는다 | `open_attempt_exists`; no new ID |
| two or more valid reservations without terminal | 자동 terminal/supersession을 만들지 않는다 | `multiple_nonterminal_attempts` hard block |
| selected/approved/shared committed prefixes differ | merge/supersession을 자동 생성하지 않는다 | `event_prefix_divergence` block |

normal attempt는 owner-approved single integration branch에서만 실행한다. cross-branch chain supersession은 이 plan의 자동 recovery가 아니며 별도 owner-reviewed governance scope다. `selected_worktree_event_prefix = approved_canonical_event_prefix = shared_reservation_ledger_committed_prefix`가 reservation과 terminal transaction 직전에 모두 참이어야 한다.

local staging supporting evidence는 active attempt 동안 필수지만 terminal records가 durable하게 봉인된 뒤에는 clean-checkout required surface가 아니다. clean checkout은 tracked bootstrap executor/contract, attempt and lifecycle ledgers/records, immutable terminal/evidence records, durable promoted bundle, successful attempt의 durable closeout packet actual bytes를 검증한다. local supporting evidence가 없다는 사실은 `local_supporting_evidence_available=false` diagnostic으로 기록하되 current route를 실패시키지 않는다. `required_durable_reference_missing_count`, `attempt_reuse_count`, `duplicate_reservation_count`, `prior_event_mutation_count`, `event_hash_chain_break_count`, `claim_file_overwrite_attempt_count`, `unreconciled_partial_event_transaction_count`, `event_prefix_divergence_count`, `retroactive_attempt_materialization_count`, `durable_closeout_artifact_missing_count`, `durable_closeout_hash_mismatch_count`, `bundle_lifecycle_chain_break_count`는 모두 `0`이어야 한다.

Evidence class:

| Class | Location | Live manifest eligibility | Retention |
|---|---|---|---|
| `required_durable` | tracked `Iris/_docs/round3/registry_runtime_compatibility/` 또는 tracked test | eligible after promotion/hash check; closeout packet is governance authority, not live-manifest input | append/supersede only |
| `supporting_generated` | local attempt phase directories | not directly eligible | active execution과 review 동안 보존; terminal sealing 뒤 clean-checkout requirement 아님 |
| `attempt_local_temp` | attempt `tmp/` or fresh package root | never eligible | cleanup allowed after receipt/hash capture |
| `diagnostic_only` | attempt diagnostics | never eligible and never PASS-bearing | preserve on failure |

Live manifest는 attempt-local staging path나 post-adoption closeout packet을 required artifact로 직접 참조하지 않는다. 성공 attempt의 approved source bundle만 complete promotion report를 거쳐 immutable durable bundle로 승격한다. 모든 attempt는 terminal record와 evidence inventory/hash를 append-only event ledger에 결속하며 successful canonical attempt는 tracked closeout content를 추가로 요구한다. clean-checkout validator는 local supporting file의 존재가 아니라 tracked bootstrap/terminal/bundle/lifecycle/closeout bytes와 hash-chain을 검사한다.

주요 attempt evidence:

- `phase0/bootstrap_tool_manifest.json` byte-copy/hash-binding receipt
- `phase0/bootstrap_executor_validation_report.json` byte-copy/hash-binding receipt
- `phase0/governance_ledger_bootstrap_report.json`
- `phase0/roadmap_input_materialization_report.json`
- `phase0/implementation_plan_fingerprint_report.json`
- `phase0/roadmap_plan_traceability_matrix.json`
- `phase0/revised_plan_review_report.json`
- `phase0/allowlist_contract_scope_report.json`
- `phase0/exporter_package_invocation_inventory.json`
- `phase0/invocation_migration_matrix.json`
- `phase0/original_dirty_doc_invocation_comparison.json`
- `phase0/attempt_reservation_receipt.json`
- `phase0/abandoned_mutex_recovery_receipt.json` when applicable
- `phase0/preimplementation_gate_report.json`
- `phase0/execution_baseline_report.json`
- `phase0/fresh_surface_census.json`
- `phase0/dual_identity_representation_report.json`
- `phase0/comparison_collision_inventory.json`
- `phase0/payload_equivalence_report.json`
- `phase0/alias_regression_report.json`
- tracked selected owner input `plan_approvals/approval-<approval-id>.json`
- tracked selected owner input `collision_dispositions/disposition-<disposition-id>.json`
- tracked selected Review 2 input `reviews/phase0-contract-review-<review-id>.json`
- `phase0/artifact_binding_manifest.json`
- `phase0/phase0_disposition_verdict.json`
- `phaseN/cross_phase_input_freshness_report.json` for every phase entry
- `phase1/identity_contract_report.json`
- `phase1/policy_hash_report.json`
- `phase1/invalidation_matrix_report.json`
- `phase1/implementation_toolchain_manifest.json`
- `phase1/candidate/authority/plan_approvals/approval-<approval-id>.json`
- `phase1/candidate/authority/collision_dispositions/disposition-<disposition-id>.json`
- `phase1/candidate/authority/reviews/phase0-contract-review-<review-id>.json`
- `phase1/candidate/candidate_contract_binding_manifest.json`
- `phaseN/implementation_toolchain_freshness_<checkpoint>.json` for every required checkpoint, including exact promotion input `phase5/implementation_toolchain_freshness_before_durable_promotion.json`
- `phase2/bridge_preflight_inputs.json`
- `phase2/bridge_preflight_report.json`
- `phase2/compatibility_surface_inputs.json`
- `phase2/chunk_generation_compatibility_report.json`
- `phase2/chunk_merge_compatibility_report.json`
- `phase2/runtime_reconstruction_report.json`
- `phase2/package_projection_compatibility_report.json`
- `phase2/package_transport_observation_report.json`
- `phase2/package_guard_invocation_receipt.json`
- `phase2/package_guard_contract_report.json`
- `phase3/windows_surface_inputs.json`
- `phase3/windows_route_conformance_report.json`
- `phase3/windows_projection.json`
- `phase3/windows_projection_report.json`
- `phase3/windows_round_trip_report.json`
- `phase3/powershell_5_1_execution_report.json`
- `phase4/fixture_matrix_report.json`
- `phase4/current_full_payload_regression_report.json`
- `phase4/package_projection_regression_report.json`
- `phase4/determinism_report.json`
- `phase4/lua_merge_report.json`
- `phase4/lua_syntax_report.json`
- `phase4/default_route_compatibility_report.json`
- `phase5/pre_adoption_compatibility_machine_report.json`
- `phase5/durable_promotion_report.json`
- `phase5/durable_bundle_lifecycle_report.json`
- `phase5/bundle_lifecycle_event_receipt.json`
- `phase5/promotion-staging/<bundle-id>/durable_bundle_manifest.json` before directory publish
- `phase5/required_gate_candidate_diff.json`
- `phase5/candidate_manifest_route_probe.json`
- `phase5/post_promotion_package_probe.json`
- `phase5/post_adoption_current_route_result.json`
- `phase5/live_gate_package_finalization_result.json`
- `phase5/final_machine_report.json`
- `phase5/independent_review_gate_report.json`
- `phase5/owner_canonical_seal_gate_report.json`
- `phase5/final_registry_runtime_compatibility_report.json`
- `phase5/final_claim_scan_report.json`
- `phase5/closeout_content_manifest.json`
- `phase5/terminal_hash_seal.json`
- `phase5/durable_closeout_packet_manifest.json`
- `phase5/durable_closeout_packet_commit_receipt.json`

---

## 6. Planned Changes

### Change 0 — Provenance, Baseline, Attempt Allocation, and Entry Gate

Purpose:

production mutation 전에 approved input identity, clean baseline, blocker-zero를 machine-readable하게 결속한다.

Implementation Notes:

- repo-local roadmap/review와 original attachment의 byte hash, canonical text equivalence, materialization normalization을 검사한다.
- external plan fingerprint report가 현재 plan bytes/hash와 superseded plan hash를 기록한다. plan 본문에 자신의 최종 hash를 넣지 않아 self-reference를 만들지 않는다.
- roadmap section/requirement를 plan section/change/validation/artifact에 연결하고 roadmap fixture 1~10을 exact plan fixture ID에 1:1로 연결한 traceability matrix를 만든다.
- `EXECUTION_CONTRACT.md`, template, top-doc readpoint hash와 적용 상태를 기록한다.
- `round3_run_contract_tests.py`의 exact CLI surface에서 `--required-validations` 존재를 검사한다. 부재 시 runner를 이 scope에서 암묵 수정하지 않고 `compatibility_blocked_required_dependency`로 종료한다.
- `DECISIONS.md`의 import-allowlist 문장과 runner의 `tools.build.*` import 검사 구현을 대조해 `allowlist_contract_scope=import_closure_only`를 기록한다. authority text 또는 runner가 executed-tooling closure를 요구하면 subprocess를 진행하지 않고 `compatibility_blocked_allowlist_expansion_requires_separate_scope`로 종료한다.
- owner-approved HEAD/branch와 clean selected worktree를 검증하고 original dirty paths를 preservation inventory에 둔다.
- final incremental plan review의 `WARN`, Critical `0`, implementation blocker `0`, bootstrap allowed `true`와 두 warning disposition을 검사한 뒤 Gate A에서 owner-approved round-local bootstrap executor/contract/test/report, selected versioned plan approval record, zero-event ledgers만 commit하고 exact paths의 tracked/not-ignored 상태를 clean checkout에서 확인한다. current census가 unignored인데도 `.gitignore`를 불필요하게 수정하지 않으며 broad unignore를 금지한다.
- Gate A executor/test/manifest/validation report의 committed bytes/hash와 forbidden responsibility scan을 검증한다. Gate B reservation receipt의 executor/contract/python/git hashes가 Gate A와 정확히 같고 `ad_hoc_or_manual_reservation_count=0`, `reservation_preflight_nonterminal_attempt_count=0`, `reservation_preflight_open_attempt_ids=[]`인지 확인한다.
- owner가 bootstrap commit을 baseline과 single integration branch로 다시 승인한 뒤 committed executor를 exact CLI로 실행해 attempt id를 atomic reserve하고 reservation commit/Gate B report를 만든다. commit 뒤 local `governance_ledger_bootstrap_report.json`과 bootstrap provenance를 phase0 supporting evidence에 byte-copy/hash-bind한다.
- `implementation_entry_allowed=true` 뒤 신규 compatibility tooling/tests만 작성하고, existing exporter/package/live config를 건드리기 전에 아래 invocation census와 production integration gate를 실행한다.
- invocation execution authority는 owner-approved clean execution baseline 하나다. 그 baseline의 tracked/non-ignored code, tests, scripts, current operator docs/command manifests를 대상으로 exporter CLI/direct import/function call과 package script path/command를 AST + exact token scan으로 census한다. generated caches와 historical evidence는 별도 route class로 분류하되 scan denominator에서 조용히 제외하지 않는다.
- original worktree의 dirty `ARCHITECTURE.md`, `DECISIONS.md`, `ROADMAP.md`와 다른 dirty docs는 `original_dirty_doc_invocation_comparison.json`에 preservation-only delta로 기록하고 authority inventory row, route class, migration completion count에 포함하지 않는다. owner가 그 text를 closeout 전 execution branch에 적용하려면 application 뒤 inventory/migration review를 새로 실행하며, 적용하지 않으면 `owner_application_pending`으로 둔다.
- `exporter_package_invocation_inventory.json`과 `invocation_migration_matrix.json`의 caller path, command origin, route class, current invocation, required/default invocation, policy context, migration required/status, regression test, unresolved status를 채우고 `unknown=0`, planned `unmigrated=0`을 요구한다.
- `round3_active_core_closure.json` baseline hash를 protected config로 기록한다.

Validation:

- materialized input canonical text parity
- current plan fingerprint exact match
- traceability orphan requirement count 0
- roadmap fixture 1~10 unmapped/duplicate mapping count 0
- revised review open critical/blocker count 0
- final review WARN disposition fields complete and governance bootstrap allowed
- versioned plan approval exact path/id/hash selected with no `current_*` authority pointer
- reservation preflight nonterminal attempt count 0 and open attempt ids empty
- selected worktree clean/HEAD match
- selected integration branch/baseline/bootstrap commit match
- bootstrap executor/test/contract/report hash match와 scope violation/manual substitution count 0
- pre-entry required path ignored/untracked count 0
- selected/approved/shared committed event prefix exact equality
- event append partial-state unresolved count 0
- retroactive attempt materialization count 0
- target overlap unresolved count 0
- invocation inventory unknown count 0
- invocation migration plan unresolved count 0
- invocation authority baseline is owner-approved clean baseline
- dirty original docs consumed as authority count 0
- allowlist planned mutation count 0
- allowlist contract scope `import_closure_only`
- required-validation override flag present
- attempt event-chain/immutable-record/root parity와 reuse/prior-event-mutation count 0
- `implementation_entry_allowed=true`
- `production_integration_allowed=true` before existing exporter/package/live config mutation

### Change 1 — Phase 0A Dual Census and Phase 0B Disposition

Purpose:

ordinary dictionary materialization 전에 exact/code-point/raw-byte/comparison identity, aliases, payloads를 losslessly census하고 typed failure route를 결정한다.

Implementation Notes:

- Phase 0A는 source facts/decisions/overlay, raw rendered JSON pairs, raw Lua assignments, isolated package assignments를 ordered records로 읽는다.
- JSON object pair reader는 exact duplicate와 case comparison collision을 dictionary collapse 전에 기록한다.
- Lua reader는 manifest-declared chunk order와 raw table assignments를 보존한다.
- format adapter record는 `raw_token_text`, `raw_token_bytes_sha256`, `decoded_format_string`, `decoded_utf8_bytes_sha256`, `decoded_exact_codepoints`, `decoded_exact_key_sha256`, `comparison_key`를 구분한다.
- JSON `"\u0042ase.LemonGrass"`와 literal `"Base.LemonGrass"`처럼 decoded exact key가 같은 pair는 raw token이 달라도 exact duplicate다.
- Lua `["Base.\076emonGrass"]`와 literal `["Base.LemonGrass"]`도 Lua string escape decode 뒤 exact duplicate로 판정한다.
- source/rendered/runtime/package는 하나의 decoded exact key universe와 비교하며 symmetric difference가 모두 `0`이어야 한다.
- existing alias declaration은 diagnostic contribution만 계량하고 `applied_new_alias_key_count=0`을 요구한다.
- Phase 0A는 unfiltered payload delta와 proposed exclusion/role/policy를 만들지만 final payload equivalence나 final Branch A를 기록하지 않는다.
- technical mismatch는 typed matrix대로 machine fail한다. owner record로 Branch A로 바꾸지 않는다.
- Phase 0A terminal token은 `branch_a_machine_eligible`, `branch_b_machine_required`, `branch_c_blocked` 중 하나다.
- `branch_a_machine_eligible`일 때 Review 2가 exclusion manifest, C-6 multiplicity/role, proposed policy, invalidation contract를 ratify한다.
- owner는 exact selected tracked `collision_dispositions/disposition-<disposition-id>.json`으로 C-6 group/member roles를 승인하고 Review 2는 exact selected tracked `reviews/phase0-contract-review-<review-id>.json`으로 reviewed bytes/hashes, reviewer eligibility, findings 0, verdict PASS를 기록한다.
- collision owner disposition과 Review 2 record는 exact owner-input paths만 stage하는 immutable authority commit으로 owner-approved integration branch에 먼저 commit한다. attempt implementation/result files나 source/runtime mutation을 이 authority commit에 섞지 않는다.
- plan approval, owner disposition, Review 2 records의 actual bytes가 모두 present/tracked/not-ignored/schema-valid이고 reviewed policy/exclusion/disposition hashes 및 authority commit과 일치한 뒤에만 Phase 0B가 final Branch A/B/C를 기록한다.

Phase 0B result:

```text
Branch A = machine integrity PASS
           + Review 2 ratification PASS
           + all observed collision groups have valid bounded disposition
           + C-6 multiplicity/roles valid
           + protected hashes fresh

Branch B = authority/source correction handoff required

Branch C = missing dependency/decision, invalid policy, unauthorized collision,
           or execution contract block
```

### Change 2 — Phase 1 Identity, Policy, Invalidation, and Freshness Contract

Purpose:

review-ratified identity/comparator와 bounded exception을 versioned policy로 봉인한다.

Implementation Notes:

- Phase 0A가 제안하고 Review 2가 ratify한 policy/exclusion/disposition을 byte-for-byte Phase 1 candidate files로 봉인한다.
- candidate policy exact path는 `<attempt-root>/phase1/candidate/registry_runtime_compatibility_policy.json`이다.
- candidate exclusion exact path는 `<attempt-root>/phase1/candidate/registry_runtime_compatibility_identity_field_exclusions.json`이다.
- candidate disposition exact path는 `<attempt-root>/phase1/candidate/current_collision_disposition.json`이다.
- candidate plan approval exact path는 `<attempt-root>/phase1/candidate/authority/plan_approvals/approval-<approval-id>.json`이다.
- candidate owner disposition exact path는 `<attempt-root>/phase1/candidate/authority/collision_dispositions/disposition-<disposition-id>.json`이다.
- candidate Review 2 exact path는 `<attempt-root>/phase1/candidate/authority/reviews/phase0-contract-review-<review-id>.json`이다.
- candidate binding manifest exact path는 `<attempt-root>/phase1/candidate/candidate_contract_binding_manifest.json`이다.
- 세 authority records는 selector가 지목한 tracked owner/review source bytes의 byte-identical copy이며 candidate에서도 versioned relative subpath를 보존한다. source/candidate selected path/id/hash parity와 successor chain을 검증하며 missing/untracked/ignored record를 embedded hash literal이나 `current` alias로 대체하지 않는다.
- policy는 algorithm id/version, JSON/Lua decode rules, normalization forbidden rule, ASCII fold vectors, non-ASCII failure, single exact universe, comparison universe를 명시한다.
- exclusion manifest는 permitted identity reference fields만 열거하고 wildcard를 금지한다.
- disposition은 exact member set/hash, role multiplicity, edge payload projection hashes, Phase 0 source artifact binding, selected C-6 owner record id/path/hash를 결속한다. sibling candidate leaf final hash는 포함하지 않는다.
- policy는 `plan_contract_approval_record_id`, candidate-relative `plan_contract_approval_record_path`, `plan_contract_approval_record_sha256`를 직접 포함하고 이 exact versioned triple이 C-1/C-2 approval authority다.
- Review 2 record는 reviewed policy/exclusion/disposition/owner-record hashes를 포함하지만 policy/exclusion/disposition은 Review 2 final hash를 포함하지 않는다. authority record는 policy/disposition/binding/downstream hash를 역참조하지 않는다.
- policy/exclusion/disposition/authority leaf는 아래에서 허용한 단방향 authority/review hash 외 sibling final SHA-256, binding manifest final hash, 자기 final hash, downstream report hash를 포함하지 않는다. 허용 edges는 plan-approval→policy, owner-disposition→disposition, reviewed-leaves→Review-2뿐이다.
- external binding manifest는 manifest directory 기준 normalized relative path만 사용하고 relative path 순으로 정렬한 정확히 여섯 leaf rows를 갖는다: policy, exclusion, disposition, selected versioned plan approval, selected versioned collision owner disposition, selected versioned Phase 0/Review 2 contract review. 각 row는 `artifact_path`, `artifact_role`, role-specific `record_id` 또는 `not_applicable`, `schema_version`, `byte_count`, `sha256`을 결속한다.
- candidate와 durable bundle은 같은 leaf filenames/layout을 사용하므로 binding manifest bytes를 바꾸지 않고 각각 자기 directory를 base로 resolve한다. absolute/parent-traversal path는 금지한다.
- binding manifest 자체 hash는 `policy_hash_report.json`과 downstream consumer receipt가 기록하며 binding manifest 내부에는 넣지 않는다.
- candidate consumer는 binding manifest를 먼저 검증한 뒤 manifest에 열거된 exact leaf bytes만 소비한다.
- candidate files와 binding manifest는 attempt root containment 및 acyclic binding check 뒤 immutable하게 닫는다.
- claim-affecting implementation edit가 끝나고 Phase 2 evidence를 만들기 전에 `<attempt-root>/phase1/implementation_toolchain_manifest.json`을 봉인한다. 이후 claim-affecting tool/test/harness/fixture를 수정하면 같은 attempt를 계속하지 않는다.
- manifest root roles는 bootstrap executor provenance, canonical analyzer, standalone validator, runner, Windows record exporter, bridge exporter, package script, Windows wrapper, Lua merge harness, Lua syntax checker, required unittest, focused compatibility tests/fixtures, consumed schemas다. bootstrap provenance row는 Gate A executor/test/tool manifest/contract/report hashes와 reservation receipt hash를 import한다. Python project-local transitive import closure, PowerShell dot-source/invoked child closure, test fixture dependency를 계산하고 unclassified dependency를 허용하지 않는다.
- 각 toolchain row는 normalized repository-relative `path`, `role`, `sha256`, `byte_count`, `tracked`, `not_ignored`, `dependency_parent_paths[]`를 가진다. row ordering과 canonical JSON serialization을 고정하고 manifest는 자기 hash를 포함하지 않는다.
- `package_guard_contract_report.json`, pre-adoption report, durable bundle manifest, candidate/live required manifest는 이 toolchain manifest hash를 결속한다.
- 다음 checkpoint마다 current checkout을 baseline toolchain manifest와 byte 비교한 별도 freshness receipt를 만든다.

```text
before_phase2_evidence
before_pre_adoption_report
before_durable_promotion
before_candidate_manifest_probe
before_live_adoption
before_official_post_adoption_route
before_final_machine_report
```

- durable promotion 전 receipt는 `implementation_toolchain_freshness_report.json`으로 승격하며 이후 checkpoint receipt는 selected durable manifest hash를 직접 소비한다.
- 모든 checkpoint에서 `implementation_toolchain_drift_count=0`, `required_tool_missing_count=0`, `required_tool_untracked_count=0`, `required_tool_ignored_count=0`, `unclassified_tool_dependency_count=0`이어야 한다.
- invalidation predicates:
  - member set/count/hash drift
  - payload divergence
  - exclusion expansion
  - policy/comparator/algorithm change
  - source/rendered/runtime/package input hash drift
  - alias declaration drift 또는 applied new alias key count 증가
  - new unauthorized collision
  - owner/reviewer record mismatch
  - owner/review authority record missing/untracked/ignored/schema/eligibility/decision/supersession drift
  - implementation toolchain path/hash/tracking/dependency-closure drift
- 각 phase 진입 직전에 Phase 0 protected input hashes와 current hashes를 비교한다.
- protected input 또는 implementation toolchain freshness mismatch는 current attempt를 invalid로 닫고 새 attempt에서 Phase 0부터 재시작한다. live adoption 뒤 drift가 발견되면 selected bundle을 rewrite하지 않고 gate가 current route/package를 fail-closed하도록 둔 채 새 attempt를 요구한다.

### Change 3 — Phase 2 Bridge, Chunk, Actual Reconstruction, and Package Guards

Purpose:

bridge export부터 isolated package까지 exact identity/payload binding과 overwrite-free reconstruction을 강제한다.

Implementation Notes:

- `export_dvf_3_3_lua_bridge.py`는 compatibility analyzer/validator module을 direct import하지 않는다. `tools.build.dvf_3_3_registry_runtime_compatibility`, bare module import, dynamic import 모두 forbidden이다.
- exporter는 writer/dictionary materialization 전에 exact tracked validator child process를 실행한다.

```powershell
<current-python> -B Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_runtime_compatibility.py --bridge-preflight --bridge-preflight-input-manifest <bridge-preflight-input-manifest> --policy-context <candidate-or-canonical_durable> --policy <policy-path> --disposition <disposition-path> --binding-manifest <binding-manifest-path> --out <bridge-preflight-receipt>
```

- `<current-python>`은 exporter를 실행 중인 `sys.executable`의 resolved path다. shell search, module invocation, implicit fallback을 사용하지 않는다.
- exporter CLI는 bridge preflight input manifest, policy context/path, disposition path, binding manifest path, receipt path를 child command에 그대로 전달한다.
- `bridge_preflight_inputs.json`은 rendered path/hash/byte count, candidate binding manifest path/hash, policy/disposition resolved paths/hashes, toolchain manifest path/hash, producer attempt id를 explicit하게 결속한다. `AttemptRoot` 또는 exporter defaults에서 이 input을 탐색하지 않는다.
- bridge preflight의 책임은 raw rendered property pairs의 pre-materialization exact duplicate/comparison collision, candidate/canonical-durable contract binding, rendered/toolchain freshness까지다. source/runtime/package equality, generated chunk merge, isolated package parity 또는 `four_surface_status=PASS`를 생성하지 않는다.
- child stdout/stderr/exit code, executable path/hash, validator path/hash, exact argv를 receipt에 기록한다.
- child exit code가 non-zero이거나 receipt schema/hash가 불일치하면 exporter는 source JSON `json.load()`와 bridge/chunk writer 진입 전에 같은 failure class로 종료한다.
- exporter test는 AST/import graph에서 forbidden analyzer direct import count `0`, exact child invocation count `1`, writer-before-guard count `0`, missing/stale bridge input manifest acceptance count `0`, preflight four-surface overclaim count `0`을 요구한다.
- bridge/chunk generation 전 rendered exact duplicate, unauthorized collision, invalid disposition, rendered binding drift를 차단한다.
- chunk generation 뒤 serialized Lua를 다시 읽어 assignment count, exact set, cross-chunk duplicate, comparison collision, payload hash를 검증한다.
- generated runtime과 isolated package가 준비된 뒤 post-generation standalone validator는 explicit `compatibility_surface_inputs.json`을 소비해 source/rendered/generated-runtime/package four-surface equality, alias-added new key, merge/overwrite/loss를 검증한다. preflight receipt는 이 report를 대신하지 않는다.
- static parser 검증과 actual Lua reconstruction 검증을 별도 evidence로 남긴다.
- protected live source/rendered/runtime payload는 수정하지 않고 fresh isolated output에서 검증한다.

Candidate/canonical-durable policy resolution and package state:

- Phase 2~4 package probe는 다음 explicit arguments를 사용한다.

```powershell
-RegistryCompatibilityContext candidate
-RegistryCompatibilityPolicy <attempt-root>\phase1\candidate\registry_runtime_compatibility_policy.json
-RegistryCompatibilityDisposition <attempt-root>\phase1\candidate\current_collision_disposition.json
-RegistryCompatibilityBindingManifest <attempt-root>\phase1\candidate\candidate_contract_binding_manifest.json
-RegistryCompatibilityRequiredGateState not_adopted
-RegistryCompatibilityProbe
```

- candidate context는 exact six-leaf set(policy, exclusion, disposition, three authority records)과 binding manifest가 같은 attempt candidate root 아래에 있고 manifest hashes, owner/reviewer schemas/decisions/eligibility와 일치할 때만 허용한다.
- candidate context output은 fresh attempt-local package root로 제한하며 live package root, publication, durable required-manifest adoption을 금지한다.
- canonical-durable context는 selected immutable `<durable-bundle-root>` 아래 exact six-leaf set과 binding manifest만 허용한다.
- candidate 또는 canonical-durable context에 다른 lifecycle path를 전달하면 `policy_context_substitution`으로 non-zero 종료한다.
- live gate adoption 전 context/path/binding/gate state를 생략한 package command는 `compatibility_policy_context_required`로 차단한다. adoption 뒤에는 complete omission만 live manifest의 selected immutable bundle과 `live_gate_adopted`로 결정론적으로 resolve하며 partial omission/override는 계속 차단한다.
- durable promotion 전에는 candidate probe만 허용하고 normal package finalization과 ZIP을 차단한다.
- durable bundle이 존재하지만 `required_gate_state=not_adopted`이면 canonical-durable probe만 허용한다. normal package finalization은 `package_guard_active_not_required_gate_adopted`로 차단한다.
- `required_gate_state=live_gate_adopted`이고 live manifest hash가 selected durable bundle을 결속할 때만 canonical-durable normal package finalization을 허용한다.
- Windows wrapper와 standalone validator는 context/path default를 허용하지 않고 항상 explicit inputs를 요구한다.

Existing invocation census and migration:

- `exporter_package_invocation_inventory.json`은 Python AST import/call, CLI/subprocess argv, PowerShell invocation, current test, command manifest, operator-facing current docs를 census한다. 단순 path/hash inspection과 historical/frozen evidence는 `static_reference` 또는 `historical_non_executable`로 분리한다.
- route class enum은 `executable_current`, `test_current`, `operator_current`, `diagnostic`, `historical_non_executable`, `static_reference`, `unknown`이다. `unknown`은 성공 경로가 아니다.
- 각 row는 `caller_path`, `caller_sha256`, `source_location`, `command_origin`, `invocation_kind`, `route_class`, `current_invocation`, `required_invocation`, `policy_resolution`, `migration_required`, `updated_status`, `regression_test_id`, `unresolved_status`를 가진다.
- 이 plan은 Option A를 고정한다. live adoption 뒤 exporter CLI/library와 package CLI의 compatibility arguments가 전부 생략되면 `current_route_required_validations.json`이 결속한 exact versioned bundle을 읽어 `canonical_durable + live_gate_adopted`로 resolve한다. non-versioned `current` directory, newest-directory scan, environment variable, caller working directory를 default authority로 사용하지 않는다.
- pre-adoption attempt/test는 explicit candidate arguments를 사용하고 isolated output에만 쓴다. canonical-durable pre-adoption probe도 exact bundle args를 명시한다.
- live adoption 전 legacy/default invocation은 fail-closed한다. live adoption 뒤 exact legacy package command `package_iris.ps1 -Clean -Zip`과 exporter omitted-compatibility route가 unconditional guard를 실제 실행해 PASS하는지를 regression으로 검증한다.
- partial explicit arguments, candidate context outside reviewed attempt, historical caller의 current-route 재분류, unbound direct `export_lua_bridge()` call은 실패한다.
- direct function callers는 explicit invocation contract object를 전달하도록 migration하거나 post-adoption canonical default wrapper를 통과시킨다. analyzer direct import를 caller에 분산하지 않는다.
- `invocation_migration_matrix.json`은 inventory 모든 row를 정확히 한 disposition에 연결한다. `unmigrated_invocation_count=0`, `unknown_invocation_count=0`, `inventory_orphan_count=0`이어야 implementation validation을 진행한다.
- `default_route_compatibility_report.json`은 pre-adoption omission rejection, post-adoption exporter/library/package default resolution, exact selected bundle hash, guard execution receipt, existing adjacent regressions를 결속한다.

Package logical binding:

```text
normalized_manifest_subset = {
  schema/version fields,
  normalized forward-slash relative manifest path,
  manifest-declared chunk order,
  each referenced relative chunk path,
  each referenced chunk sha256,
  each referenced chunk byte_count
}

chunk_bundle_binding_sha256
= sha256(sorted(relative_path NUL file_sha256 NUL byte_count))

package_binding_sha256
= sha256(canonical_json(normalized_manifest_subset)
          + LF
          + chunk_bundle_binding_sha256)
```

- absolute `source_root`, absolute `package_root`, build timestamp, ZIP timestamp/order/permission, output path는 logical identity에서 제외하고 transport observation report에 둔다.
- exclusion된 transport field가 logical equality를 대신하지 않는다.
- package guard는 copy 완료 후 ZIP finalization/성공 메시지 전에 unconditional로 실행한다.
- `package_iris.ps1`에는 guard skip switch를 추가하지 않는다.
- child validator non-zero면 package command도 같은 failure class를 non-zero로 propagate하고 ZIP/final success artifact를 만들지 않는다.
- C-5가 live manifest 미채택을 선택해도 package guard는 계속 mandatory다.
- Phase 2 producer는 candidate positive probe, child-failure/no-ZIP negative probe, context-substitution negative probe, pre-adoption omission rejection의 invocation receipts를 검증한 뒤 `<attempt-root>/phase2/package_guard_contract_report.json`을 생성한다.
- package guard contract schema는 `schema_version`, `producer_phase`, `package_script_path/hash`, `validator_path/hash`, `implementation_toolchain_manifest_path/hash`, `candidate_binding_manifest_path/hash`, `positive_receipt_path/hash`, `negative_receipt_paths/hashes`, `guard_before_zip`, `child_nonzero_propagated`, `zip_created_on_failure`, `pre_adoption_implicit_context_allowed=false`, `post_adoption_canonical_default_contract`, `status`를 포함한다.
- `package_guard_invocation_receipt.json`은 한 실행의 command evidence이고 `package_guard_contract_report.json`은 모든 required positive/negative receipts를 결속한 promotion-eligible contract다. 둘을 같은 artifact로 취급하지 않는다.
- promoted contract의 attempt-local source/receipt paths는 provenance-only이며 clean-checkout existence predicate가 아니다. authoritative relationship은 binding manifest hash와 receipt hashes이고 durable consumer는 `durable_bundle_manifest.json`의 role mapping으로 files를 resolve한다.

### Actual Lua Harness Contract

Tracked harness:

`Iris/build/description/v2/tests/fixtures/registry_runtime_compatibility/lua_merge_harness.lua`

Runner contract:

- `Get-Command lua`로 resolved executable path를 기록한다.
- `lua -v`의 actual stdout/stderr, exit code, parsed version을 기록한다.
- parsed major/minor가 `5.1` 또는 `5.4`인지 검사한다. planning-time `5.4.8` observation을 hard-code하지 않는다.
- executable path와 가능한 경우 executable file hash를 기록한다.
- harness path/hash와 isolated runtime root hash를 기록한다.
- working directory와 relevant environment allowlist를 기록하고 host `LUA_PATH`/`LUA_CPATH` 상속을 차단한다.
- harness는 다음 exact package path만 설정한다.

```lua
package.path = isolated_client_lua_root .. "/?.lua;"
            .. isolated_client_lua_root .. "/?/init.lua"
package.cpath = ""
```

- harness는 `require`를 instrument해 `Iris/Data/IrisLayer3DataChunks/ChunkNNN`별 table cardinality와 aggregate assignment count를 센다.
- chunk 간 duplicate exact key, manifest-loaded chunk count, final returned table count, `_G.IrisLayer3Data` identity를 검증한다.
- Python analyzer가 계산한 expected assignment/final count와 collision-member presence를 argument/fixture로 전달한다.
- stdout은 정확히 하나의 UTF-8 JSON object만 허용한다.
- stderr는 failure diagnostic 전용이다.

Exit contract:

| Exit | Meaning |
|---|---|
| 0 | actual Lua reconstruction PASS |
| 20 | Lua executable/version/harness unavailable |
| 21 | manifest/chunk require failure |
| 22 | duplicate assignment or overwrite |
| 23 | expected/final cardinality or required-key mismatch |
| 24 | terminal stdout schema/protocol failure |
| 25 | unsupported Lua major/minor version |

`lua` missing 또는 unsupported version을 static parser PASS로 대체하지 않는다. PUC Lua 5.1/5.4 harness PASS는 Kahlua/PZ runtime equivalence가 아니다.

`lua_merge_report.json`과 final machine report는 `lua_runtime_family=PUC_LUA`, `executed_lua_version`, `accepted_version_rule`, `validation_role=offline_table_reconstruction_only`, `project_zomboid_runtime_executed=false`, `cross_version_parity_executed`, `cross_version_parity_claimed=false`, `kahlua_equivalence_claimed=false`를 기록한다. 한 version만 실행했으면 `cross_version_parity_executed=false`여야 하며 실행하지 않은 다른 accepted version과의 parity를 주장하지 않는다.

### Change 4 — Phase 3 Windows Lossless Consumer Routes

Purpose:

PowerShell 5.1에서 case-variant key를 losslessly 검사하되 projection을 authority로 승격하지 않는다.

Common report fields:

- `canonical_route`
- `executed_command`
- `dependency_path`
- `dependency_version`
- `producer_path`
- `producer_sha256`
- `surface_input_manifest_path`
- `surface_input_manifest_sha256`
- `package_attempt_id`
- `package_binding_sha256`
- `input_path`
- `input_sha256`
- `output_path`
- `output_sha256`
- `fallback_used`
- `stdout_path`
- `stderr_path`
- `exit_code`
- `exact_record_count`
- `source_cardinality`
- `rendered_cardinality`
- `runtime_cardinality`
- `package_cardinality`
- `exact_distinct_count`
- `comparison_collision_group_count`
- `unauthorized_collision_group_count`
- `exception_backed_collision_group_count`
- `round_trip_restored_count`
- `merged_count`
- `lost_count`
- `overwritten_count`
- `terminal_status`
- `round_trip_record_count`
- `round_trip_exact_keyset_match`
- `round_trip_payload_binding_match`
- `non_authority_projection=true`
- `algorithm_proof_count=1`
- `transport_conformance_count=2`

Route enum:

| Route | Exact command template | Dependency | Producer | Fallback | Report | Authority |
|---|---|---|---|---|---|---|
| A `windows_uv_python` | `powershell -NoProfile -ExecutionPolicy Bypass -File .\Iris\tools\inspect_registry_runtime_compatibility.ps1 -Route windows_uv_python -AttemptRoot <attempt-root> -SurfaceInputManifest <attempt-root>\phase3\windows_surface_inputs.json -PolicyContext candidate -PolicyPath <candidate-policy> -DispositionPath <candidate-disposition> -BindingManifestPath <candidate-binding-manifest>` | PowerShell 5.1 + `uv` + Python | standalone `export_registry_runtime_records.py` child process | forbidden | `phase3/windows_route_conformance_report.json` | false |
| B `windows_jq_raw_object` | no accepted command in this scope | `jq` default object mode / separately assessed `--stream` mode | default object mode cannot prove identical duplicate preservation | forbidden and route ineligible | conformance rejection row | false |
| C `windows_record_sidecar` | `powershell -NoProfile -ExecutionPolicy Bypass -File .\Iris\tools\inspect_registry_runtime_compatibility.ps1 -Route windows_record_sidecar -AttemptRoot <attempt-root> -SurfaceInputManifest <attempt-root>\phase3\windows_surface_inputs.json -PolicyContext candidate -PolicyPath <candidate-policy> -DispositionPath <candidate-disposition> -BindingManifestPath <candidate-binding-manifest>` | PowerShell 5.1 + `uv` + Python | hash-bound JSONL record sidecar from standalone producer | forbidden | `phase3/windows_route_conformance_report.json` | false |

Route A internal producer invocation:

```powershell
uv run python -B Iris/build/description/v2/tools/build/export_registry_runtime_records.py --surface-input-manifest <attempt-root>/phase3/windows_surface_inputs.json --policy-context candidate --policy <attempt-root>/phase1/candidate/registry_runtime_compatibility_policy.json --disposition <attempt-root>/phase1/candidate/current_collision_disposition.json --binding-manifest <attempt-root>/phase1/candidate/candidate_contract_binding_manifest.json --out <attempt-root>/phase3/windows_projection.json
```

`windows_surface_inputs.json`은 source input manifest와 facts/decisions/overlay paths/hashes/roles, rendered path/hash, runtime manifest path/hash와 ordered chunk root/file hashes, isolated package root, package attempt id, package binding report path/hash, package binding SHA-256을 포함한다. 모든 path는 repository 또는 current attempt root 안에 resolve되어야 하고 Phase 0/2 bindings와 같아야 한다. `AttemptRoot`에서 입력을 암묵 탐색하지 않는다.

Route C uses the same producer to create one JSON object per exact record in JSONL, then PowerShell reads records line-by-line. It must not run `ConvertFrom-Json` against the main rendered object.

C-4는 Route A를 canonical Windows inspection route로, Route C를 required transport regression으로 고정한다. 두 route 모두 PASS해야 하며 owner가 둘 중 하나를 선택하지 않는다. A/C는 같은 canonical Python producer를 사용하므로 두 독립 algorithm proof가 아니라 transport conformance variants다. combined report는 `algorithm_proof_count=1`, `transport_conformance_count=2`, `route_a_transport_status=PASS`, `route_c_transport_status=PASS`를 요구한다.

Route B rejection은 case-variant key collapse를 주장하지 않는다. `Base.LemonGrass`와 `Base.Lemongrass`는 jq object에서도 distinct하다. 문제는 default object mode가 identical duplicate key를 last-wins materialize해 pre-materialization duplicate proof를 제공하지 못한다는 점이다. `jq --stream`은 별도 duplicate-aware route가 될 가능성이 있지만 이 plan의 reviewed producer/schema/fixture에 포함되지 않으므로 미채택한다. Any fallback or producer substitution produces non-zero exit.

두 clean Windows rerun은 timestamp, duration, absolute output root, stdout/stderr path를 제외한 normalized report hash, decoded ordered record sequence hash, round-trip exact key-set hash, payload-binding hash가 모두 같아야 한다. 하나라도 다르면 determinism FAIL이다.

### Change 5 — Phase 4 Fixtures, Current Regression, Determinism, and Lua Validation

Purpose:

positive/negative fixtures와 actual current data에서 failure code/stage, determinism, protected no-mutation을 검증한다.

Fixture row fields:

- fixture id/path/hash
- expected status
- expected failure code
- expected failure stage
- actual status/code/stage
- first failing predicate
- stdout/stderr receipt

Roadmap fixture 1~10 exact traceability:

| Roadmap fixture | Plan fixture ID | Expected | Expected failure code | Expected failure stage | Expected first failing predicate |
|---|---|---|---|---|---|
| 1 일반 key 집합 positive | `RTC-RM-01-ordinary-exact-key-set-positive` | PASS; collision 0, exact count/round trip preserved | `none` | `none` | `none` |
| 2 Unauthorized collision negative | `RTC-RM-02-unauthorized-collision` | FAIL | `unauthorized_collision` | `disposition_validation` | `unauthorized_collision_count == 0` |
| 3 Owner record missing negative | `RTC-RM-03-owner-record-missing` | FAIL | `blocked_owner_disposition_missing` | `owner_binding_validation` | `owner_record_present_and_hash_bound == true` |
| 4 Payload-divergent exception negative | `RTC-RM-04-payload-divergent-exception` | FAIL | `collision_payload_divergence` | `payload_equivalence_validation` | `payload_equivalence == true` |
| 5 Third variant negative | `RTC-RM-05-third-variant` | FAIL | `invalid_collision_member_count` | `disposition_validation` | `collision_member_count == 2` |
| 6 Windows cardinality-loss negative | `RTC-RM-06-windows-projection-cardinality-loss` | FAIL | `windows_projection_cardinality_loss` | `windows_round_trip_validation` | `source_count == projection_count` |
| 7 Exact overwrite/merge negative | `RTC-RM-07-exact-overwrite-merge` | FAIL | `exact_key_overwrite` | `lua_merge_or_runtime_reconstruction` | `overwritten_key_count == 0` |
| 8 Current collision positive regression | `RTC-RM-08-current-collision-positive` | PASS; valid exception-backed group and payload parity | `none` | `none` | `none` |
| 9 Current full payload regression | `RTC-RM-09-current-full-payload` | PASS; source/rendered/runtime exact parity and loss 0 | `none` | `none` | `none` |
| 10 Package projection regression | `RTC-RM-10-package-projection` | PASS; package exact/payload parity and forbidden hit 0 | `none` | `none` | `none` |

`RTC-RM-06`은 parser rejection이 아니라 projection defect를 직접 주입한다. required observed fields는 `source_count > projection_count`, `lost_count > 0`, `round_trip_restored_count < source_count`, `round_trip_exact_keyset_match=false`다. `Windows main-object ConvertFrom-Json rejection`은 별도 supplemental fixture이며 RM-06을 대신하지 않는다. roadmap traceability producer는 1~10 각각 mapping count `1`, duplicate/unmapped/unresolved count `0`을 요구한다.

Required fixture classes:

- ordinary exact-key positive with no collision/exception/role disposition (`RTC-RM-01`)
- preserved case-variant pair
- exact duplicate before materialization
- JSON escaped/literal token pair decoding to one exact key
- Lua escaped/literal token pair decoding to one exact key
- payload divergence outside exclusions
- over-broad exclusion
- third comparison-collision member
- two-member comparison collision with missing disposition → `unauthorized_collision` at disposition-validation stage
- C-6 duplicate role, overlap, and unassigned-member rejection
- non-ASCII comparator-domain rejection
- alias-added new key and undeclared emission rejection
- cross-chunk exact duplicate/overwrite
- Windows projection cardinality-loss injection with lost/restored counts (`RTC-RM-06`)
- Windows main-object `ConvertFrom-Json` rejection with lossless route success
- package child guard failure propagation/no ZIP finalization
- candidate policy outside attempt root, canonical-durable bundle substitution, and context downgrade rejection
- concurrent attempt reservation, open attempt blocks second reservation, terminal completion permits next reservation, clean worktree with open attempt still blocks, multiple nonterminal attempts hard-block, existing-root reuse, pre-Phase 0 failure ID consumption, failed-attempt deletion detection
- bootstrap executor missing/hash drift/scope escape, test failure, alternate executor, manual Git/PowerShell reservation rejection
- exporter forbidden direct import, missing child invocation, writer-before-guard, child non-zero propagation
- reciprocal leaf hash, leaf self-hash, downstream bundle-hash cycle edge, candidate binding manifest mismatch
- missing/untracked/ignored/schema-invalid versioned plan approval, collision owner disposition, Review 2 record; filename/record-id mismatch; `current_*` pointer rejection; selector missing/multiple; stale selected head; successor chain break/fork/cycle; owner decision/disposition mismatch; reviewer ineligibility; valid second-generation successor positive path
- prior attempt event mutation/deletion/reordering and event hash-chain break
- record-without-event recovery, event-without-record block, shared/durable divergence, orphan local root, cross-worktree/branch prefix mismatch
- ignored/untracked bootstrap path, mixed governance/production bootstrap commit, retroactive attempt materialization rejection
- incomplete durable promotion, disposition parity mismatch, missing package guard contract source, partial bundle publish rejection
- bundle lifecycle event mutation/chain break/invalid transition, invalidated-or-superseded content reuse rejection
- Windows missing/stale four-surface input, package attempt mismatch, package binding mismatch
- durable bundle present with `not_adopted` normal package finalization rejection
- existing exporter/package invocation inventory orphan, unknown caller, unmigrated direct function call, pre-adoption omitted context, partial override, post-adoption wrong-bundle default
- implementation toolchain changed/missing/untracked/ignored/unclassified dependency at every required freshness checkpoint
- bridge preflight missing/stale explicit input manifest and preflight four-surface overclaim rejection
- terminal event before durable closeout commit, missing closeout original bytes, closeout hash mismatch, partial closeout publish, independent review/owner seal/terminal seal content absence
- Lua require failure/cardinality mismatch/protocol failure
- unsupported Lua major/minor rejection

Current-data regression:

- fresh source/rendered/runtime/package counts and exact key-set equality
- current collision inventory/disposition validity
- alias declaration regression with applied new key/unexpected emission/collision increase all 0
- bridge/chunk/post-serialization parity
- actual Lua reconstruction
- logical package binding parity
- transport metadata observation separation
- Windows round-trip exact key/payload binding
- existing exact duplicate/stale bridge/monolith/predecessor guard
- two clean reruns with normalized deterministic outputs
- Windows normalized report/decoded record/restored key-set/payload-binding hash parity
- protected surface hash unchanged
- `round3_active_core_closure.json` hash unchanged
- exporter import graph contains no compatibility analyzer direct dependency
- candidate contract binding graph is acyclic
- actual durable owner/review authority bytes and decisions match candidate/durable policy/disposition
- append-only attempt event prefix/hash chain unchanged
- append-only bundle lifecycle event/record chain and selected bundle lifecycle match
- single integration branch three-prefix equality
- invocation inventory/migration/default-route compatibility status
- implementation toolchain manifest and every checkpoint freshness status
- durable promotion required source/destination role set is exactly equal
- durable closeout packet required role set, commit-before-terminal ordering, clean-checkout content availability
- roadmap fixture 1~10 exact one-to-one mapping and unresolved count 0

### Change 6 — Phase 5 Pre-Adoption Report and Additive Required Gate

Purpose:

Phase 0~4의 immutable evidence에서 pre-adoption machine result를 만들고, 자기참조 없이 live current route에 additive gate를 채택한다.

Required DAG:

```text
Phase 0..4 immutable evidence
-> pre-adoption implementation-toolchain freshness check
-> pre_adoption_compatibility_machine_report
-> pre-promotion implementation-toolchain freshness check
-> complete versioned durable bundle promotion
-> durable bundle lifecycle eligibility checkpoint
-> canonical-durable context package probe
-> durable package_guard_active_not_required_gate_adopted lifecycle event commit
-> required-validation candidate manifest
-> pre-candidate-probe implementation-toolchain freshness check
-> candidate_manifest_route_probe
-> pre-live-adoption implementation-toolchain freshness check
-> live additive manifest adoption
-> durable live_required_gate_adopted lifecycle event commit
-> pre-official-route implementation-toolchain freshness check
-> post-adoption current-route result
-> live-gate-adopted normal package finalization
-> pre-final-report implementation-toolchain freshness check
-> final_machine_report
-> independent_review_gate_report
-> owner_canonical_seal_gate_report
-> final_registry_runtime_compatibility_report
-> final_claim_scan_report
-> closeout_content_manifest
-> terminal_hash_seal
-> durable_closeout_packet_manifest
-> durable closeout packet commit
-> terminal record/event transaction
-> terminal commit/shared-prefix update
```

Live manifest가 요구할 수 있는 것은 다음 pre-adoption durable surfaces뿐이다.

- durable compatibility policy
- durable identity-field exclusion contract
- durable current collision disposition
- durable selected versioned plan contract approval record
- durable selected versioned collision owner disposition record
- durable selected versioned Phase 0/Review 2 contract review record
- durable candidate contract binding manifest
- durable pre-adoption compatibility machine report
- durable package guard contract report
- durable implementation toolchain manifest
- durable pre-promotion implementation toolchain freshness report
- durable bundle manifest
- tracked required unittest `test_dvf_3_3_registry_runtime_compatibility_current.RegistryRuntimeCompatibilityCurrentRouteTest.test_required_gate_runs_standalone_subprocess`

Live manifest는 다음 post-adoption/governance artifacts를 요구하지 않는다.

- `post_adoption_current_route_result.json`
- `live_gate_package_finalization_result.json`
- `final_machine_report.json`
- `independent_review_gate_report.json`
- `owner_canonical_seal_gate_report.json`
- `final_registry_runtime_compatibility_report.json`
- `final_claim_scan_report.json`
- `closeout_content_manifest.json`
- `terminal_hash_seal.json`
- `durable_closeout_packet_manifest.json`

Implementation Notes:

- pre-adoption report는 candidate contract binding manifest hash와 six leaf hashes, owner/reviewer identity/eligibility/decision validation, Phase 0~4 artifact hash manifest, implementation toolchain manifest/freshness hashes, machine predicates, package guard proof, protected no-mutation, claim ceiling을 결속한다. leaf reciprocal hash를 새로 만들지 않는다.
- promotion source set은 정확히 다음 열한 artifact다.

| Role | Attempt-local source | Durable destination under `<durable-bundle-root>` |
|---|---|---|
| policy | `phase1/candidate/registry_runtime_compatibility_policy.json` | `registry_runtime_compatibility_policy.json` |
| exclusion | `phase1/candidate/registry_runtime_compatibility_identity_field_exclusions.json` | `registry_runtime_compatibility_identity_field_exclusions.json` |
| disposition | `phase1/candidate/current_collision_disposition.json` | `current_collision_disposition.json` |
| plan contract approval | `phase1/candidate/authority/plan_approvals/approval-<approval-id>.json` | `authority/plan_approvals/approval-<approval-id>.json` |
| collision owner disposition | `phase1/candidate/authority/collision_dispositions/disposition-<disposition-id>.json` | `authority/collision_dispositions/disposition-<disposition-id>.json` |
| Phase 0/Review 2 contract review | `phase1/candidate/authority/reviews/phase0-contract-review-<review-id>.json` | `authority/reviews/phase0-contract-review-<review-id>.json` |
| candidate binding | `phase1/candidate/candidate_contract_binding_manifest.json` | `candidate_contract_binding_manifest.json` |
| package guard contract | `phase2/package_guard_contract_report.json` | `package_guard_contract_report.json` |
| implementation toolchain | `phase1/implementation_toolchain_manifest.json` | `implementation_toolchain_manifest.json` |
| pre-promotion toolchain freshness | `phase5/implementation_toolchain_freshness_before_durable_promotion.json` | `implementation_toolchain_freshness_report.json` |
| pre-adoption machine result | `phase5/pre_adoption_compatibility_machine_report.json` | `pre_adoption_compatibility_machine_report.json` |

- `bundle_id`는 위 rows의 normalized `role`, canonical durable destination relative path, role-specific authority `record_id` 또는 `not_applicable`, schema/version, byte count, SHA-256 canonical JSON hash다. attempt-local source root, attempt id, absolute path, timestamp는 ID input에서 제외하고 provenance rows에만 기록한다. 따라서 같은 selected authority ids와 byte-identical approved content는 attempt가 달라도 같은 content-addressed ID를 갖는다.
- `<durable-bundle-root>`는 `Iris/_docs/round3/registry_runtime_compatibility/bundles/<bundle-id>/`다.
- promotion은 same-volume attempt-local staging directory에 열한 files와 generated `durable_bundle_manifest.json`을 먼저 쓰고 전부 검증한다. destination이 없으면 single directory rename으로 publish한다. 같은 content-addressed destination이 이미 있으면 그 directory의 role set/manifest/file bytes가 staged bundle과 exact-equal하고 current durable lifecycle이 `canonical_durable`, `package_guard_active_not_required_gate_adopted`, 또는 같은 live row의 `live_required_gate_adopted`일 때만 `content_reuse=true`로 재사용하고 rename/write를 하지 않는다. 같은 ID 아래 한 byte라도 다르면 hash collision/corruption으로 block한다.
- existing bundle의 latest durable lifecycle이 `invalidated` 또는 `superseded`이면 byte-exact라도 automatic reuse와 `canonical_durable` 복귀를 금지하고 `content_reuse_forbidden_terminal_lifecycle`로 block한다. 재정당화는 이 plan 밖의 별도 owner-reviewed lifecycle scope다.
- `durable_bundle_manifest.json`은 bundle id, source/destination rows, roles, schemas, byte counts, source/destination hashes, parity를 기록하고 자기 final hash를 포함하지 않는다.
- `durable_promotion_report.json`은 required live durable roles와 promoted/reused roles의 exact equality, partial-promotion count, mismatched destination collision count, `content_reuse`, directory rename receipt 또는 verified-existing receipt를 기록한다.
- rename 전 실패는 durable bundle을 만들지 않고 attempt failure로 보존한다. rename 후 probe/candidate/adoption 실패는 bundle을 삭제·rewrite하지 않고 lifecycle state를 `invalidated` 또는 `package_guard_active_not_required_gate_adopted`로 기록한다.
- newly published bundle은 `canonical_durable` lifecycle event/record를 append/commit한다. byte-exact existing bundle reuse는 latest eligible lifecycle event/record를 검증하고 prior state로 되돌리는 duplicate/backward event를 만들지 않는다.
- bundle lifecycle authority는 `bundle_lifecycle_events.jsonl`과 `bundle_lifecycle/event-NNNN-<bundle-id>-<state>.json`의 append-only pair다. event/record는 sequence, bundle id/manifest hash, prior/current state, reason code, triggering attempt/artifact path/hash, selected/superseding bundle when applicable, previous event hash를 포함하고 attempt event와 같은 record-first/exact-one-append/commit discipline을 사용한다.
- 허용 transition은 `absent → canonical_durable → package_guard_active_not_required_gate_adopted → live_required_gate_adopted`, active state→`invalidated`, `live_required_gate_adopted → superseded`뿐이다. invalidated/superseded는 terminal lifecycle이며 bundle files나 prior event를 수정하지 않는다. local `durable_bundle_lifecycle_report.json`은 이 ledger의 diagnostic projection일 뿐 authority가 아니다.
- promotion 직후 package command를 `canonical_durable` context, `not_adopted` gate state, `RegistryCompatibilityProbe` mode로 실행하고 candidate path/context와 다른 bundle substitution이 거부되는지 확인한다.
- canonical-durable package probe가 PASS하고 latest state가 `canonical_durable`이면 `package_guard_active_not_required_gate_adopted` lifecycle event를 durable commit한다. already-active eligible reuse는 same-state hash parity를 검증하고 backward transition을 만들지 않는다. probe가 실패하면 `invalidated` event를 commit하고 candidate manifest를 만들지 않는다.
- required unittest는 analyzer를 direct import하지 않고 `sys.executable -B <validator-path> --required-gate ...` standalone child process로 fresh current surfaces를 검증한다.
- required unittest는 selected durable `implementation_toolchain_manifest.json`과 current checkout을 비교해 drift/missing/untracked/ignored/unclassified count가 모두 0인지 먼저 검사한다.
- required unittest는 durable plan approval/owner disposition/Review 2 records의 actual bytes, tracked/not-ignored state, schemas, record-id/path parity, unique successor-chain head, identities/eligibility, selected decisions/verdict, policy/disposition hashes를 직접 검증한다. record absence를 disposition 안의 hash string으로 대체하지 않으며 `RTC-RM-03`과 production route가 같은 missing-owner predicate를 사용한다.
- candidate manifest probe는 repository에서 확인된 `--required-validations <candidate-manifest>` option을 사용한다. Change 0 exact CLI preflight가 실패하면 runner를 암묵 수정하지 않고 dependency blocker로 종료한다.
- candidate manifest probe는 live manifest를 바꾸기 전에 candidate override로 수행하며 output field는 `candidate_manifest_route_status`다. 이 probe를 `current-route PASS` 또는 official current route result로 부르지 않는다.
- candidate/live required manifest rows는 non-versioned `current` pointer가 아니라 selected `<durable-bundle-root>`의 exact versioned paths와 durable bundle manifest hash를 사용한다.
- adoption 직전 current live manifest bytes/hash를 `pre_adoption_live_manifest_sha256`로, additive commit 뒤 bytes/hash를 `post_adoption_live_manifest_sha256`로 기록하고 selected bundle id/manifest hash와 exact adopted row key/path/predicate identity를 `adopted_row_identity`에 결속한다.
- live diff는 additive row만 허용하고 existing entry removal/reclassification/duplicate를 금지한다.
- `round3_active_core_closure.json`과 tooling allowlist는 before/after byte hash가 같아야 한다.
- `allowlist_contract_scope`는 `import_closure_only`여야 하며 executed-tooling closure로 바뀌면 subprocess route와 adoption을 차단한다.
- required artifacts/tests는 tracked/not-ignored이고 clean checkout에서 resolve 가능해야 한다.
- candidate probe, live adoption, official current route, final machine report 직전에는 각각 새 toolchain freshness receipt를 생성하고 selected durable baseline manifest hash와 current checkout hash parity를 요구한다. earlier PASS receipt 재사용은 금지한다.
- C-5 `live_additive_required_gate`가 승인되고 post-promotion package probe와 candidate manifest route probe가 PASS일 때만 adoption한다.
- live additive manifest commit/hash 검증 뒤 `live_required_gate_adopted` lifecycle event를 commit해야 official current route와 normal package finalization을 실행할 수 있다. 같은 adopted row/hash의 already-live reuse는 existing live event를 검증하고 duplicate transition을 만들지 않는다. live adoption commit 뒤 lifecycle event commit이 실패하면 default route와 final claim을 block한다.
- C-5 `blocked_no_live_adoption`은 safe blocked state이며 canonical compatibility closeout을 허용하지 않는다.
- C-5 owner ratification은 roadmap의 prior `current required-validation 또는 package-required guard` 선택지를 강화해 package guard를 unconditional로 만들고 live additive gate도 canonical closeout에 필수화했다는 사실을 `roadmap_or_condition_superseded_by_plan_and_condition=true`, `package_guard_and_live_required_gate_both_mandatory_for_closeout=true`, `owner_explicitly_approved=true`로 명시한다.

Policy lifecycle:

| `policy_lifecycle_state` | Durable bundle | Required gate | Normal package finalization |
|---|---|---|---|
| `candidate` | absent | not adopted | blocked; attempt-local probe only |
| `canonical_durable` | promoted/immutable | not adopted, probes pending | blocked; canonical-durable probe only |
| `package_guard_active_not_required_gate_adopted` | promoted/immutable | not adopted or owner blocked | blocked |
| `live_required_gate_adopted` | promoted/immutable and manifest-bound | adopted | allowed with unconditional guard |
| `invalidated` | retained/immutable | forbidden | blocked |
| `superseded` | retained/immutable historical | newer bundle governs | blocked for superseded bundle |

`live_required_gate_adopted`에서만 complete argument omission을 canonical default로 허용한다. 이때 exporter/package wrapper는 live required manifest가 직접 결속한 exact versioned bundle과 durable toolchain manifest를 사용하고 receipt에 `resolution_mode=post_adoption_live_manifest_default`를 기록한다.

### Change 7 — Post-Adoption Machine Result, Independent Review, Owner Seal, and Closeout

Purpose:

post-adoption machine validation, independent review, owner seal을 비대체 축으로 결속한다.

Independent reviewer eligibility:

- roadmap author가 아니다.
- current plan 초안/개정의 author 또는 coauthor가 아니다.
- implementation/tool/test/package integration author 또는 coauthor가 아니다.
- collision disposition signer, roadmap/plan approval owner, final owner seal signer가 아니다.
- roadmap/plan/implementation을 생성한 동일 agent/session identity가 아니다.
- review scope, reviewer identity/provenance, artifacts reviewed, hashes, rerun commands/receipts, findings, verdict를 machine-readable record에 남긴다.
- supplied combined review는 revision input이며 final implementation independent review를 대신하지 않는다.
- owner는 eligible reviewer를 지정할 수 있지만 위 조건을 waive하거나 자기 review를 independent로 선언할 수 없다.

Closeout ordering:

1. post-adoption current-route result
2. live-gate-adopted normal package finalization result
3. final machine report
4. eligible independent review
5. owner canonical seal record
6. final compatibility report
7. final claim scan report
8. closeout content manifest
9. terminal hash seal
10. durable closeout packet manifest
11. atomic durable closeout directory publish
12. durable closeout packet/evidence manifest VCS commit
13. terminal record/event transaction
14. terminal VCS commit and shared committed-prefix update
15. optional additive top-doc draft/application

local phase5 copies는 closeout packet의 provenance source일 뿐 canonical authority가 아니다. 위 1~7의 exact bytes를 `closeout_content_manifest.json`이 normalized relative path/role/schema/byte count/SHA-256으로 결속한다. `terminal_hash_seal.json`은 content manifest hash, selected durable bundle/lifecycle event, pre/post live manifest hashes, adopted row identity, attempt reservation/event prefix를 결속하고 자기 hash나 downstream packet manifest hash를 포함하지 않는다.

`durable_closeout_packet_manifest.json`은 위 1~7, content manifest, terminal seal의 정확히 아홉 roles를 결속하고 자기 hash를 포함하지 않는다. same-volume staging `closeout-staging/`에서 모두 검증한 뒤 non-existing durable `attempts/attempt-NNNN/closeout/`으로 single directory rename하고 exact closeout directory와 immutable `evidence_manifest.json`만 별도 closeout commit으로 commit한다. partial directory, existing destination, source/destination role/hash mismatch는 block한다.

terminal record/event는 closeout commit이 branch tip에서 확인된 뒤에만 생성한다. terminal record는 `durable_closeout_packet_commit`, packet manifest path/hash, terminal seal path/hash, evidence manifest path/hash, selected bundle/lifecycle event를 직접 포함하고 terminal event는 이 terminal record path/hash와 closeout commit을 결속한다. terminal event 전 closeout commit이 없거나 closeout commit 뒤 bytes가 달라지면 terminal transaction을 실행하지 않는다.

final machine report는 disposition, actual owner/review authority bytes, policy/artifact binding, four-surface exact-key equality, alias no-new-key regression, exact duplicate/collision/payload/merge/loss/overwrite counts, roadmap fixture mapping, invocation migration/default-route status, implementation toolchain manifest/current freshness, event/lifecycle transaction/prefix status, Windows/Lua/package/official current-route status, allowlist no-mutation, protected no-mutation, evidence freshness, claim scope와 다음 exact fields를 포함한다.

```text
pre_adoption_live_manifest_sha256
post_adoption_live_manifest_sha256
selected_durable_bundle_id
selected_bundle_manifest_sha256
adopted_row_identity
```

independent review, owner seal, final compatibility report, terminal hash seal도 위 five fields를 동일하게 결속한다. owner seal은 final machine report와 independent review actual bytes/hash를 직접 bind하며 failed machine result나 ineligible review를 override할 수 없다.

claim-bearing report와 terminal seal은 write-once다. 실패 evidence를 같은 attempt의 PASS로 덮어쓰지 않는다.

formal claim scanner는 current claim field에서 exact `Registry Runtime Compatibility PASS`만 허용한다. bare `Runtime Compatibility PASS` 또는 축이 없는 `PASS`를 current claim으로 생성하면 실패한다. prohibition, negation, quoted review text는 claim-bearing field가 아님을 parser가 구분한다.

clean-checkout validator는 `durable_closeout_artifact_missing_count=0`, `durable_closeout_hash_mismatch_count=0`, `independent_review_content_available=true`, `owner_seal_content_available=true`, `terminal_seal_content_available=true`, `terminal_event_before_closeout_commit_count=0`을 요구한다. hash만 있고 referenced content bytes가 없는 상태는 PASS가 아니다.

---

## 7. Validation Plan

### Automated Validation

아래 command는 구현 시 실제 `attempt-XXXX` root를 대입하고 exact command/start/end/exit/stdout/stderr/first-failure receipt를 보존한다.

0. Committed Gate A bootstrap executor contract:

```powershell
<bootstrap-python> -I -B Iris/_docs/round3/registry_runtime_compatibility/bootstrap/test_reserve_registry_runtime_compatibility_attempt.py
```

이 command와 Gate B exact invocation은 committed bootstrap manifest/contract hashes와 같은 executable/test bytes만 사용한다. missing executor, hash drift, alternate/manual reservation은 `implementation_entry_allowed=false`다.

1. Static implementation/contract validation:

```powershell
uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_runtime_compatibility.py --require-implementation --attempt-root <attempt-root>
```

2. Focused compatibility tests:

```powershell
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_registry_runtime_compatibility_*.py"
```

3. Existing adjacent bridge/package regressions:

```powershell
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_lua_bridge_export_contract_realign.py"
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_layer3_data_chunking_contract.py"
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_interaction_cluster_phase_d_runtime.py"
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_package_layer3_chunks_only_contract.py"
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_vcs_tracking_policy.py"
```

4. Fresh isolated package probe with unconditional guard:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -OutputRoot <fresh-attempt-package-root> -RegistryCompatibilityContext candidate -RegistryCompatibilityPolicy <attempt-root>\phase1\candidate\registry_runtime_compatibility_policy.json -RegistryCompatibilityDisposition <attempt-root>\phase1\candidate\current_collision_disposition.json -RegistryCompatibilityBindingManifest <attempt-root>\phase1\candidate\candidate_contract_binding_manifest.json -RegistryCompatibilityRequiredGateState not_adopted -RegistryCompatibilityProbe -RegistryCompatibilityReceipt <attempt-root>\phase2\package_guard_invocation_receipt.json
```

5. Canonical Windows route and required transport regression:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Iris\tools\inspect_registry_runtime_compatibility.ps1 -Route windows_uv_python -AttemptRoot <attempt-root> -SurfaceInputManifest <attempt-root>\phase3\windows_surface_inputs.json -PolicyContext candidate -PolicyPath <attempt-root>\phase1\candidate\registry_runtime_compatibility_policy.json -DispositionPath <attempt-root>\phase1\candidate\current_collision_disposition.json -BindingManifestPath <attempt-root>\phase1\candidate\candidate_contract_binding_manifest.json
powershell -NoProfile -ExecutionPolicy Bypass -File .\Iris\tools\inspect_registry_runtime_compatibility.ps1 -Route windows_record_sidecar -AttemptRoot <attempt-root> -SurfaceInputManifest <attempt-root>\phase3\windows_surface_inputs.json -PolicyContext candidate -PolicyPath <attempt-root>\phase1\candidate\registry_runtime_compatibility_policy.json -DispositionPath <attempt-root>\phase1\candidate\current_collision_disposition.json -BindingManifestPath <attempt-root>\phase1\candidate\candidate_contract_binding_manifest.json
```

6. Post-promotion canonical-durable package probe:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -OutputRoot <fresh-post-promotion-package-root> -RegistryCompatibilityContext canonical_durable -RegistryCompatibilityPolicy <durable-bundle-root>\registry_runtime_compatibility_policy.json -RegistryCompatibilityDisposition <durable-bundle-root>\current_collision_disposition.json -RegistryCompatibilityBindingManifest <durable-bundle-root>\candidate_contract_binding_manifest.json -RegistryCompatibilityRequiredGateState not_adopted -RegistryCompatibilityProbe -RegistryCompatibilityReceipt <attempt-root>\phase5\post_promotion_package_probe.json
```

7. Candidate manifest route probe before live adoption:

```powershell
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --required-validations <candidate-manifest> --out <attempt-root>/phase5/candidate_manifest_route_probe.json
```

이 command의 성공 field는 `candidate_manifest_route_status=PASS`이며 official `current-route PASS`가 아니다.

8. Official live current-route validation after adoption:

```powershell
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --out <attempt-root>/phase5/post_adoption_current_route_result.json
```

9. Live-gate-adopted normal package finalization:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -OutputRoot <fresh-live-gate-package-root> -Zip -RegistryCompatibilityContext canonical_durable -RegistryCompatibilityPolicy <durable-bundle-root>\registry_runtime_compatibility_policy.json -RegistryCompatibilityDisposition <durable-bundle-root>\current_collision_disposition.json -RegistryCompatibilityBindingManifest <durable-bundle-root>\candidate_contract_binding_manifest.json -RegistryCompatibilityRequiredGateState live_gate_adopted -RegistryCompatibilityRequiredManifest .\Iris\_docs\round3\current_route_required_validations.json -RegistryCompatibilityReceipt <attempt-root>\phase5\live_gate_package_finalization_result.json
```

10. Post-adoption existing default package command regression:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean -Zip
```

이 exact legacy command는 live manifest-selected bundle로만 resolve되어야 하며 outer command receipt와 package-generated compatibility receipt를 `default_route_compatibility_report.json`에 결속한다. live adoption 전 같은 command의 non-zero `compatibility_policy_context_required` fixture도 실행한다. exporter/library omitted-compatibility default는 focused tests가 isolated output에서 같은 pre/post-adoption transition을 검증한다.

11. Lua syntax:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

12. VCS and diff checks:

```powershell
git diff --check
git diff --stat
git status --short
```

Additional machine checks:

- repo-local input canonical text parity
- current plan fingerprint parity
- preimplementation blocker count 0
- committed bootstrap executor/test/contract/report presence/hash/scope/test PASS, ad hoc/manual reservation count 0, reservation preflight nonterminal count 0/open ids empty
- governance bootstrap commit/path visibility와 selected/approved/shared prefix parity
- event record/append/VCS/shared-ledger transaction 및 partial-state reconciliation
- required-validation override flag and allowlist scope verification
- named-mutex reservation, append-only event chain, immutable terminal records, open-attempt-before-new-reservation rejection, terminal-then-next-reservation positive path, reuse/prior-event-mutation count 0
- exporter/package repository-wide invocation inventory, migration matrix, default-route compatibility; unknown/unmigrated count 0
- invocation authority baseline equals owner-approved clean baseline; dirty original docs authority consumption count 0
- Phase 0 fresh census twice
- identity/policy hash determinism twice
- roadmap fixture 1~10 exact mapping, ordinary positive, Windows cardinality-loss injection, unresolved count 0
- candidate leaf/binding-manifest acyclic graph validation and attempt-root containment
- six-leaf candidate authority contract, selected versioned authority path/id/hash, valid successor positive path, no-current-pointer, unique-head/no-fork/no-cycle, three durable owner/review record presence/hash/schema/decision/eligibility/supersession validation
- canonical-durable selected-bundle containment and policy lifecycle transition validation
- cross-phase freshness before every phase
- implementation toolchain baseline plus all seven checkpoint freshness receipts; drift/missing/untracked/ignored/unclassified count 0
- JSON/Lua raw-token vs decoded-key escaped fixtures
- actual Lua harness for repo and isolated package
- accepted Lua version and unsupported-version fixture
- Windows route/projection/round-trip twice with normalized report/record/key/payload parity
- Windows four-surface input manifest completeness/freshness/package binding
- bridge preflight explicit input manifest completeness, rendered/policy-only responsibility, post-generation four-surface report separation
- exporter forbidden-import scan, exact subprocess receipt, writer-before-guard and preflight-overclaim count 0
- package logical binding and transport separation
- package negative guard propagation/no ZIP
- complete eleven-role durable promotion source/destination parity, content-addressed bundle-id reproducibility, lifecycle-eligible content reuse, and partial-publish count 0
- append-only bundle lifecycle record/event chain, allowed transition, selected/superseded bundle binding
- four-surface exact key-set equality and alias-added key count 0
- candidate manifest probe/live manifest additive diff/official post-adoption result separation
- pre/post live manifest hashes, selected bundle id/manifest hash, adopted row identity parity across final artifacts
- atomic durable closeout nine-role packet publish/commit before terminal record/event
- clean-checkout durable final machine/review/owner seal/final claim/terminal seal content and hash validation
- required artifact/test tracked/not-ignored
- `round3_active_core_closure.json` before/after exact hash equality
- protected source/rendered/runtime/package before/after hash equality
- final claim/terminal-token scan including bare current `Runtime Compatibility PASS` count 0

각 required command는 exit code `0`일 때만 PASS로 기록한다. missing tool은 `blocked`, not passed다.

### Manual Review Gates

- Final plan review: recorded `WARN`, Critical 0, implementation blocker 0, `governance_bootstrap_allowed=true`다. 이 reviewer는 final closeout independent review에 부적격이며 책임 경계/DAG/claim ceiling이 바뀌지 않는 한 plan-level re-review를 반복하지 않는다.
- Gate A review: approved plan review provenance 뒤 round-local executor/test/manifest/contract/report exact bytes, versioned plan approval path/id, nonterminal-attempt fixtures와 금지 책임을 검토해 `bootstrap_executor_contract_reviewed`를 판정한다.
- Entry review: owner가 plan/roadmap fingerprints, committed bootstrap executor hash, execution baseline, integration branch, eligible future reviewer assignment을 승인한다.
- Review 1: Phase 0A raw census, unfiltered delta, format decoding, machine eligibility token을 검토한다.
- Review 2: proposed C-6 multiplicity/roles, exclusions, candidate policy/invalidation을 selected tracked `reviews/phase0-contract-review-<review-id>.json`으로 ratify한다. actual selected versioned plan approval/owner disposition/review bytes가 durable candidate contract에 준비되기 전에는 final Phase 0 Branch A를 기록하지 않는다.
- Phase 0B: Review 2 결과와 owner records를 소비해 final Branch A/B/C를 기록한다.
- Review 3: owner-approved C-4 transition, fixed Route A canonical + Route C required regression, exporter subprocess/preflight responsibility boundary, bridge/chunk/package integration과 no-fallback을 검토한다.
- Review 4: actual diff, roadmap fixture traceability/failure stage, invocation migration/default route, toolchain freshness, event transaction/prefix, package/Windows/Lua/no-mutation evidence를 검토한다.
- Review 5: eleven-role durable bundle, owner authority records, lifecycle event, C-5 candidate/live additive adoption, pre/post manifest binding과 allowlist no-mutation을 검토한다.
- Review 6: eligible independent review, owner seal, nine-role durable closeout packet commit, terminal transaction ordering, claim boundary와 clean-checkout content availability를 검토한다.

### Validation Limits

수행하지 않는 검증:

- manual in-game behavior
- Browser/Tooltip/Wiki UX
- public text/semantic quality
- item meaning/legitimacy
- Workshop packaging/publication
- release/B42/deployment readiness
- multiplayer/long session
- 모든 third-party parser/PowerShell/OS matrix
- external mod compatibility sweep
- Branch B source correction validity
- full runtime equivalence
- Kahlua/Project Zomboid runtime equivalence

---

## 8. Risk Surface Touch

### Authority Surface

있음 — compatibility policy, actual owner/review authority records, bounded role disposition, durable required gate, bundle lifecycle ledger, tracked closeout seal을 추가한다. source/rendered/runtime/package authority ownership과 lookup semantics는 변경하지 않는다.

### Runtime Behavior Surface

제한적 — live Lua payload를 변경하지 않는다. bridge/package build가 invalid identity/policy 상태에서 더 일찍 non-zero로 실패하도록 build-time guard를 강화한다.

### Compatibility Surface

있음 / 핵심 — exact code-point identity, ASCII comparison identity, alias no-new-key regression, Windows projection, chunk merge, actual Lua reconstruction, isolated package binding을 다룬다.

### Sealed Artifact Surface

있음 — protected inputs를 read/hash-bind하고 Branch A completion에서 mutation count 0을 요구하며 bootstrap executor, owner records, lifecycle events, final closeout actual bytes를 tracked immutable surface에 보존한다.

### Public-Facing Output Surface

없음 — user-visible text/quality/release 메시지를 변경하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- comparison role이 runtime canonical winner나 alias로 오용될 수 있다.
- Windows sidecar가 authority로 오독될 수 있다.
- standalone subprocess가 future authority text에서 executed-tooling closure로 판독될 수 있다.
- final governance artifact가 live required manifest에 들어가 self-cycle을 만들 수 있다.

완화:

- role fields를 non-resolution 값으로 고정한다.
- 모든 Windows report에 `non_authority_projection=true`를 요구한다.
- Change 0에서 allowlist scope를 `import_closure_only`로 재검증하고 다른 판독이면 separate-scope blocker로 종료한다.
- live manifest post-adoption/governance artifact forbidden list를 validator로 검사한다.

### Runtime Risk

- JSON/Lua dict가 duplicate를 사전 collapse할 수 있다.
- chunk merge overwrite가 final unique count만으로 숨겨질 수 있다.
- package guard가 ZIP 뒤 실행되거나 child exit가 숨겨질 수 있다.
- existing alias declaration을 근거로 four-surface exact equality를 약화할 수 있다.
- Lua/Windows path/encoding 차이가 fallback을 유도할 수 있다.
- candidate/canonical-durable policy context 또는 required-gate state가 바뀌거나 hidden default로 대체될 수 있다.

완화:

- ordered raw record stream과 post-serialization reread를 분리한다.
- raw assignments와 actual Lua final table을 함께 측정한다.
- package guard ordering/non-zero/no-ZIP negative test를 둔다.
- alias declaration/applied-new-key/unexpected-emission metrics를 별도 report로 검증하고 new-key count 0을 요구한다.
- no-fallback, resolved executable/version/path/hash receipt를 요구한다.
- explicit policy context/path/binding/gate-state와 attempt-root/durable-bundle containment을 검증한다.

### Compatibility Risk

- ASCII comparator가 future non-ASCII key에 잘못 적용될 수 있다.
- byte provenance와 equality authority가 혼동될 수 있다.
- exclusion manifest가 divergence를 숨길 수 있다.
- disposition이 input drift 후 stale하게 재사용될 수 있다.
- JSON/Lua escape token 차이를 exact identity 차이로 오판할 수 있다.

완화:

- non-ASCII를 fail-closed하고 새 reviewed comparator scope를 요구한다.
- decoded equality와 byte diagnostic fields를 schema에서 구분한다.
- format-specific raw token과 decoded exact-key hashes를 분리하고 escaped duplicate fixtures를 실행한다.
- wildcard exclusion과 over-broad fixture를 금지한다.
- per-phase freshness와 invalidation matrix를 사용한다.

### Regression Risk

- exporter/package 변경이 existing route를 깨뜨릴 수 있다.
- `.gitignore` 예외가 unrelated generated artifacts를 추적할 수 있다.
- required adoption이 existing rows를 제거/reclassify할 수 있다.
- original dirty top-doc changes를 덮어쓸 수 있다.
- concurrent worktree가 attempt ID를 중복 reserve하거나 과거 attempt event를 수정할 수 있다.
- exporter direct import, reciprocal candidate hashes, partial durable promotion이 sealed boundary를 우회할 수 있다.
- Phase 2 evidence 뒤 claim-affecting tool/test가 바뀌어 stale contract가 promotion될 수 있다.
- 서로 다른 branch의 event prefix가 분기되거나 record/event append가 partial state로 남을 수 있다.
- unreviewed/manual bootstrap executor가 Gate B authority를 가장할 수 있다.
- owner/review record hash literal만 남고 actual authority bytes가 사라질 수 있다.
- fixed `current_*` authority path가 successor를 막거나 ambiguous active authority를 만들 수 있다.
- nonterminal attempt가 남은 상태에서 clean/prefix checks만 통과해 다음 attempt가 열릴 수 있다.
- final review/owner seal/terminal seal bytes가 local cleanup으로 사라지거나 terminal event가 closeout commit보다 먼저 기록될 수 있다.
- invalidated/superseded content-addressed bundle이 lifecycle 확인 없이 재사용될 수 있다.

완화:

- repository-wide invocation inventory/migration matrix, adjacent regressions, post-adoption legacy default command, current-route validation을 함께 실행한다.
- reviewed round-local bootstrap executor/test/contract/report와 exact-path unignore만 Gate A에 허용하고 manual/substitution count 0을 요구한다.
- additive diff removal/reclassification/duplicate count 0을 요구한다.
- clean selected worktree와 owner top-doc application separation을 사용한다.
- named mutex, single integration branch, three-prefix parity, transactional event append, immutable terminal records를 사용한다.
- exporter child receipt/import-graph scan, external candidate binding manifest, versioned directory promotion을 사용한다.
- claim-affecting toolchain manifest와 seven-checkpoint current-byte freshness 검사를 사용한다.
- three authority record actual bytes를 eleven-role durable bundle과 live required test가 직접 검증한다.
- record-id 기반 versioned authority namespace, exact selector path/hash, valid successor positive fixture를 사용하고 `current_*` pointer를 금지한다.
- bootstrap executor가 mutex 안에서 nonterminal count/open ids를 ledger replay로 계산해 0/empty일 때만 새 reservation을 허용한다.
- append-only bundle lifecycle record/event와 nine-role durable closeout packet commit-before-terminal ordering을 검증한다.

---

## 10. Rollback Plan

### Implementation Entry 이전

Gate A 전에는 plan과 final incremental review provenance만 존재하며 final review는 WARN/blocker-zero로 governance bootstrap을 허용했다. Gate A executor/versioned approval/nonterminal fixtures가 실패하면 production mutation 없이 candidate bootstrap bytes를 수정하고 다시 Gate A review를 받는다. owner-approved governance bootstrap commit이 만들어진 뒤 Gate B가 실패하면 bootstrap executor/test/contract/report, selected versioned approval record와 zero-event attempt/lifecycle ledgers를 삭제하지 않고 durable governance history로 유지하되 compatibility production tool/test/live manifest는 수정하지 않는다.

### Phase 0 Branch B 또는 C

- Branch B는 typed failure, bound evidence, prohibited mutation statement를 가진 authority-correction handoff만 보존한다.
- Branch C는 missing decision/dependency/policy/freshness를 기록하고 blocked로 종료한다.
- source/rendered/runtime/package를 임시 rename/merge/alias로 우회하지 않는다.

### Live Adoption 이전

- 신규 standalone tooling/integration/tests/candidate config를 비채택 상태로 되돌릴 수 있다.
- durable failed/invalidated terminal records, event history, failure summary, review finding은 삭제하지 않는다. local supporting evidence는 terminal seal과 review가 끝날 때까지 보존한다.
- 새 실행은 새 attempt id를 사용한다.
- invocation migration 또는 default route가 불완전하면 unrelated caller를 임시 bypass하지 않고 package/exporter success를 차단한다.
- toolchain drift가 발생하면 old PASS receipts를 재사용하거나 durable baseline manifest를 rewrite하지 않는다.
- package guard가 이미 integration되었으나 정확하지 않으면 package 성공을 차단한 상태로 수정하고 false PASS를 허용하지 않는다.
- directory publish 전 partial promotion은 attempt failure로 남기고 durable bundle을 만들지 않는다.
- published durable bundle은 rewrite/delete하지 않는다. 후속 probe/adoption이 실패하면 `invalidated` 또는 `package_guard_active_not_required_gate_adopted` lifecycle record를 추가하고 normal package finalization을 차단한다.
- invalidated/superseded lifecycle bundle은 byte-exact이어도 자동 content reuse하지 않는다.

### Live Adoption 이후

- required row나 package guard를 silent removal/default OFF/warning-only로 낮추지 않는다.
- rollback은 reason, affected entry, before/after hash, prior evidence, independent review, owner approval, current-route rerun을 요구한다.
- 잘못된 gate는 additive supersession record로 대체한다.
- post-adoption artifact가 live manifest self-cycle을 만들면 offending additive rows만 reviewed rollback하고 failed attempt를 보존한다.
- closeout packet publish/commit이 실패하면 terminal record/event를 만들지 않고 local failure evidence와 already-durable lifecycle/live state를 보존한다.
- live bundle을 대체할 때 prior bundle directory를 수정하지 않고 `superseded` lifecycle event와 new selected bundle binding을 append한다.

### Policy/Disposition Invalidation 이후

```text
policy or disposition invalidated
-> bridge/package/canonical-durable and live required gate block
-> current attempt closes invalid
-> new owner disposition or separately reviewed successor scope required
```

source correction이 필요하면 이 계획에서 mutation하지 않는다.

---

## 11. Governance Constraints

- `Philosophy.md`의 타 모드 compatibility 우선과 Hub & Spoke/SPI 경계를 유지한다.
- Pulse는 Iris에 의존하지 않고 Iris는 다른 spoke를 직접 참조하지 않는다.
- Iris runtime은 Lua/display-only다. Python/PowerShell은 offline build/inspection tooling이다.
- DVF Body Compiler는 approved inputs에서 rendered body를 만드는 책임에 머문다.
- Registry Runtime Compatibility는 source/rendered/runtime/package identity lifecycle만 소유한다.
- Registry Authority predecessor를 rewrite하거나 재봉인하지 않는다.
- exact identity와 comparison identity는 상호 대체하지 않는다.
- source/rendered/runtime/package decoded exact key-set은 모두 같아야 하며 alias-added new key를 허용하지 않는다.
- comparison key는 collision analysis 외 lookup/alias/source correction에 쓰지 않는다.
- owner disposition/role은 technical failure를 override하지 않는다.
- current core와 tooling allowlist를 변경하지 않는다.
- allowlist가 필요하면 이 execution을 막고 separate reviewed scope로 이관한다.
- exporter/package caller는 repository-wide inventory와 migration matrix에서 정확히 한 route/disposition을 가지며 unknown/unmigrated caller를 허용하지 않는다.
- post-adoption canonical default는 live manifest-selected exact versioned bundle만 사용하고 pre-adoption omission/partial override는 fail-closed한다.
- candidate manifest probe는 official current route가 아니며 official `current-route PASS`는 live adoption 후에만 허용한다.
- candidate policy는 attempt-local explicit context로, canonical-durable policy는 selected immutable bundle explicit context로만 소비한다.
- exporter는 compatibility analyzer를 direct import하지 않고 exact validator subprocess receipt를 writer 전에 요구한다.
- candidate contract는 external binding manifest로만 hash-bind하며 reciprocal/self/downstream hash edge를 금지한다.
- plan approval, collision owner disposition, Phase 0/Review 2 record actual bytes는 candidate/durable/live required contract의 필수 six-leaf authority surface다.
- 세 authority record는 selected versioned path/id/hash로만 소비하고 mutable `current_*` pointer를 만들지 않는다.
- package guard는 unconditional이다.
- required-validation adoption은 additive-only이고 self-cycle을 만들지 않는다.
- live required artifacts는 durable tracked surface만 허용한다.
- bundle lifecycle은 round-local append-only durable event/record authority이며 local report로 대체하지 않는다.
- failed/invalidated terminal records와 attempt event history를 삭제하거나 rewrite하지 않는다.
- attempt ID는 named-mutex reservation, append-only event ledger, immutable per-attempt records를 통해 no-reuse하며 pre-Phase 0 failure도 ID를 소비한다.
- 새 attempt 전 canonical ledger의 nonterminal count 0/open ids empty를 요구하며 기존 open attempt를 새 ID로 우회하지 않는다.
- first attempt 전 governance-only bootstrap commit과 owner re-baseline을 요구하며 attempt를 사후 durable materialize하지 않는다.
- attempt는 owner-approved single integration branch에서만 실행하고 selected/approved/shared committed event prefix equality를 요구한다.
- record/event append transaction의 unreconciled partial state나 cross-branch supersession을 자동 override하지 않는다.
- local supporting evidence는 terminal sealing 뒤 clean-checkout authority가 아니며 required durable bootstrap/owner bundle/lifecycle/terminal/closeout actual bytes가 current route와 canonical claim을 검증한다.
- claim-affecting implementation toolchain은 durable manifest와 current checkout이 모든 required checkpoint에서 byte-identical해야 한다.
- independent review와 owner seal은 서로 대체하지 않는다.
- successful closeout은 nine-role per-attempt durable packet commit 뒤에만 terminal record/event를 append하고 terminal event가 closeout commit/manifest/seal을 직접 결속한다.
- bootstrap executor, attempt ledger, bundle lifecycle ledger, closeout packet은 `dvf_3_3_registry_runtime_compatibility` round-local namespace 밖에서 재사용하거나 general framework로 승격하지 않는다.
- protected source/rendered/runtime/package와 active core closure mutation count는 Branch A completion에서 0이다.
- final claim은 axis-qualified한다.
- bare `DVF PASS`, `DVF System PASS`, bare `PASS`, bare `complete`, bare `partial`을 terminal state로 사용하지 않는다.
- bare `Runtime Compatibility PASS`는 current formal claim으로 금지한다.
- 최대 claim은 `Registry Runtime Compatibility PASS`다.

---

## 12. Expected Closeout State

### Current Planning Artifact State

```text
cycle5_final_incremental_review_verdict = WARN
final_plan_review_open_critical_count = 0
final_plan_review_open_implementation_blocker_count = 0
governance_bootstrap_allowed = true
gate_a_status = pending
implementation_entry_allowed = false
```

이 token은 plan execution이 Gate A로 진행 가능하다는 뜻이다. Gate A/B의 실제 executor review, owner approval, bootstrap commit, reservation이 완료되지 않았으므로 implementation entry나 machine PASS를 뜻하지 않는다. independent review, owner seal, required-gate adoption, package/release readiness도 주장하지 않는다.

### Future Successful Execution State

다음 조건이 모두 충족된 future attempt만 허용한다.

```text
implementation_entry_allowed = true
production_integration_allowed = true
preentry_executor_contract_complete = true
bootstrap_executor_contract_reviewed = true
bootstrap_executor_test_status = PASS
bootstrap_executor_hash_matches = true
bootstrap_executor_scope_violation_count = 0
ad_hoc_or_manual_reservation_count = 0
reservation_preflight_nonterminal_attempt_count = 0
reservation_preflight_open_attempt_ids = []
selected_versioned_authority_record_count = 3
mutable_current_authority_pointer_count = 0
authority_successor_chain_break_count = 0
authority_successor_fork_or_cycle_count = 0
selected_authority_not_chain_head_count = 0
final_plan_reviewer_reused_as_closeout_reviewer_count = 0
phase0_branch = A
technical_failure_count = 0
source_rendered_runtime_package_exact_keyset_match = true
applied_new_alias_key_count = 0
alias_induced_comparison_collision_increase = 0
attempt_reuse_count = 0
prior_event_mutation_count = 0
event_hash_chain_break_count = 0
unreconciled_partial_event_transaction_count = 0
event_prefix_divergence_count = 0
retroactive_attempt_materialization_count = 0
preentry_required_path_ignored_count = 0
preentry_required_path_untracked_count = 0
required_durable_reference_missing_count = 0
roadmap_fixture_1_to_10_mapping_complete = true
unresolved_roadmap_fixture_count = 0
ordinary_exact_key_set_positive_status = PASS
windows_projection_cardinality_loss_negative_status = PASS
invocation_inventory_unknown_count = 0
unmigrated_invocation_count = 0
invocation_inventory_authority_baseline = owner_approved_clean_baseline
dirty_original_docs_consumed_as_authority_count = 0
default_route_compatibility_status = PASS
implementation_toolchain_drift_count = 0
required_tool_missing_count = 0
required_tool_untracked_count = 0
required_tool_ignored_count = 0
unclassified_tool_dependency_count = 0
exporter_forbidden_analyzer_import_count = 0
exporter_writer_before_guard_count = 0
bridge_preflight_four_surface_overclaim_count = 0
candidate_binding_cycle_edge_count = 0
candidate_authority_leaf_count = 6
durable_owner_review_authority_record_count = 3
durable_owner_authority_record_count > 0
durable_owner_authority_missing_or_invalid_count = 0
durable_promotion_required_role_mismatch_count = 0
durable_promotion_required_role_count = 11
durable_promotion_partial_publish_count = 0
bundle_lifecycle_chain_break_count = 0
selected_bundle_lifecycle_state = live_required_gate_adopted
terminal_lifecycle_content_reuse_count = 0
windows_surface_input_missing_or_stale_count = 0
candidate_policy_context_validation = PASS
canonical_durable_policy_context_validation = PASS
policy_lifecycle_state = live_required_gate_adopted
candidate_manifest_route_status = PASS
official_post_adoption_current_route_status = PASS
pre_adoption_live_manifest_sha256 = present_and_bound
post_adoption_live_manifest_sha256 = present_and_bound
selected_durable_bundle_id = present_and_bound
selected_bundle_manifest_sha256 = present_and_bound
adopted_row_identity = present_and_bound
C-4_route_a_canonical_status = PASS
C-4_route_c_transport_regression_status = PASS
C-4_algorithm_proof_count = 1
C-4_transport_conformance_count = 2
C-5 = live_additive_required_gate
roadmap_or_condition_superseded_by_plan_and_condition = true
owner_explicitly_approved = true
package_guard_mode = unconditional
tooling_allowlist_mutation_count = 0
machine_contract_status = PASS
independent_review_status = PASS
owner_seal_status = PASS
durable_closeout_required_role_count = 9
durable_closeout_artifact_missing_count = 0
durable_closeout_hash_mismatch_count = 0
independent_review_content_available = true
owner_seal_content_available = true
terminal_seal_content_available = true
terminal_event_before_closeout_commit_count = 0
clean_checkout_final_evidence_validation = PASS
review_verdict = PASS
closeout_state = registry_runtime_compatibility_canonical_complete
claim_scope = registry_runtime_compatibility_only
formal_claim_token = Registry Runtime Compatibility PASS
bare_runtime_compatibility_pass_current_claim_count = 0
lua_runtime_family = PUC_LUA
executed_lua_validation_role = offline_table_reconstruction_only
project_zomboid_runtime_executed = false
cross_version_parity_executed = false
cross_version_parity_claimed = false
kahlua_equivalence_claimed = false
```

허용되는 formal claim:

```text
Registry Runtime Compatibility PASS
```

Alternative terminal states:

- `compatibility_blocked_authority_correction_handoff_ready`
- `compatibility_blocked_missing_owner_disposition`
- `compatibility_blocked_required_dependency`
- `compatibility_blocked_allowlist_expansion_requires_separate_scope`
- `compatibility_blocked_alias_identity_expansion_requires_separate_scope`
- `compatibility_blocked_policy_context_substitution`
- `compatibility_blocked_attempt_allocation_failure`
- `compatibility_blocked_governance_ledger_bootstrap`
- `compatibility_blocked_bootstrap_executor_contract`
- `compatibility_blocked_event_prefix_divergence`
- `compatibility_blocked_event_transaction_partial_state`
- `compatibility_blocked_invocation_migration`
- `compatibility_blocked_toolchain_freshness`
- `compatibility_blocked_roadmap_fixture_coverage`
- `compatibility_blocked_candidate_binding_cycle`
- `compatibility_blocked_owner_authority_record`
- `compatibility_blocked_incomplete_durable_promotion`
- `compatibility_blocked_bundle_lifecycle`
- `compatibility_blocked_durable_closeout_packet`
- `compatibility_blocked_windows_surface_input`
- `compatibility_blocked_unsupported_lua_version`
- `compatibility_blocked_live_adoption_not_approved`
- `compatibility_implemented_not_adopted`
- `compatibility_machine_pass_governance_pending`

어떤 alternative도 `partial complete` 또는 compatibility PASS로 요약하지 않는다.

필수 non-claim:

```text
Registry Runtime Compatibility PASS
does not imply Registry Authority PASS,
DVF Body Compiler PASS,
Publish Boundary PASS,
source mutation authority,
package publication,
release readiness,
Workshop readiness,
B42 readiness,
deployment readiness,
or manual QA completion.
```
