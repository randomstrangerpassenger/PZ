# Iris Wearable(6) 소분류 증거표 (v0.3)

이 문서는 **Wearable 대분류(6)**의 각 소분류별로 사용할 수 있는 증거를 정의한다.

> ⚠️ **v0.3 주요 변경**: Context Outcome 증거 추가. 특히 6-F(배낭)에서 `has_outcome("equip_back")` 사용 가능.

---

## 증거 우선순위 원칙

1. **1차**: Item Script 필드 (Type = Clothing, BodyLocation)
2. **2차**: Tags
3. **3차**: 방어/보호 관련 필드 (exists 여부)
4. **4차**: Context Outcome (정적 추출 결과) — v0.3 신규
5. **최후**: 수동 오버라이드 (증거 누락 시에만)

---

## Wearable 분류의 핵심 원칙

### Type = Clothing이 기본 가드

Wearable 대분류 진입은 `Type = Clothing`이 기본.

### BodyLocation이 소분류 핵심 증거

착용 부위(`BodyLocation`)로 소분류 결정.

### 방어 수치는 표시 정보

`BladeDefense`, `BiteDefense` 등 방어 수치는:
- **exists 여부**만 보조 증거로 사용 가능
- **수치 비교 금지**
- 수치 자체는 **표시 정보**로만 사용

---

## 6-A. 모자/헬멧 (Headwear)

**핵심 질문**: 머리에 착용하는 아이템인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 |
|------|------|
| Type | `= Clothing` |
| **AND** BodyLocation | 아래 허용값 중 하나 |

### BodyLocation 허용값 (6-A)

| 값 | 설명 | 개수 |
|----|------|------|
| `Hat` | 일반 모자 | 83 |
| `FullHat` | 풀페이스 헬멧 | 6 |
| `FullHelmet` | 복싱 헬멧 등 | 2 |
| `Mask` | 발라클라바 등 | 7 |
| `MaskEyes` | 가스마스크 | 2 |
| `MaskFull` | 용접마스크 | 1 |

### 보조 증거

| 증거 | 조건 |
|------|------|
| Tags | `GasMask` |
| BladeDefense | `exists` |

### 예시 아이템

- 야구 모자 (Baseball Cap) — BodyLocation = Hat
- 건설 헬멧 (Hard Hat) — BodyLocation = Hat
- 오토바이 헬멧 (Crash Helmet) — BodyLocation = FullHat
- 가스마스크 (Gas Mask) — BodyLocation = MaskEyes

---

## 6-B. 상의 (Upperwear)

**핵심 질문**: 상체에 착용하는 아이템인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 |
|------|------|
| Type | `= Clothing` |
| **AND** BodyLocation | 아래 허용값 중 하나 |

### BodyLocation 허용값 (6-B)

| 값 | 설명 | 개수 |
|----|------|------|
| `Shirt` | 셔츠 | 21 |
| `ShortSleeveShirt` | 반팔 셔츠 | 13 |
| `Tshirt` | 티셔츠 | 44 |
| `TankTop` | 민소매 | 2 |
| `Sweater` | 스웨터 | 7 |
| `SweaterHat` | 후드 스웨터 | 1 |
| `Jacket` | 재킷 | 17 |
| `JacketHat` | 후드 재킷 | 2 |
| `JacketHat_Bulky` | 두꺼운 후드 재킷 | 1 |
| `JacketSuit` | 정장 재킷 | 4 |
| `Jacket_Bulky` | 두꺼운 재킷 | 7 |
| `Jacket_Down` | 다운 재킷 | 2 |
| `TorsoExtra` | 앞치마 등 | 11 |
| `TorsoExtraVest` | 방탄조끼 등 | 9 |

### 보조 증거 — v0.3 신규

| 증거 | 조건 |
|------|------|
| Context Outcome | `has_outcome("rip_clothing")` |

### 예시 아이템

- 티셔츠 (T-Shirt) — BodyLocation = Tshirt
- 재킷 (Jacket) — BodyLocation = Jacket
- 방탄조끼 (Bulletproof Vest) — BodyLocation = TorsoExtraVest
- 후드티 (Hoodie) — BodyLocation = SweaterHat

---

## 6-C. 하의 (Lowerwear)

**핵심 질문**: 하체에 착용하는 아이템인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 |
|------|------|
| Type | `= Clothing` |
| **AND** BodyLocation | 아래 허용값 중 하나 |

### BodyLocation 허용값 (6-C)

| 값 | 설명 | 개수 |
|----|------|------|
| `Pants` | 바지 | 48 |
| `Skirt` | 스커트 | 5 |
| `Legs1` | 롱존스 하의 | 1 |

### 보조 증거 — v0.3 신규

| 증거 | 조건 |
|------|------|
| Context Outcome | `has_outcome("rip_clothing")` |

### 예시 아이템

- 청바지 (Jeans) — BodyLocation = Pants
- 작업 바지 (Work Pants) — BodyLocation = Pants
- 스커트 (Skirt) — BodyLocation = Skirt

---

## 6-D. 장갑 (Handwear)

**핵심 질문**: 손에 착용하는 아이템인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 |
|------|------|
| Type | `= Clothing` |
| **AND** BodyLocation | `= Hands` |

### BodyLocation 허용값 (6-D)

| 값 | 설명 | 개수 |
|----|------|------|
| `Hands` | 장갑 | 8 |

### 예시 아이템

- 가죽 장갑 (Leather Gloves)
- 작업 장갑 (Work Gloves)
- 핑거리스 장갑 (Fingerless Gloves)

---

## 6-E. 신발 (Footwear)

**핵심 질문**: 발에 착용하는 아이템인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 |
|------|------|
| Type | `= Clothing` |
| **AND** BodyLocation | 아래 허용값 중 하나 |

### BodyLocation 허용값 (6-E)

| 값 | 설명 | 개수 |
|----|------|------|
| `Shoes` | 신발 | 17 |
| `Socks` | 양말 | 2 |

### 예시 아이템

- 운동화 (Sneakers) — BodyLocation = Shoes
- 작업화 (Work Boots) — BodyLocation = Shoes
- 양말 (Socks) — BodyLocation = Socks

---

## 6-F. 배낭 (Backpack)

**핵심 질문**: 등에 착용하는 수납 아이템인가?

### 필수 증거 — v0.3 개정

| 증거 | 조건 | 비고 |
|------|------|------|
| Context Outcome | `has_outcome("equip_back")` | **v0.3 신규 — 핵심 증거** |

> ⚠️ **v0.3 변경**: 바닐라에서 `BodyLocation = Back`이 확인되지 않아 자동 분류 불가였으나, Context Outcome `equip_back`으로 자동 분류 가능해짐.

### 대안: 수동 오버라이드

Context Outcome 데이터가 없는 경우 여전히 수동 오버라이드 필요:

```lua
manualOverrides = {
    ["Base.Bag_BigHikingBag"] = { add = { "Wearable.6-F" } },
}
```

### 예시 아이템

- 대형 등산 배낭 (Big Hiking Bag) — `has_outcome("equip_back")`
- 학교 가방 (School Bag) — `has_outcome("equip_back")`
- 군용 배낭 (Military Backpack) — `has_outcome("equip_back")`

---

---

## 6-G. 액세서리 (Accessory)

**핵심 질문**: 장식용 또는 기능성 액세서리인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 |
|------|------|
| Type | `= Clothing` |
| **AND** BodyLocation | 아래 허용값 중 하나 |

### BodyLocation 허용값 (6-G)

| 값 | 설명 | 개수 |
|----|------|------|
| `Belt` | 벨트 | 1 |
| `BeltExtra` | 홀스터 | 2 |
| `Neck` | 초커 | 10 |
| `Necklace` | 목걸이 | 11 |
| `Necklace_Long` | 긴 목걸이 | 7 |
| `Eyes` | 안경 | 9 |
| `LeftEye` | 왼쪽 안대 | 1 |
| `RightEye` | 오른쪽 안대 | 1 |
| `Ears` | 귀걸이 | 17 |
| `EarTop` | 상단 귀걸이 | 2 |
| `Scarf` | 스카프 | 4 |
| `LeftWrist` | 왼손목 시계 | 12 |
| `RightWrist` | 오른손목 시계 | 12 |
| `Left_MiddleFinger` | 왼손 중지 반지 | 5 |
| `Left_RingFinger` | 왼손 약지 반지 | 5 |
| `Right_MiddleFinger` | 오른손 중지 반지 | 5 |
| `Right_RingFinger` | 오른손 약지 반지 | 5 |
| `Nose` | 코걸이 | 4 |
| `BellyButton` | 배꼽 피어싱 | 15 |
| `AmmoStrap` | 탄약 스트랩 | 2 |
| `FannyPackFront` | 앞쪽 힙색 | 1 |
| `FannyPackBack` | 뒤쪽 힙색 | 1 |

### 예시 아이템

- 시계 (Watch) — BodyLocation = LeftWrist 또는 RightWrist
- 벨트 (Belt) — BodyLocation = Belt
- 홀스터 (Holster) — BodyLocation = BeltExtra
- 안경 (Glasses) — BodyLocation = Eyes
- 목걸이 (Necklace) — BodyLocation = Necklace

### 보조 증거 — v0.3.1 신규

| 증거 | 조건 | 비고 |
|------|------|------|
| Context Outcome | `has_outcome("equip_variant")` | 착용 시 슬롯 선택 옵션 존재 (좌/우 손목시계 등) |

---

## 다중 태그 처리 예시

### 점프수트/전신복 (Boilersuit)

```
증거:
- Type = Clothing → Wearable 대분류 ✓
- BodyLocation = Boilersuit → Wearable.6-B + Wearable.6-C ✓

결과: [Wearable.6-B, Wearable.6-C]
```

### 드레스 (Dress)

```
증거:
- Type = Clothing → Wearable 대분류 ✓
- BodyLocation = Dress → Wearable.6-B + Wearable.6-C ✓

결과: [Wearable.6-B, Wearable.6-C]
```

### 방호복 (Hazmat Suit)

```
증거:
- Type = Clothing → Wearable 대분류 ✓
- BodyLocation = FullSuitHead → Wearable.6-A + Wearable.6-B + Wearable.6-C ✓

결과: [Wearable.6-A, Wearable.6-B, Wearable.6-C]
```

### 대형 배낭 (Big Hiking Bag) — v0.3 신규

```
증거:
- Context Outcome = equip_back → Wearable.6-F ✓

결과: [Wearable.6-F]
```

---

## 분류 제외 BodyLocation

| 값 | 제외 사유 |
|----|-----------|
| `ZedDmg` | 좀비 데미지 표시용 |
| `Wound` | 상처 표시용 |
| `Bandage` | 붕대 표시용 (착용 아이템 아님) |
| `MakeUp_*` | 메이크업 |
| `Underwear*` | 속옷류 |
| `Tail` | 코스튬 |

---

## 다중 태그 BodyLocation 매핑

| BodyLocation | 분류 |
|--------------|------|
| `Boilersuit` | 6-B + 6-C |
| `Dress` | 6-B + 6-C |
| `FullSuit` | 6-B + 6-C |
| `FullSuitHead` | 6-A + 6-B + 6-C |
| `FullTop` | 6-B + 6-C |
| `Torso1Legs1` | 6-B + 6-C |
| `BathRobe` | 6-B + 6-C |

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | - | 초안 작성 |
| 0.2 | - | 바닐라 데이터 기반 전면 개정: BodyLocation 실제 값으로 교체, 6-F 수동 오버라이드 전환 |
| 0.3 | - | Context Outcome 증거 추가: 6-F `has_outcome("equip_back")` 자동 분류 가능, 6-B/6-C `rip_clothing` 보조 증거 추가 |
| 0.3.1 | - | 완전성 감사 반영: 6-H `has_outcome("equip_variant")` 보조 증거 추가 (착용 변형 옵션) |
| 0.4 | 2026-02-06 | 6-G 힙색을 삭제하고 6-H 액세서리를 6-G 액세서리로 리넘버링. FannyPack BodyLocation을 6-G에 통합. |
