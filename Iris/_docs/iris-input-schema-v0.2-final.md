# Iris 자동 분류 입력 스키마 (v0.2 FINAL)

이 문서는 Iris 자동 분류 시스템의 **입력 데이터 스키마**를 정의한다.  
모든 분류 로직은 이 스키마에 정의된 데이터만 참조해야 한다.

> 🔒 **동결 버전**: v0.2 FINAL  
> 📅 **동결 일자**: 2026-01-23

---

## 1. 파일 구성

| 파일명 | 스키마 키 | 용도 | 필수 |
|--------|-----------|------|------|
| `items_itemscript.json` | `items_itemscript` | 아이템 속성 데이터 | ✅ |
| `recipes_index_full.json` | `recipes_index` | Recipe 관계 데이터 | ✅ |
| `fixing_fixers.json` | `fixing_fixers` | Fixer 아이템 목록 | ✅ |
| `moveables_tooldefs.json` | `moveables_tooldefs` | Moveables 도구 정의 | ✅ |
| `extraction_stats.json` | — | 추출 통계 (참고용) | ❌ |

> ℹ️ **스키마 키 매핑**: JSON Schema(`iris-input-schema-v0.2-final.json`)는 각 파일의 스키마를 `스키마 키`로 정의한다. 파일명과 스키마 키는 위 표의 매핑을 따른다.

---

## 2. items_itemscript.json

아이템 스크립트에서 추출한 필드 데이터.

### 2.1 구조

```json
{
  "Base.ItemName": {
    "FullType": "Base.ItemName",
    "Type": "Normal",
    "field1": value1,
    "field2": value2
  }
}
```

- **키**: `{module}.{itemName}` 형식의 FullType
- **값**: 해당 아이템의 필드 객체

### 2.2 필드 명세

#### 기본 필드

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `FullType` | string | 아이템 전체 ID | `"Base.Hammer"` |
| `Type` | string | 아이템 기본 타입 | `"Weapon"`, `"Food"`, `"Clothing"` |
| `DisplayName` | string | 표시 이름 (분류 금지) | `"Hammer"` |
| `DisplayCategory` | string | 표시 카테고리 (분류 금지) | `"Tool"` |
| `Weight` | number | 무게 (분류 금지, 표시용) | `2.0` |

#### 분류용 필드

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `Categories` | string | 무기 카테고리 (세미콜론 구분) | `"Axe"`, `"Blunt"` |
| `SubCategory` | string | 무기 세부 카테고리 | `"Swinging"`, `"Stab"` |
| `BodyLocation` | string | 착용 부위 | `"Hat"`, `"Shirt"` |
| `AmmoType` | string | 탄약 타입 | `"Base.Bullets9mm"` |
| `Tags` | string | 아이템 태그 (세미콜론 구분) | `"Hammer;HasMetal"` |

> ⚠️ 각 필드의 **허용값**은 Evidence Allowlist 문서에서 정의한다. 이 스키마는 필드 존재와 타입만 정의.

#### 무기 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `TwoHandWeapon` | boolean | 양손 무기 여부 (`true`만 존재, 없으면 한손) |
| `IsAimedFirearm` | boolean | 조준 총기 여부 |
| `MountOn` | string | 장착 대상 총기 |

#### 광원/점화 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `LightStrength` | number | 광원 강도 |
| `LightDistance` | number | 광원 거리 |
| `TorchCone` | boolean | 손전등형 광원 |
| `ActivatedItem` | boolean | 활성화 가능 여부 |

#### 소비 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `HungerChange` | number | 배고픔 변화 |
| `ThirstChange` | number | 갈증 변화 |
| `StressChange` | number | 스트레스 변화 |
| `UnhappyChange` | number | 불행 변화 |
| `Alcoholic` | boolean | 알코올 여부 |

#### 행동 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `CustomContextMenu` | string | 컨텍스트 메뉴 액션 |
| `TeachedRecipes` | string | 레시피 해금 |
| `SkillTrained` | string | 스킬 훈련 |
| `CanStoreWater` | boolean | 물 저장 가능 |
| `TwoWay` | boolean | 양방향 송수신 |
| `IsCookable` | boolean | 조리 가능 여부 |

### 2.3 Type 허용값

| Type | 설명 |
|------|------|
| `Normal` | 일반 아이템 |
| `Weapon` | 무기 |
| `Food` | 음식 |
| `Drainable` | 소모품 (액체) |
| `Clothing` | 의류 |
| `Literature` | 문서 |
| `Map` | 지도 |
| `Radio` | 라디오 |
| `Container` | 컨테이너 |
| `WeaponPart` | 총기 부품 |
| `Moveable` | 가구 |
| `Key` | 열쇠 |
| `AlarmClock` | 알람시계 |
| `AlarmClockClothing` | 착용 알람시계 |

> ⚠️ Type과 대분류의 **연결 관계**는 Evidence Table에서 정의한다.

### 2.4 Experimental 필드 (v0.3 후보)

다음 필드들은 바닐라에 존재하지만, 샘플 수가 적거나 모드 호환성 검증이 필요하여 **실험적 상태**로 분류한다.

| 필드 | 타입 | 설명 | 바닐라 존재 수 | 비고 |
|------|------|------|----------------|------|
| `Medical` | boolean | 의료 아이템 여부 | 20 | 3-C 분류 후보 |
| `CanBandage` | boolean | 붕대 기능 여부 | 11 | 3-C 분류 후보 |
| `AlcoholPower` | number | 소독 효과 수치 | 4 | exists 판정 후보 |
| `BandagePower` | number | 붕대 효과 수치 | 11 | 표시용 |

> ⚠️ **사용 주의**: 이 필드들을 분류 핵심 증거로 사용할 경우, 모드 아이템에서 일관성이 보장되지 않을 수 있다. v0.3에서 검증 후 정식 채택 여부 결정.

---

## 3. recipes_index_full.json

레시피에서 아이템이 어떤 역할로 참조되는지.

### 3.1 구조

```json
{
  "meta": {
    "source": "scripts.zip (static recipes only)",
    "recipes_total": 386,
    "items_with_relations": 355,
    "relations_total": 934,
    "roles_total": { "input": 758, "keep": 176 },
    "get_item_types_groups_referenced": [...],
    "unresolved_tokens": {}
  },
  "items": {
    "Base.ItemName": [
      {
        "role": "input",
        "category": "Cooking",
        "recipe": "Recipe Name",
        "source": "recipes.txt"
      }
    ]
  }
}
```

### 3.2 관계(Relation) 객체

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `role` | string | ✅ | 아이템 역할: `"input"`, `"keep"` |
| `category` | string \| null | ❌ | 레시피 카테고리 (**null 가능**) |
| `recipe` | string | ✅ | 레시피 이름 |
| `source` | string | ✅ | 소스 파일 |

> ⚠️ `category`는 **null일 수 있음**. 일부 레시피는 카테고리가 지정되지 않음.

### 3.3 Role 허용값

| Role | 설명 |
|------|------|
| `input` | 재료로 소모됨 |
| `keep` | 도구로 사용, 소모 안 됨 |

> ⚠️ Role과 분류의 **연결 관계**는 Evidence Table에서 정의한다.

### 3.4 Category 허용값

| Category | 설명 |
|----------|------|
| `Carpentry` | 목공 |
| `Cooking` | 조리 |
| `Electrical` | 전자 |
| `Engineer` | 공학 |
| `Farming` | 농업 |
| `Fishing` | 낚시 |
| `Health` | 의료 |
| `Smithing` | 대장 |
| `Survivalist` | 생존 |
| `Trapper` | 덫 |
| `Welding` | 용접 |
| `null` | 미지정 |

> ⚠️ Category와 분류의 **연결 관계**는 Evidence Table에서 정의한다.

---

## 4. fixing_fixers.json

Fixing 시스템에서 Fixer 역할로 등록된 아이템 목록.

### 4.1 구조

```json
[
  "Base.DuctTape",
  "Base.Glue",
  "Base.Nails"
]
```

- **타입**: string[] (아이템 FullType 배열)

### 4.2 사용 방법

```
IF item.FullType IN fixing_fixers.json
THEN → Evidence Table 참조
```

---

## 5. moveables_tooldefs.json

ISMoveableDefinitions.lua에서 추출한 Moveables 도구 정의.

### 5.1 구조

```json
{
  "itemIds": [
    "Base.Hammer",
    "Base.Screwdriver"
  ],
  "tags": [
    "Crowbar",
    "SharpKnife"
  ],
  "defs": [
    ["Hammer", ["Base.Hammer"]],
    ["Crowbar", ["Tag.Crowbar", "Crowbar"]],
    ["Cutter", ["Tag.SharpKnife", "Tag.Scissors"]]
  ]
}
```

### 5.2 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| `itemIds` | string[] | Moveables에 등록된 아이템 ID 목록 |
| `tags` | string[] | Moveables에서 참조하는 태그 목록 |
| `defs` | array[] | [도구정의명, [매칭항목들]] 형태 |

### 5.3 사용 방법

```
IF item.FullType IN moveables_tooldefs.itemIds
THEN → Evidence Table 참조

IF item.Tags INTERSECTS moveables_tooldefs.tags
THEN → Evidence Table 참조
```

---

## 6. 필드 연산 규칙

### 6.1 exists 연산

필드 존재 여부 확인.

```
{ field: "HungerChange", exists: true }
```

### 6.2 equals 연산

값 동등 비교.

```
{ field: "Type", equals: "Weapon" }
{ field: "Alcoholic", equals: true }
```

### 6.3 contains 연산

문자열 포함 여부. 세미콜론 구분 필드에 사용.

```
{ field: "Tags", contains: "Hammer" }
{ field: "Categories", contains: "Axe" }
```

> ⚠️ 연산의 **제약 조건** (가드 필수 여부, 수치 비교 금지 등)은 Evidence Allowlist에서 정의한다.

---

## 7. 분류 흐름 요약

```
┌─────────────────────────────────────────────────────────┐
│                    입력 데이터                          │
│              (이 스키마가 정의하는 범위)                │
├─────────────────────────────────────────────────────────┤
│  items_itemscript.json        → 아이템 필드             │
│  recipes_index_full.json      → Recipe role/category   │
│  fixing_fixers.json           → Fixer 목록             │
│  moveables_tooldefs.json      → Moveables 도구         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Evidence Allowlist / Table                 │
│              (별도 문서에서 정의)                       │
├─────────────────────────────────────────────────────────┤
│  - 필드별 허용값                                        │
│  - 연산 제약 조건                                       │
│  - 분류 연결 규칙                                       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  태그 출력                              │
├─────────────────────────────────────────────────────────┤
│  { "Base.Hammer": ["Tool.1-A", "Tool.1-B", "Combat.2-C"] │
└─────────────────────────────────────────────────────────┘
```

---

## 8. 문서 계층 구조

| 계층 | 문서 | 책임 |
|------|------|------|
| **입력 스키마** | 이 문서 | 데이터 구조, 필드 타입, 파일 형식 |
| **분류 정책** | Evidence Allowlist | 허용값, 연산 제약, 가드 규칙 |
| **분류 규칙** | Evidence Table (×6) | 소분류별 증거 매칭 조건 |
| **분류 철학** | Iris Philosophy | 원칙, 금지 사항, 설계 의도 |

> ⚠️ 이 스키마는 **입력 계약**만 정의한다. "어떤 값이 어떤 분류로 연결되는지"는 Evidence Allowlist/Table의 책임이다.

---

## 9. 버전 정보

| 항목 | 값 |
|------|-----|
| 스키마 버전 | v0.2 FINAL |
| items 파일 | items_itemscript.json (2,281 아이템) |
| recipes 파일 | recipes_index_full.json (386 레시피, 355 관계 아이템) |
| 동결 일자 | 2026-01-23 |
| 메타 파일 | iris-input-schema-v0.2-final.meta.json |

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | — | 초안 |
| 0.2 FINAL | 2026-01-23 | 스키마 동결, 레이어 분리 적용 (Allowlist 제거, Medical 필드 Experimental 격리) |
