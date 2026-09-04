# Iris DVF Layer 3 복수 의미·정보 해상도 Successor Contract

> 문제 ID: `DVF-L3-01`
>
> 상태: current semantic authority / contract-only adoption
>
> 채택일: 2026-09-03
>
> 상위 권위: `docs/Philosophy.md`
>
> machine contract: `Iris/_docs/authority/dvf/layer3_successor/contract.json`

## 1. 채택 범위

이 계약은 Iris Layer 3가 아이템의 의미를 표현하는 방식과 Menu·Tooltip이 그 의미를 서로 다른 해상도로 소비하는 경계를 정의한다. exact case-sensitive FullType 하나는 대표 용도나 대표 역할 없이 `0..N`개의 독립적인 Layer 3 semantic fact를 가질 수 있다.

이번 채택은 의미 계약과 current semantic authority readpoint에 한정된다. 기존 2,105개 facts·decisions, KO/EN 본문, current generation, Lua runtime과 package는 predecessor-compatible product로 그대로 남는다. 이 문서는 실제 corpus migration, profile taxonomy, Tooltip first-contact axis, 자연어 조합기 또는 runtime 적용의 완료를 주장하지 않는다.

## 2. 식별자와 semantic node

- item identity는 exact case-sensitive FullType이다.
- 한 item의 semantic fact 수는 `0..N`이다. `0`은 곧 조사 완료나 용도 없음이라는 뜻이 아니다.
- 각 fact는 bundle 안에서 유일한 stable `fact_id`, 정확히 하나의 `fact_kind`, kind-specific payload와 하나 이상의 provenance reference를 가진다.
- 직렬화 순서는 재현성만 제공한다. 첫 fact나 첫 context는 대표성·중요도·빈도·효율·Tooltip 우선순위를 뜻하지 않는다.
- presentation order가 필요하면 canonical fact order를 재해석하지 않고 별도 projection이 fact reference로 표현한다.

초기 fact kind는 다음과 같다.

| fact kind | 의미 |
|---|---|
| `use_context` | 요리·건축·수리처럼 사용자가 first-contact에서 이해할 수 있는 전체 활동 맥락 |
| `context_role` | 한 `use_context` 안에서의 도구·재료·용기 등 context-local 역할 |
| `direct_function` | item이 직접 수행하는 확인된 기능 |
| `effect` | item 사용으로 발생하는 확인된 효과 |
| `state` | 의미 있는 item 상태 또는 상태 변화 특성 |
| `condition` | 다른 fact가 참이거나 적용되는 조건 |
| `constraint` | 다른 fact의 범위나 사용을 제한하는 제약 |
| `acquisition` | 확인된 획득 장소·방식·조건 |
| `acquisition_unobtainable` | admissible negative evidence로 확인된 획득 불가 |

`context_role`은 정확히 하나의 `use_context` fact를 참조해야 한다. item-global role은 successor 의미가 아니다. `condition`과 `constraint`는 적용 대상 fact reference를 하나 이상 가져야 하며 qualifier끼리 연결하지 않는다. 같은 조건을 nested qualifier와 top-level node로 이중 표현하지 않는다.

`acquisition_unobtainable`은 의미와 증거 요구만 정의한다. 현재 v1 producer는 `none`, assignment는 `0`이며 별도 negative-evidence authority 없이 이 fact를 만들지 않는다.

## 3. 다섯 독립 축

Layer 3 successor는 다음 축을 분리한다.

1. **Semantic fact** — 무엇이 확인된 사실인가.
2. **Provenance** — 어떤 source와 evidence에서 그 사실이 왔고 어떻게 변환됐는가.
3. **Investigation / coverage** — 어떤 축이 적용 가능하며 어디까지 조사됐는가.
4. **Approved expression** — 확인된 fact를 어느 locale에서 어떤 문장으로 표현할 수 있는가.
5. **Surface projection** — accepted fact 가운데 Menu와 Tooltip이 어떤 reference와 dependency를 표시하는가.

한 축의 상태는 다른 축을 자동 생성하지 않는다. fact가 있다는 사실은 조사 완료·표현 존재·Tooltip 표시를 뜻하지 않는다. 문장이 없다고 fact가 사라지지 않으며, 표시됐다고 새로운 fact가 생기지 않는다.

## 4. 금지되는 대표 의미와 output leakage

`primary_use`, `secondary_use`, `headline_fact`, `primary_fact`, `representative_fact`, `selected_role`, `primary_role`, `selected_profile`, `primary_profile`, `single_core_fact`는 successor semantic node나 projection의 대표 선택 필드로 사용할 수 없다.

Layer 2 projection, Layer 3 rendered body, Layer 4 rendered row·relation count·display string, Tooltip projection과 Menu projection에서 successor Layer 3 fact를 생성하지 않는다. Layer 3와 Layer 4가 같은 upstream source를 조사할 수는 있지만 각자 별도 fact/relation identity와 provenance를 가져야 한다.

## 5. Layer 3 / Layer 4 정보 해상도

Layer 3는 전체 활동 맥락, 그 맥락 안의 역할, broad direct function/effect, fact-local 상태·조건·제약과 acquisition result를 소유한다.

Layer 4는 exact Recipe, Right-click action, EvolvedRecipe relation identity와 relation-local target, result, requirement를 소유한다.

예를 들어 `요리 재료로 사용할 수 있다`는 Layer 3의 broad cooking context와 role이 될 수 있다. 어떤 Recipe나 EvolvedRecipe에서 어떤 음식에 들어가고 어떤 조건·결과가 있는지는 Layer 4다. 두 계층은 독립적이고 동등한 의미 권위를 유지하며 한 계층의 output을 다른 계층의 semantic input으로 사용하지 않는다.

## 6. context / role vocabulary

Vocabulary는 닫힌 전수 enum이 아니라 versioned open registry다. 이 계약의 `cooking`, `construction`, `repair`, `ingredient`, `tool`은 boundary 검증용 비전수 seed example일 뿐 전체 token 목록이 아니다.

새 token은 token, axis, 정의, positive/negative example, evidence reference와 기존 Layer 3/4 boundary를 바꾸지 않는다는 판정을 함께 가져야 한다. source-family 이름이어서는 안 되고, `여러 작업`처럼 지나치게 넓거나 exact relation 하나를 재현할 만큼 좁아서도 안 된다.

기존 정의와 boundary를 바꾸지 않는 token 추가는 후속 investigation/corpus candidate에서 수행할 수 있으며 이 계약 전체의 재채택을 요구하지 않는다. 기존 token의 정의 변경·merge·split 또는 계층 boundary 변경은 contract revision과 current semantic readpoint 갱신이 필요하다.

## 7. acquisition completeness

Acquisition은 모든 current Layer 3 대상 FullType에서 반드시 조사해야 하는 축이다. 의미 결과와 조사 상태는 분리한다.

- `resolved`: positive `acquisition` fact가 하나 이상 있거나 admissible negative evidence에 결속된 `acquisition_unobtainable` fact가 하나 있어 acquisition 축이 완료됐다.
- `investigated_unresolved`: 허용 source를 조사했지만 결과를 확정하지 못했다.
- `not_investigated`: 아직 조사하지 않았다. explicit disposition이 없는 predecessor row의 초기 상태다.

`resolved`는 acquisition 축의 완료만 뜻하며 item 전체 Layer 3 investigation 완료를 단독으로 보장하지 않는다. 다른 필수 조사 축과 item-level 완료 조건은 `DVF-L3-02`가 정한다. `investigated_unresolved`와 `not_investigated`는 acquisition fact를 만들지 않으며 item의 Layer 3 investigation-complete 상태가 아니다. resolved acquisition result는 Menu Layer 3의 필수 정보다. Tooltip S2에 acquisition을 반드시 넣는다는 뜻은 아니다. Acquisition이 unresolved여도 이미 확인된 다른 facts는 보존하고, generic prose나 획득 불가 assertion으로 결손을 덮지 않는다.

## 8. profile 책임

Profile은 investigation scope, composition scope와 profile별 first-contact axis의 범위를 제공할 수 있다. 다만 importance·frequency·ordinal·profile label을 이용해 대표 fact·role을 선택하거나 semantic priority를 부여하지 않는다.

Profile taxonomy와 profile별 조사 축·first-contact axis는 `DVF-L3-02`가 정한다. 실제 S2 fact 결합·표현·문장/줄 구성과 omission tracking은 `DVF-L3-05`가 정한다. 이 계약은 어떤 `use_context`, `direct_function`, `effect`가 모든 item의 S2에 필수인지, 몇 문장으로 표현할지 또는 구체적으로 무엇을 생략할지 미리 고정하지 않는다.

## 9. Menu / Tooltip same-authority, different-depth

Menu Layer 3와 Tooltip S2는 동일한 accepted Layer 3 fact set을 canonical authority로 사용한다.

- Menu Layer 3는 accepted facts를 expanded detail로 보존하고 resolved acquisition을 반드시 포함한다.
- Tooltip S2는 profile별 first-contact axis에 따라 만들어지는 lower-resolution projection이다.
- Tooltip projection은 여러 facts를 더 넓은 한 문장으로 aggregate할 수 있지만 represented fact references를 추적해야 한다.
- 중요도·빈도·효율·첫 ordinal 또는 profile label로 하나를 대표 fact로 선택하지 않는다.
- Tooltip에서 직접 표현하지 않은 detail은 Menu에 남고 omission reference로 추적한다.
- condition/constraint를 빼면 문장의 truth나 범위가 달라질 때 해당 dependency를 projection에 포함한다.
- 유효한 한 logical row 표현을 만들 수 없으면 fact를 버리지 않고 후속 expression 문제로 남긴다.
- runtime은 summary, truncation, semantic reselection, translation 또는 inference를 수행하지 않는다.

구체 first-contact axis는 `DVF-L3-02`, 실제 fact 결합·KO/EN 압축·표현 실패는 `DVF-L3-05`의 책임이다. 기존 Tooltip의 `0..4` logical-row 구조와 S1 Layer 2, S2 Layer 3, S3·S4 Layer 4 ownership은 바뀌지 않는다.

## 10. predecessor transition

Predecessor concept의 exact disposition과 baseline hash는 `predecessor_inventory.json`이 소유한다. 핵심 전환은 다음과 같다.

- exact FullType과 per-fact source/evidence/provenance는 유지한다.
- `identity_hint`는 predecessor identity/expression material로 보존하며 Layer 3 use fact로 자동 승격하지 않는다.
- `primary_use`는 source 재확인 뒤 `0..N` typed facts로 대체한다. predecessor prose를 자동 승격하지 않는다.
- `secondary_use`라는 의미적 구분은 제거하고 primary/secondary 없는 multiplicity로 바꾼다.
- `special_context`는 predecessor detail/evidence material로 보존하고 `DVF-L3-03`에서 source 재확인 후 fact-local로 분해한다. 특별 priority를 주지 않는다.
- item-global selected role은 context-local roles로 대체한다.
- selected compose profile은 semantic identity가 아니라 investigation/composition/first-contact axis scope로 재해석하며 대표 fact나 semantic priority 권한을 갖지 않는다.
- single core/body와 S2 single-core consumption은 canonical fact set과 별도 projection으로 대체한다.
- acquisition optional-only와 readiness/body disposition은 각각 mandatory investigation과 독립 축으로 대체·재해석한다.
- S1/S3/S4 ownership과 `0..4` logical-row structure는 유지한다. 구체 S2 선택·결합·문장 구성은 후속 문제에 남긴다.
- current corpus/runtime generation은 별도 migration까지 predecessor-compatible product로 유지한다.

## 11. 채택과 완료 한계

Owner approval은 2026-09-03 실행 프롬프트의 사전 승인으로 충족했다. Current semantic route는 contract bundle manifest를 가리키며 기존 product pointer와 Tooltip locator를 변경하지 않는다.

이 계약 채택으로 완료되는 것은 복수 use context, context-local role, typed facts, acquisition mandatory investigation, Layer 3/4 information-resolution boundary와 Tooltip first-contact/Menu expanded-detail의 상위 의미 계약뿐이다.

다음은 미완료이며 후속 문제 2~6의 범위다.

- 2,105개 item의 semantic/acquisition 전수 조사
- predecessor prose의 typed-fact migration
- profile taxonomy와 first-contact axis
- 전체 context/role vocabulary와 item mapping
- KO/EN successor body 및 Tooltip/Menu composition
- generation/runtime/package/in-game migration
- compatibility, release, Workshop와 deployment readiness
