# Iris Misc(9) 소분류 증거표 (v0.1)

이 문서는 **Misc 대분류(9)**의 각 소분류별로 사용할 수 있는 증거를 정의한다.

---

## 증거 우선순위 원칙

1. **1차**: 다른 모든 대분류 조건 불일치 (잔여 분류)
2. **2차**: Misc 5개 부정 조건 확인
3. **최후**: 수동 오버라이드 (경계 아이템)

---

## Misc 분류의 핵심 원칙

### Misc는 최종 잔여 분류

Misc는 다른 8개 대분류에 진입하지 못한 아이템의 최종 도착지다.
"기타 잡동사니"가 아니라, **5개 부정 조건을 모두 만족하는 비기능 물리 아이템**만 허용한다.

### 5개 부정 조건 (모두 충족 필수)

```
1. 기능 없음     — Tool/Combat/Consumable 어디에도 해당하지 않음
2. 상태 영향 없음 — Resource/Consumable 조건 불충족
3. Storage 없음   — Type ≠ Container
4. Access 없음    — Type ≠ Key
5. 배치 없음      — Type ≠ Moveable
```

### Type 가드의 부재

Misc 아이템은 대부분 `Type = Normal` (73/79, Junk 기준)이다.
`Type = Normal`은 Resource, Tool, Combat 등 다수 대분류와 공유하므로,
Misc 진입은 **다른 대분류 조건 불일치**로만 판정된다.

### 소분류는 단일

Misc 내부에 역할 기반 분할 축이 존재하지 않는다.
모든 아이템이 동일한 역할("비기능 물리 아이템")을 수행한다.
테마 분류(장난감/식기/문구)는 원칙 1 위반.

---

## 9-A. 비활성 물체 (Inert)

**핵심 질문**: 게임 내 기능이 없는 물리적 오브젝트인가?

### 필수 증거 (AND 결합)

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `≠ Weapon` | Combat 제외 |
| **AND** Type | `≠ Food` | Consumable 제외 |
| **AND** Type | `≠ Literature` | Literature 제외 |
| **AND** Type | `≠ Map` | Literature 제외 |
| **AND** Type | `≠ Clothing` | Wearable 제외 |
| **AND** Type | `≠ Radio` | Tool 제외 |
| **AND** Type | `≠ Container` | Tool.Storage 제외 |
| **AND** Type | `≠ Key` | Tool.Security 제외 |
| **AND** Type | `≠ Moveable` | Furniture 제외 |
| **AND** Type | `≠ Drainable` (단독) | 단, MechanicsItem=TRUE면 Vehicle |
| **AND** MechanicsItem | `≠ TRUE` 또는 `not exists` | Vehicle 제외 |
| **AND** Recipe role | `≠ input` (해당 대분류 없음) | Resource 제외 |
| **AND** Recipe role | `≠ keep/require` (해당 대분류 없음) | Tool 제외 |
| **AND** 의료 필드 | 모두 `not exists` | Consumable.3-C 제외 |
| **AND** 무기 필드 | 모두 `not exists` | Combat 제외 |

### 실질 판정

위 조건은 논리적으로 정확하지만 실제 구현에서는:

**다른 8개 대분류의 자동 분류 엔진이 모두 태그를 부여하지 않은 아이템 → 9-A**

즉, 9-A는 분류 파이프라인의 **최종 폴백(fallback)**이다.

### 금지

| 증거 | 이유 |
|------|------|
| DisplayCategory = Junk | 금지 증거 |
| DisplayCategory = Sports | 금지 증거 |
| DisplayCategory = Entertainment | 금지 증거 |
| DisplayCategory = Household | 금지 증거 |
| DisplayName 추론 | 이름 추론 금지 |
| Weight 수치 비교 | 수치 비교 금지 |

### 경계 아이템 처리

일부 아이템은 자동 분류에서 다른 대분류에 태그가 부여될 수 있으나,
해당 태그가 유일한 분류이고 Misc 5개 부정 조건을 만족하면 9-A에도 다중 태그 가능.

그러나 원칙적으로 **Misc 진입 = 다른 대분류 미진입**이므로 다중 태그는 발생하지 않아야 한다.

> ⚠️ **다중 태그 정책**: Misc는 다중 태그의 대상이 아님.
> 다른 대분류에 하나라도 태그가 부여되면 Misc에는 진입하지 않는다.

### 예시 아이템

**장난감/게임용품:**
- Doll, Toy Bear, Toy Car, Yoyo, Playing Cards, Dice, Chess Pieces

**식기/주방용품:**
- Plate, Chopsticks, Straw, Plastic Tray

**문구/사무용품:**
- Stapler, Hole Puncher, Crayons, Credit Card

**전자/가치품:**
- Camera, Disposable Camera, Camera Film, Money

**위생/외모:**
- Cologne, Perfume, Razor, Comb, Toothbrush

**기념품/소지품:**
- Frame, Locket, Wallet, NPC 사진류

**기타 잡물:**
- Bell, Button, Cork, Pine Cone, Toilet Paper, Broken Glass

### 바닐라 현황 (Junk 기준)

- Type = Normal: 73개 (92%)
- Type = Moveable: 4개 (5%) — ⚠️ Furniture 대분류로 이동해야 할 수 있음
- Type = Drainable: 2개 (3%) — 소모성 여부 확인 필요
- Tags 존재: 10개 (13%) — BrokenGlass(4), Camera(3), Write계열(1), Corkscrew(1), Razor(1)

---

## Misc 진입 아이템 중 재검증 필요 항목

### Type = Moveable인 Junk 아이템 (4개)

`Type = Moveable`이면 Furniture 대분류 가드에 해당한다.
이 4개 아이템은 Junk(DisplayCategory)에 분류되어 있지만,
Type 기반으로는 Furniture에 진입해야 한다.

> ⚠️ **v0.2에서 해결 필요**: 이 4개 아이템의 정체를 바닐라 데이터에서 확인하고,
> Furniture.7-E(고정물)로 이동하거나 수동 오버라이드로 Misc에 유지할지 결정.

### Type = Drainable인 Junk 아이템 (2개)

`Type = Drainable`은 소모성을 나타낸다.
Consumable 또는 Resource 조건을 충족하는지 재확인 필요.

### Tags가 있는 Junk 아이템

| Tags | 아이템 | 재검증 |
|------|--------|--------|
| Camera(3) | Camera, High-end Camera, Disposable Camera | 기능 없음 확인 → Misc 유지 |
| BrokenGlass(4) | Broken Glass ×4 | 기능 없음 확인 → Misc 유지 |
| Write계열(1) | (확인 필요) | Tool 진입 여부 확인 |
| Corkscrew(1) | Corkscrew | Tool.1-B(분해/개방) 진입 여부 확인 |
| Razor(1) | Razor | 기능 없음 확인 → Misc 유지 |

> ⚠️ **Corkscrew 주의**: Corkscrew 태그가 Tool 증거표의 허용 Tags에 없으므로 현재는 Misc에 잔류.
> 그러나 "열기" 기능이 있다면 Tool.1-B에 진입해야 할 수 있다. 바닐라 행동 확인 필요.

---

## 분류 흐름도

```
아이템 입력
    │
    ▼
┌──────────────────────────────────┐
│ 다른 8개 대분류 중               │──Yes──▶ 해당 대분류로 분류
│ 하나라도 태그 부여?              │
└──────────────────────────────────┘
    │ No
    ▼
┌──────────────────────────────────┐
│ blocklist (시스템 아이템)?       │──Yes──▶ 분류 제외
└──────────────────────────────────┘
    │ No
    ▼
  9-A (비활성 물체) ← 최종 폴백
```

---

## 바닐라 데이터 확인 결과 (v0.1)

| 항목 | 확인 결과 |
|------|-----------|
| Junk DisplayCategory | 79개 |
| Junk 외 Misc 예상 | ~36개 (Sports 9, Entertainment 5, Household 일부, 기타) |
| Type = Normal (Junk) | 73개 (92%) |
| Type = Moveable (Junk) | 4개 — Furniture 이동 후보 |
| Type = Drainable (Junk) | 2개 — 재검증 필요 |
| Tags 존재 (Junk) | 10개 (13%) |

### Misc에 흡수될 다른 DisplayCategory 아이템

| DisplayCategory | 아이템 수 | Misc 진입 조건 |
|-----------------|-----------|----------------|
| Sports | 9개 | Type=Normal(8), 기능 없음 → 9-A |
| Entertainment | 5개 | Type=Normal(5), 기능 없음 → 9-A |
| Household (일부) | ~일부 | 기능 없는 아이템만 |

> ⚠️ **Sports 내 Dart**: `Type = Weapon`(1개). Combat 대분류 가드에 해당하므로 Misc에 진입하지 않음.
> → Combat 소분류에서 처리 필요 (2-J 투척/폭발 수동 오버라이드 대상 검토).

> ⚠️ **Household 내 무기**: BluePen, Umbrella 등 `Type = Weapon`(4개). Combat 대분류 가드에 해당.
> 나머지 Household 아이템 중 기능 없는 것만 Misc 진입.

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | 2026-02-15 | 초안 작성. 소분류 1개(9-A) 정의. 최종 폴백 분류 전략 확립. 재검증 필요 항목 식별 (Type=Moveable 4개, Type=Drainable 2개, Corkscrew 태그). |
