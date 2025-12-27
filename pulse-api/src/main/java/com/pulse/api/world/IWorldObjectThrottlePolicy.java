package com.pulse.api.world;

/**
 * Interface for world object throttle policy.
 * This interface provides loose coupling between Pulse Mixins and the Fuse
 * throttle implementation.
 * 
 * Implementing classes should determine appropriate throttle levels based on:
 * - Player distance
 * - System load (ShellShock state)
 * - Object type and characteristics
 * - Starvation prevention
 * 
 * @since Pulse 2.0 - Phase 4: Moved to pulse-api
 */
public interface IWorldObjectThrottlePolicy {

    /**
     * Decide the throttle level for a world inventory item.
     * 
     * @param item                 The world inventory object to evaluate
     * @param sequenceId           The unique sequence ID assigned to this object
     * @param cachedLevel          The previously cached throttle level (may be
     *                             null)
     * @param lastCacheTick        The tick when the cache was last updated
     * @param currentTick          The current game tick
     * @param ticksSinceLastUpdate Number of ticks since this object was last
     *                             updated
     * @return The appropriate WorldObjectThrottleLevel for this object
     */
    WorldObjectThrottleLevel decideThrottleLevel(
            Object item, // zombie.iso.objects.IsoWorldInventoryObject
            int sequenceId,
            WorldObjectThrottleLevel cachedLevel,
            long lastCacheTick,
            long currentTick,
            int ticksSinceLastUpdate);

    /**
     * Decide the throttle level for a corpse.
     * 
     * @param corpse               The dead body to evaluate
     * @param sequenceId           The unique sequence ID assigned to this corpse
     * @param cachedLevel          The previously cached throttle level (may be
     *                             null)
     * @param lastCacheTick        The tick when the cache was last updated
     * @param currentTick          The current game tick
     * @param ticksSinceLastUpdate Number of ticks since this corpse was last
     *                             updated
     * @return The appropriate WorldObjectThrottleLevel for this corpse
     */
    WorldObjectThrottleLevel decideThrottleLevelForCorpse(
            Object corpse, // zombie.iso.objects.IsoDeadBody
            int sequenceId,
            WorldObjectThrottleLevel cachedLevel,
            long lastCacheTick,
            long currentTick,
            int ticksSinceLastUpdate);
}
