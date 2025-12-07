# 🔥 Pulse

**Project Zomboid를 위한 경량 Mixin 기반 모드로더**

[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org/)
[![Mixin](https://img.shields.io/badge/SpongePowered-Mixin%200.8.5-blue.svg)](https://github.com/SpongePowered/Mixin)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 목차

- [소개](#-소개)
- [주요 기능](#-주요-기능)
- [설치 방법](#-설치-방법)
- [API 레퍼런스](#-api-레퍼런스)
- [모드 개발 가이드](#-모드-개발-가이드)
- [빌드 방법](#-빌드-방법)

---

## 🎯 소개

**Pulse**는 Project Zomboid 게임을 위한 현대적인 모드로더입니다. SpongePowered Mixin 라이브러리를 활용하여 게임 코드를 런타임에 안전하게 수정할 수 있습니다.

### 장점

- **🔧 Mixin 지원**: 바이트코드 수준의 정밀한 게임 수정
- **📦 모듈화**: 모드 간 충돌 최소화  
- **🚀 경량**: 게임 성능에 미치는 영향 최소화
- **🛠️ 풍부한 API**: 55+ 헬퍼 메서드로 모드 개발 난이도 80% 감소
- **🌙 Lua 통합**: Java ↔ Lua 양방향 브릿지

---

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| **🎭 Mixin System** | SpongePowered Mixin 0.8.5 완전 통합 |
| **📢 Event Bus** | 우선순위 기반 이벤트 시스템 |
| **🎮 GameAccess** | 55+ 게임 API 헬퍼 (플레이어, 좀비, 날씨 등) |
| **⚡ MixinHelper** | Mixin 개발 간소화 유틸리티 |
| **🌙 LuaBridge** | Java ↔ Lua 양방향 브릿지 |
| **⚙️ Config System** | 어노테이션 기반 자동 설정 관리 |
| **📊 ModProfiler** | 모드별 성능 프로파일링 |
| **🔍 CrashReporter** | 상세 크래시 리포트 생성 |
| **⏰ Scheduler** | 틱 기반 태스크 스케줄링 |
| **🌐 Networking** | 클라이언트-서버 패킷 통신 |

---

## 📥 설치 방법

### 방법 1: PulseLauncher.bat (권장)

1. `Pulse.jar`와 `PulseLauncher.bat`를 같은 폴더에 배치
2. `PulseLauncher.bat` 더블클릭
3. 자동으로 게임 경로 감지 및 실행

### 방법 2: 수동 설정

Steam 라이브러리 → Project Zomboid → 속성 → 시작 옵션:

```
-javaagent:"Pulse.jar경로"
```

---

## 📚 API 레퍼런스

### GameAccess - 게임 접근 API (55+ 메서드)

```java
import com.pulse.api.GameAccess;

// ═══════════════════════════════════════════════════════════════
// 플레이어 API
// ═══════════════════════════════════════════════════════════════
Object player = GameAccess.getLocalPlayer();
float health = GameAccess.getPlayerHealth();
float x = GameAccess.getPlayerX();
float y = GameAccess.getPlayerY();
boolean alive = GameAccess.isPlayerAlive();

// 멀티플레이어
List<Object> allPlayers = GameAccess.getAllPlayers();
int playerCount = GameAccess.getPlayerCount();
Object target = GameAccess.getPlayerByName("username");

// ═══════════════════════════════════════════════════════════════
// 월드/시간 API
// ═══════════════════════════════════════════════════════════════
boolean loaded = GameAccess.isWorldLoaded();
String worldName = GameAccess.getWorldName();
Object cell = GameAccess.getCell();
Object square = GameAccess.getSquare(x, y, z);

int hour = GameAccess.getGameHour();
int day = GameAccess.getGameDay();
boolean isNight = GameAccess.isNight();

// ═══════════════════════════════════════════════════════════════
// 좀비 API
// ═══════════════════════════════════════════════════════════════
List<Object> zombies = GameAccess.getAllZombies();
List<Object> nearby = GameAccess.getNearbyZombies(x, y, 50f);
int count = GameAccess.getZombieCount();

// 좀비 스폰
Object zombie = GameAccess.spawnZombie(1000, 2000, 0);
Object nearbyZombie = GameAccess.spawnZombieNearPlayer(10, 10);

// ═══════════════════════════════════════════════════════════════
// 거리 계산 API
// ═══════════════════════════════════════════════════════════════
float dist = GameAccess.getDistance(entity1, entity2);
float distToPlayer = GameAccess.getDistanceToPlayer(zombie);
float distToPoint = GameAccess.getDistanceToPoint(entity, 1000f, 2000f);

// ═══════════════════════════════════════════════════════════════
// 날씨 API
// ═══════════════════════════════════════════════════════════════
String weather = GameAccess.getWeather();  // "sunny", "rain", "fog", "snow"
boolean raining = GameAccess.isRaining();
boolean snowing = GameAccess.isSnowing();
boolean foggy = GameAccess.isFoggy();

GameAccess.startRain();
GameAccess.stopRain();
GameAccess.setRainIntensity(0.8f);

// ═══════════════════════════════════════════════════════════════
// 아이템 API
// ═══════════════════════════════════════════════════════════════
Object item = GameAccess.createItem("Base.Axe");
GameAccess.spawnItem("Base.Apple", x, y, z);
GameAccess.addInventoryItem(player, item);
List<Object> inventory = GameAccess.getInventoryItems(player);

// ═══════════════════════════════════════════════════════════════
// 사운드 API
// ═══════════════════════════════════════════════════════════════
GameAccess.playSound("zombieHurt", x, y, z);

// ═══════════════════════════════════════════════════════════════
// 게임 상태 API
// ═══════════════════════════════════════════════════════════════
boolean paused = GameAccess.isPaused();
boolean mp = GameAccess.isMultiplayer();
boolean server = GameAccess.isServer();
boolean admin = GameAccess.isAdmin();
boolean debug = GameAccess.isDebugMode();
```

---

### MixinHelper - Mixin 개발 유틸리티

```java
import com.pulse.mixin.MixinHelper;

@Mixin(targets = "zombie.characters.IsoZombie")
public class ZombieMixin {
    
    @Inject(method = "update", at = @At("HEAD"), cancellable = true)
    private void onUpdate(CallbackInfo ci) {
        // this를 원본 타입으로 캐스팅
        IsoZombie zombie = MixinHelper.self(this);
        
        // 이벤트 발행 + 자동 취소 처리
        ZombieUpdateEvent event = new ZombieUpdateEvent(zombie);
        MixinHelper.fireEvent(event, ci);
    }
    
    @Inject(method = "getSpeed", at = @At("HEAD"), cancellable = true)
    private void onGetSpeed(CallbackInfoReturnable<Float> cir) {
        // 반환값이 있는 이벤트
        ZombieSpeedEvent event = new ZombieSpeedEvent(zombie);
        MixinHelper.fireEventWithReturn(event, cir, 0.5f);
    }
}
```

**사용 가능한 헬퍼 메서드:**

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

---

### LuaBridge - Lua 통합

```java
import com.pulse.lua.LuaBridge;

// Lua 함수 호출
LuaBridge.call("Events.OnTick.Add", myCallback);

// 전역 변수 접근
Object value = LuaBridge.getGlobal("SomeVar");
LuaBridge.setGlobal("MyModData", data);

// Lua 코드 직접 실행
LuaBridge.executeLuaCode("print('Hello from Pulse!')");

// Java 클래스를 Lua에 노출
LuaBridge.expose("MyAPI", MyModAPI.class);

// Java 콜백 등록
LuaBridge.registerCallback("MyCallback", args -> {
    System.out.println("Called from Lua!");
    return "result";
});

// 테이블 조작
Object table = LuaBridge.createLuaTable();
LuaBridge.setTableField(table, "key", "value");
```

---

### Event System

```java
import com.pulse.event.EventBus;

// 이벤트 구독
EventBus.subscribe(GameTickEvent.class, event -> {
    long tick = event.getTick();
});

// 우선순위 지정
EventBus.subscribe(PlayerDamageEvent.class, event -> {
    event.setCancelled(true);  // 데미지 취소
}, EventPriority.HIGH);

// 모드 ID로 구독 (언로드 시 자동 정리)
EventBus.subscribe(ZombieDeathEvent.class, this::onZombieDeath, "mymod");
```

---

### ModProfiler - 성능 프로파일링

```java
import com.pulse.debug.ModProfiler;

// 프로파일링 활성화
ModProfiler.enable();

// 섹션 측정
ProfilerSection section = ModProfiler.start("mymod", "onTick");
try {
    // 작업 수행
} finally {
    section.end();
}

// 람다로 간편하게
ModProfiler.profile("mymod", "zombieAI", () -> {
    // 무거운 작업
});

// 결과 출력
ModProfiler.printResults();
```

---

## 🔨 모드 개발 가이드

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
  "description": "An awesome mod for Project Zomboid",
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
        System.out.println("[MyMod] Loading!");
        
        EventBus.subscribe(GameTickEvent.class, this::onTick, "mymod");
    }
    
    private void onTick(GameTickEvent event) {
        // 매 틱마다 실행
        if (event.getTick() % 200 == 0) {
            int zombies = GameAccess.getZombieCount();
            System.out.println("Zombies nearby: " + zombies);
        }
    }
}
```

---

## 🔧 빌드 방법

```bash
# 클론
git clone https://github.com/randomstrangerpassenger/Pulse.git
cd Pulse

# 빌드
./gradlew build

# 결과물: build/libs/Pulse.jar
```

---

## 📄 라이선스

MIT 라이선스. [LICENSE](LICENSE) 파일 참조.

---

<div align="center">
  <sub>Built with ❤️ for the Project Zomboid modding community</sub>
</div>
