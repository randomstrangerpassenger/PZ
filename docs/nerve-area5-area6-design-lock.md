# Nerve Area 5·6 Design Lock (v1.0)

> **상태**: 🔒 **DESIGN LOCKED** — v1.x 기능 동결  
> **날짜**: 2026-01-11

---

## 📜 헌법 준수 선언

본 문서는 Nerve Area 5·6 고도화 작업이 **Pulse 생태계 설계 철학(Philosophy.md)**을 준수함을 선언합니다.

### 준수 원칙

| 원칙 | 준수 상태 |
|------|-----------|
| Hub & Spoke (Area 5↔6 직접 참조 금지) | ✅ `SharedFlags`로 플래그만 공유 |
| 의미 불변 | ✅ 삭제/순서변경/지연 없음 |
| opt-in 기본 OFF | ✅ sustainedPressure, earlyExit 기본 OFF |
| fail-soft | ✅ 모든 컴포넌트 pcall/비활성화 시 통과 |
| Echo 관측 → Nerve 개입 분리 | ✅ 자체 로그/Stats만 사용 |

---

## 🧩 Phase 1 — Area 6 컴포넌트

| 파일 | 역할 | 기본 상태 |
|------|------|-----------|
| `EventFormClassifier.lua` | 이벤트 형태 분류 (SINGLE/HIGH_FREQ/CASCADE/FRAME_BOUND) | 항상 활성 |
| `SustainedPressureDetector.lua` | Sustained 압력 감지 (상태 플래그만) | **OFF** |
| `EarlyExitHandler.lua` | PASSTHROUGH/ACTIVE/COOLDOWN 상태 머신 | **OFF** |

---

## 🎯 Phase 2 — Area 5 컴포넌트

| 파일 | 역할 | 기본 상태 |
|------|------|-----------|
| `UIFormClassifier.lua` | UI 형태 분류 (LIST_BULK/TOOLTIP_CASCADE 등) | 항상 활성 |
| `UISustainedDegradationDetector.lua` | UI degradation 감지 (상태 플래그만) | 항상 활성 |
| `SharedFlags.lua` | Area 5↔6 상태 공유 인터페이스 | 항상 활성 |

---

## ❌ 명시적 배제 (위헌 요소)

| 항목 | 상태 |
|------|------|
| Echo 힌트 기반 동적 조정 | ❌ 제외 |
| 이벤트별 중요도/우선순위 | ❌ 제외 |
| 자동 임계값 튜닝 | ❌ 제외 |
| 이벤트 의미 기반 Allowlist | ❌ 제외 |
| Java strong ref 유지 | ❌ 제외 (Fuse 영역) |
| Area 9 (네트워크) | ❌ 제외 |

---

## 📊 관측 API

```lua
-- Area 6 통계
Nerve.Area6.getStats()
  → formClassifier, pressureDetector, earlyExitHandler, deduplicator, cascadeGuard

-- Area 5 통계
Nerve.Area5.getStats()
  → formClassifier, degradationDetector, sharedFlags, area5Stats

-- 공유 플래그
Nerve.SharedFlags.getAll()
  → area6Sustained, area6EarlyExitState, area5Degraded
```

---

## 🔒 동결 선언

**v1.x 버전에서 본 문서에 명시된 컴포넌트 및 API는 변경하지 않습니다.**

확장이 필요한 경우:
1. 새 Area 번호 할당 (e.g., Area 5.1)
2. 기존 컴포넌트 수정 대신 새 컴포넌트 추가
3. 설정 키 추가는 허용 (기본값 = 기존 동작 유지)
