package com.pulse.api.util;

import com.pulse.PulseEnvironment;

import java.lang.reflect.Field;
import java.lang.reflect.Method;

/**
 * 리플렉션 유틸리티.
 * GameAccess에서 분리된 범용 리플렉션 기능.
 * 
 * @since 1.1.0
 */
public final class ReflectionUtil {

    private ReflectionUtil() {
    }

    /**
     * 리플렉션으로 정적 필드 값 가져오기
     */
    public static Object getStaticField(String className, String fieldName) {
        try {
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();

            Class<?> clazz = loader.loadClass(className);
            Field field = clazz.getDeclaredField(fieldName);
            field.setAccessible(true);
            return field.get(null);
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 리플렉션으로 정적 메서드 호출
     */
    public static Object invokeStaticMethod(String className, String methodName, Object... args) {
        try {
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();

            Class<?> clazz = loader.loadClass(className);

            // 인자 없는 메서드
            if (args.length == 0) {
                Method method = clazz.getMethod(methodName);
                return method.invoke(null);
            }

            // 인자 타입 추론
            Class<?>[] argTypes = new Class<?>[args.length];
            for (int i = 0; i < args.length; i++) {
                argTypes[i] = args[i] != null ? args[i].getClass() : Object.class;
            }

            Method method = clazz.getMethod(methodName, argTypes);
            return method.invoke(null, args);
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 게임 클래스 로드
     */
    public static Class<?> getGameClass(String className) {
        try {
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
            if (loader == null)
                loader = ClassLoader.getSystemClassLoader();
            return loader.loadClass(className);
        } catch (ClassNotFoundException e) {
            return null;
        }
    }
}
