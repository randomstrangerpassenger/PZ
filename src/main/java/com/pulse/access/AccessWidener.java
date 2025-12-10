package com.pulse.access;

import java.lang.reflect.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 접근 확장기 (Access Widener).
 * 게임 클래스의 private/protected 멤버에 대한 접근을 제공.
 * 
 * Fabric의 Access Widener와 유사하지만 리플렉션 기반으로 런타임에 동작.
 * 
 * 사용 예:
 * 
 * <pre>
 * // 클래스 접근
 * Class<?> clazz = AccessWidener.getClass("zombie.inventory.ItemContainer");
 * 
 * // 필드 접근
 * Object value = AccessWidener.getField(instance, "privateField");
 * AccessWidener.setField(instance, "privateField", newValue);
 * 
 * // 메서드 호출
 * Object result = AccessWidener.invoke(instance, "privateMethod", arg1, arg2);
 * 
 * // 생성자 호출
 * Object instance = AccessWidener.newInstance("zombie.SomeClass", arg1);
 * </pre>
 */
public class AccessWidener {

    private static final AccessWidener INSTANCE = new AccessWidener();

    // 캐시
    private final Map<String, Class<?>> classCache = new ConcurrentHashMap<>();
    private final Map<String, Field> fieldCache = new ConcurrentHashMap<>();
    private final Map<String, Method> methodCache = new ConcurrentHashMap<>();
    private final Map<String, Constructor<?>> constructorCache = new ConcurrentHashMap<>();

    // 게임 클래스로더
    private ClassLoader gameClassLoader;

    private AccessWidener() {
    }

    public static AccessWidener getInstance() {
        return INSTANCE;
    }

    /**
     * 게임 클래스로더 설정
     */
    public static void setGameClassLoader(ClassLoader loader) {
        INSTANCE.gameClassLoader = loader;
    }

    // ─────────────────────────────────────────────────────────────
    // 클래스 접근
    // ─────────────────────────────────────────────────────────────

    /**
     * 클래스 가져오기
     */
    public static Class<?> getClass(String className) {
        return INSTANCE.loadClass(className);
    }

    private Class<?> loadClass(String className) {
        return classCache.computeIfAbsent(className, name -> {
            try {
                ClassLoader loader = gameClassLoader != null ? gameClassLoader : ClassLoader.getSystemClassLoader();
                return loader.loadClass(name);
            } catch (ClassNotFoundException e) {
                System.err.println("[Pulse/Access] Class not found: " + name);
                return null;
            }
        });
    }

    // ─────────────────────────────────────────────────────────────
    // 필드 접근
    // ─────────────────────────────────────────────────────────────

    /**
     * 필드 값 가져오기
     */
    public static Object getField(Object instance, String fieldName) {
        return INSTANCE.getFieldValue(instance, fieldName);
    }

    /**
     * 정적 필드 값 가져오기
     */
    public static Object getStaticField(Class<?> clazz, String fieldName) {
        return INSTANCE.getFieldValue(clazz, null, fieldName);
    }

    /**
     * 정적 필드 값 가져오기 (클래스명)
     */
    public static Object getStaticField(String className, String fieldName) {
        Class<?> clazz = getClass(className);
        if (clazz == null)
            return null;
        return INSTANCE.getFieldValue(clazz, null, fieldName);
    }

    /**
     * 필드 값 설정
     */
    public static void setField(Object instance, String fieldName, Object value) {
        INSTANCE.setFieldValue(instance, fieldName, value);
    }

    /**
     * 정적 필드 값 설정
     */
    public static void setStaticField(Class<?> clazz, String fieldName, Object value) {
        INSTANCE.setFieldValue(clazz, null, fieldName, value);
    }

    private Object getFieldValue(Object instance, String fieldName) {
        if (instance == null)
            return null;
        return getFieldValue(instance.getClass(), instance, fieldName);
    }

    private Object getFieldValue(Class<?> clazz, Object instance, String fieldName) {
        Field field = findField(clazz, fieldName);
        if (field == null)
            return null;

        try {
            return field.get(instance);
        } catch (IllegalAccessException e) {
            System.err.println("[Pulse/Access] Cannot access field: " + fieldName);
            return null;
        }
    }

    private void setFieldValue(Object instance, String fieldName, Object value) {
        if (instance == null)
            return;
        setFieldValue(instance.getClass(), instance, fieldName, value);
    }

    private void setFieldValue(Class<?> clazz, Object instance, String fieldName, Object value) {
        Field field = findField(clazz, fieldName);
        if (field == null)
            return;

        try {
            // final 필드도 수정 가능하게
            if (Modifier.isFinal(field.getModifiers())) {
                Field modifiersField = Field.class.getDeclaredField("modifiers");
                modifiersField.setAccessible(true);
                modifiersField.setInt(field, field.getModifiers() & ~Modifier.FINAL);
            }
            field.set(instance, value);
        } catch (Exception e) {
            System.err.println("[Pulse/Access] Cannot set field: " + fieldName);
        }
    }

    private Field findField(Class<?> clazz, String fieldName) {
        String key = clazz.getName() + "#" + fieldName;
        return fieldCache.computeIfAbsent(key, k -> {
            Class<?> current = clazz;
            while (current != null) {
                try {
                    Field field = current.getDeclaredField(fieldName);
                    field.setAccessible(true);
                    return field;
                } catch (NoSuchFieldException e) {
                    current = current.getSuperclass();
                }
            }
            System.err.println("[Pulse/Access] Field not found: " + fieldName);
            return null;
        });
    }

    // ─────────────────────────────────────────────────────────────
    // 메서드 호출
    // ─────────────────────────────────────────────────────────────

    /**
     * 메서드 호출
     */
    public static Object invoke(Object instance, String methodName, Object... args) {
        return INSTANCE.invokeMethod(instance, methodName, args);
    }

    /**
     * 정적 메서드 호출
     */
    public static Object invokeStatic(Class<?> clazz, String methodName, Object... args) {
        return INSTANCE.invokeMethod(clazz, null, methodName, args);
    }

    /**
     * 정적 메서드 호출 (클래스명)
     */
    public static Object invokeStatic(String className, String methodName, Object... args) {
        Class<?> clazz = getClass(className);
        if (clazz == null)
            return null;
        return INSTANCE.invokeMethod(clazz, null, methodName, args);
    }

    private Object invokeMethod(Object instance, String methodName, Object... args) {
        if (instance == null)
            return null;
        return invokeMethod(instance.getClass(), instance, methodName, args);
    }

    private Object invokeMethod(Class<?> clazz, Object instance, String methodName, Object... args) {
        Method method = findMethod(clazz, methodName, args);
        if (method == null)
            return null;

        try {
            return method.invoke(instance, args);
        } catch (Exception e) {
            System.err.println("[Pulse/Access] Cannot invoke method: " + methodName);
            e.printStackTrace();
            return null;
        }
    }

    private Method findMethod(Class<?> clazz, String methodName, Object... args) {
        // 간단한 캐시 키 생성
        StringBuilder keyBuilder = new StringBuilder(clazz.getName());
        keyBuilder.append("#").append(methodName).append("(");
        for (Object arg : args) {
            if (arg != null) {
                keyBuilder.append(arg.getClass().getName()).append(",");
            } else {
                keyBuilder.append("null,");
            }
        }
        keyBuilder.append(")");
        String key = keyBuilder.toString();

        return methodCache.computeIfAbsent(key, k -> {
            Class<?> current = clazz;
            while (current != null) {
                for (Method method : current.getDeclaredMethods()) {
                    if (method.getName().equals(methodName) &&
                            isCompatible(method.getParameterTypes(), args)) {
                        method.setAccessible(true);
                        return method;
                    }
                }
                current = current.getSuperclass();
            }
            System.err.println("[Pulse/Access] Method not found: " + methodName);
            return null;
        });
    }

    private boolean isCompatible(Class<?>[] paramTypes, Object[] args) {
        if (paramTypes.length != args.length)
            return false;
        for (int i = 0; i < paramTypes.length; i++) {
            if (args[i] != null && !isAssignable(paramTypes[i], args[i].getClass())) {
                return false;
            }
        }
        return true;
    }

    private boolean isAssignable(Class<?> target, Class<?> source) {
        if (target.isAssignableFrom(source))
            return true;
        // 기본형 처리
        if (target.isPrimitive()) {
            if (target == int.class && source == Integer.class)
                return true;
            if (target == long.class && source == Long.class)
                return true;
            if (target == double.class && source == Double.class)
                return true;
            if (target == float.class && source == Float.class)
                return true;
            if (target == boolean.class && source == Boolean.class)
                return true;
            if (target == byte.class && source == Byte.class)
                return true;
            if (target == short.class && source == Short.class)
                return true;
            if (target == char.class && source == Character.class)
                return true;
        }
        return false;
    }

    // ─────────────────────────────────────────────────────────────
    // 생성자
    // ─────────────────────────────────────────────────────────────

    /**
     * 인스턴스 생성
     */
    public static Object newInstance(String className, Object... args) {
        Class<?> clazz = getClass(className);
        if (clazz == null)
            return null;
        return INSTANCE.createInstance(clazz, args);
    }

    /**
     * 인스턴스 생성
     */
    public static Object newInstance(Class<?> clazz, Object... args) {
        return INSTANCE.createInstance(clazz, args);
    }

    private Object createInstance(Class<?> clazz, Object... args) {
        try {
            if (args.length == 0) {
                Constructor<?> constructor = clazz.getDeclaredConstructor();
                constructor.setAccessible(true);
                return constructor.newInstance();
            }

            // 적합한 생성자 찾기
            for (Constructor<?> constructor : clazz.getDeclaredConstructors()) {
                if (isCompatible(constructor.getParameterTypes(), args)) {
                    constructor.setAccessible(true);
                    return constructor.newInstance(args);
                }
            }

            System.err.println("[Pulse/Access] No matching constructor found");
            return null;
        } catch (Exception e) {
            System.err.println("[Pulse/Access] Cannot create instance of: " + clazz.getName());
            e.printStackTrace();
            return null;
        }
    }

    /**
     * 캐시 비우기
     */
    public static void clearCache() {
        INSTANCE.classCache.clear();
        INSTANCE.fieldCache.clear();
        INSTANCE.methodCache.clear();
        INSTANCE.constructorCache.clear();
    }
}
