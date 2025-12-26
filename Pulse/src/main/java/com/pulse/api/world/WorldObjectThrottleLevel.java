package com.pulse.api.world;

/**
 * Throttle levels for world objects (items and corpses).
 * These levels control the update frequency through a spread-based system.
 */
public enum WorldObjectThrottleLevel {
    /**
     * Full update - object updates every tick (spread=1, skip=0).
     * Used for objects very close to players or requiring immediate updates.
     */
    FULL(1, 0),

    /**
     * Light throttle - minimal performance saving (spread=2, skip=1).
     * Updates roughly every other tick.
     */
    LIGHT(2, 1),

    /**
     * Medium throttle - moderate performance saving (spread=4, skip=3).
     * Updates roughly every 4 ticks.
     */
    MEDIUM(4, 3),

    /**
     * Heavy throttle - significant performance saving (spread=8, skip=7).
     * Updates roughly every 8 ticks.
     */
    HEAVY(8, 7),

    /**
     * Very heavy throttle - maximum performance saving (spread=16, skip=15).
     * Updates roughly every 16 ticks.
     */
    VERY_HEAVY(16, 15);

    private final int spread;
    private final int maxSkip;

    WorldObjectThrottleLevel(int spread, int maxSkip) {
        this.spread = spread;
        this.maxSkip = maxSkip;
    }

    /**
     * Get the spread value for this throttle level.
     * The spread determines how updates are distributed across ticks.
     * 
     * @return The spread value
     */
    public int getSpread() {
        return spread;
    }

    /**
     * Get the maximum number of consecutive skips allowed.
     * 
     * @return The max skip value
     */
    public int getMaxSkip() {
        return maxSkip;
    }

    /**
     * Determine if an object with the given sequenceId should update on the current
     * tick.
     * Uses modulo arithmetic: (currentTick + sequenceId) % spread == 0
     * 
     * @param currentTick The current game tick
     * @param sequenceId  The object's unique sequence ID
     * @return true if the object should update, false otherwise
     */
    public boolean shouldUpdate(long currentTick, int sequenceId) {
        return ((currentTick + sequenceId) % spread) == 0;
    }
}
