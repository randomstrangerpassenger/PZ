# Iris Artifact Registry Authority Canonical Closure / DVF System Stable Development Baseline — Synthesized Roadmap

```text
document_status        = synthesized_final_roadmap_draft
template               = ROADMAP_TEMPLATE.md
round_display_name     = Iris Artifact Registry Authority Canonical Closure
problem_class          = terminal parent problem
maximum_claim          = Registry Authority Closure = canonical_complete
canonical_authority    = owner approval pending
```

## 0. Synthesis Boundary / Pending Owner Decisions

### 공통 채택 항목

두 로드맵이 공통으로 채택한 기준은 다음이다.

```text
DVF System
= facts / decisions / profile / body_plan
  -> rendered 3-3 body

Iris Artifact Registry
= artifact role / lifecycle / authority
  / runtime-package identity pipeline

Legacy Combined DVF Governance Route
= historical polluted governance surface
```

이 roadmap의 목적은 새로운 Registry 시스템 구축이 아니라, Legacy Combined DVF Governance Route 아래 분산되어 있던 authority / guard / seal evidence를 current checkout 기준으로 재수렴하여 독립된 `Registry Authority Closure` readpoint로 봉인하는 것이다.

### 차이 / 보류 항목

다음 항목은 두 안에서 세부 수준이 다르므로 owner-ratification pending으로 둔다.

```text
round_identifier
evidence_root final path
branch selection
vocabulary token final ratification
per-artifact disposition
independent reviewer designation
independent review verdict
owner canonical seal
```

### Phase 구조 판정 필요 항목

두 안은 phase granularity가 다르다.

```text
ChatGPT draft
= 13-phase 상세 lifecycle
  roadmap approval -> plan -> census -> classification -> handoff -> identity chain
  -> freshness -> seal/cutover -> stale guard -> pre-review -> implementation
  -> final validation -> independent closeout / owner seal

Claude draft
= 5-phase lifecycle
  roadmap approval -> roadmap-derived plan -> pre-implementation reviews
  -> implementation WP-1~WP-7 -> final validation / independent review / canonical seal
```

본 종합본은 5개 대단계를 유지하되, Phase 4 구현 내부에 ChatGPT draft의 상세 단계들을 WP-1~WP-7로 배치한다. 이는 phase 수의 임의 절충이 아니라, 두 안의 공통 lifecycle을 보존하면서 상세 검증 항목을 implementation work package로 위치시키는 구조다.

---

## 1. Problem Statement

Legacy Combined DVF Governance Route 아래에서 successor authority chain, artifact guard, required-evidence integrity, seal 관련 산출물은 이미 개별적으로 생성·소비되었다. 그러나 이들은 분산 evidence로 존재할 뿐, Iris Artifact Registry가 소유하는 독립된 axis-qualified `Registry Authority Closure` readpoint로 재수렴되지 않았다.

현재 canonical read는 다음으로 고정되어 있다.

```text
DVF System
= facts / decisions / profile / body_plan
  -> rendered 3-3 body

Iris Artifact Registry
= artifact lifecycle / authority
  / runtime-package identity pipeline

Legacy Combined DVF Governance Route
= historical polluted governance surface
```

핵심 문제는 다음이다.

```text
Iris Artifact Registry의 current authority chain을
독립된 Registry 축으로 재구성·재검증하고,
DVF System이 안정적인 개발 기준선으로 소비할 수 있는
canonical Registry Authority readpoint를 확립해야 한다.
```

현재 닫히지 않은 표면은 다음이다.

```text
artifact role classification
source identity
rendered identity
Lua bridge identity
runtime manifest / chunk identity
package payload identity
required-validation ownership / freshness
candidate-to-current promotion boundary
seal / cutover
stale / predecessor reentry guard
```

이 문제를 닫지 않으면 다음 위험이 남는다.

* fixture / staging / diagnostic / historical artifact를 current 입력으로 오인할 수 있다.
* DVF compiler failure와 Registry identity drift를 구분하기 어렵다.
* rendered output과 runtime/package identity의 연결 기준이 뒤늦게 바뀔 수 있다.
* candidate output과 current artifact가 혼동될 수 있다.
* DVF가 current artifact selector, promotion, seal 책임을 다시 흡수할 수 있다.
* 과거 stored PASS가 current checkout의 fresh evidence처럼 재사용될 수 있다.
* DVF System 본개발이 움직이는 Registry 기준선을 소비하게 될 수 있다.

따라서 이 roadmap은 단순 문서 정리가 아니라, Registry Authority axis를 current checkout 기준으로 inventory → identity binding → freshness validation → seal / cutover contract → stale reentry guard → independent review → owner/canonical seal까지 닫는 terminal parent lifecycle이다.

---

## 2. Current State

### 2.1 Sealed / Accepted State

현재 이미 닫힌 것은 다음이다.

* DVF System / DVF Body Compiler는 3-3 본문 생산만 담당한다.
* Iris Artifact Registry는 DVF System의 내부 하위 구성요소가 아니다.
* Legacy Combined DVF Governance Route PASS는 DVF Body Compiler PASS가 아니다.
* 단독 current `DVF PASS`와 `DVF System PASS`는 금지된다.
* Registry Authority, Registry Runtime Compatibility, Publish Boundary는 서로 대체하지 않는다.
* Registry authority, runtime/package guard, required validation, seal, cutover, stale guard 책임은 DVF System에 재부착될 수 없다.
* current combined manifest는 여러 축을 실행하는 governance aggregator일 수는 있지만, 각 축의 의미 권한을 소유하지 않는다.
* canonical terminology는 `DVF System` / `DVF Body Compiler`로 고정되며, `DVF Core`는 retired predecessor label이다.
* current runtime successor bundle은 `IrisLayer3DataChunks.lua` manifest + `IrisLayer3DataChunks/*.lua` chunk files 단일 bundle로 읽힌다.
* successor chain은 다음 방향으로 봉인되어 있다.

```text
facts
-> decisions
-> compose
-> rendered
-> Lua bridge
-> chunk runtime data
```

### 2.2 Active Limitation

다음 표면들은 선행 evidence가 있으나, 아직 Registry Authority라는 독립 parent claim으로 통합되어 있지 않다.

```text
artifact role classification
source identity
rendered identity
Lua bridge identity
runtime manifest / chunk identity
package payload identity
required-validation ownership / freshness
candidate-to-current promotion boundary
seal / cutover
stale / predecessor reentry guard
```

현재 상태는 “자료 없음”이 아니라 다음에 가깝다.

```text
predecessor evidence exists
but
axis-qualified Registry Authority Closure is not canonical_complete
```

### 2.3 Known Limitations

* required artifact / test denominator는 readpoint별로 상이한 sealed 값들이 존재하며, 어느 것도 현재 checkout의 current denominator로 직접 치환할 수 없다.
* `current_route_required_validations.json`은 여전히 `legacy_combined_governance_route` container이며, 기존 gate들은 이 container 안에서 additive required-validation으로 소비되어 왔다.
* manifest 전면 물리 분해는 본 roadmap의 범위가 아니다.
* stored PASS와 fresh execution evidence는 구분되어야 한다.
* generated staging evidence와 durable required evidence는 구분되어야 한다.
* tracked status는 authority 승격 근거가 아니다.
* ignored status는 삭제 가능성 근거가 아니다.
* owner seal은 independent review를 대체하지 않는다.
* canonical seal은 release readiness나 public readiness를 의미하지 않는다.

### 2.4 Active Dependencies

이 closure의 baseline을 소비할 수 있는 downstream은 다음이다.

```text
DVF System 본개발
Phase 4 Live Migration Execution
MIGV-QA deferred surface
Registry Runtime Compatibility Closure
Publish Boundary Closure
```

단, 이 roadmap은 위 downstream 항목을 실행하거나 닫지 않는다.

### 2.5 Current Validation Confidence

현재 validation confidence는 부분적으로 높다.

* DVF / Registry / Publish 경계는 구조적으로 분리되어 있다.
* current route가 legacy combined governance route라는 사실은 이미 인정되어 있다.
* successor authority chain, required-evidence integrity, stale guard, seal 관련 산출물은 존재한다.
* required-validation manifest 기반 guard 구조도 이미 존재한다.

하지만 Registry Authority Closure 관점의 confidence는 아직 terminal하지 않다.

* 현재 checkout 기준 전체 artifact role census가 Registry axis로 다시 묶였는지 확정되지 않았다.
* stored PASS와 fresh execution evidence가 최종 closeout에서 완전히 분리됐는지 확인이 필요하다.
* candidate-to-current promotion contract와 seal/cutover contract가 Registry Authority PASS의 일부로 단일하게 봉인되어야 한다.
* stale / predecessor reentry guard가 current source/runtime/package authority 전체에 대해 fail-closed인지 다시 확인해야 한다.

---

## 3. Desired Outcome

완료 후 상태는 다음이어야 한다.

```text
Registry Authority Closure
= canonical_complete

Registry Authority PASS
= artifact role classification complete
+ single current identity chain
+ required-validation ownership/freshness complete
+ seal / cutover contract complete
+ stale / predecessor reentry guard complete
```

완료 후 canonical read는 다음으로 고정된다.

```text
DVF System
= facts / decisions / profile / body_plan
  -> rendered 3-3 body

DVF input
= contract-valid facts / decisions / profile / body_plan

DVF output
= rendered 3-3 body
+ compiler trace / receipt

DVF output before Registry adoption
= candidate artifact

Registry current artifact
= Registry Authority Closure를 통과해 seal된 current artifact
```

이 결과는 다음 개선을 가져야 한다.

* DVF 본개발 중 current 입력 identity가 움직이는 표적이 되지 않는다.
* DVF compiler failure와 Registry identity drift를 분리해서 판정할 수 있다.
* candidate artifact와 current artifact의 경계가 명확해진다.
* rendered / bridge / runtime / package identity pipeline이 단일 current chain으로 읽힌다.
* stored PASS 재사용이 차단되고, current checkout fresh evidence만 completion 근거가 된다.
* DVF System이 Registry selector / promoter / sealer 책임을 다시 흡수하지 않는다.
* 종결 후 예정된 successor Registry Authority round가 남지 않는다.
* 재개방은 새로운 evidence에 근거한 correction으로만 허용된다.

---

## 4. Constraints

### 4.1 Philosophy / Architecture Constraints

* `Philosophy.md`가 최상위 기준이다.
* Pulse 생태계는 Hub & Spoke + SPI 구조를 유지한다.
* 각 모듈은 자기 역할을 고수하고 타 모듈 역할을 침범하지 않는다.
* Iris 런타임은 sealed artifact를 표시하는 계층이며, 런타임에서 source 검증이나 설명 재생성을 수행하지 않는다.
* Registry Authority Closure는 DVF System 내부 구현 책임이 아니다.
* DVF System은 Registry의 하위 writer나 authority selector가 아니다.
* Runtime / Build-time separation을 보존한다.
* FAIL-LOUD 원칙을 보존한다.

### 4.2 Authority Constraints

DVF System responsibility ceiling은 다음 경로로 끝난다.

```text
facts / decisions / profile / body_plan
-> rendered 3-3 body
```

Registry responsibility는 다음 경로에 한정한다.

```text
artifact role / identity classification
+ candidate-to-current promotion
+ required validation
+ seal / cutover
+ stale / predecessor reentry prevention
```

Registry Authority PASS는 다음을 의미하지 않는다.

```text
DVF Body Compiler PASS
Registry Runtime Compatibility PASS
Publish Boundary PASS
runtime consumer behavior guarantee
package readiness
public text acceptance
release / Workshop readiness
manual QA
```

### 4.3 Mutation Constraints

기본 roadmap 단계에서는 다음 mutation을 열지 않는다.

* source facts / decisions mutation
* source overlay support mutation
* rendered body content mutation
* Lua bridge live export mutation
* runtime chunk replacement
* package payload mutation
* current route runner rewrite
* manifest physical split
* historical artifact bulk rename
* machine schema breaking rename

허용되는 생성 범위는 다음으로 제한한다.

```text
governance docs
inventory reports
validation tooling
focused tests
required gate adoption records
seal records
staging evidence
```

### 4.4 Validation Constraints

* stored PASS는 fresh evidence가 아니다.
* generated staging evidence는 durable required evidence가 아니다.
* final validation은 최종 변경 이후 다시 실행해야 한다.
* final artifact와 validation 결과는 hash-bound 되어야 한다.
* independent review와 owner/canonical seal은 서로 대체하지 않는다.
* current checkout 사실은 live recensus로만 확정한다.
* count-equality는 authority substitution 근거가 아니다.

### 4.5 Review / Seal Constraints

* Claude roadmap draft는 co-draft input이므로, 그 파생 plan에 대한 Claude review는 independent closeout review를 충족하지 못한다.
* canonical closure는 non-Claude independent review PASS와 owner seal을 요구한다.
* owner-reserved decision은 draft나 plan이 선점하지 않는다.

---

## 5. Non-Goals

이 roadmap은 다음을 하지 않는다.

* DVF Body Compiler 본문 생성 로직 구현
* `body_plan` semantics 개발
* rendered body 문장 품질 개선
* 입력 facts의 의미·사실성 재판정
* Registry Runtime Compatibility Closure
* runtime consumer 동작 검증
* Publish Boundary Closure
* public text quality acceptance
* semantic quality acceptance
* package publication
* release / Workshop readiness
* B42 readiness
* deployment readiness
* manual in-game QA
* required-validation manifest 전면 물리 분해
* current route runner 전면 재작성
* historical artifact 대량 rename
* machine schema breaking rename
* source / rendered / runtime / package content mutation
* Phase 4 Live Migration Execution 실행
* 닫힌 readpoint의 재개방
* ACQ_DOMINANT / FUNCTION_NARROW publish authority disposition
* Layer 4 detector seal round
* Registry 문제를 명분으로 한 DVF 책임 재결합

특히 이 roadmap은 `Registry Authority PASS`를 닫는 것이지, `DVF Body Compiler PASS`, `Registry Runtime Compatibility PASS`, `Publish Boundary PASS`를 함께 닫는 roadmap이 아니다.

---

## 6. Proposed Approach

### Direction

전략은 새 Registry 시스템을 만드는 것이 아니라, 기존 sealed authority / guard / seal evidence를 read-only predecessor input으로 소비하고, current checkout 기준 recensus를 통해 단일 Registry Authority readpoint를 봉인하는 것이다.

### Sequencing

전체 lifecycle은 다음 순서를 따른다.

```text
Roadmap
-> Roadmap approval
-> Roadmap-derived implementation plan
-> Pre-implementation reviews
-> Blocker resolution
-> Implementation
-> Fresh current-checkout validation
-> Independent closeout review
-> Owner / canonical seal
-> Registry Authority Closure canonical_complete
```

### Decomposition

구현은 다음 7개 Work Package로 분해한다.

```text
WP-1 DVF / Registry Handoff Contract
WP-2 Authority Surface Inventory / Artifact Role Classification
WP-3 Single Current Identity Chain Binding
WP-4 Required-Validation Ownership / Freshness Reseal
WP-5 Seal / Cutover Contract
WP-6 Stale / Predecessor Reentry Guard
WP-7 Registry Authority Claim Contract
```

### Risk Reduction

* 과거 fixed scan universe나 stored inventory를 현재 universe로 대신 쓰지 않는다.
* stored PASS는 predecessor trace로만 소비한다.
* 완료 주장은 최종 변경 이후 fresh rerun evidence로만 한다.
* Registry-owned defect만 같은 문제 안에서 correction한다.
* DVF-owned / Runtime Compatibility-owned / Publish-owned defect는 fail-closed로 기록하고 대리 수정하지 않는다.
* protected surface mutation은 0을 유지한다.
* candidate output은 Registry adoption 전 current artifact로 읽지 않는다.
* stale / predecessor artifact는 삭제보다 current reentry 금지를 우선한다.

### Validation Strategy

Validation은 heavy로 수행한다.

최종 검증은 반드시 최종 변경 이후 전량 재실행하고, final artifact와 validation 결과를 hash로 결속한다. independent closeout review는 non-Claude reviewer가 수행하며, owner seal은 independent review를 대체하지 않는다.

---

## 7. Authority / Surface Impact

### Authority Surface

영향 있음.

이 roadmap은 `Registry Authority Closure` readpoint를 신설하고, 다음 의미 권한을 Iris Artifact Registry 축으로 봉인한다.

```text
artifact role classification
single current identity chain
required-validation ownership / freshness
candidate-to-current promotion
seal / cutover
stale / predecessor reentry guard
```

허용되는 final authority claim은 다음이다.

```text
Registry Authority Closure
= canonical_complete

Registry Authority PASS
= artifact role classification complete
+ single current identity chain
+ required-validation ownership/freshness complete
+ seal / cutover contract complete
+ stale / predecessor reentry guard complete
```

금지되는 authority claim은 다음이다.

```text
Registry Authority PASS
!= DVF Body Compiler PASS
!= Registry Runtime Compatibility PASS
!= Publish Boundary PASS
!= release readiness
```

### Runtime Behavior Surface

없음.

이 roadmap은 runtime Lua 동작, chunk 소비 방식, public require contract를 변경하지 않는다. runtime manifest / chunk identity는 기록·봉인 대상이지 mutation 대상이 아니다.

### Compatibility Surface

없음.

Runtime consumer compatibility 판정은 `Registry Runtime Compatibility` 별도 축이며 본 roadmap에서 닫지 않는다.

### Sealed Artifact Surface

영향 있음.

신규 sealed 산출물은 additive-only로 생성한다.

```text
Registry Authority roadmap
Registry Authority plan
review packets
contract docs
machine reports
validation reports
seal record
closure record
```

DECISIONS.md 반영은 owner의 additive append로만 수행한다. 기존 sealed body는 immutable로 취급한다.

### Public-Facing Output Surface

없음.

Browser / Wiki / Tooltip 노출, public text, package 산출물, release note, Workshop readiness는 변경하거나 닫지 않는다.

---

## 8. Phases

## Phase 1 — Registry Authority Roadmap Approval

Goal:

Registry Authority Closure를 terminal parent problem으로 수행하기 위한 roadmap을 승인한다.

Primary Changes:

* problem definition 고정
* scope / non-goals 고정
* phase dependency 고정
* protected surface 고정
* validation ceiling 고정
* final completion claim 고정
* owner-reserved decision 목록 보존

Expected Risks:

* roadmap이 implementation plan 수준의 detail을 선점할 수 있다.
* Registry Authority Closure가 DVF Body Compiler 구현 prerequisite처럼 오독될 수 있다.
* Registry Runtime Compatibility / Publish Boundary가 혼입될 수 있다.
* owner-reserved 항목을 draft가 선점할 수 있다.

Expected Validation:

* ROADMAP_TEMPLATE 13-section structure 충족
* claim boundary 명시
* non-goals 명시
* mutation ceiling 명시
* final completion claim이 `Registry Authority Closure = canonical_complete`로 제한됨
* problem definition의 필수 해결 범위와 1:1 대조

Expected Deliverables:

```text
docs/dvf_3_3_registry_authority_canonical_closure_roadmap.md
roadmap_approval_record
roadmap_scope_boundary_record
owner_reserved_decision_register
```

Exit Criteria:

* roadmap 승인 완료
* unresolved roadmap decision 0 또는 owner-reserved pending으로 명시
* Registry / DVF / Runtime Compatibility / Publish Boundary 축 구분 완료
* successor Registry Authority round로 넘기는 항목 없음

---

## Phase 2 — Roadmap-Derived Implementation Plan

Goal:

승인된 roadmap에서만 implementation plan을 파생한다.

Primary Changes:

* concrete artifact path 정의
* inventory method 정의
* identity binding method 정의
* required-validation recensus method 정의
* seal / cutover implementation method 정의
* stale reentry guard method 정의
* test matrix 정의
* protected-surface mutation policy 정의
* evidence root 정의
* closeout artifact 정의
* independent review input 정의

Expected Risks:

* implementation plan이 roadmap에 없는 claim을 추가할 수 있다.
* fixed scan universe 재사용 설계가 혼입될 수 있다.
* artifact path가 과거 staging evidence를 current authority처럼 취급할 수 있다.
* self-reference validation cycle이 설계될 수 있다.
* protected source/rendered/runtime/package surface mutation 범위가 불명확할 수 있다.

Expected Validation:

* roadmap-to-plan traceability matrix
* plan-only claim additions 0
* protected surface mutation policy present
* evidence root present
* closeout artifact schema present
* artifact fingerprint 고정

Expected Deliverables:

```text
docs/dvf_3_3_registry_authority_canonical_closure_plan.md
registry_authority_plan_traceability_matrix.json
registry_authority_protected_surface_policy.md
registry_authority_evidence_root_manifest.json
implementation_plan_fingerprint_report.json
```

Exit Criteria:

* implementation plan 승인 완료
* roadmap에 없는 responsibility / claim 0
* protected surface mutation ceiling 명시
* implementation blocker 0 또는 fail-closed disposition 완료
* Phase 3 review 제출 가능 상태

---

## Phase 3 — Pre-Implementation Reviews / Blocker-Zero Gate

Goal:

구현 전 독립 검토를 통해 blocker를 0으로 만든다.

Required Reviews:

```text
Responsibility Boundary Review
Authority / Evidence Integrity Review
Adversarial / Failure-Mode Review
```

Primary Changes:

검토 대상은 다음을 포함한다.

```text
DVF responsibility reabsorption
Runtime Compatibility contamination
Publish Boundary contamination
stale artifact reentry
dual authority
stored PASS reuse
dirty / untracked / ignored required artifact
manifest omission
candidate/current confusion
implicit fallback
fixed scan universe omission
self-reference validation cycle
```

Expected Risks:

* review가 형식적으로 PASS만 생산할 수 있다.
* self-generated PASS가 independent review로 오독될 수 있다.
* owner seal이 independent review를 대체할 수 있다.
* review 간 판정 불일치로 수렴이 지연될 수 있다.
* Minor disposition이 owner decision 없이 남을 수 있다.

Expected Validation:

```text
responsibility_boundary_review_status=PASS
authority_evidence_integrity_review_status=PASS
adversarial_failure_mode_review_status=PASS
pre_implementation_blocker_count=0
self_generated_pass_as_independent_review_count=0
Critical_count=0
Important_count=0
Minor_disposition=owner_resolved_or_accepted
```

Expected Deliverables:

```text
phase3/responsibility_boundary_review.md
phase3/authority_evidence_integrity_review.md
phase3/adversarial_failure_mode_review.md
phase3/consolidated_review.md
phase3/carry_forward_findings_table.json
phase3/pre_implementation_blocker_resolution_report.json
phase3/blocker_zero_record.json
```

Exit Criteria:

* pre-implementation blocker 0
* Critical / Important 0
* Minor owner disposition 완료
* independent review eligibility 확인
* implementation 착수 가능 상태

---

## Phase 4 — Implementation / Work Package Execution

Goal:

review-approved implementation plan 범위만 구현한다.

Primary Changes:

구현 범위는 다음으로 제한한다.

```text
Registry Authority docs
artifact role inventory tooling
identity chain validation tooling
required-validation freshness tooling
seal / cutover contract tooling
stale / predecessor reentry guard tooling
focused tests
evidence materialization
optional additive required-validation gate
```

Implementation은 다음 WP로 수행한다.

### WP-1 — DVF / Registry Handoff Contract

Goal:

DVF System이 소비할 입력과 Registry가 채택할 산출물의 경계를 고정한다.

Contract:

```text
DVF input
= contract-valid facts / decisions / profile / body_plan

DVF output
= rendered 3-3 body
+ compiler trace / receipt

DVF output before Registry adoption
= candidate artifact

Registry adoption
= candidate -> current promotion
  only through Registry Authority contract
```

Expected Validation:

```text
dvf_current_artifact_selector_claim_count=0
registry_body_generation_claim_count=0
candidate_direct_current_consumption_count=0
compiler_trace_misread_as_seal_count=0
```

Expected Deliverables:

```text
docs/dvf_registry_handoff_contract.md
phase4/wp1_dvf_registry_handoff_validation_report.json
phase4/wp1_candidate_artifact_consumption_guard_report.json
```

### WP-2 — Authority Surface Inventory / Artifact Role Classification

Goal:

current checkout 기준 Registry Authority universe를 재계수하고 모든 Registry-relevant artifact를 명시적 role로 분류한다.

Roles:

```text
current
candidate
staging
fixture
historical
diagnostic
quarantine
forbidden-current-looking
```

Each role record:

```text
path
role
authority_axis
hash
cardinality
producer
consumer
predecessor_relation
current_reentry_allowed
package_reentry_allowed
required_validation_status
```

Expected Validation:

```text
artifact_surface_census_status=PASS
artifact_role_classification_complete=true
ambiguous_role_count=0
unclassified_role_count=0
forbidden_current_looking_violation_count=0
candidate_current_confusion_count=0
stored_pass_reused_as_fresh_evidence=false
```

Expected Deliverables:

```text
phase4/wp2_current_checkout_artifact_surface_census.json
phase4/wp2_required_validation_manifest_recensus.json
phase4/wp2_required_artifact_vcs_surface_report.json
phase4/wp2_artifact_role_classification_ledger.jsonl
phase4/wp2_artifact_role_classification_summary.md
phase4/wp2_forbidden_current_looking_surface_report.json
phase4/wp2_candidate_current_boundary_report.json
```

### WP-3 — Single Current Identity Chain Binding

Goal:

Registry current artifact identity chain을 단일하게 봉인한다.

Identity Chain:

```text
current source identity
-> rendered artifact identity
-> Lua bridge identity
-> runtime manifest identity
-> runtime chunk identity
-> package payload identity
```

Expected Validation:

```text
single_current_identity_chain=true
dual_authority_count=0
ambiguous_current_authority_count=0
source_rendered_identity_match=true
rendered_bridge_identity_match=true
bridge_runtime_identity_match=true
runtime_package_identity_match=true
```

Expected Deliverables:

```text
phase4/wp3_current_identity_chain_manifest.json
phase4/wp3_current_identity_chain_hash_report.json
phase4/wp3_dual_authority_scan_report.json
phase4/wp3_predecessor_relation_map.json
```

### WP-4 — Required-Validation Ownership / Freshness Reseal

Goal:

Registry Authority PASS를 지탱하는 required-validation ownership과 freshness를 current checkout 기준으로 다시 봉인한다.

Primary Changes:

* live required-validation manifest recensus
* required artifact denominator rebinding
* required test denominator rebinding
* required artifact existence vs semantic validation separation
* durable required evidence vs generated staging evidence separation
* stored PASS vs fresh execution evidence separation
* final rerun requirement 정의

Expected Validation:

```text
required_manifest_current_checkout_bound=true
required_artifact_denominator_matches_manifest=true
required_test_denominator_matches_manifest=true
stored_pass_reuse_count=0
generated_staging_as_durable_evidence_count=0
required_evidence_freshness_status=PASS
```

Expected Deliverables:

```text
phase4/wp4_required_validation_ownership_report.json
phase4/wp4_required_evidence_freshness_report.json
phase4/wp4_durable_vs_generated_evidence_report.json
phase4/wp4_fresh_execution_manifest.json
```

### WP-5 — Seal / Cutover Contract

Goal:

candidate artifact가 current artifact로 승격되는 조건과 seal / cutover contract를 고정한다.

Primary Changes:

* candidate-to-current promotion 조건 정의
* seal identity 정의
* seal receipt schema 정의
* cutover precondition 정의
* cutover postcondition 정의
* rollback / historical preservation / predecessor trace rule 정의
* partial cutover 금지
* dual-current 금지

Expected Validation:

```text
candidate_promotion_contract_complete=true
seal_identity_defined=true
seal_receipt_schema_valid=true
partial_cutover_allowed=false
dual_current_after_cutover_count=0
rollback_current_reentry_count=0
```

Expected Deliverables:

```text
docs/registry_authority_seal_cutover_contract.md
phase4/wp5_candidate_to_current_promotion_contract.json
phase4/wp5_seal_receipt_schema.json
phase4/wp5_cutover_precondition_report.json
phase4/wp5_cutover_postcondition_report.json
phase4/wp5_rollback_reentry_guard_report.json
```

### WP-6 — Stale / Predecessor Reentry Guard

Goal:

historical / diagnostic / fixture / stale / predecessor artifacts가 current source/runtime/package authority로 재진입하지 못하게 한다.

Guard Targets:

```text
historical fixture
diagnostic output
old monolith
stale bridge
predecessor runtime chunks
rollback snapshot
current-looking stale path
package fallback
```

Guard Surface:

```text
current source authority
current rendered authority
current Lua bridge authority
current runtime authority
current package authority
required manifest path
docs current-authority claim
```

Expected Validation:

```text
stale_source_reentry_violation_count=0
stale_runtime_reentry_violation_count=0
stale_package_reentry_violation_count=0
current_looking_stale_path_count=0
package_fallback_forbidden_hit_count=0
docs_current_authority_overclaim_count=0
```

Expected Deliverables:

```text
docs/stale_predecessor_reentry_guard_policy.md
phase4/wp6_stale_current_looking_path_scan_report.json
phase4/wp6_package_fallback_forbidden_scan_report.json
phase4/wp6_required_manifest_reentry_report.json
phase4/wp6_docs_current_authority_claim_scan_report.json
```

### WP-7 — Registry Authority Claim Contract

Goal:

`Registry Authority PASS`의 허용 의미와 금지 의미를 고정한다.

Allowed Claim:

```text
Registry Authority PASS
= artifact role classification complete
+ single current identity chain
+ required-validation ownership/freshness complete
+ seal / cutover contract complete
+ stale / predecessor reentry guard complete
```

Forbidden Claim:

```text
Registry PASS
DVF PASS
DVF System PASS
Legacy Combined DVF Governance Route PASS == Registry Authority PASS
Registry Authority PASS == Runtime Compatibility PASS
Registry Authority PASS == Publish Boundary PASS
Registry Authority Closure == release readiness
```

Expected Validation:

```text
registry_authority_claim_contract_complete=true
forbidden_claim_hit_count=0
axis_qualified_completion_vocabulary_enforced=true
```

Expected Deliverables:

```text
docs/registry_authority_claim_contract.md
phase4/wp7_registry_authority_claim_scan_report.json
phase4/wp7_required_validation_additive_gate_record.json
```

Phase 4 Expected Risks:

* census 중 forbidden-current-looking artifact가 발견될 수 있다.
* dual authority가 실증될 수 있다.
* live manifest denominator와 recensus 결과가 불일치할 수 있다.
* protected surface mutation이 발생할 수 있다.
* 구현 중 Registry-owned 문제와 non-Registry 문제를 섞을 수 있다.
* current route runner rewrite 유혹이 생길 수 있다.
* tooling이 current 선택 / 승격 판단을 DVF-style 책임으로 흡수할 수 있다.

Phase 4 Expected Validation:

```text
implementation_scope_matches_review_approved_plan=true
non_registry_blocker_bypassed=false
protected_source_mutation_count=0
protected_rendered_mutation_count=0
protected_lua_bridge_mutation_count=0
protected_runtime_mutation_count=0
protected_package_mutation_count=0
registry_blocker_count=0
```

Phase 4 Expected Deliverables:

```text
phase4/implementation_scope_report.json
phase4/protected_surface_no_mutation_report.json
phase4/registry_authority_tooling_validation_report.json
phase4/focused_test_result_report.json
phase4/wp_completion_summary.md
```

Phase 4 Exit Criteria:

* WP-1~WP-7 완료
* 구현 범위가 review-approved plan과 일치
* protected surface mutation 0
* Registry-owned defect correction 완료
* non-Registry blocker 발견 시 fail-closed
* Registry blocker 0

---

## Phase 5 — Final Current-Checkout Validation / Independent Closeout Review / Owner Canonical Seal

Goal:

모든 변경 이후 validation을 처음부터 다시 실행하고, independent review와 owner/canonical seal로 종결한다.

Primary Changes:

* final census rerun
* final identity chain validation
* final required-validation validation
* final stale reentry guard validation
* final protected surface no-mutation validation
* final current-route validation
* final Lua syntax validation, 필요한 경우
* final command matrix binding
* final artifact hash-bound independent review
* reviewer eligibility 기록
* owner seal input manifest 작성
* owner/canonical seal record 작성
* final machine/governance state 작성
* reopening rule 작성

Expected Risks:

* 이전 PASS를 재사용할 수 있다.
* final artifact hash와 validation result가 결속되지 않을 수 있다.
* validation 순서가 closeout claim보다 뒤섞일 수 있다.
* independent review가 self-generated PASS로 대체될 수 있다.
* owner seal이 review를 대체할 수 있다.
* canonical seal이 release readiness처럼 오독될 수 있다.
* successor Registry Authority round가 암묵적으로 남을 수 있다.

Expected Validation:

```text
final_validation_rerun_after_last_change=true
stored_pass_reused_for_final_completion=false
final_artifact_hash_bound=true
final_validation_result_hash_bound=true
current_route_validation_status=PASS
protected_surface_mutation_count=0
registry_blocker_count=0
independent_closeout_review_status=PASS
reviewed_artifact_hash_coverage=complete
owner_seal_status=PASS
canonical_seal_status=PASS
canonical_seal_allowed=true
successor_registry_authority_round_required=false
```

Expected Deliverables:

```text
phase5/final_current_checkout_validation_report.json
phase5/final_command_matrix_report.json
phase5/final_artifact_hash_manifest.json
phase5/final_validation_hash_binding_report.json
phase5/final_registry_blocker_report.json
phase5/independent_closeout_review.md
phase5/independent_review_artifact_hash_report.json
phase5/owner_seal_input_manifest.json
phase5/owner_canonical_seal_record.json
phase5/final_registry_authority_closure_report.json
docs/dvf_3_3_registry_authority_canonical_closure_closeout.md
```

Exit Criteria:

```text
Registry Authority Closure
= canonical_complete

required Registry item
= unresolved 0
+ deferred 0
+ pending 0
+ blocker 0

successor Registry Authority round
= not required
```

---

## 9. Validation Expectations

### Expected Validation Depth

Heavy.

이 roadmap은 단순 문서 정리나 lightweight governance round가 아니다. current checkout 기준 authority surface, identity chain, required-validation freshness, seal/cutover, stale reentry guard를 모두 다루므로 heavy validation이 필요하다.

### Expected Validation Areas

Required:

```text
authority
artifact role classification
identity chain determinism
required-validation freshness
VCS preservation
stale / predecessor reentry
candidate/current boundary
seal / cutover contract
protected surface no-mutation
claim vocabulary boundary
independent review hash binding
owner/canonical seal validation
```

Conditional:

```text
current-route required-validation rerun
Lua syntax validation
package forbidden-surface scan
docs current-authority overclaim scan
current-route regression
determinism rerun for census / binding tooling
```

### Known Validation Limits

이 roadmap에서는 다음 validation을 기대하지 않는다.

* runtime consumer behavior validation
* multiplayer validation
* long-session runtime validation
* manual in-game QA
* release readiness validation
* Workshop readiness validation
* B42 readiness validation
* deployment readiness validation
* public text acceptance validation
* semantic quality acceptance validation
* package publication validation
* external ecosystem compatibility sweep
* full historical byte reproducibility
* Registry Runtime Compatibility closure
* Publish Boundary closure

---

## 10. Risk Assessment

### High Risk

* `Registry Authority PASS`가 DVF Body Compiler PASS, Registry Runtime Compatibility PASS, Publish Boundary PASS와 섞이는 위험
* candidate artifact가 current artifact처럼 소비되는 위험
* stored PASS가 fresh evidence로 재사용되는 위험
* stale / predecessor artifact가 current source/runtime/package authority로 재진입하는 위험
* required-validation manifest가 stale evidence를 durable required evidence로 소비하는 위험
* dual current identity chain이 생기는 위험
* fixed scan universe / stored inventory 재사용으로 census가 누락되는 위험
* forbidden-current-looking artifact가 current identity chain을 오염시키는 위험
* live manifest denominator와 recensus 결과가 불일치하는 위험
* owner seal / independent review / machine PASS가 서로 대체되는 위험
* closeout이 release readiness처럼 오독되는 위험
* tooling이 current 선택 / 승격 / seal 판단을 DVF 쪽 책임으로 흡수하는 위험

### Medium Risk

* scan universe가 current checkout 전체를 반영하지 못하는 위험
* dirty / untracked / ignored required artifact를 놓치는 위험
* package route에서 old monolith / stale bridge fallback을 놓치는 위험
* docs claim scan에서 quoted prior claim과 actual current-authority overclaim을 구분하지 못하는 위험
* registry-owned blocker와 non-registry blocker가 섞이는 위험
* final validation 이후 추가 변경이 발생하는 위험
* self-reference validation cycle이 생기는 위험
* review 수렴 지연
* non-Claude independent reviewer 확보 지연
* evidence root / round id 미비준 상태의 선행 구현

### Low Risk

* 문서명 / artifact명 drift
* evidence root naming inconsistency
* report schema field 누락
* positive / negative fixture coverage 부족
* historical trace 표현이 과도하게 길어지는 문제
* retired label `DVF Core` 혼입
* hash 표기 정규화 불일치
* ROADMAP / docs sync 지연

---

## 11. Rollback Strategy

Rollback은 destructive deletion이 아니라 governance-scoped containment로 수행한다.

1. Registry Authority Closure가 seal 전 실패하면, 이 round의 additive required-validation entries만 제거하거나 supersede한다.
2. 이 round에서 생성한 scanner / validator / focused test는 제거 또는 supersede한다.
3. 이 round의 docs는 삭제보다 correction / supersession을 우선한다.
4. source facts / decisions, rendered output, Lua bridge, runtime chunks, package payload는 rollback 대상이 되지 않아야 한다. 애초에 mutation을 열지 않았어야 한다.
5. gate 채택 전 모든 산출물은 staging evidence이며, 결함 발견 시 quarantine role로 격리하고 live manifest 미채택 상태를 유지한다.
6. gate 채택 후 silent rollback을 금지한다. 결함은 새 evidence 기반 correction으로만 처리한다.
7. top-doc이나 governance docs가 수정됐다면 pre-edit hash를 기준으로 되돌리되, 이미 DECISIONS.md에 append된 sealed trace는 삭제하지 않고 correction entry로 supersede한다.
8. stale / predecessor artifact는 삭제하지 않는다. current reentry 금지만 유지한다.
9. rollback 이후에도 `Registry Authority Closure`가 실패했다는 뜻이지, Registry 책임이 DVF System으로 되돌아간다는 뜻은 아니다.
10. rollback 후 재개방은 미완료 successor가 아니라 새로운 evidence에 근거한 correction으로만 허용한다.

Fail-closed condition:

```text
protected surface pre/post mutation count > 0
non-Registry-owned blocker found
dual-current state detected
partial cutover state detected
required evidence freshness violation
stored PASS reused as final evidence
stale predecessor artifact promoted
```

Rollback success condition:

```text
protected source/rendered/Lua/runtime/package mutation = 0
current route restored or superseded cleanly
no dual current authority introduced
no stale predecessor artifact promoted
failure state documented
Registry responsibility not reabsorbed by DVF System
```

---

## 12. Success Criteria

이 roadmap은 다음 조건이 모두 충족되어야 성공이다.

### Procedure Success

* Registry Authority Roadmap 승인
* roadmap-derived implementation plan 승인
* Responsibility Boundary Review 완료
* Authority / Evidence Integrity Review 완료
* Adversarial / Failure-Mode Review 완료
* pre-implementation blocker 0
* Critical / Important 0
* Minor owner disposition 완료

### Implementation Success

* current checkout authority surface census 완료
* 모든 Registry-relevant artifact role 분류 완료
* ambiguous / unclassified role 0
* forbidden-current-looking violation 0
* single current identity chain 봉인
* 각 current artifact path / role / hash / cardinality 기록
* predecessor relation 기록
* dual authority 0
* required artifact/test denominator가 current manifest와 일치
* required evidence freshness PASS
* stored PASS 재사용 0
* generated staging evidence의 durable required evidence 오독 0
* DVF / Registry handoff contract 고정
* candidate-to-current promotion contract 고정
* seal / cutover contract 고정
* stale / predecessor reentry violation 0
* protected surface mutation 0
* Registry blocker 0

### Closeout Success

* 최종 변경 이후 full validation 재실행 PASS
* final artifact / validation hash binding 완료
* independent closeout review PASS
* reviewed artifact hash coverage complete
* owner/canonical seal PASS
* unresolved Registry required item 0
* deferred Registry required item 0
* pending owner decision 0
* Registry blocker 0
* successor Registry Authority round not required

최종 상태:

```text
Registry Authority Closure
= canonical_complete

Registry Authority PASS
= single current identity chain
+ required-validation freshness
+ seal / cutover
+ stale / predecessor reentry guard
```

---

## 13. Expected Claim Boundary

이 roadmap이 성공해도 자동으로 의미하지 않는 것:

```text
DVF Body Compiler PASS
DVF System Body Compiler PASS
input facts factual approval
Registry Runtime Compatibility PASS
Runtime Payload Consumer Compatibility closure
runtime consumer behavior guarantee
Publish Boundary PASS
public text acceptance
semantic quality acceptance
package publication
package readiness
release readiness
Workshop readiness
B42 readiness
deployment readiness
manual in-game QA
full runtime equivalence
full compatibility preservation
full historical byte reproducibility
production validation
architectural correctness beyond validated scope
```

허용되는 최종 claim:

```text
Registry Authority Closure
= canonical_complete

Registry Authority PASS
= artifact role classification complete
+ single current identity chain
+ required-validation ownership/freshness complete
+ seal / cutover contract complete
+ stale / predecessor reentry guard complete
```

금지되는 축약 claim:

```text
Registry PASS
DVF PASS
DVF System PASS
Legacy Combined DVF Governance Route PASS == Registry Authority PASS
Registry Authority PASS == Runtime Compatibility PASS
Registry Authority PASS == Publish Boundary PASS
Registry Authority Closure == release readiness
```

최종 canonical read:

```text
DVF System
= facts / decisions / profile / body_plan
  -> rendered 3-3 body

Iris Artifact Registry
= artifact role / lifecycle / authority
  / runtime-package identity pipeline

Registry Authority PASS
= single current identity chain
+ required-validation freshness
+ seal / cutover
+ stale / predecessor reentry guard

Registry Authority PASS
!= DVF Body Compiler PASS
!= Registry Runtime Compatibility PASS
!= Publish Boundary PASS

DVF output
= Registry adoption 전 candidate artifact

Registry current artifact
= Registry Authority Closure를 통과해
  seal된 current artifact
```

종결 후 재개방은 다음 증거가 새로 발생한 경우에만 별도 correction으로 허용한다.

```text
new authority drift
current identity chain mismatch
required artifact omission
required evidence freshness violation
seal / cutover error
stale / predecessor artifact reentry
new artifact class introduction
authority contract explicit change
```

재개방은 기존 문제의 미완료 successor가 아니라, 새로운 증거에 근거한 correction이어야 한다.
