# Implementation Plan

Iris DVF Layer 3 복수 의미·정보 해상도 Successor Contract

> 문제 ID: `DVF-L3-01`
>
> 계획 기준일: 2026-09-03
>
> 계획 기준선: repository HEAD `ef0ecc60896d729013852ef415b0e46ec89d6f81`
>
> 계획 상태: execution complete / G1 PASS (2026-09-03)
>
> 실행 무게: `heavy` — current Layer 3 semantic authority readpoint를 변경한다. `heavy`는 disclosure·evidence·closeout 의무이며 별도 전체 테스트나 다단 Gate를 자동 요구하지 않는다.
>
> 기본 완료 경계: successor semantic contract와 current authority readpoint의 채택. 실제 corpus·문장·runtime은 변경하지 않는다.

---

## 1. Objective

현재 `primary_use` 하나, item-global `selected_role` 하나, `compose_profile` 하나와 single-core 설명을 중심으로 구성된 Iris Layer 3 의미 계약을 다음 successor contract로 대체하고 current semantic authority에 채택한다.

- exact case-sensitive FullType 하나가 `0..N`개의 독립 Layer 3 semantic fact를 가질 수 있다.
- 복수 use context와 context-local role을 대표 용도나 대표 역할 없이 보존한다.
- semantic fact, provenance, investigation/coverage, approved expression과 surface projection을 서로 다른 축으로 정의한다.
- Layer 3의 전체 활동 맥락과 Layer 4의 exact Recipe / Right-click / EvolvedRecipe relation을 정보 해상도로 구분한다.
- acquisition을 모든 current Layer 3 대상 FullType에서 조사해야 하는 필수 축으로 정의한다.
- 근거가 확인된 acquisition은 Menu Layer 3에서 필수로 표현하고, 미조사·미해결 상태는 추측해 채우지 않으며 Layer 3 조사 완료로 판정하지 않는다.
- Tooltip S2와 Menu Layer 3가 같은 canonical fact authority를 서로 다른 깊이로 소비하도록 정의한다.
- Tooltip S2는 대표 용도나 importance ranking을 사용하지 않지만, 모든 세부 fact를 한 줄에 직접 열거하도록 강제하지도 않는다.
- profile별 first-contact axis, 실제 fact corpus, 구체 KO/EN 압축 문법과 출력은 후속 문제의 책임으로 남긴다.
- predecessor의 `identity_hint`, `primary_use`, `secondary_use`, `special_context`, selected role/profile, acquisition, core/readiness와 S2 계약에 명시적인 transition disposition을 부여한다.

이번 계획의 `complete`는 successor semantic contract와 그 current authority readpoint가 채택됐다는 뜻이다. 다음 완료를 뜻하지 않는다.

- 2,105개 item의 semantic/acquisition 전수 조사
- predecessor prose의 typed-fact migration
- profile taxonomy와 first-contact axis 확정
- KO/EN Menu·Tooltip 문장 생성
- generation, runtime, package 또는 실제 PZ 적용

---

## 2. Scope

### In Scope

- current Layer 3 source, decision, rendered generation과 Tooltip owner input의 exact baseline census
- predecessor field와 named set의 current → successor transition disposition
- representative field가 없는 `0..N` multi-fact semantic contract
- context-local role과 fact-local condition/constraint binding
- fact / provenance / investigation / expression / presentation axis 분리
- Layer 3 / Layer 4 information-resolution boundary와 최소 casebook
- context/role vocabulary의 정의·admission·extension 규칙
- acquisition mandatory-investigation, item-completeness와 Menu publication 계약
- Tooltip S2 first-contact / Menu expanded-detail 관계의 상위 계약
- human-readable contract와 최소 machine-readable contract bundle
- current semantic authority manifest/index의 additive successor 등록
- contract 범위에 직접 대응하는 단일 focused validation Gate
- `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md` 정렬과 closeout

### Explicitly Out Of Scope

- `dvf_3_3_facts.jsonl` 2,105개 row의 successor schema 변환
- `primary_use` 2,097건과 `special_context` 44건의 fact 분해·source 재조사
- no-primary 8건, review-hold 273건, Tooltip owner absence 175건의 실제 의미 재판정
- acquisition 1,105개 hint의 사실성 감사 또는 누락 1,000개 보강
- 실제 `acquisition_unobtainable` assertion이나 negative-evidence producer 구현
- profile taxonomy, profile별 조사 축과 first-contact axis의 최종 목록
- context/role token의 전수 목록과 2,105개 item mapping
- KO/EN body authoring, 자연어 압축과 pixel/wrapping 적합성 구현
- Tooltip T1/T2 data, S2 renderer, Menu ViewModel, Lua payload 변경
- current generation, `IrisLayer3DataCurrent.lua`, package 또는 installed mod 변경
- Layer 2 taxonomy와 Layer 4 owner/presentation/search/navigation 변경
- release, Workshop, RTC, deployment 또는 외부 모드 compatibility 판정
- unrelated refactor와 새 범용 governance·validation framework 도입

---

## 3. Non-Goals

- `primary_use`를 `headline_fact`, 첫 fact, 첫 context 또는 다른 이름의 대표 필드로 바꾸지 않는다.
- deterministic serialization order를 중요도·대표성·유용성 또는 Tooltip priority로 해석하지 않는다.
- Recipe·Right-click·EvolvedRecipe 같은 source-family 이름을 Layer 3 context vocabulary로 사용하지 않는다.
- Layer 4 rendered row, relation count, density 또는 표시 문자열에서 Layer 3 fact를 생성하지 않는다.
- Layer 3 context에서 exact Layer 4 relation을 역추론하지 않는다.
- body나 표현의 부재를 fact 부재·조사 완료·획득 불가로 자동 변환하지 않는다.
- acquisition mandatory investigation을 모든 item의 mandatory Tooltip prose로 해석하지 않는다.
- profile이 importance·frequency·ordinal·profile label로 대표 fact·role을 선택하거나 semantic priority를 부여하게 하지 않는다. Profile별 first-contact axis는 문제 2가, 실제 S2 fact 결합·표현·문장/줄 구성과 omission tracking은 문제 5가 결정한다.
- 문제 1에서 모든 `use_context`, `context_role`, `direct_function`, `effect`를 S2 required로 고정하지 않는다.
- 문제 1에서 실제 context/role vocabulary 전체를 봉인하지 않는다.
- Menu와 Tooltip이 서로 다른 Layer 3 fact authority를 갖게 하지 않는다.
- 이번 contract adoption을 corpus·product·runtime migration 완료로 확대하지 않는다.

---

## 4. Assumptions

### 4.1 Current Baseline

실행 시작 시 HEAD, dirty state와 아래 수치를 다시 읽는다. 계획의 숫자를 writer 상수로 사용하지 않으며 의미나 owner boundary가 바뀌었으면 실행 전에 계획을 수정한다.

| 관찰 대상 | 계획 작성 시 관찰 | 의미 |
|---|---:|---|
| `dvf_3_3_facts.jsonl` | 2,105 rows | current Layer 3 source universe |
| non-empty `primary_use` | 2,097 | predecessor prose; successor fact 자동 승격 금지 |
| non-empty `secondary_use` | 0 | 실질적 multi-use를 제공하지 않음 |
| non-empty `identity_hint` | 2,105 | predecessor identity/expression material; use fact가 아님 |
| non-empty `special_context` | 44 | predecessor detail prose; source 재확인 전 typed fact가 아님 |
| non-empty `acquisition_hint` | 1,105 | field presence일 뿐 resolved acquisition이 아님 |
| `dvf_3_3_decisions.jsonl` | 2,105 rows | current decision universe |
| decision state | adopted 2,099 / unadopted 6 | presentation state와 fact/coverage state를 구분 |
| selected role/profile | tool 1,144 / material 240 / output 721 | current item-global selection |
| Tooltip Layer 3 owner facts | 2,048 | current S2 single-core input set |
| Tooltip Layer 3 empty-core | 57 | 2,105 universe와 owner fact set의 차집합 |
| Tooltip T1 support universe | 2,280 | Layer 3 universe와 다른 denominator |
| Tooltip owner absence | 175 | support-minus-Layer-3의 별도 set |

같은 count는 같은 집합을 뜻하지 않는다. 필요한 denominator는 이름·정의·source와 exact-set digest를 따로 가진다.

### 4.2 Authority and Architecture

- `Philosophy.md`의 근거 기반·비추천·근거 부족 시 침묵·Menu/Tooltip same facts/different depth·runtime 100% Lua 원칙이 최상위다.
- Layer 1~5는 의미 권위의 서열이 아니며 한 Layer output이 다른 Layer fact를 자동 생성하지 않는다.
- Layer 3와 Layer 4는 같은 upstream source를 각자 조사할 수 있지만 서로의 owner/rendered output을 semantic input으로 사용하지 않는다.
- exact case-sensitive FullType이 source, fact, projection과 runtime identity를 연결한다.
- current corpus와 runtime은 contract adoption 후에도 predecessor-compatible product로 남는다.
- old field는 migration과 historical reproduction을 위해 물리적으로 남길 수 있지만 successor semantic authority가 아니다.

### 4.3 Semantic Node Contract

successor는 대표 필드 없는 top-level semantic node/relation 모델을 사용한다.

```text
Exact FullType
└─ 0..N Layer 3 semantic nodes
   ├─ stable fact_id
   ├─ exactly one fact_kind
   ├─ kind-specific payload
   ├─ 필요한 context/target fact reference
   └─ one or more provenance_refs
```

초기 fact kind는 다음 의미 범위를 제공한다.

```text
use_context
context_role
direct_function
effect
state
condition
constraint
acquisition
acquisition_unobtainable
```

- `context_role`은 item-global이 아니라 정확히 하나의 `use_context`에 귀속한다.
- `condition`과 `constraint`는 적용 대상 fact를 명시한다.
- 같은 의미를 nested qualifier와 top-level node로 이중 표현하지 않는다.
- presentation order가 필요하면 semantic serialization order가 아니라 별도 projection이 fact refs로 표현한다.

### 4.4 Vocabulary Extensibility

문제 1은 context/role vocabulary의 구조와 admission 규칙만 채택한다. `cooking`, `construction`, `repair`, `ingredient`, `tool` 등은 boundary를 검증하는 비전수 seed example이다.

새 token 처리는 다음처럼 구분한다.

| 변경 | 처리 |
|---|---|
| 기존 definition과 Layer 3/4 boundary를 바꾸지 않는 새 token 추가 | 후속 investigation/corpus candidate에서 definition·positive/negative example·source를 검증해 확장 가능. 문제 1 contract 전체 재채택은 요구하지 않음 |
| 기존 token definition 변경, merge, split 또는 boundary 변경 | successor contract revision과 current semantic readpoint 갱신 필요 |

token은 exact relation 하나의 이름이 아니어야 하고, first-contact에서 이해할 수 있는 활동·역할 단위이며, 너무 넓은 `여러 작업`이나 exact relation을 재현할 정도로 좁은 단위가 아니어야 한다.

### 4.5 Tooltip and Menu Resolution

- canonical Layer 3 fact set은 확인된 facts를 전부 보존한다.
- Menu Layer 3는 accepted Layer 3 facts를 expanded detail로 보존한다.
- Tooltip S2는 profile별 first-contact axis와 fact dependency를 사용한 lower-resolution projection이다.
- 어떤 profile과 axis가 first-contact에 필요한지는 DVF-L3-02에서 확정한다.
- 실제 fact 결합·압축·KO/EN 표현과 표현 실패 상태는 DVF-L3-05에서 확정한다.
- Tooltip projection은 importance·frequency·efficiency·첫 ordinal을 기준으로 representative fact를 선택하지 않는다.
- 여러 facts를 하나의 더 넓은 문장으로 표현할 때 어떤 source fact refs를 대표하는지 추적해야 한다.
- Tooltip에서 직접 표현하지 않는 detail은 명시적으로 Menu Layer 3에 남아야 한다.
- condition/constraint를 빼면 문장이 거짓이 되거나 범위가 달라지는 경우 해당 dependency를 projection에 보존한다.
- 한 logical row에서 유효한 lower-resolution 표현을 만들 수 없으면 fact를 임의로 버리지 않고 후속 expression 문제로 남긴다.
- runtime은 summary, truncation, semantic reselection 또는 inference를 수행하지 않는다.

### 4.6 Acquisition Completeness

acquisition은 semantic result와 investigation state를 분리한다.

```text
semantic result:
- acquisition
- acquisition_unobtainable

investigation state:
- resolved
- investigated_unresolved
- not_investigated
```

- `resolved`는 positive acquisition fact가 하나 이상 있거나 admissible negative evidence에 결속된 `acquisition_unobtainable` 하나가 있을 때만 허용하며 acquisition 축 완료만 뜻한다.
- `resolved` acquisition만으로 item 전체 Layer 3 investigation complete를 판정하지 않는다. 다른 필수 조사 축과 item-level 완료 조건은 DVF-L3-02가 정한다.
- `investigated_unresolved`와 `not_investigated`는 acquisition fact를 발명하지 않는다.
- explicit disposition이 없는 current row의 effective initial state는 `not_investigated`다.
- `not_investigated`와 `investigated_unresolved`는 item의 Layer 3 investigation-complete 상태가 아니다.
- resolved acquisition fact는 Menu Layer 3 required information이다.
- acquisition이 unresolved라는 이유로 확인된 다른 facts를 폐기하거나 거짓 prose를 만들지 않는다.
- `acquisition_unobtainable`의 의미는 정의하지만 v1 current producer와 assignment는 `none / 0`으로 둔다. 별도 negative-evidence authority 전에는 assertion하지 않는다.

### 4.7 Predecessor Dispositions

| Current concept | Disposition | Successor treatment |
|---|---|---|
| exact FullType | retain | canonical item identity |
| source/evidence/provenance | retain | per-fact provenance refs |
| `identity_hint` | reinterpret/defer | predecessor identity/expression material로 보존. Layer 3 use fact로 자동 승격하지 않으며 장기 Layer 1/3 placement는 별도 identity-boundary 작업에 맡김 |
| `primary_use` | replace | source 재확인 후 `0..N` typed facts; 자동 승격 금지 |
| `secondary_use` | remove as semantic distinction | primary/secondary 없는 multiplicity. historical field는 보존 가능 |
| `special_context` | defer | predecessor detail/evidence material로 보존하고 DVF-L3-03에서 source 재확인 후 fact-local 분해. 특별 priority를 부여하지 않음 |
| selected item-global role | replace | context-local `0..N` roles |
| selected `compose_profile` as semantic identity | reinterpret | investigation/composition/first-contact axis scope. 대표 fact나 semantic priority 권한은 없음 |
| single core fact/body | replace | canonical fact set + separate projections |
| acquisition optional support only | replace | mandatory investigation axis + Menu-required resolved result |
| readiness/body disposition | reinterpret | fact/coverage/expression/presentation 축으로 분리 |
| S2 single-core consumption | replace | offline first-contact projection |
| S1/S3/S4 and `0..4` rows | retain | unchanged Tooltip ownership/structure |
| current corpus/runtime generation | defer | separate migration 전 predecessor-compatible product |

---

## 5. Repository Areas Affected

### Code

- `Iris/build/description/v2/tests/test_layer3_successor_contract.py` — 하나의 focused validation entry point

다음 runtime/production 코드는 조사만 하고 변경하지 않는다.

- `Iris/tooling/src/iris_tooling/build/compose_layer3_body_profile.py`
- `Iris/tooling/src/iris_tooling/build/compose_layer3_item.py`
- `Iris/tooling/src/iris_tooling/build/compose_layer3_render.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/**`
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`
- `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailModelAssembler.lua`

### Docs

- `docs/iris_dvf_layer3_multi_meaning_information_resolution_successor_contract.md`
- `docs/iris_dvf_layer3_multi_meaning_information_resolution_successor_contract_closeout.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- 본 계획

### Config

필수 machine-readable artifact를 다음 최소 집합으로 제한한다.

- `Iris/_docs/authority/dvf/layer3_successor/contract.json`
- `Iris/_docs/authority/dvf/layer3_successor/casebook.json`
- `Iris/_docs/authority/dvf/layer3_successor/predecessor_inventory.json`
- `Iris/_docs/authority/dvf/layer3_successor/contract_manifest.json`
- 기존 `Iris/_docs/authority/iris_current_authority_manifest.json`
- 기존 `Iris/_docs/authority/iris_current_route_index.json`
- `Iris/validation/execution/required_validations.json`의 focused test identity 한 건
- 기존 pytest discovery가 새 focused test를 fail-closed로 분류하도록 `Iris/_docs/round3/round3_pytest_source_classification.json`의 planned current source 한 건과 exact source-set binding
- 사용자 요청에 따른 Git 반영 시 같은 source-set binding을 tracked 상태로 갱신한다. `.gitattributes`에는 위 contract bundle 디렉터리와 human contract의 exact bytes를 checkout 시 보존하는 `-text` 규칙만 추가한다. 이는 계약·검증 범위 확대가 아니라 VCS 저장·복원 경계의 보존 조치다.

별도 authorship attestation, review-independence attestation, owner-ratification JSON, adoption record, vocabulary별 파일, omission ledger와 새 receipt taxonomy는 만들지 않는다. 필요한 author, review, adoption과 validation ceiling 정보는 plan·contract·DECISIONS·closeout 및 기존 current route로 충분히 기록한다.

### Generated Artifacts

runtime/generated artifact 변경은 없다. 다음 current product input/output은 byte-identical이어야 한다.

- `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
- `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
- `Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua`
- pointer-selected `IrisLayer3Generations/<generation_id>/**`

---

## 6. Planned Changes

### Change 1 — Freeze Baseline and Transition

**Purpose:** successor가 대체·유지·유예하는 current 의미를 정확히 식별한다.

**Implementation Notes:**

1. 실행 시작 HEAD/tree/dirty state를 기록한다.
2. facts, decisions, current generation과 Tooltip owner input의 exact case-sensitive set/count/hash를 재도출한다.
3. 서로 다른 denominator를 이름과 source로 분리한다.
4. §4.7의 predecessor concept 전부에 정확히 하나의 disposition을 materialize한다.
5. `identity_hint`와 `special_context`가 자동 typed fact나 priority input이 되지 않음을 명시한다.
6. current facts/decisions/generation/runtime은 변경하지 않는다.

**Validation:** 단일 Gate G1에서 baseline set relation, disposition completeness와 protected hash를 확인한다.

### Change 2 — Define the Minimal Successor Semantic Contract

**Purpose:** 대표 필드 없는 `0..N` fact model과 독립 축을 채택한다.

**Implementation Notes:**

1. human contract와 `contract.json`에 semantic node, provenance, investigation, expression, projection의 분리를 정의한다.
2. context-local role과 fact-local condition/constraint binding을 정의한다.
3. forbidden representative aliases와 forbidden implications를 정의한다.
4. vocabulary는 token 목록이 아니라 admission/extension/versioning 규칙을 우선 정의한다.
5. seed token은 casebook 검증용 비전수 예시로 표시한다.

**Validation:** G1에서 대표 alias, axis leakage, invalid binding, duplicate identity와 vocabulary-extension 규칙을 확인한다.

### Change 3 — Define Resolution and Acquisition Boundaries

**Purpose:** Layer 3 전체 맥락과 Layer 4 exact relation, acquisition fact와 investigation 상태를 구분한다.

**Implementation Notes:**

1. Layer 3는 활동 context·context-local role·broad function/effect를 소유한다.
2. Layer 4는 exact Recipe/action/EvolvedRecipe identity, target/result/requirement와 relation-local detail을 소유한다.
3. Layer 4 row/count/display에서 Layer 3 fact를 만들지 않는다.
4. shared upstream source는 각 Layer가 별도 identity/provenance로 독립 소비한다.
5. acquisition의 resolved/unresolved/uninvestigated와 positive/negative semantic result를 분리한다.
6. unresolved acquisition은 item investigation complete가 아니고, resolved는 acquisition 축 완료일 뿐 item 전체 완료의 충분조건이 아니며 resolved acquisition은 Menu Layer 3 required임을 명시한다.

casebook은 다음 최소 유형만 포함한다.

- single context
- materially distinct multi-context
- same-context multi-role
- direct-function/effect와 truth-qualifying condition
- acquisition positive / unresolved / uninvestigated
- Layer 3 broad cooking context와 Layer 4 exact Recipe/EvolvedRecipe 관계
- current `identity_hint`와 `special_context` transition
- representative alias와 Layer output leakage의 negative fixture

**Validation:** G1에서 위 casebook의 결정성, boundary leakage `0`과 acquisition false-completion `0`을 확인한다.

### Change 4 — Define Tooltip/Menu Resolution Without Premature Selection Rules

**Purpose:** same-authority/different-depth를 확정하면서 문제 2와 문제 5의 설계 여지를 보존한다.

**Implementation Notes:**

1. Tooltip S2와 Menu Layer 3가 같은 canonical fact set을 참조하도록 정의한다.
2. Menu Layer 3는 accepted Layer 3 facts와 resolved acquisition을 보존한다.
3. Tooltip S2는 profile first-contact axis로 결정되는 lower-resolution projection이라고만 정의한다.
4. 모든 context/function/effect를 S2 required로 고정하지 않는다.
5. importance, frequency, first ordinal 또는 profile label로 대표 fact를 선택하지 않는다.
6. semantic aggregation은 허용하되 represented fact refs를 추적한다.
7. Tooltip에서 직접 표현하지 않은 detail은 Menu에 남기고 omission을 추적한다.
8. truth를 바꾸는 condition/constraint dependency를 보존한다.
9. 구체 first-contact axis는 문제 2, 실제 composition/status/KO/EN 표현은 문제 5에 넘긴다.
10. S1/S3/S4와 `0..4` logical-row 구조를 유지한다.

**Validation:** G1에서 same-authority, no-primary projection, Menu preservation, dependency preservation과 runtime-inference 금지를 확인한다.

### Change 5 — Adopt the Contract and Close the Bounded Work

**Purpose:** 최소 artifact로 successor contract를 current semantic readpoint에 등록하고 후속 문제의 입력을 고정한다.

**Implementation Notes:**

1. human contract, `contract.json`, `casebook.json`, `predecessor_inventory.json`을 final한다.
2. `contract_manifest.json`은 위 네 member의 path와 digest를 결속한다. review/adoption/timestamp/host metadata를 semantic identity에 넣지 않는다.
3. `DECISIONS.md`에는 scalar/single-core predecessor를 삭제하지 않고 additive supersession을 기록한다.
4. `ARCHITECTURE.md`에는 multi-fact axes, Layer 3/4 boundary와 Tooltip/Menu 관계를 반영한다.
5. `ROADMAP.md`에는 문제 1 완료와 문제 2~6의 미완료 범위를 구분한다.
6. 기존 current authority manifest/index가 successor contract manifest를 한 번만 가리키게 한다. current product pointer와 Tooltip locator는 변경하지 않는다.
7. required validation registry에는 G1의 exact test identity 한 건만 추가하고, 기존 Round 3 pytest discovery policy에는 같은 test source를 planned current로 분류한다. 이는 새 validation authority가 아니라 G1 실행에 필요한 기존 discovery boundary 갱신이다.
8. 전체 final working-tree subject에서 G1을 한 번 실행한다.
9. G1이 PASS한 경우에만 closeout에 current semantic adoption, evidence와 validation ceiling을 기록한다.

**Validation:** 아래 단일 Gate G1만 사용한다.

---

## 7. Validation Plan

### Required Gate — G1 Contract Adoption

필수 Gate는 하나뿐이다. 모든 contract·docs·current route 변경이 끝난 동일 working-tree subject에서 다음 focused command를 한 번 실행한다.

```powershell
uv run --project .\Iris\tooling --no-sync pytest .\Iris\build\description\v2\tests\test_layer3_successor_contract.py -q --round3-contract=diagnostic --round3-additional-source=Iris/build/description/v2/tests/test_layer3_successor_contract.py
```

실행 중 확인된 기존 pytest discovery 전제에 따라 위 명령은 focused source를 `additional-source`로 명시한다. 기본 `current` collection은 이 테스트가 소비하지 않는 repository 전체 current-route external output seed를 configure 시점에 요구하므로 사용하지 않는다. Test source 자체의 policy classification과 required-validation identity는 `current`로 유지하며, `diagnostic`은 외부 seed 없는 단일 source collection boundary일 뿐 semantic claim을 낮추거나 별도 Gate를 만들지 않는다.

test module은 하나의 current-required test identity를 제공하고 내부 helper로 다음만 확인한다.

1. JSON parse/schema와 manifest member digest
2. `0..N` fact model, context-local role와 fact-local qualifier binding
3. fact/provenance/investigation/expression/projection axis 분리
4. forbidden primary/representative alias와 output-to-fact implication 금지
5. 최소 Layer 3/4·acquisition·identity/special-context casebook
6. vocabulary seed가 비전수 example인지와 compatible token extension이 전체 contract 재채택을 요구하지 않는지
7. Tooltip/Menu same-authority, Menu preservation과 no-importance-selection 원칙
8. predecessor disposition completeness
9. top docs·contract manifest·current authority manifest/index가 같은 contract digest를 가리키는지
10. protected current facts/decisions/owner input/generation/runtime hash가 baseline과 같은지

G1 PASS 조건은 exact command exit `0`이다. 실패하면 `complete`나 current semantic adoption을 주장하지 않는다.

### Deliberately Not Added

이번 변경은 static contract와 authority route만 바꾸므로 다음 Gate를 추가하지 않는다.

- 별도 pre-adoption/post-adoption Gate
- 별도 independent-review Gate
- 별도 owner-ratification Gate
- 별도 canonical A/B run
- full repository test suite
- current-required runner 전체 실행
- Lua syntax 검사
- package/install validation
- actual PZ observation
- multiplayer·long-session·compatibility sweep

동일한 내용을 여러 test function, runner와 receipt로 중복 검증하지 않는다. 구현 중 runtime, generator, installed tooling 또는 package를 실제로 변경하게 되면 이 계획을 먼저 수정하고 해당 surface에 필요한 검증만 추가한다.

### Validation Limits

G1은 다음을 검증하지 않는다.

- 2,105개 item의 successor fact 정확성
- primary/special-context/acquisition prose의 migration 정확성
- profile taxonomy와 profile별 first-contact axis
- 실제 context/role token 전체
- KO/EN 문장 품질과 Tooltip 한 줄 적합성
- Menu/Tooltip successor implementation
- runtime/package/in-game behavior
- compatibility·performance·release readiness

---

## 8. Risk Surface Touch

### Authority Surface

**변경함.** `primary_use`·selected role/profile·single-core·acquisition optional-only·S2 single-core semantic interpretation을 additive successor contract로 대체한다.

### Runtime Behavior Surface

**변경 없음.** Lua, current generation pointer, Menu ViewModel, Tooltip static data와 runtime selection을 변경하지 않는다.

### Compatibility Surface

**변경 없음.** public API/SPI, external format와 mod interoperability를 변경하지 않는다. machine contract는 Iris 내부 offline handoff다.

### Sealed Artifact Surface

**변경함.** 새 contract bundle manifest와 existing current semantic route만 변경한다. predecessor decisions와 product artifacts는 read-only로 보존한다.

### Public-Facing Output Surface

**현재 변경 없음.** 향후 public 의미 기준은 바뀌지만 이번 실행은 게임 내 KO/EN body를 변경하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- context token이 exact Layer 4 relation 이름이나 지나치게 넓은 일반명으로 변할 수 있다.
- context-local role을 도입하고도 compatibility alias로 item-global primary role을 유지할 수 있다.
- profile이 importance·frequency·ordinal·profile label로 대표 fact/role을 선택하거나 semantic priority를 부여해 first-contact/composition scope를 사실상 대표 의미로 바꿀 수 있다.
- old product와 new semantic contract가 동시에 migrated current처럼 보일 수 있다.

대응은 boundary casebook, forbidden aliases, explicit transition과 separate semantic/product status로 제한한다.

### Runtime Risk

기본 scope에는 runtime mutation이 없다. current authority manifest/index 변경이 product pointer나 Tooltip locator를 바꾸는 실수만 protected hash와 route assertion으로 차단한다.

### Compatibility Risk

- old field를 즉시 제거하면 historical generation 재현이 깨질 수 있다.
- case-insensitive FullType map은 identity collision을 만들 수 있다.
- successor token을 current runtime enum으로 노출하면 미이행 consumer가 오동작할 수 있다.

old field physical retention, exact-case identity와 no-runtime-change scope를 유지한다.

### Regression Risk

- `primary_use`를 first/headline fact로 재도입
- 모든 facts를 S2 required로 다시 고정
- compatible vocabulary token 추가마다 전체 contract 재채택 요구
- Tooltip omission을 canonical fact absence로 해석
- acquisition 미조사를 complete 또는 unobtainable로 해석
- `identity_hint`를 use fact로, `special_context`를 특별 priority fact로 자동 승격
- different denominator를 같은 집합으로 대체
- static contract adoption을 corpus/runtime completion으로 표현

G1의 최소 positive/negative fixtures와 closeout ceiling으로 차단한다.

---

## 10. Rollback Plan

- G1 실패 시 current semantic adoption을 주장하지 않고 이번 change set의 contract·docs·route 변경을 되돌린다.
- predecessor current authority와 product pointer는 삭제하거나 덮어쓰지 않는다.
- contract contradiction이 adoption 뒤 발견되면 기존 bundle을 조용히 수정하지 않고 bounded successor revision을 발행한다.
- compatible vocabulary token 추가는 contract contradiction이 아니며 후속 corpus candidate에서 확장한다.
- 항상 baseline inventory, predecessor trace, validation result와 ceiling을 보존한다.

---

## 11. Governance Constraints

- `Philosophy.md`가 최상위 authority다.
- Iris는 근거가 있는 사실만 설명하고 추천·효율·우열·빈도·대표성 판단을 추가하지 않는다.
- 근거가 부족하면 fact/prose를 만들지 않고 investigation state로 남긴다.
- Layer 1~5를 통합하거나 새 의미 계층을 만들지 않는다.
- Layer 3와 Layer 4는 shared source를 독립 소비하지만 서로의 output을 semantic input으로 사용하지 않는다.
- Menu와 Tooltip은 같은 canonical Layer 3 facts를 다른 깊이로 표시한다.
- Tooltip은 최대 4 logical rows를 유지하고 S2는 offline-composed다.
- S2 first-contact 세부 축과 압축 문법을 문제 1에서 선점하지 않는다.
- runtime은 semantic selection, translation, summarization 또는 inference를 하지 않는다.
- exact case-sensitive FullType과 source provenance를 보존한다.
- predecessor prose를 source 재확인 없이 successor typed fact로 승격하지 않는다.
- old fields/artifacts는 migration과 historical trace를 위해 보존할 수 있지만 successor claim을 발행하지 않는다.
- predecessor decision은 additive supersession을 사용하고 소급 편집하지 않는다.
- validation은 G1 exact command exit `0`일 때만 PASS다.
- closeout은 `validated / out_of_scope / unvalidated_but_in_scope`와 non-claims를 명시한다.
- 불필요한 runner, registry, receipt, attestation, review Gate 또는 state enum을 추가하지 않는다.

---

## 12. Expected Closeout State

Expected closeout target: `complete`

다음 조건이 모두 충족될 때만 사용한다.

1. 대표 alias 없는 `0..N` multi-fact와 context-local role contract가 current semantic authority로 채택된다.
2. semantic fact, provenance, investigation, expression과 presentation 축이 분리된다.
3. Layer 3/4 resolution과 shared-source/separate-authority 규칙이 최소 casebook에서 결정적으로 판정된다.
4. acquisition이 mandatory investigation axis이며 unresolved는 item investigation complete가 아니고 resolved는 acquisition 축만 완료하며 resolved result는 Menu Layer 3 required임이 채택된다.
5. profile은 investigation/composition/first-contact axis scope를 제공할 수 있으나 대표 fact·role 또는 semantic priority를 정하지 않는다. First-contact axis는 문제 2, 실제 S2 결합·표현·문장/줄 구성과 omission tracking은 문제 5에 남는다.
6. Tooltip S2와 Menu Layer 3의 same-authority/different-depth, no-primary-selection, Menu preservation과 dependency-preservation 계약이 채택된다.
7. 모든 facts를 S2 required로 강제하는 규칙은 채택되지 않는다.
8. vocabulary admission/extension 규칙이 채택되고 비전수 seed token이 closed corpus vocabulary로 오인되지 않는다.
9. `identity_hint`와 `special_context`를 포함한 predecessor concept의 transition disposition이 존재한다.
10. S1/S3/S4와 `0..4` logical-row ownership이 유지된다.
11. current product facts/decisions/owner input/generation/runtime hash가 바뀌지 않는다.
12. human contract, machine contract, manifest, top docs와 current semantic route가 같은 contract digest를 가리킨다.
13. 단일 Gate G1이 exact final subject에서 exit `0`이다.
14. closeout이 validation ceiling과 후속 문제 2~6의 미완료 범위를 기록한다.

허용되는 최종 claim은 다음과 같다.

> Iris Layer 3의 adopted successor semantic contract가 복수 use context, context-local role, typed facts, acquisition mandatory investigation, Layer 3/4 information-resolution boundary와 Tooltip first-contact/Menu expanded-detail 관계를 정의한다.

다음 claim은 하지 않는다.

- 2,105개 item successor 조사 완료
- 2,097개 primary-use migration 완료
- acquisition coverage 완료
- profile/first-contact axis 완료
- KO/EN corpus 또는 Tooltip/Menu implementation 완료
- generation/runtime/package/in-game adoption 완료
- compatibility·release·Workshop·deployment readiness 완료
