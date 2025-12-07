package com.echo.measure;

import com.echo.aggregate.TimingData;
import com.echo.aggregate.TickHistogram;
import com.echo.aggregate.SpikeLog;

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

    private static final EchoProfiler INSTANCE = new EchoProfiler();

    // 스레드별 프로파일링 스택
    private final ThreadLocal<Deque<ProfilingFrame>> frameStack = ThreadLocal.withInitial(ArrayDeque::new);

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

    private EchoProfiler() {
        // 모든 ProfilingPoint에 대한 TimingData 초기화
        for (ProfilingPoint point : ProfilingPoint.values()) {
            timingRegistry.put(point, new TimingData(point.name()));
        }
    }

    public static EchoProfiler getInstance() {
        return INSTANCE;
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
        frameStack.get().push(frame);

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
        frameStack.get().push(frame);

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

        Deque<ProfilingFrame> stack = frameStack.get();
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
            tickHistogram.addSample(elapsedMicros);
        }

        // 스파이크 로그에 기록 (임계값 초과 시)
        spikeLog.logSpike(elapsedMicros, point, frame.customLabel);
    }

    /**
     * 자동 종료를 위한 try-with-resources 지원
     */
    public ProfilingScope scope(ProfilingPoint point) {
        push(point);
        return new ProfilingScope(point, this);
    }

    public ProfilingScope scope(ProfilingPoint point, String label) {
        push(point, label);
        return new ProfilingScope(point, this);
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
        if (!enabled && resetStats) {
            reset();
        }
        this.enabled = true;
        if (sessionStartTime == 0) {
            this.sessionStartTime = System.currentTimeMillis();
        }
        System.out.println("[Echo] Profiler ENABLED" + (resetStats ? " (stats reset)" : ""));
    }

    public void disable() {
        this.enabled = false;
        System.out.println("[Echo] Profiler DISABLED");
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
        timingRegistry.values().forEach(TimingData::reset);
        tickHistogram.reset();
        spikeLog.reset();
        sessionStartTime = System.currentTimeMillis();
        System.out.println("[Echo] All timing data RESET");
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
        return frameStack.get().size();
    }

    /**
     * 현재 최상위 프레임 확인 (디버그용)
     */
    public ProfilingPoint getCurrentPoint() {
        Deque<ProfilingFrame> stack = frameStack.get();
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
     * try-with-resources용 스코프
     */
    public static class ProfilingScope implements AutoCloseable {
        private final ProfilingPoint point;
        private final EchoProfiler profiler;

        ProfilingScope(ProfilingPoint point, EchoProfiler profiler) {
            this.point = point;
            this.profiler = profiler;
        }

        @Override
        public void close() {
            profiler.pop(point);
        }
    }
}
