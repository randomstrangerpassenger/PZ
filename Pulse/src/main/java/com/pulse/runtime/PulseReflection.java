package com.pulse.runtime;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import com.pulse.api.util.ReflectionCache;

/**
 * 안전한 Reflection 유틸리티.
 * 
 * B42에서 클래스/메서드 시그니처가 변경될 수 있으므로
 * Reflection 호출을 안전하게 래핑합니다.
 * 로드맵의 "Reflection Safety Layer" 요구사항을 충족합니다.
 * 
 * <p>
 * v2.0: 내부적으로 {@link ReflectionCache}를 사용하여 캐시를 일원화합니다.
 * </p>
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * // 안전한 메서드 호출
 * Object result = PulseReflection.safeInvoke(player, "getHealth");
 * 
 * // 안전한 필드 접근
 * Object value = PulseReflection.getField(player, "lastHeardSound");
 * 
 * // 메서드 존재 여부 확인
 * if (PulseReflection.methodExists("IsoPlayer", "getNewMethod")) {
 *     // B42 전용 API 사용
 * }
 * }</pre>
 * 
 * @since Pulse 1.2
 * @since Pulse 2.0 - ReflectionCache 통합
 */
public final class PulseReflection {

    // 존재하지 않는 항목 캐시 (반복 실패 방지) - PulseReflection 고유 기능
    private static final Map<String, Boolean> notFoundCache = new ConcurrentHashMap<>();

    private PulseReflection() {
    }

    // ─────────────────────────────────────────────────────────────
    // 클래스 조회
    // ─────────────────────────────────────────────────────────────

    /**
     * 클래스 안전하게 조회
     */
    public static Class<?> findClass(String className) {
        if (notFoundCache.containsKey("class:" + className)) {
            return null;
        }

        Class<?> result = ReflectionCache.getClassOrNull(className, getClassLoader());
        if (result == null) {
            notFoundCache.put("class:" + className, true);
        }
        return result;
    }

    /**
     * 클래스 존재 여부
     */
    public static boolean classExists(String className) {
        return findClass(className) != null;
    }

    // ─────────────────────────────────────────────────────────────
    // 메서드 호출
    // ─────────────────────────────────────────────────────────────

    /**
     * 안전한 메서드 호출 (인자 없음)
     */
    public static Object safeInvoke(Object obj, String methodName) {
        return safeInvoke(obj, methodName, new Object[0]);
    }

    /**
     * 안전한 메서드 호출
     */
    public static Object safeInvoke(Object obj, String methodName, Object... args) {
        if (obj == null || methodName == null) {
            return null;
        }

        String cacheKey = "method:" + obj.getClass().getName() + "." + methodName;
        if (notFoundCache.containsKey(cacheKey)) {
            return null;
        }

        try {
            // 인자 타입 추론
            Class<?>[] paramTypes = new Class<?>[args.length];
            for (int i = 0; i < args.length; i++) {
                paramTypes[i] = args[i] != null ? args[i].getClass() : Object.class;
            }

            Method method = ReflectionCache.getMethodOrNull(obj.getClass(), methodName, paramTypes);
            if (method == null) {
                // 파라미터 타입 무시하고 이름만으로 검색
                method = findMethodByName(obj.getClass(), methodName, args.length);
            }

            if (method != null) {
                return method.invoke(obj, args);
            } else {
                notFoundCache.put(cacheKey, true);
                return null;
            }
        } catch (Exception e) {
            // 조용히 실패
            return null;
        }
    }

    /**
     * 메서드 존재 여부
     */
    public static boolean methodExists(String className, String methodName) {
        Class<?> clazz = findClass(className);
        if (clazz == null)
            return false;

        for (Method m : clazz.getDeclaredMethods()) {
            if (m.getName().equals(methodName)) {
                return true;
            }
        }
        return false;
    }

    private static Method findMethodByName(Class<?> clazz, String name, int paramCount) {
        for (Method m : clazz.getMethods()) {
            if (m.getName().equals(name) && m.getParameterCount() == paramCount) {
                m.setAccessible(true);
                return m;
            }
        }
        return null;
    }

    // ─────────────────────────────────────────────────────────────
    // 필드 접근
    // ─────────────────────────────────────────────────────────────

    /**
     * 필드 값 안전하게 읽기
     */
    public static Object getField(Object obj, String fieldName) {
        if (obj == null || fieldName == null) {
            return null;
        }

        String cacheKey = "field:" + obj.getClass().getName() + "." + fieldName;
        if (notFoundCache.containsKey(cacheKey)) {
            return null;
        }

        try {
            Field field = findFieldInHierarchy(obj.getClass(), fieldName);
            if (field != null) {
                return field.get(obj);
            } else {
                notFoundCache.put(cacheKey, true);
                return null;
            }
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 클래스의 필드 조회 (static 포함)
     */
    public static Object findField(String className, String fieldName) {
        Class<?> clazz = findClass(className);
        if (clazz == null)
            return null;

        try {
            Field field = findFieldInHierarchy(clazz, fieldName);
            if (field != null) {
                return field.get(null); // static 필드
            }
        } catch (Exception e) {
            // pass
        }
        return null;
    }

    /**
     * 필드 존재 여부
     */
    public static boolean fieldExists(String className, String fieldName) {
        Class<?> clazz = findClass(className);
        return clazz != null && findFieldInHierarchy(clazz, fieldName) != null;
    }

    private static Field findFieldInHierarchy(Class<?> clazz, String name) {
        // ReflectionCache 먼저 시도
        try {
            return ReflectionCache.getField(clazz, name);
        } catch (NoSuchFieldException e) {
            // 부모 클래스 검색
            Class<?> parent = clazz.getSuperclass();
            if (parent != null) {
                return findFieldInHierarchy(parent, name);
            }
            return null;
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 유틸리티
    // ─────────────────────────────────────────────────────────────

    /**
     * 캐시 초기화
     */
    public static void clearCaches() {
        notFoundCache.clear();
        // ReflectionCache는 전역 캐시이므로 여기서 초기화하지 않음
        // ReflectionCache.clearAll()은 필요시 별도 호출
    }

    /**
     * 캐시 통계
     */
    public static String getCacheStats() {
        return String.format("PulseReflection: notFound=%d, ReflectionCache: methods=%d, fields=%d, classes=%d",
                notFoundCache.size(),
                ReflectionCache.getMethodCacheSize(),
                ReflectionCache.getFieldCacheSize(),
                ReflectionCache.getClassCacheSize());
    }

    private static ClassLoader getClassLoader() {
        ClassLoader loader = Thread.currentThread().getContextClassLoader();
        return loader != null ? loader : ClassLoader.getSystemClassLoader();
    }
}
