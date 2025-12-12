package com.pulse.api.util;

import java.lang.reflect.Method;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 리플렉션 캐시.
 * Method 조회 결과를 캐싱하여 반복적인 리플렉션 호출 성능을 개선합니다.
 * 
 * <p>
 * Thread-safe: ConcurrentHashMap + computeIfAbsent로 원자성 보장
 * </p>
 * 
 * @since 1.1.0
 */
public final class ReflectionCache {

    private ReflectionCache() {
    }

    // Method 캐시: "className.methodName(paramTypes...)" → Method
    private static final Map<String, Method> METHOD_CACHE = new ConcurrentHashMap<>();

    // Class 캐시: className → Class
    private static final Map<String, Class<?>> CLASS_CACHE = new ConcurrentHashMap<>();

    /**
     * 캐시된 Method 조회.
     * 
     * @param cls    대상 클래스
     * @param name   메서드 이름
     * @param params 파라미터 타입
     * @return Method 객체
     * @throws NoSuchMethodException 메서드가 없으면 발생
     */
    public static Method getMethod(Class<?> cls, String name, Class<?>... params)
            throws NoSuchMethodException {
        String key = buildMethodKey(cls, name, params);

        // computeIfAbsent로 원자적 조회/삽입 보장
        Method cached = METHOD_CACHE.computeIfAbsent(key, k -> {
            try {
                Method m = cls.getMethod(name, params);
                m.setAccessible(true);
                return m;
            } catch (NoSuchMethodException e) {
                return null; // 예외를 값으로 저장 불가, null 반환
            }
        });

        if (cached == null) {
            throw new NoSuchMethodException(cls.getName() + "." + name);
        }
        return cached;
    }

    /**
     * 캐시된 Method 조회 (Optional 스타일).
     */
    public static Method getMethodOrNull(Class<?> cls, String name, Class<?>... params) {
        try {
            return getMethod(cls, name, params);
        } catch (NoSuchMethodException e) {
            return null;
        }
    }

    /**
     * 캐시된 Class 조회.
     * 
     * @param className 클래스 전체 경로
     * @param loader    클래스 로더
     * @return Class 객체
     * @throws ClassNotFoundException 클래스가 없으면 발생
     */
    public static Class<?> getClass(String className, ClassLoader loader)
            throws ClassNotFoundException {
        Class<?> cached = CLASS_CACHE.computeIfAbsent(className, k -> {
            try {
                return loader.loadClass(className);
            } catch (ClassNotFoundException e) {
                return null;
            }
        });

        if (cached == null) {
            throw new ClassNotFoundException(className);
        }
        return cached;
    }

    /**
     * 캐시된 Class 조회 (Optional 스타일).
     */
    public static Class<?> getClassOrNull(String className, ClassLoader loader) {
        try {
            return getClass(className, loader);
        } catch (ClassNotFoundException e) {
            return null;
        }
    }

    /**
     * 캐시 통계 (디버깅용).
     */
    public static int getMethodCacheSize() {
        return METHOD_CACHE.size();
    }

    public static int getClassCacheSize() {
        return CLASS_CACHE.size();
    }

    /**
     * 캐시 전체 초기화.
     */
    public static void clearAll() {
        METHOD_CACHE.clear();
        CLASS_CACHE.clear();
    }

    private static String buildMethodKey(Class<?> cls, String name, Class<?>... params) {
        StringBuilder sb = new StringBuilder();
        sb.append(cls.getName()).append('.').append(name).append('(');
        for (int i = 0; i < params.length; i++) {
            if (i > 0)
                sb.append(',');
            sb.append(params[i].getName());
        }
        sb.append(')');
        return sb.toString();
    }
}
