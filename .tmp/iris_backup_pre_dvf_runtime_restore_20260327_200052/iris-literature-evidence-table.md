# Iris Literature(5) 소분류 증거표 (v0.2)

이 문서는 **Literature 대분류(5)**의 각 소분류별로 사용할 수 있는 증거를 정의한다.

> ⚠️ **v0.2 주요 변경**: 바닐라 데이터 전수 검증, SkillTrained 값 목록 확정, Type=Map 15개 확인

---

## 증거 우선순위 원칙

1. **1차**: Item Script 필드 (Type = Literature, Type = Map)
2. **2차**: SkillTrained / TeachedRecipes 필드 (소분류 결정)
3. **최후**: 잔여 분류 (5-D)

---

## Literature 분류의 핵심 원칙

### Type이 1차 증거

| Type | 대분류 | 소분류 |
|------|--------|--------|
| `Literature` | 5 (Literature) | 5-A, 5-B, 5-D |
| `Map` | 5 (Literature) | 5-C |

### 소분류는 "효과"로 구분

Literature 내 소분류는 **읽었을 때 무슨 효과가 있는지**로 구분:
- 스킬 경험치 배율 → 5-A(스킬북)
- 레시피 해금 → 5-B(레시피잡지)
- 지도 표시 → 5-C(지도)
- 효과 없음/기타 → 5-D(일반 서적)

---

## 바닐라 데이터 요약 (v0.2)

| 항목 | 값 |
|------|-----|
| Type=Literature | 106개 |
| Type=Map | 15개 |
| SkillTrained 있음 | 60개 (12개 스킬 × 5레벨) |
| TeachedRecipes 있음 | 30개 |
| 둘 다 없음 (5-D) | 16개 |

---

## 5-A. 스킬북 (Skill Book)

**핵심 질문**: 읽으면 특정 스킬 경험치 배율이 증가하는가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Literature` | 필수 |
| **AND** SkillTrained | `exists` | 스킬 훈련 효과 |

### 바닐라 현황

- SkillTrained 있는 아이템: **60개**
- 12개 스킬 × 5개 레벨(Vol.1~5)

### SkillTrained 허용값 (v0.2 확정)

| 스킬명 | 개수 |
|--------|------|
| `Carpentry` | 5 |
| `Cooking` | 5 |
| `Electricity` | 5 |
| `Farming` | 5 |
| `FirstAid` | 5 |
| `Fishing` | 5 |
| `Foraging` | 5 |
| `Mechanics` | 5 |
| `MetalWelding` | 5 |
| `Blacksmith` | 5 |
| `Tailoring` | 5 |
| `Trapping` | 5 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| "고급/초급" 판단 | 판단 금지 |
| LvlSkillTrained 수치 비교 | 수치 비교 금지 |

---

## 5-B. 레시피잡지 (Recipe Magazine)

**핵심 질문**: 읽으면 새로운 제작 레시피가 해금되는가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Literature` | 필수 |
| **AND** TeachedRecipes | `exists` | 레시피 해금 |

### 바닐라 현황

- TeachedRecipes 있는 아이템: **30개**

### SkillTrained + TeachedRecipes 복합

**바닐라에 해당 케이스 없음** (0개). 모드에서 발생 시 둘 다 태깅.

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| TeachedRecipes 내용 분석 | 레시피 내용으로 세분화 금지 |

---

## 5-C. 지도 (Map)

**핵심 질문**: 읽으면 게임 내 지도에 정보가 표시되는가?

### 필수 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Map` | 지도 전용 타입 |

### 바닐라 현황

- Type=Map: **15개**
- 예: `Base.Map`, `Base.LouisvilleMap1` ~ `Base.LouisvilleMap14`

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Map 필드 | `exists` | 지도 데이터 키 (14개) |

### 금지

| 증거 | 이유 |
|------|------|
| Tags = Map | 바닐라에 없음 |
| DisplayName 추론 | 이름 추론 금지 |

---

## 5-D. 일반 서적 (General Reading)

**핵심 질문**: 위 분류에 해당하지 않는 읽을 수 있는 아이템인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Literature` | 필수 |
| **AND** SkillTrained | `not exists` | 스킬북 아님 |
| **AND** TeachedRecipes | `not exists` | 레시피잡지 아님 |

### 바닐라 현황

- Literature - 특수효과 없음: **16개**
- 예: 소설류, 만화책, 신문

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| "재미있는/지루한" 판단 | 판단 금지 |

---

## 분류 흐름도

```
아이템 입력
    │
    ▼
┌─────────────────────┐
│ Type = Map ?        │──Yes──▶ 5-C (지도)
└─────────────────────┘
    │ No
    ▼
┌─────────────────────┐
│ Type = Literature ? │──No───▶ (분류 대상 아님)
└─────────────────────┘
    │ Yes
    ▼
┌─────────────────────┐
│ SkillTrained        │──Yes──▶ 5-A (스킬북)
│   exists ?          │
└─────────────────────┘
    │ No
    ▼
┌─────────────────────┐
│ TeachedRecipes      │──Yes──▶ 5-B (레시피잡지)
│   exists ?          │
└─────────────────────┘
    │ No
    ▼
  5-D (일반 서적)
```

---

## 바닐라 데이터 확인 결과 (v0.2)

| 항목 | 확인 결과 | 영향 |
|------|-----------|------|
| Type=Literature | 106개 | 5-A, 5-B, 5-D 분류 대상 |
| Type=Map | 15개 | 5-C 자동 분류 가능 |
| SkillTrained 필드 | 60개 (12종 × 5레벨) | 5-A 자동 분류 가능 |
| TeachedRecipes 필드 | 30개 | 5-B 자동 분류 가능 |
| SkillTrained + TeachedRecipes | 0개 | 복합 케이스 없음 |
| 잔여 (5-D) | 16개 | 5-D 자동 분류 가능 |
| Tags = Map | **없음** | 사용 금지 |

### 확인된 SkillTrained 값 (v0.2 확정)

```
Blacksmith, Carpentry, Cooking, Electricity, Farming, 
FirstAid, Fishing, Foraging, Mechanics, MetalWelding, 
Tailoring, Trapping
```

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | — | 초안 작성 |
| 0.2 | 2026-01-24 | 바닐라 데이터 전수 검증, SkillTrained 12종 확정, Type=Map 15개 확인 |
