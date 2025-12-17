package com.fuse.throttle;

import com.fuse.config.FuseConfig;
import com.pulse.api.profiler.IZombieThrottlePolicy;

/**
 * Fuse Throttle Controller.
 * 
 * 거리 기반 좀비 업데이트 throttling (경량화).
 * 
 * @since Fuse 0.3.0
 */
public class FuseThrottleController implements IZombieThrottlePolicy {

    private static final String LOG = "Fuse";

    // 멀티플레이어 캐시
    private boolean isMultiplayer = false;
    private int lastMpCheckTick = -100;

    // 통계
    private long skipCount = 0;
    private long updateCount = 0;

    public FuseThrottleController() {
        System.out.println("[" + LOG + "] ThrottleController initialized (optimized)");
    }

    @Override
    public boolean shouldSkipFast(float distSq, boolean isAttacking, boolean hasTarget,
            int iterIndex, int worldTick) {
        // 1. Config 체크
        if (!FuseConfig.getInstance().isThrottlingEnabled()) {
            return false;
        }

        // 2. MP 체크
        if (checkMultiplayer(worldTick)) {
            return false;
        }

        // 3. 상태 예외
        if (isAttacking || hasTarget) {
            updateCount++;
            return false;
        }

        // 4. 거리 band
        int intervalMask = getIntervalMask(distSq);
        if (intervalMask == 0) {
            updateCount++;
            return false;
        }

        // 5. 비트 연산 throttle
        boolean skip = ((iterIndex + worldTick) & intervalMask) != 0;

        if (skip) {
            skipCount++;
        } else {
            updateCount++;
        }

        return skip;
    }

    private int getIntervalMask(float distSq) {
        FuseConfig config = FuseConfig.getInstance();

        if (distSq < config.getNearDistSq())
            return 0; // 매 틱
        if (distSq < config.getMediumDistSq())
            return 1; // 2틱
        if (distSq < config.getFarDistSq())
            return 3; // 4틱
        return 7; // 8틱
    }

    private boolean checkMultiplayer(int currentTick) {
        if (currentTick - lastMpCheckTick < 100) {
            return isMultiplayer;
        }
        lastMpCheckTick = currentTick;

        try {
            Class<?> gc = Class.forName("zombie.network.GameClient");
            isMultiplayer = (boolean) gc.getField("bClient").get(null);
        } catch (Throwable t) {
            isMultiplayer = false;
        }
        return isMultiplayer;
    }

    // --- Stats ---

    public long getSkipCount() {
        return skipCount;
    }

    public long getUpdateCount() {
        return updateCount;
    }

    public float getSkipRatio() {
        long total = skipCount + updateCount;
        return total == 0 ? 0f : (float) skipCount / total;
    }

    public void resetStats() {
        skipCount = 0;
        updateCount = 0;
    }

    public void printStatus() {
        System.out.println("[" + LOG + "] Throttle: skip=" + skipCount +
                " update=" + updateCount + " ratio=" + String.format("%.1f%%", getSkipRatio() * 100));
    }
}
