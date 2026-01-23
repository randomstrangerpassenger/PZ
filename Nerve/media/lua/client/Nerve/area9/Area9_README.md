# Area 9: Network/Multiplayer Stability

## Overview

Area 9 provides **Network/Multiplayer stability** for the Nerve module. It monitors network boundary handlers for potential issues and responds by **withdrawing** (pass-through) rather than blocking or modifying event flow.

## Constitution (Immutable)

### ❌ FORBIDDEN (Echo 분석 구조 침투 금지)

| 카테고리 | 금지 항목 |
|----------|-----------|
| 분석 구조 | TrendAnalysis, QualityScore, BottleneckDetector |
| 정책화 | Priority 계산, Ratio 판정, weight/가중치 |
| 모듈 참조 | `require "Echo/..."`, `Echo.*` |
| 패턴 | 복합 조건 판정, 시계열 분석, 자동 분석기 |

### ✅ ALLOWED

- 단일 플래그 체크 (`hasIncident`, `isQuarantined`)
- 정수 enum (`categoryId`, `reasonCode`)
- tick-local 카운터 (wipe 필수)
- 고정 크기 링버퍼 (정수만)
- observe/guard 모드 (opt-in)

### 필수 원칙 (4개)

1. **필수-1**: tickId 갱신은 Area9TickCtx에서만
2. **필수-2**: endpoints 폐쇄 목록 (네트워크 훅만)
3. **필수-3**: incident 조건은 단일 플래그만
4. **필수-4**: quarantine 키 전역 금지

## Files

| File | Purpose |
|------|---------|
| `Area9Guard.lua` | CONSTITUTION 가드, 금지 키워드 |
| `Area9TickCtx.lua` | Per-tick 컨텍스트 (tickId 단일 진실) |
| `Area9Install.lua` | 래핑/언래핑/무결성 체크 |
| `Area9InstallState.lua` | Applied/Partial/Bypassed + DisabledReason |
| `Area9Forensic.lua` | 링버퍼 (정수만) |
| `Area9Reentry.lua` | Re-entrancy 감지 (표시만) |
| `Area9Duplicate.lua` | 중복 카운트 (스킵 금지) |
| `Area9Shape.lua` | observe/guard 모드 |
| `Area9Depth.lua` | 히스테리시스 |
| `Area9Call.lua` | callFast/callGuarded 분리 |
| `Area9Quarantine.lua` | 1틱 철수 |
| `Area9Dispatcher.lua` | 고정 실행 순서 |

## Configuration

Located in `media/lua/shared/Nerve/NerveConfig.lua`:

```lua
NerveConfig.area9 = {
    enabled = false,  -- DEFAULT OFF
    endpoints = { "OnClientCommand", "OnServerCommand" },
    optIn = { guardedPcall = {}, quarantine = {}, guards = {} },
}
```
