package com.pulse.api;

/**
 * Tick timing contract constants.
 * 
 * Defines timing thresholds and validation parameters for tick events.
 * Used by Echo's PulseContractVerifier to validate Pulse tick events.
 * 
 * @since Pulse 1.1
 */
public final class TickContract {

    private TickContract() {
    } // Utility class

    /**
     * Contract version for compatibility checking.
     */
    public static final String VERSION = "1.0";

    /**
     * Maximum reasonable delta time in milliseconds.
     * DeltaTime above this is considered a potential stall or lag spike.
     */
    public static final float MAX_REASONABLE_DELTA_MS = 500.0f;

    /**
     * Maximum absolute delta time in milliseconds.
     * DeltaTime above this is considered invalid.
     */
    public static final float MAX_ABSOLUTE_DELTA_MS = 5000.0f;

    /**
     * Threshold in nanoseconds below which two events are considered duplicates.
     * Default: 100 microseconds (100,000 nanoseconds).
     */
    public static final long DUPLICATE_THRESHOLD_NS = 100_000L;

    /**
     * Time in milliseconds after which tick missing fallback activates.
     * Default: 3000ms (3 seconds).
     */
    public static final long FALLBACK_ACTIVATION_DELAY_MS = 3000L;

    /**
     * Target tick time in milliseconds (60 TPS = 16.67ms).
     */
    public static final float TARGET_TICK_MS = 16.67f;

    /**
     * Maximum acceptable tick time before warning (in milliseconds).
     */
    public static final float WARNING_TICK_MS = 50.0f;

    /**
     * Critical tick time threshold (in milliseconds).
     */
    public static final float CRITICAL_TICK_MS = 100.0f;

    /**
     * Target tick rate (ticks per second).
     * Default: 60 TPS.
     */
    public static final int TARGET_TICK_RATE = 60;
}
