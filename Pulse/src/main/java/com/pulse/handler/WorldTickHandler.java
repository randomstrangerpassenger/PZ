package com.pulse.handler;

import com.pulse.api.log.PulseLogger;

/**
 * 월드 틱 상태 관리 핸들러.
 * 
 * <p>
 * IsoWorldMixin에서 분리된 틱 관리 로직을 캡슐화합니다.
 * 이벤트 발행은 Mixin에서 수행하고, 이 클래스는 상태 관리와 계산만 담당합니다.
 * </p>
 * 
 * <h3>책임:</h3>
 * <ul>
 * <li>틱 카운트 관리</li>
 * <li>틱 타이밍 계산 (duration, deltaTime)</li>
 * <li>첫 틱 감지</li>
 * <li>PulseMetrics 연동</li>
 * </ul>
 * 
 * @since Pulse 1.6 - Extracted from IsoWorldMixin
 */
public final class WorldTickHandler {

    private static final String LOG = "Pulse/WorldTickHandler";

    // Singleton instance
    private static final WorldTickHandler INSTANCE = new WorldTickHandler();

    // ═══════════════════════════════════════════════════════════════
    // State
    // ═══════════════════════════════════════════════════════════════

    private long tickCount = 0;
    private long lastTickTime = System.nanoTime();
    private long currentTickStartNanos = -1;
    private boolean firstTickProcessed = false;
    private boolean installed = false;

    private WorldTickHandler() {
        // Singleton
    }

    /**
     * Get singleton instance.
     */
    public static WorldTickHandler getInstance() {
        return INSTANCE;
    }

    // ═══════════════════════════════════════════════════════════════
    // Lifecycle
    // ═══════════════════════════════════════════════════════════════

    /**
     * Install handler (called at world load).
     */
    public synchronized void install() {
        if (installed) {
            return;
        }
        reset();
        installed = true;
        PulseLogger.debug(LOG, "Installed");
    }

    /**
     * Reset all state (for world reload).
     */
    public synchronized void reset() {
        tickCount = 0;
        lastTickTime = System.nanoTime();
        currentTickStartNanos = -1;
        firstTickProcessed = false;
        PulseLogger.debug(LOG, "State reset");
    }

    // ═══════════════════════════════════════════════════════════════
    // Tick Processing
    // ═══════════════════════════════════════════════════════════════

    /**
     * Called at IsoWorld.update() HEAD.
     * 
     * <p>
     * Records tick start time and determines if this is the first tick.
     * Caller (Mixin) is responsible for posting events.
     * </p>
     * 
     * @return Result containing firstTick flag and timing info
     */
    public TickStartResult onUpdateStart() {
        boolean isFirstTick = !firstTickProcessed;

        if (isFirstTick) {
            tickCount = 0;
            lastTickTime = System.nanoTime();
            firstTickProcessed = true;
            PulseLogger.debug(LOG, "First tick detected");
        }

        currentTickStartNanos = System.nanoTime();

        // Notify PulseMetrics (Echo integration)
        com.pulse.api.PulseMetrics.onTickStart();

        return new TickStartResult(isFirstTick, currentTickStartNanos, tickCount + 1);
    }

    /**
     * Called at IsoWorld.update() RETURN.
     * 
     * <p>
     * Calculates tick duration and delta time.
     * Caller (Mixin) is responsible for posting events and calling scheduler.
     * </p>
     * 
     * @return Result containing tick count, duration, and delta time
     */
    public TickEndResult onUpdateEnd() {
        long currentTime = System.nanoTime();

        // Calculate duration
        long tickDurationNanos = currentTime - currentTickStartNanos;

        // Notify PulseMetrics
        com.pulse.api.PulseMetrics.onTickEnd(tickDurationNanos);

        // Calculate delta time
        float deltaTime = (currentTime - lastTickTime) / 1_000_000_000.0f;
        lastTickTime = currentTime;

        // Increment tick count
        tickCount++;

        // Periodic debug logging
        if (tickCount % 1000 == 0) {
            PulseLogger.debug(LOG, "Tick #{}, deltaTime={}", tickCount, String.format("%.4f", deltaTime));
        }

        currentTickStartNanos = -1;

        return new TickEndResult(tickCount, tickDurationNanos, deltaTime);
    }

    // ═══════════════════════════════════════════════════════════════
    // Accessors
    // ═══════════════════════════════════════════════════════════════

    /**
     * Get current tick count.
     */
    public long getTickCount() {
        return tickCount;
    }

    /**
     * Get current tick start time in nanoseconds.
     * Returns -1 if not in an active tick.
     */
    public long getCurrentTickStartNanos() {
        return currentTickStartNanos;
    }

    /**
     * Whether the first tick has been processed.
     */
    public boolean isFirstTickProcessed() {
        return firstTickProcessed;
    }

    /**
     * Whether the handler is installed.
     */
    public boolean isInstalled() {
        return installed;
    }
}
