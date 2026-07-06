# ROADMAP — DVF Core / Iris Artifact Registry Boundary Claim Contract Closure

Round identifier: `dvf_3_3_core_registry_boundary_claim_contract_closure`
Status: staging roadmap draft / canonical 아님 / 저자 확정 필요

---

## 1. Problem Statement

DVF Core와 Iris Artifact Registry의 책임 경계가 공식 claim contract로 닫혀 있지 않다.

선행 preflight에서 current-route / governance surface는 axis별로 분류되었고, `current_route_required_validations.json`은 `legacy_combined_governance_route`로 동결되었다. 또한 이 legacy combined route의 PASS가 DVF Core PASS authority가 아니라는 freeze sentence도 존재한다.

그러나 아직 다음은 공식 계약으로 닫히지 않았다.

* `DVF Core PASS`가 무엇을 뜻하고 무엇을 뜻하지 않는지
* `Registry Authority PASS`가 무엇을 뜻하고 무엇을 뜻하지 않는지
* `Registry Runtime Compatibility PASS`가 무엇을 뜻하고 무엇을 뜻하지 않는지
* `Publish Boundary PASS`가 무엇을 뜻하고 무엇을 뜻하지 않는지
* `Legacy Combined Current Route PASS`가 다른 claim으로 승격 해석되지 않는다는 기계 가드
* `DVF PASS` 단독 claim의 current claim 처분

현재 상태에서는 `DVF PASS` 또는 `current route PASS`가 다음 의미로 오독될 수 있다.

* DVF Core body compiler 성공
* Registry authority 안전성
* runtime consumer compatibility
* package safety
* public text acceptance
* release / Workshop readiness
* stale / predecessor artifact reentry guard
* required-validation manifest ownership
* seal / cutover completion

따라서 이번 로드맵의 목적은 구현 확장이 아니라, claim vocabulary / non-claim matrix / routing contract / machine guard를 통해 DVF Core, Iris Artifact Registry, Registry Runtime Compatibility, Publish Boundary, Legacy Combined Current Route의 claim boundary를 분리하는 것이다.

---

## 2. Current State

현재 닫힌 상태는 다음과 같다.

* `legacy_combined_route_axis_inventory` 선행 preflight가 완료되었다.
* `current_route_required_validations.json`은 `legacy_combined_governance_route`로 동결되었다.
* freeze sentence는 `current_route_required_validations.json = legacy_combined_governance_route != DVF Core PASS authority`로 존재한다.
* current combined route에는 body compiler, registry authority, runtime payload compatibility, publish/package guard, stale/historical artifact guard, diagnostic fixture, completion vocabulary gate가 함께 들어 있다.
* 선행 preflight는 manifest physical split, required test 이동, runner rewrite, Registry Authority PASS, Runtime Payload Consumer Compatibility closure, Public Text Quality closure, runtime/package mutation을 열지 않았다.
* current route의 PASS는 legacy combined route container의 PASS일 뿐이며, 각 claim class의 공식 의미 범위는 아직 doc / machine / test 수준에서 분리되지 않았다.
* parent closure 기준 current route PASS / 127 tests / closure_enforced true가 언급되어 있으나, 이번 라운드에서는 해당 count를 규범 상수로 하드코딩하지 않고 live inventory에서 재도출해야 한다.

현재 DVF Core 책임 상한은 다음으로 제한된다.

```text
facts / decisions / profile / body_plan -> rendered 3-3 body
```

Iris Artifact Registry 책임 축은 다음으로 분리된다.

* artifact authority
* artifact role classification
* source / rendered / runtime / package identity
* staging evidence
* required validation
* seal
* cutover
* stale / predecessor reentry guard
* runtime consumer compatibility

Publish Boundary 책임 축은 다음으로 분리된다.

* public text acceptance
* semantic quality acceptance
* package publication
* release / Workshop readiness
* manual QA

현재 validation confidence는 “routing preflight ready” 수준이다. 즉, routing input은 준비되었지만 claim boundary closure 자체는 아직 완료되지 않았다.

---

## 3. Desired Outcome

이번 라운드 완료 후 다음 5개 claim class가 서로 대체 불가능한 별도 의미를 가진다.

```text
DVF Core PASS
Registry Authority PASS
Registry Runtime Compatibility PASS
Publish Boundary PASS
Legacy Combined Current Route PASS
```

각 claim class는 다음 수준에서 계약된다.

* doc 수준: claim contract 문서
* machine 수준: machine-readable claim contract / registry
* test 수준: claim vocabulary guard / negative fixture / overclaim scan

### DVF Core PASS

의미:

* body compiler determinism
* `facts / decisions / profile / body_plan` 소비 계약
* rendered 3-3 body shape
* body block composition contract
* 해당 scope 안에서의 protected output no-mutation boundary

비의미:

* runtime compatible 아님
* package safe 아님
* public accepted 아님
* release ready 아님
* Registry authority PASS 아님
* required-validation manifest ownership 아님
* stale / predecessor guard PASS 아님

### Registry Authority PASS

의미:

* artifact authority 분리
* artifact role classification
* source / rendered / runtime / package identity role 분류
* staging evidence와 required validation의 소비 경계
* stale / predecessor reentry guard가 authority surface로 재진입하지 않음

비의미:

* public text acceptance 아님
* semantic quality acceptance 아님
* package publication readiness 아님
* release readiness 아님
* DVF Core compiler 성공 자체 아님
* Registry Runtime Compatibility PASS 자체 아님

### Registry Runtime Compatibility PASS

의미:

* runtime consumer가 현재 Registry artifact shape를 안전하게 소비할 수 있음
* runtime payload / consumer compatibility contract가 닫힘
* source authority mutation 없이 runtime compatibility가 검증됨

비의미:

* source authority mutation 아님
* text quality acceptance 아님
* public acceptance 아님
* package publication 아님
* release readiness 아님
* Registry Authority PASS 전체 달성 아님

### Publish Boundary PASS

의미:

* public text acceptance
* semantic quality acceptance
* package publication readiness
* release / Workshop readiness
* manual QA, 별도 검증 시에만

비의미:

* DVF Core compiler 성공 아님
* Registry Authority PASS 아님
* Registry Runtime Compatibility PASS 아님
* Legacy Combined Current Route PASS 아님

### Legacy Combined Current Route PASS

의미:

* 기존 combined governance route container가 해당 readpoint에서 통과함
* runner / manifest / taxonomy-required-validation chain의 legacy combined 검증 통과
* routing evidence 또는 historical governance evidence로 보존 가능

비의미:

* DVF Core PASS의 정의 권한 아님
* Registry Authority PASS 아님
* Registry Runtime Compatibility PASS 아님
* Publish Boundary PASS 아님
* release readiness 아님

### `DVF PASS` 단독 claim 처분

두 로드맵 모두 `DVF PASS` 단독 current claim을 그대로 허용하지 않는 방향이다.

다만 최종 처분은 저자 유보로 남긴다.

* Option A: current claim 전면 금지
* Option B: `legacy_alias_only` / `historical_quote` / `negated_claim` / `forbidden_claim_example` 등 role-qualified 예외로만 잔존

---

## 4. Constraints

보존해야 할 제약은 다음과 같다.

* `Philosophy.md` 준수
* Hub & Spoke / SPI 구조 보존
* Core 오염 방지
* DVF Core는 설명 블록 조합 시스템으로만 유지
* Iris Artifact Registry는 artifact authority / validation / runtime compatibility / guard / seal 책임을 Core로 넘기지 않음
* Publish Boundary는 public acceptance / release readiness 축으로 별도 유지
* runtime/build-time separation 보존
* FAIL-LOUD 보존
* source / rendered / Lua bridge / runtime chunk / package payload no-mutation
* current combined route 보존
* `legacy_combined_governance_route` 물리 분해 금지
* current route runner rewrite 금지
* runtime chunk 변경 금지
* bridge export 변경 금지
* rendered text rewrite 금지
* public-facing copy 변경 금지
* 대량 rename 금지
* required-validation manifest 전면 물리 분해 금지
* required test / required artifact의 axis 간 물리 이동 금지
* Registry 전체 구현 완료를 이번 scope로 열지 않음
* Runtime Payload Consumer Compatibility 실제 closure를 이번 scope로 열지 않음
* Public Text Quality acceptance를 이번 scope로 열지 않음
* package publication / manual QA를 이번 scope로 열지 않음
* additive-only sealed surfaces
* single-writer authority per newly created claim contract surface
* denominator non-substitution: preflight count를 이번 라운드 gate 값으로 치환 상속하지 않음
* plan-level PASS와 independent-review / owner-seal gate 분리

---

## 5. Non-Goals

이번 로드맵에서 제외되는 작업은 다음과 같다.

* Registry 전체 구현 완료
* Registry Authority 전체 closeout
* Registry Runtime Compatibility 실제 closure
* Runtime Payload Consumer Compatibility 실제 구현 / 검증 완료
* Public Text Quality acceptance
* semantic quality acceptance
* package publication
* release / Workshop / B42 readiness
* deployment readiness
* manual in-game QA
* current-route runner 재작성
* manifest 전면 물리 분해
* required test / required artifact 대량 이동
* runtime chunk 변경
* Lua bridge export 변경
* rendered text rewrite
* source facts / decisions / overlay mutation
* package payload mutation
* stale artifact 삭제
* predecessor artifact cleanup
* public-facing copy 변경
* 새로운 release strategy 수립
* 5개 claim class 각각의 실제 PASS 달성
* `legacy_combined_governance_route`의 폐기 또는 대체 route 신설
* MIGV-QA / `ready_for_release` / B42 / Workshop / deployment readiness 관련 실행

---

## 6. Proposed Approach

전략은 물리 분해가 아니라 claim-contract-first closure다.

진행 방향은 다음과 같다.

1. 선행 axis inventory / routing preflight report / axis policy doc을 이번 라운드의 read-only routing input으로 소비한다.
2. DVF Core / Registry Authority / Registry Runtime Compatibility / Publish Boundary / Legacy Combined Current Route의 claim vocabulary를 분리한다.
3. 각 claim의 allowed meaning과 forbidden meaning을 문서화한다.
4. 동일 내용을 machine-readable claim contract / registry로 미러링한다.
5. 후속 work intake routing matrix를 문서와 machine contract에 고정한다.
6. standalone `DVF PASS`, ambiguous PASS, overclaim 문구를 scan하고 fail-closed한다.
7. `Legacy Combined Current Route PASS`가 DVF Core PASS나 Registry / Publish PASS로 승격 해석되지 않도록 negative fixture를 둔다.
8. current route는 legacy combined route로 보존한다.
9. closeout 이후 새 DVF Core 작업이 Registry / runtime / package / publish 책임을 Core로 추가하려 할 때 fail-loud 또는 reroute되도록 한다.
10. 상위 문서 반영은 additive-only로 제한한다.
11. optional required-gate adoption은 별도 저자 결정으로 남긴다.

핵심 레이어는 다음 다섯 가지다.

```text
human docs
machine-readable claim contract / registry
focused test / validator / negative fixture
legacy combined route preservation
future-work routing guard
```

---

## 7. Authority / Surface Impact

### Authority Surface

Describe.

신규 claim contract 문서와 machine contract 파일이 새 authority surface로 생성될 수 있다. 단, 이는 source / rendered / runtime / package authority 변경이 아니라 claim authority 분리다.

후보 산출물:

* claim contract 문서
* routing policy 문서
* claim boundary 문서
* machine-readable claim contract / registry JSON
* routing matrix JSON
* claim surface inventory
* forbidden overclaim scan report
* validation report
* final boundary split closure report

파일명과 경로는 저자 확정 필요 항목이다.

### Runtime Behavior Surface

None.

runtime Lua, runtime chunks, bridge export, package payload, UI display behavior는 변경하지 않는다.

### Compatibility Surface

None / direct runtime compatibility change 없음.

다만 문서와 machine claim에서 다음 routing은 고정된다.

```text
Runtime Payload Consumer Compatibility -> Registry Runtime Compatibility Closure
Current authority / required validation / seal / stale artifact -> Registry Authority Closure
Public Text Quality / public acceptance / release readiness -> Publish Boundary Closure
Body compiler determinism / body_plan / rendered body shape -> DVF Core Closure
```

### Sealed Artifact Surface

Describe.

새 sealed artifact는 claim contract / routing policy / scan report / final report / validation report 수준이다. 기존 sealed runtime / source / rendered / package artifacts는 변경하지 않는다.

### Public-Facing Output Surface

None.

public text, tooltip, wiki body, package README, Workshop description, release note는 변경하지 않는다. public-facing wording은 Publish Boundary scope에서만 다룬다.

---

## 8. Phases

### Phase 0 — Scope Lock / Preflight Consumption Readpoint

Goal:

선행 preflight를 이번 closure의 유일한 routing input으로 고정하고, Registry implementation이나 Publish acceptance로 scope가 확장되지 않게 막는다.

Primary Changes:

* `legacy_combined_route_axis_inventory.json`을 canonical input으로 선언
* `routing_preflight_report.json` 및 axis policy doc fingerprint 기록
* `current_route_required_validations.json = legacy_combined_governance_route != DVF Core PASS authority` freeze sentence 재확인
* source / rendered / Lua bridge / runtime / package protected no-mutation baseline 선언
* required test / required artifact / union test count는 live inventory에서 재도출
* 선행 preflight를 boundary closure 완료로 오독하지 않도록 scope lock report 생성

Expected Risks:

* 선행 preflight를 이미 closure 완료로 오독할 위험
* current route PASS를 다시 Core PASS로 축약할 위험
* 선행 inventory와 live manifest 간 drift 발견 가능성
* Registry Runtime Compatibility를 이번 scope에 끌어들이는 위험

Expected Validation:

* input inventory presence / hash binding
* routing preflight report fingerprint 기록
* live count 재도출 및 inventory 내부 count와 정합 확인
* protected no-mutation baseline capture
* forbidden scope expansion `0`
* drift 발견 시 fail-loud / silent 재분류 금지

Expected Deliverables:

* `phase0/input_readpoint_binding.json`
* `phase0/protected_surface_baseline.json`
* `phase0/scope_lock_report.json`
* `phase0/preflight_consumption_readpoint.json`
* `phase0/live_inventory_count_derivation.json`

---

### Phase 1 — Boundary Claim Contract Document

Goal:

5개 claim class의 의미 / 비의미 / routing을 담은 정본 claim contract 문서를 작성한다.

Primary Changes:

* claim contract 문서 신설
* 5개 claim class 정의
* 각 claim의 allowed meaning / forbidden meaning 대칭 행렬 작성
* DVF Core 책임 상한 명시
* Registry 책임 축 명시
* Publish Boundary 책임 축 명시
* 후속 routing 4문장 명시
* `DVF PASS` 단독 claim 처분 규정 작성
* post-closeout Core 확장 금지 규정 작성

최소 포함 non-claim:

* `DVF Core PASS`는 runtime compatible / package safe / public accepted / release ready를 뜻하지 않는다.
* `Legacy Combined Current Route PASS`는 DVF Core PASS의 정의 권한이 아니다.
* `Registry Authority PASS`는 public text acceptance / release readiness를 뜻하지 않는다.
* `Registry Runtime Compatibility PASS`는 source authority mutation / text quality acceptance를 뜻하지 않는다.
* `Publish Boundary PASS`는 DVF Core compiler 성공을 뜻하지 않는다.

Expected Risks:

* claim 정의 문안이 기존 sealed vocabulary와 충돌할 위험
* `Registry Authority PASS`와 `Registry Runtime Compatibility PASS`가 다시 합쳐질 위험
* `Publish Boundary PASS`가 Core compiler 성공까지 포괄하는 식으로 넓어질 위험
* `Legacy Combined Current Route PASS`가 상위 통합 PASS처럼 부활할 위험
* `DVF PASS` 처분을 저자 결정 없이 선결정할 위험

Expected Validation:

* 기존 freeze sentence와 무모순 대조
* 기존 DECISIONS / ARCHITECTURE vocabulary와 대조
* 모든 claim이 exactly one owner axis를 갖는지 확인
* 모든 claim이 allowed meaning과 forbidden meaning을 모두 갖는지 확인
* `Legacy Combined Current Route PASS`의 `may_define_dvf_core_pass=false`
* `DVF Core PASS`의 runtime / package / public / release 권한 false
* adversarial review 대상 지정

Expected Deliverables:

* claim contract document staging draft
* claim non-claim matrix draft
* unresolved author-decision list

저자 유보:

* `DVF PASS` 처분: current claim 전면 금지 vs legacy alias로만 잔존
* 5개 claim token 최종 표기
* 문서 경로 / 파일명 확정

---

### Phase 2 — Machine-Readable Claim Contract / Routing Matrix

Goal:

Phase 1의 claim contract를 machine-readable contract로 미러링하고, 후속 work intake routing을 구조화한다.

Primary Changes:

* claim contract JSON 신설
* 5 claim class 구조화
* non-claim matrix 구조화
* routing matrix 구조화
* `DVF PASS` 처분 상태 구조화
* Core 확장 금지 목록 구조화
* 문서 ↔ JSON hash reference 기록
* 선행 inventory의 7축 vocabulary에서 derive
* 신규 축 발명 금지

Claim field 후보:

```text
claim_id
allowed_meaning
forbidden_meaning
owner_axis
allowed_inputs
required_evidence_kind
may_consume_legacy_combined_route
may_define_dvf_core_pass
may_claim_release_readiness
may_claim_runtime_compatibility
may_claim_public_acceptance
```

Routing matrix:

```text
Runtime Payload Consumer Compatibility -> Registry Runtime Compatibility Closure
Current authority / required validation / seal / stale artifact -> Registry Authority Closure
Public Text Quality / public acceptance / release readiness -> Publish Boundary Closure
Body compiler determinism / body_plan / rendered body shape -> DVF Core Closure
```

Expected Risks:

* 문서와 JSON 간 내용 drift
* routing matrix가 문서에만 있고 test가 없어 흐려질 위험
* legacy combined route를 routed-through와 responsibility-of로 구분하지 못할 위험
* unknown / todo / unclear routing이 잔존할 위험

Expected Validation:

* JSON schema-level 자기검증
* 재생성 결정론 / byte-stability
* 문서 ↔ JSON 정합
* routing matrix total coverage
* unknown / todo / tbd / unclear routing `0`
* forbidden reroute fixture 준비

Expected Deliverables:

* `phase2/claim_contract.json`
* `phase2/claim_non_claim_matrix.json`
* `phase2/future_work_routing_matrix.json`
* `phase2/document_machine_hash_binding.json`
* generator / validator 후보

저자 유보:

* machine contract JSON 경로 / 파일명
* stable machine fields 범위
* routing exception 표현 방식

---

### Phase 3 — Claim Vocabulary Guard / Overclaim Scanner / Negative Fixture

Goal:

계약 위반 claim이 docs / staging reports / claim boundary / ledger packet에서 재등장하지 않게 fail-closed guard를 만든다.

Primary Changes:

* governance claim surface scan
* bare `DVF PASS` current claim 탐지
* historical quote / legacy alias / negated claim / forbidden example 예외 class 구분
* `DVF Core PASS = runtime compatible`류 overclaim 금지
* `Legacy Combined Current Route PASS = DVF Core PASS`류 overclaim 금지
* `Registry Authority PASS = release ready`류 overclaim 금지
* `Registry Runtime Compatibility PASS = source mutation / text quality acceptance`류 overclaim 금지
* `Publish Boundary PASS = compiler success`류 overclaim 금지
* contract JSON ↔ contract document 정합 test
* negative fixture가 실제 FAIL을 내는지 검증

Expected Risks:

* scan scope가 너무 넓어 historical 문구를 false positive로 잡을 위험
* scan scope가 너무 좁아 실제 overclaim을 놓칠 위험
* regex-only guard로 흘러 의미 위반을 놓칠 위험
* guard가 존재하지만 실제로 fail하지 않는 위험
* 예외 class가 과도하게 넓어지는 위험

Expected Validation:

* positive fixtures 통과
* negative fixtures fail 실증
* historical quote / legacy alias fixture role-qualified 통과
* no unknown claim class
* no unclassified PASS surface
* contract JSON ↔ doc 정합
* existing current route 표면과 비파괴 공존 확인

Expected Deliverables:

* guard test
* negative fixtures
* claim surface inventory
* forbidden overclaim scan report
* guard execution report JSON
* validator / unittest 후보

저자 유보:

* guard scan 대상 governance claim surface 목록
* 예외 규칙
* live required-validation manifest additive 채택 여부

---

### Phase 4 — Top-Doc Additive Sync

Goal:

ARCHITECTURE.md / DECISIONS.md / ROADMAP.md 계열에서 claim boundary를 additive로 정렬한다.

Primary Changes:

* ARCHITECTURE.md에 DVF Core / Registry / Publish Boundary 역할 경계 additive 반영
* DECISIONS.md에 신규 봉인 항목 초안 추가
* ROADMAP.md에 claim boundary closure 상태 반영
* legacy combined route 보존 문구 유지
* standalone `DVF PASS` current claim 금지 또는 legacy-alias-only 처분 반영
* release readiness / public acceptance / runtime compatibility non-claim 명시
* canonical 반영 전 staging draft 유지

Expected Risks:

* top-doc update가 구현 change처럼 오독될 위험
* DECISIONS 항목이 compact trace 원칙을 깨는 위험
* ROADMAP이 다음 구현 단계를 자동으로 여는 위험
* live repo top docs와 draft copy 간 hash divergence 가능성
* 기존 오래된 `DVF PASS` 문구를 고치려다 대량 text rewrite로 확장될 위험

Expected Validation:

* top-doc additive-only validation
* 기존 본문 무변형 diff 검사
* claim scanner over top docs
* no forbidden standalone `DVF PASS`
* no release/package/public acceptance overclaim
* no source/rendered/runtime/package mutation
* top-doc sync state 기록

Expected Deliverables:

* `phase4/top_doc_claim_boundary_patch_report.json`
* `phase4/top_doc_overclaim_scan_report.json`
* ARCHITECTURE.md additive draft
* DECISIONS.md additive draft
* ROADMAP.md additive draft
* top-doc sync state report

저자 유보:

* 상위 문서 반영 시점
* 최종 문안
* canonical seal 여부

---

### Phase 5 — Optional Additive Required-Gate Adoption

Goal:

이번 boundary claim contract closure를 legacy combined route에 물리 분해 없이 additive governance gate로 소비할지 결정한다.

Primary Changes:

* `current_route_required_validations.json`에 final report와 focused unittest를 additive required gate로 넣을 수 있다.
* 이 adoption은 `legacy_combined_governance_route` 보존이며 manifest split이 아니다.
* required artifact / test removal 금지
* predicate meaning change 금지
* runner rewrite 금지
* stable machine fields만 required artifact로 사용
* self-referential current-route dependency 회피
* adoption 생략 가능

Expected Risks:

* required gate adoption이 Registry Authority PASS나 DVF Core PASS 자체로 오독될 위험
* current route PASS test count가 claim boundary complete를 과장하는 위험
* manifest additive adoption이 물리 분해의 시작처럼 해석될 위험
* additive adoption 생략 시 closure visibility가 약해질 위험

Expected Validation:

* existing required artifacts/tests removal count `0`
* predicate meaning change count `0`
* current route rerun PASS
* route count 변화 시 재도출 기록
* focused unittest PASS
* validator `--require-complete` PASS
* no self-referential final claim dependency

Expected Deliverables:

* `phase5/required_manifest_adoption_report.json`
* `phase5/current_route_boundary_gate_result.json`
* `phase5/validation_report.require_complete.json`
* adoption decision record

저자 유보:

* additive required-gate 채택 여부
* 채택 시 exact fields / artifact list

---

### Phase 6 — Closure Validation / Final Claim Boundary Seal / Independent Review Gate

Goal:

라운드 machine PASS와 governance / independent review / owner seal을 분리하여 claim boundary closure를 닫는다.

Primary Changes:

* final report JSON 생성
* claim contract fingerprint 기록
* routing matrix fingerprint 기록
* overclaim scan 결과 기록
* negative fixture 결과 기록
* protected-surface no-mutation 확인
* top-doc sync 상태 기록
* current route regression 결과 기록
* exact-command matrix 기록
* optional Lua syntax sweep는 no-change 확인 성격으로만 기록
* machine PASS와 independent_review_gate PASS를 분리

Final report 요구 필드 후보:

```text
status
claim_boundary_split_complete
dvf_pass_standalone_current_claim_allowed
dvf_pass_disposition
legacy_combined_route_preserved
legacy_combined_route_pass_is_dvf_core_pass
dvf_core_pass_runtime_compatible
dvf_core_pass_package_safe
dvf_core_pass_public_accepted
dvf_core_pass_release_ready
registry_authority_pass_public_accepted
registry_authority_pass_release_ready
registry_runtime_compatibility_pass_source_mutation
registry_runtime_compatibility_pass_text_quality_acceptance
publish_boundary_pass_dvf_core_compiler_success
protected_surface_changed_count
source_rendered_runtime_package_mutation_allowed
required_gate_adopted
independent_review_gate_status
owner_seal_status
```

Expected Risks:

* final report가 Registry / Publish future closure까지 완료로 오독될 위험
* final report가 canonical seal / owner seal / independent review를 자동 주장할 위험
* machine PASS와 canonical PASS가 섞일 위험
* additive required-gate 채택 시 route count 변화가 과장될 위험

Expected Validation:

* final report schema validation
* claim registry validation
* routing matrix validation
* overclaim scan validation
* focused unittest
* negative fixture failure evidence
* protected no-mutation validation
* current route regression, 선택 또는 채택 시 필수
* exact-command matrix
* VCS preservation recensus
* independent review / owner seal은 별도 gate

Expected Deliverables:

* `phase6/final_boundary_split_closure_report.json`
* `phase6/final_claim_boundary.md`
* `phase6/protected_surface_no_mutation_report.json`
* `phase6/validation_report.require_complete.json`
* `phase6/exact_command_matrix.json`
* `phase6/independent_review_gate.md`

저자 유보:

* canonical seal
* owner seal
* independent review 수행자 / 조건

---

## 9. Validation Expectations

### Expected Validation Depth

판정 보류.

두 안의 판단이 충돌한다.

* ChatGPT안: `heavy`

  * 이유: claim vocabulary가 잘못 닫히면 이후 closeout claim 전체가 오염될 수 있음.
* Claude안: `standard`

  * 이유: governance-only 라운드이며 runtime / package surface 무변형.

공통 최소 요구는 다음이다.

* negative fixture는 existence-only가 아니라 실제 fail 실증 필요
* contract JSON 재생성 결정론 / byte-stability 확인
* 문서 ↔ machine contract 정합 확인
* overclaim scan 확인
* protected source / rendered / Lua bridge / runtime / package no-mutation 확인
* current route regression 확인, 특히 additive required-gate 채택 시 필수

### Expected Validation Areas

* governance claim boundary
* routing contract
* determinism
* regression against legacy overclaim
* documentation consistency
* machine-readable final report schema
* negative fixture validation
* required manifest additive adoption safety, 선택 시
* protected-surface no-mutation
* public-facing output no-mutation

### Known Validation Limits

이번 로드맵에서 기대하지 않는 검증은 다음과 같다.

* runtime consumer compatibility 실제 검증 없음
* package safety 실제 검증 없음
* release readiness 검증 없음
* Workshop readiness 검증 없음
* B42 readiness 검증 없음
* deployment validation 없음
* manual in-game QA 없음
* semantic quality acceptance 없음
* public-facing text acceptance 없음
* full Registry implementation validation 없음
* live migration execution 없음
* runtime chunk parity 검증 없음
* Lua bridge export 변경 검증 없음
* source / rendered regeneration 검증 없음
* external ecosystem compatibility sweep 없음
* multiplayer validation 없음
* 5개 claim class 각각의 실제 PASS 달성 검증 없음
* 이 라운드의 PASS는 claim 의미 계약 완료이지 Registry / Runtime / Publish / Release closure 완료가 아님

---

## 10. Risk Assessment

### High Risk

* `DVF PASS` 단독 claim이 current claim으로 재진입하는 위험
* `Legacy Combined Current Route PASS`가 다시 DVF Core PASS authority로 읽히는 위험
* Registry Authority와 Registry Runtime Compatibility가 한 claim으로 합쳐지는 위험
* Publish Boundary가 Registry / Core 성공과 섞여 release readiness를 과대 주장하는 위험
* claim contract 문안이 기존 sealed vocabulary와 충돌하여 이후 완성 claim 해석에 이중 기준이 생기는 위험
* machine scanner가 historical quote와 current overclaim을 구분하지 못하는 위험
* additive required-gate adoption이 manifest split이나 runner rewrite로 확장되는 위험

### Medium Risk

* guard scan scope가 과광범위하여 false positive로 가드가 무시되는 위험
* guard scan scope가 과협소하여 실제 overclaim을 놓치는 위험
* top-doc update가 source/runtime mutation처럼 오해되는 위험
* final report가 canonical seal / owner seal / independent review를 자동 주장하는 위험
* downstream 계획이 DVF Core 작업 안에 runtime/package guard를 다시 넣는 위험
* 기존 docs의 오래된 `DVF PASS` 문구를 모두 고치려다 대량 rename / text rewrite로 커지는 위험
* 선행 inventory와 live manifest 간 drift 발견 시 라운드 전체 blocked 가능성
* top-doc hash divergence / certification ceiling

### Low Risk

* runtime / compatibility regression, 해당 surface 무변형 전제
* claim vocabulary naming mismatch
* report artifact path drift
* optional manifest adoption 생략 시 closure visibility 약화
* Markdown 문서와 JSON registry 간 용어 차이
* 상위 문서 additive sync 형식 위반
* future routing table에 새 axis가 생길 경우 별도 extension rule 필요

---

## 11. Rollback Strategy

이번 로드맵은 source / rendered / Lua bridge / runtime chunks / package payload를 변경하지 않으므로 rollback은 governance artifact 단위로 제한된다.

Rollback 방식은 다음과 같다.

1. 신규 claim contract 문서를 revert 또는 staging draft로 격하한다.
2. 신규 machine contract JSON을 제거하거나 failed attempt evidence로 격하한다.
3. 신규 guard test / negative fixtures / validator를 revert한다.
4. 신규 staging evidence root를 삭제하거나 historical failed attempt로 격하한다.
5. optional required-validation manifest additive gate를 적용했다면 해당 additive entries만 되돌린다.
6. Phase 4 상위 문서 반영은 additive 단락 제거로 rollback한다.
7. 이미 sealed DECISIONS 항목이 된 이후에는 역사 재작성 대신 supersession entry로 정정한다.
8. legacy combined route는 그대로 유지한다.
9. 기존 `legacy_combined_route_axis_inventory` preflight readpoint는 유지한다.
10. source / rendered / runtime / package artifacts는 rollback 대상이 아니다.
11. rollback 후에는 `Boundary Claim Contract Closure = not adopted / draft only`로 표기한다.

Rollback은 DVF Core와 Registry 경계를 다시 합친다는 뜻이 아니다. 이번 closure artifact adoption을 철회하고 선행 preflight 상태로 돌아가는 것이다.

---

## 12. Success Criteria

이 로드맵은 다음 조건이 만족될 때 성공으로 본다.

* 5개 claim class의 의미와 non-claim이 doc / machine / test 세 수준에서 상호 정합하게 존재한다.
* `DVF Core PASS`의 의미가 body compiler / body_plan / rendered body shape로 제한된다.
* `Registry Authority PASS`의 의미가 artifact authority / role / identity / required validation / seal / stale guard로 제한된다.
* `Registry Runtime Compatibility PASS`의 의미가 runtime consumer compatibility로 제한된다.
* `Publish Boundary PASS`의 의미가 public acceptance / semantic quality / release readiness로 제한된다.
* `Legacy Combined Current Route PASS`가 legacy route container PASS로만 남는다.
* `DVF PASS` 단독 claim이 저자 확정 처분에 따라 계약·가드된다.
* legacy alias / historical quote / negated example / forbidden example 예외가 있을 경우 role-qualified로만 허용된다.
* 후속 routing 4문장이 contract document와 machine contract에 동일하게 고정된다.
* future work routing matrix가 machine-readable하게 존재한다.
* post-closeout Core 확장 금지 규정이 문서와 기계 양쪽에 존재한다.
* negative fixtures가 forbidden claim을 fail-closed한다.
* forbidden overclaim scan이 PASS한다.
* no unknown claim class / no unclassified PASS surface 상태가 확인된다.
* protected source / rendered / Lua bridge / runtime / package surface changed count가 `0`이다.
* current route runner rewrite가 없다.
* manifest physical split이 없다.
* runtime chunk 변경이 없다.
* bridge export 변경이 없다.
* text rewrite가 없다.
* optional required gate adoption 시 기존 required artifact / test removal count가 `0`이다.
* final report가 release readiness / public acceptance / package readiness / runtime compatibility를 과대 주장하지 않는다.
* 라운드 machine PASS와 independent review / owner seal gate가 분리된다.
* non-Claude independent review + owner seal이 필요한 경우 별도 gate로 닫힌다.

---

## 13. Expected Claim Boundary

이 로드맵의 완료는 다음을 자동으로 의미하지 않는다.

* DVF Core PASS의 실제 달성
* Registry Authority PASS의 실제 달성
* Registry Runtime Compatibility PASS의 실제 달성
* Publish Boundary PASS의 실제 달성
* full runtime equivalence
* full compatibility preservation
* Runtime Payload Consumer Compatibility closure
* Public Text Quality acceptance
* semantic quality acceptance
* release readiness
* deployment readiness
* Workshop readiness
* B42 readiness
* package publication
* package safety
* manual QA
* production validation
* current authority cutover
* live migration execution
* source mutation
* rendered mutation
* Lua bridge mutation
* runtime chunk mutation
* package payload mutation
* stale artifact deletion
* predecessor cleanup
* required-validation manifest physical split
* route runner 구조 변경 승인
* architectural correctness beyond this claim boundary

이번 로드맵의 성공 claim은 다음 하나로 제한한다.

```text
DVF Core / Iris Artifact Registry / Registry Runtime Compatibility / Publish Boundary / Legacy Combined Current Route
claim vocabulary and routing boundary are separated and machine-guarded.
```

Registry Authority closure, Registry Runtime Compatibility closure, Publish Boundary closure, Runtime Payload Consumer Compatibility closure, public text acceptance, release readiness는 각각 별도 로드맵으로 열어야 한다.

---

## 부록 — 보류 / 저자 확정 필요 항목

1. Round identifier 최종 확정
2. `DVF PASS` 처분: current claim 전면 금지 vs legacy alias로만 잔존
3. 5개 claim token 최종 표기
4. claim contract document 경로 / 파일명
5. machine contract JSON 경로 / 파일명
6. guard scan 대상 governance claim surface 목록
7. historical quote / legacy alias / negated claim / forbidden example 예외 규칙
8. live required-validation manifest additive gate 채택 여부
9. additive required-gate 채택 시 stable machine fields 범위
10. 상위 문서 additive 반영 시점
11. top-doc 최종 문안
12. validation depth: `standard` vs `heavy`
13. canonical seal 조건
14. independent review gate 조건
15. owner seal 조건
