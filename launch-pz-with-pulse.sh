#!/bin/bash
# ============================================================================
# Pulse Mod Loader - Project Zomboid Development Launcher
# This script is for DEVELOPMENT use - launches PZ with Pulse from source
# For distribution, use PulseLauncher-linux.sh or PulseLauncher-macos.sh
# ============================================================================

# Detect platform
case "$(uname -s)" in
    Linux*)     PLATFORM="Linux";;
    Darwin*)    PLATFORM="macOS";;
    *)          PLATFORM="Unknown";;
esac

echo ""
echo "════════════════════════════════════════"
echo " PULSE MOD LOADER (Development Mode)"
echo " Platform: $PLATFORM"
echo "════════════════════════════════════════"

# Configuration - Update these paths as needed
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PULSE_JAR="$SCRIPT_DIR/build/libs/Pulse.jar"
MODS_DIR="$SCRIPT_DIR/mods"

# Read version
VERSION_FILE="$SCRIPT_DIR/pulse-version.txt"
if [[ -f "$VERSION_FILE" ]]; then
    PULSE_VERSION=$(cat "$VERSION_FILE" | tr -d '\n\r')
else
    PULSE_VERSION="dev"
fi

# Auto-detect PZ path based on platform
if [[ "$PLATFORM" == "Linux" ]]; then
    DEFAULT_PZ_PATH="$HOME/.steam/steam/steamapps/common/ProjectZomboid"
    ALT_PZ_PATH="$HOME/.local/share/Steam/steamapps/common/ProjectZomboid"
elif [[ "$PLATFORM" == "macOS" ]]; then
    DEFAULT_PZ_PATH="$HOME/Library/Application Support/Steam/steamapps/common/ProjectZomboid"
    ALT_PZ_PATH="/Applications/Project Zomboid.app/Contents/MacOS"
else
    DEFAULT_PZ_PATH=""
    ALT_PZ_PATH=""
fi

# Use environment variable or default
if [[ -n "$PZ_PATH" ]]; then
    : # Use provided PZ_PATH
elif [[ -d "$DEFAULT_PZ_PATH" ]]; then
    PZ_PATH="$DEFAULT_PZ_PATH"
elif [[ -d "$ALT_PZ_PATH" ]]; then
    PZ_PATH="$ALT_PZ_PATH"
else
    echo "ERROR: Could not find Project Zomboid installation."
    echo "Please set the PZ_PATH environment variable:"
    echo "  export PZ_PATH=/path/to/ProjectZomboid"
    exit 1
fi

# Check if Pulse.jar exists
if [ ! -f "$PULSE_JAR" ]; then
    echo "ERROR: Pulse.jar not found at $PULSE_JAR"
    echo "Please run './gradlew build' first."
    exit 1
fi

# Create mods directory if not exists
mkdir -p "$MODS_DIR"

# Copy first-party mods if they exist
if [[ -d "$SCRIPT_DIR/first-party-mods" ]]; then
    echo "Copying first-party mods..."
    find "$SCRIPT_DIR/first-party-mods" -name "*.jar" -path "*/build/libs/*" -exec cp -f {} "$MODS_DIR/" \; 2>/dev/null || true
fi

# Count mods
MOD_COUNT=$(find "$MODS_DIR" -maxdepth 1 -name "*.jar" 2>/dev/null | wc -l | tr -d ' ')

echo ""
echo " Pulse Version: $PULSE_VERSION"
echo " PZ Path: $PZ_PATH"
echo " Pulse JAR: $PULSE_JAR"
echo " Mods: $MOD_COUNT mod(s) in $MODS_DIR"
echo ""
echo "════════════════════════════════════════"
echo ""

# Launch PZ with Pulse agent
echo "Launching Project Zomboid with Pulse..."
cd "$PZ_PATH"

# Use PZ's bundled Java or system Java
JAVA_CMD="${PZ_PATH}/jre64/bin/java"
if [ ! -f "$JAVA_CMD" ]; then
    JAVA_CMD="${PZ_PATH}/jre/bin/java"
fi
if [ ! -f "$JAVA_CMD" ]; then
    JAVA_CMD="java"
fi

# Build JVM args
JVM_ARGS=(
    -javaagent:"$PULSE_JAR"
    -Dpulse.mods.dir="$MODS_DIR"
    -Dpulse.debug=true
    -Xms2g -Xmx4g
    -XX:+UseG1GC
    -Djava.library.path="$PZ_PATH:$PZ_PATH/natives"
)

# Add macOS-specific flag
if [[ "$PLATFORM" == "macOS" ]]; then
    JVM_ARGS+=(-XstartOnFirstThread)
fi

# Execute
exec "$JAVA_CMD" "${JVM_ARGS[@]}" \
    -cp "$PZ_PATH/*:$PZ_PATH/zombie.jar" \
    zombie.gameStates.MainScreenState
