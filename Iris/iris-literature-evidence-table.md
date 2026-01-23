# Iris Literature(5) 소분류 증거표

이 문서는 **Literature 대분류(5)**의 각 소분류별로 사용할 수 있는 증거를 정의한다.

---

## 증거 우선순위 원칙

1. **1차**: Item Script 필드 (Type = Literature, IsLiterature)
2. **2차**: TeachedRecipes / SkillTrained 필드
3. **3차**: Tags
4. **최후**: 수동 오버라이드 (증거 누락 시에만)

---

## Literature 분류의 핵심 원칙

### Type = Literature가 1차 증거

Literature 대분류 진입은 `Type = Literature`가 기본.

```
Type = Literature → Literature 대분류 확정
```

### IsLiterature는 보조 증거

`IsLiterature = true`는 모드 호환용 보조 증거.
Type이 없을 때만 사용.

### 소분류는 "효과"로 구분

Literature 내 소분류는 **읽었을 때 무슨 효과가 있는지**로 구분:
- 스킬 경험치 → 5-A(스킬북)
- 레시피 해금 → 5-B(레시피잡지)
- 지도 표시 → 5-C(지도)
- 효과 없음/기타 → 5-D(일반 서적)

---

## 5-A. 스킬북 (Skill Book)

**핵심 질문**: 읽으면 특정 스킬 경험치 배율이 증가하는가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Literature` | 필수 |
| **AND** SkillTrained | `exists` | 스킬 훈련 효과 |

> ℹ️ **바닐라 확인됨**: `SkillTrained`는 스킬명 문자열 (예: `Carpentry`, `Fishing`, `Electricity`)

### 대안 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| IsLiterature | `= true` | Type 없을 때 |
| **AND** SkillTrained | `exists` | 스킬 훈련 효과 |

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| LvlSkillTrained | `exists` | 적용 시작 레벨 (정수) |
| NumLevelsTrained | `exists` | 훈련 레벨 범위 (정수, 보통 2) |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| "고급/초급" 판단 | 판단 금지 |
| LvlSkillTrained 수치 비교 | 수치 비교 금지 |

### 표시 정보 (분류 아님)

- 대상 스킬 (SkillTrained 값)
- 적용 레벨 범위 (LvlSkillTrained, NumLevelsTrained)
- 경험치 배율 (NumberOfPages 등)

### 예시 아이템

- Carpentry for Beginners (목공 초급)
- The Herbalist (약초학)
- Farming Guide (농업 가이드)

---

## 5-B. 레시피잡지 (Recipe Magazine)

**핵심 질문**: 읽으면 새로운 제작 레시피가 해금되는가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Literature` | 필수 |
| **AND** TeachedRecipes | `exists` | 레시피 해금 |

### 대안 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| IsLiterature | `= true` | Type 없을 때 |
| **AND** TeachedRecipes | `exists` | 레시피 해금 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| TeachedRecipes 내용 분석 | 레시피 내용으로 세분화 금지 |

### 표시 정보 (분류 아님)

- 해금 레시피 목록 (TeachedRecipes 값)
- 레시피 카테고리

### 예시 아이템

- The Hunter Magazine (사냥꾼 잡지)
- Engineer Magazine (엔지니어 잡지)
- Guerilla Radio (게릴라 라디오 잡지)

---

## 5-C. 지도 (Map)

**핵심 질문**: 읽으면 게임 내 지도에 정보가 표시되는가?

### 필수 증거 (최소 1개)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Map` | 지도 전용 타입 |

> ℹ️ **바닐라 확인됨**: 지도는 `Type = Map`으로 별도 타입이 존재함.  
> `Type = Literature`가 아니라 `Type = Map`이다.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Map | `exists` | 지도 데이터 키 (예: `LouisvilleMap1`) |

> ℹ️ **Map 필드**: 실제 지도 데이터 연결 여부. 기본 Map 아이템은 Type=Map만 있고 Map 필드는 없을 수 있음.

### 금지

| 증거 | 이유 |
|------|------|
| Tags = Map | 바닐라에 없음 — 거짓 근거 |
| DisplayName 추론 | 이름 추론 금지 |

### 예시 아이템

- Louisville Map (루이빌 지도)
- West Point Map (웨스트포인트 지도)
- March Ridge Map (마치릿지 지도)

---

## 5-D. 일반 서적 (General Reading)

**핵심 질문**: 위 분류에 해당하지 않는 읽을 수 있는 아이템인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Literature` | 필수 |
| **AND** SkillTrained | `not exists` | 스킬북 아님 |
| **AND** TeachedRecipes | `not exists` | 레시피잡지 아님 |

> ℹ️ **5-C(지도)와 구분**: 지도는 `Type = Map`이므로 `Type = Literature`인 5-D와 자동으로 구분됨.

### 대안 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| IsLiterature | `= true` | Type 없을 때 |
| **AND** 위 효과 필드들 | `not exists` | 특수 효과 없음 |

> ⚠️ **잔여 분류**: 5-D는 "Literature이지만 특수 효과가 없는 것"을 위한 분류.
> 스트레스/행복 변화만 있는 일반 읽을거리가 여기에 해당.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| StressChange | `exists` + Type = Literature | 스트레스 감소 효과 |
| UnhappyChange | `exists` + Type = Literature | 행복 변화 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| "재미있는/지루한" 판단 | 판단 금지 |

### 표시 정보 (분류 아님)

- 스트레스 감소량 (있을 경우)
- 읽는 데 걸리는 시간

### 예시 아이템

- 소설류 (Novel)
- 만화책 (Comic Book)
- 신문 (Newspaper)
- 잡지 (일반, 레시피 해금 없는 것)

---

## 다중 태그 처리 예시

### Carpentry for Beginners (목공 초급)

```
증거:
- Type = Literature → Literature 대분류 ✓
- SkillTrained exists (= Carpentry) → Literature.5-A ✓

결과: [Literature.5-A]
```

### The Hunter Magazine (사냥꾼 잡지)

```
증거:
- Type = Literature → Literature 대분류 ✓
- TeachedRecipes exists → Literature.5-B ✓

결과: [Literature.5-B]
```

### 일반 소설 (Novel)

```
증거:
- Type = Literature → Literature 대분류 ✓
- SkillTrained not exists ✓
- TeachedRecipes not exists ✓
→ Literature.5-D ✓

결과: [Literature.5-D]
```

### 지도 (Louisville Map)

```
증거:
- Type = Map → Literature.5-C ✓
- Map = LouisvilleMap1 (보조 확인)

결과: [Literature.5-C]
```

### 복합 케이스 (스킬북 + 레시피)

```
증거:
- Type = Literature → Literature 대분류 ✓
- SkillTrained exists → Literature.5-A ✓
- TeachedRecipes exists → Literature.5-B ✓

결과: [Literature.5-A, Literature.5-B]
```

> ℹ️ **다중 태그 허용**: 스킬 훈련과 레시피 해금을 동시에 제공하는 서적은 둘 다 태깅.

---

## Evidence Allowlist 개정 필요

다음 필드들을 **Iris Evidence Allowlist**에 추가:

**Type enum 추가:**
- `Map` — 5-C 필수 증거

**분류 증거로 추가:**
- `SkillTrained` — 5-A 필수 증거 (문자열, 스킬명)
- `LvlSkillTrained` — 5-A 보조 증거 (정수)
- `NumLevelsTrained` — 5-A 보조 증거 (정수)
- `Map` (필드) — 5-C 보조 증거 (지도 데이터 키)

**이미 등록됨:**
- `TeachedRecipes` — 5-B 필수 증거

> ℹ️ 실제 필드 추가는 Evidence Allowlist 개정 절차를 따른다.

---

## 바닐라 데이터 확인 결과

| 항목 | 확인 결과 | 판정 |
|------|-----------|------|
| Map 필드/Type | `Type = Map` 별도 존재, `Map` 필드로 데이터 키 연결 | 5-C 자동 분류 가능 |
| Tags = Map | **없음** — 거짓 근거 | 사용 금지 |
| SkillTrained 필드 | **존재** — 스킬명 문자열 (`Carpentry`, `Fishing` 등) | 5-A 자동 분류 가능 |
| LvlSkillTrained | **존재** — 정수 (1, 3, 5, 7, 9) | 보조 증거 |
| NumLevelsTrained | **존재** — 정수 (보통 2) | 보조 증거 |

### 확인된 Type 값

| Type | 용도 | 소분류 |
|------|------|--------|
| `Literature` | 책/잡지류 | 5-A, 5-B, 5-D |
| `Map` | 지도류 | 5-C |

### 확인된 SkillTrained 값 (예시)

`Carpentry`, `Fishing`, `Trapping`, `Electricity`, `Farming`, `Cooking`, `Mechanics` 등

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | - | 초안 작성 |
