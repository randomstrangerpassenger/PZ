# Iris Furniture(7) 소분류 증거표 (v0.2)

이 문서는 **Furniture 대분류(7)**의 각 소분류별로 사용할 수 있는 증거를 정의한다.

> ⚠️ **v0.2 주요 변경**: v0.1의 5개 소분류(Appliance/Seating/Surface/Storage/Fixture)를 단일 소분류로 통합.
> 사유: 소분류를 구분하는 Evidence 필드가 존재하지 않으며, 수동 오버라이드 100% 의존은 Evidence 시스템 철학 위반.

---

## 증거 우선순위 원칙

1. **1차**: Item Script 필드 (Type = Moveable)
2. **최후**: 수동 오버라이드 (경계 아이템 시에만)

---

## Furniture 분류의 핵심 원칙

### Type = Moveable이 유일한 가드

Furniture 대분류 진입은 `Type = Moveable`이 기본이자 유일한 Evidence.

> ⚠️ **바닐라 데이터**: Furniture 137개 중 137개가 `Type = Moveable` (100%).

### DisplayCategory = Furniture는 금지 증거

`DisplayCategory`는 표시용이며 분류 증거로 사용 불가.

### 소분류 분할하지 않는 근거

Furniture의 모든 아이템은 동일한 필드 구조를 공유한다:
- `Type = Moveable`
- `Weight = 0.5` (136/137)
- `WorldObjectSprite` (136/137)

소분류를 구분할 수 있는 전용 필드가 존재하지 않는다.
BodyLocation(Wearable), Categories(Combat), 구동계 필드(Vehicle)와 같은
**Evidence 기반 분할 축이 없다.**

분할 축이 없는 상태에서 소분류를 나누면:
- 수동 오버라이드 100% 의존 → Evidence 시스템 위반
- 사람의 의미 판단 개입 → Allowlist 철학 충돌
- B42에서 신규 Moveable 추가 시 수동 분류 부채 누적

따라서 **Misc(9-A)와 동일한 원칙을 적용**: Evidence 없으면 분할하지 않는다.

### B42 확장 대비

B42에서 Moveable 아이템에 상호작용 필드(예: 조리 가능, 수납 용량 등)가 추가되면,
그 시점에서 Evidence 기반으로 소분류를 분리한다.
지금 없는 Evidence로 미리 쪼개는 것은 구조 부채다.

---

## 7-A. 배치물 (Placed)

**핵심 질문**: 월드에 배치되는 이동 가능 오브젝트인가?

### 필수 증거

| 증거 | 조건 | 비고 |
|------|------|------|
| Type | `= Moveable` | 유일한 가드 |

### 금지

| 증거 | 이유 |
|------|------|
| DisplayCategory = Furniture | 금지 증거 |
| DisplayName 추론 | 이름 추론 금지 |
| WorldObjectSprite 패턴 매칭 | 패턴 불규칙, 신뢰도 낮음 |
| Weight 수치 비교 | 수치 비교 금지 |

### 예시 아이템

- 오븐 (Green Oven)
- 접이식 의자 (Folding Chair)
- 테이블 (Round Table)
- 벽 로커 (Green Wall Locker)
- 그림 (Paintings)
- 묘비 (Gravestones)
- 램프 (Lamp)
- 도로 차단물 (Road Cone)

### 바닐라 현황

- 총 아이템: **137개**
- Type = Moveable: 137개 (100%)

---

## Tool.Storage와의 경계

| 분류 | Type 가드 | 역할 |
|------|-----------|------|
| Furniture.7-A | `Type = Moveable` | 월드에 배치되는 오브젝트 |
| Tool.Storage | `Type = Container` | 플레이어가 휴대하는 수납 인터페이스 |

Type 가드로 자연 분리. 경계 충돌 없음.

---

## Misc와의 경계

| 분류 | Type 가드 | 역할 |
|------|-----------|------|
| Furniture.7-A | `Type = Moveable` | 배치 기능 있음 |
| Misc.9-A | `Type = Normal` (대부분) | 배치 없음 (5개 부정 조건) |

Misc 진입 조건 중 "배치 없음"에 의해 `Type = Moveable`은 Misc에 진입하지 않는다.
Type 가드로 자연 분리. 경계 충돌 없음.

---

## 분류 흐름도

```
아이템 입력
    │
    ▼
┌─────────────────────┐
│ Type = Moveable ?   │──No───▶ (Furniture 대분류 아님)
└─────────────────────┘
    │ Yes
    ▼
  7-A (배치물)
```

---

## 바닐라 데이터 확인 결과 (v0.2)

| 항목 | 확인 결과 |
|------|-----------|
| Type = Moveable | 137개 (100%) |
| DisplayCategory = Furniture | 137개 (100%) — 금지 증거 |
| Weight = 0.5 | 136개 (99%) — 분류 증거 아님 |
| WorldObjectSprite 존재 | 136개 (99%) — 분류 증거 아님 |
| DisplayName = "Moveable" (이름 미설정) | 11개 |

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| 0.1 | 2026-02-15 | 초안 작성. 소분류 5개(7-A~7-E). 수동 오버라이드 중심. |
| 0.2 | 2026-02-15 | 전면 재설계. 5개 소분류 → 단일 소분류(7-A Placed)로 통합. Evidence 없는 분할 제거. Phase 2 철학 준수. |
