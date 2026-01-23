# Iris Tool(1) 소분류 증거표

이 문서는 **Tool 대분류(1)**의 각 소분류별로 사용할 수 있는 증거를 정의한다.

---

## 증거 우선순위 원칙

1. **1차**: Item Script 필드 (Type, Tags 등)
2. **2차**: Recipe role (keep/require)
3. **3차**: Recipe category (보조 힌트)
4. **4차**: Moveables/Fixing 관계
5. **최후**: 수동 오버라이드 (증거 누락 시에만)

---

## 1-A. 건설/제작 (Construction/Crafting)

**핵심 질문**: 목공, 금속, 석공 작업에 쓰이는 도구인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Recipe role | `keep` 또는 `require` | 필수 |
| **AND** Recipe category | `Carpentry`, `MetalWelding`, `Masonry` 중 하나 | 필수 |

> ⚠️ **1-A는 role만으론 불충분**. Recipe role + category 결합을 필수로 한다.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Tags | `contains "Tool"` | 단독 불충분, 보조로만 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName에 "망치", "톱" 포함 | 이름 추론 금지 |
| Recipe category 단독 | role 없이 category만으로 분류 금지 |
| Recipe role 단독 | category 없이 role만으로 분류 금지 |

### 예시 아이템

- 망치 (Hammer)
- 톱 (Saw)
- 용접토치 (Welding Torch)

---

## 1-B. 분해/개방 (Disassembly/Opening)

**핵심 질문**: 가구, 전자기기, 차량, 통조림 등을 분해하거나 여는 도구인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 | 비고 |
|------|------|------|
| Moveables.ToolDefinition.itemId | `Base.*` 형태로 등록됨 | 분해 도구 |
| Moveables.ToolDefinition.moveablesTag | MoveablesTag allowlist에 있는 값 | 분해 도구 |
| Recipe.GetItemTypes | `CanOpener` 그룹에 포함됨 | 개방 도구 |

> ⚠️ **CanOpener는 Tags 증거가 아님**. `Recipe.GetItemTypes.CanOpener` 그룹 증거로 취급한다.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Recipe role + category | `keep` + category `Disassemble` 계열 | 존재 시 보조 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| Tags contains "CanOpener" | Tags가 아닌 Recipe.GetItemTypes 증거 사용 |
| 임의 "Dismantle" 문자열 매칭 | Moveables 정의에 있는 것만 허용 |

### 예시 아이템

- 스크류드라이버 (Screwdriver)
- 빠루 (Crowbar)
- 캔따개 (Can Opener)

---

## 1-C. 정비 (Maintenance)

**핵심 질문**: 차량, 발전기, 총기 등을 수리/개조하는 도구인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 | 비고 |
|------|------|------|
| Fixing role | `Fixer`로 등록됨 | 수리 도구 |
| Recipe role + category | `keep/require` + `Mechanics` | 차량 정비 |

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Recipe role + category | `keep/require` + `GunModify` 계열 | 총기 개조 |

### 금지

| 증거 | 이유 |
|------|------|
| Fixing.FixerSkill 값 | 표시 정보일 뿐, 분류 증거 아님 |

### 예시 아이템

- 렌치 (Wrench)
- 잭 (Jack)
- 타이어펌프 (Tire Pump)
- 총기수리키트 (Screwdriver for gun)

---

## 1-D. 조리 (Cooking)

**핵심 질문**: 요리, 물끓이기에 쓰이는 도구인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 | 비고 |
|------|------|------|
| Tags | `contains "Cookware"` | 조리도구 태그 |
| Recipe role + category | `keep/require` + `Cooking` | AND 결합 |

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| CanStoreWater | `= true` **AND** (Tags Cookware **OR** Recipe Cooking) | 단독 사용 금지 |
| Type | `Drainable` + 위 필수 조건 조합 | 물병 등 |

### 금지

| 증거 | 이유 |
|------|------|
| CanStoreWater 단독 | 컨테이너/물통 오분류 위험 |
| HungerChange 존재 | 이건 소비(Consumable) 증거 |
| DisplayName 추론 | 이름 추론 금지 |

> ⚠️ **CanStoreWater 단독 금지**: 물병/물통류가 조리도구로 오분류되는 것을 방지.  
> 반드시 Tags(Cookware) 또는 Recipe(Cooking)과 AND 결합해서만 사용.

### 예시 아이템

- 냄비 (Pot)
- 프라이팬 (Frying Pan)
- 그릇 (Bowl)
- 주전자 (Kettle)

---

## 1-E. 농업/채집 (Farming/Foraging)

**핵심 질문**: 농사, 채집, 벌목에 쓰이는 도구인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 | 비고 |
|------|------|------|
| Recipe role + category | `keep/require` + `Farming` | AND 결합 |

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Moveables.ToolDefinition | 벌목/채집 관련 | 확인 후 추가 |

> ℹ️ **태그 기반 증거 없음**: 바닐라에서 농업/채집 전용 태그가 확인되지 않음.  
> 추후 allowlist 개정 절차로만 추가 가능.

### 금지

| 증거 | 이유 |
|------|------|
| 가정 기반 태그 (예: "DigPlow") | 바닐라 미확인 태그 사용 금지 |
| 전투용 도끼와 혼동 | Combat.2-A와 구분 필요 — 다중 태그로 해결 |

### 예시 아이템

- 삽 (Shovel)
- 괭이 (Hoe)
- 도끼 (Axe) — 벌목용, Combat.2-A와 다중 태그

### 참고

도끼처럼 1-E(벌목)와 2-A(전투)에 동시 해당하는 아이템은 **다중 태그** 부여.

---

## 1-F. 의료 (Medical)

**핵심 질문**: 수술, 이물질 제거 등 의료 행위에 필요한 도구인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 | 비고 |
|------|------|------|
| CustomContextMenu | `contains "Stitch"` | 봉합 |
| CustomContextMenu | `contains "RemoveBullet"` | 총알 제거 |
| CustomContextMenu | `contains "RemoveGlass"` | 유리 제거 |
| Tags | `contains "Medical"` | — |

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Recipe role + category | 의료 관련 제작 | 존재 시 보조 |

### 금지

| 증거 | 이유 |
|------|------|
| Disinfect만으로 1-F 태깅 | Disinfect는 3-C(의약품) 증거, 1-F(도구)와 구분 |

### 예시 아이템

- 핀셋 (Tweezers)
- 봉합니들 (Suture Needle)
- 수술용 메스 (Scalpel)

### 참고

**1-F(의료 도구) vs 3-C(의약품) 구분**:
- 1-F: 수술/제거 **행위에 필요한 도구**
- 3-C: 상처/감염 **치료에 소모되는 물품**

버번 위스키의 Disinfect는 3-C 증거이지 1-F가 아님.

---

## 1-G. 포획 (Trapping/Fishing)

**핵심 질문**: 덫, 낚시에 쓰이는 도구인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 | 비고 |
|------|------|------|
| Recipe role + category | `keep/require` + `Trapping` | AND 결합 |
| Recipe role + category | `keep/require` + `Fishing` | AND 결합 |

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Tags | 포획 관련 태그 (바닐라 확인 후) | allowlist 개정 필요 |

> ℹ️ **Type enum 증거 없음**: `Type=Trap` 같은 enum이 바닐라에서 확인되지 않음.  
> Type enum 확정 시 allowlist 개정 절차로 추가.

### 금지

| 증거 | 이유 |
|------|------|
| 가정 기반 Type (예: "Trap") | 바닐라 미확인 Type 사용 금지 |
| DisplayName 추론 | 이름 추론 금지 |

### 예시 아이템

- 덫 (Trap)
- 낚싯대 (Fishing Rod)
- 미끼통 (Bait)

---

## 1-H. 광원/점화 (Light/Ignition)

**핵심 질문**: 조명을 제공하거나 불을 붙이는 도구인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 | 비고 |
|------|------|------|
| LightStrength exists | **AND** (`ActivatedItem = true` **OR** `TorchCone = true`) | 가드 필수 |
| LightDistance exists | **AND** (`ActivatedItem = true` **OR** `TorchCone = true`) | 가드 필수 |
| TorchCone | `= true` | 손전등형 — 단독 허용 |
| Tags | `contains "StartFire"` | 점화 |
| Tags | `contains "Lighter"` | 라이터류 |

> ⚠️ **LightStrength/LightDistance 단독 금지**: exists 단독 사용 금지 원칙 적용.  
> 반드시 `ActivatedItem = true` 또는 `TorchCone = true`와 AND 결합.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `Drainable` + 위 필수 조건 조합 | 연료 소모형 광원 |
| ActivatedItem | `= true` + 위 조건 조합 | 단독 불가, 보조로만 |

### 금지

| 증거 | 이유 |
|------|------|
| LightStrength/LightDistance 단독 | exists 단독 금지 원칙 |
| LightStrength 수치 비교 | 수치 비교 금지 |
| ActivatedItem 단독 | 광원 외 활성화 아이템 오분류 위험 |

### 예시 아이템

- 손전등 (Flashlight)
- 라이터 (Lighter)
- 성냥 (Matches)
- 촛불 (Candle)

---

## 1-I. 통신 (Communication)

**핵심 질문**: 방송 수신, 송수신이 가능한 도구인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Radio` | 라디오류 |

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| TwoWay | `= true` | 워키토키 구분 (표시용) |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |

### 예시 아이템

- 라디오 (Radio)
- 워키토키 (Walkie-Talkie)
- 햄 라디오 (Ham Radio)

---

## 1-J. 전력 (Power)

**핵심 질문**: 전기를 공급하는 장치인가?

### 필수 증거

**없음** — 자동 분류 불가

### 처리 방식

**수동 오버라이드로만 처리**

```lua
manualOverrides = {
    -- 발전기: 스크립트에 분류 가능한 고유 필드 없음
    ["Base.Generator"] = { add = { "Tool.1-J" } },
}
```

### 이유

- `Type = Normal`로 되어 있어 Type 기반 분류 불가
- 고유 필드 없음
- 아이템 ID 기반 규칙을 만들면 예외가 계속 늘어남
- 발전기는 바닐라에 1~2개뿐이라 수동 오버라이드가 현실적

### 예시 아이템

- 발전기 (Generator)

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
- Type = Weapon, Categories = Blade → Combat.2-E ✓

결과: [Tool.1-B, Tool.1-C, Combat.2-E]
```

### 도끼 (Axe)

```
증거:
- Recipe role = keep, category = Farming (벌목) → Tool.1-E ✓
- Type = Weapon, Categories = Axe → Combat.2-A ✓

결과: [Tool.1-E, Combat.2-A]
```

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | - | 초안 작성 |

---

## 부록 A: MoveablesTag Allowlist

### 정의

`MoveablesTag`는 Item Script의 `Tags`와 **완전히 다른 네임스페이스**다.

- **소스**: `ISMoveableDefinitions.lua`의 `Tag.*` 토큰
- **용도**: 1-B(분해/개방) 소분류의 증거로만 사용
- **형식**: `MoveablesTag.<Name>`

### 허용값 목록

바닐라에서 실제로 사용되는 값만 등록. 새로운 값 추가 시 개정 절차 필요.

| 허용값 | 설명 | 바닐라 출처 |
|--------|------|-------------|
| `Crowbar` | 빠루류 | ISMoveableDefinitions.lua |
| `SharpKnife` | 날카로운 칼류 | ISMoveableDefinitions.lua |
| `Hammer` | 망치류 | ISMoveableDefinitions.lua |
| `Screwdriver` | 스크류드라이버류 | ISMoveableDefinitions.lua |
| `Saw` | 톱류 | ISMoveableDefinitions.lua |
| `Wrench` | 렌치류 | ISMoveableDefinitions.lua |

### 개정 규칙

1. **추가 사유**: 오분류 사례 또는 커버리지 부족 (바닐라/주요 모드)
2. **검증**: 해당 값이 `ISMoveableDefinitions.lua`에 실제 존재하는지 확인
3. **절차**: Evidence Allowlist 개정 절차와 동일

### Item Script Tags와의 관계

| 구분 | Item Script Tags | MoveablesTag |
|------|------------------|--------------|
| 소스 | 아이템 스크립트 `.txt` | `ISMoveableDefinitions.lua` |
| 네임스페이스 | `Tags.*` | `MoveablesTag.*` |
| Allowlist | Evidence Allowlist의 Tags 허용값 | 이 부록의 허용값 |
| 혼용 | **금지** | **금지** |

> ⚠️ **혼용 금지**: `Tags contains "Crowbar"`와 `MoveablesTag.Crowbar`는 **서로 다른 증거**다.  
> Item Script에 `Tags = Crowbar`가 없는 아이템도 MoveablesTag로는 매칭될 수 있음.
