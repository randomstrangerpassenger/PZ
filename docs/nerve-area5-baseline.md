# Nerve Area 5 기준선 문서 (v0.1-baseline)

> **목적**: Area 5 컴포넌트가 **무엇을 하고, 무엇을 안 하는지** 증명 가능한 형태로 고정

---

## 컴포넌트 목록

### 1. InventoryGuard

| 항목 | 내용 |
|------|------|
| **파일** | `area5/InventoryGuard.lua` |
| **역할** | `ISInventoryPage.refreshBackpack` 틱 단위 coalesce |
| **막는 체감 붕괴** | 동일 틱 내 refreshBackpack 중복 호출로 인한 UI 프리즈 |
| **개입 없는 조건** | `inventoryGuard.enabled = false` / 틱 내 첫 호출 / `ISInventoryPage` 미존재 시 fail-soft |

**의미 불변 보장**:
- ✅ 데이터는 즉시 반영
- ✅ 시각(렌더)만 틱 단위 합치기
- ❌ UI 순서 변경 없음
- ❌ 표시 정보 변경/축소 없음
- ❌ 사용자 입력 무시 없음

**기술 특징**:
- WeakRef 레지스트리 (메모리 누수 방지)
- flush 시 원본 직접 호출 (래퍼 우회 → 루프 방지)

---

### 2. UIRefreshCoalescer

| 항목 | 내용 |
|------|------|
| **파일** | `area5/UIRefreshCoalescer.lua` |
| **역할** | 범용 UI 갱신 합치기 |
| **막는 체감 붕괴** | 대량 UI 패널 동시 갱신으로 인한 프레임 드롭 |
| **개입 없는 조건** | `uiCoalesce.enabled = false` / 틱 내 첫 요청 / overflow 시 bypass |

**overflow 정책**:
- ✅ `bypass`: coalesce 포기 후 즉시 실행 (의미 보존)
- ❌ `defer`: 금지 (틱 넘김 = 캐시)
- ❌ `drop`: 금지 (UI 누락 = 의미 변화)

---

### 3. ContainerScanDedup

| 항목 | 내용 |
|------|------|
| **파일** | `area5/ContainerScanDedup.lua` |
| **역할** | 컨테이너 스캔 중복 제거 |
| **막는 체감 붕괴** | 동일 틱 내 동일 컨테이너 중복 스캔으로 인한 연산 낭비 |
| **개입 없는 조건** | `containerScan.enabled = false` / 틱 내 첫 스캔 |

**안전 원칙**:
- 틱 경계에서 초기화 (캐시 금지)

---

### 4. Area5Coordinator

| 항목 | 내용 |
|------|------|
| **파일** | `area5/Area5Coordinator.lua` |
| **역할** | Area 5 통합 조율 |
| **막는 체감 붕괴** | 컴포넌트 조합 효과 |
| **개입 없는 조건** | `area5.enabled = false` |

**지연 초기화**:
- InventoryGuard init 실패 시 재시도 (최대 3회)

---

## 관측 지표 (Echo 연동)

| 지표 | 함수 |
|------|------|
| 래퍼 호출 수 | `Area5Stats.wrapperCalls` |
| 차단된 호출 수 | `Area5Stats.blockedCalls` |
| 원본 호출 수 | `Area5Stats.originalCalls` |
| 플러시된 pending | `Area5Stats.pendingFlushed` |
| 스캔 요청 수 | `Area5Stats.scanRequests` |
| 스캔 스킵 수 | `Area5Stats.scanSkipped` |
| overflow 횟수 | `Area5Stats.overflowCount` |

---

## 기준선 스냅샷

- **버전**: v0.1.0
- **태그**: v0.1-baseline
- **날짜**: 2026-01-11
