package com.echo.measure;

import com.echo.aggregate.TimingData;
import com.echo.aggregate.TickHistogram;
import com.echo.aggregate.SpikeLog;
import com.echo.lua.LuaCallTracker;
import com.echo.history.MetricCollector;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Echo Profiler - 계층적 프로파일링 엔진
 * 
 * Stack 기반 push/pop으로 중첩된 호출 구조를 추적합니다.
 * ThreadLocal을 사용하여 멀티스레드 환경에서도 안전합니다.
 */
public class EchoProfiler {

    private static EchoProfiler INSTANCE = new EchoProfiler();

    // --- Main Thread Fast-Path ---

    // 메인 스레드 (Fast-Path용)
    private static volatile Thread mainThread = null;

    // 메인 스레드 전용 스택 (ThreadLocal 우회)
    private final Deque<ProfilingFrame> mainThreadStack = new ArrayDeque<>();

    // --- Core Fields ---

    // 스레드별 프로파일링 스택 (메인 스레드 외)
    private final ThreadLocal<Deque<ProfilingFrame>> frameStack = ThreadLocal.withInitial(ArrayDeque::new);

    // Phase 1 최적화: ProfilingScope 객체 풀
    private final ThreadLocal<ProfilingScopePool> scopePool = ThreadLocal.withInitial(ProfilingScopePool::new);
    private final ProfilingScopePool mainThreadScopePool = new ProfilingScopePool();

    // 포인트별 누적 데이터
    private final Map<ProfilingPoint, TimingData> timingRegistry = new ConcurrentHashMap<>();

    // 틱 히스토그램 (Phase 3)
    private final TickHistogram tickHistogram = new TickHistogram();

    // 스파이크 로그 (Phase 3)
    private final SpikeLog spikeLog = new SpikeLog();

    // 메트릭 수집기 (Phase 3)
    private final MetricCollector metricCollector = new MetricCollector();

    // 프로파일링 활성화 상태
    private volatile boolean enabled = false;

    // Lua 프로파일링 (On-Demand)
    private volatile boolean luaProfilingEnabled = false;

    // 세션 시작 시간
    private volatile long sessionStartTime = 0;

    // 의존성
    private final com.echo.config.EchoConfig config;

    /**
     * @deprecated Use Constructor Injection via PulseServiceLocator
     */
    @Deprecated
    private EchoProfiler() {
        this(com.echo.config.EchoConfig.getInstance());
    }

    public EchoProfiler(com.echo.config.EchoConfig config) {
        this.config = config;
        // 모든 ProfilingPoint에 대한 TimingData 초기화
        for (ProfilingPoint point : ProfilingPoint.values()) {
            timingRegistry.put(point, new TimingData(point.name()));
        }
    }

    public static EchoProfiler getInstance() {
        // 1. Try ServiceLocator (Hybrid DI)
        try {
            com.pulse.di.PulseServiceLocator locator = com.pulse.di.PulseServiceLocator.getInstance();
            EchoProfiler service = locator.getService(EchoProfiler.class);
            if (service != null) {
                return service;
            }
        } catch (NoClassDefFoundError | Exception ignored) {
            // Pulse might not be fully loaded
        }

        // 2. Fallback
        if (INSTANCE == null) {
            INSTANCE = new EchoProfiler(com.echo.config.EchoConfig.getInstance());
        }
        return INSTANCE;
    }

    /**
     * 테스트용 인스턴스 설정.
     */
    @com.pulse.api.VisibleForTesting
    static void setInstance(EchoProfiler instance) {
        INSTANCE = instance != null ? instance : new EchoProfiler();
    }

    @com.pulse.api.VisibleForTesting
    static void resetInstance() {
        INSTANCE = new EchoProfiler();
    }

    /** 메인 스레드 설정 */
    public static void setMainThread(Thread thread) {
        mainThread = thread;
        System.out.println("[Echo] Main thread set: " + thread.getName());
    }

    private boolean isMainThread() {
        return Thread.currentThread() == mainThread;
    }

    private Deque<ProfilingFrame> getFrameStack() {
        if (isMainThread()) {
            return mainThreadStack;
        }
        return frameStack.get();
    }

    private ProfilingScopePool getScopePool() {
        if (isMainThread()) {
            return mainThreadScopePool;
        }
        return scopePool.get();
    }

    // --- Core API: push / pop ---

    public long push(ProfilingPoint point) {
        if (!enabled)
            return -1;
        if (point.isLuaRelated() && !luaProfilingEnabled)
            return -1;

        ProfilingFrame frame = new ProfilingFrame(point, System.nanoTime());
        getFrameStack().push(frame);

        return frame.id;
    }

    public long push(ProfilingPoint point, String customLabel) {
        if (!enabled)
            return -1;
        if (point.isLuaRelated() && !luaProfilingEnabled)
            return -1;

        ProfilingFrame frame = new ProfilingFrame(point, customLabel, System.nanoTime());
        getFrameStack().push(frame);

        return frame.id;
    }

    public void pop(ProfilingPoint point) {
        if (!enabled)
            return;

        Deque<ProfilingFrame> stack = getFrameStack();
        if (stack.isEmpty()) {
            System.err.println("[Echo] Warning: Unmatched pop for " + point);
            return;
        }

        ProfilingFrame frame = stack.pop();

        if (frame.point != point) {
            System.err.println("[Echo] Warning: Mismatched push/pop - expected "
                    + frame.point + ", got " + point);
        }

        long elapsed = System.nanoTime() - frame.startTime;
        long elapsedMicros = elapsed / 1000;

        TimingData data = timingRegistry.get(point);
        if (data != null) {
            data.addSample(elapsed, frame.customLabel);
        }

        if (point == ProfilingPoint.TICK) {
            tickHistogram.addSample(elapsedMicros);
        }

        spikeLog.logSpike(elapsedMicros, point, frame.customLabel);
    }

    public ProfilingScope scope(ProfilingPoint point) {
        push(point);
        return getScopePool().acquire(point, this);
    }

    public ProfilingScope scope(ProfilingPoint point, String label) {
        push(point, label);
        return getScopePool().acquire(point, this);
    }

    // --- Raw API (Zero-Allocation) ---

    public long startRaw(ProfilingPoint point) {
        if (!enabled)
            return -1;
        if (point.isLuaRelated() && !luaProfilingEnabled)
            return -1;
        return System.nanoTime();
    }

    public void endRaw(ProfilingPoint point, long startTime) {
        if (startTime < 0)
            return;

        long elapsed = System.nanoTime() - startTime;
        long elapsedMicros = elapsed / 1000;

        TimingData data = timingRegistry.get(point);
        if (data != null) {
            data.addSample(elapsed, null);
        }

        if (point == ProfilingPoint.TICK) {
            tickHistogram.addSample(elapsedMicros);
        }

        spikeLog.logSpike(elapsedMicros, point, null);
    }

    public void endRaw(ProfilingPoint point, long startTime, String label) {
        if (startTime < 0)
            return;

        long elapsed = System.nanoTime() - startTime;
        long elapsedMicros = elapsed / 1000;

        TimingData data = timingRegistry.get(point);
        if (data != null) {
            data.addSample(elapsed, label);
        }

        if (point == ProfilingPoint.TICK) {
            tickHistogram.addSample(elapsedMicros);
        }

        spikeLog.logSpike(elapsedMicros, point, label);
    }

    // --- Control API ---

    public void enable() {
        enable(true);
    }

    public void enable(boolean resetStats) {
        config.sanitize();

        if (!enabled && resetStats) {
            reset();
        }
        this.enabled = true;

        // Apply Lua profiling setting from config
        this.luaProfilingEnabled = config.isLuaProfilingEnabled();
        if (sessionStartTime == 0) {
            this.sessionStartTime = System.currentTimeMillis();
        }
        com.echo.measure.FreezeDetector.getInstance().start();
        com.echo.validation.SelfValidation.getInstance().scheduleValidation();
        com.echo.validation.FallbackTickEmitter.getInstance().startMonitoring();

        System.out.println("[Echo] Profiler ENABLED" + (resetStats ? " (stats reset)" : ""));
    }

    public void disable() {
        int orphanedFrames = clearActiveStacks();
        if (orphanedFrames > 0) {
            System.err.println("[Echo] Warning: " + orphanedFrames + " orphaned frames cleared on disable");
        }

        this.enabled = false;
        com.echo.measure.FreezeDetector.getInstance().stop();
        com.echo.validation.SelfValidation.getInstance().shutdown();
        com.echo.validation.FallbackTickEmitter.getInstance().stop();

        System.out.println("[Echo] Profiler DISABLED");
    }

    private int clearActiveStacks() {
        int count = 0;
        count += mainThreadStack.size();
        mainThreadStack.clear();

        Deque<ProfilingFrame> currentStack = frameStack.get();
        count += currentStack.size();
        currentStack.clear();

        return count;
    }

    public void enableLuaProfiling() {
        this.luaProfilingEnabled = true;
        System.out.println("[Echo] Lua Profiling ENABLED (On-Demand)");
    }

    public void disableLuaProfiling() {
        this.luaProfilingEnabled = false;
        System.out.println("[Echo] Lua Profiling DISABLED");
    }

    public boolean isEnabled() {
        return enabled;
    }

    public boolean isLuaProfilingEnabled() {
        return luaProfilingEnabled;
    }

    public long getSessionStartTime() {
        return sessionStartTime;
    }

    public void reset() {
        timingRegistry.clear();
        for (ProfilingPoint point : ProfilingPoint.values()) {
            timingRegistry.put(point, new TimingData(point.name()));
        }

        tickHistogram.reset();
        spikeLog.reset();
        sessionStartTime = System.currentTimeMillis();

        SubProfiler.getInstance().reset();
        LuaCallTracker.getInstance().reset();
        com.echo.lua.LuaGCProfiler.getInstance().reset();

        com.echo.fuse.PathfindingProfiler.getInstance().reset();
        com.echo.fuse.ZombieProfiler.getInstance().reset();
        com.echo.fuse.IsoGridProfiler.getInstance().reset();

        System.out.println("[Echo] Profiler stats RESET");
    }

    public SubProfiler getSubProfiler() {
        return SubProfiler.getInstance();
    }

    public Map<ProfilingPoint, TimingData> getTimingData() {
        return timingRegistry;
    }

    public TimingData getTimingData(ProfilingPoint point) {
        return timingRegistry.get(point);
    }

    public TickHistogram getTickHistogram() {
        return tickHistogram;
    }

    public SpikeLog getSpikeLog() {
        return spikeLog;
    }

    public MetricCollector getMetricCollector() {
        return metricCollector;
    }

    // --- Utility ---

    public int getCurrentStackDepth() {
        return getFrameStack().size();
    }

    public ProfilingPoint getCurrentPoint() {
        Deque<ProfilingFrame> stack = getFrameStack();
        if (stack.isEmpty())
            return null;
        return stack.peek().point;
    }

    public void printStatus() {
        System.out.println("\n[Echo] === Profiler Status ===");
        System.out.println("  Enabled: " + enabled);
        System.out.println("  Lua Profiling: " + luaProfilingEnabled);
        System.out.println("  Session Duration: " + getSessionDurationSeconds() + "s");
        System.out.println();

        for (ProfilingPoint point : ProfilingPoint.values()) {
            TimingData data = timingRegistry.get(point);
            if (data != null && data.getCallCount() > 0) {
                System.out.printf("  %-15s | calls: %,8d | avg: %6.2f ms | max: %6.2f ms%n",
                        point.getDisplayName(),
                        data.getCallCount(),
                        data.getAverageMicros() / 1000.0,
                        data.getMaxMicros() / 1000.0);
            }
        }
        System.out.println();
    }

    public long getSessionDurationSeconds() {
        if (sessionStartTime == 0)
            return 0;
        return (System.currentTimeMillis() - sessionStartTime) / 1000;
    }

    public long getSessionDurationMs() {
        if (sessionStartTime == 0)
            return 0;
        return System.currentTimeMillis() - sessionStartTime;
    }
}
