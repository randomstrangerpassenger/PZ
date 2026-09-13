# Iris DVF 플레이어 관점 용도 설명 전환 — Implementation Plan

> 작성일: 2026-09-11  
> 수정일: 2026-09-12 — 상세 정보 기준, 근거 추적 범위, 최소 모델 변경 허용 및 검증 실행 통합 반영.  
> 상태: planned — 코드베이스 조사에 근거한 실행 계획. 구현·재생성·제품 수락은 이 문서 작성에 포함하지 않는다.  
> 양식: [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md)  
> 입력: 사용자 제공 「Iris DVF 플레이어 관점 용도 설명 전환 — 종합 로드맵」 및 현재 checkout.  
> 상위 기준: [Philosophy.md](Philosophy.md), [DECISIONS.md](DECISIONS.md), [ARCHITECTURE.md](ARCHITECTURE.md), [ROADMAP.md](ROADMAP.md), [EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md).

이전 검토안의 실행 준비도 PASS는 구현·corpus 생성·전수 검토·B/C 후보 생성·실제 PZ 수락의 완료를 뜻하지 않는다. 이번 개정은 사용자 요청에 따라 전체 의미 교정 범위를 유지하면서 구현 선택과 검증 실행을 유연하게 한다. §4의 코드·입력 조사 기준일은 최초 작성일인 2026-09-11로 유지한다.

---

## 1. Objective

Iris Layer 3의 exact case-sensitive FullType 2,105개에 공통 플레이어 관점 공개 용도 판정을 적용하여, KO/EN compact·expanded가 확인된 활용·기능·결과를 먼저 설명하도록 교정한다. 모든 accepted fact를 공개 문장으로 만들지 않되, 확인된 독립 활용과 그 의미를 바꾸는 조건은 보존한다.

기존 r6 → 의미 블록 → 공통 설명 합성 경로를 이어서 사용한다. 전수 8,420개 좌표를 새 기준으로 재판정하고, 검수된 successor compact와 expanded를 각각 기존 Tooltip B와 Menu C에 연결한다. 런타임은 완성된 원문과 표시 단위를 조회·표시한다.

표현 결함이 남은 항목과 근거 부족으로 침묵하는 항목을 구별하며, 변경량·부재 감소율만으로 완료하지 않는다.

---

## 2. Scope

- 현재 조사 입력과 과거 수락 corpus, B/C 후보의 identity 및 적용 범위 정리.
- 기존 composition 내부의 전역 공개 용도 판정, 독립 활용 grouping, qualifier 배치, KO/EN 실현 교정.
- 전체 대상의 공개 용도 판단·설명 결과 대조와, 정보 부족·관계 누락·조건 충돌에 필요한 저장소 내부 근거 추적 및 기존 상류 owner correction.
- 전체 재생성 및 2,105개 × 2개 locale × 2개 surface의 의미 검토.
- 새 Tooltip S2 후보 생성, 동일 corpus의 Menu expanded 재결속, 격리 stage/ZIP 생성과 관련 검증.
- 같은 후보를 이용한 실제 PZ Tooltip·Browser Detail·Wiki 관찰. 미관찰이면 구현 완료와 제품 수락을 분리한다.
- 기존 계약·audit/report·walkthrough에 successor 범위와 결과 기록.

### Explicitly Out Of Scope

- 현재 live pointer 전환, strict production finalization, 게임 폴더 자동 설치, release/Workshop publish, commit/push.
- A 및 DVF-L3-01~06 재구축, Layer 2 분류·Layer 4/QG 재설계, Tooltip S1/S3/S4 및 opening lifecycle 재설계.
- Menu 전체 UI 재설계, unrelated refactor, 정규 검증 체계 확대, 전체 repository Run A/B 신규 수행.
- 기존 dirty/deleted/untracked 변경의 정리·복원·일괄 덮어쓰기.

### 종합 로드맵의 선택 항목에 대한 실행안

아래는 원 로드맵의 양안이 합의한 내용이라는 주장이 아니라, 현재 구현을 확인해 이 계획에서 선택한 범위다.

| 항목 | 이 계획의 선택과 근거 |
|---|---|
| Menu C | 이미 `build_menu_product()`와 두 UI consumer가 구현되어 있으므로 동일 successor 재결속을 포함한다. 신규 Menu 구축 단계는 두지 않는다. |
| 실제 PZ 수락 | B/C의 새 content-dependent 표시 수락까지 최종 complete 조건에 포함한다. 자동 검사까지만 끝나면 `implemented_only`다. |
| Determinism | 변경 producer와 기존 product node의 제한된 재생성 결정성 검사를 재사용한다. 전체 checkout Run A/B나 별도 comparator는 추가하지 않는다. |
| Migration | 새 소비 계약 이전이 아니라 기존 계약 안의 corpus/owner/package 재결속으로 검증한다. 별도 migration authority를 만들지 않는다. |
| Schema | 기존 schema/field와 소비 좌표를 우선 활용한다. 정확한 의미 전달에 필요한 최소 모델 변경 및 관련 기존 reader/consumer·version의 일관된 수정은 범위 안에서 허용한다. 기존 필드에 의미를 억지로 넣거나 우회 자료를 만들지 않는다. 새 외부 API·별도 authority·전면 migration이 필요할 때만 범위 재검토 대상으로 삼는다. |
| Contract | 기존 composition contract에 날짜가 있는 successor 절을 추가한다. 과거 수락 의미를 소급 변경하거나 새 독립 authority 문서를 만들지 않는다. |
| 독립 reviewer | 별도 외부 Reviewer를 필수 gate로 만들지 않는다. 자체 전수 판정의 한계를 기록하며, 독립 검토가 실제 없으면 독립 검토 완료를 주장하지 않는다. |

---

## 3. Non-Goals

- 모든 게임 사실의 발견, accepted fact 29,202개 전체의 진위 재감사, 모든 unresolved·absence 해소.
- 웹·외부 위키·아이템 이름·기존 prose로 새로운 기능이나 효과를 추론하는 작업.
- 추천, 효율 평가, 우열 비교, 대표 `primary_use` 선정.
- FullType별 완성 문장 hardcode 또는 runtime semantic engine.
- 2,105개 전부의 인게임 개별 관찰, 모든 모드·해상도·UI scale·멀티플레이 환경 보장.
- audit 자료의 fact authority 승격, 새 seal/receipt/proof tree/validation authority 신설.
- Iris 전체 freeze-ready, RTC-ready, publish-ready 판정.

---

## 4. Assumptions

### 조사 시점에 확인한 입력

현재 파일을 PowerShell `Get-FileHash`와 `ConvertFrom-Json`으로 읽었다. 두 해시는 첨부 로드맵 및 `docs/review/uses/items.json`의 조사 subject와 일치한다. 이것은 raw input 일치 확인이며, 정상 adopted reader 실행 또는 새 의미 품질 수락을 뜻하지 않는다.

| 대상 | 현재 checkout SHA-256 |
|---|---|
| `Iris/build/description/composition/descriptions.json` | `1df567f8442ba93b76b4390fb8962d5ff98d7489223be2a5ea2a7edb0e424478` |
| `Iris/build/description/composition/blocks.json` | `048d16806c5dc47254e47b35bbaffa62c7f2c7de0447ce92f88dcd701583ed52` |
| 과거 COMPOSITION-3 및 B/C 수락 기록의 descriptions | `ba0fc047b3a613e7ef98d2d762cfbd10c1996a02ad4e6f96d1bffa61878262d0` — 현재 bytes와 다름 |

| 분모 | 현재 JSON 또는 기록에서 확인한 값 | 적용 경계 |
|---|---:|---|
| 대상 | 2,105 | exact FullType 집합은 실행 시 case-sensitive 동등성까지 재검증 |
| accepted facts / blocks / grouped blocks | 29,202 / 10,304 / 1,591 | 현재 blocks summary |
| 전체 좌표 | 8,420 | 누락 좌표 없이 네 상태를 모두 기록 |
| 현재 present / absent / failed | 7,936 / 484 / 0 | 각 locale·surface마다 present 1,984, absent 121 |
| 과거 present / absent / failed | 8,054 / 366 / 0 | `ba0fc047…` 수락 corpus의 기록, 현재 분모로 사용 금지 |
| 기존 결함 고유 아이템 | 1,599 | 현재 조사 subject의 재검토 출발점, 전체 검토 대체 불가 |

첨부 §2.6의 present 8,054 / absent 366은 현재 해시의 집계와 맞지 않는다. 현재 `iris_dvf_use_audit.md`는 7,936 / 484로 기록하며 실제 JSON과 일치한다. 계획 실행의 baseline은 후자를 사용하고 과거 숫자는 보존한다. 부재 121은 item 수, 484는 surface 수다.

### 확인한 코드와 제품 상태

| 실제 경로/함수 | 현재 역할과 이 계획에 주는 제약 |
|---|---|
| `composition_results.produce()` | `recovery.load_adopted()` 이후 의미 블록을 구성하고 `recovery_relations.enrich()`로 채택 관찰에 연결된 구조화 참여자·결과를 보강한다. composer가 원본을 임의 해석하지 않는다. |
| `description_composition_planner.plan()` | fact/branch/qualifier application을 unit으로 구성한다. `DETAIL_FUNCTIONS`, recipe context 및 detail-only fallback은 공통 용도 판정 관점에서 검토해야 한다. |
| `description_composition_uses.prepare()/frames()` | 일부 관리·획득 정보를 내부에 두고 세척·연료·발화·개봉 등 명시적 frame을 만든다. 전역 판정이 이미 완료됐다는 근거는 아니다. |
| `description_composition_results._expanded_remaining()` / `_clauses()` | frame 미처리 unit을 역할·조건별 묶음과 `_core()`로 문장화한다. generic leftover 공개 경로의 주요 교정 지점이다. |
| `compose_item()` | preserved refs/internal uses와 공개 surface를 분리하지만, 빈 결과 reason은 일반적인 `no accepted content` 계열이다. accepted fact 존재와 공개 용도 부재의 원인을 구별해야 한다. |
| `tooltip_s2_supply.DESCRIPTION` | 현재 `1df567…`에 결속되어 있다. 코드 상수 변경 자체는 B 후보 생성·사용자 수락의 증거가 아니다. |
| `product_projection.read_menu_inputs()` / `build_menu_product()` | 현재 description/block binding은 조사 해시다. `ACCEPTED_TOOLTIP` 및 `ACCEPTED_DESCRIPTION`은 과거 B ZIP/`ba0fc047…`를 가리킨다. 새 corpus에는 새 B owner/ZIP이 필요하다. |
| Menu Lua 경로 | `IrisLayer3DataLookup → layer3_renderer.getDisplay → IrisItemDetailModelAssembler → IrisWikiSections`를 통해 Browser/Wiki가 ordered units를 표시한다. runtime 의미 복구 계층을 추가할 이유가 없다. |

현재 문서는 B v3를 과거 후보에 대한 실제 PZ 수락 완료로, C를 `implemented_only`로 기록한다. [C closeout](iris_dvf_expanded_menu_structuring_common_candidate_recovery_closeout.md)의 후보는 `ba0fc047…` descriptions / `b0b1f8…` blocks를 사용했다. 따라서 현재 source binding과 과거 후보 수락은 같은 상태가 아니다. ZIP 파일의 현재 존재·bytes 및 정상 reader 동작은 실행 Change 1에서 확인한다.

저장소에는 이미 관련 Python/Lua/JSON 수정과 문서 삭제·신규 파일이 있다. 이 계획은 HEAD만이 아니라 관찰한 working tree를 출발점으로 삼으며, 실행 재개 시 delta를 다시 확인한다. 삭제된 과거 문서를 현재 계약 파일로 전제하지 않는다.

---

## 5. Repository Areas Affected

### Code

경로는 저장소 루트 기준이다. 아래는 계획상 수정 후보이며 전부의 수정을 강제하지 않는다.

- `Iris/tooling/src/iris_tooling/domains/layer3/description_composition_planner.py`
- `Iris/tooling/src/iris_tooling/domains/layer3/description_composition_uses.py`
- `Iris/tooling/src/iris_tooling/domains/layer3/description_composition_results.py`
- `Iris/tooling/src/iris_tooling/domains/layer3/description_composition_model.py`
- `Iris/tooling/src/iris_tooling/domains/layer3/description_composition_families.py`
- `Iris/tooling/src/iris_tooling/domains/layer3/description_composition_lexicon.py`
- `Iris/tooling/src/iris_tooling/domains/layer3/description_composition_ko.py`, `description_composition_en.py`
- 원인 확인 시에만: 같은 디렉터리의 `composition_rules.py`, `composition_model.py`, `composition_results.py`, `recovery_relations.py` 및 기존 semantic/recovery owner.
- 소비 재결속: 같은 디렉터리의 `tooltip_s2_supply.py`, `product_projection.py`, `product_install.py`; `Iris/tooling/src/iris_tooling/domains/tooltip_t1/s2_candidate.py`와 기존 static projection 경로.
- 패키지 결속: `Iris/tools/Layer3PackageProjection.psm1`, 기존 `package_iris.ps1` 경로.
- 기존 검사: `Iris/build/description/v2/tests/test_layer3_composition.py`, `test_layer3_description_composition.py`, `test_layer3_product_integration.py`, `Iris/tooling/tests/test_tooltip_t2_projection.py`.
- Lua는 소비 계약상 필요가 확인된 경우만 수정한다: `Iris/media/lua/client/Iris/Data/IrisLayer3DataLookup.lua`, `layer3_renderer.lua`, `UI/Detail/IrisItemDetailModelAssembler.lua`, `UI/Wiki/IrisWikiSections.lua`, `IrisWikiPanel.lua`, `UI/Browser/IrisBrowserDetail.lua` 및 기존 Lua harness.

### Docs

- 본 계획, `docs/iris_dvf_description_composition_contract.md`, 필요 시 `docs/iris_dvf_semantic_block_integration_contract.md`.
- `docs/iris_dvf_use_audit.md`, `docs/review/uses/items.json`, `docs/iris_dvf_use_description_report.md` 및 기존 review HTML.
- `docs/iris_layer3_composition_walkthrough.md`, `docs/iris_layer3_product_walkthrough.md`, `docs/iris_tooltip_supply_walkthrough.md` 등 해당 실행 기록.
- 최종 상태에 필요한 범위의 `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`. input hash에 미치는 영향을 먼저 확인한다.

### Config

- 새 설정·feature flag·validation authority는 추가하지 않는다.
- `Iris/validation/execution/required_validations.json`은 관련 기존 node 확인용이다. 이번 교정만으로 membership를 늘리지 않는다.
- 기존 B owner/공통 product descriptor의 candidate binding은 기존 writer를 통해 갱신한다. current route/pointer는 변경하지 않는다.

### Generated Artifacts

- `Iris/build/description/composition/descriptions.json`; 상류 교정 필요 시에만 같은 폴더의 `blocks.json`.
- 기존 audit/report와 그 항목별 판정 자료. 조사 baseline을 덮기 전에 원문과 identity를 보존한다.
- 기존 격리 `.tmp/tooltip/`, `.tmp/menu/` 흐름의 새 후보, static Lua, Menu generation, owner/product descriptor, ZIP.
- r6 adoption과 기존 수락 ZIP은 predecessor로 보존하며 제자리 재발행하지 않는다.

---

## 6. Planned Changes

아래 Change는 작업 책임을 설명하며 독립 Gate·승인·단계별 테스트 실행 의무가 아니다. 데이터 의존성을 지키는 범위에서 묶거나 순서를 조정할 수 있다. 각 **Validation**은 필요한 확인 내용이며, 읽기·생성 문장 검토는 작업 중 수행하고 자동 검사는 §7의 마지막 최소 묶음에서 공유한다. 같은 사실/관계/후보의 확인을 단계마다 재실행하거나 별도 보고서·workspace로 나누지 않는다.

### Change 1 — Exact subject와 B/C baseline 확정

**Purpose:** 조사·구현·제품 수락의 서로 다른 subject를 분리한다. 로드맵 Phase 1에 대응한다.

**Files:** 두 composition JSON, `docs/review/uses/items.json`, 기존 B/C closeout, `tooltip_s2_supply.py`, `product_projection.py`, 기존 reader.

**Implementation Notes:**

1. dirty delta, 두 JSON raw SHA, exact FullType 집합, 네 좌표, 실제 state 집계를 재확인한다. 문서 작성 이후 변경이 있으면 이 계획의 고정 baseline과 비교한다.
2. 조사 input identity와 일치하는 경우 기존 결함 목록을 재현 가능한 출발점으로 사용한다. 다르면 바뀐 item/locale/surface 및 원문·ref delta를 구별한다.
3. `ba0fc047…` 당시 후보와 현재 입력의 차이를 설명한다. 과거 candidate가 없으면 historical record와 실제 확인 가능 범위를 나누고 bytes를 추정하지 않는다.
4. `recovery.load_adopted`, composition reader, B/C reader의 정상 소비 조건과 source/document dependencies를 확인한다. hash를 대체하거나 검사를 우회해 읽지 않는다.
5. 이 단계에서는 corpus를 재생성하지 않는다. 결과는 기존 audit/walkthrough의 baseline 절에 기록한다.

**Validation:** JSON 정상 load, case-sensitive ID 집합 동등성, 8,420 좌표 중복/누락 없음, raw hash 및 reader 결과 구별. 조사 일치만으로 과거 수락을 승계하지 않는다.

### Change 2 — 공통 공개 용도 판정 계약과 의미 계획

**Purpose:** 모든 unit에 공개 여부와 배치 이유를 부여한다. Phase 2에 대응한다.

**Files:** 기존 composition contract, planner, uses, results/model.

**Implementation Notes:**

- 기존 내부 plan에 `use`, `result/target`, `qualifier`, `supporting detail`, `self-management`, `internal`, `unresolved` 책임을 구분한다. 이는 이번 composition의 공개 선택·배치와 audit 설명을 위한 내부 분류다. 새 runtime enum/API, 생태계 공통 장기 taxonomy, 별도 authority schema 또는 새 closeout state로 확대하지 않는다.
- 각 분류는 payload 의미, explicit relation, fact-local scope를 근거로 한다. item name/profile/input order 또는 완성 문장 패턴으로 공개 우선순위를 추정하지 않는다.
- 결과·도구·대상이 구조화되어 있으면 그 구체성을 사용한다. 역할명만 있는 경우 근거 이상의 결과를 발명하지 않는다.
- 모든 accepted fact는 공개 use/해당 use의 qualifier·detail/비공개 보존/미확정 중 하나로 추적 가능해야 한다. 비공개 fact 보존과 독립 활용 공개 coverage를 별도 검사한다.
- compact는 모든 독립 활용을 직접 표현하거나 근거 있는 활용군으로 포괄한다. 서로 포괄되지 않는 활용을 expanded에만 옮겨 compact 누락을 정당화하지 않는다.
- expanded는 활용별 결과·대상·대안 → 의미상 필수 조건 → 필요한 detail 순으로 구성한다. 하나의 절차를 여러 독립 용도로 세지 않는다.
- detail은 플레이어가 활용 목적·대상·결과·중요한 제한을 이해하는 데 기여해야 한다. 실행 절차·자체 관리·내부 처리 사실이라는 이유만으로 상세에 포함하지 않는다. 조건부 회수, 도구 대안, 재사용/소모의 차이는 필요한 의미일 수 있지만 소지품 이전·반복 validity·이동 중단 등을 자동으로 따라붙이지 않는다. supporting detail 분류는 기존 절차 나열의 대체 경로가 아니다.
- 미처리 입력을 `_expanded_remaining()`/`_core()`로 자동 공개하지 않는다. 미분류를 failure 또는 명시적 unresolved로 기록하고, 단순 absence로 성공 처리하지 않는다.
- 일반 qualifier 제거와 사용 의미를 바꾸는 qualifier 생략을 구별한다. 현재 `frames.emit()`의 qualifier refs 축소 역시 각 주장에 조건 누락이 없는지 검토한다.
- acquisition은 별도 정보로 보존한다. 용도 문장 내부에 넣지 않는 것과 기존 acquisition 정보 공급을 없애는 것을 구별한다.

**Validation:** 관리/실제 기능, 대상/도구/재료, 조건부/확정 결과, 다중 활용, 미확정 관계의 대조 사례 및 전체 입력의 미분류 경로 확인. ref 보존만으로 활용 공개를 통과시키지 않는다.

### Change 3 — 근거 부족과 표현 부족의 전수 원인 판정

**Purpose:** 실패 위치를 기존 owner에 귀속한다. Phase 3에 대응한다.

**Files:** audit/report, blocks, `recovery_relations.py`, 필요가 입증된 기존 semantic/recovery 경로.

**Implementation Notes:**

1. 2,105개 전체의 `accepted fact/block → public plan → realization`에서 활용 선택과 실제 설명을 대조한다. `repository source → accepted fact/block`의 재추적은 정보 부족·관계 누락·조건 충돌·역할 오귀속 등 원인 확인이 필요한 곳에 집중한다. 이미 확인된 공통 source/관계는 적용 범위를 확인하여 결과를 공유한다. 모든 아이템의 원본이나 29,202개 사실의 진위를 처음부터 재감사하는 단계로 확대하지 않는다.
2. 우선 조사군은 활용 정보 부족 241개, 설명 부재 121개, compact 독립 용도 누락 17개, 역할 혼동 4개, 범위 불일치 1개다. 서로 겹칠 수 있으며 전체 검토의 대체 집합이 아니다.
3. 각 gap을 projection 문제 / block 관계 문제 / accepted fact 누락 / source evidence 부족으로 귀속한다. source locator와 fact/ref 관계, 수정 경로, 남은 이유를 기존 item record에 기록한다.
4. provenance-bound participant/result 누락은 기존 `recovery_relations.enrich()` 책임과 대조한다. accepted fact의 의미를 바꾸는 수정은 상류 owner에서 처리하고 composer의 임의 source parse로 우회하지 않는다.
5. 상류에 근거가 없으면 evidence gap을 남긴다. 표현 실패나 미구현 규칙을 evidence gap으로 숨기지 않는다.

**Validation:** 모든 residual의 이유·owner 확인, bounded correction 전후 fact/관계 delta 검토. 전면 신규 사실 수집이 필요하면 해당 항목을 unresolved로 남기고 범위를 자동 확대하지 않는다.

### Change 4 — 공통 composer 교정 및 전체 재생성

**Purpose:** 새 기준을 네 surface에 적용한다. Phase 4에 대응한다.

**Files:** planner/uses/results/families/lexicon/KO/EN, 기존 composition tests, 두 JSON.

**Implementation Notes:**

- locale-neutral 공개 계획을 먼저 만들고 KO/EN이 같은 use/group/qualifier 범위를 실현하도록 한다. 언어별 문법은 독립 처리하고 cross-locale fallback은 금지한다.
- family는 검증된 use plan을 표현하는 역할로 제한한다. 알려진 family 바깥의 입력도 공통 공개 판정을 통과해야 한다.
- unclassified leftover 공개, 역할명 단독 anchor, 관리/내부 정보의 핵심 승격을 제거한다. 기존 기능군의 올바른 대상·도구 대안·조건부 결과는 유지한다.
- `internal_uses`, preserved refs, qualifiers, relations, unresolved, segments, detail links 등 기존 구조를 우선 활용한다. 필요한 최소 모델 변경은 기존 소비자와 함께 일관되게 처리하고 변경 이유를 기존 기록에 남긴다. 공개되지 않은 accepted fact가 있는데 `no accepted content`라고 잘못 설명하지 않도록 reason을 실제 원인과 맞춘다.
- 전체 regeneration 전에 baseline bytes를 보존한다. 상류 변경이 없으면 불필요하게 blocks를 다시 쓰지 않는다. 변경됐다면 blocks와 description input binding을 함께 생성한다.
- 8,420개 state, before/after 원문·ref delta, absence 증감 원인, successor raw SHA를 기록한다. 새 absent 수를 과거 484로 강제하지 않는다.

**Validation:** 기존 두 composition node에 의미 있는 반례를 통합한다. 독립 use 손실, 잘못된 umbrella, qualifier 오적용, 확률적 결과의 확정화, locale divergence, 실패의 absence 은폐를 검사한다. 생성 성공은 의미 품질 수락과 분리한다.

### Change 5 — 2,105개 전수 품질 재판정

**Purpose:** Phase 5의 전수 의미 검토를 완료한다.

**Files:** 기존 `iris_dvf_use_audit.md`, `review/uses/items.json`, `iris_dvf_use_description_report.md`, review HTML.

**Implementation Notes:**

- 기존 1,599개와 결함 미확인 385개, 부재 121개 모두 재검토한다. KO와 EN 원문을 각각 읽고 compact/expanded 의미 관계를 비교한다.
- item별 네 좌표의 상태, 실제 활용, 근거 refs, grouping, 조건 scope, 결함 및 수정 결과를 기록한다. 도구는 추출·집계 보조이며 의미 수락 authority가 아니다.
- terminal disposition은 용도 설명 적합 / 정당한 공개 부재 / 근거상 unresolved / upstream evidence gap / 수정 필요 표현 결함으로 구분한다. 미검토는 별도로 남긴다. 이는 항목별 review record의 판정 설명이며, 의미 원천 권한이나 §12의 실행 closeout state를 새로 정의하지 않는다.
- 표현 결함이 있으면 Change 2~4의 공통 규칙 또는 해당 상류 owner로 돌아간다. 개별 FullType 완성 문장 패치로 봉합하지 않는다.
- 수정 후 영향 좌표를 다시 읽고 전체 ledger의 coverage를 확인한다. 이미 검토한 결과도 입력/ref가 바뀌면 영향을 재판정한다.

**Validation:** 2,105 items와 8,420 coordinates의 판정 누락 0, 알려진 수정 필요 표현 결함 0, 모든 absence/unresolved에 근거와 이유 존재. 원인을 설명할 수 있는 표현 결함도 해결 대상이다. 미분류·미구현 규칙·표현 실패를 unresolved/evidence gap으로 바꿔 완료하지 않는다. 자동 패턴 검사나 defect 감소율은 이 조건을 대체하지 않는다.

### Change 6 — 새 B 후보 생성 및 동일 corpus의 C 재결속

**Purpose:** Phase 6의 same-corpus product candidate를 만든다.

**Files:** `tooltip_s2_supply.py`, 기존 T1/S2 candidate·static producer, `product_projection.py`, `product_install.py`, package projection, 기존 product/supply tests 및 Lua harness.

**Implementation Notes:**

1. 전수 검토된 corpus의 compact/state/ref를 B 공급 경로로 넘기고 기존 owner binding을 갖는 새 격리 Tooltip 후보를 생성한다. S1/S3/S4 내용과 역할, exact support 및 out-of-DVF 처리를 보존한다.
2. 과거 accepted B는 rollback 기준이다. successor S2가 바뀌므로 과거 B static bytes 전부와의 동등성을 새 B 생성 조건으로 삼지 않는다. 변경 S2와 비변경 슬롯·동작을 구별해 검증한다.
3. C는 새 B 후보 ZIP/owner와 같은 successor description/block을 입력으로 사용한다. `ACCEPTED_TOOLTIP`의 과거 ZIP과 새 description SHA를 섞지 않는다.
4. 새 B 생성 후 C의 보존 검사는 **그 새 B 후보**의 bytes를 기준으로 한다. 기존 accepted/raw-byte 보호를 해제하거나 해시만 고쳐 mismatch를 숨기지 않는다.
5. Menu ordered segments, 연속 표시 단위, refs/detail destinations를 보존한다. 기존 grouping은 표시 책임이며 use 우선순위·요약을 다시 결정하지 않는다.
6. 같은 stage와 실제 ZIP에서 B S2와 C expanded의 item/locale/corpus identity를 대조한다. invalid payload는 fault, 정상 부재는 absent로 유지한다.
7. install/recovery는 격리 후보에서 기존 경로를 사용한다. live current/promotion guard, writer lock 및 source-drift 보호는 유지한다.

**Validation:** 기존 supply/product node와 그 자식 Lua/package 검사. Tooltip Alt·opening·최대 네 물리적 줄·fit-failure, Menu 두 consumer·locale/item 전환·scroll, Layer 4 접근 회귀, stage/ZIP readback을 포함한다. B/C 같은 generation 주장에는 실제 새 후보 identity가 필요하다.

### Change 7 — 실제 PZ 표시 수락 및 closeout

**Purpose:** Phase 7과 성공 조건을 정확한 후보에 닫는다.

**Files:** 기존 walkthrough/결과 기록, audit/report, 필요한 current-state 문서.

**Implementation Notes:**

- 새 공통 ZIP의 SHA와 실제 관찰 결과를 연결하고, 관찰자·locale·검사 사례와 결과를 기록한다. PZ 버전·해상도/UI scale 등 환경 메타데이터는 제공된 범위에서 기록하며, 미제공 값은 `unknown / not reported`로 남긴다. exact candidate에 대한 실제 관찰이 확인되었다면 환경 값 미제공만으로 수락을 차단하거나 추가 보고를 필수 gate로 만들지 않는다. 표시 수락 주장은 실제 보고된 관찰 범위로 제한하고 확인되지 않은 환경으로 일반화하지 않는다.
- Tooltip: 가장 긴 KO/EN compact, 독립 활용이 많은 항목, S2 부재, 대상 밖 item, Alt/opening 및 S1/S3/S4 공존을 관찰한다. 원문 삭제·대표 용도 선정으로 fit 문제를 숨기지 않는다.
- Menu: Browser/Wiki 모두 긴 expanded, 복수 활용·복수 branch, 조건이 많은 항목, 부재/획득 정보 경계, 좁은 폭·스크롤 끝·Layer 4 접근을 관찰한다. `Base.Plank`, `Base.Lipstick` 등 기존 선행 조건 사례를 포함하되 새 후보의 위험 목록으로 보완한다.
- 같은 item/locale에서 compact의 실제 활용이 expanded와 모순되지 않는지 확인한다. 인게임 표본 검사는 오프라인 전수 검토와 목적·분모가 다르다.
- 결함이 있으면 원인 owner를 수정하고 변경된 후보에 필요한 재검토를 수행한다. 이전 ZIP의 관찰을 새 ZIP에 자동 승계하지 않는다.
- 실제 PZ 관찰이 없으면 그 축을 `unvalidated_but_in_scope`로 남기며 구현·자동 검사 완료까지만 보고한다. 사용자가 exact candidate의 관찰 결과를 제공한 경우에는 실행자의 직접 PZ 접근 여부와 환경 메타데이터의 완전성을 별도 합격 조건으로 요구하지 않는다.

**Validation:** 새 후보에 대한 내용 의존 표시 수락. B의 과거 수락과 C의 과거 Lua harness 성공은 successor actual PZ 증거를 대신하지 않는다.

---

## 7. Validation Plan

### Automated Validation

실행 위치는 `PZ` 루트, shell은 PowerShell이다. 아래는 사용 가능한 기존 관련 명령이며 **전부를 독립 Gate로 실행하라는 목록도, 이 계획 작성에서 실행한 테스트 목록도 아니다**. 변경에 필요한 coverage를 기존 node의 실제 범위와 대조해 마지막 최소 묶음으로 선택한다. 정확한 관련 명령 exit 0일 때만 PASS로 기록하고 도구 부재는 BLOCKED다.

- 자동 검사는 구현과 문장 교정이 준비된 뒤 가능한 마지막에 모아 수행한다. 계획에 없는 중간 테스트·신뢰도 확보용 추가 실행을 하지 않는다. 문장 읽기와 필요한 corpus 생성은 품질 교정 작업으로서 진행 중 수행할 수 있다.
- 기본 대상은 설명 조합, S2 공급, B/C product의 변경된 계약이다. 상류/블록 검사는 해당 생산자·계약을 수정한 경우에만 추가한다. 하위 node가 같은 입력·생산자·실행 경계의 해당 검사를 실제 포함하면 그 결과를 공유하고 재호출하지 않는다. 이름이 비슷하다는 이유만으로 coverage를 생략하지 않는다.
- 독립 node가 필요해도 가능한 같은 pytest 호출로 묶고 기존 생성 결과·짧은 후보 경로를 공유한다. 검사별 장기 중간 tree나 새 workspace를 만들지 않는다. 전체 Run A/B+comparator는 추가하지 않는다.
- Lua syntax는 같은 변경/생성 Lua와 필요한 roots를 product 자식 검사가 이미 검사하면 재사용한다. 기존 authority가 별도 명령 실행을 명시적으로 요구하거나 자식 검사의 범위가 부족한 경우에만 아래 별도 명령을 실행한다.
- 30~60초 간격으로 실행 상태·출력·진행 여부를 확인하고 무한루프나 비정상 장기 실행은 필요시 중단한다. 실패 후 수정 또는 새로 확인된 영향 때문에 필요한 재실행만 허용하며 이미 유효한 독립 결과는 재사용한다.

```powershell
# 블록/상류 관계를 수정한 경우
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract -q --tb=short

# 공통 공개 계획, 생성 및 상태/참조 계약
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition -q --tb=short

# 새 S2 및 owner 통합
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration -q --tb=short

# 공통 B/C candidate, Lua, package 및 recovery를 묶는 기존 product node
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract -q -s --tb=short

# Lua coverage가 product 자식 검사로 충족되지 않거나 별도 실행 의무가 있는 경우
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

product node의 기존 `detail_view_model_locale_harness.lua`, `tooltip_static_data_runtime_harness.lua`, `browser_interaction_density_acceptance_harness.lua`, candidate roots syntax 및 package 검사는 같은 final stage/ZIP을 사용한다. 자식 명령 실패를 부모가 숨기지 않으며 exact 명령·exit를 기록한다. 기존 검사가 같은 후보를 검증했다면 신뢰도 명목으로 반복하지 않는다.

기존 node가 과거 corpus 수치·binding을 고정했다면 새 의미 계약에 맞게 기대를 교정하되 identity/trace/absence/fault/owner 보호를 삭제하지 않는다. 변경 producer의 제한된 결정성과 입력 순서에 따른 의미 불변성은 해당 node 안에서 검사한다. 전체 repository 재현성으로 확대하지 않는다.

### Manual Validation

- Change 5의 8,420 좌표 전수 원문 및 근거 대조. KO/EN 각각의 자연스러움과 동일 의미 범위를 검토한다.
- Change 7의 실제 PZ 위험 기반 사례를 같은 ZIP으로 관찰한다.
- 이전 수락 corpus와 새 corpus의 부재 증감, 독립 활용 coverage, 조건·결과·도구 대안 delta를 검토한다.

### Validation Limits

- 이 문서 작성·개정은 Markdown만 변경하며 Python/Lua 구현·생성·테스트를 수행하지 않는다. 해시/JSON/코드 열람은 제품 검사 PASS가 아니다.
- Java/Gradle 및 JS/TS는 수정 범위가 아니므로 해당 검사를 실행하지 않는다. 범위가 바뀌면 각각 `.\gradlew test`, `pnpm biome check .`를 적용한다.
- 자동 구조·ref 보존과 전수 의미 검토, 실제 PZ 폰트/fit 수락을 서로 대체하지 않는다.
- 환경 메타데이터 미제공과 실제 관찰 부재를 구별한다. 전자는 `unknown / not reported`와 제한된 claim으로 기록하고, 후자는 실제 PZ 검증 미완료로 남긴다. exact candidate와 관찰의 연결은 유지한다.
- 멀티플레이·장시간 실행·외부 모드 sweep·전수 인게임 열람·배포 검증은 수행하지 않는다.
- 별도 Reviewer가 없으면 자체 판정이라는 한계를 남긴다. 현재 문서의 코드 조사만으로 기존 미관찰 축을 수락하지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

공개 표현의 판정 기준이 바뀐다. accepted facts와 관계의 기존 owner는 유지하고 composer는 공개 선택·배치만 소유한다. 계약에는 successor 적용일/subject를 명시하며 이전 완료 기록을 수정하지 않는다.

### Runtime Behavior Surface

표시 원문과 길이, Menu 표시 단위가 영향을 받는다. Tooltip lifecycle, S1/S3/S4, Menu navigation의 책임은 유지하며 표시 오류에 필요한 bounded correction만 허용한다.

### Compatibility Surface

기존 description 구조를 우선 활용하고 exact FullType/locale/state/refs의 의미와 소비 일관성을 유지한다. 필요한 최소 모델 변경은 producer와 기존 consumer·version을 함께 맞춘다. B owner와 C product/package identity 재결속이 필요하다. stale locale, malformed payload, predecessor fallback으로 실패를 숨기지 않는다.

### Sealed Artifact Surface

새 corpus와 candidate를 만든다. 이전 r6/adoption, COMPOSITION-3 및 B/C 후보 수락 identity는 historical evidence로 남긴다. 기존 manifest를 재사용하는 것은 새 governance 체계 신설을 의미하지 않는다.

### Public-Facing Output Surface

2,105개 Layer 3의 네 surface가 직접적인 변경 대상이다. 의미상 영향이 크므로 단순 문체 수정으로 분류하지 않는다. 단, 이번 계획 문서 작성 자체는 제품 변경을 수행하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- 공개 유용성을 이유로 새 사실을 생성할 위험: 모든 결과·목적을 기존 fact/관계에 연결하고 상류 correction은 기존 owner에서 수행한다.
- Layer 3 절차 축소가 Layer 4 정보를 삭제할 위험: S4/Recipe/Right-click/EvolvedRecipe는 별도 회귀 대상으로 유지한다.
- audit가 새 authority가 될 위험: 기록·검토 보조 역할과 공식 생산 경로를 구별한다.

### Runtime Risk

- 독립 활용 보존으로 compact가 길어질 위험: grounded grouping을 먼저 교정하고 실제 폰트·네 물리적 줄을 확인한다. fit 실패를 정상 부재로 수락하지 않는다.
- 긴 Menu units의 overflow·scroll 회귀: 두 UI와 item/locale 전환을 실제 후보에서 확인한다.
- 새 B와 과거 C의 혼합: 동일 corpus 및 실제 ZIP member/owner를 묶어 검사한다.

### Compatibility Risk

- 문서·source 변화가 adopted input identity를 깨뜨릴 위험: 정상 reader의 정확한 소비 경계를 확인하고 보호를 우회하지 않는다.
- 과거 B ZIP을 보존해야 한다는 검사를 successor 변경에 그대로 적용할 위험: 새 B 생성 전후와 C의 새 B 보존 시점을 구분한다.
- 기존 삭제 문서 또는 임시 후보의 존재를 가정할 위험: 실행 전 실제 파일·reader 상태를 확인하고 누락이면 영향 축을 BLOCKED로 남긴다.

### Regression Risk

- procedure 축소 중 회수 결과·도구 대안·조건부 활용 손실: fact 보존과 공개 use coverage를 별도 검증한다.
- 내부 unknown을 임의 정상 absence로 처리할 위험: reason/owner를 전수 기록하고 실패/미분류를 분리한다.
- 일부 family만 개선하고 leftover fallback이 재발할 위험: 전체 입력 disposition과 미처리 공개 경로를 검사한다.
- known defect 감소만으로 완료할 위험: 기존 결함 미확인 항목 포함 전수 재판정을 완료 조건으로 둔다.

---

## 10. Rollback Plan

1. 실행 시작 시 작업 대상의 현재 dirty bytes와 조사 baseline, 과거 제품 identity를 보존한다. `git reset`/`checkout`으로 사용자 변경을 되돌리지 않는다.
2. successor 후보가 독립 활용 손실, qualifier 왜곡, 근거 없는 결과, KO/EN 불일치, 설명 불가능한 신규 부재를 보이면 B/C 연결을 진행하지 않는다.
3. 후보 문제는 격리 stage에서 기존 `product_install`/recovery 경로로 되돌린다. live pointer는 이 계획에서 전환하지 않으므로 product current rollback은 원칙적으로 발생하지 않는다.
4. 공유 corpus 파일을 교체한 뒤 되돌려야 하면 이번 실행이 변경한 파일만 실행 직전 보관 bytes로 복구하고 description/block/consumer binding의 일관성을 확인한다.
5. 수정한 source와 조사 기록을 삭제해 결함을 숨기지 않는다. 과거 generic procedural fallback 재활성화를 해결책으로 삼지 않는다.
6. source evidence 부족은 unresolved로 containment한다. 전체 입력을 공통 규칙으로 설명할 수 없거나 scope 밖의 전면 사실 수집이 필요하면 완료를 중단하고 이유·owner·잔여 범위를 기록한다.

---

## 11. Governance Constraints

- Philosophy 준수: 근거 기반 정보, 추천·우열 금지, 근거 부족 시 침묵, 정보 표시만 수행.
- PZ runtime은 100% Lua. Python은 offline 생산·검증에 한정한다.
- Hub & Spoke/SPI 경계 유지. Pulse의 Iris 역의존이나 타 Spoke 직접 의존을 만들지 않는다.
- Recipe와 Right-click은 동등한 독립 관점이다. 한 관점의 정보를 다른 관점으로 흡수하지 않는다.
- 사용자-facing 표면은 Iris 메뉴와 Alt Tooltip 두 가지, Tooltip 최대 네 물리적 줄을 유지한다.
- 과거 complete/PASS는 당시 subject의 evidence다. successor에 승계하거나 소급 실패로 고치지 않는다.
- existing contract에 additive successor 절을 기록하고, 별도 승인·seal·receipt·validation authority를 신설하지 않는다.
- player-use disposition과 audit 판정은 composition 내부 판단·검토 기록에 한정한다. 이를 생태계 공통 taxonomy, 새 semantic authority/schema 또는 실행 closeout state로 승격하지 않는다.
- 현재 schema/reader를 우선 활용하되 §2에서 허용한 최소 모델·소비자 변경은 범위 안에서 수행한다. 새 외부 계약·authority 등 범위 밖 작업의 필요가 드러나면 잔여로 명시하고 조용히 확대하지 않는다.
- 정확한 exit 0 없이 PASS를 주장하지 않는다. 미실행·도구 부재·중단과 실제 실패를 구별한다.

---

## 12. Expected Closeout State

목표는 **complete — exact successor corpus의 전수 자체 의미 검토, 기존 B/C의 동일 corpus candidate 연결, 새 후보의 실제 PZ 표시 수락 범위**다. 아래는 한 번의 closeout에서 함께 판단할 결과 조건이며 각각 독립 Gate·승인·재실행을 요구하지 않는다. 모두 충족되어야 한다.

1. 조사 subject와 predecessor/successor identity가 구분되고 exact 2,105 FullType/8,420 좌표가 유지된다.
2. 모든 입력이 공통 공개 용도 판정을 거치며 자동 leftover 공개 경로가 남지 않는다.
3. 모든 확인된 독립 활용이 compact에 직접 또는 grounded grouping으로 보존되고 expanded에서 필요한 대상·결과·대안·조건을 설명한다.
4. 절차·자체 관리·내부 정보가 용도를 대신하는 알려진 표현 결함이 해결되며, 모든 absence/unresolved/evidence gap에 실제 이유가 있다.
5. 전체 KO/EN compact·expanded 재판정이 끝났고, 미검토·수정 필요 표현 결함이 남지 않는다.
6. 적용되는 기존 자동 검증이 exact exit 0이며, B/C와 실제 ZIP이 같은 successor corpus를 소비한다.
7. 새 후보의 Tooltip·Browser·Wiki 실제 PZ 관찰이 기록되고 content-dependent 결함이 해결된다. 환경 메타데이터가 일부 미제공되어도 exact candidate의 실제 관찰이 확인되면 해당 미제공만으로 완료를 차단하지 않으며, 수락 주장은 보고된 관찰 범위에 한정한다.
8. historical evidence, source/current 경계, runtime viewer 책임을 보존한다.

자동 검증·후보 생성까지 완료하고 실제 PZ 관찰이 없으면 **implemented_only**, 의미 교정/전수 판정이 남으면 **partial**, 필수 도구·근거·정상 reader/후보 소비가 막히면 해당 축을 **blocked**로 기록한다. 정당하게 설명된 evidence gap 자체는 complete를 막지 않지만 구현되지 않은 공개 규칙이나 표현 실패를 그 이름으로 남길 수는 없다.

완료 주장에는 exact corpus/ZIP, 검사 명령과 exit, 전수 판정 결과, 실제 관찰 범위, residual과 미검증 환경을 함께 명시한다. live activation·strict production finalization·release 및 Iris 전체 준비 완료는 이 계획의 완료 주장에 포함하지 않는다.
