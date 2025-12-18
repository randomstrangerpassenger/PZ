package com.fuse.cache;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Zombie State Cache for Fuse Optimization.
 * 
 * IsoZombie 상태를 캐싱하여 throttle 정책에 활용합니다.
 * - FakeDead, Eating 상태 좀비는 더 공격적으로 throttle
 * - 플레이어 근처 좀비는 throttle 면제
 * 
 * @since Fuse 0.3.1
 */
public class ZombieStateCache {

    private static final ZombieStateCache INSTANCE = new ZombieStateCache();
    private static final int MAX_CACHE_SIZE = 10000;

    /** 좀비 ID → 상태 캐시 */
    private final ConcurrentHashMap<Integer, ZombieState> stateCache = new ConcurrentHashMap<>();

    /** 통계 */
    private final AtomicInteger cacheHits = new AtomicInteger(0);
    private final AtomicInteger cacheMisses = new AtomicInteger(0);

    public static ZombieStateCache getInstance() {
        return INSTANCE;
    }

    /**
     * 좀비 상태 업데이트
     */
    public void updateState(int zombieId, ZombieState state) {
        if (stateCache.size() > MAX_CACHE_SIZE) {
            evictOldEntries();
        }
        stateCache.put(zombieId, state);
    }

    /**
     * 좀비 상태 조회
     */
    public ZombieState getState(int zombieId) {
        ZombieState state = stateCache.get(zombieId);
        if (state != null) {
            cacheHits.incrementAndGet();
            return state;
        }
        cacheMisses.incrementAndGet();
        return ZombieState.UNKNOWN;
    }

    /**
     * 좀비 제거 (사망 시)
     */
    public void removeZombie(int zombieId) {
        stateCache.remove(zombieId);
    }

    /**
     * 캐시 정리
     */
    private void evictOldEntries() {
        // 절반 제거 (LRU 대신 간단한 랜덤 제거)
        int toRemove = stateCache.size() / 2;
        stateCache.keySet().stream()
                .limit(toRemove)
                .forEach(stateCache::remove);
    }

    /**
     * 캐시 통계
     */
    public float getHitRatio() {
        int total = cacheHits.get() + cacheMisses.get();
        return total == 0 ? 0f : (float) cacheHits.get() / total;
    }

    public void reset() {
        stateCache.clear();
        cacheHits.set(0);
        cacheMisses.set(0);
    }

    public int getCacheSize() {
        return stateCache.size();
    }

    // --- Zombie State Enum ---

    public enum ZombieState {
        UNKNOWN(1.0f), // 기본 - 일반 throttle
        IDLE(1.5f), // 대기 중 - 더 공격적 throttle
        FAKE_DEAD(2.0f), // 누워있음 - 매우 공격적 throttle
        EATING(1.8f), // 시체 섭취 - 공격적 throttle
        ALERT(0.5f), // 경계 상태 - 덜 throttle
        CHASING(0.0f), // 추격 중 - throttle 면제
        ATTACKING(0.0f); // 공격 중 - throttle 면제

        /** Throttle 배수 (높을수록 더 공격적으로 throttle) */
        public final float throttleMultiplier;

        ZombieState(float throttleMultiplier) {
            this.throttleMultiplier = throttleMultiplier;
        }

        /**
         * 이 상태에서 throttle 가능 여부
         */
        public boolean canThrottle() {
            return throttleMultiplier > 0.0f;
        }
    }
}
