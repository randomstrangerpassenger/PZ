# Iris 분류 체계 최종 아키텍처

> 2026-02-15 확정 (v2 — 구조 리뷰 반영)

## 1. 대분류 9개 (기존 6 + 신규 3)

| # | 대분류 | 역할 축 | 기존/신규 | 규모 |
|---|--------|---------|----------|-----:|
| 1 | Tool | 행동 인터페이스 | 기존 | ~143 |
| 2 | Combat | 공격 | 기존 | 150 |
| 3 | Consumable | 소모 | 기존 | 451 |
| 4 | Resource | 재료/부품 | 기존 | 226 |
| 5 | Literature | 정보 | 기존 | 121 |
| 6 | Wearable | 착용 (신체 슬롯) | 기존 | 478 |
| 7 | **Furniture** | **월드 배치** | 신규 | ~137 |
| 8 | **Vehicle** | **차량 구성요소** | 신규 | ~93 |
| 9 | **Misc** | **비기능 물리** | 신규 | ~115 |

### 역할 축 구조

```
기능 수행 축     Tool / Combat / Consumable
상태 영향 축     Resource
장착·정보 축     Wearable / Literature
환경·시스템 축   Furniture / Vehicle
비기능 축        Misc
```

---

## 2. 경계 규칙

### 경계 1: Resource vs Vehicle

```
Vehicle  = 장착되면 차량의 구조를 구성하는 아이템
Resource = 제작/수리에 소모되는 재료
```

| 예시 | 분류 | 이유 |
|------|------|------|
| Tire, Front Door, Muffler | Vehicle | 구조 구성 |
| Spare Engine Parts | Resource | 수리 시 소모 |

### 경계 2: Misc 오염 방지

```
Misc = 기능 없음 + 상태 영향 없음
       + Storage 없음 + Access 없음 + 배치 없음
```

| 예시 | Misc | 이유 |
|------|:----:|------|
| Wallet, Toy, Photo, Ball | ✔ | 비기능 물리 |
| Key, Padlock | ❌ | Access 기능 |
| Cooler, Plastic Bag | ❌ | Storage 기능 |
| Moveable (가구) | ❌ | 배치 기능 |

> [!CAUTION]
> Misc를 "기타"로 쓰면 구조가 붕괴된다. 5개 부정 조건을 모두 만족하는 아이템만 허용.

### 경계 3: Wearable 정의 보존

```
Wearable = 신체 슬롯(BodyLocation) 기반 착용 아이템
```

> [!WARNING]
> Wearable 정의를 "장착·휴대"로 확장하면 경계 붕괴 위험.
> 비착용 Container는 Wearable이 아닌 Tool.Storage로 배치.

---

## 3. 기능 축 배치

### Tool.Security (Key/Lock 9개)

- 사용 행위 → 상태 변경 트리거 (Access Control)
- Tool의 "인터페이스 기능" 축에 부합

> [!NOTE]
> **조건부 분리**: Access 계열 아이템이 15개 이상으로 커지면 독립 검토.

### Tool.Storage (Non-wearable Container ~26개)

- Storage 인터페이스 (Open, Transfer, Store)
- Tool의 "인터페이스 기능" 축에 부합
- Wearable에 넣으면 착용 정의 위반
- **진입 기준**: 게임 내 Inventory container 기능(아이템 수납/이동)이 존재하는 아이템만 해당
- Storage 기능 없는 단순 용기 오브젝트 → Misc

### Tool의 역할 축 정리

```
Tool = 플레이어가 사용하여 상태/행동을 가능하게 하는 인터페이스
 ├ 작업 도구 (1-A~1-J)
 ├ Security (Access 인터페이스)
 └ Storage (보관 인터페이스)
```

---

## 4. 차량 정비 도구 → Tool.1-C 유지

Jack, Lug Wrench, Tire Pump, Car Battery Charger (4개)

- "부품"이 아니라 "도구" → Vehicle이 아닌 Tool
- Vehicle로 옮기면 역할 축(대상 vs 역할) 혼합

---

## 5. 아이템 분배 요약 (활성 미분류 906개)

| 구분 | 수 | 처리 |
|------|---:|------|
| 기존 소분류에 흡수 | ~335 | 빌드 규칙 확장 |
| 시스템 아이템 제외 | ~228 | blocklist |
| → Furniture | ~137 | 신규 대분류 |
| → Vehicle | ~93 | 신규 대분류 |
| → Misc | ~115 | 신규 대분류 |

### 제외 대상 (228개)

ZedDmg(74) + Wound(60) + Appearance(43) + Bandage(34) + Animals(8) + Hidden(4) + MaleBody(3) + Corpse(2)

---

## 6. 남은 작업

1. 신규 대분류 소분류 설계 — Furniture(7-\*), Vehicle(8-\*), Misc(9-\*)
2. 기존 대분류 소분류 확장 — Tool.Security, Tool.Storage 코드 배정
3. ~335개 흡수 규칙 — 빌드 파이프라인 phase2_rules 확장
4. 제외 목록 — blocklist 정의 및 빌드 적용
