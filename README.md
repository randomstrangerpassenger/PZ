# Echo Profiler

Project Zomboid용 Pulse 모드 로더 위에서 동작하는 프로파일링 도구

> **핵심 철학**: "패치가 아닌 관찰" - 게임 로직을 변경하지 않고 성능 병목을 발견하는 센서 역할

## 기능

### v0.2.0
- ✅ **Tick 시간 측정** - 평균, 최대 스파이크, 히스토리
- ✅ **Subsystem별 시간 측정** - Render, Simulation, Physics, Zombie AI, Lua
- ✅ **호출 빈도 데이터 수집**
- ✅ **Heavy Function Top N 랭킹**
- ✅ **히스토그램** - P50/P95/P99 백분위수 (개선된 정확도)
- ✅ **스파이크 감지** - 조정 가능한 임계값
- ✅ **Lua 프로파일링** - On-Demand 함수별 통계
- ✅ **메모리 프로파일링** - 힙 사용량, GC 통계
- ✅ **JSON 자동 리포트 생성**
- ✅ **성능 권장사항** - 자동 분석 및 제안

## 설치

1. `Echo.jar`를 Pulse mods 폴더에 복사
2. 게임 실행

## 콘솔 명령어

| 명령어 | 설명 |
|--------|------|
| `/echo help` | 도움말 표시 |
| `/echo enable` | 프로파일링 시작 (통계 초기화) |
| `/echo disable` | 프로파일링 중지 |
| `/echo status` | 현재 상태 출력 |
| `/echo report` | 콘솔에 리포트 출력 |
| `/echo report json` | JSON 파일로 저장 |
| `/echo reset` | 통계 초기화 |
| `/echo lua on` | Lua 프로파일링 활성화 |
| `/echo lua off` | Lua 프로파일링 비활성화 |
| `/echo config threshold <ms>` | 스파이크 임계값 설정 |
| `/echo memory` | 메모리 상태 출력 |
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

// 통계 유지하면서 재활성화
profiler.enable(false); // resetStats = false
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

### 메모리 프로파일링

```java
import com.echo.measure.MemoryProfiler;

// 힙 사용량 조회
long heapUsed = MemoryProfiler.getHeapUsed();
double usagePercent = MemoryProfiler.getHeapUsagePercent();

// GC 정보
long gcCount = MemoryProfiler.getTotalGcCount();
long gcTime = MemoryProfiler.getTotalGcTimeMs();

// 상태 출력
MemoryProfiler.printStatus();
```

## JSON 리포트 구조

```json
{
  "echo_report": {
    "version": "0.1.1",
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
    "memory": {
      "heap": { "used_mb": 512, "max_mb": 2048, "usage_percent": 25.0 },
      "gc": { "total_count": 45, "total_time_ms": 320 }
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

### 사전 요구사항

> **중요:** 빌드 전에 `libs/` 폴더에 다음 파일들이 필요합니다:
> - `Pulse.jar` - Pulse 모드 로더 JAR (빌드된 버전)
> - `pz-stubs.jar` - Project Zomboid 클래스 스텁

#### Stub JAR 생성 방법

`pz-stubs.jar`는 Project Zomboid의 게임 클래스를 컴파일시에만 참조하기 위한 스텁 파일입니다:

1. **자동화 도구 사용** (권장):
   ```bash
   # Pulse 저장소의 stub 생성 스크립트 사용
   java -jar pulse-stub-generator.jar "C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid"
   ```

2. **수동 생성**:
   - Project Zomboid 설치 폴더에서 `zombie/*.class` 파일들을 추출
   - 필요한 클래스 시그니처만 포함하는 빈 구현체로 JAR 생성

3. **Pulse 저장소에서 복사**:
   - Pulse 빌드 시 생성된 `pz-stubs.jar` 사용

### 빌드 명령

```bash
./gradlew build
```

빌드 결과물: `build/libs/Echo-0.1.1.jar`

## 요구사항

- Project Zomboid (Build 41+)
- Pulse Mod Loader v1.0.0+
- Java 17+

## 변경 로그

### v0.2.0
- **버그 수정**: `LuaFunctionStats.maxMicros` 스레드 안전성 (AtomicLong CAS 패턴)
- **버그 수정**: `RollingStats.addSample()` 동기화 추가
- **버그 수정**: `EchoProfiler.getCurrentStackDepth()` 메인 스레드 감지 수정
- **개선**: 전체 버전 통일 (0.2.0)

### v0.1.1
- **버그 수정**: `enable()` 호출 시 통계 자동 초기화 (재활성화 시 데이터 섞임 방지)
- **버그 수정**: `ProfilingFrame.idCounter` 스레드 안전성 개선 (AtomicLong)
- **개선**: `TickHistogram` 백분위수 계산 정확도 향상 (실제 샘플 기반)
- **개선**: `SpikeLog` 임계값 런타임 변경 지원
- **신규**: `MemoryProfiler` - 힙/GC 모니터링
- **신규**: `/echo config threshold <ms>` 명령어
- **신규**: `/echo memory` 명령어

### v0.1.0
- 초기 릴리스

## 라이선스

MIT License

---

**Echo Team** | "Observe, Don't Patch"
