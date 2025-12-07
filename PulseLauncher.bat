@echo off
:: ============================================================================
:: Pulse Smart Launcher for Project Zomboid (Enhanced Edition)
:: A wrapper launcher that injects Pulse.jar as a Java Agent
:: Features: Auto-detection, Config file, Logging, Multi-language support
:: ============================================================================
setlocal enabledelayedexpansion
title Pulse Mod Launcher
chcp 65001 >nul 2>&1

:: ----------------------------------------------------------------------------
:: Paths and Files
:: ----------------------------------------------------------------------------
set "LAUNCHER_DIR=%~dp0"
set "PULSE_JAR=%LAUNCHER_DIR%Pulse.jar"
set "CONFIG_FILE=%LAUNCHER_DIR%PulseLauncher.ini"
set "LOG_FILE=%LAUNCHER_DIR%pulse_launcher.log"
set "GAME_PATH="
set "JAVA_EXE="

:: ----------------------------------------------------------------------------
:: Default Configuration (can be overridden by .ini file)
:: ----------------------------------------------------------------------------
set "MIN_MEMORY=2048m"
set "MAX_MEMORY=4096m"
set "CUSTOM_GAME_PATH="
set "ENABLE_LOGGING=true"
set "LANGUAGE=auto"

:: Classpath libraries (Project Zomboid required libs)
set "CLASSPATH_LIBS=commons-compress-1.18.jar;istack-commons-runtime.jar;jassimp.jar;javacord-2.0.17-shaded.jar;javax.activation-api.jar;jaxb-api.jar;jaxb-runtime.jar;lwjgl.jar;lwjgl-natives-windows.jar;lwjgl-glfw.jar;lwjgl-glfw-natives-windows.jar;lwjgl-jemalloc.jar;lwjgl-jemalloc-natives-windows.jar;lwjgl-opengl.jar;lwjgl-opengl-natives-windows.jar;lwjgl_util.jar;sqlite-jdbc-3.27.2.1.jar;trove-3.0.3.jar;uncommons-maths-1.2.3.jar;."

:: ----------------------------------------------------------------------------
:: Language Detection and Messages
:: ----------------------------------------------------------------------------
:INIT_LANGUAGE
:: Auto-detect system language (Korean = 0412, English = 0409)
if "%LANGUAGE%"=="auto" (
    for /f "tokens=3" %%a in ('reg query "HKCU\Control Panel\International" /v LocaleName 2^>nul') do set "LOCALE=%%a"
    if "!LOCALE:~0,2!"=="ko" (
        set "LANG=KO"
    ) else (
        set "LANG=EN"
    )
) else if /i "%LANGUAGE%"=="ko" (
    set "LANG=KO"
) else (
    set "LANG=EN"
)

:: Korean Messages
if "%LANG%"=="KO" (
    set "MSG_TITLE=Pulse 모드 런처"
    set "MSG_CHECKING_PULSE=Pulse.jar 확인 중..."
    set "MSG_PULSE_FOUND=Pulse.jar 발견:"
    set "MSG_PULSE_NOT_FOUND=오류: Pulse.jar를 찾을 수 없습니다!"
    set "MSG_PULSE_LOCATION=런처와 같은 폴더에 Pulse.jar를 넣어주세요:"
    set "MSG_SEARCHING_GAME=Project Zomboid 설치 경로 검색 중..."
    set "MSG_PRIORITY_1=우선순위 1: 현재 디렉토리 확인..."
    set "MSG_PRIORITY_2=우선순위 2: Windows 레지스트리 확인..."
    set "MSG_PRIORITY_3=우선순위 3: 기본 Steam 경로 확인..."
    set "MSG_PRIORITY_4=우선순위 4: Steam 라이브러리 폴더 확인..."
    set "MSG_PRIORITY_5=우선순위 5: 자동 감지 실패. 수동 입력 필요."
    set "MSG_FOUND_LAUNCHER_DIR=발견! 런처가 게임 폴더 안에 있습니다."
    set "MSG_FOUND_REGISTRY=레지스트리에서 발견:"
    set "MSG_FOUND_DEFAULT=기본 경로에서 발견:"
    set "MSG_FOUND_LIBRARY=Steam 라이브러리에서 발견:"
    set "MSG_MANUAL_INPUT=Project Zomboid 폴더 전체 경로를 입력하세요."
    set "MSG_EXAMPLE=예시:"
    set "MSG_ENTER_PATH=경로 입력: "
    set "MSG_NO_PATH=오류: 경로가 입력되지 않았습니다."
    set "MSG_INVALID_PATH=오류: 잘못된 경로이거나 ProjectZomboid64.bat을 찾을 수 없습니다!"
    set "MSG_GAME_CONFIRMED=게임 설치 확인됨:"
    set "MSG_LOCATING_JAVA=내장 Java 런타임 검색 중..."
    set "MSG_JAVA_FOUND=Java 발견:"
    set "MSG_JAVA_NOT_FOUND=오류: Java 런타임을 찾을 수 없습니다!"
    set "MSG_BUILDING_CP=클래스패스 구성 중..."
    set "MSG_PREPARING_JVM=JVM 인자 준비 중..."
    set "MSG_LAUNCHING=Pulse 모드 로더로 Project Zomboid 실행 중..."
    set "MSG_JVM_AGENT=JVM 에이전트:"
    set "MSG_MEMORY=메모리:"
    set "MSG_GAME_PATH=게임 경로:"
    set "MSG_EXIT_ERROR=게임이 오류 코드로 종료됨:"
    set "MSG_CHECK_LOGS=로그를 확인하세요. 아무 키나 누르면 닫힙니다..."
    set "MSG_CONFIG_LOADED=설정 파일 로드됨:"
    set "MSG_CONFIG_CREATED=기본 설정 파일 생성됨:"
    set "MSG_LOG_START====== Pulse 런처 로그 시작 ====="
) else (
    :: English Messages (Default)
    set "MSG_TITLE=Pulse Mod Launcher"
    set "MSG_CHECKING_PULSE=Checking for Pulse.jar..."
    set "MSG_PULSE_FOUND=Found Pulse.jar:"
    set "MSG_PULSE_NOT_FOUND=ERROR: Pulse.jar not found!"
    set "MSG_PULSE_LOCATION=Please ensure Pulse.jar is in the same folder as this launcher:"
    set "MSG_SEARCHING_GAME=Searching for Project Zomboid installation..."
    set "MSG_PRIORITY_1=Priority 1: Checking current directory..."
    set "MSG_PRIORITY_2=Priority 2: Checking Windows Registry..."
    set "MSG_PRIORITY_3=Priority 3: Checking default Steam paths..."
    set "MSG_PRIORITY_4=Priority 4: Checking Steam library folders..."
    set "MSG_PRIORITY_5=Priority 5: Auto-detection failed. Manual input required."
    set "MSG_FOUND_LAUNCHER_DIR=Found! Launcher is inside game folder."
    set "MSG_FOUND_REGISTRY=Found in registry:"
    set "MSG_FOUND_DEFAULT=Found at default path:"
    set "MSG_FOUND_LIBRARY=Found in Steam library:"
    set "MSG_MANUAL_INPUT=Please enter the full path to your Project Zomboid folder."
    set "MSG_EXAMPLE=Example:"
    set "MSG_ENTER_PATH=Enter path: "
    set "MSG_NO_PATH=ERROR: No path entered."
    set "MSG_INVALID_PATH=ERROR: Invalid path or ProjectZomboid64.bat not found!"
    set "MSG_GAME_CONFIRMED=Game installation confirmed:"
    set "MSG_LOCATING_JAVA=Locating embedded Java runtime..."
    set "MSG_JAVA_FOUND=Found Java:"
    set "MSG_JAVA_NOT_FOUND=ERROR: Java runtime not found!"
    set "MSG_BUILDING_CP=Building classpath..."
    set "MSG_PREPARING_JVM=Preparing JVM arguments..."
    set "MSG_LAUNCHING=Launching Project Zomboid with Pulse Mod Loader..."
    set "MSG_JVM_AGENT=JVM Agent:"
    set "MSG_MEMORY=Memory:"
    set "MSG_GAME_PATH=Game Path:"
    set "MSG_EXIT_ERROR=Game exited with error code:"
    set "MSG_CHECK_LOGS=Check logs for details. Press any key to close..."
    set "MSG_CONFIG_LOADED=Config file loaded:"
    set "MSG_CONFIG_CREATED=Default config file created:"
    set "MSG_LOG_START===== Pulse Launcher Log Start ====="
)

:: Jump to main execution
goto :MAIN

:: ----------------------------------------------------------------------------
:: Logging Functions (Subroutine)
:: ----------------------------------------------------------------------------
:LOG
if "%ENABLE_LOGGING%"=="true" (
    echo [%DATE% %TIME%] %~1 >> "%LOG_FILE%"
)
echo %~1
goto :eof

:: ----------------------------------------------------------------------------
:: Main Execution Starts Here
:: ----------------------------------------------------------------------------
:MAIN

:: ----------------------------------------------------------------------------
:: Initialize Log File
:: ----------------------------------------------------------------------------
if "%ENABLE_LOGGING%"=="true" (
    echo. > "%LOG_FILE%"
    echo %MSG_LOG_START% >> "%LOG_FILE%"
    echo [%DATE% %TIME%] Pulse Smart Launcher Started >> "%LOG_FILE%"
    echo [%DATE% %TIME%] Language: %LANG% >> "%LOG_FILE%"
)

:: ----------------------------------------------------------------------------
:: Load Configuration File
:: ----------------------------------------------------------------------------
:LOAD_CONFIG
if exist "%CONFIG_FILE%" (
    call :LOG "[Pulse] %MSG_CONFIG_LOADED% %CONFIG_FILE%"
    for /f "usebackq tokens=1,* delims==" %%a in ("%CONFIG_FILE%") do (
        set "KEY=%%a"
        set "VALUE=%%b"
        :: Skip comments and empty lines
        if not "!KEY:~0,1!"=="#" if not "!KEY:~0,1!"==";" if defined KEY (
            :: Trim whitespace
            for /f "tokens=* delims= " %%c in ("!KEY!") do set "KEY=%%c"
            for /f "tokens=* delims= " %%c in ("!VALUE!") do set "VALUE=%%c"
            if /i "!KEY!"=="MinMemory" set "MIN_MEMORY=!VALUE!"
            if /i "!KEY!"=="MaxMemory" set "MAX_MEMORY=!VALUE!"
            if /i "!KEY!"=="GamePath" set "CUSTOM_GAME_PATH=!VALUE!"
            if /i "!KEY!"=="EnableLogging" set "ENABLE_LOGGING=!VALUE!"
            if /i "!KEY!"=="Language" set "LANGUAGE=!VALUE!" & goto :INIT_LANGUAGE
        )
    )
) else (
    :: Create default config file
    call :LOG "[Pulse] %MSG_CONFIG_CREATED% %CONFIG_FILE%"
    (
        echo # Pulse Launcher Configuration File
        echo # 펄스 런처 설정 파일
        echo.
        echo # Memory Settings ^(메모리 설정^)
        echo MinMemory=2048m
        echo MaxMemory=4096m
        echo.
        echo # Custom Game Path ^(사용자 지정 게임 경로^)
        echo # Leave empty for auto-detection ^(자동 감지를 위해 비워두세요^)
        echo GamePath=
        echo.
        echo # Enable Logging ^(로그 기록 활성화^)
        echo EnableLogging=true
        echo.
        echo # Language: auto, en, ko ^(언어: auto, en, ko^)
        echo Language=auto
    ) > "%CONFIG_FILE%"
)

:: ----------------------------------------------------------------------------
:: Display Header
:: ----------------------------------------------------------------------------
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║              PULSE MOD LAUNCHER for Project Zomboid           ║
echo  ╠═══════════════════════════════════════════════════════════════╣
echo  ║  Injects Pulse.jar as Java Agent - No file modifications!     ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.

:: ----------------------------------------------------------------------------
:: Step 1: Verify Pulse.jar exists in launcher directory
:: ----------------------------------------------------------------------------
call :LOG "[Pulse] %MSG_CHECKING_PULSE%"

if not exist "%PULSE_JAR%" (
    call :LOG "[Pulse] %MSG_PULSE_NOT_FOUND%"
    echo.
    echo  ╔═══════════════════════════════════════════════════════════════╗
    echo  ║  %MSG_PULSE_NOT_FOUND%
    echo  ╠═══════════════════════════════════════════════════════════════╣
    echo  ║  %MSG_PULSE_LOCATION%
    echo  ║  %LAUNCHER_DIR%
    echo  ╚═══════════════════════════════════════════════════════════════╝
    echo.
    pause
    exit /b 1
)

call :LOG "[Pulse] %MSG_PULSE_FOUND% %PULSE_JAR%"

:: ----------------------------------------------------------------------------
:: Step 2: Auto-detect Game Path (Priority Order)
:: ----------------------------------------------------------------------------
call :LOG "[Pulse] %MSG_SEARCHING_GAME%"

:: Check if custom path is set in config
if defined CUSTOM_GAME_PATH (
    if not "!CUSTOM_GAME_PATH!"=="" (
        set "GAME_PATH=!CUSTOM_GAME_PATH!"
        if not "!GAME_PATH:~-1!"=="\" set "GAME_PATH=!GAME_PATH!\"
        if exist "!GAME_PATH!ProjectZomboid64.bat" (
            call :LOG "[Pulse]   > Custom path from config: !GAME_PATH!"
            goto :GAME_FOUND
        )
    )
)

:: Priority 1: Check if launcher is inside game folder
call :LOG "[Pulse]   > %MSG_PRIORITY_1%"
if exist "%LAUNCHER_DIR%ProjectZomboid64.bat" (
    set "GAME_PATH=%LAUNCHER_DIR%"
    call :LOG "[Pulse]   > %MSG_FOUND_LAUNCHER_DIR%"
    goto :GAME_FOUND
)

if exist "%cd%\ProjectZomboid64.bat" (
    set "GAME_PATH=%cd%\"
    call :LOG "[Pulse]   > %MSG_FOUND_LAUNCHER_DIR%"
    goto :GAME_FOUND
)

:: Priority 2: Check Windows Registry (Steam App ID 108600)
call :LOG "[Pulse]   > %MSG_PRIORITY_2%"

:: Try 64-bit registry first
for /f "tokens=2*" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 108600" /v InstallLocation 2^>nul') do (
    set "GAME_PATH=%%b"
)

:: Try 32-bit registry (Wow6432Node) if not found
if not defined GAME_PATH (
    for /f "tokens=2*" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 108600" /v InstallLocation 2^>nul') do (
        set "GAME_PATH=%%b"
    )
)

if defined GAME_PATH (
    if not "!GAME_PATH:~-1!"=="\" set "GAME_PATH=!GAME_PATH!\"
    call :LOG "[Pulse]   > %MSG_FOUND_REGISTRY% !GAME_PATH!"
    goto :GAME_FOUND
)

:: Priority 3: Check default Steam installation paths
call :LOG "[Pulse]   > %MSG_PRIORITY_3%"

set "STEAM_PATHS[0]=C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\"
set "STEAM_PATHS[1]=C:\Program Files\Steam\steamapps\common\ProjectZomboid\"
set "STEAM_PATHS[2]=D:\Steam\steamapps\common\ProjectZomboid\"
set "STEAM_PATHS[3]=D:\SteamLibrary\steamapps\common\ProjectZomboid\"
set "STEAM_PATHS[4]=E:\Steam\steamapps\common\ProjectZomboid\"
set "STEAM_PATHS[5]=E:\SteamLibrary\steamapps\common\ProjectZomboid\"

for /L %%i in (0,1,5) do (
    if exist "!STEAM_PATHS[%%i]!ProjectZomboid64.bat" (
        set "GAME_PATH=!STEAM_PATHS[%%i]!"
        call :LOG "[Pulse]   > %MSG_FOUND_DEFAULT% !GAME_PATH!"
        goto :GAME_FOUND
    )
)

:: Priority 4: Parse Steam libraryfolders.vdf
call :LOG "[Pulse]   > %MSG_PRIORITY_4%"

set "STEAM_CONFIG=C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf"
if exist "%STEAM_CONFIG%" (
    for /f "tokens=2 delims=	" %%a in ('findstr /r /c:"\"path\"" "%STEAM_CONFIG%" 2^>nul') do (
        set "LIB_PATH=%%~a"
        set "LIB_PATH=!LIB_PATH:"=!"
        set "LIB_PATH=!LIB_PATH:\\=\!"
        if exist "!LIB_PATH!\steamapps\common\ProjectZomboid\ProjectZomboid64.bat" (
            set "GAME_PATH=!LIB_PATH!\steamapps\common\ProjectZomboid\"
            call :LOG "[Pulse]   > %MSG_FOUND_LIBRARY% !GAME_PATH!"
            goto :GAME_FOUND
        )
    )
)

:: Priority 5: Ask user for manual input
call :LOG "[Pulse]   > %MSG_PRIORITY_5%"
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║  %MSG_MANUAL_INPUT%
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.
echo  %MSG_EXAMPLE% C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid
echo.
set /p "GAME_PATH=%MSG_ENTER_PATH%"

if not defined GAME_PATH (
    call :LOG "[Pulse] %MSG_NO_PATH%"
    pause
    exit /b 1
)

if not "!GAME_PATH:~-1!"=="\" set "GAME_PATH=!GAME_PATH!\"

if not exist "!GAME_PATH!ProjectZomboid64.bat" (
    call :LOG "[Pulse] %MSG_INVALID_PATH%"
    echo.
    echo  ╔═══════════════════════════════════════════════════════════════╗
    echo  ║  %MSG_INVALID_PATH%
    echo  ╚═══════════════════════════════════════════════════════════════╝
    echo.
    pause
    exit /b 1
)

:GAME_FOUND
call :LOG "[Pulse] %MSG_GAME_CONFIRMED% %GAME_PATH%"

:: ----------------------------------------------------------------------------
:: Step 3: Verify Java executable exists
:: ----------------------------------------------------------------------------
call :LOG "[Pulse] %MSG_LOCATING_JAVA%"

set "JAVA_EXE=%GAME_PATH%jre64\bin\java.exe"

if not exist "%JAVA_EXE%" (
    set "JAVA_EXE=%GAME_PATH%jre\bin\java.exe"
)

if not exist "%JAVA_EXE%" (
    call :LOG "[Pulse] %MSG_JAVA_NOT_FOUND%"
    echo.
    echo  ╔═══════════════════════════════════════════════════════════════╗
    echo  ║  %MSG_JAVA_NOT_FOUND%
    echo  ║  Expected: %GAME_PATH%jre64\bin\java.exe
    echo  ╚═══════════════════════════════════════════════════════════════╝
    echo.
    pause
    exit /b 1
)

call :LOG "[Pulse] %MSG_JAVA_FOUND% %JAVA_EXE%"

:: ----------------------------------------------------------------------------
:: Step 4: Build classpath
:: ----------------------------------------------------------------------------
call :LOG "[Pulse] %MSG_BUILDING_CP%"

set "FULL_CLASSPATH="
for %%L in (%CLASSPATH_LIBS%) do (
    if "!FULL_CLASSPATH!"=="" (
        set "FULL_CLASSPATH=%GAME_PATH%%%L"
    ) else (
        set "FULL_CLASSPATH=!FULL_CLASSPATH!;%GAME_PATH%%%L"
    )
)

:: ----------------------------------------------------------------------------
:: Step 5: Prepare JVM arguments
:: ----------------------------------------------------------------------------
call :LOG "[Pulse] %MSG_PREPARING_JVM%"

set "LIB_PATH=%GAME_PATH%;%GAME_PATH%natives;%GAME_PATH%win64;."
set "MAIN_CLASS=zombie.gameStates.MainScreenState"

:: ----------------------------------------------------------------------------
:: Step 6: Launch the game with Pulse injection
:: ----------------------------------------------------------------------------
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║  %MSG_LAUNCHING%
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.
call :LOG "[Pulse] %MSG_JVM_AGENT% %PULSE_JAR%"
call :LOG "[Pulse] %MSG_MEMORY% %MIN_MEMORY% - %MAX_MEMORY%"
call :LOG "[Pulse] %MSG_GAME_PATH% %GAME_PATH%"
echo.

cd /d "%GAME_PATH%"

:: Log the full command
if "%ENABLE_LOGGING%"=="true" (
    echo [%DATE% %TIME%] Executing Java command... >> "%LOG_FILE%"
)

"%JAVA_EXE%" ^
    -javaagent:"%PULSE_JAR%" ^
    -Djava.awt.headless=true ^
    -Dzomboid.steam=1 ^
    -Dzomboid.znetlog=1 ^
    "-Djava.library.path=%LIB_PATH%" ^
    -Xms%MIN_MEMORY% ^
    -Xmx%MAX_MEMORY% ^
    -XX:+UseG1GC ^
    -XX:-OmitStackTraceInFastThrow ^
    -Djdk.lang.Process.allowAmbiguousCommands=true ^
    -cp "%FULL_CLASSPATH%" ^
    %MAIN_CLASS%

set "EXIT_CODE=%ERRORLEVEL%"

:: ----------------------------------------------------------------------------
:: Step 7: Handle exit
:: ----------------------------------------------------------------------------
if "%ENABLE_LOGGING%"=="true" (
    echo [%DATE% %TIME%] Game exited with code: %EXIT_CODE% >> "%LOG_FILE%"
)

if %EXIT_CODE% NEQ 0 (
    call :LOG "[Pulse] %MSG_EXIT_ERROR% %EXIT_CODE%"
    echo.
    echo  ╔═══════════════════════════════════════════════════════════════╗
    echo  ║  %MSG_EXIT_ERROR% %EXIT_CODE%
    echo  ╚═══════════════════════════════════════════════════════════════╝
    echo.
    echo [Pulse] %MSG_CHECK_LOGS%
    pause >nul
)

endlocal
exit /b %EXIT_CODE%
