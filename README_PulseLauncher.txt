# ═══════════════════════════════════════════════════════════════════════
#  PULSE LAUNCHER - Quick Start Guide
#  펄스 런처 - 빠른 시작 가이드
# ═══════════════════════════════════════════════════════════════════════

## 📁 Files / 파일 구성

  Pulse.jar              - Pulse mod loader core (필수)
  pulse-version.txt      - Version info (자동 생성)
  
  PulseLauncher.bat      - Windows launcher
  PulseLauncher-linux.sh - Linux launcher  
  PulseLauncher-macos.sh - macOS launcher
  
  mods/                  - Put your Pulse mods here (모드 폴더)
  crash-logs/            - Crash logs saved here (크래시 로그)

───────────────────────────────────────────────────────────────────────

## 🚀 Quick Start / 빠른 시작

### Windows
  1. Double-click PulseLauncher.bat
  2. The launcher will auto-detect your game and start

### Linux / macOS
  1. Open terminal in this folder
  2. Make executable: chmod +x PulseLauncher-linux.sh
  3. Run: ./PulseLauncher-linux.sh
  
  (macOS: use PulseLauncher-macos.sh)

───────────────────────────────────────────────────────────────────────

## ⚙️ Configuration / 설정

Edit PulseLauncher.ini (Windows) or PulseLauncher.conf (Linux/Mac):

  MinMemory=2048m        # Minimum memory
  MaxMemory=4096m        # Maximum memory  
  GamePath=              # Leave empty for auto-detect
  EnableLogging=true     # Enable/disable logging
  Language=auto          # auto, en, ko

───────────────────────────────────────────────────────────────────────

## 📋 CLI Options / 명령줄 옵션

  --version, -v      Show version / 버전 표시
  --help, -h         Show help / 도움말
  --debug, -d        Debug mode / 디버그 모드
  --check-update, -u Check for updates (Windows only)

Example:
  PulseLauncher.bat --debug
  ./PulseLauncher-linux.sh --version

───────────────────────────────────────────────────────────────────────

## 🔧 Troubleshooting / 문제 해결

1. "Pulse.jar not found"
   → Place Pulse.jar in the same folder as the launcher
   
2. "Game path not found"  
   → Edit config file and set GamePath manually

3. Game won't start
   → Run with --debug flag to see detailed output
   → Check crash-logs/ folder for crash reports

───────────────────────────────────────────────────────────────────────

## 📦 Installing Mods / 모드 설치

1. Download .jar mod files
2. Place them in the mods/ folder
3. Launch the game - mods load automatically!

───────────────────────────────────────────────────────────────────────

For more info: https://github.com/randomstrangerpassenger/Pulse
