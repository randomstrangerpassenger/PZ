# Iris Tooltip T1 표시 계약 및 상류 입력 준비성 확정 Implementation Plan

> 상태: implemented / owner ratification adopted from the execution prompt / required validation governed by this plan's canonical receipts / T2 handoff blocked by upstream corrections
> 작성일: 2026-08-27
> 기준 로드맵: `Iris Tooltip T1 — 표시 계약 / 상류 입력 준비성 확정 종합 로드맵`
> 검증 깊이: heavy — contract, determinism, whole-universe completeness, locale identity, Menu parity
> inspected S0 commit: `95e17f5b44525a54c202fb7e6e062336d98d4544`
> inspected S0 tree: `1c672145b3deef3795df181bc106bd776900a84b`

이 계획은 Iris Tooltip의 정적 Lua payload나 runtime renderer를 만드는 T2/T3 계획이 아니다. T1은 current exact subject에서 Classification, DVF System, QG가 이미 소유한 사실을 Tooltip용 구조화 입력으로 연결하고, 0~4 slot projection과 absence/readiness/defect attribution을 확정하는 offline contract/audit 단계다.

2026-08-27 Cycle 1/2 종합 검토의 Critical/Important 항목은 보수적으로 모두 반영한다. Cycle 2의 Layer 4 경계는 Option A인 `semantic/public eligibility → identity selection → locale/Menu readiness`로 단일화하며 locale/Menu evidence 결손은 selected identity를 바꾸지 않는다.

현재 코드 조사에서 확인한 중요한 출발점은 다음과 같다. 아래 수치는 inspected S0의 관측값이며 Tooltip support denominator나 영구 계약값이 아니다.

| Surface | Inspected S0 observation | T1 implication |
| --- | --- | --- |
| Current Tooltip | `IrisAltTooltip.lua`가 Alt keycode `56/184`를 확인하고 `drawText`로 최대 4개의 logical row를 그린다. | Alt/runtime renderer는 read-only 조사 대상이며 T1 mutation 대상이 아니다. |
| Tooltip summary | `IrisTooltipSummary.lua`가 Detail ViewModel의 수치 fact를 우선 사용하고, 그 외에는 tag/connection/use-case count를 조립한다. | current Tooltip behavior는 non-verdict baseline observation이다. T1 contract 입력으로 역승격하지 않는다. |
| Layer 2 runtime data | `IrisClassifications.lua`에 2,079 FullType, 50 distinct tag, multi-tag 291행과 27개 `IrisPrimarySubcategory` override가 있다. | 2,079를 support denominator로 가정하지 않는다. resolved category/primary identity의 structured owner가 별도로 필요하다. |
| Menu Layer 2 path | `IrisBrowserProjectionBuilder.lua`가 raw tag를 runtime presentation rank와 description priority로 다시 훑고 override를 적용한다. | T2/T1이 이 Lua rule을 복제해서 resolved identity를 만들 수 없다. P-10 owner seal 또는 upstream correction이 필요하다. |
| Layer 3 | pointer-selected generation `dvf33-028a3968...7145e9`에 2,105 entry, KO public 2,072, silent 33이 있다. | 2,105/2,072/33은 Layer 3 universe이며 Tooltip support universe가 아니다. |
| Layer 3 identity | current entry는 `core_source_fact_ids`, `acquisition_source_fact_ids`, `menu_public_acquisition_fact_ids`와 `text_ko`를 가지지만 단일 Tooltip `fact_id`와 readiness는 runtime entry에 없다. | body 전체를 core description으로 자르거나 요약하지 않는다. approved fact identity/surface가 없으면 correction으로 귀속한다. |
| Layer 4 | current output seed는 1,631 FullType, 2,679 total row, 877 positive row(Recipe 791, Right-click 86), positive FullType 415를 가진다. | 1,631/415/877 중 어느 것도 support denominator가 아니다. |
| Layer 4 ordering/locale | 877 positive row 모두 explicit `stable_order_key`와 `display_by_locale`가 없다. Menu는 source array ordinal을 `baseOrdinal`로 보존하고 locale별 display를 runtime에서 조회한다. | raw array order를 Tooltip order로 사용하지 않는다. stable order/locale identity gap은 P-6/P-9와 QG/locale correction 대상으로 fail-close한다. |
| Current command owner | installed `iris_tooling` package와 `Iris/build/ENTRYPOINTS.md`가 current producer/command route다. | 새 T1 producer는 installed package 경계에 둔다. retired source-root copy를 실행·수정하지 않는다. |

이 관측 baseline은 계획의 조사 근거일 뿐이다. 실행 시점에는 새 exact commit/tree, current authority manifest, Layer 3 pointer/generation descriptor, classification artifact, Layer 4 current-output seed와 locale sources를 다시 hash-bind해야 한다.

---

## 1. Objective

current Tooltip support universe 전체에 대해 다음 연결을 기계 판정 가능한 contract와 audit artifact로 확정한다.

```text
exact current subject
→ Tooltip support state
→ resolved Layer 2 identity
→ optional Layer 3 approved fact identity
→ eligible Layer 4 Recipe / Right-click identities
→ bounded deterministic Layer 4 projection
→ selected Layer 4 identity freeze
→ same selected identities의 KO / EN surface와 Menu evidence readiness
→ fixed S1 → S2 → S3 → S4 projection
→ per-slot / per-locale / overall readiness
→ owner-attributed correction ledger
→ T2 progression gate
```

구체 목표는 다음과 같다.

1. Tooltip support denominator를 exact current subject에 결속하고 adjacent universe와 구분한다.
2. `S1=Layer 2`, `S2=Layer 3`, `S3/S4=Layer 4`인 0~4 slot contract와 fixed ordering을 봉인한다.
3. `legitimate_absence`와 broken required input을 같은 빈 출력으로 축약하지 않는다.
4. Menu와 Tooltip의 same-facts 원칙을 identity 관계로 검증하되 independent consumer evidence가 없는 범위는 `unverified`로 명시하고 parity를 주장하지 않는다.
5. Layer 2 resolved identity를 current owner가 제공하게 하고 T1/T2의 raw-tag inference를 금지한다.
6. Layer 3는 approved core-description fact만 소비하고 body truncation/summarization/rewrite를 금지한다.
7. Layer 4 semantic/public eligibility, 최대 2개 identity selection, selected-identity locale/Menu readiness를 분리하고 Recipe/Right-click의 독립성과 동등성을 보존한다.
8. Layer 4 selection이 importance, frequency, recommendation, text similarity 또는 input array order에 의존하지 않게 한다.
9. KO/EN selection을 identity-first로 고정하고 cross-locale raw-text fallback 및 locale별 candidate reselection을 금지한다.
10. rich readiness/audit manifest와 최소 T2 handoff schema를 분리하고, T2가 selected identity와 requested locale surface만 조립하게 한다.
11. supported FullType 전체를 audit하고 모든 correction에 owner, machine reason, T2 blocker, acceptance/re-audit condition을 부여한다.
12. contract/audit 상태와 `T2_FULL_DATA_PROGRESSION`을 별도 축으로 보고한다.

T2의 허용 연산은 다음으로 제한한다.

```text
selected identity read
→ requested locale text read
→ legitimate absent slot compact
→ fixed slot order concatenate
→ static payload emit
```

T2 mock consumer가 raw tag scan, rule rerun, text truncation, summarization, semantic ranking, semantic dedupe, fallback, reselection, inferred sorting 또는 Menu parity inference를 요구하면 T1은 완료되지 않은 것으로 판정한다.

whole-universe audit에서 T2-blocking 상류 결손이 발견되면 전체 개발 순서는 다음으로 명시한다. correction은 T1에 흡수하지 않고 owner별 별도 scope에서 수행한다.

```text
T1 contract/audit
→ Classification / DVF / QG / locale / Menu-authority correction
→ affected range 또는 owner-ratified full-range T1 re-audit
→ T2 static generation
→ T3 runtime adoption/acceptance
```

---

## 2. Scope

### 2.1 Included

- inspected subject의 current authority/readpoint/producer/validator/artifact route 재결속
- Tooltip support universe의 explicit inclusion/exclusion contract와 exact subject binding
- current Tooltip/Menu path의 read-only inventory
- canonical P-1~P-12 fixed/open definition, already-fixed adoption과 open-decision ratification record
- Layer 2 resolved input owner census와 structured input admissibility
- Layer 3 current readiness/fact/surface mapping과 Tooltip eligibility
- Layer 4 semantic/public candidate eligibility, stable identity selection, selected-identity locale/Menu readiness와 2-slot projection
- KO/EN identity-first locale mapping과 no-fallback contract
- Menu/Tooltip identity parity contract
- deterministic lexical guard fixture
- slot state, per-locale readiness, overall readiness와 reason-code registry
- rich T1 readiness/audit schema, 최소 T2 handoff schema와 bounded mock consumer
- current support universe whole-universe audit
- upstream/cross-owner correction ledger와 T2 blocker summary
- contract fixture와 audit observation의 물리적/논리적 분리
- installed `iris_tooling` package 안의 bounded producer/validator/comparator
- current authority docs/manifest/route의 additive adoption update
- exact terminal subject의 focused tests와 canonical clean-checkout validation

### 2.2 Execution boundary

T1은 기본적으로 repository source를 읽고 repository-external empty output root에 candidate contract result와 audit evidence를 생성한다.

```text
tracked contract/schema/fixture source
        +
hash-bound current Iris inputs
        ↓
installed iris_tooling tooltip-t1 producer
        ↓
external run-local immutable output root
```

audit 실행은 다음을 변경하지 않는다.

- `Iris/media/lua/**`
- current Layer 3 pointer/generation
- current Layer 4 runtime projection
- Classification/DVF/QG source facts
- translations
- package output

tracked 변경은 T1 producer, tests, contract/schema/fixture source와 current authority adoption 문서에 한정한다. audit result, whole-universe manifest, correction ledger와 run receipt는 repository-external result root에 둔다. current contract로 채택할 최소 machine contract만 tracked authority가 될 수 있으며, 한 번의 current census나 observation을 regular validation authority로 자동 등록하지 않는다.

### 2.3 Required decision gates

로드맵의 P-1~P-12는 구현 중 편의에 따라 선택하지 않는다. 이미 constitutional/sealed contract에서 고정된 값과 T1에서 실제로 열려 있는 선택을 다음 canonical table 하나로 구분한다. `already_fixed` 행은 owner가 다른 값을 다시 선택하는 decision이 아니라 required choice와 authority reference를 ratification record에 채택하는 항목이다. `open_in_T1` 행만 allowed choice 중 하나를 선택할 수 있다.

| Decision ID | Exact Question | Status | Allowed Choices | Required Choice | Owner | Must Close Before |
| --- | --- | --- | --- | --- | --- | --- |
| P-1 | T1 contract/audit completion과 T2 full-data progression을 어떻게 관계짓는가? | `already_fixed` | — 재선택 불가 | 두 축을 분리한다. 상류 correction이 남아도 모든 T1 completion criteria가 충족되면 contract/audit axis는 `complete`일 수 있고 T2만 원인별 blocked가 된다. criteria 미충족 때만 `partial/blocked`를 사용한다. | Iris T1 contract owner/reviewer | closeout vocabulary 구현 |
| P-2 | owner가 인정한 Layer 2 legitimate absence에서 나머지 정상 slot의 partial Tooltip을 허용하는가? | `open_in_T1` | `allow_partial_after_owner_absence` / `suppress_projection` | census evidence를 인용해 둘 중 하나를 owner-ratify | Classification owner + Iris presentation-contract owner | Change 2 decision table |
| P-3 | legitimate absent slot을 표시 sequence에서 어떻게 다루는가? | `already_fixed` | — 재선택 불가 | absent display row는 compact하되 semantic slot ID와 S1→S4 상대 순서는 유지한다. defect/unresolved slot은 compaction으로 숨기지 않는다. | Iris presentation-contract owner | Change 2 decision table |
| P-4 | Layer 4에 한 Source만 있을 때 같은 Source에서 최대 2개를 선택할 수 있는가? | `open_in_T1` | `one_from_single_source` / `up_to_two_from_single_source` | census density와 source 분포를 인용해 둘 중 하나를 owner-ratify | QG owner + Iris presentation-contract owner | Change 2/4 single-source branch |
| P-5 | 양 Source가 eligible일 때 2-slot source-equivalence를 어떤 구조 규칙으로 보존하는가? | `open_in_T1` | `one_recipe_plus_one_rightclick` / owner-specified equivalent structural rule | importance/frequency 없이 양 Source 독립성·동등성을 보존하는 한 규칙을 ratify | QG owner + Iris presentation-contract owner | Change 4 projection |
| P-6 | Layer 4 stable presentation order anchor는 무엇인가? | `open_in_T1` | existing QG canonical key / new owner-approved stable key / stable-identity-derived presentation tie-break / `no_admissible_anchor` correction | W1-A census가 존재 여부를 증명한 뒤 하나를 ratify. identity-derived order는 importance/frequency/대표성 순위가 아니라 동률 해소용 presentation order로만 허용 | QG order/identity owner + Iris presentation-contract owner | Change 4 ordering |
| P-7 | exact interaction identity duplicate suppression을 어느 owner layer에서 수행하는가? | `open_in_T1` | upstream QG canonicalization / T1 projection-level single projection | identity trace를 보존하는 한 위치를 owner-ratify | QG identity owner + Iris T1 projection owner | Change 4 duplicate handling |
| P-8 | Layer 3 semantic eligibility와 locale surface readiness를 어떻게 분리하는가? | `open_in_T1` | identity-level eligibility + per-locale readiness / owner-specified equivalent normalized schema | 같은 fact identity를 유지하고 locale surface 결손을 별도 readiness로 드러내는 schema를 ratify | DVF owner + Iris presentation-contract owner | Change 3/5 locale model |
| P-9 | Layer 4에서 cross-locale fallback 또는 locale별 candidate reselection을 허용하는가? | `already_fixed` | — 재선택 불가 | 허용하지 않는다. KO/EN은 같은 selected identity/order를 사용하고 requested locale 결손은 correction/readiness로 남긴다. | Iris locale/presentation-contract owner | Change 5 locale contract |
| P-10 | Layer 2 official resolved identity와 Menu consumer evidence의 admissible route는 무엇인가? | `open_in_T1` | independent current owner/consumer structured evidence / shared-authority identity relation + explicit consumer `unverified` / `no_admissible_authority_relation` correction | W1-A census를 인용해 하나를 ratify. T1 raw-tag resolver나 owner-output 자기대조는 허용하지 않는다. shared-authority relation이 확인된 consumer `unverified`는 T2 static handoff를 막지 않지만 full Menu parity와 T3 runtime adoption claim은 막는다. authority relation 자체가 없거나 모순되면 T2-blocking correction이다. | Classification owner + Menu consumer owner | Change 3 Layer 2 input/parity |
| P-11 | logical 4-row/line-fit의 offline admissibility와 T2-blocking 경계는 무엇인가? | `already_fixed` | — 재선택 불가 | logical row `0~4`와 embedded newline 금지만 T2 hard gate로 둔다. deterministic width proxy는 선택적 advisory이며 actual pixel/font/UI-scale/wrapping acceptance는 T3로 넘긴다. | Iris presentation-contract owner + validation owner | Change 3/6 line-fit contract |
| P-12 | T1 validation에 `regression` 용어를 어떤 범위로 사용하는가? | `already_fixed` | — 재선택 불가 | contract/offline deterministic regression만 뜻한다. runtime/migration/compatibility regression acceptance는 T1 claim이 아니다. | Iris validation/authority owner | validation/report vocabulary |

각 owner 표기는 역할을 뜻하며 decision record에는 실제 signer identity를 기록한다. 모든 행은 `decision_id`, `exact_question`, `status`, `allowed_choices`, `required_choice`, `selected_choice`, `owner`, `rationale`, `evidence_refs`, `subject_binding`, `dependent_phases`, `must_close_before`, `contract_sha256`을 가진다. `open_in_T1` rationale은 반드시 W1-A census artifact identity와 row/summary reference를 인용한다. inspected S0 수치나 계획 문구만을 근거로 선택할 수 없다.

`already_fixed` 행은 다음 authority binding을 추가로 가진다. originating roadmap input은 repository authority로 직접 승격하지 않고 raw SHA-256 `57263a62affe7bd745334c601df2d84b8b0a548cf924c2ff351c77d02ca254e8`의 pre-adoption premise로만 인용하며, final authority는 owner-sealed T1 adoption record가 소유한다.

| Decision ID | `authority_reference_class` | `authority_reference` | Binding meaning |
| --- | --- | --- | --- |
| P-1 | `approved_roadmap_fixed_premise` + `execution_contract_mapping` | originating roadmap P-1/Success Criteria; `docs/EXECUTION_CONTRACT.md` §6-2, §7-1~§7-3 | task-specific T1/T2 축 분리와 formal closeout mapping을 함께 봉인 |
| P-3 | `approved_roadmap_fixed_premise` + `sealed_presentation_principle` | originating roadmap Phase 2/P-3; `docs/DECISIONS.md` “Iris Layer 4 — Recipe / Right-click `use_case`, requirement / adaptive presentation contract” | absence compaction은 presentation mechanics이며 semantic slot identity/order를 바꾸지 않음 |
| P-9 | `sealed_principle_applied_to_adjacent_scope` | `docs/ARCHITECTURE.md` “Locale projection 구조”; `docs/DECISIONS.md` “Iris — Layer 2–3 locale projection contract”; originating roadmap P-9 | sealed no-fallback/locale-identity principle을 Layer 4 selected identity readiness에 적용하되 adjacent-scope adoption임을 명시 |
| P-11 | `sealed_presentation_principle` + `execution_scope_boundary` | `docs/Philosophy.md` Iris Tooltip 최대 4줄; `docs/DECISIONS.md` “Iris — Menu / Tooltip presentation contract”; T1/T3 scope boundary | T1은 logical-row/newline contract만 hard gate로 소유하고 실제 visual fit은 T3 acceptance로 남김 |
| P-12 | `execution_contract_exact` + `approved_roadmap_fixed_premise` | `docs/EXECUTION_CONTRACT.md` §6-1~§6-3; originating roadmap P-12 | contract/offline validation claim과 runtime/compatibility claim ceiling을 구분 |

decision contract schema는 `already_fixed` 행에서 `authority_reference_class`, exact document/heading or external premise hash, adoption target과 scope (`exact`/`adjacent_application`)를 required로 검증한다. reference가 없거나 adjacent application을 exact sealed decision으로 허위 표기하면 fail-loud한다.

sequencing은 다음으로 고정한다.

| Step/Gate | Permitted work | Required result |
| --- | --- | --- |
| W0 | exact subject binding, current route/tool disposition 확인 | semantic decision이 없는 immutable read subject |
| W1-A | bound subject의 read-only authority/universe/Menu-consumer/renderer baseline census | P-2/P-4/P-5/P-6/P-8/P-10/P-11 evidence package |
| G1-A | P-1/P-2/P-3/P-10/P-11/P-12 adoption/ratification | slot, Layer 2, line-fit, closeout implementation 허가 |
| G1-B | P-4/P-5/P-6/P-7 ratification | Layer 4 implementation 허가 |
| G1-C | P-8/P-9 ratification | Layer 3 locale/readiness와 parity implementation 허가 |
| G1-D | Layer 2/3/4 모두 admissible structured owner output이 없을 때 global-gap continuation checkpoint | contract-only continuation 또는 gap-ledger `partial` closeout의 explicit owner disposition |
| W1-B | ratified support predicate로 exact included/excluded set freeze | immutable Tooltip support denominator |

W1-A는 read-only evidence 수집만 허용하며 projection, semantic mapping, candidate selection, fallback 또는 contract adoption을 수행하지 않는다. G1-A/B/C는 W1-A 이후이면서 관련 contract 구현 이전에 닫는다. G1-D는 세 layer의 global gap 조건이 참일 때만 필요하며 새 semantic default를 허용하지 않는다.

미ratify `open_in_T1` 결정에는 default를 만들지 않는다. candidate execution은 `blocked_unresolved_contract_decision`으로 닫고 final manifest 또는 T2 handoff를 생성하지 않는다. Philosophy/DECISIONS에서 이미 고정된 Menu/Tooltip same-facts, evidence-first, no-fallback 원칙은 P choice로 다시 열지 않는다.

### Explicitly Out Of Scope

- Tooltip static Lua generation 또는 T2 production generator
- `IrisAltTooltip.lua`, `IrisTooltipSummary.lua`, `IrisItemDetailPresentation.lua` mutation
- Alt input hook, cache, renderer, tooltip width/height/layout 변경
- current Menu Browser/Detail/Wiki behavior 변경
- Classification rule, taxonomy, override 또는 `IrisClassifications.lua` correction
- DVF facts/decisions/body rewrite, new sentence authoring, silent/public disposition 변경
- QG PASS/NO/REVIEW 재판정, interaction authoring 또는 exclusion 변경
- KO/EN 번역 신규 작성 또는 번역 품질 승인
- current Layer 3/Layer 4 runtime artifact install
- stale/historical producer 복원 또는 `Iris/build/description/v2/tools/build/**` direct execution
- stateful registry, mutable latest pointer, IAR lifecycle 재도입
- regular validation denominator 재설계
- runtime/API/package migration
- multiplayer, save/load, long-session, external-mod compatibility sweep
- DVF freeze, RTC, Publish, release, Workshop 또는 deployment readiness 판정
- Iris 밖의 Pulse/Echo/Fuse/Nerve/Frame/Canvas/Cortex 변경

---

## 3. Non-Goals

이 계획은 다음 문제를 해결하려 하지 않는다.

- current Tooltip의 numeric fact/tag/connection/count 표시를 T1에서 교체하는 것
- 사용자에게 가장 중요하거나 유용한 사실을 고르는 ranking system
- 모든 supported item에 반드시 4줄을 채우는 coverage 목표
- Layer 3가 없는 item에 설명을 새로 만드는 것
- Recipe와 Right-click을 하나의 일반 interaction capability로 합치는 것
- 비슷한 문장을 semantic duplicate로 자동 판정하는 것
- locale 누락을 다른 locale, 다른 candidate 또는 raw source text로 보충하는 것
- Menu 문자열과 Tooltip 문자열의 유사도를 fact parity로 사용하는 것
- line width proxy를 actual PZ visual acceptance로 확대하는 것
- 발견된 upstream defect를 T1 범위에서 직접 수정하는 것
- census/artifact 수를 regular validation 수로 그대로 추가하는 것
- audit PASS를 runtime, package, compatibility 또는 release PASS로 확대하는 것

---

## 4. Assumptions

### 4.1 Constitutional and authority assumptions

- `docs/Philosophy.md`가 최상위 설계 authority다.
- Iris는 근거 기반 정보 모드이며 추천, 효율, 우열, 중요도 판단을 하지 않는다.
- 충분한 근거가 없으면 추측하지 않고 침묵한다.
- Menu와 Tooltip은 같은 facts authority를 다른 깊이로 투영한다.
- Recipe와 Right-click은 독립적이고 동등한 Source다.
- PZ runtime Iris는 100% Lua이며 T1 offline Python tooling은 이 경계를 변경하지 않는다.
- planning/implementation bootstrap은 `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`다.
- current command literal owner는 `Iris/build/ENTRYPOINTS.md`다.
- current producer는 installed `Iris/tooling/src/iris_tooling/**` package다.
- authority manifest나 current route가 채택하지 않은 historical/reproduction 파일은 current input으로 사용하지 않는다.

### 4.2 Current subject assumptions

inspected S0 관측값은 실행 입력으로 자동 승계하지 않는다. 실행은 최소 다음 identity를 새로 캡처한다.

- Git commit/tree와 clean-checkout identity
- `Iris/_docs/authority/iris_current_authority_manifest.json` raw SHA-256
- `Iris/_docs/authority/iris_current_route_index.json` raw SHA-256
- `Iris/media/lua/client/Iris/Data/IrisClassifications.lua` raw SHA-256
- pointer-selected Layer 3 generation ID, descriptor와 canonical input/output hashes
- `Iris/build/description/v2/data/dvf_3_3_input_manifest.json` raw SHA-256
- current Layer 3 KO/EN public key-set identity
- current Layer 4 source/output-seed identity와 QG evidence identities
- `Iris/media/lua/shared/translate/{ko,en}/Iris_*.txt` raw SHA-256
- Menu Layer 2/3/4 consumer implementation hashes
- current Tooltip summary/renderer implementation hashes

어느 input이 current owner로 확인되지 않거나 hash binding이 끊기면 rendered/runtime artifact를 source authority로 역승격하지 않고 `upstream_correction_required` 또는 `blocked_subject_binding`으로 판정한다.

### 4.3 Support-universe assumption

다음 universe는 서로 다르며 동일성을 가정하지 않는다.

```text
Layer 3 canonical = 2105 at inspected S0
Layer 3 public KO/EN = 2072 at inspected S0
Layer 2 runtime classification = 2079 at inspected S0
Layer 2 templates/tags = 50 at inspected S0
Layer 4 fulltypes = 1631 at inspected S0
Layer 4 positive fulltypes = 415 at inspected S0
Layer 4 positive rows = 877 at inspected S0
runtime ScriptManager item universe = runtime-dependent
```

Tooltip support universe는 owner-ratified support predicate와 explicit included/excluded FullType set으로 별도 생성한다. union, intersection, maximum count 또는 가장 큰 adjacent universe를 암묵적으로 선택하지 않는다.

W1-B에서 support denominator가 freeze된 뒤에는 다음 readiness defect를 이유로 이미 supported인 FullType을 denominator에서 제거하지 않는다.

- missing/unresolved Classification identity
- missing/ineligible DVF fact or locale surface
- missing QG identity/order/menu trace/translation
- Menu parity evidence gap
- line-fit blocker 또는 기타 readiness defect

이 결손은 동일 denominator 안에서 readiness/correction으로만 집계한다. denominator 변경은 support authority 자체의 additive successor decision과 new subject binding을 요구한다.

### 4.4 Layer 2 assumption

현재 Menu path는 raw tags, presentation rank, description priority와 `IrisPrimarySubcategory` override를 runtime에서 소비한다. 이 동작을 읽어 같은 결과를 내는 T1-side resolver를 새 authority로 만들지 않는다.

P-10은 다음 둘 중 하나를 owner가 ratify해야 한다.

1. current Classification owner가 exact FullType별 resolved category/primary subcategory/label key/authority identity를 구조화 output으로 제공하고, current Menu consumer가 실제 소비한 resolved identity를 별도 authority/evidence reference로 관측할 수 있다.
2. owner output 또는 독립 Menu consumer evidence가 없음을 correction ledger에 기록하고 affected FullType을 T2-blocking으로 둔다.

runtime Lua parsing, tag-order selection 또는 Browser code reimplementation은 세 번째 선택지가 아니다. Classification owner output을 owner reference와 Menu consumer reference 양쪽에 넣는 자기대조도 parity evidence가 아니다.

Layer 2 parity는 per-row로 `verified`, `correction_required`, `unverified_without_independent_consumer_evidence`를 구분한다. 마지막 상태는 parity violation을 0으로 세는 근거가 아니며 full Menu/Tooltip parity와 T3 runtime adoption claim을 차단한다. 다만 owner-public Menu identity universe와 Tooltip selected identity의 shared-authority subset relation이 별도로 성립하면 consumer observation 부재만으로 T2 static handoff를 차단하지 않는다. authority relation 자체가 없거나 모순되면 `correction_required`와 T2 blocker다.

### 4.5 Layer 3 assumption

- current Layer 3 facts/decisions/readiness contract와 pointer-selected generation을 함께 확인한다.
- `text_ko` 전체가 자동으로 Tooltip core description인 것은 아니다.
- acquisition paragraph를 core description으로 승격하지 않는다.
- `core_source_fact_ids`가 여러 개인 경우 T1이 임의로 하나를 중요도 기준으로 고르지 않는다.
- stable approved Tooltip fact identity와 complete locale surface가 current owner에 의해 연결되어야 한다.
- `description_ready`, `acquisition_only`, `omission_allowed`, `insufficient_material`, `review_required`는 이름만으로 Tooltip disposition을 추정하지 않고 ratified mapping을 사용한다.
- `review_required`를 T1이 PASS로 승격하지 않는다.

### 4.6 Layer 4 assumption

- QG public positive row와 exclusion/debug/quality/requirement-only row를 구조적으로 구분한다.
- current `use_case_id`/runtime `label_key`가 stable interaction identity 후보지만, stable presentation order와 locale surface contract는 별도 확인 대상이다.
- Layer 4는 `semantic/public eligibility → identity selection → selected-identity readiness`의 세 단계를 가진다. locale surface completeness와 independent Menu consumer evidence availability는 앞의 두 단계에 입력되지 않는다.
- KO/EN 또는 Menu evidence가 missing인 selected identity는 그대로 유지하고 correction/unverified readiness를 부여한다. 더 완전한 다음 candidate로 substitution하지 않는다.
- input array ordinal은 stable order가 아니다.
- P-6이 identity-derived order를 채택할 수는 있지만 이는 stable identity의 canonical byte/tuple order를 presentation tie-break로 쓰는 것뿐이며 중요도, 빈도, 대표성, 효율 또는 추천 ranking을 암시하지 않는다.
- Recipe navigation identity와 Right-click action identity의 namespace 차이를 보존한다.
- exact identity duplicate만 explicit contract에 따라 처리한다. text similarity는 사용하지 않는다.
- capacity 때문에 제외된 valid candidate는 upstream defect가 아니다.

### 4.7 Locale and line-fit assumptions

- identity selection이 locale lookup보다 먼저다.
- selected identity set은 KO/EN에서 동일해야 한다.
- missing locale surface는 다른 locale, raw display text 또는 다른 candidate로 대체하지 않는다.
- 현재 renderer는 `drawText`를 logical row마다 호출하고 automatic wrapping을 T1에 제공하지 않는다.
- P-11은 logical row `0~4`와 embedded newline 금지만 T2-blocking contract로 고정한다.
- deterministic width proxy가 있더라도 advisory로만 기록하며 T2 readiness나 identity selection을 바꾸지 않는다.
- T1은 actual pixel width, font, UI scale, wrapping 또는 visual acceptance를 주장하지 않는다. 해당 검증은 T3가 소유한다.
- lexical guard는 explicit vocabulary fixture에만 권한을 가지며 자유로운 자연어 semantic 판단기로 성장하지 않는다.

### 4.8 Validation assumptions

- Python tooling은 `uv run python ...` 또는 exact installed wheel environment에서 실행한다.
- PASS는 relevant exact command가 exit `0`일 때만 주장한다.
- exact terminal subject는 current receipt-bound clean-checkout full gate를 통과해야 한다.
- T1 one-off audit/whole-universe census는 regular validation membership으로 자동 승격하지 않는다.
- 반복 보호 가치가 있는 최소 contract validator만 별도 owner disposition 후 current membership 후보가 된다.
- W0는 Change 0의 exact subject binding/tool disposition 단계다. W1-A/W1-B 또는 semantic contract 구현과 같은 이름이 아니다.

---

## 5. Repository Areas Affected

아래는 계획 시점의 최대 예상 경로다. W0, 즉 Change 0의 exact subject binding/tool disposition 단계에서 current ownership과 package layout을 재확인한 뒤 exact file set을 freeze한다. contract/projection/audit 경계와 failure attribution을 보존할 수 있다면 구현자는 파일을 더 합칠 수 있으며, 목록을 맞추기 위해 빈 wrapper나 1기능 파일을 만들지 않는다. 같은 책임을 historical source-root copy에 중복 구현하지 않는다.

### Code

- `Iris/tooling/src/iris_tooling/__main__.py`
  - package-owned `build tooltip-t1` 또는 동등한 explicit lifecycle-bound command routing
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/__init__.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/cli.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/models.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py` — subject binding, input authority와 slot/input schema
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/projection.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py` — locale/Menu readiness, reporting과 bounded mock consumer 포함
- `Iris/tooling/tests/test_tooltip_t1_contract.py`
- `Iris/tooling/tests/test_tooltip_t1_projection.py`
- `Iris/tooling/tests/test_tooltip_t1_audit.py`
- `Iris/tooling/tests/fixtures/tooltip_t1/**`

현재 runtime/Menu 파일은 read-only evidence surface다. 다음 파일을 T1에서 수정하지 않는다.

- `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua`
- `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailPresentation.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserProjectionBuilder.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserCategoryIndex.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua`
- `Iris/media/lua/client/Iris/Data/**`

### Docs

- `docs/iris_tooltip_t1_display_contract_upstream_input_readiness_plan.md`
- `docs/iris_tooltip_t1_display_contract_policy.md` — owner-ratified human contract candidate
- `docs/DECISIONS.md` — adoption 시 additive successor/refinement
- `docs/ARCHITECTURE.md` — owner-sealed additive update로만 offline T1 → mechanical T2 boundary와 artifact flow 반영
- `docs/ROADMAP.md` — owner-sealed additive update로만 T1 contract/audit와 원인별 T2 progression 축 반영
- `Iris/build/ENTRYPOINTS.md` — exact installed command literal

### Config

- `Iris/_docs/authority/tooltip_t1/tooltip_t1_decision_contract.json`
- `Iris/_docs/authority/tooltip_t1/tooltip_display_contract.json`
- `Iris/_docs/authority/tooltip_t1/layer2_tooltip_input_contract.json`
- `Iris/_docs/authority/tooltip_t1/layer3_tooltip_input_contract.json`
- `Iris/_docs/authority/tooltip_t1/layer4_tooltip_projection_contract.json`
- `Iris/_docs/authority/tooltip_t1/tooltip_locale_menu_parity_contract.json`
- `Iris/_docs/authority/tooltip_t1/tooltip_t2_handoff.schema.json` — OPEN일 때만 소비되는 최소 mechanical schema
- `Iris/_docs/authority/tooltip_t1/tooltip_readiness_reason_registry.json`
- `Iris/_docs/authority/tooltip_t1/tooltip_t1_tool_disposition_contract.json`
- `Iris/_docs/authority/iris_current_authority_manifest.json` — adoption된 exact contract/code/test classification
- `Iris/_docs/authority/iris_current_route_index.json` — current route에 실제로 필요한 최소 navigation only
- `Iris/_docs/round3/current_route_required_validations.json` — minimum validator를 regular membership으로 채택한 경우에만 additive update
- `Iris/tooling/pyproject.toml` — package data 또는 command metadata 변경이 실제로 필요한 경우에만

### Generated Artifacts

repository-external run root 아래에 최소 다음을 생성한다.

```text
subject_binding.json
tooltip_support_universe_census.jsonl
tooltip_support_universe_summary.json
current_tooltip_input_authority_inventory.json
pre_ratification_decision_evidence.json
decision_adoption_receipt.json
contract_fixture_expectations.jsonl
contract_fixture_result.json
layer4_invariance_result.json
tooltip_readiness_manifest.jsonl
upstream_correction_ledger.jsonl
t2_progression_record.json
bounded_validation_report.json
axis_separated_closeout_record.json
t2_handoff_input.jsonl                 # OPEN일 때만 생성
t2_handoff_manifest.json
run_receipt.json
```

fixture expectations는 tracked contract/fixture identity에 결속하고 audit observations와 별도 파일에 둔다. audit observation을 expected result로 다시 사용하지 않는다.

`layer4_invariance_result.json`은 한 bound candidate set에서 수행한 두 독립 check section을 가진다. `permutation` section은 array-order 변형 전후 selected identity/order hash를, `readiness_masking` section은 locale/Menu evidence mask/restore 전후 identity/order hash와 readiness-only delta를 기록한다. 두 section은 입력 변형과 assertion을 공유하지 않지만 동일 candidate execution 안에서 생성해 별도 lifecycle run을 요구하지 않는다.

---

## 6. Planned Changes

### Change 0 — W0 exact subject baseline and pre-ratification preparation

Purpose:

current subject를 재현 가능하게 묶고 W1-A read-only census가 decision보다 먼저 수행될 수 있는 non-semantic 경계를 만든다.

Files:

- `Iris/_docs/authority/tooltip_t1/tooltip_t1_decision_contract.json`
- `Iris/_docs/authority/tooltip_t1/tooltip_t1_tool_disposition_contract.json`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py`
- `Iris/tooling/tests/test_tooltip_t1_contract.py`

Implementation Notes:

- inspected S0가 아니라 execution-time clean commit/tree를 canonical subject로 기록한다.
- current route를 따라 authority, producer, validator, artifact를 재확인한다.
- broad glob보다 exact current manifest entry를 우선한다.
- current Layer 3 pointer가 가리키는 generation descriptor와 canonical input/output hashes를 기록한다.
- current Layer 4 source/output seed와 its producer closure를 기록한다. repository baseline이 current full-gate seed일 뿐 semantic source authority가 아니면 그 차이를 명시한다.
- current Tooltip path는 `IrisAltTooltip → IrisTooltipSummary → DetailViewModel/DetailPresentation`, Menu path는 Layer 2/3/4별로 별도 기록한다.
- canonical P-1~P-12 table을 schema/fixture로 표현하되 W0에서는 `already_fixed` authority reference와 `open_in_T1` 질문/choice vocabulary만 검증한다. open decision의 `selected_choice`는 아직 요구하지 않는다.
- W0 완료 후 W1-A read-only census만 실행할 수 있다. decision contract가 ratify되기 전에는 semantic producer, projection, readiness mapping 또는 support freeze를 실행하지 않는다.
- 신규 tool/test의 `current_required`, `lifecycle_bound`, `diagnostic`, `historical` disposition을 terminal freeze 전에 명시한다.
- historical or reproduction artifact가 current input으로 필요한 경우 current authority가 exact path/hash/role을 명시적으로 재채택하지 않으면 사용하지 않는다.

Validation:

- risk test #1의 parameterized lifecycle table이 subject-binding, dirty/stale/hash/route mismatch, historical reentry, P fixed/open authority와 phase sequencing을 함께 검증한다.

Blocking conditions:

- `blocked_subject_binding`
- `blocked_authority_route`
- `blocked_tool_disposition`

---

### Change 1 — W1-A read-only census, decision evidence and W1-B support freeze

Purpose:

bound exact subject에서 adjacent universe, actual input owner, independent Menu consumer evidence와 ordering/line-fit evidence를 먼저 census한다. 그 결과를 P decision evidence로 ratify한 뒤에만 Tooltip support denominator를 freeze한다.

Files:

- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py`
- `Iris/tooling/tests/test_tooltip_t1_contract.py`
- external census/inventory/path-map/gap artifacts

Implementation Notes:

- W1-A에서는 다음 set을 독립적으로 census하고 candidate support predicate별 set difference를 계산하되 어느 set도 아직 Tooltip denominator라고 부르지 않는다.
  - proposed Tooltip supported/excluded FullType sets by existing authority-backed predicate
  - Layer 2 classification FullType
  - Layer 3 canonical/public/silent FullType
  - Layer 4 source FullType와 positive-candidate FullType
  - KO/EN public surface key sets
  - current Menu-consumed FullType/identity set
- support predicate가 existing current owner에 없으면 T1 presentation-scope decision으로 owner ratification을 요구한다. 가장 큰 universe나 union/intersection을 default로 사용하지 않는다.
- W1-A는 P-6에서 사용할 current QG ordering anchor 존재/부재와 P-10에서 사용할 resolved Classification output 및 independent Menu consumer identity route 존재/부재를 각각 evidence row로 기록한다.
- W1-A는 P-11용 logical row/newline/renderer read-only baseline과 proxy 입력의 관측 가능 범위만 기록한다. visual acceptance나 proxy threshold를 결정하지 않는다.
- 모든 open decision rationale은 `pre_ratification_decision_evidence`의 exact artifact hash와 record identity를 인용한다.
- G1-A/B/C ratification 후 W1-B에서 support predicate를 적용한다. support universe row에는 `full_type`, `support_state`, `inclusion_rule_id`, `source_authority_ref`, `subject_binding`을 둔다.
- W1-B denominator freeze 뒤 readiness gap 때문에 supported FullType을 제외하거나 predicate를 완화하지 않는다.
- duplicate case-sensitive FullType, normalized collision, missing inclusion proof와 excluded-without-reason을 fail-loud한다.
- runtime ScriptManager enumeration은 current runtime observation일 수 있지만 offline exact support authority와 동일시하지 않는다.
- Layer 2에서는 다음을 구분한다.
  - all classification tag membership
  - Menu browsing `primaryLocation`
  - description/navigation `primaryTag`
  - `IrisPrimarySubcategory` override
  - localized category/subcategory label key
- Layer 3에서는 facts, decisions, role-material readiness contract, pointer-selected rendered generation, KO/EN companion과 source fact identities를 추적한다.
- Layer 4에서는 QG public/exclusion/review/requirement state, `use_case_id`, surface, recipe navigation identity, right-click label identity, current array ordinal, locale surface source와 Menu consumer identity를 추적한다.
- current Tooltip numeric/tag/count behavior는 baseline observation으로만 기록하고 T1 candidate eligibility에 사용하지 않는다.
- read-only census 중 upstream source나 runtime payload를 수정하지 않는다.

Validation:

- risk test #1이 exact subject/hash, read-only source parity, same-subject decision evidence와 P-6/P-10 branch를 검증한다.
- risk test #6이 support set equality, duplicate/missing/case collision, denominator substitution 거부와 W1-B freeze identity를 함께 검증한다.

Deliverables:

- `tooltip_support_universe_census`
- `current_tooltip_input_authority_inventory`
- `pre_ratification_decision_evidence`
- current Menu/Tooltip path map과 phase gap rows를 포함한 `current_tooltip_input_authority_inventory`
- `subject_binding`
- P-11에 따른 renderer/offline-fit read-only baseline

#### Post-census decision closure checkpoint

W1-A가 끝나면 G1-A/B/C를 닫고 그 뒤 W1-B support freeze를 수행한다. decision contract의 rationale/evidence가 W1-A artifact identity를 인용하지 않거나 W1-A와 다른 subject를 가리키면 ratification은 무효다.

Layer 2/3/4 모두에 admissible structured owner output이 없으면 G1-D를 연다. owner가 contract-only continuation을 명시적으로 승인한 경우에도 모든 gap은 correction/readiness로 남고 T2 progression은 열리지 않는다. 승인하지 않으면 gap record와 correction ledger까지만 생성하고 contract/audit axis를 `partial`로 닫는다. 이 checkpoint는 missing data를 추론하거나 contract를 완화하는 권한이 아니다.

---

### Change 2 — Tooltip slot, absence and readiness contract

Purpose:

0~4 slot의 의미, fixed order, 정상 absence와 defect 경계를 단일 decision table로 봉인한다.

Files:

- `Iris/_docs/authority/tooltip_t1/tooltip_display_contract.json`
- `Iris/_docs/authority/tooltip_t1/tooltip_readiness_reason_registry.json`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/models.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py`
- `Iris/tooling/tests/test_tooltip_t1_contract.py`
- `Iris/tooling/tests/fixtures/tooltip_t1/display_contract/**`

Implementation Notes:

기본 slot identity는 다음으로 고정한다. P-3의 already-fixed compaction rule을 채택하고 P-2/P-4의 open branch만 census 이후 ratified decision을 따른다.

```text
S1 = Layer 2 classification
S2 = Layer 3 core description
S3 = Layer 4 interaction #1
S4 = Layer 4 interaction #2

fixed order = S1 → S2 → S3 → S4
```

candidate/pre-ratification execution은 semantic slot state와 locale surface readiness를 분리한다. exact token은 decision contract와 schema에서 봉인한다.

```text
semantic_slot_state:
  selected
  legitimate_absence
  upstream_identity_correction_required

locale_surface_readiness[ko|en]:
  ready
  correction_required
  not_applicable

execution-only:
  blocked_contract_decision
```

`blocked_contract_decision`은 execution-only 상태다. G1-A/B/C 전 candidate result 또는 중단 receipt에서만 사용할 수 있으며 adopted final readiness manifest와 T2 handoff schema에는 남지 않는다. unresolved decision이 있으면 final manifest 또는 handoff input을 생성하지 않는다.

- `selected`는 locale과 무관하게 stable approved semantic identity가 선택되었을 때 사용한다.
- selected identity의 requested locale public surface 존재 여부는 `locale_surface_readiness`에서만 판정한다.
- `displayable(locale)`은 `semantic_slot_state == selected`이면서 해당 locale readiness가 `ready`일 때만 참이다.
- `legitimate_absence`는 해당 upstream owner/ratified mapping이 absence를 허용할 때만 사용한다.
- required identity/surface/authority trace가 깨진 상태를 slot compaction으로 숨기지 않는다.
- all legitimate absence의 0-line output과 generation failure를 구분한다.
- locale text 누락을 slot 제거, 다른 candidate 또는 다른 locale로 보충하지 않는다.
- Layer 3가 legitimate absence이면 표시 row는 compact하지만 Layer 4는 semantic S3/S4 slot identity를 유지하며 S1→S4 상대 순서를 바꾸지 않는다. 이는 P-3의 already-fixed required choice다.
- 한 source만 있는 Layer 4에서 같은 source의 두 candidate를 허용하는지는 P-4에서 결정한다.
- semantic slot state, per-locale surface readiness, overall readiness와 `t2_blocking`을 별도 field로 둔다.
- readiness는 fact taxonomy가 아니라 projection consumability다.

Decision-table coverage:

- L2 only
- L2 + L3
- L2 + L4
- L3 only
- L4 only
- L2 + L3 + L4×1
- L2 + L3 + L4×2
- all legitimate absence
- missing required identity
- missing required locale surface
- mixed legitimate absence + defect
- unresolved contract decision

Validation:

- risk test #2 하나의 parameterized input-contract table로 semantic/locale tuple, absence compaction, defect concealment 거부, slot order와 KO-ready/EN-missing 분리를 검증한다.

Deliverables:

- `tooltip_display_contract`
- `slot_state_decision_table`
- `legitimate_absence_contract`
- P-2/P-3/P-4 disposition

---

### Change 3 — Layer 2 and Layer 3 structured input readiness

Purpose:

T2가 raw classification tag나 rendered body를 해석하지 않고 Layer 2/3 slot을 소비할 수 있는 구조화 입력을 확정한다.

Files:

- `Iris/_docs/authority/tooltip_t1/layer2_tooltip_input_contract.json`
- `Iris/_docs/authority/tooltip_t1/layer3_tooltip_input_contract.json`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py`
- `Iris/tooling/tests/test_tooltip_t1_contract.py`
- `Iris/tooling/tests/fixtures/tooltip_t1/layer2_layer3/**`

Implementation Notes:

Layer 2 contract candidate는 최소 다음을 요구한다.

```text
classification_identity
category_id
primary_subcategory_id
category_label_key
primary_subcategory_label_key
localized_surfaces.ko
localized_surfaces.en
authority_ref
menu_consumer_identity_ref
menu_parity_status
```

- `category_id`/`primary_subcategory_id`는 raw tag array에서 T1이 선택하지 않는다.
- Menu의 `primaryLocation`과 `primaryTag`가 다르면 어느 값이 Tooltip identity인지 P-10 owner contract가 명시해야 한다.
- `IrisPrimarySubcategory` override는 source owner가 resolved output에 반영해야 하며 T1이 별도 override engine을 구현하지 않는다.
- `Misc.9-A`는 current decision상 output-stage fallback이므로 raw occurrence만으로 Tooltip S1 public classification identity/header가 될 수 없다. P-10의 Classification owner가 resolved public identity와 label surface를 제공한 경우에만 S1 input으로 인정하고, 그렇지 않으면 `CLASSIFICATION_FALLBACK_NOT_ADMISSIBLE` correction으로 귀속한다.
- label fallback string을 canonical locale surface로 간주하지 않는다. requested locale key가 실제로 존재해야 한다.
- T2는 ratified format이 허용할 때 단순 `[category label - primary subcategory label]` 조립만 수행한다.

Layer 2 Menu parity evidence는 두 reference를 분리한다.

```text
classification_owner_resolved_identity_ref
menu_consumer_observed_identity_ref
```

- 두 reference는 독립 artifact/record identity와 hash를 가져야 한다.
- owner resolved output을 두 reference에 복사하거나 같은 producer result를 양쪽 evidence로 사용하지 않는다.
- actual Menu consumer가 소비한 resolved identity를 current source-owned structured output/receipt에서 관측할 수 있을 때만 `verified` 또는 `correction_required`를 판정한다.
- 독립 consumer evidence가 없으면 shared-authority subset relation을 먼저 검증한다. relation이 성립하면 `unverified_without_independent_consumer_evidence`로 남기고 T2 static handoff는 허용할 수 있으며, full Menu parity와 T3 runtime adoption claim만 보류한다.
- shared-authority relation 자체가 없거나 selected Tooltip identity가 owner-public Menu identity universe에 속하지 않으면 `correction_required`와 T2 blocker로 둔다.
- raw-tag/runtime rule을 offline에서 재구현하지 않는다.

Layer 3 contract candidate는 최소 다음을 요구한다.

```text
fact_id
fact_kind = core_description
source_fact_ids[]
source_ref
authority_ref
upstream_readiness
tooltip_eligibility
localized_surfaces.ko
localized_surfaces.en
```

- current `text_ko` body 전체를 자동 사용하지 않는다.
- `core_source_fact_ids`와 acquisition source ids를 분리한다.
- core와 acquisition paragraph가 결합된 body를 newline, length 또는 paragraph heuristic으로 자르지 않는다.
- 여러 core fact를 하나의 Tooltip sentence로 합성하지 않는다.
- complete user-facing sentence와 approved identity/surface가 이미 존재할 때만 eligible이다.
- no summarization/no truncation/no rewrite를 code-path absence와 negative fixture로 증명한다.
- `description_ready`, `acquisition_only`, `omission_allowed`, `insufficient_material`, `review_required` 전 상태에 ratified mapping 하나를 부여한다.
- `insufficient_material`은 명칭만으로 legitimate absence 또는 defect를 자동 선택하지 않는다.
- P-8은 Layer 3 semantic fact eligibility와 per-locale surface readiness를 분리할지 exact schema로 닫는다.
- DVF owner output은 Menu consumer evidence를 스스로 발급하지 않는다. `menu_consumer_fact_identity_refs` 같은 self-attestation은 owner output에 포함하지 않으며, fact identity/surface readiness와 Menu parity evidence를 분리한다.
- current generation의 rendered fact relation과 `IrisLayer3DataCurrent → IrisLayer3DataLookup → layer3_renderer → IrisItemDetailModelAssembler` FullType 소비 경로가 공유 authority relation을 제공하더라도, 독립 Menu fact-identity observation이 없으면 Layer 3 parity는 `unverified_without_independent_consumer_evidence`로 남긴다.
- P-11에 따라 embedded newline과 logical row `>4`만 hard correction으로 판정한다. deterministic width proxy는 존재해도 advisory field만 만들며 eligibility/readiness/T2 progression을 바꾸지 않는다.
- explicit prohibited-expression fixture에 걸린 public surface는 rewrite하지 않고 ineligible/correction으로 귀속한다.

Validation:

- risk test #2가 Layer 2 resolved identity/multi-tag/override/no raw inference와 Layer 3 readiness/core-acquisition/no rewrite를 같은 input-contract table에서 검증한다.
- risk test #4가 prohibited/allowed text, embedded-newline hard failure와 long single-line advisory를 locale/Menu table과 함께 검증한다.

Deliverables:

- `layer2_tooltip_input_contract`
- `layer3_tooltip_input_contract`
- `dvf_to_tooltip_readiness_mapping`
- line-fit/offline-length admissibility contract
- P-8/P-10/P-11 disposition

---

### Change 4 — Layer 4 semantic/public eligibility and deterministic bounded identity selection

Purpose:

QG approval을 변경하지 않고 Recipe/Right-click candidate 중 최대 2개의 stable identity를 deterministic structural rule로 projection한다.

Files:

- `Iris/_docs/authority/tooltip_t1/layer4_tooltip_projection_contract.json`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/projection.py`
- `Iris/tooling/tests/test_tooltip_t1_projection.py`
- `Iris/tooling/tests/fixtures/tooltip_t1/layer4_projection/**`

Implementation Notes:

semantic/public candidate eligibility는 최소 다음을 모두 요구한다.

```text
approved/public QG state
stable interaction_id
surface ∈ {recipe, rightclick}
stable_order_key or ratified equivalent
not exclusion
not debug/quality-only
not requirement-only
```

- current output의 `use_case_id`/`label_key`, `surface`, recipe navigation identity와 QG state를 exact authority trace로 연결한다.
- QG `REVIEW`를 T1이 승인하지 않는다.
- runtime `baseOrdinal` 또는 source array ordinal을 stable presentation order로 채택하지 않는다.
- current 877 positive row에 explicit stable order key가 없다는 inspected observation은 P-6 owner decision/gap inventory의 시작점이다. 실행 subject에서 다시 확인한다.
- selection과 downstream readiness를 다음 단계로 분리한다.

```text
semantic/public eligibility
→ stable ordering
→ exact identity duplicate handling
→ source-equivalence rule
→ bounded 2-slot selection
→ capacity disposition
→ selected identity freeze
→ KO/EN surface lookup
→ independent Menu evidence/parity lookup
→ per-locale/parity readiness
```

- `localized_surfaces`, translation completeness, Menu identity trace와 parity status는 `selected identity freeze` 전의 eligibility/order/dedupe/source-equivalence/capacity logic에서 읽지 않는다.
- 같은 semantic/public candidate set에서 locale/Menu evidence field만 제거·추가·변경한 실행은 selected identity/order가 byte-identical해야 한다.
- selected identity에 KO/EN surface 또는 independent Menu evidence가 없으면 identity를 유지한 채 Change 5에서 `correction_required` 또는 `unverified_without_independent_consumer_evidence`를 부여한다.
- readiness가 더 좋은 차순위 candidate로 대체하는 API/branch를 두지 않는다.

- P-5는 both-source일 때 `Recipe 1 + Right-click 1` 또는 다른 structural-equivalence rule을 ratify한다.
- P-6은 W1-A가 확인한 QG canonical order key, 별도 owner-approved stable key, stable-identity-derived presentation tie-break 또는 `no_admissible_anchor` correction 중 하나를 정한다. identity-derived key를 허용할 때 canonical tuple/byte encoding과 version을 봉인하며 importance/frequency/대표성 surrogate로 쓰지 않는다.
- P-7은 exact identity duplicate suppression의 owner layer를 정한다.
- P-4가 같은-source 2개를 허용하더라도 그 내부 선택은 stable structural order만 사용한다.
- output은 모든 candidate의 disposition을 기록한다.

candidate disposition 후보:

```text
selected
excluded_capacity
excluded_exact_duplicate_identity
ineligible_not_public
ineligible_review
ineligible_exclusion
ineligible_requirement_only
correction_missing_identity
correction_missing_order_identity
```

exact vocabulary와 owner mapping은 reason registry에서 봉인한다.

`correction_missing_surface`와 `correction_missing_menu_trace`는 candidate eligibility disposition이 아니라 selected-identity readiness reason이며 Change 5/6/7에서만 발생한다.

금지:

- importance/representativeness/frequency/general usefulness ranking
- efficiency/recommendation ordering
- input array order dependency
- text similarity dedupe
- locale surface completeness를 eligibility/order key로 사용
- Menu evidence availability/parity를 eligibility/order key로 사용
- locale-dependent reselection
- readiness-dependent candidate substitution
- candidate overflow 자체를 defect로 처리
- one Source를 다른 Source의 fallback/residue로 처리

Validation:

- risk test #3의 parameterized projection/property table이 Recipe/Right-click 조합, identity/order/dedupe/overflow와 permutation·readiness-masking 불변성을 함께 검증한다.
- risk test #6 whole-universe assertion이 ratified P-5 source-equivalence invariant와 violation `0`을 검증한다.

Deliverables:

- `layer4_semantic_public_candidate_eligibility_contract`
- `layer4_projection_decision_table`
- `layer4_deterministic_selection_fixtures`
- `selection_disposition_reason_codes`
- P-5/P-6/P-7 disposition

---

### Change 5 — Locale identity, Menu parity and public-text lexical eligibility

Purpose:

KO/EN은 같은 selected identity set을 사용하도록 검증하고, Menu/Tooltip은 독립 consumer evidence가 있는 layer/row에서만 same-facts identity parity를 주장한다. evidence가 없으면 자기대조 없이 명시적 unverified 상태로 좁힌다.

Files:

- `Iris/_docs/authority/tooltip_t1/tooltip_locale_menu_parity_contract.json`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/projection.py`
- `Iris/tooling/tests/test_tooltip_t1_projection.py`
- `Iris/tooling/tests/fixtures/tooltip_t1/locale_parity/**`

Implementation Notes:

identity selection 순서는 다음으로 고정한다.

```text
Layer 2: classification_identity/category_id/primary_subcategory_id
Layer 3: fact_id
Layer 4: interaction_id
        ↓
selected semantic identity set
        ↓
requested locale surface lookup
        ↓
independent Menu consumer evidence/parity lookup
```

- KO와 EN은 같은 selected identity list와 slot order를 사용한다.
- selected identity의 locale surface가 없으면 locale readiness가 correction 상태가 된다.
- other locale, raw `display_text`, fallback label 또는 next candidate를 사용하지 않는다.
- Layer 4 selected identity는 locale/Menu readiness 계산 전에 freeze하며 readiness 결과가 selection 단계로 역류하지 않는다.
- selected A가 EN missing이고 차순위 B가 KO/EN complete여도 A를 유지하고 A의 EN correction을 기록한다.
- selected A에 independent Menu evidence가 없고 차순위 B에 evidence가 있어도 A를 유지하고 A를 `unverified_without_independent_consumer_evidence`로 기록한다.
- P-9 no-fallback/parity는 `already_fixed` required choice로 채택한다. current runtime의 recipe original/translated split과 Right-click translation-key path를 observation으로만 사용한다.
- Menu parity는 문자열 비교가 아니라 identity relation이다.

```text
Tooltip selected identity set
⊆
current Menu public fact identity set
```

- Layer 2는 independent observed Menu resolved identity, Layer 3는 independently traceable Menu-consumed source/fact identity, Layer 4는 independently traceable public interaction `label_key/use_case_id`와 비교한다.
- Menu에 public display되지 않는 debug/exclusion/requirement identity를 parity parent로 사용하지 않는다.
- current Menu가 display-unavailable placeholder를 보이는 row는 locale surface availability PASS가 아니다.
- owner output과 동일 source/record를 Menu consumer evidence로 재사용하지 않는다.
- layer/row별 parity status는 다음으로 제한한다.

```text
verified
correction_required
unverified_without_independent_consumer_evidence
not_applicable
```

- `verified`는 independent owner/consumer evidence와 identity relation이 모두 성립할 때만 허용한다.
- `correction_required`는 independent evidence가 존재하며 identity relation이 모순될 때 사용한다.
- `unverified_without_independent_consumer_evidence`는 violation 0으로 계산하지 않는다. shared-authority subset relation이 성립한 경우 해당 layer의 full Menu parity와 T3 runtime adoption claim을 보류하지만 T2 static handoff만으로는 차단하지 않는다. independent consumer evidence의 acceptance/re-audit condition은 계속 기록한다.
- shared-authority subset relation이 없거나 모순되는 경우는 `unverified`가 아니라 `correction_required`이며 T2 blocker다.
- `unverified_without_independent_consumer_evidence`는 `docs/EXECUTION_CONTRACT.md` §6-2의 `unvalidated_but_in_scope`다. `out_of_scope`로 분류하거나 scope 밖이라는 이유로 success claim에서 제외하지 않는다.
- `not_applicable`은 ratified legitimate absence로 Menu/Tooltip 양쪽에 비교할 fact가 없을 때만 사용한다.
- lexical guard는 KO/EN explicit forbidden token/phrase와 allowed contrast fixture만 검사한다.
- lexical scanner가 sentence quality, recommendation implication 또는 semantic equivalence를 판단하지 않는다.

Validation:

- risk test #4의 parameterized locale/Menu/text table이 KO/EN identity, missing locale/no fallback, A→B substitution 금지, shared-authority/consumer evidence 상태와 lexical/line-fit 경계를 함께 검증한다.

Deliverables:

- `tooltip_locale_identity_contract`
- `menu_tooltip_identity_parity_contract` with evidence admissibility and status vocabulary
- `tooltip_readiness_manifest`의 locale/Menu parity view
- `forbidden_expression_fixture_set`
- P-9 disposition

---

### Change 6 — Rich T1 audit model, minimal T2 handoff boundary and mock consumer

Purpose:

owner-attributed readiness/audit 정보는 T1 manifest에 남기고, T2에는 semantic interpretation 없이 소비할 최소 handoff schema만 제공한다.

Files:

- `Iris/_docs/authority/tooltip_t1/tooltip_t2_handoff.schema.json`
- `Iris/_docs/authority/tooltip_t1/tooltip_readiness_reason_registry.json`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/models.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py`
- `Iris/tooling/tests/test_tooltip_t1_audit.py`
- `Iris/tooling/tests/fixtures/tooltip_t1/schema/**`

Implementation Notes:

rich T1 readiness manifest는 Change 2~5와 Change 7이 요구하는 authority, parity, readiness, owner, reason과 correction trace를 소유한다. 이 필드는 T2 handoff schema에 복제하지 않는다.

`T2_FULL_DATA_PROGRESSION = OPEN`일 때만 생성하는 T2 handoff row는 다음 최소 구조로 제한한다.

```text
schema_version
subject_binding_ref
full_type
slots[]
  slot_id
  semantic_identity
  localized_surfaces {ko,en}
```

slot은 semantic S1→S4 순서로 이미 정렬되며 legitimate absence slot은 handoff에서 제거한다. handoff가 존재한다는 사실 자체가 해당 subject의 T2-blocking correction, unresolved contract decision과 mock consumer product decision이 0임을 뜻한다.

전체 Layer 4 candidate set, eligibility, capacity/duplicate disposition, authority refs, Menu evidence, readiness와 correction은 external audit/readiness manifest가 소유한다. mechanical T2 consumer가 선택이나 품질 판정을 다시 수행할 이유가 없으므로 T2 handoff에는 unselected candidate, readiness, parity, owner, reason 또는 blocker field를 넣지 않는다.

다음 raw/internal field는 minimal T2 handoff schema에서 제외한다.

- raw classification tag arrays
- Rule predicate/debug trace
- unapproved QG internals
- quality/importance/frequency score
- rewrite/summarization suggestion
- predecessor lifecycle state
- raw source text fallback
- semantic-dedupe hint
- authority/menu consumer evidence
- readiness/parity/quality state
- defect owner/reason/blocker metadata

reason-code family는 defect attribution에만 사용한다.

```text
SUBJECT_*
SUPPORT_*
CLASSIFICATION_*
DVF_*
QG_*
LOCALE_*
IDENTITY_*
PARITY_*
LINE_FIT_*
CONTRACT_*
```

- 모든 blocking code는 owner class, affected layer, acceptance condition과 re-audit condition을 가진다.
- unknown owner/reason/enum/schema version은 fail-loud한다.
- multiple issues를 generic `not_ready` 하나로 축약하지 않는다.
- `blocked_contract_decision`과 readiness enum은 T2 handoff schema에 포함하지 않는다. unresolved decision은 candidate execution receipt에서 중단 원인으로만 기록한다.
- `LINE_FIT_EMBEDDED_NEWLINE`과 `LINE_FIT_LOGICAL_ROW_OVERFLOW`만 T2-blocking이며 width proxy 계열은 존재할 경우 항상 advisory다.
- parity status가 `unverified_without_independent_consumer_evidence`이면 T1 audit manifest에 evidence-gap owner와 re-audit condition을 남긴다. shared-authority subset relation이 성립하면 T2 blocker가 아니며, relation 부재/모순은 별도 correction reason으로 T2를 차단한다.
- Layer 4 selected row의 locale/Menu readiness field를 바꾸어도 `interaction_id`, `source`, `slot_id`, selected order를 재계산하지 않는다. schema/model API도 readiness에서 selection으로 되돌아가는 dependency를 제공하지 않는다.
- mock consumer는 ordered slot read, requested locale surface read와 fixed-order concatenation만 구현한다. legitimate absence compaction은 handoff 생성 전에 T1이 끝낸다.
- mock consumer에 sorting/ranking/truncation/fallback/repair API를 두지 않는다.

Validation:

- risk test #5의 parameterized handoff/mock table이 minimal schema strictness, audit-field rejection, OPEN-only generation, ordered KO/EN concatenation과 product-decision `0`을 함께 검증한다.
- risk test #6의 audit/progression table이 readiness reason owner/re-audit completeness, unknown reason 거부와 handoff/progression consistency를 검증한다.

Deliverables:

- `tooltip_t2_handoff_schema`
- `schema_fixture_set`
- `readiness_state_model`
- `reason_code_registry`
- `mock_projection_consumer`

---

### Change 7 — Whole-universe readiness audit and correction ledger

Purpose:

대표 sample이 아니라 owner-ratified Tooltip support universe 전체를 동일 contract로 판정한다.

Files:

- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py`
- `Iris/tooling/tests/test_tooltip_t1_audit.py`
- external readiness/correction/blocker artifacts

Implementation Notes:

각 supported FullType row에는 최소 다음을 기록한다.

| Field | Required content |
| --- | --- |
| `full_type` | case-sensitive canonical identity |
| `support_state` | supported/explicitly excluded contract state |
| `classification` | resolved IDs, KO/EN surface, separate authority/Menu consumer refs, parity status |
| `layer3` | fact identity, source ids, KO/EN surface, eligibility |
| `recipe_candidates` | semantic/public eligibility and selection disposition; locale/Menu readiness is not an eligibility field |
| `rightclick_candidates` | semantic/public eligibility and selection disposition; locale/Menu readiness is not an eligibility field |
| `layer4_selected` | frozen selected identities/slot mapping plus KO/EN and Menu readiness |
| `ko_slot_count` / `en_slot_count` | 0~4 logical slots |
| `semantic_slot_states` | locale-independent selected / legitimate absence / identity correction state |
| `ko_readiness` / `en_readiness` | per-locale surface readiness |
| `overall_readiness` | aggregate projection state |
| `menu_parity_by_layer` | verified/correction/unverified/not-applicable with evidence refs |
| `owner` | upstream/cross-owner attribution |
| `reason_codes` | registry-valid codes |
| `t2_blocking` | explicit boolean |
| `subject` | exact generation/readpoint binding |

completeness invariants:

```text
audited supported FullTypes
==
owner-ratified current Tooltip support universe

duplicate audited FullType = 0
missing supported FullType = 0
unexpected supported FullType = 0
unclassified readiness = 0
unknown defect owner = 0
unknown reason code = 0
missing re-audit condition = 0
supported row removed because of readiness defect = 0
unclassified Menu parity status = 0
owner-output self-comparison = 0
Layer 4 selected identity changed by locale readiness = 0
Layer 4 selected identity changed by Menu evidence availability = 0
```

correction ledger row는 최소 다음을 요구한다.

```text
full_type
locale
layer
owner
observed_state
expected_contract
reason_code
selected_identity_ref
t2_blocking
correction_acceptance_condition
re_audit_condition
subject_binding_ref
```

- correction 자체는 수행하지 않는다.
- W1-B에서 freeze한 support denominator는 missing classification/DVF/QG/translation/order/parity/line-fit readiness 때문에 축소하지 않는다.
- silent Layer 3 row를 일괄 defect로 취급하지 않는다.
- capacity-excluded Layer 4 candidate를 defect로 취급하지 않는다.
- missing stable identity/order/locale/menu trace는 legitimate absence로 완화하지 않는다.
- audit observations와 fixture expectations를 별도 artifact로 유지하고 comparator에서만 대조한다.
- candidate input order를 permutation한 재실행에서도 selected identity/readiness가 같아야 한다.
- audit 중 source/runtime tree hash가 바뀌면 결과를 폐기하고 `blocked_source_mutation`으로 닫는다.
- execution-time support subject가 변경되면 이전 audit을 자동 재사용하지 않는다.
- `legitimate_absence`는 layer, locale, reason code, authority reference별 분포를 summary에 기록하고 각 row에 positive owner proof를 요구한다. 단순 input 결손은 absence proof가 아니다.
- Recipe-only, Right-click-only, both-source universe별 eligible/selected/capacity-excluded 분포를 기록한다. both-source row에는 P-5 source-equivalence invariant 결과를 기록한다.
- Menu parity는 layer/status별 분포와 evidence route를 기록한다. `unverified_without_independent_consumer_evidence`를 PASS 또는 zero violation으로 합산하지 않는다. shared-authority subset relation이 성립한 unverified는 T2 blocker에서 제외하고 T3 runtime adoption 검증 대상으로 남기며, relation 부재/모순만 T2-blocking correction으로 센다.
- Layer 4 selection trace와 selected-readiness trace를 별도 record/field group으로 유지한다. readiness producer는 selection writer API를 갖지 않는다.
- locale/Menu evidence masking run은 base run과 같은 Layer 4 selected identity/order를 가져야 하며 달라지면 `IDENTITY_READINESS_FEEDBACK_VIOLATION`으로 fail-loud한다.

Validation:

- risk test #6의 whole-universe table이 denominator equality, readiness/owner/reason, absence proof, source-equivalence, source hash와 stale subject를 검증한다.
- risk test #3/#4의 whole-universe assertion이 Layer 4 invariance와 KO/EN/Menu relation을 동일 audit result 위에서 재확인한다.

Deliverables:

- `tooltip_readiness_manifest`
- `tooltip_readiness_manifest`의 canonical aggregate section
- `upstream_correction_ledger`
- `T2_blocker_summary`
- current Tooltip baseline observation
- exact subject binding record

---

### Change 8 — Contract adoption, deterministic validation and T2 handoff

Purpose:

contract/schema/audit의 상호 모순을 닫고 T2가 추가 제품 판단 없이 진행 가능한지를 별도 progression axis로 기록한다.

Files:

- all tracked T1 contract/schema/fixtures
- `docs/iris_tooltip_t1_display_contract_policy.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `Iris/build/ENTRYPOINTS.md`
- `Iris/_docs/authority/iris_current_authority_manifest.json`
- `Iris/_docs/authority/iris_current_route_index.json`
- conditional `Iris/_docs/round3/current_route_required_validations.json`
- external handoff/validation/receipt artifacts

Implementation Notes:

다음 산출물의 schema/identity/decision을 cross-check한다.

```text
subject binding
support contract
P-1~P-12 decision contract
display/absence contract
Layer 2 input contract
Layer 3 input contract
Layer 4 eligibility/projection contract
Layer 4 selected-identity readiness contract
locale contract
Menu parity contract
minimal T2 handoff schema
readiness manifest
correction ledger
reason registry
mock consumer result
```

- contract-level unresolved decision이 하나라도 있으면 handoff 불가다.
- T2 mock consumer가 raw inference, semantic choice 또는 fallback을 요구하면 handoff 불가다.
- `T2_FULL_DATA_PROGRESSION`은 `OPEN`, `BLOCKED_BY_UPSTREAM_CORRECTIONS`, `BLOCKED_BY_T1_CONTRACT_INCOMPLETENESS`, `BLOCKED_BY_MIXED_CAUSES`를 구분한다.
- progression record에는 `blocking_cause_classes[]`, `blocking_cause_owners[]`, source artifact refs, blocker counts와 acceptance/re-audit conditions를 필수로 둔다.
- unresolved contract decision 또는 mock consumer product-decision은 T1 contract incompleteness로 귀속하며 upstream correction으로 표현하지 않는다.
- classification/DVF/QG/locale/Menu evidence 결손처럼 owner-attributed external input correction만 남으면 upstream correction으로 귀속한다. 두 종류가 함께 있으면 mixed cause를 사용한다.
- `OPEN`은 upstream T2 blocker 0, contract-level unresolved decision 0과 mock consumer product-decision 0일 때만 허용한다. shared-authority subset relation이 성립한 consumer-evidence `unverified`는 T2 blocker가 아니며, authority relation 부재/모순은 upstream T2 blocker다.
- P-1은 `already_fixed` 두 축 분리를 채택한다. 구현자가 별도 `T1_COMPLETE` 의미를 재정의하지 않는다.
- adopted contract는 기존 DECISIONS를 조용히 수정하지 않고 additive successor/refinement로 연결한다.
- `docs/ARCHITECTURE.md`와 `docs/ROADMAP.md`는 execution-side narrative edit가 아니라 owner-sealed adoption receipt를 인용하는 additive update만 허용한다. predecessor 문구를 조용히 대체하지 않는다.
- current route index에는 current navigation에 필요한 최소 route만 추가한다. audit latest pointer나 mutable result locator를 넣지 않는다.
- one-off census/ledger는 regular validation membership에 자동 포함하지 않는다.
- 최소 validator를 regular membership으로 채택하는 경우 owner reason, execution cost, failure attribution과 exact membership delta를 기록한다.
- exact terminal implementation subject는 canonical clean-checkout full gate가 소유하는 Run A/B와 deterministic comparator를 통과해야 한다. 별도 lifecycle Run A/B를 중복 수행하지 않는다.
- Layer 4 selection contract graph에는 locale/Menu readiness input edge가 없어야 하고, readiness contract graph에는 selected identity writer edge가 없어야 한다.

Validation:

- focused 6 risk-focused parameterized test family 전체 exit `0`
- candidate `--verify-invariants`의 permutation/readiness-masking/source-mutation assertion exit `0`
- whole-universe denominator/readiness/correction/progression consistency exit `0`
- canonical full-gate Run A/B deterministic comparator exit `0`
- current route/membership/tool disposition과 claim ceiling consistency exit `0`

Deliverables:

- canonical T1 contract candidate/adoption receipt
- final readiness manifest
- final correction ledger
- bounded validation report
- `OPEN`일 때만 생성하는 minimal T2 handoff input
- `OPEN`일 때만 생성하는 T2 handoff manifest
- blocked일 때 생성하는 cause-attributed T2 progression record
- `T2_FULL_DATA_PROGRESSION` result
- axis-separated contract/audit closeout record

---

## 7. Validation Plan

### Automated Validation

#### 7.1 Focused package tests

예상 command는 다음과 같다. exact test list는 W0 tool disposition에서 freeze한다.

```powershell
uv run --project .\Iris\tooling python -B -m pytest `
  .\Iris\tooling\tests\test_tooltip_t1_contract.py `
  .\Iris\tooling\tests\test_tooltip_t1_projection.py `
  .\Iris\tooling\tests\test_tooltip_t1_audit.py `
  -q
```

테스트 수는 구현 세부 branch마다 늘리지 않고 다음 **6개 risk-focused parameterized test family**로 제한한다. 세 파일에 각각 두 family를 둔다.

1. subject/decision lifecycle — subject/hash/current route, stale/dirty rejection, W0→W1-A→G1→W1-B와 P authority
2. slot/Layer 2/Layer 3 input contract — semantic/locale state, absence, resolved identity, no raw inference와 no rewrite
3. Layer 4 projection invariance — eligibility/order/dedupe/source-equivalence, permutation과 readiness masking 불변성
4. locale/Menu/public text — KO/EN identity/no fallback, shared-authority/consumer evidence 상태, lexical/newline/width 경계
5. minimal T2 handoff/mock consumer — strict schema, audit-field rejection, OPEN-only handoff와 product-decision `0`
6. whole-universe audit/progression — denominator, readiness/owner/reason, source immutability와 progression consistency

각 번호는 하나의 parameterized test family를 기본으로 한다. 새 edge case는 기존 table row로 추가하며 독립 test function/file을 만들지 않는다. 발견된 결함의 재현에 독립 격리가 반드시 필요한 경우에만 test를 추가하고 closeout에 증가 이유를 기록한다.

#### 7.2 Lifecycle-bound T1 candidate run

개발 중에는 installed wheel/fresh environment에서 exact subject와 empty external root를 사용해 candidate run을 한 번 수행한다.

```powershell
iris-tooling --repository-root <repo> build tooltip-t1 `
  --output-root <external-empty-candidate-run> `
  --decision-contract-sha256 <sha256> `
  --verify-invariants
```

candidate command는 같은 bound input을 메모리에서 permutation하고 locale/Menu readiness를 mask/restore하는 `--verify-invariants` 동등 모드를 내부적으로 한 번 수행한다. 이 검사는 selected identity/order 불변과 readiness-only delta만 확인하며 별도 external lifecycle run/root를 만들지 않는다.

terminal subject의 반복 실행 결정성은 §7.4 canonical receipt-bound full gate가 이미 소유하는 Run A/B와 comparator로 한 번만 검증한다. T1 전용 lifecycle Run A/B를 별도로 반복하지 않는다.

#### 7.3 Whole-universe gates

필수 식:

```text
audited supported FullTypes
==
current bound Tooltip support universe
```

unconditional zero metrics:

```text
duplicate_full_type = 0
missing_supported_full_type = 0
unexpected_supported_full_type = 0
unclassified_readiness = 0
unknown_owner = 0
unknown_reason_code = 0
missing_reaudit_condition = 0
raw_semantic_inference_path = 0
locale_dependent_reselection = 0
cross_locale_fallback = 0
menu_parity_unclassified = 0
menu_owner_output_self_comparison = 0
mock_consumer_product_decision = 0
progression_unknown_blocking_cause_owner = 0
source_equivalence_contract_violation = 0
supported_row_removed_for_readiness_defect = 0
layer4_selection_changed_by_locale_readiness = 0
layer4_selection_changed_by_menu_evidence = 0
source_mutation = 0
```

`layer4_selection_changed_by_locale_readiness`와 `layer4_selection_changed_by_menu_evidence`의 evidence carrier는 `layer4_invariance_result.json`의 `readiness_masking` section이다. section이 없거나 base/masked/restored subject/candidate-set identity가 다르면 metric을 0으로 간주하지 않고 validation을 fail-loud한다.

claim-conditional zero metrics:

```text
menu_parity_contradiction = 0
  for rows/layers claimed verified or ready

menu_parity_unverified = 0
  only for a full Menu-parity or T3 runtime-adoption readiness claim
```

ready가 아닌 row는 parity contradiction/evidence gap을 숨기지 않고 `correction_required` 또는 `unverified_without_independent_consumer_evidence`와 owner/reason으로 남긴다. `menu_parity_unverified > 0`이어도 T1 contract/audit 자체는 gap을 완전히 귀속했다면 complete일 수 있고, shared-authority subset relation이 성립하면 `T2_FULL_DATA_PROGRESSION = OPEN`도 가능하다. 다만 해당 범위는 `unvalidated_but_in_scope`이며 full Menu-parity와 T3 runtime-adoption readiness claim은 금지한다.

whole-universe summary는 추가로 다음 분포를 출력하고 contract fixture와 대조한다.

- `legitimate_absence` by layer/locale/reason/authority proof
- Recipe-only/Right-click-only/both-source eligible and selected counts
- P-5 source-equivalence invariant result for every both-source FullType
- parity status by layer/evidence route
- T2 blocker by cause class and owner

#### 7.4 Current repository validation

terminal tracked subject에서는 `Iris/build/ENTRYPOINTS.md`가 소유한 current route를 사용한다.

read-only membership 확인:

```powershell
uv run python .\Iris\_docs\round3\round3_run_contract_tests.py --class current --list
```

receipt-bound full validation:

```powershell
iris-tooling --repository-root <repo> validate full `
  --commit <terminal-commit> `
  --claim-id <claim-id> `
  --environment-receipt <external-environment-receipt> `
  --work-root <external-empty-work-root> `
  --result-root <external-empty-result-root> `
  --orchestration-receipt <external-new-orchestration-receipt>
```

Run A/B와 comparator는 `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1` 및 `invoke_deterministic_compare.ps1`의 current parameter/receipt contract를 따른다. 계획 문서가 validation membership, phase list 또는 verdict를 복제해 별도 authority가 되지 않는다.

#### 7.5 Conditional validation

- T1 범위에서 Lua를 수정하지 않으므로 Lua syntax validation은 기본 required set이 아니다.
- 예상 밖 Lua/runtime mutation이 필요해지면 이 계획을 확대하지 않고 중단해 별도 plan/authorization을 요구한다.
- `pyproject.toml` 또는 package data가 바뀌면 exact wheel build/install/fresh-environment import test를 추가한다.
- current-route membership이 바뀌면 before/after identity count와 failure attribution을 기록한다.

### Manual Validation

- decision/support review: P-1~P-12 owner·authority·same-subject evidence와 support inclusion/exclusion을 한 번 검토
- representative input review: Layer 2 multi-tag/override, Layer 3 core/absence/review, Layer 4 Recipe-only/Right-click-only/both-source/overflow를 각 1개 이상 검토
- identity/readiness review: KO/EN missing surface, independent Menu evidence 유무와 shared-authority relation, selection-before-readiness code path를 검토
- boundary review: legitimate absence/defect 분리, correction owner/re-audit, 최소 T2 handoff와 mock consumer product-decision `0`을 검토
- claim review: current Tooltip observation과 width advisory가 runtime/visual PASS로 확대되지 않았는지 검토

T1 기본 범위에서는 PZ in-game manual acceptance를 수행하지 않는다.

### Validation Limits

T1은 다음을 검증하거나 주장하지 않는다.

- actual PZ Tooltip rendering acceptance
- Alt key runtime behavior
- automatic wrapping/pixel width/font/UI scale acceptance
- runtime cache correctness or performance
- static Lua generation/install/package projection
- save/load, multiplayer, long session
- external-mod compatibility sweep
- all-natural-language semantic correctness
- translation quality approval
- upstream Classification/DVF/QG correction 완료
- DVF freeze, RTC, Publish, package, release, Workshop, deployment readiness

formal closeout은 `docs/EXECUTION_CONTRACT.md` §6-2에 따라 validation ceiling을 다음 세 분류로 기록한다.

| Ceiling class | T1 classification |
| --- | --- |
| `validated` | exact-subject contract/schema/audit, deterministic identity selection, locale/Menu readiness attribution과 실제 exit `0` evidence가 있는 항목 |
| `unvalidated_but_in_scope` | independent Menu consumer evidence가 없어 `unverified_without_independent_consumer_evidence`인 layer/row 및 그 parity claim |
| `out_of_scope` | 위 목록의 runtime rendering, package/install, compatibility, upstream mutation completion, freeze/publish/release/deployment |

`unvalidated_but_in_scope`가 비어 있지 않으면 그 범위의 Menu/Tooltip parity success claim을 하지 않는다. 이를 `out_of_scope`로 옮겨 claim을 넓히거나 숨기지 않는다. 각 closeout은 세 분류의 artifact/count/reference를 모두 기록한다.

P-11이 offline width proxy를 채택하더라도 proxy PASS는 actual visual-line PASS가 아니다. P-12가 `contract regression` 용어를 채택하더라도 actual runtime regression acceptance는 T1 success claim에 포함하지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

**높음.**

새 game fact authority를 만들지는 않지만 다음 presentation/consumption boundary를 current contract로 봉인한다.

- Tooltip support scope
- slot meaning/order/absence
- Layer 2/3/4 admissibility
- Layer 4 bounded projection
- locale identity/no-fallback
- Menu parity
- readiness/reason/owner attribution
- T2 input schema/progression gate

Classification, DVF System, QG의 semantic ownership은 이전하지 않는다.

### Runtime Behavior Surface

**없음.**

- runtime Lua mutation 없음
- current Tooltip/Menu payload mutation 없음
- Alt behavior/cache/layout mutation 없음

T1 contract는 후속 T2/T3가 할 수 있는 일을 제한하지만 T1 실행 자체는 user-visible runtime behavior를 바꾸지 않는다.

### Compatibility Surface

**직접 변경 없음.**

- public Lua API/require/global contract 변경 없음
- external mod runtime contract 변경 없음
- package payload 변경 없음

installed offline CLI에 lifecycle-bound target이 추가될 수 있으나 기존 build target과 validation authority의 behavior를 변경하지 않는다.

### Sealed Artifact Surface

**높음, read-only.**

- current authority manifest/route
- Classification runtime artifact
- Layer 3 facts/decisions/readiness policy/pointer-selected generation/locale companion
- Layer 4 current source/output seed and runtime projection
- translations
- Menu/Tooltip runtime source

기존 artifact는 수정하지 않는다. 새 T1 contract adoption은 additive record로 처리한다.

### Public-Facing Output Surface

**T1 direct mutation 없음 / future contract impact 있음.**

T1은 public string을 바꾸지 않지만 향후 Tooltip에 표시할 수 있는 identity와 fail-closed 조건을 제한한다. contract impact를 current output change로 표현하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- T1/T2가 Classification/DVF/QG 위의 네 번째 semantic authority가 될 위험
- Menu runtime selection logic을 offline T1에서 복제해 dual Layer 2 authority를 만들 위험
- runtime/generated output을 source authority로 역승격할 위험
- Layer 3 body를 Tooltip fact database로 다시 분해하며 heuristic authority를 만들 위험
- Layer 4 projection schema가 독립 mini facts database로 성장할 위험
- one-off audit/correction ledger를 regular validation 또는 mutable registry로 승격할 위험
- current installed package와 retired source-root copy에 구현을 중복할 위험
- support denominator를 adjacent universe count로 대체할 위험
- readiness 결손 FullType을 denominator에서 제거해 coverage goalpost를 축소할 위험
- W1-A census 전에 P-6/P-10을 ratify하거나 P-11 fixed scope를 width-blocking 정책으로 다시 여는 위험
- Classification owner output을 Menu consumer evidence로 재사용해 Layer 2 parity를 자기 검증할 위험

### Runtime Risk

T1 planned mutation은 없지만 후속 handoff 오해에 따른 간접 위험이 있다.

- mock consumer를 production runtime generator처럼 확장할 위험
- current Tooltip baseline을 T1 target behavior로 잘못 채택할 위험
- missing data를 runtime fallback/repair 요구로 넘길 위험
- logical 4 row를 actual wrapped visual 4줄로 오인할 위험

### Compatibility Risk

- supported `IrisPrimarySubcategory` global과 Menu behavior를 T1 structured input이 성급히 대체할 위험
- FullType case sensitivity와 Windows filesystem semantics를 혼동할 위험
- current Menu identity shape와 minimal T2 handoff schema를 같은 public API로 오인할 위험
- package command 추가가 기존 legacy alias/target routing을 바꿀 위험
- external mod/runtime item universe를 exact offline support universe와 혼동할 위험

### Regression Risk

- `legitimate_absence`로 required input defect를 숨길 위험
- multi-tag Layer 2에서 category/primary subcategory를 서로 다른 rule로 선택할 위험
- `description_ready`를 이유로 combined Menu body 전체를 Tooltip에 넣을 위험
- acquisition text를 core description으로 승격할 위험
- stable identity lexical order를 importance ranking surrogate로 사용할 위험
- source array ordinal에 selection이 의존할 위험
- Recipe/Right-click 중 한 source를 구조적으로 잔여화할 위험
- candidate overflow를 upstream defect로 오인할 위험
- same text/different identity를 dedupe할 위험
- selected locale surface 누락을 다른 candidate로 숨길 위험
- Layer 4 locale completeness가 semantic/public eligibility에 섞여 selected identity를 바꿀 위험
- independent Menu evidence availability가 더 잘 검증되는 차순위 candidate로 substitution을 유발할 위험
- string equality를 Menu parity로 사용할 위험
- independent Menu consumer evidence가 없는 row를 parity PASS로 세는 위험
- lexical scanner를 unrestricted semantic judge로 확대할 위험
- fixture expectation과 audit observation이 같은 producer에서 생성되어 자기 검증할 위험
- stale audit를 new current generation에 재사용할 위험
- T1 completion과 T2 progression을 하나의 PASS로 축약할 위험
- T1 contract incompleteness를 `BLOCKED_BY_UPSTREAM_CORRECTIONS`로 오귀속할 위험

---

## 10. Rollback Plan

T1은 runtime/product payload를 변경하지 않으므로 runtime rollback은 없다.

### Before contract adoption

- external candidate/audit root를 rejected evidence로 보존하거나 폐기한다.
- current Classification/DVF/QG/Menu/Tooltip authority와 runtime artifact는 그대로 유지한다.
- subject/decision/schema/fixture가 불완전하면 corrected additive candidate를 새 external root에서 재생성한다.
- failed result를 같은 path에서 PASS로 덮어쓰지 않는다.

### After contract adoption

- accepted contract/schema/decision record를 조용히 수정하지 않는다.
- 오류 발견 시 successor/supersession contract를 additive하게 만든다.
- affected FullType과 exact successor subject를 다시 audit한다.
- current authority manifest/route는 successor adoption record를 통해 갱신한다.
- predecessor contract와 당시 audit는 historical subject observation으로 보존한다.

### Tooling rollback

- 새 package command/producer가 current contract를 만족하지 못하면 prior installed tooling owner와 command route를 유지한다.
- 기존 build target/validation adapter behavior를 되돌리되 failed receipt/evidence는 삭제하지 않는다.
- partial CLI adoption, dual current producer 또는 source-root fallback은 허용하지 않는다.

### Upstream correction

- Classification/DVF/QG/locale correction은 별도 owner scope에서 수행한다.
- correction 후 affected subject의 hash가 바뀌면 기존 audit는 stale observation이 된다.
- new exact subject에서 affected row 또는 owner-ratified full range를 재-audit한다.
- T1 correction ledger가 upstream mutation authorization 역할을 하지 않는다.

### Immediate stop conditions

다음이 발견되면 해당 execution을 즉시 중단한다.

- raw tag interpretation 또는 Menu selection rule 복제
- Layer 3 body truncation/summarization/rewrite
- text similarity dedupe 또는 semantic ranking
- locale fallback/reselection
- Layer 4 locale/Menu readiness를 pre-selection eligibility/order/dedupe/source-equivalence input으로 사용
- selected Layer 4 identity의 readiness 결손을 이유로 next candidate substitution
- unratified P decision 적용
- W1-A 이전 open decision ratification 또는 W1-A와 다른 subject evidence 인용
- rendered/runtime output의 source-authority 승격
- source/runtime mutation
- support denominator substitution
- readiness defect를 이유로 frozen support denominator 축소
- owner output과 Menu consumer evidence 자기대조
- unknown owner/reason/identity를 generic readiness로 축약
- fixture expectation과 audit observation의 self-seeding
- current/historical/reproduction role violation

---

## 11. Governance Constraints

- `docs/Philosophy.md`의 evidence, neutrality, silence-on-insufficient-evidence, Menu/Tooltip surface와 100% Lua runtime 원칙을 보존한다.
- Iris는 Pulse 외 다른 Spoke를 직접 참조하지 않는다. 이번 작업은 새 inter-Spoke dependency를 추가하지 않는다.
- Classification/Rule은 Layer 2, DVF System은 Layer 3, QG는 Layer 4 semantic authority를 계속 소유한다.
- T1은 Tooltip projection/readiness metadata만 소유한다.
- Recipe와 Right-click은 독립적이고 동등한 Source다.
- Menu와 Tooltip은 같은 semantic identity를 다른 깊이로 표시한다.
- `primary_subcategory`는 navigation anchor이며 Layer 3 fact authority가 아니다.
- Layer 3 optionality를 모든 item의 mandatory description으로 되돌리지 않는다.
- acquisition information과 core description을 분리한다.
- QG REVIEW/exclusion/debug/quality/requirement-only state를 public interaction으로 승격하지 않는다.
- importance/frequency/recommendation/efficiency/representativeness ranking을 사용하지 않는다.
- semantic duplicate를 text similarity로 판정하지 않는다.
- raw input array order를 stable presentation order로 사용하지 않는다.
- identity를 locale text보다 먼저 선택한다.
- Layer 4는 semantic/public eligibility와 identity selection을 locale/Menu readiness보다 먼저 완료하고 selected identity를 freeze한다.
- missing locale/Menu evidence는 selected Layer 4 identity를 유지한 채 correction/unverified로 귀속하며 차순위 candidate substitution을 금지한다.
- cross-locale raw-text fallback과 locale-dependent candidate reselection을 금지한다.
- defect를 legitimate absence 또는 partial Tooltip로 숨기지 않는다.
- current subject binding 없는 audit를 재사용하지 않는다.
- installed `iris_tooling` package가 current producer를 소유하며 retired source-root copy를 current 구현으로 복원하지 않는다.
- runtime/generated/baseline/reproduction artifact는 current authority가 exact role을 채택하지 않는 한 semantic source가 아니다.
- audit output과 run receipt는 repository-external immutable result root에 둔다.
- mutable latest pointer, cross-run ledger 또는 stateful registry를 만들지 않는다.
- one-off audit/census/correction ledger를 regular validation authority로 자동 승격하지 않는다.
- regular membership 변경은 owner disposition, exact identity delta, execution cost와 failure attribution을 요구한다.
- P-1~P-12 definition/adoption/open decision은 owner-ratified hash-bound contract 없이 구현하지 않는다.
- `open_in_T1` 결정은 same-subject W1-A census evidence 없이 ratify하지 않는다. `already_fixed` decision은 owner choice로 다시 열지 않는다.
- owner output을 actual Menu consumer evidence로 자기대조하지 않으며, 독립 evidence가 없으면 parity claim을 `unverified`로 좁힌다.
- unverified parity는 `unvalidated_but_in_scope`로 공개하며 `out_of_scope`로 재분류하지 않는다.
- `docs/ARCHITECTURE.md`/`docs/ROADMAP.md` adoption update는 owner-sealed additive record와 receipt를 요구한다.
- exact relevant command exit `0` 없이는 PASS를 주장하지 않는다.
- T1 result를 runtime, package, compatibility, freeze, Publish, release 또는 deployment PASS로 확대하지 않는다.

---

## 12. Expected Closeout State

### Planning-time expected closeout

Expected closeout target: **conditional / decision-gated**

P-1의 required choice에 따라 실행은 두 축을 분리해 닫는다. `contract_and_audit_axis`는 T1 자체 계약/감사의 충족도를, `T2_FULL_DATA_PROGRESSION`은 후속 full-data generation 가능 여부와 차단 원인을 표현한다.

```text
contract_and_audit_axis
  = complete | partial | blocked

T2_FULL_DATA_PROGRESSION
  = OPEN
  | BLOCKED_BY_UPSTREAM_CORRECTIONS
  | BLOCKED_BY_T1_CONTRACT_INCOMPLETENESS
  | BLOCKED_BY_MIXED_CAUSES
```

`contract_and_audit_axis`는 task-specific result axis이며 `docs/EXECUTION_CONTRACT.md` §7-1의 formal execution closeout state를 대체하지 않는다. `T2_FULL_DATA_PROGRESSION`도 formal state가 아니라 orthogonal handoff gate다.

| Task-specific result | Formal closeout mapping |
| --- | --- |
| `contract_and_audit_axis = complete` | 모든 plan criteria, exit-0 evidence, §6-2 ceiling과 owner-sealed adoption을 충족하므로 formal `complete`에만 mapping 가능 |
| `contract_and_audit_axis = partial` | formal `partial` |
| `contract_and_audit_axis = blocked` | missing external authority/evidence/dependency로 진전 불가일 때 formal `blocked`; 내부 구현/검증 미완료일 뿐이면 `partial` 또는 `implemented_only` |
| implementation artifacts complete, required validation missing | axis를 `complete`로 기록하지 않고 formal `implemented_only` |
| any `T2_FULL_DATA_PROGRESSION` value | formal state를 자동 결정하거나 변경하지 않음 |

axis-separated closeout record는 task-specific 두 축, formal closeout state, `validated`/`unvalidated_but_in_scope`/`out_of_scope`, non-claims를 함께 기록한다.

pre-full-gate candidate는 `contract_and_audit_axis = partial`, `formal_closeout_state = implemented_only`로만 기록한다. canonical same-subject Run A/Run B와 deterministic comparator가 모두 exit `0`이고 candidate/gate/comparator receipt의 path·SHA-256·subject가 검증된 뒤에만 lifecycle-bound `finalize tooltip-t1` 경계가 repository-external empty root에 `contract_and_audit_axis = complete`, `formal_closeout_state = complete`인 final closeout을 쓸 수 있다. gate failure, receipt hash failure 또는 subject mismatch에서는 final closeout 파일을 만들지 않는다.

상류 correction이 남았다는 사실만으로 contract/audit axis를 `partial`로 낮추지 않는다. 아래 T1 completion criteria가 모두 충족되고 gap의 owner/reason/acceptance/re-audit가 완결되면 contract/audit axis는 `complete`일 수 있다. T1 criteria 자체가 미충족이면 `partial` 또는 `blocked`이며 이를 upstream-only blocker로 표현하지 않는다.

### Contract/audit axis completion criteria

다음 목록은 모두 필요한 조건이며 각 항목만으로 충분조건이 아니다. formal `complete`는 1~18 전체 충족, exact required validation command exit `0`, same-subject deterministic receipt, owner-sealed adoption receipt가 함께 있을 때만 허용한다. G1-D에서 gap-ledger-only closeout을 선택했거나 unresolved decision 때문에 final manifest를 만들지 못하면 `complete`가 아니다.

1. exact current Tooltip support universe가 owner-ratified subject에 결속되어 있다.
2. supported FullType 전체가 정확히 한 번 audit되었다.
3. canonical P-1~P-12의 fixed/open status가 보존되고 모든 `open_in_T1` decision이 same-subject W1-A evidence를 인용해 ratify되었다.
4. slot meaning/order/absence decision table이 완전하다.
5. Layer 2 official resolved input owner가 지정되었거나 gap이 correction으로 귀속되었다.
6. Layer 3 approved fact identity/surface와 readiness mapping이 완전하다.
7. Layer 4 semantic/public eligibility와 identity selection이 locale/Menu readiness보다 먼저 닫히며, ordering/duplicate/source-equivalence/projection이 deterministic하고 readiness perturbation에도 selected identity가 불변이다.
8. KO/EN selection이 identity-first이고 no-fallback이다.
9. 모든 applicable layer/row에 shared-authority relation과 Menu consumer evidence status가 있으며 owner-output 자기대조가 0이다. consumer-unverified row는 `unvalidated_but_in_scope`로 기록하고 full parity/T3 adoption claim을 하지 않되 authority relation이 성립하면 T2 blocker로 세지 않는다.
10. 모든 row에 per-locale/overall readiness가 있다.
11. 모든 correction에 owner, reason, blocker, acceptance/re-audit condition이 있다.
12. 최소 T2 handoff schema가 audit/readiness/parity/owner/reason 및 raw semantic internals를 포함하지 않는다.
13. mock consumer product-decision count가 0이다.
14. focused 6 risk-focused parameterized test family, candidate invariant check와 canonical full-gate Run A/B/comparator가 exit `0`이다.
15. current source/runtime mutation이 0이다.
16. readiness defect 때문에 W1-B frozen support denominator에서 제거된 row가 0이다.
17. `legitimate_absence` positive proof와 layer/locale/reason 분포, Recipe/Right-click universe-level equivalence invariant가 완전하다.
18. owner-sealed additive adoption receipt가 contract/schema/DECISIONS/ARCHITECTURE/ROADMAP update identity와 formal validation ceiling을 결속한다.

### T2 progression

다음일 때만:

```text
T2-blocking correction count == 0
and contract-level unresolved decision count == 0
and mock consumer product-decision count == 0
```

다음을 기록한다.

```text
T2_FULL_DATA_PROGRESSION = OPEN
```

그 외에는 원인에 따라 다음 중 정확히 하나를 기록한다.

```text
upstream blockers > 0 and T1 contract blockers == 0
→ BLOCKED_BY_UPSTREAM_CORRECTIONS

upstream blockers == 0 and T1 contract blockers > 0
→ BLOCKED_BY_T1_CONTRACT_INCOMPLETENESS

upstream blockers > 0 and T1 contract blockers > 0
→ BLOCKED_BY_MIXED_CAUSES
```

progression record는 `blocking_cause_classes[]`, `blocking_cause_owners[]`, source artifact refs와 acceptance/re-audit condition을 포함한다. unresolved P decision과 mock consumer product-decision은 T1 contract owner에게, Classification/DVF/QG/locale 및 Menu authority relation correction은 해당 upstream/cross-owner에게 귀속한다. consumer observation evidence만 없는 shared-authority `unverified`는 blocker 목록이 아니라 T3 재검증 목록에 둔다. blocked 상태에서는 production T2 handoff input/manifest를 만들지 않고 cause-attributed progression record만 생성해 T2가 semantic workaround를 구현하지 못하게 한다.

### Claim boundary on successful T1 execution

조건을 충족하면 다음만 주장할 수 있다.

- Tooltip 0~4 slot projection contract가 확정되었다.
- current support universe와 Layer 2/3/4 input authority가 연결되었다.
- Layer 4 eligibility와 bounded projection이 분리되었다.
- selection이 deterministic structural rule을 사용한다.
- Layer 4 locale/Menu readiness 결손은 selected identity를 바꾸거나 차순위 candidate substitution을 유발하지 않는다.
- KO/EN identity-first/no-fallback contract가 확정되었다.
- legitimate absence와 upstream defect를 구분할 수 있다.
- independent Menu consumer evidence가 있는 layer/row의 Menu/Tooltip identity parity를 검증했고, evidence가 없는 shared-authority 범위는 명시적으로 unverified/T3 재검증 대상으로 귀속했다. authority relation 부재/모순만 T2 blocker로 귀속했다.
- whole-universe readiness와 correction attribution이 완료되었다.
- T2용 structured input boundary와 progression gate가 확정되었다.

T2 blocker가 0일 때만 current supported FullType 전체가 T2 full-data generation input으로 준비되었다고 주장할 수 있다.

### Explicitly not claimed

- static Tooltip Lua generation 완료
- `IrisAltTooltip` behavior 변경/완료
- actual Alt/runtime/PZ acceptance
- actual visual 4-line fit
- 모든 KO/EN 번역 품질 승인
- 모든 upstream correction 완료
- current runtime/package install 완료
- external-mod compatibility
- DVF freeze/RTC/Publish/package/Workshop/release/deployment readiness

T1의 최종 경계는 다음으로 유지한다.

```text
Classification / DVF / QG semantic authority
→ T1 projection and readiness contract
→ T2 mechanical static generation
→ later runtime adoption/acceptance scope
```

T2가 이 경계를 넘어 새로운 semantic 판단을 요구하면 T1 contract 또는 upstream input이 아직 닫히지 않은 것으로 처리한다.
