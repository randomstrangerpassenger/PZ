# Iris Combat(2) 소분류 증거표 (v0.2)

이 문서는 **Combat 대분류(2)**의 각 소분류별로 사용할 수 있는 증거를 정의한다.

> ⚠️ **v0.2 주요 변경**: Categories 허용값 수정 (`Blade` → `LongBlade`/`SmallBlade`), `Unarmed` 제외 처리, SubCategory 검증, 총기 14개 전수 확인

---

## 증거 우선순위 원칙

1. **1차**: Item Script 필드 (Type, Categories, SubCategory)
2. **2차**: TwoHandWeapon (장/단 구분)
3. **3차**: AmmoType (총기 세분류)

> ⚠️ **우선순위는 설명용이다.** 실제 판정은 **각 소분류의 증거 조건을 독립적으로 평가**하며, "먼저 매칭되면 나머지 무시" 같은 로직은 없다. 다중 태그가 기본이다.

---

## Combat 분류의 핵심 원칙

### 1차 증거는 Type + Categories

Combat 소분류는 **Item Script의 무기 분류 필드**를 1차 증거로 사용한다.

```
Type = Weapon (필수)
Categories = Axe / Blunt / SmallBlunt / LongBlade / SmallBlade / Spear (1차 분류)
TwoHandWeapon = exists/not exists (장/단 구분)
SubCategory = Firearm (총기 분류)
```

### Damage 필드는 분류 증거가 아님

`MaxDamage`, `MinDamage` 등 수치 필드는 **표시 정보로만** 사용.
분류 태그 부여의 근거로 사용 금지.

### Unarmed 제외

`Categories = Unarmed` (Base.BareHands)는 **Combat 분류 대상에서 제외**.
"맨손"은 아이템이 아니며, 분류 표시 의미 없음.

### 수동 오버라이드의 계층

**수동 오버라이드(`overrides_manual.lua`)는 자동 분류 엔진 바깥의 별도 레이어다.**

- 자동 분류 엔진은 Evidence Table에 "자동 분류 불가"로 명시된 소분류에 **절대 태그를 부여하지 않는다**
- 수동 오버라이드는 자동 분류 **이후** 병합되며, 자동 분류 결과를 **대체하지 않고 추가**한다
- Evidence Table 문서 내 "수동 오버라이드 대상" 목록은 **참고용**이며, 실제 데이터는 `overrides_manual.lua`에서 관리한다

---

## 바닐라 데이터 요약 (v0.2)

| 항목 | 값 |
|------|-----|
| Type=Weapon 총 개수 | 162개 |
| SubCategory=Firearm | 14개 (권총 6, 소총 4, 산탄총 4) |
| MountOn 있음 (총기부품) | 14개 |
| Categories 종류 | Axe(5), Blunt(40), SmallBlunt(25), Spear(20), SmallBlade(18), LongBlade(2), Improvised(56), Unarmed(1) |

---

## 2-A. 도끼류 (Axe)

**핵심 질문**: 도끼 스킬을 사용하는 무기인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** Categories | `contains "Axe"` | 필수 |

### 바닐라 현황

- 총 5개 아이템
- 예: `Base.Axe`, `Base.AxeStone`, `Base.HandAxe`, `Base.WoodAxe`

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| MaxDamage 수치 비교 | 수치 비교 금지 |

### 참고

도끼는 **Tool.1-E(농업/채집 — 벌목)**와 다중 태그 가능.

---

## 2-B. 장둔기 (Long Blunt)

**핵심 질문**: 양손 둔기인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** Categories | `contains "Blunt"` | 필수 |
| **AND** TwoHandWeapon | `exists` (= TRUE) | 양손 = 장둔기 |

> ⚠️ **바닐라 데이터 기준**: `TwoHandWeapon = TRUE`만 존재하고, 한손 무기는 필드 자체가 없음.  
> 따라서 `TwoHandWeapon exists` = 양손(장둔기), `not exists` = 한손(단둔기)로 구분.

### 바닐라 현황

- Blunt + TwoHandWeapon: **39개**
- 예: 야구방망이, 쇠파이프, 골프채

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| SubCategory | `= "Swinging"` | 바닐라에서 확인된 값 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| MaxDamage 수치 비교 | 수치 비교 금지 |
| SubCategory = "Smashing" | 바닐라에 없는 값 |

---

## 2-C. 단둔기 (Short Blunt)

**핵심 질문**: 한손 둔기인가?

### 필수 증거 (AND 결합) — 방법 1

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** Categories | `contains "Blunt"` | 필수 |
| **AND** TwoHandWeapon | `not exists` | 한손 = 단둔기 |

### 필수 증거 — 방법 2 (SmallBlunt 직접 사용)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** Categories | `contains "SmallBlunt"` | SmallBlunt 직접 사용 |

> ℹ️ **v0.2 발견**: `SmallBlunt` 카테고리가 독립적으로 존재 (25개).  
> `Blunt + not TwoHandWeapon` (26개)과 거의 일치하나, 완전히 동일하지는 않음.  
> **양쪽 방법 모두 허용** (OR 결합).

### 바닐라 현황

- Blunt - TwoHandWeapon: **26개**
- SmallBlunt: **25개**
- 예: 프라이팬, 망치, 렌치

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| MaxDamage 수치 비교 | 수치 비교 금지 |

### 참고

프라이팬은 **Tool.1-D(조리)**와 다중 태그.
망치/렌치는 **Tool.1-A(건설/제작)** 또는 **Tool.1-C(정비)**와 다중 태그 가능.

---

## 2-D. 장검류 (Long Blade)

**핵심 질문**: 장검 스킬을 사용하는 무기인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** Categories | `contains "LongBlade"` | 필수 |

> ⚠️ **v0.2 변경**: `Blade + TwoHandWeapon` 대신 **`LongBlade` 직접 사용**.  
> 바닐라에 `Blade` 카테고리는 없고, `LongBlade`와 `SmallBlade`만 존재.

### 바닐라 현황

- LongBlade: **2개**
- 예: `Base.Katana`, `Base.Machete`

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| SubCategory | `= "Stab"` | 바닐라에서 확인 |
| TwoHandWeapon | `exists` | Katana만 해당, Machete는 없음 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| Categories = "Blade" | 바닐라에 없는 값 |

---

## 2-E. 단검류 (Short Blade)

**핵심 질문**: 단검 스킬을 사용하는 무기인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** Categories | `contains "SmallBlade"` | 필수 |

> ⚠️ **v0.2 변경**: `Blade + not TwoHandWeapon` 대신 **`SmallBlade` 직접 사용**.

### 바닐라 현황

- SmallBlade: **18개**
- 예: 부엌칼, 사냥칼, 스크류드라이버

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| SubCategory | `= "Stab"` | 바닐라에서 확인 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| Categories = "Blade" | 바닐라에 없는 값 |

### 참고

스크류드라이버는 **Tool.1-B(분해)**, **Tool.1-C(정비)**와 다중 태그.

---

## 2-F. 창류 (Spear)

**핵심 질문**: 창 스킬을 사용하는 무기인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** Categories | `contains "Spear"` | 필수 |

### 바닐라 현황

- Spear: **20개**
- 예: 창, 제작 창, 각종 즉석 창

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| SubCategory | `= "Spear"` | 바닐라에서 확인 (15개) |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |

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

| 허용값 | 바닐라 총기 |
|--------|-------------|
| `Base.Bullets9mm` | Pistol |
| `Base.Bullets45` | Pistol2, Revolver |
| `Base.Bullets44` | Pistol3, Revolver_Long |
| `Base.Bullets38` | Revolver_Short |

### 바닐라 현황

- 권총: **6개**
- 모두 `TwoHandWeapon = FALSE` (한손)

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| SubCategory = "Handgun" | 바닐라에 없는 값 |
| TwoHandWeapon 단독 | 총기 분류는 AmmoType으로 |

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

| 허용값 | 바닐라 총기 |
|--------|-------------|
| `Base.223Bullets` | VarmintRifle |
| `Base.308Bullets` | HuntingRifle, AssaultRifle2 |
| `Base.556Bullets` | AssaultRifle |

### 바닐라 현황

- 소총: **4개**
- 모두 `TwoHandWeapon = TRUE` (양손)

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| SubCategory = "Rifle" | 바닐라에 없는 값 |

---

## 2-I. 산탄총 (Shotgun)

**핵심 질문**: 산탄총류 총기인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Weapon` | 필수 |
| **AND** SubCategory | `= "Firearm"` | 필수 |
| **AND** AmmoType | `= "Base.ShotgunShells"` | 산탄 탄약 |

### 바닐라 현황

- 산탄총: **4개**
- Shotgun, DoubleBarrelShotgun, DoubleBarrelShotgunSawnoff, ShotgunSawnoff
- 모두 `TwoHandWeapon = TRUE` (양손)

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| SubCategory = "Shotgun" | 바닐라에 없는 값 |

---

## 2-J. 투척/폭발 (Thrown/Explosive)

**핵심 질문**: 투척하거나 폭발하는 무기인가?

### 필수 증거

**없음** — 자동 분류 불가

### 처리 방식

**자동 분류 엔진은 이 소분류에 태그를 부여하지 않는다.**

해당 아이템은 분류 엔진 **바깥**의 별도 레이어(`overrides_manual.lua`)에서 처리한다.
수동 오버라이드는 자동 분류 결과와 **병합**되며, 자동 분류를 대체하지 않는다.

**수동 오버라이드 대상 (참고용):**
- `Base.Molotov`
- `Base.PipeBomb`
- `Base.SmokeBomb`

### 이유

- `Categories = Thrown` 바닐라에 **없음**
- 몰로토프는 `SwingAnim = Throw`로 되어 있으나 Allowlist 외 필드
- `DisplayCategory = Explosives`는 **금지 증거**

---

## 2-K. 탄약 (Ammunition)

**핵심 질문**: 총기에 사용되는 탄약인가?

### 필수 증거

**없음** — 자동 분류 불가

### 처리 방식

**자동 분류 엔진은 이 소분류에 태그를 부여하지 않는다.**

해당 아이템은 분류 엔진 **바깥**의 별도 레이어(`overrides_manual.lua`)에서 처리한다.
수동 오버라이드는 자동 분류 결과와 **병합**되며, 자동 분류를 대체하지 않는다.

**수동 오버라이드 대상 (참고용):**
- 권총 탄약: `Base.Bullets9mm`, `Base.Bullets45`, `Base.Bullets44`, `Base.Bullets38`
- 소총 탄약: `Base.223Bullets`, `Base.308Bullets`, `Base.556Bullets`
- 산탄: `Base.ShotgunShells`

### 이유

- `Type = Ammo` 바닐라에 **없음**
- 탄약 아이템은 `Type = Normal` + `DisplayCategory = Ammo`
- `DisplayCategory`는 **금지 증거**

---

## 2-L. 총기부품 (Firearm Parts)

**핵심 질문**: 총기에 장착하는 부품/액세서리인가?

### 필수 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| MountOn | `exists` | 장착 가능 부품 |

### 바닐라 현황

- MountOn 있는 아이템: **14개**
- 예: IronSight, x2Scope, x4Scope, x8Scope, AmmoStraps, Sling, RecoilPad, RedDot, Laser, Choke, FiberglassStock, GunLight

### MountOn 허용값 (참고)

```
HuntingRifle, VarmintRifle, Pistol, Pistol2, Pistol3, 
Revolver, Revolver_Long, AssaultRifle, AssaultRifle2, Shotgun
```

> ⚠️ **MountOn exists가 핵심 증거**: 총기 부품은 반드시 `MountOn` 필드가 있음.

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| Type = WeaponPart 단독 | 범용적이라 오분류 위험 |

---

## 다중 태그 처리 예시

### 프라이팬 (Frying Pan)

```
증거:
- Recipe keep+Cooking → Tool.1-D ✓
- Type = Weapon, Categories = SmallBlunt → Combat.2-C ✓

결과: [Tool.1-D, Combat.2-C]
```

### 스크류드라이버 (Screwdriver)

```
증거:
- Moveables.ToolDefinition.itemId = "Base.Screwdriver" → Tool.1-B ✓
- Type = Weapon, Categories = SmallBlade → Combat.2-E ✓

결과: [Tool.1-B, Combat.2-E]
```

### 도끼 (Axe)

```
증거:
- Tags contains "ChopTree" → Tool.1-E ✓
- Type = Weapon, Categories = Axe → Combat.2-A ✓

결과: [Tool.1-E, Combat.2-A]
```

### 망치 (Hammer)

```
증거:
- Recipe role = keep, category = Carpentry → Tool.1-A ✓
- Moveables.ToolDefinition → Tool.1-B ✓
- Type = Weapon, Categories = SmallBlunt → Combat.2-C ✓

결과: [Tool.1-A, Tool.1-B, Combat.2-C]
```

---

## 바닐라 데이터 확인 결과 (v0.2)

| 항목 | 확인 결과 | 영향 |
|------|-----------|------|
| Categories 값 | `Axe`, `Blunt`, `SmallBlunt`, `LongBlade`, `SmallBlade`, `Spear`, `Improvised`, `Unarmed` | `Blade` 폐기, 세분화된 값 사용 |
| SubCategory 값 | `Swinging`(79), `Stab`(20), `Spear`(15), `Firearm`(14) | 4개만 존재 |
| TwoHandWeapon | TRUE만 존재 (72개), 없으면 한손 (90개) | exists/not exists로 구분 |
| Type = Ammo | **없음** | 2-K 수동 오버라이드 |
| Categories = Thrown | **없음** | 2-J 수동 오버라이드 |
| MountOn 필드 | **14개 존재** | 2-L 자동 분류 가능 |
| IsAimedFirearm | **0개** (필드 미사용) | 보조 증거에서 제외 |

### 확인된 Categories 값 (v0.2 최종)

| Category | 개수 | 분류 연결 |
|----------|------|-----------|
| `Axe` | 5 | 2-A |
| `Blunt` | 40 | 2-B/2-C (TwoHandWeapon으로 구분) |
| `SmallBlunt` | 25 | 2-C |
| `LongBlade` | 2 | 2-D |
| `SmallBlade` | 18 | 2-E |
| `Spear` | 20 | 2-F |
| `Improvised` | 56 | 보조 태그 (단독 분류 기준 아님) |
| `Unarmed` | 1 | 제외 (맨손) |

### 확인된 AmmoType 값 (v0.2 최종)

| AmmoType | 총기 수 | 분류 |
|----------|---------|------|
| `Base.Bullets9mm` | 1 | 권총 (2-G) |
| `Base.Bullets45` | 2 | 권총 (2-G) |
| `Base.Bullets44` | 2 | 권총 (2-G) |
| `Base.Bullets38` | 1 | 권총 (2-G) |
| `Base.223Bullets` | 1 | 소총 (2-H) |
| `Base.308Bullets` | 2 | 소총 (2-H) |
| `Base.556Bullets` | 1 | 소총 (2-H) |
| `Base.ShotgunShells` | 4 | 산탄총 (2-I) |

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | — | 초안 작성 |
| 0.2 | 2026-01-24 | Categories 허용값 전면 개정 (`Blade` → `LongBlade`/`SmallBlade`), `Unarmed` 제외, `IsAimedFirearm` 미사용 확인, 바닐라 데이터 전수 검증 |
