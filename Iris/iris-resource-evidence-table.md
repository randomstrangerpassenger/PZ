# Iris Resource(4) 소분류 증거표 (v0.3)

이 문서는 **Resource 대분류(4)**의 각 소분류별로 사용할 수 있는 증거를 정의한다.

> ⚠️ **v0.3 주요 변경**: Context Outcome 보조 증거 추가. 바닐라 Lua에서 정적 추출한 결과 타입을 보조 증거로 사용 가능.

---

## 증거 우선순위 원칙

1. **1차**: Recipe role = `input` (재료로 소모되는지)
2. **2차**: Item Script 필드 (Type, Tags)
3. **3차**: Fixing role (수리 재료)
4. **4차**: Context Outcome (정적 추출 결과) — v0.3 신규
5. **최후**: 수동 오버라이드 (증거 누락 시에만)

---

## Resource 분류의 핵심 원칙

### Recipe input이 핵심 증거

Resource는 "다른 것을 만드는 데 사용되는 재료"다.
따라서 **Recipe에서 input으로 참조되는지**가 1차 증거.

### Category 기반 세분화

Recipe의 category를 조합하여 소분류 결정:
- Carpentry/Welding/Smithing → 4-A(건설 재료)
- Cooking → 4-B(조리 재료)
- Health → 4-C(의료 재료)
- Electrical/Engineer → 4-E(전자부품)

### Type = Normal의 함정

대부분의 재료 아이템은 `Type = Normal`이다.
따라서 Type만으로는 분류 불가능 — Recipe 관계가 필수.

---

## 4-A. 건설 재료 (Construction Material)

**핵심 질문**: 목공, 금속, 건축 제작에 소모되는 재료인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 |
|------|------|
| Recipe role | `= input` |
| **AND** Recipe category | `Carpentry`, `Welding`, `Smithing` 중 하나 |

### 보조 증거

| 증거 | 조건 |
|------|------|
| Fixing role | 건물/가구 수리 재료 |

### 금지

| 증거 | 이유 |
|------|------|
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

| 증거 | 조건 |
|------|------|
| Recipe role | `= input` |
| **AND** Recipe category | `Cooking` |

> ⚠️ **Consumable.3-A와 구분**:
> - 3-A: `Type = Food` + `HungerChange exists` → 직접 먹을 수 있음
> - 4-B: Recipe input + Cooking → 요리의 재료로 사용됨
>
> 하나의 아이템이 둘 다 해당 가능 (예: 밀가루)

### 보조 증거

| 증거 | 조건 |
|------|------|
| Tags | `Flour`, `Egg`, `Cheese` |

### 예시 아이템

- 밀가루 (Flour)
- 소금 (Salt)
- 설탕 (Sugar)
- 버터 (Butter)

---

## 4-C. 의료 재료 (Medical Supply)

**핵심 질문**: 의료 아이템 제작에 소모되는 재료인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 |
|------|------|
| Recipe role | `= input` |
| **AND** Recipe category | `Health` |

### 대안 증거

| 증거 | 조건 |
|------|------|
| Medical | `= TRUE` **AND** Recipe role = input |

### 금지

| 증거 | 이유 |
|------|------|
| `Tags = Medical` | Medical은 Tags가 아닌 필드 |
| Medical = TRUE 단독 | 3-C(의약품)과 구분 필요 — Recipe input 필수 |

### 예시 아이템

- 천 조각 (Ripped Sheets) — 붕대 제작 재료
- 실 (Thread) — 봉합 재료
- 알코올 (Alcohol) — 소독약 제작 재료

---

## 4-D. 연료 (Fuel)

**핵심 질문**: 차량, 발전기, 난방에 사용되는 연료인가?

### 필수 증거 (최소 1개)

| 증거 | 조건 |
|------|------|
| Tags | `contains "Petrol"` |

### 보조 증거 — v0.3 신규

| 증거 | 조건 |
|------|------|
| Context Outcome | `has_outcome("fill_container")` **AND** `has_outcome("empty_container")` |
| Context Outcome | `has_outcome("transform_replace")` — v0.3.1 신규 (소비 시 빈 용기로 교체 등) |

> ⚠️ Context Outcome만으로는 4-D 자동 분류에 불충분 (물통 등 오분류 위험). Tags = Petrol이 핵심.

### 수동 오버라이드 필요 항목

Petrol 태그가 없는 연료류:

```lua
manualOverrides = {
    ["Base.PropaneTank"] = { add = { "Resource.4-D" } },
}
```

### 금지

| 증거 | 이유 |
|------|------|
| Type = Drainable 단독 | 음료, 세제 등 오분류 위험 |
| DisplayCategory = Fuel | 금지 증거 |

### 예시 아이템

- 휘발유 (Petrol) — Tags Petrol
- 가스캔 (Gas Can) — Tags Petrol
- 프로판 (Propane) — 수동 오버라이드

---

## 4-E. 전자부품 (Electronic Component)

**핵심 질문**: 전자기기 제작/수리에 사용되는 부품인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 |
|------|------|
| Recipe role | `= input` |
| **AND** Recipe category | `Electrical` 또는 `Engineer` |

### 대안 증거

| 증거 | 조건 |
|------|------|
| Fixing role | 전자기기 Fixing의 재료 |

### 예시 아이템

- 전선 (Wire)
- 배터리 (Battery)
- 전자부품 (Electronic Parts)
- 라디오 부품 (Radio Parts)

---

## 4-F. 기타 재료 (Miscellaneous Material)

**핵심 질문**: 위 분류에 해당하지 않지만 제작에 사용되는 재료인가?

### 필수 증거

| 증거 | 조건 |
|------|------|
| Recipe role | `= input` |
| **AND** 위 4-A~4-E에 해당 안 함 | — |

> ⚠️ **잔여 분류 주의**: 4-F는 "어디에도 안 맞는 재료"를 위한 분류.

### 보조 증거

| 증거 | 조건 |
|------|------|
| Tags | `Rope` |

### 예시 아이템

- 덕트테이프 (Duct Tape)
- 로프 (Rope) — Tags Rope
- 접착제 (Glue)

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
- Type = Food → Consumable.3-A 가능

결과: [Consumable.3-A, Resource.4-B]
```

### 버번 위스키 (Bourbon)

```
증거:
- Type = Food, ThirstChange exists → Consumable.3-B ✓
- Alcoholic = true → Consumable.3-C ✓ (소독), Consumable.3-D ✓
- Recipe role = input (Molotov 제작) → Resource.4-F ✓

결과: [Consumable.3-B, Consumable.3-C, Consumable.3-D, Resource.4-F]
```

### 휘발유 (Petrol)

```
증거:
- Tags = Petrol → Resource.4-D ✓

결과: [Resource.4-D]
```

---

## 바닐라 데이터 확인 결과 (v0.2)

| 항목 | 확인 결과 |
|------|-----------|
| `Category = Electrical` | 존재 (163 input, 0 keep) |
| `Category = Engineer` | 존재 (16 input, 0 keep) |
| `Category = Health` | 존재 (29 input, 0 keep) |
| `Category = Smithing` | 존재 (50 input, 64 keep) |
| `Category = Welding` | 존재 (11 input, 0 keep) |
| `Category = MetalWelding` | **없음** |
| `Category = Masonry` | **없음** |
| `Category = Electronics` | **없음** (Electrical 사용) |
| `Tags = Petrol` | 존재 (6개) |

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | - | 초안 작성 |
| 0.2 | - | 바닐라 데이터 기반 전면 개정: Recipe Category 수정, 4-C Health 기반, 4-D Petrol 태그 추가 |
| 0.3 | - | Context Outcome 보조 증거 추가 (4-D fill_container/empty_container) |
| 0.3.1 | - | 완전성 감사 반영: 4-D `has_outcome("transform_replace")` 보조 증거 추가 (소비-교체형) |
