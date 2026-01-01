package com.fuse.throttle;

import com.fuse.config.FuseConfig;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.profiler.ZombieStepHook.IStepContext;
import com.pulse.api.profiler.ZombieStepHook.IZombieStepPolicy;
import com.pulse.api.profiler.ZombieStepHook.StepType;

/**
 * Fuse Step Throttle Policy.
 * 
 * Fuse 내부 ThrottleLevel과 연동하여 Step별 throttle 결정.
 * 
 * @since Fuse 0.4.0
 * @since Fuse 0.5.0 - ThrottleLevel 연동
 * @since Fuse 2.0 - Pulse 정화로 인해 Fuse 내부 ThrottleLevel 사용
 */
public class FuseStepPolicy implements IZombieStepPolicy {

    private static final String LOG = "Fuse";

    // 통계
    private long perceptionSkipCount = 0;
    private long perceptionExecCount = 0;
    private long behaviorSkipCount = 0;
    private long behaviorExecCount = 0;
    private long targetSkipCount = 0;
    private long targetExecCount = 0;
    private long totalStepCalls = 0;

    // 현재 스로틀 레벨 캐시
    private ThrottleLevel currentLevel = ThrottleLevel.FULL;

    public FuseStepPolicy() {
        PulseLogger.info(LOG, "StepPolicy initialized (ThrottleLevel mode)");
    }

    public void setCurrentThrottleLevel(ThrottleLevel level) {
        this.currentLevel = level != null ? level : ThrottleLevel.FULL;
    }

    @Override
    public boolean shouldSkipStep(StepType stepType, float distSq, IStepContext context) {
        if (!FuseConfig.getInstance().isStepThrottlingEnabled()) {
            return false;
        }

        totalStepCalls++;

        // Context에서 필요 정보 추출
        int zombieId = context != null ? context.getIterIndex() : 0;
        long worldTick = context != null ? context.getWorldTick() : 0;

        // Fuse 내부 ThrottleLevel 사용
        ThrottleLevel level = currentLevel;

        // ThrottleLevel의 shouldExecute()로 실행 여부 결정
        ThrottleLevel.StepType fuseStepType = mapStepType(stepType);
        boolean shouldExecute = level.shouldExecute(fuseStepType, zombieId, worldTick);
        boolean skip = !shouldExecute;

        // 통계 업데이트
        updateStats(stepType, skip);

        return skip;
    }

    /**
     * Pulse StepType을 Fuse 내부 ThrottleLevel.StepType으로 변환.
     */
    private ThrottleLevel.StepType mapStepType(StepType stepType) {
        if (stepType == null)
            return null;
        return switch (stepType) {
            case PERCEPTION -> ThrottleLevel.StepType.PERCEPTION;
            case BEHAVIOR -> ThrottleLevel.StepType.BEHAVIOR;
            case TARGET -> ThrottleLevel.StepType.TARGET;
            case MOTION -> ThrottleLevel.StepType.MOTION;
            case COLLISION -> ThrottleLevel.StepType.COLLISION;
        };
    }

    private void updateStats(StepType stepType, boolean skip) {
        if (stepType == null)
            return;

        switch (stepType) {
            case PERCEPTION:
                if (skip)
                    perceptionSkipCount++;
                else
                    perceptionExecCount++;
                break;
            case BEHAVIOR:
                if (skip)
                    behaviorSkipCount++;
                else
                    behaviorExecCount++;
                break;
            case TARGET:
                if (skip)
                    targetSkipCount++;
                else
                    targetExecCount++;
                break;
            default:
                break;
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
        perceptionExecCount = 0;
        behaviorSkipCount = 0;
        behaviorExecCount = 0;
        targetSkipCount = 0;
        targetExecCount = 0;
        totalStepCalls = 0;
    }

    public void printStatus() {
        PulseLogger.info(LOG, "Step Throttle Stats:");
        PulseLogger.info(LOG, "  PERCEPTION: exec=" + perceptionExecCount + " skip=" + perceptionSkipCount);
        PulseLogger.info(LOG, "  BEHAVIOR: exec=" + behaviorExecCount + " skip=" + behaviorSkipCount);
        PulseLogger.info(LOG, "  TARGET: exec=" + targetExecCount + " skip=" + targetSkipCount);
        PulseLogger.info(LOG, "  Total calls: " + totalStepCalls);
    }
}
