#!/bin/bash
# ============================================================================
# Pulse Smart Launcher for Project Zomboid (macOS Edition v1.2.0)
# A wrapper launcher that injects Pulse.jar as a Java Agent
# Features: Auto-detection, Config file, Logging, Multi-language support
# ============================================================================

# Exit on error (but handle errors gracefully)
set -e

# Paths
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
LAUNCHER_VERSION="1.2.0"

# ----------------------------------------------------------------------------
# CLI Argument Parsing
# ----------------------------------------------------------------------------
show_version() {
    [[ -f "$VERSION_FILE" ]] && PULSE_VERSION=$(cat "$VERSION_FILE" | tr -d '\n\r')
    echo "Pulse Launcher v$LAUNCHER_VERSION"
    echo "Pulse Core: $PULSE_VERSION"
    exit 0
}

show_help() {
    echo ""
    echo "  Pulse Launcher - Project Zomboid Mod Loader (macOS)"
    echo "  ===================================================="
    echo ""
    echo "  Usage: ./PulseLauncher-macos.sh [OPTIONS]"
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
        MSG_PULSE_NOT_FOUND="오류: Pulse.jar를 찾을 수 없습니다!"
        MSG_SEARCHING_GAME="Project Zomboid 설치 경로 검색 중..."
        MSG_FOUND_PATH="발견:"
        MSG_NOT_FOUND="Project Zomboid를 찾을 수 없습니다."
        MSG_MANUAL_INPUT="Project Zomboid 폴더 경로를 입력하세요:"
        MSG_GAME_CONFIRMED="게임 설치 확인됨:"
        MSG_JAVA_NOT_FOUND="오류: Java 런타임을 찾을 수 없습니다!"
        MSG_LAUNCHING="Pulse 모드 로더로 Project Zomboid 실행 중..."
        MSG_VERSION="버전"
        MSG_MODS="개의 모드 감지됨"
        MSG_NO_MODS="mods 폴더에 Pulse 모드가 없습니다"
        MSG_EXIT_ERROR="게임 오류 코드"
    else
        MSG_PULSE_NOT_FOUND="ERROR: Pulse.jar not found!"
        MSG_SEARCHING_GAME="Searching for Project Zomboid installation..."
        MSG_FOUND_PATH="Found:"
        MSG_NOT_FOUND="Could not find Project Zomboid."
        MSG_MANUAL_INPUT="Please enter the path to your Project Zomboid folder:"
        MSG_GAME_CONFIRMED="Game installation confirmed:"
        MSG_JAVA_NOT_FOUND="ERROR: Java runtime not found!"
        MSG_LAUNCHING="Launching Project Zomboid with Pulse Mod Loader..."
        MSG_VERSION="Version"
        MSG_MODS="mod(s) detected"
        MSG_NO_MODS="No Pulse mods found in mods folder"
        MSG_EXIT_ERROR="Game exited with error code"
    fi
}

# ----------------------------------------------------------------------------
# Logging Function
# ----------------------------------------------------------------------------
log() {
    local message="$1"
    [[ "$DEBUG_MODE" == "true" ]] && echo "[DEBUG] $message"
    [[ "$ENABLE_LOGGING" == "true" ]] && echo "[$(date '+%Y-%m-%d %H:%M:%S')] $message" >> "$LOG_FILE"
}

# ----------------------------------------------------------------------------
# Load Configuration
# ----------------------------------------------------------------------------
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        log "Loading config: $CONFIG_FILE"
        while IFS='=' read -r key value; do
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
        log "Creating default config: $CONFIG_FILE"
        cat > "$CONFIG_FILE" << 'EOF'
# Pulse Launcher Configuration File (macOS)
# 펄스 런처 설정 파일 (macOS)

# Memory Settings / 메모리 설정
MinMemory=2048m
MaxMemory=4096m

# Custom Game Path / 사용자 지정 게임 경로
# Leave empty for auto-detection / 자동 감지를 위해 비워두세요
GamePath=

# Enable Logging / 로그 기록 활성화
EnableLogging=true
EOF
    fi
}

# ----------------------------------------------------------------------------
# Read Pulse Version and Count Mods
# ----------------------------------------------------------------------------
read_version() {
    [[ -f "$VERSION_FILE" ]] && PULSE_VERSION=$(cat "$VERSION_FILE" | tr -d '\n\r')
}

count_mods() {
    [[ -d "$MODS_DIR" ]] && MOD_COUNT=$(find "$MODS_DIR" -maxdepth 1 -name "*.jar" 2>/dev/null | wc -l | tr -d ' ')
}

# ----------------------------------------------------------------------------
# Display Header
# ----------------------------------------------------------------------------
display_header() {
    echo ""
    echo "========================================================================"
    echo "  PULSE MOD LAUNCHER v$LAUNCHER_VERSION for Project Zomboid (macOS)"
    echo "========================================================================"
    echo "  Pulse $MSG_VERSION: $PULSE_VERSION"
    echo "  Mods: $MOD_COUNT $MSG_MODS"
    [[ "$DEBUG_MODE" == "true" ]] && echo "  Mode: DEBUG"
    echo "------------------------------------------------------------------------"
    echo "  Injects Pulse.jar as Java Agent - No file modifications!"
    echo "========================================================================"
    echo ""
    
    [[ $MOD_COUNT -eq 0 ]] && echo "  [INFO] $MSG_NO_MODS" && echo ""
    
    if [[ "$DEBUG_MODE" == "true" ]]; then
        echo "  [DEBUG] Script Dir: $SCRIPT_DIR"
        echo "  [DEBUG] Pulse JAR:  $PULSE_JAR"
        echo "  [DEBUG] Memory:     $MIN_MEMORY - $MAX_MEMORY"
        echo ""
    fi
}

# ----------------------------------------------------------------------------
# Auto-detect Game Path (macOS specific)
# ----------------------------------------------------------------------------
detect_game_path() {
    log "$MSG_SEARCHING_GAME"
    
    # Custom path
    if [[ -n "$CUSTOM_GAME_PATH" ]] && [[ -d "$CUSTOM_GAME_PATH" ]]; then
        GAME_PATH="$CUSTOM_GAME_PATH"
        log "Custom path: $GAME_PATH"
        return 0
    fi
    
    # macOS Steam paths
    local steam_paths=(
        "$HOME/Library/Application Support/Steam/steamapps/common/ProjectZomboid"
        "/Applications/Project Zomboid.app/Contents/MacOS"
        "$HOME/Applications/Project Zomboid.app/Contents/MacOS"
        "/Applications/ProjectZomboid"
        "$HOME/Games/ProjectZomboid"
    )
    
    for path in "${steam_paths[@]}"; do
        if [[ -d "$path" ]]; then
            GAME_PATH="$path"
            log "$MSG_FOUND_PATH $GAME_PATH"
            return 0
        fi
    done
    
    # Parse Steam libraryfolders.vdf
    local library_file="$HOME/Library/Application Support/Steam/steamapps/libraryfolders.vdf"
    if [[ -f "$library_file" ]]; then
        while IFS= read -r line; do
            if [[ "$line" == *'"path"'* ]]; then
                local lib_path=$(echo "$line" | sed 's/.*"\([^"]*\)".*/\1/')
                local pz_path="$lib_path/steamapps/common/ProjectZomboid"
                if [[ -d "$pz_path" ]]; then
                    GAME_PATH="$pz_path"
                    log "Found in Steam library: $GAME_PATH"
                    return 0
                fi
            fi
        done < "$library_file"
    fi
    
    # Manual input
    log "$MSG_NOT_FOUND"
    echo ""
    echo "  $MSG_MANUAL_INPUT"
    echo "  Example: ~/Library/Application Support/Steam/steamapps/common/ProjectZomboid"
    echo ""
    read -r -p "  Enter path: " GAME_PATH
    
    if [[ -z "$GAME_PATH" ]] || [[ ! -d "$GAME_PATH" ]]; then
        echo "  ERROR: Invalid path!"
        exit 1
    fi
}

# ----------------------------------------------------------------------------
# Collect Crash Logs
# ----------------------------------------------------------------------------
collect_crash_logs() {
    mkdir -p "$CRASH_LOG_DIR"
    local crash_file="$CRASH_LOG_DIR/crash_$(date '+%Y%m%d_%H%M%S').log"
    
    {
        echo "PULSE CRASH LOG (macOS)"
        echo "Time: $(date)"
        echo "Exit Code: $EXIT_CODE"
        echo "Game Path: $GAME_PATH"
        echo "Java: $JAVA_CMD"
        echo "Memory: $MIN_MEMORY - $MAX_MEMORY"
        echo ""
        echo "--- Launcher Log ---"
        [[ -f "$LOG_FILE" ]] && cat "$LOG_FILE"
        echo ""
        echo "--- PZ Console Log (last 100 lines) ---"
        local pz_log="$HOME/Zomboid/console.txt"
        [[ -f "$pz_log" ]] && tail -100 "$pz_log"
    } > "$crash_file"
    
    echo "  Crash log saved: $crash_file"
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
    
    # Init log
    [[ "$ENABLE_LOGGING" == "true" ]] && echo "===== Pulse Launcher Log (macOS) =====" > "$LOG_FILE"
    
    # Display header
    display_header
    
    # Check Pulse.jar
    if [[ ! -f "$PULSE_JAR" ]]; then
        echo ""
        echo "  ========================================"
        echo "  $MSG_PULSE_NOT_FOUND"
        echo "  Path: $SCRIPT_DIR"
        echo "  ========================================"
        exit 1
    fi
    echo "  [OK] Found Pulse.jar"
    
    # Detect game path
    detect_game_path
    echo "  [OK] $MSG_GAME_CONFIRMED $GAME_PATH"
    
    # Find Java (macOS specific)
    JAVA_CMD=""
    
    # Check bundled JRE locations
    local java_paths=(
        "$GAME_PATH/jre/bin/java"
        "$GAME_PATH/../PlugIns/jre/Contents/Home/bin/java"
        "/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/java"
        "/Library/Java/JavaVirtualMachines/adoptopenjdk-17.jdk/Contents/Home/bin/java"
        "/Library/Java/JavaVirtualMachines/zulu-17.jdk/Contents/Home/bin/java"
        "/opt/homebrew/opt/openjdk@17/bin/java"
        "/usr/local/opt/openjdk@17/bin/java"
    )
    
    for java_path in "${java_paths[@]}"; do
        if [[ -f "$java_path" ]]; then
            JAVA_CMD="$java_path"
            break
        fi
    done
    
    # Fall back to system Java
    if [[ -z "$JAVA_CMD" ]] && command -v java &> /dev/null; then
        JAVA_CMD="java"
    fi
    
    if [[ -z "$JAVA_CMD" ]] || { [[ ! -f "$JAVA_CMD" ]] && ! command -v "$JAVA_CMD" &> /dev/null; }; then
        echo ""
        echo "  $MSG_JAVA_NOT_FOUND"
        echo ""
        echo "  Install Java using Homebrew:"
        echo "    brew install openjdk@17"
        echo ""
        echo "  Or download from: https://adoptium.net/"
        exit 1
    fi
    echo "  [OK] Found Java: $JAVA_CMD"
    
    # Launch
    echo ""
    echo "  ========================================"
    echo "  $MSG_LAUNCHING"
    echo "  Memory: $MIN_MEMORY - $MAX_MEMORY"
    echo "  ========================================"
    echo ""
    
    log "Launching game..."
    mkdir -p "$MODS_DIR"
    cd "$GAME_PATH"
    
    # Build classpath
    CLASSPATH="$GAME_PATH/*:$GAME_PATH/zombie.jar"
    
    # Execute (with macOS-specific flags)
    set +e  # Don't exit on error for game execution
    "$JAVA_CMD" \
        -javaagent:"$PULSE_JAR" \
        -Dpulse.mods.dir="$MODS_DIR" \
        -Djava.library.path="$GAME_PATH:$GAME_PATH/natives" \
        -XstartOnFirstThread \
        -Xms"$MIN_MEMORY" \
        -Xmx"$MAX_MEMORY" \
        -XX:+UseG1GC \
        -XX:-OmitStackTraceInFastThrow \
        -Dapple.awt.application.appearance=system \
        -cp "$CLASSPATH" \
        zombie.gameStates.MainScreenState
    
    EXIT_CODE=$?
    
    if [[ $EXIT_CODE -ne 0 ]]; then
        echo ""
        echo "  $MSG_EXIT_ERROR: $EXIT_CODE"
        collect_crash_logs
    fi
    
    exit $EXIT_CODE
}

# Run main
main "$@"
