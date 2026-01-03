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
 * @since Pulse 3.0 - 헌법 정화: 정책 파라미터 getter 추가
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

        // ═══════════════════════════════════════════════════════════════
        // 정책 파라미터 Getter (v3.0 - 헌법 정화)
        // Pulse mixin은 이 값을 읽기만 하고, 정책 결정은 하지 않음.
        // ═══════════════════════════════════════════════════════════════

        /**
         * 캐시 갱신 주기 (틱 단위).
         * Pulse mixin은 이 간격마다 정책을 재평가함.
         * 
         * @return 캐시 갱신 주기 (기본값: 10 ticks)
         */
        default int getCacheRefreshTicks() {
                return 10;
        }

        /**
         * 기아(starvation) 한계 - 최대 연속 스킵 횟수.
         * 이 횟수를 넘으면 무조건 업데이트 수행 (안정성 보장).
         * 
         * @return 기아 한계 (기본값: 60 ticks)
         */
        default int getStarvationLimit() {
                return 60;
        }

        /**
         * 근거리 임계값 (제곱 거리).
         * 이 거리 내의 객체는 즉시 FULL 업데이트.
         * 
         * @return 근거리 임계값 제곱 (기본값: 100.0 = 10타일)
         */
        default float getNearDistanceSquared() {
                return 100.0f;
        }
}
