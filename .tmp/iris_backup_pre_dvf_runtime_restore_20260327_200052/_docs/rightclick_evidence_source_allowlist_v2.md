# Right-click Evidence Source Allowlist v2

> **원칙**: 이 문서는 Gate-0의 A/B/C/Exclusion을 증명할 때 사용할 수 있는 **근거 타입(Evidence Source Type)** 허용/금지 목록을 정의한다.  
> 필드/행동/그룹을 정의하지 않는다. 금지된 소스 사용 = **FAIL**.

---

## 1. Purpose

이 문서의 역할은 3가지로 한정된다.

1. **근거 타입 허용 목록 정의**: 증거가 될 수 있는 것(허용)과 절대 쓸 수 없는 것(금지)을 고정
2. **각 근거 타입의 증명 범위 고정**: A/B/C/Exclusion 중 무엇을 증명할 수 있는지를 매핑
3. **증명 실패(unknown) 합법화**: 근거 타입이 커버하지 못하는 항목은 unknown으로 남기는 것이 합법

이 문서는 다음을 하지 **않는다**:
- 필드(Field ID) 생성/정의
- 특정 행동이나 capability 목록 관리
- Decision(STRONG/WEAK/NO/REVIEW) 산출 (→ `rightclick_resolution_rules_v2.md`의 책임)

---

## 2. Definitions

### Evidence Source Type

Evidence 후보를 추출하거나 A/B/C/Exclusion을 증명하기 위해 사용하는 **정적 근거의 유형**. SourceType은 "근거 유형"이지 "기능 이름"이 아니다. `can_*` 같은 이름을 쓰지 않는다.

### Anchor

근거의 정적 출처를 식별하는 구조체. `rightclick_source_index_v2.json` 스키마의 `anchor.kind` / `anchor.ref` / `anchor.version`을 따른다.

본 문서의 4절 표에서 사용하는 `Anchor.kind` 값(`lua_function` / `lua_class` / `lua_table` / `file_span` / `script_tag` / `itemscript_field`)은 `rightclick_source_index_v2.json`의 `schema.anchor.kind` enum을 확장한 것이다. source_index에 새 kind가 필요한 경우 양쪽 문서를 동시에 갱신해야 한다.

### Proof

A/B/C 각 기준에 대해 해당 근거 타입이 산출할 수 있는 판정값.

| 값 | 의미 |
|---|---|
| `true` | 해당 기준을 결정적으로 증명 가능 |
| `false` | 해당 기준에 미충족임을 결정적으로 증명 가능 |
| `unknown` | 해당 근거 타입으로는 증명 불가. 추론으로 true를 만드는 것은 금지 (FAIL) |

### Exclusion Flag

제외 규칙을 결정적으로 증명할 수 있는 플래그. 사용 가능한 키: `recipe` / `consumption` / `equip` / `passive` / `auto` / `input_material` / `property_based`

---

## 3. Forbidden Sources (FAIL)

아래 근거를 사용하여 candidate를 생성하거나 proof를 설정한 경우 **즉시 FAIL**.

| 금지 근거 | 이유 |
|---|---|
| 메뉴 문자열 (`addOption` 라벨 등) | 로케일 의존, 비결정적 |
| DisplayName | 로케일 의존, 비결정적 |
| 번역 문자열 / tooltip / description | 표시용 텍스트, 데이터 아님 |
| 이름 패턴 매칭 (정규식/글로브 패턴) | `*Petrol*` 같은 추론, 비결정적 |
| 카테고리 의미 추론 | 카테고리 값에서 행동/역할을 해석하는 것 |
| 런타임 함수 결과를 후보 추출 기준으로 사용 | `runtime_condition` / `excluded_matchers`에 격리된 동적 판단 |
| 프로파일링/관측 기반 데이터 | 런타임 측정값, 재현 불가 |
| 조건 흐름 추론 | 복잡한 조건 분기를 해석하여 의미를 부여하는 것 |

> 이 목록은 `rightclick_fail_conditions_v2.md` 3-A (Forbidden Evidence Source)와 1:1로 맞물린다.

---

## 4. Allowed Evidence Source Types

각 근거 타입이 **무엇을 할 수 있는지**(후보 추출 / A·B·C 증명 / Exclusion 증명)를 고정한다.

> **핵심 원칙**: 후보군 추출과 증명(proof)은 분리된다. items_itemscript로 후보를 뽑아도 A/B/C가 자동으로 증명되는 것은 아니다.

| Source Type | Anchor.kind | 후보 추출 | A (실행 주체) | B (외부 대상) | C (지속 변화) | Exclusion | 비고 |
|---|---|---|---|---|---|---|---|
| `lua_predicate_on_inventory_item` | `lua_function` / `file_span` | ✅ | ✅ | unknown | unknown | — | 옵션 추가 조건이 특정 FullType/Type/Tag를 검사하는 구조 |
| `lua_action_invocation` | `lua_function` / `lua_class` | ❌ (보통) | unknown | ✅ | ✅ | — | TimedAction/함수 호출이 외부 상태를 바꾸는 구조 |
| `static_table_item_list` | `lua_table` | ✅ | ✅ (조건부) | unknown | unknown | — | 테이블에 FullType 리스트가 명시되는 경우. 리스트가 불명확하면 추출 불가(REVIEW) |
| `itemscript_tag` | `script_tag` | ✅ | — | — | — | — | 후보군 결정만. A/B/C 증명은 별도 근거 필요 |
| `itemscript_type` | — | ✅ | — | — | — | — | 후보군 결정만. A/B/C 증명은 별도 근거 필요 |
| `itemscript_display_category` | — | ✅ | — | — | — | `input_material` | 후보군 결정 + input_material 제외 증명 가능 (예: WeaponPart) |
| `itemscript_category` | — | ✅ | — | — | — | — | 후보군 결정만. A/B/C 증명은 별도 근거 필요 |
| `itemscript_property` | — | ✅ (조건부) | — | — | — | — | items_itemscript.json에서 정적으로 확인 가능한 property만 허용. 불가 시 excluded_matchers로 격리 |
| `recipe_tool_requirement` | `file_span` / `script_tag` | ✅ | — | — | — | `recipe` | Recipe 기반 제외를 결정적으로 증명 |
| `equip_requirement` | `itemscript_field` | ✅ | — | — | — | `equip` | BodyLocation/CanBeEquipped 등 |
| `consumption_effect` | `itemscript_field` | ✅ | — | — | — | `consumption` | Eat/Drink/Read 계열 |
| `property_based_container_logic` | `lua_function` | ✅/❌ | — | — | — | `property_based` | Tag/State 기반 요구를 증명. 정책상 REVIEW로 격리 |

> Exclusion 열은 해당 Source Type이 **결정적으로 증명 가능한 구체 플래그만** 표기한다. Exclusion의 정식 정의 및 결과(NO/REVIEW)는 6절 Exclusion Rules만이 진실이다.

### 표 읽는 법

- **✅**: 해당 항목을 결정적으로 증명 가능
- **unknown**: 해당 근거 타입만으로는 증명 불가. unknown으로 남겨야 함
- **—**: 해당 항목에 관여하지 않음
- **조건부**: 특정 구조를 만족할 때만 가능 (비고 참조)

---

## 5. Proof Rules

### 최소 요구치

| 증명 대상 | 최소 필요 Source Type |
|---|---|
| **A (실행 주체)** | `lua_predicate_on_inventory_item` 또는 `static_table_item_list` 중 하나 이상 |
| **B (외부 대상)** | `lua_action_invocation` 계열 없이는 true로 설정 불가 |
| **C (지속 변화)** | `lua_action_invocation` 계열 없이는 true로 설정 불가 |

### unknown 처리 규칙

- 근거 타입이 커버하지 못하는 proof 항목은 반드시 `unknown`으로 남긴다.
- `unknown`을 추론으로 `true`로 확정하는 것은 **금지 근거 사용과 동일하게 FAIL** 처리한다.
- `unknown`이 하나라도 남으면 `rightclick_resolution_rules_v2.md` 5절 순위 4에 의해 **REVIEW**로 격리된다.

---

## 6. Exclusion Rules

Exclusion을 **추론 없이 결정적으로** 켤 수 있는 근거 타입만 아래에 나열한다.

| Exclusion Flag | 허용 Source Type | 결과 |
|---|---|---|
| `recipe` | `recipe_tool_requirement` | → **NO** (결정적 제외) |
| `consumption` | `consumption_effect` | → **NO** (결정적 제외) |
| `equip` | `equip_requirement` | → **NO** (결정적 제외) |
| `passive` | (해당 근거 타입 존재 시 추가) | → **NO** (결정적 제외) |
| `auto` | (해당 근거 타입 존재 시 추가) | → **NO** (결정적 제외) |
| `input_material` | `itemscript_display_category` (WeaponPart 등) | → **NO** (결정적 제외) |
| `property_based` | `property_based_container_logic` | → **REVIEW** (자동 결론 금지 정책) |

> `property_based`는 다른 Exclusion과 달리 NO가 아닌 **REVIEW**로 격리한다. 이는 executing_tool 확정이 불가하기 때문이며, 정책 선택에 의한 것이다.

---

## 7. Cross-Document Links

| 문서 | 연결 |
|---|---|
| `rightclick_source_index_v2.json` | 각 rule의 anchor/extract/prove/exclusions가 본 문서의 Source Type 및 Proof Rules를 준수해야 함 |
| `rightclick_fail_conditions_v2.md` | 3-A (Forbidden Source) 위반 시 FAIL. 본 문서 3절과 1:1 대응 |
| `rightclick_resolution_rules_v2.md` | proof/exclusion 우선순위로 decisions 산출. 본 문서의 Proof Rules가 입력 계약 |
| `rightclick_field_registry_v2.md` | anchor 규격(kind/ref/version)을 기반으로 필드 생성/갱신. 본 문서의 Anchor 정의와 정합 |

---

## 버전 정보

- **Version**: v2
- **Created**: 2026-02-08
- **Revised**: 2026-02-18
- **Status**: Active
- **Supersedes**: `rightclick_evidence_source_allowlist_v1.md`
