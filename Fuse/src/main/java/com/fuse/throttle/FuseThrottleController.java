package com.fuse.throttle;

import com.fuse.config.FuseConfig;
import com.pulse.api.profiler.IZombieThrottlePolicy;
import com.pulse.api.profiler.ThrottleLevel;

/**
 * Fuse Throttle Controller.
 * 
 * Tiered 거리 기반 좀비 업데이트 throttling.
 * update()는 절대 취소하지 않고, ThrottleLevel만 반환.
 * 
 * @since Fuse 0.3.0
 * @since Fuse 0.5.0 - Tiered ThrottleLevel 방식으로 전환
 */
public class FuseThrottleController implements IZombieThrottlePolicy {

    private static final String LOG = "Fuse";

    // 멀티플레이어 캐시
    private boolean isMultiplayer = false;
    private int lastMpCheckTick = -100;

    // 통계
    private long fullCount = 0;
    private long reducedCount = 0;
    private long lowCount = 0;
    private long minimalCount = 0;
    private long engagedUpgradeCount = 0; // recentlyEngaged로 인한 순수 FULL 승격

    public FuseThrottleController() {
        System.out.println("[" + LOG + "] ThrottleController initialized (Tiered mode)");
    }

    @Override
    public ThrottleLevel getThrottleLevel(float distSq, boolean isAttacking,
            boolean hasTarget, boolean recentlyEngaged) {

        // 1. Config 체크
        if (!FuseConfig.getInstance().isThrottlingEnabled()) {
            return ThrottleLevel.FULL;
        }

        // 2. 즉시 FULL 승격 조건
        if (isAttacking || hasTarget || recentlyEngaged) {
            fullCount++;
            // 순수 engaged 승격만 카운트 (attacking, hasTarget 아닌 경우)
            if (recentlyEngaged && !isAttacking && !hasTarget) {
                engagedUpgradeCount++;
            }
            return ThrottleLevel.FULL;
        }

        // 3. MP 모드에서는 throttle 비활성화 (동기화 문제 방지)
        // TODO: MP 환경 테스트 후 점진적으로 활성화
        // if (checkMultiplayer(currentTick)) {
        // return ThrottleLevel.FULL;
        // }

        // 4. 거리 기반 Tiered 레벨 결정
        FuseConfig config = FuseConfig.getInstance();

        if (distSq < config.getNearDistSq()) {
            fullCount++;
            return ThrottleLevel.FULL;
        }

        if (distSq < config.getMediumDistSq()) {
            reducedCount++;
            return ThrottleLevel.REDUCED;
        }

        if (distSq < config.getFarDistSq()) {
            lowCount++;
            return ThrottleLevel.LOW;
        }

        minimalCount++;
        return ThrottleLevel.MINIMAL;
    }

    /**
     * @deprecated Tiered 방식으로 전환됨. 하위 호환용.
     */
    @Deprecated
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

    public long getFullCount() {
        return fullCount;
    }

    public long getReducedCount() {
        return reducedCount;
    }

    public long getLowCount() {
        return lowCount;
    }

    public long getMinimalCount() {
        return minimalCount;
    }

    public long getEngagedUpgradeCount() {
        return engagedUpgradeCount;
    }

    public long getTotalCount() {
        return fullCount + reducedCount + lowCount + minimalCount;
    }

    public void resetStats() {
        fullCount = 0;
        reducedCount = 0;
        lowCount = 0;
        minimalCount = 0;
        engagedUpgradeCount = 0;
    }

    public void printStatus() {
        long total = getTotalCount();
        System.out.println("[" + LOG + "] Tiered Throttle Stats:");
        System.out.println("  FULL: " + fullCount + " (" + pct(fullCount, total) + "%)");
        System.out.println("  REDUCED: " + reducedCount + " (" + pct(reducedCount, total) + "%)");
        System.out.println("  LOW: " + lowCount + " (" + pct(lowCount, total) + "%)");
        System.out.println("  MINIMAL: " + minimalCount + " (" + pct(minimalCount, total) + "%)");
        System.out.println("  EngagedUpgrade: " + engagedUpgradeCount);
    }

    private String pct(long count, long total) {
        return total == 0 ? "0.0" : String.format("%.1f", (count * 100.0) / total);
    }
}
