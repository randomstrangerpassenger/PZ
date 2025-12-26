package com.fuse.governor;

import com.pulse.api.world.IWorldObjectThrottlePolicy;
import com.pulse.api.world.WorldObjectThrottleLevel;
import com.pulse.api.log.PulseLogger;

/**
 * ItemGovernor - implements IWorldObjectThrottlePolicy for world items.
 * 
 * Features:
 * - Sequence-based throttle distribution
 * - ShellShock integration
 * - Starvation-aware policy
 * 
 * @since Fuse v2.2 Area 7
 */
public class ItemGovernor implements IWorldObjectThrottlePolicy {

    private static final String LOG = "Fuse/ItemGovernor";

    // ShellShock state
    private volatile boolean shellShockActive = false;

    // Statistics
    private long fullLevelCount = 0;
    private long lightLevelCount = 0;
    private long mediumLevelCount = 0;
    private long heavyLevelCount = 0;
    private long veryHeavyLevelCount = 0;
    private long shellShockThrottleCount = 0;
    private long starvationPreventCount = 0;

    // Starvation limit (from WorldItemMixin)
    private static final int ITEM_STARVATION_LIMIT = 60;

    public ItemGovernor() {
        PulseLogger.info(LOG, "✅ ItemGovernor initialized");
    }

    /**
     * Set ShellShock state - called by FuseThrottleController.
     */
    public void setShellShockActive(boolean active) {
        if (active && !this.shellShockActive) {
            this.shellShockActive = true;
            PulseLogger.info(LOG, "🔥 ShellShock ACTIVE - aggressive throttling enabled");
        } else if (!active && this.shellShockActive) {
            this.shellShockActive = false;
            PulseLogger.info(LOG, "✅ ShellShock ENDED - normal throttling resumed");
        }
    }

    public boolean isShellShockActive() {
        return shellShockActive;
    }

    @Override
    public WorldObjectThrottleLevel decideThrottleLevel(
            Object item,
            int sequenceId,
            WorldObjectThrottleLevel cachedLevel,
            long lastCacheTick,
            long currentTick,
            int ticksSinceLastUpdate) {
        try {
            // Starvation prevention
            if (ticksSinceLastUpdate >= ITEM_STARVATION_LIMIT - 10) {
                starvationPreventCount++;
                return WorldObjectThrottleLevel.LIGHT;
            }

            // ShellShock handling - throttle more aggressively
            if (shellShockActive) {
                shellShockThrottleCount++;
                return WorldObjectThrottleLevel.HEAVY;
            }

            // Sequence-based distribution
            WorldObjectThrottleLevel level = calculateLevelSimple(sequenceId);
            incrementLevelStat(level);
            return level;

        } catch (Throwable t) {
            PulseLogger.error(LOG, "Error in decideThrottleLevel: " + t.getMessage());
            return WorldObjectThrottleLevel.FULL;
        }
    }

    @Override
    public WorldObjectThrottleLevel decideThrottleLevelForCorpse(
            Object corpse,
            int sequenceId,
            WorldObjectThrottleLevel cachedLevel,
            long lastCacheTick,
            long currentTick,
            int ticksSinceLastUpdate) {
        // Corpse throttling not implemented (corpses don't use update() loop)
        return WorldObjectThrottleLevel.FULL;
    }

    /**
     * Simple level calculation based on sequenceId distribution.
     */
    private WorldObjectThrottleLevel calculateLevelSimple(int sequenceId) {
        int mod = sequenceId % 10;
        if (mod < 3) {
            return WorldObjectThrottleLevel.FULL;
        } else if (mod < 6) {
            return WorldObjectThrottleLevel.LIGHT;
        } else if (mod < 8) {
            return WorldObjectThrottleLevel.MEDIUM;
        } else {
            return WorldObjectThrottleLevel.HEAVY;
        }
    }

    private void incrementLevelStat(WorldObjectThrottleLevel level) {
        switch (level) {
            case FULL:
                fullLevelCount++;
                break;
            case LIGHT:
                lightLevelCount++;
                break;
            case MEDIUM:
                mediumLevelCount++;
                break;
            case HEAVY:
                heavyLevelCount++;
                break;
            case VERY_HEAVY:
                veryHeavyLevelCount++;
                break;
        }
    }

    public long getTotalDecisions() {
        return fullLevelCount + lightLevelCount + mediumLevelCount + heavyLevelCount + veryHeavyLevelCount;
    }

    public void printStatus() {
        long total = getTotalDecisions();
        PulseLogger.info(LOG, "ItemGovernor Status:");
        PulseLogger.info(LOG, String.format("  FULL: %d (%.1f%%)", fullLevelCount, pct(fullLevelCount, total)));
        PulseLogger.info(LOG, String.format("  LIGHT: %d (%.1f%%)", lightLevelCount, pct(lightLevelCount, total)));
        PulseLogger.info(LOG, String.format("  MEDIUM: %d (%.1f%%)", mediumLevelCount, pct(mediumLevelCount, total)));
        PulseLogger.info(LOG, String.format("  HEAVY: %d (%.1f%%)", heavyLevelCount, pct(heavyLevelCount, total)));
        PulseLogger.info(LOG,
                String.format("  VERY_HEAVY: %d (%.1f%%)", veryHeavyLevelCount, pct(veryHeavyLevelCount, total)));
        PulseLogger.info(LOG, "  ---");
        PulseLogger.info(LOG, "  ShellShock throttles: " + shellShockThrottleCount);
        PulseLogger.info(LOG, "  Starvation prevents: " + starvationPreventCount);
        PulseLogger.info(LOG, "  ShellShock active: " + (shellShockActive ? "YES" : "NO"));
    }

    public void resetStats() {
        fullLevelCount = 0;
        lightLevelCount = 0;
        mediumLevelCount = 0;
        heavyLevelCount = 0;
        veryHeavyLevelCount = 0;
        shellShockThrottleCount = 0;
        starvationPreventCount = 0;
    }

    private double pct(long count, long total) {
        return total == 0 ? 0.0 : (count * 100.0) / total;
    }

    // Getters for telemetry
    public long getShellShockThrottleCount() {
        return shellShockThrottleCount;
    }

    public long getStarvationPreventCount() {
        return starvationPreventCount;
    }
}
