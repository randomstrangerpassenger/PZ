package com.pulse.runtime;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 안전한 Reflection 유틸리티.
 * 
 * B42에서 클래스/메서드 시그니처가 변경될 수 있으므로
 * Reflection 호출을 안전하게 래핑합니다.
 * 로드맵의 "Reflection Safety Layer" 요구사항을 충족합니다.
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
 */
public final class PulseReflection {

    // 클래스 캐시
    private static final Map<String, Class<?>> classCache = new ConcurrentHashMap<>();

    // 메서드 캐시
    private static final Map<String, Method> methodCache = new ConcurrentHashMap<>();

    // 필드 캐시
    private static final Map<String, Field> fieldCache = new ConcurrentHashMap<>();

    // 존재하지 않는 항목 캐시 (반복 실패 방지)
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

        return classCache.computeIfAbsent(className, name -> {
            try {
                return Class.forName(name);
            } catch (ClassNotFoundException e) {
                notFoundCache.put("class:" + name, true);
                return null;
            }
        });
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
        return safeInvoke(obj, methodName, (Object[]) new Class<?>[0]);
    }

    /**
     * 안전한 메서드 호출
     */
    public static Object safeInvoke(Object obj, String methodName, Object... args) {
        if (obj == null || methodName == null) {
            return null;
        }

        String cacheKey = obj.getClass().getName() + "." + methodName;
        if (notFoundCache.containsKey("method:" + cacheKey)) {
            return null;
        }

        try {
            Method method = methodCache.get(cacheKey);
            if (method == null) {
                // 인자 타입 추론
                Class<?>[] paramTypes = new Class<?>[args.length];
                for (int i = 0; i < args.length; i++) {
                    paramTypes[i] = args[i] != null ? args[i].getClass() : Object.class;
                }

                method = findMethod(obj.getClass(), methodName, paramTypes);
                if (method != null) {
                    method.setAccessible(true);
                    methodCache.put(cacheKey, method);
                } else {
                    notFoundCache.put("method:" + cacheKey, true);
                    return null;
                }
            }
            return method.invoke(obj, args);
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

    private static Method findMethod(Class<?> clazz, String name, Class<?>[] paramTypes) {
        try {
            return clazz.getMethod(name, paramTypes);
        } catch (NoSuchMethodException e) {
            // 부모 클래스에서도 검색
            try {
                return clazz.getDeclaredMethod(name, paramTypes);
            } catch (NoSuchMethodException e2) {
                // 파라미터 타입 무시하고 이름만으로 검색
                for (Method m : clazz.getMethods()) {
                    if (m.getName().equals(name) && m.getParameterCount() == paramTypes.length) {
                        return m;
                    }
                }
                return null;
            }
        }
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

        String cacheKey = obj.getClass().getName() + "." + fieldName;
        if (notFoundCache.containsKey("field:" + cacheKey)) {
            return null;
        }

        try {
            Field field = fieldCache.get(cacheKey);
            if (field == null) {
                field = findField(obj.getClass(), fieldName);
                if (field != null) {
                    field.setAccessible(true);
                    fieldCache.put(cacheKey, field);
                } else {
                    notFoundCache.put("field:" + cacheKey, true);
                    return null;
                }
            }
            return field.get(obj);
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
            Field field = findField(clazz, fieldName);
            if (field != null) {
                field.setAccessible(true);
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
        return clazz != null && findField(clazz, fieldName) != null;
    }

    private static Field findField(Class<?> clazz, String name) {
        try {
            return clazz.getField(name);
        } catch (NoSuchFieldException e) {
            try {
                return clazz.getDeclaredField(name);
            } catch (NoSuchFieldException e2) {
                // 부모 클래스 검색
                Class<?> parent = clazz.getSuperclass();
                if (parent != null) {
                    return findField(parent, name);
                }
                return null;
            }
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 유틸리티
    // ─────────────────────────────────────────────────────────────

    /**
     * 캐시 초기화
     */
    public static void clearCaches() {
        classCache.clear();
        methodCache.clear();
        fieldCache.clear();
        notFoundCache.clear();
    }

    /**
     * 캐시 통계
     */
    public static String getCacheStats() {
        return String.format("PulseReflection Cache: classes=%d, methods=%d, fields=%d, notFound=%d",
                classCache.size(), methodCache.size(), fieldCache.size(), notFoundCache.size());
    }
}
