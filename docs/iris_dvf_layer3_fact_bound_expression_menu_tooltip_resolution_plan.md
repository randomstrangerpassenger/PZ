# Implementation Plan

> **제목:** Iris DVF Layer 3 근거 결속 표현과 Menu·Tooltip 정보 해상도 구축\
> **문제 ID:** `DVF-L3-05`\
> **작성일:** 2026-09-05\
> **개정:** 2026-09-05 — accepted fact의 실제 Menu 표현 완료 조건, 복수 프로필별 조합 구조, 최소 Gate 원칙 반영\
> **상태:** 2026-09-05 실행 완료 — off-live expression authority `complete / adopted`; current product/runtime 미전환\
> **기준:** `Philosophy.md`, `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `EXECUTION_CONTRACT.md`, adopted DVF-L3-01~04 authority

---

## 1. Objective

Adopted Layer 3 의미 결과를 사실보다 강하게 확대하거나 대표 용도 하나로 축약하지 않고 KO/EN 설명으로 변환한다.

Exact case-sensitive FullType 2,105개에 대해 다음 두 Layer 3 설명 해상도를 같은 accepted fact authority에서 만든다.

- **Expanded Layer 3 description:** Iris Menu의 제3계층에서 사용할 상세 설명. Locale에서 모든 accepted Layer 3 fact를 보존하고, resolved acquisition의 장소·방식·조건을 반드시 포함한다.
- **Compact first-contact Layer 3 description:** 기존 Tooltip S2에서 사용할 첫 접촉 설명. L3-02의 first-contact obligation과 실제 accepted contributor를 기반으로, 대표 사실 선택 없이 사용자가 즉시 이해해야 할 기능·효과·활동 맥락·맥락별 역할을 한 logical row로 표현한다.

표현은 적용 가능한 프로필별 조합 문법을 사용한다. 프로필은 사실을 선별하거나 우선순위를 부여하지 않으며, 한 아이템에는 여러 프로필이 동시에 적용될 수 있다.

이번 결과는 독립적인 off-live Layer 3 description authority다. 현재 Menu·Tooltip payload, Lua runtime, generation pointer와 package를 전환하지 않는다. 후속 제품 통합은 이 결과를 재조사·재해석·재선택하지 않고 소비해야 한다.

---

## 2. Scope

- L3-01 semantic/provenance/expression/presentation 분리 계약을 소비한다.
- L3-02의 exact target, 적용 프로필, composition scope와 first-contact obligation을 소비한다.
- L3-03의 accepted non-acquisition facts 4,233개와 L3-04의 accepted acquisition facts 1,057개를 qualified reference로 결속한다.
- Fact-local condition/constraint, context-local role와 acquisition route condition을 보존한다.
- 복수 적용 가능한 프로필별 KO/EN 표현 규칙을 작성한다.
- 모든 accepted fact를 Menu용 expanded description에 표현한다.
- 실제 accepted first-contact contributor를 Tooltip S2용 compact description으로 조합한다.
- Menu와 S2의 represented fact/dependency, 정상적인 Tooltip detail omission, upstream first-contact gap을 구조적으로 추적한다.
- 독립 producer/loader, 단일 focused acceptance Gate와 adopted readback을 제공한다.

### Explicitly Out Of Scope

- L3-01~04의 정의, accepted fact, provenance, 조사 결과 또는 sealed member 수정.
- 미해결 non-acquisition 질문 9,900개와 acquisition unresolved 1,080개의 추가 조사.
- 기존 `primary_use`·single-core composer의 successor 의미 경로 재사용.
- Layer 2 분류와 Tooltip S1 수정.
- exact Recipe, Right-click action, EvolvedRecipe relation과 Tooltip S3/S4 수정.
- 현재 `IrisLayer3DataCurrent.lua`, static Tooltip payload, runtime Lua, generation pointer와 package/install 전환.
- 실제 PZ 화면 줄바꿈·가독성·인게임 동작 검증.
- 추천, 효율, 우열, 확률 환산 또는 근거에 없는 일반 게임 지식 생성.

---

## 3. Non-Goals

- 모든 아이템을 하나의 공통 문장 형태나 고정 문장 수로 맞추지 않는다.
- 한 아이템의 대표 프로필·대표 용도·대표 역할·headline fact를 선택하지 않는다.
- 정보가 적은 아이템을 generic filler로 채우지 않는다.
- Tooltip 한 logical row를 맞추기 위해 first-contact fact를 중요도·빈도·입력 순서로 탈락시키지 않는다.
- Menu 상세를 exact Layer 4 interaction catalogue로 확장하지 않는다.
- Authority 구축을 current 제품 적용 완료나 release readiness로 표현하지 않는다.
- 새 validation framework, recurring registry 또는 범용 proof package를 만들지 않는다.

---

## 4. Assumptions

### Adopted inputs

| Readpoint | SHA-256 | 역할 |
|---|---|---|
| `Iris/_docs/authority/dvf/layer3_successor/contract_manifest.json` | `6735c3eadafaf4c4fd51ae56c8d0748d32903ee996d53ed43bca38822cf0932a` | 복수 fact, 표현과 projection 경계 |
| `Iris/_docs/authority/dvf/layer3_investigation/manifest.json` | `47be8947a0b18745560b1e7e2463adbe86ab878e5e9fefd461f2a838c164290e` | exact target, profile, composition/first-contact scope |
| `Iris/_docs/authority/dvf/layer3_semantic_results/manifest.json` | `a3416672aa47fe4c6c84d9b8e9912377adda6e20e9eb679bf2d229cb9d3456bd` | accepted non-acquisition facts |
| `Iris/_docs/authority/dvf/layer3_acquisition_results/manifest.json` | `0281e7db661d2c37984568b715e53c97a3e78234b95b9fdfbb59ea1e31fa2a29` | accepted acquisition facts와 combined resolver 시작점 |

실행 시작 시 loader가 위 readpoint와 bound member를 검증한다. 불일치를 새 값으로 자동 갱신하지 않는다.

### Fixed denominators

- Exact FullType: 2,105
- Accepted non-acquisition facts: 4,233
- Accepted acquisition facts: 1,057
- Combined accepted facts: 5,290
- Fact × locale (`ko`, `en`): 10,580
- Acquisition resolved items: 1,025
- Acquisition unresolved items: 1,080
- Combined item investigation complete: 0

Item investigation incomplete는 이미 accepted된 fact의 표현을 막는 전역 Gate가 아니다. 반대로 accepted fact가 존재한다는 사실만으로 표현 승인이나 first-contact 충족을 자동 판정하지 않는다.

### Execution boundary

- Offline tooling의 implementation owner는 installed `iris_tooling` package다.
- Formal execution은 source-root `PYTHONPATH`/`sys.path` bootstrap에 의존하지 않는다.
- PZ에서 실행되는 Iris runtime은 계속 100% Lua다.
- Target identity는 exact case-sensitive FullType이며 trim, alias, casefold, Unicode normalization을 하지 않는다.
- Qualified fact reference는 최소한 authority identity와 fact identity를 함께 보존한다. Bare fact ID만으로 authority 사이 facts를 병합하지 않는다.

---

## 5. Repository Areas Affected

### Code

- `Iris/tooling/src/iris_tooling/domains/layer3/` 아래의 신규 expression/description producer와 loader.
- 구현자는 model, realization, projection, result 처리를 필요한 수의 모듈로 결합하거나 분리할 수 있다. 이 계획은 특정 파일 분할이나 내부 class 구조를 Gate로 삼지 않는다.
- 기존 `acquisition_consumption.load()`와 adopted semantic/acquisition loader는 읽기 전용으로 사용한다.
- 기존 `compose_layer3_shared.py`, `compose_layer3_item.py`, `compose_layer3_body_profile.py`의 primary/single-core 의미 경로는 successor producer로 사용하지 않는다.
- Focused validation source는 원칙적으로 `Iris/build/description/v2/tests/test_layer3_expression_results.py` 한 파일로 제한한다. 동등한 기존 위치가 더 적합하면 구현 시 하나의 focused source로 확정하고 closeout에 기록한다.

### Docs

- 현재 계획 문서.
- 구현 결과의 Layer 3 expression contract와 단일 closeout 문서.
- Adoption 성공 시 `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`에 exact readpoint와 제품 미전환 경계를 additive 기록한다.

### Config

- 새 Layer 3 description subject가 필요로 하는 최소 schema/rule/review 자료.
- 기존 current route, current authority manifest, validation registry와 source classification은 이번 작업에서 수정하지 않는다.
- `Iris/tooling/pyproject.toml`과 `Iris/tooling/uv.lock`은 새 dependency가 실제로 필요하지 않은 한 수정하지 않는다.

### Generated Artifacts

최종 authority root는 `Iris/_docs/authority/dvf/layer3_expression/`을 기본 위치로 사용한다.

반드시 제공할 논리적 readpoint는 다음뿐이다. 구현자는 독립 검증 가능성과 deterministic serialization을 유지하는 범위에서 여러 논리 단위를 한 파일에 합치거나 나눌 수 있다.

- Input/readpoint binding
- KO/EN fact-bound expressions와 review binding
- Item/locale별 expanded description과 compact S2 description
- Represented fact/dependency refs, Tooltip detail omission과 upstream gap state
- Manifest와 adoption receipt

별도 validation aggregation JSON, stage별 wrapper result, package forensic report, final-binding receipt를 recurring authority로 만들지 않는다. 단일 closeout이 실제 명령, exit code, subject hash와 validation ceiling을 기록한다.

---

## 6. Planned Changes

### Change 1 — Adopted fact와 dependency의 불변 입력 모델

**Purpose:** L3-03/04의 accepted facts 전체를 표현 과정의 유일한 의미 입력으로 고정한다.

**Implementation Notes:**

- `acquisition_consumption.load(root, manifest_binding, mode="adopted")` 또는 동등한 adopted loader 경로를 사용한다.
- 각 fact에 authority-qualified identity, exact FullType, kind/payload, provenance refs와 dependency refs를 보존한다.
- `context_role`은 연결된 `use_context` 안에서만 해석한다.
- Top-level condition/constraint의 역방향 적용 관계와 acquisition payload 내부 조건을 모두 찾을 수 있어야 한다.
- Rendered Menu/Tooltip prose, Layer 2/4 output, predecessor 설명과 profile label은 새 semantic fact의 입력이 아니다.
- Stable ordering은 직렬화용일 뿐 중요도나 표시 우선순위가 아니다.

**Validation:** 단일 focused Gate에서 exact 2,105 targets, 5,290 qualified facts, dependency closure와 adopted input binding을 검사한다.

---

### Change 2 — 복수 프로필별 설명 조합 문법

**Purpose:** 모든 아이템에 동일한 범용 문장을 적용하지 않고, 정보 종류에 맞는 설명 구조를 제공한다.

**Implementation Notes:**

- L3-02에서 적용 가능하다고 판정된 프로필과 composition scope를 사용한다.
- 음식, 도구, 무기, 의류, 용기, 문헌, drainable, crafting/cooking/world-work/direct residual 등 실제 적용 프로필마다 필요한 표현 문법을 둔다. 이는 닫힌 전역 enum이 아니며 실제 adopted profile registry가 authority다.
- 프로필은 다음만 결정할 수 있다.
  - 어떤 종류의 facts를 한 clause/block으로 조합할 수 있는가.
  - context와 context-local role을 어떤 문장 구조로 연결하는가.
  - 효과·상태·조건·제약을 어느 claim에 결속하는가.
  - expanded description과 first-contact description에서 어느 수준으로 풀어 쓰는가.
- 프로필은 fact의 존재, 중요도, 대표성 또는 의미 우선순위를 결정하지 않는다.
- 한 아이템에 적용 가능한 모든 프로필이 함께 기여한다. 하나를 primary profile로 선택하지 않는다.
- 여러 프로필이 같은 fact를 참조하면 fact identity로 중복 mention을 조정할 수 있지만 fact 자체를 삭제하거나 다른 fact와 합치지 않는다.
- 어떤 프로필에도 포함되지 않는 accepted fact는 residual composition으로 반드시 보존한다.
- 프로필마다 고정 문장 수나 전역 최대 fact 수를 두지 않는다.

**Validation:** 단일 focused Gate에서 multi-profile item, context-local role, residual fact와 입력 순서 변경을 검사한다.

---

### Change 3 — Fact-bound KO/EN expression

**Purpose:** 모든 accepted fact를 조건과 범위를 잃지 않는 사용자 문장으로 만든다.

**Implementation Notes:**

- Expression은 locale, text, represented fact refs, 실제로 표현된 dependency refs와 적용 rule/review identity를 가진다.
- KO/EN 규칙은 같은 source semantics를 사용하지만 문장 구조와 승인은 locale별로 독립적이다.
- 한 locale의 문장을 다른 locale의 fallback으로 사용하지 않는다.
- Shared clause와 aggregation은 허용하지만 ref만 metadata에 붙이고 실제 문장에서 기능·맥락·역할·조건을 지우면 represented로 인정하지 않는다.
- `여러 용도로 사용할 수 있다`, `생존에 유용하다`처럼 구체적인 활동·기능·효과를 지우는 generic aggregate를 금지한다.
- 기존 표현 문구를 참고할 수는 있지만 semantic admission은 accepted proposition과 dependency에서 다시 성립해야 한다. Predecessor prose를 사실 authority로 사용하지 않는다.
- 규칙으로 안전하게 표현할 수 없는 예외는 fact-bound freeform으로 작성하고 직접 검토한다.
- `expression_gap`은 candidate/partial 상태에서 결손을 숨기지 않기 위한 상태다. Missing rule, 미완료 번역, 미검토 freeform 또는 안전한 표현 실패가 남아 있으면 `complete`로 닫지 않는다.

**Validation:** `complete` 후보에서는 10,580 fact-locale pair 전부가 승인된 expression을 가져야 한다. Accepted fact가 없는 문장, stale review, locale fallback과 truth-changing dependency 누락은 허용하지 않는다.

---

### Change 4 — Expanded Layer 3 description

**Purpose:** Menu 제3계층이 accepted facts를 상세하게 전부 보존할 수 있는 설명 결과를 만든다.

**Implementation Notes:**

- Item/locale별로 0..N개의 deterministic description block을 만든다.
- Block grouping과 순서는 가독성과 재현성을 위한 것이며 중요도나 대표성을 뜻하지 않는다.
- 각 locale에서 `expanded represented fact set = accepted fact set`이어야 한다.
- Condition/constraint는 별도 문장이 아니어도 되지만 적용 대상 claim의 진실성이나 범위를 바꾸면 실제 문장에 표현되어야 한다.
- L3-04의 1,057 acquisition facts는 KO/EN 모두에서 장소·방식·조건을 보존한다. 서로 다른 route를 대표 경로 하나로 합치지 않는다.
- Acquisition unresolved는 획득 불가나 generic 획득 문장으로 바꾸지 않는다.
- Broad cooking/construction/repair context와 ingredient/tool role은 표현할 수 있지만 exact Recipe·action·target·result·requirement 목록은 만들지 않는다.

**Validation:** 단일 focused Gate에서 locale별 accepted/represented exact set equality와 acquisition subset equality를 검사한다. Expression gap이 하나라도 있으면 expanded description completion은 실패한다.

---

### Change 5 — Compact first-contact Layer 3 description

**Purpose:** 사용자가 Tooltip S2에서 아이템의 첫 기능·효과·활동 맥락을 실제로 이해할 수 있게 한다.

**Implementation Notes:**

- L3-02의 `(FullType, axis_id, scope_ref)` obligation과 accepted whole/partial contributor를 사용한다.
- Accepted first-contact contributor가 여러 개면 중요도·빈도·ordinal·profile label로 하나를 선택하지 않고 검토된 composition rule로 함께 표현한다.
- 서로 다른 사실을 합칠 때 각각의 구체적인 동사·대상·효과가 문장에 남아야 한다.
- S2는 item/locale당 0..1 logical row이며 CR/LF를 포함하지 않는다. 하나의 logical row 안에 여러 문장을 둘 수 있다. Character count나 임의 width proxy로 semantic truncation하지 않는다.
- Truth 또는 scope를 바꾸는 조건은 compact description에도 포함한다.
- Acquisition은 실제 first-contact obligation/contributor일 때만 S2에 포함하며 전역 필수로 만들지 않는다.
- Accepted first-contact contributor의 표현 또는 안전한 조합 실패는 정상 omission이 아니라 미완료 expression으로 처리하고 `complete`를 막는다.
- Accepted contributor가 없는 upstream unresolved obligation, scoped N/A 또는 실제 Layer 3 first-contact 부재는 구조화된 upstream/absence state로 남길 수 있다. 이를 공개 negative 문장으로 바꾸지 않는다.
- Menu의 accepted facts 중 first-contact 범위 밖 상세는 정상 Tooltip omission으로 추적한다.

**Validation:** 단일 focused Gate에서 `S2 represented ⊆ expanded represented`, accepted first-contact contributor 보존, omission partition, upstream gap 분리와 0..1 logical-row envelope를 검사한다.

---

### Change 6 — 독립 readpoint와 additive adoption

**Purpose:** 후속 제품 소비자가 raw source나 predecessor prose를 다시 해석하지 않고 두 Layer 3 설명 해상도를 읽게 한다.

**Implementation Notes:**

- Manifest는 input readpoints, producer/rule/review identity, exact target/fact denominators, 모든 data member path/hash와 deterministic serialization 규칙을 결속한다.
- Loader는 candidate와 adopted 상태를 구별하고 member/hash drift, path escape, unknown/duplicate ref와 mixed input을 거부한다.
- Output은 특정 후속 작업의 내부 구현에 맞춘 전용 포맷이 아니라 독립 Layer 3 description consumer contract로 제공한다.
- Adoption은 성공한 exact candidate와 사용자의 구현·채택 권한을 결속한다. 현재 실행 요청이 그 범위를 명확히 승인하면 별도 승인 Gate를 다시 만들지 않고 그 요청을 closeout에 기록한다.
- Adoption 명령은 exact candidate를 최종 위치에 기록한 뒤 같은 실행에서 adopted loader readback까지 수행하거나, 실패 시 receipt를 완료 상태로 남기지 않는다.
- 기존 L3-01~04, current product, media/runtime와 공용 registry는 변경하지 않는다.

**Validation:** 별도 final-binding, aggregation, preservation, adopted-readback Gate를 만들지 않는다. 단일 focused Gate가 성공한 exact candidate만 adoption 대상이며 adoption 명령의 fail-closed readback을 상태 전환 확인으로 사용한다.

---

## 7. Validation Plan

### Automated Validation

자동 acceptance Gate는 **하나**다.

구현 시 확정한 단일 focused test source를 installed `iris_tooling` 환경에서 한 번 실행한다. 이 한 Gate가 다음을 함께 검증한다.

- Installed package/module resolution과 source-root bootstrap 부재.
- Adopted L3-01~04 manifest/member binding.
- Exact 2,105 FullType, 5,290 facts, 10,580 KO/EN expression completeness.
- Qualified ref와 condition/context/acquisition dependency closure.
- Multi-profile composition과 no-primary/no-representative.
- Locale별 expanded represented set과 accepted set의 exact equality.
- Resolved acquisition fact의 KO/EN expanded description 보존.
- Accepted first-contact contributor의 S2 표현과 구체 의미 보존.
- S2/expanded/omission/upstream-gap reconciliation.
- Locale fallback, generic filler, Layer 4 exact relation 생성과 unresolved-to-negative 변환 부재.
- 동일 입력·규칙·review로 두 번 생성한 canonical output의 동일성.
- 기존 L3-01~04와 current product 경로의 변경 부재.

결정성 확인을 위해 두 번 생성하더라도 같은 focused test 안의 assertion으로 수행하며 별도 Gate나 별도 acceptance subject를 만들지 않는다.

비편집 installed package가 아직 현재 구현을 포함하지 않는 경우에는 `pyproject.toml`과 `uv.lock`을 바꾸지 않는 재설치를 환경 준비로 한 번 수행한다. 이는 acceptance Gate가 아니다. 단일 focused Gate는 실제 import된 package/module identity가 검사 대상 구현과 일치하는지 확인하고 stale package 또는 source-root override를 거부한다.

예상 명령 형태는 다음과 같다. 실제 module/test 경로가 구현 재량으로 달라지면 동등한 단일 명령을 사용하고 closeout에 기록한다.

```powershell
uv run --project .\Iris\tooling --no-sync python -I -B -m pytest -q .\Iris\build\description\v2\tests\test_layer3_expression_results.py
```

Adoption은 두 번째 acceptance Gate가 아니다. 성공한 exact candidate와 권한을 확인하고 materialize한 뒤 loader readback을 같은 상태 전환 안에서 수행한다. Readback이 실패하면 adopted/complete로 기록하지 않는다.

기존 L3-04 코드나 shared loader를 수정하지 않았다면 L3-04 focused suite를 다시 실행하지 않고 bound manifest/member와 실제 loader 성공으로 보존을 확인한다. 해당 shared code를 수정한 경우에만 직접 영향을 받는 기존 focused 검사를 추가한다.

### Manual Validation

Manual review는 별도 통과 Gate를 늘리는 절차가 아니라 expression rule/review 자료를 완성하는 콘텐츠 작업이다.

- 사용되는 모든 profile composition rule과 KO/EN realization rule을 실제 accepted fact branch에 대조한다.
- Rule 밖 freeform expression은 각각 검토한다.
- 최소한 다음 의미 유형을 포함한다.
  - 음식: 섭취 효과와 조리 재료 맥락을 함께 표현하되 exact 조리법은 표시하지 않는 사례.
  - 복수 프로필 아이템: 여러 맥락과 context-local role을 대표 선택 없이 표현하는 사례.
  - `Base.Worm`: 서로 다른 획득 경로와 조건을 Menu에서 보존하는 사례.
  - `Base.Generator`: world recovery 조건을 일반 제작·항상 획득 가능으로 확대하지 않는 사례.
  - Condition/constraint 또는 shared clause가 claim 범위를 실제로 제한하는 사례.
- 표현의 자연스러움은 rule branch와 freeform 범위에서 검토한다. 5,290 facts 각각에 대한 별도 문장 수작업 승인을 의무화하지 않는다.

### Validation Limits

- 실제 PZ 실행, Menu UI rendering, Tooltip physical wrapping과 Alt 동작을 검증하지 않는다.
- S1/S3/S4와 최종 0..4줄 payload 조합을 검증하지 않는다.
- Current generation, Lua runtime, package/install과 Workshop/release를 검증하지 않는다.
- 미해결 질문을 재조사하거나 source corpus 전수 정확성을 재인증하지 않는다.
- 모든 사용자 문장의 취향·문체·번역 품질을 item별로 전수 보증하지 않는다.
- 전체 repository suite와 외부 모드 compatibility sweep을 실행하지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

**Affected.** Accepted Layer 3 fact에서 KO/EN expression과 expanded/compact description을 만드는 새 off-live authority를 추가한다.

### Runtime Behavior Surface

**None.** Current Lua, current generation과 Menu·Tooltip runtime behavior는 변경하지 않는다.

### Compatibility Surface

**신규 내부 consumer contract만 Affected.** 기존 외부 API/SPI와 다른 모드의 동작은 변경하지 않는다.

### Sealed Artifact Surface

**Additive successor만 Affected.** L3-01~04와 current product artifact는 읽기 전용으로 보존한다.

### Public-Facing Output Surface

**Off-live content authority 수준에서 Affected.** 향후 표시할 문장을 만들지만 이번 단계에서 사용자가 보는 제품 텍스트는 바뀌지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- 프로필을 하나 선택하면 `primary_use`와 같은 대표 의미 구조가 되살아난다. 모든 적용 프로필의 동시 기여와 residual 보존으로 방지한다.
- Fact kind별 범용 문장만 사용하면 설명 깊이 불균형 문제가 반복된다. Profile composition과 locale realization을 분리한다.
- Projection이 fact를 새로 만들거나 Layer 4 output을 역입력하면 계층 독립성이 깨진다. Accepted Layer 3 facts만 의미 입력으로 허용한다.

### Runtime Risk

- 이번 작업은 runtime을 변경하지 않는다. Current product writer나 기존 composer를 실수로 호출하는 경로를 단일 focused Gate에서 거부한다.

### Compatibility Risk

- 새 multi-fact output을 기존 single-core schema에 그대로 주입하면 의미 손실이 생긴다. 이번 output은 독립 consumer contract이며 current adapter는 범위 밖이다.

### Regression Risk

- `expression_gap`을 정상 완료로 허용하면 실제 설명이 비어도 authority가 complete가 될 수 있다. Complete 후보에서는 모든 10,580 fact-locale expression을 요구한다.
- Fact refs만 보존하고 문장에서 조건·역할을 삭제할 수 있다. 실제 text scope를 review와 focused fixture로 확인한다.
- Tooltip 압축이 generic 문장이나 임의 선택으로 회귀할 수 있다. Accepted first-contact contributor의 구체 의미 보존을 검사한다.
- 여러 acquisition route가 한 문장으로 합쳐져 경로 차이가 사라질 수 있다. Route별 fact/dependency equality를 검사한다.

---

## 10. Rollback Plan

- Candidate 또는 단일 focused Gate가 실패하면 adoption하지 않는다. 선행 authority와 current product에는 변경이 없으므로 runtime rollback은 필요하지 않다.
- Adoption 상태 전환 중 readback이 실패하면 adopted receipt를 완료 상태로 남기지 않고 candidate와 실패 원인을 보존한다.
- 표현 결함은 fact/provenance를 바꾸지 않고 expression/rule/projection correction으로 처리한다.
- Input fact 결함이 발견되면 이번 단계에서 재판정하지 않고 해당 upstream authority correction으로 분리한다.
- 사용자 기존 변경이나 삭제 문서를 일괄 복구하지 않는다. 이번 실행이 만든 파일만 exact diff로 되돌린다.

---

## 11. Governance Constraints

- Iris는 근거에 기반한 사실만 설명하고 추천·효율·우열을 만들지 않는다.
- 근거가 없으면 추측이나 filler로 채우지 않는다.
- Menu와 Tooltip S2는 같은 Layer 3 facts를 서로 다른 깊이로 표현하며 모순되지 않는다.
- Layer 3는 broad interaction context를 설명할 수 있지만 exact Recipe·Right-click·EvolvedRecipe relation은 Layer 4에 남긴다.
- Acquisition은 모든 target의 필수 조사 축이고 resolved result는 Menu Layer 3의 필수 정보다. Tooltip 전역 필수는 아니다.
- `primary_use`, representative fact/role/profile과 semantic priority를 도입하지 않는다.
- Profile은 investigation/composition/first-contact scope이며 fact 선택기나 중요도 정책이 아니다.
- Runtime은 요약·번역·추론·재선택하지 않는다.
- PZ runtime은 100% Lua를 유지한다.
- Pulse는 Iris를 참조하거나 의존하지 않고, Iris는 다른 spoke와 직접 의존하지 않는다.
- Heavy 분류는 evidence와 closeout을 요구하지만 특정 전체 suite나 반복 Gate를 자동 요구하지 않는다.

---

## 12. Expected Closeout State

목표는 **`complete / adopted`인 off-live Layer 3 expression authority**다.

`complete`에는 다음이 모두 필요하다.

- Exact 2,105 target과 5,290 accepted fact가 adopted input에 결속된다.
- 10,580 fact-locale pair 전부가 승인된 표현을 가진다.
- 각 locale의 expanded represented fact set이 accepted fact set과 정확히 같다.
- 1,057 acquisition facts와 각 route/condition이 KO/EN expanded description에 보존된다.
- 적용 가능한 모든 프로필이 대표 선택 없이 composition에 기여하고 residual fact가 보존된다.
- Accepted first-contact contributor가 compact S2에 구체적인 의미로 표현된다.
- Normal Tooltip detail omission과 upstream first-contact gap이 expression 실패와 구별된다.
- Layer 4 exact relation, 추천, filler, locale fallback과 runtime inference가 생성되지 않는다.
- 단일 focused Gate가 exit `0`이고 exact candidate의 adoption/readback이 성공한다.
- 기존 L3-01~04와 current product/runtime bytes가 변경되지 않는다.
- 단일 closeout이 실제 명령, exit code, authority hash와 validation ceiling을 기록한다.

Accepted fact의 expression 미완료, accepted first-contact contributor의 조합 실패 또는 설명되지 않은 dependency loss가 남으면 `partial` 또는 `implemented_only`로 닫는다. Upstream에 accepted contributor가 없는 unresolved first-contact obligation은 명시적으로 추적할 수 있으며, 그것만으로 이미 수행 가능한 expression 작업의 완료를 부정하지 않는다.

이번 `complete`는 설명 authority의 완료다. 실제 Iris Menu 제3계층과 Tooltip S2에 연결하여 사용자에게 노출하고 S1/S3/S4와 통합하는 제품 전환은 포함하지 않는다.

### 선행 실행 기록 — 2026-09-05, superseded

- 신규 installed producer/loader: `iris_tooling.domains.layer3.expression_results`.
- Adopted readpoint: `Iris/_docs/authority/dvf/layer3_expression/manifest.json`, SHA-256
  `0abd0d3837321558252970a1ef007ac57d8f5b149c28d1532b24d44e74d673ff`.
- 단일 focused source는 계획의 기본 위치를 사용했다. 공용 conftest가 요구하는
  정규 registry와 저장소 밖 output을 가져오지 않도록 `--noconftest`, installed
  import mode와 repository-local basetemp를 명시했다. Gate는 한 번 실행했으며
  `1 passed in 16.91s`, exit `0`이다. Exact candidate adoption/readback도 exit `0`이다.
- 사용자의 실행 프롬프트가 구현·표현·owner approval·채택 권한을 제공했다.
  별도 approval gate를 추가하지 않았다.
- [소비 계약](iris_layer3_expression_contract.md)과
  [단일 closeout](iris_layer3_expression_closeout.md)에 명령·hash·검토·ceiling을 기록했다.

### 사용자-facing 해상도 교정과 현재 채택

보고 세션은 선행 결과의 S2가 일반 실행 전제를 반복하고 Menu 획득 설명에 내부
가중치·무작위 검사·등록/전달 세부가 섞였음을 지적했다. 이 후속 지시를 같은 작업의
표현 해상도 기준으로 채택했다. 모든 payload를 발화하는 대신 사용자-facing
proposition을 정확히 설명한다. S2는 모든 비조건 contributor를 유지하고, 일반 실행
qualifier는 expanded에 남기며 명시적 detail disposition으로 추적한다. 생략한 ref를
represented라고 표시하지 않는다. 의미 있는 조건과 서로 다른 scope는 유지한다.

현재 readpoint의 SHA-256은 `cff8acd83715e70c6e7b82553d47e538c7f75131437491d7cf6781875f5435be`다.
동일 focused source를 수정해 교정 최종 후보에 한 번 다시 실행했으며
`1 passed in 14.17s`, exit `0`이다. 교정 후보의 adoption/readback도 exit `0`이다.
선행 SHA와 PASS는 superseded 이력이며 현재 후보에 승계하지 않았다. 최종 제품
통합은 이 compact 결과를 그대로 사용하며 L3-06에 재요약·truncation을 넘기지 않는다.
