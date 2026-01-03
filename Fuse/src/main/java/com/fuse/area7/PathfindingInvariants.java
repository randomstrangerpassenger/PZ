package com.fuse.area7;

/**
 * Area 7 (경로탐색/충돌/물리) 불변 원칙.
 * 
 * <p>
 * <b>이 주석을 삭제하거나 무시하지 말 것.</b>
 * </p>
 * 
 * <h2>절대 금지 (NEVER)</h2>
 * <ul>
 * <li>경로 알고리즘 변경 (A*, heuristic 수정)</li>
 * <li>충돌 판정 로직 변경</li>
 * <li>물리 계산 결과 변경</li>
 * <li>AI 판단/행동 영향</li>
 * <li>"더 나은 경로", "덜 부딪히게" 등 최적화</li>
 * </ul>
 * 
 * <h2>허용 언어 (ALLOWED)</h2>
 * <ul>
 * <li>guard, limit, defer, deduplicate</li>
 * <li>stabilize, clamp, budget, throttle</li>
 * <li>fail-soft, sanity check, deadman switch</li>
 * </ul>
 * 
 * @since Fuse 2.2
 */
public final class PathfindingInvariants {

    // ═══════════════════════════════════════════════════════════════
    // 경로탐색 예산 (Pathfinding Budget)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 틱당 기본 경로탐색 예산.
     * 예산 초과 시 다음 틱으로 지연 (DROP 아님).
     */
    public static final int DEFAULT_BUDGET_PER_TICK = 50;

    /**
     * 지연 큐 최대 크기.
     * 초과 시 최저 우선순위 DROP.
     */
    public static final int MAX_DEFER_QUEUE_SIZE = 200;

    /**
     * 최대 연속 DROP 횟수.
     * 이 횟수 초과 시 Starvation 방지로 강제 처리.
     */
    public static final int MAX_CONSECUTIVE_DROPS = 3;

    // ═══════════════════════════════════════════════════════════════
    // 우선순위 (엔진 정의 읽기)
    // ═══════════════════════════════════════════════════════════════

    /** 엔진 우선순위: 배회 (최저) */
    public static final int PRIORITY_WANDER = 0;

    /** 엔진 우선순위: 추적 */
    public static final int PRIORITY_CHASE = 1;

    /** 엔진 우선순위: 전투 (최고, 무조건 허용) */
    public static final int PRIORITY_COMBAT = 2;

    // ═══════════════════════════════════════════════════════════════
    // 거리 임계값 (제곱값 - sqrt 회피)
    // ═══════════════════════════════════════════════════════════════

    /** 근거리 (20타일²) - 모든 최적화 중단, 정상 처리 */
    public static final float NEAR_DIST_SQ = 20f * 20f; // 400

    /** 중거리 (40타일²) */
    public static final float MEDIUM_DIST_SQ = 40f * 40f; // 1600

    /** 원거리 (80타일²) - DROP 후보 */
    public static final float FAR_DIST_SQ = 80f * 80f; // 6400

    // ═══════════════════════════════════════════════════════════════
    // 타임아웃 (NavMesh Guard)
    // ═══════════════════════════════════════════════════════════════

    /** 경고 임계값 (ms) */
    public static final long NAVMESH_WARNING_MS = 50;

    /** 타임아웃 임계값 (ms) - Silent Fail */
    public static final long NAVMESH_TIMEOUT_MS = 100;

    // ═══════════════════════════════════════════════════════════════
    // 캐시 TTL
    // ═══════════════════════════════════════════════════════════════

    /** 충돌 캐시 TTL (틱) - 1틱 엄수 */
    public static final int COLLISION_CACHE_TTL = 1;

    // ═══════════════════════════════════════════════════════════════
    // Private Constructor
    // ═══════════════════════════════════════════════════════════════

    private PathfindingInvariants() {
        throw new AssertionError("PathfindingInvariants는 인스턴스화할 수 없습니다.");
    }
}
