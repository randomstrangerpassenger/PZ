package com.echo.lua;

import com.echo.measure.EchoProfiler;
import com.pulse.api.log.PulseLogger;

import java.util.*;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Lua 호출 추적기 (v3.0 - Refactored).
 * 
 * <p>
 * v3.0에서 로직을 분리하여 조정자 역할만 담당합니다:
 * </p>
 * <ul>
 * <li>{@link CallStackTracker} - 스택/프레임 관리</li>
 * <li>{@link LuaStatistics} - 통계 수집/조회</li>
 * <li>{@link DetailedWindowManager} - Detailed Window 관리 (기존)</li>
 * </ul>
 * 
 * <h3>핵심 원칙:</h3>
 * <ul>
 * <li>"tracked 프레임만 push" - 추적 조건 만족 시에만 스택에 push</li>
 * <li>빈 스택 = 정상 (Start가 추적 안 됨)</li>
 * </ul>
 * 
 * @since Echo 0.9
 * @since Echo 1.0 - v3.0 Refactored
 */
public class LuaCallTracker {

    private static LuaCallTracker INSTANCE;

    // ═══════════════════════════════════════════════════════════════
    // Delegate Components
    // ═══════════════════════════════════════════════════════════════

    private final CallStackTracker stackTracker = new CallStackTracker();
    private final LuaStatistics statistics = new LuaStatistics();

    // ═══════════════════════════════════════════════════════════════
    // Detailed Window State
    // ═══════════════════════════════════════════════════════════════

    private volatile long detailedUntilNanos = 0;
    private volatile int sampleRate = 1; // 1 = 100%, 4 = 25%
    private final AtomicLong sampleCounter = new AtomicLong(0);
    private volatile long lastWindowOpenTime = 0;
    private volatile String currentContextTag = "Unknown";

    // ═══════════════════════════════════════════════════════════════
    // Function Name Cache
    // ═══════════════════════════════════════════════════════════════

    private final Map<Object, String> functionNameCache = Collections.synchronizedMap(new WeakHashMap<>(256));

    // ═══════════════════════════════════════════════════════════════
    // Dependencies
    // ═══════════════════════════════════════════════════════════════

    private final EchoProfiler profiler;

    // ═══════════════════════════════════════════════════════════════
    // Constructor & Singleton
    // ═══════════════════════════════════════════════════════════════

    public LuaCallTracker(com.echo.config.EchoConfig config, EchoProfiler profiler) {
        // config is accepted for API compatibility but not used internally
        this.profiler = profiler;
    }

    public static LuaCallTracker getInstance() {
        // 1. Try ServiceLocator (Hybrid DI)
        try {
            var locator = com.pulse.di.PulseServiceLocator.getInstance();
            LuaCallTracker service = locator.getService(LuaCallTracker.class);
            if (service != null) {
                return service;
            }
        } catch (Exception ignored) {
            // ServiceLocator not available
        }

        if (INSTANCE == null) {
            INSTANCE = new LuaCallTracker(com.echo.config.EchoConfig.getInstance(), EchoProfiler.getInstance());
        }
        return INSTANCE;
    }

    /**
     * 싱글톤 인스턴스 리셋 (테스트 전용)
     */
    @com.pulse.api.VisibleForTesting
    public static void resetInstance() {
        INSTANCE = null;
    }

    // ═══════════════════════════════════════════════════════════════
    // Detailed Window Control
    // ═══════════════════════════════════════════════════════════════

    public void openDetailedWindow(long durationMs, int sampleRate, String contextTag) {
        long now = System.nanoTime();

        // 이전 윈도우가 열려있었다면 시간 누적
        if (lastWindowOpenTime > 0 && now < detailedUntilNanos) {
            long activeMs = (now - lastWindowOpenTime) / 1_000_000L;
            statistics.addDetailedActiveMs(activeMs);
        }

        this.detailedUntilNanos = now + durationMs * 1_000_000L;
        this.sampleRate = Math.max(1, sampleRate);
        this.currentContextTag = (contextTag != null) ? contextTag : "Unknown";
        this.lastWindowOpenTime = now;

        statistics.incrementDetailedWindowsOpened();
        statistics.incrementDetailedWindowsOpened();
        PulseLogger.info("Echo", "[LuaTracker] Detailed window opened: " + durationMs + "ms, rate=1/" + sampleRate
                + ", context=" + contextTag);
    }

    public void openDetailedWindow(long durationMs, int sampleRate) {
        openDetailedWindow(durationMs, sampleRate, "Manual");
    }

    public boolean isDetailedActive() {
        return System.nanoTime() < detailedUntilNanos;
    }

    public void setContextTag(String tag) {
        this.currentContextTag = (tag != null) ? tag : "Unknown";
    }

    private boolean shouldSample() {
        if (sampleRate == 1)
            return true;
        return sampleCounter.incrementAndGet() % sampleRate == 0;
    }

    // ═══════════════════════════════════════════════════════════════
    // Core Recording API (위임)
    // ═══════════════════════════════════════════════════════════════

    public void recordCallStart(Object func, long startNanos) {
        statistics.incrementTotalCalls();

        // 추적 여부 결정: Detailed Window 활성 && 샘플링 통과
        boolean shouldTrack = isDetailedActive() && shouldSample();

        if (!shouldTrack) {
            statistics.incrementUntrackedCalls();
            return;
        }

        String funcName = extractFunctionName(func);
        boolean pushed = stackTracker.recordStart(funcName, currentContextTag, startNanos);

        if (pushed) {
            statistics.incrementTrackedCalls();
        } else {
            statistics.addDroppedFrames(1);
        }
    }

    public void recordCallEnd(Object func, long endNanos) {
        CallStackTracker.CallResult result = stackTracker.recordEnd(endNanos);

        // 스택이 비어있다 = Start가 추적 안 됨 (정상 케이스)
        if (result == null) {
            return;
        }

        // 통계 기록
        statistics.recordFunction(result.funcName, result.elapsedMicros,
                result.selfMicros, result.contextTag);
    }

    public void resetStack() {
        int resetCount = stackTracker.resetStack();
        if (resetCount > 0) {
            statistics.incrementStackResets();
        }
    }

    public void onTickBoundary() {
        stackTracker.onTickBoundary();

        // 윈도우 종료 감지 및 시간 누적
        if (lastWindowOpenTime > 0 && !isDetailedActive()) {
            long activeMs = (detailedUntilNanos - lastWindowOpenTime) / 1_000_000L;
            statistics.addDetailedActiveMs(Math.max(0, activeMs));
            lastWindowOpenTime = 0;
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Legacy API (하위 호환성)
    // ═══════════════════════════════════════════════════════════════

    public void recordFunctionCall(String functionName, long durationMicros) {
        if (!profiler.isLuaProfilingEnabled())
            return;
        statistics.recordFunction(functionName, durationMicros);
        String context = EchoLuaContext.getContext();
        statistics.recordFunction(functionName, durationMicros, 0, context);
    }

    public void recordFunctionCall(String functionName, String sourceFile, long durationMicros) {
        recordFunctionCall(functionName, durationMicros);
        statistics.recordFile(sourceFile, durationMicros);
    }

    public void recordEventCall(String eventName, long durationMicros, int handlerCount) {
        if (!profiler.isLuaProfilingEnabled())
            return;
        statistics.recordEvent(eventName, durationMicros, handlerCount);
    }

    public void recordUIElementCall(LuaUICategory category, String elementName, long durationMicros) {
        if (!profiler.isLuaProfilingEnabled())
            return;
        statistics.recordUIElement(category, elementName, durationMicros);
    }

    public void profileFunction(String functionName, Runnable function) {
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

    public void profileEvent(String eventName, int handlerCount, Runnable event) {
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

    // ═══════════════════════════════════════════════════════════════
    // Function Name Extraction
    // ═══════════════════════════════════════════════════════════════

    private String extractFunctionName(Object func) {
        if (func == null)
            return "<anonymous>";
        return FunctionLabeler.labelOf(func);
    }

    // ═══════════════════════════════════════════════════════════════
    // Query API (위임)
    // ═══════════════════════════════════════════════════════════════

    public long getTotalCalls() {
        return statistics.getTotalCalls();
    }

    public long getTrackedCalls() {
        return statistics.getTrackedCalls();
    }

    public long getUntrackedCalls() {
        return statistics.getUntrackedCalls();
    }

    public long getSampledCalls() {
        return statistics.getSampledCalls();
    }

    public long getDroppedCalls() {
        return statistics.getDroppedCalls();
    }

    public long getMismatchCount() {
        return statistics.getMismatchCount();
    }

    public long getDroppedFrames() {
        return statistics.getDroppedFrames();
    }

    public long getStackResets() {
        return statistics.getStackResets();
    }

    public long getOrphanedEnds() {
        return statistics.getOrphanedEnds();
    }

    public int getSampleRate() {
        return sampleRate;
    }

    public double getTotalTimeMs() {
        return statistics.getTotalTimeMs();
    }

    public long getDetailedWindowsOpened() {
        return statistics.getDetailedWindowsOpened();
    }

    public long getDetailedTotalActiveMs() {
        return statistics.getDetailedTotalActiveMs();
    }

    public LuaFunctionStats getFunctionStats(String functionName) {
        return statistics.getFunctionStats(functionName);
    }

    public Collection<LuaFunctionStats> getAllFunctionStats() {
        return statistics.getAllFunctionStats();
    }

    public LuaEventStats getEventStats(String eventName) {
        return statistics.getEventStats(eventName);
    }

    public Collection<LuaEventStats> getAllEventStats() {
        return statistics.getAllEventStats();
    }

    public LuaUIElementStats getUIElementStats(LuaUICategory category, String elementName) {
        return statistics.getUIElementStats(category, elementName);
    }

    public Collection<LuaUIElementStats> getAllUIElementStats() {
        return statistics.getAllUIElementStats();
    }

    public List<LuaFunctionStats> getTopFunctionsByTime(int n) {
        return statistics.getTopFunctionsByTime(n);
    }

    public List<LuaFunctionStats> getTopFunctionsByCalls(int n) {
        return statistics.getTopFunctionsByCalls(n);
    }

    // ═══════════════════════════════════════════════════════════════
    // Reset & Print
    // ═══════════════════════════════════════════════════════════════

    public void reset() {
        statistics.reset();
        functionNameCache.clear();
        statistics.reset();
        functionNameCache.clear();
        PulseLogger.info("Echo", "Lua call tracker RESET");
    }

    public void printStats(int topN) {
        statistics.printStats(topN, sampleRate);
    }

    public Map<String, Object> toMap(int topN) {
        Map<String, Object> map = statistics.toMap(topN,
                profiler.isLuaProfilingEnabled(),
                isDetailedActive(),
                sampleRate);

        // FunctionLabeler 통계 추가
        map.put("labeling_stats", FunctionLabeler.getStats());

        // Path hits from Pulse
        long pathHits = getPathHitsFromPulse();
        map.put("path_hits", pathHits);
        map.put("path_verified", pathHits > 0);

        String mode = (getTrackedCalls() > 0) ? "detailed" : "path_verify";
        map.put("mode", mode);

        return map;
    }

    private long getPathHitsFromPulse() {
        try {
            return com.pulse.api.lua.PulseLuaHook.getPathHitCount();
        } catch (NoClassDefFoundError | Exception e) {
            return 0;
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Internal Accessors (for advanced use)
    // ═══════════════════════════════════════════════════════════════

    public CallStackTracker getStackTracker() {
        return stackTracker;
    }

    public LuaStatistics getStatistics() {
        return statistics;
    }
}
