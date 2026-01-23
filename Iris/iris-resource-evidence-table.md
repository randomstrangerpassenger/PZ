# Iris Resource(4) 소분류 증거표

이 문서는 **Resource 대분류(4)**의 각 소분류별로 사용할 수 있는 증거를 정의한다.

---

## 증거 우선순위 원칙

1. **1차**: Recipe role = `input` (재료로 소모되는지)
2. **2차**: Item Script 필드 (Type, 특수 필드)
3. **3차**: Fixing role (수리 재료)
4. **최후**: 수동 오버라이드 (증거 누락 시에만)

---

## Resource 분류의 핵심 원칙

### Recipe input이 핵심 증거

Resource는 "다른 것을 만드는 데 사용되는 재료"다.
따라서 **Recipe에서 input으로 참조되는지**가 1차 증거.

### Category 기반 세분화

Recipe의 category를 조합하여 소분류 결정:
- Carpentry/MetalWelding → 4-A(건설 재료)
- Cooking → 4-B(조리 재료)
- 등등

### Type = Normal의 함정

대부분의 재료 아이템은 `Type = Normal`이다.
따라서 Type만으로는 분류 불가능 — Recipe 관계가 필수.

---

## 4-A. 건설 재료 (Construction Material)

**핵심 질문**: 목공, 금속, 건축 제작에 소모되는 재료인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Recipe role | `= input` | 재료로 소모 |
| **AND** Recipe category | `Carpentry`, `MetalWelding`, `Masonry` 중 하나 | 건설 카테고리 |

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Fixing role | 건물/가구 수리 재료 | 보조 확인 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| Type = Normal 단독 | 대부분의 아이템이 해당 |
| Recipe category 단독 | role 없이 category만으로 분류 금지 |

### 예시 아이템

- 나무판자 (Plank)
- 못 (Nail)
- 금속판 (Sheet Metal)
- 접착제 (Glue)

---

## 4-B. 조리 재료 (Cooking Ingredient)

**핵심 질문**: 요리 제작에 소모되는 재료인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Recipe role | `= input` | 재료로 소모 |
| **AND** Recipe category | `Cooking` | 조리 카테고리 |

> ⚠️ **Consumable.3-A와 구분**:
> - 3-A: `Type = Food` + `HungerChange exists` → 직접 먹을 수 있음
> - 4-B: Recipe input + Cooking → 요리의 재료로 사용됨
>
> 하나의 아이템이 둘 다 해당 가능 (예: 밀가루 — 먹을 수도, 재료로 쓸 수도)

> ⚠️ **우선권 없음**: Consumable(3-A)와 Resource(4-B)가 동시에 해당되는 경우, 어느 쪽도 우선하지 않는다.  
> Iris는 컨텍스트에 따라 다른 태그를 표시할 뿐, 분류 간 우선권을 정의하지 않는다.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Food` | 식재료 확인 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| HungerChange 수치 | 이건 소비(3-A) 증거 |

### 예시 아이템

- 밀가루 (Flour)
- 소금 (Salt)
- 설탕 (Sugar)
- 버터 (Butter)
- 야채류 (조리 재료로 사용 시)

---

## 4-C. 의료 재료 (Medical Supply)

**핵심 질문**: 의료 아이템 제작에 소모되는 재료인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Recipe role | `= input` | 재료로 소모 |
| **AND** Recipe output | 3-C(의약품) 또는 1-F(의료도구) 아이템 | 의료 제작물 |

> ⚠️ **output 역참조의 지위**: 본 항목에서 `output`은 **분류 태그를 추가하는 증거가 아니다.**  
> `input` 아이템의 사용 맥락 확인용 **보조 증거로만** 사용된다.  
> 실제 분류 태그 부여는 항상 `input` role을 기준으로 한다.

### 대안 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Tags | `contains "Medical"` | 의료 태그 |
| **AND** Recipe role | `= input` | 재료로 사용 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| CustomContextMenu | 이건 3-C(의약품) 증거 |

### 예시 아이템

- 천 조각 (Ripped Sheets) — 붕대 제작 재료
- 실 (Thread) — 봉합 재료
- 알코올 (Alcohol) — 소독약 제작 재료

### 참고

알코올(버번 등)은 **3-B(음료) + 3-C(의약품) + 3-D(기호품) + 4-C(의료재료)**에 모두 해당 가능.

---

## 4-D. 연료 (Fuel)

**핵심 질문**: 차량, 발전기, 난방에 사용되는 연료인가?

### 필수 증거

**없음** — 자동 분류 불가

### 바닐라 데이터 확인 결과

연료 아이템(휘발유 등)의 특징:
- `Type = Drainable`
- `UseDelta` 존재
- `CanStoreWater = FALSE`
- `DisplayCategory = Fuel` (⚠️ 분류 증거 금지)

연료 사용 정보:
- Item Script에 선언되지 **않음**
- 차량/발전기 Lua/Java 코드에서 **아이템 ID로 하드코딩** 참조
- 전용 Type, 전용 분류 필드 **없음**

### 처리 방식

**수동 오버라이드로만 처리** (Tool.1-J와 동일한 케이스)

```lua
manualOverrides = {
    -- 휘발유
    ["Base.PetrolCan"] = { add = { "Resource.4-D" } },
    ["Base.Gasoline"] = { add = { "Resource.4-D" } },
    
    -- 프로판
    ["Base.PropaneTank"] = { add = { "Resource.4-D" } },
}
```

### 금지

| 증거 | 이유 |
|------|------|
| Type = Drainable 단독 | 음료, 세제 등 오분류 위험 |
| DisplayCategory = Fuel | 금지 증거 |
| DisplayName 추론 | 이름 추론 금지 |

> ⚠️ **Drainable 오염 방지**: 규칙 엔진에 "연료 의미"를 넣으면 Drainable 전체가 오염될 위험.  
> Iris 철학 준수를 위해 수동 오버라이드 유지.

### 예시 아이템

- 휘발유 (Petrol/Gasoline)
- 프로판 (Propane)
- 등유 (Kerosene)

---

## 4-E. 전자부품 (Electronic Component)

**핵심 질문**: 전자기기 제작/수리에 사용되는 부품인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Recipe role | `= input` | 재료로 소모 |
| **AND** Recipe category | `Electronics` 또는 `Electrical` | 전자 카테고리 |

> ℹ️ **바닐라 확인됨**: `Category:Electronics`와 `Category:Electrical` 둘 다 사용됨.

### 대안 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Fixing role | 전자기기 Fixing의 재료 | 수리 부품 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| Recipe category 단독 | role 없이 category만으로 분류 금지 |

### 예시 아이템

- 전선 (Wire)
- 배터리 (Battery)
- 전자부품 (Electronic Parts)
- 라디오 부품 (Radio Parts)

---

## 4-F. 기타 재료 (Miscellaneous Material)

**핵심 질문**: 위 분류에 해당하지 않지만 제작에 사용되는 재료인가?

### 필수 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Recipe role | `= input` | 재료로 소모 |
| **AND** 위 4-A~4-E에 해당 안 함 | — | 잔여 분류 |

> ⚠️ **잔여 분류 주의**: 4-F는 "어디에도 안 맞는 재료"를 위한 분류.
> 남용하면 분류 의미가 희석됨 — 가능하면 4-A~4-E로 분류 시도.

### 예시 아이템

- 덕트테이프 (Duct Tape) — 다용도
- 로프 (Rope) — 다용도
- 접착제 (Glue) — 여러 카테고리에 걸침

---

## 다중 태그 처리 예시

### 나무판자 (Plank)

```
증거:
- Recipe role = input, category = Carpentry → Resource.4-A ✓

결과: [Resource.4-A]
```

### 밀가루 (Flour)

```
증거:
- Recipe role = input, category = Cooking → Resource.4-B ✓
- Type = Food (먹을 수 있다면) → Consumable.3-A 가능

결과: [Resource.4-B] 또는 [Consumable.3-A, Resource.4-B]
```

### 버번 위스키 (Bourbon)

```
증거:
- Type = Food, ThirstChange exists → Consumable.3-B ✓
- CustomContextMenu contains "Disinfect" → Consumable.3-C ✓
- Alcoholic = true → Consumable.3-D ✓
- Recipe role = input (Molotov 제작) → Resource.4-? ✓

결과: [Consumable.3-B, Consumable.3-C, Consumable.3-D, Resource.4-F]
```

### 천 조각 (Ripped Sheets)

```
증거:
- Recipe role = input, output = Bandage (3-C) → Resource.4-C ✓

결과: [Resource.4-C]
```

### 휘발유 (Petrol)

```
증거:
- Type = Drainable (단독 불충분)
- 수동 오버라이드 → Resource.4-D ✓

결과: [Resource.4-D]
```

---

## Evidence Allowlist 개정 필요

다음 Recipe category 값들을 **Iris Evidence Allowlist**에 추가:

**확인되어 추가 필요:**
- `Electronics` — 전자부품 분류용
- `Electrical` — 전자부품 분류용 (Electronics와 함께)
- `Masonry` — 건설 재료 분류용

> ℹ️ 실제 category 추가는 Evidence Allowlist 개정 절차를 따른다.

---

## 바닐라 데이터 확인 결과

| 항목 | 확인 결과 | 판정 |
|------|-----------|------|
| Electronics category | **존재** — `Electronics`, `Electrical` 둘 다 사용 | 4-E 자동 분류 가능 |
| 연료 시스템 필드 | **없음** — 아이템 ID 하드코딩 | 4-D 수동 오버라이드 |
| Masonry category | **존재** — 돌/벽돌/콘크리트 레시피 | 4-A 자동 분류 가능 |

### 확인된 Recipe Category 값

| Category | 용도 | 소분류 |
|----------|------|--------|
| `Carpentry` | 목공 | 4-A |
| `MetalWelding` | 금속 | 4-A |
| `Masonry` | 석공/콘크리트 | 4-A |
| `Cooking` | 조리 | 4-B |
| `Electronics` | 전자 | 4-E |
| `Electrical` | 전자 | 4-E |

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | - | 초안 작성 |
