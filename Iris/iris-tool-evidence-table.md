# Iris Tool(1) 소분류 증거표 (v0.3)

이 문서는 **Tool 대분류(1)**의 각 소분류별로 사용할 수 있는 증거를 정의한다.

> ⚠️ **v0.3 주요 변경**: Context Outcome 보조 증거 추가. 바닐라 Lua에서 정적 추출한 결과 타입을 보조 증거로 사용 가능.

---

## 증거 우선순위 원칙

1. **1차**: Item Script 필드 (Type, Tags 등)
2. **2차**: Recipe role (keep/require)
3. **3차**: Recipe category (보조 힌트)
4. **4차**: Moveables/Fixing 관계
5. **5차**: Context Outcome (정적 추출 결과) — v0.3 신규
6. **최후**: 수동 오버라이드 (증거 누락 시에만)

---

## 1-A. 건설/제작 (Construction/Crafting)

**핵심 질문**: 목공, 금속 작업에 쓰이는 도구인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Recipe role | `keep` 또는 `require` | 필수 |
| **AND** Recipe category | `Carpentry`, `Welding`, `Smithing` 중 하나 | 필수 |

### 보조 증거

| 증거 | 조건 |
|------|------|
| Tags | `Hammer`, `Saw`, `Sledgehammer`, `WeldingMask` |

### 예시 아이템

- 망치 (Hammer)
- 톱 (Saw)
- 대형망치 (Sledgehammer)

---

## 1-B. 분해/개방 (Disassembly/Opening)

**핵심 질문**: 가구, 전자기기, 통조림 등을 분해하거나 여는 도구인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 |
|------|------|
| Moveables.ToolDefinition.itemId | `Base.Hammer`, `Base.Screwdriver` |
| Moveables.ToolDefinition.tag | `Tag.Crowbar`, `Tag.SharpKnife`, `Tag.Scissors` |
| Tags | `CanOpener`, `Crowbar`, `RemoveBarricade` |

### 보조 증거

| 증거 | 조건 |
|------|------|
| Tags | `Scissors`, `Screwdriver` |
| Context Outcome | `has_outcome("disassemble")` — v0.3 신규 |

### 예시 아이템

- 스크류드라이버 (Screwdriver)
- 빠루 (Crowbar)
- 캔따개 (Can Opener)
- 가위 (Scissors)

---

## 1-C. 정비 (Maintenance)

**핵심 질문**: 차량, 발전기 등을 수리하는 도구인가?

### 필수 증거

| 증거 | 조건 |
|------|------|
| Moveables.ToolDefinition | Wrench 정의에 포함 (`Base.Wrench`, `Base.PipeWrench`) |

### 보조 증거 — v0.3 신규

| 증거 | 조건 |
|------|------|
| Context Outcome | `has_outcome("repair_item")` |

### 예시 아이템

- 렌치 (Wrench)
- 파이프렌치 (Pipe Wrench)

---

## 1-D. 조리 (Cooking)

**핵심 질문**: 요리, 물끓이기에 쓰이는 도구인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 |
|------|------|
| Recipe role + category | `keep` + `Cooking` (AND 결합) |
| Tags | `CoffeeMaker` |

### 보조 증거

| 증거 | 조건 |
|------|------|
| CanStoreWater | `= true` **AND** (Tags CoffeeMaker **OR** Recipe Cooking+keep) |
| Tags | `SharpKnife`, `DullKnife`, `Fork`, `Spoon` |

### 금지

| 증거 | 이유 |
|------|------|
| CanStoreWater 단독 | 컨테이너/물통 오분류 위험 |
| `Tags = Cookware` | 바닐라에 없음 |

### 예시 아이템

- 냄비 (Pot) — Recipe Cooking+keep
- 프라이팬 (Pan) — Recipe Cooking+keep
- 주전자 (Kettle) — Tags CoffeeMaker
- 머그컵 (Mug) — Tags CoffeeMaker

---

## 1-E. 농업/채집 (Farming/Foraging)

**핵심 질문**: 농사, 채집, 벌목에 쓰이는 도구인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 |
|------|------|
| Recipe role + category | `keep/require` + `Farming` |
| Tags | `DigPlow`, `ChopTree`, `ClearAshes`, `TakeDirt`, `DigGrave` |

### 예시 아이템

- 삽 (Shovel) — Tags DigPlow, TakeDirt
- 손삽 (Hand Shovel) — Tags DigPlow, TakeDirt
- 도끼 (Axe) — Tags ChopTree (Combat.2-A와 다중 태그)

---

## 1-F. 의료 (Medical Tool)

**핵심 질문**: 수술, 이물질 제거 등 의료 행위에 필요한 도구인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 |
|------|------|
| Tags | `RemoveBullet`, `RemoveGlass`, `SewingNeedle` |

### 금지

| 증거 | 이유 |
|------|------|
| Medical = TRUE 단독 | 의약품(3-C)과 구분 필요 |
| AlcoholPower exists | 3-C(의약품) 증거 |

### 예시 아이템

- 핀셋 (Tweezers) — Tags RemoveBullet, RemoveGlass
- 봉합니들홀더 (Suture Needle Holder) — Tags RemoveBullet, RemoveGlass
- 바늘 (Needle) — Tags SewingNeedle

### 1-F vs 3-C 구분

- **1-F**: 수술/제거 **행위에 필요한 도구** — `Tags = RemoveBullet/RemoveGlass/SewingNeedle`
- **3-C**: 상처/감염 **치료에 소모되는 물품** — `Medical = TRUE`, `CanBandage = TRUE`, `AlcoholPower exists`

---

## 1-G. 포획 (Trapping/Fishing)

**핵심 질문**: 덫, 낚시에 쓰이는 도구인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 |
|------|------|
| Recipe role + category | `keep/require` + `Trapper` 또는 `Fishing` |
| Tags | `FishingRod`, `FishingSpear` |

### 예시 아이템

- 낚싯대 (Fishing Rod) — Tags FishingRod
- 작살 (Spear) — Tags FishingSpear

---

## 1-H. 광원/점화 (Light/Ignition)

**핵심 질문**: 조명을 제공하거나 불을 붙이는 도구인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 |
|------|------|
| LightStrength exists | **AND** `ActivatedItem = true` |
| TorchCone | `= true` |
| Tags | `StartFire`, `Lighter` |

### 보조 증거 — v0.3 신규

| 증거 | 조건 |
|------|------|
| Context Outcome | `has_outcome("toggle_activate")` |

### 금지

| 증거 | 이유 |
|------|------|
| LightStrength 단독 | exists 단독 금지 원칙 |
| LightStrength 수치 비교 | 수치 비교 금지 |

### 예시 아이템

- 손전등 (Torch) — TorchCone = true
- 라이터 (Lighter) — Tags Lighter, StartFire
- 양초 (Candle Lit) — Tags StartFire

---

## 1-I. 통신 (Communication)

**핵심 질문**: 방송 수신, 송수신이 가능한 도구인가?

### 필수 증거

| 증거 | 조건 |
|------|------|
| Type | `= Radio` |

### 보조 증거

| 증거 | 조건 |
|------|------|
| TwoWay | `= true` (워키토키 구분) |
| Context Outcome | `has_outcome("toggle_state")` — v0.3.1 신규 (전원/모드 전환) |

### 예시 아이템

- 라디오 (Radio)
- 워키토키 (Walkie-Talkie)

---

## 1-J. 전력 (Power)

**핵심 질문**: 전기를 공급하는 장치인가?

### 필수 증거

**없음** — 자동 분류 불가

### 보조 증거 — v0.3 신규

| 증거 | 조건 |
|------|------|
| Context Outcome | `has_outcome("place_world")` **AND** `has_outcome("toggle_activate")` |

> ⚠️ Context Outcome만으로는 1-J 자동 분류에 불충분. 여전히 수동 오버라이드 권장.

### 처리 방식

**수동 오버라이드로만 처리**

```lua
manualOverrides = {
    ["Base.Generator"] = { add = { "Tool.1-J" } },
}
```

### 예시 아이템

- 발전기 (Generator)

---

## 다중 태그 처리 예시

### 프라이팬 (Pan)

```
증거:
- Recipe role = keep, category = Cooking → Tool.1-D ✓
- Type = Weapon, Categories = SmallBlunt → Combat.2-C ✓

결과: [Tool.1-D, Combat.2-C]
```

### 도끼 (HandAxe)

```
증거:
- Tags = ChopTree → Tool.1-E ✓
- Type = Weapon, Categories = Axe → Combat.2-A ✓

결과: [Tool.1-E, Combat.2-A]
```

### 핀셋 (Tweezers)

```
증거:
- Tags = RemoveBullet, RemoveGlass → Tool.1-F ✓
- Medical = TRUE (보조)

결과: [Tool.1-F]
```

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | - | 초안 작성 |
| 0.2 | - | 바닐라 데이터 기반 전면 개정 |
| 0.3 | - | Context Outcome 보조 증거 추가 (1-B, 1-C, 1-H, 1-J) |
| 0.3.1 | - | 완전성 감사 반영: 1-I `has_outcome("toggle_state")` 보조 증거 추가 |
