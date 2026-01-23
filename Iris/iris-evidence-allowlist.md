# Iris Evidence Allowlist

이 문서는 Iris 자동 분류 시스템에서 **허용되는 증거(Evidence)**를 정의한다.  
여기에 명시되지 않은 증거는 분류 규칙에서 사용할 수 없다.

---

## 핵심 원칙

1. **추론 금지** — 아이템 이름, DisplayName, 설명 문자열에서 의미를 추론하지 않는다
2. **판단 금지** — 수치의 크기, 수준, 효율을 비교하지 않는다
3. **누적만 허용** — 태그는 추가만, 제거/선택/우선순위 없음
4. **목록 외 금지** — 이 문서에 없는 증거 소스는 사용 불가

---

## 1. 허용 증거 소스

### 1-1. Item Script 필드

아이템 스크립트(`.txt`)에서 직접 참조 가능한 필드 목록.

#### 분류용 필드 (Classification)

| 필드명 | 타입 | 용도 | 예시 |
|--------|------|------|------|
| `Type` | enum | 아이템 기본 타입 | `Weapon`, `Food`, `Literature`, `Clothing`, `Drainable`, `Radio` |
| `Categories` | string | 무기 카테고리 | `Blunt`, `Blade`, `Firearm` |
| `SubCategory` | string | 무기 세부 카테고리 | `Swinging`, `Stab`, `Spear`, `Firearm` |
| `BodyLocation` | string | 착용 부위 | `Head`, `Torso`, `Hands`, `Legs`, `Feet` |
| `AmmoType` | string | 탄약 타입 | `9mm`, `Shotgun`, `.308` |

#### 무기 세부 분류 필드 (Weapon Detail)

| 필드명 | 타입 | 용도 | 분류 연결 |
|--------|------|------|-----------|
| `TwoHandWeapon` | boolean | 양손 무기 여부 | 장/단 무기 구분 — exists=장, not exists=단 |
| `IsAimedFirearm` | boolean | 조준 총기 여부 | 총기 확인 (보조) |
| `MountOn` | string | 장착 가능 총기 | 2-L(총기부품) — exists가 핵심 증거 |

> ⚠️ **TwoHandWeapon 특이사항**: 바닐라에서 `TRUE`만 존재하고, 한손 무기는 필드 자체가 없음.  
> 따라서 `exists` = 양손(장무기), `not exists` = 한손(단무기)로 구분.

> ⚠️ **MountOn**: 총기 부품의 핵심 증거. 값 비교가 아닌 `exists` 여부로 2-L 판정.
| `Tags` | string[] | 아이템 태그 | `Cookware`, `Medical`, `Tool` |

> ⚠️ **Tags 정의**: `Tags`는 **Item Script에 명시적으로 선언된 태그 문자열만**을 의미한다.  
> 런타임에서 파생/추론된 태그는 사용 불가.

#### 광원/점화 필드 (Light/Fire)

| 필드명 | 타입 | 용도 | 분류 연결 |
|--------|------|------|-----------|
| `LightStrength` | number | 광원 강도 | 1-H(광원) — exists만 허용, 수치 비교 금지 |
| `LightDistance` | number | 광원 거리 | 1-H(광원) — exists만 허용, 수치 비교 금지 |
| `TorchCone` | boolean | 손전등형 광원 | 1-H(광원) |

> ⚠️ **광원 필드 제한**: `LightStrength`, `LightDistance`는 **exists 여부만** 분류 증거로 사용.  
> 수치 비교(`> 0.5` 등)는 금지.

#### 행동 연결 필드 (Action-Indicating)

| 필드명 | 타입 | 나타내는 행동 | 분류 연결 |
|--------|------|---------------|-----------|
| `CustomContextMenu` | string | 컨텍스트 메뉴 액션 | 3-C(의약품): `Disinfect` |
| `TeachedRecipes` | string[] | 레시피 해금 | 5-B(레시피잡지) |
| `CanStoreWater` | boolean | 물 저장 가능 | 1-D(조리) 보조 |
| `Alcoholic` | boolean | 알코올 여부 | 3-D(기호품) |
| `IsLiterature` | boolean | 읽기 가능 여부 | 5(Literature) 대분류 |
| `ActivatedItem` | boolean | 활성화/토글 가능 | 1-H(광원/점화) 보조 |
| `TwoWay` | boolean | 양방향 송수신 | 1-I(통신) — 워키토키 구분 |

> ⚠️ **ActivatedItem 정의**: "활성화 가능"이라는 UI 속성의 존재를 나타냄.  
> "행동"을 추론하는 것이 아니라, 토글 UI가 존재하는지의 사실.

> ⚠️ **TwoWay 정의**: Radio 타입 아이템의 양방향 송수신 속성.  
> "통신 가능" 판단이 아니라, 속성의 존재/값으로만 사용.

> ⚠️ **Literature 분류 우선순위**:  
> - 1순위: `Type = Literature`  
> - 보조: `IsLiterature = true` (모드 호환용)

#### 상태/수치 필드 (Display Only)

이 필드들은 **분류 증거로 사용 불가**. UI 표시 정보로만 사용.

| 필드명 | 용도 |
|--------|------|
| `MaxDamage`, `MinDamage` | 전투 상세 패널 표시 |
| `HungerChange`, `ThirstChange` | 소비 상세 패널 표시 |
| `StressChange`, `UnhappyChange` | 소비 상세 패널 표시 |
| `Weight` | 일반 정보 표시 |
| `UseDelta` | 소모품 잔량 표시 |

---

### 1-2. Recipe 관계

아이템이 레시피에서 어떤 역할로 참조되는지.

#### 허용 Role

| Role | 설명 | 분류 연결 예시 |
|------|------|----------------|
| `input` | 재료로 소모됨 | 4(Resource) |
| `output` | 결과물로 생성됨 | (분류 아닌 역참조용) |
| `keep` | 도구로 사용, 소모 안 됨 | 1(Tool) |
| `require` | 필수 도구 | 1(Tool) |

> ⚠️ **output role 제한**: `output` role은 **분류 태그를 추가하는 증거로 사용하지 않는다.**  
> Iris 메뉴의 "연결된 제작 결과" 표시 용도로만 사용한다.

#### Recipe.GetItemTypes 그룹

레시피에서 `[Recipe.GetItemTypes.X]` 형태로 참조되는 아이템 그룹.

| 그룹명 | 설명 | 분류 연결 |
|--------|------|-----------|
| `CanOpener` | 캔따개류 | 1-B(분해/개방) |

> ⚠️ **Tags와 구분**: `CanOpener`는 Item Script의 Tags가 아니라 Recipe.GetItemTypes 그룹 증거다.  
> Tags allowlist와 혼용하지 않는다.

#### 보조 힌트 (Optional)

| 속성 | 용도 | 주의 |
|------|------|------|
| `category` | 레시피 카테고리 | **1순위 증거로 사용 금지**, role과 조합 시 보조로만 |

> ℹ️ **Recipe Category 활용**: `Category:<Skill>` 형태로 존재 (예: `Category:Carpentry`, `Category:Cooking`).  
> 1-A(건설/제작), 1-C(정비), 1-D(조리) 등 Tool 소분류 구분 시 **보조 힌트**로 사용 가능.  
> 단, role(keep/require) 없이 category만으로 분류하는 것은 금지.

---

### 1-3. Fixing 관계

아이템이 수리/개조 시스템에서 어떤 역할로 참조되는지.

| Role | 설명 | 분류 연결 |
|------|------|-----------|
| `Fixer` | 수리 도구 | 1-C(정비) |
| `FixerSkill` | 필요 스킬 | (표시 정보) |

---

### 1-4. Moveables 관계 (Lua)

가구/오브젝트 분해(Dismantle) 시스템에서 도구로 참조되는지.

소스 파일: `ISMoveableDefinitions.lua`

#### 허용 증거

| 증거 타입 | 형식 | 설명 | 예시 |
|-----------|------|------|------|
| `Moveables.ToolDefinition.itemId` | `Base.*` | 분해 도구로 등록된 아이템 ID | `Base.Screwdriver`, `Base.Hammer` |
| `Moveables.ToolDefinition.moveablesTag` | `MoveablesTag.*` | 분해 도구로 등록된 태그 | `MoveablesTag.Crowbar`, `MoveablesTag.SharpKnife` |

> ⚠️ **네임스페이스 분리**: 
> - `Moveables.ToolDefinition.itemId`: `Base.*` 형태의 아이템 ID 매칭
> - `Moveables.ToolDefinition.moveablesTag`: `MoveablesTag.*` 형태의 별도 네임스페이스
> 
> **Item Script `Tags`와 완전히 다른 세계**. 혼용 금지.

> ⚠️ **MoveablesTag 격리**: Moveables의 `Tag.*` 토큰은 Item Script의 `Tags`와 **별도 취급**한다.  
> Item Script `Tags` allowlist와 혼용하지 않으며, 별도 MoveablesTag allowlist로 관리한다.

#### MoveablesTag 허용값 목록

새로운 값 추가 시 이 문서 개정 필요.

| 허용값 |
|--------|
| `Crowbar` |
| `SharpKnife` |
| `Hammer` |
| `Screwdriver` |
| `Saw` |
| `Wrench` |

> ℹ️ **분류 연결**: Moveables.ToolDefinition에 등록된 아이템은 **1-B(분해/개방)** 태그 후보.

---

## 2. 필드 연산 규칙

### 2-1. `exists` 연산

필드 존재 여부 확인.

**규칙: 단독 사용 금지, 반드시 Type 가드와 함께**

```
// ❌ 금지
{ field = "ThirstChange", exists = true }

// ✅ 허용
{ field = "Type", equals = "Food" }
AND
{ field = "ThirstChange", exists = true }
```

---

### 2-2. `equals` 연산

값 동등 비교.

**규칙: boolean/enum만 허용, 수치 비교 금지**

```
// ✅ 허용 (boolean)
{ field = "Alcoholic", equals = true }
{ field = "CanStoreWater", equals = true }

// ✅ 허용 (enum)
{ field = "Type", equals = "Weapon" }
{ field = "Type", equals = "Food" }

// ❌ 금지 (수치 비교)
{ field = "MaxDamage", greaterThan = 0.7 }
{ field = "HungerChange", lessThan = -10 }
```

---

### 2-3. `contains` 연산

문자열 포함 여부 확인.

**규칙: 허용 필드 + 허용값 목록만**

#### 허용 필드

- `CustomContextMenu`
- `Tags`
- `Categories`

#### 허용값 목록

새로운 값 추가 시 이 문서 개정 필요.

| 필드 | 허용값 |
|------|--------|
| `CustomContextMenu` | `Disinfect`, `Bandage`, `Splint`, `Stitch`, `RemoveBullet`, `RemoveGlass`, `CleanWound` |
| `Tags` | `Cookware`, `Medical`, `Tool`, `Weapon`, `Clothing`, `Food`, `Literature`, `StartFire`, `Lighter` |
| `Categories` | `Blunt`, `Blade`, `Axe`, `Spear`, `Firearm`, `Thrown` |

> ℹ️ **중복 매칭 허용**: `Categories`와 `Tags`는 의미가 중복될 수 있으며, 중복 매칭은 허용하고 태그는 누적한다.

> ℹ️ **Categories 용도 제한**: `Categories`는 무기 분류 중심의 문자열이며, 도구/소비/지식 분류의 1차 증거로 사용하지 않는다.

```
// ✅ 허용
{ field = "CustomContextMenu", contains = "Disinfect" }
{ field = "Tags", contains = "Cookware" }

// ❌ 금지 (허용 목록에 없음)
{ field = "CustomContextMenu", contains = "Use" }
{ field = "CustomContextMenu", contains = "Open" }
```

---

## 3. 금지 목록

### 절대 금지

| 항목 | 이유 |
|------|------|
| `DisplayName` | 이름 추론 금지 |
| `DisplayCategory` | 표시용 카테고리, 분류 증거 아님 |
| 아이템 설명(Description) | 텍스트 추론 금지 |
| 수치 비교 (`>`, `<`, `>=`, `<=`) | 판단/평가로 이어짐 |
| 허용 목록 외 문자열 매칭 | 분류 기준 오염 방지 |

### 조건부 금지

| 항목 | 조건 |
|------|------|
| `exists` 단독 사용 | Type 가드 없이 사용 금지 |
| Recipe `category` | 1순위 증거로 사용 금지 (보조만) |
| Damage 계열 필드 | 분류 증거 금지 (표시만) |

---

## 4. 수동 오버라이드 규칙

자동 분류가 기본. 수동 오버라이드는 예외 처리용.

> ⚠️ **수동 오버라이드 허용 조건**: 수동 오버라이드는 **바닐라/모드 데이터에 증거가 누락된 경우에만 허용**한다.  
> 분류 결과가 마음에 들지 않는 경우를 이유로 사용할 수 없다.

### 허용

- 태그 **추가**만 가능
- 아이템 ID 기준으로 지정
- 주석으로 이유 필수

### 금지

- 태그 **제거** 불가
- 자동 분류 결과 **덮어쓰기** 불가

### 형식

```lua
manualOverrides = {
    -- 프라이팬: 바닐라 스크립트에 Cookware 태그 누락
    ["Base.FryingPan"] = { add = { "Tool.1-D" } },
    
    -- 특수 모드 아이템: 자동 분류 불가
    ["ModName.SpecialItem"] = { add = { "Resource.4-A" } },
}
```

---

## 5. 문서 개정 규칙

이 문서는 Iris 자동 분류의 **헌법**이다.

### 개정 필요 사항

- 새로운 증거 소스 추가
- 허용값 목록 확장
- 연산 규칙 변경

### 개정 절차

1. 필요성 검토 (오분류 사례 또는 커버리지 부족)
2. Iris 철학 정합성 확인 (판단/추천 요소 없는지)
3. 문서 업데이트
4. 기존 Rule 영향도 검토

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | - | 초안 작성 |
