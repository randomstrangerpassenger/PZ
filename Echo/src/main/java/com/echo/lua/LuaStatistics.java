package com.echo.lua;

import com.echo.util.StringUtils;
import com.pulse.api.util.TopNCollector;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.LongAdder;

/**
 * Lua 호출 통계 수집 및 조회.
 * 
 * <p>
 * LuaCallTracker에서 분리된 통계 전용 클래스입니다.
 * 통계 저장, Top N 캐싱, 리셋, 출력 등을 담당합니다.
 * </p>
 * 
 * <h3>Thread Safety:</h3>
 * <ul>
 * <li>ConcurrentHashMap으로 동시성 지원</li>
 * <li>읽기 스레드 (Render/Debug UI)에서 안전하게 조회 가능</li>
 * </ul>
 * 
 * @since Echo 0.9 - Extracted from LuaCallTracker
 */
public class LuaStatistics {

    // ═══════════════════════════════════════════════════════════════
    // Statistics Storage
    // ═══════════════════════════════════════════════════════════════

    private final Map<String, LuaFunctionStats> functionStats = new ConcurrentHashMap<>();
    private final Map<String, LuaEventStats> eventStats = new ConcurrentHashMap<>();
    private final Map<String, LuaUIElementStats> uiElementStats = new ConcurrentHashMap<>();
    private final Map<String, LongAdder> contextStats = new ConcurrentHashMap<>();
    private final Map<String, LongAdder> fileStats = new ConcurrentHashMap<>();

    // ═══════════════════════════════════════════════════════════════
    // Counters
    // ═══════════════════════════════════════════════════════════════

    private final LongAdder totalCalls = new LongAdder();
    private final LongAdder trackedCalls = new LongAdder();
    private final LongAdder untrackedCalls = new LongAdder();
    private final LongAdder totalTimeMicros = new LongAdder();

    // Quality metrics
    private final LongAdder mismatchCount = new LongAdder();
    private final LongAdder droppedFrames = new LongAdder();
    private final LongAdder stackResets = new LongAdder();

    // Detailed window stats
    private final LongAdder detailedWindowsOpened = new LongAdder();
    private final LongAdder detailedTotalActiveMs = new LongAdder();

    // ═══════════════════════════════════════════════════════════════
    // Top N Cache
    // ═══════════════════════════════════════════════════════════════

    private volatile List<LuaFunctionStats> topByTimeCached = new ArrayList<>();
    private volatile List<LuaFunctionStats> topByCallsCached = new ArrayList<>();
    private volatile long lastCacheUpdate = 0;
    private static final long CACHE_TTL_MS = 1000;

    // ═══════════════════════════════════════════════════════════════
    // Recording API
    // ═══════════════════════════════════════════════════════════════

    /**
     * 함수 호출 통계 기록.
     */
    public void recordFunction(String funcName, long elapsedMicros, long selfMicros, String contextTag) {
        LuaFunctionStats stats = functionStats.computeIfAbsent(funcName, LuaFunctionStats::new);
        stats.record(elapsedMicros, selfMicros);
        if (contextTag != null) {
            stats.setContext(contextTag);
        }

        totalTimeMicros.add(elapsedMicros);
        contextStats.computeIfAbsent(contextTag != null ? contextTag : "Unknown",
                k -> new LongAdder()).add(elapsedMicros);
    }

    /**
     * 함수 호출 통계 기록 (Legacy API).
     */
    public void recordFunction(String funcName, long durationMicros) {
        functionStats.computeIfAbsent(funcName, LuaFunctionStats::new).record(durationMicros);
        totalCalls.increment();
        trackedCalls.increment();
        totalTimeMicros.add(durationMicros);
    }

    /**
     * 이벤트 호출 통계 기록.
     */
    public void recordEvent(String eventName, long durationMicros, int handlerCount) {
        eventStats.computeIfAbsent(eventName, LuaEventStats::new)
                .record(durationMicros, handlerCount);
    }

    /**
     * UI 요소 호출 통계 기록.
     */
    public void recordUIElement(LuaUICategory category, String elementName, long durationMicros) {
        String key = category.name() + ":" + elementName;
        uiElementStats.computeIfAbsent(key, k -> new LuaUIElementStats(category, elementName))
                .record(durationMicros);
    }

    /**
     * 파일별 통계 기록.
     */
    public void recordFile(String sourceFile, long durationMicros) {
        if (sourceFile != null && !sourceFile.isEmpty()) {
            fileStats.computeIfAbsent(sourceFile, k -> new LongAdder()).add(durationMicros);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Counter Updates
    // ═══════════════════════════════════════════════════════════════

    public void incrementTotalCalls() {
        totalCalls.increment();
    }

    public void incrementTrackedCalls() {
        trackedCalls.increment();
    }

    public void incrementUntrackedCalls() {
        untrackedCalls.increment();
    }

    public void incrementMismatchCount() {
        mismatchCount.increment();
    }

    public void addDroppedFrames(int count) {
        droppedFrames.add(count);
    }

    public void incrementStackResets() {
        stackResets.increment();
    }

    public void incrementDetailedWindowsOpened() {
        detailedWindowsOpened.increment();
    }

    public void addDetailedActiveMs(long ms) {
        detailedTotalActiveMs.add(ms);
    }

    // ═══════════════════════════════════════════════════════════════
    // Query API
    // ═══════════════════════════════════════════════════════════════

    public long getTotalCalls() {
        return totalCalls.sum();
    }

    public long getTrackedCalls() {
        return trackedCalls.sum();
    }

    public long getUntrackedCalls() {
        return untrackedCalls.sum();
    }

    public long getSampledCalls() {
        return trackedCalls.sum();
    } // Legacy

    public long getDroppedCalls() {
        return untrackedCalls.sum();
    } // Legacy

    public long getMismatchCount() {
        return mismatchCount.sum();
    }

    public long getDroppedFrames() {
        return droppedFrames.sum();
    }

    public long getStackResets() {
        return stackResets.sum();
    }

    public long getOrphanedEnds() {
        return 0;
    } // v2.1: 더 이상 에러 아님

    public double getTotalTimeMs() {
        return totalTimeMicros.sum() / 1000.0;
    }

    public long getDetailedWindowsOpened() {
        return detailedWindowsOpened.sum();
    }

    public long getDetailedTotalActiveMs() {
        return detailedTotalActiveMs.sum();
    }

    public LuaFunctionStats getFunctionStats(String name) {
        return functionStats.get(name);
    }

    public Collection<LuaFunctionStats> getAllFunctionStats() {
        return Collections.unmodifiableCollection(functionStats.values());
    }

    public LuaEventStats getEventStats(String name) {
        return eventStats.get(name);
    }

    public Collection<LuaEventStats> getAllEventStats() {
        return Collections.unmodifiableCollection(eventStats.values());
    }

    public LuaUIElementStats getUIElementStats(LuaUICategory category, String elementName) {
        return uiElementStats.get(category.name() + ":" + elementName);
    }

    public Collection<LuaUIElementStats> getAllUIElementStats() {
        return Collections.unmodifiableCollection(uiElementStats.values());
    }

    // ═══════════════════════════════════════════════════════════════
    // Top N with Caching
    // ═══════════════════════════════════════════════════════════════

    public List<LuaFunctionStats> getTopFunctionsByTime(int n) {
        updateCacheIfNeeded();
        return topByTimeCached.size() <= n ? topByTimeCached : topByTimeCached.subList(0, n);
    }

    public List<LuaFunctionStats> getTopFunctionsByCalls(int n) {
        updateCacheIfNeeded();
        return topByCallsCached.size() <= n ? topByCallsCached : topByCallsCached.subList(0, n);
    }

    private void updateCacheIfNeeded() {
        long now = System.currentTimeMillis();
        if (now - lastCacheUpdate < CACHE_TTL_MS)
            return;

        Collection<LuaFunctionStats> all = functionStats.values();

        // TopNCollector 활용 (Phase 8 개선)
        topByTimeCached = TopNCollector.topNByLong(all, LuaFunctionStats::getTotalMicros, all.size());
        topByCallsCached = TopNCollector.topNByLong(all, LuaFunctionStats::getCallCount, all.size());

        lastCacheUpdate = now;
    }

    // ═══════════════════════════════════════════════════════════════
    // Reset
    // ═══════════════════════════════════════════════════════════════

    public void reset() {
        functionStats.clear();
        eventStats.clear();
        uiElementStats.clear();
        contextStats.clear();
        fileStats.clear();

        totalCalls.reset();
        trackedCalls.reset();
        untrackedCalls.reset();
        totalTimeMicros.reset();
        mismatchCount.reset();
        droppedFrames.reset();
        stackResets.reset();
        detailedWindowsOpened.reset();
        detailedTotalActiveMs.reset();

        topByTimeCached.clear();
        topByCallsCached.clear();
    }

    // ═══════════════════════════════════════════════════════════════
    // Output
    // ═══════════════════════════════════════════════════════════════

    public void printStats(int topN, int sampleRate) {
        System.out.println("\n🔷 LUA PROFILING STATS (v2.1)");
        System.out.println("───────────────────────────────────────────────────────");
        System.out.printf("  Total Calls: %,d | Tracked: %,d | Untracked: %,d%n",
                getTotalCalls(), getTrackedCalls(), getUntrackedCalls());
        System.out.printf("  Dropped Frames: %,d | Stack Resets: %,d%n",
                getDroppedFrames(), getStackResets());
        System.out.printf("  Windows Opened: %,d | Active Time: %,d ms%n",
                getDetailedWindowsOpened(), getDetailedTotalActiveMs());
        System.out.printf("  Total Time: %.2f ms%n", getTotalTimeMs());
        System.out.println();

        System.out.println("  Top Functions by Time:");
        int rank = 1;
        for (LuaFunctionStats stats : getTopFunctionsByTime(topN)) {
            System.out.printf("    #%d %-30s | calls: %,6d | total: %6.2f ms | self: %6.2f ms%n",
                    rank++,
                    StringUtils.truncate(stats.getName(), 30),
                    stats.getCallCount(),
                    stats.getTotalMs(),
                    stats.getSelfTimeMs());
        }

        if (!eventStats.isEmpty()) {
            System.out.println("\n  Events:");
            for (LuaEventStats stats : eventStats.values()) {
                System.out.printf("    %-25s | fires: %,6d | handlers: %,d | total: %.2f ms%n",
                        StringUtils.truncate(stats.getName(), 25),
                        stats.getFireCount(),
                        stats.getTotalHandlers(),
                        stats.getTotalMs());
            }
        }
        System.out.println();
    }

    /**
     * JSON 출력용 Map.
     */
    public Map<String, Object> toMap(int topN, boolean luaProfilingEnabled,
            boolean detailedActive, int sampleRate) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("enabled", luaProfilingEnabled);
        map.put("detailed_active", detailedActive);

        // Counters
        map.put("total_calls", getTotalCalls());
        map.put("tracked_calls", getTrackedCalls());
        map.put("untracked_calls", getUntrackedCalls());
        map.put("total_time_ms", Math.round(getTotalTimeMs() * 100) / 100.0);

        // Detailed Window stats
        Map<String, Object> windowStats = new LinkedHashMap<>();
        windowStats.put("windows_opened", getDetailedWindowsOpened());
        windowStats.put("total_active_ms", getDetailedTotalActiveMs());
        map.put("detailed_window_stats", windowStats);

        // Quality metrics
        Map<String, Object> quality = new LinkedHashMap<>();
        quality.put("dropped_frames", getDroppedFrames());
        quality.put("stack_resets", getStackResets());
        quality.put("sample_rate", "1/" + sampleRate);

        long total = getTotalCalls();
        long tracked = getTrackedCalls();
        double trackingRate = (total > 0) ? (tracked * 100.0 / total) : 0;
        quality.put("tracking_rate_percent", Math.round(trackingRate * 10) / 10.0);
        map.put("quality_metrics", quality);

        // Top Functions
        List<Map<String, Object>> topFunctions = new ArrayList<>();
        int rank = 1;
        for (LuaFunctionStats stats : getTopFunctionsByTime(topN)) {
            topFunctions.add(stats.toMap(rank++));
        }
        map.put("top_functions_by_time", topFunctions);

        // Events
        List<Map<String, Object>> events = new ArrayList<>();
        for (LuaEventStats stats : eventStats.values()) {
            events.add(stats.toMap());
        }
        map.put("events", events);

        // UI Elements
        List<Map<String, Object>> uiList = new ArrayList<>();
        List<LuaUIElementStats> sortedUI = new ArrayList<>(uiElementStats.values());
        sortedUI.sort((a, b) -> Long.compare(b.getTotalMicros(), a.getTotalMicros()));
        int count = 0;
        for (LuaUIElementStats stats : sortedUI) {
            if (count++ >= topN)
                break;
            uiList.add(stats.toMap());
        }
        map.put("ui_elements", uiList);

        // Context Stats
        Map<String, Double> contextMap = new LinkedHashMap<>();
        contextStats.entrySet().stream()
                .sorted((a, b) -> Long.compare(b.getValue().sum(), a.getValue().sum()))
                .forEach(e -> contextMap.put(e.getKey(), e.getValue().sum() / 1000.0));
        map.put("context_stats", contextMap);

        // File Stats
        List<Map<String, Object>> fileList = new ArrayList<>();
        fileStats.entrySet().stream()
                .sorted((a, b) -> Long.compare(b.getValue().sum(), a.getValue().sum()))
                .limit(topN)
                .forEach(e -> {
                    Map<String, Object> f = new LinkedHashMap<>();
                    f.put("file", e.getKey());
                    f.put("total_ms", Math.round((e.getValue().sum() / 1000.0) * 100) / 100.0);
                    fileList.add(f);
                });
        map.put("heavy_files", fileList);

        return map;
    }
}
