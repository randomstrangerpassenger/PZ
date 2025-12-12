package com.echo.lua;

import com.echo.measure.EchoProfiler;
import com.echo.util.StringUtils;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.LongAdder;

/**
 * Lua 호출 추적기
 * 
 * Lua 함수/이벤트 호출을 세부적으로 추적하고 통계를 제공합니다.
 * On-Demand 방식으로 활성화됩니다.
 * 
 * v1.1 Enhancements: UI Element Tracking, debug.sethook support foundation
 */
public class LuaCallTracker {

    private static LuaCallTracker INSTANCE;

    // Auto-Enable 설정 (Echo 0.9.0)
    private static final int AUTO_ENABLE_THRESHOLD = 5;
    private final java.util.concurrent.atomic.AtomicInteger consecutiveCallCount = new java.util.concurrent.atomic.AtomicInteger(
            0);

    // 함수별 통계
    private final Map<String, LuaFunctionStats> functionStats = new ConcurrentHashMap<>();

    // 이벤트별 통계
    private final Map<String, LuaEventStats> eventStats = new ConcurrentHashMap<>();

    // UI 요소별 통계 (Phase 2.1)
    private final Map<String, LuaUIElementStats> uiElementStats = new ConcurrentHashMap<>();

    // Context별 통계 (Phase 3)
    private final Map<String, LongAdder> contextStats = new ConcurrentHashMap<>();

    // 파일별 통계 (Phase 3)
    private final Map<String, LongAdder> fileStats = new ConcurrentHashMap<>();

    // 전체 통계
    private final LongAdder totalCalls = new LongAdder();
    private final LongAdder totalTimeMicros = new LongAdder();

    // Top N 캐시
    private volatile List<LuaFunctionStats> topByTimeCached = new ArrayList<>();
    private volatile List<LuaFunctionStats> topByCallsCached = new ArrayList<>();
    private volatile long lastCacheUpdate = 0;
    private static final long CACHE_TTL_MS = 1000;

    public enum LuaUICategory {
        TOOLTIP, CONTEXT_MENU, INVENTORY_GRID, MODAL_DIALOG, HUD_ELEMENT, OTHER
    }

    // Dependencies
    private final com.echo.config.EchoConfig config;
    private final EchoProfiler profiler;

    /**
     * @deprecated Use Constructor Injection via PulseServiceLocator
     */
    @Deprecated
    private LuaCallTracker() {
        this(com.echo.config.EchoConfig.getInstance(), EchoProfiler.getInstance());
    }

    public LuaCallTracker(com.echo.config.EchoConfig config, EchoProfiler profiler) {
        this.config = config;
        this.profiler = profiler;
    }

    public static LuaCallTracker getInstance() {
        // 1. Try ServiceLocator (Hybrid DI)
        try {
            com.pulse.di.PulseServiceLocator locator = com.pulse.di.PulseServiceLocator.getInstance();
            LuaCallTracker service = locator.getService(LuaCallTracker.class);
            if (service != null) {
                return service;
            }
        } catch (NoClassDefFoundError | Exception ignored) {
            // Pulse might not be fully loaded
        }

        // 2. Fallback
        if (INSTANCE == null) {
            INSTANCE = new LuaCallTracker(com.echo.config.EchoConfig.getInstance(), EchoProfiler.getInstance());
        }
        return INSTANCE;
    }

    // ============================================================
    // 기록 API
    // ============================================================

    /**
     * Lua 함수 호출 기록
     */
    public void recordFunctionCall(String functionName, long durationMicros) {
        if (!profiler.isLuaProfilingEnabled())
            return;

        functionStats.computeIfAbsent(functionName, LuaFunctionStats::new)
                .record(durationMicros);

        totalCalls.increment();
        totalTimeMicros.add(durationMicros);

        // Phase 3: Context Tracking
        String context = EchoLuaContext.getContext();
        contextStats.computeIfAbsent(context, k -> new LongAdder()).add(durationMicros);
    }

    /**
     * Lua 함수 호출 기록 (Source File 포함) - Phase 3
     */
    public void recordFunctionCall(String functionName, String sourceFile, long durationMicros) {
        recordFunctionCall(functionName, durationMicros);

        if (sourceFile != null && !sourceFile.isEmpty()) {
            fileStats.computeIfAbsent(sourceFile, k -> new LongAdder()).add(durationMicros);
        }
    }

    /**
     * Lua 이벤트 호출 기록
     */
    public void recordEventCall(String eventName, long durationMicros, int handlerCount) {
        if (!profiler.isLuaProfilingEnabled())
            return;

        eventStats.computeIfAbsent(eventName, LuaEventStats::new)
                .record(durationMicros, handlerCount);
    }

    /**
     * UI 요소 비용 기록 (Phase 2.1)
     */
    public void recordUIElementCall(LuaUICategory category, String elementName, long durationMicros) {
        if (!profiler.isLuaProfilingEnabled())
            return;

        String key = category.name() + ":" + elementName;
        uiElementStats.computeIfAbsent(key, k -> new LuaUIElementStats(category, elementName))
                .record(durationMicros);
    }

    /**
     * 프로파일링 래퍼 - 함수
     */
    public void profileFunction(String functionName, Runnable function) {
        // Phase 2.2: Auto-Enable Logic
        checkAutoEnable();

        if (!profiler.isLuaProfilingEnabled()) {
            function.run();
            return;
        }

        long start = System.nanoTime();
        try {
            function.run();
        } finally {
            long elapsed = (System.nanoTime() - start) / 1000;
            recordFunctionCall(functionName, elapsed);
        }
    }

    /**
     * 프로파일링 래퍼 - 이벤트
     */
    public void profileEvent(String eventName, int handlerCount, Runnable event) {
        // Phase 2.2: Auto-Enable Logic
        checkAutoEnable();

        if (!profiler.isLuaProfilingEnabled()) {
            event.run();
            return;
        }

        long start = System.nanoTime();
        try {
            event.run();
        } finally {
            long elapsed = (System.nanoTime() - start) / 1000;
            recordEventCall(eventName, elapsed, handlerCount);
        }
    }

    // ============================================================
    // 조회 API
    // ============================================================

    public long getTotalCalls() {
        return totalCalls.sum();
    }

    public double getTotalTimeMs() {
        return totalTimeMicros.sum() / 1000.0;
    }

    public LuaFunctionStats getFunctionStats(String functionName) {
        return functionStats.get(functionName);
    }

    public Collection<LuaFunctionStats> getAllFunctionStats() {
        return Collections.unmodifiableCollection(functionStats.values());
    }

    public LuaEventStats getEventStats(String eventName) {
        return eventStats.get(eventName);
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

        List<LuaFunctionStats> all = new ArrayList<>(functionStats.values());

        all.sort((a, b) -> Long.compare(b.getTotalMicros(), a.getTotalMicros()));
        topByTimeCached = new ArrayList<>(all);

        all.sort((a, b) -> Long.compare(b.getCallCount(), a.getCallCount()));
        topByCallsCached = new ArrayList<>(all);

        lastCacheUpdate = now;
    }

    private void checkAutoEnable() {
        // 이미 켜져있거나, 사용자가 명시적으로 껐으면 체크 안함
        if (config.isLuaProfilingEnabled()) {
            // 이미 켜져있으면 카운터 0으로 유지 (불필요한 증가 방지)
            consecutiveCallCount.set(0);
            return;
        }
        if (config.isUserExplicitLuaOff()) {
            return;
        }

        // 연속 호출 감지
        if (consecutiveCallCount.incrementAndGet() >= AUTO_ENABLE_THRESHOLD) {
            System.out.println("[Echo] ⚠️ Detected sustained Lua activity (" + AUTO_ENABLE_THRESHOLD
                    + " calls). Auto-enabling Lua Profiling.");
            config.setLuaProfilingEnabled(true);
            config.save();
        }
    }

    /**
     * 초기화
     */
    public void reset() {
        functionStats.clear();
        eventStats.clear();
        uiElementStats.clear();
        totalCalls.reset();
        totalTimeMicros.reset();
        topByTimeCached.clear();
        topByCallsCached.clear();
        contextStats.clear();
        fileStats.clear();

        // Reset auto-enable counter
        consecutiveCallCount.set(0);

        System.out.println("[Echo] Lua call tracker RESET");
    }

    /**
     * 콘솔 출력
     */
    public void printStats(int topN) {
        System.out.println("\n🔷 LUA PROFILING STATS");
        System.out.println("───────────────────────────────────────────────────────");
        System.out.printf("  Total Calls: %,d | Total Time: %.2f ms%n",
                getTotalCalls(), getTotalTimeMs());
        System.out.println();

        System.out.println("  Top Functions by Time:");
        int rank = 1;
        for (LuaFunctionStats stats : getTopFunctionsByTime(topN)) {
            System.out.printf("    #%d %-25s | calls: %,6d | total: %6.2f ms | avg: %.3f ms%n",
                    rank++,
                    StringUtils.truncate(stats.getName(), 25),
                    stats.getCallCount(),
                    stats.getTotalMs(),
                    stats.getAverageMs());
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

        if (!uiElementStats.isEmpty()) {
            System.out.println("\n  UI Elements:");
            List<LuaUIElementStats> sortedUI = new ArrayList<>(uiElementStats.values());
            sortedUI.sort((a, b) -> Long.compare(b.getTotalMicros(), a.getTotalMicros()));

            int count = 0;
            for (LuaUIElementStats stats : sortedUI) {
                if (count++ >= topN)
                    break;
                System.out.printf("    %-15s | %-20s | draws: %,6d | total: %6.2f ms | avg: %.3f ms%n",
                        stats.getCategory(),
                        StringUtils.truncate(stats.getElementName(), 20),
                        stats.getDrawCount(),
                        stats.getTotalMs(),
                        stats.getAverageMs());
            }
        }
        System.out.println();
    }

    /**
     * JSON 출력용 Map
     */
    public Map<String, Object> toMap(int topN) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("enabled", profiler.isLuaProfilingEnabled());
        map.put("total_calls", getTotalCalls());
        map.put("total_time_ms", Math.round(getTotalTimeMs() * 100) / 100.0);

        List<Map<String, Object>> topFunctions = new ArrayList<>();
        int rank = 1;
        for (LuaFunctionStats stats : getTopFunctionsByTime(topN)) {
            topFunctions.add(stats.toMap(rank++));
        }
        map.put("top_functions_by_time", topFunctions);

        List<Map<String, Object>> events = new ArrayList<>();
        for (LuaEventStats stats : eventStats.values()) {
            events.add(stats.toMap());
        }
        map.put("events", events);

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

    // ============================================================
    // 내부 클래스
    // ============================================================

    public static class LuaFunctionStats {
        private final String name;
        private final LongAdder callCount = new LongAdder();
        private final LongAdder totalMicros = new LongAdder();
        private final java.util.concurrent.atomic.AtomicLong maxMicros = new java.util.concurrent.atomic.AtomicLong(0);

        public LuaFunctionStats(String name) {
            this.name = name;
        }

        public void record(long durationMicros) {
            callCount.increment();
            totalMicros.add(durationMicros);
            long current;
            do {
                current = maxMicros.get();
                if (durationMicros <= current)
                    return;
            } while (!maxMicros.compareAndSet(current, durationMicros));
        }

        public String getName() {
            return name;
        }

        public long getCallCount() {
            return callCount.sum();
        }

        public long getTotalMicros() {
            return totalMicros.sum();
        }

        public long getMaxMicros() {
            return maxMicros.get();
        } // Added getter

        public double getTotalMs() {
            return totalMicros.sum() / 1000.0;
        }

        public double getAverageMs() {
            long count = callCount.sum();
            return count == 0 ? 0 : getTotalMs() / count;
        }

        public Map<String, Object> toMap(int rank) {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("rank", rank);
            map.put("name", name);
            map.put("call_count", getCallCount());
            map.put("total_time_ms", Math.round(getTotalMs() * 100) / 100.0);
            map.put("average_time_ms", Math.round(getAverageMs() * 1000) / 1000.0);
            map.put("max_time_ms", Math.round(getMaxMicros() / 1000.0 * 100) / 100.0);
            return map;
        }
    }

    public static class LuaEventStats {
        private final String name;
        private final LongAdder fireCount = new LongAdder();
        private final LongAdder totalHandlers = new LongAdder();
        private final LongAdder totalMicros = new LongAdder();

        public LuaEventStats(String name) {
            this.name = name;
        }

        public void record(long durationMicros, int handlerCount) {
            fireCount.increment();
            totalHandlers.add(handlerCount);
            totalMicros.add(durationMicros);
        }

        public String getName() {
            return name;
        }

        public long getFireCount() {
            return fireCount.sum();
        }

        public long getTotalHandlers() {
            return totalHandlers.sum();
        }

        public double getTotalMs() {
            return totalMicros.sum() / 1000.0;
        }

        public double getAverageHandlersPerFire() {
            long count = fireCount.sum();
            return count == 0 ? 0 : (double) totalHandlers.sum() / count;
        }

        public Map<String, Object> toMap() {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("name", name);
            map.put("fire_count", getFireCount());
            map.put("total_handlers", getTotalHandlers());
            map.put("avg_handlers_per_fire", Math.round(getAverageHandlersPerFire() * 10) / 10.0);
            map.put("total_time_ms", Math.round(getTotalMs() * 100) / 100.0);
            return map;
        }
    }

    public static class LuaUIElementStats {
        private final LuaUICategory category;
        private final String elementName;
        private final LongAdder drawCount = new LongAdder();
        private final LongAdder totalMicros = new LongAdder();
        private final java.util.concurrent.atomic.AtomicLong maxMicros = new java.util.concurrent.atomic.AtomicLong(0);

        public LuaUIElementStats(LuaUICategory category, String elementName) {
            this.category = category;
            this.elementName = elementName;
        }

        public void record(long durationMicros) {
            drawCount.increment();
            totalMicros.add(durationMicros);
            long current;
            do {
                current = maxMicros.get();
                if (durationMicros <= current)
                    return;
            } while (!maxMicros.compareAndSet(current, durationMicros));
        }

        public LuaUICategory getCategory() {
            return category;
        }

        public String getElementName() {
            return elementName;
        }

        public long getDrawCount() {
            return drawCount.sum();
        }

        public long getTotalMicros() {
            return totalMicros.sum();
        }

        public double getTotalMs() {
            return totalMicros.sum() / 1000.0;
        }

        public double getAverageMs() {
            long count = drawCount.sum();
            return count == 0 ? 0 : getTotalMs() / count;
        }

        public Map<String, Object> toMap() {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("category", category.name());
            map.put("element", elementName);
            map.put("draw_count", getDrawCount());
            map.put("total_ms", Math.round(getTotalMs() * 100) / 100.0);
            map.put("avg_ms", Math.round(getAverageMs() * 1000) / 1000.0);
            return map;
        }
    }
}
