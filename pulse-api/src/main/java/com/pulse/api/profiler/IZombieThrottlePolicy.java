package com.pulse.api.profiler;

/**
 * Zombie throttle policy interface.
 * Implemented by Fuse or other optimization modules.
 * 
 * @since Pulse 1.2
 */
public interface IZombieThrottlePolicy {
    /**
     * Check if zombie update should be skipped.
     * 
     * @param distSq      Distance squared to nearest player
     * @param isAttacking Whether zombie is attacking
     * @param hasTarget   Whether zombie has a target
     * @param iterIndex   Iteration index
     * @param worldTick   Current world tick
     * @return true to skip this update
     */
    boolean shouldSkipFast(float distSq, boolean isAttacking, boolean hasTarget,
            int iterIndex, int worldTick);
}
