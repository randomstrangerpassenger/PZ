#!/bin/bash
# Pulse Mod Scaffolding Script
# Usage: ./new-pulse-mod.sh --mod-id "mymod" --mod-name "My Awesome Mod" --package "com.example.mymod" --author "YourName"

set -e

# Default values
MOD_ID=""
MOD_NAME=""
PACKAGE=""
AUTHOR="Unknown"
OUTPUT_DIR="."

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mod-id)
            MOD_ID="$2"
            shift 2
            ;;
        --mod-name)
            MOD_NAME="$2"
            shift 2
            ;;
        --package)
            PACKAGE="$2"
            shift 2
            ;;
        --author)
            AUTHOR="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$MOD_ID" ]; then
    echo "Usage: $0 --mod-id <modid> [--mod-name <name>] [--package <package>] [--author <author>]"
    exit 1
fi

# Set defaults based on mod-id if not provided
[ -z "$MOD_NAME" ] && MOD_NAME="$MOD_ID"
[ -z "$PACKAGE" ] && PACKAGE="com.example.$MOD_ID"

# Validate ModId format
if ! [[ "$MOD_ID" =~ ^[a-z][a-z0-9_]*$ ]]; then
    echo "Error: ModId must start with lowercase letter and contain only lowercase letters, numbers, and underscores"
    exit 1
fi

PROJECT_DIR="$OUTPUT_DIR/$MOD_ID"
PACKAGE_PATH="${PACKAGE//./\/}"
JAVA_DIR="$PROJECT_DIR/src/main/java/$PACKAGE_PATH"
RESOURCES_DIR="$PROJECT_DIR/src/main/resources"

# Create directories
echo "Creating mod project: $MOD_NAME ($MOD_ID)"
mkdir -p "$JAVA_DIR"
mkdir -p "$RESOURCES_DIR"

# Generate build.gradle
cat > "$PROJECT_DIR/build.gradle" << EOF
plugins {
    id 'java'
}

group = '$PACKAGE'
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
            'Implementation-Title': '$MOD_NAME',
            'Implementation-Version': version
        )
    }
}

tasks.withType(JavaCompile) {
    options.encoding = 'UTF-8'
}
EOF

# Generate pulse.mod.json
cat > "$RESOURCES_DIR/pulse.mod.json" << EOF
{
  "id": "$MOD_ID",
  "name": "$MOD_NAME",
  "version": "1.0.0",
  "author": "$AUTHOR",
  "description": "A Pulse mod for Project Zomboid",
  "entrypoint": "$PACKAGE.${MOD_ID^}Mod",
  "dependencies": [
    {
      "id": "Pulse",
      "version": ">=1.0.0"
    }
  ]
}
EOF

# Generate class name (capitalize first letter)
CLASS_NAME="$(tr '[:lower:]' '[:upper:]' <<< ${MOD_ID:0:1})${MOD_ID:1}"

# Generate main mod class
cat > "$JAVA_DIR/${CLASS_NAME}Mod.java" << EOF
package $PACKAGE;

import com.pulse.api.Pulse;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameInitEvent;
import com.pulse.event.lifecycle.GameTickEvent;
import com.pulse.mod.PulseMod;

/**
 * $MOD_NAME - Main mod class
 */
public class ${CLASS_NAME}Mod implements PulseMod {

    private static final String MOD_ID = "$MOD_ID";

    @Override
    public void onInitialize() {
        Pulse.log(MOD_ID, "$MOD_NAME initializing...");
        
        // Register event listeners
        EventBus.subscribe(GameInitEvent.class, this::onGameInit, MOD_ID);
        EventBus.subscribe(GameTickEvent.class, this::onGameTick, MOD_ID);
        
        Pulse.log(MOD_ID, "$MOD_NAME initialized!");
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
        Pulse.log(MOD_ID, "$MOD_NAME unloading...");
    }
}
EOF

# Generate README
cat > "$PROJECT_DIR/README.md" << EOF
# $MOD_NAME

A Pulse mod for Project Zomboid.

## Building

1. Update \`build.gradle\` with the correct path to \`Pulse.jar\`
2. Run: \`./gradlew build\`
3. Find the JAR in \`build/libs/\`

## Installation

1. Copy the built JAR to \`ProjectZomboid/mods/\`
2. Enable the mod in-game

## Development

- Main class: \`$PACKAGE.${CLASS_NAME}Mod\`
- Mod ID: \`$MOD_ID\`
EOF

echo ""
echo "Mod project created successfully!"
echo "Location: $PROJECT_DIR"
echo ""
echo "Next steps:"
echo "  1. Update build.gradle with path to Pulse.jar"
echo "  2. Run './gradlew build' to build your mod"
echo "  3. Copy the JAR to your mods folder"
