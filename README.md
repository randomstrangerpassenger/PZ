<<<<<<< HEAD
<p align="center">
  <img src="https://img.shields.io/badge/🔥_PULSE-1.0.0-ff6f00?style=for-the-badge&labelColor=1a1a2e" alt="Pulse Logo"/>
</p>

<h1 align="center">🔥 Pulse</h1>

<p align="center">
  <strong>Next-generation Mixin-based Mod Loader for Project Zomboid</strong>
</p>

<p align="center">
  <a href="https://openjdk.org/"><img src="https://img.shields.io/badge/Java-17+-ED8B00?style=flat-square&logo=openjdk&logoColor=white" alt="Java 17+"/></a>
  <a href="https://github.com/SpongePowered/Mixin"><img src="https://img.shields.io/badge/SpongePowered-Mixin%200.8.5-00adb5?style=flat-square&logo=java&logoColor=white" alt="Mixin 0.8.5"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="MIT License"/></a>
  <img src="https://img.shields.io/badge/Status-Production%20Ready-success?style=flat-square" alt="Production Ready"/>
</p>

<p align="center">
  <a href="#-installation">Installation</a> •
  <a href="#-key-features">Features</a> •
  <a href="#-for-developers">Developers</a> •
  <a href="#-한국어-korean">한국어</a>
</p>

---

## 🎯 Introduction

**Pulse** is a revolutionary mod loader that brings the power of **SpongePowered Mixin** technology to Project Zomboid. Built for both players and developers, it enables precise runtime bytecode manipulation while providing a rich API ecosystem that significantly simplifies mod development.

> _"Where traditional Lua hooks end, Pulse begins."_

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔧 **Powerful Runtime Manipulation** | Leverages SpongePowered Mixin 0.8.5 for safe, precise bytecode modification — overcoming the limitations of Lua hooks |
| 🌉 **Innovative Two-way Bridge** | Seamless Java ↔ Lua bidirectional communication via `LuaBridge` — call Lua functions from Java and expose Java objects to Lua |
| 📦 **Smart Dependency Management** | Topological Sort-based automatic load ordering with conflict prevention |
| ⚡ **Developer Productivity (DX)** | `GameAccess` Facade API (55+ methods), `EventBus`, `CrashReporter`, `ModProfiler` and more |

### More Features

- 🎭 **Mixin System** — Full SpongePowered Mixin 0.8.5 integration
- 📢 **Event Bus** — Priority-based event subscription system
- 🎮 **GameAccess** — 55+ game API helpers (Player, Zombie, Weather, etc.)
- ⚡ **MixinHelper** — Mixin development utilities
- ⚙️ **Config System** — Annotation-based automatic configuration
- ⏰ **Scheduler** — Tick-based task scheduling
- 🌐 **Networking** — Client-server packet communication
- 📊 **ModProfiler** — Per-mod performance profiling
- 🔍 **CrashReporter** — Detailed crash report generation

---

## 📥 Installation

### Method 1: PulseLauncher (Recommended)

1. Download `Pulse.jar` and `PulseLauncher.bat` to the same folder
2. Double-click `PulseLauncher.bat`
3. The launcher will automatically detect your game path and start with Pulse

```
📁 Your Folder
├── Pulse.jar
└── PulseLauncher.bat   ← Run this!
```

### Method 2: Manual Configuration

Add the following to Steam → Project Zomboid → Properties → Launch Options:

```
-javaagent:"<path_to_Pulse.jar>"
```

**Example:**
```
-javaagent:"C:\Games\PZ-Mods\Pulse.jar"
```

---

## 👩‍💻 For Developers

### Project Structure

```
my-mod/
├── build.gradle
├── src/main/
│   ├── java/com/mymod/
│   │   ├── MyMod.java           # Entrypoint
│   │   └── mixin/               # Mixin classes
│   └── resources/
│       ├── pulse.mod.json       # Mod metadata
│       └── mixins.mymod.json    # Mixin configuration
```

### pulse.mod.json

```json
{
  "id": "mymod",
  "name": "My Awesome Mod",
  "version": "1.0.0",
  "description": "An awesome mod for Project Zomboid",
  "authors": ["YourName"],
  "entrypoint": "com.mymod.MyMod",
  "mixins": ["mixins.mymod.json"],
  "dependencies": [
    { "id": "pulse", "version": ">=1.0.0" }
  ]
}
```

### Entrypoint Class

```java
package com.mymod;

import com.pulse.mod.PulseMod;
import com.pulse.api.GameAccess;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameTickEvent;

public class MyMod implements PulseMod {
    
    @Override
    public void onInitialize() {
        System.out.println("[MyMod] Loading!");
        EventBus.subscribe(GameTickEvent.class, this::onTick, "mymod");
    }
    
    private void onTick(GameTickEvent event) {
        if (event.getTick() % 200 == 0) {
            int zombies = GameAccess.getZombieCount();
            System.out.println("Zombies nearby: " + zombies);
        }
    }
}
```

### Mixin Usage

```java
import com.pulse.mixin.MixinHelper;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(targets = "zombie.characters.IsoZombie")
public class ZombieMixin {
    
    @Inject(method = "update", at = @At("HEAD"), cancellable = true)
    private void onUpdate(CallbackInfo ci) {
        // Cast 'this' to the original type
        Object zombie = MixinHelper.self(this);
        
        // Fire event with automatic cancellation handling
        ZombieUpdateEvent event = new ZombieUpdateEvent(zombie);
        MixinHelper.fireEvent(event, ci);
    }
}
```

#### MixinHelper Methods

| Method | Description |
|--------|-------------|
| `fireEvent(event, ci)` | Fire event + auto cancel |
| `fireEventWithReturn(event, cir, value)` | Event with return value |
| `fire(event)` | Simple event dispatch |
| `self(mixinThis)` | Cast this → original type |
| `safeCast(obj, clazz)` | Null-safe casting |
| `setReturn(cir, value)` | Set return value |
| `setReturnIf(condition, cir, value)` | Conditional return |
| `debug(name, msg)` | Debug logging |

### LuaBridge Usage

The `LuaBridge` enables seamless Java ↔ Lua bidirectional communication:

```java
import com.pulse.lua.LuaBridge;

// Call Lua functions from Java
LuaBridge.call("Events.OnTick.Add", myCallback);

// Access global variables
Object value = LuaBridge.getGlobal("SomeVar");
LuaBridge.setGlobal("MyModData", data);

// Execute Lua code directly
LuaBridge.executeLuaCode("print('Hello from Pulse!')");

// Expose Java class to Lua environment
LuaBridge.expose("MyAPI", MyModAPI.class);

// Register Java callback for Lua
LuaBridge.registerCallback("MyCallback", args -> {
    System.out.println("Called from Lua!");
    return "result";
});

// Table manipulation
Object table = LuaBridge.createLuaTable();
LuaBridge.setTableField(table, "key", "value");
Object field = LuaBridge.getTableField(table, "key");
```

---

## 🛠️ Utilities

### ModProfiler

Monitor and optimize your mod's performance:

```java
import com.pulse.debug.ModProfiler;

// Enable profiling
ModProfiler.enable();

// Profile a section
ProfilerSection section = ModProfiler.start("mymod", "onTick");
try {
    // Your heavy operation
} finally {
    section.end();
}

// Lambda-style profiling
ModProfiler.profile("mymod", "zombieAI", () -> {
    // Heavy computation
});

// Print results
ModProfiler.printResults();
```

### CrashReporter

Automatic detailed crash report generation with:
- Full stack trace analysis
- Active mod list with versions
- Applied Mixin information
- System environment details

### EventBus

Priority-based event subscription system:

```java
import com.pulse.event.EventBus;

// Subscribe to events
EventBus.subscribe(GameTickEvent.class, event -> {
    long tick = event.getTick();
});

// Priority-based subscription
EventBus.subscribe(PlayerDamageEvent.class, event -> {
    event.setCancelled(true);  // Cancel damage
}, EventPriority.HIGH);

// Mod-scoped subscription (auto-cleanup on unload)
EventBus.subscribe(ZombieDeathEvent.class, this::onZombieDeath, "mymod");
```

---

## 🔨 Building from Source

```bash
# Clone the repository
git clone https://github.com/randomstrangerpassenger/Pulse.git
cd Pulse

# Build
./gradlew build

# Output: build/libs/Pulse.jar
```

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<br>

<h1 align="center">🔥 Pulse</h1>

<h2 align="center">한국어 (Korean)</h2>

---

## 🎯 소개

**Pulse**는 Project Zomboid를 위한 차세대 모드 로더입니다. **SpongePowered Mixin** 기술을 도입하여 런타임에 게임의 바이트코드를 안전하고 정밀하게 수정할 수 있습니다. 기존 Lua 훅킹의 한계를 극복하고, 개발자와 플레이어 모두를 위한 풍부한 API 생태계를 제공합니다.

> _"기존 Lua 훅의 한계를 넘어, Pulse가 시작됩니다."_

---

## ✨ 핵심 기능

| 기능 | 설명 |
|------|------|
| 🔧 **강력한 런타임 조작 (Mixin)** | SpongePowered Mixin 0.8.5를 활용한 안전하고 정밀한 바이트코드 수정 — Lua 훅의 한계 극복 |
| 🌉 **혁신적인 양방향 브릿지 (LuaBridge)** | Java ↔ Lua 완벽한 양방향 통신 — Java에서 Lua 함수 호출 및 Java 객체의 Lua 전역 노출 |
| 📦 **스마트 의존성 관리** | 위상 정렬(Topological Sort) 기반 자동 로드 순서 결정 및 충돌 방지 |
| ⚡ **개발자 생산성 (DX)** | `GameAccess` Facade API (55+ 메서드), `EventBus`, `CrashReporter`, `ModProfiler` 등 |

### 추가 기능

- 🎭 **Mixin System** — SpongePowered Mixin 0.8.5 완전 통합
- 📢 **Event Bus** — 우선순위 기반 이벤트 구독 시스템
- 🎮 **GameAccess** — 55+ 게임 API 헬퍼 (플레이어, 좀비, 날씨 등)
- ⚡ **MixinHelper** — Mixin 개발 간소화 유틸리티
- ⚙️ **Config System** — 어노테이션 기반 자동 설정 관리
- ⏰ **Scheduler** — 틱 기반 태스크 스케줄링
- 🌐 **Networking** — 클라이언트-서버 패킷 통신
- 📊 **ModProfiler** — 모드별 성능 프로파일링
- 🔍 **CrashReporter** — 상세 크래시 리포트 생성

---

## 📥 설치 방법

### 방법 1: PulseLauncher (권장)

1. `Pulse.jar`와 `PulseLauncher.bat`를 같은 폴더에 다운로드
2. `PulseLauncher.bat` 더블클릭
3. 런처가 자동으로 게임 경로를 감지하고 Pulse와 함께 실행

```
📁 폴더 구조
├── Pulse.jar
└── PulseLauncher.bat   ← 실행!
```

### 방법 2: 수동 설정

Steam → Project Zomboid → 속성 → 시작 옵션에 다음을 추가:

```
-javaagent:"<Pulse.jar 경로>"
```

**예시:**
```
-javaagent:"C:\Games\PZ-Mods\Pulse.jar"
```

---

## 👩‍💻 개발자 가이드

### 프로젝트 구조

```
my-mod/
├── build.gradle
├── src/main/
│   ├── java/com/mymod/
│   │   ├── MyMod.java           # 엔트리포인트
│   │   └── mixin/               # Mixin 클래스들
│   └── resources/
│       ├── pulse.mod.json       # 모드 메타데이터
│       └── mixins.mymod.json    # Mixin 설정
```

### pulse.mod.json

```json
{
  "id": "mymod",
  "name": "My Awesome Mod",
  "version": "1.0.0",
  "description": "Project Zomboid를 위한 멋진 모드",
  "authors": ["YourName"],
  "entrypoint": "com.mymod.MyMod",
  "mixins": ["mixins.mymod.json"],
  "dependencies": [
    { "id": "pulse", "version": ">=1.0.0" }
  ]
}
```

### 엔트리포인트 클래스

```java
package com.mymod;

import com.pulse.mod.PulseMod;
import com.pulse.api.GameAccess;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameTickEvent;

public class MyMod implements PulseMod {
    
    @Override
    public void onInitialize() {
        System.out.println("[MyMod] 로딩 중!");
        EventBus.subscribe(GameTickEvent.class, this::onTick, "mymod");
    }
    
    private void onTick(GameTickEvent event) {
        if (event.getTick() % 200 == 0) {
            int zombies = GameAccess.getZombieCount();
            System.out.println("주변 좀비 수: " + zombies);
        }
    }
}
```

### Mixin 사용법

```java
import com.pulse.mixin.MixinHelper;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(targets = "zombie.characters.IsoZombie")
public class ZombieMixin {
    
    @Inject(method = "update", at = @At("HEAD"), cancellable = true)
    private void onUpdate(CallbackInfo ci) {
        // 'this'를 원본 타입으로 캐스팅
        Object zombie = MixinHelper.self(this);
        
        // 이벤트 발행 + 자동 취소 처리
        ZombieUpdateEvent event = new ZombieUpdateEvent(zombie);
        MixinHelper.fireEvent(event, ci);
    }
}
```

#### MixinHelper 메서드

| 메서드 | 설명 |
|--------|------|
| `fireEvent(event, ci)` | 이벤트 발행 + 자동 취소 |
| `fireEventWithReturn(event, cir, value)` | 반환값 있는 이벤트 |
| `fire(event)` | 단순 이벤트 발행 |
| `self(mixinThis)` | this → 원본 타입 캐스팅 |
| `safeCast(obj, clazz)` | null-safe 캐스팅 |
| `setReturn(cir, value)` | 반환값 설정 |
| `setReturnIf(condition, cir, value)` | 조건부 반환값 |
| `debug(name, msg)` | 디버그 로그 |

### LuaBridge 사용법

`LuaBridge`는 Java와 Lua 간의 완벽한 양방향 통신을 지원합니다:

```java
import com.pulse.lua.LuaBridge;

// Java에서 Lua 함수 호출
LuaBridge.call("Events.OnTick.Add", myCallback);

// 전역 변수 접근
Object value = LuaBridge.getGlobal("SomeVar");
LuaBridge.setGlobal("MyModData", data);

// Lua 코드 직접 실행
LuaBridge.executeLuaCode("print('Hello from Pulse!')");

// Java 클래스를 Lua 환경에 노출
LuaBridge.expose("MyAPI", MyModAPI.class);

// Lua용 Java 콜백 등록
LuaBridge.registerCallback("MyCallback", args -> {
    System.out.println("Lua에서 호출됨!");
    return "result";
});

// 테이블 조작
Object table = LuaBridge.createLuaTable();
LuaBridge.setTableField(table, "key", "value");
Object field = LuaBridge.getTableField(table, "key");
```

---

## 🛠️ 유틸리티

### ModProfiler

모드의 성능을 모니터링하고 최적화하세요:

```java
import com.pulse.debug.ModProfiler;

// 프로파일링 활성화
ModProfiler.enable();

// 섹션 측정
ProfilerSection section = ModProfiler.start("mymod", "onTick");
try {
    // 무거운 작업 수행
} finally {
    section.end();
}

// 람다 스타일 프로파일링
ModProfiler.profile("mymod", "zombieAI", () -> {
    // 무거운 연산
});

// 결과 출력
ModProfiler.printResults();
```

### CrashReporter

자동 상세 크래시 리포트 생성:
- 전체 스택 트레이스 분석
- 활성 모드 목록 및 버전
- 적용된 Mixin 정보
- 시스템 환경 정보

### EventBus

우선순위 기반 이벤트 구독 시스템:

```java
import com.pulse.event.EventBus;

// 이벤트 구독
EventBus.subscribe(GameTickEvent.class, event -> {
    long tick = event.getTick();
});

// 우선순위 기반 구독
EventBus.subscribe(PlayerDamageEvent.class, event -> {
    event.setCancelled(true);  // 데미지 취소
}, EventPriority.HIGH);

// 모드 범위 구독 (언로드 시 자동 정리)
EventBus.subscribe(ZombieDeathEvent.class, this::onZombieDeath, "mymod");
=======
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
>>>>>>> echo-history/main
```

---

<<<<<<< HEAD
## 🔨 빌드 방법

```bash
# 저장소 클론
git clone https://github.com/randomstrangerpassenger/Pulse.git
cd Pulse

# 빌드
./gradlew build

# 결과물: build/libs/Pulse.jar
=======
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
>>>>>>> echo-history/main
```

---

<<<<<<< HEAD
## 📄 라이선스

이 프로젝트는 **MIT 라이선스** 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

<div align="center">
  <sub>Built with ❤️ for the Project Zomboid modding community</sub>
</div>
=======
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
>>>>>>> echo-history/main
