# Iris Layer 4 QG — Build 41 EvolvedRecipe 수집·판정·표시 구현 계획

> 상태: 통합 검토 반영 / 구현 준비 완료
> 작성 기준일: 2026-09-02
> 입력: EvolvedRecipe 문제 정의와 계획 검토 결과
> 양식: `PLAN_TEMPLATE.md`
> 기본 표시 표면: Iris Menu
> 영향 확인 표면: Tooltip
> 실행 원칙: 의미 계층의 독립성을 지키고, 검증과 Gate는 필요한 최소 단위로만 둔다.

---

## 1. Objective

Project Zomboid Build 41의 `EvolvedRecipe`를 Layer 4 QG가 독립적인 게임 상호작용 근거로 수집하고, 확인 가능한 아이템별 역할·조건·음식 유형을 Iris Menu에 표시한다.

이 작업은 다음 결과를 목표로 한다.

1. 아이템이 어떤 `EvolvedRecipe` 음식 유형에 재료 또는 향신료로 참여하는지 정확한 `FullType` 기준으로 추적한다.
2. `Cooked`, `Spice`처럼 관계에 붙는 조건을 아이템의 보편 속성으로 확대하지 않고 해당 관계에만 보존한다.
3. 고정 Recipe 및 Right-click과 다른 EvolvedRecipe의 의미를 유지하면서도 기존 QG Menu 표현과 자연스럽게 함께 표시한다.
4. 실제 소스가 입증하지 않는 조합, 결과물, 조리법, 탐색 링크를 만들어 내지 않는다.
5. Layer 3 DVF나 Tooltip에 의존하거나 그 의미를 변경하지 않는다.

완료된 사용자는 Menu에서 다음 수준의 정보를 얻을 수 있어야 한다.

- 이 아이템이 EvolvedRecipe 계열 조리에 쓰이는지
- 어떤 음식 유형에 참여하는지
- 일반 재료인지 향신료인지
- 해당 관계에 적용되는 확인 가능한 조건이 무엇인지

개별 재료 조합을 완성된 고정 레시피처럼 제시하거나 가능한 모든 조리 행동을 튜토리얼로 설명하는 것은 목표가 아니다.

---

## 2. Scope

### 포함

- Build 41 바닐라 `EvolvedRecipe` 소스의 구조적 파싱
- 아이템 `FullType`과 음식 유형 정의의 연결
- 재료와 향신료 역할 구분
- 관계별 조건의 정규화
- 원천·로케일·판정 근거를 포함한 QG owner 산출물 생성
- PASS 관계의 KO/EN 표시 문자열 생성
- 기존 QG Menu Detail ViewModel 또는 표현 경계에서 EvolvedRecipe 표시
- compact/full/search 등 기존 Menu 표시 방식과의 호환
- 기존 fixed Recipe 및 Right-click 정보 보존
- Tooltip 무변경 확인
- 저장소 밖 candidate 패키지 생성, 실제 PZ 관찰, 동일 candidate의 채택
- 구현 결과에 필요한 핵심 문서의 현재 상태 갱신

### Explicitly Out of Scope

- Layer 3 DVF와의 연결, 상호 완전성 검사, 설명 문장 변경
- Tooltip에 EvolvedRecipe 행을 추가하는 작업
- 외부 모드 데이터 수집 또는 모드별 예외 처리
- Build 42 지원
- Java 엔진 내부 동작의 재구현
- 가능한 재료 조합의 전수 생성
- 조합별 완성 음식, 영양값, 맛, 행복도 또는 독성 결과 계산
- 게임에 존재하지 않는 Recipe ID, 결과물, 이름 또는 탐색 경로 합성
- 조리 행동 전반을 안내하는 튜토리얼
- QG의 Source 계층을 Recipe/Right-click/EvolvedRecipe의 세 번째 전역 분류로 재편하는 작업
- 사용자의 실제 모드 설치본을 candidate 검증 전에 덮어쓰는 작업

---

## 3. Non-Goals

1. EvolvedRecipe를 fixed Recipe로 평탄화하지 않는다.
2. “수프에 무엇이든 넣을 수 있다”와 같은 런타임 일반 규칙을 추측으로 데이터화하지 않는다.
3. 동일한 아이템이 여러 음식 유형에 들어간다는 이유로 조합 수만큼 행을 폭증시키지 않는다.
4. Menu 행을 클릭 가능하게 보이게 하기 위해 근거 없는 navigation reference를 만들지 않는다.
5. 로케일 문구를 파싱하여 의미 근거를 역추론하지 않는다.
6. EvolvedRecipe 도입을 명분으로 기존 fixed Recipe 및 Right-click 자료 구조를 전면 마이그레이션하지 않는다.
7. 이 계획에 없는 중간 승인, 전체 회귀 Gate, 중복 determinism 검사를 새로 만들지 않는다.

---

## 4. Assumptions

### 4.1 정보 계층과 owner 경계

- Layer 4 QG는 Recipe, Right-click 등 아이템과 연결된 상호작용 정보를 소유한다.
- Layer 3 DVF와 Layer 4 QG는 독립적이고 동등한 정보 계층이다.
- EvolvedRecipe 판정은 DVF 문구나 DVF의 `primary_use`를 입력으로 사용하지 않는다.
- Menu는 여러 정보 계층을 함께 표시할 수 있지만, 그 사실이 계층 간 생성 의존성을 뜻하지 않는다.
- 이 계획의 채택은 아래 경계 안에서 필요한 구현 선택을 진행할 권한을 포함한다. routine 구현 선택을 위해 별도의 owner ratification을 두지 않는다.
- 다음과 같이 계획의 의미 경계를 바꾸는 새 결정이 실제로 필요할 때만 구현을 멈추고 owner 판단을 요청한다.
  - 합성 navigation 또는 합성 결과물을 도입해야 하는 경우
  - EvolvedRecipe를 QG 전역 Source 계층으로 승격해야 하는 경우
  - 런타임 관찰만으로 새로운 정적 PASS 근거를 만들려는 경우
  - Tooltip 또는 DVF 변경이 필요해지는 경우
  - 기존 fixed Recipe/Right-click 의미나 공개 구조를 보존할 수 없는 경우

### 4.2 확인된 기준선

계획 작성 시 확인한 Build 41 원천의 lexical 기준선은 다음과 같다.

| 원천 | `EvolvedRecipe` lexical occurrence |
|---|---:|
| `scripts/items_food.txt` | 333 |
| `scripts/farming.txt` | 14 |
| 합계 | 347 |

이 수치는 고유 아이템 수나 공개 관계 수가 아니다. 구조적 파서가 모듈·아이템 블록과 속성 값을 해석한 뒤 별도의 분모를 산출해야 한다.

추가 기준선은 다음과 같다.

- active candidate property row: 226
- 원천 속성 안의 raw `;` token: 2,187
- `evolvedrecipes.txt` 정의 header: 38
- 현재 QG canonical input의 EvolvedRecipe occurrence: 0

수치는 구현 시작 시 현재 checkout과 실제 Build 41 source root에서 한 번 재측정한다. 차이가 있으면 원천 버전과 차이를 기록하고 새 측정값을 기준으로 진행한다. 단순 수치 차이만으로 구현을 막지 않는다.

### 4.3 원천과 의미 판정

- item script는 정규식 occurrence 계산이 아니라 PZ module/item block 구조로 파싱한다.
- `FullType`은 대소문자를 포함해 정확히 보존한다.
- `EvolvedRecipe` 속성 값은 음식 유형, 역할, 조건을 원래 token 경계에 따라 해석한다.
- `EvolvedRecipeName_*`, 주석, 비활성 블록, malformed token은 active relation과 분리한다.
- `evolvedrecipes.txt`의 정의 속성(`BaseItem`, `ResultItem`, `Spice`, `MaxItems` 등)은 음식 유형의 존재와 의미를 확인하는 별도 원천으로 읽는다.
- 관련 Lua의 `getEvolvedRecipe`, `getAllEvolvedRecipes`, `getItemsCanBeUse`, `getPossibleItems`, `needToBeCooked`, `addItem`, `getItemRecipe` 및 frozen/poison 조건 경로는 소스 해석을 확인하는 데 사용한다.
- 저장소에 없는 Java 엔진 내부 로직은 재구현하거나 추측하지 않는다.

정적 판정은 다음 세 상태면 충분하다.

| 상태 | 의미 | 공개 |
|---|---|---|
| PASS | 원천에서 FullType, 음식 유형, 역할, 필요한 조건을 확인함 | Menu 표시 가능 |
| REVIEW | token 또는 의미를 안전하게 확정하지 못함 | 기본적으로 비공개 |
| non-target | 주석, 이름 표면, 비활성 또는 관계가 아닌 occurrence | 비공개 |

실제 PZ 관찰은 PASS 관계의 해석과 표시를 검증한다. 관찰만으로 원천에 없는 새로운 전체 아이템 관계를 PASS로 승격하지 않는다.

### 4.4 로케일

- 음식 유형의 정체성은 번역 문자열이 아니라 원천의 exact definition ID다.
- KO/EN 문구는 `ContextMenu_EvolvedRecipe_<food_type_id>` 계열에서 찾되, 실제 locale loader의 중복 key 처리와 유효값을 확인한다.
- 계획 작성 시 EN/KO 모두 38개 음식 유형 key가 관찰되었고, KO에는 `RicePan`과 `Sandwich` 중복 정의가 존재한다.
- 중복 key의 실제 유효값을 코드 또는 로더 동작으로 확정할 수 없으면 해당 영향 관계는 REVIEW로 남긴다.
- `EvolvedRecipeName_*.txt`는 재료 이름 표현을 위한 표면이며 음식 유형 identity authority로 사용하지 않는다.

### 4.5 관계 모델

각 공개 관계는 최소한 다음 정보를 가져야 한다.

- exact item `FullType`
- exact `food_type_id`
- 역할: 일반 재료 또는 향신료
- 정규화된 관계별 조건
- PASS/REVIEW 판정과 reason
- 원천 파일과 위치를 추적할 수 있는 provenance
- 위 의미 tuple에서 안정적으로 계산되는 relation identity
- KO/EN `display_by_locale`

`Cooked`, `Spice` 등은 FullType의 전역 capability가 아니라 개별 EvolvedRecipe 관계에 귀속한다.

EvolvedRecipe 관계에는 fixed Recipe 전용 필드인 `rule_id`, `recipe_id`, `recipe_nav_ref` 또는 합성 `ResultItem`을 부여하지 않는다. 실제 원천에서 안정적인 navigation target이 발견되지 않는 한 비클릭 행으로 표시하며, 핵심 불변식은 **합성 navigation을 만들지 않는 것**이다.

### 4.6 기존 QG와 통합

- 우선 구현은 기존 fixed Recipe 및 Right-click 행을 가능한 한 byte-identical하게 보존한다.
- EvolvedRecipe는 별도 typed collection 또는 lookup으로 생성하고, Detail ViewModel/표현 경계에서 기존 QG 정보와 합성한다.
- 현행 코드 구조상 별도 collection이 불가능하다는 구체적 증거가 있을 때만 기존 Menu projection schema를 확장한다.
- schema 확장이 불가피해도 fixed Recipe/Right-click의 의미, 정렬, navigation, 표시 문자열은 바꾸지 않으며 final no-diff 또는 허용 delta 비교로 입증한다.
- runtime은 완성된 `display_by_locale`를 소비한다. Lua에서 semantic token을 다시 조합하거나 번역 문자열을 파싱하지 않는다.
- 같은 역할과 조건을 가진 관계만 표시 단계에서 묶을 수 있다. 묶어도 원래 relation identity와 KO/EN의 동일한 관계 집합을 보존해야 한다.
- compact/full/search 전환은 기존 QG의 적응형 표시 정책을 재사용한다.

### 4.7 Tooltip 격리

- 현재 Tooltip 입력은 fixed Recipe/Right-click 중심의 bounded owner input을 사용한다.
- 이 작업은 `upstream_usecases_by_fulltype.json`에 EvolvedRecipe를 쓰지 않는다.
- Tooltip generator, payload, 표시 행은 변경하지 않는다.
- 최종 검증은 bounded owner input과 생성 payload의 no-diff를 확인한다. 예상하지 못한 차이가 있을 때만 조사 범위를 확대한다.

### 4.8 candidate와 채택 순서

구현 결과는 먼저 저장소 외부 candidate 패키지로 만든다.

1. source와 의미를 확정한다.
2. candidate를 생성한다.
3. candidate 패키지를 별도 위치에 준비한다.
4. 그 candidate를 실제 PZ에서 관찰한다.
5. 관찰한 candidate와 byte-identical한 결과만 guarded updater로 채택한다.
6. 채택본과 배포 패키지의 parity를 확인한다.

사용자의 실제 설치본을 직접 덮어쓰지 않는다.

---

## 5. Repository Areas Affected

정확한 파일 배치는 구현자가 현행 구조를 확인한 뒤 최소 변경으로 정한다.

### Code

- `Iris/tooling/src/iris_tooling/domains/layer4/`
  - Build 41 EvolvedRecipe parser 또는 owner producer
  - source-accounted 판정과 locale resolution
- `Iris/build/description/v2/generate_layer4_runtime_projection.py`
  - 별도 typed EvolvedRecipe projection 연결이 필요한 경우
- `Iris/build/description/v2/validate_layer4_runtime_projection.py`
  - 새 collection의 구조·identity·locale 검증
- `Iris/build/description/v2/update_layer4_runtime_projection.py`
  - 기존 guarded adoption 경로를 재사용하거나 최소 확장하는 경우
- `Iris/Contents/mods/Iris/media/lua/client/Iris/UI/IrisBrowserInteractionProjection.lua`
- `Iris/Contents/mods/Iris/media/lua/client/Iris/UI/IrisBrowserInteractionRenderer.lua`
- 필요할 때만 `IrisItemDetailModelAssembler.lua`

### Data / Generated Artifacts

- Build 41 EvolvedRecipe source-accounted owner output
- runtime용 typed EvolvedRecipe projection 또는 lookup
- KO/EN `display_by_locale`
- 저장소 외부 candidate manifest와 배포 패키지

새 owner output은 여러 중간 파일을 필수로 만들지 않는다. 한 산출물 안에 source census, PASS/REVIEW/non-target accounting, relation evidence를 함께 둘 수 있다. exact filename과 schema version은 기존 Layer 4 관례에 맞춰 구현 시 정한다.

### Tests / Harness

- parser와 의미 판정을 위한 집중 Python test
- QG Menu projection/renderer의 집중 Lua harness
- 기존 fixed Recipe/Right-click 및 Tooltip no-diff 비교기

### Docs

- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- 구현 walkthrough 또는 closeout 문서

핵심 문서는 구현으로 실제 현재 계약이 바뀐 부분만 갱신한다. 작업 이력을 장황하게 추가하지 않는다.

---

## 6. Planned Changes

구현은 세 단계와 세 Gate만 사용한다. Gate는 중간 승인 회의가 아니라 다음 단계로 넘어가기 위한 검증 묶음이다.

### Change 1 — Build 41 source와 의미 확정

#### 작업

1. 실제 Build 41 source root와 파일 버전을 기록한다.
2. item script의 module/item block을 파싱해 active `EvolvedRecipe` property를 추출한다.
3. lexical occurrence, active property row, raw token, exact FullType, malformed/non-target를 서로 다른 분모로 집계한다.
4. `evolvedrecipes.txt` 정의와 관련 Lua를 읽어 음식 유형, 역할, 조건의 의미를 확정한다.
5. locale key와 중복 처리의 실제 유효값을 확인한다.
6. 각 relation을 PASS 또는 REVIEW로 분류하고 reason/provenance를 남긴다.
7. source census와 relation evidence를 하나의 owner output으로 생성한다.

#### 구현 유연성

- parser의 내부 class, 함수, 중간 구조 이름은 강제하지 않는다.
- 중간 debug dump는 필요할 때 생성할 수 있지만 canonical 산출물로 고정하지 않는다.
- REVIEW reason vocabulary는 안정적인 집계가 가능할 정도로만 정규화한다.
- source row를 공개 relation으로 바꾸는 과정에서 의미 없는 중복만 제거하되, 서로 다른 조건·역할·음식 유형은 합치지 않는다.

#### Gate 1 — source-accounted semantic closure

다음 조건만 확인한다.

- 구조적 parser가 모든 대상 source file을 읽었다.
- lexical/active/token/PASS/REVIEW/non-target 분모가 서로 섞이지 않고 합계가 설명된다.
- 공개 PASS는 exact FullType, food type, 역할, 조건, provenance를 모두 가진다.
- locale를 안전하게 확정하지 못한 관계가 PASS로 새지 않는다.
- focused parser/semantic test가 통과한다.

Gate 1에서 owner 승인을 별도로 요구하지 않는다. 계획 경계를 바꾸는 예외가 없는 한 Change 2로 진행한다.

### Change 2 — QG candidate와 Menu 표시 구현

#### 작업

1. PASS 관계를 runtime용 typed EvolvedRecipe collection/lookup으로 투영한다.
2. relation identity와 KO/EN `display_by_locale`를 생성한다.
3. 기존 fixed Recipe/Right-click 자료는 그대로 두고 Detail ViewModel 또는 renderer 경계에서 EvolvedRecipe를 함께 표시한다.
4. 일반 재료/향신료와 관계별 조건을 사용자가 구분할 수 있는 간결한 Menu 행으로 렌더링한다.
5. 같은 역할·조건의 행은 필요한 경우에만 묶고, full/search에서는 원 relation을 다시 식별할 수 있게 한다.
6. 기존 compact/full/search 정책과 고밀도 처리 방식을 재사용한다.
7. navigation target이 없으면 비클릭 행으로 표시한다.
8. 저장소 외부에 candidate manifest와 실제 PZ 투입용 candidate 패키지를 만든다.

#### 기존 QG 보존 우선순위

1. 별도 typed collection + 표현 경계 합성
2. 불가피할 때만 기존 projection schema 확장
3. 기존 행 재작성은 최후 수단

2번 또는 3번이 필요하면 이유를 closeout에 기록하고, fixed Recipe/Right-click에 발생한 delta가 허용된 구조 필드 추가뿐인지 한 번의 최종 비교로 확인한다.

#### 표시 예시

실제 문구는 source와 locale 확인 후 결정하되 의미 구조는 다음 정도다.

- 일반 재료: “스튜 재료로 사용할 수 있음”
- 조건 포함: “익힌 뒤 샐러드 재료로 사용할 수 있음”
- 향신료: “수프의 향신료로 사용할 수 있음”

이 문구는 가능한 조합이나 완성 레시피를 약속하지 않는다.

#### Gate 2 — candidate integrity

다음 조건만 확인한다.

- candidate의 모든 공개 행이 Gate 1 PASS relation으로 역추적된다.
- relation identity, role, condition, KO/EN relation set이 보존된다.
- fixed Recipe와 Right-click의 기존 의미·문구·navigation에 예상 밖 delta가 없다.
- Tooltip bounded owner input과 generated payload에 delta가 없다.
- focused Menu harness와 Lua syntax 검사가 통과한다.
- candidate A/B 생성 한 번으로 byte determinism이 확인된다.
- 저장소 외부 candidate 패키지와 manifest가 준비된다.

예상 밖 delta가 발견된 영역만 추가 조사한다. 전체 파이프라인의 반복 검증을 기본 절차로 추가하지 않는다.

### Change 3 — 실제 PZ 관찰, 동일 candidate 채택, closeout

#### 관찰 범위

실제 PZ에서는 최대 네 개의 대표 사례로 다음 의미 가지를 함께 확인한다.

1. 기본 재료이며 여러 음식 유형에 참여하는 사례
2. `Cooked` 또는 `Spice` 조건이 있는 사례
3. 같은 아이템에 fixed Recipe 또는 Right-click 정보가 함께 있는 사례
4. 관계가 많은 아이템의 compact/full/search 표시 사례

KO와 EN은 같은 사례를 재사용한다. 한 사례가 여러 가지를 충족하면 수를 줄인다. 실제 source에 해당 가지가 없으면 억지로 사례를 만들지 않고 not applicable로 기록한다.

확인할 내용은 다음으로 제한한다.

- Menu 문구가 candidate의 음식 유형·역할·조건과 일치하는가
- 고밀도 표시에서 정보가 누락되거나 잘못 합쳐지지 않는가
- fixed Recipe/Right-click이 정상적으로 함께 보이는가
- EvolvedRecipe 행이 합성 navigation을 제공하지 않는가
- Tooltip이 기존과 동일한가

#### 채택과 패키징

1. 관찰한 candidate manifest/hash를 기록한다.
2. 관찰 결과가 허용 범위 안이면 그 candidate와 byte-identical한 산출물만 guarded updater로 저장소에 채택한다.
3. 채택 후 runtime 파일과 배포 패키지의 parity를 확인한다.
4. owner output의 PASS/REVIEW/non-target 수와 알려진 한계를 closeout에 기록한다.
5. 실제 계약 변경만 핵심 문서에 반영한다.

#### Gate 3 — final adoption

다음 조건만 확인한다.

- 대표 실제 PZ 사례가 candidate와 일치한다.
- 관찰한 candidate와 채택본이 동일하다.
- 채택본과 배포 패키지가 동일하다.
- 관련 저장소 필수 검사가 종료 코드 0으로 통과한다.
- REVIEW 관계가 공개 runtime에 포함되지 않는다.
- 문서와 closeout이 실제 채택 상태를 설명한다.

실제 PZ 실행 환경을 사용할 수 없으면 구현과 candidate 검증을 `implemented_only`로 종료하고 채택은 보류한다. 이 경우 실제 관찰을 하지 않은 상태를 PASS로 표현하지 않는다.

---

## 7. Validation Plan

### Automated

필수 검증은 아래 한 묶음으로 제한한다.

1. **집중 Python test**
   - module/item block 파싱
   - token/role/condition 판정
   - exact FullType 및 stable relation identity
   - locale resolution과 REVIEW 격리

2. **최종 candidate 비교**
   - candidate A/B 한 번의 byte determinism
   - source relation에서 public relation으로의 역추적
   - KO/EN relation set parity
   - fixed Recipe/Right-click no-diff 또는 사전에 정의한 최소 허용 delta
   - Tooltip bounded input 및 final payload no-diff

3. **집중 runtime 검증**
   - QG Menu projection/renderer harness
   - compact/full/search 및 non-clickable row
   - Lua syntax:

     ```powershell
     powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
     ```

4. **현행 계약이 요구하는 관련 suite**
   - Python 구현은 저장소가 해당 경로에 요구하는 test command를 실행한다.
   - Java/Gradle 또는 JS/TS를 실제로 수정한 경우에만 각각 `.\gradlew test`, `pnpm biome check .`를 실행한다.
   - 기존 authority가 요구하지 않는 새 full-repository Gate를 이 계획에서 만들지 않는다.

동일한 census, evidence, generation, Tooltip matrix를 단계마다 반복하지 않는다. 한 검증이 같은 불변식을 이미 입증하면 다음 Gate에서 재실행하지 않고 최종 candidate 검증에서 한 번만 확인한다.

### Manual

- Change 3의 최대 네 개 대표 사례
- KO/EN 동일 사례
- candidate 패키지에서 먼저 관찰
- Tooltip은 동일 사례의 무변경 확인

### Validation Limits

- 실제 PZ 관찰은 선택한 아이템 관계의 표시와 source 해석을 확인하지만 모든 런타임 조합 가능성을 증명하지 않는다.
- 저장소에 없는 Java 내부 eligibility 규칙은 source-level PASS 범위에 포함하지 않는다.
- “모든 음식이 특정 EvolvedRecipe에 들어간다” 같은 포괄 규칙은 명시적 source 근거 없이는 산출하지 않는다.
- REVIEW는 결함을 숨기는 상태가 아니라 공개하기에 근거가 부족한 관계를 격리하는 상태다.

---

## 8. Risk Surface Touch

| Surface | Touch | 통제 |
|---|---|---|
| Layer 4 source ingestion | 직접 변경 | 구조적 parser와 source accounting |
| QG owner data | 새 typed relation 추가 | PASS/REVIEW 격리와 provenance |
| fixed Recipe | 보존 우선 | 별도 collection, 최종 no-diff |
| Right-click | 보존 우선 | 별도 collection, 최종 no-diff |
| Menu projection/renderer | 직접 변경 | focused harness와 대표 실제 관찰 |
| KO/EN locale | 직접 사용 | exact food type ID, duplicate resolution |
| Tooltip | 변경 금지 | bounded input/payload no-diff |
| DVF | 변경 금지 | 입력·출력·완전성 연결 금지 |
| 사용자 설치본 | 변경 금지 | external candidate와 guarded adoption |
| 외부 모드 | 대상 아님 | Build 41 바닐라 source만 사용 |

---

## 9. Risk Analysis

### Risk 1 — lexical occurrence를 실제 관계 수로 오인

- **영향:** coverage와 누락 수치가 틀어지고 잘못된 공개 관계가 생긴다.
- **대응:** lexical, active property, raw token, relation, unique FullType을 별도 분모로 유지한다.

### Risk 2 — EvolvedRecipe를 fixed Recipe로 오인

- **영향:** 존재하지 않는 결과물·Recipe ID·탐색 링크가 생성된다.
- **대응:** typed EvolvedRecipe relation을 사용하고 fixed Recipe 전용 필드를 금지한다.

### Risk 3 — 관계별 조건을 아이템 전역 속성으로 확대

- **영향:** 한 음식 유형의 `Cooked` 또는 `Spice`가 다른 관계에도 잘못 적용된다.
- **대응:** 조건을 relation tuple과 identity에 포함한다.

### Risk 4 — locale 중복 또는 누락

- **영향:** KO/EN 문구가 서로 다른 음식 유형을 가리키거나 실행마다 바뀐다.
- **대응:** 실제 loader 유효값을 확정하고 불확실한 영향 관계를 REVIEW로 둔다.

### Risk 5 — 기존 QG 회귀

- **영향:** fixed Recipe/Right-click 문구, 정렬, navigation이 바뀐다.
- **대응:** 별도 collection을 우선하고 final no-diff 또는 최소 허용 delta 비교를 한 번 수행한다.

### Risk 6 — 고밀도 Menu에서 정보 손실

- **영향:** 관계가 많은 음식 아이템의 역할·조건·음식 유형이 잘못 묶인다.
- **대응:** 역할과 조건이 같은 관계만 묶고 compact/full/search 대표 사례를 관찰한다.

### Risk 7 — 검증 절차가 구현을 고정

- **영향:** schema와 함수 단위까지 계획이 강제되어 더 단순한 구현을 선택할 수 없다.
- **대응:** Gate는 observable invariant만 검사하고 내부 구조, 파일명, 중간 산출물 수는 구현자에게 맡긴다.

### Risk 8 — candidate와 실제 채택본 불일치

- **영향:** 관찰하지 않은 결과가 배포된다.
- **대응:** 외부 candidate를 먼저 관찰하고 동일 hash/bytes만 guarded updater로 채택한다.

---

## 10. Rollback Plan

1. 새 EvolvedRecipe owner/projection 생성 경로를 비활성화한다.
2. Menu의 typed EvolvedRecipe 합성 지점을 제거한다.
3. 기존 fixed Recipe/Right-click projection과 renderer 경로로 되돌린다.
4. EvolvedRecipe generated artifact만 마지막 채택 전 버전 또는 부재 상태로 복원한다.
5. Tooltip과 DVF는 이 작업에서 변경하지 않으므로 별도 데이터 rollback 대상이 아니어야 한다.
6. 저장소 밖 candidate와 manifest는 진단 자료로 보존할 수 있으나 사용자 설치본에는 적용하지 않는다.

schema 확장이 불가피해 기존 파일을 수정했다면 rollback은 guarded updater가 기록한 pre-adoption hash와 백업을 사용한다.

---

## 11. Governance Constraints

1. `Philosophy.md`가 설계 판단의 최상위 기준이다.
2. Layer 4 QG는 Layer 3 DVF를 입력이나 권위로 사용하지 않는다.
3. Layer 1~5는 독립적이고 동등한 정보 계층이다.
4. EvolvedRecipe는 아이템과 연결된 Layer 4 상호작용 근거이며, 외부 모드 자체를 인식하지 않는다.
5. source가 입증하지 않는 조합, 결과물, navigation을 합성하지 않는다.
6. 사용자 설치본을 직접 수정하지 않는다.
7. generated artifact는 canonical source가 아니며 재생성 가능해야 한다.
8. PASS는 관련 필수 명령이 종료 코드 0을 반환했을 때만 주장한다.
9. 실제 PZ를 관찰하지 못했으면 `implemented_only`와 PASS를 구분한다.
10. 테스트나 Gate를 구현 편의상 추가할 수는 있지만, 이 계획의 완료 조건으로 승격하려면 새로운 고위험 불변식을 실제로 보호한다는 근거가 있어야 한다.
11. 구현 도중 계획 경계 안의 선택은 별도 승인을 기다리지 않는다.

---

## 12. Expected Closeout State

완료 시 다음 상태가 기대된다.

- Build 41 EvolvedRecipe source occurrence가 설명 가능한 분모로 account된다.
- 공개 가능한 관계는 exact FullType, 음식 유형, 역할, 조건, provenance, relation identity를 가진다.
- 불확실한 관계는 REVIEW로 격리되고 공개 runtime에 들어가지 않는다.
- QG Menu는 fixed Recipe/Right-click과 독립적인 EvolvedRecipe 관계를 표시한다.
- 사용자는 재료 또는 향신료로서 참여 가능한 음식 유형과 확인된 조건을 이해할 수 있다.
- 가능한 모든 조합이나 합성 레시피는 표시되지 않는다.
- 기존 fixed Recipe 및 Right-click의 의미·문구·navigation은 보존된다.
- Tooltip과 DVF는 변경되지 않는다.
- KO/EN은 같은 relation set을 서로 올바른 로케일 문구로 표시한다.
- 대표 실제 PZ 사례에서 candidate가 의도대로 보인다.
- 관찰한 candidate, 채택본, 배포 패키지가 동일하다.
- closeout은 다음만 간결하게 기록한다.
  - source 기준과 PASS/REVIEW/non-target 수
  - 실제 관찰 사례와 결과
  - 실행한 필수 검증과 종료 코드
  - 저장소에 없는 Java 내부 규칙 등 남은 한계

이 계획의 성공 기준은 EvolvedRecipe를 많이 표시하는 것이 아니라, **원천으로 입증된 Layer 4 관계만 기존 QG를 훼손하지 않고 Menu에서 유용하게 보여 주는 것**이다.
