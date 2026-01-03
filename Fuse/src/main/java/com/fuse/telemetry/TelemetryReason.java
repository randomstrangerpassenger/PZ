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

    // --- IOGuard 관련 (v2.0) ---
    IO_GUARD_ACTIVE("Save/Load in progress"),
    IO_GUARD_RECOVERY("Post-IO recovery in progress"),
    IO_GUARD_TIMEOUT("IO timeout - forced exit"),

    // --- GC Pressure 관련 (v2.1) ---
    GC_PRESSURE_DIET("GC pressure high - budget reduced"),
    GC_PRESSURE_RECOVERING("GC pressure recovering"),
    GC_PRESSURE_POST_GC("Post-GC recovery in progress"),

    // --- Area 7: 경로탐색/충돌/물리 (v2.2) ---
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
