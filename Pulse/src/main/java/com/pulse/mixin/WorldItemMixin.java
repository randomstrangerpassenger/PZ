package com.pulse.mixin;

import com.pulse.api.world.IWorldObjectThrottlePolicy;
import com.pulse.api.world.WorldObjectThrottleLevel;
import com.pulse.api.log.PulseLogger;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import zombie.inventory.InventoryItem;

/**
 * Mixin for IsoWorldInventoryObject - implements Pulse throttling for world
 * items.
 * 
 * P0 Features:
 * - SequenceId assignment (session-stable, monotonically increasing)
 * - Throttle level caching with policy-based decisions
 * - Starvation limit enforcement
 * - Near-distance immediate level update
 * 
 * Injection Point: IsoWorldInventoryObject.update()
 * 
 * @since v2.2 Area 7
 */
@Mixin(targets = "zombie.iso.objects.IsoWorldInventoryObject")
public class WorldItemMixin {

    // Shadow fields from IsoWorldInventoryObject
    @Shadow
    public InventoryItem item;

    @Shadow
    public boolean removeProcess;

    // Pulse$ fields - unique to this Mixin

    /**
     * Unique sequence ID assigned once on object creation.
     * Used for spread-based throttle distribution.
     */
    @Unique
    private int Pulse$sequenceId = -1;

    /**
     * Cached throttle level - avoids recalculating every tick.
     */
    @Unique
    private WorldObjectThrottleLevel Pulse$cachedLevel = null;

    /**
     * Tick when the cache was last updated.
     */
    @Unique
    private long Pulse$lastCacheTick = 0;

    /**
     * Number of consecutive ticks this object has been skipped.
     * Used for starvation limit enforcement.
     */
    @Unique
    private int Pulse$consecutiveSkips = 0;

    /**
     * Static policy instance - injected by ThrottleController.
     * Volatile to ensure visibility across threads.
     */
    @Unique
    private static volatile IWorldObjectThrottlePolicy Pulse$policy = null;

    /**
     * Static sequence ID counter - assigns unique IDs to all world items.
     * Thread-safe via AtomicInteger.
     */
    @Unique
    private static final java.util.concurrent.atomic.AtomicInteger Pulse$sequenceCounter = new java.util.concurrent.atomic.AtomicInteger(
            0);

    /**
     * Static tick counter for approximating game ticks.
     * Updated by each update call.
     */
    @Unique
    private static long Pulse$tickCounter = 0;

    // 헌법 정화 v3.0: 정책 상수들 제거됨
    // CACHE_REFRESH_TICKS, STARVATION_LIMIT, NEAR_DIST_SQ
    // 이제 policy.getCacheRefreshTicks() 등을 사용

    /**
     * Static method to inject the policy from ThrottleController.
     * This maintains loose coupling via the interface.
     * 
     * @param policy The throttle policy implementation
     */
    @Unique
    private static void Pulse$setPolicy(IWorldObjectThrottlePolicy policy) {
        Pulse$policy = policy;
        PulseLogger.info("Pulse/WorldItemMixin", "✅ IWorldObjectThrottlePolicy injected");
    }

    /**
     * Assign sequence ID to this object on first update.
     * Called lazily to handle items loaded from save files.
     */
    @Unique
    private void Pulse$ensureSequenceId() {
        if (Pulse$sequenceId == -1) {
            Pulse$sequenceId = Pulse$sequenceCounter.getAndIncrement();
        }
    }

    /**
     * Inject throttle logic into IsoWorldInventoryObject.update().
     * 
     * Logic:
     * 1. Assign sequenceId if not yet assigned
     * 2. Check if policy is available
     * 3. Evaluate near-distance immediate update
     * 4. Check starvation limit
     * 5. Evaluate cached throttle level or refresh cache
     * 6. Decide whether to allow update or cancel
     * 
     * @param ci Callback info - used to cancel the update if throttled
     */
    @Inject(method = "update", at = @At("HEAD"), cancellable = true)
    private void Pulse$onUpdate(CallbackInfo ci) {
        try {
            // Ensure sequenceId is assigned
            Pulse$ensureSequenceId();

            // Get current tick (approximate using counter)
            long currentTick = ++Pulse$tickCounter;

            // If no policy is set, allow update (fail-open for safety)
            if (Pulse$policy == null) {
                return;
            }

            // If removeProcess is true or item is null, always allow update
            if (this.removeProcess || this.item == null) {
                return;
            }

            // Check starvation limit (policy에서 값 획득)
            if (Pulse$consecutiveSkips >= Pulse$policy.getStarvationLimit()) {
                Pulse$consecutiveSkips = 0;
                return;
            }

            // Cache refresh check (policy에서 값 획득)
            boolean needsCacheRefresh = (Pulse$cachedLevel == null
                    || (currentTick - Pulse$lastCacheTick) >= Pulse$policy.getCacheRefreshTicks());

            if (needsCacheRefresh) {
                try {
                    WorldObjectThrottleLevel newLevel = Pulse$policy.decideThrottleLevel(
                            (zombie.iso.objects.IsoWorldInventoryObject) (Object) this,
                            Pulse$sequenceId,
                            Pulse$cachedLevel,
                            Pulse$lastCacheTick,
                            currentTick,
                            Pulse$consecutiveSkips);

                    // Null check with fallback
                    if (newLevel == null) {
                        newLevel = WorldObjectThrottleLevel.FULL;
                    }

                    Pulse$cachedLevel = newLevel;
                    Pulse$lastCacheTick = currentTick;

                } catch (Throwable policyError) {
                    PulseErrorHandler.reportMixinFailure("WorldItemMixin.policy", policyError);
                    Pulse$cachedLevel = WorldObjectThrottleLevel.FULL;
                    Pulse$lastCacheTick = currentTick;
                }
            }

            // Final null safety
            if (Pulse$cachedLevel == null) {
                Pulse$cachedLevel = WorldObjectThrottleLevel.FULL;
            }

            // Decision
            boolean shouldUpdate = Pulse$cachedLevel.shouldUpdate(currentTick, Pulse$sequenceId);

            if (shouldUpdate) {
                Pulse$consecutiveSkips = 0;
            } else {
                Pulse$consecutiveSkips++;
                ci.cancel();
            }

        } catch (Throwable t) {
            PulseErrorHandler.reportMixinFailure("WorldItemMixin.onUpdate", t);
        }
    }

    /**
     * Calculate distance squared to nearest player.
     * 
     * @return Distance squared to nearest player
     */
    @Unique
    private float Pulse$getDistanceToNearestPlayer() {
        try {
            zombie.iso.objects.IsoWorldInventoryObject self = (zombie.iso.objects.IsoWorldInventoryObject) (Object) this;

            if (self.square == null) {
                return Float.MAX_VALUE;
            }

            float minDistSq = Float.MAX_VALUE;

            // [FIX] Use IsoPlayer.players + numPlayers (SP/MP compatible)
            for (int i = 0; i < zombie.characters.IsoPlayer.numPlayers; i++) {
                zombie.characters.IsoPlayer player = zombie.characters.IsoPlayer.players[i];

                if (player == null || player.isDead())
                    continue;

                float dx = player.getX() - (self.square.getX() + 0.5f);
                float dy = player.getY() - (self.square.getY() + 0.5f);
                float distSq = dx * dx + dy * dy;

                if (distSq < minDistSq) {
                    minDistSq = distSq;
                }
            }

            return minDistSq;

        } catch (Exception e) {
            return Float.MAX_VALUE; // Fail-soft
        }
    }
}
