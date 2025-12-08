package com.echo.lua;

import com.echo.measure.EchoProfiler;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.LongAdder;

import com.echo.util.StringUtils;

/**
 * Lua 호출 추적기
 * 
 * Lua 함수/이벤트 호출을 세부적으로 추적하고 통계를 제공합니다.
 * On-Demand 방식으로 활성화됩니다.
 */
public class LuaCallTracker {

    private static final LuaCallTracker INSTANCE = new LuaCallTracker();

    // 함수별 통계
    private final Map<String, LuaFunctionStats> functionStats = new ConcurrentHashMap<>();

    // 이벤트별 통계
    private final Map<String, LuaEventStats> eventStats = new ConcurrentHashMap<>();

    // 전체 통계
    private final LongAdder totalCalls = new LongAdder();
    private final LongAdder totalTimeMicros = new LongAdder();

    // Top N 캐시
    private volatile List<LuaFunctionStats> topByTimeCached = new ArrayList<>();
    private volatile List<LuaFunctionStats> topByCallsCached = new ArrayList<>();
    private volatile long lastCacheUpdate = 0;
    private static final long CACHE_TTL_MS = 1000;

    private LuaCallTracker() {
    }

    public static LuaCallTracker getInstance() {
        return INSTANCE;
    }

    // ============================================================
    // 기록 API
    // ============================================================

    /**
     * Lua 함수 호출 기록
     */
    public void recordFunctionCall(String functionName, long durationMicros) {
        if (!EchoProfiler.getInstance().isLuaProfilingEnabled())
            return;

        functionStats.computeIfAbsent(functionName, LuaFunctionStats::new)
                .record(durationMicros);

        totalCalls.increment();
        totalTimeMicros.add(durationMicros);
    }

    /**
     * Lua 이벤트 호출 기록
     */
    public void recordEventCall(String eventName, long durationMicros, int handlerCount) {
        if (!EchoProfiler.getInstance().isLuaProfilingEnabled())
            return;

        eventStats.computeIfAbsent(eventName, LuaEventStats::new)
                .record(durationMicros, handlerCount);
    }

    /**
     * 프로파일링 래퍼 - 함수
     */
    public void profileFunction(String functionName, Runnable function) {
        if (!EchoProfiler.getInstance().isLuaProfilingEnabled()) {
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
        if (!EchoProfiler.getInstance().isLuaProfilingEnabled()) {
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

    /**
     * 총 Lua 호출 수
     */
    public long getTotalCalls() {
        return totalCalls.sum();
    }

    /**
     * 총 Lua 실행 시간 (밀리초)
     */
    public double getTotalTimeMs() {
        return totalTimeMicros.sum() / 1000.0;
    }

    /**
     * 함수별 통계 조회
     */
    public LuaFunctionStats getFunctionStats(String functionName) {
        return functionStats.get(functionName);
    }

    /**
     * 모든 함수 통계
     */
    public Collection<LuaFunctionStats> getAllFunctionStats() {
        return Collections.unmodifiableCollection(functionStats.values());
    }

    /**
     * 이벤트별 통계 조회
     */
    public LuaEventStats getEventStats(String eventName) {
        return eventStats.get(eventName);
    }

    /**
     * 모든 이벤트 통계
     */
    public Collection<LuaEventStats> getAllEventStats() {
        return Collections.unmodifiableCollection(eventStats.values());
    }

    /**
     * Top N 함수 (총 시간 기준)
     */
    public List<LuaFunctionStats> getTopFunctionsByTime(int n) {
        updateCacheIfNeeded();
        return topByTimeCached.size() <= n ? topByTimeCached : topByTimeCached.subList(0, n);
    }

    /**
     * Top N 함수 (호출 횟수 기준)
     */
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

    /**
     * 초기화
     */
    public void reset() {
        functionStats.clear();
        eventStats.clear();
        totalCalls.reset();
        totalTimeMicros.reset();
        topByTimeCached.clear();
        topByCallsCached.clear();
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
        System.out.println();
    }

    // truncate method removed - using StringUtils.truncate()

    /**
     * JSON 출력용 Map
     */
    public Map<String, Object> toMap(int topN) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("enabled", EchoProfiler.getInstance().isLuaProfilingEnabled());
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

        return map;
    }

    // ============================================================
    // 내부 클래스
    // ============================================================

    /**
     * 개별 Lua 함수 통계
     */
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
            // CAS pattern for thread-safe max update
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
        }

        public double getTotalMs() {
            return totalMicros.sum() / 1000.0;
        }

        public double getAverageMs() {
            long count = callCount.sum();
            return count == 0 ? 0 : getTotalMs() / count;
        }

        public double getMaxMs() {
            return maxMicros.get() / 1000.0;
        }

        public Map<String, Object> toMap(int rank) {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("rank", rank);
            map.put("name", name);
            map.put("call_count", getCallCount());
            map.put("total_time_ms", Math.round(getTotalMs() * 100) / 100.0);
            map.put("average_time_ms", Math.round(getAverageMs() * 1000) / 1000.0);
            map.put("max_time_ms", Math.round(getMaxMs() * 100) / 100.0);
            return map;
        }
    }

    /**
     * 개별 Lua 이벤트 통계
     */
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
}
