package com.fuse.telemetry;

/**
 * Telemetry Reason Codes.
 * 
 * Fuse 개입 이유를 추적 가능하게 기록합니다.
 * 상세 성능 로그가 아닌 reason 코드(enum) + 간단한 카운터만 사용.
 * 
 * @since Fuse 1.1
 */
public enum TelemetryReason {

    // --- Throttle 관련 ---
    THROTTLE_WINDOW_EXCEEDED("last_1s.max > 33.33ms"),
    THROTTLE_AVG_HIGH("last_5s.avg > 20ms"),

    // --- Adaptive Gate 관련 (v2.5) ---
    ADAPTIVE_GATE_ACTIVATED("Gate activated - entering intervention mode"),
    ADAPTIVE_GATE_PASSTHROUGH("Gate passthrough - zero overhead"),

    // --- Bundle C: Sustained Early Exit (v2.6) ---
    SUSTAINED_EARLY_EXIT("forced cooldown due to sustained ACTIVE"),

    // --- Budget 관련 (v2.5) ---
    BUDGET_SOFT_LIMIT("Fuse overhead soft limit exceeded (0.5ms)"),
    BUDGET_HARD_LIMIT("Fuse overhead hard limit - cutoff (2.0ms)"),
    BUDGET_PRESSURE_SKIP("Budget pressure - secondary step skipped"),

    // --- Dedup 관련 (v2.5) ---
    DUPLICATE_SKIPPED("Duplicate call skipped this tick"),

    // --- Panic 관련 ---
    PANIC_WINDOW_SPIKES("100ms+ spikes x2 in 5s"),
    RECOVERING_GRADUAL("Gradual recovery in progress"),

    // --- Guard 관련 ---
    GUARD_VEHICLE("Vehicle guard active"),
    GUARD_STREAMING("Streaming guard active"),

    // --- Failsoft 관련 ---
    FAILSOFT_ERROR("Intervention disabled due to errors"),

    // --- Governor 관련 ---
    GOVERNOR_CUTOFF("Budget exceeded, cutoff triggered"),

    /*
     * === LEGACY SECTION (v2.3) ===
     * The following reason codes are no longer triggered.
     * Kept for binary/log compatibility. Do not remove.
     */

    // --- IOGuard (legacy, never triggered) ---
    IO_GUARD_ACTIVE("Save/Load in progress"),
    IO_GUARD_RECOVERY("Post-IO recovery in progress"),
    IO_GUARD_TIMEOUT("IO timeout - forced exit"),

    // --- GC Pressure (legacy, never triggered) ---
    GC_PRESSURE_DIET("GC pressure high - budget reduced"),
    GC_PRESSURE_RECOVERING("GC pressure recovering"),
    GC_PRESSURE_POST_GC("Post-GC recovery in progress"),

    // --- Area 7: 경로탐색/충돌/물리 (v2.2) ---
    DEFERRED_EXPIRED("Deferred request expired (>1 tick)"),
    PATH_REQUEST_DEFERRED("Path request deferred to next tick"),
    PATH_REQUEST_DROPPED("Path request dropped - queue overflow"),
    PHYSICS_SANITY_FAILURE("Physics sanity check failed - state restored");

    public final String description;

    TelemetryReason(String description) {
        this.description = description;
    }

    @Override
    public String toString() {
        return name() + ": " + description;
    }
}
