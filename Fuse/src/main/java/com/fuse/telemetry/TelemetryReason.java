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
    GOVERNOR_CUTOFF("Budget exceeded, cutoff triggered");

    public final String description;

    TelemetryReason(String description) {
        this.description = description;
    }

    @Override
    public String toString() {
        return name() + ": " + description;
    }
}
