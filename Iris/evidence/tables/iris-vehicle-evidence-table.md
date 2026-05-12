# Iris Vehicle(8) 소분류 증거표 (v0.2)

이 문서는 **Vehicle 대분류(8)**의 각 소분류별로 사용할 수 있는 증거를 정의한다.

> ⚠️ **v0.2 주요 변경**: `ConditionAffectsCapacity`를 8-A 구동계 판별 필드에서 제거.
> 사유: 트렁크(8-B)에도 존재하여 오분류 위험. 가스탱크는 수동 오버라이드로 전환.

---

## 증거 우선순위 원칙

1. **1차**: Item Script 필드 (MechanicsItem, VehicleType)
2. **2차**: 구동계 전용 필드 존재 여부 (WheelFriction, brakeForce, SuspensionDamping, SuspensionCompression, EngineLoudness)
3. **3차**: Tags (CarBattery)
4. **최후**: 수동 오버라이드 (가스탱크, 엔진 파츠 등)

---

## Vehicle 분류의 핵심 원칙

### 대분류 가드: MechanicsItem + VehicleType

Vehicle 대분류 진입은 `MechanicsItem = TRUE` **AND** `VehicleType exists`의 조합이 핵심.

> ⚠️ **바닐라 데이터**:
> - `MechanicsItem = TRUE`: 92/93 (99%)
> - `VehicleType exists`: 91/93 (98%)
> - 두 조건 동시 충족: ~91개

### Type = Normal의 함정

Vehicle 아이템 대부분은 `Type = Normal` (90/93)이다.
`Type = Normal` 단독으로는 Vehicle을 판별할 수 없다 — Resource, Misc 등도 `Type = Normal`.

### VehicleType은 품질 등급

`VehicleType`의 값(1, 2, 3)은 품질 등급을 나타내며, 소분류 분류 증거가 아닌 **표시 정보**다.

### 소분류는 "구동 기여 vs 구조 기여"로 구분

- Drivetrain: 구동·주행 성능에 직접 관여하는 부품
- Body: 차량의 외장·내장 구조를 구성하는 부품

### 구동계 전용 필드의 정의

8-A 판별에 사용하는 구동계 필드는 **트렁크/문/창문 등 차체 부품에는 존재하지 않는 필드만** 허용한다.

| 필드 | 존재 부품 | 차체에 존재 여부 |
|------|----------|:---------------:|
| `WheelFriction` | 타이어 | ✗ |
| `brakeForce` | 브레이크 | ✗ |
| `SuspensionDamping` | 서스펜션 | ✗ |
| `SuspensionCompression` | 서스펜션 | ✗ |
| `EngineLoudness` | 머플러 | ✗ |
| ~~`ConditionAffectsCapacity`~~ | ~~가스탱크~~ | **⚠️ 트렁크에도 존재** |

`ConditionAffectsCapacity`는 가스탱크(9개)와 트렁크(최대 13개)에 모두 존재하므로
구동계 전용 필드가 아니다. **8-A 판별 조건에서 제거**.

---

## 8-A. 구동계 (Drivetrain)

**핵심 질문**: 장착 시 차량의 구동·주행 성능을 구성하는 부품인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| MechanicsItem | `= TRUE` | 필수 |
| **AND** VehicleType | `exists` | 필수 |
| **AND** 구동계 필드 | 아래 중 최소 1개 exists | 소분류 결정 |

### 구동계 판별 필드 (최소 1개 exists)

| 필드 | 설명 | 해당 부품 | 개수 |
|------|------|----------|-----:|
| `WheelFriction` | 타이어 마찰 계수 | 타이어 | 9 |
| `brakeForce` | 제동력 | 브레이크 | 9 |
| `SuspensionDamping` | 서스펜션 감쇠 | 서스펜션 | 6 |
| `SuspensionCompression` | 서스펜션 압축 | 서스펜션 | 6 |
| `EngineLoudness` | 엔진 소음 | 머플러 | 9 |

> ⚠️ 이 5개 필드는 **차체 부품에 존재하지 않음이 확인된** 구동계 전용 필드다.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Tags | `contains "CarBattery"` | 차량 배터리 (3개) |

### 수동 오버라이드 필요 항목

구동계 전용 필드가 없지만 구동계인 부품:

```lua
manualOverrides = {
    -- 가스탱크: ConditionAffectsCapacity가 트렁크와 공유되므로 자동 분류 불가
    ["Base.BigGasTank1"]       = { add = { "Vehicle.8-A" } },
    ["Base.BigGasTank2"]       = { add = { "Vehicle.8-A" } },
    ["Base.BigGasTank3"]       = { add = { "Vehicle.8-A" } },
    ["Base.StandardGasTank1"]  = { add = { "Vehicle.8-A" } },
    ["Base.StandardGasTank2"]  = { add = { "Vehicle.8-A" } },
    ["Base.StandardGasTank3"]  = { add = { "Vehicle.8-A" } },
    ["Base.SmallGasTank1"]     = { add = { "Vehicle.8-A" } },
    ["Base.SmallGasTank2"]     = { add = { "Vehicle.8-A" } },
    ["Base.SmallGasTank3"]     = { add = { "Vehicle.8-A" } },
    -- 엔진 파츠: 구동계 전용 필드 없음
    ["Base.EngineParts"]       = { add = { "Vehicle.8-A" } },
}
```

### 금지

| 증거 | 이유 |
|------|------|
| DisplayCategory = VehicleMaintenance | 금지 증거 |
| VehicleType 수치 비교 | 품질 등급 비교 금지 |
| ConditionMax 수치 비교 | 수치 비교 금지 |
| MaxCapacity 수치 비교 | 수치 비교 금지 |
| Weight 수치 비교 | 수치 비교 금지 |
| **ConditionAffectsCapacity** | **트렁크에도 존재하여 구동계 전용이 아님** |

### 예시 아이템

**자동 분류:**
- Regular Tire (1/2/3) — WheelFriction exists
- Regular Brake (1/2/3) — brakeForce exists
- Regular Suspension (1/2/3) — SuspensionDamping exists
- Average Muffler (1/2/3) — EngineLoudness exists
- Car Battery (1/2/3) — Tags CarBattery

**수동 오버라이드:**
- Big Gas Tank (1/2/3) — 구동계 전용 필드 없음
- Spare Engine Parts — 구동계 전용 필드 없음

### 바닐라 현황

| 분류 경로 | 아이템 수 |
|-----------|----------:|
| 자동 분류 (5개 필드 + CarBattery 태그) | ~42 |
| 수동 오버라이드 (가스탱크 + 엔진 파츠) | ~10 |
| **8-A 총계** | **~52** |

---

## 8-B. 차체 (Body)

**핵심 질문**: 장착 시 차량의 외장·내장 구조를 구성하는 부품인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| MechanicsItem | `= TRUE` | 필수 |
| **AND** VehicleType | `exists` | 필수 |
| **AND** 8-A 구동계 필드 | 모두 `not exists` | 잔여 분류 |
| **AND** Tags | `not contains "CarBattery"` | 배터리 제외 |
| **AND** 수동 오버라이드 | 8-A 지정 아님 | 가스탱크/엔진 제외 |

### 처리 방식

**잔여 분류**

Vehicle 대분류에 진입했으나 8-A(구동계) 조건을 충족하지 않는 아이템은 자동으로 8-B에 배치된다.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| ConditionLowerStandard | `exists` | 문/창문류 (24개) |
| ConditionLowerOffroad | `exists` | 문/창문류 (24개) |

> ⚠️ 보조 증거는 참고용. 8-B 진입은 잔여 분류로 결정된다.

### 금지

| 증거 | 이유 |
|------|------|
| DisplayCategory = VehicleMaintenance | 금지 증거 |
| MaxCapacity 수치 비교 | 트렁크 용량 비교 금지 |

### 예시 아이템

- Front Door (1/2/3)
- Rear Window (1/2/3)
- Windshield (1/2/3)
- Trunk Lid (1/2/3)
- Standard Seat (1/2/3)
- Glove Box (1/2/3)
- Small/Standard/Big/Trailer Trunk
- Hood (1/2/3)

### 바닐라 현황

| 분류 경로 | 아이템 수 |
|-----------|----------:|
| 잔여 분류 (8-A 미해당) | **~40** |

---

## Vehicle 대분류 가드: 예외 처리

### MechanicsItem 없는 아이템 (1개)

바닐라에서 MechanicsItem이 없는 Vehicle 아이템이 1개 존재할 수 있다.
이 경우 수동 오버라이드로 처리.

### Car Key는 Vehicle이 아님

Car Key는 `Type = Key` (Security)로, Vehicle 대분류 가드(`MechanicsItem = TRUE` AND `VehicleType exists`)를 충족하지 않는다.
→ Tool.Security(1-K)에 배치.

---

## 분류 흐름도

```
아이템 입력
    │
    ▼
┌──────────────────────────────────┐
│ MechanicsItem = TRUE             │──No───▶ (Vehicle 대분류 아님)
│ AND VehicleType exists ?         │
└──────────────────────────────────┘
    │ Yes
    ▼
┌──────────────────────────────────┐
│ 구동계 전용 필드 exists ?        │──Yes──▶ 8-A (구동계)
│ (WheelFriction / brakeForce /    │
│  SuspensionDamping /             │
│  SuspensionCompression /         │
│  EngineLoudness)                 │
│ OR Tags contains "CarBattery" ?  │
└──────────────────────────────────┘
    │ No
    ▼
┌──────────────────────────────────┐
│ 수동 오버라이드 = 8-A ?          │──Yes──▶ 8-A (구동계)
│ (가스탱크, 엔진 파츠)            │
└──────────────────────────────────┘
    │ No
    ▼
  8-B (차체) ← 잔여 분류
```

---

## 바닐라 데이터 확인 결과 (v0.2)

| 항목 | 확인 결과 |
|------|-----------|
| 총 아이템 | 93개 |
| Type = Normal | 90개 (97%) |
| Type = Drainable | 3개 (Car Battery) |
| MechanicsItem = TRUE | 92개 (99%) |
| VehicleType exists | 91개 (98%) |
| VehicleType 값 | 1(30), 2(31), 3(30) — 품질 등급 |
| WheelFriction exists | 9개 (타이어) — **구동계 전용 ✓** |
| brakeForce exists | 9개 (브레이크) — **구동계 전용 ✓** |
| SuspensionDamping exists | 6개 (서스펜션) — **구동계 전용 ✓** |
| SuspensionCompression exists | 6개 (서스펜션) — **구동계 전용 ✓** |
| EngineLoudness exists | 9개 (머플러) — **구동계 전용 ✓** |
| ConditionAffectsCapacity exists | 22개 — **⚠️ 구동계 전용 아님 (트렁크 포함)** |
| Tags = CarBattery | 3개 |
| Tags = EmptyPetrol | 1개 |
| ConditionLowerStandard exists | 24개 (차체 보조) |
| ConditionLowerOffroad exists | 24개 (차체 보조) |

### 8-A 자동 분류 커버리지

| 경로 | 필드 | 아이템 수 |
|------|------|----------:|
| 자동 | WheelFriction | 9 (타이어) |
| 자동 | brakeForce | 9 (브레이크) |
| 자동 | SuspensionDamping + SuspensionCompression | 6 (서스펜션) |
| 자동 | EngineLoudness | 9 (머플러) |
| 자동 | Tags CarBattery | 3 (배터리) |
| **자동 소계** | | **~36** |
| 수동 | 가스탱크 (9) + 엔진 파츠 (1) | ~10 |
| **8-A 총계** | | **~46** |

> ⚠️ v0.1에서 추정한 ~54개와 차이 발생.
> v0.1은 ConditionAffectsCapacity(22개)를 포함했으나, 트렁크 제외 후 실제 구동계는 ~46개.

### 8-B 잔여 분류

| 아이템 | 예상 수 |
|--------|--------:|
| 8-A 미해당 Vehicle | **~46** |

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | 2026-02-15 | 초안 작성. ConditionAffectsCapacity를 8-A 판별 필드에 포함. 오분류 위험 식별. |
| 0.2 | 2026-02-15 | ConditionAffectsCapacity를 8-A 판별 필드에서 제거 (트렁크 공유 확인). 가스탱크 9개 + 엔진 파츠 1개를 수동 오버라이드로 전환. 금지 증거에 ConditionAffectsCapacity 추가. 커버리지 재계산. |
