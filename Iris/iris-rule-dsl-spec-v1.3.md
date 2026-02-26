# Iris Rule DSL 명세서

**버전**: 1.3  
**상태**: FROZEN (Evidence Table/Allowlist v0.3 기반 확정)

> ⚠️ **v1.3 주요 변경**: Context Outcome predicate 신규 추가.  
> Allowlist v0.3과 동기화하여 바닐라 Lua에서 정적 추출한 결과 타입을 분류 증거로 사용 가능.

---

## 1. 목적

이 문서는 **동결된 Evidence Table + Evidence Allowlist v0.3**를 Lua Rule 파일로 직렬화하기 위한 **공식 DSL 명세**를 정의한다.

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

- 필드, 연산자, 허용값 모두 Allowlist v0.3에 명시된 것만 사용 가능
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

### 2.6 행동(Action) 기반 증거 금지 — v1.3 신규

```
❌ 금지: has_action("Rip Clothing")     -- 행동명
❌ 금지: menu_contains("...")           -- 메뉴 문자열
❌ 금지: 런타임 getContextMenu() 참조
```

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
eq("Type", "Normal")
eq("Type", "Container")
eq("Type", "WeaponPart")

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
eq("Medical", true)
eq("CanBandage", true)
```

**제약**:
- `value`는 boolean 또는 Allowlist에 등록된 enum 값만 허용
- 수치 값 비교 금지
- **SubCategory는 단일 enum** → `eq`만 허용, `contains` 금지

#### 3.1.2 `has(field)` — 필드 존재 확인

```lua
has("LightStrength")
has("HungerChange")
has("ThirstChange")
has("StressChange")
has("UnhappyChange")
has("MountOn")
has("SkillTrained")
has("TeachedRecipes")
has("Map")
has("TwoHandWeapon")
has("AlcoholPower")
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
contains("Categories", "Axe")
contains("Categories", "Blunt")
contains("Categories", "SmallBlunt")
contains("Categories", "LongBlade")
contains("Categories", "SmallBlade")
contains("Categories", "Spear")
contains("Categories", "Improvised")

-- Tags — 리스트 필드 (도구 관련)
contains("Tags", "Hammer")
contains("Tags", "Saw")
contains("Tags", "Screwdriver")
contains("Tags", "Crowbar")
contains("Tags", "Scissors")
contains("Tags", "CanOpener")
contains("Tags", "RemoveBarricade")
contains("Tags", "FishingRod")
contains("Tags", "FishingSpear")
contains("Tags", "Lighter")
contains("Tags", "StartFire")
contains("Tags", "ChopTree")
contains("Tags", "DigPlow")
contains("Tags", "DigGrave")
contains("Tags", "ClearAshes")
contains("Tags", "TakeDirt")
contains("Tags", "Sledgehammer")
contains("Tags", "WeldingMask")

-- Tags — 의료 관련
contains("Tags", "RemoveBullet")
contains("Tags", "RemoveGlass")
contains("Tags", "SewingNeedle")
contains("Tags", "Disinfectant")

-- Tags — 조리 관련
contains("Tags", "CoffeeMaker")
contains("Tags", "SharpKnife")
contains("Tags", "DullKnife")
contains("Tags", "Fork")
contains("Tags", "Spoon")

-- Tags — 식품/음료 관련
contains("Tags", "AlcoholicBeverage")
contains("Tags", "LowAlcohol")
contains("Tags", "HerbalTea")

-- Tags — 기타
contains("Tags", "Petrol")
contains("Tags", "Rope")
contains("Tags", "GasMask")

-- CustomContextMenu — 리스트 필드
contains("CustomContextMenu", "Drink")
contains("CustomContextMenu", "Smoke")
contains("CustomContextMenu", "Take")
```

**제약**:
- `token`은 Allowlist v0.3의 허용값 목록에 있는 것만 사용 가능
- **리스트 필드 전용** — 단일 값 필드(SubCategory 등)에 사용 금지

> ⚠️ **v1.2 폐기된 값** (사용 시 로드 실패):
> - Categories: `Blade` (→ `SmallBlade`, `LongBlade` 사용)
> - Tags: `Cookware`, `Medical`, `Tool`, `Weapon`, `Clothing`, `Food`, `Literature`
> - CustomContextMenu: `Disinfect`, `Bandage`, `Splint`, `Stitch`, `RemoveBullet`, `RemoveGlass`, `CleanWound`

#### 3.1.5 `eq_bodyLocation(value)` — BodyLocation 전용

```lua
-- 6-A 모자/헬멧
eq_bodyLocation("Hat")
eq_bodyLocation("FullHat")
eq_bodyLocation("FullHelmet")
eq_bodyLocation("Mask")
eq_bodyLocation("MaskEyes")
eq_bodyLocation("MaskFull")

-- 6-B 상의
eq_bodyLocation("Shirt")
eq_bodyLocation("ShortSleeveShirt")
eq_bodyLocation("Tshirt")
eq_bodyLocation("TankTop")
eq_bodyLocation("Sweater")
eq_bodyLocation("SweaterHat")
eq_bodyLocation("Jacket")
eq_bodyLocation("JacketHat")
eq_bodyLocation("JacketHat_Bulky")
eq_bodyLocation("JacketSuit")
eq_bodyLocation("Jacket_Bulky")
eq_bodyLocation("Jacket_Down")
eq_bodyLocation("TorsoExtra")
eq_bodyLocation("TorsoExtraVest")

-- 6-C 하의
eq_bodyLocation("Pants")
eq_bodyLocation("Skirt")
eq_bodyLocation("Legs1")

-- 6-D 장갑
eq_bodyLocation("Hands")

-- 6-E 신발
eq_bodyLocation("Shoes")
eq_bodyLocation("Socks")

-- 6-G 액세서리/힙색
eq_bodyLocation("FannyPackFront")
eq_bodyLocation("FannyPackBack")
eq_bodyLocation("Belt")
eq_bodyLocation("BeltExtra")
eq_bodyLocation("Neck")
eq_bodyLocation("Necklace")
eq_bodyLocation("Necklace_Long")
eq_bodyLocation("Eyes")
eq_bodyLocation("LeftEye")
eq_bodyLocation("RightEye")
eq_bodyLocation("Ears")
eq_bodyLocation("EarTop")
eq_bodyLocation("Scarf")
eq_bodyLocation("LeftWrist")
eq_bodyLocation("RightWrist")
eq_bodyLocation("Left_MiddleFinger")
eq_bodyLocation("Left_RingFinger")
eq_bodyLocation("Right_MiddleFinger")
eq_bodyLocation("Right_RingFinger")
eq_bodyLocation("Nose")
eq_bodyLocation("BellyButton")
eq_bodyLocation("AmmoStrap")

-- 다중 태그 (전신복)
eq_bodyLocation("Boilersuit")    -- → 6-B + 6-C
eq_bodyLocation("Dress")         -- → 6-B + 6-C
eq_bodyLocation("FullSuit")      -- → 6-B + 6-C
eq_bodyLocation("FullSuitHead")  -- → 6-A + 6-B + 6-C
```

**제약**:
- Allowlist v0.3의 BodyLocation 허용값만 사용 가능
- **분류 제외**: `ZedDmg`, `Wound`, `Bandage`, `MakeUp_*`, `Underwear*`, `Tail`

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
recipe.matches({ role = "keep", category = "Cooking" })
recipe.matches({ role = "require", category = "Farming" })
recipe.matches({ role = "input", category = "Electrical" })
recipe.matches({ role = "input", category = "Health" })
recipe.matches({ role = "input", category = "Welding" })
```

**의미**:
- "이 아이템이 **어떤 레시피에서** 지정된 role로 참조되고, **그 레시피의 category가** 지정된 값인가"

**제약**:
- `role`과 `category`는 **반드시 함께** 지정
- `category` 단독 사용 금지
- `role` 허용값: `input`, `keep`, `require`, `output`
- `output`은 분류 태그 부여 증거로 사용 금지 (연결 정보 표시용만)

**허용된 category 값 (Allowlist v0.3)**:

| Category | 용도 |
|----------|------|
| `Carpentry` | 목공 |
| `Cooking` | 조리 |
| `Electrical` | 전자 |
| `Smithing` | 대장 |
| `Welding` | 용접 |
| `Survivalist` | 생존 |
| `Farming` | 농업 |
| `Fishing` | 낚시 |
| `Trapper` | 덫 |
| `Health` | 의료 |
| `Engineer` | 공학 |

> ⚠️ **v1.2 폐기된 category** (사용 시 로드 실패):
> - `MetalWelding` → `Welding` 사용
> - `Masonry` — 바닐라에 없음
> - `Mechanics` — 바닐라에 없음
> - `Electronics` → `Electrical` 사용
> - `Trapping` → `Trapper` 사용

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

**허용된 itemId (Allowlist v0.3)**:

| ItemId | 도구 정의 |
|--------|-----------|
| `Base.Hammer` | Hammer |
| `Base.Screwdriver` | Electrician, Metal |
| `Base.Shovel` | Shovel |
| `Base.Wrench` | Wrench |
| `Base.PipeWrench` | Wrench |

#### 3.3.2 `moveables.tag_in(tags)` — MoveablesTag 매칭

```lua
moveables.tag_in({ "Crowbar", "SharpKnife", "Hammer", "Screwdriver", "Saw", "Wrench" })
```

**의미**:
- "이 아이템이 `ISMoveableDefinitions.lua`의 ToolDefinition.moveablesTag로 참조되고, 그 태그가 허용 목록에 있는가"

**허용된 MoveablesTag 값 (Allowlist v0.3)**:

| Tag | 설명 |
|-----|------|
| `Crowbar` | 빠루류 |
| `SharpKnife` | 날카로운 칼류 |
| `Hammer` | 망치류 |
| `Screwdriver` | 스크류드라이버류 |
| `Saw` | 톱류 |
| `Wrench` | 렌치류 |
| `Scissors` | 가위류 |
| `WeldingMask` | 용접마스크 |

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
| `HungerChange` | `eq("Type", "Food")` |
| `ThirstChange` | `eq("Type", "Food")` OR `eq("Type", "Drainable")` + 보조가드 |
| `StressChange` | `eq("Type", "Food")` |
| `UnhappyChange` | `eq("Type", "Food")` |

**예외: 단독 exists 허용 필드**

다음 필드는 전용 필드이므로 단독 `has()` 허용:

- `Medical` — 의료 아이템 전용
- `CanBandage` — 붕대 아이템 전용
- `MountOn` — 총기부품 전용
- `TorchCone` — 손전등 전용
- `TeachedRecipes` — 레시피잡지 전용
- `SkillTrained` — 스킬북 전용
- `AlcoholPower` — 소독 효과 전용

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
```

---

### 3.7 Context Outcome Predicate — v1.3 신규

#### 3.7.1 `has_outcome(outcome)` — 결과 타입 존재 확인

```lua
-- 착용/장착 관련
has_outcome("equip_primary")      -- 주무기 슬롯 장착 가능
has_outcome("equip_secondary")    -- 보조 슬롯 장착 가능
has_outcome("equip_back")         -- 등 슬롯 장착 가능

-- 변형 관련
has_outcome("rip_clothing")       -- 찢어서 천 조각으로 변환 가능
has_outcome("disassemble")        -- 분해 가능

-- 컨테이너 관련
has_outcome("fill_container")     -- 내용물 채우기 가능
has_outcome("empty_container")    -- 내용물 비우기 가능

-- 상태 토글 관련
has_outcome("toggle_activate")    -- 활성화/비활성화 토글 가능

-- 배치 관련
has_outcome("place_world")        -- 월드에 배치 가능

-- 소비 관련
has_outcome("read_literature")    -- 읽기 가능
has_outcome("eat_food")           -- 먹기 가능
has_outcome("drink_beverage")     -- 마시기 가능
has_outcome("apply_medical")      -- 의료 적용 가능
has_outcome("smoke_item")         -- 흡연 가능

-- 총기 관련
has_outcome("insert_magazine")    -- 탄창 삽입 가능
has_outcome("attach_part")        -- 부품 장착 가능

-- 수리 관련
has_outcome("repair_item")        -- 수리 가능
```

**의미**:
- "이 아이템이 **정적 추출된 Context Outcome 데이터**에서 해당 결과 타입을 가지고 있는가"

**제약**:
- **존재 여부만 검사** — 비교 연산 금지
- **조건부 로직 금지** — `if`, `when` 없음
- **순서/우선순위 금지**
- **횟수/효율 금지**
- **Allowlist에 명시된 Outcome만 사용 가능**

**허용된 Outcome 값 (Allowlist v0.3)**:

| Outcome | 설명 | 분류 연결 |
|---------|------|-----------|
| `rip_clothing` | 찢어서 천 조각으로 변환 가능 | Wearable 보조 |
| `equip_primary` | 주무기 슬롯 장착 가능 | Combat 보조 |
| `equip_secondary` | 보조 슬롯 장착 가능 | Combat 보조 |
| `equip_back` | 등 슬롯 장착 가능 | Wearable.6-F |
| `place_world` | 월드에 배치 가능 | Tool.1-J 보조 |
| `fill_container` | 내용물 채우기 가능 | Resource 보조 |
| `empty_container` | 내용물 비우기 가능 | Resource 보조 |
| `toggle_activate` | 활성화/비활성화 토글 가능 | Tool.1-H 보조 |
| `read_literature` | 읽기 가능 | Literature 보조 |
| `eat_food` | 먹기 가능 | Consumable.3-A 보조 |
| `drink_beverage` | 마시기 가능 | Consumable.3-B 보조 |
| `apply_medical` | 의료 적용 가능 | Consumable.3-C 보조 |
| `smoke_item` | 흡연 가능 | Consumable.3-D 보조 |
| `insert_magazine` | 탄창 삽입 가능 | Combat.2-G/H/I 보조 |
| `attach_part` | 부품 장착 가능 | Combat.2-L 보조 |
| `disassemble` | 분해 가능 | Tool.1-B 보조 |
| `repair_item` | 수리 가능 | Tool.1-C 보조 |

#### 3.7.2 핵심 원칙 — 행동이 아닌 결과

> **Iris는 '어떻게 클릭하는가'를 기록하지 않는다.**  
> **Iris는 '이 아이템이 가질 수 있는 상태/변형/용도'를 기록한다.**

**허용**:
```lua
has_outcome("rip_clothing")       -- ✅ 결과 타입
```

**금지**:
```lua
has_action("Rip Clothing")        -- ❌ 행동명
menu_contains("Rip Clothing")     -- ❌ 메뉴 문자열
```

#### 3.7.3 데이터 추출 규칙

1. **오프라인 추출**: 바닐라 Lua 파일에서 정적 분석으로 추출
2. **정적 동결**: 추출 결과를 고정 데이터로 저장
3. **재현 가능**: 바닐라 Lua 변경 시 재추출로 갱신 가능

---

## 4. 복합 조건 (Combinators)

### 4.1 `allOf([...])` — AND 조합

```lua
allOf({
  eq("Type", "Weapon"),
  contains("Categories", "Blunt"),
  has("TwoHandWeapon"),
})
```

**의미**: 모든 조건이 참일 때만 참

### 4.2 `anyOf([...])` — OR 조합

```lua
anyOf({
  contains("Tags", "Lighter"),
  contains("Tags", "StartFire"),
})
```

**의미**: 하나 이상 조건이 참이면 참

### 4.3 중첩 허용

```lua
allOf({
  eq("Type", "Weapon"),
  anyOf({
    contains("Categories", "SmallBlade"),
    contains("Categories", "LongBlade"),
  }),
})
```

### 4.4 Context Outcome과 조합 — v1.3 신규

```lua
-- 배낭 분류: Type=Clothing이 아니지만 등에 장착 가능한 경우
anyOf({
  allOf({
    eq("Type", "Clothing"),
    eq_bodyLocation("Back"),
  }),
  has_outcome("equip_back"),  -- Context Outcome 기반 대안
})
```

---

## 5. Rule 파일 형식

### 5.1 단일 Rule 구조

```lua
{
  id = "Category.X-Y.RuleName",     -- 고유 식별자
  when = <predicate>,               -- 매칭 조건
  add = { "Category.X-Y" },         -- 부여할 태그 (add만 허용)
  reason = "EvidenceTable:...",     -- 추적용 사유
}
```

### 5.2 파일 형식

```lua
-- category_xy.lua
return {
  { id = "...", when = ..., add = {...}, reason = "..." },
  { id = "...", when = ..., add = {...}, reason = "..." },
}
```

### 5.3 reason 형식 규칙

```
EvidenceTable:<대분류>.<소분류>.<증거요약>
```

예시:
- `EvidenceTable:Tool.1-A.RecipeKeepCarpentry`
- `EvidenceTable:Combat.2-G.AmmoTypeHandgun`
- `EvidenceTable:Wearable.6-A.BodyLocationHat`
- `EvidenceTable:Wearable.6-F.ContextOutcomeEquipBack` — v1.3 신규

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
├── allowlist.lua             -- Allowlist v0.3 동기화
├── overrides_manual.lua      -- 수동 오버라이드
├── context_outcomes.lua      -- Context Outcome 정적 데이터 (v1.3 신규)
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

### 8.3 Context Outcome 데이터 파일 — v1.3 신규

```lua
-- context_outcomes.lua
-- 바닐라 Lua에서 정적 추출한 Context Outcome 데이터
-- 이 파일은 오프라인 추출 스크립트로 생성됨

return {
  ["Base.Bag_BigHikingBag"] = { "equip_back" },
  ["Base.Shirt"] = { "rip_clothing" },
  ["Base.Generator"] = { "place_world", "toggle_activate" },
  -- ...
}
```

---

## 9. 검증 규칙

Rule 로더는 다음을 **정적 검증**해야 함.

### 9.1 Allowlist 준수

- 사용된 모든 필드명이 Allowlist v0.3에 존재
- 사용된 모든 허용값이 Allowlist v0.3에 존재
- 금지된 연산자 (`gt`, `lt`, `gte`, `lte`) 부재
- **폐기된 값 사용 시 로드 실패**

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

### 9.7 Context Outcome 검증 — v1.3 신규

- `has_outcome()`에 사용된 값이 Allowlist v0.3의 Outcome 허용값에 존재하는지
- 행동명(`has_action`) 또는 메뉴 문자열(`menu_contains`) 사용 시 **로드 실패**

---

## 10. 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 1.0 | - | 초안 확정 |
| 1.1 | - | SubCategory eq 전환, Type=Drainable 가드 추가, reason 정규화 |
| 1.1.1 | - | CanStoreWater 가드 튜플 규칙 정합, Drainable 보조증거 구체화 |
| 1.2 | - | Allowlist v0.2 동기화. 폐기된 값 명시 (Blade, MetalWelding, Cookware 등). BodyLocation 전면 개정. Medical/CanBandage 추가 |
| 1.3 | - | Allowlist v0.3 동기화. Context Outcome predicate 신규 추가 (`has_outcome`). 행동 기반 증거 금지 규칙 명시. |

---

## 부록 A: Predicate 요약표

| Predicate | 용도 | 예시 |
|-----------|------|------|
| `eq(field, value)` | boolean/enum 동등 | `eq("Type", "Weapon")` |
| `has(field)` | 필드 존재 | `has("MountOn")` |
| `not_has(field)` | 필드 부재 | `not_has("TwoHandWeapon")` |
| `contains(field, token)` | 리스트 포함 (**리스트 필드 전용**) | `contains("Tags", "Hammer")` |
| `eq_bodyLocation(value)` | BodyLocation 매칭 | `eq_bodyLocation("Hat")` |
| `eq_ammoType(value)` | AmmoType 매칭 | `eq_ammoType("Base.Bullets9mm")` |
| `recipe.matches({...})` | Recipe 튜플 매칭 | `recipe.matches({ role="input", category="Cooking" })` |
| `recipe.inGetItemTypes(group)` | 그룹 포함 | `recipe.inGetItemTypes("CanOpener")` |
| `moveables.itemId_registered()` | Moveables ID 등록 | — |
| `moveables.tag_in(tags)` | MoveablesTag 매칭 | `moveables.tag_in({ "Crowbar" })` |
| `fixing.role_eq(role)` | Fixing 역할 | `fixing.role_eq("Fixer")` |
| `has_outcome(outcome)` | Context Outcome 존재 (**v1.3 신규**) | `has_outcome("equip_back")` |
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
| Wearable | 6-A ~ 6-G |

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
| `Medical` | boolean |
| `CanBandage` | boolean |

### Context Outcome 필드 (has_outcome만 허용) — v1.3 신규

| 필드 | 설명 |
|------|------|
| `ContextOutcome` | 정적 추출된 결과 타입 (복수 가능) |

---

## 부록 D: 폐기된 값 목록 (v1.2)

**사용 시 로드 실패 (Fail-loud)**

### Categories

| 폐기 값 | 대체 |
|---------|------|
| `Blade` | `SmallBlade`, `LongBlade` |
| `Thrown` | 수동 오버라이드 |

### Tags

| 폐기 값 | 대체 |
|---------|------|
| `Cookware` | `CoffeeMaker` 또는 Recipe Cooking+keep |
| `Medical` | `Medical = TRUE` 필드 사용 |
| `Tool` | 개별 도구 태그 사용 |
| `Weapon` | `Type = Weapon` 사용 |
| `Clothing` | `Type = Clothing` 사용 |
| `Food` | `Type = Food` 사용 |
| `Literature` | `Type = Literature` 사용 |

### CustomContextMenu

| 폐기 값 | 대체 |
|---------|------|
| `Disinfect` | `has("AlcoholPower")` 또는 `contains("Tags", "Disinfectant")` |
| `Bandage` | `eq("CanBandage", true)` |
| `Splint` | 수동 오버라이드 |
| `Stitch` | `contains("Tags", "SewingNeedle")` |
| `RemoveBullet` | `contains("Tags", "RemoveBullet")` |
| `RemoveGlass` | `contains("Tags", "RemoveGlass")` |
| `CleanWound` | 수동 오버라이드 |

### Recipe Category

| 폐기 값 | 대체 |
|---------|------|
| `MetalWelding` | `Welding` |
| `Masonry` | 바닐라 없음 |
| `Mechanics` | 바닐라 없음 |
| `Electronics` | `Electrical` |
| `Trapping` | `Trapper` |

### BodyLocation (v1.1 이전 값)

| 폐기 값 | 대체 |
|---------|------|
| `Head` | `Hat`, `FullHat`, `FullHelmet`, `Mask` 등 |
| `Torso` | `Shirt`, `Jacket`, `TorsoExtra` 등 |
| `Torso_Upper` | `Shirt`, `Tshirt`, `Sweater` 등 |
| `Torso_Lower` | `TorsoExtra` 등 |
| `Legs` | `Pants`, `Skirt`, `Legs1` |
| `Groin` | `Pants` 등으로 처리 |
| `Feet` | `Shoes`, `Socks` |
| `Back` | 폐기 (바닐라 확인 안 됨, Allowlist에 없음) → 사용 시 로드 실패. 6-F는 수동 오버라이드 대상 또는 `has_outcome("equip_back")` 사용 (v1.3) |
| `FannyPack` | `FannyPackFront`, `FannyPackBack` |
| `Waist` | `Belt` 등 |

---

## 부록 E: Context Outcome 허용값 목록 — v1.3 신규

**사용 가능한 Outcome 값**

| Outcome | 설명 | 분류 연결 |
|---------|------|-----------|
| `rip_clothing` | 찢어서 천 조각으로 변환 가능 | Wearable 보조 |
| `equip_primary` | 주무기 슬롯 장착 가능 | Combat 보조 |
| `equip_secondary` | 보조 슬롯 장착 가능 | Combat 보조 |
| `equip_back` | 등 슬롯 장착 가능 | Wearable.6-F |
| `place_world` | 월드에 배치 가능 | Tool.1-J 보조 |
| `fill_container` | 내용물 채우기 가능 | Resource 보조 |
| `empty_container` | 내용물 비우기 가능 | Resource 보조 |
| `toggle_activate` | 활성화/비활성화 토글 가능 | Tool.1-H 보조 |
| `read_literature` | 읽기 가능 | Literature 보조 |
| `eat_food` | 먹기 가능 | Consumable.3-A 보조 |
| `drink_beverage` | 마시기 가능 | Consumable.3-B 보조 |
| `apply_medical` | 의료 적용 가능 | Consumable.3-C 보조 |
| `smoke_item` | 흡연 가능 | Consumable.3-D 보조 |
| `insert_magazine` | 탄창 삽입 가능 | Combat.2-G/H/I 보조 |
| `attach_part` | 부품 장착 가능 | Combat.2-L 보조 |
| `disassemble` | 분해 가능 | Tool.1-B 보조 |
| `repair_item` | 수리 가능 | Tool.1-C 보조 |

**금지 패턴**

| 금지 | 이유 |
|------|------|
| `has_action("...")` | 행동명 사용 금지 |
| `menu_contains("...")` | 메뉴 문자열 사용 금지 |
| 런타임 `getContextMenu()` | 동적 판정 금지 |
