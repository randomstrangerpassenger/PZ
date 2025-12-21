package com.fuse.throttle;

import com.fuse.config.FuseConfig;
import com.pulse.api.profiler.ThrottleLevel;
import com.pulse.api.profiler.ZombieHook;
import com.pulse.api.profiler.ZombieStepHook.IStepContext;
import com.pulse.api.profiler.ZombieStepHook.IZombieStepPolicy;
import com.pulse.api.profiler.ZombieStepHook.StepType;

/**
 * Fuse Step Throttle Policy.
 * 
 * ThrottleLevel과 연동하여 Step별 throttle 결정.
 * ZombieHook의 ThreadLocal 컨텍스트에서 현재 ThrottleLevel을 읽어
 * shouldExecute()로 실행 여부를 판단합니다.
 * 
 * @since Fuse 0.4.0
 * @since Fuse 0.5.0 - ThrottleLevel 연동
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

    public FuseStepPolicy() {
        System.out.println("[" + LOG + "] StepPolicy initialized (ThrottleLevel mode)");
    }

    @Override
    public boolean shouldSkipStep(StepType stepType, float distSq, IStepContext context) {
        if (!FuseConfig.getInstance().isStepThrottlingEnabled()) {
            return false;
        }

        totalStepCalls++;

        // Context에서 필요 정보 추출
        int zombieId = context != null ? context.getIterIndex() : 0;
        int worldTick = context != null ? context.getWorldTick() : 0;

        // ZombieHook에서 현재 ThrottleLevel 조회
        ThrottleLevel level = ZombieHook.getCurrentThrottleLevel(worldTick);

        // ThrottleLevel의 shouldExecute()로 실행 여부 결정
        boolean shouldExecute = level.shouldExecute(stepType, zombieId, worldTick);
        boolean skip = !shouldExecute;

        // 통계 업데이트
        updateStats(stepType, skip);

        return skip;
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
        System.out.println("[" + LOG + "] Step Throttle Stats:");
        System.out.println("  PERCEPTION: exec=" + perceptionExecCount + " skip=" + perceptionSkipCount);
        System.out.println("  BEHAVIOR: exec=" + behaviorExecCount + " skip=" + behaviorSkipCount);
        System.out.println("  TARGET: exec=" + targetExecCount + " skip=" + targetSkipCount);
        System.out.println("  Total calls: " + totalStepCalls);
    }
}
