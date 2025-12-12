package com.echo.measure;

import com.echo.aggregate.TimingData;
import com.echo.aggregate.TickHistogram;
import com.echo.aggregate.SpikeLog;
import com.echo.lua.LuaCallTracker;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Echo Profiler - 계층적 프로파일링 엔진
 * 
 * Stack 기반 push/pop으로 중첩된 호출 구조를 추적합니다.
 * ThreadLocal을 사용하여 멀티스레드 환경에서도 안전합니다.
 */
public class EchoProfiler {

    private static EchoProfiler INSTANCE = new EchoProfiler();

    // ============================================================
    // Phase 1 최적화: Main Thread Fast-Path
    // ============================================================

    // 메인 스레드 (Fast-Path용)
    private static volatile Thread mainThread = null;

    // 메인 스레드 전용 스택 (ThreadLocal 우회)
    private final Deque<ProfilingFrame> mainThreadStack = new ArrayDeque<>();

    // ============================================================
    // Core Fields
    // ============================================================

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

    // 프로파일링 활성화 상태
    private volatile boolean enabled = false;

    // Lua 프로파일링 (On-Demand)
    private volatile boolean luaProfilingEnabled = false;

    // 세션 시작 시간
    private volatile long sessionStartTime = 0;

    // 의존성
    private final com.echo.config.EchoConfig config;

    /**
     * @deprecated Use Constructor Injection via PulseServiceLocator or
     *             PulseBootstrap
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
     * 
     * @param instance 테스트용 인스턴스 (null이면 기본 인스턴스로 리셋)
     */
    @com.pulse.api.VisibleForTesting
    static void setInstance(EchoProfiler instance) {
        INSTANCE = instance != null ? instance : new EchoProfiler();
    }

    /**
     * 테스트용 인스턴스 리셋.
     */
    @com.pulse.api.VisibleForTesting
    static void resetInstance() {
        INSTANCE = new EchoProfiler();
    }

    /**
     * 메인 스레드 설정 (게임 시작 시 호출)
     * ThreadLocal 우회를 통해 성능 향상
     */
    public static void setMainThread(Thread thread) {
        mainThread = thread;
        System.out.println("[Echo] Main thread set: " + thread.getName());
    }

    /**
     * 현재 스레드가 메인 스레드인지 확인
     */
    private boolean isMainThread() {
        return Thread.currentThread() == mainThread;
    }

    /**
     * 현재 스레드의 프레임 스택 획득 (Fast-Path 적용)
     */
    private Deque<ProfilingFrame> getFrameStack() {
        if (isMainThread()) {
            return mainThreadStack;
        }
        return frameStack.get();
    }

    /**
     * 현재 스레드의 스코프 풀 획득 (Fast-Path 적용)
     */
    private ProfilingScopePool getScopePool() {
        if (isMainThread()) {
            return mainThreadScopePool;
        }
        return scopePool.get();
    }

    // ============================================================
    // 핵심 API: push / pop
    // ============================================================

    /**
     * 프로파일링 구간 시작
     * 
     * @param point 측정 대상
     * @return 측정 ID (디버그용)
     */
    public long push(ProfilingPoint point) {
        if (!enabled)
            return -1;
        if (point.isLuaRelated() && !luaProfilingEnabled)
            return -1;

        ProfilingFrame frame = new ProfilingFrame(point, System.nanoTime());
        getFrameStack().push(frame);

        return frame.id;
    }

    /**
     * 프로파일링 구간 시작 (커스텀 라벨)
     * 
     * @param point       측정 대상
     * @param customLabel 세부 라벨 (예: 함수명)
     */
    public long push(ProfilingPoint point, String customLabel) {
        if (!enabled)
            return -1;
        if (point.isLuaRelated() && !luaProfilingEnabled)
            return -1;

        ProfilingFrame frame = new ProfilingFrame(point, customLabel, System.nanoTime());
        getFrameStack().push(frame);

        return frame.id;
    }

    /**
     * 프로파일링 구간 종료
     * 
     * @param point 종료할 측정 대상 (검증용)
     */
    public void pop(ProfilingPoint point) {
        if (!enabled)
            return;

        Deque<ProfilingFrame> stack = getFrameStack();
        if (stack.isEmpty()) {
            System.err.println("[Echo] Warning: Unmatched pop for " + point);
            return;
        }

        ProfilingFrame frame = stack.pop();

        // 검증: push/pop 매칭 확인
        if (frame.point != point) {
            System.err.println("[Echo] Warning: Mismatched push/pop - expected "
                    + frame.point + ", got " + point);
        }

        long elapsed = System.nanoTime() - frame.startTime;
        long elapsedMicros = elapsed / 1000;

        // TimingData에 샘플 추가
        TimingData data = timingRegistry.get(point);
        if (data != null) {
            data.addSample(elapsed, frame.customLabel);
        }

        // TICK 포인트인 경우 히스토그램에 기록
        if (point == ProfilingPoint.TICK) {
            if (config.isDebugMode() && !isMainThread()) {
                System.err.println("[Echo] CRITICAL: TICK recorded on non-main thread!");
            }
            tickHistogram.addSample(elapsedMicros);
        }

        // 스파이크 로그에 기록 (임계값 초과 시)
        spikeLog.logSpike(elapsedMicros, point, frame.customLabel);
    }

    /**
     * 자동 종료를 위한 try-with-resources 지원 (Zero-Allocation)
     */
    public ProfilingScope scope(ProfilingPoint point) {
        push(point);
        return getScopePool().acquire(point, this);
    }

    public ProfilingScope scope(ProfilingPoint point, String label) {
        push(point, label);
        return getScopePool().acquire(point, this);
    }

    // ============================================================
    // Phase 1: Low-Level Raw API (완전 Zero-Allocation)
    // ============================================================

    /**
     * 원시 프로파일링 시작 (객체 생성 없음)
     * 렌더 루프 등 극한 성능 구간용
     * 
     * @param point 측정 대상
     * @return 시작 시간 (나노초), -1이면 비활성화 상태
     */
    public long startRaw(ProfilingPoint point) {
        if (!enabled)
            return -1;
        if (point.isLuaRelated() && !luaProfilingEnabled)
            return -1;
        return System.nanoTime();
    }

    /**
     * 원시 프로파일링 종료 (객체 생성 없음)
     * 
     * @param point     측정 대상
     * @param startTime startRaw()에서 반환받은 시작 시간
     */
    public void endRaw(ProfilingPoint point, long startTime) {
        if (startTime < 0)
            return;

        long elapsed = System.nanoTime() - startTime;
        long elapsedMicros = elapsed / 1000;

        // TimingData에 직접 기록 (스택 없음)
        TimingData data = timingRegistry.get(point);
        if (data != null) {
            data.addSample(elapsed, null);
        }

        // TICK 포인트인 경우 히스토그램에 기록
        if (point == ProfilingPoint.TICK) {
            tickHistogram.addSample(elapsedMicros);
        }

        // 스파이크 로그에 기록
        spikeLog.logSpike(elapsedMicros, point, null);
    }

    /**
     * 원시 프로파일링 종료 (라벨 포함)
     */
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

    // ============================================================
    // 제어 API
    // ============================================================

    /**
     * 프로파일러 활성화 (새 세션 시 통계 초기화)
     */
    public void enable() {
        enable(true);
    }

    /**
     * 프로파일러 활성화
     * 
     * @param resetStats true: 기존 통계 초기화, false: 기존 통계 유지
     */
    public void enable(boolean resetStats) {
        // Config 검증 및 자동 수정 (Echo 0.9.0)
        config.sanitize();

        if (!enabled && resetStats) {
            reset();
        }
        this.enabled = true;
        if (sessionStartTime == 0) {
            this.sessionStartTime = System.currentTimeMillis();
        }
        FreezeDetector.getInstance().start();

        // Self-Validation 스케줄링 (Echo 0.9.0)
        com.echo.validation.SelfValidation.getInstance().scheduleValidation();

        // Fallback Tick 모니터링 시작 (Echo 0.9.0)
        com.echo.validation.FallbackTickEmitter.getInstance().startMonitoring();

        System.out.println("[Echo] Profiler ENABLED" + (resetStats ? " (stats reset)" : ""));
    }

    public void disable() {
        // Phase 2: 진행 중 스택 경고 및 정리
        int orphanedFrames = clearActiveStacks();
        if (orphanedFrames > 0) {
            System.err.println("[Echo] Warning: " + orphanedFrames + " orphaned frames cleared on disable");
        }

        this.enabled = false;
        FreezeDetector.getInstance().stop();

        // Self-Validation 종료 (Echo 0.9.0)
        com.echo.validation.SelfValidation.getInstance().shutdown();

        // Fallback Tick 종료 (Echo 0.9.0)
        com.echo.validation.FallbackTickEmitter.getInstance().stop();

        System.out.println("[Echo] Profiler DISABLED");
    }

    /**
     * 모든 활성 스택 정리 (Session 종료 시)
     * 
     * @return 정리된 프레임 수
     */
    private int clearActiveStacks() {
        int count = 0;

        // 메인 스레드 스택 정리
        count += mainThreadStack.size();
        mainThreadStack.clear();

        // 현재 스레드의 스택 정리 (ThreadLocal)
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

    /**
     * 모든 통계 초기화
     */
    public void reset() {
        // TimingData를 clear 후 다시 초기화 (getTimingData가 null을 반환하지 않도록)
        timingRegistry.clear();
        for (ProfilingPoint point : ProfilingPoint.values()) {
            timingRegistry.put(point, new TimingData(point.name()));
        }

        tickHistogram.reset();
        spikeLog.reset();
        sessionStartTime = System.currentTimeMillis();

        // SubProfiler 초기화 (Echo 1.0)
        SubProfiler.getInstance().reset();

        // Lua Profiler 초기화
        LuaCallTracker.getInstance().reset();

        // Lua GC Profiler 초기화 (Echo 1.0 Phase 2.2)
        com.echo.lua.LuaGCProfiler.getInstance().reset();

        // Fuse Deep Analysis 초기화 (Echo 1.0 Phase 4)
        com.echo.fuse.PathfindingProfiler.getInstance().reset();
        com.echo.fuse.ZombieProfiler.getInstance().reset();
        com.echo.fuse.IsoGridProfiler.getInstance().reset();

        System.out.println("[Echo] Profiler stats RESET");
    }

    /**
     * SubProfiler 접근 (Echo 1.0)
     */
    public SubProfiler getSubProfiler() {
        return SubProfiler.getInstance();
    }

    /**
     * 모든 TimingData 접근
     */
    public Map<ProfilingPoint, TimingData> getTimingData() {
        return timingRegistry;
    }

    public TimingData getTimingData(ProfilingPoint point) {
        return timingRegistry.get(point);
    }

    /**
     * 틱 히스토그램 접근
     */
    public TickHistogram getTickHistogram() {
        return tickHistogram;
    }

    /**
     * 스파이크 로그 접근
     */
    public SpikeLog getSpikeLog() {
        return spikeLog;
    }

    // ============================================================
    // 편의 메서드
    // ============================================================

    /**
     * 현재 스택 깊이 확인 (디버그용)
     */
    public int getCurrentStackDepth() {
        return getFrameStack().size();
    }

    /**
     * 현재 최상위 프레임 확인 (디버그용)
     */
    public ProfilingPoint getCurrentPoint() {
        Deque<ProfilingFrame> stack = getFrameStack();
        if (stack.isEmpty())
            return null;
        return stack.peek().point;
    }

    /**
     * 콘솔에 간단한 상태 출력
     */
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

    /**
     * 세션 지속 시간 (밀리초)
     */
    public long getSessionDurationMs() {
        if (sessionStartTime == 0)
            return 0;
        return System.currentTimeMillis() - sessionStartTime;
    }

    // ============================================================
    // 내부 클래스
    // ============================================================

    /**
     * 스택 프레임 - 진행 중인 측정 정보
     */
    private static class ProfilingFrame {
        private static final AtomicLong idCounter = new AtomicLong(0);

        final long id;
        final ProfilingPoint point;
        final String customLabel;
        final long startTime;

        ProfilingFrame(ProfilingPoint point, long startTime) {
            this.id = idCounter.incrementAndGet();
            this.point = point;
            this.customLabel = null;
            this.startTime = startTime;
        }

        ProfilingFrame(ProfilingPoint point, String customLabel, long startTime) {
            this.id = idCounter.incrementAndGet();
            this.point = point;
            this.customLabel = customLabel;
            this.startTime = startTime;
        }
    }

    /**
     * try-with-resources용 스코프 (Poolable)
     * 
     * 예외 안전성:
     * try-with-resources 블록 내에서 예외가 발생해도 close()가 자동 호출되어
     * pop()이 실행됩니다. 이로 인해 스택의 정합성이 유지됩니다.
     * 
     * 예시:
     * 
     * <pre>
     * try (var scope = profiler.scope(TICK)) {
     *     throw new RuntimeException(); // 예외 발생
     * } // 예외가 throw되어도 close() → pop() 자동 호출됨
     * </pre>
     */
    public static class ProfilingScope implements AutoCloseable {
        ProfilingPoint point;
        EchoProfiler profiler;
        ProfilingScopePool pool;

        void init(ProfilingPoint point, EchoProfiler profiler, ProfilingScopePool pool) {
            this.point = point;
            this.profiler = profiler;
            this.pool = pool;
        }

        @Override
        public void close() {
            profiler.pop(point);
            if (pool != null) {
                pool.release(this);
            }
        }
    }

    /**
     * ProfilingScope 객체 풀 (Zero-Allocation)
     * 스레드당 하나씩 유지되어 동기화 불필요
     */
    static class ProfilingScopePool {
        private static final int POOL_SIZE = 16;
        private final ProfilingScope[] pool = new ProfilingScope[POOL_SIZE];
        private int index = 0;

        ProfilingScopePool() {
            for (int i = 0; i < POOL_SIZE; i++) {
                pool[i] = new ProfilingScope();
            }
        }

        ProfilingScope acquire(ProfilingPoint point, EchoProfiler profiler) {
            ProfilingScope scope;
            if (index > 0) {
                scope = pool[--index];
            } else {
                // 풀이 비어있으면 새로 생성 (드문 경우)
                scope = new ProfilingScope();
            }
            scope.init(point, profiler, this);
            return scope;
        }

        void release(ProfilingScope scope) {
            if (index < POOL_SIZE) {
                pool[index++] = scope;
            }
            // 풀이 가득 차면 버림 (GC가 정리)
        }
    }
}
