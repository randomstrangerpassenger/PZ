package com.fuse.throttle;

/**
 * Throttle Level for Tiered Zombie Optimization.
 * 
 * 각 레벨은 Step별 interval을 정의합니다.
 * interval=1이면 매 틱 실행, 2면 2틱마다 실행.
 * 
 * Pulse에서 Fuse 내부로 이동됨.
 * 
 * @since Fuse 0.5.0
 */
public enum ThrottleLevel {
    /**
     * 풀 업데이트 - 모든 Step 매 틱 실행.
     * 근거리 또는 공격/타겟/최근 교전 시 적용.
     */
    FULL(1, 1, 1, 100),

    /**
     * 경량 업데이트 - PERCEPTION만 2틱.
     * 중거리 (20-40타일) 적용.
     */
    REDUCED(2, 1, 1, 75),

    /**
     * 최소 업데이트 - PERCEPTION 4틱, BEHAVIOR 2틱.
     * 원거리 (40-80타일) 적용.
     */
    LOW(4, 2, 1, 50),

    /**
     * 휴면 업데이트 - 공격적 throttle.
     * 초원거리 (80타일+) 적용.
     */
    MINIMAL(8, 4, 2, 25);

    /** PERCEPTION step 실행 간격 (틱) */
    public final int perceptionInterval;

    /** BEHAVIOR step 실행 간격 (틱) */
    public final int behaviorInterval;

    /** TARGET step 실행 간격 (틱) */
    public final int targetInterval;

    /** 예산값 (0-100) - IThrottlePolicy 호환용 */
    public final int budget;

    ThrottleLevel(int perception, int behavior, int target, int budget) {
        this.perceptionInterval = perception;
        this.behaviorInterval = behavior;
        this.targetInterval = target;
        this.budget = budget;
    }

    /**
     * 주어진 Step이 이번 틱에 실행되어야 하는지 판단.
     * 
     * @param type      Step 유형
     * @param zombieId  좀비 고유 ID (분산용)
     * @param worldTick 현재 월드 틱
     * @return true면 실행, false면 스킵
     */
    public boolean shouldExecute(StepType type, int zombieId, long worldTick) {
        int interval = getIntervalFor(type);
        if (interval <= 1) {
            return true;
        }
        return ((zombieId + worldTick) % interval) == 0;
    }

    /**
     * Step 유형별 interval 반환.
     */
    public int getIntervalFor(StepType type) {
        if (type == null)
            return 1;

        return switch (type) {
            case PERCEPTION -> perceptionInterval;
            case BEHAVIOR -> behaviorInterval;
            case TARGET -> targetInterval;
            case MOTION, COLLISION -> 1; // 항상 실행
        };
    }

    /**
     * Step 유형 enum.
     */
    public enum StepType {
        PERCEPTION,
        BEHAVIOR,
        TARGET,
        MOTION,
        COLLISION
    }
}
