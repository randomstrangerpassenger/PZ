# Echo Profiler v0.8.0

Project Zomboid용 성능 프로파일링 도구 - Pulse 모드 로더와 네이티브 통합

> **핵심 철학**: "패치가 아닌 관찰" - 게임 로직을 변경하지 않고 성능 병목을 발견하는 센서 역할

## ✨ v0.8.0 주요 기능

- **Pulse Native UI**: `HUDOverlay.HUDLayer` 상속으로 Pulse UI 시스템과 완전 통합
- **Zero-Allocation 렌더링**: `String.format` 제거, `StringBuilder` 재사용으로 GC 압박 최소화
- **SPI Provider**: `IProfilerProvider` 구현으로 Pulse 생태계와 표준화된 연동
- **HTTP 모니터 API**: 외부 도구에서 실시간 메트릭 조회 가능
- **다중 리포트 형식**: JSON, CSV, HTML 지원

---

## 🎯 주요 기능

| 기능 | 설명 |
|------|------|
| ⏱️ **실시간 HUD** | FPS, Frame/Tick 시간, Top 3 핫스팟 (F6 토글) |
| 📊 **상세 패널** | 5초/60초 롤링 윈도우, 스파이크 로그 (F8 토글) |
| 📈 **틱 히스토그램** | P50/P95/P99 백분위수 + Jank 비율 |
| 🔥 **스파이크 감지** | 임계값 설정 (기본 33.33ms) + 스택 캡처 옵션 |
| 🌙 **Lua 프로파일링** | 함수별/이벤트별 시간·호출 통계 (On-Demand) |
| 💾 **다중 리포트** | JSON, CSV, HTML 형식 지원 |
| 🖥️ **HTTP 모니터** | REST API로 외부 도구 연동 |
| 🔌 **Pulse SPI** | 표준 프로파일러 인터페이스 제공 |

---

## 🚀 빠른 시작

### 설치

1. `Echo-0.8.0.jar`를 Pulse mods 폴더에 복사
   - Windows: `%USERPROFILE%/.pulse/mods/`
   - Linux/macOS: `~/.pulse/mods/`
2. PulseLauncher로 게임 실행

### 키보드 단축키

| 키 | 동작 |
|----|------|
| **F6** | HUD 토글 (FPS, 프레임/틱 시간, 핫스팟) |
| **F7** | 프로파일링 On/Off |
| **F8** | 상세 패널 토글 |

---

## 📊 리포트 수집 가이드

### Step 1: 프로파일링 시작
```
/echo enable
```
또는 **F7** 키

### Step 2: 게임 플레이
- 최소 1-2분간 일반적인 플레이
- 렉이 발생하는 상황 재현

### Step 3: 리포트 생성
```
/echo report          # 콘솔에 출력
/echo report json     # JSON 파일 저장
/echo report csv      # CSV 파일 저장
/echo report html     # HTML 파일 저장 (시각화 포함)
```

리포트 저장 위치: `./echo_reports/`

---

## 📈 리포트 해석 가이드

### 핵심 지표

| 지표 | 좋음 | 주의 | 위험 |
|------|------|------|------|
| **평균 틱** | < 16ms | 16-33ms | > 33ms |
| **P95** | < 33ms | 33-50ms | > 50ms |
| **Jank 비율** | < 5% | 5-15% | > 15% |
| **스파이크** | < 10 | 10-30 | > 30 |

### 서브시스템 분석

```
📈 SUBSYSTEM BREAKDOWN
───────────────────────────────────────────────────────
  Zombie AI       │ avg:  2.45 ms │ max: 15.20 ms │ calls: 12,000
  Rendering       │ avg:  8.12 ms │ max: 25.00 ms │ calls: 18,000
  Lua Event       │ avg:  0.35 ms │ max:  5.80 ms │ calls: 50,000
```

- **높은 avg**: 해당 서브시스템이 전반적으로 느림
- **높은 max**: 간헐적 스파이크 발생 (스파이크 로그 확인)
- **높은 calls**: 호출 빈도 최적화 필요

---

## 🎮 콘솔 명령어

### 기본 명령어
| 명령어 | 설명 |
|--------|------|
| `/echo help` | 도움말 표시 |
| `/echo enable` | 프로파일링 시작 |
| `/echo disable` | 프로파일링 중지 |
| `/echo status` | 현재 상태 출력 (Pulse 통합 포함) |
| `/echo report [json\|csv\|html]` | 리포트 생성 |
| `/echo reset` | 통계 초기화 |

### Lua 프로파일링
| 명령어 | 설명 |
|--------|------|
| `/echo lua on` | Lua 프로파일링 활성화 |
| `/echo lua off` | Lua 프로파일링 비활성화 |

### 설정
| 명령어 | 설명 |
|--------|------|
| `/echo config` | 현재 설정 표시 |
| `/echo config set threshold <ms>` | 스파이크 임계값 설정 |
| `/echo memory` | 메모리 상태 출력 |

### 고급 기능
| 명령어 | 설명 |
|--------|------|
| `/echo stack on` | 스파이크 스택 캡처 활성화 ⚠️ (성능 비용 큼) |
| `/echo overhead` | 프로파일러 자체 오버헤드 측정 |
| `/echo monitor start [port]` | HTTP 모니터 서버 시작 (기본: 8765) |
| `/echo monitor stop` | HTTP 모니터 서버 중지 |
| `/echo test` | 빠른 기능 테스트 |

---

## 🖥️ HTTP 모니터 API

HTTP 서버 시작: `/echo monitor start` (기본 포트: 8765)

### 엔드포인트

| Endpoint | 설명 |
|----------|------|
| `GET /api/status` | 프로파일러 상태 (enabled, lua_profiling, session_duration) |
| `GET /api/summary` | 틱 요약 (total_ticks, average_ms, max_ms, rolling_stats) |
| `GET /api/histogram` | 틱 분포 (buckets, counts, percentiles) |
| `GET /api/spikes` | 최근 스파이크 목록 |
| `GET /api/memory` | 메모리 상태 (heap, used, free, gc_count) |

### 사용 예시
```bash
curl http://localhost:8765/api/summary
```

```json
{
  "total_ticks": 3600,
  "average_ms": 15.23,
  "max_ms": 45.67,
  "last_5s": {
    "avg_ms": 14.85,
    "max_ms": 22.10,
    "samples": 300
  }
}
```

---

## 🔧 API 사용법 (모드 개발자용)

### 기본 프로파일링

```java
import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;

// try-with-resources 방식 (권장, Zero-Allocation)
try (var scope = EchoProfiler.getInstance().scope(ProfilingPoint.TICK)) {
    // 게임 틱 로직
}

// 라벨 추가
try (var scope = profiler.scope(ProfilingPoint.ZOMBIE_AI, "pathfinding")) {
    // AI 로직
}

// Raw API (극한 성능, 완전 Zero-Allocation)
long start = profiler.startRaw(ProfilingPoint.RENDER);
try {
    // 렌더링 로직
} finally {
    profiler.endRaw(ProfilingPoint.RENDER, start);
}
```

### Lua 프로파일링

```java
import com.echo.lua.LuaCallTracker;

LuaCallTracker.getInstance().profileFunction("onPlayerUpdate", () -> {
    luaManager.call("onPlayerUpdate", player);
});

// 이벤트 프로파일링
LuaCallTracker.getInstance().profileEvent("OnZombieDead", handlerCount, () -> {
    events.trigger("OnZombieDead", zombie);
});
```

### 프로파일링 포인트

| 카테고리 | 포인트 |
|----------|--------|
| **CORE** | `TICK`, `FRAME` |
| **SUBSYSTEM** | `RENDER`, `RENDER_WORLD`, `RENDER_UI`, `SIMULATION`, `PHYSICS`, `ZOMBIE_AI`, `NPC_AI`, `NETWORK`, `AUDIO`, `CHUNK_IO` |
| **LUA** | `LUA_EVENT`, `LUA_FUNCTION`, `LUA_GC` |
| **CUSTOM** | `MOD_INIT`, `MOD_TICK`, `CUSTOM_1` ~ `CUSTOM_5` |
| **INTERNAL** | `ECHO_OVERHEAD` |

---

## ⚙️ 설정 파일

설정 파일 위치: `./config/echo.json`

```json
{
  "spikeThresholdMs": 33.33,
  "luaProfilingDefault": false,
  "autoSaveReports": true,
  "reportDirectory": "./echo_reports",
  "stackCaptureEnabled": false,
  "debugMode": false,
  "topNFunctions": 10
}
```

---

## 🏗️ 빌드

### 사전 요구사항

> **중요:** 단독 빌드 시 `libs/` 폴더에 다음 파일들이 필요합니다:
> - `pulse-api.jar` - Pulse API JAR
> - `pz-stubs.jar` - Project Zomboid 클래스 스텁 (선택사항)

### 빌드 명령

```bash
./gradlew build
```

빌드 결과물: `build/libs/Echo-0.8.0.jar`

### 멀티프로젝트 빌드 (권장)

PZ 루트에서 빌드 시 자동으로 `pulse-api`, `Pulse` 프로젝트 의존성 해결:

```bash
cd /path/to/PZ
./gradlew :Echo:build
```

---

## 📋 요구사항

- Project Zomboid (Build 41+)
- Pulse Mod Loader v0.8.0+
- Java 17+

---

## 🔌 Pulse SPI 통합

Echo는 Pulse의 SPI (Service Provider Interface)를 통해 표준화된 프로파일러로 동작합니다.

```java
// Pulse에서 Echo 프로파일러 조회
IProfilerProvider profiler = Pulse.getProviderRegistry()
    .getFirst(IProfilerProvider.class);

if (profiler != null) {
    profiler.startProfiling();
    double fps = profiler.getCurrentFps();
    double tickMs = profiler.getAverageTickTimeMs();
}
```

---

## 📝 변경 로그

자세한 변경 사항은 [CHANGELOG.md](CHANGELOG.md)를 참조하세요.

### v0.8.0 (2025-12-09)
- 🚀 **Pulse Native UI 통합**: `HUDOverlay.HUDLayer` 상속
- ⚡ **Zero-Allocation 렌더링**: HUD에서 GC 압박 제거
- 🔌 **SPI Provider 구현**: `IProfilerProvider` 표준 인터페이스
- 📡 **HTTP Monitor API**: CORS 지원, 5개 엔드포인트
- 📄 **다중 리포트 형식**: JSON, CSV, HTML 지원

### v0.7.0 (2025-12-08)
- 🎉 **첫 공개 릴리스**
- 핵심 프로파일링 엔진 구현
- RollingStats/SpikeLog 구현
- 메타 프로파일링 (오버헤드 측정)
- Jank 비율 추적

---

## 📜 라이선스

MIT License

---

**Echo Team** | "Observe, Don't Patch"
