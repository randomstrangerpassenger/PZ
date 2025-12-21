package com.pulse.api.profiler;

/**
 * Throttle Policy Interface.
 * 
 * Tiered throttle 방식: update() 취소 없이 ThrottleLevel 반환.
 * 
 * @since Pulse 1.2
 * @since Pulse 1.5 - ThrottleLevel 기반으로 변경
 */
public interface IZombieThrottlePolicy {

    /**
     * 좀비의 throttle 레벨 결정.
     * 
     * update()는 절대 취소되지 않으며, 반환된 ThrottleLevel에 따라
     * AI Step들만 선택적으로 throttle됩니다.
     * 
     * @param distSq          플레이어까지 거리 제곱
     * @param isAttacking     공격 중 여부
     * @param hasTarget       타겟 있음 여부
     * @param recentlyEngaged 최근 60틱 내 교전 여부 (피격/사운드 감지)
     * @return ThrottleLevel (FULL/REDUCED/LOW/MINIMAL)
     */
    ThrottleLevel getThrottleLevel(float distSq, boolean isAttacking,
            boolean hasTarget, boolean recentlyEngaged);

    /**
     * 레거시 호환용 (deprecated).
     * 기존 코드 호환을 위해 유지, 내부적으로 getThrottleLevel() 호출.
     * 
     * @deprecated Use getThrottleLevel() instead
     */
    @Deprecated
    default boolean shouldSkipFast(float distSq, boolean isAttacking, boolean hasTarget,
            int iterIndex, int worldTick) {
        // 레거시: FULL이 아니면 skip으로 간주 (하위 호환)
        ThrottleLevel level = getThrottleLevel(distSq, isAttacking, hasTarget, false);
        return level != ThrottleLevel.FULL;
    }
}
