package com.pulse.luaoptim;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Lua 결과 캐싱 유틸리티.
 * 무거운 계산 결과를 재사용.
 */
public class LuaCache {

    private static final Map<String, CacheEntry> cache = new ConcurrentHashMap<>();

    private static class CacheEntry {
        final Object value;
        final long timestamp;

        CacheEntry(Object value) {
            this.value = value;
            this.timestamp = System.currentTimeMillis();
        }
    }

    /**
     * 캐시에서 값 가져오기
     */
    public static Object get(String key, long ttlMs) {
        if (!LuaOptimConfig.enableCaching)
            return null;

        CacheEntry entry = cache.get(key);
        if (entry == null)
            return null;

        if (System.currentTimeMillis() - entry.timestamp > ttlMs) {
            cache.remove(key); // 만료
            return null;
        }

        return entry.value;
    }

    /**
     * 값 캐싱
     */
    public static void put(String key, Object value) {
        if (!LuaOptimConfig.enableCaching)
            return;
        cache.put(key, new CacheEntry(value));
    }

    public static void clear() {
        cache.clear();
    }
}
