# Iris Wearable(6) 소분류 증거표

이 문서는 **Wearable 대분류(6)**의 각 소분류별로 사용할 수 있는 증거를 정의한다.

---

## 증거 우선순위 원칙

1. **1차**: Item Script 필드 (Type = Clothing, BodyLocation)
2. **2차**: Tags
3. **3차**: 방어/보호 관련 필드 (exists 여부)
4. **최후**: 수동 오버라이드 (증거 누락 시에만)

---

## Wearable 분류의 핵심 원칙

### Type = Clothing이 기본 가드

Wearable 대분류 진입은 `Type = Clothing`이 기본.

### BodyLocation이 소분류 핵심 증거

착용 부위(`BodyLocation`)로 소분류 결정:
- Head → 6-A(모자/헬멧)
- Torso/Torso_Upper/Torso_Lower → 6-B(상의)
- Legs/Groin → 6-C(하의)
- Hands → 6-D(장갑)
- Feet → 6-E(신발)
- Back → 6-F(배낭)
- FannyPack → 6-G(힙색)
- Neck/Eyes/Belt 등 → 6-H(액세서리)

### 방어 수치는 표시 정보

`BladeDefense`, `BiteDefense` 등 방어 수치는:
- **exists 여부**만 보조 증거로 사용 가능
- **수치 비교 금지** (예: `BiteDefense > 50` 같은 조건 금지)
- 수치 자체는 **표시 정보**로만 사용

---

## 6-A. 모자/헬멧 (Headwear)

**핵심 질문**: 머리에 착용하는 아이템인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Clothing` | 필수 |
| **AND** BodyLocation | `= Head` | 머리 부위 |

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| BladeDefense | `exists` | 방어구 여부 |
| BiteDefense | `exists` | 방어구 여부 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| BladeDefense 수치 비교 | 수치 비교 금지 |
| "좋은 헬멧" 판단 | 판단 금지 |

### 표시 정보 (분류 아님)

- 방어력 (BladeDefense, BiteDefense, BulletDefense 수치)
- 보온/방수 (Insulation, WaterResistance)
- 내구도 (ConditionMax)

### 예시 아이템

- 야구 모자 (Baseball Cap)
- 건설 헬멧 (Hard Hat)
- 오토바이 헬멧 (Motorcycle Helmet)
- 방독면 (Gas Mask)

---

## 6-B. 상의 (Upperwear)

**핵심 질문**: 상체에 착용하는 아이템인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Clothing` | 필수 |
| **AND** BodyLocation | `= Torso` 또는 `Torso_Upper` 또는 `Torso_Lower` | 상체 부위 |

### BodyLocation 허용값 (6-B)

| 값 | 설명 |
|----|------|
| `Torso` | 상체 전체 |
| `Torso_Upper` | 상체 상부 |
| `Torso_Lower` | 상체 하부 |

> ℹ️ **전신복 처리**: 점프수트 등 전신복은 `Torso` + `Legs`를 동시 점유.  
> Iris는 각 BodyLocation에 따라 6-B + 6-C 둘 다 태깅.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| BladeDefense | `exists` | 방어구 여부 |
| Insulation | `exists` | 보온 의류 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| 방어력 수치 비교 | 수치 비교 금지 |

### 예시 아이템

- 티셔츠 (T-Shirt)
- 재킷 (Jacket)
- 방탄조끼 (Bulletproof Vest)
- 후드티 (Hoodie)

---

## 6-C. 하의 (Lowerwear)

**핵심 질문**: 하체에 착용하는 아이템인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Clothing` | 필수 |
| **AND** BodyLocation | `= Legs` 또는 `= Groin` | 하체 부위 |

### BodyLocation 허용값 (6-C)

| 값 | 설명 |
|----|------|
| `Legs` | 다리 |
| `Groin` | 골반/엉덩이 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |

### 예시 아이템

- 청바지 (Jeans)
- 작업 바지 (Work Pants)
- 반바지 (Shorts)

---

## 6-D. 장갑 (Handwear)

**핵심 질문**: 손에 착용하는 아이템인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Clothing` | 필수 |
| **AND** BodyLocation | `= Hands` | 손 부위 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |

### 예시 아이템

- 가죽 장갑 (Leather Gloves)
- 작업 장갑 (Work Gloves)
- 의료 장갑 (Medical Gloves)

---

## 6-E. 신발 (Footwear)

**핵심 질문**: 발에 착용하는 아이템인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Clothing` | 필수 |
| **AND** BodyLocation | `= Feet` | 발 부위 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |

### 예시 아이템

- 운동화 (Sneakers)
- 작업화 (Work Boots)
- 슬리퍼 (Slippers)

---

## 6-F. 배낭 (Backpack)

**핵심 질문**: 등에 착용하는 수납 아이템인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Clothing` | 필수 |
| **AND** BodyLocation | `= Back` | 등 부위 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |
| 수납 용량 비교 | 수치 비교 금지 |

### 표시 정보 (분류 아님)

- 수납 용량 (Capacity)
- 무게 감소율 (WeightReduction)

### 예시 아이템

- 배낭 (Backpack)
- 등산 배낭 (Hiking Bag)
- 학생 가방 (School Bag)
- 군용 배낭 (Military Backpack)

---

## 6-G. 힙색 (Fanny Pack)

**핵심 질문**: 허리에 착용하는 수납 아이템인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Clothing` | 필수 |
| **AND** BodyLocation | `= FannyPack` | 허리 가방 슬롯 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |

### 표시 정보 (분류 아님)

- 수납 용량 (Capacity)

### 예시 아이템

- 힙색 (Fanny Pack)
- 허리 파우치 (Waist Pouch)

---

## 6-H. 액세서리 (Accessory)

**핵심 질문**: 장식용 또는 기능성 액세서리인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Clothing` | 필수 |
| **AND** BodyLocation | 액세서리 계열 | 아래 참조 |

### BodyLocation 허용값 (6-H)

| 값 | 설명 |
|----|------|
| `Neck` | 목걸이/스카프 |
| `Belt` | 벨트 |
| `BeltExtra` | 추가 벨트/홀스터 |
| `Waist` | 허리 |
| `Eyes` | 안경/고글 |

> ℹ️ **Back, FannyPack 제외**: 이들은 각각 6-F, 6-G로 분리됨.

### 금지

| 증거 | 이유 |
|------|------|
| DisplayName 추론 | 이름 추론 금지 |

### 예시 아이템

- 시계 (Watch)
- 벨트 (Belt)
- 홀스터 (Holster)
- 안경 (Glasses)
- 스카프 (Scarf)

---

## 다중 태그 처리 예시

### 오토바이 헬멧 (Motorcycle Helmet)

```
증거:
- Type = Clothing → Wearable 대분류 ✓
- BodyLocation = Head → Wearable.6-A ✓

결과: [Wearable.6-A]
```

### 점프수트 (Jumpsuit) — 전신복

```
증거:
- Type = Clothing → Wearable 대분류 ✓
- BodyLocation = Torso → Wearable.6-B ✓
- BodyLocation = Legs → Wearable.6-C ✓

결과: [Wearable.6-B, Wearable.6-C]
```

> ℹ️ **전신복 처리**: 전신복 전용 BodyLocation은 없음.  
> 복합 BodyLocation(Torso + Legs)으로 정의되므로, 해당되는 모든 소분류에 태깅.

### 방탄조끼 (Bulletproof Vest)

```
증거:
- Type = Clothing → Wearable 대분류 ✓
- BodyLocation = Torso → Wearable.6-B ✓
- BladeDefense exists, BiteDefense exists (표시 정보)

결과: [Wearable.6-B]
```

### 배낭 (Backpack)

```
증거:
- Type = Clothing → Wearable 대분류 ✓
- BodyLocation = Back → Wearable.6-F ✓

결과: [Wearable.6-F]
```

### 힙색 (Fanny Pack)

```
증거:
- Type = Clothing → Wearable 대분류 ✓
- BodyLocation = FannyPack → Wearable.6-G ✓

결과: [Wearable.6-G]
```

---

## 바닐라 데이터 확인 결과

| 항목 | 확인 결과 | 판정 |
|------|-----------|------|
| BodyLocation 값 목록 | 고정 enum, 동적 확장 없음 | 자동 분류 안전 |
| 전신복 BodyLocation | **없음** — 복합 슬롯으로 표현 | 6-B + 6-C 다중 태깅 |
| 가방류 분리 | Back / FannyPack 별도 슬롯 | 6-F / 6-G 분리 |

### 확인된 BodyLocation 값

| BodyLocation | 소분류 |
|--------------|--------|
| `Head` | 6-A |
| `Eyes` | 6-H |
| `Neck` | 6-H |
| `Torso` | 6-B |
| `Torso_Upper` | 6-B |
| `Torso_Lower` | 6-B |
| `Hands` | 6-D |
| `Legs` | 6-C |
| `Groin` | 6-C |
| `Feet` | 6-E |
| `Waist` | 6-H |
| `Belt` | 6-H |
| `BeltExtra` | 6-H |
| `Back` | 6-F |
| `FannyPack` | 6-G |

---

## Evidence Allowlist 개정 필요

다음 필드들을 **Iris Evidence Allowlist**에 추가:

**BodyLocation 허용값 (바닐라 확인됨):**
- 머리: `Head`
- 상체: `Torso`, `Torso_Upper`, `Torso_Lower`
- 하체: `Legs`, `Groin`
- 손: `Hands`
- 발: `Feet`
- 배낭: `Back`
- 힙색: `FannyPack`
- 액세서리: `Neck`, `Eyes`, `Waist`, `Belt`, `BeltExtra`

**Display Only로 추가:**
- `BladeDefense`, `BiteDefense`, `BulletDefense` — 방어력 표시
- `Insulation` — 보온 표시
- `WaterResistance` — 방수 표시
- `ConditionMax` — 내구도 표시
- `Capacity` — 수납 용량 표시
- `WeightReduction` — 무게 감소율 표시

> ℹ️ 실제 값 추가는 Evidence Allowlist 개정 절차를 따른다.

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | - | 초안 작성 |
