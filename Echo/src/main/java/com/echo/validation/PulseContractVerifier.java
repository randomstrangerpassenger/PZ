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

    // Violations (진짜 계약 파손)
    private final AtomicLong orderViolations = new AtomicLong(0);
    private final AtomicLong invalidDeltaTimes = new AtomicLong(0);
    private final AtomicLong zeroDeltaTimes = new AtomicLong(0);
    private final AtomicLong duplicateEvents = new AtomicLong(0);

    // Stall Events (환경 이벤트 - 계약 파손 아님)
    private final AtomicLong largeDeltaTimes = new AtomicLong(0);
    private volatile String lastStallMessage = null;

    // v0.9: Burst tick allowance for MP catch-up (server sync)
    private int burstTickCount = 0;
    private static final int MAX_BURST_ALLOWANCE = 5;

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

        // Check 1: Zero deltaTime with burst allowance (v0.9 MP catch-up fix)
        if (deltaTime <= 0.000001f) {
            burstTickCount++;
            if (burstTickCount > MAX_BURST_ALLOWANCE) {
                if (zeroDeltaTimes.incrementAndGet() == 1) {
                    recordViolation("Excessive zero-delta ticks (Limit: " + MAX_BURST_ALLOWANCE + ")");
                }
            }
            // Within burst allowance - treat as normal server sync
        } else {
            burstTickCount = 0; // Reset burst counter on normal tick
        }

        // Check 2: Large deltaTime (indicates stall or lag spike)
        // v1.1: 스톨은 환경 이벤트로 분리 - 계약 파손으로 처리하지 않음
        if (deltaTime > LARGE_DELTA_THRESHOLD && deltaTime <= MAX_REASONABLE_DELTA) {
            if (largeDeltaTimes.incrementAndGet() <= 3) { // Only log first 3
                recordStallEvent("Large deltaTime: " + String.format("%.1f", deltaTime * 1000) + "ms (possible stall)");
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
     * 스톨 이벤트 기록 (환경 이벤트 - 계약 파손 아님).
     * v1.1: 스톨은 WARNING으로만 표시, VIOLATED 상태로 전환하지 않음.
     */
    private void recordStallEvent(String message) {
        lastStallMessage = message;
        System.out.println("[Echo] Stall Event: " + message);
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
        burstTickCount = 0;
        lastTickReceivedTime = 0;
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();
        // v0.9: TickContract 버전 포함
        map.put("pulse_contract_version", TickContract.VERSION);
        map.put("tick_contract_valid", !contractViolated.get());
        map.put("status", getStatusForDisplay()); // v1.1: use getStatusForDisplay()

        // 진짜 계약 파손
        map.put("order_violations", orderViolations.get());
        map.put("invalid_delta_times", invalidDeltaTimes.get());
        map.put("zero_delta_times", zeroDeltaTimes.get());
        map.put("duplicate_events", duplicateEvents.get());
        map.put("thread_contentions", threadContentions.get());

        // v1.1: 스톨 이벤트 (환경 이벤트 - 별도 카테고리)
        map.put("stall_events", largeDeltaTimes.get());
        if (lastStallMessage != null) {
            map.put("last_stall", lastStallMessage);
        }

        map.put("burst_tick_allowance", MAX_BURST_ALLOWANCE);
        map.put("current_burst_count", burstTickCount);
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
     * v1.1: 스톨은 WARNING, 진짜 계약 파손만 VIOLATED
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
     * v1.1: stall_events 제외 (환경 이벤트는 계약 파손 아님)
     */
    public long getTotalViolationCount() {
        return orderViolations.get() + invalidDeltaTimes.get() + zeroDeltaTimes.get()
                + duplicateEvents.get() + threadContentions.get();
    }

    /**
     * Get stall event count (환경 이벤트).
     */
    public long getStallEventCount() {
        return largeDeltaTimes.get();
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
    // v0.9.1: Tick 누락 감지 API (개선됨)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 리포트용: 세션 중 마지막으로 확인된 tick_missing 상태 반환
     * 
     * v0.9.1: 리포트 생성 시점이 아닌 세션 중 상태를 반환하여
     * 게임 종료 후 false positive 방지
     * 
     * @return 세션 중 tick 누락이 발생했는지 여부
     */
    public boolean isTickMissing() {
        // 세션 중 마지막으로 저장된 상태 반환 (false positive 방지)
        return tickMissing;
    }

    /**
     * 실시간 체크: 현재 tick이 누락되었는지 확인
     * FallbackTickEmitter에서 활성화 조건으로 사용.
     * 
     * @return 현재 시점에서 tick 누락 여부
     */
    public boolean checkTickMissingNow() {
        if (lastTickReceivedTime == 0) {
            return false; // 아직 시작 안됨
        }
        long elapsed = System.currentTimeMillis() - lastTickReceivedTime;
        // 3초 이상 Tick이 없으면 누락으로 판정
        if (elapsed > TickContract.FALLBACK_ACTIVATION_DELAY_MS) {
            tickMissing = true; // 세션 상태 업데이트
            return true;
        }
        return false;
    }

    /**
     * Real tick 수신 시 tick_missing 상태 리셋
     * onGameTick()에서 자동 호출됨
     */
    public void onRealTickReceived() {
        tickMissing = false;
        lastTickReceivedTime = System.currentTimeMillis();
    }

    /**
     * Tick 누락 상태 수동 설정 (테스트용)
     */
    public void setTickMissing(boolean missing) {
        this.tickMissing = missing;
    }
}
