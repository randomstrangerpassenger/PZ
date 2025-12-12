package com.pulse.api.util;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import com.pulse.api.exception.ReflectionException;

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

    // Field 캐시: "className.fieldName" → Field
    private static final Map<String, Field> FIELD_CACHE = new ConcurrentHashMap<>();

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
     * 캐시된 Method 조회 (예외 발생).
     */
    public static Method getMethodOrThrow(Class<?> cls, String name, Class<?>... params) {
        try {
            return getMethod(cls, name, params);
        } catch (NoSuchMethodException e) {
            throw new ReflectionException("Method not found: " + cls.getName() + "." + name, e);
        }
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
     * 캐시된 Field 조회.
     *
     * @param cls  대상 클래스
     * @param name 필드 이름
     * @return Field 객체
     * @throws NoSuchFieldException 필드가 없으면 발생
     */
    public static Field getField(Class<?> cls, String name) throws NoSuchFieldException {
        String key = cls.getName() + "." + name;

        Field cached = FIELD_CACHE.computeIfAbsent(key, k -> {
            try {
                Field f = cls.getDeclaredField(name);
                f.setAccessible(true);
                return f;
            } catch (NoSuchFieldException e) {
                return null;
            }
        });

        if (cached == null) {
            throw new NoSuchFieldException(cls.getName() + "." + name);
        }
        return cached;
    }

    public static Field getFieldOrThrow(Class<?> cls, String name) {
        try {
            return getField(cls, name);
        } catch (NoSuchFieldException e) {
            throw new ReflectionException("Field not found: " + cls.getName() + "." + name, e);
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
     * 캐시된 Class 조회 (예외 발생).
     */
    public static Class<?> getClassOrThrow(String className, ClassLoader loader) {
        try {
            return getClass(className, loader);
        } catch (ClassNotFoundException e) {
            throw new ReflectionException("Class not found: " + className, e);
        }
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

    public static int getFieldCacheSize() {
        return FIELD_CACHE.size();
    }

    /**
     * 캐시 전체 초기화.
     */
    public static void clearAll() {
        METHOD_CACHE.clear();
        FIELD_CACHE.clear();
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
