# Changelog

All notable changes to Echo Profiler will be documented in this file.

## [1.0.0] - 2025-12-08

### 🎉 v1.0.0 Stable Release

Echo reaches production-ready status with comprehensive bug fixes and performance optimizations.

### Added
- **RenderHelper** - Reflection caching utility for HUD rendering (eliminates per-frame overhead)
- **HTTP Monitor Server** - Real-time metrics via `/echo monitor start`
- **Meta Profiling** - Measure profiler overhead via `/echo overhead`
- **Spike Stack Capture** - Optional stack trace on spikes via `/echo stack on`
- **Jank Metrics** - 16ms/33ms threshold tracking in TickHistogram
- **Multi-format Reports** - JSON, CSV, HTML export support
- **Enhanced Help** - Organized command documentation with Phase 4 commands

### Fixed
- **[Critical]** RollingStats max recalculation off-by-one bug
- **[Critical]** Per-frame reflection lookups in EchoHUD/HotspotPanel
- **[Medium]** SpikeLog.toMap() AtomicLong serialization
- **[Low]** Version constant inconsistency across files

### Changed
- EchoHUD and HotspotPanel now delegate to RenderHelper
- Unified version references to EchoConstants.VERSION
- Enhanced `/echo help` with categorized sections

---

## [0.2.1] - 2025-12-07

### Fixed
- Thread safety improvements in LuaFunctionStats
- RollingStats synchronization
- Main thread detection in EchoProfiler

---

## [0.2.0] - 2025-12-07

### Added
- Lua profiling with per-function statistics
- Memory profiling (heap, GC tracking)
- CSV/HTML report generation
- Configuration persistence (EchoConfig)
- StringUtils utility class

### Fixed
- LuaFunctionStats.maxMicros thread safety (AtomicLong CAS)
- RollingStats.addSample() synchronization

---

## [0.1.1] - 2025-12-06

### Added
- MemoryProfiler for heap/GC monitoring
- `/echo config threshold <ms>` command
- `/echo memory` command

### Fixed
- enable() auto-reset to prevent data mixing
- ProfilingFrame.idCounter thread safety
- TickHistogram percentile accuracy

---

## [0.1.0] - 2025-12-05

### Added
- Initial release
- Tick time measurement
- Subsystem profiling (Render, Simulation, Physics, AI, Lua)
- Histogram with P50/P95/P99
- Spike detection
- JSON report generation
