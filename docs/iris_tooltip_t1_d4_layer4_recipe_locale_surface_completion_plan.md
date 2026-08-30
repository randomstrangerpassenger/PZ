# Iris Tooltip T1-D4 Layer 4 Recipe Locale Surface Completion Implementation Plan

> 상태: planned / synchronized for parallel execution / implementation not started / owner ratification required
> 작성일: 2026-08-28
> 기준 로드맵: `T1-D4 — Layer 4 Recipe Locale Surface Completion 종합 Roadmap`
> 상위 작업: `Tooltip T1-C: Upstream Correction Closure and T2 Readiness Opening`
> 대상 blocker: `QG/locale — LOCALE_SELECTED_SURFACE_MISSING`
> 검증 깊이: heavy offline authority / determinism / whole-T1 re-audit
> 실행 predecessor: Tooltip T1-C final commit `6b7118dc229bf8138302696e1aa5e5b7454589dc`, tree `4eae6fbdb3d0b2cb532f875b96137335a403f2fc`
> 병렬 실행 계약: `docs/iris_tooltip_t1_parallel_workstream_execution_contract.md`
> 동기화 반영: `Layer4Candidate`의 locale/Menu readiness field 제거, current width-advisory contract, authority-ceiling fail-loud, reverse-flow type guard와 three-way validation ceiling은 유지하되 global adoption/docs carrier/canonical gate는 D6로 이관한다.

이 계획은 Recipe 이름 266개를 번역하는 작업이 아니다. Current Tooltip T1은 Layer 4 identity를 locale readiness보다 먼저 선택하고, 선택된 exact Recipe identity에 명시적인 KO/EN surface가 없으면 locale별 correction을 발행한다. D4는 이 selected identity를 바꾸지 않은 채 QG가 승인한 동일 interaction fact의 KO/EN projection을 제공하고, 이를 current T1 audit가 exact identity 기준으로 소비하게 만드는 bounded owner-correction 작업이다.

계획 작성 시점의 read-only 코드베이스 관측은 다음과 같다. 아래 수치와 해시는 roadmap planning baseline과 일치하지만 실행 authority가 아니며, 실제 구현은 clean exact subject에서 다시 census한다.

| Surface | Current code observation | Planning consequence |
| --- | --- | --- |
| Layer 4 identity owner input | `Iris/build/description/v2/data/upstream_usecases_by_fulltype.json`, SHA-256 `2af068b1ea898125e81e9103af79019a35a1c51b8fd7c74325906d26567ad43f` | 이 파일의 identity/public/source/line-kind authority는 유지한다. D4가 selection을 바꾸기 위해 재생성하지 않는다. |
| Authority ceiling | `iris_current_authority_manifest.json`과 `layer4_tooltip_projection_contract.json`은 위 파일을 **locale surface authority가 아닌** read-only identity input으로 봉인한다. | `display_by_locale`를 기존 파일에 임의로 끼워 넣어 authority ceiling을 우회하지 않는다. 별도 QG-owned Recipe locale owner output을 채택한다. |
| Current owner universe | 1,606 FullType, 2,678 use-case row; Recipe 791 instance와 Right-click 1,887 instance | D4 authoring denominator는 전체 791 Recipe row가 아니라 frozen selection에서 실제 선택된 Recipe identity다. |
| Current selected Layer 4 | 총 530 instance: Recipe 444, Right-click 86 | Recipe와 Right-click을 독립 source로 유지한다. D4가 Right-click surface를 수정하지 않는다. |
| D4 Recipe target | affected FullType 349, selected Recipe instance 444, unique Recipe identity 266 | ledger row, selected instance, unique identity, FullType 네 universe를 독립 산출한다. |
| Current locale state | selected Recipe instance 중 embedded locale surface 0 | KO/EN correction 888은 현재 `444 × 2`와 일치하지만, 실행 시 ledger 구조를 산술로 가정하지 않고 actual correction rows에서 재산출한다. |
| Selected source shape | both 20, Recipe-only 329, Right-click-only 66, no selected public interaction 1,191 | pre/post selected mapping과 source distribution을 byte/canonical identity 수준으로 비교한다. |
| Recipe identity reuse | 266 identity 중 194개는 1회, 72개는 여러 FullType에서 재사용되며 최대 10회 선택된다. | surface는 identity 수준에서 한 번 승인할 수 있지만 모든 selected instance의 canonical semantic relation을 먼저 검증한다. |
| Role divergence diagnostic | 10개 selected Recipe identity가 selected instances 사이에서 `consume`과 `keep` role을 모두 가진다. | role 차이를 곧바로 semantic collision 또는 동일 의미로 판정하지 않는다. QG owner가 exact evidence relation을 확인하기 전에는 해당 identity surface를 승인하지 않는다. |
| T1 implementation seam | `audit.py`는 candidate 안의 optional `display_by_locale`를 읽지만 current adopted identity input에는 해당 권위와 필드가 없다. | identity input과 locale owner output을 명시적으로 분리하고, selection freeze 후 exact identity lookup으로 결합한다. |
| Selection object seam | `Layer4Candidate`는 현재 `localized_surfaces`와 `menu_consumer_identity_ref`를 보유하지만 selection은 이 값을 읽지 않는다는 behavioral invariant에 의존한다. | 두 readiness field를 candidate type에서 제거해 selection graph에서 locale/Menu input을 구조적으로 도달 불가능하게 만든다. Production fixture도 separate post-selection resolver를 통과한다. |
| Current line-fit authority | `iris_tooltip_t1_display_contract_policy.md`는 `0~4` logical rows와 embedded CR/LF만 T2 hard gate로 두며 actual pixel/font/UI-scale fit은 T3로 미룬다. `test_locale_menu_public_text(width_advisory)`도 긴 single line을 허용한다. | D4가 새 numeric character/byte/pixel bound를 발명하지 않는다. Single-line/NFC/semantic owner review만 D4 gate이며 visual/width acceptance는 existing T3 boundary에 남긴다. |
| Retired label map | `Iris/build/data/v2.4/usecase_label_map.json`과 `convert_labelmap_to_lua.py`는 retained non-current predecessor이며 Recipe label coverage도 없다. | 이 경로를 D4 current semantic/locale authority로 재승격하지 않는다. |
| Runtime Recipe prose | `UseCaseDescriptions/Chunk*.lua`의 Recipe `display_text`는 recipe translated name에서 생성된 downstream runtime projection이다. | runtime prose, Recipe original/translated name, localization key를 누락 interaction meaning의 역추론 source로 사용하지 않는다. |

---

## 0. Parallel execution synchronization amendment

이 계획은 공통 병렬 실행 계약을 따른다. T1-D4는 T1-D1, T1-D3, T1-D5와 동일 predecessor에서 별도 clean worktree로 동시에 실행한다. 다른 workstream의 진행 중 branch나 current route를 소비하지 않는다.

이 절은 후속 절의 selected integration commit 대기, global current manifest/route/environment locator, `ENTRYPOINTS.md`, governance status 직접 채택, workstream별 canonical full-gate Run A/B/finalizer, mandatory docs-only carrier와 신규 `test_tooltip_t1_d4.py` 요구를 폐기한다. 동일 내용을 담은 후속 문구보다 이 절과 공통 계약이 우선한다.

D4의 terminal output은 QG-approved Recipe locale registry/projection, isolated T1 integration delta, invariance evidence와 immutable D4 correction bundle이다. Current ecosystem adoption과 formal whole-product closeout은 T1-D6가 수행한다.

공통 Tooltip T1 code/contracts/tests 변경은 `shared_path_delta`로 bundle에 기록한다. Runtime/static Tooltip payload, Right-click route와 global current paths는 protected read-only inputs다.

테스트 예산은 새 파일 `0`, 새 top-level function/family `0`이다. D4 cases는 기존 Tooltip T1 contract/projection/audit parameter tables에 통합한다. 기존 family로 필수 type/API path를 실행할 수 없을 때만 기존 파일 안 parameterized function 최대 1개 예외를 허용한다.

---

## 1. Objective

Clean exact subject에서 current authoritative Tooltip T1 audit가 선택한 Recipe identity 전체에 대해 다음 관계를 QG owner authority로 확정하고 isolated T1 candidate readiness lookup에 연결한다.

```text
exact selected Recipe identity
-> current QG Recipe Evidence / rule_id / structured relation
-> one approved canonical interaction fact
-> approved KO single-line surface
-> approved EN single-line surface
```

동시에 D4 전후 다음 tuple은 동일해야 한다.

```text
FullType
+ slot_id
+ source_type
+ selected source identity
+ selected Recipe identity
+ selection result/order identity
```

최종 목표는 current authoritative T1 re-audit에서 D4 frozen Recipe scope의 `LOCALE_SELECTED_SURFACE_MISSING`을 0으로 만들고, 그 과정에서 locale-dependent reselection, cross-locale fallback, Recipe→Right-click substitution, source-distribution 변화와 non-target semantic mutation이 모두 0임을 증명하는 것이다.

D4의 terminal `complete`는 strict full closure를 사용하되 **모든 divergence identity가 하나의 canonical fact로 owner-disposition되고 최종 authority subject가 검증된 경우에만 기대할 수 있는 조건부 목표**다. Canonical meaning 또는 KO/EN pair를 owner authority로 승인할 수 없는 identity가 하나라도 남으면 추론으로 채우거나 다른 owner/cause로 이동해 완료 처리하지 않는다. 구현된 부분과 blocked identity는 보존할 수 있지만 D4 closeout은 `blocked` 또는 `implemented_only`로 남긴다.

---

## 2. Scope

### Included

- clean exact subject에서 current T1 audit를 실행해 D4 correction row, selected Recipe instance, unique Recipe identity, affected FullType을 각각 재산출
- pre-mutation selected tuple, selected identity set, selected source shape와 owner input hash freeze
- selected Recipe identity별 `evidence_sources`, `rule_id`, role, current provenance와 selected FullType relation census
- Recipe name/key/runtime prose를 authoring input에서 구조적으로 제외한 QG semantic review packet
- same identity / multi-FullType reuse와 `consume`/`keep` role divergence에 대한 per-identity owner disposition
- exact identity와 canonical semantic reference에 결속된 KO/EN single-line neutral surface authoring 및 owner approval
- 지원 locale `ko`, `en`의 explicit pair, no-fallback, Unicode NFC와 CR/LF 금지 검증
- selection-only `Layer4Candidate`에서 `localized_surfaces`와 `menu_consumer_identity_ref` 제거 및 모든 locale/Menu lookup의 post-selection 구조화
- current identity input과 분리된 QG-owned Recipe locale registry 및 deterministic owner projection
- T1이 Recipe locale owner output을 **selection 이후** exact identity lookup으로만 소비하도록 하는 contract/audit 수정
- existing Right-click locale route와 Layer 4 runtime consumer identity route의 non-mutation 증명
- same Recipe identity를 참조하는 모든 selected instance의 identical authoritative resolution 검증
- 다른 identity가 우연히 같은 surface text를 갖더라도 identity merge가 없음을 검증
- selected-missing/unselected-ready, one-locale-only, Recipe-missing/Right-click-ready 등 negative fixture
- existing focused T1 parameterized tests, immutable repository-external candidate audit와 materializer Run A/Run B digest comparison
- corrected exact subject의 whole-T1 re-audit와 D4 before/after correction reconciliation
- `QG/locale` 전체 owner bucket과 D4 Recipe-filtered target을 별도 denominator로 기록하고 explicit delta 산출
- QG owner ratification을 workstream candidate/registry/projection hash에 결속하고 D6 integration proposal을 생성
- global current adoption 없이 workstream subject와 external bundle을 봉인
- complete뿐 아니라 blocked/implemented_only materialized path의 invariance·non-mutation·whole-T1 validation과 three-way validation ceiling 기록
- predecessor external audit/ledger를 덮어쓰지 않는 additive successor closeout
- current authority/governance/command owner에 대한 bounded successor proposal; actual adoption은 D6 소유

### Explicitly Out Of Scope

- 새로운 Recipe interaction fact, Recipe Evidence 또는 `rule_id` 생성
- Recipe importance, frequency, efficiency, usefulness, priority 또는 recommendation 판단
- Recipe original name, translated name, `use_case_id`, localization key, DisplayName에서 interaction meaning 추론
- selected Recipe identity, candidate set, stable ordering 또는 capacity rule 변경
- locale가 준비된 unselected Recipe로 substitution
- Right-click identity/surface/translation correction 또는 Recipe와 Right-click 병합
- unselected Recipe 347개 instance 전체의 locale authoring
- Recipe 이름 번역 프로젝트 또는 current runtime Recipe `display_text` 교정
- `upstream_usecases_by_fulltype.json`의 Recipe Evidence/identity 재생성
- Layer 2, Layer 3, Classification, DVF, Menu consumer 또는 Iris presentation-contract blocker 수정
- Tooltip slot 조립, T2 handoff/static Lua generation 또는 `IrisAltTooltip` runtime 변경
- `UseCaseDescriptions/Chunk*.lua`, `IrisUseCaseLabelMap.lua`, KO/EN runtime translation 파일 갱신
- actual Alt Tooltip render, pixel/font/UI-scale fit 또는 in-game 4-line visual 검사
- D4가 새 character/byte/pixel length limit을 정의하거나 current width-advisory contract를 변경하는 작업
- package/install, Runtime Compatibility, Publish, release, Workshop 또는 deployment 판정
- arbitrary external-mod compatibility sweep
- D4 lifecycle census/ledger/receipt를 새 regular validation authority나 stateful registry로 추가
- unrelated refactor, dependency 변경 또는 architecture redesign

---

## 3. Non-Goals

- planning baseline `888 / 349 / 444 / 266`을 실행 시점 denominator로 고정하지 않는다.
- 888이 444×2라는 이유만으로 correction ledger schema를 instance×locale 구조라고 가정하지 않는다.
- 266 unique identity마다 물리적으로 정확히 한 row가 있어야 한다는 새 전역 QG schema를 D4 밖까지 강제하지 않는다. D4 owner projection은 exact identity-keyed lookup을 제공하되 기존 QG data model 전체를 migration하지 않는다.
- Recipe surface를 recipe title의 단순 재표현으로 만들지 않는다.
- 동일 문장이 다른 identity에 존재한다는 이유만으로 identity를 병합하거나 자동 거부하지 않는다. 각 identity의 semantic binding을 독립적으로 검증한다.
- `consume`/`keep` role 차이만으로 semantic collision을 자동 확정하지 않는다.
- 한 locale만 준비된 identity를 부분적으로 render할지 결정하지 않는다. D4/T1 readiness에는 KO/EN pair가 모두 필요하다.
- unresolved semantic identity를 새 reason code나 다른 owner로 이동해 D4 correction count만 줄이지 않는다.
- focused D4 validation PASS를 전체 T1-C 완료나 `T2_FULL_DATA_PROGRESSION = OPEN`으로 확대하지 않는다.
- D4 bundle이나 D6 integration proposal을 predecessor T1/D4 machine closeout의 소급 수정으로 취급하지 않는다.
- post-change selector를 pre/post 양쪽에 다시 실행해 selector regression을 상쇄하지 않는다. Pre-side는 Change 1 frozen artifact 하나만 사용한다.
- D1/D3/D5는 D4와 별도 clean worktree에서 병렬 실행한다. D4는 공통 predecessor와 frozen support만 소비하고 다른 진행 중 workstream mutation을 포함하지 않는다.

---

## 4. Assumptions

### Repository and authority assumptions

- product/architecture authority order는 `Philosophy.md -> DECISIONS.md -> ARCHITECTURE.md -> ROADMAP.md -> current authority manifest/contracts`다. `AGENTS.md`는 이 authority chain의 semantic 문서가 아니라 현재 작업 세션의 execution/validation constraint이며, 그 fail-closed 요구를 본 계획에 직접 반복한다.
- Iris runtime은 계속 100% Lua이며 D4 tooling은 repository-side offline Python에 한정한다.
- installed `iris_tooling` package가 current implementation/command owner다. Retired description-tree scripts와 label-map converter는 current writer로 복원하지 않는다.
- `upstream_usecases_by_fulltype.json`은 identity/public/source/line-kind authority이며 locale surface authority가 아니다.
- current T1 audit의 selected tuple은 D4 authoring의 input이며 D4가 다시 쓰는 output이 아니다.
- repository-external D4 census, review packet, reconciliation과 closeout은 lifecycle evidence이지 regular validation authority가 아니다.
- 기존 dirty worktree의 D1/D3/D5 변경은 보존한다. D4는 공통 T1-C predecessor에서 dedicated clean worktree를 만들고 exact commit/tree를 확인한 뒤 병렬 실행한다. Main worktree를 clean/reset/stash하지 않는다.
- D4 workstream subject는 다른 병렬 correction을 포함하지 않는다. Cross-workstream integration과 combined re-audit는 D6가 담당한다.

### Exact target assumptions

- 계획 시점 current input의 exact selection은 Recipe instance 444, affected FullType 349, unique identity 266이며 locale correction 888이다.
- 실행은 clean exact subject의 current T1 `upstream_correction_ledger.jsonl`에서 `reason_code=LOCALE_SELECTED_SURFACE_MISSING`, `layer=layer4`, selected source `recipe`인 rows를 primary target으로 재구성한다.
- frozen correction rows를 audit manifest의 exact `FullType + slot_id + source + selected_identity` relation과 교차 검증한다.
- ledger row, selected instance, unique identity, FullType count는 각각 실제 records에서 산출하며 다른 count에서 계산하지 않는다.
- current target set을 authoritative하게 재구성할 수 없거나 correction row와 selected mapping이 불일치하면 authoring 전에 `blocked`다.
- `QG/locale` 전체 blocking bucket과 D4의 `reason=LOCALE_SELECTED_SURFACE_MISSING + source=recipe` filtered target은 별도 count/set/hash로 기록한다. 둘이 같다는 사실은 실행 census가 증명할 때만 주장한다.

### Semantic and locale assumptions

- QG owner가 승인할 수 있는 canonical semantic reference는 current Recipe Evidence와 exact `rule_id`, structured role/relation 및 current provenance에 결속돼야 한다.
- Recipe name, identity 문자열, runtime `display_text`, historical output과 reproduction baseline은 semantic reference가 아니다.
- same identity가 여러 selected instances에서 다른 canonical fact를 뜻하면 D4가 identity를 분할하거나 대표 의미를 고르지 않는다.
- KO와 EN은 직역·문자열 유사성이 아니라 같은 exact identity와 canonical semantic reference에 결속됨으로써 same-fact 관계를 증명한다.
- 신규 surface는 NFC로 저장하고 CR/LF를 포함하지 않으며 recommendation/importance/frequency/efficiency 의미를 추가하지 않는다.
- Current T1 authority는 numeric width/length hard gate를 두지 않는다. D4 owner는 사실을 과장하지 않는 간결한 single-line 표현을 검토하지만 character/byte/pixel 수를 machine PASS 조건으로 만들지 않으며 actual fit은 T3 validation ceiling이다.
- cross-identity byte-identical text는 각 identity binding과 owner approval이 독립적으로 존재하면 허용한다. 단, dedupe/alias/merge는 금지한다.

### Conflict dispositions from the roadmap

- **Completion:** strict full closure를 채택한다. unresolved identity가 남으면 D4 `complete`가 아니다.
- **Owner/cause movement:** current `LOCALE_SELECTED_SURFACE_MISSING`을 다른 owner/cause로 옮기는 행위는 D4 completion으로 인정하지 않는다. 별도 owner decision이 실제 governing contract를 supersede하지 않는 한 original D4 row를 유지한다.
- **Surface storage:** current identity input을 locale carrier로 확장하지 않고 별도 exact identity-keyed QG Recipe locale owner output을 사용한다. 이는 D4 lookup contract이며 QG 전체 schema의 물리적 1:1 migration은 아니다.
- **Selection proof:** semantic tuple의 canonical byte identity와 aggregate SHA-256을 모두 비교한다. JSON 파일 전체 byte identity는 volatile metadata/order 차이 때문에 요구하지 않되, normalized selection records는 byte-identical이어야 한다.
- **Legacy locale/Menu seam:** `Layer4Candidate.localized_surfaces`와 `menu_consumer_identity_ref`를 제거한다. Identity input의 embedded `display_by_locale`는 production Recipe authority로 소비하지 않으며 contract 위반으로 fail-loud한다. 모든 fixture는 separate production post-selection resolver를 사용한다.
- **Length owner:** current policy/test의 existing disposition인 `single logical line hard gate + width advisory + T3 actual fit`을 유지한다. D4는 새 numeric bound를 추가하지 않고 validation ceiling을 명시한다.
- **Determinism:** D4 materializer candidate Run A/Run B byte comparison을 수행하고 integrated canonical Run A/B/comparator는 D6에 유보한다.
- **Single-locale rendering:** runtime policy로 열지 않는다. D4 readiness에는 complete KO/EN pair를 요구한다.
- **Generation:** runtime/static generation은 D4 밖에 둔다. 별도 Adoption -> Generation -> Install 작업 전에는 runtime payload를 바꾸지 않는다.
- **Sealed artifacts:** predecessor audit/ledger는 immutable하게 보존하고 새 audit/ledger/closeout만 additive successor로 생성한다.
- **Decision ratification:** QG owner registry/projection과 shared-path delta를 완성한 뒤, QG/product owner가 exact workstream candidate와 해당 hashes에 결속된 repository-external ratification receipt를 발행한다. Global governance successor는 D6 proposal로만 남긴다.
- **Terminal sequencing:** Changes 1~6의 D4-owned implementation과 isolated shared-path proposal -> clean workstream candidate freeze -> owner pre-validation ratification -> affected-range/focused/materializer Run A/B comparison -> owner terminal seal -> immutable D4 bundle 순서를 사용한다. D4는 global authority/docs를 채택하거나 docs-only status carrier를 만들지 않으며, integrated canonical validation과 current adoption은 D6가 수행한다.

---

## 5. Repository Areas Affected

아래 `(new)`는 계획상 신규 path이며, exact implementation 중 existing package structure에 더 적합한 동등 경로가 확인되면 같은 owner boundary 안에서 최소 조정할 수 있다. 경로 변경은 closeout에서 명시한다.

### Code

- `Iris/tooling/src/iris_tooling/domains/layer4/tooltip_t1_d4.py` (new) — exact target freeze, semantic-reference census, registry validation, deterministic owner projection과 D4 reconciliation
- `Iris/tooling/src/iris_tooling/domains/layer4/cli.py` — installed `iris-tooling build layer4` 아래 lifecycle-bound D4 route 추가; existing Layer 4 route 보존
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py` — separate Recipe locale owner output load, post-selection exact lookup, D4 source/binding metrics와 successor re-audit
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py` — new locale input contract/schema/hash/locale-set/NFC/exact-binding validation
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/projection.py` — `Layer4Candidate`를 selection-only type으로 축소하고 locale/Menu readiness field와 masking behavior 제거
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/models.py` — post-selection `Slot.localized_surfaces`는 유지하되 candidate/readiness 경계를 명시하는 최소 typed validation
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/d4_invariance.py` (new) — 같은 Tooltip T1 domain 안에서 producer와 분리된 frozen-pre/post selected tuple, source shape와 non-target comparator; domain-independent claim은 하지 않음
- existing Tooltip T1 parameterized test files; no D4-specific test file
- `Iris/tooling/tests/test_tooltip_t1_contract.py`
- `Iris/tooling/tests/test_tooltip_t1_projection.py`
- `Iris/tooling/tests/test_tooltip_t1_audit.py`
- `Iris/tooling/tests/fixtures/tooltip_t1/contract_expectations.json`

### Docs

- `docs/iris_tooltip_t1_d4_layer4_recipe_locale_surface_completion_plan.md`
- `docs/iris_tooltip_t1_display_contract_policy.md` — identity input과 Recipe locale owner output의 분리 및 post-selection lookup 명시
- `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` — read-only D6 integration inputs; D4 proposal은 bundle에 기록
- `Iris/build/ENTRYPOINTS.md` — read-only command-owner input

### Config

- `Iris/_docs/authority/qg/tooltip_t1_d4_recipe_locale_surface_registry.schema.json` (new) — exact identity, canonical semantic refs, KO/EN, approval/provenance schema
- `Iris/_docs/authority/qg/tooltip_t1_d4_recipe_locale_surface_registry.json` (new) — QG owner-approved D4 records
- `Iris/_docs/authority/qg/tooltip_t1_d4_decision_ratification.schema.json` (new) — exact candidate subject와 successor decision/registry/contracts를 결속하는 owner receipt schema
- `Iris/_docs/authority/tooltip_t1/layer4_recipe_locale_input_contract.json` (new) — T1이 소비하는 current owner output과 binding contract
- `Iris/_docs/authority/tooltip_t1/layer4_tooltip_projection_contract.json` — identity input의 locale-authority ceiling은 보존하고 separate locale route만 참조
- `Iris/_docs/authority/tooltip_t1/tooltip_locale_menu_parity_contract.json` — Recipe/Right-click별 locale authority route를 구분
- `Iris/_docs/authority/tooltip_t1/tooltip_readiness_reason_registry.json` — reason code는 유지하고 acceptance를 new owner-output route에 결속
- `Iris/_docs/authority/tooltip_t1/tooltip_t1_tool_disposition_contract.json` — D4 lifecycle output/regular-authority 비승격 명시가 필요한 경우 additive update
- `Iris/_docs/authority/iris_current_authority_manifest.json` — read-only D6 integration input
- `Iris/_docs/authority/iris_current_route_index.json` — read-only D6 integration input

### Generated Artifacts

- `Iris/build/description/v2/data/tooltip_t1_layer4_recipe_locale_owner_input.json` (new) — deterministic exact identity-keyed QG owner projection; T1 readiness input
- repository-external immutable D4 result root:
  - `subject_binding.json`
  - `d4_exact_target_freeze.jsonl`
  - `d4_denominator_census.json`
  - `d4_qg_locale_bucket_vs_recipe_target.json`
  - `d4_authority_ceiling_violation_report.json`
  - `d4_selected_recipe_baseline.jsonl`
  - `d4_source_distribution_baseline.json`
  - `d4_identity_semantic_reference_matrix.jsonl`
  - `d4_role_divergence_disposition.jsonl`
  - `d4_owner_surface_review_report.json`
  - `d4_locale_binding_report.jsonl`
  - `d4_selected_tuple_comparison.json`
  - `d4_source_distribution_comparison.json`
  - `d4_non_target_invariance_verdict.json`
  - `d4_correction_reconciliation.json`
  - `d4_whole_t1_reaudit_report.json`
  - `d4_prevalidation_owner_ratification_receipt.json`
  - `d4_machine_validation_closeout.json`
  - `d4_terminal_owner_seal.json`
  - `d4_axis_separated_closeout_record.json`
  - `d4_parallel_integration_manifest.json`
  - `d4_shared_path_delta.json`
  - `run_receipt.json`
- existing repository-external Tooltip T1 audit/ledger의 additive successor; predecessor root는 수정하지 않음

Runtime/generated files 아래는 D4에서 **변경 금지** 대상으로 hash freeze한다.

- `Iris/media/lua/client/Iris/Data/UseCaseDescriptions/**`
- `Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptions.lua`
- `Iris/media/lua/client/Iris/Data/IrisUseCaseLabelMap.lua`
- `Iris/media/lua/shared/translate/ko/Iris_ko.txt`
- `Iris/media/lua/shared/translate/en/Iris_en.txt`
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`

---

## 6. Planned Changes

### Change 1 — Clean exact subject and D4 denominator freeze

**Purpose:**

Planning counts가 아니라 하나의 current exact subject에 결속된 D4 target과 protected selection baseline을 만든다.

**Files:**

- `Iris/tooling/src/iris_tooling/domains/layer4/tooltip_t1_d4.py` (new)
- repository-external D4 census/baseline artifacts

**Implementation Notes:**

1. clean commit/tree, installed wheel/environment receipt, current T1 contract hashes와 all semantic input hashes를 `subject_binding.json`에 결속한다.
2. current T1 audit를 실행하고 correction ledger에서 D4 target rows를 직접 추출한다.
3. audit manifest의 selected Layer 4 rows와 join해 각 target에 `FullType`, `slot_id`, source, selected identity, locale, reason을 기록한다.
4. `QG/locale` owner의 전체 blocking set과 D4 Recipe-filtered set을 먼저 분리한다.

   ```text
   QG/locale total
   D4 Recipe target = reason LOCALE_SELECTED_SURFACE_MISSING
                      + layer4
                      + selected source recipe
   explicit set/count delta
   ```

5. 다음 universe를 독립적으로 산출한다.

   ```text
   correction ledger row
   selected Recipe instance
   unique selected Recipe identity
   affected FullType
   missing KO cell
   missing EN cell
   ```

6. 모든 selected Layer 4 instance의 normalized tuple과 selected source shape를 immutable pre-side artifact로 freeze한다. 이후 comparator가 pre-side selection을 재실행하거나 재구성하는 대체 경로를 허용하지 않는다.
7. `upstream_usecases_by_fulltype.json`, Right-click locale route, runtime consumer identity chunks와 runtime/static Tooltip files의 hash baseline을 기록한다.
8. planning `888 / 349 / 444 / 266`과 current census의 차이는 오류로 숨기지 않고 explicit delta로 보고한다.

**Validation:**

- orphan correction row `0`
- selected Recipe identity 없는 locale correction `0`
- 서로 다른 subject hash 혼합 `0`
- source identity/slot identity 중복 또는 누락 `0`
- four-universe counts가 actual record membership에서 각각 재현됨
- `QG/locale total`, D4 Recipe target과 exact delta가 별도 set/count/hash로 방출됨
- pre-mutation selected source distribution과 tuple SHA-256 생성
- frozen pre-side artifact가 immutable input으로 receipt에 결속됨

---

### Change 2 — Canonical semantic reference and reuse census

**Purpose:**

각 unique selected Recipe identity가 어떤 current QG evidence relation을 의미하는지 확인하고 surface authoring 가능한 identity와 fail-closed identity를 분리한다.

**Files:**

- `Iris/tooling/src/iris_tooling/domains/layer4/tooltip_t1_d4.py`
- `d4_identity_semantic_reference_matrix.jsonl`
- `d4_role_divergence_disposition.jsonl`

**Implementation Notes:**

각 unique identity에 대해 다음을 current owner input의 structured fields와 admissible QG authority에서 수집한다.

```text
use_case_id
evidence_sources[].source_type
evidence_sources[].rule_id
evidence_sources[].decision
evidence_sources[].role
selected FullType / slot instances
current authority/provenance ref
canonical interaction fact ref
existing approved KO/EN surface, if any
```

Authoring packet에서는 Recipe original/translated name, DisplayName, runtime `display_text`, localization key와 historical output을 제외한다. 이 값들은 identity/provenance cross-check에만 제한적으로 표시할 수 있으며 semantic proposition column으로 승격하지 않는다.

동일 identity가 여러 FullType 또는 role에 나타나면 모든 instance가 하나의 approved canonical interaction fact로 설명 가능한지 QG owner가 판정한다. 계획 시점에 발견된 10개 consume/keep divergence identity는 mandatory review 대상이다. Divergent fact가 확인되면 해당 identity는 authoring하지 않고 blocked로 남기며 D4가 split/alias를 만들지 않는다.

Divergent fact로 확정된 identity는 current `LOCALE_SELECTED_SURFACE_MISSING` row를 D4 안에서 다른 cause/owner로 재분류하지 않는다. 대신 closeout observation에 `upstream QG identity-definition owner follow-up scope`임을 기록해 후속 작업 경로를 명명한다. 이는 새 reason code, state enum 또는 D4 completion 이동이 아니며 original correction은 governing successor가 생길 때까지 유지된다.

**Validation:**

- selected unique identity coverage 100%
- selected instance -> identity -> evidence source LEFT JOIN orphan `0`
- non-Recipe evidence로 Recipe semantic ref를 대체한 row `0`
- Recipe name/key/runtime prose를 canonical meaning source로 사용한 row `0`
- same identity의 rule/role/proposition divergence가 disposition 없이 통과한 row `0`
- cross-identity similarity merge `0`
- divergent fact identity마다 upstream QG identity-definition follow-up observation 존재; cause/owner mutation `0`

---

### Change 3 — QG owner registry and KO/EN semantic approval

**Purpose:**

Canonical meaning이 확인된 exact Recipe identity에 대해 중립적인 KO/EN pair를 owner-approved current authority로 만든다.

**Files:**

- `Iris/_docs/authority/qg/tooltip_t1_d4_recipe_locale_surface_registry.schema.json` (new)
- `Iris/_docs/authority/qg/tooltip_t1_d4_recipe_locale_surface_registry.json` (new)
- existing `test_tooltip_t1_contract.py` parameter table; no D4-specific test file

**Implementation Notes:**

Registry record는 최소 다음을 가진다.

```text
exact Recipe identity
canonical semantic reference(s)
selected-instance evidence digest
localized_surfaces.ko
localized_surfaces.en
QG owner approval reference
provenance / subject binding
```

Surface는 approved interaction fact만 표현한다. importance, frequency, efficiency, recommendation, 대표성, 우선순위나 새 조건/outcome을 추가하지 않는다. KO와 EN은 같은 semantic reference 집합에 결속한다. Text는 non-empty single line, NFC이고 T1 lexical guard를 통과해야 한다.

현행 T1 contract에는 character/byte/pixel width hard gate가 없고 actual fit은 T3다. 따라서 D4 registry/schema는 임의의 numeric length cap을 추가하지 않는다. QG owner는 문장이 canonical fact보다 불필요하게 장황하지 않은지 수동 검토하지만, D4 machine validation은 semantic binding, non-empty, NFC와 CR/LF 금지만 판정한다. 향후 width bound가 필요하면 T2/T3 owner가 별도 ratified contract로 도입해야 하며 D4 surface를 downstream에서 임의 truncate/rewrite하는 방식은 허용하지 않는다.

다른 identity가 같은 text를 가져도 record는 별도로 유지한다. Tooling은 text dedupe로 record를 병합하지 않는다. Existing valid surface가 발견되면 identity/semantic binding이 검증되는 경우에만 그대로 채택하고 불필요한 rewrite를 하지 않는다.

**Validation:**

- schema/unknown-field fail-loud
- exact identity 중복 `0`
- missing canonical semantic ref `0`
- missing owner approval ref `0`
- KO-only 또는 EN-only accepted record `0`
- CR/LF, empty/whitespace-only, non-NFC `0`
- forbidden recommendation/priority expression `0`
- unsupported semantic invention `0` owner review
- identical text를 이유로 identity가 합쳐진 row `0`

Machine validation은 identity/reference/schema/locale 형식 결속을 검증한다. KO/EN 문장이 실제로 동일 canonical fact를 정확히 표현하는지와 문장 간 의미 동등성은 QG owner semantic judgment이며 automated PASS가 대신하지 않는다. Owner review receipt가 없으면 해당 record는 승인되지 않는다.

**Phase Gate:**

모든 frozen selected Recipe identity가 approved registry record를 갖지 못하면 complete-path materialization과 D4 complete closeout을 차단한다. Resolvable rows만 materialize한 candidate는 만들 수 있지만 status는 `implemented_only` 또는 `blocked`다.

차단 시점에 따라 필수 검증 범위를 분리한다.

- Read-only census/semantic review 중 implementation mutation 전에 차단되면 frozen baseline, census, registry/schema와 unresolved owner-evidence disposition까지만 검증한다. Complete-path materialization과 complete-only assertions는 실행 대상이 아니다.
- Code/data/contract 또는 owner projection이 일부라도 materialize되거나 tracked implementation이 존재한 뒤 차단되면 기술적으로 실행 가능한 focused tests, frozen-pre/post invariance, protected-surface non-mutation, candidate re-audit와 materializer Run A/B digest comparison을 실행한다. Complete-only assertions는 `N/A — blocked`로 기록한다.
- Required authority, owner judgment 또는 실행 환경이 없어 수행하지 못한 in-scope axis는 `unvalidated_but_in_scope`에 기록하며 `complete`를 주장하지 않는다.

---

### Change 4 — Deterministic Recipe locale owner projection

**Purpose:**

QG registry를 T1이 소비할 수 있는 최소 exact identity-keyed owner output으로 투영하되 Layer 4 identity source와 runtime payload를 변경하지 않는다.

**Files:**

- `Iris/tooling/src/iris_tooling/domains/layer4/tooltip_t1_d4.py`
- `Iris/tooling/src/iris_tooling/domains/layer4/cli.py`
- `Iris/build/description/v2/data/tooltip_t1_layer4_recipe_locale_owner_input.json` (new)
- `Iris/_docs/authority/tooltip_t1/layer4_recipe_locale_input_contract.json` (new)
- `Iris/build/ENTRYPOINTS.md` (read-only command-owner input)

**Implementation Notes:**

Materializer는 approved registry와 frozen current identity input만 읽고 deterministic canonical JSON을 생성한다. Owner output에는 T1 lookup에 필요한 exact identity, same-fact binding, KO/EN surface와 authority ref만 포함한다. FullType별 prose copy를 만들지 않는다.

Input contract는 다음을 고정한다.

- source는 `recipe` identity만 허용
- locale set exactly `ko`, `en`
- current identity owner input에 존재하는 exact identity만 허용
- D4 complete candidate에서는 frozen selected unique identity와 exact key-set equality
- selected instance 전체가 같은 identity record로 resolve
- no cross-locale fallback
- no source substitution
- canonical file hash, registry hash, source identity hash와 count binding

`upstream_usecases_by_fulltype.json`은 byte-identical하게 보존한다. Retired `usecase_label_map.json`을 수정하거나 current authority로 채택하지 않는다.

**Validation:**

- canonical materialization Run A/B byte identity
- owner projection key order/digest determinism
- registry -> owner output semantic binding loss `0`
- frozen selected identity missing output `0` for complete candidate
- unselected Recipe 또는 Right-click record accidental inclusion `0`
- identity owner input hash delta `0`
- runtime/generated payload hash delta `0`

---

### Change 5 — Post-selection T1 locale lookup and contract adoption

**Purpose:**

Current T1이 selected Recipe identity freeze 후 separate QG locale owner output을 lookup하도록 만들고, current optional embedded-field seam을 명시적 owner route로 교체한다.

**Files:**

- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/projection.py`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/models.py`
- `Iris/_docs/authority/tooltip_t1/layer4_tooltip_projection_contract.json`
- `Iris/_docs/authority/tooltip_t1/tooltip_locale_menu_parity_contract.json`
- `Iris/_docs/authority/tooltip_t1/tooltip_readiness_reason_registry.json`
- Tooltip T1 focused tests and fixtures

**Implementation Notes:**

처리 순서를 코드와 contract에서 다음처럼 고정한다.

```text
current identity candidates
-> eligibility/order/dedupe/source-equivalence/capacity
-> selected identity freeze
-> if recipe: exact Recipe locale owner lookup
-> if rightclick: existing exact translation route lookup
-> locale readiness
-> Menu identity relation
```

`Layer4Candidate`를 selection-only value object로 만든다. 현재의 `localized_surfaces`와 `menu_consumer_identity_ref` field를 제거하고, `select_layer4`/`selection_identity`/`verify_invariants` 호출 그래프에는 locale owner output, Right-click translation map 또는 Menu evidence를 전달하지 않는다. Locale/Menu readiness는 selected tuple이 완성된 뒤 별도 resolver가 source별 authority route로 조회한다.

역방향 data flow도 금지한다. Locale-bearing post-selection object인 `Slot` 또는 동등한 resolved/readiness object는 selection 호출 그래프의 입력 type이 될 수 없고, selection API는 identity-only candidate collection만 받는다.

Production identity input에 embedded `display_by_locale`가 나타나면 new Recipe locale authority로 인정하거나 조용히 무시하지 않고 authority-ceiling 위반으로 fail-loud한다. Fixture도 candidate embedded field를 사용하지 않고 실제 production post-selection resolver API를 통과한다. 따라서 locale independence는 readiness masking behavior에만 의존하지 않고 type/API 구조로 보장한다.

Missing Recipe locale은 기존 reason `LOCALE_SELECTED_SURFACE_MISSING`을 유지한다. Right-click ready surface가 있어도 Recipe slot을 대체하지 않는다. 한 locale 누락 시 다른 locale을 복사하지 않는다.

**Validation:**

기존 parameterized family에 다음 네 composite rows를 추가한다. 한 row는 관련 불변식을 함께 assertion해 개별 test identity 증가를 피한다.

1. **selection independence:** selected Recipe missing, unselected Recipe 또는 Right-click ready, readiness-map permutation에서도 selected identity/source/order와 correction이 유지된다.
2. **locale pair:** KO-only와 EN-only subcase가 각각 반대 locale correction을 유지하고 fallback하지 않는다.
3. **identity relation:** cross-identity same text는 merge하지 않고 same identity/multiple FullTypes는 한 authoritative pair로 일관되게 resolve한다.
4. **authority/type guard:** missing semantic/locale mapping, embedded `display_by_locale`, locale-bearing post-selection object의 reverse flow는 각각 fail-loud한다.

Existing `both`, Recipe-only, Right-click-only, capacity, duplicate, ineligible와 permutation selection tests는 유지한다. 기존 readiness-mask test는 embedded candidate field를 masking하는 형태로 유지하지 않고, production resolver의 locale map 변화가 frozen selection output에 도달할 수 없음을 검증하는 구조/API test로 대체한다.

---

### Change 6 — Independent identity/source/non-target invariance validation

**Purpose:**

D4 producer나 updated T1 audit의 self-assertion에만 의존하지 않고 pre/post normalized records를 독립 비교한다.

**Files:**

- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/d4_invariance.py` (new)
- existing Tooltip T1 parameterized test files
- repository-external comparison artifacts

**Implementation Notes:**

Comparator의 pre-side는 Change 1이 mutation 전에 생성하고 receipt로 봉인한 frozen selected-record artifact 하나만 사용한다. Post-side만 corrected subject의 current selector에서 새로 산출한다. Post-change selector를 pre-side에도 실행하거나 pre record를 재구성하는 대체 경로를 허용하지 않는다. 이 comparator는 D4 producer와 분리돼 있지만 같은 Tooltip T1 domain 안에 있으므로 `producer-separated` claim만 하며 domain-independent review/validation으로 확대하지 않는다. 다음 relation을 exact compare한다.

```text
FullType + slot_id + source_type + selected identity + order/result identity
Recipe-only / Right-click-only / both / none distribution
identity owner input bytes/hash
Right-click surface route bytes/hash
runtime Layer 4 consumer identity set
non-target Layer 4 rows
Layer 2 / Layer 3 inputs
runtime/static Tooltip payload
```

Selection record는 normalized canonical bytes가 identical해야 하며 aggregate SHA-256도 동일해야 한다. Surface file이 추가된 사실은 selection tuple에 포함하지 않는다.

**Validation:**

- selected Recipe identity delta `0`
- selected Right-click identity delta `0`
- slot/source/order identity delta `0`
- selected source distribution delta `0`
- same-identity identity-keyed structural resolution divergence `0`
- locale-dependent reselection `0`
- cross-source substitution `0`
- cross-locale fallback `0`
- non-target semantic mutation `0`
- runtime/static payload mutation `0`
- pre artifact hash가 Change 1 receipt와 불일치한 경우 fail-loud

`same-identity identity-keyed structural resolution divergence = 0`은 identity-keyed unique owner record가 제공하는 structural invariant를 selected instance 전체에서 재확인하는 검사다. 서로 독립적인 per-FullType surface가 우연히 같다는 empirical 비교로 주장하지 않는다.

---

### Change 7 — Workstream candidate freeze and owner ratification

**Purpose:**

Isolated D4 candidate를 freeze하고 QG owner ratification을 registry, projection, shared-path delta와 claim ceiling에 결속한다. Global current adoption은 수행하지 않는다.

**Files:**

- `Iris/_docs/authority/qg/tooltip_t1_d4_decision_ratification.schema.json` (new)
- repository-external `d4_prevalidation_owner_ratification_receipt.json`
- repository-external `d4_shared_path_delta.json`
- repository-external `d4_parallel_integration_manifest.json`

**Implementation Notes:**

Changes 1~6의 owner registry/projection과 isolated shared-path delta를 먼저 완성한다. Current manifest, route index, command owner와 governance docs는 frozen read-only inputs로 hash-bind한다. D4가 이 경로들을 갱신하거나 candidate PASS를 current product status로 기록하지 않는다.

그 다음 D4 workstream candidate를 dedicated clean worktree에서 freeze하고 exact commit/tree, input/contract/shared-delta hashes를 결속한다. 다른 병렬 workstream이나 dirty main을 reset/stash/clean하지 않는다.

QG/product owner는 repository-external pre-validation ratification receipt로 다음을 승인한다.

```text
exact workstream candidate commit/tree
QG D4 registry and owner projection hash
Tooltip T1 shared-path delta hash
strict closure / no fallback / no reselection disposition
validation and claim ceiling
```

Receipt가 없거나 candidate subject와 다르면 final validation을 시작하지 않고 `implemented_only` 또는 `blocked`로 남긴다. Ratification 뒤 D4-owned tracked authority proposal이나 shared-path delta를 수정하면 receipt와 subject가 무효화되며 최소 candidate freeze, ratification과 affected-range validation을 새 subject에서 다시 수행한다.

**Validation:**

- workstream candidate와 shared-path delta가 freeze 전에 완료됨
- exact clean worktree tracked status clean
- decision/registry/contract/document hashes가 ratification receipt와 일치
- owner identity와 approval scope가 schema를 충족
- protected global current/governance path mutation `0`
- pre-validation ratification 후 tracked mutation `0`

---

### Change 8 — Candidate re-audit, correction reconciliation, owner seal and bundle closeout

**Purpose:**

Owner-ratified workstream candidate에서 affected/whole-T1 candidate re-audit와 focused validation을 수행하고 D4 bundle을 봉인한다. Integrated canonical validation은 D6가 수행한다.

**Files:**

- existing installed Tooltip T1 producer/audit path
- repository-external successor T1 audit root
- repository-external D4 reconciliation/validation/owner-seal/closeout artifacts

**Implementation Notes:**

Ratified final subject에서 whole-T1 audit를 재실행하고 initial D4 correction rows를 exact `FullType + slot + identity + locale`로 reconcile한다.

Complete candidate에서는:

```text
initial D4 target retired by approved exact locale binding
= frozen initial D4 target count

remaining LOCALE_SELECTED_SURFACE_MISSING for D4 Recipe scope
= 0

replacement blocker
= 0

other-owner movement caused by D4
= 0
```

Other T1-C corrections는 owner/reason/count/exact identity 기준으로 비교하되, D1/D3 등 다른 workstream의 정당한 변화는 frozen integration subject에 이미 포함되어야 한다. Comparator는 모든 other-owner delta를 자동 실패로 만들지 않고 provenance/input hash로 `D4-caused`, `pre-integrated external`, `unattributed`를 구분한다. `D4-caused` 또는 `unattributed` movement는 fail-loud하며, post-freeze concurrent mutation은 subject mismatch다.

Same workstream subject에서 focused tests, candidate invariant와 materializer Run A/Run B digest comparison을 실행한다. Candidate와 receipts의 subject/hash가 모두 일치할 때만 D4 bundle closeout을 완성한다.

Candidate validation closeout이 생성되면 QG/product owner가 같은 workstream subject, pre-validation ratification receipt와 closeout SHA-256에 결속된 terminal owner seal을 발행한다. D4 bundle은 이 seal까지 검증하며 global manifest/route/command/governance files를 수정하지 않는다.

Blocked/implemented-only 경로도 차단 시점에 맞는 검증을 기록한다. Mutation 전 read-only 차단이면 baseline/census/registry axes를 실행하고 materialization/complete-only axes는 `N/A — blocked before implementation`로 분류한다. 일부 구현이 materialize된 뒤 차단이면 technically available focused tests, frozen-pre/post comparator, protected-surface non-mutation, candidate re-audit와 deterministic materializer Run A/B를 실행한다. Required authority 또는 환경이 없어 실행하지 못한 in-scope 축은 `unvalidated_but_in_scope`로 남긴다.

`d4_axis_separated_closeout_record.json`은 `EXECUTION_CONTRACT.md` §6-2와 §7-2에 맞춰 각 검증/claim axis를 정확히 다음 세 범주 중 하나로 emit한다.

```text
validated
out_of_scope
unvalidated_but_in_scope
```

`unvalidated_but_in_scope`가 하나라도 있으면 그 영역의 PASS/complete claim을 금지하고 terminal state와 next gate에 반영한다.

**Validation:**

- current T1 audit exit `0`
- D4 exact correction reconciliation complete
- D4 target reason/cause 이동 `0`
- D4-caused 또는 unattributed other-owner correction movement `0`
- T2 handoff count remains `0` while any blocking correction remains
- candidate/artifact/receipt subject mismatch `0`
- materializer Run A/B canonical bytes equal and bundle validator exit `0`
- terminal owner seal이 exact subject + decision ratification + machine closeout hash와 일치
- closeout axis가 `validated` / `out_of_scope` / `unvalidated_but_in_scope`로 완전 분류되고 validation ceiling이 명시됨
- validated machine subject의 machine-relevant tracked mutation `0`
- predecessor artifact mutation `0`

---

### Change 9 — Produce the D6 integration proposal

**Purpose:**

Package the D4 result, shared-path delta and governance/current-route proposals for T1-D6 without changing tracked global status.

**Files:**

- repository-external `d4_parallel_integration_manifest.json`
- repository-external `d4_shared_path_delta.json`
- D4 owner seal, closeout and artifact hashes

**Implementation Notes:**

Change 8의 external closeout과 terminal owner seal을 common bundle envelope에 결속한다. D6가 적용할 current route/governance successor 문구는 proposal로만 포함하며 tracked files를 수정하지 않는다.

**Validation:**

- bundle subject와 모든 receipt/closeout/seal hash가 integration manifest와 일치
- global current/governance tracked delta `0`
- proposal이 current adoption 완료를 주장한 count `0`
- `validated` / `out_of_scope` / `unvalidated_but_in_scope` ceiling 누락 `0`
- broken local reference 또는 malformed SHA-256 `0`
- D6-exclusive tracked file delta `0`

---

## 7. Validation Plan

### Automated Validation

#### Focused contract and D4 validation

Implementation 후 current Windows/PowerShell 환경에서 installed tooling source를 다음 범위로 검증한다.

```powershell
uv run --project .\Iris\tooling python -B -m pytest .\Iris\tooling\tests\test_tooltip_t1_contract.py .\Iris\tooling\tests\test_tooltip_t1_projection.py .\Iris\tooling\tests\test_tooltip_t1_audit.py -q
```

필수 검증 축:

- schema and authority binding
- exact target reconstruction
- denominator independence
- `QG/locale` total vs D4 Recipe-filtered set/count/hash separation
- deterministic owner projection
- selected tuple identity invariance
- source distribution invariance
- selection-only candidate type; embedded locale/Menu readiness fields unavailable
- locale-bearing `Slot`/post-selection object의 selection call graph 역유입 불가
- production identity input embedded `display_by_locale` cannot satisfy Recipe readiness
- embedded `display_by_locale`는 normal missing-surface correction이 아니라 authority-ceiling violation으로 별도 보고
- KO/EN completeness and NFC/single-line checks
- same-fact semantic binding metadata
- no fallback / no reselection / no substitution
- same-identity reuse consistency
- cross-identity non-merge
- non-target and runtime/static payload non-mutation
- correction reconciliation
- decision ratification, final subject and terminal owner-seal binding
- closeout axis의 `validated` / `out_of_scope` / `unvalidated_but_in_scope` three-way emission과 claim ceiling

#### Immutable candidate and whole-T1 re-audit

- Isolated candidate는 current command-owner contract를 read-only로 준수하며 branch-installed tooling을 사용한다.
- output은 repository-external empty root에만 생성한다.
- Pre-side는 Change 1 frozen baseline만 사용하고 post-side만 final corrected subject에서 산출해 normalized selected tuple과 correction ledger를 비교한다.
- blocked progression에서는 T2 handoff input/manifest가 생성되지 않는지 검사한다.
- mutation 전 read-only blocked path는 frozen baseline/census/registry validation을 실행하고 complete-path materialization/complete-only assertion을 `N/A — blocked before implementation`로 명시한다.
- partial materialization 또는 tracked implementation이 존재하는 blocked path는 technically available focused tests, frozen-pre/post invariance, protected-surface non-mutation, candidate re-audit와 materializer Run A/B digest comparison을 실행한다.
- D6-exclusive current/governance paths의 tracked delta가 없는지 검사한다.
- Change 9 integration manifest가 workstream subject/receipt/closeout/seal identity를 정확히 결속하는지 검사한다.

#### Integrated canonical validation ownership

- D4는 materializer candidate Run A/B bytes와 bundle integrity를 검증한다.
- Receipt-bound canonical Run A/B, repository comparator, fresh integrated environment authority와 post-gate finalizer는 T1-D6가 모든 bundle을 병합한 exact subject에서 한 번 실행한다.
- D4 owner ratification/terminal seal은 bundle에 결속되어 D6가 재검증할 수 있어야 한다.

이 계획에 직접 채택한 fail-closed execution constraint에 따라 relevant exact command가 exit `0`일 때만 PASS를 주장한다. Required tooling이나 immutable environment/owner receipt가 없으면 PASS 대신 `BLOCKED`로 보고한다. 이 constraint의 session source는 `AGENTS.md`지만 product semantic authority로 취급하지 않는다.

각 automated/manual/owner/environment axis는 `d4_axis_separated_closeout_record.json`에서 `validated`, `out_of_scope`, `unvalidated_but_in_scope` 중 하나로 완전 분류한다. Required tooling, immutable environment 또는 owner judgment가 없어 in-scope axis를 실행하지 못하면 이를 `out_of_scope`로 축소하지 않으며, 해당 축을 `unvalidated_but_in_scope`로 기록하고 그 영역의 PASS와 D4 `complete`를 금지한다.

### Manual Validation

- QG owner가 각 canonical semantic reference, KO surface, EN surface와 same-fact relation을 검토한다.
- 계획 시점 10개 consume/keep divergence identity를 우선 확인한다.
- recommendation, frequency, efficiency, importance, preferred-choice 의미가 추가되지 않았는지 검토한다.
- KO와 EN이 각각 canonical fact를 정확히 표현하고 서로 같은 의미인지 owner가 판단한다. Machine binding만으로 semantic equivalence PASS를 발급하지 않는다.
- Current width-advisory contract 아래 문장이 불필요하게 장황하지 않은지 검토하되 numeric character/byte/pixel PASS 기준을 만들지 않는다.
- cross-identity identical text가 있는 경우 identity binding이 분리돼 있는지 확인한다.
- unresolved identity가 다른 owner/cause로 조용히 이동하지 않았는지 correction reconciliation을 검토한다.
- docs/authority manifests가 actual machine receipts보다 넓은 claim을 하지 않는지 확인한다.

### Validation Limits

D4 실행에서는 다음을 검증하지 않는다.

- actual PZ runtime render
- actual Alt Tooltip activation/behavior
- pixel/font/UI-scale 또는 4-line visual fit
- character/byte/pixel 기반 Recipe sentence fit certification; current hard gate는 single logical line과 CR/LF 금지뿐이며 actual width는 T3
- automated KO/EN semantic equivalence certification; 이는 QG owner review axis
- full Menu/Tooltip visual parity
- runtime/static Layer 4 generation correctness beyond non-mutation
- package/install correctness
- multiplayer 또는 long-session runtime
- arbitrary external-mod compatibility
- Runtime Compatibility certification
- Publish/release/Workshop/deployment readiness
- 전체 Iris localization quality
- 전체 T1-C blocker closure 또는 T2 production readiness

따라서 positive claim은 validated offline Recipe locale authority와 T1 re-audit scope를 넘지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

**Touched — bounded QG Recipe locale authority and Tooltip T1 input contract.**

새 exact identity-keyed QG owner registry/projection과 T1 adoption contract를 추가한다. Recipe Evidence, `rule_id`, selected identity, selection policy와 Right-click authority는 변경하지 않는다.

### Runtime Behavior Surface

**None intended.**

D4는 runtime Lua와 static Tooltip payload를 생성·설치하지 않는다. Runtime tree hash delta가 발생하면 closeout을 중단한다.

### Compatibility Surface

**None expected.**

외부 API, PZ integration 또는 external mod contract를 변경하지 않는다. Offline owner input이 추가되는 범위만 다룬다.

### Sealed Artifact Surface

**Touched additively.**

새 corrected candidate audit/ledger/closeout과 owner seal을 bundle에 추가하며 predecessor external roots와 historical artifacts는 immutable하게 보존한다. Global successor adoption과 status carrier는 D6가 소유한다.

### Public-Facing Output Surface

**Touched at offline authority level.**

KO/EN user-facing surface가 승인되므로 public-facing content authority가 바뀐다. 다만 D4는 이를 runtime package에 생성·설치하지 않으므로 actual in-game output change는 주장하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- locale surface를 current identity input에 직접 삽입하면 현재 authority ceiling과 owner 분리가 무너질 수 있다.
- locale/Menu readiness field가 `Layer4Candidate`에 남으면 selection이 값을 현재 읽지 않더라도 future regression seam이 유지된다.
- retired `usecase_label_map` 또는 runtime Recipe text를 재사용하면 predecessor/downstream output이 semantic authority로 역승격될 수 있다.
- D4 전용 registry가 QG 전체 data model의 새 master authority로 과도하게 확장될 수 있다.

Mitigation: separate bounded owner output, selection-only candidate type, embedded locale-field fail-loud, explicit contract ceiling, protected current-manifest hash와 D4-only schema scope를 사용한다.

### Runtime Risk

- intended runtime mutation은 없지만 broad generation command나 live-tree writer가 잘못 실행되면 Chunk/translation/runtime Lua가 바뀔 수 있다.

Mitigation: repository-external output only, protected runtime hash freeze, no generation/install route와 immediate stop condition을 둔다.

### Compatibility Risk

- Recipe locale lookup이 Right-click translation route나 Browser consumer identity relation을 덮으면 source independence가 깨질 수 있다.
- locale owner output이 candidate selection에 전달되면 readiness-aware selection이 생길 수 있다.

Mitigation: source-specific post-selection lookup, readiness-free selection API, production-route negative fixtures, selected tuple/source distribution exact comparator를 사용한다.

### Regression Risk

- same identity를 여러 FullType에 적용하면서 실제 semantic divergence를 한 문장으로 숨길 수 있다.
- KO/EN이 자연스럽지만 서로 다른 condition/outcome을 표현할 수 있다.
- correction count가 다른 reason/owner로 이동해 수치만 0이 될 수 있다.
- hard-coded 266/444/888 count가 current subject 변화에서 stale authority가 될 수 있다.
- identity file과 new locale file hash를 함께 갱신하면서 selection mutation을 놓칠 수 있다.
- post-change selector를 pre/post 양쪽에 실행하면 selector regression이 상쇄될 수 있다.

Mitigation: instance-level semantic matrix, owner review, same-fact binding, dynamic exact census, immutable frozen pre artifact와 post-only recomputation, whole-ledger reconciliation을 사용한다.

### Operational Risk

- dirty main에서 lifecycle evidence를 생성하면 exact subject claim이 불가능하다.
- candidate wheel/environment와 source tree가 다르면 focused/bundle validation이 다른 subject에 귀속될 수 있다.
- unresolved identity를 빠르게 끝내기 위해 Recipe name 기반 prose를 작성할 유인이 크다.
- final validation 뒤 workstream subject나 bundle manifest를 직접 수정하면 validated identity가 흐려진다.
- D6 integration proposal을 adopted current authority나 D4 machine receipt로 오인하면 검증 근거가 왜곡된다.
- D1/D3 mutation이 final freeze 뒤 섞이면 other-owner delta attribution이 불가능해진다.

Mitigation: common predecessor의 dedicated clean worktree, owner ratification, hash-bound candidate/materializer Run A/B, protected global path no-mutation과 strict blocked disposition을 사용한다.

---

## 10. Rollback Plan

Rollback의 mutation boundary는 D4에서 추가한 QG Recipe locale registry/projection, isolated T1 locale binding code/contracts와 shared-path proposal이다.

### Before owner adoption

- repository-external census/review candidate만 폐기한다.
- tracked identity input, runtime payload와 predecessor audit는 변경하지 않는다.

### After owner registry/projection candidate creation

- D4에서 추가한 registry records와 generated owner output을 해당 change 단위로 되돌린다.
- `layer4_recipe_locale_input_contract.json` proposal과 D4 shared-path delta를 함께 되돌린다.
- `upstream_usecases_by_fulltype.json`, Recipe Evidence, `rule_id`, selection ordering과 Right-click data는 rollback 대상이 아니다.

### After isolated T1 candidate integration

- `audit.py`/`contract.py`의 proposed separate Recipe locale lookup delta를 되돌리고 isolated candidate input에서 new owner output을 제거한다.
- predecessor T1 behavior와 external artifacts를 복원 source로 덮어쓰지 않는다. Git predecessor와 immutable receipt identity를 사용한다.

### Documentation and closeout

- 잘못된 successor claim은 predecessor 문서를 rewrite하지 않고 additive correction record로 정정한다.
- failed/blocked execution artifact는 failure evidence로 보존하되 D6 adoption input으로 표시하지 않는다.
- pre-validation owner ratification 뒤 rollback이 필요하면 해당 exact candidate를 complete로 채택하지 않고 새 successor candidate/ratification을 만든다. Ratified tracked subject를 validation 후 조용히 수정하지 않는다.
- terminal owner seal과 external bundle은 global current authority를 쓰거나 되돌리는 writer가 아니다.

### Immediate stop conditions

다음 중 하나라도 발생하면 D4 complete adoption을 중단한다.

```text
selected Recipe identity delta != 0
selected Right-click identity delta != 0
slot/source/order identity delta != 0
selected source distribution delta != 0
identity owner input hash delta != 0
runtime/static payload hash delta != 0
same-identity semantic or surface divergence != 0
cross-locale fallback detected
locale-dependent reselection detected
cross-source substitution detected
non-target semantic mutation detected
replacement blocker detected
D4-caused or unattributed other-owner movement detected
candidate Run A/B bytes differ or bundle validator exit != 0
subject/hash binding mismatch
pre-validation owner ratification missing or mismatched
terminal owner seal missing or mismatched
validated machine subject mutation after final validation
protected global current/governance path mutation detected
D6 integration proposal reassigns D4 machine subject/receipt identity
```

Semantic collision이나 insufficient evidence가 발견되면 해당 identity surface adoption을 중단한다. D4는 identity split, representative meaning selection, Recipe-name inference 또는 false owner reassignment로 해결하지 않는다.

---

## 11. Governance Constraints

- `Philosophy.md`의 Iris 근거성, 중립성, no-inference, no-recommendation, menu/tooltip same-fact와 100% Lua runtime 원칙을 보존한다.
- Pulse/Hub-and-Spoke/SPI 경계를 변경하지 않는다. D4는 Iris 내부 offline tooling/data 작업이다.
- Recipe와 Right-click을 독립적이고 동등한 Source로 유지한다.
- identity selection을 locale/Menu readiness보다 먼저 freeze한다.
- `Layer4Candidate`와 selection API를 locale/Menu-readiness-free 구조로 유지한다.
- current QG authority 밖의 의미를 Recipe 이름, key, runtime/historical output에서 만들지 않는다.
- KO와 EN은 exact same identity와 canonical semantic reference에 결속하며 cross-locale fallback을 금지한다.
- same identity reuse는 semantic equality가 확인된 경우에만 허용한다.
- 다른 identity는 text가 같아도 merge하지 않는다.
- current identity input의 locale-authority ceiling을 우회하지 않는다.
- retired label-map converter, description-tree direct writer와 repository-local generated output fallback을 current route로 복원하지 않는다.
- runtime/build-time boundary를 유지하고 D4에서 runtime Lua 또는 static Tooltip payload를 생성하지 않는다.
- minimal diff와 additive amendment를 우선하며 predecessor/sealed artifacts를 rewrite하지 않는다.
- exact subject, environment, input, contract, output과 receipt hash를 결속한다.
- workstream owner registry/projection과 shared-path delta를 candidate validation 전에 완료하고 QG owner ratification에 결속한다.
- global current authority/docs adoption과 status synchronization은 D6에 유보한다. D4는 external owner seal/closeout과 integration proposal만 생성한다.
- 모든 closeout axis를 `validated`, `out_of_scope`, `unvalidated_but_in_scope`로 분류하고 `unvalidated_but_in_scope` 영역의 PASS/complete claim을 금지한다.
- lifecycle evidence를 regular validation authority로 승격하지 않는다.
- fail-closed validation을 적용한다. Required exact command exit `0` 없이는 PASS를 주장하지 않는다.
- D4 correction closure를 전체 T1-C 완료, T2 OPEN, Menu parity, runtime fit, package, RTC, Publish 또는 release readiness로 확대하지 않는다.
- 사용자의 기존 dirty worktree 변경을 덮어쓰거나 정리하지 않는다.

---

## 12. Expected Closeout State

### Planning-time expected closeout

**Conditional target: `complete` under strict full closure.**

계획 시점에 이미 관측된 consume/keep divergence identity를 포함해 모든 selected identity가 하나의 canonical fact로 owner-disposition되고, exact candidate ratification과 final machine/owner seal이 모두 성립할 때만 `complete`를 기대한다. 하나라도 성립하지 않으면 expected terminal state는 `blocked` 또는 `implemented_only`다.

다음 조건이 모두 만족될 때만 D4를 `complete`로 닫는다.

```text
all frozen selected Recipe identities
have one owner-approved canonical semantic binding
+ explicit KO surface
+ explicit EN surface

remaining LOCALE_SELECTED_SURFACE_MISSING
for frozen D4 Recipe scope = 0

selected identity/source/slot/order delta = 0
source distribution delta = 0
selection candidate locale/Menu readiness fields = absent
fallback/reselection/substitution = 0
same-identity identity-keyed structural binding divergence = 0
non-target/runtime mutation = 0
replacement blocker = 0
D4-caused or unattributed other-owner movement = 0

focused tests + candidate re-audit
+ materializer Run A/B bytes equal + bundle validator exit 0

pre-validation owner ratification
+ terminal owner seal = valid for the same exact subject

validated machine subject mutation after final validation = 0
global current/governance path mutation = 0
validation axes classified as validated/out_of_scope/unvalidated_but_in_scope = 100%
current_ecosystem_adoption = pending_T1_D6
new test files/functions = 0 unless the one-function exception is justified
```

Canonical meaning 또는 pair approval이 불가능한 identity가 남으면:

- approved/resolvable records와 tooling 구현은 보존할 수 있다.
- exact unresolved identities와 owner evidence gap을 closeout에 기록한다.
- D4 status는 `blocked` 또는 `implemented_only`다.
- target correction을 0으로 주장하지 않는다.
- 별도 governing owner decision 없이 `partial`을 terminal success로 사용하지 않는다.

### Expected successful D4 claims

검증이 성공하면 다음 bounded claim만 허용한다.

```text
selected Recipe identity mapping was preserved
selected source/slot/order mapping was preserved
selected source distribution was preserved

validated Recipe KO/EN surfaces are bound
to exact Recipe identities and the same canonical QG semantic references

cross-locale fallback = 0
locale-dependent reselection = 0
cross-source substitution = 0
same-identity identity-keyed structural resolution divergence = 0
non-target semantic mutation = 0
embedded candidate locale authority path = absent

QG/locale total and D4 Recipe-filtered target
were reported as separate exact sets

LOCALE_SELECTED_SURFACE_MISSING
for the validated frozen D4 Recipe scope = 0
```

### Explicitly not established

D4만으로 다음을 주장하지 않는다.

```text
all T1-C blockers = 0
T2_FULL_DATA_PROGRESSION = OPEN
production T2 handoff complete

Layer 4 runtime generation complete
Menu/Tooltip visual parity complete
IrisAltTooltip runtime complete
4-line visual fit complete
Recipe sentence width/length certification complete
automated KO/EN semantic-equivalence certification complete

package/install correctness
Runtime Compatibility PASS
Publish Boundary PASS
release/Workshop/deployment readiness
full Iris localization quality certification
```

다른 T1-C owner blocker가 남아 있으면 D4 `complete`와 무관하게 progression은 `BLOCKED_BY_UPSTREAM_CORRECTIONS`이고 production T2 handoff는 0을 유지한다.
