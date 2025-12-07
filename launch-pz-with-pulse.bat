@echo off
REM Pulse Mod Loader - Project Zomboid Launcher
REM This script launches Project Zomboid with Pulse as a Java agent

set PZ_PATH=C:\SteamLibrary\steamapps\common\ProjectZomboid
set PULSE_JAR=%~dp0build\libs\Pulse.jar
set MODS_DIR=%~dp0mods

REM Check if Pulse.jar exists
if not exist "%PULSE_JAR%" (
    echo ERROR: Pulse.jar not found!
    echo Please run 'gradlew build' first.
    pause
    exit /b 1
)

REM Create mods directory if not exists
if not exist "%MODS_DIR%" mkdir "%MODS_DIR%"

REM Copy first-party mods
echo Copying first-party mods...
if exist "%~dp0first-party-mods\pulse-engine-optim\build\libs\*.jar" copy /Y "%~dp0first-party-mods\pulse-engine-optim\build\libs\*.jar" "%MODS_DIR%" >nul
if exist "%~dp0first-party-mods\pulse-lua-optim\build\libs\*.jar" copy /Y "%~dp0first-party-mods\pulse-lua-optim\build\libs\*.jar" "%MODS_DIR%" >nul
if exist "%~dp0first-party-mods\pulse-profiler\build\libs\*.jar" copy /Y "%~dp0first-party-mods\pulse-profiler\build\libs\*.jar" "%MODS_DIR%" >nul

echo.
echo ========================================
echo  PULSE MOD LOADER
echo ========================================
echo  PZ Path: %PZ_PATH%
echo  Pulse:   %PULSE_JAR%
echo  Mods:    %MODS_DIR%
echo ========================================
echo.

REM Launch PZ with Pulse agent
echo Launching Project Zomboid with Pulse...
cd /d "%PZ_PATH%"

REM Use the project zomboid's bundled java
"%PZ_PATH%\jre64\bin\java.exe" ^
    -javaagent:"%PULSE_JAR%" ^
    -Dpulse.mods.dir="%MODS_DIR%" ^
    -Dpulse.debug=true ^
    -Xms2g -Xmx4g ^
    -Djava.library.path="%PZ_PATH%;%PZ_PATH%\natives" ^
    -cp "%PZ_PATH%\*;%PZ_PATH%\zombie.jar" ^
    zombie.gameStates.MainScreenState

pause
