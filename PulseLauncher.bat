@echo off
setlocal enabledelayedexpansion
title Pulse Mod Launcher
chcp 65001 >nul 2>&1

:: ============================================================================
:: Pulse Smart Launcher for Project Zomboid (v1.2.0)
:: Injects Pulse.jar as Java Agent - No file modifications!
:: Compatible with paths containing parentheses
:: ============================================================================

:: Paths
set "LAUNCHER_DIR=%~dp0"
set "PULSE_JAR=!LAUNCHER_DIR!Pulse.jar"
set "VERSION_FILE=!LAUNCHER_DIR!pulse-version.txt"
set "MODS_DIR=!LAUNCHER_DIR!mods"
set "CONFIG_FILE=!LAUNCHER_DIR!PulseLauncher.ini"
set "LOG_FILE=!LAUNCHER_DIR!pulse_launcher.log"
set "CRASH_LOG_DIR=!LAUNCHER_DIR!crash-logs"
set "GAME_PATH="
set "JAVA_EXE="
set "PULSE_VERSION=Unknown"
set "MOD_COUNT=0"
set "DEBUG_MODE=false"
set "LAUNCHER_VERSION=1.2.0"

:: Default config
set "MIN_MEMORY=2048m"
set "MAX_MEMORY=4096m"
set "CUSTOM_GAME_PATH="
set "ENABLE_LOGGING=true"

:: Classpath
set "CLASSPATH_LIBS=commons-compress-1.18.jar;istack-commons-runtime.jar;jassimp.jar;javacord-2.0.17-shaded.jar;javax.activation-api.jar;jaxb-api.jar;jaxb-runtime.jar;lwjgl.jar;lwjgl-natives-windows.jar;lwjgl-glfw.jar;lwjgl-glfw-natives-windows.jar;lwjgl-jemalloc.jar;lwjgl-jemalloc-natives-windows.jar;lwjgl-opengl.jar;lwjgl-opengl-natives-windows.jar;lwjgl_util.jar;sqlite-jdbc-3.27.2.1.jar;trove-3.0.3.jar;uncommons-maths-1.2.3.jar;."

:: CLI args
:PARSE_ARGS
if "%~1"=="" goto :ARGS_DONE
if /i "%~1"=="--version" goto :SHOW_VERSION
if /i "%~1"=="-v" goto :SHOW_VERSION
if /i "%~1"=="--help" goto :SHOW_HELP
if /i "%~1"=="-h" goto :SHOW_HELP
if /i "%~1"=="--debug" set "DEBUG_MODE=true" & shift & goto :PARSE_ARGS
if /i "%~1"=="-d" set "DEBUG_MODE=true" & shift & goto :PARSE_ARGS
shift
goto :PARSE_ARGS

:SHOW_VERSION
if exist "!VERSION_FILE!" set /p PULSE_VERSION=<"!VERSION_FILE!"
echo Pulse Launcher v!LAUNCHER_VERSION!
echo Pulse Core: !PULSE_VERSION!
exit /b 0

:SHOW_HELP
echo.
echo  Pulse Launcher - Project Zomboid Mod Loader
echo  Usage: PulseLauncher.bat [--debug] [--help] [--version]
echo.
exit /b 0

:ARGS_DONE

:: Language detection
set "LANG=EN"
for /f "tokens=3" %%a in ('reg query "HKCU\Control Panel\International" /v LocaleName 2^>nul') do set "LOCALE=%%a"
if "!LOCALE:~0,2!"=="ko" set "LANG=KO"

:: Messages based on language
if "!LANG!"=="KO" (
    set "MSG_NOT_FOUND=오류: Pulse.jar를 찾을 수 없습니다!"
    set "MSG_JAVA_ERR=오류: Java를 찾을 수 없습니다!"
    set "MSG_LAUNCHING=Pulse로 Project Zomboid 실행 중..."
    set "MSG_EXIT_ERR=게임 오류 코드"
    set "MSG_ENTER_PATH=경로 입력: "
    set "MSG_MODS=개의 모드 감지됨"
) else (
    set "MSG_NOT_FOUND=ERROR: Pulse.jar not found!"
    set "MSG_JAVA_ERR=ERROR: Java not found!"
    set "MSG_LAUNCHING=Launching Project Zomboid with Pulse..."
    set "MSG_EXIT_ERR=Game exited with error code"
    set "MSG_ENTER_PATH=Enter path: "
    set "MSG_MODS=mod(s) detected"
)

goto :MAIN

:: Log function
:LOG
if "!ENABLE_LOGGING!"=="true" echo [!DATE! !TIME!] %~1 >> "!LOG_FILE!"
if "!DEBUG_MODE!"=="true" echo [DEBUG] %~1
goto :eof

:: ============================================================================
:: Main
:: ============================================================================
:MAIN

:: Init log
if "!ENABLE_LOGGING!"=="true" (
    echo ===== Pulse Launcher Log ===== > "!LOG_FILE!"
    echo Started: !DATE! !TIME! >> "!LOG_FILE!"
)

:: Load config
if exist "!CONFIG_FILE!" (
    for /f "usebackq tokens=1,* delims==" %%a in ("!CONFIG_FILE!") do (
        set "K=%%a"
        set "V=%%b"
        if not "!K:~0,1!"=="#" if defined K (
            if /i "!K!"=="MinMemory" set "MIN_MEMORY=!V!"
            if /i "!K!"=="MaxMemory" set "MAX_MEMORY=!V!"
            if /i "!K!"=="GamePath" set "CUSTOM_GAME_PATH=!V!"
            if /i "!K!"=="EnableLogging" set "ENABLE_LOGGING=!V!"
        )
    )
) else (
    :: Create config
    (
        echo # Pulse Launcher Config
        echo MinMemory=2048m
        echo MaxMemory=4096m
        echo GamePath=
        echo EnableLogging=true
    ) > "!CONFIG_FILE!"
)

:: Read version
if exist "!VERSION_FILE!" set /p PULSE_VERSION=<"!VERSION_FILE!"

:: Create mods folder if not exists
if not exist "!MODS_DIR!" (
    mkdir "!MODS_DIR!"
    call :LOG "Created mods directory: !MODS_DIR!"
)

:: Count mods
if exist "!MODS_DIR!" (
    for %%f in ("!MODS_DIR!\*.jar") do set /a MOD_COUNT+=1
)

:: Header
echo.
echo  ========================================================================
echo   PULSE MOD LAUNCHER v!LAUNCHER_VERSION! for Project Zomboid
echo  ========================================================================
echo   Pulse Version: !PULSE_VERSION!
echo   Mods: !MOD_COUNT! !MSG_MODS!
if "!DEBUG_MODE!"=="true" echo   Mode: DEBUG
echo  ========================================================================
echo.

if "!DEBUG_MODE!"=="true" (
    echo [DEBUG] Launcher: !LAUNCHER_DIR!
    echo [DEBUG] Pulse: !PULSE_JAR!
    echo [DEBUG] Memory: !MIN_MEMORY! - !MAX_MEMORY!
    echo.
)

:: ============================================================================
:: Step 1: Check Pulse.jar
:: ============================================================================
call :LOG "Checking Pulse.jar..."

if not exist "!PULSE_JAR!" (
    echo  !MSG_NOT_FOUND!
    echo  Path: !PULSE_JAR!
    pause
    exit /b 1
)
echo  [OK] Found Pulse.jar

:: ============================================================================
:: Step 2: Find Game Path
:: ============================================================================
call :LOG "Finding game path..."

:: Custom path
if defined CUSTOM_GAME_PATH (
    if not "!CUSTOM_GAME_PATH!"=="" (
        set "GAME_PATH=!CUSTOM_GAME_PATH!"
        if not "!GAME_PATH:~-1!"=="\" set "GAME_PATH=!GAME_PATH!\"
        if exist "!GAME_PATH!ProjectZomboid64.bat" goto :FOUND
    )
)

:: Launcher directory
if exist "!LAUNCHER_DIR!ProjectZomboid64.bat" (
    set "GAME_PATH=!LAUNCHER_DIR!"
    goto :FOUND
)

:: Registry
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 108600" /v InstallLocation 2^>nul') do set "GAME_PATH=%%b"
if not defined GAME_PATH (
    for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 108600" /v InstallLocation 2^>nul') do set "GAME_PATH=%%b"
)
if defined GAME_PATH (
    if not "!GAME_PATH:~-1!"=="\" set "GAME_PATH=!GAME_PATH!\"
    if exist "!GAME_PATH!ProjectZomboid64.bat" goto :FOUND
    set "GAME_PATH="
)

:: Common paths - all drives
for %%D in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%D:\Steam\steamapps\common\ProjectZomboid\ProjectZomboid64.bat" (
        set "GAME_PATH=%%D:\Steam\steamapps\common\ProjectZomboid\"
        goto :FOUND
    )
    if exist "%%D:\SteamLibrary\steamapps\common\ProjectZomboid\ProjectZomboid64.bat" (
        set "GAME_PATH=%%D:\SteamLibrary\steamapps\common\ProjectZomboid\"
        goto :FOUND
    )
    if exist "%%D:\Program Files\Steam\steamapps\common\ProjectZomboid\ProjectZomboid64.bat" (
        set "GAME_PATH=%%D:\Program Files\Steam\steamapps\common\ProjectZomboid\"
        goto :FOUND
    )
    if exist "%%D:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\ProjectZomboid64.bat" (
        set "GAME_PATH=%%D:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\"
        goto :FOUND
    )
    if exist "%%D:\Games\Steam\steamapps\common\ProjectZomboid\ProjectZomboid64.bat" (
        set "GAME_PATH=%%D:\Games\Steam\steamapps\common\ProjectZomboid\"
        goto :FOUND
    )
)

:: Manual input
echo.
echo  Game not found. Please enter the path manually.
echo  Example: D:\Steam\steamapps\common\ProjectZomboid
echo.
set /p "GAME_PATH=!MSG_ENTER_PATH!"
if not defined GAME_PATH (
    echo  No path entered.
    pause
    exit /b 1
)
if not "!GAME_PATH:~-1!"=="\" set "GAME_PATH=!GAME_PATH!\"
if not exist "!GAME_PATH!ProjectZomboid64.bat" (
    echo  Invalid path.
    pause
    exit /b 1
)

:FOUND
call :LOG "Game path: !GAME_PATH!"
echo  [OK] Game: !GAME_PATH!

:: ============================================================================
:: Step 3: Find Java
:: ============================================================================
call :LOG "Finding Java..."

set "JAVA_EXE=!GAME_PATH!jre64\bin\java.exe"
if not exist "!JAVA_EXE!" set "JAVA_EXE=!GAME_PATH!jre\bin\java.exe"
if not exist "!JAVA_EXE!" (
    echo  !MSG_JAVA_ERR!
    pause
    exit /b 1
)
echo  [OK] Java found

:: ============================================================================
:: Step 4: Build classpath
:: ============================================================================
set "FULL_CLASSPATH="
for %%L in (%CLASSPATH_LIBS%) do (
    if "!FULL_CLASSPATH!"=="" (
        set "FULL_CLASSPATH=!GAME_PATH!%%L"
    ) else (
        set "FULL_CLASSPATH=!FULL_CLASSPATH!;!GAME_PATH!%%L"
    )
)

:: ============================================================================
:: Step 5: Launch
:: ============================================================================
set "LIB_PATH=!GAME_PATH!;!GAME_PATH!natives;!GAME_PATH!win64;."
set "MAIN_CLASS=zombie.gameStates.MainScreenState"

echo.
echo  ========================================================================
echo   !MSG_LAUNCHING!
echo   Memory: !MIN_MEMORY! - !MAX_MEMORY!
echo  ========================================================================
echo.

call :LOG "Launching..."
cd /d "!GAME_PATH!"

"!JAVA_EXE!" ^
    -javaagent:"!PULSE_JAR!" ^
    -Djava.awt.headless=true ^
    -Dzomboid.steam=1 ^
    -Dzomboid.znetlog=1 ^
    "-Djava.library.path=!LIB_PATH!" ^
    -Xms!MIN_MEMORY! ^
    -Xmx!MAX_MEMORY! ^
    -XX:+UseG1GC ^
    -XX:-OmitStackTraceInFastThrow ^
    -Djdk.lang.Process.allowAmbiguousCommands=true ^
    -cp "!FULL_CLASSPATH!" ^
    !MAIN_CLASS!

set "EXIT_CODE=!ERRORLEVEL!"

:: ============================================================================
:: Step 6: Exit handling
:: ============================================================================
if "!ENABLE_LOGGING!"=="true" echo [!DATE! !TIME!] Exit: !EXIT_CODE! >> "!LOG_FILE!"

if !EXIT_CODE! NEQ 0 (
    echo.
    echo  !MSG_EXIT_ERR!: !EXIT_CODE!
    
    :: Crash log
    if not exist "!CRASH_LOG_DIR!" mkdir "!CRASH_LOG_DIR!"
    for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set "DT=%%I"
    set "CRASH=!CRASH_LOG_DIR!\crash_!DT:~0,8!_!DT:~8,6!.log"
    (
        echo PULSE CRASH LOG
        echo Time: !DATE! !TIME!
        echo Exit: !EXIT_CODE!
        echo Game: !GAME_PATH!
        echo Java: !JAVA_EXE!
        echo Memory: !MIN_MEMORY! - !MAX_MEMORY!
    ) > "!CRASH!"
    echo  Crash log: !CRASH!
    echo.
    pause
)

endlocal
exit /b !EXIT_CODE!
