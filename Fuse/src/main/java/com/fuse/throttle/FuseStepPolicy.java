package com.fuse.throttle;

import com.fuse.config.FuseConfig;
import com.pulse.api.profiler.ZombieStepHook;
import com.pulse.api.profiler.ZombieStepHook.IStepContext;
import com.pulse.api.profiler.ZombieStepHook.IZombieStepPolicy;
import com.pulse.api.profiler.ZombieStepHook.StepType;

/**
 * Fuse Step Throttle Policy.
 * 
 * Implements Pulse's IZombieStepPolicy to provide step-level throttling.
 * Different steps have different throttle intervals based on distance.
 * 
 * @since Fuse 0.4.0
 */
public class FuseStepPolicy implements IZombieStepPolicy {

    private static final String LOG = "Fuse";

    // 통계
    private long perceptionSkipCount = 0;
    private long behaviorSkipCount = 0;
    private long targetSkipCount = 0;
    private long totalStepCalls = 0;

    public FuseStepPolicy() {
        System.out.println("[" + LOG + "] StepPolicy initialized");
    }

    @Override
    public boolean shouldSkipStep(StepType stepType, float distSq, IStepContext context) {
        if (!FuseConfig.getInstance().isStepThrottlingEnabled()) {
            return false;
        }

        totalStepCalls++;

        // Context에서 추가 정보 추출
        int iterIndex = context != null ? context.getIterIndex() : 0;
        int worldTick = context != null ? context.getWorldTick() : 0;
        boolean isAttacking = context != null && context.isAttacking();
        boolean hasTarget = context != null && context.hasTarget();

        // 공격 중이거나 타겟 있으면 스킵 안 함
        if (isAttacking || hasTarget) {
            return false;
        }

        // Step별 다른 interval 적용
        int intervalMask = getIntervalMask(stepType, distSq);
        if (intervalMask == 0) {
            return false;
        }

        boolean skip = ((iterIndex + worldTick) & intervalMask) != 0;

        // 통계 업데이트
        if (skip) {
            switch (stepType) {
                case PERCEPTION:
                    perceptionSkipCount++;
                    break;
                case BEHAVIOR:
                    behaviorSkipCount++;
                    break;
                case TARGET:
                    targetSkipCount++;
                    break;
                default:
                    break;
            }
        }

        return skip;
    }

    /**
     * Step별, 거리별 interval mask 반환.
     * 
     * PERCEPTION: 가장 비싼 연산 → 적극적 throttle
     * BEHAVIOR: 중간 비용 → 중간 throttle
     * TARGET: 가벼운 편 → 보수적 throttle
     */
    private int getIntervalMask(StepType stepType, float distSq) {
        FuseConfig config = FuseConfig.getInstance();

        // 근거리는 모든 step 매 틱 실행
        if (distSq < config.getNearDistSq()) {
            return 0;
        }

        switch (stepType) {
            case PERCEPTION:
                // 가장 비싼 연산: 적극적 throttle
                if (distSq < config.getMediumDistSq())
                    return 1; // 2틱
                if (distSq < config.getFarDistSq())
                    return 3; // 4틱
                return 7; // 8틱

            case BEHAVIOR:
                // 중간 비용
                if (distSq < config.getMediumDistSq())
                    return 0; // 매 틱
                if (distSq < config.getFarDistSq())
                    return 1; // 2틱
                return 3; // 4틱

            case TARGET:
                // 가벼운 편: 보수적 throttle
                if (distSq < config.getFarDistSq())
                    return 0; // 매 틱
                return 1; // 2틱

            default:
                return 0;
        }
    }

    // --- Stats ---

    public long getPerceptionSkipCount() {
        return perceptionSkipCount;
    }

    public long getBehaviorSkipCount() {
        return behaviorSkipCount;
    }

    public long getTargetSkipCount() {
        return targetSkipCount;
    }

    public long getTotalStepCalls() {
        return totalStepCalls;
    }

    public void resetStats() {
        perceptionSkipCount = 0;
        behaviorSkipCount = 0;
        targetSkipCount = 0;
        totalStepCalls = 0;
    }

    public void printStatus() {
        System.out.println("[" + LOG + "] Step Throttle Stats:");
        System.out.println("  PERCEPTION skipped: " + perceptionSkipCount);
        System.out.println("  BEHAVIOR skipped: " + behaviorSkipCount);
        System.out.println("  TARGET skipped: " + targetSkipCount);
        System.out.println("  Total calls: " + totalStepCalls);
    }
}
