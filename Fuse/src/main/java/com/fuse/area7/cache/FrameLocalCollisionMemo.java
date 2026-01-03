package com.fuse.area7.cache;

import java.util.HashMap;
import java.util.Map;

/**
 * 프레임 로컬 충돌 메모이제이션.
 * 
 * <p>
 * 2/3 모델 강한 합의: 프레임 내 충돌 검사 결과 캐싱.
 * </p>
 * 
 * <h2>TTL = 1틱 엄수</h2>
 * <ul>
 * <li>틱 종료 시 강제 클리어</li>
 * <li>유령 충돌 방지</li>
 * </ul>
 * 
 * @since Fuse 2.2
 */
public class FrameLocalCollisionMemo {

    private final Map<Long, Boolean> cache = new HashMap<>();
    private long currentTick = -1;

    // 텔레메트리
    private int cacheHits;
    private int cacheMisses;

    /**
     * 틱 시작 시 호출.
     */
    public void onTickStart(long gameTick) {
        if (gameTick != currentTick) {
            cache.clear(); // 1틱 TTL 엄수
            currentTick = gameTick;
        }
    }

    /**
     * 충돌 결과 조회.
     * 
     * @param objectA 객체 A ID
     * @param objectB 객체 B ID
     * @return 캐시된 결과 (null = 캐시 미스)
     */
    public Boolean getCollision(int objectA, int objectB) {
        long key = computeKey(objectA, objectB);
        Boolean result = cache.get(key);

        if (result != null) {
            cacheHits++;
        } else {
            cacheMisses++;
        }

        return result;
    }

    /**
     * 충돌 결과 저장.
     */
    public void putCollision(int objectA, int objectB, boolean collides) {
        long key = computeKey(objectA, objectB);
        cache.put(key, collides);
    }

    /**
     * 셀 기반 장애물 조회.
     */
    public Boolean getCellObstacle(int cellX, int cellY) {
        long key = computeCellKey(cellX, cellY);
        Boolean result = cache.get(key);

        if (result != null) {
            cacheHits++;
        } else {
            cacheMisses++;
        }

        return result;
    }

    /**
     * 셀 기반 장애물 저장.
     */
    public void putCellObstacle(int cellX, int cellY, boolean hasObstacle) {
        long key = computeCellKey(cellX, cellY);
        cache.put(key, hasObstacle);
    }

    /**
     * 키 계산 (객체 쌍).
     * 순서 무관하게 동일한 키 생성.
     */
    private long computeKey(int objectA, int objectB) {
        int min = Math.min(objectA, objectB);
        int max = Math.max(objectA, objectB);
        return ((long) min << 32) | (max & 0xFFFFFFFFL);
    }

    /**
     * 키 계산 (셀 좌표).
     */
    private long computeCellKey(int cellX, int cellY) {
        // 음수 좌표 지원을 위해 MSB 설정
        return (1L << 63) | ((long) (cellX + 0x7FFFFFFF) << 32) | ((cellY + 0x7FFFFFFF) & 0xFFFFFFFFL);
    }

    /**
     * 틱 종료 시 호출.
     * TTL = 1틱 엄수.
     */
    public void onTickEnd() {
        cache.clear(); // 무조건 클리어
    }

    // ═══════════════════════════════════════════════════════════════
    // 텔레메트리
    // ═══════════════════════════════════════════════════════════════

    public int getCacheHits() {
        return cacheHits;
    }

    public int getCacheMisses() {
        return cacheMisses;
    }

    public int getCacheSize() {
        return cache.size();
    }

    public double getHitRate() {
        int total = cacheHits + cacheMisses;
        return total > 0 ? (double) cacheHits / total : 0.0;
    }

    public void resetTelemetry() {
        cacheHits = 0;
        cacheMisses = 0;
    }
}
