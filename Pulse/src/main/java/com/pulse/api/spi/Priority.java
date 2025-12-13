package com.pulse.api.spi;

/**
 * Priority constants for SPI providers.
 * 
 * @since Pulse 1.0
 */
public final class Priority {

    private Priority() {
    } // Utility class

    /**
     * Lowest priority (loaded last).
     */
    public static final int LOWEST = 0;

    /**
     * Low priority.
     */
    public static final int LOW = 25;

    /**
     * Normal priority (default).
     */
    public static final int NORMAL = 50;

    /**
     * High priority.
     */
    public static final int HIGH = 75;

    /**
     * Highest priority (loaded first).
     */
    public static final int HIGHEST = 100;
}
