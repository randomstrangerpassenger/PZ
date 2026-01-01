package com.pulse.api.profiler;

import java.lang.reflect.Method;

/**
 * SubProfiler Hook API
 * 
 * Echo의 SubProfiler를 Pulse Mixin에서 호출하기 위한 인터페이스.
 * 
 * <p>
 * <b>ClassLoader 분리 해결 (v2.2):</b>
 * </p>
 * Mixin(AppClassLoader)과 Echo(URLClassLoader)가 다른 ClassLoader에서
 * 로드되어 static 필드가 공유되지 않는 문제를 해결합니다.
 * 
 * <p>
 * 해결 방식:
 * </p>
 * <ul>
 * <li>callback을 Object 타입으로 저장 (ClassLoader 독립적)</li>
 * <li>start()/end() 호출 시 Reflection으로 callback 메서드 호출</li>
 * <li>Echo가 setCallback 시 모든 ClassLoader의 SubProfilerHook에 등록</li>
 * </ul>
 * 
 * @since Pulse 1.1 / Echo 1.0
 * @since Pulse 2.2 - ClassLoader-agnostic callback via Object + Reflection
 */
public final class SubProfilerHook {

    /**
     * Callback 저장 (Object 타입으로 ClassLoader 독립적)
     */
    private static volatile Object callbackObj = null;

    /**
     * Cached reflection methods
     */
    private static volatile Method cachedStartMethod = null;
    private static volatile Method cachedEndMethod = null;

    private SubProfilerHook() {
    }

    /**
     * 콜백 등록 (Echo 초기화 시 호출됨)
     * Object 타입으로 받아서 ClassLoader 경계를 넘어 저장합니다.
     */
    public static void setCallback(ISubProfilerCallback cb) {
        setCallbackObject(cb);
    }

    /**
     * Object 타입으로 콜백 등록 (Reflection용)
     * Echo에서 이 메서드를 Reflection으로 호출하여 다른 ClassLoader에도 등록합니다.
     */
    public static void setCallbackObject(Object cb) {
        callbackObj = cb;
        // Cache 무효화
        cachedStartMethod = null;
        cachedEndMethod = null;
    }

    /**
     * 콜백 해제
     */
    public static void clearCallback() {
        callbackObj = null;
        cachedStartMethod = null;
        cachedEndMethod = null;
    }

    /**
     * SubTiming 측정 시작
     * Reflection으로 callback의 start() 메서드를 호출합니다.
     * 
     * @param label SubLabel 이름 (예: "ZOMBIE_UPDATE", "PATHFINDING")
     * @return 시작 시간 (나노초), 비활성화 시 -1
     */
    public static long start(String label) {
        Object cb = callbackObj;
        if (cb == null) {
            return -1;
        }

        try {
            Method startMethod = cachedStartMethod;
            if (startMethod == null) {
                startMethod = cb.getClass().getMethod("start", String.class);
                startMethod.setAccessible(true);
                cachedStartMethod = startMethod;
            }

            Object result = startMethod.invoke(cb, label);
            if (result instanceof Long) {
                return (Long) result;
            }
            return -1;
        } catch (Exception e) {
            return -1;
        }
    }

    /**
     * SubTiming 측정 종료
     * 
     * @param label     SubLabel 이름
     * @param startTime start()에서 반환받은 시작 시간
     */
    public static void end(String label, long startTime) {
        if (startTime < 0) {
            return;
        }

        Object cb = callbackObj;
        if (cb == null) {
            return;
        }

        try {
            Method endMethod = cachedEndMethod;
            if (endMethod == null) {
                endMethod = cb.getClass().getMethod("end", String.class, long.class);
                endMethod.setAccessible(true);
                cachedEndMethod = endMethod;
            }

            endMethod.invoke(cb, label, startTime);
        } catch (Exception e) {
            // Silently fail
        }
    }

    /**
     * SubProfiler 콜백 인터페이스
     */
    public interface ISubProfilerCallback {
        long start(String label);

        void end(String label, long startTime);
    }
}
