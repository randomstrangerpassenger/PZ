# Implementation Plan

> 계획명: Iris DVF 3-3 — Korean Prose Naturalization / Public Text Rewrite Closure

> 상태: owner-directed `aa49e8f9` four-plan synchronized implementation plan; synchronization-only revision requires no additional plan-level review; implementation entry waits for tracked plan-set materialization, G1 Clean-Checkout PASS, G2 Food successor closeout, G3 Registry adoption and G4 Publish foundation readiness
>
> 기준 로드맵: 사용자 제공 `Iris DVF 3-3 — Korean Prose Naturalization / Public Text Rewrite Closure Roadmap`
>
> 동기화 대상: `docs/iris_publish_boundary_public_text_quality_acceptance_policy_closure_plan.md`
>
> 교차 계획 계약: `dvf3_3_korean_naturalization__publish_boundary_sync_v1`
>
> 상류 동기화 대상: `docs/dvf_3_3_food_semantic_facts_authority_reconstruction_implementation_plan.md`
>
> 상류 교차 계획 계약: `dvf3_3_food_semantic_facts_authority__naturalization_phase2_sync_v1`
>
> 로드맵 입력 관찰값: `C:\Users\MW\.codex\attachments\91b61f60-9f67-4407-b32f-4952747614ae\pasted-text.txt`, SHA-256 `C0C4838352910F8CACBCEDFCA8B74912D544D4F2EBC1D8D96F5CD34860EB3D1D`
>
> 계획 검토 피드백: `C:\Users\MW\.codex\attachments\245e56e9-90fb-4f85-9b76-6ec568de0a4f\pasted-text.txt`, SHA-256 `DEE1B7D3368936E88FFFA2BC2DD2B5AFDEAD1A55C8DF749DB387959C256D989F`
>
> Cycle 2 계획 검토 피드백: `C:\Users\MW\.codex\attachments\800664bb-cbe3-4b88-885c-d703af54a644\pasted-text.txt`, SHA-256 `278DAED986A32CC8964B0CFD9C786AE015F8E6FBCAAC879A32EC2FEA30098848`
>
> 역사적 코드 조사 기준점: branch `main`, HEAD `129c6c124ffa5a6b671041c6ab86675c660fb494`
>
> 공통 실행 ancestry/readpoint: `aa49e8f9fce19955a374b45d0744b1418a45ac9e`
>
> 계획 검토 판정 반영: Cycle 1의 Critical `2`, Important `6`, Minor `6`과 Cycle 2 종합 판정 `WARN`의 Open Important `1`, Minor `6`을 finding crosswalk, canonical terminal sequence 및 terminal predicate로 해소한다.
>
> 주의: 위 hash, row count, profile count, quality count는 계획 작성 시점의 관찰값이다. 실행 권한이나 봉인된 baseline을 뜻하지 않으며 Phase 0에서 live checkout을 다시 측정한다. 이번 coordination-only 동기화는 기존 검토 finding이나 implementation design을 다시 열지 않으며 추가 plan-level review를 요구하지 않는다.

## 0. `aa49e8f9` Four-Plan Synchronization Contract

이 계획은 공통 계약 `iris_aa49_four_plan_execution_sync_v1`에서 `G5_naturalization_phase0_through_phase8`과 `G7_naturalization_terminal_finalize`를 소유한다. `aa49e8f9fce19955a374b45d0744b1418a45ac9e`는 immutable ancestry/planning readpoint이며, 그 commit에는 이 계획을 포함한 네 plan blob 전부가 없으므로 직접 execution base가 아니다.

`G0_plan_set_materialization_and_owner_sync`는 네 exact plan blob과 SHA-256, 공통 projection을 clean descendant commit에 tracked 상태로 materialize한다. 현재 dirty planning worktree의 staged/unstaged/untracked implementation, staging, candidate, attempt 산출물은 자동 편입하지 않는다. 이번 개정은 실행 순서와 prerequisite만 동기화하는 owner directive이므로 추가 plan-level review를 요구하지 않는다.

네 계획이 동일하게 소비할 canonical compact-JSON projection은 다음과 같다.

```json
{"authority_boundaries":{"clean":"validation_reproducibility_only","food":"sealed_non_current_successor_only","naturalization_phase8":"immutable_candidate_handoff_only","naturalization_terminal":"requires_publish_accepted_and_policy_closure_complete","publish_foundation":"authority_effect_none","publish_official":"accepted_required_before_live_gate","registry_cutover":"separate_registry_owned_plan"},"baseline_commit":"aa49e8f9fce19955a374b45d0744b1418a45ac9e","baseline_role":"immutable_ancestry_and_planning_readpoint_only","contract_id":"iris_aa49_four_plan_execution_sync_v1","fresh_attempt_rules":{"clean":"fresh_phase0_from_plan_set_commit","food":"fresh_attempt_from_change0_no_attempt_0007_reuse","naturalization":"fresh_attempt_from_phase0_do_not_resume_attempt_0014","publish":"fresh_official_attempt_from_phase0_do_not_resume_attempt_0003"},"owner_directive":"synchronization_only_no_additional_plan_level_review","plan_paths":["docs/iris_clean_checkout_full_repository_validation_reproducibility_authority_closure_plan.md","docs/dvf_3_3_food_semantic_facts_authority_reconstruction_implementation_plan.md","docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md","docs/iris_publish_boundary_public_text_quality_acceptance_policy_closure_plan.md"],"prerequisite_closures":{"registry_authority":"canonical_complete","registry_runtime_compatibility":"canonical_complete"},"stage_order":["G0_plan_set_materialization_and_owner_sync","G1_clean_checkout_full_repository_validation","G2_food_semantic_facts_authority","G3_registry_food_successor_operational_cutover","G4_publish_boundary_foundation","G5_naturalization_phase0_through_phase8","G6_publish_boundary_official_phase0_through_phase7","G7_naturalization_terminal_finalize"]}
```

```text
four_plan_sync_projection_sha256 = 12c32873dc7e16e0d64e416bdb6693599e2790e9fc129606a90a72ca745a6eb0
```

| Global stage | Naturalization relationship |
|---|---|
| `G0_plan_set_materialization_and_owner_sync` | 네 plan blob/projection equality를 결속한다. |
| `G1_clean_checkout_full_repository_validation` | terminal PASS가 없으면 upstream Food와 이 plan 모두 실행하지 않는다. |
| `G2_food_semantic_facts_authority` | fresh Food attempt가 sealed non-current successor를 만든다. `attempt-0007`은 재사용하지 않는다. |
| `G3_registry_food_successor_operational_cutover` | successor facts/manifest를 current로 채택하고 adoption receipt를 만든다. |
| `G4_publish_boundary_foundation` | candidate-independent foundation만 만들며 `authority_effect=none`을 유지한다. |
| `G5_naturalization_phase0_through_phase8` | `attempt-0014`를 재개하지 않고 새 Phase 0 attempt로 Phase 8 immutable handoff까지 실행한다. |
| `G6_publish_boundary_official_phase0_through_phase7` | 이 plan은 candidate를 바꾸지 않고 fresh official result를 기다린다. |
| `G7_naturalization_terminal_finalize` | Publish `accepted`, policy closure complete, live gate adopted가 모두 확인된 뒤에만 terminal finalize한다. |

G1~G4 중 하나라도 complete/PASS가 아니면 G5를 시작하지 않는다. Publish result가 `blocked` 또는 `deferred_internal_debt`이면 G7로 진행하지 않고 exact earliest-affected phase를 가진 새 Naturalization remediation attempt를 연다.

## 1. Objective

이 계획의 목적은 DVF 3-3의 승인된 사실과 결정을 바꾸지 않으면서, 현재의 section-slot 조립 결과를 자연스러운 한국어 설명문으로 변환하는 **결정적(candidate-only) 문장화 경로**를 구현하고 검증하는 것이다.

목표 변환은 다음과 같다.

```text
approved facts / decisions / source-supported fields
-> semantic proposition inventory

profile / body_plan
-> structural role / requirement / ordering constraints

semantic proposition inventory
+ structural requirement inventory
+ sealed Korean prose realization policy
+ candidate-independent Publish Boundary development foundation contract
-> deterministic discourse plan
-> deterministic Korean surface realization
-> candidate rendered body
-> semantic-preservation evidence
-> Korean style and human-review evidence
-> immutable Publish Boundary handoff
-> separate fresh Publish Boundary official attempt
-> qualified public-text disposition
```

완료 상태는 다음 네 가지를 동시에 만족해야 한다.

1. 동일 입력과 동일 정책으로 생성한 두 candidate run이 byte-identical하다.
2. 각 candidate clause가 승인된 source proposition으로 역추적되고, 새 사실·새 추천·새 비교·새 사용법을 만들지 않는다.
3. full-corpus raw detector/metric 산출이 완전하고, Publish Boundary 정책이 분류한 machine blocker가 `0`이며, exact-hash human review의 **정책상 required review denominator 안에서** blocker가 `0`이다.
4. 별도 Publish Boundary 정책이 candidate payload에 대해 `accepted`에 해당하는 aggregate disposition을 산출한다.

이 계획의 최대 claim은 다음처럼 축을 분리한다.

- `DVF Korean Prose Naturalization Implementation Closure: complete`
- candidate 범위의 `DVF Body Compiler PASS`
- `Qualified public-text disposition: accepted`

다음 claim은 이 계획만으로 만들지 않는다.

- `Registry Authority PASS`
- `Registry Runtime Compatibility PASS`
- `Publish Boundary PASS`
- `Registry handoff eligibility: ready` 또는 그와 동등한 Registry readiness claim
- `Legacy Combined DVF Governance Route PASS` — 단, 별도 채택 후 기존 combined route 재실행 결과는 그 route의 기존 vocabulary로만 기록한다.
- runtime 배포, package release, current authority 전환 완료

## 2. Scope

### In Scope

- 첨부 로드맵의 repository provenance를 materialize하거나 exact hash로 owner approval에 결속한다.
- 별도 Public Text Quality Acceptance Policy 계획의 candidate-independent development foundation contract와 readiness report를 선행 입력으로 검증한다.
- 현재 3-3 source universe, adopted emission universe, profile, section topology, fact origin, 문장 골격, 중복 패턴을 다시 census한다.
- 한국어 품질 기준, gold corpus, 현재 표면 기준선, style regression fixture, semantic negative fixture를 서로 다른 역할의 tracked artifact로 만든다.
- approved facts/decisions/source-supported fields를 semantic proposition 단위로 정규화하고 proposition identity와 clause provenance를 기록한다.
- profile/`body_plan`은 semantic content가 아니라 structural role, requirement, ordering constraint만 제공한다.
- `identity`, `use`, `context`, `acquisition`, `limitation`의 정보 관계를 바탕으로 discourse plan을 만든다.
- 반복 identity noun, 의미 없는 section paragraph 분리, use/context 중복, acquisition 평탄화, 내부 추상어 노출을 줄이는 deterministic Korean surface realization을 구현한다.
- candidate 전용 full-universe 생성과 proposition trace sidecar 생성을 구현한다.
- source/candidate key-set equality, semantic preservation, suppression validity, determinism, full-corpus raw detector completeness, Publish-classified blocker closure, denominator-qualified human review, waiver/disposition을 서로 독립된 gate로 검증한다.
- candidate artifact와 검증 receipt를 Registry가 별도 adoption round에서 소비할 수 있도록 handoff contract를 만든다.
- Phase 8에서 immutable candidate/evidence bundle을 Publish Boundary 공식 Phase 0 입력으로 인계하고, 그 계획이 산출·봉인한 exact accepted disposition과 closure hash를 역인계 받는다.
- owner 승인 후 additive required gate를 기존 legacy combined current route에 연결하고 regression을 재실행한다.
- closeout report, independent review, owner seal, claim-boundary scan을 만든다.

### Explicitly Out Of Scope

- facts, decisions, source overlay, identity precedence 또는 compose profile의 authority 의미 변경
- current rendered output의 제자리 rewrite
- Lua bridge, runtime chunks, package payload, release archive 생성 또는 수정
- Registry current-source selection, promotion, cutover, adoption 또는 lifecycle seal 수행
- Registry Runtime Compatibility 의미 재검증 또는 compatibility claim 흡수
- 3-4 동작 절차, 사용 조건, 메뉴 조작, 추천, 비교, 공략성 정보의 3-3 유입
- source가 제공하지 않은 구체 용도·획득처·성능·효과·제한의 추론
- style 점수, quality disposition, reviewer note의 runtime 노출
- 닫힌 vNext authority 또는 2105 migration scope 재개방
- 기존 12개 DVF System current core closure module 수의 무승인 증가
- 현재 tooling allowlist의 `export_dvf_3_3_lua_bridge` 외 항목 무승인 추가
- `blocked_by_source`를 source 보강 작업으로 자동 전환
- owner 판단, waiver, human review, independent review를 도구가 대리 생성

## 3. Non-Goals

- 모든 item을 서로 다른 문학적 문체로 쓰는 것이 목표가 아니다. 같은 사실은 같은 규칙으로 안정적으로 표현한다.
- 기존 `StyleNormalizer`의 치환 규칙을 늘려 완성 문장을 사후 교정하는 방식이 목표가 아니다.
- 문장 유사도나 금칙어 0건만으로 의미 보존 또는 사람 검토를 대체하지 않는다.
- section 수, paragraph 수, 문장 수를 품질의 대리 지표로 사용하지 않는다.
- `coverage_quality=strong` 같은 기존 구조 지표를 자연스러운 한국어 품질 판정으로 재해석하지 않는다.
- source universe와 adopted prose universe를 하나의 denominator로 합치지 않는다.
- candidate acceptance를 current authority adoption 또는 공개 배포 승인으로 해석하지 않는다.
- 이미 닫힌 Registry Authority / Runtime Compatibility governance를 이 round에서 다시 설계하지 않는다.
- ignored staging artifact나 로컬 prototype을 durable authority로 승격하지 않는다.

## 4. Assumptions

### Phase 0 remeasurement requirements

- 계획 작성 시점의 current source universe는 `2105` item이다.
- 현재 rendered 관찰값은 adopted/composed `2084`, unadopted `21`이다.
- 현재 구조 품질 관찰값은 weak `1040`, adequate `729`, strong `315`이며, `1507` row가 하나 이상의 profile-required section을 충족하지 못한다.
- adopted `2084`의 profile 관찰값은 tool `519`, consumable `466`, wearable `451`, output `374`, material `213`, container `61`이다.
- 대표 section topology 관찰값은 `identity+use` `1049`, `identity+use+acquisition` `652`, `identity+use+context+acquisition` `260`이다.
- `primary_use` origin 관찰값은 `cluster_summary` `1275`, `identity_fallback` `718`, `role_fallback` `100`, `direct_use` `12`이다.

이 count와 denominator는 모두 Phase 0에서 다시 측정한다. 값이 다르면 silently rebaseline하지 않고 drift report를 만들며, policy binding이나 implementation scope에 영향을 주면 owner 재승인을 요구한다.

### Planning-time reference observations

다음은 구현 경로를 정하기 위한 planning-time reference이며 terminal evidence가 아니다. Phase 0은 실재 여부와 contract를 다시 확인한다.

- `compose_layer3_body_profile.py`는 section별 독립 문장을 만들고, `compose_layer3_item.py`는 여러 section을 `\n\n`으로 연결한다.
- context-required profile은 이미 use가 같은 내용을 표현하더라도 별도 `"... 맥락에서 쓰인다"` 문장을 만들 수 있다.
- `compose_layer3_identity.py`의 한국어 지원은 copula/jongseong 및 제한된 context parsing 중심이다.
- `StyleNormalizer`는 literal/regex 치환과 `postprocess_ko`를 수행하지만 proposition/discourse compiler가 아니다.
- current input manifest는 facts, decisions, overlay, compose profiles, identity precedence의 exact path/hash와 expected universe를 결속한다.
- `body_plan`은 별도 사실 authority가 아니라 compose profile 내부의 structural plan이다.
- `tools/style/` 아래 다수의 linter/baseline/closeout prototype은 `.gitignore` 대상이며 durable tracked implementation으로 간주할 수 없다.
- live current core closure는 12개 module이고 tooling allowlist는 `export_dvf_3_3_lua_bridge` 한 항목이다.
- current rendered output은 `.gitignore` 대상 JSON object이며 `meta`와 `entries`를 가진다. 계획 작성 시점에는 `entries`가 `2105`개다.
- current composer는 `generated_at`을 기록하므로 raw output 전체를 그대로 재실행 determinism authority로 사용할 수 없다.
- live required-validation manifest의 계획 작성 시점 관찰값은 required artifact `149`, required test `56`이며 Phase 0에서 다시 계산한다.
- live `current_route_required_validations.json`은 DVF System PASS authority가 아니라 `legacy_combined_governance_route` container다.

### Authority and prerequisite assumptions

1. `docs/Philosophy.md`가 최상위 설계 원칙이다.
2. `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 최신 축 분리와 책임 경계를 유지한다.
3. `docs/EXECUTION_CONTRACT.md`는 heavy/authority/public-output 작업의 실행·증거·closeout ceiling 계약으로 Phase 0에서 exact path/hash/checked-state/conflict count를 기록한다.
4. tracked repository에는 계획 작성 시점 기준 Korean prose naturalness를 판정하는 sealed Publish Boundary official disposition이 없다.
5. synchronized `docs/iris_publish_boundary_public_text_quality_acceptance_policy_closure_plan.md`는 S1에서 candidate-independent development foundation contract를 먼저 만든다. 이 foundation은 remediation target과 runner interface를 동결하지만 `authority_effect=none`, `official_disposition=not_issued`, `live_gate_adopted=false`, `policy_closure_state=not_started`이며 sealed policy closure가 아니다.
6. 이 계획은 로드맵의 **State B 책임 분리**를 유지하되 circular prerequisite를 제거한다. Phase 1 이후 진행의 hard prerequisite는 별도 policy closure 완료가 아니라 다음 정보를 exact path/hash로 제공하는 Publish Boundary foundation readiness다.
   - synchronization contract ID와 foundation version
   - candidate-independent policy candidate identity와 schema
   - policy input/output 및 required handoff schema
   - development runner/validator command
   - exit-code 및 fail-closed contract
   - acceptance metric/denominator candidate registry
   - raw detector → disposition candidate mapping과 threshold
   - full-corpus machine blocker와 human-only blocker의 claim scope
   - human-review sample selection algorithm
   - required human-review denominator definition
   - item-level 및 aggregate disposition candidate mapping
   - waiver authority와 expiry/freshness 규칙
   - `foundation_contract_ready_for_remediation=true`
7. owner ratification, independent review, official policy seal, exact disposition, live gate adoption과 Publish policy closure는 이 계획의 immutable Phase 8 handoff가 준비된 뒤 Publish Boundary 공식 Phase 0~7에서 수행한다. official projection은 이 계획이 소비한 foundation projection과 byte-equivalent해야 하며, 다르면 candidate를 평가하지 않고 stale 처리한다.
8. canonical phase boundary는 다음 한 문장으로 고정한다: **Phase 0의 read-only prerequisite 진단과 attempt-local report 생성만 foundation readiness 전 허용하며, Phase 0 PASS 전에는 Phase 1 artifact 생성·corpus 승인·compiler code 수정·candidate 실행을 모두 금지한다.**
9. 첨부 로드맵은 repo 밖 입력이다. 실행 전 다음 중 하나가 필요하다.
   - owner-approved roadmap을 `docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_roadmap.md`로 materialize
   - 또는 attachment SHA-256과 채택 범위를 명시한 tracked owner approval record
10. `docs/dvf_3_3_body_role_policy.md`, `docs/dvf_3_3_text_policy.md`, `docs/3_3_vs_3_4_boundary_examples.md`는 current tracked authority에 존재하지 않는다. archive나 과거 삭제 기록에서 이름이 발견되더라도 Phase 0에서 `non-authoritative historical reference`로 분류하며, current authority로 복원·가정하지 않는다.

### Resolved implementation decisions

- Publish Boundary foundation readiness는 이 계획의 Phase 1 hard prerequisite이고, official policy ratification/sealing/closure는 Phase 8 cross-plan handoff 이후 Publish Boundary가 소유한다. compiler가 자신의 acceptance threshold를 정의하지 않는다.
- `korean_prose_policy.json`은 realization constraints, raw detector definitions, metric calculation, compiler-invalid patterns만 소유한다. `blocking`/`advisory`/`human_only` mapping, threshold, waiver, item/aggregate disposition은 sealed Publish Boundary policy만 소유한다.
- semantic proposition content authority는 approved facts/decisions/source-supported fields에만 있다. profile/`body_plan`은 structural role, requirement, ordering constraint authority이며 source에 없는 semantic proposition을 만들 수 없다. current rendered snapshot은 기존 표면 회귀 비교용일 뿐 semantic authority가 아니다.
- source proposition inventory는 candidate 생성 경로와 독립된 extractor가 approved facts/decisions/source-supported fields만 읽어 먼저 봉인한다. profile/`body_plan`은 별도 requirement inventory로 읽고, candidate text나 candidate trace를 입력으로 읽지 않는다.
- current surface snapshot, positive gold corpus, positive/negative style regression fixture를 별도 artifact와 schema로 관리한다. 서로를 대체하거나 하나의 corpus로 합치지 않는다.
- source universe, candidate emission universe, semantic-validation universe, style-review universe, human-review universe, waiver universe를 별도 denominator로 기록한다.
- raw detector/metric은 full candidate denominator에서 완전해야 하고, sealed Publish policy가 그 결과를 분류한 machine blocker는 `0`이어야 한다. human-only blocker는 required review denominator 안에서 `0`이어야 하며, 전수 human review를 하지 않았다면 corpus-wide human-only blocker `0`을 주장하지 않는다.
- `item_prose_disposition`의 roadmap vocabulary와 `aggregate_publish_disposition` vocabulary가 다르면, Phase 0에서 foundation contract의 exact candidate mapping을 결속하고 Phase 8에서 official sealed policy와 byte-equivalent임을 다시 확인한다. 이름이 비슷하다는 이유로 자동 변환하지 않는다.
- 새 candidate path는 기존 12개 current core closure module 경계 안에 additive mode로 구현한다. default mode는 normalized stable content identity와 volatile metadata contract를 보존하며, raw file byte identity는 주장하지 않는다.
- 새 compose context enum을 추가하지 않고 기존 `compose_context=staging`과 attempt-local output path를 candidate mode에 사용한다.
- candidate payload는 기존 rendered schema와 같은 JSON object인 단일 `candidate_rendered.json`이다. proposition/discourse trace, proposition resolution, Publish-owned item prose disposition은 각각 별도 namespace와 sidecar로 기록한다.
- candidate content bytes에는 `generated_at`, attempt ID, 절대 경로 같은 volatile metadata를 넣지 않는다. 그런 실행 정보는 manifest/receipt에 두며, candidate content SHA-256은 하나만 봉인한다.
- ignored style prototype은 algorithm inventory의 참고 자료일 뿐, required gate가 import하거나 authority로 인용하지 않는다.
- 새 runner/validator는 current core import graph 밖의 standalone subprocess tool로 구현한다.
- 새 imported build module이 정말 필요해지면 작업을 중단하고 별도 core-closure change decision을 요청한다. module count를 조용히 `13`으로 만들지 않는다.
- residual override는 로드맵의 선택지 중 **B**를 채택한다. item ID·item-specific text·per-item phrase override는 전면 금지하며, 잔여 문제는 generic rule, source-owned `blocked_by_source`, 또는 후속 backlog로만 처리한다.
- `deferred`는 이 round 범위 밖의 **DVF 3-3 facts authority correction** 또는 별도 **Layer 4 QG debt**를 owner namespace까지 분리해 기록하고 exact owner-approved backlog ID/hash가 있을 때만 허용한다. Layer 3 facts 부족을 Layer 4 QG로 자동 routing할 수 없으며 translationese compiler blocker를 일반 `deferred`로 숨길 수 없다.

### DVF 3-3 Facts Authority / Layer 4 QG architecture correction

- DVF 3-3 facts authority는 Layer 3-3 body가 소비할 semantic proposition의 작성·보강·승격을 소유한다. `dvf_3_3_facts.jsonl`에 승인된 구분 정보가 없어서 body compiler가 결정론적으로 문장을 분리할 수 없는 경우의 current routing target은 `docs/dvf_3_3_food_semantic_facts_authority_reconstruction_implementation_plan.md`다. 기존 `docs/dvf_3_3_facts_authority_enrichment_plan.md`는 non-executable predecessor diagnostic draft로만 보존한다.
- Layer 4는 recipe, right-click source, 요구조건, 사용 맥락 같은 상호작용 정보 계층이다. Layer 4 QG는 그 증거·분류·상호작용 산출물의 품질을 검문하지만 Layer 3 facts authority가 아니며 Layer 3 source 부족의 기본 owner가 아니다.
- Layer 4 trace/readpoint/support artifact를 Layer 3 facts로 사용하려면 별도 approved cross-layer promotion plan과 새 facts authority seal이 선행되어야 한다. naturalization runner나 validator는 이를 자동 routing·자동 승격·자동 읽기할 수 없다.
- `attempt-0014-remediation`의 317-row identical-approved-condition 분석과 Phase 3 fail-closed 판정은 immutable evidence로 유지한다. 그 attempt 안의 `source_qg` owner/routing 표현은 append-only correction record가 무효화하며 attempt artifact 자체는 수정하지 않는다.
- 새 runner artifact는 `facts_authority_enrichment_request.json`, `owner=dvf_3_3_facts_authority`, `authority_domain=layer3_3_facts`, `layer4_qg_routing_allowed=false`를 사용한다. validator는 이 구분을 위반하는 새 routing artifact를 거부한다.

### Food Semantic Facts Authority → Naturalization Phase 2 synchronization

이 계획은 `dvf3_3_food_semantic_facts_authority__naturalization_phase2_sync_v1`의 consumer다. Facts Authority 계획의 producer 선언만으로 동기화가 성립하지 않으며, 양쪽 계획의 projection이 execution time에 byte-equivalent해야 한다.

Producer가 봉인해야 하는 exact identity set은 다음 네 개다.

```text
successor facts SHA-256
successor input-manifest SHA-256
approved food-semantic schema SHA-256
approved proposition-licensing contract SHA-256
```

Required upstream artifacts:

```text
phase11_successor/selected_successor_input_binding.json
phase11_successor/sealed_successor_receipt.json
phase12_phase2_handoff/phase2_handoff_contract.json
phase12_phase2_handoff/phase2_handoff_acceptance_report.json
phase12_phase2_handoff/naturalization_tooling_authorization_binding.json
phase12_phase2_handoff/downstream_resume_packet.json
```

소비 상태를 다음 둘로 분리한다.

| State | Allowed consumer behavior | Forbidden claim/action |
|---|---|---|
| `sealed_non_current_compatibility_probe` | actual Phase 2 inventory path가 explicit non-current override로 읽고 no-render compatibility만 검증 | official naturalization attempt, candidate 생성, Phase 4~8, Publish handoff |
| `registry_adopted_official_retry` | Registry adoption receipt와 current facts/manifest의 successor identity 일치를 결속한 뒤 새 naturalization attempt를 Phase 0부터 열고 Phase 2 source inventory를 재봉인 | prior Phase 2 probe/attempt/human review/Publish disposition 재사용 |

Facts Authority round의 no-render Phase 2 PASS는 이 계획의 Phase 2 PASS가 아니며 official retry authorization도 아니다. Official retry는 별도 Registry-owned operational-cutover가 successor facts/manifest를 current로 채택하고 다음 predicate를 만족한 뒤에만 허용한다.

```text
registry_adoption_receipt = present
current_facts_sha256 = selected_successor_facts_sha256
current_input_manifest_sha256 = selected_successor_manifest_sha256
registry_current_identity_ambiguity_count = 0
official_naturalization_retry_allowed = true
```

Official retry는 `attempt-0014-remediation`을 재개하지 않는다. 새 attempt ID로 Phase 0 prerequisite/provenance를 다시 봉인하고, source가 바뀌었으므로 Change 2 source proposition inventory부터 새 hash로 재생성한다. 이전 candidate, trace, Phase 6 detector, human review, Phase 8 handoff와 Publish disposition은 모두 stale이다.

Phase 2 consumer adapter는 approved structured facts와 proposition-licensing contract만 읽는다. Schema token을 문장 의미로 추측하거나 item ID/hash/random/order로 partition을 만들 수 없다. Facts producer와 consumer의 네 identity 중 하나라도 다르면 `blocked_stale_food_semantic_facts_handoff`로 종료한다.

이 상류 동기화는 Publish Boundary 계약을 변경하지 않는다. 새 naturalization attempt가 fresh Phase 8 handoff를 만든 뒤에만 기존 `dvf3_3_korean_naturalization__publish_boundary_sync_v1`을 사용한다.

상류 실행 순서는 다음으로 고정한다.

| Upstream stage | Owner | Naturalization state |
|---|---|---|
| `F0_facts_roadmap_plan_review` | Food Semantic Facts Authority | implementation과 naturalization 모두 blocked |
| `F1_facts_implementation` | Food Semantic Facts Authority | protected read-only; official retry forbidden |
| `F2_sealed_successor_probe` | Food Semantic Facts Authority + Naturalization tooling owner | actual Phase 2 path의 non-current no-render compatibility probe only |
| `F3_registry_operational_cutover` | Iris Artifact Registry | successor facts/manifest의 current adoption 및 exact receipt |
| `F4_fresh_naturalization_retry` | 이 계획 | new attempt Phase 0, then Phase 2 inventory reseal and Phase 3~8 |

### Cross-Plan Canonical Execution Order

교차 계획 계약 `dvf3_3_korean_naturalization__publish_boundary_sync_v1`의 실행 순서와 ownership은 다음으로 고정한다.

| Sync stage | Owning plan | This plan state |
|---|---|---|
| `S0_plan_sync` | 양쪽 계획 | 공통 schema, enum, artifact path, freshness와 claim boundary의 projection hash를 일치시킨다. |
| `S1_publish_foundation` | Publish Boundary 계획 | 이 계획은 실행하지 않고 tracked foundation contract/readiness를 기다린다. |
| `S2_naturalization_build` | 이 계획 | Phase 0~7과 Phase 8 handoff-build를 실행해 immutable candidate/evidence bundle을 만든다. |
| `S3_publish_official_attempt` | Publish Boundary 계획 | 이 계획은 candidate를 수정하지 않고 official Phase 0~7 결과를 기다린다. |
| `S4_naturalization_finalize` | 이 계획 | exact accepted disposition과 Publish closure hash를 검증한 뒤 Phase 8 consume 및 Phase 9를 실행한다. |

이 local `S0~S4` contract는 전역 계약에 다음처럼 매핑한다.

```text
S0_plan_sync               = G0_plan_set_materialization_and_owner_sync의 Naturalization/Publish projection
S1_publish_foundation      = G4_publish_boundary_foundation
S2_naturalization_build    = G5_naturalization_phase0_through_phase8
S3_publish_official        = G6_publish_boundary_official_phase0_through_phase7
S4_naturalization_finalize = G7_naturalization_terminal_finalize
```

foundation contract required state:

```text
synchronization_contract_id = dvf3_3_korean_naturalization__publish_boundary_sync_v1
foundation_contract_ready_for_remediation = true
authority_effect = none
official_disposition = not_issued
live_gate_adopted = false
policy_closure_state = not_started
```

Phase 8 handoff는 최소 다음 exact constituent를 열거하고 hash-bound한다.

```text
naturalization_attempt_id
foundation_contract_hash
candidate_rendered_hash
candidate_manifest_hash
source_proposition_manifest_hash
body_plan_requirement_digest
structural_satisfaction_ledger_hash
semantic_preservation_report_hash
raw_detector_report_hash
human_review_sample_manifest_hash
human_review_decision_hash
compiler_implementation_hash
korean_prose_policy_hash
corpus_manifest_hash
protected_surface_no_mutation_report_hash
requested_evaluation_subject_kind = dvf_3_3_korean_naturalization_candidate
```

handoff 후 candidate constituent를 수정하지 않는다. Publish result가 `blocked` 또는 `deferred_internal_debt`이면 Publish attempt는 `adoption_timing=after_remediation`으로 incomplete하게 보존하고, 이 계획은 exact blocker owner와 earliest affected phase를 따라 새 naturalization attempt를 연다. synchronized path에서 blocked-immediate Publish adoption은 금지한다.

Publish official result를 역인계 받을 때 다음을 모두 검증한다.

```text
evaluation_subject_kind = dvf_3_3_korean_naturalization_candidate
evaluation_subject_hash = candidate_rendered_hash
consumed_handoff_manifest_hash = exact Phase 8 handoff hash
consumed_foundation_contract_hash = exact Phase 0 bound foundation hash
qualified_disposition = accepted
publish_policy_closure_state = complete
publish_live_required_gate_adopted = true
registry_runtime_current_adoption_claimed = false
```

두 계획이 canonical JSON으로 투영해 hash를 비교할 synchronization projection은 다음 field를 정확히 사용한다.

```text
synchronization_contract_id
canonical_stage_order = S0_plan_sync,S1_publish_foundation,S2_naturalization_build,S3_publish_official_attempt,S4_naturalization_finalize
foundation_required_state
evaluation_subject_kind_enum
candidate_structural_status_enum
required_handoff_constituent_ids
nonaccepted_candidate_action = after_remediation
blocked_immediate_allowed_for_synchronized_candidate = false
candidate_runtime_parity_applicability = not_applicable
candidate_runtime_parity_reason = candidate_not_registry_adopted
publish_owns_metric_mapping_threshold_waiver_disposition = true
dvf_owns_proposition_discourse_realization_raw_detector = true
```

### Workspace assumptions

- 시작 시 존재하는 modified/untracked 파일은 사용자 소유다.
- 특히 기존 `dvf_3_3_current_source_authority_drift_verification_recovery_scope_retirement` staging 변경과 untracked Publish Boundary plan을 이 계획의 baseline이나 산출물로 흡수하지 않는다.
- 실행 도구는 PowerShell, `rg`, `fd`, `jq`, `uv`, Git을 우선한다.
- required tool이 없거나 exact command가 exit `0`이 아니면 validation은 `blocked` 또는 `failed`로 기록하며 PASS로 쓰지 않는다.

## 5. Repository Areas Affected

### Code

기존 core module의 candidate-only additive 변경 후보:

- `Iris/build/description/v2/tools/build/compose_layer3_text.py`
  - explicit candidate prose mode, policy binding, staging-only guard
- `Iris/build/description/v2/tools/build/compose_layer3_body_profile.py`
  - section 후보 대신 proposition inventory와 discourse relation 생성
- `Iris/build/description/v2/tools/build/compose_layer3_item.py`
  - candidate discourse plan 소비, trace sidecar row 생성
- `Iris/build/description/v2/tools/build/compose_layer3_render.py`
  - deterministic paragraph/sentence realization
- `Iris/build/description/v2/tools/build/compose_layer3_blocks.py`
  - 기존 block contract와 candidate rendering boundary 정합
- `Iris/build/description/v2/tools/build/compose_layer3_identity.py`
  - 제한된 조사·copula·명사 반복 제어 helper
- `Iris/build/description/v2/tools/build/compose_layer3_io.py`
  - candidate-only output/trace path validation이 필요한 경우에 한해 변경

새 standalone orchestration:

- `Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py`
- `Iris/build/description/v2/tools/build/validate_dvf_3_3_korean_prose_naturalization.py`

새 test 후보:

- `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_policy.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_compiler.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_semantic_preservation.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_candidate_route.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_acceptance_gate.py`

기존 no-regression test:

- `Iris/build/description/v2/tests/test_compose_entrypoint_guard_hardening.py`
- `Iris/build/description/v2/tests/test_compose_layer3_text_overlay.py`
- `Iris/build/description/v2/tests/test_compose_layer3_text_v2.py`

### Docs

- 이 계획 문서
- `docs/iris_publish_boundary_public_text_quality_acceptance_policy_closure_plan.md` (read-only synchronized plan input)
- 필요 시 owner-approved source roadmap:
  - `docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_roadmap.md`
- `docs/dvf_3_3_korean_prose_quality_standard.md`
- `docs/dvf_3_3_korean_prose_compiler_contract.md`
- `docs/dvf_3_3_korean_prose_claim_boundary.md`
- `docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closeout.md`
- terminal bundle freeze 전에만 적용하는 additive update 후보:
  - `docs/DECISIONS.md`
  - `docs/ARCHITECTURE.md`
  - `docs/ROADMAP.md`
- `docs/EXECUTION_CONTRACT.md`는 read-only prerequisite이며 이 closure의 update target이 아니다.

### Config / Tracked Data

- `Iris/build/description/v2/data/korean_prose_naturalization/korean_prose_policy.json`
- `Iris/build/description/v2/data/korean_prose_naturalization/gold_corpus.jsonl`
- `Iris/build/description/v2/data/korean_prose_naturalization/style_regression_fixtures.jsonl`
- `Iris/build/description/v2/data/korean_prose_naturalization/current_surface_snapshot_manifest.json`
- `Iris/build/description/v2/data/korean_prose_naturalization/semantic_negative_fixtures.jsonl`
- `Iris/build/description/v2/data/korean_prose_naturalization/corpus_manifest.json`
- 선택적 변경:
  - `.gitignore` — required artifact/test가 active ignore rule에 걸릴 때 exact-path unignore만 추가
  - `Iris/_docs/round3/current_route_required_validations.json` — informed owner authorization 후 additive adoption만 허용

`korean_prose_policy.json`은 surface realization constraints, raw detector/metric definitions, compiler-invalid patterns만 정의한다. detector hit를 `blocking`/`advisory`/`human_only`로 분류하거나 item/aggregate disposition, threshold, waiver를 결정하지 않는다.

### Durable Governance Artifacts

다음은 owner/reviewer가 제공하거나 terminal phase가 검증하는 tracked artifact 후보다.

- `Iris/_docs/round3/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/roadmap_binding.json`
- `.../publish_foundation_binding.json`
- `.../publish_official_result_binding.json`
- `.../quality_standard_approval.json`
- `.../gold_corpus_approval.json`
- `.../human_review_decision.json`
- `.../independent_review.json` — frozen `terminal_bundle_hash`에 결속한 append-only attestation
- `.../registry_handoff_receipt.json` — packet completeness를 기록하는 receipt이며 eligibility/readiness claim이 아님
- `.../owner_seal.json` — 같은 bundle hash와 independent-review hash에 결속한 append-only seal
- `.../closure_receipt.json` — terminal validator exit `0` 뒤 frozen bundle 밖에 기록하는 post-seal external additive operational receipt

도구는 owner/reviewer 판단 내용을 생성하지 않는다. 제공된 artifact의 schema, role separation, exact candidate hash, freshness만 검증한다.

`closure_receipt.json`은 frozen terminal bundle의 구성원이 아니며 terminal PASS를 새로 판정하거나 재정의하지 않는다. 외부 append-only receipt recorder가 terminal no-write validator의 exit `0` 이후 다음 값만 기록한다.

```text
terminal_bundle_hash
independent_review_sha256
owner_seal_sha256
terminal_validator_command_digest
terminal_validator_exit_code
terminal_validator_stdout_digest
recorded_at
```

receipt 수정이 필요하면 기존 receipt를 덮어쓰지 않고 `supersedes`를 가진 새 external receipt를 추가한다.

### Generated / Attempt-Local Artifacts

attempt root:

```text
Iris/build/description/v2/staging/
  dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/
    <attempt-id>/
      phase0/
      phase1/
      phase2/
      phase3/
      phase4/
      phase5/
      phase6/
      phase7/
      phase8/
      phase9/
```

phase와 Change의 canonical mapping은 다음과 같다.

| Phase | Change | Phase-local evidence |
|---|---|---|
| `phase0` | Change 0 | prerequisite, provenance, baseline, write-boundary |
| `phase1` | Change 1 | census, quality standard, corpus evidence |
| `phase2` | Change 2 | source proposition 및 body-plan requirement inventory |
| `phase3` | Change 3 | compiler contract tests, default-mode regression, write-boundary negative tests |
| `phase4` | Change 4 | immutable full-corpus candidate와 determinism |
| `phase5` | Change 5 | semantic, equivalence, body-plan, rendered-shape evidence |
| `phase6` | Change 6 | raw detector와 compiler-invalid residual evidence |
| `phase7` | Change 7 | exact-hash human review |
| `phase8` | Change 8 | immutable Publish handoff, official Publish attempt 대기, accepted result 역인계 |
| `phase9` | Change 9 | required gate, final docs, frozen terminal bundle, review/seal |

주요 generated artifact:

- preflight/baseline/hash/protected-surface report
- pre-change default-mode normalized golden baseline과 volatile metadata contract
- prose census와 recurring-skeleton report
- current surface snapshot manifest와 분리된 positive/negative fixture corpus
- candidate-independent `source_proposition_inventory.jsonl`
- `source_proposition_manifest.json`과 `source_to_proposition_coverage_report.json`
- 단일 full-corpus `candidate_rendered.json`
- proposition/discourse/transformation trace JSONL
- `structural_satisfaction_ledger.jsonl`과 body-plan application report
- source-to-candidate semantic preservation report
- suppression and paragraph-merging report
- determinism comparison report
- full-corpus raw detector/metric report
- exact-hash human-review sample manifest와 review decision
- Publish policy가 산출한 item prose disposition ledger와 aggregate acceptance result
- immutable `phase8/publish_acceptance_handoff_manifest.json`
- `phase8/publish_official_attempt_binding.json`
- `phase8/publish_acceptance_cross_plan_receipt.json`
- required-gate candidate patch
- Registry handoff manifest
- post-required-gate-adoption 및 post-final current-route result
- `phase9/pre_freeze_lua_syntax_report.json`
- `phase9/pre_freeze_vcs_durability_report.json`
- final claim-scan result와 frozen `terminal_bundle_manifest.json`
- terminal no-write validation 대상 binding

staging artifact는 그 자체로 durable authority가 아니다. required gate는 clean checkout에서 tracked policy/input으로 같은 verdict를 재생하거나, terminal receipt가 결속한 exact tracked artifact만 소비해야 한다.

## 6. Planned Changes

### Feedback finding crosswalk

| Feedback revision | Plan resolution | Required artifact / predicate | Disposition |
|---|---|---|---|
| R1 handoff claim ceiling | Section 1, Change 9, Section 12 | `registry_handoff_packet_complete`; receipt field only | resolved in plan |
| R2 translationese terminal condition | Change 6, Change 8, Change 9, Section 12 | unresolved/deferred translationese predicates | resolved in plan |
| R3 detector/disposition authority | Section 4, Changes 1/6/8 | raw detector output → sealed Publish mapping | resolved in plan |
| R4 independent proposition inventory | Changes 2/4/5, Validation 3 | source inventory/manifest/coverage report | resolved in plan |
| R5 legacy identity | Changes 0/3, Rollback, Section 12 | normalized content, metadata contract, protected no-mutation | resolved in plan |
| R6 body-plan application | Changes 2/3/5/9 | structural satisfaction ledger and claim-evidence matrix | resolved in plan |
| R7 policy runner/phase boundary | Section 4, Change 0, Validation 1 | runner command/schema/exit contract; Phase 1 hard gate | resolved in plan |
| R8 `not_applicable` reason | Change 5, Section 12 | closed reason enum; missing-reason count `0` | resolved in plan |
| R9 enum namespace | Changes 5/6/8 | proposition/item/aggregate namespaces | resolved in plan |
| R10 execution contract state | Change 0, Validation 1, Section 11 | path/hash/checked/conflict fields | resolved in plan |
| R11 previous-finding crosswalk | this table and Change 0 | feedback hash plus `previous_finding_crosswalk.json`, including upstream `C3`/`I4`/`M3` labels | resolved in plan |
| R12 validator read-only contract | Change 5, Section 7, Rollback | every `--require-*` uses `--no-write` | resolved in plan |

### Cycle 2 feedback crosswalk

| Cycle 2 revision | Plan resolution | Required artifact / predicate | Disposition |
|---|---|---|---|
| C2-R1 canonical terminal sequence | Section 5, Change 9, Validation 12, Sections 11/12 | Option A frozen bundle sequence and `terminal_bundle_hash` | resolved in plan |
| C2-R2 execution contract Read list | Change 0, Section 5 | explicit read-only `docs/EXECUTION_CONTRACT.md` | resolved in plan |
| C2-R3 semantic/structural authority | Sections 1/2/4, Changes 2/5 | semantic proposition vs body-plan requirement inventories | resolved in plan |
| C2-R4 human-review selection prerequisite | Section 4, Changes 0/7 | selection algorithm and required denominator binding | resolved in plan |
| C2-R5 phase mapping | Section 5, Change 3, Validation 4–6 | phase-to-Change table and phase3 evidence | resolved in plan |
| C2-R6 residual report contract | Change 6 | `compiler_invalid_residual_report.json` | resolved in plan |
| C2-R7 retry/equivalence protocol | Changes 2/5/8, Rollback | typed equivalence proof and new-attempt stale cascade | resolved in plan |

### Post-Cycle 2 advisory crosswalk

| Advisory | Plan resolution | Required artifact / predicate | Disposition |
|---|---|---|---|
| A1 Lua/VCS terminal position | Change 9, Validation 12–14 | pre-freeze Lua/VCS reports included in terminal bundle | resolved in plan |
| A2 closure receipt timing | Section 5, Change 9, Section 12 | post-seal external additive `closure_receipt.json` | resolved in plan |
| A3 pre-freeze top-doc claim tense | Change 9, claim scanner, Section 11 | seal-complete assertion count `0` | resolved in plan |

### Change 0 — Prerequisite, provenance, baseline, and write-boundary lock

**Purpose**

구현이 잘못된 policy, stale denominator, repo 밖 roadmap, 누락된 authority reference, 사용자 변경 파일 위에서 시작되지 않도록 실행 기준점을 고정한다.

**Files**

- Read:
  - `docs/Philosophy.md`
  - `docs/DECISIONS.md`
  - `docs/ARCHITECTURE.md`
  - `docs/ROADMAP.md`
  - `docs/EXECUTION_CONTRACT.md`
  - `docs/dvf_3_3_food_semantic_facts_authority_reconstruction_implementation_plan.md`
  - `docs/dvf_3_3_registry_authority_canonical_closure_plan.md`
  - roadmap 및 plan-review feedback attachments
  - `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
  - `Iris/_docs/round3/round3_active_core_closure.json`
  - `Iris/_docs/round3/current_route_required_validations.json`
  - current facts, decisions, overlay, profiles, rendered output
- Create:
  - `phase0/preflight_report.json`
  - `phase0/four_plan_sync_binding_report.json`
  - `phase0/clean_validation_prerequisite_report.json`
  - `phase0/roadmap_provenance_report.json`
  - `phase0/publish_foundation_binding_report.json`
  - `phase0/publish_foundation_runner_contract_report.json`
  - `phase0/cross_plan_sync_projection_report.json`
  - `phase0/food_semantic_facts_handoff_binding_report.json`
  - `phase0/registry_adoption_receipt_binding_report.json`
  - `phase0/execution_contract_checked_state.json`
  - `phase0/default_mode_golden_baseline.json`
  - `phase0/previous_finding_crosswalk.json`
  - `phase0/source_authority_reference_audit.json`
  - `phase0/protected_surface_snapshot.json`
  - `phase0/worktree_ownership_ledger.json`

**Implementation Notes**

- roadmap 및 plan-review attachment hash와 owner-approved 적용 범위를 결속한다.
- `aa49e8f9` ancestry, synchronized plan-set commit, 네 plan blob/SHA-256, 공통 projection SHA-256, owner synchronization-only/no-additional-review directive와 G1 Clean-Checkout terminal PASS/downstream-unblock receipt를 검증한다.
- upstream source review의 original finding ID를 보존해 `previous finding → plan section → artifact/predicate → disposition`으로 연결한다. 최소한 선행 chain에서 참조된 `C3`, `I4`, `M3`의 누락 여부를 fail-loud하게 검사한다.
- `EXECUTION_CONTRACT.md`의 path, SHA-256, checked boolean, conflict count와 이 계획의 heavy/authority/public-output risk classification을 기록한다.
- `EXECUTION_CONTRACT.md`는 이 round 전체에서 read-only로 유지하며 terminal docs patch, bundle mutation allowlist, rollback target에 포함하지 않는다.
- tracked Publish foundation contract/readiness의 path, SHA-256, schema, synchronization contract ID, candidate-independent projection과 `authority_effect=none` 상태를 검증한다.
- official retry이면 `dvf3_3_food_semantic_facts_authority__naturalization_phase2_sync_v1` producer projection, selected successor four-hash identity, Registry adoption receipt와 current facts/manifest identity를 검증한다. Sealed non-current successor만 있으면 official attempt를 열지 않고 compatibility probe state로 되돌린다.
- foundation이 제공한 policy-candidate input/output schema, required handoff schema, development runner/validator command, expected exit code, stdout/stderr/receipt contract와 fail-closed 동작을 실제 `--help`/schema와 대조한다.
- human-review sample selection algorithm, mandatory strata, required review denominator definition과 deterministic selection contract를 foundation binding report에 고정한다.
- item/aggregate disposition vocabulary mapping을 exact enum table로 고정한다.
- current input manifest와 실제 파일 hash를 대조하고 source key set을 다시 측정한다.
- composer code 변경 전에 default mode를 isolated path에서 한 번 생성하여 stable content canonicalization rule과 normalized content hash를 봉인한다. canonicalization은 schema에 열거된 volatile metadata value만 제외하며 prose, key order, newline 또는 non-volatile field를 정규화해 drift를 숨기지 않는다. volatile metadata field의 이름·type·format contract는 별도로 봉인하고 raw file byte hash 재현성은 요구하지 않는다.
- current rendered/Lua/runtime/package 및 user-owned dirty path의 before hash를 기록한다.
- 실행 중 허용할 mutation path allowlist를 선언한다.
- 누락된 `docs/dvf_3_3_body_role_policy.md`, `docs/dvf_3_3_text_policy.md`, `docs/3_3_vs_3_4_boundary_examples.md`를 archive 증거와 함께 `non-authoritative historical reference`로 기록하고, current authority chain에 포함되지 않았음을 검증한다. owner가 current authority로 복원을 요구하면 이 계획을 중단하고 별도 authority change를 연다.
- prerequisite 하나라도 실패하면 Phase 0 report만 남긴 채 `blocked_prerequisite`로 종료한다. Phase 1 artifact, corpus approval, composer code, candidate output은 만들지 않는다.

**Validation**

- foundation/roadmap/source manifest identity가 exact hash로 결속된다.
- four-plan sync projection hash가 네 계획에서 일치하고 G1 clean-validation terminal PASS가 exact receipt로 결속된다.
- synchronization contract projection hash가 Publish 계획의 projection과 일치한다.
- food-semantic Facts producer/consumer synchronization projection이 일치하고 official retry에서 Registry adoption receipt/current identity mismatch가 `0`이다.
- foundation runner/validator command와 input/output/handoff/exit contract가 실행 가능하며, 부재·schema mismatch·비정상 exit는 `blocked_prerequisite`다.
- foundation readiness가 official disposition, gate adoption 또는 policy closure를 주장한 count는 `0`이다.
- `execution_contract_checked = true`, `execution_contract_conflict_count = 0`이다.
- pre-change default baseline이 code mutation보다 앞선 timestamp/order receipt와 normalized content hash를 가진다.
- declared source universe와 actual key set이 일치한다.
- protected write set에 current rendered, Lua bridge, runtime chunks, package가 포함되지 않는다.
- worktree ownership ledger가 기존 변경을 새 산출물로 오인하지 않는다.
- missing authority reference가 unresolved인데 Phase 1 이후 artifact를 만들 수 없음을 negative test로 확인한다.

### Change 1 — Current surface census, quality standard, and distinct review corpora

**Purpose**

자연스러움 문제를 개인적 인상 대신 재현 가능한 defect taxonomy와 검토 corpus로 고정한다.

**Files**

- Create:
  - `docs/dvf_3_3_korean_prose_quality_standard.md`
  - `Iris/build/description/v2/data/korean_prose_naturalization/gold_corpus.jsonl`
  - `Iris/build/description/v2/data/korean_prose_naturalization/style_regression_fixtures.jsonl`
  - `Iris/build/description/v2/data/korean_prose_naturalization/current_surface_snapshot_manifest.json`
  - `Iris/build/description/v2/data/korean_prose_naturalization/corpus_manifest.json`
  - `phase1/current_prose_census.json`
  - `phase1/recurring_skeleton_inventory.json`
  - `phase1/review_strata_report.json`

**Implementation Notes**

- current rendered file이 ignored/stale일 수 있으므로 input manifest와 current composer를 사용한 isolated baseline generation을 우선한다.
- artifact 역할을 다음처럼 분리한다.
  - `current_surface_snapshot_manifest.json`: 현재 composer 표면의 반복·회귀 비교 기준. semantic authority가 아니며 candidate 정답 corpus도 아니다.
  - `gold_corpus.jsonl`: 승인된 proposition inventory에 결속한 positive realization 예시와 허용 transformation.
  - `style_regression_fixtures.jsonl`: 현재 나쁜 패턴, 경계 사례, positive/negative lint 기대값.
- 다음 strata를 최소 분리한다.
  - compose profile
  - item family/cluster
  - section topology
  - `primary_use` origin
  - acquisition/limitation presence
  - adopted/unadopted state
  - short/medium/long output
- defect taxonomy는 최소 다음을 포함한다.
  - repeated identity noun
  - duplicate use/context proposition
  - internal abstraction leakage (`작업`, `맥락`, `부품`, `용도` 등)
  - acquisition flattening
  - section-per-paragraph fragmentation
  - forced filler for required shape
  - broad-category first sentence
  - repeated sentence skeleton
  - translationese/passive overuse
  - unsupported inference
- gold corpus는 좋은 출력만 저장하지 않는다. source row, expected proposition coverage, 허용/금지 transformation, expected paragraph shape를 함께 저장한다.
- style regression fixture는 현재 나쁜 패턴, 경계 사례, `Base.LemonGrass`/`Base.Lemongrass` exact-key coexistence 같은 identity-sensitive 사례를 포함한다.
- quality standard는 raw detector 정의·metric 산식·compiler-invalid pattern과 사람 평가 rubric을 기술한다. detector hit의 blocker/advisory/human-only 분류, threshold, waiver, acceptance는 foundation이 candidate-independent하게 precommit하고 별도 official sealed Publish policy만 authority로 확정한다.

**Validation**

- gold/style fixture row는 모두 live source key 또는 명시적 synthetic-negative identity로 resolve된다.
- strata coverage와 selection algorithm이 manifest에 기록된다.
- corpus selection이 임의 수동 목록으로만 구성되지 않는다.
- gold expected claim이 source proposition보다 넓지 않다.
- current surface snapshot을 semantic expected output이나 approved proposition source로 참조하는 row가 `0`이다.
- corpus/standard hash가 owner approval에 결속된다.

### Change 2 — Proposition, discourse, and trace contract

**Purpose**

문장 문자열을 직접 이어 붙이지 않고, source fact와 최종 clause 사이에 검증 가능한 중간 표현을 둔다.

**Files**

- Create:
  - `docs/dvf_3_3_korean_prose_compiler_contract.md`
  - `Iris/build/description/v2/data/korean_prose_naturalization/korean_prose_policy.json`
  - `Iris/build/description/v2/data/korean_prose_naturalization/semantic_negative_fixtures.jsonl`
- Generate before candidate compilation:
  - `phase2/source_proposition_inventory.jsonl`
  - `phase2/source_proposition_manifest.json`
  - `phase2/source_to_proposition_coverage_report.json`
  - `phase2/body_plan_requirement_inventory.jsonl`
- Modify candidate-only path in:
  - `compose_layer3_body_profile.py`
  - `compose_layer3_item.py`
  - `compose_layer3_render.py`

**Implementation Notes**

proposition record는 최소 다음 field를 가진다.

```text
item_id
proposition_id
role
source_path
source_field
source_value_hash
fact_origin
modality
qualifier
condition
semantic_key
structural_requirement
emission_eligibility
food_semantic_schema_ref
proposition_license_id
```

discourse record는 최소 다음 field를 가진다.

```text
item_id
clause_id
proposition_ids
relation
ordering_reason
merge_reason
suppression_reason
paragraph_id
realization_rule_id
transformation_ids
```

- proposition identity는 normalized string equality만 사용하지 않는다. role, qualifier, condition, modality, source provenance를 포함한다.
- semantic proposition extractor는 approved facts/decisions/source-supported fields만 직접 읽고 candidate rendered, candidate discourse plan, candidate trace를 읽지 않는다. profile/`body_plan`은 별도 `body_plan_requirement_inventory.jsonl`만 만들며 source에 없는 proposition content를 생성할 수 없다. Phase 2에서 두 inventory의 content hash를 먼저 고정한 뒤 candidate compiler에 read-only 입력으로 전달한다.
- Food Semantic Facts handoff가 적용되는 row는 selected successor facts/manifest, approved schema와 proposition-licensing contract의 exact four-hash binding을 함께 기록한다. Licensed structured assertion만 proposition으로 승격하고 schema value 이름 자체를 자연어 사실로 추측하지 않는다.
- `use`와 `context`가 같은 proposition을 표현할 때만 merge/suppress할 수 있다.
- profile-required section과 prose emission은 분리한다. 각 body-plan role은 structural satisfaction ledger에서 `emitted_direct`, `satisfied_by_verified_fusion`, `satisfied_by_verified_suppression`, `not_required`, `missing` 중 하나와 applicable proposition/clause proof를 가진다. required role에 `not_required`를 사용할 수 없고 required role의 `missing`은 blocker다. 독립 문장을 생략해도 verified fusion/suppression이 있으면 body-plan application으로 인정하지만, 단순 `no_new_information` 문자열만으로는 인정하지 않는다.
- acquisition은 source가 허용하는 subtype을 보존한다. loot/craft/processing/general availability를 하나의 일반 문장으로 평탄화하지 않는다.
- transformation enum은 `reorder`, `merge_equivalent`, `suppress_duplicate`, `pronoun_or_zero_anaphora`, `particle_adjustment`, `copula_adjustment`, `paragraph_merge`처럼 닫힌 집합으로 만든다.
- `invent_fact`, `strengthen_modality`, `drop_qualifier`, `cross_item_copy`, `advice_conversion`은 항상 금지한다.
- fusion/suppression equivalence proof는 최소 다음 typed field를 가진다.

```text
equivalence_proof_schema_version
equivalence_proof_id
input_proposition_ids
surviving_clause_id
semantic_signature_set
qualifier_set
condition_set
modality_set
input_provenance_union
surviving_trace_provenance_set
proof_digest
```

- equivalence는 semantic signature, qualifier, condition, modality set이 정확히 같고 `input_provenance_union == surviving_trace_provenance_set`일 때만 성립한다. 부분집합 일치, 문자열 유사도, 동일 `semantic_key` 하나만으로는 충분하지 않다.
- `DVF Body Compiler PASS` 구성요소를 다음처럼 1:1 증거에 결속한다.

| PASS component | Artifact | Required predicate |
|---|---|---|
| deterministic realization | determinism comparison report | `candidate_two_run_determinism_pass` |
| body-plan application | structural satisfaction ledger | `unsatisfied_required_body_plan_role_count = 0` |
| rendered shape | rendered shape report | `rendered_shape_contract_pass` |
| source-provenance preservation | source inventory/coverage and semantic report | `source_to_proposition_coverage_pass` 및 `semantic_preservation_pass` |

**Validation**

- 모든 emitted clause는 하나 이상의 source proposition을 참조한다.
- source inventory hash가 candidate 생성 전 봉인되며 candidate/trace 입력 dependency count가 `0`이다.
- official food-semantic retry에서 Phase 2가 소비한 facts/manifest/schema/license SHA-256이 Phase 0 handoff binding 및 Registry-adopted current identity와 모두 일치한다.
- source-to-proposition coverage report가 approved source field universe를 누락 없이 inventory 또는 explicit non-proposition field ledger에 배정한다.
- 모든 transformation id는 policy registry에 존재한다.
- merge/suppression은 typed equivalence proof로 semantic signature, qualifier, condition, modality, provenance-set 동치를 증명해야 한다.
- required body-plan role의 ledger 누락과 proof 없는 fusion/suppression이 `0`이다.
- negative fixture에서 qualifier drop, role collision, cross-item proposition, unsupported acquisition inference가 fail-closed한다.
- trace schema가 candidate rendered schema와 분리되어 runtime payload에 나타나지 않는다.

### Change 3 — Deterministic Korean prose compiler

**Purpose**

현재 slot sentence assembler에 candidate-only discourse planning과 surface realization을 추가한다.

**Files**

- Modify:
  - `compose_layer3_text.py`
  - `compose_layer3_body_profile.py`
  - `compose_layer3_item.py`
  - `compose_layer3_render.py`
  - 필요 시 `compose_layer3_blocks.py`, `compose_layer3_identity.py`, `compose_layer3_io.py`
- Add focused compiler tests.
- Generate:
  - `phase3/compiler_contract_test_report.json`
  - `phase3/default_mode_regression_report.json`
  - `phase3/write_boundary_negative_test_report.json`

**Implementation Notes**

- public API는 default current behavior와 explicit candidate behavior를 분리한다.
- candidate prose mode는 다음 조건을 모두 요구한다.
  - `compose_context=staging`
  - exact policy path/hash
  - attempt-local rendered path
  - attempt-local trace path
  - current source manifest binding
- default mode에서 새 policy를 읽거나 새 output을 만들지 않는다.
- discourse ordering은 profile별 priority table과 information novelty로 결정한다.
- identity는 항상 독립 첫 문장으로 강제하지 않는다. 구체 use가 identity를 자연스럽게 포함할 수 있으면 결합한다.
- 같은 주어·identity noun 반복은 zero anaphora 또는 clause merge로 줄이되 referent가 모호해지면 원문을 유지한다.
- paragraph break는 section 수가 아니라 discourse topic/length/limitation transition 규칙으로 결정한다.
- 한국어 조사·copula helper는 제한된 deterministic morphology만 수행한다. 형태소 분석기나 확률 모델의 환경별 결과에 의존하지 않는다.
- rule priority, tie-breaker, ordering key를 정책에 명시하고 randomness를 금지한다.
- `StyleNormalizer`는 typography/확정된 low-level normalization에만 사용할 수 있다. source proposition을 고치거나 누락 의미를 복구하는 단계로 사용하지 않는다.
- 개별 item ID 조건문은 금지한다. item-specific exception count는 항상 `0`이어야 한다.

**Validation**

- legacy/current mode stable content의 normalized hash가 Phase 0 pre-change baseline과 일치한다.
- legacy volatile metadata의 field/type/format contract가 일치하며 value 자체의 byte identity는 요구하지 않는다.
- `legacy_raw_file_byte_identity_pass`는 `not_claimed`이고 protected current file no-mutation은 별도 hash 비교로 증명한다.
- candidate mode가 current output path, Lua path, runtime path, package path를 거부한다.
- gold corpus의 discourse/paragraph/semantic expectation을 만족한다.
- 동일 입력·정책·코드로 두 번 실행한 `candidate_rendered.json`과 trace가 각각 byte-identical하다.
- Python hash seed, locale, working directory가 달라도 stable ordering을 유지한다.
- current core module count와 tooling allowlist count가 변하지 않는다.

### Change 4 — Full-universe candidate regeneration

**Purpose**

sample 성공을 전체 item 성공으로 오인하지 않고 exact source universe를 candidate path로 생성한다.

**Files**

- Add:
  - `run_dvf_3_3_korean_prose_naturalization.py`
- Generate:
  - `phase4/candidate_rendered.json`
  - `phase4/candidate_proposition_trace.jsonl`
  - `phase4/candidate_manifest.json`
  - `phase4/unadopted_disposition.jsonl`
  - `phase4/full_universe_generation_report.json`
  - `phase4/protected_surface_after_snapshot.json`

**Implementation Notes**

- runner는 current input manifest를 read-only로 소비한다.
- source universe 전체 key를 enumerate한다.
- adopted candidate prose와 unadopted item을 별도 output/denominator로 유지한다.
- current 관찰값 `2105/2084/21`을 command 상수로 넣지 않는다.
- `candidate_rendered.json`은 기존 current rendered와 같은 JSON object schema를 유지하되, full-corpus candidate content를 담는 유일한 payload다. profile·strata별 candidate payload를 따로 만들지 않는다.
- candidate payload byte stream에는 wall-clock timestamp, attempt ID, 절대 경로를 넣지 않는다. 기존 `generated_at`과 같은 volatile 실행 metadata는 candidate manifest/receipt로 이동한다.
- candidate manifest는 code hash, realization policy hash, source manifest hash, **candidate-independent source proposition manifest hash**, body-plan requirement digest, corpus manifest hash, row count, key-set digest, **단일 candidate content hash**, trace hash와 실행 metadata를 기록한다.
- 두 clean attempt를 별도 directory에서 실행하고 directory-independent content hash를 비교한다.
- candidate content hash가 바뀌면 semantic, lint, human-review, acceptance, handoff evidence를 모두 stale로 처리한다.
- current rendered, Lua bridge, runtime chunks, package의 before/after hash를 비교한다.

**Validation**

- source key set = candidate manifest key set이다.
- adopted key set = candidate prose key set이고, unadopted key set과 disjoint하다.
- duplicate/missing/unknown item ID가 `0`이다.
- trace의 item/clause/proposition foreign key가 모두 resolve된다.
- candidate가 소비한 모든 proposition id가 pre-sealed source proposition inventory에서 resolve된다.
- two-run candidate content hash와 trace hash가 일치한다.
- candidate payload hash count는 정확히 `1`이다.
- payload 안의 volatile metadata field count가 `0`이다.
- protected surface mutation count가 `0`이다.

### Change 5 — Semantic preservation and adversarial closure

**Purpose**

자연스러운 표현이 source 의미를 추가·삭제·왜곡하지 않았음을 구조적으로 검증한다.

**Files**

- Add:
  - `validate_dvf_3_3_korean_prose_naturalization.py`
  - semantic-preservation tests
- Generate:
  - `phase5/semantic_preservation_report.json`
  - `phase5/proposition_resolution_ledger.jsonl`
  - `phase5/structural_satisfaction_ledger.jsonl`
  - `phase5/body_plan_application_report.json`
  - `phase5/rendered_shape_report.json`
  - `phase5/suppression_validity_report.json`
  - `phase5/transformation_frequency_report.json`
  - `phase5/adversarial_validation_report.json`

**Implementation Notes**

- string similarity는 참고 지표일 뿐 semantic PASS authority로 사용하지 않는다.
- 각 source proposition은 `proposition_resolution` namespace에서 `emitted`, `merged`, `suppressed_equivalent`, `not_applicable`, `blocked_by_source` 중 하나로 분류한다. 이는 `item_prose_disposition`이나 `aggregate_publish_disposition`과 다른 enum이다.
- `suppressed_equivalent`는 surviving clause와 exact equivalence proof를 가진다.
- `not_applicable`는 `source_role_not_required`, `profile_exclusion`, `body_plan_exclusion`, `non_emittable_metadata`의 닫힌 `not_applicable_reason` 중 하나를 반드시 가진다. Publish quality policy는 source proposition을 semantic `not_applicable`로 만들 수 없다.
- limitation/qualifier/condition/modality는 merge 후에도 별도 invariant로 확인한다.
- acquisition subtype과 source origin을 보존한다.
- negative fixture는 최소 다음 변조를 포함한다.
  - source에 없는 용도 삽입
  - `가능하다`를 `주로 사용한다`로 강화
  - limitation 삭제
  - context qualifier 삭제
  - 다른 item의 proposition 재사용
  - trace 없이 문장 삽입
  - invalid suppression reason
  - source/candidate key swap
- validator의 모든 `--require-*` mode는 `--no-write`를 요구하고 파일 생성·수정·receipt 갱신을 거부한다. 필요한 보고서는 선행 runner가 생성하며 validator는 읽기와 verdict 출력만 수행한다.

**Validation**

- emitted clause provenance completeness `100%`
- source-to-proposition extraction coverage `100%` 또는 sealed source schema가 명시한 non-proposition field ledger와 exact 합계가 성립한다.
- unresolved proposition reference `0`
- `not_applicable_without_reason_count = 0`
- `unsatisfied_required_body_plan_role_count = 0`
- `rendered_shape_contract_pass = true`
- `equivalence_proof_missing_or_mismatch_count = 0`
- forbidden transformation `0`
- unjustified suppression `0`
- qualifier/modality/limitation preservation failure `0`
- 모든 adversarial fixture가 expected failure reason으로 차단된다.
- count equality뿐 아니라 ordered key digest와 per-row source hash identity를 검증한다.

### Change 6 — Full-corpus raw detector measurement and residual evidence

**Purpose**

full candidate universe에서 raw detector/metric과 compiler-invalid pattern을 계산하되 blocker disposition을 만들지 않는 독립 evidence stage를 만든다.

**Files**

- Add style/policy tests.
- Generate:
  - `phase6/raw_detector_report.json`
  - `phase6/raw_detector_hit_ledger.jsonl`
  - `phase6/item_metric_ledger.jsonl`
  - `phase6/compiler_invalid_residual_report.json`

**Implementation Notes**

- DVF-local `korean_prose_policy.json`은 detector id, raw metric calculation, compiler-invalid pattern, realization constraint만 제공한다.
- Phase 6은 `blocking`, `advisory`, `human_only`, `accepted`, `deferred`를 산출하지 않는다. raw hit와 metric을 blocker/advisory/human-only로 해석하는 authority는 Phase 8의 sealed Publish policy binding에만 있다.
- ignored `tools/style/linter.py`, `baseline_scan.py`, `style_closeout_packet.py` 등은 Phase 1 inventory에서 재사용 가능한 algorithm만 분석한다. required test나 production runner가 이 파일을 import하지 않는다.
- full-corpus detector는 최소 다음을 측정한다.
  - duplicate proposition realization
  - repeated identity noun/window
  - banned internal abstraction
  - repeated skeleton concentration
  - paragraph fragmentation
  - overlong sentence
  - passive/translationese pattern
  - empty/filler sentence
- residual fix는 generic policy/compiler rule만 허용한다. item ID branch, item-specific replacement text, per-item phrase override count는 모두 `0`이어야 한다.
- `compiler_invalid_residual_report.json`은 compiler-invalid pattern의 잔여 count와 generic-rule ownership만 기록한다. public blocker/advisory/human-only 분류, item disposition 또는 Publish acceptance closure를 기록하거나 주장하지 않는다.

**Validation**

- raw detector denominator가 exact candidate key set과 일치한다.
- 모든 configured detector가 모든 eligible candidate row에 대해 hit/no-hit 또는 metric 값을 산출한다.
- compiler-invalid pattern count가 `0`이다. 이는 public-quality blocker disposition이 아니라 compiler contract failure다.
- translationese/passive detector hit가 별도 detector id/reason으로 보존되어 Phase 8에서 누락 없이 분류 가능하다.
- item-specific override/branch/text count가 `0`이다.
- raw detector completion이 machine blocker `0`, human-review PASS 또는 Publish acceptance PASS로 변환되지 않는다.

### Change 7 — Exact-hash denominator-qualified human review

**Purpose**

sealed policy가 요구하는 사람 검토 표본과 판정을 exact candidate hash에 결속하고, 그 결과의 claim 범위를 review denominator로 제한한다.

**Files**

- Generate:
  - `phase7/human_review_sample_manifest.json`
  - `phase7/human_review_binding_report.json`
  - `phase7/human_review_eligibility_report.json`
- Consume durable owner/reviewer input:
  - `.../human_review_decision.json`

**Implementation Notes**

- sample은 profile/family/origin/topology/raw-detector-risk strata와 Phase 0에 결속한 Publish foundation selection algorithm으로 뽑고, official sealed policy가 같은 algorithm hash를 ratify했는지 Phase 8에서 검증한다.
- manifest는 full candidate denominator, eligible review denominator, selected denominator, mandatory strata와 selection seed/rule을 기록한다.
- human reviewer는 readability, naturalness, semantic fidelity, public suitability를 별도 field로 판정한다.
- owner/reviewer identity는 운영 metadata일 뿐 compiler 기능, canonical output, policy meaning의 일부가 아니다.
- owner와 independent reviewer가 동일 주체인지, 정책의 독립성 요건을 충족하는지 eligibility report로 확인한다.
- reviewer artifact가 없으면 도구는 sample manifest까지만 만들고 `blocked_human_review_required`로 종료한다.
- candidate content hash가 바뀌면 sample, review decision, waiver를 모두 stale로 처리한다.

**Validation**

- human-review denominator와 full candidate denominator를 혼용하지 않는다.
- Phase 0에서 봉인한 selection algorithm hash와 required review denominator definition hash가 sample manifest binding과 일치한다.
- 동일 candidate/strata/policy 입력으로 sample key set과 ordered digest를 결정적으로 재생한다.
- required review denominator 안의 human-only blocker count가 `0`이다.
- review가 전수가 아니라면 corpus-wide human-only blocker count `0` claim이 생성되지 않는다.
- stale candidate hash에 대한 review/waiver는 거부한다.
- machine pass가 human pass를 대체하지 않는다.
- human pass가 semantic validator 또는 machine blocker failure를 override하지 않는다.

### Change 8 — Publish Boundary qualified acceptance

**Purpose**

compiler·raw detector/metric·human review가 만든 exact evidence bundle을 immutable cross-plan handoff로 만들고, 별도 Publish Boundary 계획의 fresh official Phase 0~7이 그 subject의 aggregate public-text disposition을 결정·봉인하도록 한 뒤 exact result를 역인계 받는다.

**Files**

- Generate:
  - `phase8/publish_acceptance_input.json`
  - `phase8/publish_acceptance_handoff_manifest.json`
  - `phase8/publish_handoff_readiness_report.json`
  - `phase8/publish_official_attempt_binding.json` (Publish attempt 생성 후)
  - `phase8/item_prose_disposition_ledger.jsonl` (Publish result에서 exact import)
  - `phase8/detector_disposition_mapping_report.json` (Publish result에서 exact import)
  - `phase8/publish_acceptance_result.json` (Publish result에서 exact import)
  - `phase8/acceptance_policy_binding_report.json` (Publish result에서 exact import)
  - `phase8/publish_acceptance_cross_plan_receipt.json`

**Implementation Notes**

- 이 change는 acceptance metric, threshold, waiver authority, aggregate enum을 새로 작성하지 않는다.
- 먼저 handoff-build substage가 exact candidate/source/code/realization-policy/foundation hash, semantic verdict, structural satisfaction, full-corpus raw detector report, human-review denominator와 verdict를 묶고 `requested_evaluation_subject_kind=dvf_3_3_korean_naturalization_candidate`를 선언한다.
- handoff readiness가 PASS하면 이 계획의 candidate와 Phase 0~7 evidence는 write-once로 동결된다. 이후 별도 Publish Boundary 계획이 새 `<publish-attempt-id>`로 공식 Phase 0부터 실행한다.
- official Publish Phase 2 policy projection은 이 계획 Phase 0에서 결속한 foundation projection과 byte-equivalent해야 한다. 다르면 candidate result를 만들지 않고 stale foundation/candidate로 반환한다.
- sealed Publish policy는 raw detector/metric을 `blocking`, `advisory`, `human_only`로 분류하고 threshold/waiver를 적용해 `item_prose_disposition`을 산출한다.
- item prose disposition은 `accepted`, `advisory_debt`, `blocked_by_source`, `deferred`를 사용할 수 있고, aggregate 결과는 별도 `aggregate_publish_disposition` namespace에서 sealed policy enum을 그대로 사용한다.
- `blocked_by_source`는 quality failure를 숨기는 waiver가 아니다. source limitation과 compiler limitation을 분리한다.
- `deferred`는 explicit out-of-scope DVF 3-3 facts-authority correction 또는 별도 Layer 4 QG debt를 서로 다른 owner namespace로 기록하고 exact owner-approved backlog ID/hash가 있을 때만 허용한다. Layer 3 facts 부족을 Layer 4 QG debt로 재분류할 수 없으며 compiler가 해결해야 할 translationese hit는 `deferred`로 이동할 수 없다.
- generic public-text policy가 naturalness candidate metrics, structural satisfaction 또는 required human-review denominator를 제외한다면 이 gate의 authority가 될 수 없다.
- `accepted`는 해당 candidate와 sealed policy에 대한 qualified disposition일 뿐 `Publish Boundary PASS`, current adoption, release authorization이 아니다.
- 이 계획은 Publish runner의 output을 복제 계산하지 않는다. `publish_acceptance_cross_plan_receipt.json`은 exact handoff hash, Publish attempt ID, evaluation subject hash, disposition hash, policy closure terminal hash를 참조하고 hash/schema/freshness 일치만 검증한다.

**Validation**

- handoff manifest가 Section 4의 required constituent를 모두 exact hash로 포함한다.
- Publish Phase 0 binding이 exact handoff hash와 candidate hash를 소비한다.
- policy path/hash/schema/owner ratification/independent review/freshness와 candidate-independent projection이 Phase 0 foundation binding과 일치한다.
- raw detector output, Publish blocker mapping, human review, aggregate acceptance가 서로 다른 artifact와 verdict field를 가진다.
- Publish-classified machine blocker count가 full candidate denominator에서 `0`이다.
- `unresolved_translationese_blocker_count = 0`이다.
- `deferred_translationese_blocker_count_outside_owner_approved_backlog = 0`이다.
- 모든 `deferred` row가 `dvf_3_3_facts_authority` 또는 별도 `layer4_qg` ownership을 명시하고 exact owner-approved backlog binding을 가진다. Layer 3 facts 부족 row의 owner가 `layer4_qg`이면 validation failure다.
- waiver denominator와 accepted/debt/source-blocked/deferred denominator를 별도 기록하고 expired/scope-mismatched waiver를 거부한다.
- 별도 Publish plan의 official Phase 0~7이 exact input을 소비해 aggregate `accepted`, live required gate adopted, policy closure complete를 반환해야 Change 9로 진행한다.
- acceptance result가 review denominator를 full-corpus human-review claim으로 확대하지 않는다.
- candidate/policy/source hash가 하나라도 바뀌면 acceptance result가 stale로 거부된다.
- candidate subject의 runtime parity `not_applicable`가 Registry Runtime Compatibility PASS나 current adoption으로 확대되지 않는다.

**Retry Protocol**

Publish-classified blocker, compiler-invalid residual, human blocker 또는 non-accepted aggregate disposition이 발견되면 naturalization attempt나 Publish attempt를 고쳐 쓰지 않는다.

1. 현재 naturalization attempt와 official Publish attempt를 각각 `failed_validation`, `not_accepted` 또는 `after_remediation`으로 닫고 candidate hash, handoff hash, failure ledger, review, waiver, acceptance와 predecessor evidence를 보존한다.
2. 새 naturalization attempt ID를 만들고 `predecessor_attempt_id`, predecessor bundle/hash, Publish attempt ID, retry reason과 변경된 generic rule/code/policy hash를 기록한다.
3. item-specific patch 없이 generic compiler/realization rule만 수정한다. DVF 3-3 facts authority, 별도 Layer 4 QG artifact 또는 Publish policy가 바뀌면 각 owner round의 새 sealed hash를 요구한다. 이 중 하나의 변경을 다른 namespace의 승인으로 대체하지 않는다.
4. 이전 candidate에 결속된 Phase 4–9 trace, semantic report, raw detector result, human review, waiver, acceptance, handoff packet은 전부 stale 처리한다.
5. compiler code/rule 변경이면 Phase 3을 다시 실행하고 Phase 4–8 handoff를 새 candidate hash로 재실행한다. source, body-plan, corpus 또는 foundation contract가 바뀌면 earliest affected phase부터 Phase 8까지 모두 재실행한다.
6. 새 immutable handoff마다 별도 fresh Publish Phase 0 attempt를 연다. prior Publish disposition/gate/closure를 재사용하지 않는다.
7. focused/default regression, semantic/equivalence, raw detector, human-review denominator, official Publish accepted disposition/closure를 포함한 required validation이 모두 새 attempt에서 통과한 뒤에만 Change 9로 진행한다.

Food Semantic Facts Authority successor가 원인인 retry에는 다음 추가 순서를 적용한다.

```text
sealed non-current successor
-> actual Phase 2 no-render compatibility probe only
-> separate Registry operational cutover and adoption receipt
-> fresh Naturalization attempt Phase 0
-> Phase 2 source inventory reseal
-> Phase 3 through Phase 8
-> fresh Publish Boundary Phase 0 attempt
```

Registry adoption 전의 Phase 2 probe를 official naturalization Phase 2 또는 Phase 4~8 진입 근거로 재사용할 수 없다.

### Change 9 — Required gate, Registry handoff, and closeout

**Purpose**

exact accepted Publish result를 소비한 candidate compiler closure를 별도의 지속 검증 가능한 gate로 만들고, Registry eligibility/readiness claim 없이 검증 packet만 조립한다.

**Files**

- Candidate/additive modification:
  - `Iris/_docs/round3/current_route_required_validations.json`
- Create:
  - `docs/dvf_3_3_korean_prose_claim_boundary.md`
  - `docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closeout.md`
  - durable governance artifacts listed in Section 5
- Pre-freeze terminal-bundle additive docs update:
  - `docs/DECISIONS.md`
  - `docs/ARCHITECTURE.md`
  - `docs/ROADMAP.md`
- Explicitly read-only:
  - `docs/EXECUTION_CONTRACT.md`

**Implementation Notes**

- 이 계획은 Section 5의 top documents를 terminal bundle에 포함하는 **Option A**만 사용한다. successor docs-sync 방식과 혼용하지 않는다.
- Change 9 진입 전에 Publish Boundary official attempt가 exact Phase 8 handoff subject에 대해 `qualified_disposition=accepted`, `policy_closure_state=complete`, `live_required_gate_adopted=true`를 반환해야 한다.
- 이 change가 추가하는 required validation은 DVF Korean prose compiler/handoff gate다. Publish Boundary 계획이 이미 소유한 public-text acceptance gate를 복제·수정·재분류하지 않는다.
- gate test는 standalone runner/validator를 subprocess로 실행한다. 새 build tool을 current core import graph에 넣지 않으며 current core count `12`, tooling allowlist max `1`을 보존한다.
- candidate artifact는 Registry current authority가 아니다.
- Registry handoff receipt의 `packet_status = complete`는 필수 파일·hash·schema가 완비됐다는 receipt metadata일 뿐 Registry eligibility/readiness claim이 아니다. receipt는 다음만 말한다.
  - exact candidate/policy/source/code hashes
  - compiler PASS의 네 구성요소별 artifact/predicate
  - semantic, raw detector, Publish-classified machine blocker, denominator-qualified human-review, qualified-acceptance verdict
  - translationese terminal predicate와 backlog binding
  - deterministic regeneration command
  - current output 미변경
  - adoption prerequisite와 책임 owner
- pre-freeze closeout/top-doc patch는 owner seal 또는 terminal seal이 이미 완료됐다고 단정하지 않는다. `owner_seal.json`의 canonical path와 그 hash가 post-seal external `closure_receipt.json`에서 결속된다는 조건부 참조만 기록한다.
- closeout claim scanner는 bare `DVF PASS`, `DVF System PASS`, `Publish Boundary PASS`, `Registry handoff eligibility/readiness`, `current adoption complete`, corpus-wide human-only blocker `0`, pre-freeze `owner seal complete`/`terminal seal complete`/`closure sealed` 단정 표현을 금지한다.
- terminal independent reviewer는 roadmap 작성, upstream source review, 이 plan review 또는 구현 owner 역할에 참여하지 않은 별도 주체여야 한다.
- Registry promotion은 별도 round에서만 가능하다.

canonical terminal sequence는 다음 순서 하나뿐이다.

1. implementation, candidate, semantic, detector, human-review, Phase 8 handoff와 exact Publish accepted disposition/closure artifact를 freeze-ready 상태로 만든다.
2. required-manifest candidate patch를 sandbox에서 검증한다.
3. informed owner authorization 후 live required-validation gate를 additive하게 채택한다. 이는 Registry candidate adoption이 아니다.
4. post-required-gate-adoption current route를 실행해 exit `0` 결과를 만든다.
5. closeout/claim-boundary 문서와 허용된 `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md` additive patch를 모두 적용한다. `EXECUTION_CONTRACT.md`는 수정하지 않는다.
6. Validation 13의 Lua syntax와 Validation 14의 VCS/artifact durability를 **이 시점에 pre-freeze 검사로** 실행해 exit `0` report를 만든다. 번호상 뒤에 있어도 post-seal 검사가 아니다.
7. post-final current route와 claim scan을 실행해 exit `0` 결과를 만든다.
8. final docs/top-doc hashes, Lua/VCS pre-freeze reports, post-final evidence, candidate/acceptance/packet manifests를 포함하는 exact terminal bundle manifest를 생성하고 `terminal_bundle_hash`를 동결한다.
9. eligible independent reviewer가 동결된 `terminal_bundle_hash`를 검토하고 append-only independent-review attestation을 제공한다.
10. owner가 같은 `terminal_bundle_hash`와 independent-review attestation hash에 결속한 append-only owner seal을 제공한다.
11. terminal validator가 같은 frozen bundle, independent review, owner seal을 `--no-write`로 검증한다.
12. terminal validator exit `0` 뒤 외부 receipt recorder가 bundle 밖의 append-only `closure_receipt.json`에 bundle/review/seal hash와 validator command/exit/output digest를 기록한다. 이 receipt는 terminal PASS를 재판정하지 않는다.

Step 8 이후 frozen bundle 안의 claim-bearing artifact는 수정하지 않는다. final/top-doc 또는 pre-freeze/post-final evidence 수정이 필요하면 terminal sequence를 계속하지 않고 새 attempt와 새 bundle hash로 되돌아간다. Step 9–10 attestation과 Step 12 receipt는 frozen payload를 변경하지 않고 그 hash만 참조한다.

**Validation**

- candidate manifest sandbox run이 existing required artifacts/tests를 제거하거나 재분류하지 않는다.
- owner authorization 없이 live manifest hash가 바뀌지 않는다.
- post-required-gate-adoption 및 post-final legacy combined current route가 exit `0`이다.
- focused tests와 full current route가 closure enforcement를 유지한다.
- durable required inputs/artifacts는 tracked 또는 clean-checkout deterministic regeneration contract를 가진다.
- Registry handoff receipt가 eligibility/readiness/promotion/adoption claim을 포함하지 않고 `packet_status = complete`만 receipt metadata로 사용한다.
- translationese terminal predicate와 네 개 compiler PASS 구성요소가 claim-evidence matrix에서 모두 resolve된다.
- Lua/VCS 보강 검사가 bundle freeze 전에 exit `0`이고 두 pre-freeze report hash가 terminal bundle manifest에 포함된다.
- terminal bundle manifest가 final docs, 허용된 top docs, Lua/VCS pre-freeze report, post-final route result와 claim-scan result의 exact hash를 포함한다.
- independent review, owner seal, terminal no-write validation이 모두 동일한 `terminal_bundle_hash`를 참조한다.
- owner seal이 independent-review attestation hash를 참조한다.
- pre-freeze final/top-doc의 seal-complete 단정 표현 count가 `0`이다.
- `closure_receipt.json`은 frozen bundle 밖의 post-seal external additive receipt이고 terminal PASS claim authority를 갖지 않는다.
- `terminal_bundle_post_freeze_mutation_count = 0`이고 terminal seal 뒤 동일 closure의 claim-bearing artifact 변경 count도 `0`이다.

## 7. Validation Plan

### Automated Validation

실행 시 실제 CLI schema가 이 계획과 달라지면 command를 임의로 맞춰 성공시키지 않는다. tool help/schema와 plan을 함께 갱신하고 owner-reviewed command matrix를 봉인한다.

`validate_dvf_3_3_korean_prose_naturalization.py`의 모든 `--require-*` invocation은 `--no-write`를 함께 요구한다. validator가 파일을 생성·수정하거나 receipt를 갱신하면 해당 validation은 실패다.

#### 1. Preflight and baseline

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --mode phase0-preflight
uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --require-phase0 --require-execution-contract --require-publish-foundation-contract --no-write
```

이 단계가 `blocked_prerequisite` 또는 non-zero로 끝나면 아래 2–14번을 실행하지 않는다.

#### 2. Census and corpus validation

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --mode phase1-census
uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --require-phase1 --no-write
```

#### 3. Candidate-independent source proposition inventory

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --mode phase2-source-inventory
uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --require-source-proposition-inventory --require-body-plan-contract --no-write
```

#### 4. Focused compiler/policy tests

```powershell
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_3_3_korean_prose_*.py"
```

#### 5. Existing compose no-regression tests

```powershell
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_compose*.py"
uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --mode phase3-compiler-evidence
uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --require-phase3 --no-write
```

#### 6. Full candidate generation and deterministic replay

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id-a> --mode phase4-candidate
uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id-b> --mode phase4-candidate
uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id-a> --compare-attempt <attempt-id-b> --require-phase4 --no-write
```

#### 7. Semantic and adversarial validation

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --mode phase5-semantic
uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --mode phase5-adversarial
uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --require-phase5 --no-write
```

#### 8. Full-corpus raw detector completeness

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --mode phase6-raw-detectors
uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --require-raw-detector-completeness --no-write
```

#### 9. Exact-hash human-review binding

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --mode phase7-human-review-sample
uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --require-human-review --no-write
```

#### 10. Publish Boundary qualified acceptance

먼저 immutable handoff를 만든 뒤, synchronized Publish Boundary 계획의 exact official runner/validator command로 별도 `<publish-attempt-id>`의 Phase 0~7을 실행한다. 이 계획이 임의 경로나 enum을 다시 정의하거나 Publish output을 자체 재계산하지 않는다.

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --mode phase8-publish-handoff
uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --require-publish-handoff-ready --no-write
uv run python -B Iris/build/description/v2/tools/build/run_public_text_quality_acceptance.py --attempt-id <publish-attempt-id> --mode phase0-binding --evaluation-subject-kind dvf_3_3_korean_naturalization_candidate --subject-handoff <phase8-publish-handoff-manifest>
<continue synchronized Publish Boundary Phase 1 through Phase 7 exact commands>
uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --mode phase8-consume-publish-result --publish-attempt-id <publish-attempt-id>
uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --require-qualified-acceptance --no-write
```

Publish result가 non-accepted이거나 closure incomplete이면 11–14번을 실행하지 않는다. exact failure ledger를 보존하고 Retry Protocol에 따라 새 naturalization candidate와 새 Publish attempt를 만든다.

#### 11. Candidate required-manifest route

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --mode phase9-gate-candidate
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --required-validations <candidate-manifest> --out <attempt-root>/phase9/candidate_current_route_result.json
```

#### 12. Canonical Option A terminal sequence

먼저 owner가 live required-validation gate의 additive adoption을 승인한 뒤 post-required-gate-adoption route를 실행한다.

```powershell
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --out <attempt-root>/phase9/post_required_gate_adoption_current_route_result.json
```

그 다음 closeout/claim-boundary 문서와 허용된 top-doc patch를 모두 적용한다. `EXECUTION_CONTRACT.md`는 수정하지 않는다.

문서 변경이 끝나면 아래에 번호상 후행하는 Validation 13과 14를 먼저 실행한다. phase9 orchestrator는 exact command, exit code, tool version, output digest와 worktree ownership scope를 각각 `pre_freeze_lua_syntax_report.json`, `pre_freeze_vcs_durability_report.json`에 기록한다. 두 결과가 exit `0`일 때만 다음을 순서대로 실행한다.

```powershell
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --out <attempt-root>/phase9/post_final_current_route_result.json
uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --mode phase9-claim-scan
uv run python -B Iris/build/description/v2/tools/build/run_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --mode phase9-freeze-terminal-bundle
uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --require-post-final --require-claim-scan --require-terminal-bundle-freeze --no-write
```

이제 frozen `terminal_bundle_hash`에 결속한 eligible independent-review attestation을 외부 reviewer가 제공한다. 그 뒤:

```powershell
uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --terminal-bundle-hash <terminal-bundle-hash> --require-independent-review --no-write
```

owner는 같은 bundle hash와 위 independent-review attestation hash를 참조하는 owner seal을 제공한다. 마지막 명령은 어떤 artifact도 쓰지 않는다.

```powershell
uv run python -B Iris/build/description/v2/tools/build/validate_dvf_3_3_korean_prose_naturalization.py --attempt-id <attempt-id> --terminal-bundle-hash <terminal-bundle-hash> --require-independent-review --require-owner-seal --require-terminal-seal --no-write
```

마지막 명령이 exit `0`이면 validator와 분리된 external receipt recorder가 Section 5 schema의 `closure_receipt.json`을 append한다. 이 post-seal write는 frozen bundle 밖에서 일어나며 bundle hash나 terminal PASS를 변경하지 않는다.

#### 13. Lua and protected-surface no-regression

이 검사는 번호상 12번 뒤에 표시되지만 실제 실행 위치는 canonical terminal sequence Step 6, 즉 post-final 검증과 bundle freeze 전이다.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Lua syntax exit `0`은 Lua syntax no-regression 보강일 뿐 runtime behavior나 package release PASS가 아니다.

#### 14. VCS and artifact durability

이 검사도 canonical terminal sequence Step 6에서 실행하는 필수 pre-freeze durability 검사다. required artifact tracking/ignore 상태가 확인되기 전에는 terminal bundle을 freeze하지 않는다.

```powershell
git diff --check
git diff --stat
git diff
git status --short
git ls-files --error-unmatch <required-path>
git check-ignore -v <required-path>
```

`git check-ignore`는 ignore-rule 판정용이며 일반적인 command exit만으로 artifact PASS를 결정하지 않는다.

### Manual Validation

- owner가 roadmap binding과 scope/non-scope를 검토한다.
- Korean prose standard와 gold corpus를 한국어 품질 관점에서 검토한다.
- human-review sample은 exact candidate hash와 strata manifest에 결속한다.
- reviewer는 다음을 별도 field로 판정한다.
  - 사실 보존
  - 문장 자연스러움
  - 정보 순서
  - 중복 억제
  - 획득/제한 의미 보존
  - 3-3/3-4 경계 준수
  - public text suitability
- Publish-owned `item_prose_disposition`의 blocked/advisory/deferred row는 reason code와 source/compiler/policy ownership을 확인한다.
- independent reviewer는 owner approval을 복제하지 않고 evidence completeness와 claim boundary를 검토한다.
- terminal independent reviewer의 upstream roadmap/plan-review/implementation 참여 count가 `0`인지 확인한다.
- Registry owner는 handoff receipt의 `packet_status`가 eligibility/readiness/promotion을 전제하지 않는지 확인한다.
- final/top-doc patch가 seal 완료를 단정하지 않고 owner-seal path 및 external closure-receipt binding을 조건부로 표현하는지 확인한다.
- Lua/VCS pre-freeze report가 frozen terminal bundle manifest에 포함됐는지 확인한다.
- post-seal `closure_receipt.json`이 bundle/review/owner-seal/validator digest만 기록하고 terminal verdict를 재정의하지 않는지 확인한다.

### Validation Limits

- deterministic/semantic/style test는 실제 게임 UI에서의 줄바꿈, 폰트, 화면 폭을 검증하지 않는다.
- Lua syntax 검사는 runtime chunk 내용이 변경되지 않았다는 hash proof를 대신하지 않는다.
- human sample review는 전수 semantic proof를 대신하지 않는다.
- human review가 전수가 아니면 human-only blocker `0`은 required review denominator에만 적용된다. corpus-wide human-only blocker `0`은 주장하지 않는다.
- 전수 raw detector/metric과 Publish-classified machine blocker 검사는 한국어 자연스러움에 대한 사람 판단을 완전히 대체하지 않는다.
- current-route PASS는 Registry Authority, Runtime Compatibility, Publish Boundary의 개별 PASS를 자동으로 의미하지 않는다.
- candidate acceptance는 current adoption 또는 package release authorization이 아니다.
- planning-time `2105/2084/21` 및 품질 count는 terminal evidence가 아니다.
- source 자체가 모호한 proposition은 `proposition_resolution.blocked_by_source`, 해당 item은 별도 `item_prose_disposition.blocked_by_source`가 될 수 있다. compiler가 사실을 보강하지 않으며 aggregate accepted 가능 여부는 sealed Publish policy가 결정한다.

## 8. Risk Surface Touch

### Authority Surface

- source facts/decisions/overlay/profile은 read-only다.
- semantic content authority는 approved facts/decisions/source-supported overlay fields에 있고 profile/`body_plan`은 structural authority에 한정된다.
- 새 prose policy는 surface realization, raw detector/metric, compiler-invalid pattern authority만 가지며 public blocker/disposition authority는 갖지 않는다.
- Publish acceptance policy는 별도 owner와 seal을 유지한다.
- candidate output은 Registry current authority가 아니다.
- roadmap, quality standard, gold corpus, waiver, review는 각각 exact provenance를 가진다.

### Runtime Behavior Surface

- current runtime behavior 변경: **None**.
- current rendered, Lua bridge, runtime chunks, package는 protected read-only surface다.
- candidate mode는 staging path만 허용한다.
- trace/style/disposition metadata는 runtime payload에 들어가지 않는다.
- runtime QA와 deployment는 별도 Registry/Publish workflow로 남는다.

### Compatibility Surface

- 영향 수준: **Limited / additive**.
- default current composer의 normalized stable content hash와 volatile metadata contract를 보존한다. raw output byte identity는 주장하지 않는다.
- 단일 candidate rendered JSON object의 Registry-consumable 최소 schema는 유지하되 trace는 sidecar로 분리한다.
- exact item ID 대소문자와 key identity를 보존한다.
- 12-module core closure와 1-module tooling allowlist를 유지한다.
- live required manifest 변경은 additive-only다.

### Sealed Artifact Surface

- 기존 closure evidence와 staging history를 수정하지 않는다.
- final/top-doc 및 post-final evidence를 포함해 먼저 frozen terminal bundle hash를 만든 뒤 independent review와 owner seal을 그 동일 hash에 순서대로 결속한다.
- `EXECUTION_CONTRACT.md`는 prerequisite hash로 참조할 뿐 frozen bundle을 만들기 위해 수정하지 않는다.
- post-seal `closure_receipt.json`은 frozen bundle 밖의 operational trace이며 terminal PASS authority가 아니다.
- stale review, stale waiver, stale policy, stale source manifest는 fail-closed한다.
- sealed artifact를 다시 생성하거나 덮어쓰지 않고 새 attempt를 append한다.

### Public-Facing Output Surface

- current public-text surface 변경: **None**.
- staging candidate public-text surface: **Major**.
- 모든 candidate clause는 source proposition trace를 가진다.
- 추천, 비교, 조작 절차, unsupported claim을 금지한다.
- public-text acceptance는 machine/human/policy 증거가 모두 있는 경우에만 주장한다.
- quality metadata 자체는 공개 설명문에 포함하지 않는다.

## 9. Risk Analysis

### Architecture Risks

**Core closure 우회**

새 helper module을 추가하면 current core closure가 암묵적으로 확장될 수 있다. 기존 core module 내부 candidate-only implementation과 standalone subprocess orchestration을 사용하며, import graph/count 검사를 required test로 둔다.

**DVF와 Publish Boundary 책임 재혼합**

compiler가 detector hit를 blocker로 분류하거나 threshold/waiver를 소유하면 architecture 분리가 무너진다. prose policy는 realization/raw metrics/compiler-invalid rules만, Publish policy는 blocker mapping/threshold/waiver/item·aggregate disposition만 소유하도록 schema와 claim을 분리한다.

**structural body plan과 public prose shape 혼동**

required section을 paragraph 수로 강제하면 현재 문제가 반복된다. structural satisfaction과 discourse emission을 분리하고 suppression trace를 요구한다.

**ignored prototype의 권위화**

로컬 style prototype이 유용해 보여도 clean checkout에서 사라질 수 있다. algorithm만 검토하여 tracked code/policy/test로 재구현하고 import를 금지한다.

**terminal bundle 조기 freeze 또는 사후 mutation**

final docs나 post-final evidence보다 먼저 bundle을 freeze하거나 review/seal 뒤 문서를 바꾸면 attestation 대상이 갈라진다. Option A 순서, exact file/hash manifest, post-freeze mutation count `0`, 변경 시 새 attempt 규칙으로 차단한다.

### Runtime Risks

**candidate mode가 current path에 쓰기**

path typo나 default argument로 current output을 덮어쓸 수 있다. staging context, attempt root, forbidden-path realpath guard, before/after protected hash를 동시에 요구한다.

**trace metadata leakage**

새 field가 Lua/runtime bridge로 전달될 수 있다. candidate prose와 trace sidecar를 분리하고 current exporter가 candidate trace를 거부하는 fixture를 둔다.

**환경 의존 비결정성**

set/dict ordering, locale, newline, path, Python hash seed가 결과를 바꿀 수 있다. explicit sort key, UTF-8/LF contract, stable JSON serialization, two-attempt comparison을 사용한다.

### Compatibility Risks

**legacy output drift**

candidate helper가 default path에 영향을 줄 수 있다. import 시 side effect를 금지하고 pre-change normalized golden content hash, volatile metadata contract, protected current file no-mutation을 각각 gate에 포함한다.

**item key 정규화 충돌**

대소문자나 띄어쓰기 normalizing으로 distinct ID가 합쳐질 수 있다. exact-key equality를 사용하고 `Base.LemonGrass`/`Base.Lemongrass` coexistence fixture를 유지한다.

**Registry handoff schema 불일치**

candidate가 현 Registry consumer가 읽지 못하는 형식일 수 있다. 기존 rendered schema를 보존하고 추가 evidence는 sidecar/manifest로 분리한다.

**live required manifest 과대 확장**

새 tests/artifacts가 기존 route를 불필요하게 재분류할 수 있다. candidate manifest sandbox, additive diff, existing entry equality, owner-authorized single writer를 요구한다.

### Regression Risks

**중복 제거가 의미 제거가 됨**

use/context가 유사해 보여도 qualifier가 다를 수 있다. semantic identity에 qualifier/condition/modality를 포함하고 unjustified suppression을 0으로 강제한다.

**acquisition 문장 자연화가 사실 평탄화가 됨**

획득 경로 subtype을 proposition으로 유지하고 일반 availability 문장으로의 합성을 금지한다.

**자연스러움 규칙의 과적용**

명사 반복 제거가 지시 대상 모호성을 만들 수 있다. ambiguity guard가 실패하면 더 보수적인 원문형 realization을 택한다.

**gold corpus overfitting**

gold만 통과하는 item-specific rule이 생길 수 있다. item ID branch count 0, regression/negative corpus, full-universe pattern distribution을 함께 검사한다.

**source limitation을 compiler 성공으로 위장**

`item_prose_disposition.blocked_by_source` row를 accepted row와 섞지 않고 별도 denominator와 reason owner를 기록한다. 같은 문자열의 `proposition_resolution` 값과 namespace로 구분한다.

**planning-time count 고정**

2105/2084/21을 상수화하면 live drift를 숨긴다. source manifest와 actual key set에서 모든 denominator를 재계산한다.

**사용자 작업 덮어쓰기**

기존 dirty staging과 untracked plan을 보호 ledger에 넣고 declared mutation allowlist 밖 쓰기를 실패 처리한다.

## 10. Rollback

이 round는 candidate-only이므로 기본 rollback은 current payload 복구가 아니라 **candidate closeout disposition 무효화와 additive change 철회**다.

1. 실패한 attempt를 `invalidated`로 표시하고 증거를 보존한다. sealed attempt를 삭제하거나 덮어쓰지 않는다.
2. live required manifest가 채택되었다면 이 round의 additive entry만 owner-approved diff로 제거하거나 non-current candidate 상태로 되돌린다.
3. composer 변경은 candidate mode commit 범위만 revert한다. 사용자 변경과 기존 closure artifact는 건드리지 않는다.
4. `.gitignore` 변경은 이 round의 exact unignore rule만 되돌린다.
5. terminal bundle freeze 전 final/top-doc patch는 rollback diff로 되돌릴 수 있다. freeze 후에는 같은 attempt의 문서나 bundle을 수정하지 않고 predecessor hash를 가진 새 attempt/supersession trace를 만든다.
6. owner/reviewer seal은 삭제하지 않고 `superseded_by` 또는 `invalidated_reason`을 가진 새 record로 무효화한다.
7. Registry handoff packet을 아직 외부 round가 소비하지 않았다면 새 supersession receipt에서 `packet_status = invalidated`로 표시한다. eligibility/readiness claim은 생성하지 않는다.
8. Registry가 별도 round에서 이미 adoption했다면 이 계획에서 current output을 되돌리지 않는다. Registry rollback contract를 호출하는 별도 승인된 작업이 필요하다.
9. protected surface mutation이 발견되면 즉시 중단하고 before snapshot과 비교해 exact target을 확인한 뒤 사용자 승인을 받아 복구한다.
10. retry는 기존 attempt를 reopen하지 않고 새 attempt ID와 predecessor hash를 사용한다. 이전 candidate-bound review/waiver/acceptance/packet은 stale 처리하고 Change 8의 earliest-affected-phase rerun protocol을 적용한다.
11. post-seal `closure_receipt.json` 정정은 원본을 수정하지 않고 `supersedes`가 있는 새 external receipt로만 기록한다.

Rollback 후 검증:

- default composer normalized stable content hash와 volatile metadata contract가 Phase 0 baseline과 일치한다.
- legacy raw file byte identity는 계속 `not_claimed`이며 protected current file no-mutation hash는 별도로 일치한다.
- current rendered/Lua/runtime/package protected hash가 baseline과 일치한다.
- current core module/allowlist count가 원래 값이다.
- current required route가 exit `0`이다.
- candidate gate가 live authority나 current adoption으로 남아 있지 않다.
- rollback/terminal validator는 `--no-write`이고 frozen predecessor evidence를 수정하지 않는다.

## 11. Governance Constraints

- `docs/Philosophy.md`의 사실 기반, 게임 내부 관찰 가능성, 비추천/비비교 원칙을 위반하지 않는다.
- `docs/EXECUTION_CONTRACT.md`의 path/hash/checked-state/conflict count를 Phase 0 evidence에 포함하며 conflict count가 `0`이 아니면 진행하지 않는다.
- `docs/EXECUTION_CONTRACT.md`는 read-only prerequisite이며 final/top-doc patch와 terminal bundle mutation target에서 제외한다.
- 3-3은 item description이고 3-4 procedure/action guide가 아니다.
- source authority, compiler realization, Registry authority, runtime compatibility, Publish acceptance의 책임을 합치지 않는다.
- Publish foundation readiness를 official policy seal/disposition/closure로 표현하지 않으며, official Publish Phase 0은 immutable Phase 8 handoff 뒤에만 시작한다.
- synchronized candidate의 non-accepted Publish result는 `after_remediation`으로 반환하고 blocked-immediate adoption을 사용하지 않는다.
- Publish official result를 이 계획에서 재계산하거나 복제하지 않고 exact attempt/disposition/terminal hash만 역인계한다.
- `current_route_required_validations.json = legacy_combined_governance_route != DVF System PASS authority`를 유지한다.
- bare `DVF PASS`, `DVF System PASS`, unqualified `accepted`, unqualified `complete`를 금지한다.
- current core closure 12 module과 tooling allowlist 1 module은 별도 승인 없이 확장하지 않는다.
- 새 round tool/test는 current route에서 subprocess-only로 소비한다.
- source/rendered/runtime/package writer authority는 이 계획에 없다.
- current payload mutation은 항상 금지한다.
- roadmap materialization, quality standard, corpus, policy, review, waiver, adoption, seal은 각각 owner와 provenance를 기록한다.
- owner와 independent reviewer 역할을 자동 재분류하지 않는다.
- author/reviewer의 개인 식별자와 작업 chain metadata는 운영 provenance일 뿐 canonical compiler 기능이나 public-text 의미 authority가 아니다.
- stale input, missing artifact, schema mismatch, hash mismatch, denominator mismatch는 fail-closed한다.
- numerator/denominator equality만으로 identity equality를 주장하지 않는다.
- waiver는 exact metric/item/candidate hash/expiry/scope를 가져야 한다.
- human approval은 machine semantic failure를 override할 수 없다.
- raw detector completion이나 Publish-classified machine PASS는 human-review 완료를 뜻하지 않는다.
- `item_prose_disposition.blocked_by_source`는 새 source fact를 만들 권한을 주지 않는다.
- `proposition_resolution`, `item_prose_disposition`, `aggregate_publish_disposition`을 서로 변환할 때는 sealed mapping과 provenance를 요구한다.
- 모든 `--require-*` validator mode는 `--no-write`이며 rollback/terminal 검증도 artifact를 수정하지 않는다.
- candidate rendered와 trace/style metadata를 runtime에 함께 배포하지 않는다.
- existing dirty worktree 파일은 사용자 소유로 보존한다.
- required artifact가 ignored/untracked라면 tracked exact path 또는 clean-checkout deterministic regeneration contract 없이 closure하지 않는다.
- closeout/claim-boundary 및 허용된 top-level docs patch는 post-required-gate-adoption 검증 뒤, post-final 검증과 terminal bundle freeze 전에만 적용한다.
- pre-freeze closeout/top-doc는 owner/terminal seal 완료를 단정하지 않고 canonical owner-seal path와 post-seal `closure_receipt.json` hash binding 조건만 기록한다.
- Lua syntax와 VCS/artifact durability는 final/top-doc patch 뒤, post-final 검증과 bundle freeze 전에 실행하고 그 report hash를 terminal bundle에 포함한다.
- post-final route와 claim scan을 통과한 final/top-doc hash를 terminal bundle에 포함한 뒤 freeze한다.
- independent review와 owner seal은 같은 frozen `terminal_bundle_hash`에 순서대로 결속하며, terminal `--no-write` 검증은 그 뒤에만 수행한다.
- terminal bundle freeze 이후 동일 closure의 claim-bearing artifact를 수정하지 않는다. 변경이 필요하면 새 attempt와 새 bundle hash를 만든다.
- `closure_receipt.json`은 terminal validator exit `0` 뒤 외부 recorder가 frozen bundle 밖에 append하며 terminal verdict를 만들거나 변경하지 않는다.
- 계획 작성은 roadmap/policy/corpus/adoption/seal에 대한 owner 승인을 대체하지 않는다.

## 12. Expected Closeout State

목표 terminal state는 `complete`이며 다음이 모두 참이어야 한다.

```text
roadmap_provenance_bound = true
plan_review_feedback_bound = true
cycle2_plan_review_feedback_bound = true
synchronization_contract_id = dvf3_3_korean_naturalization__publish_boundary_sync_v1
cross_plan_sync_projection_hash_match = true
execution_contract_checked = true
execution_contract_conflict_count = 0
execution_contract_mutation_count = 0
publish_foundation_contract_ready_for_remediation = true
publish_foundation_authority_effect = none
publish_foundation_official_disposition = not_issued
publish_foundation_live_gate_adopted = false
publish_foundation_policy_closure_state = not_started
publish_foundation_hash_bound = true
publish_foundation_runner_contract_pass = true
publish_acceptance_policy_sealed_and_fresh = true
publish_official_policy_runner_contract_pass = true
human_review_selection_algorithm_bound = true
required_human_review_denominator_bound = true
source_manifest_identity_pass = true
source_universe_rederived = true
candidate_mode_staging_only = true
legacy_normalized_content_hash_identity_pass = true
legacy_metadata_contract_pass = true
legacy_raw_file_byte_identity_pass = not_claimed
protected_current_file_no_mutation_pass = true
candidate_full_universe_generation_pass = true
candidate_artifact_granularity = one_immutable_full_corpus
candidate_content_hash_count = 1
candidate_volatile_metadata_field_count = 0
candidate_two_run_determinism_pass = true
semantic_proposition_content_authority = approved_facts_decisions_source_supported_fields
structural_authority = profile_body_plan
profile_body_plan_generated_semantic_proposition_count = 0
current_surface_snapshot_semantic_authority = false
source_proposition_inventory_candidate_dependency_count = 0
source_to_proposition_coverage_pass = true
semantic_preservation_pass = true
unsatisfied_required_body_plan_role_count = 0
rendered_shape_contract_pass = true
phase3_compiler_evidence_pass = true
forbidden_transformation_count = 0
unjustified_suppression_count = 0
equivalence_proof_missing_or_mismatch_count = 0
not_applicable_without_reason_count = 0
protected_surface_mutation_count = 0
item_specific_patch_count = 0
item_specific_override_count = 0
tracked_policy_and_corpus_pass = true
raw_detector_full_candidate_completeness_pass = true
compiler_invalid_pattern_count = 0
publish_classified_machine_blocker_count_full_candidate = 0
unresolved_translationese_blocker_count = 0
deferred_translationese_blocker_count_outside_owner_approved_backlog = 0
human_review_exact_hash_pass = true
human_review_blocker_count_within_required_denominator = 0
corpus_wide_human_only_blocker_zero_claimed = false
publish_acceptance_handoff_manifest_frozen = true
publish_acceptance_handoff_hash_bound = true
publish_official_attempt_id_bound = true
publish_evaluation_subject_kind = dvf_3_3_korean_naturalization_candidate
publish_evaluation_subject_hash_match = true
publish_consumed_handoff_hash_match = true
publish_consumed_foundation_hash_match = true
qualified_public_text_disposition = accepted
publish_policy_closure_state = complete
publish_live_required_gate_adopted = true
publish_registry_runtime_current_adoption_claimed = false
current_core_module_count = 12
current_route_allowed_tooling_module_count = 1
registry_handoff_packet_complete = true
registry_handoff_eligibility_claimed = false
registry_current_adoption_claimed = false
runtime_release_claimed = false
post_required_gate_adoption_current_route_pass = true
final_docs_and_top_docs_applied_before_bundle_freeze = true
pre_freeze_top_doc_seal_complete_assertion_count = 0
pre_freeze_lua_syntax_pass = true
pre_freeze_vcs_artifact_durability_pass = true
post_final_current_route_pass = true
post_final_claim_scan_pass = true
terminal_bundle_frozen = true
terminal_bundle_hash_bound = true
terminal_bundle_includes_final_docs_top_docs_and_post_final_evidence = true
terminal_bundle_includes_pre_freeze_lua_vcs_report_hashes = true
terminal_bundle_post_freeze_mutation_count = 0
independent_review_pass = true
independent_reviewer_eligibility_pass = true
independent_review_terminal_bundle_hash_match = true
owner_terminal_seal_pass = true
owner_seal_terminal_bundle_hash_match = true
owner_seal_independent_review_hash_match = true
terminal_seal_pass = true
terminal_no_write_validation_pass = true
post_seal_external_closure_receipt_recorded = true
closure_receipt_in_frozen_bundle = false
closure_receipt_terminal_pass_authority = none
```

선행 foundation readiness, roadmap provenance, corpus approval, human review, official Publish accepted disposition/closure, independent review 또는 owner seal이 없으면 기준을 낮추지 않고 `blocked_<reason>`으로 종료한다.

aggregate disposition이 sealed Publish policy 기준으로 `accepted`가 아니면 compiler implementation이 기능적으로 끝났더라도 이 roadmap의 public-text rewrite closure를 `complete`로 봉인하지 않는다. 그 상태는 exact disposition과 남은 owner를 기록한 non-terminal handoff이며, current output/Lua/runtime/package는 계속 기존 authority를 유지한다.

완료 시 Registry-facing outcome은 `packet_status = complete`인 handoff receipt로 한정되며, 이는 eligibility/readiness claim이 아니다. 별도 Registry adoption, Runtime Compatibility, package/release 검증이 완료되기 전까지 current authority와 사용자에게 배포되는 runtime text는 변경되지 않는다.
