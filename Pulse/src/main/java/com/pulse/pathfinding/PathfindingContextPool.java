package com.pulse.pathfinding;

import com.pulse.api.spi.IPathfindingContext;

/**
 * PathfindingContext 풀.
 * 
 * ThreadLocal 기반 Flyweight 패턴으로 GC 압력 제거.
 * 각 스레드가 단일 컨텍스트 인스턴스를 재사용.
 * 
 * @since Pulse 2.1
 */
public final class PathfindingContextPool {

    private static final ThreadLocal<MutablePathfindingContext> POOL = ThreadLocal
            .withInitial(MutablePathfindingContext::new);

    private PathfindingContextPool() {
    }

    /**
     * 컨텍스트 획득.
     * 풀에서 인스턴스를 가져와 값을 리셋하고 반환.
     * 
     * @return 재사용 가능한 컨텍스트
     */
    public static IPathfindingContext acquire(
            int zombieId,
            float distanceSquared,
            int enginePriority,
            long gameTick,
            float targetX,
            float targetY,
            boolean inCombatState,
            boolean hasExistingPath) {
        MutablePathfindingContext ctx = POOL.get();
        ctx.reset(zombieId, distanceSquared, enginePriority, gameTick,
                targetX, targetY, inCombatState, hasExistingPath);
        return ctx;
    }

    /**
     * 컨텍스트 반환 (명시적 반환 불필요, ThreadLocal이 관리).
     * 
     * 이 메서드는 문서화 목적으로만 존재.
     * 실제로는 ThreadLocal이 스레드 종료 시 자동 정리.
     */
    public static void release(IPathfindingContext context) {
        // No-op: ThreadLocal manages lifecycle
    }
}
