# Iris Tool.Security(1-K) 증거표 보충 (v0.1)

이 문서는 **Tool.Security(1-K)** 소분류의 증거를 정의한다.
기존 Tool(1) 증거표에 추가되는 내용이다.

---

## 1-K. 보안/접근 (Security)

**핵심 질문**: 잠금/해제, 접근 제어에 사용되는 아이템인가?

### 필수 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Key` | 핵심 가드 — 9/9(100%) |

> ⚠️ **Type = Key**: 바닐라에서 Security DisplayCategory의 모든 아이템이 `Type = Key`.
> 이는 Key, Padlock, Car Key를 모두 포함한다.

### 보조 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Padlock | `exists` | Padlock 아이템 구분 (1개) |
| DigitalPadlock | `exists` | Combination Padlock 구분 (1개) |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayCategory = Security | 금지 증거 |
| DisplayName 추론 | 이름 추론 금지 |

### 예시 아이템

- Key (×6) — Type = Key
- Padlock — Type = Key, Padlock = TRUE
- Combination Padlock — Type = Key, DigitalPadlock = TRUE
- **Car Key** — Type = Key (Vehicle이 아닌 Tool.Security)

### Car Key 배치 근거

Car Key는:
- `Type = Key` → Tool.Security 가드 충족
- `MechanicsItem` 없음 → Vehicle 가드 불충족
- 역할: 차량 접근/시동 인터페이스 (Access Control)
- Key/Padlock과 동일한 "접근 인터페이스" 역할

### 바닐라 현황

| 항목 | 확인 결과 |
|------|-----------|
| Type = Key | 9개 (100%) |
| DisplayCategory = Security | 9개 — 금지 증거 |
| Padlock 필드 | 1개 |
| DigitalPadlock 필드 | 1개 |
| Car Key (Key 포함) | 1개 |
| 일반 Key | 6개 |

### 조건부 분리 규칙 (기존 아키텍처 문서 참조)

> Access 계열 아이템이 15개 이상으로 커지면 독립 검토.

현재 10개로 기준 미달. Tool 소분류로 유지.

---

## Allowlist 업데이트 필요 사항

### Type 필드 허용값 추가

현재 allowlist의 Type 허용값:
```
Weapon, Food, Literature, Clothing, Drainable, Radio, Map, Normal, Container, WeaponPart
```

추가 필요:
```
Key, Moveable, AlarmClockClothing
```

| 추가 Type | 용도 | 분류 연결 |
|-----------|------|-----------|
| `Key` | 잠금/열쇠 아이템 | Tool.1-K (Security) |
| `Moveable` | 이동 가능 배치물 | Furniture(7) |
| `AlarmClockClothing` | 알람시계 의류 (시계류) | Wearable.6-G (Accessory) |

### Vehicle 전용 필드 추가

| 추가 필드 | 타입 | 용도 | 분류 연결 |
|-----------|------|------|-----------|
| `MechanicsItem` | boolean | 차량 부품 여부 | Vehicle(8) 대분류 가드 |
| `VehicleType` | enum | 차량 부품 품질 등급 | Vehicle(8) 대분류 가드 — exists만 허용, 수치 비교 금지 |
| `WheelFriction` | number | 타이어 마찰 | Vehicle.8-A — exists만 허용 |
| `brakeForce` | number | 제동력 | Vehicle.8-A — exists만 허용 |
| `SuspensionDamping` | number | 서스펜션 감쇠 | Vehicle.8-A — exists만 허용 |
| `SuspensionCompression` | number | 서스펜션 압축 | Vehicle.8-A — exists만 허용 |
| `EngineLoudness` | number | 엔진 소음 | Vehicle.8-A — exists만 허용 |
| `ConditionAffectsCapacity` | boolean | 상태→용량 영향 | Vehicle.8-A — 보조 (오분류 주의) |

### Furniture 전용 필드 추가

| 추가 필드 | 타입 | 용도 | 분류 연결 |
|-----------|------|------|-----------|
| `WorldObjectSprite` | string | 배치 스프라이트 | Furniture(7) — 보조 힌트 |

### Security 전용 필드 추가

| 추가 필드 | 타입 | 용도 | 분류 연결 |
|-----------|------|------|-----------|
| `Padlock` | boolean | 자물쇠 여부 | Tool.1-K 보조 |
| `DigitalPadlock` | boolean | 디지털 자물쇠 여부 | Tool.1-K 보조 |

### Tags 허용값 추가

| 추가 Tags | 분류 연결 |
|-----------|-----------|
| `CarBattery` | Vehicle.8-A (차량 배터리) |
| `EmptyPetrol` | 기존 Resource.4-D와 중복 가능 — 확인 필요 |

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | 2026-02-15 | 초안 작성. Tool.1-K(Security) 정의. Car Key 배치 근거 명시. Allowlist 업데이트 사항 정리. |
