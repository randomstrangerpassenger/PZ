package com.pulse.api.util;

import com.pulse.PulseEnvironment;

import com.pulse.api.exception.ReflectionException;

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
            Class<?> clazz = ReflectionCache.getClassOrThrow(className, getLoader());
            Field field = ReflectionCache.getFieldOrThrow(clazz, fieldName);
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
            Class<?> clazz = ReflectionCache.getClassOrThrow(className, getLoader());
            Class<?>[] argTypes = getArgTypes(args);
            Method method = ReflectionCache.getMethodOrThrow(clazz, methodName, argTypes);
            return method.invoke(null, args);
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 게임 클래스 로드
     */
    public static Class<?> getGameClass(String className) {
        return ReflectionCache.getClassOrNull(className, getLoader());
    }

    /**
     * 리플렉션으로 정적 필드 값 가져오기 (예외 발생)
     * 
     * @throws com.pulse.api.exception.PulseException 실패 시
     */
    public static Object getStaticFieldOrThrow(String className, String fieldName) {
        try {
            Class<?> clazz = ReflectionCache.getClassOrThrow(className, getLoader());
            Field field = ReflectionCache.getFieldOrThrow(clazz, fieldName);
            return field.get(null);
        } catch (Exception e) {
            throw new ReflectionException("Failed to get static field: " + className + "." + fieldName, e);
        }
    }

    /**
     * 리플렉션으로 정적 메서드 호출 (예외 발생)
     * 
     * @throws com.pulse.api.exception.PulseException 실패 시
     */
    public static Object invokeStaticMethodOrThrow(String className, String methodName, Object... args) {
        try {
            Class<?> clazz = ReflectionCache.getClassOrThrow(className, getLoader());
            Class<?>[] argTypes = getArgTypes(args);
            Method method = ReflectionCache.getMethodOrThrow(clazz, methodName, argTypes);
            return method.invoke(null, args);
        } catch (Exception e) {
            throw new ReflectionException("Failed to invoke static method: " + className + "." + methodName, e);
        }
    }

    /**
     * 게임 클래스 로드 (예외 발생)
     * 
     * @throws com.pulse.api.exception.PulseException 실패 시
     */
    public static Class<?> getGameClassOrThrow(String className) {
        try {
            return ReflectionCache.getClassOrThrow(className, getLoader());
        } catch (Exception e) {
            throw new ReflectionException("Game class not found: " + className, e);
        }
    }

    private static ClassLoader getLoader() {
        ClassLoader loader = PulseEnvironment.getGameClassLoader();
        return loader != null ? loader : ClassLoader.getSystemClassLoader();
    }

    private static Class<?>[] getArgTypes(Object... args) {
        if (args == null || args.length == 0) {
            return new Class<?>[0];
        }
        Class<?>[] argTypes = new Class<?>[args.length];
        for (int i = 0; i < args.length; i++) {
            argTypes[i] = args[i] != null ? args[i].getClass() : Object.class;
        }
        return argTypes;
    }
}
