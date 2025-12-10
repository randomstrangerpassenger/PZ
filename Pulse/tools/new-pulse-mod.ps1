#!/usr/bin/env pwsh
# Pulse Mod Scaffolding Script
# Usage: .\new-pulse-mod.ps1 -ModId "mymod" -ModName "My Awesome Mod" -Package "com.example.mymod" -Author "YourName"

param(
    [Parameter(Mandatory=$true)]
    [string]$ModId,
    
    [Parameter(Mandatory=$false)]
    [string]$ModName = $ModId,
    
    [Parameter(Mandatory=$false)]
    [string]$Package = "com.example.$ModId",
    
    [Parameter(Mandatory=$false)]
    [string]$Author = "Unknown",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputDir = "."
)

$ErrorActionPreference = "Stop"

# Validate ModId
if ($ModId -notmatch '^[a-z][a-z0-9_]*$') {
    Write-Error "ModId must start with lowercase letter and contain only lowercase letters, numbers, and underscores"
    exit 1
}

$projectDir = Join-Path $OutputDir $ModId
$packagePath = $Package -replace '\.', '/'
$javaDir = Join-Path $projectDir "src/main/java/$packagePath"
$resourcesDir = Join-Path $projectDir "src/main/resources"

# Create directories
Write-Host "Creating mod project: $ModName ($ModId)" -ForegroundColor Green
New-Item -ItemType Directory -Path $javaDir -Force | Out-Null
New-Item -ItemType Directory -Path $resourcesDir -Force | Out-Null

# Generate build.gradle
$buildGradle = @"
plugins {
    id 'java'
}

group = '$Package'
version = '1.0.0'

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

repositories {
    mavenCentral()
}

dependencies {
    // Pulse API - compile time only
    compileOnly files('path/to/Pulse.jar')
}

jar {
    from('src/main/resources') {
        include 'pulse.mod.json'
    }
    
    manifest {
        attributes(
            'Implementation-Title': '$ModName',
            'Implementation-Version': version
        )
    }
}

tasks.withType(JavaCompile) {
    options.encoding = 'UTF-8'
}
"@

Set-Content -Path (Join-Path $projectDir "build.gradle") -Value $buildGradle -Encoding UTF8

# Generate pulse.mod.json
$modJson = @"
{
  "id": "$ModId",
  "name": "$ModName",
  "version": "1.0.0",
  "author": "$Author",
  "description": "A Pulse mod for Project Zomboid",
  "entrypoint": "$Package.${ModId}Mod",
  "dependencies": [
    {
      "id": "Pulse",
      "version": ">=1.0.0"
    }
  ]
}
"@

Set-Content -Path (Join-Path $resourcesDir "pulse.mod.json") -Value $modJson -Encoding UTF8

# Generate main mod class
$className = (Get-Culture).TextInfo.ToTitleCase($ModId) -replace '_', ''
$modClass = @"
package $Package;

import com.pulse.api.Pulse;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameInitEvent;
import com.pulse.event.lifecycle.GameTickEvent;
import com.pulse.mod.PulseMod;

/**
 * $ModName - Main mod class
 */
public class ${className}Mod implements PulseMod {

    private static final String MOD_ID = "$ModId";

    @Override
    public void onInitialize() {
        Pulse.log(MOD_ID, "$ModName initializing...");
        
        // Register event listeners
        EventBus.subscribe(GameInitEvent.class, this::onGameInit, MOD_ID);
        EventBus.subscribe(GameTickEvent.class, this::onGameTick, MOD_ID);
        
        Pulse.log(MOD_ID, "$ModName initialized!");
    }
    
    private void onGameInit(GameInitEvent event) {
        Pulse.log(MOD_ID, "Game initialization complete!");
    }
    
    private void onGameTick(GameTickEvent event) {
        // Called every game tick
        // Add your tick logic here
    }

    @Override
    public void onUnload() {
        Pulse.log(MOD_ID, "$ModName unloading...");
    }
}
"@

Set-Content -Path (Join-Path $javaDir "${className}Mod.java") -Value $modClass -Encoding UTF8

# Generate README
$readme = @"
# $ModName

A Pulse mod for Project Zomboid.

## Building

1. Update `build.gradle` with the correct path to `Pulse.jar`
2. Run: ``./gradlew build``
3. Find the JAR in `build/libs/`

## Installation

1. Copy the built JAR to `ProjectZomboid/mods/`
2. Enable the mod in-game

## Development

- Main class: `$Package.${className}Mod`
- Mod ID: `$ModId`
"@

Set-Content -Path (Join-Path $projectDir "README.md") -Value $readme -Encoding UTF8

Write-Host ""
Write-Host "Mod project created successfully!" -ForegroundColor Green
Write-Host "Location: $projectDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Update build.gradle with path to Pulse.jar"
Write-Host "  2. Run './gradlew build' to build your mod"
Write-Host "  3. Copy the JAR to your mods folder"
