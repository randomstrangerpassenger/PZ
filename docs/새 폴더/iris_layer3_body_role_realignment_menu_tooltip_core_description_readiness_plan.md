# Implementation Plan

Iris Layer 3 Body Role Realignment / Menu·Tooltip Core Description Readiness

> 2026-08-20 IAR retirement successor amendment: 아래의 `current IAR adoption` 조건은 더 이상 stateful registry writer/receipt를 요구하지 않는다. Layer 3 public mutation이 승인되면 DVF 3.3의 external deterministic complete-generation, stateless key/payload validation, R2-B generation-pointer install과 package projection이 후속 책임을 소유한다. Owner authorization과 Menu/Tooltip 범위는 기존 본문대로 별도다.

## 1. Objective

Iris의 current canonical item universe와 current Layer 3 corpus를 대상으로, Layer 3를 모든 item에 강제되는 상세 설명이 아니라 확인된 설명 재료가 있을 때 제공하는 선택적 개요·해설 계층으로 재정렬한다.

이번 실행은 다음 결과를 deterministic offline artifact로 만든다.

- 모든 existing Layer 3 body에 정확히 하나의 disposition을 부여한다.
- 모든 canonical item에 body 유무와 독립적인 description readiness를 정확히 하나 부여한다.
- core description과 acquisition information을 별도 role material로 분리한다.
- current facts의 문자열을 의미적으로 역추론하지 않고 registered rule, exact provenance와 explicit human exception만 사용한다.
- 기존 public artifact를 변경하지 않는 staging successor를 먼저 생성·평가한다.
- `설명 재료 부족` item만 Problem 5A candidate로 결정론적으로 투영한다.
- Menu와 Tooltip이 같은 confirmed facts에서 서로 다른 깊이의 projection을 소비할 준비 상태를 만든다.
- Change 1~8이 만든 exact tracked terminal subject를 mandatory full-repository Clean-Checkout Run A/B로 검증한 뒤에만 staging-scoped completion을 선언한다.

본 계획의 기본 closeout은 **staging-only**다. 이 표현은 public adoption 범위를 제한할 뿐 tracked repository validation을 줄이지 않는다. current IAR adoption, runtime payload 교체와 Menu public text 교체는 별도 owner authorization과 선행 계약 충족 후 열리는 조건부 후속 실행으로 분리한다. Tooltip은 role-labeled input readiness까지만 다루며 실제 UI나 줄 배치는 변경하지 않는다.

### Review Feedback Adjudication

종합 리뷰의 Critical 2건과 Revision C~K를 다음처럼 판정한다.

| Review item | 판정 | 계획 반영 |
|---|---|---|
| Eligibility mapping granularity | 채택 | mapping key를 최소 `(source_slot, fact_origin)`으로 고정하고 observed non-empty 조합의 unresolved mapping `0`을 policy-dependent execution 전 요구 |
| Staging-only Clean-Checkout 충돌 | ChatGPT안 채택 | `DECISIONS.md`의 current mandatory exact-tracked-subject contract에 따라 Change 1~8 terminal subject에도 full-repository Run A/B 필수; Change 9가 새 tracked subject를 만들면 다시 실행 |
| Exact duplicate semantics | 채택 | detection signal과 blocking defect를 분리 |
| Review capacity blocked state | 채택 | ratified capacity를 초과하거나 required review가 미완료면 `blocked_review_capacity` |
| Rule registry ratification | 채택 | defect/transformation registry를 hash-bound ratified input으로 포함하고 transform set을 closed set으로 유지 |
| Page/Layer 4 readiness boundary | 채택 | page/Layer 4 input은 optionality readiness 분기에만 사용하며 body disposition에는 사용 금지 |
| Acquisition denominator | 채택 | source-bound/current-expressed/successor-projected set을 분리하고 source-bound proposition conservation을 검증 |
| Evaluator regression | 채택 | generic evaluator 변경 시 existing subject canonical result regression `0` 필수 |
| Closeout token | 채택 | `layer3_role_realign_staging_complete`처럼 scope를 token 자체에 포함 |
| Problem 1 equivalence | 채택 | exact authority identity만 허용; 대안은 별도 hash-bound equivalence decision이 있어야 함 |
| Tooling allowlist | 채택 | 새 tool/test/dependency의 current-route/full-gate role을 terminal freeze 전에 explicit disposition |
| Clean-Checkout durable pointer | 채택 | terminal subject에는 pre-run external retrieval contract만 포함; result hash pointer는 post-validation evidence-only successor이며 validated subject가 아님 |
| Review completion semantics | 채택 | review 수행 완료와 semantic resolution을 분리; 근거 있는 `review_hold/review_required` 유지도 completed review로 인정 |
| Current-route manifest condition | 채택 | staging/adoption label이 아니라 actual required-dependency disposition에 따라 terminal freeze 전 additive update |
| Menu flat projection | 채택 | canonical acquisition 보존 set과 Menu public set을 분리하고 core/acquisition 존재 조합별 flat rule 및 신규 표면화 branch를 ratify |
| Defect/transformation content | 채택 | 로드맵의 다섯 bounded transform과 최소 defect family를 proposal로 명시 |
| Candidate replay identity | 채택 | artifact class별 byte parity와 canonical semantic-projection parity를 사전 고정; 실행 후 완화 금지 |
| Registry Authority non-claim | 채택 | staging closeout 비주장 목록에 Registry Authority PASS 추가 |

Clean-Checkout 판정 근거는 `docs/DECISIONS.md`의 current contract다. 이 계약은 full-repository PASS를 exact tracked subject에 결속하고 repository HEAD가 바뀌면 predecessor PASS 상속을 금지한다. 따라서 staging candidate 자체가 off-live라는 사실은 Change 1~8의 tracked code/test/policy/config/docs 변경에 대한 repository terminal gate를 면제하지 않는다.

---

## 2. Scope

다음을 구현 범위로 한다.

- execution-time `item_denominator`, `existing_body_denominator`와 source/rendered/runtime identity materialization
- Problem 1 Layer 3 optionality 결과의 exact identity binding과 fail-closed prerequisite gate
- body disposition vocabulary와 full coverage ledger
- description readiness vocabulary와 full item coverage ledger
- 로드맵의 closed fact-kind vocabulary와 current source slot/provenance 사이의 명시적 mapping contract
- registered duplicate, redundant structure, template/skeleton, awkward-expression, identity/classification repetition rule registry
- exact duplicate deterministic detection과 ratified registered rule 기반의 별도 blocking classification
- stale-safe, exact-input-bound human exception ledger
- core description / acquisition information 분리와 fact-preservation receipt
- canonical DVF composition 경로를 재사용하는 off-live successor compiler
- reusable IAR public-text assessment와 successor-specific regression rule 연결
- Problem 5A candidate projection
- candidate replay A/B deterministic regeneration과 current-vs-staging delta
- exact tracked staging terminal subject의 mandatory full-repository Clean-Checkout Run A/B, denominator/dependency/result parity와 source-checkout non-mutation
- current/historical/diagnostic route 및 predecessor evidence 비변경 검증
- 정책 채택 시 `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`의 additive alignment

### Explicitly Out Of Scope

- default execution에서 current Layer 3 generation, runtime Lua chunk 또는 package payload 교체
- Tooltip UI 구현, 두 번째/세 번째 줄 binding, 최대 4줄 layout, width 또는 wrapping 변경
- Browser, Wiki, Menu, Detail의 대규모 UI redesign
- Layer 4 Recipe / Right-click extraction, coverage 또는 presentation 변경
- Layer 4 use_case를 새 Layer 3 fact로 승격하는 작업
- 새로운 game fact, 외부 wiki fact 또는 Evidence Allowlist 추가
- taxonomy, Source/Outcome model 또는 1~5 Layer responsibility redesign
- 모든 item의 장문 설명 작성 또는 모든 item에 Layer 3 body 강제 생성
- semantic similarity, embedding 또는 LLM quality classifier 도입
- package publication, Workshop publication, release 또는 B42 readiness
- unrelated Iris refactor, repository 경량화 또는 performance optimization
- multiplayer, long-session 및 external-mod compatibility 전수 검증

---

## 3. Non-Goals

- 기존 body를 더 길게 만드는 것을 성공 기준으로 삼지 않는다.
- character, sentence 또는 token count를 core-description eligibility나 품질 하한으로 사용하지 않는다.
- item name, classification 또는 rendered body 문자열을 비교해 새로운 의미가 있는지 추론하지 않는다.
- acquisition-only 정보를 core description으로 포장하지 않는다.
- Layer 4 richness를 Layer 3 suitability의 대체 지표로 사용하지 않는다.
- `검토 필요`를 `설명 재료 부족` 또는 Problem 5A candidate로 자동 변환하지 않는다.
- human exception을 새 fact, 자유로운 rewrite 권한 또는 shadow policy로 사용하지 않는다.
- candidate generation, public-text assessment, IAR adoption, runtime compatibility와 release readiness를 하나의 PASS로 합치지 않는다.
- predecessor artifact, 실패 evidence 또는 이전 exception을 successor에 맞춰 수정하지 않는다.
- 계획 작성 시 관찰한 `2,285 / 2,105 / 2,084 / 21` 수치를 실행 시 denominator 상수로 하드코딩하지 않는다.

---

## 4. Assumptions

### Codebase Inspection Summary

- `Iris/input/items_itemscript.json`은 계획 작성 시 case-sensitive FullType `2,285`개를 가진다. Windows의 case-insensitive map 동작을 authoritative census에 사용하지 않는다.
- `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`은 current facts와 decisions 각각 `2,105`개 row를 결속한다.
- `Iris/build/description/v2/output/dvf_3_3_rendered.json`은 `2,105`개 entry 중 `2,084`개 `text_ko`와 `21`개 `text_ko=null` entry를 가진다. 실행 시 `existing_body_denominator`는 실제 non-empty current body set에서 다시 계산한다.
- current fact slot 관찰값은 `identity_hint=2,105`, `primary_use=2,030`, `acquisition_hint=1,050`, `special_context=12`다. `secondary_use`, `processing_hint`, `limitation_hint`, `notes`는 현재 non-empty row가 없다.
- current flat body 중 literal `획득 방법:` block을 가진 body는 계획 작성 시 `284`개다. 이는 전체 acquisition fact coverage를 뜻하지 않으며 분리 구현은 label string parsing이 아니라 source proposition/slot binding을 사용해야 한다.
- current rendered text에는 계획 작성 시 exact duplicate text group `232`개, 해당 group 소속 row `1,594`개가 관찰된다. 이 수치는 audit signal이며 registered rule 및 provenance 판정 전에는 자동 defect count가 아니다.
- `fact_origin.primary_use`는 계획 작성 시 `cluster_summary=1,275`, `identity_fallback=718`, `role_fallback=100`, `direct_use=12`다. 특히 `cluster_summary`는 existing approved Layer 3 lineage인지 exact authority binding을 확인한 뒤에만 입력으로 유지하며, 이번 작업에서 새로운 Layer 4 → Layer 3 승격을 만들지 않는다.
- current facts와 latest staging proposition inventory는 `identity/use/acquisition/food_semantic/context` role을 제공하지만 로드맵의 `target/action/result/consumption_or_retention/condition/restriction`을 current canonical fact-kind로 직접 제공하지 않는다. `primary_use` prose를 파싱해 이 세부 kind를 추정하는 것은 금지한다.
- non-empty current slot의 planning-time provenance 조합은 `identity_hint × seed`, `acquisition_hint × seed`, `primary_use × cluster_summary/direct_use/identity_fallback/role_fallback`, `special_context × origin_missing`과 structured food-semantic lineage다. `fact_origin` field가 존재한다는 이유만으로 null slot까지 mapping coverage에 포함하거나 eligibility를 부여하지 않는다.
- latest `source_proposition_inventory.jsonl`과 `body_plan_requirement_inventory.jsonl`은 naturalization staging 경로에 있으며 current input manifest의 직접 source path가 아니다. exact source identity와 derivation을 재구축하지 않고 current authority처럼 소비하지 않는다.
- new inventory의 scalar fact ID는 ratified deterministic algorithm으로 current `item_id + source_slot + source_value_hash + fact_origin`에서 파생하고 derivation trace를 남긴다. 이 derived ID는 source authority를 새로 만들지 않으며 latest naturalization staging proposition ID를 current처럼 복사하지 않는다.
- current `compose_layer3_body_profile.py`는 `identity_core`, `use_core`, `context_support`, `limitation_support`, `acquisition_support`를 한 body plan에서 조합하고, `compose_layer3_item.py`는 acquisition proposition 앞에 paragraph split을 적용해 flat `text_ko`를 만든다.
- current runtime manifest는 `2,105`개 entry를 `11`개 chunk로 투영한다. `layer3_renderer.lua`는 body를 생성·수정하지 않고 `text_ko`가 없거나 lookup miss이면 `nil`로 침묵하므로 Layer 3 absence의 표시 기반은 이미 존재한다.
- current runtime vocabulary는 `adopted / unadopted`이며 body disposition의 `숨김`과 같은 의미가 아니다. successor offline disposition을 이 vocabulary로 재사용하지 않는다.
- `IrisTooltipSummary.lua`와 `IrisAltTooltip.lua`는 현재 classification tag, Recipe/Moveables/Fixing 연결, use-case count와 Menu 안내를 소비하며 Layer 3 description 또는 acquisition projection을 소비하지 않는다. 따라서 이번 staging closeout은 Tooltip input readiness이며 Tooltip completion이 아니다.
- `iar_public_text_assessment.py`는 subject finding과 technical failure를 분리하는 reusable assessment component다. 새 rule adapter는 이 component를 재사용하되 기존 naturalization PASS를 successor에 상속하지 않는다.
- current canonical docs에는 historical `docs/dvf_3_3_body_role_policy.md`와 `docs/dvf_3_3_body_role_execution_plan.md`이 존재하지 않는다. 삭제된 historical 문서를 current authority로 복원하거나 참조하지 않고 새 successor policy를 명시적으로 ratify한다.
- 현재 작업 트리의 `docs/새 폴더/iris_item_page_information_sufficiency_plan.md`는 Layer 3 requiredness/optionality를 다루는 선행 계획이지만 계획 문서 자체는 adopted authority가 아니다. 이 physical path는 planning-time observation일 뿐 canonical location을 승인하지 않는다. 실행은 `problem1_authority_binding.json`에 exact path/hash로 결속된 owner-ratified policy/result identity를 요구한다. 다른 authority를 동등하다고 취급하려면 별도 owner-ratified `problem1_equivalence_decision.json`이 두 exact identity와 허용 범위를 hash-bound로 선언해야 한다.
- `docs/DECISIONS.md`의 current repository validation contract는 terminal PASS를 exact tracked subject에만 귀속하고 후속 HEAD 상속을 금지한다. 따라서 Change 1~8 tracked terminal subject의 `layer3_role_realign_staging_complete`에도 canonical full-repository Clean-Checkout Run A/B가 필요하다.

### Repository and Environment Assumptions

- authority 해석 순서는 `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`다.
- Python 명령은 Windows PowerShell에서 `uv run python -B <script>` 또는 `uv run python -B -m pytest ...`로 실행한다.
- Lua syntax validation은 `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`를 사용한다.
- JSON/JSONL은 strict UTF-8, duplicate-key rejection, case-sensitive FullType, deterministic ordering과 canonical hash를 사용한다.
- primary working tree에는 사용자 변경이 존재할 수 있으므로 generation, replay와 full validation은 isolated output root 또는 disposable clean checkout에서 수행한다.
- planning-time count와 hash는 관찰값이다. 모든 authority identity와 denominator는 execution 시작 시 다시 계산해 input manifest에 봉인한다.

### Authority and Ratification Assumptions

구현 전 다음 단일 policy ratification contract를 owner가 봉인한다. ratification 전에는 read-only census, current identity inventory, proposal packet과 protected-surface baseline만 생성할 수 있다.

| ID | Ratification subject | 계획상 proposal |
|---|---|---|
| `L3R-RAT-01` | execution closeout | default `staging_only`; current adoption은 별도 authorization |
| `L3R-RAT-02` | Problem 1 dependency | exact adopted requiredness/optionality policy와 result identity 필수 |
| `L3R-RAT-03` | denominator | item=`items_itemscript.json` exact FullType set; existing body=current non-empty Layer 3 text set |
| `L3R-RAT-04` | disposition/readiness vocabulary | 로드맵의 각 5개 state를 closed enum으로 채택 |
| `L3R-RAT-05` | fact-kind mapping | 최소 `(source_slot, fact_origin)` key, structured lineage 추가 key; closed 10-kind vocabulary; observed non-empty 조합 unresolved `0`; prose parsing 금지 |
| `L3R-RAT-06` | artifact/Menu projection | canonical role-material record + four-case Menu flat rule + acquisition publicity branch; current facade는 adoption 전 불변 |
| `L3R-RAT-07` | Tooltip boundary | `core_description` / `acquisition_information` input readiness까지만 봉인 |
| `L3R-RAT-08` | existing cross-layer lineage | exact prior Layer 3-approved provenance만 eligible; 신규 승격 0 |
| `L3R-RAT-09` | hide representation | offline disposition으로만 기록; `adopted/unadopted` 의미 재사용 금지 |
| `L3R-RAT-10` | human exception | exact input/policy/rule hash binding, fact addition 금지, stale 시 re-review |
| `L3R-RAT-11` | rule/public assessment gate | exact defect/transformation registry hashes, five-transform minimum proposal, closed transform set, duplicate signal/blocking 분리와 bounded manual review |
| `L3R-RAT-12` | conditional current adoption | 별도 execution authorization, IAR transaction과 clean-checkout Run A/B 필수 |
| `L3R-RAT-13` | review capacity | exact capacity/partition contract; review record 미완료 또는 capacity 초과 시 `blocked_review_capacity`; legitimate review state 유지 허용 |
| `L3R-RAT-14` | acquisition conservation | source-bound acquisition proposition set을 conservation denominator로 사용; current 표현과 successor projection은 별도 set |
| `L3R-RAT-15` | tooling disposition | 모든 새 tool/test/direct dependency의 current-route/full-gate role을 explicit/hash-bound로 분류 |
| `L3R-RAT-16` | Clean-Checkout evidence pointer | pre-run retrieval contract와 post-validation evidence-only result carrier 분리; result carrier는 validated subject 아님 |
| `L3R-RAT-17` | candidate replay identity | artifact별 `byte_exact` 또는 `canonical_semantic_projection` class와 excluded run-local field를 실행 전 봉인 |

위 proposal table은 plan review용이다. 실행 authority는 exact hash가 기록된 하나의 `policy_ratification_contract.json`만 가진다.

#### Minimum Fact-Kind Mapping Proposal

`L3R-RAT-05`와 `L3R-RAT-08`은 최소 다음 mapping을 output distribution을 보기 전에 함께 ratify한다. `description_eligible`은 fact kind 자체와 분리된 effect다.

| Source key | Proposed outcome | Fact kind | Description effect | Additional gate |
|---|---|---|---|---|
| `identity_hint × seed` | `eligible_kind` | `identity` | false | non-empty exact source binding |
| `acquisition_hint × seed` | `eligible_kind` | `acquisition` | false | acquisition projection eligible |
| `primary_use × identity_fallback` | `not_eligible` | none | false | identity fact는 `identity_hint`에서만 유지 |
| `primary_use × role_fallback` | `eligible_kind` | `role` | true | non-empty exact origin binding |
| `primary_use × direct_use` | `eligible_kind` | `role` | true | `action/result/target` 세분화 금지 |
| `primary_use × cluster_summary × layer3_approval_bound` | `eligible_kind` | `role` | true | exact existing Layer 3 facts-authority/adoption lineage 필요 |
| `primary_use × cluster_summary × layer3_approval_unbound` | `review_required` | none | false | 신규 Layer 4 승격 금지 |
| `special_context × origin_missing` | `review_required` | none | false | explicit provenance successor 없이는 eligibility 금지 |
| food `consumption_form` | `eligible_kind` | `consumption_or_retention` | true | approved structured lineage |
| food `meal_role` | `eligible_kind` | `role` | true | approved structured lineage |
| food `culinary_role` | `eligible_kind` | `role` | true | approved structured lineage |
| food `preparation_requirement` | `eligible_kind` | `condition` | true | approved structured lineage |
| food `preservation_form` | `eligible_kind` | `condition` | true | approved structured lineage |
| food `preparation_state` | `eligible_kind` | `condition` | true | approved structured lineage |

이 표는 prose 의미를 읽지 않고 current provenance/structured axis만 사용한다. execution census에서 새 origin, food axis, authority state 또는 lineage shape가 발견되면 default mapping을 적용하지 않고 `blocked_mapping_contract`로 닫는다. `cluster_summary`의 `layer3_approval_bound`는 current facts path에 존재한다는 사실만으로 참이 되지 않으며 exact adoption/source-lineage binding을 검증해야 한다.

#### Minimum Menu Flat Projection Proposal

`L3R-RAT-06`은 canonical role-material 보존과 Menu 공개를 서로 다른 축으로 ratify한다.

```text
canonical_acquisition_material_set
!= menu_public_acquisition_set
```

- canonical role-material은 `source_acquisition_fact_denominator` 전부를 보존한다.
- Menu public acquisition branch의 기본 proposal은 `preserve_current_publicity`다. predecessor trace로 current 표현이 확인된 fact만 flat Menu에 싣고 `unknown_current_expression`이나 current-unexpressed fact는 canonical material에만 보존한다.
- owner가 `surface_all_confirmed`를 선택하려면 같은 ratification contract에 explicit branch, newly surfaced fact ID set/hash와 public delta review requirement를 기록한다. 실행 결과를 본 뒤 branch를 바꾸지 않는다.
- `core_description`과 `menu_public_acquisition_set`의 flat projection은 다음 four-case total function을 사용한다.

| Core description | Public acquisition | Derived Menu `text_ko` proposal |
|---|---|---|
| present | present | core paragraph + blank line + registered acquisition label/section |
| present | absent | core paragraph only |
| absent | present | registered acquisition-only label/section; core description을 합성하지 않음 |
| absent | absent | `null`; Layer 3 renderer silence |

acquisition-only flat text는 transport compatibility projection일 뿐 `description_ready`나 core Layer 3 body로 계산하지 않는다. projector는 exact registered label/template와 source-bound fact order만 사용하고 runtime summarization을 하지 않는다. current-to-successor report는 `repositioned_acquisition_fact_set`, `newly_surfaced_acquisition_fact_set`, `preserved_nonpublic_acquisition_fact_set`을 별도 count/hash로 기록한다.

#### Minimum Defect and Transformation Registry Proposal

`L3R-RAT-11`은 다음 다섯 transformation만 initial closed set으로 제안한다. owner가 다른 transform을 원하면 execution 전에 additive ratification successor를 만든다.

| Transform ID | Allowed operation | Fail-closed precondition |
|---|---|---|
| `separate_acquisition_role_v1` | acquisition clause를 core에서 제거하고 acquisition material로 이동 | same source fact IDs의 lossless transfer |
| `remove_exact_identity_classification_repetition_v1` | exact registered identity/classification 반복 clause 제거 | source slot/rule exact match; semantic similarity 금지 |
| `replace_registered_skeleton_v1` | registered bad skeleton을 registered successor skeleton으로 교체 | exact rule/template ID와 capture-slot binding |
| `place_confirmed_fact_frame_v1` | confirmed fact fragment를 fact-kind별 registered frame에 배치 | source fragment byte/value hash 보존; 새 proposition 금지 |
| `delete_exact_duplicate_clause_v1` | 같은 proposition/fact ID set을 가진 중복 clause 하나 제거 | text-only equality로 differing fact set 삭제 금지 |

initial defect registry proposal은 다음 family를 분리한다.

- exact duplicate detector signal
- registered bad duplicate blocking rule
- same text / differing consumed fact-set inconsistency
- registered identity/classification repetition
- registered bad skeleton/template
- registered awkward-expression family
- description/acquisition cross-role leakage
- unregistered high-frequency skeleton advisory signal

각 rule은 exact matcher, severity, allowed transform IDs, source/proposition requirements와 positive/negative fixtures를 가진다. unrestricted rewrite, free-form template substitution과 unregistered transform은 허용하지 않는다.

---

## 5. Repository Areas Affected

### Code

- `Iris/build/description/v2/tools/build/layer3_body_role_realign.py` (new; pure decision/projection core)
- `Iris/build/description/v2/tools/build/run_layer3_body_role_realign.py` (new; isolated staging runner)
- `Iris/build/description/v2/tools/build/validate_layer3_body_role_realign.py` (new; read-only validator)
- `Iris/build/description/v2/tools/build/compose_layer3_role_material.py` (new; canonical role-material compiler helper)
- `Iris/build/description/v2/tools/build/compose_layer3_text.py` (candidate-mode integration only; default current path byte-preserved)
- `Iris/build/description/v2/tools/build/compose_layer3_item.py` (candidate-mode delegation only; current compose behavior preserved)
- `Iris/build/description/v2/tools/build/iar_public_text_assessment.py` (새 subject adapter가 필요한 최소 확장만)
- `Iris/build/description/v2/tests/test_layer3_body_role_realign.py` (new)
- `Iris/build/description/v2/tests/fixtures/layer3_body_role_realign/**` (new)
- `Iris/build/description/v2/tools/build/INVENTORY.md` (new entrypoint/role 기록)

다음 runtime/producer surface는 staging-only execution에서 observation과 protected-hash comparison만 수행하고 수정하지 않는다.

- `Iris/build/description/v2/tools/build/compose_layer3_body_profile.py`
- `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunkIndex.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/**`
- `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua`
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua`
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`

조건부 current-adoption follow-up에서만 `export_dvf_3_3_lua_bridge.py`, runtime projection과 관련 compatibility test 변경을 연다.

### Docs

- `docs/iris_layer3_body_role_realignment_policy.md` (new; ratification 시)
- `docs/iris_layer3_body_role_realignment_menu_tooltip_core_description_readiness_plan.md` (이 계획)
- `docs/DECISIONS.md` (policy/adoption 시 additive decision)
- `docs/ARCHITECTURE.md` (role material과 producer/IAR/runtime flow 정렬)
- `docs/ROADMAP.md` (scoped status, non-claim과 후속 5A handoff)

`docs/Philosophy.md`는 수정하지 않는다.

### Config

- `Iris/build/description/v2/data/layer3_body_role_realign/proposals/<proposal_sha256>/*.proposal.json` (new)
- `Iris/build/description/v2/data/layer3_body_role_realign/policy_ratification_contract.json` (new)
- `Iris/build/description/v2/data/layer3_body_role_realign/problem1_authority_binding.json` (new)
- `Iris/build/description/v2/data/layer3_body_role_realign/problem1_equivalence_decision.json` (new only if an alternate exact authority is selected)
- `Iris/build/description/v2/data/layer3_body_role_realign/fact_kind_mapping_contract.json` (new)
- `Iris/build/description/v2/data/layer3_body_role_realign/disposition_readiness_contract.json` (new)
- `Iris/build/description/v2/data/layer3_body_role_realign/registered_defect_rules.json` (new)
- `Iris/build/description/v2/data/layer3_body_role_realign/transformation_rules.json` (new)
- `Iris/build/description/v2/data/layer3_body_role_realign/human_exception_ledger.jsonl` (new)
- `Iris/build/description/v2/data/layer3_body_role_realign/representative_cases.json` (new)
- `Iris/build/description/v2/data/layer3_body_role_realign/review_capacity_contract.json` (new)
- `Iris/build/description/v2/data/layer3_body_role_realign/tool_disposition_contract.json` (new)
- `Iris/build/description/v2/data/layer3_body_role_realign/candidate_replay_identity_contract.json` (new)
- `Iris/build/description/v2/data/layer3_body_role_realign/clean_checkout_external_evidence_location_contract.json` (new; pre-run retrieval coordinate/schema only, no result hash)
- `Iris/_docs/authority/iris_current_authority_manifest.json` (ratified policy와 artifact role의 additive classification)
- `Iris/_docs/round3/current_route_required_validations.json` (staging/adoption label이 아니라 actual required-dependency disposition에 따라 필요한 경우 terminal freeze 전에 additive update)

### Generated Artifacts

- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase0/input_identity_manifest.json`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase1/item_denominator.jsonl`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase1/existing_body_denominator.jsonl`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase2/fact_composition_inventory.jsonl`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase2/fact_kind_mapping_coverage.json`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase3/body_disposition_ledger.jsonl`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase3/description_readiness_ledger.jsonl`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase3/review_queue.jsonl`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase4/role_material_by_fulltype.jsonl`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase4/acquisition_preservation_report.json`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase4/acquisition_projection_ledger.jsonl`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase5/successor_rendered.json`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase5/current_vs_successor_delta.jsonl`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase6/public_text_assessment_input.json`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase6/public_text_assessment_result.json`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase7/candidate_replay_determinism_report.json`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase7/protected_surface_non_mutation_report.json`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase8/problem_5a_candidate_set.jsonl`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase8/terminal_validation_report.json`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase8/tool_dependency_disposition_report.json`
- `Iris/build/description/v2/staging/layer3_body_role_realign/<run_id>/phase8/clean_checkout_terminal_subject_binding.json`
- repository-external canonical Clean-Checkout Run A/B receipts와 deterministic comparison receipt
- pre-run tracked `clean_checkout_external_evidence_location_contract.json` (external retrieval coordinate, schema와 containment contract; result identity 없음)
- `Iris/_docs/round3/layer3_body_role_realign/evidence_carriers/<carrier_id>/clean_checkout_result_pointer.json` (post-validation evidence-only successor의 Run A/B/comparator result hashes; validated terminal subject에 포함하지 않음)
- `Iris/_docs/round3/layer3_body_role_realign/<subject_sha256>/independent_review.json` (governance가 요구할 때)
- `Iris/_docs/round3/layer3_body_role_realign/<subject_sha256>/owner_seal.json` (governance가 요구할 때)
- `Iris/_docs/round3/layer3_body_role_realign/<subject_sha256>/axis_qualified_closeout.json`

Generated staging artifact는 facts, decisions, rendered current, runtime 또는 package authority가 아니며 reverse-merge input으로 사용할 수 없다.

---

## 6. Planned Changes

### Change 1 — Execution Contract, Problem 1 Gate and Denominator Lock

Purpose:

current subject와 실행 가능한 정책 범위를 먼저 고정해 historical/staging artifact 혼입, denominator substitution과 optionality 추정을 차단한다.

Files:

- `policy_ratification_contract.json`
- `run_layer3_body_role_realign.py`
- `input_identity_manifest.json`
- `item_denominator.jsonl`
- `existing_body_denominator.jsonl`

Implementation Notes:

- current item universe는 `items_itemscript.json`의 exact case-sensitive FullType set에서 생성한다.
- existing body universe는 current rendered entry 중 non-empty `text_ko` set으로 생성하고 current source/decisions/runtime set과 차이를 별도 기록한다.
- facts, decisions, profiles, overlay, rendered, runtime chunk manifest/index, Problem 1 result, policy/rules/exception identities를 SHA-256으로 봉인한다.
- `problem1_authority_binding.json`은 exact ratified policy/result path, raw hash, semantic result hash와 lifecycle state를 요구한다. alternate authority는 explicit `problem1_equivalence_decision.json` 없이는 허용하지 않는다.
- Problem 1 result가 없거나 proposal/unratified/stale 상태면 `설명 생략 가능`과 `설명 재료 부족`을 추정하지 않고 policy-dependent phases를 중단한다.
- pre-ratification runner는 read-only inventory 이외의 candidate generation을 거부한다.

Validation:

- duplicate/case-collision/missing FullType fail-close
- item/body denominator exact set and count receipt
- current/staging/historical path-role classification
- missing or unratified Problem 1 negative fixture
- missing/stale/implicit Problem 1 equivalence negative fixture
- protected current source/rendered/runtime baseline hash

---

### Change 2 — Fact-Kind Mapping and No-Inference Contract

Purpose:

문장 인상이나 flat rendered text가 아니라 confirmed source slot, provenance와 explicit registration으로 disposition/readiness 입력을 구성한다.

Files:

- `fact_kind_mapping_contract.json`
- `layer3_body_role_realign.py`
- `fact_composition_inventory.jsonl`
- mapping fixtures

Implementation Notes:

- closed vocabulary는 `identity`, `classification`, `acquisition`, `role`, `target`, `action`, `result`, `consumption_or_retention`, `condition`, `restriction`만 허용한다.
- scalar current source slot의 mapping key는 최소 `(source_slot, fact_origin)`이다. structured proposition은 여기에 `authority_class`, `authority_state`, `fact_axis`, lineage/mapping identity를 추가해 key를 좁힌다.
- mapping outcome은 `eligible_kind`, `not_eligible`, `review_required` 중 정확히 하나다. `eligible_kind`만 closed fact-kind 하나와 description/acquisition eligibility effect를 가질 수 있다.
- current source slot은 exact registered mapping이 있을 때만 fact kind를 갖는다. 예를 들어 `identity_hint × seed -> identity`, `acquisition_hint × seed -> acquisition`은 direct proposal이 가능하지만 free-form `primary_use`를 자동으로 `role/action/result/target`으로 분해하지 않는다.
- 최소 census 대상은 `primary_use × cluster_summary`, `primary_use × identity_fallback`, `primary_use × role_fallback`, `primary_use × direct_use`, `identity_hint × seed`, `acquisition_hint × seed`, `special_context × origin_missing`과 structured food-semantic proposition이다.
- execution input의 모든 non-empty source/origin/structured-lineage 조합은 policy-dependent disposition 전에 mapping row를 가져야 하며 unresolved mapping count는 `0`이어야 한다. 새 조합은 분포를 계산한 뒤 사후 분류하지 않고 execution을 중단해 policy successor를 요구한다.
- structured food-semantic proposition처럼 current authority가 이미 axis/value/lineage를 봉인한 경우에만 registered mapping을 적용한다.
- `cluster_summary`는 exact existing Layer 3-approved lineage가 확인된 row만 후보 입력으로 유지한다. Layer 4 output 또는 text similarity를 새 source로 읽지 않는다.
- unmapped, ambiguous, missing provenance, stale hash는 `review_required` reason을 생성하며 fallback description을 만들지 않는다.
- per-item inventory는 fact identity, kind, source path/field, provenance, authority hash, mapping rule과 eligibility를 남긴다.
- scalar source fact identity는 current fact row에서 결정론적으로 재구성하고 structured proposition은 existing proposition/lineage ID를 보존한다. 두 identity family를 같은 namespace로 암묵 병합하지 않는다.

Validation:

- closed vocabulary enforcement
- observed non-empty `(source_slot, fact_origin)` and structured-lineage coverage 100%, unresolved mapping 0
- rendered-string semantic parsing path 0
- unsupported source path 0
- unbound `primary_use` 세분화 negative fixture
- stale/missing provenance fail-close
- new Layer 4 promotion count 0

---

### Change 3 — Disposition, Readiness, Registered Rules and Human Exceptions

Purpose:

body disposition과 item readiness를 독립적인 total function으로 구현하고 기계 규칙과 human judgment의 경계를 명시한다.

Files:

- `disposition_readiness_contract.json`
- `registered_defect_rules.json`
- `transformation_rules.json`
- `human_exception_ledger.jsonl`
- `body_disposition_ledger.jsonl`
- `description_readiness_ledger.jsonl`
- `review_queue.jsonl`

Implementation Notes:

- disposition enum은 `keep / reduce / revise / hide / review_hold`이며 Korean public label은 `유지 / 축소 / 수정 / 숨김 / 검토 보류`다.
- readiness enum은 `description_ready / acquisition_only / omission_allowed / insufficient_material / review_required`이며 Korean report label은 로드맵의 5개 상태다.
- every existing body는 exactly one disposition, every canonical item은 exactly one readiness를 가져야 한다.
- `identity + classification + acquisition`만 있는 composition은 description-ready가 아니다.
- description eligibility는 registered confirmed kind 중 `role/target/action/result/consumption_or_retention/condition/restriction` 하나 이상이 있을 때만 열리며 public acceptance는 별도다.
- exact duplicate detection 자체는 deterministic audit signal이다. blocking은 exact duplicate가 ratified bad-duplicate rule과 일치하거나, 동일 text가 서로 다른 consumed fact-set/proposition-set을 은폐하거나, 별도 explicit eligibility violation이 있을 때만 발생한다. 동일 confirmed fact set의 동일 text는 자동 defect가 아니다.
- registered defect와 transformation registry는 policy ratification contract에 exact hash로 결속한다. transformation registry는 closed set이며 unregistered transform 적용은 즉시 실패한다.
- 새 high-frequency skeleton은 advisory review signal이며 ratified successor rule 없이는 즉시 blocking rule로 승격하지 않는다.
- exception은 `item_id`, input fact identity, predecessor body identity, policy/rule identity, decision, reason, reviewer/owner identity와 expiry/revalidation condition을 요구한다.
- exception은 새 fact나 source text를 포함할 수 없고 input identity가 바뀌면 자동 invalidation한다.
- page-level/Layer 4 information은 exact Problem 1 binding이 허용하는 `omission_allowed` 대 `insufficient_material` readiness 분기에만 입력될 수 있다. Layer 4 presence, count, richness 또는 page sufficiency는 body disposition, core-description eligibility나 public-text quality의 입력이 아니다.
- required manual-review universe와 partition/capacity는 `review_capacity_contract.json`에 봉인한다. 여기서 review completion은 eligible reviewer가 bound subject를 실제 검토하고 decision/reason/next-condition record를 남겼다는 뜻이며 semantic resolution을 강제하지 않는다. 검토 결과가 근거 있는 `review_hold` 또는 `review_required` 유지여도 review는 completed일 수 있다. review record가 누락되거나 ratified capacity ceiling을 넘어 required review를 수행하지 못하면 closeout은 `blocked_review_capacity`이며 PASS/partial success로 표현하지 않는다.

Validation:

- disposition/readiness completeness and exclusivity
- unknown enum/reason/rule rejection
- identity/classification/acquisition-only fixtures
- page/Layer 4 input이 readiness에만 영향을 주고 disposition에는 영향을 주지 않는 paired fixture
- short valid role fixture가 길이 때문에 제거되지 않음
- high-frequency unregistered skeleton이 auto-hide되지 않음
- exact duplicate signal/non-blocking, registered-bad duplicate, differing-consumed-fact-set blocking fixtures
- unregistered transformation rejection
- stale exception rejection and deterministic replay
- review capacity exceeded/incomplete negative fixtures
- completed review가 legitimate `review_hold/review_required`를 유지하는 positive fixture

---

### Change 4 — Core Description / Acquisition Separation

Purpose:

동일한 confirmed fact set에서 Menu와 future Tooltip이 독립적으로 소비할 role-labeled material을 만들고 acquisition fact loss를 차단한다.

Files:

- `compose_layer3_role_material.py`
- `compose_layer3_item.py`
- `role_material_by_fulltype.jsonl`
- `acquisition_preservation_report.json`

Implementation Notes:

- canonical staging record는 최소 `item_id`, `core_description`, `acquisition_information`, source proposition IDs, transformation trace와 readiness/disposition reference를 가진다.
- `core_description`은 eligible description fact만 사용한다. acquisition clause를 빈 description 대신 합성하지 않는다.
- `acquisition_information`은 source-bound acquisition propositions만 사용하며 description이 없더라도 독립적으로 보존한다.
- `source_acquisition_fact_denominator`는 current exact source row에서 ratified ID algorithm으로 파생된 non-empty, mapping-eligible acquisition fact ID set이다. current structured proposition ID가 있는 경우에는 그 ID를 보존한다. label scan, latest staging inventory 또는 current body 표현 여부를 denominator로 사용하지 않는다.
- `current_expressed_acquisition_set`은 predecessor source-to-render trace로 확인되는 proposition ID만 기록한다. trace가 없으면 `unknown_current_expression`으로 남기며 `획득 방법:` lexical match를 authority로 사용하지 않는다.
- `successor_projected_acquisition_set`은 `acquisition_information`이 실제 소비한 proposition ID set이다. conservation PASS는 successor set이 source denominator를 누락 없이 포함하고 unknown/unbound/additional proposition이 `0`일 때만 허용한다.
- `successor_menu_public_acquisition_set`은 `L3R-RAT-06`의 preselected publicity branch가 flat Menu에 실제 포함한 fact ID set이다. canonical conservation PASS와 Menu public coverage를 같은 count로 합치지 않는다.
- Menu flat projection은 Minimum Menu Flat Projection Proposal의 four-case total function을 사용한다. core+acquisition, core-only, acquisition-only와 both-absent를 각각 결정론적으로 처리하며 acquisition-only를 core description으로 합성하지 않는다.
- `preserve_current_publicity`가 기본 proposal이고 `surface_all_confirmed` 선택 시 newly surfaced fact ID set/hash와 bounded public delta review를 요구한다. predecessor `text_ko`를 semantic reverse parsing해 두 field로 나누지 않는다.
- exact Tooltip line assignment는 artifact에 기록하지 않는다. 각 field의 role만 봉인한다.
- disposition/reason/readiness 같은 internal governance field는 user-facing text에 포함하지 않는다.

Validation:

- source-bound acquisition denominator, current-expressed set, unknown-current-expression set과 successor-projected set 별도 count/hash
- successor Menu-public, repositioned, newly-surfaced와 preserved-nonpublic acquisition set 별도 count/hash
- `source_acquisition_fact_denominator - successor_projected_acquisition_set = 0`
- successor unbound/additional acquisition proposition 0
- Menu four-case projection fixtures와 selected publicity branch exact-set fixture
- acquisition-to-description leakage 0
- description-to-acquisition substitution 0
- role material source/provenance coverage
- description absent + acquisition present, both absent, description present + acquisition absent fixtures
- internal state vocabulary public-text leakage 0

---

### Change 5 — Canonical Staging Successor Compilation

Purpose:

DVF System의 single-writer 경계를 지키면서 disposition과 separated material로 successor body candidate를 off-live에서 생성한다.

Files:

- `compose_layer3_text.py`
- `compose_layer3_item.py`
- `compose_layer3_role_material.py`
- `successor_rendered.json`
- `current_vs_successor_delta.jsonl`

Implementation Notes:

- existing compose entrypoint에 explicit `role_realign_staging` context를 추가하고 default current composition의 input/output bytes와 behavior를 보존한다.
- direct editing of rendered JSON은 금지한다. 모든 successor text는 bound facts, policy, mapping, transformation과 exception으로 재생성한다.
- `keep/reduce/revise`는 각각 unchanged/registered reduction/rule-bounded revision trace를 요구한다.
- `hide`는 staging successor의 public body absence로 표현하되 offline reason은 ledger에 보존한다. current `unadopted` vocabulary로 자동 변환하지 않는다.
- `review_hold`는 public successor adoption 대상에서 제외하며 generic fallback을 만들지 않는다.
- predecessor identity, current-vs-successor row/field delta와 successor public-body denominator를 별도 산출한다.

Validation:

- default current compose byte parity
- no rendered direct-edit path
- every successor clause source-bound
- unsupported fact/fact strengthening 0
- hide/review-held item의 public candidate leakage 0
- successor denominator derived from dispositions, not fixed counts

---

### Change 6 — Public-Text Assessment and Bounded Review Closure

Purpose:

successor generation 성공과 public-text suitability를 분리하고 registered defect와 human-review 대상만 닫는다.

Files:

- `iar_public_text_assessment.py`
- `public_text_assessment_input.json`
- `public_text_assessment_result.json`
- review evidence under `Iris/_docs/round3/layer3_body_role_realign/**`

Implementation Notes:

- assessment subject는 exact successor text constituent identity, policy/ruleset, mapping과 source manifest에 결속한다.
- existing evaluator infrastructure를 재사용하되 predecessor result/PASS를 상속하지 않는다.
- `iar_public_text_assessment.py` 또는 generic runner/validator/contract를 변경하면 모든 existing required subject를 predecessor-bound input으로 재실행해 canonical finding/result identity regression `0`을 확인한다. 새 subject adapter는 기존 subject default behavior를 바꾸지 않는다.
- exact duplicate는 detector signal로만 수집한다. blocking metric은 ratified bad-duplicate rule, differing consumed fact/proposition set inconsistency, explicit eligibility violation, registered bad skeleton/awkward family와 known specimen regression에 한정한다.
- unregistered frequency signal은 review queue만 생성한다.
- manual review는 모든 `review_hold/review_required`, 모든 exception, registered rule의 representative sample과 current-vs-successor high-impact delta를 포함한다.
- machine result, independent review와 owner seal은 별도 axis로 기록한다.

Validation:

- subject finding / technical failure attribution separation
- evaluator input and result canonical hash
- known-bad positive and negative fixtures
- predecessor PASS inheritance 0
- existing required evaluator subject canonical result regression 0
- generic evaluator required dependency/current-route test PASS when evaluator surface changes
- unresolved blocking finding 0 before staging closeout
- review coverage and exception coverage report

---

### Change 7 — Deterministic Candidate Replay and Non-Mutation Proof

Purpose:

동일 입력에서 byte-identical successor를 독립 output root 두 곳에 재생성하고 current authority 비변경을 증명한다. 이 candidate replay A/B는 Change 8의 repository Clean-Checkout Run A/B와 다른 validation axis다.

Files:

- `run_layer3_body_role_realign.py`
- `validate_layer3_body_role_realign.py`
- `candidate_replay_identity_contract.json`
- `candidate_replay_determinism_report.json`
- `protected_surface_non_mutation_report.json`

Implementation Notes:

- candidate replay A와 B는 서로 다른 empty output root에서 동일한 sealed input을 소비한다.
- `candidate_replay_identity_contract.json`은 execution 전에 every output artifact를 `byte_exact` 또는 `canonical_semantic_projection` class로 닫고 projection schema/excluded fields를 hash-bound로 봉인한다. unclassified artifact count는 `0`이어야 한다.
- canonical JSON/JSONL/text candidate, ledgers, denominator, role material과 successor rendered처럼 deterministic serialization이 가능한 artifact는 `byte_exact`을 사용한다. UTF-8, LF, key/row order와 terminal newline까지 일치해야 하며 canonical hash equality도 함께 요구한다.
- timestamp, absolute path, random run ID, isolated output root처럼 허용된 run-local field를 가진 receipt/report만 `canonical_semantic_projection`을 사용할 수 있다. excluded field 목록과 projection algorithm은 contract에 사전 고정하며 semantic projection hash가 일치해야 한다.
- 실행 실패 후 artifact class를 `byte_exact`에서 canonical projection으로 완화하거나 excluded field를 추가하지 않는다. unknown/unexpected raw delta는 blocking이다.
- canonical artifact set, row order, counts, hashes와 final subject identity가 일치해야 한다.
- facts, decisions, profiles, overlay, current rendered, runtime chunk/index, classification, Layer 4 artifacts와 predecessor evidence의 before/after hash를 비교한다.
- source checkout residue와 partial staging generation을 terminal PASS로 인정하지 않는다.

Validation:

- every `byte_exact` artifact raw-byte parity + canonical hash parity
- every `canonical_semantic_projection` artifact bound semantic-projection hash parity
- unclassified artifact 0, post-run identity-class/exclusion amendment 0
- denominator/fact/disposition/readiness/5A set parity
- protected artifact mutation 0
- unexpected source checkout residue 0
- fail/retry/partial-output negative fixtures

---

### Change 8 — Problem 5A Projection, Tracked Subject Freeze and Staging Closeout

Purpose:

final readiness ledger에서 enrichment가 필요한 exact candidate set을 분리하고, 모든 tracked changes와 dependency disposition을 고정한 exact terminal subject에 mandatory full-repository Clean-Checkout Run A/B를 수행한 뒤 staging-only claim boundary를 닫는다.

Files:

- `problem_5a_candidate_set.jsonl`
- `terminal_validation_report.json`
- `tool_dependency_disposition_report.json`
- `clean_checkout_terminal_subject_binding.json`
- `axis_qualified_closeout.json`
- `docs/ROADMAP.md`

Implementation Notes:

- candidate set은 `readiness == insufficient_material`의 pure deterministic projection이다.
- `review_required`, `acquisition_only`, `omission_allowed`는 5A set에 포함하지 않는다.
- artifact는 source identities, readiness-ledger identity, item set hash와 projection rule ID를 기록한다.
- artifact 존재는 Problem 5A execution 또는 fact-enrichment authorization이 아니다.
- 모든 new/changed tool, test, config, policy, runner, validator와 direct dependency에 `required_tracked_source / dedicated_route_validation / historical_optional_evidence / not_required` 등 current contract가 허용하는 explicit role을 부여한다. 경로나 naming으로 current-route/full-gate 편입을 추정하지 않는다.
- 실제 required dependency가 된 tool/config는 terminal freeze 전 full-repository dependency inventory와 필요한 current-route manifest에 additive하게 편입한다. unresolved/unclassified tooling count는 `0`이어야 한다.
- Change 1~8의 code/test/fixture/policy/config/docs와 **실행 전 고정 가능한** `clean_checkout_external_evidence_location_contract.json`을 포함한 exact tracked commit/tree를 terminal subject로 고정한다. 이 contract는 external retrieval coordinate, schema, containment/retention rule만 가지며 Run A/B/comparator result hash를 포함하지 않는다. uncommitted worktree나 hash-only pseudo-subject는 terminal subject가 아니다.
- terminal subject에서 canonical mandatory full-repository Clean-Checkout Run A와 Run B를 각각 fresh disposable checkout으로 실행하고 denominator, dependency inventory, canonical result identity, standalone result와 source-checkout non-mutation parity를 확인한다.
- Run A/B/comparator가 만든 result hash pointer는 검증 뒤 `Iris/_docs/round3/layer3_body_role_realign/evidence_carriers/<carrier_id>/clean_checkout_result_pointer.json` append-only **post-validation evidence-only successor**에 기록한다. 이 carrier는 validated terminal subject가 아니며 terminal subject의 machine PASS를 자신의 PASS로 상속하거나 새 validation subject로 재귀 정의하지 않는다.
- required sequence는 `pre-run retrieval contract 포함 terminal subject freeze -> Run A/B -> deterministic compare -> external result identities 생성 -> evidence-only carrier/pointer successor`다. result pointer 추가 때문에 terminal subject를 다시 정의하거나 같은 Run A/B를 자기참조시키지 않는다.
- predecessor repository PASS는 상속하지 않는다. candidate replay PASS나 focused/current-route PASS도 full-repository PASS를 대신하지 않는다.
- closeout token은 `layer3_role_realign_staging_complete`로 고정하며 disposition/readiness/separation/successor staging/5A handoff와 exact terminal repository validation까지만 의미한다.

Validation:

- exact set equality with readiness projection
- review-required leakage 0
- manual/editorial candidate insertion 0
- tool/dependency disposition completeness, unresolved/unclassified 0
- exact terminal commit/tree binding
- terminal subject의 pre-run retrieval contract에 result hash 0
- post-validation result-hash pointer carrier가 validated terminal subject와 분리됨
- mandatory full-repository Clean-Checkout Run A/B exit 0
- Run A/B denominator/dependency inventory/canonical result parity
- source checkout mutation/residue 0
- scope-exceeding claim scan
- top-level docs terminology and non-claim consistency

---

### Change 9 — Conditional IAR Adoption and Runtime Projection

Purpose:

별도 owner authorization이 있을 때만 exact staging successor를 current generation으로 채택한다. 이 Change는 default staging-only execution에서는 실행하지 않는다.

Files:

- `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
- `Iris/_docs/round3/validated_naturalization_current_runtime_adoption/current_generation_descriptor.json`의 additive successor
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunkIndex.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/**`
- related runtime/package identity and compatibility tests

Implementation Notes:

- exact validated candidate identity와 upstream policy/fact/decision identity를 IAR transaction에 결속한다.
- predecessor generation과 rollback target을 보존하고 partial/dual-current adoption을 금지한다.
- `text_ko` compatibility facade와 optional body behavior를 보존한다.
- separated role material의 runtime physical shape는 RTC impact review와 owner-ratified artifact-shape contract 이후에만 정한다.
- runtime Lua는 disposition/readiness 또는 semantic summarization을 수행하지 않는다.
- Tooltip runtime consumption은 별도 UI plan 없이는 추가하지 않는다.
- adoption이 tracked gate input, runtime/package projection, test 또는 required dependency를 변경하면 staging terminal subject의 repository PASS는 새 adoption subject에 상속되지 않는다. adoption subject를 다시 고정해 full-repository Clean-Checkout Run A/B와 deterministic comparison을 재실행한다.

Validation:

- exact candidate == adopted identity
- partial/dual-current generation 0
- Layer 3 absent page and Layer 4-only page compatibility
- stale predecessor public text reentry 0
- runtime semantic inference path 0
- current/historical/diagnostic route separation
- exact adoption terminal tracked subject에서 fresh mandatory full-repository Clean-Checkout Run A/B
- Lua syntax, package projection identity와 required runtime compatibility tests

---

## 7. Validation Plan

### Automated Validation

- focused unit/contract tests:
  - `uv run python -B -m pytest Iris/build/description/v2/tests/test_layer3_body_role_realign.py -q`
- isolated staging generation:
  - `uv run python -B Iris/build/description/v2/tools/build/run_layer3_body_role_realign.py --mode staging --output-root <isolated-root>`
- read-only terminal validation:
  - `uv run python -B Iris/build/description/v2/tools/build/validate_layer3_body_role_realign.py --subject-root <isolated-root> --require-complete`
- same sealed inputs를 사용하는 independent candidate replay A/B와 canonical result comparison
- exact set checks:
  - every existing body -> one disposition
  - every canonical item -> one readiness
  - every insufficient-material row -> one Problem 5A candidate
- fact/provenance checks:
  - observed non-empty slot/origin/structured-lineage mapping coverage 100%
  - unresolved mapping 0 before disposition/readiness execution
  - unsupported fact 0
  - fact strengthening 0
  - semantic rendered-string parsing 0
  - new Layer 4 promotion 0
  - stale exception application 0
- separation checks:
  - source/current-expressed/successor-projected acquisition set의 count/hash 분리
  - source-bound eligible acquisition proposition loss 0
  - acquisition-only core-description admission 0
  - governance state public-text leakage 0
- exact duplicate checks:
  - detection signal과 blocking result 분리
  - registered-bad/differing-consumed-fact-set duplicate blocking
  - same-consumed-fact-set duplicate automatic blocking 0
- closed transformation registry와 unregistered transform application 0
- review capacity/partition coverage와 required review record incomplete 0; completed unresolved semantic states 허용
- current compose regression and protected-surface hash parity
- generic public-text evaluator가 변경된 경우 existing required subject canonical result regression 0
- current route, relevant historical route and diagnostic raw-result preservation checks
- Change 1~8 exact tracked terminal subject에서 mandatory repository validation:
  - terminal commit/tree freeze와 tool/dependency disposition completeness
  - `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`를 통한 fresh Clean-Checkout Run A/B
  - `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`를 통한 denominator/dependency/canonical result receipt parity
  - source checkout mutation/residue 0
- conditional adoption이 실행된 경우에만:
  - `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`
  - adopted required-validation wrapper
  - adoption changes를 포함한 새 exact terminal subject의 fresh Clean-Checkout Run A/B와 deterministic comparison 재실행

모든 PASS 주장은 exact relevant command가 exit `0`인 경우에만 허용한다. `rg` absence probe나 count 관찰 자체는 PASS가 아니다.

### Manual Validation

- `review_hold`와 `review_required` 전수 검토
- human exception 전수 검토
- disposition/readiness 조합별 representative case 검토
- exact duplicate/registered skeleton group별 representative public-text 검토
- acquisition-heavy, identity-fallback, cluster-summary, Layer 3 absent / Layer 4 present case 검토
- Menu candidate에서 core description과 acquisition의 역할 분리가 자연스럽고 정보 손실이 없는지 확인
- ratified review capacity 안에서 required review record를 모두 작성하지 못하면 `blocked_review_capacity`로 중단한다. 검토 결과가 정당한 `review_hold/review_required` 유지인 것은 blocker가 아니다.
- default staging-only에서는 in-game UI 검증을 수행하지 않는다.
- conditional adoption이 실행된 경우에만 representative Menu page, Layer 3-absent page, acquisition retention과 stale-text absence를 PZ에서 검증한다.

### Validation Limits

- Tooltip UI, exact line allocation, 4-line fit, wrapping와 pixel width는 검증하지 않는다.
- staging-only 실행에서는 current Menu replacement, runtime payload와 package projection을 검증하거나 완료로 주장하지 않는다.
- Problem 5A fact enrichment 또는 외부 source validation을 수행하지 않는다.
- Layer 4 completeness/quality, multiplayer, long-session, 모든 해상도/UI scale과 external-mod sweep를 수행하지 않는다.
- package publication, Workshop deployment, B42 및 Iris 전체 release readiness를 검증하지 않는다.
- unrestricted natural-language semantic quality의 완전 증명을 주장하지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

높음. Layer 3 role policy, fact-kind mapping, disposition/readiness와 exception contract를 새로 봉인한다. DVF System의 semantic production, IAR lifecycle, Publish Boundary assessment를 분리하고 owner ratification 전 mutation을 금지한다.

### Runtime Behavior Surface

staging-only에서는 없음. conditional adoption 시 Layer 3 body presence와 Menu text가 바뀔 수 있으나 runtime은 계속 precompiled text만 표시한다. Tooltip behavior는 변경하지 않는다.

### Compatibility Surface

staging-only에서는 observation only다. conditional adoption 시 `text_ko` facade, nil body, key-level chunk lookup, Layer 4-only page와 package projection compatibility가 영향을 받을 수 있다.

### Sealed Artifact Surface

높음. facts, decisions, profile, rendered generation, runtime chunks, public-text assessment, IAR generation descriptor와 clean-checkout evidence의 exact identity를 다룬다. predecessor는 immutable하게 보존한다.

### Public-Facing Output Surface

staging-only에서는 current output 변화가 없다. conditional adoption 시 Layer 3 Menu body의 유지/축소/수정/숨김과 acquisition 재배치가 사용자에게 보일 수 있다. `surface_all_confirmed` branch가 ratify되면 current-unexpressed confirmed acquisition의 신규 표면화도 포함될 수 있으므로 exact newly-surfaced set과 public delta review를 별도로 기록한다. internal disposition/readiness vocabulary는 노출하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- body assessment, semantic production과 IAR adoption을 하나의 새 subsystem이 소유할 위험
- staging proposition artifact를 current facts authority로 오인할 위험
- current canonical body-role policy가 없는 상태에서 historical deleted policy를 복원·상속할 위험
- Problem 1 optionality가 ratify되지 않았는데 omission/readiness를 결정할 위험
- `primary_use` 전체를 단일 `role`로 mapping해 `identity_fallback`까지 description-eligible로 승격할 위험
- observed mapping 조합을 output distribution 확인 후 사후 분류할 위험
- flat `text_ko` reverse parsing으로 single-writer와 provenance boundary를 깨뜨릴 위험

### Runtime Risk

- hidden disposition을 `unadopted`로 재사용해 기존 runtime vocabulary 의미를 변경할 위험
- nil body가 renderer/Detail/Menu fallback을 통해 stale predecessor text로 되돌아올 위험
- separated projection을 runtime에서 다시 조합·요약하면서 semantic inference가 생길 위험
- conditional adoption 중 partial chunk replacement 또는 index/chunk identity mismatch가 생길 위험

### Compatibility Risk

- role-material field를 current runtime entry에 성급히 추가해 public facade 또는 package consumer shape를 바꿀 위험
- Layer 3 absence를 오류로 가정한 unknown consumer가 있을 위험
- Tooltip future projection을 현재 `IrisTooltipSummary` cache/revision contract에 조기에 결합할 위험
- case-sensitive FullType과 Windows case-insensitive 처리 차이로 denominator가 왜곡될 위험
- 신규 tooling을 경로만으로 current-required 또는 non-required로 암묵 분류해 clean-checkout dependency inventory를 왜곡할 위험

### Regression Risk

- acquisition 분리 중 유효 획득 정보가 사라질 위험
- current body의 lexical 표현 count를 source acquisition conservation denominator로 오인할 위험
- identity/classification 제거 과정에서 유효 role/condition fact까지 제거할 위험
- high-frequency skeleton을 defect로 과탐지할 위험
- short valid description을 길이 기준으로 숨길 위험
- exception ledger가 누적되어 일반 rule보다 강한 shadow authority가 될 위험
- review queue가 ratified capacity를 넘었는데 incomplete review를 partial success로 축소할 위험
- predecessor public-text assessment나 Clean-Checkout PASS를 successor에 상속할 위험
- candidate replay A/B를 repository Clean-Checkout Run A/B로 오인할 위험
- Run A/B result hash pointer를 terminal subject에 추가해 validation subject를 자기참조시키는 위험
- canonical acquisition conservation을 자동 Menu publication으로 오인해 current-unexpressed facts를 미검토 표면화할 위험
- candidate replay 실패 후 byte-exact artifact를 canonical projection class로 완화할 위험

---

## 10. Rollback Plan

staging-only execution은 current public artifact를 변경하지 않는다. validation 실패 시 generated staging subject를 rejected 또는 review-pending lifecycle로 남기고 current facts, decisions, rendered, runtime과 package generation은 유지한다. 실패 evidence를 삭제하거나 PASS로 수정하지 않는다.

policy/rule/exception correction은 기존 record를 고치지 않고 additive successor로 만든다. exception input identity가 변경되면 해당 exception을 invalidated로 기록하고 item을 review queue로 되돌린다.

observed source/origin mapping 조합이 ratified contract에 없으면 `blocked_mapping_contract`로 중단한다. required manual review가 ratified capacity를 넘거나 required review record가 누락되면 `blocked_review_capacity`로 중단한다. completed review의 결론이 `review_hold/review_required`인 것은 누락이 아니다. Change 1~8 exact tracked terminal subject의 mandatory Clean-Checkout Run A/B 또는 comparator가 실패하면 `blocked_repository_validation`이며 candidate replay/focused PASS로 완화하지 않는다.

conditional current adoption이 별도로 승인된 경우에는 adoption 전에 predecessor rendered generation, runtime payload, package projection, exact candidate identity와 rollback target을 봉인한다. 실패 시 다음 중 하나만 허용한다.

1. sealed predecessor generation으로 explicit IAR rollback
2. corrected policy/rule/exception을 가진 additive successor 생성 및 재검증

partial adoption, dual-current generation, historical artifact rewrite, failed evidence 삭제, stale runtime fallback의 암묵적 복귀는 금지한다.

다음이 발견되면 affected execution을 즉시 중단한다.

- rendered direct edit 또는 semantic reverse parsing
- unsupported fact/fact strengthening
- unregistered rewrite/template 또는 exception-mediated fact addition
- Problem 1 prerequisite 미충족 상태의 omission/adoption
- unmapped non-empty `(source_slot, fact_origin)` 또는 structured lineage
- unregistered transformation/defect rule application
- required review capacity 초과 또는 incomplete review record; legitimate completed `review_hold/review_required`는 제외
- current/staging denominator substitution
- internal disposition/readiness user-facing leakage
- source/rendered/runtime/package partial mutation

---

## 11. Governance Constraints

- `docs/Philosophy.md`의 evidence, neutrality, silence-on-insufficient-evidence, viewer-only와 100% Lua runtime 원칙을 보존한다.
- Iris는 Pulse 외 다른 spoke를 참조하지 않으며 이번 작업은 Pulse 또는 타 모듈 dependency를 추가하지 않는다.
- DVF System은 facts/decisions/profile/body plan에서 Layer 3 body를 생산하는 책임만 가진다.
- IAR은 source/rendered/runtime/package artifact identity, lifecycle과 adoption만 소유한다.
- Registry Runtime Compatibility와 Publish Boundary는 DVF/IAR PASS로 대체하지 않는다.
- Layer 4/QG authority를 Layer 3 production으로 흡수하지 않는다.
- Menu와 Tooltip은 같은 confirmed facts의 다른 depth projection이며 별도 knowledge authority가 아니다.
- Runtime Lua는 disposition, readiness, fact-kind, rewrite 또는 summarization을 계산하지 않는다.
- current/historical/diagnostic raw result를 분리하고 diagnostic result를 disposition으로 다시 쓰지 않는다.
- predecessor source, artifact, validation evidence와 exception은 immutable하게 보존하고 additive amendment를 선호한다.
- exact hash가 없는 owner decision, review 또는 exception은 execution authority가 아니다.
- defect/transformation registry, review capacity와 tooling disposition은 exact hash-bound ratification input이며 실행 중 암묵 확장하지 않는다.
- page/Layer 4 information은 readiness optionality branch에만 사용할 수 있고 body disposition/description eligibility에는 사용할 수 없다.
- every exact tracked terminal completion subject는 current clean-checkout contract의 mandatory full-repository Run A/B를 통과해야 한다. staging-only는 이 gate의 면제가 아니다.
- 신규 tooling의 current-route/full-gate role은 terminal freeze 전에 explicit disposition하며 required dependency를 allowlist에서 누락하거나 자동 편입하지 않는다.
- current-route manifest 변경 여부는 staging/current-adoption label이 아니라 actual required-dependency disposition으로 결정한다.
- terminal subject에는 pre-run external retrieval contract만 포함하며 Run A/B result-hash pointer는 post-validation evidence-only successor로 분리한다.
- canonical acquisition material conservation은 Menu publication authority가 아니다. Menu public set과 신규 표면화 branch는 별도 owner-ratified projection contract를 따른다.
- candidate replay identity class와 semantic projection exclusions는 실행 전 봉인하며 실패 후 완화하지 않는다.
- current adoption은 Problem 1 prerequisite, owner authorization, IAR transaction, RTC checks와 adoption subject의 fresh mandatory clean-checkout Run A/B 없이 진행하지 않는다.
- Problem 5A candidate set은 handoff evidence일 뿐 enrichment나 실행 승인으로 사용하지 않는다.

---

## 12. Expected Closeout State

Expected closeout token: **`layer3_role_realign_staging_complete`**

완료 시 다음을 주장할 수 있다.

- execution-time existing Layer 3 body 전수 disposition 완료
- execution-time canonical item 전수 description readiness 완료
- core description / acquisition information role-material 분리 완료
- registered rule과 exact exception에 기반한 deterministic successor candidate 생성 완료
- current public mutation 없이 successor candidate replay A/B 재현 완료
- Change 1~8 exact tracked terminal subject mandatory full-repository Clean-Checkout Run A/B 및 deterministic comparison 완료
- `설명 재료 부족`의 exact Problem 5A candidate handoff 완료
- Menu candidate와 Tooltip input readiness 완료

다음은 주장하지 않는다.

- current Layer 3 successor adoption
- current runtime 또는 package projection update
- current Menu public text replacement
- Tooltip UI, exact Tooltip line assignment 또는 4-line layout 완료
- Problem 5A 해결 또는 실행 승인
- Registry Authority PASS
- Registry Runtime Compatibility PASS, Publish Boundary PASS 또는 release readiness

owner ratification 또는 exact Problem 1 binding이 없으면 policy-dependent 실행은 `blocked_policy_prerequisite`로 닫는다. observed mapping coverage가 불완전하면 `blocked_mapping_contract`, required review가 capacity를 초과하거나 review record가 미완료면 `blocked_review_capacity`, exact terminal repository gate가 실패하거나 실행되지 않으면 `blocked_repository_validation`로 닫는다. completed review가 semantic 결론으로 `review_hold/review_required`를 유지하는 것은 `blocked_review_capacity` 사유가 아니다. 이 blocked token들은 partial success나 PASS가 아니다.

별도 current-adoption authorization이 주어지면 Change 9를 새 exact tracked terminal subject에 대해 실행한다. 해당 IAR/RTC/Lua/package validation과 fresh repository Clean-Checkout Run A/B를 모두 exit `0`으로 통과한 경우에만 별도 token `layer3_role_realign_current_adoption_complete`를 기록할 수 있다.
