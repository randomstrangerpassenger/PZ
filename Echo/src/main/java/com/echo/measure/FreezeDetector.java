package com.echo.measure;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Freeze/Stall Detector
 * 
 * 메인 스레드의 멈춤(Freeze) 현상을 감지하는 Watchdog 스레드입니다.
 * 설정된 임계값(기본 500ms) 이상 메인 스레드가 반응하지 않으면
 * 현재 상태(스택 트레이스, 메모리 등)를 캡처하여 원인을 분석합니다.
 * 
 * @since Echo 1.0
 */
public class FreezeDetector {

    private static final FreezeDetector INSTANCE = new FreezeDetector();

    // 기본 임계값 500ms
    private static final long FREEZE_THRESHOLD_MS = 500;

    // Watchdog 체크 주기 (100ms)
    private static final long CHECK_INTERVAL_MS = 100;

    // --- 스냅샷 데이터 구조 ---

    public static class FreezeSnapshot {
        public long timestamp;
        public long freezeDurationMs;
        public MemorySnapshot memory;
        public List<String> stackTrace;
        public boolean recovered;

        // Context Data
        public java.util.Map<String, Double> currentTickPhases;
        public java.util.Map<String, Double> activeSubTimings;
        public java.util.List<java.util.Map<String, Object>> topHeavyFunctions;

        public FreezeSnapshot(long freezeDurationMs, Thread mainThread) {
            this.timestamp = System.currentTimeMillis();
            this.freezeDurationMs = freezeDurationMs;
            this.memory = new MemorySnapshot();
            this.stackTrace = captureStackTrace(mainThread);
            this.recovered = false;

            // Capture Context
            captureContext();
        }

        private void captureContext() {
            // TickPhase state
            this.currentTickPhases = new java.util.LinkedHashMap<>();
            TickPhaseProfiler.getInstance().getCurrentTickPhaseMs()
                    .forEach((phase, ms) -> this.currentTickPhases.put(phase.getDisplayName(), ms));

            // Active SubTimings (what is currently running?)
            this.activeSubTimings = new java.util.LinkedHashMap<>();
            SubProfiler.getInstance().getActiveDurations()
                    .forEach((label, ms) -> this.activeSubTimings.put(label.getDisplayName(), ms));

            // Heavy Functions (Session)
            this.topHeavyFunctions = SubProfiler.getInstance().getHeavyFunctions(5);
        }

        private List<String> captureStackTrace(Thread thread) {
            List<String> trace = new ArrayList<>();
            if (thread == null)
                return trace;

            for (StackTraceElement elem : thread.getStackTrace()) {
                trace.add(elem.toString());
            }
            return trace;
        }
    }

    public static class MemorySnapshot {
        public long used;
        public long free;
        public long total;
        public long max;

        public MemorySnapshot() {
            Runtime rt = Runtime.getRuntime();
            this.total = rt.totalMemory();
            this.free = rt.freeMemory();
            this.max = rt.maxMemory();
            this.used = this.total - this.free;
        }
    }

    // --- 필드 ---

    private final AtomicLong lastTickTime = new AtomicLong(System.currentTimeMillis());
    private final AtomicBoolean isRunning = new AtomicBoolean(false);

    private Thread watchdogThread;
    private Thread mainThread;

    // 감지된 프리징 목록
    private final List<FreezeSnapshot> recentFreezes = new ArrayList<>();
    private final int MAX_HISTORY = 10;

    private FreezeDetector() {
        // Singleton
    }

    public static FreezeDetector getInstance() {
        return INSTANCE;
    }

    // --- 제어 API ---

    /**
     * 감지기 시작
     * EchoProfiler.enable() 시 호출
     */
    public synchronized void start() {
        if (isRunning.get())
            return;

        // 메인 스레드 참조 획득 (현재 스레드가 메인이라고 가정)
        // 주의: start()는 반드시 메인 스레드에서 호출되어야 함
        this.mainThread = Thread.currentThread();

        this.isRunning.set(true);
        this.lastTickTime.set(System.currentTimeMillis());

        this.watchdogThread = new Thread(this::watchdogLoop, "Echo-FreezeDetector");
        this.watchdogThread.setDaemon(true);
        this.watchdogThread.setPriority(Thread.MAX_PRIORITY); // 높은 우선순위
        this.watchdogThread.start();

        System.out.println("[Echo] FreezeDetector started");
    }

    /**
     * 감지기 종료
     */
    public synchronized void stop() {
        if (!isRunning.get())
            return;

        this.isRunning.set(false);
        if (watchdogThread != null) {
            watchdogThread.interrupt();
            watchdogThread = null;
        }
        System.out.println("[Echo] FreezeDetector stopped");
    }

    /**
     * 메인 스레드 생존 신고 (매 틱마다 호출)
     */
    public void tick() {
        if (!isRunning.get())
            return;

        // 첫 tick 호출 시 진짜 메인 스레드 캡처
        // (start()가 Monitor 스레드에서 호출되었을 수 있음)
        if (this.mainThread == null || !this.mainThread.getName().contains("LWJGL")) {
            Thread current = Thread.currentThread();
            if (current.getName().contains("LWJGL") || current.getName().contains("main") ||
                    current.getName().contains("Main") || this.mainThread == null) {
                this.mainThread = current;
                System.out.println("[Echo] FreezeDetector: Main thread captured: " + current.getName());
            }
        }

        lastTickTime.set(System.currentTimeMillis());

        // Self-Validation: freeze check heartbeat (Echo 0.9.0)
        com.echo.validation.SelfValidation.getInstance().freezeCheckHeartbeat();
    }

    // --- Watchdog 로직 ---

    private void watchdogLoop() {
        while (isRunning.get()) {
            try {
                Thread.sleep(CHECK_INTERVAL_MS);

                long now = System.currentTimeMillis();
                long last = lastTickTime.get();
                long elapsed = now - last;

                if (elapsed >= FREEZE_THRESHOLD_MS) {
                    onFreezeDetected(elapsed);

                    // 프리즈 상태가 지속되는 동안 반복 캡처 방지
                    // 다음 틱이 올 때까지 대기
                    // (단, 너무 오래 걸리면(5초) 다시 체크)
                    while (isRunning.get() && lastTickTime.get() == last) {
                        Thread.sleep(1000);
                        // 5초마다 갱신된 지속시간 업데이트 등은 여기서 가능
                    }
                }
            } catch (InterruptedException e) {
                break;
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    private void onFreezeDetected(long initialDuration) {
        // 프리즈 감지!
        System.err.println("[Echo] Freeze Detected! Main thread stalled for " + initialDuration + "ms");

        // 스냅샷 캡처
        FreezeSnapshot snapshot = new FreezeSnapshot(initialDuration, mainThread);

        synchronized (recentFreezes) {
            if (recentFreezes.size() >= MAX_HISTORY) {
                recentFreezes.remove(0);
            }
            recentFreezes.add(snapshot);
        }
    }

    // --- 조회 API ---

    public List<FreezeSnapshot> getRecentFreezes() {
        synchronized (recentFreezes) {
            return new ArrayList<>(recentFreezes);
        }
    }
}
