# Iris Consumable(3) 소분류 증거표

이 문서는 **Consumable 대분류(3)**의 각 소분류별로 사용할 수 있는 증거를 정의한다.

---

## 증거 우선순위 원칙

1. **1차**: Item Script 필드 (Type, 상태변화 필드 존재 여부)
2. **2차**: Tags / CustomContextMenu
3. **3차**: Recipe 관계 (input으로 사용되는 경우)
4. **최후**: 수동 오버라이드 (증거 누락 시에만)

---

## Consumable 분류의 핵심 원칙

### Type = Food가 기본 가드

Consumable 소분류 대부분은 `Type = Food`를 기본 가드로 사용한다.

### 상태변화 필드는 "exists"로만

`HungerChange`, `ThirstChange` 등 상태변화 필드는:
- **exists 여부**만 분류 증거로 사용
- **수치 비교 금지** (예: `HungerChange < -20` 같은 조건 금지)
- 수치 자체는 **표시 정보**로만 사용

### 다중 분류 허용

하나의 아이템이 여러 소분류에 동시 소속 가능.
예: 버번 위스키 → 3-B(음료) + 3-C(의약품) + 3-D(기호품)

---

## 3-A. 식품 (Food)

**핵심 질문**: 먹으면 배고픔/영양 상태가 변하는가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Food` | 필수 |
| **AND** HungerChange | `exists` | 배고픔 변화 |

> ⚠️ **exists 단독 금지 원칙 적용**: `HungerChange exists`는 반드시 `Type = Food`와 AND 결합.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Calories | `exists` | 영양 정보 |
| Carbohydrates | `exists` | 영양 정보 |
| Proteins | `exists` | 영양 정보 |
| Lipids | `exists` | 영양 정보 |
| IsCookable | `= true` | 조리 가능 |
| DaysFresh / DaysTotallyRotten | `exists` | 부패 시스템 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| HungerChange 수치 비교 | 수치 비교 금지 |
| "좋은 음식" / "나쁜 음식" 판단 | 판단 금지 |

### 표시 정보 (분류 아님)

- 포만감 (HungerChange 수치)
- 영양소 (Calories, Carbohydrates, Proteins, Lipids)
- 부패 상태 (DaysFresh, DaysTotallyRotten)
- 조리 필요 여부
- 개봉 필요 여부
- 독성 여부 (Poison)

### 예시 아이템

- 사과 (Apple)
- 스테이크 (Steak)
- 통조림 (Canned Food)
- 라면 (Ramen)

---

## 3-B. 음료 (Drink)

**핵심 질문**: 마시면 갈증 상태가 변하는가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Food` | 기본 |
| **AND** ThirstChange | `exists` | 갈증 변화 |

### 대안 증거 (Type = Drainable인 경우)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Drainable` | — |
| **AND** ThirstChange | `exists` | 필수 결합 |

> ⚠️ **Drainable 단독 금지**: `Type = Drainable`은 연료, 세제, 공업용 액체 등도 포함할 수 있음.  
> 반드시 `ThirstChange exists` 또는 `CanStoreWater = true`와 AND 결합해야만 3-B 증거로 인정.

> ⚠️ **3-A와 중복 가능**: 음식이면서 음료인 아이템 존재 (예: 수프, 과일).
> 둘 다 해당되면 둘 다 태깅.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| CanStoreWater | `= true` + Type 가드 | 물 용기 (단, Tool.1-D와 구분 필요) |

### 금지

| 증거 | 이유 |
|------|------|
| Type = Drainable 단독 | 연료/세제 등 오분류 위험 |
| DisplayName 추론 | 이름 추론 금지 |
| ThirstChange 수치 비교 | 수치 비교 금지 |

### 표시 정보 (분류 아님)

- 갈증 해소량 (ThirstChange 수치)
- 남은 양 (UseDelta)

### 예시 아이템

- 물 (Water)
- 탄산음료 (Soda)
- 주스 (Juice)
- 커피 (Coffee)

---

## 3-C. 의약품 (Medicine)

**핵심 질문**: 체력, 상처, 감염 등 건강 상태를 치료하는가?

### 필수 증거 (최소 1개)

| 증거 | 조건 | 비고 |
|------|------|------|
| CustomContextMenu | `contains "Disinfect"` | 소독 |
| CustomContextMenu | `contains "Bandage"` | 붕대 |
| CustomContextMenu | `contains "Splint"` | 부목 |
| CustomContextMenu | `contains "CleanWound"` | 상처 세척 |
| Tags | `contains "Medical"` | 의료 태그 |

> ⚠️ **Tool.1-F(의료 도구)와 구분**:
> - 3-C: 상처/감염 **치료에 소모되는 물품** (붕대, 소독약 등)
> - 1-F: 수술/제거 **행위에 필요한 도구** (핀셋, 봉합니들 등)
>
> `Stitch`, `RemoveBullet`, `RemoveGlass`는 **1-F 증거**이지 3-C가 아님.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Food` + 치료 관련 필드 | 경구 약물 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| "효과 좋은 약" 판단 | 판단 금지 |
| Stitch/RemoveBullet/RemoveGlass | 이건 1-F(의료 도구) 증거 |

### 표시 정보 (분류 아님)

- 치료 대상 (상처 유형)
- 남은 횟수 (UseDelta)
- 부작용 여부

### 예시 아이템

- 붕대 (Bandage)
- 진통제 (Painkillers)
- 항생제 (Antibiotics)
- 알코올 솜 (Alcohol Wipes)
- 버번 위스키 (Bourbon) — 소독용

---

## 3-D. 기호품 (Luxury/Vice)

**핵심 질문**: 스트레스, 행복, 중독 등 정신 상태에 영향을 주는가?

### 필수 증거 (최소 1개)

| 증거 | 조건 | 비고 |
|------|------|------|
| Alcoholic | `= true` | 알코올 |
| StressChange | `exists` **AND** Type = Food | 스트레스 변화 |
| UnhappyChange | `exists` **AND** Type = Food | 행복 변화 |

> ⚠️ **exists 단독 금지**: `StressChange exists`, `UnhappyChange exists`는 반드시 Type 가드와 함께.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Tags | 담배/술 관련 (바닐라 확인 필요) | — |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| StressChange 수치 비교 | 수치 비교 금지 |
| "중독성" 판단 | 판단 금지 |

### 표시 정보 (분류 아님)

- 스트레스 변화량 (StressChange 수치)
- 행복 변화량 (UnhappyChange 수치)
- 취함 수치 (Alcoholic 관련)
- 중독 여부

### 예시 아이템

- 담배 (Cigarettes)
- 술 (Alcohol — 버번, 와인, 맥주 등)
- 초콜릿 (Chocolate)
- 커피 (Coffee) — 스트레스 영향 시

### 참고

버번 위스키는 **3-B(음료) + 3-C(의약품) + 3-D(기호품)**에 모두 해당 — 다중 태그.

---

## 3-E. 약초 (Herbs)

**핵심 질문**: 채집으로 얻는 자연 약재인가?

### 필수 증거

**자동 분류 어려움** — 아래 대안 참조

### 바닐라 데이터 현실

약초류 아이템의 특징:
- `Type = Food` 또는 `Type = Normal`
- 특별한 전용 필드가 없을 가능성 높음
- Foraging(채집) 시스템과 연결

### 대안 1: Tags 기반 (바닐라 확인 필요)

| 증거 | 조건 | 비고 |
|------|------|------|
| Tags | 약초 관련 태그 (예: `Herb`, `Medicinal`) | 바닐라 확인 필요 |

### 대안 2: Recipe input 역참조

| 증거 | 조건 | 비고 |
|------|------|------|
| Recipe input | 의료 제작 레시피의 재료 | 약초 → 연고 등 |

### 대안 3: 수동 오버라이드 (권장)

```lua
manualOverrides = {
    -- 레몬그라스
    ["Base.Lemongrass"] = { add = { "Consumable.3-E" } },
    
    -- 컴프리
    ["Base.Comfrey"] = { add = { "Consumable.3-E" } },
    
    -- 기타 약초류...
}
```

> ⚠️ **바닐라 스크립트 확인 필요**: 약초류 아이템의 실제 필드 구조 확인 후 자동 분류 가능 여부 결정.

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| "자연산" / "효능" 판단 | 판단 금지 |

### 표시 정보 (분류 아님)

- 효과 (다양)
- 채집 가능 시기/장소 (표시 가능 여부 확인 필요)

### 예시 아이템

- 레몬그라스 (Lemongrass)
- 컴프리 (Comfrey)
- 야생 마늘 (Wild Garlic)
- 로즈힙 (Rosehips)

---

## 다중 태그 처리 예시

### 버번 위스키 (Bourbon)

```
증거:
- Type = Food, ThirstChange exists → Consumable.3-B ✓
- CustomContextMenu contains "Disinfect" → Consumable.3-C ✓
- Alcoholic = true → Consumable.3-D ✓
- Recipe input (Molotov) → Resource.4-? (화염 재료)

결과: [Consumable.3-B, Consumable.3-C, Consumable.3-D, Resource.4-?]
```

### 초콜릿 (Chocolate)

```
증거:
- Type = Food, HungerChange exists → Consumable.3-A ✓
- Type = Food, UnhappyChange exists → Consumable.3-D ✓

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
- Tags contains "Medical" 또는 관련 필드 → Consumable.3-C ✓
- Type = Food, StressChange exists → Consumable.3-D ✓ (스트레스 감소 시)

결과: [Consumable.3-C, Consumable.3-D]
```

---

## Evidence Allowlist 개정 필요

다음 필드들은 **Iris Evidence Allowlist** 문서에 추가 검토 필요:

**Display Only로 추가:**
- 영양 정보: `Calories`, `Carbohydrates`, `Proteins`, `Lipids`
- 부패 정보: `DaysFresh`, `DaysTotallyRotten`
- 독성: `Poison`

**보조 증거로 추가:**
- 조리 가능: `IsCookable`

> ℹ️ 실제 필드 추가는 Evidence Allowlist 개정 절차를 따른다.

---

## 바닐라 데이터 확인 결과

| 항목 | 확인 결과 | 판정 |
|------|-----------|------|
| 약초류 전용 필드/태그 | **없음** — 일반 Food와 구분 불가 | 3-E 수동 오버라이드 유지 |
| 담배 관련 필드 | **없음** — Alcoholic 외 기호품 구분 불가 | 3-D는 Alcoholic + StressChange 기반 유지 |
| ReduceInfectionPower | **없음** — 치료 효과는 Lua/Java 내부 로직 | 3-C는 CustomContextMenu 기반 유지 |

### 세부 확인 내용

**3-E 약초류:**
- `HerbalistType`, `Tags = Herbal/Medicinal` 같은 통일 필드 없음
- 효과는 레시피/Lua 로직/하드코딩에 분산
- Item Script만으로는 일반 Food와 구분 불가
- **결론: 자동 분류 불가, 수동 오버라이드 정당**

**3-D 담배/기호품:**
- `Alcoholic = TRUE`는 술 전용
- 담배는 `StressChange`, `UnhappyChange` 값만 존재
- `AddictionType = Nicotine` 같은 필드 없음
- 중독/금단 로직은 Lua/Java 캐릭터 상태 머신에서 처리
- **결론: Alcoholic + StressChange/UnhappyChange 기반이 최대 안전선**

**3-C 의약품:**
- `ReduceInfectionPower`, `HealingPower` 같은 수치 필드 없음
- 치료 효과는 ContextMenu 액션 내부 구현에 있음
- **결론: CustomContextMenu 기반 분류가 데이터 구조상 최적해**

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | - | 초안 작성 |
