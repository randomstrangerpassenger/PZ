# Implementation Plan

Iris Layer 4 상호작용 밀도 적응형 표시 체계

> 2026-08-20 IAR retirement Walkthrough synchronization: product outcome은 `FULL_RETIREMENT`, Layer 1–5 active product IAR consumer와 residual allowlist는 모두 `0`이다. closeout readpoint는 main `c91d8f79`, terminal implementation subject `6f362b5e`, full-gate subject `c924349e`다. DVF 3.3은 R2-B immutable generation + `IrisLayer3DataCurrent.lua` single pointer로 전환됐지만 이 successor는 Layer 3 전용이다. Layer 4 generated mutation에는 QG owner의 별도 deterministic complete-generation/stateless-validation/safe-install contract와 별도 owner decision이 필요하며 DVF 3.3 installer/descriptor를 자동 일반화하지 않는다. Presentation/UI scope와 기존 ratification gate는 그대로다.

> 상태: CLD Round 4 Important 2건·Minor 2건 반영 / proposed / `L4-RAT-08` pending / Recipe fallback cutover blocked by planning census (`recipe_only=3`, all `qg_decided_no`) / implementation not authorized / independent review pending
>
> 이 계획 수정 요청은 문서 보강 승인이다. 아래 owner-reserved presentation decision, runtime behavior 변경, Layer 4 generated installation 또는 canonical document promotion의 owner seal로 해석하지 않는다. Retirement closeout은 RTC PASS, Publish PASS, release readiness 또는 owner-sealed canonical closure를 제공하지 않았다.

## 1. Objective

Iris Menu의 Layer 4 상호작용 표시를 현재의 일률적인 접힌 평면 목록에서 interaction 수와 조회 상태에 따라 달라지는 결정론적 presentation으로 교체한다.

owner policy seal과 source migration gate 뒤 구현이 허가되면 다음 하나의 계약이 저밀도와 고밀도 항목을 함께 설명해야 한다. planning-time `recipe_only=3`이 해소되기 전에는 Change 2 이후 policy-dependent 구현, QG-only Recipe cutover와 full completion을 진행하지 않는다.

- `0`: authoritative lookup이 정상 완료된 verified-empty 상태를 명시적으로 표시한다.
- `1`: 전체 interaction과 Recipe requirement를 추가적인 section 펼치기 없이 바로 표시한다.
- `2~8`: 전체 interaction을 Source별 열린 목록으로 바로 표시한다.
- `9+`: total과 Source별 count를 먼저 표시하고, compact 상태에서 전체 목록으로 진입할 수 있게 한다.
- dense 목록을 연 뒤에는 literal local search, Source section, 기존 Detail 외부 scroll을 통해 모든 interaction에 접근할 수 있게 한다.
- Recipe와 Right-click을 독립적이고 동등한 Source로 보존하고 대표 항목 선정, 중요도 순위, 의미 추론 기반 grouping을 도입하지 않는다.
- Recipe requirement는 원래 Recipe row에만 결속하며 item-global 조건으로 승격하지 않는다.
- lookup/data fault를 verified-empty로 바꾸지 않는다.

이 변경은 QG의 Layer 4 의미 생산물을 수정하는 작업이 아니다. `docs/ARCHITECTURE.md`가 Browser/Wiki에 부여한 sort/fold/layout/density 책임 안에서, sealed QG line을 읽는 private runtime presentation projection과 Menu renderer를 구현하는 작업이다.

### Proposed Presentation Contract — Owner Seal Pending

이 계획은 첨부 로드맵에서 미결정으로 남은 항목을 다음과 같이 제안한다. 표의 proposal은 owner가 exact 항목을 명시적으로 ratify하기 전까지 current decision, sealed policy 또는 구현 권한이 아니다.

| Ratification ID | Owner-reserved decision | Proposed contract | Seal status |
|---|---|---|---|
| `L4-RAT-01` | Density threshold | `0 / 1 / 2~8 / 9+`의 네 상태 | `pending_owner_seal` |
| `L4-RAT-02` | Policy owner | Browser의 private runtime presentation projection; 새 semantic/sealed presentation-policy artifact 없음 | `pending_owner_seal` |
| `L4-RAT-03` | Grouping axis | Source만 사용; Recipe와 Right-click의 peer section | `pending_owner_seal` |
| `L4-RAT-04` | Source order | Recipe, Right-click의 고정 presentation order; 중요도 의미 없음 | `pending_owner_seal` |
| `L4-RAT-05` | Row order / completeness | QG line order 보존; stable identity-set 및 visible/hidden union parity | `pending_owner_seal` |
| `L4-RAT-06` | Dense access / requirement density | compact-by-default, literal search, single outer-scroll; single/small requirement 즉시 표시, dense row-local fold | `pending_owner_seal` |
| `L4-RAT-07` | Locale / Tooltip / package boundary | cross-locale base order 불변; Tooltip regression-only; disposable package projection 포함 | `pending_owner_seal` |
| `L4-RAT-08` | Legacy-only Recipe authority disposition | fresh `qg_absent`/`qg_decided_no` tuple별 `preserve_legacy` / `separate_legacy_removal_scope` / category별 `separate_qg_authority_scope`; 앞의 두 선택은 producer-index denominator를 바꾸지 않아 Gate 3을 계속 닫으며, 어느 선택도 QG decision을 변경하거나 migration gate를 우회하지 않음 | `pending_owner_disposition` |

### Execution Authorization Gates

이 계획은 다음 gate를 순서대로 적용한다.

1. **Pre-seal ceiling**
   - 허용: read-only census, capability/Recipe↔QG crosswalk/parity report, lookup invocation characterization, candidate validator/test 설계, stable-ID만 추가하는 isolated off-live data-contract plumbing candidate, staging decision packet 작성.
   - 금지: runtime/public behavior mutation, current generated Layer 4 artifact mutation, `DECISIONS.md`/`ARCHITECTURE.md`/`ROADMAP.md` canonical write.
2. **Owner policy seal**
   - owner가 `L4-RAT-01`~`L4-RAT-07`의 exact disposition을 명시적으로 제공하고 그 identity가 staging decision packet에 결속돼야 policy proposal을 current contract 후보로 사용할 수 있다.
   - fresh census에 `qg_absent` 또는 `qg_decided_no`가 있으면 owner가 `L4-RAT-08`의 exact tuple별 disposition을 제공해야 한다. 이 disposition은 책임 경계를 정할 뿐 Gate 3을 통과시키거나 QG decision을 변경하지 않는다.
   - 수정본 계획을 작성하거나 검토받은 사실만으로 owner seal을 만들지 않는다.
3. **Source migration readiness**
   - current subject의 fresh structured crosswalk에서 `capability_only == 0 AND recipe_only == 0`이어야 legacy presentation fallback removal이 허가된다.
   - 모든 `recipe_only` tuple을 `identity_unavailable`, `qg_absent`, `qg_decided_no` 중 정확히 하나로 분류하고 category별 책임/disposition evidence를 materialize한다.
   - planning-time `recipe_only=3`은 모두 `qg_decided_no`이며 아직 이 gate를 통과하지 못한다. `L4-RAT-08` seal만으로 이를 0으로 간주하지 않는다.
   - 이 계획은 Gate 3 실패 시 **A 방향**을 채택한다: Change 2 이후 policy-dependent runtime/generated/current implementation 전체를 `BLOCKED`로 유지한다. 허용되는 것은 pre-seal read-only census, isolated off-live stable-ID plumbing candidate/validation, 별도 prerequisite/owner packet과 staging evidence뿐이다.
   - legacy Recipe fallback과 QG projection을 합친 mixed presentation은 terminal 또는 partial runtime state로 지원하지 않는다.
4. **Implementation and machine validation**
   - sealed policy identity와 통과한 migration-gate identity를 소비해 runtime/build/test candidate를 구현하고 Section 7의 validation을 실행한다.
5. **Conditional Layer 4 Complete-Generation and Safe Installation**
   - declared Layer 4 generated artifact diff가 없으면 inspected path/hash universe와 `not_applicable(no_generated_mutation)`으로 증명한다.
   - diff가 있으면 QG/Layer 4 owner가 ratify한 canonical inputs, deterministic off-live complete generation, stateless validation, exact successor identity, protected visibility boundary와 rollback contract 없이는 current runtime/package projection으로 진행하지 않는다.
   - DVF 3.3 `install_dvf_3_3_complete_generation.py`, `generation_descriptor.json`과 `IrisLayer3DataCurrent.lua`는 Layer 4 authority가 아니다.
   - 이 gate는 Gate 3이 먼저 통과한 subject에만 적용한다. authorized Layer 4 contract/writer가 없으면 generated-artifact-dependent scope만 `deferred`로 분리하고 overall closeout을 `partial`로 제한한다. exact mutation-independent subject는 mixed Recipe presentation을 만들지 않는 범위에서만 계속할 수 있다.
6. **Independent review and canonical promotion**
   - exact implementation/evidence/staging-doc subject에 대한 independent review와 owner canonical seal을 machine validation 및 generated installation과 별도 축으로 충족한 뒤에만 canonical top documents를 갱신한다.
   - 상위 로드맵 공동 기안자의 검토는 provenance로 보존할 수 있지만 independent-review credit으로 사용하지 않는다.

owner policy seal이 제공되지 않으면 이 계획은 pre-seal ceiling에서 멈추며 구현 완료나 canonical adoption을 claim하지 않는다.

### CLD Round 4 Review Remediation Trace

| Review finding | Plan closure |
|---|---|
| `CLD-R4-I01` — legacy removal과 Gate 3 | producer `recipe_index` denominator 불변을 명시; `separate_legacy_removal_scope`는 책임 지정만 하며 Gate 3 해소 경로가 아님 |
| `CLD-R4-I02` — blocked validation subset | Section 7에 Gate 3 blocked / full / post-Gate-3 Layer 4 install-contract partial별 required와 `not_applicable(no_subject)` command set 추가 |
| `CLD-R4-M01` — identity taxonomy layer | `identity_unavailable`을 producer/QG crosswalk identity 부재로 한정; runtime Lua stable-ID plumbing은 모든 mapped tuple에 적용되는 별도 공통 prerequisite로 분리 |
| `CLD-R4-M02` — `qg_absent` owner surface | `L4-RAT-08`을 fresh `qg_absent`에도 조건부 적용하고 category별 QG coverage/reconsideration scope를 구분 |
| 이전 라운드에서 CLOSED인 축 | generated mutation의 gated installation, one lookup → two projections, capability/Recipe parity, Gate 3 strict blocked, mixed-state 금지, owner seal과 validation ceiling을 유지. Stateful IAR adoption은 retirement 결과에 따라 제거 |

---

## 2. Scope

다음을 구현 범위로 한다.

- current QG description lookup의 `available / verified_empty / fault` 상태 보존
- 한 detail build당 정확히 한 번 실행되는 private status-bearing lookup과 그 결과에서 파생되는 legacy `useCases` projection
- `label_key`, `surface`, Recipe navigation reference와 requirements를 보존하는 Layer 4 presentation row projection
- current QG positive line을 Recipe와 Right-click의 단일 presentation source로 사용하는 collector 정리
- legacy capability tuple과 QG context-menu tuple의 structured exact crosswalk 및 `capability_only == 0` cutover hard gate
- legacy recipe connection/index tuple과 QG Recipe tuple의 stable-ID structured crosswalk 및 `recipe_only == 0` cutover hard gate
- `recipe_only`의 exhaustive/disjoint disposition taxonomy와 `qg_decided_no`의 owner-reserved 책임 경계
- `capability_only == 0 AND recipe_only == 0`일 때만 legacy Layer 4 presentation fallback을 제거하는 경계
- Gate 3 실패 시 policy-dependent implementation 전체를 차단하고 mixed QG + legacy Recipe runtime projection을 만들지 않는 경계
- Source별 count와 total count를 갖는 immutable presentation model
- `0 / 1 / 2~8 / 9+` density 분기
- verified-empty, fault, single, small, dense 상태의 Menu 표시
- dense 목록의 compact/full 전환과 literal local search
- Source section과 Source별 빈 상태 처리
- Recipe-local requirement의 density-aware 표시
- stable interaction identity와 Recipe navigation target의 결속
- per-FullType disclosure/search/row state와 item 전환 격리
- `(browser_generation, normalizedLocale, FullType)`에 결속된 interaction projection/state invalidation
- detail rebuild 뒤 scroll clamp와 single outer-scroll 유지
- Korean/English header, count, search, disclosure, empty/fault 문구
- locale 변경 시 localized presentation/search state 갱신
- normalized external QG row가 동일 schema를 만족할 때 같은 presentation 적용
- offline schema/completeness validator, standalone Lua acceptance harness와 실제 PZ UI 검증
- architecture/decision/roadmap 문서의 additive 정합성 갱신
- generated artifact mutation 발생 시 Layer 4-specific complete-generation/stateless-validation/safe-install contract를 거치는 conditional boundary
- Gate 3 PASS 뒤 Layer 4 generation/install contract만 blocked일 때 projection-dependent scope를 유예하고 non-public mutation-independent subject만 계속하는 partial closeout 경계
- staging governance text와 owner-sealed canonical write의 분리
- disposable package projection의 Lua syntax 및 payload parity 검증

### Explicitly Out Of Scope

- QG Evidence, classification, use-case 결정 또는 requirement 의미의 변경
- Layer 3 body, DVF System 또는 item-page information sufficiency assessment 변경
- 새 Recipe/Right-click 사실 추출 또는 current Layer 4 coverage 확대
- `qg_absent`에 대한 QG coverage 추가, `qg_decided_no`에 대한 QG 재판정, 또는 exact legacy-row 제거 교정의 실행; 각각 별도 authority/scope/validation subject다.
- output 부재에서 실제 게임 기능 부재를 추론하는 closed-world authority 생성
- Recipe와 Right-click 외의 제3 동등 Source 도입
- role/category/label 분석 기반 semantic grouping
- importance, usefulness, efficiency, relevance 기반 sort 또는 recommendation
- 대표 interaction, preview subset 또는 top-N 표시
- Source filter; Source section만 제공한다.
- fuzzy search, synonym search, stemming, 초성 검색, relevance scoring
- 제작 자동 실행, requirement 충족 자동화 또는 플레이어 상태 변경
- requirement 상태를 item sort/filter/ranking에 사용하는 기능
- Tooltip의 Layer 4 summary 추가 또는 Tooltip 4줄 계약 변경
- Browser 정상 경로 실패 시 사용하는 legacy `IrisWikiPanel`의 dense UI 재설계
- 모든 외부 모드의 비정규 raw 문자열 추론
- 모든 PZ locale, 모든 해상도/UI scale, multiplayer, long-session 검증
- package publication, Workshop 업로드, release readiness 판정
- owner seal 전 policy-dependent implementation 또는 canonical top-document write
- producer regeneration/validation만으로 current derived generation을 채택하는 행위
- partial generated generation의 current/runtime/package 노출
- Gate 3 실패 상태의 mixed QG + legacy Recipe adaptive presentation 또는 projection-dependent partial runtime 설치
- machine validation이나 package PASS를 generated installation, independent review 또는 owner seal로 대체하는 행위
- FPS, frame-time, heap 또는 latency 개선 claim

---

## 3. Non-Goals

- interaction이 많은 항목을 덜 중요하게 보이게 만드는 것이 목표가 아니다.
- interaction이 적은 항목에 artificial detail을 추가하지 않는다.
- verified-empty 문구를 world-level 기능 부재 보증으로 사용하지 않는다.
- 표시 밀도에 따라 QG line을 추가·삭제·병합·대표화하지 않는다.
- 동일 display label을 duplicate로 간주해 제거하지 않는다.
- Recipe name을 stable identity로 사용하지 않는다.
- `surface`, `label_key`, requirement display text 같은 문자열에서 새 의미를 추론하지 않는다.
- Recipe와 Right-click의 visual order를 source priority로 해석하지 않는다.
- compact state를 completeness 실패로 간주하지 않되, full view에서 모든 identity에 접근할 수 있어야 한다.
- search query가 source model이나 total count를 변경하게 하지 않는다.
- viewport 크기에 따라 semantic threshold나 Source membership을 바꾸지 않는다. 화면 크기는 폭, 높이, wrapping 같은 layout만 바꾼다.
- legacy capability API나 recipe connection API 자체를 제거하지 않는다. Layer 4 presentation row의 authority로만 사용하지 않는다.
- 계획 작성 시점의 항목 수를 runtime 상수나 semantic baseline으로 봉인하지 않는다.
- `.223BulletsMold`나 `Base.Tongs`만을 위한 item-specific 분기를 만들지 않는다.

---

## 4. Assumptions

### Codebase Inspection Summary

- `IrisBrowserInteractionRenderer.lua`는 현재 Recipe와 capability row를 합친 뒤 모든 interaction section을 기본적으로 접고, `Interactions (N) [+]` 한 줄만 먼저 표시한다.
- `IrisBrowserInteractionCollector.lua`는 Recipe를 recipe name으로 dedupe하고 QG Recipe line이 없을 때 `model.connections.recipes` 또는 `Index.getRecipeConnectionsForItem()`의 `recipe`를 사용해 navigation reference와 user-visible row를 합성한다. Right-click은 `model.capabilities` 또는 `IrisCapabilities.lua`에서 별도로 합성한다.
- current runtime `IrisRecipeIndexData.lua` entry는 `role`, `category`, `recipe`만 보존하지만 그 producer 입력 `Iris/output/recipe_index.v2.4.json`은 case-sensitive FullType 연결을 `recipe_id`, `recipe_name`, `inputs`/`keeps`로 표현한다. Recipe cutover parity는 display용 `recipe_name`이 아니라 이 producer-level `recipe_id`를 보존·전달하는 data-contract prerequisite를 요구한다.
- `Iris/output/recipe_nav_registry.v2.4.json`은 QG `uc.recipe.*`별 `recipe_id`, `original_name`, `category`, `nav_eligible`을 가지며 `build_recipe_nav_registry.py`는 이를 `rp.recipe.*` rule lineage에서 만든다. current converted `recipe_nav_ref`에는 stable `recipe_id`/rule ID가 없으므로 이름 비교로 공백을 숨기지 않고 stable lineage가 양쪽 tuple에 공급되지 않으면 Recipe cutover를 fail-closed한다.
- planning-time read-only stable-ID census에서는 legacy `(FullType, recipe_id)` 794개, QG Recipe 791개, mapped intersection 791개, `recipe_only=3`, `qg_recipe_only=0`이었다. legacy-only는 `Base.HandTorch`, `Base.Rubberducky2`, `Base.Torch`의 `remove_battery`이며 `rp.recipe.remove_battery`는 current decision `NO`이고 이 세 항목은 `matched_keep_fulltypes`에 있다. 세 tuple은 planning taxonomy상 모두 `qg_decided_no`다. 이는 implementation constant나 legacy/QG 중 어느 쪽이 옳다는 semantic 판정이 아니라 fresh execution census로 재검증할 관찰값이며, 현재 Gate 3이 닫혀 있음을 뜻한다.
- current QG chunk에는 Recipe뿐 아니라 86개의 structured `context_menu` positive line이 이미 존재한다. current capability set도 86개이므로 capability path를 Layer 4 표시 authority로 함께 유지하면 이중 source-of-truth가 된다.
- count `86 == 86`은 identity parity 증거가 아니다. current legacy capability는 7개 capability family를 사용하지만 QG context-menu set은 structured rule에 따라 10개 `use_case_id`로 분화된다. 특히 `can_scrap_moveables`는 construction/metal-cutting/screw-disassembly/wood-cutting으로 나뉘므로 FullType, legacy capability ID와 QG identity/rule lineage를 함께 결속한 crosswalk가 필요하다.
- `Iris/API/UseCases.lua`의 public `getUseCaseLines()`와 `IrisItemDetailViewModel.safeUseCaseCall()`은 최종 실패를 빈 line 배열로 정규화한다. 반면 `IrisUseCaseDescriptionsLookup.lua` 내부는 `lookup_miss`와 router/index/chunk fault를 구분한다.
- current detail build는 ViewModel이 `getUseCaseLines()`를 호출한 뒤 Renderer가 `_getDescriptionEntry()`를 다시 호출할 수 있다. status path를 추가만 하면 같은 build 안에 두 invocation과 서로 다른 fallback 결과가 남을 수 있다.
- `IrisItemDetailViewModel.lua`는 Browser와 Wiki가 공유하는 read-only detail model이며 Layer 3, QG line, capabilities, recipe connections를 함께 담는다.
- `IrisBrowserDetail.lua`는 detail child를 이동시키는 하나의 외부 scroll을 소유한다. interaction 영역에 nested scroll을 추가하지 않고 기존 `detailContentHeight`와 scroll clamp를 유지해야 한다.
- item 선택 변경은 `IrisBrowserListController.lua`에서 `detailScrollY`를 0으로 되돌리지만, current interaction 펼침 상태는 `recipeExpandedByFullType`에 FullType별로 저장된다.
- `IrisBrowserData.lua`는 generation과 normalized locale에 결속된 cache/search snapshot을 만들고 `resetForReload()`에서 generation을 invalidate한다. 새 interaction state도 이 lifecycle을 따라야 하며 FullType만으로 cache key를 구성해서는 안 된다.
- `IrisBrowserRecipeNav.lua`는 recipe navigation reference를 제작 UI category/filter로 연결하며 제작 자체를 실행하지 않는다.
- `IrisRequirementPolicy.lua`는 requirement atom을 Recipe row에서 표시하고 player 상태에 따라 색만 계산한다. 이 상태는 item-global capability나 sort 근거가 아니다.
- normal context-menu 진입은 `IrisContextMenu.lua`에서 Browser를 연다. `IrisWikiPanel.lua`는 Browser 로드 실패 시의 제한된 fallback이며 fixed-size/non-scroll 구조다.
- `IrisWikiSections.lua`와 `IrisWikiUseCaseLineRenderer.lua`는 fallback/static 경로에서 line을 표시하지만 normal Menu density 구현의 primary surface가 아니다.
- `build_usecases_by_fulltype.py`는 structured `evidence_sources[].source_type`에서 `surface`를 결정한다. `description_generator.py`와 `convert_descriptions_to_lua.py`는 `use_case_id`를 `label_key`로 보존한다.
- current upstream positive set에는 하나의 use case가 Recipe와 Right-click source를 동시에 갖는 `surface=both` 사례가 없다. Source별 별도 row를 통해 두 Source를 모두 가진 FullType은 20개이며, FullType 내부 duplicate `use_case_id`는 없다.
- current generated line count snapshot은 FullType 1,631개에 대해 `0=1,216`, `1=300`, `2~8=99`, `9+=16`, 최대 40이다. exactly 8은 3개, exactly 9는 6개이므로 threshold 양쪽을 실제 fixture로 검증할 수 있다.
- `Base.223BulletsMold`는 current QG에서 Recipe 1건과 requirement 3개를 갖는다.
- 첨부 로드맵은 `Base.Tongs`를 32건으로 기술하지만 current generated snapshot은 Recipe 33건이다. 테스트는 roadmap 숫자를 하드코딩하지 않고 실행 시 source count와 presentation count의 exact parity를 검사한다.
- `IrisUseCaseLabelMap.lua`는 KO/EN use-case label과 Source label을 제공한다. Recipe line은 original/translated name과 pre-rendered text를 함께 가진다.
- current recipe requirement index의 `display`는 localized-neutral schema가 아니므로 locale별 requirement 표시를 지원하려면 structured `check`를 보존한 additive display projection 또는 translation key가 필요하다. runtime에서 raw display text를 분석해 번역하지 않는다.
- Retirement Walkthrough는 Layer 1–5 active product IAR consumer를 0으로 닫았고 DVF 3.3 전용 stateless successor만 설치했다. Layer 4는 해당 successor의 consumer/migration 대상이 아니었으므로 generated diff가 생기면 QG/Layer 4-specific owner decision과 generation/install contract를 별도로 열어야 한다. Producer regeneration과 package projection만으로 current installation을 주장하지 않는다.
- `docs/EXECUTION_CONTRACT.md`에 따라 이 작업은 Authority/Runtime/Sealed Artifact/Public-Facing Output을 만지는 Heavy execution이다. machine validation, independent review, owner seal과 canonical closure eligibility는 별도 축이다.

### Proposed Policy Assumptions — Owner Seal Pending

- Layer 4 semantic authority는 QG에 남는다.
- owner가 `L4-RAT-02`를 seal하면 Browser가 소유하는 것은 `sort/fold/layout/density/basic exposure`뿐이다.
- `label_key`는 current generator contract에서 exact `use_case_id`다. 이를 private presentation identity로 사용하되 public API 이름으로 새로 약속하지 않는다.
- Recipe migration identity는 producer-level `recipe_index.recipes[*].recipe_id`와 QG의 `uc.recipe.*`/`rp.recipe.*` structured lineage다. `recipe_name`, `original_name`, translated/localized label, `display_text`는 표시 또는 navigation 동작 payload일 뿐 crosswalk identity가 아니다.
- `qg_decided_no`는 legacy 정보가 유효하다거나 과다 표시라는 뜻을 자체적으로 결정하지 않는다. owner disposition은 legacy row 처리의 후속 책임만 정하고 QG `NO`의 의미나 증거를 재판정하지 않는다.
- Source membership은 `surface=recipe_ui`와 `surface=context_menu`의 구조화된 값만 사용한다.
- `surface=both`는 current positive data에 없으므로 multi-membership 정책을 추측하지 않는다. 그런 row가 등장하면 validator와 runtime projection이 fault로 처리하고 정책 갱신을 요구한다.
- `line_kind=exclusion`은 positive interaction이나 verified-empty count에 포함하지 않는다.
- owner가 `L4-RAT-04`를 seal하면 Source 고정 순서는 Recipe 다음 Right-click이다. 이는 layout 안정성을 위한 presentation 순서이며 의미상 우선순위가 아니다.
- Source 내부에서는 QG line order를 그대로 보존한다. 따라서 locale 변경에도 base identity order가 바뀌지 않는다.
- owner가 `L4-RAT-01`을 seal하면 threshold는 versioned private presentation policy module의 단일 상수이며 screen size, locale, item category 또는 player state로 달라지지 않는다.
- verified-empty는 lookup이 정상 종료되어 valid entry의 positive line set이 비었거나 authoritative `lookup_miss`가 반환된 경우에만 산출한다.
- router/index/chunk/module/schema failure는 fault다. fallback이 실제 entry를 성공적으로 반환하면 available로 표시할 수 있지만, failure 뒤 entry가 없다는 이유로 verified-empty가 되지는 않는다.
- public `getUseCaseLines()` return shape와 existing `require` path는 호환성을 위해 유지한다.
- `verified_empty`는 current QG presentation output의 정상 empty/miss 상태일 뿐 실제 게임 interaction 부재를 나타내는 world-level negative fact가 아니다.
- planning-time census drift 자체는 failure가 아니다. failure가 되는 source/order drift는 같은 execution subject 안에서 current QG source identity와 그 candidate/generated/runtime projection identity가 어긋나는 경우다.

### Runtime and Environment Assumptions

- Project Zomboid runtime 구현은 계속 100% Lua다.
- Python은 offline validation과 fixture 생성에만 사용한다.
- Windows PowerShell과 저장소가 제공하는 `uv`/Lua/PZ harness를 사용한다.
- current working tree의 기존 사용자 변경은 이 계획 구현 시에도 보존한다. generated artifact를 갱신해야 할 때는 관련 producer를 통해서만 재생성하고 unrelated output을 덮어쓰지 않는다.
- planning-time census는 관찰값이다. 구현 시작 시 동일한 input에서 다시 산출하고 drift를 report한다.

---

## 5. Repository Areas Affected

### Code

Primary runtime changes:

- `Iris/media/lua/client/Iris/API/UseCases.lua`
- `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionCollector.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionPolicy.lua` (new, owner-sealed threshold/Source order의 단일 runtime authority)
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserDetail.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserListController.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisRequirementPolicy.lua`
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua` (status-aware legacy projection consumption)
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiPanel.lua` (single ViewModel build가 필요한 경우)

New private modules that keep projection/state logic out of widget creation:

- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua` (new)
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionState.lua` (new)

Offline producer/validator changes:

- `Iris/build/tools/pipeline/build_usecases_by_fulltype.py` (contract validation only unless schema gap is found)
- `Iris/build/description/v2/tools/build/build_iris_recipe_index_data.py` (stable `recipe_id` 보존용 data-contract prerequisite)
- `Iris/build/tools/pipeline/build_recipe_nav_registry.py` (structured Recipe lineage/nav identity source)
- `Iris/build/tools/pipeline/build_recipe_requirements_index.py`
- `Iris/build/description_generator.py`
- `Iris/build/convert_descriptions_to_lua.py`
- `Iris/build/description/v2/tools/build/validate_interaction_presentation_contract.py` (new)
- `Iris/build/description/v2/tools/build/validate_layer4_complete_generation_install.py` (new; 별도 Layer 4 owner decision이 있는 generated mutation branch에서만)

Regression-observed but not normally modified:

- `Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptionsLookup.lua`
- `Iris/media/lua/client/Iris/Data/IrisCapabilities.lua`
- `Iris/media/lua/client/Iris/Data/IrisRecipeIndex.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserRecipeNav.lua`
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiUseCaseLineRenderer.lua`
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua`

### Docs

- `docs/iris_layer4_adaptive_interaction_density_presentation_plan.md` (이 계획)
- `docs/iris_layer4_adaptive_interaction_density_presentation_decision_packet.md` (new, STAGING DRAFT; owner policy seal input)
- `docs/iris_layer4_adaptive_interaction_density_presentation_closeout.md` (new, staging/evidence-bounded closeout)
- `docs/DECISIONS.md` (independent review와 owner canonical seal 뒤에만 additive canonical 결정)
- `docs/ARCHITECTURE.md` (같은 canonical promotion gate 뒤 QG line → single lookup → private projection → Browser renderer 흐름)
- `docs/ROADMAP.md` (같은 gate 뒤 완료 상태, `Base.Tongs` current-count 정정과 remaining validation limits)

`docs/iris_item_page_information_sufficiency_plan.md`는 별도 assessment 계획이며 수정하거나 결합하지 않는다.

### Config

- `Iris/media/lua/shared/translate/en/Iris_en.txt`
- `Iris/media/lua/shared/translate/ko/Iris_ko.txt`

새 user option이나 config toggle은 추가하지 않는다. threshold는 private presentation policy constant다.

### Generated Artifacts

- `Iris/media/lua/client/Iris/Data/IrisTranslationData.lua`
- `Iris/media/lua/client/Iris/Data/IrisRecipeIndexData.lua` (stable `recipe_id` additive generation이 필요한 경우)
- `Iris/media/lua/client/Iris/Data/IrisUseCaseLabelMap.lua` (label-map producer 입력이 실제로 변경될 때만)
- `Iris/media/lua/client/Iris/Data/UseCaseDescriptions/**` (requirement locale projection의 additive schema가 필요한 경우 producer를 통해 재생성)
- `Iris/media/lua/client/Iris/Data/UseCaseDescriptions/RequirementsLookup.lua`
- `Iris/output/recipe_index.v2.4.json` (read-only legacy Recipe stable-identity source)
- `Iris/output/recipe_evidence_decisions.v2.4.json` (read-only `recipe_id` ↔ `rp.recipe.*` lineage source)
- `Iris/output/recipe_nav_registry.v2.4.json` (read-only QG Recipe lineage/navigation source)
- `Iris/build/description/v2/staging/iris_layer4_adaptive_interaction_density_presentation/` 아래의 source identity, capability/QG parity, policy-seal binding, candidate generation, successor identity, installation/rollback과 validation report
- focused offline census/validation report는 disposable staging/output root에 생성하고 authorized Layer 4 installation 전 current/runtime/package artifact로 취급하지 않는다.
- declared Layer 4 generated path에 diff가 없으면 no-mutation report와 `not_applicable(no_generated_mutation)` 근거만 남긴다.
- diff가 있으면 complete off-live candidate manifest와 exact successor identity를 남긴다. 별도 Layer 4 owner decision이 정한 validator/installer evidence만 허용하며 임의 receipt/current descriptor 또는 DVF 3.3 pointer를 만들지 않는다.

### Tests

- `Iris/test/test_interaction_presentation_contract.py` (new, Round 3 controlled-source taxonomy 밖의 focused contract test)
- `Iris/build/description/v2/tests/test_iris_detail_view_model_acceptance.py`
- `Iris/test/lua/browser_interaction_density_acceptance_harness.lua` (new)
- `Iris/test/lua/browser_state_acceptance_harness.lua`
- `Iris/test/lua/detail_view_model_locale_acceptance_harness.lua`
- `Iris/_dev/media/lua/client/Iris/Dev/BrowserInteractionDensityAcceptanceHarness.lua` (new, 실제 PZ executable에서 구동)
- `Iris/test/run_pz_core_refactor_harness.ps1` 또는 별도 interaction-density PZ runner
- `Iris/test/validate_disposable_package.ps1`

---

## 6. Planned Changes

### Change 1 — Run pre-seal census, capability/Recipe migration gates, and owner decision staging

**Purpose**

current input과 legacy/current presentation sources를 exact identity로 다시 계수하고, owner가 판단할 presentation proposal과 Right-click/Recipe cutover hard gate를 current mutation 없이 준비한다.

**Files**

- `Iris/build/description/v2/tools/build/validate_interaction_presentation_contract.py` (new)
- `Iris/test/test_interaction_presentation_contract.py` (new)
- `Iris/media/lua/client/Iris/Data/IrisCapabilities.lua` (read-only input)
- `Iris/output/recipe_index.v2.4.json` (read-only input)
- `Iris/output/recipe_evidence_decisions.v2.4.json` (read-only input)
- `Iris/output/recipe_nav_registry.v2.4.json` (read-only input)
- `Iris/build/description/v2/data/upstream_usecases_by_fulltype.json` (read-only input)
- `docs/iris_layer4_adaptive_interaction_density_presentation_decision_packet.md` (new, STAGING DRAFT)

**Implementation Notes**

- current upstream use-case data, generated line-count index와 runtime chunks를 case-sensitive FullType로 읽는다.
- pre-seal density census는 이 계획의 `L4-RAT-01` proposal을 source로 지목한 explicit `small_max=8`/`dense_min=9` CLI parameter를 받으며 decision packet은 그 exact parameter binding을 복사한다. report에는 exact value, source path/hash와 `proposal_not_sealed=true`를 기록하며 validator/test source의 literal `8`/`9`를 authority로 사용하지 않는다.
- 다음을 machine-readable report로 산출한다.
  - density bucket별 FullType count
  - exact 8/exact 9 fixture 목록
  - max count와 max item identity
  - Recipe/Right-click positive line count
  - 두 Source를 모두 가진 item count
  - duplicate identity, missing identity, unknown surface, `surface=both`, source/surface mismatch count
  - Recipe navigation/requirements binding 상태
- capability cutover report는 count가 아니라 다음 raw tuple을 보존한다.

```text
legacy_capability_tuple = (case-sensitive FullType, capability_id)
qg_context_tuple = (case-sensitive FullType, use_case_id/label_key, structured rightclick rule_id)
```

- 7개 legacy capability family와 current QG의 10개 action identity를 display string 분석 없이 연결하는 explicit audited crosswalk를 만든다. crosswalk 근거는 current structured right-click evidence/rule lineage이며 `can_scrap_moveables`의 action 분화를 보존한다.
- crosswalk를 적용한 뒤 `capability_only`, `qg_only`, `intersection`을 raw tuple 및 mapped QG identity와 함께 report한다.
- count equality는 identity parity의 대체 근거가 아니다.
- `qg_only > 0`이면 exact identities/count와 legacy capability surface에 없던 신규 user-visible exposure라는 disposition을 staging decision packet에 별도 기록한다. 자동 삭제하지 않으며 owner는 이를 본 상태에서 policy seal을 판단한다.
- Recipe fallback cutover report는 current runtime의 이름-only row를 그대로 crosswalk하지 않는다. producer source에서 stable identity를 보존하는 다음 tuple을 materialize한다.

```text
legacy_recipe_tuple = (
    case-sensitive FullType,
    recipe_index.recipes[*].recipe_id,
    recipe_id-keyed canonical navigation target reference
)
qg_recipe_tuple = (
    case-sensitive FullType,
    label_key/use_case_id,
    recipe_evidence_decisions rule_id + recipe_id,
    recipe_nav_registry entry.recipe_id + emitted recipe_nav_ref payload
)
```

- `recipe_evidence_decisions.v2.4.json`의 `rules[rp.recipe.*].recipe_id`, `matched_fulltypes`/`matched_keep_fulltypes`, `recipe_nav_registry.v2.4.json`의 entry key/`recipe_id`와 QG `use_case_id=uc.recipe.*`를 audited structured lineage edge로 사용한다. `input`/`keep` role과 category는 relation provenance로 함께 기록하되 current user-visible fallback identity는 `(FullType, recipe_id)`로 distinct한다. emitted navigation payload의 `original_name`/`category`는 target-behavior parity 검사에 보존하되 crosswalk key로 쓰지 않는다. `recipe_name`, `original_name`, translated/localized label, `display_text` 또는 그 정규화 결과로 identity를 매칭하지 않는다.
- planning crosswalk는 producer-level `recipe_index.v2.4.json`, `recipe_evidence_decisions.v2.4.json`, `recipe_nav_registry.v2.4.json`만으로 수행한다. 이 층의 stable ID/structured lineage가 없어 tuple 비교 자체가 불가능할 때만 `identity_unavailable`로 분류하고 이름 매칭으로 우회하지 않는다.
- current `IrisRecipeIndexData.lua`와 converted `recipe_nav_ref`에 stable `recipe_id`가 없는 문제는 taxonomy bucket과 별개인 **Gate 3 공통 runtime-plumbing prerequisite**다. producer crosswalk에서 mapped된 모든 Recipe tuple의 stable identity를 runtime까지 additive하게 전달하는 isolated off-live candidate를 설계·검증하며, current installation은 Gate 3과 Change 9를 우회하지 않는다.
- Recipe crosswalk 결과는 `recipe_only`, `qg_recipe_only`, `mapped_recipe_intersection`으로 disposition하고 raw tuple, mapped identity, navigation-target binding을 report한다. count equality는 QG absorption 증거가 아니다.
- 각 `recipe_only` tuple에는 다음 exhaustive/disjoint `failure_category`와 책임을 정확히 하나 부여한다. category 선택은 structured field 존재와 current QG decision record만으로 수행하고 display/name 의미를 해석하지 않는다.

```text
identity_unavailable
  condition: producer-level legacy recipe_id 또는 QG rule/recipe/nav-registry structured identity가 없어 offline crosswalk 자체를 수행할 수 없음
  responsibility: producer/QG 측 structured identity 공급 prerequisite; runtime Lua plumbing으로 해소하지 않음

qg_absent
  condition: stable legacy identity는 있으나 대응 positive QG row가 없고 current decision이 NO도 아님
  responsibility: L4-RAT-08 exact owner disposition; QG coverage 선택 시에도 이 계획에서 QG fact/decision을 추가하지 않음

qg_decided_no
  condition: 대응 rp.recipe.* rule과 recipe_id가 존재하고 current QG decision == NO
  responsibility: L4-RAT-08 exact owner disposition; 이 계획에서 QG decision을 변경하지 않음
```

- classifier precedence는 producer-level legacy stable ID 부재이면 `identity_unavailable` → stable ID로 찾은 structured rule의 `decision == NO`이면 nav row 부재와 관계없이 `qg_decided_no` → positive QG candidate/row의 producer-level structured identity가 불완전하면 `identity_unavailable` → 그 밖의 unmapped tuple은 `qg_absent`다. raw `recipe_only` 밖의 mapped tuple에는 failure category를 붙이지 않는다.
- `qg_absent` report는 `no_rule`, `no_decision_record`, `positive_row_unmaterialized` 같은 machine subreason을 보존할 수 있지만 category를 display string으로 추론하지 않는다.
- `L4-RAT-08` owner choices의 실행 효과는 다음처럼 제한한다.
  - `preserve_legacy`: current fallback을 유지한다. producer `recipe_index` legacy denominator와 raw `recipe_only`가 그대로이므로 Gate 3은 계속 `BLOCKED`다.
  - `separate_legacy_removal_scope`: exact tuple의 user-visible legacy 표시 교정을 이 계획 밖의 별도 correction subject에 배정한다. 이 correction은 사실 색인인 `recipe_index`를 변경하지 않으므로 채택·실행돼도 이 계획의 raw `recipe_only`와 Gate 3 상태는 변하지 않는다. 이는 migration 해소 경로가 아니다.
  - `separate_qg_authority_scope` for `qg_absent`: QG coverage 판단을 별도 authority subject에 요청한다. 별도 subject가 positive QG row를 실제 채택하고 fresh census가 이를 mapped intersection으로 확인한 경우에만 해당 tuple이 Gate 3 해소에 기여할 수 있다.
  - `separate_qg_authority_scope` for `qg_decided_no`: QG 재판정을 별도 authority subject에 요청한다. 별도 subject가 positive QG row를 실제 채택하고 fresh census가 이를 mapped intersection으로 확인한 경우에만 해당 tuple이 Gate 3 해소에 기여할 수 있다.
- 현 crosswalk의 legacy side는 collector의 현재 visible row set이 아니라 producer `recipe_index`의 case-sensitive `(FullType, recipe_id)` fact set으로 계속 고정한다. legacy 표시 correction을 이유로 denominator에서 tuple을 제외하거나 색인 사실을 삭제하지 않는다.
- 현 denominator 계약에서 `qg_absent`/`qg_decided_no` tuple의 Gate 3 해소 가능성이 있는 선택은 category별 `separate_qg_authority_scope`뿐이며, 이마저 positive QG row의 별도 adoption과 fresh census PASS를 보장하지는 않는다. decision packet은 각 선택에 `gate_effect=remains_blocked` 또는 `gate_effect=potential_only_after_external_adoption_and_fresh_census`를 명시해 owner에게 병렬 선택지의 실제 효과를 보여준다.
- 어떤 `L4-RAT-08` 선택도 raw `recipe_only`를 0으로 간주하거나 absorption evidence를 대체하지 않는다. owner disposition이 없거나 tuple/hash가 stale하면 `unresolved_owner_disposition` diagnostic을 추가하고 Gate 3을 닫는다.
- Change 3의 QG-only presentation cutover hard gate는 `capability_only == 0 AND recipe_only == 0`이다. 어느 값이든 남으면 owner policy seal 유무와 관계없이 해당 fallback 제거를 중단한다.
- `recipe_only > 0`이면 runtime에서 QG Recipe line을 추론 생성하거나 recipe name으로 억지 mapping하거나 legacy row를 조용히 삭제하지 않는다. category-specific prerequisite/owner disposition을 report하고 Recipe fallback removal과 Change 2 이후 policy-dependent implementation 전체를 `BLOCKED`로 둔다.
- `qg_recipe_only`는 QG current source로 report하되 legacy absorption의 대체 근거로 사용하지 않는다. `qg_recipe_only > 0`이면 exact identities/count와 legacy Recipe surface에 없던 신규 user-visible exposure라는 disposition을 staging decision packet에 별도 기록한다.
- count snapshot은 report에 기록하되 implementation constant로 사용하지 않는다.
- pre-seal 단계에서는 census parameter로 받은 proposed threshold나 Source order를 runtime/canonical current decision으로 선언하지 않는다. `L4-RAT-01`~`L4-RAT-08` proposal/disposition 선택지와 대안/영향을 staging decision packet에 기록한다.
- owner seal record는 owner-supplied exact disposition과 decision-packet hash를 가져야 한다. tool이나 구현자가 owner approval을 생성하지 않는다.
- 같은 execution subject 안에서 current QG source와 generated/runtime projection의 source/order identity가 다르면 실패한다. planning-time census 값의 자연스러운 변화만으로 실패하지 않는다.

**Validation**

- current snapshot에서 duplicate identity 0, unknown surface 0, source/surface mismatch 0을 확인한다.
- raw capability/QG tuple, audited crosswalk, `capability_only`, `qg_only`, `intersection`을 모두 materialize한다.
- raw legacy/QG Recipe tuple, audited structured lineage crosswalk, `recipe_only`, `qg_recipe_only`, `mapped_recipe_intersection`과 navigation binding을 모두 materialize한다.
- 모든 `recipe_only` tuple이 세 category 중 정확히 하나에 속하고 category union이 raw `recipe_only` set과 같으며 pairwise intersection이 0인지 검사한다. category별 structured condition, responsibility와 subreason을 함께 검증한다.
- producer crosswalk가 성공하지만 runtime Lua stable-ID field가 없는 fixture는 tuple별 `identity_unavailable`로 분류하지 않고 별도 common runtime-plumbing prerequisite로 보고하는지 검사한다.
- `capability_only == 0 AND recipe_only == 0`을 Change 3 진입의 machine hard gate로 검사하며 count-only fixture가 거부되는지 확인한다.
- fresh report에 모든 input path/hash를 기록하고 planning diagnostic인 `legacy=794`, `qg=791`, `mapped_recipe_intersection=791`, `recipe_only=3`, `qg_recipe_only=0` 및 세 `remove_battery` tuple과의 drift를 별도 표시한다. gate는 이 숫자나 category를 상수로 쓰지 않고 fresh tuple/disposition만 사용한다.
- planning snapshot의 세 `remove_battery` tuple이 `qg_decided_no`로 materialize되고 `L4-RAT-08`이 없거나 stale한 상태에서는 Gate 3과 Change 2 이후 implementation이 `BLOCKED`인지 확인한다.
- `preserve_legacy`와 adopted `separate_legacy_removal_scope` fixture 모두 producer legacy denominator, raw `recipe_only`와 Gate 3 `BLOCKED` 상태가 동일한지 검사한다. legacy correction이 collector 표시를 바꾸더라도 이를 absorption이나 gate PASS로 계산하지 않는다.
- `qg_absent`/`qg_decided_no`의 `separate_qg_authority_scope`는 별도 adopted positive QG row가 없으면 gate를 바꾸지 않고, adopted positive row 뒤 fresh structured census에서만 mapped intersection/`recipe_only`를 재평가하는지 검사한다.
- 모든 `L4-RAT-08` 선택이 이 계획 안에서 QG decision이나 producer fact index를 mutate하지 않는지 검사한다.
- owner decision packet의 모든 `L4-RAT-08` 선택에 exact `gate_effect`가 있고 preserve/removal에는 `remains_blocked`, QG authority 선택에는 potential-only 문구가 결속됐는지 검사한다.
- `qg_only > 0`이면 decision packet에 신규 user-visible exposure identities/count가 존재하는지 검사한다.
- `qg_recipe_only > 0`이면 decision packet에 신규 Recipe user-visible exposure identities/count가 존재하는지 검사한다.
- explicit proposal parameter `small_max=8`/`dense_min=9`와 source/hash가 report에 기록되고 validator/test source에 threshold literal이 authority로 고정되지 않았는지 검사한다. 그 parameter 아래 `Base.223BulletsMold`가 count 1 bucket에 있고 exact-boundary fixture가 양쪽에 최소 하나 존재함을 확인한다.
- `Base.Tongs`의 expected count는 literal 32/33이 아니라 current QG identity set과 exact parity로 검증한다.
- report replay의 ordering과 hash가 deterministic인지 확인한다.
- pre-seal mutation manifest가 declared baseline path/hash와 비교해 owner seal record 부재 상태의 policy-dependent runtime module, current generated artifact, canonical top-document diff가 정확히 0임을 기계적으로 증명하는지 확인한다. unrelated user diff는 declared subject 밖으로 분리해 숨기거나 덮어쓰지 않는다.
- owner seal 부재 시 Change 2 이후를 금지하는 human authorization 조건은 Section 1 `Execution Authorization Gates`에서 판정하며 machine PASS로 대체하지 않는다.

### Change 2 — Preserve verified-empty and fault as distinct lookup states

**Purpose**

현재 public empty normalization 아래에서 사라지는 lookup 상태를 private presentation path에 전달해 fault-as-zero를 방지한다.

**Files**

- `Iris/media/lua/client/Iris/API/UseCases.lua`
- `Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptionsLookup.lua` (필요한 최소 additive reason exposure만)
- `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua`
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`
- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiPanel.lua` (direct relookup이 확인되는 경우)
- `Iris/build/description/v2/tests/test_iris_detail_view_model_acceptance.py`

**Implementation Notes**

- Change 2는 `L4-RAT-01`~`L4-RAT-07` owner policy seal, 필요한 `L4-RAT-08` disposition과 Gate 3의 fresh combined migration PASS 뒤에만 시작한다.
- `UseCases`에 internal/private status-bearing 함수(예: `_getDescriptionState(fullType)`)를 추가한다.
- 상태 schema는 최소 다음을 가진다.
  - `status = available | verified_empty | fault`
  - `entry` 또는 normalized positive `lines`
  - machine `reason`
  - fallback 사용 여부
- valid entry의 positive line set이 비었거나 authoritative `lookup_miss`인 경우만 verified-empty 후보로 인정한다. router/index/content/chunk/module/schema failure는 fault다.
- fallback facade가 valid entry를 반환하면 `available`로 회복할 수 있다. fallback도 entry를 찾지 못하면 original failure reason을 버리지 않는다.
- 한 번의 `IrisItemDetailViewModel.fromItem()`은 `_getDescriptionState(fullType)`를 정확히 한 번 호출한다. Renderer나 in-repo Wiki/fallback consumer가 같은 detail build에서 `_getDescriptionEntry()` 또는 `getUseCaseLines()`를 다시 호출하지 않는다.
- status-bearing result의 normalized line arrays에서 두 하위 projection을 만든다.

```text
one status-bearing lookup result
├─ interactionState (status/reason/entry/lines)
└─ legacy model.useCases (same ordered lines/debug_lines + additive status/reason)
```

- legacy `model.useCases` line set/order는 `interactionState`와 동일한 result에서 파생하며 별도 fallback을 수행하지 않는다.
- public `getUseCaseLines()`, `_getDescriptionEntry()`와 public facade의 기존 return shape는 유지한다. detail model의 additive status field는 in-repo legacy consumer가 fault를 empty로 오인하지 않게 한다.
- Browser/Wiki/fallback의 in-repo consumer를 모두 inventory하고 empty presentation 전에 status를 확인하도록 migration한다. 외부 public facade 호환성을 이유로 Menu 내부 fault를 verified-empty로 표시하지 않는다.
- normal Browser detail과 Wiki section renderer는 그 build의 동일 ViewModel instance를 전달받는다. Browser-load failure fallback도 자체 ViewModel을 한 번만 만들고 direct UseCases relookup을 하지 않는다.
- existing `capabilities`, `connections` fields는 호환성을 위해 보존한다.
- machine reason은 diagnostic log/test에 사용하고 user-facing UI에는 raw module/path/token을 노출하지 않는다.

**Validation**

- valid empty entry, authoritative miss, router unavailable, invalid index shape, chunk require failure, malformed entry, fallback success fixture를 각각 검증한다.
- 각 detail fixture에서 description lookup invocation count가 정확히 1인지 검사한다.
- `interactionState.lines`와 legacy `model.useCases.lines`의 identity set/order parity를 검사한다.
- fault fixture에서 Browser와 Wiki/fallback consumer 모두 unavailable/fault를 관찰하며 legacy empty presentation으로 내려가지 않는지 검사한다.
- 같은 ViewModel fixture를 Browser/Wiki renderer에 전달해 ordered line identity와 status observation이 같은지 검사한다.
- public facade compatibility test가 기존 shape를 유지하는지 확인한다.
- 모든 fault fixture가 `verified_empty`로 정규화되지 않는지 확인한다.

### Change 3 — Build a lossless private interaction presentation projection

**Purpose**

QG line을 stable identity, Source, display payload와 action payload로 분리해 renderer가 count/search/folding 과정에서 semantic source를 다시 해석하지 않게 한다.

**Files**

- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionCollector.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua` (new)
- `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua`
- `Iris/test/test_interaction_presentation_contract.py`

**Implementation Notes**

- projection input은 private status-bearing QG description state다.
- projection은 ViewModel이 이미 만든 `interactionState`만 소비하며 UseCases API 또는 static facade를 다시 조회하지 않는다.
- positive `lines`만 row로 만들고 `exclusion_lines`/`line_kind=exclusion`은 count에서 제외한다.
- 각 row는 최소 다음을 보존한다.
  - `identity`: exact `label_key`
  - `source`: exact `recipe` 또는 `rightclick`
  - `baseOrdinal`: QG line ordinal
  - localized display payload
  - Recipe stable `recipe_id`/rule lineage와 navigation reference
  - Recipe-local requirements
  - original source line reference 또는 필요한 immutable copy
- `surface=recipe_ui`는 Recipe, `surface=context_menu`는 Right-click로 매핑한다.
- `surface=both`, unknown surface, blank/missing identity와 duplicate identity는 fail-closed projection fault다. label/name/requirement text를 보고 복구하지 않는다.
- identical display labels는 서로 다른 identity라면 모두 보존한다.
- Recipe name dedupe를 제거하고 identity collision을 숨기지 않는다.
- normal Layer 4 presentation은 QG context-menu line과 Recipe line만 사용한다. `IrisCapabilities`와 recipe connection/index는 public compatibility 및 다른 화면을 위해 남기되 missing QG line을 합성하는 fallback으로 사용하지 않는다.
- 이 두 cutover는 Change 1의 exact crosswalk report가 현재 implementation subject에 대해 fresh하고 `capability_only == 0 AND recipe_only == 0`일 때만 함께 활성화한다. capability/Recipe count equality나 QG-only renderability는 이 hard gate를 대신하지 않는다.
- Recipe row는 installed current generated line의 `recipe_nav_ref.recipe_id`와 structured rule lineage를 보존해야 한다. current generated schema에 이 stable field가 없어 additive generated mutation이 필요하면 Change 9의 safe installation 전에는 Recipe fallback 제거를 current runtime에 활성화하지 않는다.
- `recipe_only > 0`, `identity_unavailable`, stale Recipe crosswalk 또는 navigation-target mismatch 중 하나라도 있으면 Recipe fallback removal은 `BLOCKED`다. runtime name inference, display/localized string mapping, silent legacy-row deletion은 금지한다.
- Gate 3 실패 시 이 projection과 Change 2 이후 policy-dependent runtime work는 시작하지 않는다. legacy fallback을 유지한 current renderer가 그대로 남으며 QG rows와 legacy-only rows를 합친 adaptive/mixed model은 생성하지 않는다.
- total과 Source count는 projection rows에서 한 번 계산한다.
- 다음 completeness invariant는 Gate 3을 통과한 QG-only implementation subject에만 적용한다.

```text
source_positive_identity_set == full_projection_identity_set
full_projection_identity_set == visible_identity_set U temporarily_hidden_identity_set
recipe_count + rightclick_count == total_count
```

- current singleton Source membership 계약 아래에서 Source identity set은 서로 겹치지 않아야 한다.
- mixed-state completeness invariant는 정의하지 않는다. fallback이 남아 있으면 projection-dependent Changes 3~8 및 10과 adaptive renderer의 current installation을 모두 deferred/blocked하므로 `label_key` 없는 legacy row를 임시 identity로 발명하거나 Recipe count에 혼합하지 않는다.

**Validation**

- duplicate display label 2건이 row 2개로 유지되는 fixture를 추가한다.
- duplicate identity, blank identity, unknown/both surface가 fault가 되는지 확인한다.
- current full dataset에서 QG identity set과 projection identity set의 parity를 검사한다.
- capability/Recipe crosswalk report의 `capability_only == 0 AND recipe_only == 0`과 subject hash freshness를 다시 검사한다. 실패하면 해당 collector cutover 및 legacy synthesis 제거를 수행하지 않는다.
- Gate 3 failure fixture에서 Change 2 이후 declared policy-dependent current-path diff가 0이고 existing legacy renderer/fallback hash가 유지되며 mixed projection row/count가 생성되지 않는지 검사한다.
- legacy capability tuple 각각이 exact QG identity로 도달하는지 검사하고 capability-only public interaction loss 0을 확인한다.
- legacy Recipe tuple 각각이 stable structured lineage를 통해 exact QG Recipe identity와 installed current `recipe_nav_ref.recipe_id`에 도달하는지 검사하고 Recipe presentation absorption loss 0을 확인한다.
- capability/recipe-index fallback을 차단한 상태에서 legacy presentation identity set이 QG projection에 전부 흡수되고 current positive rows도 모두 표시 가능한지 확인한다.
- Source partition union/intersection과 total count invariant를 검사한다.

### Change 4 — Implement the four-state adaptive disclosure renderer

**Purpose**

interaction density에 맞는 초기 표시를 제공하되 모든 상태가 같은 projection과 completeness contract를 사용하게 한다.

**Files**

- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserDetail.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserTheme.lua` (기존 token으로 표현할 수 없을 때만)

**Implementation Notes**

- owner-sealed threshold와 Source order는 data-only `IrisBrowserInteractionPolicy.lua` 한 곳에만 정의한다. renderer/state와 Lua tests는 이 module을 require한다.
- offline validator가 threshold bucket을 필요로 하면 같은 Lua policy module의 제한된 literal을 strict parser로 읽고 module path/hash/value를 report한다. Python에 별도 `9` 상수를 두지 않으며 offline/runtime observed value parity assertion을 둔다.
- 모든 non-fault 상태에서 header에 total과 Source별 count를 표시한다. 존재하지 않는 Source도 count `0`을 통해 확인 가능하게 하되 불필요한 빈 section은 만들지 않는다.
- verified-empty는 section을 생략하지 않고 localized empty 문구를 표시한다. 문구는 “검증된 현재 Iris 자료에서 표시할 상호작용 없음” 범위를 넘는 world-level 주장을 하지 않는다.
- fault는 localized unavailable 문구와 retry-on-rebuild semantics를 사용한다. count 0처럼 표시하지 않는다.
- count 1은 header와 유일한 Source row를 열린 상태로 즉시 표시한다. master disclosure click을 요구하지 않는다.
- count 2~8은 Source section과 모든 row를 열린 상태로 즉시 표시한다.
- count 9+는 header/count와 `전체 보기` control을 먼저 표시하고 row list는 compact 상태로 시작한다. preview subset은 표시하지 않는다.
- dense full view는 기존 Detail outer scroll 안에서 전체 row를 materialize한다. nested `ISScrollingListBox`나 내부 mousewheel owner를 추가하지 않는다.
- 화면 폭/높이는 label wrapping, control width, visible viewport만 바꾸며 density bucket과 identity set을 바꾸지 않는다.
- Recipe/Right-click heading의 visual weight, font와 indentation을 동일하게 한다.
- Recipe→Right-click 고정 순서를 사용하되 heading/help text에서 우선순위 의미를 만들지 않는다.
- rebuild가 content height를 줄이면 `detailScrollY`를 새 max에 clamp하고 children/scrollbar 위치를 재동기화한다.

**Validation**

- synthetic `0, 1, 2, 8, 9, max` fixture의 initial disclosure state를 검사한다.
- offline validator와 runtime policy module이 관찰한 threshold/Source order가 동일한지 검사한다.
- Recipe-only와 Right-click-only fixture에서 absent peer Source count가 `0`이고 empty Source section은 생성되지 않는지 검사한다.
- single/small에서 master click 없이 모든 row가 생성되는지 확인한다.
- dense compact state에 대표 row가 없고, full view에서 exact total row가 생성되는지 확인한다.
- fixed Source order와 Source 내부 ordinal 보존을 확인한다.
- detail shrink/rebuild 뒤 blank viewport나 out-of-range scroll이 남지 않는지 확인한다.
- closeout에 `IrisBrowserTheme.lua`가 변경됐는지와, 변경됐다면 추가/재사용한 exact token 및 visual regression evidence를 기록한다.

### Change 5 — Add dense literal search without changing the base set

**Purpose**

고밀도 full view에서 사용자가 특정 interaction을 찾을 수 있게 하되 search가 ranking, semantic grouping 또는 omission source가 되지 않게 한다.

**Files**

- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionState.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserListController.lua`

**Implementation Notes**

- search는 count 9+의 full view에서만 제공한다.
- localized row label과 Recipe display name에 대한 plain substring match만 수행한다. requirement atom text는 search 대상이 아니다.
- locale-safe normalization은 trim과 ASCII case fold까지만 허용한다. locale collation, token relevance, synonym 또는 fuzzy score를 사용하지 않는다.
- result는 base Source/ordinal order를 그대로 유지한다.
- search 동안 header의 original total과 Source total은 유지하고 별도로 `표시 K / 전체 N`을 보여준다.
- zero result에서도 original total, Source counts와 clear control을 유지한다.
- clear는 query를 비우고 full identity set을 즉시 복원한다.
- query는 presentation state일 뿐 ViewModel/QG row를 mutate하지 않는다.
- search predicate에서 navigation reference나 requirement 상태를 변경하지 않는다.
- item 변경, locale 변경 또는 projection generation 변경 시 stale query/result projection을 명시적으로 reset/rebuild한다.

**Validation**

- 같은 locale/query에서 result identity와 order가 deterministic인지 확인한다.
- duplicate labels가 모두 result에 남는지 확인한다.
- no-result와 clear/full restoration invariant를 검사한다.
- search 전후 selected row의 Recipe navigation identity가 같은지 확인한다.
- query가 total/source count를 변경하지 않는지 확인한다.

### Change 6 — Preserve Recipe-local requirements and navigation under density changes

**Purpose**

표시를 접거나 검색해도 Recipe의 requirements와 제작 메뉴 navigation이 원래 interaction identity에서 분리되지 않게 한다.

**Files**

- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisRequirementPolicy.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserRecipeNav.lua` (regression fix가 필요한 경우만)
- `Iris/build/tools/pipeline/build_recipe_requirements_index.py`
- `Iris/build/convert_descriptions_to_lua.py`

**Implementation Notes**

- count 1/2~8에서는 Recipe requirements를 row 아래에 전량 표시한다. `.223BulletsMold`의 세 atom을 보기 위해 section을 한 번 더 펼치게 하지 않는다.
- count 9+에서는 Recipe row에 `요구 조건 N` control을 둘 수 있으며 초기에는 secondary detail을 접는다. 이를 presentation folding으로만 취급한다.
- dense row requirement를 펼치면 모든 atom을 원래 order로 표시한다. 일부 atom preview나 요약 추론을 하지 않는다.
- requirement가 없는 Recipe는 빈 requirement block/control을 만들지 않는다.
- malformed requirement와 none을 구분한다. malformed payload는 해당 row의 requirement 상태를 unavailable로 표시하고 diagnostic을 남기며 item-global fault나 verified-empty로 바꾸지 않는다.
- `RequirementPolicy.evalColor()`의 player-state coloring은 유지하되 Source grouping, row ordering, search score에 사용하지 않는다.
- Recipe navigation button은 row identity에 직접 결속된 installed current original `recipe_nav_ref`만 사용하고 stable `recipe_id`/rule lineage와 target payload를 함께 검증한다. `original_name`은 current 제작 UI filter payload로 사용할 수 있지만 crosswalk identity로 승격하지 않는다.
- unresolved navigation reference는 다른 Recipe를 추정하지 않는다. control을 disabled/unavailable로 표시하고 machine reason을 기록한다.
- navigation은 제작 UI를 열고 위치를 맞추는 current behavior까지만 유지하며 crafting을 실행하지 않는다.

**Validation**

- requirements 0/1/multiple/malformed fixture를 검증한다.
- single/small/dense에서 requirement atom identity와 count가 보존되는지 확인한다.
- search/fold 전후 `identity -> recipe_nav_ref` 매핑 hash가 동일한지 검사한다.
- wrong navigation identity 0, empty requirement block 0을 검사한다.
- player requirement color가 order/count/search result를 바꾸지 않는지 확인한다.

### Change 7 — Make presentation state item- and locale-safe

**Purpose**

item 전환, locale refresh와 detail rebuild가 이전 item의 dense/query/row 상태를 잘못 재사용하지 않게 한다.

**Files**

- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserListController.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserDetail.lua`
- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionState.lua`

**Implementation Notes**

- state ownership key는 `(IrisBrowserData browser_generation, normalizedLocale, case-sensitive FullType)`로 고정한다. interaction projection generation은 Browser generation에 종속된다.
- dense master state, query와 requirement fold state를 분리한다.
- row-level state는 display label/row index가 아니라 stable interaction identity로 key한다.
- 다른 item으로 전환할 때 새 item은 자기 default density state로 시작한다. 같은 FullType로 돌아왔을 때 dense master state를 복원할지는 private policy로 허용하되 query는 stale locale/data 위험을 피하기 위해 reset한다.
- `IrisBrowserData.resetForReload()` 또는 successful cache rebuild로 browser generation이 바뀌면 old generation의 interaction projection, dense/query/row state와 widget callback을 전부 invalidate한다.
- locale 또는 projection/browser generation이 바뀌면 localized text와 search projection을 rebuild하고 query/result cache를 invalidate한다.
- detail rebuild 전후 scroll anchor가 사라지면 safe clamp를 적용한다. stale child/widget reference는 보존하지 않는다.
- state 저장은 runtime memory에만 두며 savegame/player/game state를 변경하지 않는다.

**Validation**

- single→dense→single, dense A→dense B→A item 전환을 검증한다.
- duplicate display labels의 row toggle이 identity별로 독립적인지 확인한다.
- locale refresh 뒤 이전 locale query 결과가 남지 않는지 확인한다.
- same FullType/locale에서 Browser generation만 flip하는 fixture로 old projection/query/row callback이 재사용되지 않는지 확인한다.
- shrink/reopen 후 scroll bound와 scrollbar가 일치하는지 확인한다.

### Change 8 — Complete KO/EN presentation localization without runtime inference

**Purpose**

새 control과 상태 문구를 KO/EN에서 안정적으로 표시하고 locale 변경 시 stable identity와 localized display를 분리한다.

**Files**

- `Iris/media/lua/shared/translate/en/Iris_en.txt`
- `Iris/media/lua/shared/translate/ko/Iris_ko.txt`
- `Iris/media/lua/client/Iris/Data/IrisTranslationData.lua`
- `Iris/media/lua/client/Iris/Data/IrisUseCaseLabelMap.lua`와 generator input (필요한 경우)
- `Iris/build/tools/pipeline/build_recipe_requirements_index.py`
- `Iris/build/convert_descriptions_to_lua.py`
- `Iris/test/lua/detail_view_model_locale_acceptance_harness.lua`

**Implementation Notes**

- header, Source heading, verified-empty, unavailable, full/compact, search placeholder/clear, `visible/total`, requirement count/unavailable와 navigation unavailable key를 KO/EN에 추가한다.
- Right-click label은 stable `label_key`로 `IrisUseCaseLabelMap`을 조회한다.
- Recipe label은 locale 정책에 따라 sealed `recipe_original_name`/`recipe_translated_name` 또는 existing localized display field를 선택한다. identity/order에는 사용하지 않는다.
- requirement display는 structured `check`와 offline producer가 제공하는 display key/locale payload를 사용한다. runtime이 current Korean `display` 문장을 파싱해 영어로 재구성하지 않는다.
- producer/converter regeneration은 explicit off-live output root를 지원하도록 하거나 disposable isolated checkout에서 수행한다. Change 8은 candidate를 current generated path에 직접 쓰지 않으며 current installation은 Change 9만 소유한다.
- current requirement schema로 lossless KO/EN display를 만들 수 없는 atom은 producer 단계에서 fail-loud inventory로 보고하고 임의 번역을 만들지 않는다.
- selected locale로 표현할 수 없는 requirement atom은 runtime에서 다른 locale raw `display`로 silent fallback하지 않는다. 해당 Recipe row에 localized `requirement unavailable` 상태를 표시하고 atom identity/count와 machine reason을 diagnostic에 보존한다.
- unsupported locale는 existing English fallback policy를 사용한다.
- locale 간 identity, Source partition, base order, navigation hash는 동일해야 한다. localized text와 search result만 달라질 수 있다.

**Validation**

- Korean, English와 unsupported-locale fallback harness를 실행한다.
- locale별 모든 새 translation key 존재와 non-empty value를 검사한다.
- KO↔EN 전환 전후 identity/order/navigation parity를 검사한다.
- locale-nonrepresentable atom fixture가 다른 언어 raw text를 노출하지 않고 row-local unavailable로 표시되는지 확인한다.
- header/Source count가 긴 localized text에서도 control을 덮지 않는지 manual in-game PZ UI에서 확인한다.
- 모든 PZ locale 지원은 claim하지 않는다.

### Change 9 — Gate generated Layer 4 changes through a Layer 4-specific complete-generation and safe-install contract

**Purpose**

Recipe stable-ID/lineage, requirement localization 또는 label/schema 변경이 Layer 4 generated artifact를 바꾸는 경우, validated candidate를 current generation으로 곧바로 취급하지 않는다. QG/Layer 4 owner가 승인한 별도 complete-generation/stateless-validation/safe-install contract가 있어야 한다.

**Files**

- `Iris/build/description/v2/tools/build/validate_layer4_complete_generation_install.py` (new; 별도 owner decision 뒤에만)
- `Iris/build/description/v2/tools/build/build_iris_recipe_index_data.py`
- `Iris/build/convert_descriptions_to_lua.py`
- `Iris/media/lua/client/Iris/Data/IrisRecipeIndexData.lua`
- `Iris/build/tools/pipeline/build_recipe_requirements_index.py`
- `Iris/media/lua/client/Iris/Data/UseCaseDescriptions/**`
- `Iris/media/lua/client/Iris/Data/IrisUseCaseLabelMap.lua`
- `Iris/media/lua/client/Iris/Data/IrisTranslationData.lua` (generated-path census 대상)
- `Iris/_docs/authority/iris_current_authority_manifest.json` (retained governance classification input; product authority가 아님)
- `Iris/build/description/v2/staging/iris_layer4_adaptive_interaction_density_presentation/**` (candidate/identity/install evidence)

**Implementation Notes**

- 먼저 declared generated path의 before/after hash, QG/Layer 4 producer ownership과 retirement consumer census disposition을 조사한다.
- **No-mutation branch:** Layer 4 generated artifact diff가 없으면 `not_applicable(no_generated_mutation)` report에 exact inspected path/hash set을 기록한다. 이를 install PASS라고 부르지 않는다.
- **Mutation branch:** 하나라도 diff가 있으면 다음 순서를 강제한다.

```text
current QG/source identity
→ Layer 4 owner decision + exact generation/install contract
→ isolated off-live complete generation A/B
→ A/B byte determinism + schema/completeness/locale validation
→ ordered path/hash complete-generation manifest
→ exact successor identity
→ authorized fail-closed safe installation
→ post-install runtime/package projection validation
```

- candidate는 current generated path 밖에서 만들고 current QG/source identity, producer/converter identity, policy-seal identity, declared file universe와 ordered file hashes에 결속한다.
- Layer 4 contract는 canonical inputs, generator/serializer identity, output universe, protected visibility boundary, predecessor check, rollback과 claim token을 자체적으로 정의한다. DVF 3.3 descriptor/installer/single pointer를 자동 재사용하지 않는다.
- complete generation은 facade/index/requirements/chunks/label/translation 중 declared affected set 전체를 포함한다. partial candidate나 일부 파일만 current로 노출하지 않는다.
- Recipe fallback migration을 위해 `IrisRecipeIndexData.lua` 또는 QG `recipe_nav_ref`에 stable `recipe_id`/rule-lineage field를 추가해야 하는 경우도 generated-dependent scope로 분류하고 이 mutation branch를 거친다. safe install 전 current runtime에서 그 field를 가정하거나 Recipe fallback removal을 활성화하지 않는다.
- regeneration, candidate validation, package PASS는 각각 current installation이 아니다.
- generated installation은 current QG source authority나 use-case 의미를 수정하지 않는다.
- exact owner decision, validated complete generation과 authorized installer 전에는 current generated/runtime/package path에 candidate를 설치하지 않는다.
- installer는 predecessor exact identity, partial/mixed rejection, post-apply validation과 rollback contract를 가진다. same-generation 재적용은 protected mutation 0의 no-op이어야 한다.
- authorized Layer 4 contract/writer가 없거나 새 protected path authorization이 필요하면 mutation branch를 `blocked`로 종료한다. 임의 receipt/current descriptor를 만들거나 DVF 3.3 installer를 재사용하지 않는다.
- 이 계획은 Gate 3 PASS 뒤 Layer 4 install-contract-blocked branch에서만 **B 방향**을 채택한다: generated-artifact-dependent scope는 `deferred`, exact mutation-independent scope는 별도 subject로만 계속하며 overall closeout은 `partial`이다. Gate 3 failure의 strict A와 혼동하지 않는다.
  - generated-dependent scope: current generated Recipe stable-ID/lineage 또는 localized requirement/label/translation payload에 diff가 필요한 Change 3/8 부분, Recipe fallback removal, installed-generation runtime/package claim.
  - mutation-independent continuation은 one status-bearing lookup과 legacy `useCases` compatibility projection처럼 current public presentation output을 바꾸지 않고 generated candidate field를 읽지 않는 내부 범위로 제한한다. validator/test/staging evidence는 계속할 수 있다.
  - Changes 3~8/10의 adaptive projection, Source count, disclosure/search/state/scroll UI와 Recipe fallback cutover는 하나의 projection-dependent 묶음으로 모두 deferred한다. 일부만 current 설치해 QG + legacy Recipe mixed presentation을 만들지 않는다.
  - partial branch에서는 existing renderer와 Recipe presentation fallback의 exact hash/behavior를 유지하고, QG-only Recipe authority, adaptive density UI, lossless Recipe cutover, full KO/EN requirement localization, installed-current/package 또는 overall `complete`를 claim하지 않는다.
  - partial implementation/evidence는 staging closeout에만 기록한다. full target과 다른 partial behavior를 `DECISIONS.md`/`ARCHITECTURE.md`/`ROADMAP.md`의 완료 상태로 canonical promotion하지 않는다.
- installation 뒤 package validation은 installed exact generation을 입력으로 사용한다. off-live candidate package PASS를 current package evidence로 재사용하지 않는다.

**Validation**

- no-mutation fixture는 `not_applicable(no_generated_mutation)`과 current generated path mutation 0을 증명한다.
- mutation fixture는 candidate A/B hash parity, complete declared file set, source/policy/producer identity binding과 partial-generation rejection을 검사한다.
- exact successor manifest와 owner-approved install subject의 path/hash/generation identity가 일치하는지 검사한다.
- Layer 4 owner decision/install contract가 없거나 stale하면 runtime/package projection 진입이 차단되는지 검사한다.
- unavailable writer/path fixture에서 projection-dependent scope 전체가 deferred되고 existing renderer/Recipe fallback hash가 유지되며, mutation-independent subject manifest 밖 current diff와 mixed projection row가 0이고 overall closeout이 `partial`인지 검사한다.
- blocked/partial branch가 QG-only Recipe cutover, full KO/EN requirement localization, installed-current/package 또는 canonical-complete claim을 내지 못하는지 claim guard로 검사한다.
- injected install/post-apply failure에서 predecessor generation이 복구되고 failed successor가 current로 남지 않는지 검사한다.
- same-generation reapply의 protected mutation count가 0인지 검사한다.
- `regeneration != installation`, `package PASS != installation`, `installation != QG semantic mutation`, `DVF 3.3 successor != Layer 4 install authority` claim guards를 검사한다.

### Change 10 — Support normalized external rows and reject raw inference

**Purpose**

외부 모드 item도 QG-compatible normalized row라면 같은 presentation을 사용하되 불완전한 raw payload에서 의미를 추측하지 않는다.

**Files**

- `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua`
- `Iris/build/description/v2/tests/fixtures/interaction_presentation/**` (new)
- `Iris/test/test_interaction_presentation_contract.py`

**Implementation Notes**

- external fixture도 exact identity, supported surface, localized/display payload와 optional Recipe action payload를 요구한다.
- item module/name, display label, recipe text 또는 capability name에서 Source를 추론하지 않는다.
- normalized external row와 vanilla row에 동일 threshold/count/completeness 규칙을 적용한다.
- missing/unknown field는 fault 또는 row-local unavailable로 처리하며 verified-empty로 바꾸지 않는다.
- external collision을 이름 dedupe로 숨기지 않는다.

**Validation**

- normalized external 1/small/dense fixture가 vanilla와 같은 projection 결과를 내는지 확인한다.
- raw text-only, missing identity, unknown source, duplicate identity fixture가 fail-closed인지 확인한다.
- raw mod inference 0을 static guard로 검사한다.

### Change 11 — Add layered automated, PZ-runtime, and manual acceptance coverage

**Purpose**

projection의 수학적 completeness, standalone Lua state, PZ Kahlua runtime behavior와 manual in-game layout observation을 분리해 검증한다.

**Files**

- `Iris/test/test_interaction_presentation_contract.py`
- `Iris/build/description/v2/tests/test_iris_detail_view_model_acceptance.py`
- `Iris/test/lua/browser_interaction_density_acceptance_harness.lua`
- `Iris/test/lua/browser_state_acceptance_harness.lua`
- `Iris/_dev/media/lua/client/Iris/Dev/BrowserInteractionDensityAcceptanceHarness.lua` (new)
- `Iris/test/run_pz_core_refactor_harness.ps1`
- `Iris/test/validate_disposable_package.ps1`

**Implementation Notes**

- offline Python tests는 dataset/schema/source/identity/completeness와 threshold fixtures를 검증한다.
- standalone Lua harness는 PZ UI class를 최소 mock하여 density state, state isolation, search restoration, locale invalidation과 scroll clamp를 검증한다.
- PZ Kahlua runtime harness는 `ProjectZomboid64.exe`를 실제로 실행해 production mod와 dev harness를 로드하고 실제 runtime dialect/widget/navigation binding을 검증한다. 실행 파일을 부팅하지 않은 mock test에는 이 명칭이나 credit을 사용하지 않는다.
- manual UI matrix는 automated result를 대체하지 않고 renderer/layout 확인에 집중한다.
- disposable package validation은 external temp output root를 사용해 primary tree를 mutate하지 않는다.

**Validation**

- Section 7의 exact commands와 scenario matrix를 통과한다.
- offline Python, standalone Lua/mock, PZ Kahlua runtime harness, manual in-game UI와 package projection 결과를 별도 axis로 보고한다.
- 어떤 한 축의 PASS도 release/Workshop readiness로 확대하지 않는다.

### Change 12 — Stage governance text, then promote only after review and owner seal

**Purpose**

구현 결과를 staging governance text로 먼저 고정하고, exact subject의 independent review와 owner canonical seal 뒤에만 current authority 문서에 additive하게 반영한다.

**Files**

- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/iris_layer4_adaptive_interaction_density_presentation_plan.md`
- `docs/iris_layer4_adaptive_interaction_density_presentation_decision_packet.md`
- `docs/iris_layer4_adaptive_interaction_density_presentation_closeout.md`

**Implementation Notes**

- **Change 12-a — staging text:** sealed policy identity, `recipe_only` category/responsibility, exact `L4-RAT-08` disposition, `qg_only`/`qg_recipe_only` 신규 노출, exact code/generated candidate 또는 installed current generation, validation ceiling과 proposed top-doc patches를 staging packet/closeout에 기록한다. 이 단계에서는 top documents를 쓰지 않는다.
- staging `DECISIONS.md` patch에는 owner-sealed threshold, runtime projection ownership, Source-only grouping, identity-set completeness, fixed base order, Tooltip exclusion proposal를 담는다.
- staging `ARCHITECTURE.md` patch에는 `QG sealed lines -> one status-bearing lookup -> legacy/useCases projection + private presentation projection -> Browser density renderer` 흐름을 담는다.
- staging `ROADMAP.md` patch에는 구현/validation/installation 상태, remaining limits와 `Base.Tongs`의 roadmap 32건을 planning-time snapshot으로 정정하는 additive note를 담는다. current exact count는 source parity로 계속 계산한다.
- exact implementation, evidence, conditional Layer 4 generation/install decision과 세 staging patches를 하나의 review subject manifest로 path/hash 결속한다.
- coauthor/self-review는 independent review를 충족하지 않는다. eligible independent reviewer의 verdict를 별도 artifact로 결속한다.
- **Change 12-b — canonical promotion:** independent review PASS와 owner-supplied canonical seal이 exact subject manifest에 결속된 경우에만 `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`에 additive write를 수행한다.
- Change 9의 Gate 3 PASS 후 Layer 4 install-contract-blocked partial branch에서는 non-public mutation-independent implementation과 deferred projection-dependent scope를 staging closeout에만 기록하고 Change 12-b를 실행하지 않는다. full target과 다른 partial behavior를 canonical 완료 결정으로 봉인하지 않는다.
- implementation/machine validation/generated installation 완료는 owner canonical seal이나 canonical write 완료를 함의하지 않는다.
- `docs/iris_item_page_information_sufficiency_plan.md`의 assessment authority, Layer 3/4 sufficiency claim과 합치거나 대체하지 않는다.
- validation evidence, independent review 또는 owner seal이 없는 상태에서 해당 축의 완료 표시를 하지 않는다.

**Validation**

- Philosophy의 Menu/Tooltip, silence/evidence, read-only 원칙과 상충하지 않는지 검토한다.
- staging patch와 canonical diff의 exact text/hash parity를 검사한다.
- independent review subject, owner seal subject와 실제 canonical diff가 동일한지 검사한다. 변경되면 기존 review/seal을 stale로 판정한다.
- DECISIONS/ARCHITECTURE/ROADMAP 사이에 Source authority나 surface 수에 관한 모순이 없는지 검사한다.
- partial branch fixture에서 canonical top-document diff가 0이고 staging closeout만 `partial`을 기록하는지 검사한다.
- claim boundary가 package publication, factual completeness, performance로 확대되지 않았는지 확인한다.

---

## 7. Validation Plan

### Automated Validation

실행 경로를 먼저 결정한 뒤 아래 명령 중 해당 경로에서 `required`인 집합만 저장소 root에서 실행한다. required 명령은 정확히 exit code `0`일 때만 PASS다. `not_applicable(no_subject)`는 생략이 아니라 path/hash subject와 사유를 validation report에 기록하는 별도 disposition이며 PASS나 BLOCKED로 세지 않는다.

`V1` — Round 3 controlled-source taxonomy를 변경하지 않고 새 interaction contract test를 직접 실행하는 명령. Gate 3 blocked 경로에서는 fresh census/taxonomy report와 pre-seal no-current-mutation manifest의 존재·subject hash·assertion을 함께 검증한다.

```powershell
uv run python -m pytest -q Iris/test/test_interaction_presentation_contract.py
```

`V2` — 기존 Round 3 분류에서 detail ViewModel focused file의 current/diagnostic/historical item을 모두 실행하는 명령:

```powershell
uv run python -m pytest -q --round3-contract=all Iris/build/description/v2/tests/test_iris_detail_view_model_acceptance.py
```

`V3` — repository가 채택한 current Round 3 source만 exact approved denominator로 전수 수집·실행하는 명령:

```powershell
uv run python -m pytest -q --round3-contract=current --round3-enforce-denominator
```

`V4` — production/package 대상 Lua 전수 syntax 명령:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

`V5` — 실제 Project Zomboid executable을 부팅하는 PZ Kahlua runtime harness 명령:

```powershell
$repositoryRoot = (Resolve-Path '.').Path
$evidencePath = Join-Path $repositoryRoot 'Iris/build/description/v2/staging/iris_layer4_adaptive_interaction_density_presentation/validation/pz_kahlua_runtime.jsonl'
powershell -ExecutionPolicy Bypass -File .\Iris\test\run_pz_core_refactor_harness.ps1 -RepositoryRoot $repositoryRoot -OutputPath $evidencePath -HarnessModule 'Iris/Dev/BrowserInteractionDensityAcceptanceHarness' -TimeAxis post_refactor_acceptance
```

이 명령이 실제 PZ executable을 찾지 못하거나 부팅하지 못하면 PZ runtime axis는 BLOCKED다. standalone/mock Lua 결과를 대신 `PZ runtime PASS`라고 기록하지 않는다.

`V6` — safely installed current generation 또는 no-generated-mutation implementation subject를 external temp root에 투영하는 disposable package 명령:

```powershell
$repositoryRoot = (Resolve-Path '.').Path
powershell -ExecutionPolicy Bypass -File .\Iris\test\validate_disposable_package.ps1 -RepositoryRoot $repositoryRoot
```

JS/TS와 Java/Gradle 파일은 이 계획 범위에 없다. 해당 파일이 실제 diff에 생길 경우 AGENTS.md의 exact validation을 추가하고, tooling 부재 시 BLOCKED로 보고한다.

#### Execution-Path Required Validation Set

| Execution path | Required commands/evidence | `not_applicable(no_subject)` | Closeout rule |
|---|---|---|---|
| Pre-seal / Gate 3 `BLOCKED` (current default) | `V1`; fresh capability/Recipe census·disjoint taxonomy·deterministic replay와 declared pre-seal no-current-mutation manifest만 required | `V2`: Change 2 subject 없음; `V3`: controlled current-denominator 변경 subject 없음; `V4`: current Lua change 없음; `V5`: 신규 production/dev harness module 및 adaptive runtime subject 없음; `V6`: installed/no-mutation implementation projection subject 없음 | required evidence가 PASS여도 plan closeout은 `blocked`; `L4-RAT-08` packet은 허용 산출물이지만 owner response는 validation PASS 전제 아님; 나머지를 PASS로 주장하지 않음 |
| Gate 3 PASS 후 full implementation | `V1`, `V2`, `V3`, `V4`, `V5`, `V6`; applicable manual matrix와 Layer 4 generation/install branch evidence | 없음 | 하나라도 missing/non-zero면 해당 axis `BLOCKED`/`FAIL`; full `complete` 불가 |
| Gate 3 PASS 후 Layer 4 contract/writer `BLOCKED` partial | `V1`, `V2`, `V3`, `V4`; projection-dependent diff 0, existing renderer/fallback hash 보존과 partial subject manifest | `V5`: adaptive production/dev harness가 current 설치되지 않음; `V6`: installed current generation/package projection 없음 | `partial`만 가능; `V5`/`V6` N/A를 runtime/package PASS로 바꾸지 않음 |

- path selection report는 Gate 3 result, exact subject manifest hash와 Layer 4 generation/install branch result를 기록하며 사람이 명령을 임의로 required/N/A 전환하지 못하게 한다.
- Gate 3 blocked 경로의 `V1`은 census/taxonomy와 no-current-mutation manifest 중 하나라도 absent/stale이면 non-zero로 종료한다. 별도 runtime implementation이 없다는 이유로 이 required evidence를 생략하지 않는다.
- `V5`가 required인 full path에서 실제 PZ executable/harness를 찾지 못하면 PZ runtime axis는 `BLOCKED`다. `V5`가 `not_applicable(no_subject)`인 blocked/partial path에서는 실행 대상 부재를 실패나 PASS로 바꾸지 않는다.
- Manual Validation 12건은 full implementation path에서만 required다. Gate 3 blocked와 Layer 4 install-contract partial path에는 adaptive UI current subject가 없으므로 `not_applicable(no_subject)`이며, 선택적 baseline 확인을 수행해도 full-path manual credit으로 사용하지 않는다.

### Required Automated Scenario Matrix

| Case | Required assertion |
|---|---|
| authoritative 0 | verified-empty, total 0, fault 아님 |
| lookup/router/chunk fault | unavailable, verified-empty 아님 |
| one detail build | status-bearing description lookup invocation 정확히 1회 |
| status/legacy projection | identity set/order parity; fault가 legacy empty로 변환되지 않음 |
| capability↔QG cutover | raw tuple/crosswalk materialized, `capability_only == 0`; count equality만으로 통과 금지 |
| legacy Recipe↔QG Recipe cutover | stable-ID/raw tuple과 structured lineage crosswalk materialized, `recipe_only == 0`; recipe name/display 또는 count equality만으로 통과 금지 |
| combined fallback cutover gate | `capability_only == 0 AND recipe_only == 0`; 어느 한쪽 mismatch에도 해당 fallback removal 차단 |
| `recipe_only` taxonomy | 모든 tuple이 `identity_unavailable` / `qg_absent` / `qg_decided_no` 중 정확히 하나; category union parity와 pairwise intersection 0 |
| taxonomy/runtime layer separation | runtime Lua stable-ID field 부재를 tuple별 `identity_unavailable`로 오분류하지 않고 Gate 3 common plumbing prerequisite로 기록 |
| Recipe identity unavailable/mismatch | name mapping·runtime inference·silent deletion 없이 category-specific responsibility 및 Gate 3 `BLOCKED` |
| legacy-only owner disposition | fresh `qg_absent`/`qg_decided_no`의 exact `L4-RAT-08` tuple/hash binding; preserve/removal은 Gate 3 계속 차단, QG authority 선택도 adopted positive row + fresh census 전 효과 0 |
| legacy removal denominator | 별도 visible-row correction 전후 producer `(FullType, recipe_id)` denominator와 raw `recipe_only` 동일; 색인 삭제/collector-visible denominator 전환 금지 |
| Gate 3 failure scope | Change 2 이후 policy-dependent current diff 0, existing renderer/fallback 유지, overall `blocked`, pre-seal/prerequisite staging만 허용 |
| mixed Recipe presentation rejection | legacy fallback 유지 시 adaptive QG projection/Source count/current install 0; 임시 legacy identity 생성 금지 |
| QG-only exposure | `qg_only > 0` 및 `qg_recipe_only > 0` 각각 decision packet에 신규 user-visible identity/count 기록 |
| pre-seal threshold supply | explicit `L4-RAT-01` proposal parameter의 value/source/hash 기록; validator/test literal authority 없음 |
| owner policy gate | seal 부재 시 policy-dependent implementation 진입 금지 |
| `Base.223BulletsMold` / current 1 | Recipe 즉시 표시, requirement 전량 접근 |
| synthetic/current 2 | 모든 row open |
| exact 8 | small/open |
| exact 9 | dense/compact |
| `Base.Tongs` / current source count | total parity, compact initial, full access |
| Recipe + Right-click | peer Source partition, union parity |
| Recipe-only / Right-click-only | absent peer Source count `0`, empty section 없음 |
| duplicate display labels | 서로 다른 identity 모두 보존 |
| duplicate identity | fail-closed |
| search no-result | original total 보존 |
| search clear | full identity set 복원 |
| Recipe requirements 0/multiple | blank block 없음, atom 전량 접근 |
| malformed requirement | none/zero와 구분 |
| locale-unrepresentable requirement | 다른 locale raw fallback 없이 row-local unavailable |
| navigation unavailable | 다른 target 추정 없음 |
| locale refresh | stale query/text 없음, base order parity |
| Browser generation flip | old projection/query/row callback 전부 invalidated |
| normalized external row | 동일 presentation contract |
| raw external text | semantic inference 0 |
| detail shrink | scroll bound/clamp 정상 |
| policy authority parity | offline/runtime threshold와 Source order 동일 |
| generated no-mutation | `not_applicable(no_generated_mutation)` 근거와 current generated mutation 0 |
| generated mutation | Layer 4 owner decision + complete successor identity + authorized safe install 전 runtime/package 진입 금지 |
| Layer 4 contract/writer blocked after Gate 3 PASS | projection-dependent Changes 3~8/10 deferred, existing renderer/fallback 유지, non-public mutation-independent subject만 진행, overall `partial`, mixed/full/canonical claim 금지 |
| cross-layer generalization rejection | DVF 3.3 successor를 Layer 4 installer/descriptor authority로 자동 재사용하지 않음 |
| validation path selection | Gate 3/Layer 4 install result에 따라 V1~V6 required/N/A set 고정; N/A를 PASS/BLOCKED 또는 arbitrary omission으로 처리하지 않음 |
| canonical promotion | review/owner seal subject와 canonical diff exact parity |

### Manual Validation

실제 Project Zomboid UI에서 다음을 확인한다. visual hierarchy, overflow, 실제 mousewheel reachability와 실제 제작 UI navigation만 manual-exclusive evidence다. identity/count/state/locale parity처럼 automated matrix와 겹치는 나머지 항목은 automated evidence를 대체하지 않는 in-game confirmation으로 기록한다.

1. **[in-game confirmation]** Korean locale에서 `Base.223BulletsMold`를 열어 Recipe와 세 requirement atom이 master section click 없이 보이는지 확인한다.
2. **[in-game confirmation]** `Base.Tongs`를 열어 초기 화면이 모든 row로 채워지지 않고 total/Recipe count가 보이는지 확인한다.
3. **[manual-exclusive]** `Base.Tongs`의 full view를 열어 마지막 interaction까지 실제 mousewheel과 기존 detail scroll 하나로 접근할 수 있는지 확인한다.
4. **[in-game confirmation]** dense search에서 hit, duplicate label, no-result, clear를 확인한다.
5. **[manual-exclusive]** Recipe+Right-click item에서 두 Source heading의 visual weight가 동등하고 count/control overflow가 없는지 확인한다.
6. **[manual-exclusive]** search/fold 뒤 Recipe navigation이 실제 제작 UI의 원래 target을 여는지 확인하고 crafting이 실행되지 않는지 확인한다.
7. **[in-game confirmation]** requirement fold/open과 item switch를 반복해 다른 item state가 섞이지 않는지 확인한다.
8. **[in-game confirmation]** dense full view 아래쪽에서 compact로 전환해 scroll이 유효 범위로 clamp되는지 확인한다.
9. **[in-game confirmation]** English locale로 바꿔 control/row/requirement text가 갱신되고 identity order가 유지되는지 확인한다.
10. **[in-game confirmation]** Browser normal context-menu path, legacy Wiki fallback과 Alt Tooltip에 회귀가 없는지 확인한다.
11. **[manual-exclusive]** screen `1024x768`, `1280x720`, `1920x1080`에서 각각 실제 Browser panel/detail 폭·높이와 UI scale을 evidence에 기록하고 header/search/control overflow와 mousewheel conflict가 없는지 확인한다. 이는 대표 matrix이며 모든 resolution 지원 claim이 아니다.
12. **[manual-exclusive]** `IrisBrowserTheme.lua`의 변경 유무와 사용한 exact theme token을 closeout에 기록하고, 변경 시 세 크기에서 visual regression을 확인한다.

### Validation Limits

- all-locale validation은 수행하지 않는다. KO/EN과 existing fallback만 claim한다.
- dense literal search는 localized row label과 Recipe display name만 검색한다. requirement atom text 검색은 검증 및 기능 범위 밖이다.
- 모든 external mod schema/behavior를 보증하지 않는다. normalized fixture contract만 검증한다.
- 모든 resolution/UI scale 조합을 검증하지 않는다.
- multiplayer와 long-session behavior를 검증하지 않는다.
- QG Evidence coverage completeness나 실제 게임의 모든 interaction 존재 여부를 검증하지 않는다.
- Layer 3 prose quality 또는 item-page information sufficiency를 검증하지 않는다.
- performance, memory, FPS/frame-time 개선을 claim하지 않는다.
- disposable package projection PASS는 package publication/release/Workshop readiness가 아니다.

---

## 8. Risk Surface Touch

### Authority

- QG positive line을 presentation의 유일한 Layer 4 source로 정리하므로 authority 경계에 직접 닿는다.
- 의미 생산물은 수정하지 않지만 `surface`와 `label_key`를 structural contract로 소비한다.
- capability/recipe-index fallback의 presentation 역할 제거는 audited structured crosswalk와 결합 gate를 통과한 exact subject에서만 수행하며 public API는 유지한다.
- `qg_absent`와 `qg_decided_no`는 technical identity plumbing failure와 분리된 owner-reserved legacy-row disposition이다. planning `qg_absent=0`이지만 fresh census drift에 같은 판단 표면이 필요하므로 `L4-RAT-08`을 조건부로 함께 적용한다. 이는 QG Evidence/decision authority를 Browser나 구현자에게 이전하지 않는다.
- Source-only grouping과 threshold proposal은 owner policy seal 전 current policy가 아니다. seal 뒤에도 UI policy이며 semantic authority가 아님을 문서와 code boundary로 고정한다.
- generated Layer 4 mutation이 있으면 Layer 4-specific generation/install decision, exact successor identity와 protected installation surface를 만진다.
- canonical top-document write는 independent review와 owner canonical seal 뒤에만 수행한다.

### Runtime

- Browser detail rebuild, widget lifecycle, outer scroll, item state와 locale refresh에 닿는다.
- dense list에서 생성되는 label/button 수가 많아질 수 있으나 nested scroll이나 virtualized semantic subset을 도입하지 않는다.
- status-bearing lookup은 private path를 추가하므로 existing public caller를 깨지 않게 해야 한다.
- detail build의 단일 lookup과 Browser generation/locale state invalidation을 함께 변경한다.

### Compatibility

- public `IrisAPI.UseCases` return shape와 existing require path를 보존한다.
- Browser/Wiki가 공유하는 ViewModel field를 additive하게 확장한다.
- legacy capability/Recipe presentation cutover는 각각 audited identity crosswalk와 결합 `capability_only == 0 AND recipe_only == 0` hard gate에 종속된다.
- Gate 3 실패 시 mixed legacy/QG projection을 제공하지 않고 기존 presentation behavior를 유지한다.
- Recipe navigation target과 requirement atom schema를 보존한다.
- normalized external row는 exact schema를 만족할 때만 지원하며 legacy raw inference는 약속하지 않는다.

### Sealed Artifact

- QG semantic output, evidence와 decision을 재판정하지 않는다.
- requirement locale payload가 필요하면 current producer를 통한 additive schema로만 생성한다.
- generated Lua를 직접 수작업으로 고치지 않는다.
- producer regeneration, disposable report/package와 current safe installation을 분리한다.
- partial generation은 current로 노출하지 않고, mutation branch는 Layer 4 owner decision → off-live complete candidate → exact successor → authorized safe installation 순서를 따른다.

### Public-Facing Output

- Menu의 interaction section 초기 상태, counts, empty/fault 문구, search와 requirements 표시가 바뀐다.
- Tooltip은 변경하지 않는다.
- verified-empty 문구는 evidence scope를 분명히 하고 실제 게임 기능 부재를 보증하지 않는다.
- Recipe/Right-click의 peer presentation이 시각적 우선순위를 만들지 않게 한다.
- `qg_only`/`qg_recipe_only`는 기존 legacy surface에 없던 신규 노출일 수 있으므로 exact decision-packet disclosure 없이 owner seal 입력으로 사용하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- private projection이 label/requirement를 분석하기 시작하면 Browser가 semantic authority를 침범할 수 있다. exact structured fields만 허용하고 raw inference guard를 둔다.
- owner-reserved threshold/grouping/order를 계획 또는 machine output이 스스로 current policy로 승격할 위험이 있다. owner policy seal 전 execution ceiling과 staging-only 문서를 강제한다.
- QG context-menu line과 legacy capabilities를 동시에 row source로 유지하면 중복 또는 상이한 count가 생긴다. presentation은 QG line 하나로 통일하고 legacy API는 compatibility surface로만 남긴다.
- legacy/QG count만 같은 상태에서 cutover하면 capability-only 또는 Recipe-fallback-only identity를 잃을 수 있다. 두 structured crosswalk의 `capability_only == 0 AND recipe_only == 0`을 hard gate로 둔다.
- Recipe name/localized label로 legacy fallback을 QG에 맞추면 동명이거나 이름 drift가 있는 row를 잘못 흡수할 수 있다. producer-level `recipe_id`와 `rp.recipe.*`/`uc.recipe.*` lineage만 crosswalk identity로 허용한다.
- `qg_absent`/`qg_decided_no`를 data-contract 결함과 한 묶음으로 처리하면 구현자가 QG coverage/decision 변경 또는 legacy row 제거를 임의로 수행할 수 있다. disjoint taxonomy와 exact `L4-RAT-08` disposition으로 책임을 분리하되 raw `recipe_only == 0` gate는 유지한다.
- `label_key`를 영구 public contract로 과도하게 승격할 위험이 있다. current generator contract와 private identity 사용 범위를 문서에 명시한다.
- 향후 `surface=both`가 생길 때 자동으로 임의 Source에 넣을 위험이 있다. 현 버전에서는 fail-closed하고 multi-membership policy를 별도 결정하게 한다.
- UI policy를 sealed semantic artifact로 만들면 offline/runtime 책임이 중복된다. threshold와 disclosure는 runtime presentation constant로 유지한다.
- generated candidate validation을 current installation으로 오독하거나 canonical staging patch를 current decision으로 오독할 수 있다. Layer 4 owner-approved install subject와 owner canonical seal을 각각 별도 gate로 둔다.
- DVF 3.3 successor를 generic artifact installer로 오독할 수 있다. Retirement consumer census의 non-Layer3 migration `0`과 Layer 4-specific owner decision을 hard gate로 둔다.

### Runtime Risk

- dense full view의 많은 widgets가 detail rebuild 비용과 viewport 길이를 늘릴 수 있다. current max 40을 PZ Kahlua runtime harness와 manual in-game UI에서 검증하되 performance improvement를 claim하지 않는다.
- nested scroll을 넣으면 Browser outer scroll과 wheel ownership이 충돌한다. 하나의 outer scroll만 사용한다.
- content shrink 후 기존 scroll offset이 남으면 빈 detail 화면이 보일 수 있다. 매 rebuild 뒤 clamp를 검증한다.
- query/rebuild마다 widget callback이 stale row를 가리킬 수 있다. callback payload를 stable identity/action object에 결속하고 rebuild 시 widget reference를 폐기한다.
- Browser generation flip 뒤 FullType/locale가 같다는 이유로 stale projection을 재사용할 수 있다. state key에 browser generation을 포함한다.
- Recipe requirements가 긴 small list는 여전히 페이지를 길게 만들 수 있다. 1~8에서 completeness와 즉시 접근을 우선하며 threshold 변경으로 숨기지 않는다.

### Compatibility Risk

- public lookup shape 변경은 Wiki/외부 caller를 깨뜨릴 수 있다. private additive API만 추가하고 golden/acceptance test로 보호한다.
- status lookup과 legacy field를 별도 호출하면 같은 item에서 fault/empty가 갈릴 수 있다. one lookup → two projections 계약과 invocation-count test로 막는다.
- capability fallback 제거가 QG에 아직 없는 legacy action을 숨길 수 있다. 구현 전 census에서 capability identity와 QG context-menu identity parity를 exact 검사하고 mismatch가 있으면 cutover를 중단한다.
- Recipe fallback 제거가 QG에 아직 없는 legacy Recipe row를 숨길 수 있다. stable-ID crosswalk의 `recipe_only`가 0이 아니거나 identity 공급 자체가 불가능하면 fallback을 유지하고 각각 `identity_unavailable` / `qg_absent` / `qg_decided_no`의 책임 경계로 차단한다.
- Gate 3 실패 뒤 adaptive projection 일부만 설치하면 label-key 없는 legacy row identity와 Source count가 모호해질 수 있다. mixed state를 금지하고 Change 2 이후 current mutation을 0으로 유지한다.
- recipe name dedupe 제거로 row 수가 늘어날 수 있다. 이는 stable identity를 보존하는 의도된 변화이며 source identity parity로 판정한다.
- requirement locale schema 변경이 package artifact와 converter test를 깨뜨릴 수 있다. additive field와 disposable package parity를 사용한다.
- locale로 표현할 수 없는 requirement가 다른 언어 raw string으로 silent fallback할 수 있다. row-local unavailable 상태로 fail closed한다.
- generated schema 변경이 validation 뒤 current path로 바로 복사될 수 있다. authorized Layer 4 safe install 전 current/runtime/package write를 금지한다.
- Gate 3 failure의 `blocked`와 Gate 3 PASS 뒤 Layer 4 contract/writer failure의 `partial`이 혼동될 수 있다. 전자는 Change 2 이후 mutation 0, 후자는 non-public mutation-independent subject만 허용하는 별도 manifest로 구분한다.
- Browser fallback WikiPanel은 fixed-size이므로 dense behavior가 동일하지 않다. normal Browser 경로를 primary claim으로 제한하고 fallback은 회귀/안전성만 검증한다.

### Regression Risk

- single/small 자동-open이 기존 사용자의 접힘 기대를 바꾼다. 이는 로드맵 목표에 따른 의도된 public behavior이며 threshold tests로 고정한다.
- Source heading이 Recipe를 Right-click보다 중요하게 보이게 할 수 있다. 동일 visual treatment와 fixed-order 설명으로 완화한다.
- search가 duplicate label을 한 건으로 합치거나 base order를 바꿀 수 있다. identity list와 order parity를 매 query마다 검사한다.
- locale 변경 뒤 이전 언어 query/result가 남을 수 있다. locale generation invalidation을 acceptance test로 고정한다.
- threshold를 Python/Lua에 중복 정의하면 boundary behavior가 갈릴 수 있다. data-only Lua policy module을 단일 authority로 사용하고 offline/runtime observed parity를 검증한다.
- fault 문구가 raw internal error를 노출할 수 있다. user-safe localized status와 diagnostic reason을 분리한다.
- verified-empty 문구가 closed-world claim으로 읽힐 수 있다. “현재 Iris 검증 자료” 범위의 문구만 사용한다.
- Tooltip이나 Layer 3가 interaction presentation 로직을 재사용하면서 깊이 계약이 흔들릴 수 있다. Tooltip 변경 금지와 Layer 3 non-mutation guard를 둔다.

---

## 10. Rollback Plan

rollback 단위는 presentation layer와 private status/projection의 additive 변경이다.

1. owner policy seal 전에는 current mutation이 없어야 하므로 staging report/packet만 보존하거나 폐기하고 current rollback은 수행하지 않는다.
2. 새 density renderer, search/state/policy module과 translation key 사용을 되돌린다.
3. `IrisBrowserInteractionRenderer.lua`를 이전 flat deterministic section renderer로 복구한다.
4. private ViewModel/status fields는 caller가 없으면 제거하고 public UseCases facade는 계속 유지한다.
5. Recipe crosswalk/cutover gate가 통과하지 않았으면 current recipe connection/index fallback을 유지하거나 복구하며, legacy-only row를 fault/empty로 치환하지 않는다.
6. generated candidate가 authorized installation 전이면 off-live candidate만 폐기하고 current generation을 건드리지 않는다.
7. generated successor가 설치된 뒤 rollback이 필요하면 predecessor exact path/hash snapshot과 Layer 4 owner-approved installer의 correction/rollback 절차를 사용한다. Install report와 실패 evidence는 historical trace로 보존한다.
8. canonical promotion 전이면 staging top-doc patch만 수정한다. promotion 뒤 canonical correction이 필요하면 owner-sealed additive correction으로 수행하며 기존 decision/history를 삭제하지 않는다.
9. syntax, focused acceptance, PZ Kahlua runtime harness와 disposable package validation을 다시 실행한다.

다음은 rollback하지 않는다.

- QG Evidence와 current use-case decisions
- Layer 3 body/DVF artifact
- retirement closeout, retained governance/history와 inactive Layer 3 predecessor generation
- unrelated 사용자 변경

interaction omission이나 navigation mismatch가 발견되면 adaptive renderer만 비활성/rollback할 수 있다. fault를 zero로 바꾸거나 source row를 대표 subset으로 줄여 임시 통과시키지 않는다.

---

## 11. Governance Constraints

- `docs/Philosophy.md`가 최상위 설계 권위다.
- `docs/EXECUTION_CONTRACT.md`의 Heavy execution disclosure/evidence/closeout 규율을 적용한다.
- Iris는 확인된 사실만 설명하며 증거가 부족할 때 추론하지 않는다.
- user-facing surface는 Menu와 Alt Tooltip뿐이다. Browser/Detail/Wiki는 Menu 내부 구성 또는 fallback이며 새 독립 surface가 아니다.
- Tooltip은 Alt에서만 표시되고 최대 4줄이라는 current 계약을 유지한다.
- Recipe와 Right-click은 독립적이고 동등한 Source다.
- Static capability는 제3 동등 interaction Source가 아니다.
- Layer 4 production은 QG가 소유하고 Browser는 sort/fold/layout/density/basic exposure만 소유한다.
- 이 계획의 Browser policy proposal은 owner seal 전 current decision이 아니며 policy-dependent implementation을 허가하지 않는다.
- `recipe_only` taxonomy는 migration failure의 원인/책임 분류이지 QG 또는 legacy 사실의 우열 판정이 아니다.
- `qg_absent`/`qg_decided_no`의 legacy-row 처리는 `L4-RAT-08` owner disposition 대상이며, 이 계획은 QG decision 변경·재판정·coverage 추가 또는 tuple-specific removal correction을 직접 실행하지 않는다.
- requirement는 Recipe-local이며 item-global capability, ranking, recommendation 또는 filter 근거가 아니다.
- exclusion은 positive action이나 verified-empty의 closed-negative evidence가 아니다.
- runtime은 read-only이고 player/world/game state를 변경하지 않는다.
- PZ runtime은 100% Lua이며 offline Python을 runtime dependency로 넣지 않는다.
- 새 semantic taxonomy, ranking, representative selection, raw mod inference를 도입하지 않는다.
- public facade 변경은 additive compatibility를 우선하며 breaking change는 별도 승인 없이는 허용하지 않는다.
- generated artifact는 authoritative producer를 통해서만 변경한다.
- authoritative producer의 regeneration/validation은 current installation이 아니다. Generated diff가 있으면 Layer 4-specific owner decision, complete off-live generation, stateless validation, exact successor identity와 authorized safe install이 필요하다.
- DVF 3.3 generation/install contract를 Layer 4로 일반화하지 않는다. Cross-layer reuse는 actual obligation equivalence와 별도 owner decision 없이는 금지한다.
- Gate 3이 실패하면 Change 2 이후 policy-dependent implementation 전체가 `blocked`다. Gate 3 PASS 뒤 Layer 4 generation/install contract만 blocked인 경우에는 non-public mutation-independent subject만 진행하며 overall closeout은 `partial`이다.
- machine validation, independent review, owner policy/canonical seal과 generated installation은 서로 대체하지 않는다.
- canonical top documents는 staging patch → exact subject independent review → owner canonical seal 뒤에만 additive write한다.
- 이 계획 수정 요청, reviewer verdict 또는 구현 결과에서 owner seal을 추론하지 않는다.
- 선택된 execution path에서 required인 validation command가 없거나 exit code가 0이 아니면 PASS가 아니라 BLOCKED/FAIL로 보고한다. `not_applicable(no_subject)` command에는 이 규칙을 오적용하지 않는다.
- package projection 검증과 release/publish readiness를 구분한다.
- `docs/iris_item_page_information_sufficiency_plan.md`의 assessment scope와 이 presentation implementation scope를 합치지 않는다.

---

## 12. Expected Closeout State

현재 planning input과 pending seals를 그대로 두고 실행하면 expected closeout은 `blocked`다. 허용되는 closeout은 fresh census/taxonomy, `L4-RAT-08` decision input, isolated off-live plumbing evidence와 no-current-mutation 증명까지이며, 아래 목록은 별도 prerequisite가 실제로 채택되어 Gate 3이 통과한 뒤의 full target이다.

full 완료 시 다음 상태가 모두 성립해야 한다.

- `L4-RAT-01`~`L4-RAT-07`의 exact owner policy seal과, fresh census에 `qg_absent` 또는 `qg_decided_no`가 있으면 exact `L4-RAT-08` tuple disposition이 implementation/prerequisite subject에 결속된다.
- owner policy seal 전 runtime/generated current/canonical top-document mutation 0이 증명된다.
- capability/QG exact crosswalk의 `capability_only == 0`과 legacy Recipe/QG Recipe stable-ID crosswalk의 `recipe_only == 0`이 결합 cutover 전에 통과한다.
- 모든 observed `recipe_only` tuple의 category union parity, category pairwise intersection 0과 category-specific responsibility가 증명되며, owner disposition은 raw gate를 우회하지 않는다.
- `separate_legacy_removal_scope`는 채택 여부와 무관하게 producer legacy denominator와 Gate 3을 변경하지 않으며 migration 해소 근거로 사용되지 않는다.
- legacy Recipe presentation fallback identity 전부가 structured QG Recipe identity와 navigation target으로 흡수되어 QG absorption loss가 0이다.
- 한 detail build가 description lookup을 한 번만 실행하고 status/legacy projections의 ordered line identity가 일치한다.
- 정상 lookup에서 확인된 positive-empty 상태와 data/lookup fault가 Menu에서 구분된다.
- `0 / 1 / 2~8 / 9+`의 네 presentation 상태가 하나의 private policy로 구현된다.
- `Base.223BulletsMold`의 유일한 Recipe와 모든 requirements가 master section 조작 없이 보인다.
- `Base.Tongs`는 current source total을 보존하면서 compact로 시작하고 full view에서 모든 identity에 접근할 수 있다.
- header에서 total과 Recipe/Right-click count를 확인할 수 있다.
- fresh `qg_only`/`qg_recipe_only` 신규 user-visible exposure가 있으면 exact identity/count가 owner decision packet과 sealed subject에 결속된다.
- Recipe와 Right-click은 peer Source section으로 표시된다.
- Source 내부 base order는 locale와 무관하게 QG order를 보존한다.
- representative selection, importance ranking, semantic grouping과 source inference는 0이다.
- dense search는 base order와 total을 보존하고 clear 시 full identity set을 복원한다.
- duplicate display label은 소실되지 않고 duplicate identity는 fail-closed한다.
- Recipe requirements와 navigation target은 stable interaction identity에 결속된다.
- requirement는 item-global 의미로 승격되지 않는다.
- selected locale에서 표현 불가한 requirement는 다른 locale raw fallback 없이 row-local unavailable로 표시된다.
- item/locale/rebuild 이후 stale query, wrong row state, invalid scroll offset이 남지 않는다.
- Browser generation flip 뒤 stale interaction projection/state가 남지 않는다.
- normalized external row에는 같은 contract를 적용하고 raw external text는 추론하지 않는다.
- public UseCases facade와 existing Browser/Wiki/Tooltip entry path에 지원 범위 내 회귀가 없다.
- required Python, Lua syntax, standalone/mock Lua, PZ Kahlua runtime, manual in-game UI와 disposable package 검증 결과가 축별로 기록된다.
- declared generated diff가 없으면 `not_applicable(no_generated_mutation)` 근거가 있고, diff가 있으면 Layer 4-specific owner decision, complete successor, safe-install evidence와 installed runtime/package identity가 있다.
- exact subject의 eligible independent review와 owner canonical seal 뒤 `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`가 실제 구현 상태와 일치한다.

`docs/EXECUTION_CONTRACT.md`의 closeout state를 다음처럼 적용한다.

- owner policy seal이 없어 pre-seal ceiling을 넘지 못하면 `blocked` 또는 실제 수행 범위에 맞는 `partial`이며 구현 완료를 claim하지 않는다.
- Gate 3이 실패하거나 `L4-RAT-08`이 필요하지만 absent/stale이면 closeout은 `blocked`다. Change 2 이후 policy-dependent current diff, mixed projection과 canonical promotion은 모두 0이어야 한다.
- code가 구현됐지만 required runtime/manual/installation/review/seal 축이 남으면 `implemented_only` 또는 `partial`이며 `complete`를 사용하지 않는다.
- generated mutation branch에서 Layer 4-specific safe installation이 없으면 current runtime/package installation을 claim하지 않는다.
- Gate 3 PASS 뒤 authorized Layer 4 contract/writer 부재로 mutation branch가 blocked이면 projection-dependent scope를 `deferred`, non-public mutation-independent subject와 overall closeout을 `partial`로 기록하고 adaptive/mixed presentation, Recipe fallback removal, full KO/EN requirement localization, installed-current/package 및 canonical-complete claim을 하지 않는다.
- independent review 또는 owner canonical seal이 없으면 canonical/sealed closeout이 아니며 top-document promotion 완료를 claim하지 않는다.
- `complete`는 required gate 전부와 `validated / out_of_scope / unvalidated_but_in_scope` ceiling이 기록되고 `unvalidated_but_in_scope`가 비어 있을 때만 사용할 수 있다.

최종 closeout claim은 다음 범위로 제한한다.

```text
Iris Menu의 Layer 4 presentation은 current QG interaction identity를 보존하면서
interaction density에 맞는 공개/compact 상태, Source count와 lossless full access를 제공한다.
```

완료가 자동으로 의미하지 않는 것은 다음과 같다.

- Iris가 실제 게임의 모든 Recipe/Right-click action을 알고 있음
- verified-empty가 world-level 기능 부재를 증명함
- QG Evidence coverage completeness
- Layer 3 또는 item-page information sufficiency 해결
- 모든 외부 모드/locale/resolution 호환
- performance 개선
- package publication, deployment, release 또는 Workshop readiness
- owner seal 없이 proposed contract가 current decision이 됨
- candidate regeneration/validation 또는 package PASS만으로 current installation이 됨
- machine PASS 또는 owner seal만으로 independent review가 됨
