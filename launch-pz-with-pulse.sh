#!/bin/bash
# Pulse Mod Loader - Project Zomboid Launcher
# This script launches Project Zomboid with Pulse as a Java agent

# Configuration - Update these paths as needed
PZ_PATH="${PZ_PATH:-$HOME/.steam/steam/steamapps/common/ProjectZomboid}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PULSE_JAR="$SCRIPT_DIR/build/libs/Pulse.jar"
MODS_DIR="$SCRIPT_DIR/mods"

# Check if Pulse.jar exists
if [ ! -f "$PULSE_JAR" ]; then
    echo "ERROR: Pulse.jar not found!"
    echo "Please run './gradlew build' first."
    exit 1
fi

# Create mods directory if not exists
mkdir -p "$MODS_DIR"

# Copy first-party mods
echo "Copying first-party mods..."
cp -f "$SCRIPT_DIR"/first-party-mods/*/build/libs/*.jar "$MODS_DIR/" 2>/dev/null || true

echo ""
echo "========================================"
echo " PULSE MOD LOADER"
echo "========================================"
echo " PZ Path: $PZ_PATH"
echo " Pulse:   $PULSE_JAR"
echo " Mods:    $MODS_DIR"
echo "========================================"
echo ""

# Launch PZ with Pulse agent
echo "Launching Project Zomboid with Pulse..."
cd "$PZ_PATH"

# Use PZ's bundled Java or system Java
JAVA_CMD="${PZ_PATH}/jre64/bin/java"
if [ ! -f "$JAVA_CMD" ]; then
    JAVA_CMD="java"
fi

"$JAVA_CMD" \
    -javaagent:"$PULSE_JAR" \
    -Dpulse.mods.dir="$MODS_DIR" \
    -Dpulse.debug=true \
    -Xms2g -Xmx4g \
    -Djava.library.path="$PZ_PATH:$PZ_PATH/natives" \
    -cp "$PZ_PATH/*:$PZ_PATH/zombie.jar" \
    zombie.gameStates.MainScreenState
