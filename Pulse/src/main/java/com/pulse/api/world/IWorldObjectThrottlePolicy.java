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
 * @since Pulse 3.0 - 헌법 정화: 정책 파라미터 getter 추가
 */
public interface IWorldObjectThrottlePolicy {

        /**
         * Decide the throttle level for a world inventory item.
         */
        WorldObjectThrottleLevel decideThrottleLevel(
                        Object item,
                        int sequenceId,
                        WorldObjectThrottleLevel cachedLevel,
                        long lastCacheTick,
                        long currentTick,
                        int ticksSinceLastUpdate);

        /**
         * Decide the throttle level for a corpse.
         */
        WorldObjectThrottleLevel decideThrottleLevelForCorpse(
                        Object corpse,
                        int sequenceId,
                        WorldObjectThrottleLevel cachedLevel,
                        long lastCacheTick,
                        long currentTick,
                        int ticksSinceLastUpdate);

        // ═══════════════════════════════════════════════════════════════
        // 정책 파라미터 Getter (v3.0 - 헌법 정화)
        // ═══════════════════════════════════════════════════════════════

        default int getCacheRefreshTicks() {
                return 10;
        }

        default int getStarvationLimit() {
                return 60;
        }

        default float getNearDistanceSquared() {
                return 100.0f;
        }
}
