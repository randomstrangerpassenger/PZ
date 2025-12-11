package com.echo.validation;

import com.echo.measure.TickPhaseProfiler.TickPhase;
import com.pulse.api.TickContract;
import java.util.Map;
import java.util.LinkedHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Pulse-Echo API Contract Verifier (Phase 4)
 * 
 * Verifies that Pulse is sending events in the expected order and format.
 * - Phase Order: Update -> Render (or specific sequence)
 * - Tick Consistency: DeltaTime sanity check
 * - Duplicate Detection: Zero deltaTime indicates duplicate events
 * - Thread Contention: Detects multi-thread access in multiplayer
 * 
 * @since Echo 0.9 - Enhanced deltaTime anomaly detection, thread safety,
 *        Fuse/Nerve API
 */
public class PulseContractVerifier {

    private static final PulseContractVerifier INSTANCE = new PulseContractVerifier();

    // Contract State
    private TickPhase lastPhase = null;
    @SuppressWarnings("unused") // Reserved for phase timing analysis
    private long lastPhaseTime = 0;
    private final AtomicBoolean contractViolated = new AtomicBoolean(false);

    // Violations
    private final AtomicLong orderViolations = new AtomicLong(0);
    private final AtomicLong invalidDeltaTimes = new AtomicLong(0);
    private final AtomicLong zeroDeltaTimes = new AtomicLong(0);
    private final AtomicLong largeDeltaTimes = new AtomicLong(0);
    private final AtomicLong duplicateEvents = new AtomicLong(0);

    // Last reported violation
    private volatile String lastViolationMessage = null;

    // Duplicate detection
    private long lastTickNanos = 0;

    // v0.9: TickContract 기반 임계값 (단위: seconds)
    private static final float LARGE_DELTA_THRESHOLD = TickContract.MAX_REASONABLE_DELTA_MS / 1000f;
    private static final float MAX_REASONABLE_DELTA = TickContract.MAX_ABSOLUTE_DELTA_MS / 1000f;

    // v0.9: Tick 누락 감지 (FallbackTickEmitter용)
    private volatile boolean tickMissing = false;
    private volatile long lastTickReceivedTime = 0;

    // v0.9: Thread contention detection (multiplayer support)
    private volatile long expectedThreadId = -1;
    private final AtomicLong threadContentions = new AtomicLong(0);
    private static final int MAX_THREAD_WARNINGS = 3;

    // v0.9: Scheduler order verification
    private volatile boolean schedulerTickedThisCycle = false;

    private PulseContractVerifier() {
    }

    public static PulseContractVerifier getInstance() {
        return INSTANCE;
    }

    private final AtomicLong phaseSignalCount = new AtomicLong(0);
    private final AtomicLong gameTickCount = new AtomicLong(0);

    public void onPhaseStart(TickPhase phase) {
        phaseSignalCount.incrementAndGet();
        lastPhase = phase;
        lastPhaseTime = System.nanoTime();
    }

    /**
     * Called on each game tick. Performs comprehensive deltaTime validation.
     * 
     * @param deltaTime Time since last tick in seconds
     */
    public void onGameTick(float deltaTime) {
        gameTickCount.incrementAndGet();
        lastTickReceivedTime = System.currentTimeMillis();
        tickMissing = false;
        long currentNanos = System.nanoTime();

        // Check 1: Zero deltaTime (indicates duplicate event)
        if (deltaTime == 0) {
            if (zeroDeltaTimes.incrementAndGet() == 1) {
                recordViolation("Zero deltaTime detected (possible duplicate event)");
            }
        }

        // Check 2: Large deltaTime (indicates stall or lag spike)
        if (deltaTime > LARGE_DELTA_THRESHOLD && deltaTime <= MAX_REASONABLE_DELTA) {
            if (largeDeltaTimes.incrementAndGet() <= 3) { // Only log first 3
                recordViolation("Large deltaTime: " + String.format("%.1f", deltaTime * 1000) + "ms (possible stall)");
            }
        }

        // Check 3: Invalid deltaTime (negative or extremely large)
        if (deltaTime < 0 || deltaTime > MAX_REASONABLE_DELTA) {
            if (invalidDeltaTimes.incrementAndGet() == 1) {
                recordViolation("Invalid deltaTime: " + deltaTime + "s");
            }
        }

        // Check 4: Duplicate event detection via timestamp (TickContract 기준)
        if (lastTickNanos > 0) {
            long elapsed = currentNanos - lastTickNanos;
            if (elapsed < TickContract.DUPLICATE_THRESHOLD_NS && elapsed >= 0) {
                if (duplicateEvents.incrementAndGet() == 1) {
                    recordViolation("Duplicate tick event detected (elapsed: " + (elapsed / 1000) + "µs)");
                }
            }
        }
        lastTickNanos = currentNanos;

        // Check 5: Thread contention detection (v0.9 multiplayer support)
        long currentThread = Thread.currentThread().getId();
        if (expectedThreadId == -1) {
            expectedThreadId = currentThread;
        } else if (expectedThreadId != currentThread) {
            long count = threadContentions.incrementAndGet();
            if (count <= MAX_THREAD_WARNINGS) {
                recordViolation("Thread contention: expected thread " + expectedThreadId
                        + ", got " + currentThread + " (may cause race conditions)");
            }
        }

        // Reset scheduler flag for next cycle
        schedulerTickedThisCycle = false;
    }

    /**
     * Called by PulseScheduler to indicate it has ticked this cycle.
     * Used to verify PulseScheduler -> Echo TickProfiler order.
     */
    public void onSchedulerTick() {
        schedulerTickedThisCycle = true;
    }

    /**
     * Check if PulseScheduler ticked before Echo received events this cycle.
     * Used to verify execution order is correct.
     */
    public boolean isSchedulerOrderCorrect() {
        return schedulerTickedThisCycle;
    }

    public void onPhaseEnd(TickPhase phase) {
        if (lastPhase != phase) {
            recordViolation("Phase Mismatch: Ended " + phase + " but expected " + lastPhase);
        }
        lastPhase = null;
    }

    public boolean isPhaseSignalMissing() {
        // If we have many ticks (>60) but NO phase signals, something is wrong.
        return gameTickCount.get() > 60 && phaseSignalCount.get() == 0;
    }

    private void recordViolation(String message) {
        contractViolated.set(true);
        lastViolationMessage = message;
        System.err.println("[Echo] Pulse Contract Violation: " + message);
    }

    /**
     * Reset all counters (for testing)
     */
    public void reset() {
        contractViolated.set(false);
        orderViolations.set(0);
        invalidDeltaTimes.set(0);
        zeroDeltaTimes.set(0);
        largeDeltaTimes.set(0);
        duplicateEvents.set(0);
        phaseSignalCount.set(0);
        gameTickCount.set(0);
        lastTickNanos = 0;
        lastViolationMessage = null;
        lastPhase = null;
        tickMissing = false;
        lastTickReceivedTime = 0;
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();
        // v0.9: TickContract 버전 포함
        map.put("pulse_contract_version", TickContract.VERSION);
        map.put("tick_contract_valid", !contractViolated.get());
        map.put("status", contractViolated.get() ? "VIOLATED" : "OK");
        map.put("order_violations", orderViolations.get());
        map.put("invalid_delta_times", invalidDeltaTimes.get());
        map.put("zero_delta_times", zeroDeltaTimes.get());
        map.put("large_delta_times", largeDeltaTimes.get());
        map.put("duplicate_events", duplicateEvents.get());
        map.put("thread_contentions", threadContentions.get());
        map.put("missing_phase_data", isPhaseSignalMissing());
        map.put("tick_missing", tickMissing);
        map.put("total_ticks", gameTickCount.get());
        map.put("phase_signals", phaseSignalCount.get());
        if (lastViolationMessage != null) {
            map.put("last_violation", lastViolationMessage);
        }
        return map;
    }

    // ═══════════════════════════════════════════════════════════════
    // v0.9: Fuse/Nerve Integration API
    // ═══════════════════════════════════════════════════════════════

    /**
     * Get contract status for Fuse/Nerve debug display.
     * 
     * @return "OK", "WARNING", or "VIOLATED"
     */
    public String getStatusForDisplay() {
        if (contractViolated.get())
            return "VIOLATED";
        if (threadContentions.get() > 0 || largeDeltaTimes.get() > 0)
            return "WARNING";
        return "OK";
    }

    /**
     * Get total violation count for Fuse/Nerve display.
     */
    public long getTotalViolationCount() {
        return orderViolations.get() + invalidDeltaTimes.get() + zeroDeltaTimes.get()
                + largeDeltaTimes.get() + duplicateEvents.get() + threadContentions.get();
    }

    /**
     * Get last violation message for Fuse/Nerve display.
     */
    public String getLastViolation() {
        return lastViolationMessage;
    }

    /**
     * Check if contract is currently violated.
     */
    public boolean isViolated() {
        return contractViolated.get();
    }

    // ═══════════════════════════════════════════════════════════════
    // v0.9: Tick 누락 감지 API (FallbackTickEmitter용)
    // ═══════════════════════════════════════════════════════════════

    /**
     * Tick이 누락되었는지 확인.
     * FallbackTickEmitter에서 활성화 조건으로 사용.
     */
    public boolean isTickMissing() {
        if (lastTickReceivedTime == 0) {
            return false; // 아직 시작 안됨
        }
        long elapsed = System.currentTimeMillis() - lastTickReceivedTime;
        // 3초 이상 Tick이 없으면 누락으로 판정
        if (elapsed > TickContract.FALLBACK_ACTIVATION_DELAY_MS) {
            tickMissing = true;
            return true;
        }
        return false;
    }

    /**
     * Tick 누락 상태 수동 설정 (테스트용)
     */
    public void setTickMissing(boolean missing) {
        this.tickMissing = missing;
    }
}
