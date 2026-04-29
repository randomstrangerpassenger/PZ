# Iris Evidence Allowlist — Phase 2 추가분 (v0.4)

이 문서는 기존 Allowlist v0.3.1에 **Phase 2에서 추가되는 허용 증거**를 정의한다.
기존 내용은 변경하지 않으며, 추가 사항만 기술한다.

---

## 1. Item Script 필드 추가

### 1-1. Type 허용값 추가

기존:
```
Weapon, Food, Literature, Clothing, Drainable, Radio, Map, Normal, Container, WeaponPart
```

추가:

| 추가 Type | 용도 | 분류 연결 |
|-----------|------|-----------|
| `Key` | 잠금/열쇠 아이템 | Tool.1-K (Security) |
| `Moveable` | 이동 가능 배치물 | Furniture.7-A (Placed) |
| `AlarmClockClothing` | 알람시계 의류 (시계류) | Wearable.6-G (Accessory) |

v0.4 전체 Type 허용값:
```
Weapon, Food, Literature, Clothing, Drainable, Radio, Map, Normal, Container, WeaponPart, Key, Moveable, AlarmClockClothing
```

---

### 1-2. Vehicle 전용 필드 추가

#### 분류용 필드 (Classification)

| 필드명 | 타입 | 용도 | 분류 연결 |
|--------|------|------|-----------|
| `MechanicsItem` | boolean | 차량 부품 여부 | Vehicle(8) 대분류 가드 |
| `VehicleType` | enum | 차량 부품 품질 등급 | Vehicle(8) 대분류 가드 — **exists만 허용, 수치 비교 금지** |

#### 구동계 전용 필드 (exists로 분류 증거 사용 가능)

| 필드명 | 타입 | 용도 | 분류 연결 |
|--------|------|------|-----------|
| `WheelFriction` | number | 타이어 마찰 계수 | Vehicle.8-A — exists만 허용 |
| `brakeForce` | number | 제동력 | Vehicle.8-A — exists만 허용 |
| `SuspensionDamping` | number | 서스펜션 감쇠 | Vehicle.8-A — exists만 허용 |
| `SuspensionCompression` | number | 서스펜션 압축 | Vehicle.8-A — exists만 허용 |
| `EngineLoudness` | number | 엔진 소음 | Vehicle.8-A — exists만 허용 |

> ⚠️ 위 5개 필드는 **차체 부품에 존재하지 않음이 확인된** 구동계 전용 필드다.
> exists 여부만 분류 증거로 사용. 수치 비교 금지.

#### 상태/수치 필드 (Display Only) — Vehicle 추가분

| 필드명 | 용도 |
|--------|------|
| `VehicleType` 값 (1/2/3) | 품질 등급 표시 — 분류 증거 아님 |
| `ConditionMax` | 최대 내구도 표시 |
| `MaxCapacity` | 최대 용량 표시 |
| `ChanceToSpawnDamaged` | 스폰 시 파손 확률 표시 |

#### 금지 필드 — Vehicle

| 필드명 | 금지 사유 |
|--------|-----------|
| `ConditionAffectsCapacity` | 가스탱크와 트렁크에 모두 존재하여 구동계 전용이 아님 |

---

### 1-3. Security 전용 필드 추가

| 필드명 | 타입 | 용도 | 분류 연결 |
|--------|------|------|-----------|
| `Padlock` | boolean | 자물쇠 여부 | Tool.1-K 보조 |
| `DigitalPadlock` | boolean | 디지털 자물쇠 여부 | Tool.1-K 보조 |

> ⚠️ 보조 증거. `Type = Key`가 1-K의 핵심 가드.

---

### 1-4. Furniture 보조 필드 추가

| 필드명 | 타입 | 용도 | 분류 연결 |
|--------|------|------|-----------|
| `WorldObjectSprite` | string | 배치 스프라이트 | Furniture(7) — **분류 증거 아님, 표시 정보** |

> ⚠️ WorldObjectSprite는 분류 증거로 사용 불가. 패턴 불규칙, 신뢰도 낮음.

---

## 2. Tags 허용값 추가

| 추가 Tags | 분류 연결 |
|-----------|-----------|
| `CarBattery` | Vehicle.8-A (차량 배터리) |

---

## 3. `exists` 단독 허용 필드 추가

기존 단독 exists 허용 필드:
```
Medical, CanBandage, MountOn, TorchCone, TeachedRecipes, SkillTrained
```

추가:

| 필드명 | 사유 |
|--------|------|
| `MechanicsItem` | Vehicle 대분류 전용 필드 |
| `VehicleType` | Vehicle 대분류 전용 필드 |
| `Padlock` | Security 전용 필드 |
| `DigitalPadlock` | Security 전용 필드 |

---

## 4. 수동 오버라이드 필수 항목 추가

기존 목록에 추가:

| 소분류 | 대상 | 사유 |
|--------|------|------|
| Vehicle.8-A | 가스탱크 9개 (Big/Standard/Small × 3) | 구동계 전용 필드 없음, ConditionAffectsCapacity 공유 |
| Vehicle.8-A | Spare Engine Parts (1개) | 구동계 전용 필드 없음 |

---

## 5. 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | - | 초안 작성 |
| 0.2 | - | 바닐라 데이터 기반 전면 개정 |
| 0.3 | - | Context Outcome 증거 소스 신규 추가 |
| 0.3.1 | - | 완전성 감사 반영 |
| 0.4 | 2026-02-06 | 6-G/6-H 리넘버링 반영 |
| **0.5** | **2026-02-15** | **Phase 2 추가: Type(Key, Moveable, AlarmClockClothing), Vehicle 전용 필드 5개, Security 필드 2개, Tags(CarBattery), ConditionAffectsCapacity 금지, 수동 오버라이드 추가** |
