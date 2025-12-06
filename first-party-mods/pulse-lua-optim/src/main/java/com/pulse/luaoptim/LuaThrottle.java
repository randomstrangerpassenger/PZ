package com.pulse.luaoptim;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Lua 함수 호출 쓰로틀링 유틸리티.
 * 마지막 실행 시간을 추적하여 너무 자주 호출되는 것을 방지.
 */
public class LuaThrottle {

    private static final Map<String, Long> lastExecutionTime = new ConcurrentHashMap<>();

    /**
     * 해당 키의 함수가 지금 실행 가능한지 확인 (쓰로틀링 체크)
     * 
     * @param key           식별자 (보통 함수 이름)
     * @param minIntervalMs 최소 실행 간격 (밀리초)
     * @return 실행 가능하면 true, 쓰로틀링 걸리면 false
     */
    public static boolean check(String key, long minIntervalMs) {
        if (!LuaOptimConfig.enableThrottling)
            return true;

        long now = System.currentTimeMillis();
        long last = lastExecutionTime.getOrDefault(key, 0L);

        if (now - last >= minIntervalMs) {
            lastExecutionTime.put(key, now);
            return true;
        }

        return false;
    }

    public static void clear() {
        lastExecutionTime.clear();
    }
}
