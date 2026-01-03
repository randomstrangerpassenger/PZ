package com.fuse.area7.governor;

/**
 * 지연된 경로탐색 요청 데이터.
 * 
 * @since Fuse 2.2
 */
public final class DeferredPathRequest {

    private final int zombieId;
    private final int priority;
    private final float distanceSquared;
    private final float targetX;
    private final float targetY;
    private final long requestTick;

    public DeferredPathRequest(
            int zombieId,
            int priority,
            float distanceSquared,
            float targetX,
            float targetY,
            long requestTick) {
        this.zombieId = zombieId;
        this.priority = priority;
        this.distanceSquared = distanceSquared;
        this.targetX = targetX;
        this.targetY = targetY;
        this.requestTick = requestTick;
    }

    public int getZombieId() {
        return zombieId;
    }

    public int getPriority() {
        return priority;
    }

    public float getDistanceSquared() {
        return distanceSquared;
    }

    public float getTargetX() {
        return targetX;
    }

    public float getTargetY() {
        return targetY;
    }

    public long getRequestTick() {
        return requestTick;
    }

    @Override
    public String toString() {
        return String.format("DeferredPathRequest[zombie=%d, priority=%d, tick=%d]",
                zombieId, priority, requestTick);
    }
}
