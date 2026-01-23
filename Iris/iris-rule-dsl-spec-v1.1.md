# Iris Rule DSL 명세서

**버전**: 1.1  
**상태**: FROZEN (Evidence Table/Allowlist 기반 확정)

---

## 1. 목적

이 문서는 **동결된 Evidence Table + Evidence Allowlist**를 Lua Rule 파일로 직렬화하기 위한 **공식 DSL 명세**를 정의한다.

### 1.1 DSL의 역할

- Evidence Table의 분류 조건을 **실행 가능한 형태**로 표현
- Allowlist의 제약을 **문법 레벨에서 강제**
- 자동 분류 + 수동 오버라이드의 **병합 규칙** 명시

### 1.2 DSL이 하지 않는 것

- UI 표시 방식 결정 (Iris 메뉴/Tooltip 영역)
- 태그 우선순위/중요도 부여
- 분류 결과의 의미 해석

---

## 2. 불변 조건 (Invariants)

DSL과 Rule 파일은 다음 조건을 **절대 위반할 수 없다**.

### 2.1 태그는 누적만 (Add-Only)

```
✅ 허용: add = { "Tool.1-D" }
❌ 금지: remove = { "Tool.1-D" }
❌ 금지: replace = { "Tool.1-D" }
❌ 금지: override = { "Tool.1-D" }
```

### 2.2 Allowlist 외 증거 사용 금지

- 필드, 연산자, 허용값 모두 Allowlist에 명시된 것만 사용 가능
- Allowlist에 없는 predicate는 **파싱/로드 단계에서 거부**

### 2.3 수치 비교 연산자 금지

```
❌ 금지: gt(field, value)      -- greater than
❌ 금지: lt(field, value)      -- less than  
❌ 금지: gte(field, value)     -- greater than or equal
❌ 금지: lte(field, value)     -- less than or equal
❌ 금지: field > value         -- 어떤 형태로든 금지
```

### 2.4 가드 필수 필드의 단독 사용 금지

특정 필드는 반드시 **가드 조건과 AND 결합**해야만 사용 가능.  
단독 사용 시 **로드 실패**.

### 2.5 가드 필수 Type 값의 단독 사용 금지

특정 Type 값은 오분류 위험이 있어 **보조 증거와 AND 결합 필수**.  
단독 사용 시 **로드 실패**.

---

## 3. Predicate (원자 조건)

### 3.1 Item Script 필드 Predicate

#### 3.1.1 `eq(field, value)` — 동등 비교

```lua
-- Type (enum)
eq("Type", "Weapon")
eq("Type", "Food")
eq("Type", "Literature")
eq("Type", "Clothing")
eq("Type", "Drainable")    -- ⚠️ 가드 필수 (§3.6 참조)
eq("Type", "Radio")
eq("Type", "Map")

-- SubCategory (enum) — 단일 값, contains 사용 금지
eq("SubCategory", "Firearm")
eq("SubCategory", "Swinging")
eq("SubCategory", "Stab")
eq("SubCategory", "Spear")

-- Boolean
eq("Alcoholic", true)
eq("CanStoreWater", true)
eq("TorchCone", true)
eq("ActivatedItem", true)
eq("TwoWay", true)
eq("IsLiterature", true)
eq("IsAimedFirearm", true)
```

**제약**:
- `value`는 boolean 또는 Allowlist에 등록된 enum 값만 허용
- 수치 값 비교 금지
- **SubCategory는 단일 enum** → `eq`만 허용, `contains` 금지

#### 3.1.2 `has(field)` — 필드 존재 확인

```lua
has("LightStrength")
has("LightDistance")
has("HungerChange")
has("ThirstChange")
has("StressChange")
has("UnhappyChange")
has("MountOn")
has("SkillTrained")
has("TeachedRecipes")
has("Map")
has("TwoHandWeapon")
```

**제약**:
- **가드 필수 필드**는 단독 사용 금지 (§3.5 참조)

#### 3.1.3 `not_has(field)` — 필드 부재 확인

```lua
not_has("TwoHandWeapon")
not_has("SkillTrained")
not_has("TeachedRecipes")
```

**용도**:
- Combat 장/단 무기 구분: `TwoHandWeapon` exists = 장, not exists = 단
- Literature.5-D 잔여 분류: 특수 효과 필드 없음

#### 3.1.4 `contains(field, token)` — 문자열 리스트 포함 확인

```lua
-- Categories (무기) — 리스트 필드
contains("Categories", "Blunt")
contains("Categories", "Blade")
contains("Categories", "Axe")
contains("Categories", "Spear")

-- Tags — 리스트 필드
contains("Tags", "Cookware")
contains("Tags", "Medical")
contains("Tags", "StartFire")
contains("Tags", "Lighter")

-- CustomContextMenu — 리스트 필드
contains("CustomContextMenu", "Disinfect")
contains("CustomContextMenu", "Bandage")
contains("CustomContextMenu", "Splint")
contains("CustomContextMenu", "Stitch")
contains("CustomContextMenu", "RemoveBullet")
contains("CustomContextMenu", "RemoveGlass")
contains("CustomContextMenu", "CleanWound")
```

**제약**:
- `token`은 Allowlist의 허용값 목록에 있는 것만 사용 가능
- **리스트 필드 전용** — 단일 값 필드(SubCategory 등)에 사용 금지

#### 3.1.5 `eq_bodyLocation(value)` — BodyLocation 전용

```lua
eq_bodyLocation("Head")
eq_bodyLocation("Torso")
eq_bodyLocation("Torso_Upper")
eq_bodyLocation("Torso_Lower")
eq_bodyLocation("Hands")
eq_bodyLocation("Legs")
eq_bodyLocation("Groin")
eq_bodyLocation("Feet")
eq_bodyLocation("Back")
eq_bodyLocation("FannyPack")
eq_bodyLocation("Neck")
eq_bodyLocation("Eyes")
eq_bodyLocation("Belt")
eq_bodyLocation("BeltExtra")
eq_bodyLocation("Waist")
```

**제약**:
- Allowlist의 BodyLocation 허용값만 사용 가능

#### 3.1.6 `eq_ammoType(value)` — AmmoType 전용

```lua
-- 권총 (2-G)
eq_ammoType("Base.Bullets9mm")
eq_ammoType("Base.Bullets45")
eq_ammoType("Base.Bullets44")
eq_ammoType("Base.Bullets38")

-- 소총 (2-H)
eq_ammoType("Base.223Bullets")
eq_ammoType("Base.308Bullets")
eq_ammoType("Base.556Bullets")

-- 산탄총 (2-I)
eq_ammoType("Base.ShotgunShells")
```

**제약**:
- Allowlist의 AmmoType 허용값만 사용 가능

---

### 3.2 Recipe 관계 Predicate

#### 3.2.1 `recipe.matches({ role, category })` — 튜플 매칭

```lua
recipe.matches({ role = "input", category = "Carpentry" })
recipe.matches({ role = "input", category = "Cooking" })
recipe.matches({ role = "keep", category = "Carpentry" })
recipe.matches({ role = "keep", category = "Mechanics" })
recipe.matches({ role = "require", category = "Farming" })
```

**의미**:
- "이 아이템이 **어떤 레시피에서** 지정된 role로 참조되고, **그 레시피의 category가** 지정된 값인가"

**제약**:
- `role`과 `category`는 **반드시 함께** 지정
- `category` 단독 사용 금지
- `role` 허용값: `input`, `keep`, `require`, `output`
- `output`은 분류 태그 부여 증거로 사용 금지 (연결 정보 표시용만)

**허용된 category 값**:

| Category | 용도 |
|----------|------|
| `Carpentry` | 목공 |
| `MetalWelding` | 금속 |
| `Masonry` | 석공 |
| `Cooking` | 조리 |
| `Mechanics` | 차량 정비 |
| `Farming` | 농업 |
| `Trapping` | 포획 |
| `Fishing` | 낚시 |
| `Electronics` | 전자 |
| `Electrical` | 전자 |

#### 3.2.2 `recipe.inGetItemTypes(groupName)` — 그룹 증거

```lua
recipe.inGetItemTypes("CanOpener")
```

**의미**:
- "이 아이템이 `Recipe.GetItemTypes.X` 그룹에 포함되어 있는가"

**허용된 groupName**:

| Group | 용도 |
|-------|------|
| `CanOpener` | 캔따개류 (Tool.1-B) |

---

### 3.3 Moveables 관계 Predicate

#### 3.3.1 `moveables.itemId_registered()` — 아이템 ID 등록 확인

```lua
moveables.itemId_registered()
```

**의미**:
- "이 아이템의 fullType이 `ISMoveableDefinitions.lua`의 ToolDefinition.itemId로 등록되어 있는가"

#### 3.3.2 `moveables.tag_in(tags)` — MoveablesTag 매칭

```lua
moveables.tag_in({ "Crowbar", "SharpKnife", "Hammer", "Screwdriver", "Saw", "Wrench" })
```

**의미**:
- "이 아이템이 `ISMoveableDefinitions.lua`의 ToolDefinition.moveablesTag로 참조되고, 그 태그가 허용 목록에 있는가"

**허용된 MoveablesTag 값**:

| Tag | 설명 |
|-----|------|
| `Crowbar` | 빠루류 |
| `SharpKnife` | 날카로운 칼류 |
| `Hammer` | 망치류 |
| `Screwdriver` | 스크류드라이버류 |
| `Saw` | 톱류 |
| `Wrench` | 렌치류 |

**제약**:
- Item Script의 `Tags`와 **완전히 별개의 네임스페이스**
- 혼용 금지

---

### 3.4 Fixing 관계 Predicate

#### 3.4.1 `fixing.role_eq(role)` — Fixing 역할 확인

```lua
fixing.role_eq("Fixer")
```

**의미**:
- "이 아이템이 어떤 Fixing 정의에서 Fixer 역할로 등록되어 있는가"

**허용된 role 값**:

| Role | 용도 |
|------|------|
| `Fixer` | 수리 도구 (Tool.1-C) |

---

### 3.5 가드 필수 필드 (Guarded Fields)

다음 필드는 **단독으로 `has()` 사용 금지**.  
반드시 지정된 가드 조건과 AND 결합해야 함.

| 필드 | 필수 가드 |
|------|----------|
| `LightStrength` | `eq("ActivatedItem", true)` OR `eq("TorchCone", true)` |
| `LightDistance` | `eq("ActivatedItem", true)` OR `eq("TorchCone", true)` |
| `HungerChange` | `eq("Type", "Food")` |
| `ThirstChange` | `eq("Type", "Food")` OR `eq("Type", "Drainable")` + 보조가드 |
| `StressChange` | `eq("Type", "Food")` |
| `UnhappyChange` | `eq("Type", "Food")` |
| `CanStoreWater` | `contains("Tags", "Cookware")` OR `recipe.matches({ role = "keep", category = "Cooking" })` |

**검증 시점**: Rule 로드 시 정적 검증. 가드 누락 시 **로드 실패**.

---

### 3.6 가드 필수 Type 값 (Guarded Type Values)

다음 Type 값은 **단독 사용 금지**.  
반드시 지정된 보조 증거와 AND 결합해야 함.

| Type 값 | 필수 보조 증거 | 이유 |
|---------|---------------|------|
| `Drainable` | `has("ThirstChange")` OR `eq("CanStoreWater", true)` | 연료/세제/공업용 액체 오분류 방지 |

**위반 예시**:

```lua
-- ❌ 금지: Drainable 단독
eq("Type", "Drainable")

-- ✅ 허용: Drainable + ThirstChange
allOf({
  eq("Type", "Drainable"),
  has("ThirstChange"),
})

-- ✅ 허용: Drainable + CanStoreWater
allOf({
  eq("Type", "Drainable"),
  eq("CanStoreWater", true),
})

-- ✅ 허용: Drainable + 둘 다
allOf({
  eq("Type", "Drainable"),
  anyOf({
    has("ThirstChange"),
    eq("CanStoreWater", true),
  }),
})
```

> ⚠️ **허용되는 보조 증거는 정확히 2가지**: `has("ThirstChange")` 또는 `eq("CanStoreWater", true)`.  
> 다른 증거(예: Recipe 관계)는 Drainable 가드로 인정되지 않음.

**검증 시점**: Rule 로드 시 정적 검증. 보조 증거 누락 시 **로드 실패**.

---

## 4. 조합 연산자 (Combinators)

### 4.1 `allOf([...])` — AND 결합

```lua
allOf({
  eq("Type", "Weapon"),
  contains("Categories", "Blunt"),
  has("TwoHandWeapon"),
})
```

**의미**: 모든 조건이 참일 때 참

### 4.2 `anyOf([...])` — OR 결합

```lua
anyOf({
  contains("CustomContextMenu", "Stitch"),
  contains("CustomContextMenu", "RemoveBullet"),
  contains("CustomContextMenu", "RemoveGlass"),
})
```

**의미**: 하나 이상의 조건이 참일 때 참

### 4.3 중첩 허용

```lua
allOf({
  eq("Type", "Weapon"),
  eq("SubCategory", "Firearm"),
  anyOf({
    eq_ammoType("Base.Bullets9mm"),
    eq_ammoType("Base.Bullets45"),
    eq_ammoType("Base.Bullets44"),
    eq_ammoType("Base.Bullets38"),
  }),
})
```

---

## 5. Rule 정의

### 5.1 Rule 구조

```lua
{
  id = "Category.Subcategory.Name",
  when = <predicate_expression>,
  add = { "Tag1", "Tag2", ... },
  reason = "EvidenceTable:<Category>.<Subcategory>.<EvidenceKey>",
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `id` | string | ✅ | 고유 식별자 (디버깅/추적용) |
| `when` | predicate | ✅ | 매칭 조건 |
| `add` | string[] | ✅ | 부여할 태그 목록 (1개 이상) |
| `reason` | string | ✅ | Evidence Table 참조 근거 (**정규화 형식**) |

### 5.2 `reason` 필드 정규화 형식

```
EvidenceTable:<대분류>.<소분류>.<증거키>
```

**예시**:
- `EvidenceTable:Tool.1-D.TagsCookware`
- `EvidenceTable:Tool.1-D.RecipeKeepCooking`
- `EvidenceTable:Combat.2-G.AmmoTypeHandgun`
- `EvidenceTable:Tool.1-H.LightFieldsGuarded`
- `EvidenceTable:Consumable.3-B.DrainableThirstChange`

**목적**:
- Evidence Table ↔ Rule ↔ UI 설명의 기계적 연결
- 문구 변경으로 인한 의미 변질 방지
- 디버깅 시 역추적 용이

### 5.3 Rule 예시

#### Tool.1-D (조리)

```lua
-- tool_1d.lua
return {
  {
    id = "Tool.1-D.Cookware",
    when = contains("Tags", "Cookware"),
    add = { "Tool.1-D" },
    reason = "EvidenceTable:Tool.1-D.TagsCookware",
  },
  {
    id = "Tool.1-D.RecipeCooking",
    when = recipe.matches({ role = "keep", category = "Cooking" }),
    add = { "Tool.1-D" },
    reason = "EvidenceTable:Tool.1-D.RecipeKeepCooking",
  },
}
```

#### Combat.2-G (권총)

```lua
-- combat_2g.lua
return {
  {
    id = "Combat.2-G.Handgun",
    when = allOf({
      eq("Type", "Weapon"),
      eq("SubCategory", "Firearm"),  -- eq 사용 (contains 아님)
      anyOf({
        eq_ammoType("Base.Bullets9mm"),
        eq_ammoType("Base.Bullets45"),
        eq_ammoType("Base.Bullets44"),
        eq_ammoType("Base.Bullets38"),
      }),
    }),
    add = { "Combat.2-G" },
    reason = "EvidenceTable:Combat.2-G.AmmoTypeHandgun",
  },
}
```

#### Tool.1-H (광원/점화) — 가드 필수 적용

```lua
-- tool_1h.lua
return {
  {
    id = "Tool.1-H.LightWithGuard",
    when = anyOf({
      -- LightStrength + 가드
      allOf({
        has("LightStrength"),
        anyOf({ eq("ActivatedItem", true), eq("TorchCone", true) }),
      }),
      -- LightDistance + 가드
      allOf({
        has("LightDistance"),
        anyOf({ eq("ActivatedItem", true), eq("TorchCone", true) }),
      }),
      -- TorchCone 단독 허용
      eq("TorchCone", true),
    }),
    add = { "Tool.1-H" },
    reason = "EvidenceTable:Tool.1-H.LightFieldsGuarded",
  },
  {
    id = "Tool.1-H.StartFire",
    when = contains("Tags", "StartFire"),
    add = { "Tool.1-H" },
    reason = "EvidenceTable:Tool.1-H.TagsStartFire",
  },
  {
    id = "Tool.1-H.Lighter",
    when = contains("Tags", "Lighter"),
    add = { "Tool.1-H" },
    reason = "EvidenceTable:Tool.1-H.TagsLighter",
  },
}
```

#### Consumable.3-B (음료) — Type=Drainable 가드 적용

```lua
-- consumable_3b.lua
return {
  {
    id = "Consumable.3-B.FoodThirst",
    when = allOf({
      eq("Type", "Food"),
      has("ThirstChange"),
    }),
    add = { "Consumable.3-B" },
    reason = "EvidenceTable:Consumable.3-B.FoodThirstChange",
  },
  {
    id = "Consumable.3-B.DrainableThirst",
    when = allOf({
      eq("Type", "Drainable"),
      has("ThirstChange"),  -- Drainable 가드: ThirstChange 필수
    }),
    add = { "Consumable.3-B" },
    reason = "EvidenceTable:Consumable.3-B.DrainableThirstChange",
  },
}
```

---

## 6. 수동 오버라이드 (Manual Overrides)

### 6.1 용도

- **자동 분류 불가 아이템**: 바닐라/모드 데이터에 증거가 누락된 경우
- **자동 분류 보강**: 자동 결과에 추가 태그가 필요한 경우

### 6.2 구조

```lua
-- overrides_manual.lua
return {
  -- Tool.1-J (전력) — 자동 분류 불가
  ["Base.Generator"] = { add = { "Tool.1-J" } },
  
  -- Combat.2-J (투척/폭발) — 자동 분류 불가
  ["Base.Molotov"] = { add = { "Combat.2-J" } },
  ["Base.PipeBomb"] = { add = { "Combat.2-J" } },
  ["Base.SmokeBomb"] = { add = { "Combat.2-J" } },
  
  -- Combat.2-K (탄약) — 자동 분류 불가
  ["Base.Bullets9mm"] = { add = { "Combat.2-K" } },
  ["Base.Bullets45"] = { add = { "Combat.2-K" } },
  ["Base.Bullets44"] = { add = { "Combat.2-K" } },
  ["Base.Bullets38"] = { add = { "Combat.2-K" } },
  ["Base.223Bullets"] = { add = { "Combat.2-K" } },
  ["Base.308Bullets"] = { add = { "Combat.2-K" } },
  ["Base.556Bullets"] = { add = { "Combat.2-K" } },
  ["Base.ShotgunShells"] = { add = { "Combat.2-K" } },
  
  -- Consumable.3-E (약초) — 자동 분류 불가
  ["Base.Lemongrass"] = { add = { "Consumable.3-E" } },
  ["Base.Comfrey"] = { add = { "Consumable.3-E" } },
  
  -- Resource.4-D (연료) — 자동 분류 불가
  ["Base.PetrolCan"] = { add = { "Resource.4-D" } },
  ["Base.PropaneTank"] = { add = { "Resource.4-D" } },
}
```

### 6.3 제약

| 허용 | 금지 |
|------|------|
| `add = {...}` | `remove = {...}` |
| | `replace = {...}` |
| | `override = {...}` |
| | 자동 분류 결과 덮어쓰기 |

### 6.4 사용 조건

수동 오버라이드는 다음 경우에**만** 허용:

1. 바닐라/모드 데이터에 증거가 **구조적으로 누락**된 경우
2. Evidence Table이 **"자동 분류 불가"**로 명시한 소분류

**금지 사유**:
- 분류 결과가 마음에 들지 않음
- 특정 아이템을 "특별 취급"하고 싶음

---

## 7. 병합 규칙 (Merge Rules)

### 7.1 실행 순서

```
1. autoTags = runAllRules(item)
2. manualTags = manualOverrides[item.fullType]?.add or {}
3. finalTags = set_union(autoTags, manualTags)
```

### 7.2 충돌 해결

**충돌 없음** — 둘 다 add-only이므로 단순 합집합.

```
autoTags = { "Tool.1-D", "Combat.2-C" }
manualTags = { "Tool.1-D" }  -- 중복

finalTags = { "Tool.1-D", "Combat.2-C" }  -- 중복 제거된 합집합
```

### 7.3 금지되는 병합 패턴

```
❌ manual이 auto를 막음
❌ manual이 auto를 대체함
❌ manual이 auto보다 우선순위를 가짐
```

---

## 8. 파일 구조

### 8.1 디렉토리 레이아웃

```
media/lua/client/Iris/rules/
├── iris_ruleset.lua          -- 엔트리 포인트
├── allowlist.lua             -- Allowlist 동기화
├── overrides_manual.lua      -- 수동 오버라이드
│
├── tool/
│   ├── tool_1a.lua           -- 건설/제작
│   ├── tool_1b.lua           -- 분해/개방
│   ├── tool_1c.lua           -- 정비
│   ├── tool_1d.lua           -- 조리
│   ├── tool_1e.lua           -- 농업/채집
│   ├── tool_1f.lua           -- 의료
│   ├── tool_1g.lua           -- 포획
│   ├── tool_1h.lua           -- 광원/점화
│   ├── tool_1i.lua           -- 통신
│   └── tool_1j.lua           -- 전력 (빈 파일)
│
├── combat/
│   ├── combat_2a.lua         -- 도끼류
│   ├── combat_2b.lua         -- 장둔기
│   ├── combat_2c.lua         -- 단둔기
│   ├── combat_2d.lua         -- 장검류
│   ├── combat_2e.lua         -- 단검류
│   ├── combat_2f.lua         -- 창류
│   ├── combat_2g.lua         -- 권총
│   ├── combat_2h.lua         -- 소총
│   ├── combat_2i.lua         -- 산탄총
│   ├── combat_2j.lua         -- 투척/폭발 (빈 파일)
│   ├── combat_2k.lua         -- 탄약 (빈 파일)
│   └── combat_2l.lua         -- 총기부품
│
├── consumable/
│   ├── consumable_3a.lua     -- 식품
│   ├── consumable_3b.lua     -- 음료
│   ├── consumable_3c.lua     -- 의약품
│   ├── consumable_3d.lua     -- 기호품
│   └── consumable_3e.lua     -- 약초 (빈 파일)
│
├── resource/
│   ├── resource_4a.lua       -- 건설 재료
│   ├── resource_4b.lua       -- 조리 재료
│   ├── resource_4c.lua       -- 의료 재료
│   ├── resource_4d.lua       -- 연료 (빈 파일)
│   ├── resource_4e.lua       -- 전자부품
│   └── resource_4f.lua       -- 기타 재료
│
├── literature/
│   ├── literature_5a.lua     -- 스킬북
│   ├── literature_5b.lua     -- 레시피잡지
│   ├── literature_5c.lua     -- 지도
│   └── literature_5d.lua     -- 일반 서적
│
└── wearable/
    ├── wearable_6a.lua       -- 모자/헬멧
    ├── wearable_6b.lua       -- 상의
    ├── wearable_6c.lua       -- 하의
    ├── wearable_6d.lua       -- 장갑
    ├── wearable_6e.lua       -- 신발
    ├── wearable_6f.lua       -- 배낭
    ├── wearable_6g.lua       -- 힙색
    └── wearable_6h.lua       -- 액세서리
```

### 8.2 빈 파일 규칙

자동 분류 불가 소분류는 **빈 테이블을 반환**:

```lua
-- tool_1j.lua (전력 — 자동 분류 불가)
-- Evidence Table: "필수 증거 없음 — 수동 오버라이드로만 처리"
return {}
```

---

## 9. 검증 규칙

Rule 로더는 다음을 **정적 검증**해야 함.

### 9.1 Allowlist 준수

- 사용된 모든 필드명이 Allowlist에 존재
- 사용된 모든 허용값이 Allowlist에 존재
- 금지된 연산자 (`gt`, `lt`, `gte`, `lte`) 부재

### 9.2 가드 필수 필드 검증

- `has("LightStrength")`가 적절한 가드와 AND 결합되어 있는지
- `has("HungerChange")`가 `eq("Type", "Food")`와 AND 결합되어 있는지
- 기타 GUARDED_FIELDS 모두 검증

### 9.3 가드 필수 Type 값 검증

- `eq("Type", "Drainable")`가 적절한 보조 증거와 AND 결합되어 있는지
- 기타 GUARDED_TYPES 모두 검증

### 9.4 contains 사용 제한 검증

- `contains("SubCategory", ...)`가 사용되면 **로드 실패**
- SubCategory는 `eq`만 허용

### 9.5 Recipe Category 단독 사용 금지

- `recipe.matches`에서 `category`만 있고 `role`이 없는 경우 거부

### 9.6 수동 오버라이드 구조

- `add` 외의 키 (`remove`, `replace`, `override`) 존재 시 거부

---

## 10. 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 1.0 | - | 초안 확정 |
| 1.1 | - | SubCategory eq 전환, Type=Drainable 가드 추가, reason 정규화 |
| 1.1.1 | - | CanStoreWater 가드 튜플 규칙 정합, Drainable 보조증거 구체화 (2가지만 허용) |

---

## 부록 A: Predicate 요약표

| Predicate | 용도 | 예시 |
|-----------|------|------|
| `eq(field, value)` | boolean/enum 동등 | `eq("Type", "Weapon")` |
| `has(field)` | 필드 존재 | `has("MountOn")` |
| `not_has(field)` | 필드 부재 | `not_has("TwoHandWeapon")` |
| `contains(field, token)` | 리스트 포함 (**리스트 필드 전용**) | `contains("Tags", "Cookware")` |
| `eq_bodyLocation(value)` | BodyLocation 매칭 | `eq_bodyLocation("Head")` |
| `eq_ammoType(value)` | AmmoType 매칭 | `eq_ammoType("Base.Bullets9mm")` |
| `recipe.matches({...})` | Recipe 튜플 매칭 | `recipe.matches({ role="input", category="Cooking" })` |
| `recipe.inGetItemTypes(group)` | 그룹 포함 | `recipe.inGetItemTypes("CanOpener")` |
| `moveables.itemId_registered()` | Moveables ID 등록 | — |
| `moveables.tag_in(tags)` | MoveablesTag 매칭 | `moveables.tag_in({ "Crowbar" })` |
| `fixing.role_eq(role)` | Fixing 역할 | `fixing.role_eq("Fixer")` |
| `allOf([...])` | AND 조합 | — |
| `anyOf([...])` | OR 조합 | — |

---

## 부록 B: 태그 형식

태그는 다음 형식을 따름:

```
<대분류>.<소분류코드>
```

| 대분류 | 소분류 범위 |
|--------|------------|
| Tool | 1-A ~ 1-J |
| Combat | 2-A ~ 2-L |
| Consumable | 3-A ~ 3-E |
| Resource | 4-A ~ 4-F |
| Literature | 5-A ~ 5-D |
| Wearable | 6-A ~ 6-H |

예시:
- `Tool.1-D` (조리)
- `Combat.2-G` (권총)
- `Consumable.3-A` (식품)
- `Wearable.6-A` (모자/헬멧)

---

## 부록 C: 필드 타입 분류

### 리스트 필드 (contains 허용)

| 필드 | 설명 |
|------|------|
| `Categories` | 무기 카테고리 (복수 가능) |
| `Tags` | 아이템 태그 (복수 가능) |
| `CustomContextMenu` | 컨텍스트 메뉴 액션 (복수 가능) |

### 단일 값 필드 (eq만 허용)

| 필드 | 설명 |
|------|------|
| `Type` | 아이템 타입 enum |
| `SubCategory` | 무기 세부 카테고리 enum |
| `BodyLocation` | 착용 부위 enum |
| `AmmoType` | 탄약 타입 |
| `Alcoholic` | boolean |
| `CanStoreWater` | boolean |
| `TorchCone` | boolean |
| `ActivatedItem` | boolean |
| `TwoWay` | boolean |
| `IsLiterature` | boolean |
| `IsAimedFirearm` | boolean |
