package com.pulse.api.profiler;

/**
 * Zombie Context Interface.
 * 
 * 좀비 상태 정보를 Pulse API로 추상화.
 * Fuse가 PZ 클래스를 직접 참조하지 않도록 함.
 * 
 * @since Pulse 1.2 / Phase 2
 */
public interface IZombieContext {

    /**
     * 가장 가까운 플레이어까지의 거리 제곱.
     * 제곱근 연산 회피를 위해 squared distance 사용.
     */
    float getDistanceSquaredToPlayer();

    /**
     * 좀비가 현재 공격 중인지.
     */
    boolean isAttacking();

    /**
     * 좀비에게 타겟이 있는지.
     */
    boolean hasTarget();

    /**
     * 좀비 iteration index (순회 순서).
     * deterministic skip 계산용.
     */
    int getIterationIndex();

    /**
     * 현재 월드 틱.
     */
    int getWorldTick();
}
