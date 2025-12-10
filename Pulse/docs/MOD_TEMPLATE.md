# Pulse Mod Template

A starter template for creating Pulse mods.

## Quick Start

1. Clone this template
2. Update `src/main/resources/pulse.mod.json` with your mod info
3. Implement your mod in `src/main/java/com/example/mymod/MyMod.java`
4. Build with `gradle shadowJar`
5. Copy the JAR to your `mods` folder

## Project Structure

```
my-mod/
├── build.gradle
├── src/
│   └── main/
│       ├── java/
│       │   └── com/example/mymod/
│       │       └── MyMod.java
│       └── resources/
│           └── pulse.mod.json
└── README.md
```

## build.gradle Example

```groovy
plugins {
    id 'java'
    id 'com.github.johnrengelman.shadow' version '8.1.1'
}

group = 'com.example'
version = '1.0.0'

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

repositories {
    mavenCentral()
    // Pulse repository
    maven { url 'https://pulse-mods.example.com/maven' }
}

dependencies {
    // Pulse API (compile-only)
    compileOnly 'com.pulse:pulse-api:1.0.0'
    
    // PZ classes (provided at runtime)
    compileOnly files("${System.getProperty('user.home')}/Zomboid/java/pz.jar")
}

shadowJar {
    archiveClassifier.set('')
    // Don't include Pulse API in the output
    dependencies {
        exclude(dependency('com.pulse:pulse-api'))
    }
}
```

## pulse.mod.json Example

```json
{
    "id": "my-mod",
    "name": "My Awesome Mod",
    "version": "1.0.0",
    "author": "Your Name",
    "description": "A cool mod for Project Zomboid",
    "entrypoint": "com.example.mymod.MyMod",
    "loaderVersion": ">=1.0.0",
    "gameVersion": "41.78+",
    "dependencies": [
        { "id": "pulse", "version": ">=1.0.0" }
    ],
    "permissions": ["file.read", "game.world_modify"]
}
```

## Mod Entry Point

```java
package com.example.mymod;

import com.pulse.mod.PulseMod;
import com.pulse.api.Pulse;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameTickEvent;

public class MyMod implements PulseMod {
    
    public static final String MOD_ID = "my-mod";
    
    @Override
    public void onInitialize() {
        Pulse.log(MOD_ID, "Initializing...");
        
        // Register event listeners
        EventBus.subscribe(GameTickEvent.class, this::onTick, MOD_ID);
        
        Pulse.log(MOD_ID, "Initialized!");
    }
    
    private void onTick(GameTickEvent event) {
        // Called every game tick
    }
    
    @Override
    public void onUnload() {
        Pulse.log(MOD_ID, "Unloading...");
        // Cleanup if needed
    }
}
```

## Available APIs

- **EventBus**: Subscribe to game events
- **ConfigManager**: Create mod configuration
- **NetworkManager**: Send/receive packets
- **IMC**: Inter-mod communication
- **ItemRegistry**: Register custom items
- **RecipeRegistry**: Register crafting recipes
- **DevConsole**: Debug commands

## Documentation

See the [Pulse Wiki](https://github.com/pulse-loader/pulse/wiki) for full documentation.
