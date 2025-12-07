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
```

---

## 🔨 빌드 방법

```bash
# 저장소 클론
git clone https://github.com/randomstrangerpassenger/Pulse.git
cd Pulse

# 빌드
./gradlew build

# 결과물: build/libs/Pulse.jar
```

---

## 📄 라이선스

이 프로젝트는 **MIT 라이선스** 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

<div align="center">
  <sub>Built with ❤️ for the Project Zomboid modding community</sub>
</div>
