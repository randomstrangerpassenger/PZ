# Echo Profiler

Project Zomboid용 Pulse 모드 로더 위에서 동작하는 프로파일링 도구

> **핵심 철학**: "패치가 아닌 관찰" - 게임 로직을 변경하지 않고 성능 병목을 발견하는 센서 역할

## 기능

### v0.1.0
- ✅ **Tick 시간 측정** - 평균, 최대 스파이크, 히스토리
- ✅ **Subsystem별 시간 측정** - Render, Simulation, Physics, Zombie AI, Lua
- ✅ **호출 빈도 데이터 수집**
- ✅ **Heavy Function Top N 랭킹**
- ✅ **히스토그램** - P50/P95/P99 백분위수
- ✅ **스파이크 감지** - 33ms 임계값 기반 경고
- ✅ **Lua 프로파일링** - On-Demand 함수별 통계
- ✅ **JSON 자동 리포트 생성**
- ✅ **성능 권장사항** - 자동 분석 및 제안

## 설치

1. `Echo.jar`를 Pulse mods 폴더에 복사
2. 게임 실행

## 콘솔 명령어

| 명령어 | 설명 |
|--------|------|
| `/echo help` | 도움말 표시 |
| `/echo enable` | 프로파일링 시작 |
| `/echo disable` | 프로파일링 중지 |
| `/echo status` | 현재 상태 출력 |
| `/echo report` | 콘솔에 리포트 출력 |
| `/echo report json` | JSON 파일로 저장 |
| `/echo reset` | 통계 초기화 |
| `/echo lua on` | Lua 프로파일링 활성화 |
| `/echo lua off` | Lua 프로파일링 비활성화 |
| `/echo test` | 빠른 테스트 실행 |

## API 사용법

### 기본 프로파일링

```java
import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;

// try-with-resources 방식 (권장)
try (var scope = EchoProfiler.getInstance().scope(ProfilingPoint.TICK)) {
    // 게임 틱 로직
}

// 라벨 추가
try (var scope = profiler.scope(ProfilingPoint.ZOMBIE_AI, "pathfinding")) {
    // AI 로직
}
```

### 서브시스템 래핑

```java
import com.echo.pulse.SubsystemProfiler;

// 간편 래퍼
SubsystemProfiler.profileZombieAI(() -> {
    zombie.updateAI();
});

// 라벨 포함
SubsystemProfiler.profileNetwork("packet_send", () -> {
    network.sendPacket(packet);
});
```

### Lua 프로파일링

```java
import com.echo.lua.LuaCallTracker;

// Lua 함수 호출 측정
LuaCallTracker.getInstance().profileFunction("onPlayerUpdate", () -> {
    luaManager.call("onPlayerUpdate", player);
});

// 통계 출력
LuaCallTracker.getInstance().printStats(10);
```

## JSON 리포트 구조

```json
{
  "echo_report": {
    "version": "0.1.0",
    "summary": {
      "total_ticks": 18000,
      "average_tick_ms": 16.2,
      "max_tick_spike_ms": 45.8,
      "performance_score": 87.5
    },
    "tick_histogram": {
      "p50_ms": 12.5,
      "p95_ms": 28.3,
      "p99_ms": 42.1
    },
    "spikes": {
      "total_spikes": 15,
      "worst_spike_ms": 85.2
    },
    "lua_profiling": {
      "total_calls": 50000,
      "top_functions_by_time": [...]
    },
    "recommendations": [
      "Performance looks good!"
    ]
  }
}
```

## 빌드

```bash
./gradlew build
```

빌드 결과물: `build/libs/Echo-0.1.0.jar`

## 요구사항

- Project Zomboid (Build 41+)
- Pulse Mod Loader v1.0.0+
- Java 17+

## 라이선스

MIT License

---

**Echo Team** | "Observe, Don't Patch"
