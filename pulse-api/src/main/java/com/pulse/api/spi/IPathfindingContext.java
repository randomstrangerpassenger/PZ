package com.pulse.api.spi;

/**
 * 경로탐색 요청 컨텍스트.
 * 
 * Pulse가 제공하는 읽기 전용 사실(facts) 객체.
 * Fuse 등 안정성 레이어가 이 정보를 읽고 defer/guard 결정을 내림.
 * 
 * GC-free 설계: Flyweight 패턴으로 재사용.
 * 
 * @since Pulse 2.1
 */
public interface IPathfindingContext {

    /**
     * 좀비 ID (인스턴스 식별자).
     * 엔진이 부여한 고유 ID.
     */
    int getZombieId();

    /**
     * 플레이어까지의 거리 제곱.
     * 제곱값으로 제공하여 sqrt 연산 회피.
     */
    float getDistanceSquared();

    /**
     * 엔진이 할당한 우선순위.
     * 
     * 주의: 이 값은 엔진이 정의한 것이며 Fuse가 정한 것이 아님.
     * Fuse는 이 값을 읽기만 함.
     * 
     * @return 0=WANDER, 1=CHASE, 2=COMBAT (엔진 정의)
     */
    int getEngineAssignedPriority();

    /**
     * 현재 게임 틱.
     */
    long getGameTick();

    /**
     * 목표 X 좌표.
     */
    float getTargetX();

    /**
     * 목표 Y 좌표.
     */
    float getTargetY();

    /**
     * 좀비가 전투 상태인지 (엔진 상태 읽기).
     * COMBAT 우선순위 판정에 사용.
     */
    boolean isInCombatState();

    /**
     * 이미 유효한 경로가 있는지 (재계산 필요 여부).
     */
    boolean hasExistingPath();

    // ═══════════════════════════════════════════════════════════════
    // Defer 상태 (Fuse가 설정)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 이 요청이 지연 처리되어야 하는지.
     * Fuse가 설정하고 Pulse가 읽음.
     */
    boolean isDeferred();

    /**
     * 지연 상태 설정 (Fuse 전용).
     */
    void setDeferred(boolean deferred);
}
