# Iris Consumable(3) 소분류 증거표 (v0.3)

이 문서는 **Consumable 대분류(3)**의 각 소분류별로 사용할 수 있는 증거를 정의한다.

> ⚠️ **v0.3 주요 변경**: Context Outcome 보조 증거 추가. 바닐라 Lua에서 정적 추출한 결과 타입을 보조 증거로 사용 가능.

---

## 증거 우선순위 원칙

1. **1차**: Item Script 필드 (Type, 상태변화 필드 존재 여부)
2. **2차**: Tags / 의료 필드
3. **3차**: Recipe 관계 (input으로 사용되는 경우)
4. **4차**: Context Outcome (정적 추출 결과) — v0.3 신규
5. **최후**: 수동 오버라이드 (증거 누락 시에만)

---

## Consumable 분류의 핵심 원칙

### Type = Food가 기본 가드

Consumable 소분류 대부분은 `Type = Food`를 기본 가드로 사용한다.

### 상태변화 필드는 "exists"로만

`HungerChange`, `ThirstChange` 등 상태변화 필드는:
- **exists 여부**만 분류 증거로 사용
- **수치 비교 금지**
- 수치 자체는 **표시 정보**로만 사용

### 다중 분류 허용

하나의 아이템이 여러 소분류에 동시 소속 가능.
예: 버번 위스키 → 3-B(음료) + 3-C(의약품) + 3-D(기호품)

---

## 3-A. 식품 (Food)

**핵심 질문**: 먹으면 배고픔/영양 상태가 변하는가?

### 필수 증거 (AND 결합)

| 증거 | 조건 |
|------|------|
| Type | `= Food` |
| **AND** HungerChange | `exists` |

### 보조 증거

| 증거 | 조건 |
|------|------|
| IsCookable | `= true` |
| DaysFresh / DaysTotallyRotten | `exists` |
| Context Outcome | `has_outcome("eat_food")` — v0.3 신규 |
| Context Outcome | `has_outcome("transform_replace")` — v0.3.1 신규 (소비 시 다른 아이템으로 교체) |

### 금지

| 증거 | 이유 |
|------|------|
| HungerChange 수치 비교 | 수치 비교 금지 |
| DisplayName 추론 | 이름 추론 금지 |

### 예시 아이템

- 사과 (Apple)
- 스테이크 (Steak)
- 통조림 (Canned Food)
- 라면 (Ramen)

---

## 3-B. 음료 (Drink)

**핵심 질문**: 마시면 갈증 상태가 변하는가?

### 필수 증거 (AND 결합)

| 증거 | 조건 |
|------|------|
| Type | `= Food` 또는 `= Drainable` |
| **AND** ThirstChange | `exists` |

### 보조 증거

| 증거 | 조건 |
|------|------|
| CustomContextMenu | `contains "Drink"` |
| CanStoreWater | `= true` + Type 가드 |
| Context Outcome | `has_outcome("drink_beverage")` — v0.3 신규 |

> ⚠️ **Drainable 단독 금지**: 연료, 세제 등도 포함할 수 있음. 반드시 `ThirstChange exists`와 AND 결합.

### 예시 아이템

- 물 (Water)
- 탄산음료 (Soda)
- 주스 (Juice)
- 커피 (Coffee)

---

## 3-C. 의약품 (Medicine)

**핵심 질문**: 체력, 상처, 감염 등 건강 상태를 치료하는가?

### 필수 증거 (최소 1개)

| 증거 | 조건 |
|------|------|
| Medical | `= TRUE` |
| CanBandage | `= TRUE` |
| AlcoholPower | `exists` |
| Tags | `contains "Disinfectant"` |

### 보조 증거

| 증거 | 조건 |
|------|------|
| CustomContextMenu | `contains "Take"` |
| Context Outcome | `has_outcome("apply_medical")` — v0.3 신규 |

### 금지

| 증거 | 이유 |
|------|------|
| `CustomContextMenu = Disinfect` | 바닐라 Item Script에 없음 |
| `CustomContextMenu = Bandage` | 바닐라 Item Script에 없음 |
| `Tags = Medical` | Medical은 Tags가 아닌 **독립 필드** |

### 예시 아이템

- 붕대 (Bandage) — Medical = TRUE, CanBandage = TRUE
- 더러운 붕대 (Dirty Bandage) — Medical = TRUE, CanBandage = TRUE
- 소독 붕대 (Sterilized Bandage) — Medical = TRUE, CanBandage = TRUE
- 소독제 (Disinfectant) — Medical = TRUE, Tags = Disinfectant, AlcoholPower exists
- 알코올 솜 (Alcohol Wipes) — Medical = TRUE, AlcoholPower exists
- 진통제 (Painkillers) — Medical = TRUE
- 항생제 (Antibiotics) — Medical = TRUE
- 버번 위스키 (Bourbon) — Alcoholic = TRUE (소독용, 3-D와 다중 태그)

### 3-C vs 1-F 구분

- **3-C**: 상처/감염 **치료에 소모되는 물품** — `Medical = TRUE`, `CanBandage = TRUE`, `AlcoholPower exists`
- **1-F**: 수술/제거 **행위에 필요한 도구** — `Tags = RemoveBullet/RemoveGlass/SewingNeedle`

핀셋(Tweezers)은 1-F, 붕대(Bandage)는 3-C.

---

## 3-D. 기호품 (Luxury/Vice)

**핵심 질문**: 스트레스, 행복, 중독 등 정신 상태에 영향을 주는가?

### 필수 증거 (최소 1개)

| 증거 | 조건 |
|------|------|
| Alcoholic | `= true` |
| StressChange | `exists` **AND** Type = Food |
| CustomContextMenu | `contains "Smoke"` |
| Tags | `contains "AlcoholicBeverage"` |

### 보조 증거

| 증거 | 조건 |
|------|------|
| Tags | `LowAlcohol` |
| UnhappyChange | `exists` **AND** Type = Food |
| Context Outcome | `has_outcome("smoke_item")` — v0.3 신규 |

### 예시 아이템

- 담배 (Cigarettes) — CustomContextMenu = Smoke
- 버번 위스키 (Bourbon) — Alcoholic = true
- 맥주 (Beer) — Alcoholic = true
- 와인 (Wine) — Alcoholic = true
- 초콜릿 (Chocolate) — StressChange exists (스트레스 감소 시)

### 참고

버번 위스키는 **3-B(음료) + 3-C(의약품) + 3-D(기호품)**에 모두 해당 — 다중 태그.

---

## 3-E. 약초 (Herbs)

**핵심 질문**: 채집으로 얻는 자연 약재인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 |
|------|------|
| Tags | `contains "HerbalTea"` |

### 대안: 수동 오버라이드

HerbalTea 태그가 없는 약초류는 수동 오버라이드 필요.

```lua
manualOverrides = {
    ["Base.Lemongrass"] = { add = { "Consumable.3-E" } },
    ["Base.Comfrey"] = { add = { "Consumable.3-E" } },
}
```

### 예시 아이템

- 레몬 (Lemon) — Tags HerbalTea
- 라임 (Lime) — Tags HerbalTea
- 레몬그라스 (Lemongrass) — 수동 오버라이드 필요
- 컴프리 (Comfrey) — 수동 오버라이드 필요

---

## 다중 태그 처리 예시

### 버번 위스키 (Bourbon)

```
증거:
- Type = Food, ThirstChange exists → Consumable.3-B ✓
- Alcoholic = true → Consumable.3-C ✓ (소독), Consumable.3-D ✓
- Recipe input (Molotov) → Resource.4-? (화염 재료)

결과: [Consumable.3-B, Consumable.3-C, Consumable.3-D, Resource.4-?]
```

### 초콜릿 (Chocolate)

```
증거:
- Type = Food, HungerChange exists → Consumable.3-A ✓
- Type = Food, StressChange exists → Consumable.3-D ✓

결과: [Consumable.3-A, Consumable.3-D]
```

### 통조림 수프 (Canned Soup)

```
증거:
- Type = Food, HungerChange exists → Consumable.3-A ✓
- Type = Food, ThirstChange exists → Consumable.3-B ✓

결과: [Consumable.3-A, Consumable.3-B]
```

### 진통제 (Painkillers)

```
증거:
- Medical = TRUE → Consumable.3-C ✓
- Context Outcome = apply_medical → Consumable.3-C ✓ (보조)

결과: [Consumable.3-C]
```

### 붕대 (Bandage)

```
증거:
- Medical = TRUE → Consumable.3-C ✓
- CanBandage = TRUE → Consumable.3-C ✓ (중복)
- Context Outcome = apply_medical → Consumable.3-C ✓ (보조)

결과: [Consumable.3-C]
```

---

## 바닐라 데이터 확인 결과 (v0.2)

| 항목 | 확인 결과 |
|------|-----------|
| `Medical = TRUE` | 붕대, 진통제, 항생제, 소독제 등에 존재 |
| `CanBandage = TRUE` | 붕대류에 존재 |
| `AlcoholPower` | 소독제, 알코올 솜, 알코올화 면볼에 존재 |
| `Tags = Disinfectant` | Base.Disinfectant에만 존재 (1개) |
| `Tags = HerbalTea` | 레몬, 라임 등 16개 아이템에 존재 |
| `CustomContextMenu = Smoke` | Base.Cigarettes에 존재 (1개) |
| `CustomContextMenu = Disinfect` | **Item Script에 없음** |
| `CustomContextMenu = Bandage` | **Item Script에 없음** |

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | - | 초안 작성 |
| 0.2 | - | 바닐라 데이터 기반 전면 개정: 3-C Medical 필드 추가, 3-D Smoke/AlcoholicBeverage 추가, 3-E HerbalTea 추가 |
| 0.3 | - | Context Outcome 보조 증거 추가 (3-A eat_food, 3-B drink_beverage, 3-C apply_medical, 3-D smoke_item) |
| 0.3.1 | - | 완전성 감사 반영: 3-A `has_outcome("transform_replace")` 보조 증거 추가 (소비-교체형) |
