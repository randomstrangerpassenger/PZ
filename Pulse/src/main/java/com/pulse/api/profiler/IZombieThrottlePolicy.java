package com.pulse.api.profiler;

/**
 * Throttle Policy Interface.
 * 
 * @since Pulse 1.2
 */
public interface IZombieThrottlePolicy {

    /**
     * 경량 throttle 체크 (리플렉션 없음).
     * Mixin에서 직접 호출.
     * 
     * @param distSq      플레이어까지 거리 제곱
     * @param isAttacking 공격 중 여부
     * @param hasTarget   타겟 있음 여부
     * @param iterIndex   순회 인덱스
     * @param worldTick   월드 틱
     * @return true면 스킵
     */
    boolean shouldSkipFast(float distSq, boolean isAttacking, boolean hasTarget,
            int iterIndex, int worldTick);
}
