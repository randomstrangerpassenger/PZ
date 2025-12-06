# 🧬 Mutagen

**Project Zomboid를 위한 경량 Mixin 기반 모드로더**

[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.org/)
[![Mixin](https://img.shields.io/badge/SpongePowered-Mixin%200.8.5-blue.svg)](https://github.com/SpongePowered/Mixin)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 목차

- [소개](#-소개)
- [주요 기능](#-주요-기능)
- [시스템 요구사항](#-시스템-요구사항)
- [설치 방법](#-설치-방법)
- [모드 개발 가이드](#-모드-개발-가이드)
- [API 레퍼런스](#-api-레퍼런스)
- [빌드 방법](#-빌드-방법)
- [라이선스](#-라이선스)

---

## 🎯 소개

**Mutagen**은 Project Zomboid 게임을 위한 현대적인 모드로더입니다. SpongePowered Mixin 라이브러리를 활용하여 게임 코드를 런타임에 안전하게 수정할 수 있습니다.

### 왜 Mutagen인가?

- **🔧 Mixin 지원**: 바이트코드 수준의 정밀한 게임 수정
- **📦 모듈화**: 모드 간 충돌 최소화
- **🚀 경량**: 게임 성능에 미치는 영향 최소화
- **🛠️ 풍부한 API**: 이벤트, 설정, 네트워킹 등 모드 개발에 필요한 모든 것

---

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| **🎭 Mixin System** | SpongePowered Mixin 0.8.5 완전 통합 |
| **📢 Event Bus** | 우선순위 기반 이벤트 시스템 |
| **⚙️ Config System** | 어노테이션 기반 자동 설정 관리 |
| **📝 Registry** | Minecraft 스타일 범용 레지스트리 |
| **⏰ Scheduler** | 틱 기반 태스크 스케줄링 |
| **⌨️ Key Bindings** | 커스텀 키 바인딩 등록 |
| **💬 Commands** | 인게임 명령어 시스템 |
| **🌐 Networking** | 클라이언트-서버 패킷 통신 |
| **🔓 Access Widener** | private 멤버 접근 유틸리티 |

---

## 💻 시스템 요구사항

- **Java**: 17 이상
- **Project Zomboid**: 최신 버전
- **OS**: Windows, Linux, macOS

---

## 📥 설치 방법

### 1. Mutagen 다운로드

[Releases](https://github.com/yourusername/Mutagen/releases)에서 최신 `Mutagen.jar`를 다운로드합니다.

### 2. 게임 실행 설정

Steam 라이브러리에서 Project Zomboid → 속성 → 시작 옵션에 다음을 추가:

```
-javaagent:Mutagen.jar경로\Mutagen.jar
```

**예시 (Windows):**
```
-javaagent:C:\Games\PZMods\Mutagen.jar
```

### 3. 모드 설치

게임 폴더에 `mods` 디렉토리를 생성하고 모드 JAR 파일을 넣습니다:

```
ProjectZomboid/
├── mods/
│   ├── MyMod.jar
│   └── AnotherMod.jar
└── ...
```

### 4. 게임 실행

게임을 시작하면 콘솔에 Mutagen 초기화 메시지가 표시됩니다:

```
╔══════════════════════════════════════════════════════════════╗
║              MUTAGEN MOD LOADER v1.0.0                       ║
║          Project Zomboid Modding Platform                    ║
╚══════════════════════════════════════════════════════════════╝
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
│   │   ├── config/MyConfig.java # 설정
│   │   └── mixin/               # Mixin 클래스들
│   └── resources/
│       ├── mutagen.mod.json     # 모드 메타데이터
│       └── mixins.mymod.json    # Mixin 설정
```

### 1. mutagen.mod.json

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
    { "id": "mutagen", "version": ">=1.0.0" }
  ]
}
```

### 2. 엔트리포인트 클래스

```java
package com.mymod;

import com.mutagen.mod.MutagenMod;
import com.mutagen.api.Mutagen;
import com.mutagen.event.EventBus;
import com.mutagen.event.lifecycle.GameInitEvent;

public class MyMod implements MutagenMod {
    
    @Override
    public void onInitialize() {
        Mutagen.log("MyMod is loading!");
        
        // 이벤트 구독
        EventBus.subscribe(GameInitEvent.class, this::onGameInit);
    }
    
    private void onGameInit(GameInitEvent event) {
        Mutagen.log("Game initialized!");
    }
}
```

### 3. Mixin 작성

**mixins.mymod.json:**
```json
{
  "required": true,
  "package": "com.mymod.mixin",
  "compatibilityLevel": "JAVA_17",
  "mixins": [
    "PlayerMixin"
  ]
}
```

**PlayerMixin.java:**
```java
package com.mymod.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(targets = "zombie.characters.IsoPlayer")
public abstract class PlayerMixin {
    
    @Inject(method = "update", at = @At("HEAD"))
    private void onUpdate(CallbackInfo ci) {
        // 플레이어 업데이트 시 호출
    }
}
```

### 4. build.gradle

```groovy
plugins {
    id 'java'
    id 'com.github.johnrengelman.shadow' version '8.1.1'
}

group = 'com.mymod'
version = '1.0.0'

java {
    sourceCompatibility = JavaVersion.VERSION_17
}

repositories {
    mavenCentral()
    maven { url 'https://repo.spongepowered.org/maven/' }
}

dependencies {
    compileOnly files('path/to/Mutagen.jar')
    compileOnly 'org.spongepowered:mixin:0.8.5'
}

shadowJar {
    archiveBaseName.set('MyMod')
    archiveClassifier.set('')
    archiveVersion.set('')
}
```

---

## 📚 API 레퍼런스

### Event System

```java
// 이벤트 구독
EventBus.subscribe(GameTickEvent.class, event -> {
    long tick = event.getTick();
    float deltaTime = event.getDeltaTime();
});

// 우선순위 지정
EventBus.subscribe(PlayerDamageEvent.class, event -> {
    event.setCancelled(true); // 데미지 취소
}, EventPriority.HIGH);

// 커스텀 이벤트 발행
EventBus.post(new MyCustomEvent());
```

### Config System

```java
@Config(modId = "mymod")
public class MyConfig {
    
    @ConfigValue(comment = "Enable debug mode")
    public static boolean debugMode = false;
    
    @ConfigValue(min = 0, max = 100)
    public static int someValue = 50;
}

// 등록
ConfigManager.register(MyConfig.class);

// 사용
if (MyConfig.debugMode) { ... }

// 저장
ConfigManager.save(MyConfig.class);
```

### Registry System

```java
// 레지스트리 생성
Registry<MyItem> ITEMS = Registry.create(
    Identifier.of("mymod", "items")
);

// 등록
ITEMS.register(Identifier.of("mymod", "cool_item"), new MyCoolItem());

// 조회
MyItem item = ITEMS.get(Identifier.of("mymod", "cool_item"));
```

### Scheduler

```java
// 60틱(약 3초) 후 1회 실행
MutagenScheduler.runLater(() -> {
    System.out.println("Delayed!");
}, 60);

// 20틱마다 반복 실행
TaskHandle timer = MutagenScheduler.runTimer(() -> {
    System.out.println("Every second!");
}, 20, 0);

// 취소
timer.cancel();

// 비동기 실행
MutagenScheduler.runAsync(() -> {
    // 무거운 작업
});
```

### Key Bindings

```java
KeyBinding openMenu = KeyBinding.create("mymod", "open_menu")
    .defaultKey(KeyCode.KEY_M)
    .withCtrl()
    .category("My Mod")
    .build();

KeyBindingRegistry.register(openMenu);

// 매 틱 체크
if (openMenu.wasPressed()) {
    openMyMenu();
}
```

### Commands

```java
// 람다 기반
CommandRegistry.register("hello", ctx -> {
    ctx.reply("Hello, " + ctx.getSender().getName() + "!");
});

// 어노테이션 기반
public class MyCommands {
    @Command(name = "heal", description = "Heal the player")
    public void heal(CommandContext ctx) {
        // 힐 로직
    }
}
CommandRegistry.register(new MyCommands());
```

### Access Widener

```java
// private 필드 접근
Object value = AccessWidener.getField(instance, "privateField");
AccessWidener.setField(instance, "privateField", newValue);

// private 메서드 호출
Object result = AccessWidener.invoke(instance, "privateMethod", arg1, arg2);

// 인스턴스 생성
Object obj = AccessWidener.newInstance("zombie.SomeClass", arg1);
```

---

## 🔧 빌드 방법

### 요구사항

- JDK 17+
- Gradle 8.0+

### 빌드

```bash
# 클론
git clone https://github.com/yourusername/Mutagen.git
cd Mutagen

# 빌드
./gradlew shadowJar

# 결과물
# build/libs/Mutagen.jar
```

### IDE 설정

```bash
# IntelliJ IDEA
./gradlew idea

# Eclipse
./gradlew eclipse
```

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 🤝 기여하기

1. 이 저장소를 Fork합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

---

## 💬 지원

- **Issues**: [GitHub Issues](https://github.com/yourusername/Mutagen/issues)
- **Discord**: [Discord Server](https://discord.gg/yourserver)

---

<div align="center">
  <sub>Built with ❤️ for the Project Zomboid modding community</sub>
</div>
