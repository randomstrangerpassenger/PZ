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
import zombie.iso.IsoWorld;
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
 * @since Fuse v2.2 Area 7
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
     * Static policy instance - injected by FuseThrottleController.
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

    /**
     * Cache refresh interval in ticks.
     * Policy decisions are re-evaluated every CACHE_REFRESH_TICKS.
     */
    @Unique
    private static final int CACHE_REFRESH_TICKS = 10;

    /**
     * Starvation limit - maximum consecutive skips before forcing an update.
     * P0 mandatory feature for stability.
     */
    @Unique
    private static final int STARVATION_LIMIT = 60;

    /**
     * Near distance threshold (squared) - items within this distance get FULL
     * throttle immediately.
     * Distance in grid squares: ~10 squares = 100 squared.
     */
    @Unique
    private static final float NEAR_DIST_SQ = 100.0f;

    /**
     * Static method to inject the policy from FuseThrottleController.
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

            // If no policy is set, allow update (fail-open for safety)
            if (Pulse$policy == null) {
                return;
            }

            // If removeProcess is true or item is null, always allow update
            if (this.removeProcess || this.item == null) {
                return;
            }

            // Get current tick (approximate using counter)
            long currentTick = ++Pulse$tickCounter;

            // Check near-distance immediate update
            // Calculate distance to nearest player (placeholder - should use actual
            // implementation)
            float distSq = Pulse$getDistanceToNearestPlayer();
            if (distSq < NEAR_DIST_SQ) {
                // Force FULL throttle for nearby items
                if (Pulse$cachedLevel != WorldObjectThrottleLevel.FULL) {
                    Pulse$cachedLevel = WorldObjectThrottleLevel.FULL;
                    Pulse$lastCacheTick = currentTick;
                    Pulse$consecutiveSkips = 0;
                }
                return; // Allow update
            }

            // Check starvation limit - force update if exceeded
            if (Pulse$consecutiveSkips >= STARVATION_LIMIT) {
                Pulse$consecutiveSkips = 0;
                return; // Allow update
            }

            // Refresh cache if needed
            if (Pulse$cachedLevel == null || (currentTick - Pulse$lastCacheTick) >= CACHE_REFRESH_TICKS) {
                Pulse$cachedLevel = Pulse$policy.decideThrottleLevel(
                        (zombie.iso.objects.IsoWorldInventoryObject) (Object) this,
                        Pulse$sequenceId,
                        Pulse$cachedLevel,
                        Pulse$lastCacheTick,
                        currentTick,
                        Pulse$consecutiveSkips);
                Pulse$lastCacheTick = currentTick;
            }

            // Check if this tick should update based on throttle level
            boolean shouldUpdate = Pulse$cachedLevel.shouldUpdate(currentTick, Pulse$sequenceId);

            if (shouldUpdate) {
                Pulse$consecutiveSkips = 0;
                // Allow update
            } else {
                Pulse$consecutiveSkips++;
                // Cancel update
                ci.cancel();
            }

        } catch (Throwable t) {
            PulseErrorHandler.reportMixinFailure("WorldItemMixin.onUpdate", t);
            // Fail-open: allow update on error
        }
    }

    /**
     * Calculate distance squared to nearest player.
     * TODO: Implement actual distance calculation using player positions.
     * 
     * @return Distance squared to nearest player
     */
    @Unique
    private float Pulse$getDistanceToNearestPlayer() {
        // Placeholder implementation - returns large distance
        // Actual implementation should iterate through players and calculate min
        // distance
        try {
            zombie.iso.objects.IsoWorldInventoryObject self = (zombie.iso.objects.IsoWorldInventoryObject) (Object) this;

            if (self.square == null) {
                return Float.MAX_VALUE;
            }

            // Find nearest player manually using ZombieList
            zombie.characters.IsoPlayer nearestPlayer = null;
            float minDistSq = Float.MAX_VALUE;

            for (int i = 0; i < zombie.iso.IsoWorld.instance.getCell().getZombieList().size(); i++) {
                Object obj = zombie.iso.IsoWorld.instance.getCell().getZombieList().get(i);
                if (obj instanceof zombie.characters.IsoPlayer) {
                    zombie.characters.IsoPlayer player = (zombie.characters.IsoPlayer) obj;
                    float dx = player.getX() - (self.square.getX() + 0.5f);
                    float dy = player.getY() - (self.square.getY() + 0.5f);
                    float distSq = dx * dx + dy * dy;
                    if (distSq < minDistSq) {
                        minDistSq = distSq;
                        nearestPlayer = player;
                    }
                }
            }

            if (nearestPlayer == null) {
                return Float.MAX_VALUE;
            }

            return minDistSq;

        } catch (Exception e) {
            return Float.MAX_VALUE;
        }
    }
}
