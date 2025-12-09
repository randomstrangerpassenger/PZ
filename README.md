# Echo Profiler

Project Zomboid용 Pulse 모드 로더 위에서 동작하는 프로파일링 도구

> **핵심 철학**: "패치가 아닌 관찰" - 게임 로직을 변경하지 않고 성능 병목을 발견하는 센서 역할

## 주요 기능 (v1.0.0)

| 기능 | 설명 |
|------|------|
| ⏱️ **실시간 HUD** | FPS, Frame/Tick 시간, Top 3 핫스팟 (F6 토글) |
| 📊 **상세 패널** | 5초/60초 윈도우, 스파이크 로그, Lua 상태 (F8 토글) |
| 📈 **히스토그램** | P50/P95/P99 백분위수 + Jank 비율 |
| 🔥 **스파이크 감지** | 임계값 설정 + 스택 캡처 옵션 |
| 🌙 **Lua 프로파일링** | 함수별 시간/호출 통계 |
| 💾 **다중 리포트** | JSON, CSV, HTML 형식 |
| 🖥️ **HTTP 모니터** | 실시간 메트릭 API |

## 빠른 시작

### 설치

1. `Echo-1.0.0.jar`를 Pulse mods 폴더에 복사
2. PulseLauncher로 게임 실행

### 키보드 단축키

| 키 | 동작 |
|----|------|
| **F6** | HUD 토글 (FPS, 프레임/틱 시간, 핫스팟) |
| **F7** | 프로파일링 On/Off |
| **F8** | 상세 패널 토글 |

## 리포트 수집 가이드

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
/echo report html     # HTML 파일 저장
```

리포트 저장 위치: `./echo_reports/`

## 리포트 해석 가이드

### 핵심 지표

| 지표 | 좋음 | 주의 | 위험 |
|------|------|------|------|
| **평균 틱** | < 16ms | 16-33ms | > 33ms |
| **P99** | < 33ms | 33-50ms | > 50ms |
| **Jank 60fps** | < 5% | 5-15% | > 15% |
| **스파이크** | < 10 | 10-30 | > 30 |

### 서브시스템 분석

```
📊 SUBSYSTEMS
──────────────────────────────────────────────────
  ZOMBIE_AI     calls:  12,000  avg:  2.45ms  max: 15.20ms
  RENDER        calls:  18,000  avg:  8.12ms  max: 25.00ms
  LUA_EVENT     calls:  50,000  avg:  0.35ms  max:  5.80ms
```

- **높은 avg**: 해당 서브시스템이 전반적으로 느림
- **높은 max**: 간헐적 스파이크 발생 (스파이크 로그 확인)
- **높은 calls**: 호출 빈도 최적화 필요

### 권장사항 예시

```
⚠️ RECOMMENDATIONS
──────────────────────────────────────────────────
  🔴 High tick time detected (avg: 28.5ms)
  🟡 Zombie AI spike: 45.2ms (consider reducing zombie count)
  🟡 Lua functions taking 15% of tick time
```

## 콘솔 명령어

### 기본 명령어
| 명령어 | 설명 |
|--------|------|
| `/echo help` | 도움말 표시 |
| `/echo enable` | 프로파일링 시작 |
| `/echo disable` | 프로파일링 중지 |
| `/echo status` | 현재 상태 출력 |
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

### 고급 기능 (Phase 4)
| 명령어 | 설명 |
|--------|------|
| `/echo stack on` | 스파이크 스택 캡처 활성화 ⚠️ |
| `/echo overhead` | 프로파일러 오버헤드 측정 |
| `/echo monitor start [port]` | HTTP 모니터 서버 시작 |
| `/echo test` | 빠른 기능 테스트 |

> ⚠️ 스택 캡처는 성능 비용이 크므로 디버깅 시에만 사용

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

### Lua 프로파일링

```java
import com.echo.lua.LuaCallTracker;

LuaCallTracker.getInstance().profileFunction("onPlayerUpdate", () -> {
    luaManager.call("onPlayerUpdate", player);
});
```

## 빌드

### 사전 요구사항

> **중요:** 빌드 전에 `libs/` 폴더에 다음 파일들이 필요합니다:
> - `Pulse.jar` - Pulse 모드 로더 JAR
> - `pz-stubs.jar` - Project Zomboid 클래스 스텁

### 빌드 명령

```bash
./gradlew build
```

빌드 결과물: `build/libs/Echo-1.0.0.jar`

## 요구사항

- Project Zomboid (Build 41+)
- Pulse Mod Loader v1.0.0+
- Java 17+

## 변경 로그

자세한 변경 사항은 [CHANGELOG.md](CHANGELOG.md)를 참조하세요.

### v1.0.0 (2025-12-08)
- 🎉 **안정 릴리스**
- RenderHelper 리플렉션 캐싱 (성능 대폭 개선)
- RollingStats/SpikeLog 버그 수정
- HTTP 모니터 서버
- 메타 프로파일링 (오버헤드 측정)
- Jank 비율 추적

## 라이선스

MIT License

---

**Echo Team** | "Observe, Don't Patch"
