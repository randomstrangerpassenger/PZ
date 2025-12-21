package com.echo.lua;

import com.echo.measure.EchoProfiler;
import com.echo.util.StringUtils;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.LongAdder;

/**
 * Lua 호출 추적기 (v2.1 - Orphaned Ends 수정)
 * 
 * 핵심 원칙: "tracked 프레임만 push"
 * - Start에서 추적 여부 결정 → 추적 시에만 스택에 push
 * - End에서 스택이 비어있으면 = Start가 추적 안 됨 → 조용히 리턴 (에러 아님)
 * 
 * v2.1 변경사항:
 * - lastPushedToken 제거 (중첩 호출 오탐 방지)
 * - 빈 스택 = 정상 케이스 (orphaned 카운트 안 함)
 * - Detailed Window 통계 추가
 * - Context 태깅 지원
 */
public class LuaCallTracker {

    private static LuaCallTracker INSTANCE;

    // ─────────────────────────────────────────────────────────────
    // Detailed Window 상태
    // ─────────────────────────────────────────────────────────────
    private volatile long detailedUntilNanos = 0;
    private volatile int sampleRate = 1; // 1 = 100%, 4 = 25%
    private final AtomicLong sampleCounter = new AtomicLong(0);

    // Detailed Window 세션 통계 (P1 요구사항)
    private final LongAdder detailedWindowsOpened = new LongAdder();
    private final LongAdder detailedTotalActiveMs = new LongAdder();
    private volatile long lastWindowOpenTime = 0;
    private volatile String currentContextTag = "Unknown";

    // ─────────────────────────────────────────────────────────────
    // 스레드별 호출 스택 (중첩 호출 + Self-Time 계산)
    // ─────────────────────────────────────────────────────────────
    private final ThreadLocal<ArrayDeque<CallFrame>> callStack = ThreadLocal.withInitial(() -> new ArrayDeque<>(32));

    // 프레임 설정
    private static final int MAX_STACK_DEPTH = 128;
    private static final long FRAME_TTL_NANOS = 5_000_000_000L; // 5초

    // 현재 프레임 ID (틱 경계에서 증가)
    private final AtomicLong currentFrameId = new AtomicLong(0);

    // ─────────────────────────────────────────────────────────────
    // 함수별/이벤트별 통계
    // ─────────────────────────────────────────────────────────────
    private final Map<String, LuaFunctionStats> functionStats = new ConcurrentHashMap<>();
    private final Map<String, LuaEventStats> eventStats = new ConcurrentHashMap<>();
    private final Map<String, LuaUIElementStats> uiElementStats = new ConcurrentHashMap<>();

    // Context/File 통계
    private final Map<String, LongAdder> contextStats = new ConcurrentHashMap<>();
    private final Map<String, LongAdder> fileStats = new ConcurrentHashMap<>();

    // ─────────────────────────────────────────────────────────────
    // 카운터
    // ─────────────────────────────────────────────────────────────
    private final LongAdder totalCalls = new LongAdder(); // 전체 호출 수
    private final LongAdder trackedCalls = new LongAdder(); // 추적된 호출 수 (스택에 push됨)
    private final LongAdder untrackedCalls = new LongAdder(); // 추적 안 된 호출 수 (필터링/샘플링)
    private final LongAdder totalTimeMicros = new LongAdder();

    // Fail-safe 카운터 (품질 지표)
    private final LongAdder mismatchCount = new LongAdder(); // 함수 불일치 (디버깅용)
    private final LongAdder droppedFrames = new LongAdder(); // TTL 초과로 정리된 프레임
    private final LongAdder stackResets = new LongAdder(); // 스택 리셋 발생 횟수

    // ─────────────────────────────────────────────────────────────
    // 함수 이름 캐시 (WeakHashMap - GC 시 자동 정리)
    // ─────────────────────────────────────────────────────────────
    private final Map<Object, String> functionNameCache = Collections.synchronizedMap(new WeakHashMap<>(256));

    // Top N 캐시
    private volatile List<LuaFunctionStats> topByTimeCached = new ArrayList<>();
    private volatile List<LuaFunctionStats> topByCallsCached = new ArrayList<>();
    private volatile long lastCacheUpdate = 0;
    private static final long CACHE_TTL_MS = 1000;

    // Dependencies
    private final com.echo.config.EchoConfig config;
    private final EchoProfiler profiler;

    // ─────────────────────────────────────────────────────────────
    // CallFrame 구조체
    // ─────────────────────────────────────────────────────────────
    private static class CallFrame {
        final String funcName;
        final String contextTag;
        final long startNanos;
        final long frameId;
        long childTime = 0; // 하위 호출에 소요된 시간

        CallFrame(String funcName, String contextTag, long startNanos, long frameId) {
            this.funcName = funcName;
            this.contextTag = contextTag;
            this.startNanos = startNanos;
            this.frameId = frameId;
        }
    }

    public LuaCallTracker(com.echo.config.EchoConfig config, EchoProfiler profiler) {
        this.config = config;
        this.profiler = profiler;
    }

    public static LuaCallTracker getInstance() {
        try {
            com.pulse.di.PulseServiceLocator locator = com.pulse.di.PulseServiceLocator.getInstance();
            LuaCallTracker service = locator.getService(LuaCallTracker.class);
            if (service != null) {
                return service;
            }
        } catch (NoClassDefFoundError | Exception ignored) {
        }

        if (INSTANCE == null) {
            INSTANCE = new LuaCallTracker(com.echo.config.EchoConfig.getInstance(), EchoProfiler.getInstance());
        }
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // Detailed Window 제어
    // ─────────────────────────────────────────────────────────────

    /**
     * Detailed Window 열기 (컨텍스트 태그 포함)
     */
    public void openDetailedWindow(long durationMs, int sampleRate, String contextTag) {
        long now = System.nanoTime();

        // 이전 윈도우가 열려있었다면 시간 누적
        if (lastWindowOpenTime > 0 && now < detailedUntilNanos) {
            long activeMs = (now - lastWindowOpenTime) / 1_000_000L;
            detailedTotalActiveMs.add(activeMs);
        }

        this.detailedUntilNanos = now + durationMs * 1_000_000L;
        this.sampleRate = Math.max(1, sampleRate);
        this.currentContextTag = (contextTag != null) ? contextTag : "Unknown";
        this.lastWindowOpenTime = now;

        detailedWindowsOpened.increment();
        System.out.println("[Echo/LuaTracker] Detailed window opened: " + durationMs + "ms, rate=1/" + sampleRate
                + ", context=" + contextTag);
    }

    /**
     * Detailed Window 열기 (기본 컨텍스트)
     */
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

    // ─────────────────────────────────────────────────────────────
    // 핵심 기록 API (v2.1 - 수정된 로직)
    // ─────────────────────────────────────────────────────────────

    /**
     * Lua 함수 호출 시작 기록 (Pulse에서 호출)
     * 
     * 핵심: "tracked 프레임만 push"
     * - 추적 조건을 만족하지 않으면 push 안 함
     * - push된 프레임만 End에서 pop됨
     */
    public void recordCallStart(Object func, long startNanos) {
        totalCalls.increment();

        // 추적 여부 결정: Detailed Window 활성 && 샘플링 통과
        boolean shouldTrack = isDetailedActive() && shouldSample();

        if (!shouldTrack) {
            untrackedCalls.increment();
            return; // push 안 함 → End에서 빈 스택 = 정상
        }

        ArrayDeque<CallFrame> stack = callStack.get();

        // Fail-safe: 스택 깊이 초과 시 정리
        if (stack.size() >= MAX_STACK_DEPTH) {
            cleanupStaleFrames(stack, startNanos);
        }

        String funcName = extractFunctionName(func);
        stack.push(new CallFrame(funcName, currentContextTag, startNanos, currentFrameId.get()));
        trackedCalls.increment();
    }

    /**
     * Lua 함수 호출 종료 기록 (Pulse에서 호출)
     * 
     * 핵심: 스택이 비어있으면 = Start가 추적 안 됨 → 조용히 리턴 (에러 아님)
     */
    public void recordCallEnd(Object func, long endNanos) {
        ArrayDeque<CallFrame> stack = callStack.get();

        // 스택이 비어있다 = Start가 추적 안 됨 (정상 케이스)
        if (stack.isEmpty()) {
            // 이건 에러가 아님! 조용히 리턴
            return;
        }

        CallFrame frame = stack.pop();
        long elapsed = endNanos - frame.startNanos;
        long elapsedMicros = elapsed / 1000;

        // Self time 계산 (하위 호출 시간 제외)
        long selfTime = elapsed - frame.childTime;
        long selfMicros = selfTime / 1000;

        // 상위 프레임에 child time 전파
        if (!stack.isEmpty()) {
            stack.peek().childTime += elapsed;
        }

        // 통계 집계 (self-time + context 포함)
        LuaFunctionStats stats = functionStats.computeIfAbsent(frame.funcName, LuaFunctionStats::new);
        stats.record(elapsedMicros, selfMicros);
        stats.setContext(frame.contextTag);

        totalTimeMicros.add(elapsedMicros);

        // Context 추적 (프레임에 저장된 컨텍스트 사용)
        contextStats.computeIfAbsent(frame.contextTag, k -> new LongAdder()).add(elapsedMicros);
    }

    /**
     * 오래된 프레임 정리 (예외 탈출 대응)
     */
    private void cleanupStaleFrames(ArrayDeque<CallFrame> stack, long nowNanos) {
        int cleaned = 0;
        while (!stack.isEmpty()) {
            CallFrame oldest = stack.peekLast();
            if (nowNanos - oldest.startNanos > FRAME_TTL_NANOS) {
                stack.pollLast();
                cleaned++;
            } else {
                break;
            }
        }
        if (cleaned > 0) {
            droppedFrames.add(cleaned);
            System.out.println("[Echo/LuaTracker] Cleaned " + cleaned + " stale frames (likely exception escape)");
        }
    }

    /**
     * 스택 강제 리셋 (비상 시 사용)
     */
    public void resetStack() {
        ArrayDeque<CallFrame> stack = callStack.get();
        int size = stack.size();
        if (size > 0) {
            stack.clear();
            stackResets.increment();
            System.out.println("[Echo/LuaTracker] Stack reset (had " + size + " frames)");
        }
    }

    /**
     * 틱 경계에서 호출 - 프레임 ID 증가 및 정리
     */
    public void onTickBoundary() {
        currentFrameId.incrementAndGet();

        // 윈도우 종료 감지 및 시간 누적
        if (lastWindowOpenTime > 0 && !isDetailedActive()) {
            long activeMs = (detailedUntilNanos - lastWindowOpenTime) / 1_000_000L;
            detailedTotalActiveMs.add(Math.max(0, activeMs));
            lastWindowOpenTime = 0;
            // 결과는 echo_reports JSON에 포함됨
        }
    }

    // ─────────────────────────────────────────────────────────────
    // Legacy API (하위 호환성)
    // ─────────────────────────────────────────────────────────────

    public void recordFunctionCall(String functionName, long durationMicros) {
        if (!profiler.isLuaProfilingEnabled())
            return;

        functionStats.computeIfAbsent(functionName, LuaFunctionStats::new)
                .record(durationMicros);

        totalCalls.increment();
        trackedCalls.increment();
        totalTimeMicros.add(durationMicros);

        String context = EchoLuaContext.getContext();
        contextStats.computeIfAbsent(context, k -> new LongAdder()).add(durationMicros);
    }

    public void recordFunctionCall(String functionName, String sourceFile, long durationMicros) {
        recordFunctionCall(functionName, durationMicros);
        if (sourceFile != null && !sourceFile.isEmpty()) {
            fileStats.computeIfAbsent(sourceFile, k -> new LongAdder()).add(durationMicros);
        }
    }

    public void recordEventCall(String eventName, long durationMicros, int handlerCount) {
        if (!profiler.isLuaProfilingEnabled())
            return;
        eventStats.computeIfAbsent(eventName, LuaEventStats::new)
                .record(durationMicros, handlerCount);
    }

    public void recordUIElementCall(LuaUICategory category, String elementName, long durationMicros) {
        if (!profiler.isLuaProfilingEnabled())
            return;
        String key = category.name() + ":" + elementName;
        uiElementStats.computeIfAbsent(key, k -> new LuaUIElementStats(category, elementName))
                .record(durationMicros);
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

    // ─────────────────────────────────────────────────────────────
    // 함수 이름 추출 (FunctionLabeler 위임)
    // ─────────────────────────────────────────────────────────────

    private String extractFunctionName(Object func) {
        if (func == null)
            return "<anonymous>";

        // FunctionLabeler로 위임 (캐싱, 3단계 폴백 지원)
        return FunctionLabeler.labelOf(func);
    }

    // ─────────────────────────────────────────────────────────────
    // 조회 API
    // ─────────────────────────────────────────────────────────────

    public long getTotalCalls() {
        return totalCalls.sum();
    }

    public long getTrackedCalls() {
        return trackedCalls.sum();
    }

    public long getUntrackedCalls() {
        return untrackedCalls.sum();
    }

    // Legacy 호환
    public long getSampledCalls() {
        return trackedCalls.sum();
    }

    public long getDroppedCalls() {
        return untrackedCalls.sum();
    }

    public long getMismatchCount() {
        return mismatchCount.sum();
    }

    public long getDroppedFrames() {
        return droppedFrames.sum();
    }

    public long getStackResets() {
        return stackResets.sum();
    }

    // Legacy 호환 (이제 항상 0 반환 - 빈 스택은 에러가 아님)
    public long getOrphanedEnds() {
        return 0; // v2.1: 더 이상 에러로 카운트하지 않음
    }

    public int getSampleRate() {
        return sampleRate;
    }

    public double getTotalTimeMs() {
        return totalTimeMicros.sum() / 1000.0;
    }

    public long getDetailedWindowsOpened() {
        return detailedWindowsOpened.sum();
    }

    public long getDetailedTotalActiveMs() {
        return detailedTotalActiveMs.sum();
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

    // ─────────────────────────────────────────────────────────────
    // 리셋 및 출력
    // ─────────────────────────────────────────────────────────────

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
        functionNameCache.clear();

        System.out.println("[Echo] Lua call tracker RESET");
    }

    public void printStats(int topN) {
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
     * JSON 출력용 Map (품질 지표 포함 - v2.1)
     */
    public Map<String, Object> toMap(int topN) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("enabled", profiler.isLuaProfilingEnabled());
        map.put("detailed_active", isDetailedActive());

        // 카운터
        map.put("total_calls", getTotalCalls());
        map.put("tracked_calls", getTrackedCalls());
        map.put("untracked_calls", getUntrackedCalls());
        map.put("total_time_ms", Math.round(getTotalTimeMs() * 100) / 100.0);

        // Detailed Window 통계 (P1 요구사항)
        Map<String, Object> windowStats = new LinkedHashMap<>();
        windowStats.put("windows_opened", getDetailedWindowsOpened());
        windowStats.put("total_active_ms", getDetailedTotalActiveMs());
        map.put("detailed_window_stats", windowStats);

        // 품질 지표 (v2.1)
        Map<String, Object> quality = new LinkedHashMap<>();
        quality.put("dropped_frames", getDroppedFrames());
        quality.put("stack_resets", getStackResets());
        quality.put("sample_rate", "1/" + sampleRate);

        // 추적 비율 계산
        long total = getTotalCalls();
        long tracked = getTrackedCalls();
        double trackingRate = (total > 0) ? (tracked * 100.0 / total) : 0;
        quality.put("tracking_rate_percent", Math.round(trackingRate * 10) / 10.0);

        map.put("quality_metrics", quality);

        // 라벨링 통계 (FunctionLabeler)
        map.put("labeling_stats", FunctionLabeler.getStats());

        // path_hits (Pulse 연동)
        long pathHits = getPathHitsFromPulse();
        map.put("path_hits", pathHits);
        map.put("path_verified", pathHits > 0);

        String mode = (getTrackedCalls() > 0) ? "detailed" : "path_verify";
        map.put("mode", mode);

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

        // Context Stats (P2 요구사항)
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

    private long getPathHitsFromPulse() {
        try {
            return com.pulse.api.lua.PulseLuaHook.getPathHitCount();
        } catch (NoClassDefFoundError | Exception e) {
            return 0;
        }
    }
}
