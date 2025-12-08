#!/bin/bash
# ============================================================================
# Pulse Smart Launcher for Project Zomboid (Linux Edition)
# A wrapper launcher that injects Pulse.jar as a Java Agent
# Features: Auto-detection, Config file, Logging, Multi-language support
# ============================================================================

set -e

# ----------------------------------------------------------------------------
# Paths and Files
# ----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PULSE_JAR="$SCRIPT_DIR/Pulse.jar"
VERSION_FILE="$SCRIPT_DIR/pulse-version.txt"
MODS_DIR="$SCRIPT_DIR/mods"
CONFIG_FILE="$SCRIPT_DIR/PulseLauncher.conf"
LOG_FILE="$SCRIPT_DIR/pulse_launcher.log"
CRASH_LOG_DIR="$SCRIPT_DIR/crash-logs"

# Default Configuration
MIN_MEMORY="2048m"
MAX_MEMORY="4096m"
CUSTOM_GAME_PATH=""
ENABLE_LOGGING="true"
PULSE_VERSION="Unknown"
MOD_COUNT=0
GAME_PATH=""
DEBUG_MODE="false"
LAUNCHER_VERSION="1.1.0"

# ----------------------------------------------------------------------------
# CLI Argument Parsing
# ----------------------------------------------------------------------------
show_version() {
    if [[ -f "$VERSION_FILE" ]]; then
        PULSE_VERSION=$(cat "$VERSION_FILE" | tr -d '\n\r')
    fi
    echo "Pulse Launcher v$LAUNCHER_VERSION"
    echo "Pulse Core: $PULSE_VERSION"
    exit 0
}

show_help() {
    echo ""
    echo "  Pulse Launcher - Project Zomboid Mod Loader (Linux)"
    echo "  ===================================================="
    echo ""
    echo "  Usage: ./PulseLauncher-linux.sh [OPTIONS]"
    echo ""
    echo "  Options:"
    echo "    --version, -v      Show version information"
    echo "    --help, -h         Show this help message"
    echo "    --debug, -d        Enable debug mode (verbose output)"
    echo ""
    echo "  Configuration:"
    echo "    Edit PulseLauncher.conf to customize memory settings,"
    echo "    game path, and language preferences."
    echo ""
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --version|-v) show_version ;;
        --help|-h) show_help ;;
        --debug|-d) DEBUG_MODE="true"; shift ;;
        *) shift ;;
    esac
done

# ----------------------------------------------------------------------------
# Language Detection
# ----------------------------------------------------------------------------
detect_language() {
    if [[ "$LANG" == ko* ]] || [[ "$LC_ALL" == ko* ]]; then
        LANG_CODE="KO"
    else
        LANG_CODE="EN"
    fi
}

# ----------------------------------------------------------------------------
# Messages
# ----------------------------------------------------------------------------
set_messages() {
    if [[ "$LANG_CODE" == "KO" ]]; then
        MSG_TITLE="Pulse 모드 런처"
        MSG_CHECKING_PULSE="Pulse.jar 확인 중..."
        MSG_PULSE_FOUND="Pulse.jar 발견:"
        MSG_PULSE_NOT_FOUND="오류: Pulse.jar를 찾을 수 없습니다!"
        MSG_SEARCHING_GAME="Project Zomboid 설치 경로 검색 중..."
        MSG_FOUND_PATH="발견:"
        MSG_NOT_FOUND="Project Zomboid를 찾을 수 없습니다."
        MSG_MANUAL_INPUT="Project Zomboid 폴더 경로를 입력하세요:"
        MSG_GAME_CONFIRMED="게임 설치 확인됨:"
        MSG_JAVA_FOUND="Java 발견:"
        MSG_JAVA_NOT_FOUND="오류: Java 런타임을 찾을 수 없습니다!"
        MSG_LAUNCHING="Pulse 모드 로더로 Project Zomboid 실행 중..."
        MSG_VERSION="버전:"
        MSG_MODS_DETECTED="개의 Pulse 모드 감지됨"
        MSG_NO_MODS="mods 폴더에 Pulse 모드가 없습니다"
        MSG_STEAM_TIP="[선택사항] Steam 연동 (고급 사용자용)"
    else
        MSG_TITLE="Pulse Mod Launcher"
        MSG_CHECKING_PULSE="Checking for Pulse.jar..."
        MSG_PULSE_FOUND="Found Pulse.jar:"
        MSG_PULSE_NOT_FOUND="ERROR: Pulse.jar not found!"
        MSG_SEARCHING_GAME="Searching for Project Zomboid installation..."
        MSG_FOUND_PATH="Found:"
        MSG_NOT_FOUND="Could not find Project Zomboid."
        MSG_MANUAL_INPUT="Please enter the path to your Project Zomboid folder:"
        MSG_GAME_CONFIRMED="Game installation confirmed:"
        MSG_JAVA_FOUND="Found Java:"
        MSG_JAVA_NOT_FOUND="ERROR: Java runtime not found!"
        MSG_LAUNCHING="Launching Project Zomboid with Pulse Mod Loader..."
        MSG_VERSION="Version:"
        MSG_MODS_DETECTED="Pulse mod(s) detected"
        MSG_NO_MODS="No Pulse mods found in mods folder"
        MSG_STEAM_TIP="[OPTIONAL] Steam Integration (Advanced Users)"
    fi
}

# ----------------------------------------------------------------------------
# Logging Function
# ----------------------------------------------------------------------------
log() {
    local message="$1"
    echo "$message"
    if [[ "$ENABLE_LOGGING" == "true" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $message" >> "$LOG_FILE"
    fi
}

# ----------------------------------------------------------------------------
# Load Configuration
# ----------------------------------------------------------------------------
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        log "[Pulse] Loading config: $CONFIG_FILE"
        while IFS='=' read -r key value; do
            # Skip comments and empty lines
            [[ "$key" =~ ^#.*$ ]] && continue
            [[ -z "$key" ]] && continue
            
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)
            
            case "$key" in
                MinMemory) MIN_MEMORY="$value" ;;
                MaxMemory) MAX_MEMORY="$value" ;;
                GamePath) CUSTOM_GAME_PATH="$value" ;;
                EnableLogging) ENABLE_LOGGING="$value" ;;
            esac
        done < "$CONFIG_FILE"
    else
        # Create default config
        log "[Pulse] Creating default config: $CONFIG_FILE"
        cat > "$CONFIG_FILE" << 'EOF'
# Pulse Launcher Configuration File (Linux)
# 펄스 런처 설정 파일 (리눅스)

# Memory Settings (메모리 설정)
MinMemory=2048m
MaxMemory=4096m

# Custom Game Path (사용자 지정 게임 경로)
# Leave empty for auto-detection (자동 감지를 위해 비워두세요)
GamePath=

# Enable Logging (로그 기록 활성화)
EnableLogging=true
EOF
    fi
}

# ----------------------------------------------------------------------------
# Read Pulse Version
# ----------------------------------------------------------------------------
read_version() {
    if [[ -f "$VERSION_FILE" ]]; then
        PULSE_VERSION=$(cat "$VERSION_FILE" | tr -d '\n\r')
    fi
}

# ----------------------------------------------------------------------------
# Count Installed Mods
# ----------------------------------------------------------------------------
count_mods() {
    if [[ -d "$MODS_DIR" ]]; then
        MOD_COUNT=$(find "$MODS_DIR" -maxdepth 1 -name "*.jar" 2>/dev/null | wc -l)
    fi
}

# ----------------------------------------------------------------------------
# Display Header
# ----------------------------------------------------------------------------
display_header() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║           🔥 PULSE MOD LAUNCHER v$LAUNCHER_VERSION for Project Zomboid      ║"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    echo "║  Pulse $MSG_VERSION $PULSE_VERSION"
    echo "║  Mods: $MOD_COUNT $MSG_MODS_DETECTED"
    if [[ "$DEBUG_MODE" == "true" ]]; then
        echo "║  Mode: DEBUG"
    fi
    echo "╠═══════════════════════════════════════════════════════════════╣"
    echo "║  Injects Pulse.jar as Java Agent - No file modifications!     ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    
    if [[ $MOD_COUNT -eq 0 ]]; then
        echo "  [INFO] $MSG_NO_MODS"
        echo ""
    fi
    
    # Debug mode: show environment details
    if [[ "$DEBUG_MODE" == "true" ]]; then
        echo "  [DEBUG] ─────────────────────────────────────────────────"
        echo "  [DEBUG] Script Dir:   $SCRIPT_DIR"
        echo "  [DEBUG] Pulse JAR:    $PULSE_JAR"
        echo "  [DEBUG] Config File:  $CONFIG_FILE"
        echo "  [DEBUG] Mods Dir:     $MODS_DIR"
        echo "  [DEBUG] Memory:       $MIN_MEMORY - $MAX_MEMORY"
        echo "  [DEBUG] Language:     $LANG_CODE"
        echo "  [DEBUG] ─────────────────────────────────────────────────"
        echo ""
        # Enable verbose bash execution
        set -x
    fi
}

# ----------------------------------------------------------------------------
# Auto-detect Game Path
# ----------------------------------------------------------------------------
detect_game_path() {
    log "[Pulse] $MSG_SEARCHING_GAME"
    
    # Check custom path first
    if [[ -n "$CUSTOM_GAME_PATH" ]] && [[ -d "$CUSTOM_GAME_PATH" ]]; then
        if [[ -f "$CUSTOM_GAME_PATH/ProjectZomboid64" ]] || [[ -f "$CUSTOM_GAME_PATH/ProjectZomboid32" ]]; then
            GAME_PATH="$CUSTOM_GAME_PATH"
            log "[Pulse]   > Custom path: $GAME_PATH"
            return 0
        fi
    fi
    
    # Common Steam paths for Linux
    local steam_paths=(
        "$HOME/.steam/steam/steamapps/common/ProjectZomboid"
        "$HOME/.local/share/Steam/steamapps/common/ProjectZomboid"
        "$HOME/.steam/debian-installation/steamapps/common/ProjectZomboid"
        "/usr/share/games/ProjectZomboid"
    )
    
    for path in "${steam_paths[@]}"; do
        if [[ -d "$path" ]]; then
            if [[ -f "$path/ProjectZomboid64" ]] || [[ -f "$path/ProjectZomboid32" ]] || [[ -f "$path/ProjectZomboid.sh" ]]; then
                GAME_PATH="$path"
                log "[Pulse]   > $MSG_FOUND_PATH $GAME_PATH"
                return 0
            fi
        fi
    done
    
    # Parse Steam libraryfolders.vdf
    local library_file="$HOME/.steam/steam/steamapps/libraryfolders.vdf"
    if [[ -f "$library_file" ]]; then
        while IFS= read -r line; do
            if [[ "$line" == *'"path"'* ]]; then
                local lib_path=$(echo "$line" | sed 's/.*"\([^"]*\)".*/\1/')
                local pz_path="$lib_path/steamapps/common/ProjectZomboid"
                if [[ -d "$pz_path" ]]; then
                    GAME_PATH="$pz_path"
                    log "[Pulse]   > Found in Steam library: $GAME_PATH"
                    return 0
                fi
            fi
        done < "$library_file"
    fi
    
    # Manual input
    log "[Pulse] $MSG_NOT_FOUND"
    echo ""
    echo "$MSG_MANUAL_INPUT"
    echo "Example: /home/user/.steam/steam/steamapps/common/ProjectZomboid"
    echo ""
    read -r -p "Enter path: " GAME_PATH
    
    if [[ -z "$GAME_PATH" ]] || [[ ! -d "$GAME_PATH" ]]; then
        echo "ERROR: Invalid path!"
        exit 1
    fi
}

# ----------------------------------------------------------------------------
# Main Execution
# ----------------------------------------------------------------------------
main() {
    # Initialize
    detect_language
    set_messages
    load_config
    read_version
    count_mods
    
    # Display header
    display_header
    
    # Check Pulse.jar
    log "[Pulse] $MSG_CHECKING_PULSE"
    if [[ ! -f "$PULSE_JAR" ]]; then
        log "[Pulse] $MSG_PULSE_NOT_FOUND"
        echo ""
        echo "╔═══════════════════════════════════════════════════════════════╗"
        echo "║  $MSG_PULSE_NOT_FOUND"
        echo "╠═══════════════════════════════════════════════════════════════╣"
        echo "║  Please place Pulse.jar in: $SCRIPT_DIR"
        echo "╚═══════════════════════════════════════════════════════════════╝"
        exit 1
    fi
    log "[Pulse] $MSG_PULSE_FOUND $PULSE_JAR"
    
    # Detect game path
    detect_game_path
    log "[Pulse] $MSG_GAME_CONFIRMED $GAME_PATH"
    
    # Find Java
    JAVA_CMD="$GAME_PATH/jre64/bin/java"
    if [[ ! -f "$JAVA_CMD" ]]; then
        JAVA_CMD="$GAME_PATH/jre/bin/java"
    fi
    if [[ ! -f "$JAVA_CMD" ]]; then
        JAVA_CMD="java"  # Fall back to system Java
    fi
    
    if ! command -v "$JAVA_CMD" &> /dev/null && [[ ! -f "$JAVA_CMD" ]]; then
        log "[Pulse] $MSG_JAVA_NOT_FOUND"
        exit 1
    fi
    log "[Pulse] $MSG_JAVA_FOUND $JAVA_CMD"
    
    # Launch message
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║  $MSG_LAUNCHING"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Create mods directory if not exists
    mkdir -p "$MODS_DIR"
    
    # Change to game directory
    cd "$GAME_PATH"
    
    # Launch with exec to replace process (better Steam integration)
    exec "$JAVA_CMD" \
        -javaagent:"$PULSE_JAR" \
        -Dpulse.mods.dir="$MODS_DIR" \
        -Djava.library.path="$GAME_PATH:$GAME_PATH/natives" \
        -Xms"$MIN_MEMORY" \
        -Xmx"$MAX_MEMORY" \
        -XX:+UseG1GC \
        -XX:-OmitStackTraceInFastThrow \
        -cp "$GAME_PATH/*:$GAME_PATH/zombie.jar" \
        zombie.gameStates.MainScreenState
}

# Run main
main "$@"
