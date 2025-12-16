package com.echo.validation;

import com.echo.config.EchoConfig;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;

/**
 * FallbackTickEmitter - 디버그 전용 Fallback Tick 생성기
 * 
 * Pulse Hook이 완전히 누락된 경우에만 작동하며,
 * Echo 파이프라인이 정상인지 검증하기 위한 **최소한의 데이터**를 생성합니다.
 * 
 * ⚠️ 중요: 이 fallback tick은 실제 게임 성능과 관련이 없습니다!
 * - 성능 분석(histogram, P95/P99)에서 **절대 사용되지 않음**
 * - `used_fallback_ticks: true` 플래그로 명확히 라벨링
 * - 기본값 OFF (`EchoConfig.allowFallbackTicks = false`)
 * 
 * @since Echo 0.9.0
 */
public class FallbackTickEmitter {

    private static final FallbackTickEmitter INSTANCE = new FallbackTickEmitter();

    /** Fallback 활성화 대기 시간 (밀리초) - 실제 tick hook을 기다림 */
    private static final long ACTIVATION_DELAY_MS = 3000;

    private ScheduledExecutorService scheduler;
    private ScheduledFuture<?> fallbackTask;

    private final AtomicBoolean fallbackActive = new AtomicBoolean(false);
    private final AtomicLong fallbackTickCount = new AtomicLong(0);

    /**
     * v0.9.1: Fallback이 히스토그램 데이터를 오염시켰는지 추적
     * 이전 버전에서는 fallback tick이 히스토그램에 기록됐음
     * 이 플래그는 레거시 오염 감지용 (새 버전에서는 항상 false)
     */
    private final AtomicBoolean histogramContaminated = new AtomicBoolean(false);

    private FallbackTickEmitter() {
    }

    public static FallbackTickEmitter getInstance() {
        return INSTANCE;
    }

    /**
     * Real tick 수신 시 호출 - Fallback 자동 비활성화
     * 
     * TickProfiler.recordTickDuration()에서 호출됨.
     * Real tick이 들어오면 fallback은 더 이상 필요 없음.
     * 
     * @since Echo 0.9.1
     */
    public void onRealTickReceived() {
        if (fallbackActive.compareAndSet(true, false)) {
            // Fallback task 중지
            if (fallbackTask != null) {
                fallbackTask.cancel(false);
                fallbackTask = null;
            }
            System.out.println("[Echo/FallbackTick] Real tick received - Fallback DEACTIVATED after "
                    + fallbackTickCount.get() + " fallback ticks");
        }
    }

    /**
     * Fallback 모니터링 시작
     * 지정된 시간 후 tick hook이 없으면 fallback 활성화
     */
    public synchronized void startMonitoring() {
        EchoConfig config = EchoConfig.getInstance();

        // Config에서 허용하지 않으면 즉시 반환
        if (!config.isAllowFallbackTicks()) {
            System.out.println("[Echo/FallbackTick] Fallback ticks disabled (Config.allowFallbackTicks = false)");
            return;
        }

        // 이미 실행 중이면 반환
        if (scheduler != null && !scheduler.isShutdown()) {
            return;
        }

        scheduler = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r, "Echo-FallbackTickEmitter");
            t.setDaemon(true);
            return t;
        });

        // 지정된 시간 후 tick hook 상태 확인
        scheduler.schedule(this::checkAndActivateFallback, ACTIVATION_DELAY_MS, TimeUnit.MILLISECONDS);
        System.out.println("[Echo/FallbackTick] Monitoring started (will check in " + ACTIVATION_DELAY_MS + "ms)");
    }

    /**
     * Tick hook 상태 확인 및 필요 시 fallback 활성화
     * 
     * v0.9.1: 강화된 조건 - heartbeat == 0 AND phase_start_count == 0
     * 둘 다 0이어야 진짜 hook 누락으로 판정
     */
    private int retryCount = 0;
    private static final int MAX_RETRIES = 3;

    private void checkAndActivateFallback() {
        SelfValidation validation = SelfValidation.getInstance();
        long heartbeat = validation.getHeartbeatCount();
        long phaseStartCount = validation.getPhaseStartCount();

        // v0.9.1: 강화된 조건 - tick과 phase 둘 다 없어야 fallback 활성화
        boolean noTickHook = heartbeat == 0;
        boolean noPhaseHook = phaseStartCount == 0;

        if (noTickHook && noPhaseHook) {
            retryCount++;
            if (retryCount >= MAX_RETRIES) {
                // 3번 시도 후에도 둘 다 0이면 강제 활성화
                System.err.println("[Echo/FallbackTick] ⚠️ No tick/phase hook detected after "
                        + (ACTIVATION_DELAY_MS + retryCount * 1000) + "ms!");
                System.err.println("[Echo/FallbackTick] ⚠️ Starting FALLBACK tick emitter");
                System.err.println("[Echo/FallbackTick] ⚠️ WARNING: This data is for PIPELINE TESTING ONLY!");
                activateFallback();
            } else {
                System.out.println("[Echo/FallbackTick] Heartbeat=0, phase=0, retry " + retryCount + "/" + MAX_RETRIES);
                scheduler.schedule(this::checkAndActivateFallback, 1000, TimeUnit.MILLISECONDS);
            }
        } else {
            System.out.println(
                    "[Echo/FallbackTick] Hook detected (heartbeat=" + heartbeat + ", phase=" + phaseStartCount
                            + "). No fallback needed.");
        }
    }

    /**
     * Fallback tick 생성 활성화
     */
    private void activateFallback() {
        if (fallbackActive.getAndSet(true)) {
            return; // 이미 활성화됨
        }

        // Config에 fallback 사용 표시
        EchoConfig config = EchoConfig.getInstance();
        config.setUsedFallbackTicks(true);

        // Configurable interval로 fallback tick 생성 (default: 200ms)
        long intervalMs = config.getFallbackTickIntervalMs();
        System.out.println("[Echo/FallbackTick] Using interval: " + intervalMs + "ms");

        fallbackTask = scheduler.scheduleAtFixedRate(
                this::emitFallbackTick,
                0,
                intervalMs,
                TimeUnit.MILLISECONDS);
    }

    /**
     * Fallback tick 발생
     * 
     * v0.9.1: 히스토그램에는 기록하지 않음 (데이터 오염 방지)
     * Fallback tick은 파이프라인 검증용으로만 사용
     */
    private void emitFallbackTick() {
        fallbackTickCount.incrementAndGet();

        // SelfValidation heartbeat 증가 (파이프라인 검증용)
        SelfValidation.getInstance().tickHeartbeat();

        // SessionManager.onTick() 호출 - 세션 자동 시작 및 데이터 수집 마킹
        com.echo.session.SessionManager.getInstance().onTick();

        // v0.9.1: 히스토그램에는 기록하지 않음!
        // 이전 버전에서는 200ms 고정값이 기록되어 P95/P99를 오염시켰음
        // 이제 fallback tick은 heartbeat/session 유지용으로만 사용

        // 디버그 로그 (매 50회마다)
        if (fallbackTickCount.get() % 50 == 0) {
            System.out.println(
                    "[Echo/FallbackTick] " + fallbackTickCount.get() + " fallback ticks (pipeline only, no histogram)");
        }
    }

    /**
     * Fallback 모니터링 중지
     */
    public synchronized void stop() {
        if (fallbackTask != null) {
            fallbackTask.cancel(false);
            fallbackTask = null;
        }

        if (scheduler != null && !scheduler.isShutdown()) {
            scheduler.shutdownNow();
            scheduler = null;
        }

        if (fallbackActive.get()) {
            System.out.println("[Echo/FallbackTick] Stopped after " + fallbackTickCount.get() + " fallback ticks");
        }

        fallbackActive.set(false);
    }

    /**
     * 리셋
     */
    public void reset() {
        stop();
        fallbackTickCount.set(0);
    }

    // --- 조회 API ---

    public boolean isFallbackActive() {
        return fallbackActive.get();
    }

    public long getFallbackTickCount() {
        return fallbackTickCount.get();
    }

    /**
     * v0.9.1: 히스토그램 데이터가 fallback tick으로 오염됐는지 확인
     * 
     * 새 버전(0.9.1+)에서는 fallback tick이 히스토그램에 기록되지 않으므로
     * 항상 false를 반환합니다. 이 플래그는 레거시 호환성과
     * 명시적인 "오염 없음" 확인을 위해 유지됩니다.
     * 
     * @return true if histogram was contaminated by fallback ticks (legacy only)
     */
    public boolean isHistogramContaminated() {
        return histogramContaminated.get();
    }
}
