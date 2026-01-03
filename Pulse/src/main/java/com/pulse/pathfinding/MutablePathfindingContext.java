package com.pulse.pathfinding;

import com.pulse.api.spi.IPathfindingContext;

/**
 * IPathfindingContext 구현체.
 * 
 * Flyweight 패턴: ThreadLocal 풀에서 재사용하여 GC 압력 제거.
 * 
 * @since Pulse 2.1
 */
public final class MutablePathfindingContext implements IPathfindingContext {

    private int zombieId;
    private float distanceSquared;
    private int enginePriority;
    private long gameTick;
    private float targetX;
    private float targetY;
    private boolean inCombatState;
    private boolean hasExistingPath;
    private boolean deferred;

    /**
     * 컨텍스트 리셋 (풀에서 재사용 시 호출).
     */
    public void reset(
            int zombieId,
            float distanceSquared,
            int enginePriority,
            long gameTick,
            float targetX,
            float targetY,
            boolean inCombatState,
            boolean hasExistingPath) {
        this.zombieId = zombieId;
        this.distanceSquared = distanceSquared;
        this.enginePriority = enginePriority;
        this.gameTick = gameTick;
        this.targetX = targetX;
        this.targetY = targetY;
        this.inCombatState = inCombatState;
        this.hasExistingPath = hasExistingPath;
        this.deferred = false; // 매번 리셋
    }

    @Override
    public int getZombieId() {
        return zombieId;
    }

    @Override
    public float getDistanceSquared() {
        return distanceSquared;
    }

    @Override
    public int getEngineAssignedPriority() {
        return enginePriority;
    }

    @Override
    public long getGameTick() {
        return gameTick;
    }

    @Override
    public float getTargetX() {
        return targetX;
    }

    @Override
    public float getTargetY() {
        return targetY;
    }

    @Override
    public boolean isInCombatState() {
        return inCombatState;
    }

    @Override
    public boolean hasExistingPath() {
        return hasExistingPath;
    }

    @Override
    public boolean isDeferred() {
        return deferred;
    }

    @Override
    public void setDeferred(boolean deferred) {
        this.deferred = deferred;
    }

    @Override
    public String toString() {
        return String.format(
                "PathfindingContext[zombie=%d, dist²=%.1f, priority=%d, tick=%d, deferred=%s]",
                zombieId, distanceSquared, enginePriority, gameTick, deferred);
    }
}
