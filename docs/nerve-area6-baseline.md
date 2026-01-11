# Nerve Area 6 기준선 문서 (v0.1-baseline)

> **목적**: Area 6 컴포넌트가 **무엇을 하고, 무엇을 안 하는지** 증명 가능한 형태로 고정

---

## 컴포넌트 목록

### 1. EventDeduplicator

| 항목 | 내용 |
|------|------|
| **파일** | `area6/EventDeduplicator.lua` |
| **역할** | 틱 단위 이벤트 중복 제거 |
| **막는 체감 붕괴** | 동일 틱 내 동일 이벤트+contextKey 반복 호출로 인한 프레임 드롭 |
| **개입 없는 조건** | `contextKey == nil` / `deduplicateEvents`에 미등록 / `limit` 미초과 / `maxSeenEntriesPerTick` 도달 시 bypass |

**의미 불변 보장**:
- ❌ 이벤트 삭제하지 않음
- ❌ 순서 변경하지 않음  
- ❌ 지연 실행하지 않음
- ✅ 동일 틱 내 중복 경로만 무음 스킵

---

### 2. CascadeGuard

| 항목 | 내용 |
|------|------|
| **파일** | `area6/CascadeGuard.lua` |
| **역할** | 이벤트 연쇄 깊이 관측 |
| **막는 체감 붕괴** | v0.1에서는 없음 (observeOnly 모드) |
| **개입 없는 조건** | `enabled = false` (기본값) / `observeOnly = true` |

**v0.1 상태**:
- 기본 OFF
- 스킵 없이 깊이만 로깅
- `maxObservedDepth`, `depthHistogram` 수집

---

### 3. ContextExtractors

| 항목 | 내용 |
|------|------|
| **파일** | `area6/ContextExtractors.lua` |
| **역할** | 이벤트별 contextKey 추출 |
| **막는 체감 붕괴** | 없음 (데이터 제공만) |
| **개입 없는 조건** | 추출기 미등록 이벤트 → `nil` 반환 → 중복 체크 건너뛰기 |

**안전 원칙**:
- 추출 실패 시 `nil` 반환 (항상 실행 허용)
- `"global"` 폴백 사용 금지 (Entity Event 안전)

---

### 4. Area6Coordinator

| 항목 | 내용 |
|------|------|
| **파일** | `area6/Area6Coordinator.lua` |
| **역할** | Area 6 통합 조율 |
| **막는 체감 붕괴** | 컴포넌트 조합 효과 |
| **개입 없는 조건** | `area6.enabled = false` |

---

## 관측 지표 (Echo 연동)

| 지표 | 함수 |
|------|------|
| 총 이벤트 수 | `EventDeduplicator.getStats().totalCount` |
| 스킵된 이벤트 수 | `EventDeduplicator.getStats().skipCount` |
| 틱당 seenThisTick 엔트리 | `EventDeduplicator.getStats().entryCount` |
| 최대 관측 깊이 | `CascadeGuard.getStats().maxObservedDepth` |
| 깊이 히스토그램 | `CascadeGuard.getStats().depthHistogram` |

---

## 기준선 스냅샷

- **버전**: v0.1.0
- **태그**: v0.1-baseline
- **날짜**: 2026-01-11
