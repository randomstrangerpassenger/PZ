# Iris Combat(2) 소분류 증거표

이 문서는 **Combat 대분류(2)**의 각 소분류별로 사용할 수 있는 증거를 정의한다.

---

## 증거 우선순위 원칙

1. **1차**: Item Script 필드 (Type, Categories, SubCategory)
2. **2차**: AmmoType / 탄약 관련 필드
3. **3차**: Tags (허용 목록 내)
4. **최후**: 수동 오버라이드 (증거 누락 시에만)

---

## Combat 분류의 핵심 원칙

### 1차 증거는 Type + Categories + SubCategory

Combat 소분류는 **Item Script의 무기 분류 필드**를 1차 증거로 사용한다.

```
Type = Weapon
Categories = Blunt / Blade / Axe / Spear / Firearm / Thrown
SubCategory = Smashing / Stabbing / ...
```

### Damage 필드는 분류 증거가 아님

`MaxDamage`, `MinDamage` 등 수치 필드는 **표시 정보로만** 사용.
분류 태그 부여의 근거로 사용 금지.

---

## 2-A. 도끼류 (Axe)

**핵심 질문**: 도끼 스킬을 사용하는 무기인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** Categories | `contains "Axe"` | 필수 |

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| SubCategory | 세부 분류 | 표시 정보 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| MaxDamage 수치 비교 | 수치 비교 금지 |

### 예시 아이템

- 손도끼 (Hand Axe)
- 소방도끼 (Fire Axe)
- 돌도끼 (Stone Axe)

### 참고

도끼는 **Tool.1-E(농업/채집 — 벌목)**와 다중 태그 가능.

---

## 2-B. 장둔기 (Long Blunt)

**핵심 질문**: Long Blunt 스킬을 사용하는 무기인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** Categories | `contains "Blunt"` | 필수 |
| **AND** TwoHandWeapon | `exists` (= TRUE) | 양손 = 장둔기 |

> ⚠️ **바닐라 데이터 기준**: `TwoHandWeapon = TRUE`만 존재하고, 한손 무기는 필드 자체가 없음.  
> 따라서 `TwoHandWeapon exists` = 양손(장둔기), `not exists` = 한손(단둔기)로 구분.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| SubCategory | `= "Swinging"` | 바닐라에서 확인된 값 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| MaxDamage 수치 비교 | 수치 비교 금지 |
| 길이/크기 수치 비교 | 수치 비교 금지 |
| SubCategory = "Smashing" 등 | 바닐라에 없는 값 |

### 예시 아이템

- 야구방망이 (Baseball Bat)
- 쇠파이프 (Metal Pipe)
- 골프채 (Golf Club)

---

## 2-C. 단둔기 (Short Blunt)

**핵심 질문**: Short Blunt 스킬을 사용하는 무기인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** Categories | `contains "Blunt"` | 필수 |
| **AND** TwoHandWeapon | `not exists` | 한손 = 단둔기 |

> ⚠️ **바닐라 데이터 기준**: 한손 무기는 `TwoHandWeapon` 필드가 없음.  
> `TwoHandWeapon not exists` = 한손(단둔기)로 판정.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| SubCategory | `= "Swinging"` | 있으면 보조 확인 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| MaxDamage 수치 비교 | 수치 비교 금지 |
| SubCategory = "Smashing" 등 | 바닐라에 없는 값 |

### 예시 아이템

- 프라이팬 (Frying Pan)
- 망치 (Hammer)
- 렌치 (Wrench)

### 참고

프라이팬은 **Tool.1-D(조리)**와 다중 태그.
망치/렌치는 **Tool.1-A(건설/제작)** 또는 **Tool.1-C(정비)**와 다중 태그 가능.

---

## 2-D. 장검류 (Long Blade)

**핵심 질문**: Long Blade 스킬을 사용하는 무기인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** Categories | `contains "Blade"` | 필수 |
| **AND** TwoHandWeapon | `exists` (= TRUE) | 양손 = 장검류 |

> ⚠️ **바닐라 데이터 기준**: Blade 카테고리 내에서 `TwoHandWeapon exists` = 장검류로 구분.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| SubCategory | `= "Stab"` | 바닐라에서 확인된 값 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| 블레이드 길이 수치 비교 | 수치 비교 금지 |
| SubCategory = "Slashing" 등 | 바닐라에 없는 값 |

### 예시 아이템

- 카타나 (Katana)
- 마체테 (Machete)

---

## 2-E. 단검류 (Short Blade)

**핵심 질문**: Short Blade 스킬을 사용하는 무기인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** Categories | `contains "Blade"` | 필수 |
| **AND** TwoHandWeapon | `not exists` | 한손 = 단검류 |

> ⚠️ **바닐라 데이터 기준**: 한손 무기는 `TwoHandWeapon` 필드가 없음.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| SubCategory | `= "Stab"` | 바닐라에서 확인된 값 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| SubCategory = "Stabbing" 등 | 바닐라에 없는 값 |

### 예시 아이템

- 부엌칼 (Kitchen Knife)
- 사냥칼 (Hunting Knife)
- 스크류드라이버 (Screwdriver) — 무기로 사용 시

### 참고

스크류드라이버는 **Tool.1-B(분해)**, **Tool.1-C(정비)**와 다중 태그.

---

## 2-F. 창류 (Spear)

**핵심 질문**: Spear 스킬을 사용하는 무기인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** Categories | `contains "Spear"` | 필수 |

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| SubCategory | 세부 분류 | 표시 정보 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |

### 예시 아이템

- 창 (Spear)
- 제작 창 (Crafted Spear)

---

## 2-G. 권총 (Handgun)

**핵심 질문**: 권총류 총기인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** SubCategory | `= "Firearm"` | 필수 |
| **AND** AmmoType | 권총 탄약 allowlist | 아래 참조 |

### AmmoType Allowlist (권총)

| 허용값 | 설명 |
|--------|------|
| `Base.Bullets9mm` | 9mm |
| `Base.Bullets45` | .45 |
| `Base.Bullets44` | .44 |
| `Base.Bullets38` | .38 |

> ⚠️ **바닐라 데이터 기준**: `SubCategory = "Handgun"` 같은 값은 없음.  
> 권총/소총/산탄총 구분은 **AmmoType**으로만 가능.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| IsAimedFirearm | `= true` | 총기 확인 |
| TwoHandWeapon | `not exists` | 한손 총기 (보조) |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| 사거리/정확도 수치 비교 | 수치 비교 금지 |
| SubCategory = "Handgun" | 바닐라에 없는 값 |

### 예시 아이템

- M1911
- M9 Pistol
- Revolver

---

## 2-H. 소총 (Rifle)

**핵심 질문**: 소총류 총기인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** SubCategory | `= "Firearm"` | 필수 |
| **AND** AmmoType | 소총 탄약 allowlist | 아래 참조 |

### AmmoType Allowlist (소총)

| 허용값 | 설명 |
|--------|------|
| `Base.223Bullets` | .223 |
| `Base.308Bullets` | .308 |
| `Base.556Bullets` | 5.56mm |

> ⚠️ **바닐라 데이터 기준**: `SubCategory = "Rifle"` 같은 값은 없음.  
> 소총 구분은 **AmmoType**으로만 가능.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| IsAimedFirearm | `= true` | 총기 확인 |
| TwoHandWeapon | `exists` | 양손 총기 (보조) |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| SubCategory = "Rifle" | 바닐라에 없는 값 |

### 예시 아이템

- 사냥소총 (Hunting Rifle)
- Assault Rifle
- Varmint Rifle

---

## 2-I. 산탄총 (Shotgun)

**핵심 질문**: 산탄총류 총기인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** SubCategory | `= "Firearm"` | 필수 |
| **AND** AmmoType | 산탄 탄약 allowlist | 아래 참조 |

### AmmoType Allowlist (산탄총)

| 허용값 | 설명 |
|--------|------|
| `Base.ShotgunShells` | 산탄 |

> ⚠️ **바닐라 데이터 기준**: `SubCategory = "Shotgun"` 같은 값은 없음.  
> 산탄총 구분은 **AmmoType**으로만 가능.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| IsAimedFirearm | `= true` | 총기 확인 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| SubCategory = "Shotgun" | 바닐라에 없는 값 |

### 예시 아이템

- JS-2000
- 더블배럴 샷건 (Double Barrel Shotgun)

---

## 2-J. 투척/폭발 (Thrown/Explosive)

**핵심 질문**: 투척하거나 폭발하는 무기인가?

### 필수 증거

**없음** — 자동 분류 불가

### 처리 방식

**수동 오버라이드로만 처리**

```lua
manualOverrides = {
    -- 몰로토프: Categories=Thrown 없음, SwingAnim=Throw + DisplayCategory=Explosives
    ["Base.Molotov"] = { add = { "Combat.2-J" } },
    
    -- 파이프폭탄
    ["Base.PipeBomb"] = { add = { "Combat.2-J" } },
    
    -- 연막탄
    ["Base.SmokeBomb"] = { add = { "Combat.2-J" } },
}
```

### 이유

바닐라 데이터 기준:
- `Categories = Thrown` 같은 필드가 **없음**
- 몰로토프는 `SwingAnim = Throw` + `DisplayCategory = Explosives`로 되어 있음
- `SwingAnim`은 현재 Allowlist에 없음
- `DisplayCategory`는 **금지 증거**

> ⚠️ **SwingAnim 증거 추가 검토 가능**: `SwingAnim = Throw`를 Allowlist에 추가하면 자동 분류 가능해짐.  
> 단, 이 경우 투척 무기만 잡히고 폭발물 전체를 커버하진 못함.

### 예시 아이템

- 몰로토프 칵테일 (Molotov Cocktail)
- 파이프폭탄 (Pipe Bomb)
- 연막탄 (Smoke Bomb)

---

## 2-K. 탄약 (Ammunition)

**핵심 질문**: 총기에 사용되는 탄약인가?

### 필수 증거

**자동 분류 어려움** — 아래 대안 참조

### 바닐라 데이터 현실

- `Type = Ammo`는 **존재하지 않음**
- 탄약 아이템은 `Type = Normal` + `DisplayCategory = Ammo`로 되어 있음
- `DisplayCategory`는 **금지 증거**

### 대안 1: 역참조 (구현 복잡도 높음)

| 증거 | 조건 | 비고 |
|------|------|------|
| 다른 무기의 AmmoType | 이 아이템의 FullType을 참조 | 역참조 |

예: `Base.Bullets9mm`은 권총들의 `AmmoType = Base.Bullets9mm`으로 참조됨.

> ⚠️ **구현 난이도**: Evidence 수집 단계에서 "어떤 무기가 이 아이템을 AmmoType으로 참조하는가"를 역으로 추적해야 함.

### 대안 2: 수동 오버라이드 (권장)

```lua
manualOverrides = {
    -- 9mm 탄약
    ["Base.Bullets9mm"] = { add = { "Combat.2-K" } },
    ["Base.Bullets45"] = { add = { "Combat.2-K" } },
    ["Base.Bullets44"] = { add = { "Combat.2-K" } },
    ["Base.Bullets38"] = { add = { "Combat.2-K" } },
    
    -- 소총 탄약
    ["Base.223Bullets"] = { add = { "Combat.2-K" } },
    ["Base.308Bullets"] = { add = { "Combat.2-K" } },
    ["Base.556Bullets"] = { add = { "Combat.2-K" } },
    
    -- 산탄
    ["Base.ShotgunShells"] = { add = { "Combat.2-K" } },
}
```

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| DisplayCategory = Ammo | 금지 증거 |
| Type = Ammo | 바닐라에 없는 값 |

### 예시 아이템

- 9mm 탄약 (Base.Bullets9mm)
- 산탄 (Base.ShotgunShells)
- .308 탄약 (Base.308Bullets)

---

## 2-L. 총기부품 (Firearm Parts)

**핵심 질문**: 총기에 장착하는 부품/액세서리인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 | 비고 |
|------|------|------|
| MountOn | `exists` | 장착 가능 부품 |

### MountOn 허용값 (바닐라 확인됨)

총기 부품의 `MountOn` 필드에 등장하는 값:

| 허용값 | 설명 |
|--------|------|
| `AssaultRifle`, `AssaultRifle2` | 돌격소총 |
| `HuntingRifle`, `VarmintRifle` | 사냥/버민트 소총 |
| `Shotgun` | 산탄총 |
| `Pistol`, `Pistol2`, `Pistol3` | 권총 |
| `Revolver`, `Revolver_Long` | 리볼버 |

> ⚠️ **MountOn exists가 핵심 증거**: 총기 부품은 반드시 `MountOn` 필드가 있음.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Fixing role | 총기 Fixing에서 참조 | 보조 확인 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |

### 예시 아이템

- 조준경 (Scope)
- 소음기 (Suppressor)
- 확장 탄창 (Extended Magazine)
- 레이저 사이트 (Laser Sight)

---

## 다중 태그 처리 예시

### 프라이팬 (Frying Pan)

```
증거:
- Tags contains "Cookware" → Tool.1-D ✓
- Type = Weapon, Categories = Blunt, SubCategory = Smashing → Combat.2-C ✓

결과: [Tool.1-D, Combat.2-C]
```

### 스크류드라이버 (Screwdriver)

```
증거:
- Moveables.ToolDefinition.itemId = "Base.Screwdriver" → Tool.1-B ✓
- Fixing.Fixer (총기 개조) → Tool.1-C ✓
- Type = Weapon, Categories = Blade, SubCategory = Stabbing → Combat.2-E ✓

결과: [Tool.1-B, Tool.1-C, Combat.2-E]
```

### 도끼 (Axe)

```
증거:
- Recipe role = keep, category = Farming → Tool.1-E ✓
- Type = Weapon, Categories = Axe → Combat.2-A ✓

결과: [Tool.1-E, Combat.2-A]
```

### 망치 (Hammer)

```
증거:
- Recipe role = keep, category = Carpentry → Tool.1-A ✓
- Moveables.ToolDefinition → Tool.1-B ✓
- Type = Weapon, Categories = Blunt, TwoHandWeapon = false → Combat.2-C ✓

결과: [Tool.1-A, Tool.1-B, Combat.2-C]
```

---

## 바닐라 데이터 확인 결과

| 항목 | 확인 결과 | 영향 |
|------|-----------|------|
| SubCategory 값 목록 | `Swinging`, `Stab`, `Spear`, `Firearm` 4개만 | 장/단 구분에 SubCategory 사용 불가 |
| TwoHandWeapon 필드 | `TRUE`만 존재, 없으면 한손 | exists/not exists로 장/단 구분 |
| Type = Ammo | **없음** (Type=Normal 사용) | 2-K 수동 오버라이드 |
| 폭발물 분류 | Categories=Thrown 없음, SwingAnim=Throw | 2-J 수동 오버라이드 |
| MountOn 필드 | **존재함** | 2-L 자동 분류 가능 |
| AmmoType 값 목록 | 8개 확인 | 2-G/2-H/2-I AmmoType으로 구분 |

### 확인된 AmmoType 값

| AmmoType | 총기 분류 |
|----------|-----------|
| `Base.Bullets9mm` | 권총 (2-G) |
| `Base.Bullets45` | 권총 (2-G) |
| `Base.Bullets44` | 권총 (2-G) |
| `Base.Bullets38` | 권총 (2-G) |
| `Base.223Bullets` | 소총 (2-H) |
| `Base.308Bullets` | 소총 (2-H) |
| `Base.556Bullets` | 소총 (2-H) |
| `Base.ShotgunShells` | 산탄총 (2-I) |

### 확인된 SubCategory 값 (무기)

| SubCategory | 용도 |
|-------------|------|
| `Swinging` | 둔기류 보조 확인 |
| `Stab` | 검류 보조 확인 |
| `Spear` | 창류 |
| `Firearm` | 총기류 |

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | - | 초안 작성 |
