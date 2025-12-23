<p align="center">
  <img src="https://img.shields.io/badge/🔥_PULSE-1.0.0-ff6f00?style=for-the-badge&labelColor=1a1a2e" alt="Pulse Logo"/>
</p>

<h1 align="center">🔥 Pulse Ecosystem</h1>

<p align="center">
  <strong>Next-generation Mixin-based Mod Loader for Project Zomboid</strong>
</p>

<p align="center">
  <a href="https://openjdk.org/"><img src="https://img.shields.io/badge/Java-17+-ED8B00?style=flat-square&logo=openjdk&logoColor=white" alt="Java 17+"/></a>
  <a href="https://github.com/SpongePowered/Mixin"><img src="https://img.shields.io/badge/SpongePowered-Mixin%200.8.5-00adb5?style=flat-square&logo=java&logoColor=white" alt="Mixin 0.8.5"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="MIT License"/></a>
  <img src="https://img.shields.io/badge/Status-Production%20Ready-success?style=flat-square" alt="Production Ready"/>
</p>

---

## 📦 Modules

The Pulse ecosystem consists of 4 integrated modules:

| Module | Description | Status |
|--------|-------------|--------|
| [**Pulse**](./Pulse/README.md) | Core mod loader with Mixin support | v1.0.0 ✅ |
| [**Echo**](./Echo/README.md) | Performance profiler | v0.8.0 ✅ |
| [**Fuse**](./Fuse/README.md) | Performance optimizer | v0.1.0 🚧 |
| [**Nerve**](./Nerve/README.md) | Network & rendering optimizer | v0.1.0 🚧 |

### Module Dependencies

```
Pulse (Core)
├── Echo (Profiler) - Uses Pulse EventBus & SPI
├── Fuse (Optimizer) - Uses Echo profiling data
└── Nerve (Network) - Uses Echo bottleneck analysis
```

---

## 🎯 Introduction

**Pulse** is a revolutionary mod loader that brings the power of **SpongePowered Mixin** technology to Project Zomboid. Built for both players and developers, it enables precise runtime bytecode manipulation while providing a rich API ecosystem that significantly simplifies mod development.

> _"Where traditional Lua hooks end, Pulse begins."_

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔧 **Powerful Runtime Manipulation** | Leverages SpongePowered Mixin 0.8.5 for safe, precise bytecode modification |
| 🌉 **Innovative Two-way Bridge** | Seamless Java ↔ Lua bidirectional communication via `LuaBridge` |
| 📦 **Smart Dependency Management** | Topological Sort-based automatic load ordering with conflict prevention |
| ⚡ **Developer Productivity (DX)** | `GameAccess` Facade API (55+ methods), `EventBus`, `CrashReporter` and more |

---

## 🚀 Quick Start

### Installation

1. Download the latest release
2. Run `PulseLauncher.bat` (Windows) or `PulseLauncher.sh` (Linux/macOS)

### For Mod Developers

See the individual module documentation:
- [Pulse Developer Guide](./Pulse/README.md#-for-developers)
- [Echo Profiler Guide](./Echo/README.md)
- [Mod Template](./docs/MOD_TEMPLATE.md)
- [API Reference](./docs/API_REFERENCE.md)

---

## 🏗️ Building

### Prerequisites

- Java 17+
- Gradle 8.0+

### Build All Modules

```bash
./gradlew build
```

### Build Individual Module

```bash
./gradlew :Pulse:build
./gradlew :Echo:build
./gradlew :Fuse:build
./gradlew :Nerve:build
```

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built with ❤️ for the Project Zomboid modding community</sub>
</div>

---

## 🇰🇷 한국어 (Korean)

자세한 한국어 문서는 각 모듈의 README를 참조하세요:
- [Pulse 한국어 가이드](./Pulse/README.md#-한국어-korean)
- [Echo 한국어 가이드](./Echo/README.md)
