# Implementation Plan

Iris Item Page Information Sufficiency

> 2026-08-20 IAR retirement Walkthrough synchronization: product outcome은 `FULL_RETIREMENT`, Layer 1–5 active product IAR consumer와 residual allowlist는 모두 `0`이다. 동기화 readpoint는 main `c91d8f79`, terminal implementation subject `6f362b5e`, full-gate subject `c924349e`, current generation `dvf33-2a44a0a8d9a2e7f0d9a533ad002b7f691c1bfccec9577fb3356967ec6fd8a00c`다. 실행 시에는 이 값을 영구 상수로 사용하지 않고 `IrisLayer3DataCurrent.lua` pointer와 selected generation descriptor를 다시 읽어 drift를 봉인한다.
>
> Layer 3 current identity는 7개 canonical input, content-derived `generation_id`, immutable `IrisLayer3Generations/<generation_id>`와 single pointer로 증명한다. IAR attempt/nonce/receipt/adoption/current descriptor는 제품 입력이 아니다. `iar_` 이름이 남은 도구와 `iris_current_authority_manifest.json`은 closeout에서 허용된 validation/governance/history 역할로만 읽는다. 이 동기화는 assessment 의미나 UI scope를 바꾸지 않으며 RTC PASS, Publish PASS, release readiness 또는 owner-sealed canonical closure를 주장하지 않는다.

## 1. Objective

Iris의 current vanilla item page 전체를 독립적인 assessment unit으로 삼아, Layer 3 본문의 존재·분량과 Layer 4 output의 존재 여부만으로 충분성을 추정하지 않고 다음을 결정론적으로 판정하는 오프라인 assessment를 구현한다.

- Layer 3의 information contribution과 requiredness
- Layer 4의 applicability와 representation 상태
- explicit baseline field registry에서 파생되지 않는 confirmed fact가 page에 표현되었는지 여부
- known missing, approved artifact-set absence, unresolved 상태
- Public Text Quality와 분리된 item-page information sufficiency disposition

이 assessment는 DVF System이나 QG를 대체하는 새로운 facts authority가 아니다. current facts, rendered Layer 3와 Layer 4 artifact를 read-only로 관찰해 Publish Boundary가 소비할 component evidence를 생성한다. runtime Lua는 assessment를 계산하거나 재판정하지 않는다.

### Feedback Adjudication and Execution Gate

검토에서 제기된 네 Critical과 여섯 Important 항목은 모두 이 계획의 fail-closed 실행 계약으로 채택한다.

후속 피드백 `CLD-IPS-I7`~`CLD-IPS-I10`과 `CLD-IPS-M3`~`CLD-IPS-M7`도 모두 채택한다. 이에 따라 derivation-level reachability, `blocked_by_negative_authority` precedence, baseline lower-bound bias, stable closeout trace, Layer 2 ratification, proposal-state 구분, ledger coverage, successor-entry binding과 ratification ID namespace를 계획 전반에 반영한다.

- requiredness / applicability는 current producer provenance에서 계산하며 per-item ledger를 병렬 semantic authority로 사용하지 않는다.
- `approved_fact_set_empty`와 world-level negative를 분리한다. current closed-negative authority가 없으면 Layer 4 `not_applicable`을 산출하지 않는다.
- baseline은 `items_itemscript.json` 기반 explicit field registry로 봉인한다. `IrisWikiSections.renderCoreInfoSection()`은 구현 cross-check일 뿐 baseline authority가 아니다.
- 모든 item을 독립적인 장문 Layer 3 대상으로 되돌리는 것을 막는 regression guard를 `DECISIONS.md`, `ROADMAP.md` Hold와 terminal closeout condition에 직접 추적한다.
- `verified user-relevant information` 같은 주관 predicate 대신 `baseline에서 파생되지 않는 confirmed fact`를 사용한다.
- decision matrix는 total function으로 만들고 explicit rule과 매칭되지 않는 state vector를 `unresolved`로 보낸다.
- ratification 대상은 한 파일의 단일 authoritative list로 관리한다.
- bare `complete` 대신 axis-qualified closeout vocabulary를 사용한다.
- heading과 actual Layer responsibility의 mapping artifact를 남긴다.
- anchor별 Layer state, reason code, precedence rule과 terminal disposition trace를 남긴다.

policy-dependent Change 2–7은 owner policy ratification 전에는 시작하지 않는다. ratification 전 허용 범위는 pointer-selected generation과 Layer 4 current input identity inventory, denominator census, protected-surface hash baseline, anchor recensus와 명시적인 proposal-state policy materialization뿐이다. unratified policy로 evaluator, full assessment, required-route registration 또는 canonical document successor를 만들지 않는다.

owner가 ratify할 단일 목록은 다음 열 항목이다. `IPS-RAT-*` 접두는 review 문서의 `R#` revision ID와 혼동되지 않는 stable policy identifier다.

| ID | Ratification subject | 계획상 proposal |
|---|---|---|
| `IPS-RAT-01` | canonical disposition vocabulary | `information_sufficient / evidence_limited / known_information_missing / unresolved` |
| `IPS-RAT-02` | exact denominator | execution-time `items_itemscript.json` exact case-sensitive FullType set |
| `IPS-RAT-03` | exact baseline | owner-approved `baseline_field_registry.json`; ItemScript 보존 field에 한정된 실제 vanilla Layer 1의 하한이며 미보존 runtime field는 `information_sufficient` 방향 편향 가능 |
| `IPS-RAT-04` | state derivation | provenance-derived `required / optional / not_required / unresolved`; exception ledger는 `authority_effect=none`, `semantic_production=false` |
| `IPS-RAT-05` | negative / completeness semantics | sealed artifact-set materialization과 producer / world coverage를 분리; current `not_applicable` 비산출; `blocked_by_negative_authority`는 non-dispositive scope limitation |
| `IPS-RAT-06` | assessment authority | Publish Boundary가 소비하는 component evidence |
| `IPS-RAT-07` | execution closure | current vanilla universe 전수 assessment |
| `IPS-RAT-08` | validation depth | heavy; matrix와 provenance-derivation reachability를 모두 검증 |
| `IPS-RAT-09` | closure governance | machine validation, eligible independent review, owner seal과 exact successor-entry binding 분리 |
| `IPS-RAT-10` | Layer 2 contribution boundary | `primary_subcategory`는 identity-restatement diagnostic 전용이며 positive marginal information contribution에서 제외 |

위 표는 계획 검토를 위한 proposal schema preview다. 실행 시 ratification authority는 exact hash로 봉인된 `policy_ratification_contract.json` 한 파일뿐이며 다른 문서의 서술이나 축약 목록은 ratification evidence가 아니다.

`evidence_limited`는 양 producer의 declared artifact set이 `sealed_complete`이고 양쪽 approved fact query가 비었으며 Layer 3 requiredness가 `optional` 또는 artifact-set-scoped `not_required`인 상태다. 이는 world에 추가 fact나 interaction이 없다는 negative claim이 아니며 information-sufficiency PASS도 아니다. 이 상태만으로 item을 숨기거나 publish failure, content expansion, extraction expansion 또는 다른 Publish Boundary component로 자동 승격하지 않는다.

---

## 2. Scope

다음을 구현 범위로 한다.

- current vanilla item-page denominator와 Layer 1~4 observation surface의 exact identity 결속
- single-source owner policy ratification과 pre-ratification execution ceiling
- explicit ItemScript baseline field registry와 runtime consumer cross-check
- Layer 3 contribution / requiredness state contract
- Layer 4 applicability / absence / representation state contract
- provenance-derived state rules와 non-authoritative exception ledger
- page-level disposition과 reason-code decision matrix
- case-sensitive FullType 기반 전수 evaluator, validator와 CLI
- `.223 탄약 거푸집`(`Base.223BulletsMold`), 금속 집게(`Base.Tongs`) 및 representative positive / negative / unresolved fixture
- current-universe assessment, disposition distribution과 information-gap inventory
- Public Text Quality와 page sufficiency의 assessment-axis 분리 계약
- Menu / Tooltip depth와 terminology의 문서 수준 정합성 검토
- current top-level authority 문서의 additive alignment
- canonical regression guard와 claim-bearing successor exact identity binding
- deterministic replay, protected-artifact non-mutation, independent review와 owner seal

### Explicitly Out Of Scope

- Browser, Wiki, Detail, Tooltip의 실제 Lua 구현 변경
- user-facing heading rename 또는 번역문 변경
- Tooltip selection logic, cache, line assembly 또는 최대 4줄 계약 변경
- current facts, DVF decisions, rendered Layer 3, Layer 4 use_case / requirements, runtime chunks 또는 package payload rewrite
- 기존 DVF body의 전수 보강·장문화·재생성
- Layer 4 coverage gap의 자동 remediation
- current artifact-set absence에서 world-level negative 또는 Layer 4 `not_applicable` authority를 새로 만드는 작업
- 새로운 Recipe, Right-click, Static Capability Evidence 추출
- Evidence Allowlist, taxonomy 또는 1~5계층 정보 모델 재설계
- Layer 3 / Layer 4 semantic responsibility 병합
- assessment disposition의 Browser hiding / filtering / sorting / recommendation / badge / trust signal 노출
- `quality_exposed` 활성화
- external mod item universe 또는 current ko 이외 locale의 전수 평가
- package publication, release / Workshop / B42 readiness 판정
- multiplayer, long-session, FPS, heap, latency 또는 frame-time 검증

---

## 3. Non-Goals

- 모든 item page를 `information_sufficient`로 만드는 것이 목표가 아니다.
- `known_information_missing`과 `unresolved`의 수를 줄이기 위해 policy를 완화하지 않는다.
- output 부재에서 상호작용 부재를 추론하지 않는다.
- `approved_fact_set_empty`를 world-level negative로 해석하지 않는다.
- per-item state ledger를 DVF System / QG와 병렬하는 semantic authority로 만들지 않는다.
- 문자열 길이, 문장 수, category 반복 여부만으로 semantic fact, requiredness 또는 applicability를 확정하지 않는다.
- Layer 4가 풍부하다는 이유로 Layer 3 known missing을 상쇄하거나 그 반대의 상쇄를 허용하지 않는다.
- assessment execution PASS를 Public Text Quality PASS, Publish Boundary PASS, retired Registry Authority PASS, Registry Runtime Compatibility PASS 또는 release readiness로 부르지 않는다.
- information-gap inventory를 자동 수정 backlog나 content authoring 승인으로 승격하지 않는다.
- 로드맵의 anchor를 item-specific 예외로 하드코딩하지 않는다.

---

## 4. Assumptions

### Codebase Inspection Summary

- `Iris/input/items_itemscript.json`은 계획 작성 시 exact case-sensitive FullType `2,285`개를 포함한다. `Base.LemonGrass` / `Base.Lemongrass`처럼 case만 다른 identity가 있으므로 Windows PowerShell의 case-insensitive object materialization을 authoritative reader로 사용하지 않는다.
- retirement 이전 `dvf_3_3_input_manifest.json`은 Layer 3 facts/decisions/rendered universe를 결속했지만 current generation input authority가 아니다. 현재 generation descriptor는 facts, decisions, overlay support, compose profile, identity-hint rules, conflict-precedence rules와 approved upstream `candidate_rendered.json`의 7개 raw-byte identity를 열거한다.
- 실행 시 `IrisLayer3DataCurrent.lua`가 선택한 generation의 `generation_descriptor.json`과 `dvf_3_3_rendered.json`을 current Layer 3 readpoint로 사용한다. planning-time `2,084` body/`21` legacy unadopted/`180` absent 수치는 다시 census하며 영구 denominator로 사용하지 않는다.
- `Iris/build/description/v2/data/upstream_usecases_by_fulltype.json`은 `1,606`개 FullType을 포함한다. ItemScript universe의 나머지 `679`개에 output이 없다는 사실은 `not_applicable`의 증거가 아니다.
- `IrisItemDetailViewModel.fromItem()`은 DisplayName, weight, type/category/subcategory, food / weapon / literature / moveable 정적 사실, Layer 3, recipe connections와 use_case를 하나의 read-only view model로 모은다.
- current ItemScript snapshot의 field universe와 runtime consumer surface는 동일하지 않다. `IrisWikiSections.renderCoreInfoSection()`은 weight / type / damage / condition / thirst / hunger를 소비하지만 current `items_itemscript.json`은 그중 일부만 보존한다. 따라서 baseline authority는 owner-ratified ItemScript field registry이며 runtime function은 registry coverage / drift cross-check로만 사용한다.
- 그 결과 baseline registry는 사용자가 실제로 보는 vanilla Layer 1의 검증 가능한 하한이다. ItemScript에 보존되지 않은 runtime 표시 field는 baseline 밖 confirmed fact처럼 보일 수 있으므로 판정 편향은 page를 `information_sufficient`로 더 쉽게 보내는 방향이며, 특히 food / weapon 계열에서 두드러질 수 있다. 이 편향은 `IPS-RAT-03`의 owner-visible limitation이다.
- `IrisBrowserItemIndex.build()`은 runtime `getAllItems()`를 전수 인덱싱하므로 Browser는 static quality-filtered 목록이 아니다. 이 계획의 전수 denominator는 재현 가능한 vanilla offline snapshot이며 runtime 외부 모드 universe 전체를 대표하지 않는다.
- runtime Layer 3는 `layer3_renderer.lua`가 current chunk lookup을 읽고 text가 없으면 침묵한다. runtime은 requiredness나 sufficiency를 판정하지 않는다.
- runtime Layer 4 chunk는 positive `lines`와 `exclusion_lines`를 분리한다. evaluator는 `decision=PASS`에 결속된 positive evidence와 실제 public representation만 contribution으로 계산하고 exclusion을 positive information이나 `not_applicable` 증거로 계산하지 않는다.
- `iar_public_text_assessment.py`는 역사적 이름과 무관하게 retained validation utility로만 취급한다. 새 evaluator는 subject finding/technical failure 분리, runner/read-only validator, canonical JSON hash와 deterministic replay pattern만 재사용하며 stateful lifecycle, public-text metric 또는 PASS를 가져오지 않는다.
- 현재 두 anchor는 로드맵 작성 시점의 결함을 그대로 나타내지 않는다.
  - `Base.223BulletsMold`의 current rendered text는 탄약 주조 용도와 제작 경로를 포함하고, current Layer 4에는 positive Recipe use_case가 있다.
  - `Base.Tongs`의 current rendered text는 금속 단조 용도와 제작 경로를 포함하고, current Layer 4에는 다수의 positive Recipe use_case가 있다.
  - 따라서 두 항목은 known-insufficient 고정 fixture가 아니라 최신 input identity에서 동일 policy path를 통과하는 anchor로 사용한다.

### Repository and Environment Assumptions

- 최상위 authority는 `docs/Philosophy.md`이며 `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` 순서로 current ecosystem state를 해석한다.
- Python 실행과 검증은 Windows PowerShell에서 `uv run python -B ...`를 사용한다.
- JSON / JSONL reader는 UTF-8, case-sensitive exact key, duplicate/collision fail-close와 deterministic ordering을 보장한다.
- primary working tree에는 이미 사용자 변경이 있으므로 assessment 생성과 full validation은 disposable clean checkout 또는 명시적으로 격리된 output root에서 수행한다.
- planning-time count는 관찰값일 뿐 canonical denominator를 하드코딩하지 않는다. 실행 시 input hash와 exact FullType set을 다시 materialize한다.

### Authority Assumptions

- Layer 3 semantic production은 DVF System / DVF Body Compiler가 계속 소유한다.
- Layer 4 interaction-information production은 QG가 계속 소유한다.
- Layer 3 artifact identity는 stateless generation contract/validator와 pointer-selected immutable generation이 증명한다. Page assessment는 이를 read-only로 소비하며 DVF producer, installer 또는 package responsibility를 흡수하지 않는다.
- Page assessment result는 Publish Boundary component evidence이며 자체 bare acceptance authority가 아니다.
- owner ratification 전에 `IPS-RAT-01`~`IPS-RAT-10` 중 어느 항목도 current authority로 채택하지 않고 read-only preflight ceiling을 넘지 않는다.
- Layer 3 / 4 states는 current producer provenance에서 파생한다. exception ledger는 assessment routing 기록이며 `authority_effect=none`, `semantic_production=false`다.
- current authority에는 world-level closed-negative provider가 없다고 가정한다. 그 provider가 별도 owner decision과 exact source identity로 승인되기 전에는 evaluator가 `not_applicable`을 생성하지 않는다.
- machine result, independent review와 owner seal은 서로 대체하지 않는다.

---

## 5. Repository Areas Affected

### Code

- `Iris/build/description/v2/tools/build/item_page_information_sufficiency.py` (new)
- `Iris/build/description/v2/tools/build/run_item_page_information_sufficiency_assessment.py` (new)
- `Iris/build/description/v2/tools/build/validate_item_page_information_sufficiency_assessment.py` (new)
- `Iris/build/description/v2/tests/test_item_page_information_sufficiency.py` (new)
- `Iris/build/description/v2/tests/fixtures/item_page_information_sufficiency/**` (new)
- `Iris/build/description/v2/tools/build/INVENTORY.md`

다음 current consumer / producer는 observation 및 regression comparison만 수행하고 수정하지 않는다.

- `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua`
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserItemIndex.lua`
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`
- `Iris/build/description/v2/tools/build/iar_public_text_assessment.py` (retained validation utility; product IAR authority 없음)

### Docs

- `docs/iris_item_page_information_sufficiency_policy.md` (new, policy adoption 시)
- `docs/DECISIONS.md` (additive current decision)
- `docs/ARCHITECTURE.md` (responsibility / data-flow alignment)
- `docs/ROADMAP.md` (current state, gaps와 non-claim boundary)
- `docs/iris_item_page_information_sufficiency_plan.md` (이 계획)

`docs/Philosophy.md`는 수정하지 않는다.

### Config

- `Iris/build/description/v2/data/item_page_information_sufficiency/proposals/<proposal_sha256>/*.proposal.json` (new, pre-ratification immutable proposal packet)
- `Iris/build/description/v2/data/item_page_information_sufficiency/policy_ratification_contract.json` (new)
- `Iris/build/description/v2/data/item_page_information_sufficiency/baseline_field_registry.json` (new)
- `Iris/build/description/v2/data/item_page_information_sufficiency/assessment_contract.json` (new)
- `Iris/build/description/v2/data/item_page_information_sufficiency/layer3_state_derivation_contract.json` (new)
- `Iris/build/description/v2/data/item_page_information_sufficiency/layer4_state_derivation_contract.json` (new)
- `Iris/build/description/v2/data/item_page_information_sufficiency/state_exception_ledger.jsonl` (new)
- `Iris/build/description/v2/data/item_page_information_sufficiency/representative_cases.json` (new)
- `Iris/_docs/authority/iris_current_authority_manifest.json` (retained repository-governance container로서 새 policy input/evidence 역할만 additive하게 분류)
- `Iris/_docs/round3/current_route_required_validations.json` (policy adoption 후 별도 owner의 required validation으로 추가)

### Generated Artifacts

- `Iris/build/description/v2/output/item_page_information_sufficiency/assessment_input_manifest.json`
- `Iris/build/description/v2/output/item_page_information_sufficiency/page_assessment.jsonl`
- `Iris/build/description/v2/output/item_page_information_sufficiency/assessment_summary.json`
- `Iris/build/description/v2/output/item_page_information_sufficiency/information_gap_inventory.jsonl`
- `Iris/build/description/v2/output/item_page_information_sufficiency/anchor_assessment.json`
- `Iris/build/description/v2/output/item_page_information_sufficiency/terminology_responsibility_mapping.json`
- `Iris/build/description/v2/output/item_page_information_sufficiency/baseline_runtime_drift_report.json`
- `Iris/build/description/v2/output/item_page_information_sufficiency/protected_surface_hash_report.json`
- `Iris/build/description/v2/output/item_page_information_sufficiency/validation_report.json`
- `Iris/_docs/round3/item_page_information_sufficiency/<result_sha256>/canonical_successor_subject_manifest.json`
- `Iris/_docs/round3/item_page_information_sufficiency/<result_sha256>/independent_review.json`
- `Iris/_docs/round3/item_page_information_sufficiency/<result_sha256>/owner_seal.json`
- `Iris/_docs/round3/item_page_information_sufficiency/<result_sha256>/axis_qualified_closeout.json`

Generated assessment는 source / rendered / runtime / package authority가 아니며 reverse-merge input으로 사용할 수 없다.

---

## 6. Planned Changes

### Change 1 — Current Surface, Denominator, Policy Ratification and Execution Gate

Purpose:

current item-page denominator와 각 layer의 실제 소비 surface를 고정하고, `IPS-RAT-01`~`IPS-RAT-10`을 implementation 전에 owner-ratified single source로 닫는다.

Files:

- `docs/iris_item_page_information_sufficiency_policy.md`
- `Iris/build/description/v2/data/item_page_information_sufficiency/proposals/<proposal_sha256>/*.proposal.json`
- `Iris/build/description/v2/data/item_page_information_sufficiency/policy_ratification_contract.json`
- `Iris/build/description/v2/data/item_page_information_sufficiency/baseline_field_registry.json`
- `Iris/build/description/v2/data/item_page_information_sufficiency/assessment_contract.json`
- `Iris/build/description/v2/data/item_page_information_sufficiency/representative_cases.json`
- current input / rendered / runtime files (read-only)

Implementation Notes:

- denominator는 `items_itemscript.json`의 exact case-sensitive FullType set으로 materialize하고 input byte hash, sorted-key hash, row count를 함께 봉인한다.
- Layer 3 `2,105`, Layer 4 `1,606` 같은 planning-time subset count와 set difference를 inventory에 기록하되 이를 자동 missing / not-applicable 판정으로 사용하지 않는다.
- source/rendered/runtime/staging/diagnostic/historical role을 retirement `closeout.json`, `obligation_disposition.jsonl`, pointer-selected generation descriptor와 current top-level docs 기준으로 분리한다. `iris_current_authority_manifest.json`은 retained governance classification만 제공하고 product lifecycle authority가 아니다.
- baseline registry는 `items_itemscript.json`에 실제 존재하는 field만 exact name / type / null semantics / normalization rule과 함께 열거하고 owner가 registry hash를 ratify한다. `DisplayName`은 identity baseline으로 별도 표기한다. contract에는 이 registry가 actual vanilla Layer 1의 하한이며 미보존 runtime field가 `information_sufficient` 방향의 편향을 만들 수 있다는 `lower_bound_bias` limitation을 기록한다.
- `IrisItemDetailViewModel` / `IrisWikiSections.renderCoreInfoSection()`은 baseline source가 아니라 consumer cross-check다. runtime-only field 또는 ItemScript에 없는 field를 registry에 자동 추가하지 않는다.
- cross-check는 ItemScript registry에는 없지만 runtime consumer가 표시할 수 있는 drift field, 해당 field의 observable source, 영향을 받을 수 있는 item family와 영향 방향을 `baseline_runtime_drift_report.json`에 기록한다. 최소 family 분류에는 food / weapon이 포함되며 확인되지 않은 item별 runtime 값을 생성하지 않는다.
- Layer 2 `primary_subcategory`는 identity-restatement diagnostic comparison에 사용할 수 있지만 `IPS-RAT-10`에 따라 positive information contribution으로 계산하지 않는다.
- `policy_ratification_contract.json`을 `IPS-RAT-01`~`IPS-RAT-10`의 유일한 authoritative list로 사용한다. Objective, Change 1과 closeout은 이 list를 참조하고 별도 개수나 축약 목록을 만들지 않는다.
- ratification record는 exact proposal hash, owner identity, decision, timestamp와 rejected / amended subject를 기록한다.
- pre-ratification packet의 모든 contract는 immutable `*.proposal.json` 경로와 `ratification_state=proposal`을 가진다. adopted path의 contract는 owner가 exact proposal hash를 승인한 뒤에만 `ratification_state=ratified`, `proposal_subject_sha256`와 ratification record identity를 가지고 materialize한다. evaluator는 proposal 경로 또는 proposal state를 입력으로 받지 않는다.
- `IPS-RAT-01`~`IPS-RAT-10`이 전부 ratified되지 않으면 Change 2~7을 시작하지 않는다. 허용되는 종료 상태는 `page_sufficiency_preflight_complete_policy_blocked`이며 full assessment나 canonical adoption을 만들지 않는다.
- feedback의 Critical / Important adjudication과 실행 허용 범위를 별도 preflight artifact에 기록한다.

Validation:

- denominator key collision, case folding, duplicate FullType와 out-of-universe row를 fail-close한다.
- baseline registry의 모든 field가 current ItemScript field universe에 존재하고 owner-ratified hash와 일치하는지 검사한다. runtime drift report가 drift field, source, affected family와 `information_sufficient` 방향의 bias를 빠짐없이 공시하는지도 검사한다.
- `IPS-RAT-01`~`IPS-RAT-10` completeness와 ratification record identity를 확인하고 missing / rejected 항목이 있으면 policy-dependent execution을 fail-close한다.
- proposal / ratified path와 `ratification_state` 조합, adopted contract의 `proposal_subject_sha256`를 검사하고 proposal을 evaluator input으로 바꾼 negative fixture가 실패하는지 확인한다.
- `.223 탄약 거푸집`, `Base.Tongs`, current unadopted row와 Layer 3 / 4 absent row를 최신 artifact에서 다시 추출한다.
- historical / staging / diagnostic artifact가 current input으로 들어오지 않았음을 manifest로 검증한다.

---

### Change 2 — Layer 3 / Layer 4 State Contracts

Purpose:

Layer 3 presence와 contribution / requiredness, Layer 4 output과 applicability / representation을 분리한다.

Files:

- `Iris/build/description/v2/data/item_page_information_sufficiency/assessment_contract.json`
- `Iris/build/description/v2/data/item_page_information_sufficiency/layer3_state_derivation_contract.json`
- `Iris/build/description/v2/data/item_page_information_sufficiency/layer4_state_derivation_contract.json`
- `Iris/build/description/v2/data/item_page_information_sufficiency/state_exception_ledger.jsonl`
- `docs/iris_item_page_information_sufficiency_policy.md`

Implementation Notes:

- `artifact_set_materialization=sealed_complete`는 exact producer manifest가 선언한 record 집합이 전부 열거되고 각 record identity / hash가 결속되며 evaluator query가 그 선언 집합을 누락 없이 순회했다는 뜻이다. 이는 producer가 가능한 모든 game fact를 추출했다는 coverage, denominator의 모든 item을 authoring했다는 coverage, semantic completeness 또는 world-level absence 주장이 아니다.
- Layer 3 state는 current DVF provenance에서 계산하며 다음 orthogonal axis를 가진다.
  - `fact_availability`: `approved_fact_present`, `approved_fact_set_empty`, `unresolved`
  - `contribution`: `self_sufficient`, `supporting_context`, `identity_only`, `absent`, `unresolved`
  - `requiredness`: `required`, `optional`, `not_required`, `unresolved`
  - `representation`: `represented`, `missing`, `unresolved`
- Layer 3 `fact_availability`는 baseline / identity proposition을 제외한 approved proposition set에 대해 계산한다. 따라서 identity-only text가 있어도 non-baseline query가 0건이면 `approved_fact_set_empty`일 수 있다.
- `required`는 `sealed_complete` Layer 3 artifact set에서 해당 FullType에 결속된 approved non-baseline proposition이 한 건 이상 존재할 때 파생한다. `not_required`는 같은 exact set query 결과가 0건일 때 `no_approved_nonbaseline_proposition_in_sealed_set` reason과 함께 대칭적으로 파생한다. 이는 current artifact 집합에 대한 requiredness일 뿐 world-level fact absence나 향후 authoring 불필요 주장이 아니다.
- `optional`은 current producer contract의 owner-approved optionality provenance가 exact binding된 경우에만 파생한다. artifact set을 materialize하지 못하거나 query / proposition binding이 닫히지 않으면 `unresolved`다.
- Layer 3 `representation=missing`은 public representation이 관찰되지 않았다는 뜻이다. `required + missing`만 known missing 후보이고, `not_required / optional + missing`은 그 자체로 gap이 아니다. 요구 여부 값인 `not_required`를 representation 축에 넣지 않는다.
- `identity_only`는 rendered proposition set이 baseline / identity proposition에만 결속된 경우에만 파생한다. 문자열 유사도만으로 terminal state를 만들지 않는다.
- Layer 4 state는 current QG provenance에서 계산하며 다음 axis를 가진다.
  - `fact_availability`: `approved_fact_present`, `approved_fact_set_empty`, `unresolved`
  - `applicability`: `applicable`, `unresolved`
  - `representation`: `represented`, `missing`, `unresolved`
  - `scope_limitation`: `none`, `blocked_by_negative_authority`
- `applicable`은 current QG `PASS` fact / use_case가 있을 때만 파생한다. `approved_fact_set_empty`는 `artifact_set_materialization=sealed_complete`인 current QG 선언 집합에서 해당 FullType의 PASS fact query가 0건이라는 뜻이다.
- current emitted vocabulary에서 `not_applicable`을 제거한다. future schema가 이 token을 사용하려면 world-level closed-negative provider의 별도 adoption이 선행되어야 한다.
- `approved_fact_set_empty`는 fact-availability 값일 뿐 applicability 결론이 아니다. `sealed_complete + approved_fact_set_empty`에서는 observed representation을 `missing`, applicability를 `unresolved`, scope limitation을 `blocked_by_negative_authority`로 기록한다. 이 exact tuple은 negative authority 부재가 확정적으로 관찰됐다는 closed control state이며 world-level absence, non-applicability, approved negative fact 또는 known information gap과 동의어가 아니다.
- `evidence_absent`라는 모호한 token 대신 `approved_fact_set_empty`를 사용한다.
- `under_rendered`는 approved fact가 있으나 public representation에 결속되지 않은 `representation=missing`의 reason code로 정의하며 별도 axis value로 만들지 않는다.
- output이 없고 declared artifact-set materialization을 닫을 수 없으면 `unresolved`다.
- Layer 4 positive contribution은 structured use_case의 approved `PASS` evidence와 public positive line의 identity 결속으로 판단한다. `NO`, exclusion, debug-only, REVIEW-only는 positive contribution이 아니다.
- state exception ledger는 파생 불가능한 residue의 routing / review 기록만 가진다. `authority_effect=none`, `semantic_production=false`, `terminal_state_override_allowed=false`를 contract에 고정하며 ledger row가 없거나 미해결이면 evaluator state는 `unresolved`다.
- lexical observation은 `identity_only_candidate` 같은 diagnostic reason만 만들 수 있으며 단독으로 requiredness, applicability, negative fact 또는 final disposition을 만들 수 없다.
- 글자 수 / 문장 수 threshold와 숫자 score는 도입하지 않는다.

Validation:

- 짧지만 substantive한 Layer 3, 긴 identity-restatement, required, optional, sealed-set-derived `not_required`, known missing, unresolved fixture를 분리한다.
- Layer 4 positive Recipe, positive Right-click, Recipe + Right-click, approved-fact-set-empty / blocked-negative, missing, unresolved, exclusion-only fixture를 분리한다.
- producer artifact manifest materialization 누락, record hash drift와 declared-set query 누락을 실패시키고, `sealed_complete`가 extraction / authoring / world coverage claim으로 확장되지 않는지 contract assertion으로 검사한다.
- 같은 provenance와 state에 동일 reason code가 생성되는지 검증한다.
- state derivation의 모든 terminal decision이 exact producer input hash와 evidence reference를 가지는지 검사한다.
- exception ledger만으로 terminal state가 바뀌는 case가 0인지 검사한다.
- unsupported world-level negative, current `not_applicable` token과 `approved_fact_set_empty -> applicable/non-applicable` inference가 0인지 검사한다.

---

### Change 3 — Page-Level Decision Matrix and Assessment Contract

Purpose:

Layer 3 / Layer 4 state를 authority 병합 없이 page-level disposition으로 조합한다.

Files:

- `Iris/build/description/v2/data/item_page_information_sufficiency/assessment_contract.json`
- `docs/iris_item_page_information_sufficiency_policy.md`
- `Iris/build/description/v2/tests/fixtures/item_page_information_sufficiency/**`

Implementation Notes:

canonical machine token은 다음 네 가지로 고정한다.

- `information_sufficient`
- `evidence_limited`
- `known_information_missing`
- `unresolved`

decision precedence는 다음과 같다.

1. required Layer 3 또는 applicable Layer 4의 approved confirmed fact가 representation되지 않았으면 `known_information_missing`이다.
2. producer provenance, declared artifact-set materialization, requiredness 또는 disposition에 필요한 representation / applicability를 current authority로 닫을 수 없으면 `unresolved`다. 단 `sealed_complete + approved_fact_set_empty + applicability=unresolved + scope_limitation=blocked_by_negative_authority` tuple은 차단 사실이 확정적으로 파생된 non-dispositive scope limitation이므로 이 rule의 “닫을 수 없음”에 포함하지 않고 reason으로만 보존한다.
3. known missing / materially unresolved artifact-state가 없고 baseline에서 파생되지 않는 confirmed fact가 한 layer 이상에서 represented되면 `information_sufficient`다. `blocked_by_negative_authority`는 별도 scope limitation으로 보존하며 non-applicability 결론으로 바꾸지 않는다.
4. 양 producer의 declared artifact set이 `sealed_complete`이고, 양쪽 fact availability가 `approved_fact_set_empty`이며, Layer 3 requiredness가 `optional` 또는 `not_required`이고, baseline 밖 represented fact가 없으면 `evidence_limited`다. 이는 sealed artifact 집합 수준의 파생이며 extraction coverage, semantic completeness 또는 world-level negative가 아니다.
5. 위 explicit rule과 매칭되지 않는 모든 state vector는 terminal default `unresolved`다.

추가 불변식은 다음과 같다.

- Layer 4 represented는 Layer 3 required missing을 상쇄하지 않는다.
- Layer 3 represented는 Layer 4 applicable missing을 상쇄하지 않는다.
- Layer 3 optional + Layer 4 represented는 `information_sufficient`가 될 수 있다.
- Layer 3 represented + Layer 4 `approved_fact_set_empty` + `scope_limitation=blocked_by_negative_authority`는 world-level negative를 만들지 않으면서 `information_sufficient`가 될 수 있고 limitation reason을 유지한다.
- `blocked_by_negative_authority`는 terminal disposition을 직접 결정하지 않으며 rule 2의 unresolved trigger가 아니다. 같은 vector를 다른 해석으로 구현할 수 없다.
- identity-only / absent Layer 3 + Layer 4 output absent는 declared-set materialization, requiredness와 approved fact state에 따라 `evidence_limited`, `known_information_missing`, `unresolved` 중 하나이며 자동 success가 아니다.
- page disposition은 public visibility, recommendation, ranking, trust, publication 또는 release verdict를 포함하지 않는다.
- evaluator execution status와 subject disposition을 별도 field로 둔다. `execution_status=PASS`는 계산과 contract validation이 성공했다는 뜻일 뿐 모든 page가 sufficient하다는 뜻이 아니다.

Validation:

- 로드맵의 representative combination을 decision table fixture로 고정하고 `Layer 3 represented + Layer 4 approved_fact_set_empty + applicability unresolved + scope_limitation blocked_by_negative_authority`가 rule 2가 아니라 rule 3과 scope limitation으로 귀결되는 fixture를 명시한다.
- 알려진 missing / unresolved를 success로 보내는 matrix branch가 0인지 검사한다.
- 동일 state vector가 item identity와 무관하게 같은 disposition / reason을 만드는 metamorphic test를 둔다.
- 유효 state-space Cartesian product를 전수 평가해 모든 vector가 정확히 한 terminal disposition을 갖는지 totality test를 둔다.
- matrix-level reachability와 별도로 producer fixture → state derivation → precedence 전체 경로를 실행해 `not_required / optional + 양쪽 approved_fact_set_empty + sealed_complete -> evidence_limited`가 파생 수준에서 도달 가능한지 검사한다.
- full-universe 실행의 `evidence_limited` count를 별도 보고한다. count가 `0`이면 silent PASS하지 않고 `POLICY_REVIEW_REQUIRED`로 fail-loud하여 derivation trace와 current distribution이 의도된 honest-silence 경로를 닫았는지 owner가 재판정하게 한다. count를 만들기 위한 item-specific 예외나 synthetic production data는 금지한다.
- score, minimum length, item-specific FullType branch가 evaluator source에 없는지 검사한다.

---

### Change 4 — Deterministic Read-Only Evaluator and Validator

Purpose:

current inputs에 정책을 전수 적용하고 재현 가능한 result와 독립적인 no-write validation을 제공한다.

Files:

- `Iris/build/description/v2/tools/build/item_page_information_sufficiency.py`
- `Iris/build/description/v2/tools/build/run_item_page_information_sufficiency_assessment.py`
- `Iris/build/description/v2/tools/build/validate_item_page_information_sufficiency_assessment.py`
- `Iris/build/description/v2/tests/test_item_page_information_sufficiency.py`
- `Iris/build/description/v2/tools/build/INVENTORY.md`

Implementation Notes:

- evaluator는 retained public-text validation utility의 canonical hashing, subject/technical failure 분리, runner/validator separation과 no-write validation pattern만 재사용한다. 역사적 `iar_` 파일명에서 lifecycle 권한을 추론하지 않는다.
- evaluator는 `IPS-RAT-01`~`IPS-RAT-10` ratification record, `ratification_state=ratified`와 exact policy / baseline / derivation contract hashes가 없으면 실행을 거부한다.
- public-text metric, PASS, waiver, denominator 또는 human-review 결과를 page sufficiency input으로 재사용하지 않는다.
- default input은 `IrisLayer3DataCurrent.lua` pointer, selected `IrisLayer3Generations/<generation_id>/generation_descriptor.json`, 그 generation의 rendered/runtime universe와 Layer 4 producer identity를 contract에 명시한다. 7개 canonical input, output universe, raw SHA-256, schema/row count와 set identity를 검증한다.
- source facts, rendered Layer 3, Layer 4 structured use_case / requirements, public description / runtime projection identity를 분리해 로드한다.
- assessment row는 최소한 `fulltype`, input identities, baseline registry/hash와 observation, producer별 `artifact_set_materialization`, Layer 3 fact availability / contribution / requiredness / representation / provenance / reasons, Layer 4 fact availability / applicability / representation / scope limitation / provenance / reasons, exception-routing state, applied precedence rule, page disposition / reasons와 scope limitations를 포함한다.
- result ordering은 exact case-sensitive FullType 순서, object serialization은 canonical JSON, JSONL은 LF / UTF-8로 고정한다.
- evaluator는 지정 output root 밖에 쓰지 않는다. validator는 `--no-write`를 필수로 하며 result를 다시 계산해 hash와 row-level equality를 확인한다.
- missing / malformed / stale / out-of-universe input, duplicate identity, source-to-rendered mismatch와 protected output write attempt는 technical failure로 fail-close한다.
- assessment와 gap inventory는 source / rendered / runtime / package file을 수정하지 않는다.

Validation:

- same input / contract의 Run A / Run B byte identity를 검증한다.
- input 하나를 변조한 fixture가 identity mismatch로 실패하는지 확인한다.
- known missing, unresolved, evidence-limited, sufficient와 technical failure를 별도 결과로 확인한다.
- runner 결과와 독립 validator 재계산이 동일한지 확인한다.
- protected artifact pre / post hash가 동일한지 검사한다.
- proposal-state / unratified policy, baseline registry drift, incomplete artifact-set materialization과 exception-ledger terminal override fixture가 fail-close하는지 확인한다.

---

### Change 5 — Full Current-Universe Assessment and Gap Inventory

Purpose:

정책을 current vanilla denominator 전체에 적용하고, 성공률 목표 없이 실제 분포와 정보 공백을 기록한다.

Files:

- `Iris/build/description/v2/output/item_page_information_sufficiency/**`
- `Iris/_docs/round3/item_page_information_sufficiency/<result_sha256>/**`

Implementation Notes:

- denominator row는 모두 정확히 한 assessment row를 가져야 한다. missing Layer 3 / 4 input도 row 누락이 아니라 explicit state로 남긴다.
- summary는 disposition count, reason-code count, Layer 3 / 4 state cross-tab, assessed / unresolved denominator와 exact input hashes를 제공한다.
- exception ledger observability에는 최소 `ledger_row_count`, `denominator_with_ledger_entry_count`, `denominator_without_ledger_entry_count`, `derivation_residue_count`, `residue_routed_count`, `residue_unrouted_count`, `unresolved_due_to_unrouted_residue_count`와 denominator 대비 비율을 포함한다. ledger가 없는 정상 파생 row와 ledger 미기재 때문에 unresolved인 residue를 구분한다.
- gap inventory는 `known_information_missing`과 `unresolved`만 별도 projection하며 remediation priority, ranking, recommendation 또는 자동 authoring action을 만들지 않는다.
- `evidence_limited`는 별도 분포로 남기고 `information_sufficient`에 합치지 않는다.
- `.223 탄약 거푸집`과 `Base.Tongs`는 같은 generic evaluator path를 사용한다. 각 anchor에 Layer state, provenance, reason codes, applied precedence rule, terminal disposition과 scope limitation trace를 나란히 기록한다. 최신 source에서 서로 다른 disposition이 나와도 허용하며 roadmap의 과거 문제 진술을 결과에 강제하지 않는다.
- representative cases에는 Layer 3-only, Layer 4-only, short-substantive, identity-only, sealed approved-fact-set empty, required missing, applicable missing, unresolved와 current unadopted case를 포함한다.
- full assessment 결과를 content remediation 승인이나 release-wide threshold로 해석하지 않는다.

Validation:

- `assessment row count == exact denominator count`와 set equality를 검사한다.
- duplicate / omitted / out-of-denominator FullType가 0인지 검사한다.
- known missing 또는 unresolved가 `information_sufficient`로 분류된 row가 0인지 검사한다.
- exception-ledger coverage count / ratio가 page rows와 재계산 결과에 일치하고 unrouted residue가 별도 unresolved reason으로 추적되는지 확인한다.
- anchor / representative result가 policy table과 일치하는지 사람과 machine 양쪽에서 확인한다.
- 두 anchor에 item-specific branch 없이 동일 rule IDs가 적용됐는지 확인한다.
- distribution 합이 denominator와 정확히 같은지 확인한다.

---

### Change 6 — Public-Text / Presentation Boundary Alignment

Purpose:

Public Text Quality와 page sufficiency를 독립 claim axis로 유지하고 Menu / Tooltip terminology와 depth contract를 문서 수준에서 정리한다.

Files:

- `docs/iris_item_page_information_sufficiency_policy.md`
- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`
- `Iris/build/description/v2/output/item_page_information_sufficiency/terminology_responsibility_mapping.json`
- current Menu / Tooltip Lua files (read-only inspection)

Implementation Notes:

- 두 assessment의 subject, denominator, input identity, result와 failure attribution을 별도 표로 문서화한다.
- public-text PASS / page-insufficient, public-text finding / page-sufficient 조합을 모두 허용한다.
- `설명`, `개요`, `활용`, `관련 제작`, `제작`, `상호작용`, `요구 조건`별로 `heading`, `actual_layer_responsibility`, `implied_scope`, `mismatch_type`, `disposition=keep|rename_candidate|defer`를 mapping artifact에 기록하되 실제 heading은 변경하지 않는다.
- Recipe와 Right-click을 독립적이고 동등한 Layer 4 Source로 유지한다.
- Menu는 detailed surface, Tooltip은 동일 confirmed facts의 최대 4줄 quick-reference projection으로 유지한다.
- Tooltip 자체에 Menu와 같은 page completeness를 요구하지 않고, Tooltip을 별도 facts authority로 만들지 않는다.
- page disposition을 public-facing copy, badge, sorting, filtering 또는 selection input으로 추가하지 않는다.

Validation:

- assessment-axis 교차 fixture 네 종류를 검증한다.
- Menu / Tooltip facts authority와 최대 4줄 계약이 문서상 유지되는지 확인한다.
- runtime Lua 및 translation file diff가 0인지 확인한다.
- terminology mapping의 모든 heading이 disposition을 가지고 actual UI mutation claim을 만들지 않는지 검토한다.

---

### Change 7 — Required-Route Registration, Independent Review and Top-Level Closure

Purpose:

검증된 policy와 full assessment의 exact identity를 current governance에 additive하게 반영한다.

Files:

- `Iris/_docs/round3/current_route_required_validations.json`
- `Iris/_docs/authority/iris_current_authority_manifest.json`
- `Iris/_docs/round3/item_page_information_sufficiency/<result_sha256>/independent_review.json`
- `Iris/_docs/round3/item_page_information_sufficiency/<result_sha256>/owner_seal.json`
- `Iris/_docs/round3/item_page_information_sufficiency/<result_sha256>/canonical_successor_subject_manifest.json`
- `Iris/_docs/round3/item_page_information_sufficiency/<result_sha256>/axis_qualified_closeout.json`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`

Implementation Notes:

- required-validation entry는 `Publish Boundary / Item Page Information Sufficiency evidence` owner를 명시하고 DVF System, QG, stateless generation/installer 또는 package semantic responsibility로 귀속하지 않는다.
- canonical successor subject manifest는 policy / baseline / derivation contract, evaluator source, input / result와 함께 `current_route_required_validations.json`, `iris_current_authority_manifest.json`, `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`의 이 workstream additive successor entry identity를 포함한다.
- shared governance file 결속 단위는 전체-file raw hash가 아니라 exact additive entry다. JSON은 stable `entry_id`로 선택한 canonical object hash, Markdown은 unique start / end marker로 경계 지은 canonical UTF-8 segment hash를 사용한다. manifest에는 path, entry ID, selector / boundary rule, entry hash와 freeze 시 container raw hash를 함께 기록하되 staleness gate는 entry identity에 적용한다.
- bound entry의 내용 변경, 삭제, duplicate ID 또는 경계 ambiguity는 review / seal을 stale 처리한다. bound entry 밖의 unrelated additive edit는 container raw hash drift로 보고하되 entry hash가 그대로면 이 workstream review / seal을 무효화하지 않는다.
- independent reviewer는 위 manifest exact hash에 결속해 decision matrix, absence reasoning, denominator, regression guard와 non-mutation claim을 검토한다. roadmap / plan 작성자나 공동 작성자, policy / evaluator / claim-bearing successor 구현자, owner 또는 disposition signer는 eligible independent review credit을 갖지 않는다.
- owner seal은 policy 선택, review identity와 full assessment claim boundary를 별도로 승인한다. 계획 작성 요청 자체를 owner seal로 간주하지 않는다.
- 다섯 claim-bearing governance successor entry를 먼저 materialize하고 hash-freeze한 뒤 canonical successor subject manifest를 만든다. 그 manifest에 대한 independent review, owner seal, axis-qualified closeout 순으로 진행하며 review / seal identity를 다시 다섯 successor entry에 써서 순환 참조를 만들지 않는다.
- `DECISIONS.md`에는 새 current decision을 additive하게 추가하고 sealed historical decision을 수정하지 않는다. freeze 이전 이 entry에 stable closeout path `Iris/_docs/round3/item_page_information_sufficiency/<result_sha256>/axis_qualified_closeout.json`을 미리 기록한다. 다음 라운드는 이 path의 존재, subject-manifest / review / seal identity와 status를 따라 closure 상태를 판정하므로 post-seal `DECISIONS.md` rewrite나 두 번째 claim-bearing entry가 필요 없다.
- `ARCHITECTURE.md`에는 `current information -> read-only page assessment -> Publish Boundary component evidence` 흐름과 producer responsibility 비변경을 추가한다.
- `DECISIONS.md` additive entry와 `ROADMAP.md` Hold에는 다음 regression guard를 직접 기록한다: all-item universe를 모든 item의 독립 장문 Layer 3 authoring 의무로 해석하지 않으며, disposition distribution을 content authoring / extraction expansion / Evidence Allowlist expansion / taxonomy repartition 승인으로 해석하지 않는다.
- `ROADMAP.md`에는 full assessment의 실제 disposition 분포, gap inventory의 후속 remediation 비승인과 remaining next gate만 요약한다.
- independent review / owner seal 이후 다섯 claim-bearing governance successor의 bound entry identity 중 하나라도 변경되면 기존 review / seal을 자동 승계하지 않고 stale로 판정한다.
- required-route validation PASS를 Publish Boundary PASS, package publication 또는 release readiness로 확대하지 않는다.

Validation:

- machine validation, independent review와 owner seal의 subject / hash / status가 서로 정확히 결속되는지 확인한다.
- bound successor entry의 mutation / deletion / duplicate-marker fixture가 기존 review / seal을 invalid로 만드는지 확인하고, 같은 container의 unrelated additive entry fixture는 raw hash drift를 보고하되 seal을 유지하는지 확인한다.
- regression guard가 `DECISIONS.md`, `ROADMAP.md` Hold와 axis-qualified terminal closeout에 모두 존재하는지 추적한다.
- top-level 세 문서 사이 canonical token, authority wording, closure scope와 non-claim이 일치하는지 검사한다.
- 기존 sealed decision diff가 additive insertion 외에 없는지 검토한다.
- `DECISIONS.md` successor entry의 stable closeout path가 실제 axis-qualified closeout artifact에 도달하고 그 artifact가 exact subject-manifest / review / seal identity를 가진다는 것을 검증한다.
- current required-validation runner에서 새 validation이 exact owner와 함께 PASS하는지 확인한다.

---

## 7. Validation Plan

### Automated Validation

모든 명령은 repository root의 Windows PowerShell에서 실행한다. 생성 및 full-suite 검증은 primary dirty working tree가 아닌 disposable clean checkout과 격리된 output root를 사용한다.

#### 1. Focused policy / evaluator tests

```powershell
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_item_page_information_sufficiency.py"
```

검증 항목:

- `IPS-RAT-01`~`IPS-RAT-10` 단일 ratification contract와 exact hash binding
- ratification 이전 Change 2–7 실행 차단과 허용된 preflight 범위
- proposal path / `ratification_state=proposal`과 adopted `ratification_state=ratified`의 파일 수준 분리
- exact denominator / case-sensitive identity
- explicit `items_itemscript.json` baseline field registry와 runtime consumer cross-check 분리
- baseline lower-bound drift field / affected family / bias-direction report
- provenance-derived Layer 3 / 4 state axes와 non-authoritative exception ledger
- Layer 3 `not_required`의 sealed-set 대칭 파생과 representation 축 배제
- `approved_fact_set_empty` / `blocked_by_negative_authority` / `unresolved`의 분리
- `blocked_by_negative_authority`의 rule 2 예외와 non-dispositive limitation 보존
- 현재 authority에서 `not_applicable` terminal emission 금지
- Layer 3 × Layer 4 입력 공간 전체에 대한 total decision matrix
- producer fixture에서 `evidence_limited`까지 이어지는 derivation-level reachability
- result precedence와 reason vocabulary
- item-identity-independent policy
- malformed / stale / ambiguous input fail-close
- no score / no length threshold / no empty-output-to-not-applicable shortcut
- unmatched vector의 terminal `unresolved` 귀결과 모든 matrix row의 reachability

#### 2. Public-text axis regression

```powershell
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_iar_public_text_assessment.py"
uv run python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_public_text_quality_acceptance.py"
```

#### 3. Full assessment Run A / Run B

```powershell
uv run python -B Iris/build/description/v2/tools/build/run_item_page_information_sufficiency_assessment.py --contract Iris/build/description/v2/data/item_page_information_sufficiency/assessment_contract.json --ratification-contract Iris/build/description/v2/data/item_page_information_sufficiency/policy_ratification_contract.json --require-ratified-policy --output-root <run-a>
uv run python -B Iris/build/description/v2/tools/build/run_item_page_information_sufficiency_assessment.py --contract Iris/build/description/v2/data/item_page_information_sufficiency/assessment_contract.json --ratification-contract Iris/build/description/v2/data/item_page_information_sufficiency/policy_ratification_contract.json --require-ratified-policy --output-root <run-b>
uv run python -B Iris/build/description/v2/tools/build/validate_item_page_information_sufficiency_assessment.py --contract Iris/build/description/v2/data/item_page_information_sufficiency/assessment_contract.json --ratification-contract Iris/build/description/v2/data/item_page_information_sufficiency/policy_ratification_contract.json --result-root <run-a> --compare-result-root <run-b> --require-full-universe --require-matrix-totality --require-derivation-reachability --require-canonical-successor-binding --no-write
```

Run A / B에서 manifest, JSONL, summary, gap inventory, terminology mapping, baseline runtime drift report와 anchor rule-path trace의 byte identity를 요구한다. validator는 ratification identity / state, baseline registry hash, derivation contract hash, declared-set materialization, exception-ledger non-authority / coverage, matrix totality, derivation-level `evidence_limited` reachability와 현재 `not_applicable` 비도달성도 함께 검사한다. full-universe `evidence_limited=0`이면 PASS 대신 `POLICY_REVIEW_REQUIRED`로 종료한다.

#### 4. Current route validation

policy adoption 후 disposable clean checkout에서 실행한다.

```powershell
uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --out <isolated-output>/current-route-result.json
```

#### 5. Lua syntax no-regression

Lua를 수정하지 않지만 public runtime surface 비변경 확인의 보조 검증으로 실행한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

#### 6. Repository diff / protected artifact validation

```powershell
git diff --check
git status --short
```

evaluator가 기록한 pre / post protected-surface hash report에서 다음이 byte-identical인지 확인한다.

- current descriptor가 열거한 7개 Layer 3 canonical inputs
- `IrisLayer3DataCurrent.lua` pointer와 selected generation descriptor/rendered JSON
- current Layer 4 use_case / requirements / descriptions
- Layer 3 stable facade/index/lookup과 selected immutable generation chunks
- Layer 4 runtime facade, lookup indexes와 chunks
- Browser / Wiki / Tooltip Lua
- package snapshot이 존재할 경우 해당 projection

정확한 relevant command가 exit `0`일 때만 해당 validation을 PASS로 기록한다. required tooling이나 input identity가 없으면 PASS가 아니라 `BLOCKED`다.

### Manual Validation

- independent reviewer가 exact result뿐 아니라 `current_route_required_validations.json`, `iris_current_authority_manifest.json`, `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`의 exact additive successor-entry identity가 포함된 canonical successor subject manifest 전체에 대해 denominator, baseline, derivation provenance, absence reasoning, decision precedence와 regression guard를 검토한다.
- `.223 탄약 거푸집`, `Base.Tongs`, current unadopted row, Layer 3-only, Layer 4-only, evidence-limited, known-missing과 unresolved sample을 같은 policy table로 재판정한다.
- 각 anchor에서 Layer 3 state, Layer 4 fact availability / applicability / representation / scope limitation, provenance, reason, precedence rule, terminal disposition과 limitation을 따라갈 수 있는지 확인한다.
- public-text PASS / page-insufficient와 public-text finding / page-sufficient 조합이 실제로 독립적인지 확인한다.
- gap inventory가 recommendation, priority 또는 자동 remediation 언어를 포함하지 않는지 검토한다.
- Menu / Tooltip terminology review가 Recipe를 Right-click의 상위 체계로 만들지 않는지 확인한다.
- owner가 `IPS-RAT-01`~`IPS-RAT-10` policy, independent review identity, canonical successor subject manifest와 final claim boundary를 별도 seal로 승인한다.
- 이 계획에 반영된 ChatGPT / Claude 피드백은 roadmap 공동 작성에 해당하므로 independent review credit으로 계산하지 않는다.

### Validation Limits

- 실제 Project Zomboid 인게임 page / Tooltip UX 검증은 수행하지 않는다. runtime mutation이 없기 때문이다.
- multiplayer와 long-session runtime validation을 수행하지 않는다.
- external mod item universe compatibility sweep를 수행하지 않는다.
- current ko 이외 locale의 semantic sufficiency를 판정하지 않는다.
- package ZIP 생성·배포·설치 검증과 Workshop / B42 readiness를 수행하지 않는다.
- FPS, heap, latency, allocation 또는 frame-time 측정을 수행하지 않는다.
- 모든 information gap을 remediation하거나 새 Evidence를 추출하지 않는다.
- baseline registry는 ItemScript 보존 field에 한정되므로 실제 vanilla Layer 1 표시 항목의 하한이다. 미보존 runtime field는 baseline 밖 contribution처럼 계산될 수 있어 판정 편향이 `information_sufficient` 방향으로 작용하며, 이 계획은 인게임 전수 관찰로 그 편향의 크기를 보정하지 않는다.
- `artifact_set_materialization=sealed_complete`는 선언된 current artifact set의 identity / hash / query 완전성만 검증한다. producer extraction coverage, semantic completeness, 모든 가능한 game fact 또는 world-level absence는 검증하지 않는다.
- assessment 결과만으로 public-text quality, semantic quality, Registry, runtime compatibility 또는 release acceptance를 선언하지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

변경 있음.

새 page-level assessment policy와 component evidence가 추가된다. 다만 Layer 3 facts/body production, Layer 4 interaction production, stateless generation/validation/install과 package 책임은 변경하지 않는다. Publish Boundary만 결과를 component evidence로 소비한다.

### Runtime Behavior Surface

None.

runtime Lua, public require surface, Menu / Tooltip rendering, item identity와 game state를 변경하지 않는다.

### Compatibility Surface

None.

기존 Lua API, runtime data shape, chunk routing, Browser all-item indexing과 external mod behavior를 변경하지 않는다. 새 Python CLI와 JSON contract는 offline-only다.

### Sealed Artifact Surface

변경 있음.

새 immutable proposal packet, policy ratification, baseline registry, state derivation contract, non-authoritative exception ledger, assessment result, canonical successor subject manifest, review, owner seal과 axis-qualified closeout을 additive하게 생성한다. 기존 sealed decision / failure / closeout / current source / rendered / runtime / package artifact는 rewrite하지 않는다.

### Public-Facing Output Surface

None.

heading과 text는 검토만 하며 실제 UI, Tooltip, Browser visibility와 quality exposure는 변경하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- page aggregation이 Layer 3 / Layer 4 semantic authority 병합으로 오해될 수 있다.
- page result를 자체 Publish Boundary PASS나 새 information layer로 승격할 수 있다.
- Layer 2 browsing anchor가 baseline semantic fact로 잘못 승격될 수 있다.
- full-universe denominator와 DVF / QG subset denominator가 혼동될 수 있다.
- existing public-text evaluator 재사용이 두 assessment axis 병합으로 이어질 수 있다.
- per-item state ledger가 provenance 대신 requiredness / applicability semantic authority가 될 수 있다.
- owner ratification 없이 evaluator 구현이 선행되어 미채택 정책을 사실상 고정할 수 있다.
- `not_required`를 current sealed-set query가 아니라 world-level absence나 영구적인 authoring 불필요로 오해할 수 있다.
- matrix에서는 reachable한 `evidence_limited`가 producer provenance 파생에서는 전부 `unresolved`에 흡수될 수 있다.

완화:

- producer state와 page projection을 별도 field / module / document로 유지한다.
- assessment contract에 `authority_effect=none`, `fact_generation_allowed=false`, `publish_verdict=false`를 명시한다.
- Layer state는 sealed producer provenance에서 derivation하고 exception ledger에는 `semantic_production=false`, `terminal_state_override_allowed=false`를 강제한다.
- `not_required`는 `sealed_complete`로 materialize된 declared Layer 3 set의 zero-result query에만 결속하고 reason code에 artifact-set scope를 노출한다.
- `IPS-RAT-01`~`IPS-RAT-10` ratification 전에는 census, hash, anchor capture와 immutable proposal packet만 허용하고 policy-dependent implementation/full run/required-route registration을 차단한다.
- matrix totality와 producer-to-disposition derivation reachability를 별도 검증하고 full-universe `evidence_limited=0`을 silent PASS로 처리하지 않는다.
- denominator set identity와 subset cross-tab을 별도 산출한다.
- public-text input / result는 page evaluator의 dependency에서 금지한다.

### Runtime Risk

- evaluator 결과가 runtime data 또는 UI logic에 잘못 배선될 수 있다.
- current generated artifact를 통과시키기 위해 source / rendered / runtime file을 수정할 수 있다.

완화:

- Python offline path에만 구현하고 Lua diff 0을 required invariant로 둔다.
- output-root write allowlist와 protected-surface pre / post hash를 fail-close한다.
- current route entry도 offline validation으로만 등록한다.

### Compatibility Risk

- case-insensitive reader가 case-distinct FullType을 병합할 수 있다.
- empty Layer 4 output을 not-applicable로 처리하면 외부 모드 / 미추출 interaction이 잘못 닫힐 수 있다.
- artifact-set absence를 게임 세계 수준의 interaction 부재로 확대할 수 있다.
- planning-time static denominator를 runtime mod universe 전체로 과대 주장할 수 있다.
- ItemScript-only baseline의 하한 성격을 숨기면 runtime Layer 1의 미보존 field가 marginal contribution처럼 계산되어 sufficiency를 과대 판정할 수 있다.

완화:

- Python case-sensitive JSON reader와 exact-key hash를 사용한다.
- `approved_fact_set_empty`는 sealed artifact set에만 결속하고 world-level negative로 사용하지 않는다.
- 현재 closed-negative provider가 없으므로 `not_applicable`은 emit하지 않으며 negative authority가 필요한 경로는 `unresolved` 또는 명시적 `blocked_by_negative_authority`로 남긴다.
- baseline runtime drift report와 `IPS-RAT-03` limitation에 lower-bound bias, drift field와 affected item family를 명시한다.
- result claim을 current vanilla offline snapshot에 한정한다.

### Regression Risk

- known missing이 다른 layer의 정보량으로 숨겨질 수 있다.
- approved artifact-set absence와 representation missing이 합쳐질 수 있다.
- lexical heuristic이 사실상 semantic classifier로 굳어질 수 있다.
- anchor의 과거 설명을 맞추기 위해 최신 current state를 왜곡할 수 있다.
- machine PASS, independent review와 owner seal이 하나의 completion token으로 축약될 수 있다.
- decision matrix가 예시 조합만 덮고 새로운 state vector를 암묵적으로 통과시킬 수 있다.
- review / seal 이후 claim-bearing governance successor 변경이 기존 승인을 무효화하지 않은 채 남을 수 있다.
- shared governance file의 전체 raw hash를 gating identity로 사용하면 다른 workstream의 unrelated additive edit가 이 assessment의 review / seal을 불필요하게 stale로 만들 수 있다.
- Markdown marker 또는 JSON entry selector가 모호하면 entry-level binding이 잘못된 successor를 가리킬 수 있다.

완화:

- precedence matrix, metamorphic / adversarial fixtures와 per-axis reason codes를 고정한다.
- Layer 3 × Layer 4 전체 입력 공간의 totality test를 두고 unmatched vector는 terminal `unresolved`로 fail-close한다.
- 최신 input hash를 anchor result의 유일한 current 근거로 사용한다.
- review / seal / execution status를 별도 schema와 claim으로 유지한다.
- 다섯 shared governance successor는 unique entry ID와 canonical entry hash로 결속하고 full-file raw hash는 diagnostic drift로만 기록한다. 이 선택은 unrelated workstream 편집으로 인한 false staleness를 줄이면서 이 workstream의 exact claim-bearing segment를 보존한다.
- duplicate / missing entry ID, ambiguous Markdown boundary와 bound-entry mutation은 fail-close하고 review / seal을 stale 처리한다.

---

## 10. Rollback Plan

### Policy Adoption 이전

- immutable proposal packet과 preflight inventory를 비채택 diagnostic으로 보존하거나 제거하고 기존 Iris information model을 그대로 유지한다. policy-dependent evaluator, adopted contract, fixtures와 assessment output은 이 단계에서 존재해서는 안 된다.
- protected current artifacts에는 변화가 없으므로 source / runtime rollback은 필요하지 않다.

### Policy Adoption 이후

- current required-validation entry를 additive correction으로 비활성화하고 page assessment를 `historical` 또는 `diagnostic predecessor`로 재분류한다.
- `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`의 이미 채택된 기록을 소급 삭제하지 않고 새 correction / supersession entry로 rollback 이유와 적용 범위를 남긴다.
- independent review, owner seal, 실패 result와 gap inventory는 provenance로 보존하고 rewrite하지 않는다.
- source / rendered / runtime / package artifact는 assessment 때문에 변경하지 않았으므로 되돌리지 않는다.

### Policy Defect 발견 시

- page 결과에 맞춰 content를 수정하지 않는다.
- policy / matrix를 새 version으로 수정하고 same frozen input에 전수 재실행한다.
- predecessor result는 superseded identity로 보존하고 successor result와 섞지 않는다.
- Layer 3 / 4 responsibility 충돌, unsupported inference, protected mutation 또는 user-facing quality exposure가 확인되면 adoption을 fail-close한다.

### Immediate Rollback Triggers

- owner ratification identity가 없거나 `IPS-RAT-01`~`IPS-RAT-10` 중 하나가 미승인인 상태에서 Change 2–7 산출물이 생성된 경우 해당 산출물을 비채택 diagnostic으로 격리한다.
- proposal-state contract가 adopted path 또는 evaluator input으로 사용되거나 adopted contract가 exact `proposal_subject_sha256`에 결속되지 않은 경우 execution / adoption을 중지한다.
- exception ledger가 provenance-derived terminal state를 override하거나 semantic fact / negative를 생성한 경우 assessment adoption을 중지한다.
- `approved_fact_set_empty`가 world-level negative 또는 current `not_applicable`로 변환된 경우 해당 result와 review / seal을 invalidate한다.
- full-universe `evidence_limited=0`인데 validation이 `POLICY_REVIEW_REQUIRED` 없이 PASS를 주장한 경우 해당 result를 invalidate한다.
- canonical successor subject manifest의 다섯 bound governance successor entry 중 하나가 review / seal 이후 변경·삭제·중복된 경우 새 manifest, independent review와 owner seal 전까지 current claim을 rollback한다.

---

## 11. Governance Constraints

- `docs/Philosophy.md`의 근거 기반, 중립성, 근거 부족 시 침묵 원칙을 유지한다.
- Iris는 정보를 보여줄 뿐 item, action 또는 game state를 변경하지 않는다.
- PZ runtime Iris는 100% Lua로 유지하며 새 runtime JVM / Python dependency를 만들지 않는다.
- runtime / build-time separation을 유지한다.
- DVF System은 Layer 3 body production만, QG는 Layer 4 production만 소유한다.
- Layer 3 artifact identity는 content-derived descriptor와 stateless validation이 증명하고 protected current visibility는 `install_dvf_3_3_complete_generation.py`가 `IrisLayer3DataCurrent.lua` 한 파일로만 전환한다. 어느 메커니즘도 semantic producer가 되지 않는다.
- Page assessment는 Publish Boundary component evidence이고 bare acceptance / release claim이 아니다.
- `IPS-RAT-01`~`IPS-RAT-10` owner ratification은 하나의 authoritative list와 하나의 exact identity로 관리하며 중복 policy list를 만들지 않는다.
- policy-dependent Change 2–7은 ratification 이전에 실행하지 않는다. preflight census / hash / anchor capture / policy proposal은 채택·완료 claim 없이 수행할 수 있다.
- proposal과 ratified contract는 immutable proposal path와 `ratification_state`로 파일 수준에서 구분하며 evaluator는 ratified adopted path만 소비한다.
- Layer 3 requiredness와 Layer 4 applicability는 sealed producer provenance에서 derivation하며 per-item exception ledger는 semantic authority나 terminal override 권한을 갖지 않는다. Layer 3 `not_required`는 declared artifact-set query scope 밖으로 확대하지 않는다.
- `approved_fact_set_empty`는 approved artifact set이 비어 있다는 뜻으로만 사용하고 world-level negative와 구분한다. 현재 closed-negative authority가 없으므로 `not_applicable`을 emit하지 않는다.
- `artifact_set_materialization=sealed_complete`는 declared records의 identity / hash / exhaustive query만 뜻하며 extraction coverage, semantic completeness 또는 world absence를 뜻하지 않는다.
- `blocked_by_negative_authority`는 확정된 non-dispositive scope limitation으로 취급하고 precedence rule 2의 unresolved trigger로 사용하지 않는다.
- baseline은 explicit `items_itemscript.json` field registry로 정의하며 `renderCoreInfoSection()`은 consumer cross-check일 뿐 baseline authority가 아니다.
- baseline registry의 actual Layer 1 하한 성격과 `information_sufficient` 방향 편향을 owner ratification 및 result limitation에 노출한다.
- Recipe와 Right-click을 독립적이고 동등한 Source로 유지한다.
- Menu와 Tooltip은 동일 facts authority를 유지하고 Tooltip은 최대 4줄을 넘지 않는다.
- insufficient / unresolved / evidence-limited disposition을 Browser hiding, sorting, filtering, recommendation, badge 또는 trust signal로 사용하지 않는다.
- unsupported fact, unsupported negative conclusion과 lexical semantic inference를 생성하지 않는다.
- additive amendment와 minimal diff를 우선하고 기존 sealed historical decision을 rewrite하지 않는다.
- current source / rendered / runtime / package artifact는 assessment를 위해 mutate하지 않는다.
- current Layer 3 protected surface는 stable facade/index/lookup, `IrisLayer3DataCurrent.lua` pointer와 pointer-selected immutable generation 전체다. Assessment는 어느 것도 설치·교체하거나 predecessor pointer를 복구하지 않는다.
- generated assessment와 gap inventory를 reverse-merge authority로 사용하지 않는다.
- item-specific exception, score, ranking, minimum length / sentence threshold를 도입하지 않는다.
- execution PASS, subject disposition, independent review, owner seal과 final claim을 서로 분리한다.
- all-item universe는 모든 item의 독립 장문 Layer 3 authoring 의무가 아니며, disposition distribution은 content authoring / extraction expansion / Evidence Allowlist expansion / taxonomy repartition 승인이 아니다.
- independent review / owner seal은 exact canonical successor subject manifest에 결속하며 bound claim-bearing successor entry 변경 시 stale가 된다. unrelated container edit는 raw-hash drift로 보고하되 자동 stale 사유가 아니다.
- validation은 fail-closed다. exact relevant command가 exit `0`이 아니면 PASS를 주장하지 않는다.

---

## 12. Expected Closeout State

Expected closeout target: `page_sufficiency_assessment_complete`

이 피드백 반영 자체는 `IPS-RAT-01`~`IPS-RAT-10` owner ratification, eligible independent review 또는 owner seal을 충족하지 않는다. 특히 이번 roadmap에 기여한 reviewer의 의견은 independent review credit으로 재사용하지 않으며, 별도 eligible reviewer가 exact canonical successor subject manifest를 검토하기 전까지 해당 gate는 미충족이다.

종료 상태는 다음 axis-qualified vocabulary만 사용한다.

- `page_sufficiency_preflight_complete_policy_blocked`: census / hash / anchor / immutable policy proposal은 완료됐지만 `IPS-RAT-01`~`IPS-RAT-10` owner ratification이 없어 Change 2–7이 차단됨
- `page_sufficiency_policy_adopted`: `IPS-RAT-01`~`IPS-RAT-10`이 exact identity로 ratified됐지만 full-universe assessment와 canonical closure가 미완료임
- `page_sufficiency_assessment_partial`: ratified policy에 따른 assessment가 실행됐지만 validation, review, seal 또는 governance successor closure 중 하나 이상이 미완료임
- `page_sufficiency_assessment_complete`: 아래 모든 조건을 충족함

`page_sufficiency_assessment_complete`는 다음 조건을 모두 충족한 경우에만 사용한다.

- `IPS-RAT-01`~`IPS-RAT-10` policy가 single authoritative ratification contract의 exact identity로 ratified되고 adopted contract가 proposal hash / ratification state에 정확히 결속됨
- exact current vanilla denominator, Layer 3 pointer/generation ID/7 canonical inputs/output universe와 Layer 4 input identities sealed
- explicit `items_itemscript.json` baseline field registry가 adopted되고 runtime consumer cross-check와 분리되며 lower-bound bias / drift field / affected family가 공시됨
- Layer 3 / 4 provenance derivation contract와 non-authoritative exception ledger contract가 adopted되고 ledger coverage가 summary에 보고됨
- Layer 3 `not_required`가 sealed-set zero query에서 파생되고 representation 축에서 제거됨
- declared artifact-set materialization, extraction / semantic coverage와 world-level negative가 분리되고 current `not_applicable` 비도달성이 확인됨
- `blocked_by_negative_authority`가 rule 2의 unresolved trigger가 아닌 non-dispositive scope limitation으로 고정됨
- Layer 3 × Layer 4 total page decision matrix가 adopted되고 unmatched vector가 terminal `unresolved`로 귀결됨
- `evidence_limited`가 matrix와 producer provenance 파생 양쪽에서 reachable하며 full-universe count가 별도 보고됨; count `0`이면 owner policy review가 닫히기 전까지 assessment PASS를 주장하지 않음
- deterministic evaluator / no-write validator implemented
- current denominator 전수 assessment complete
- Run A / Run B deterministic identity PASS
- protected artifact non-mutation PASS
- terminology responsibility mapping과 representative / anchor rule-path trace complete
- canonical successor subject manifest가 policy / evaluator / input / result와 다섯 claim-bearing governance successor의 exact additive-entry identity를 포함함
- exact-manifest eligible independent review complete
- exact-manifest owner seal complete
- `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md` additive alignment complete이며 regression guard가 `DECISIONS.md`, `ROADMAP.md` Hold와 terminal closeout에 존재함
- `DECISIONS.md` successor entry가 stable axis-qualified closeout path를 포함하고 그 경로의 artifact가 exact subject-manifest / review / seal identity와 최종 상태를 기록함
- review / seal 뒤 bound claim-bearing successor entry mutation이 없거나 mutation 후 새 review / seal이 완료됨

하나라도 충족되지 않으면 위 vocabulary에서 실제로 완료된 axis를 나타내는 가장 구체적인 상태만 사용한다. bare `complete` 또는 bare `partial`은 사용하지 않는다.

이 closeout이 의미하는 것은 다음으로 한정한다.

- Layer 3 contribution / requiredness, Layer 4 applicability / representation과 page-level sufficiency를 분리하는 정책이 확립됐다.
- current vanilla offline denominator가 동일 정책으로 전수 평가됐다.
- 결과는 Publish Boundary가 소비할 read-only component evidence이며 producer authority와 runtime / public behavior는 유지됐다.
- all-item universe는 모든 item의 독립 장문 Layer 3 authoring target이 아니며 disposition distribution은 content / extraction / allowlist / taxonomy 변경을 승인하지 않는다.

다음을 의미하지 않는다.

- 모든 current page가 information-sufficient함
- 모든 known gap 또는 unresolved state가 해결됨
- DVF / QG content remediation 완료
- Public Text Quality PASS
- DVF Body Compiler, retired Registry Authority, Registry Runtime Compatibility 또는 Publish Boundary PASS
- package publication, release / Workshop / B42 readiness
- external mod universe coverage
- actual UI / Tooltip 변경 또는 인게임 QA 완료
