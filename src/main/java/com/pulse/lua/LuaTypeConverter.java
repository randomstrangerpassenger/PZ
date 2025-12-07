package com.pulse.lua;

import java.util.List;
import java.util.Map;

/**
 * Java ↔ Lua 타입 변환기.
 * 양방향으로 타입을 안전하게 변환.
 */
public class LuaTypeConverter {

    private LuaTypeConverter() {
    }

    // ─────────────────────────────────────────────────────────────
    // Java → Lua
    // ─────────────────────────────────────────────────────────────

    /**
     * Java 객체를 Lua 호환 객체로 변환.
     */
    public static Object javaToLua(Object javaValue) {
        if (javaValue == null) {
            return null;
        }

        // 기본 타입은 그대로 전달 (Kahlua가 처리)
        if (javaValue instanceof String ||
                javaValue instanceof Number ||
                javaValue instanceof Boolean) {
            return javaValue;
        }

        // 배열 → Lua 테이블 (인덱스 1부터)
        if (javaValue.getClass().isArray()) {
            return arrayToLuaTable(javaValue);
        }

        // List → Lua 테이블
        if (javaValue instanceof List<?>) {
            return listToLuaTable((List<?>) javaValue);
        }

        // Map → Lua 테이블
        if (javaValue instanceof Map<?, ?>) {
            return mapToLuaTable((Map<?, ?>) javaValue);
        }

        // 기타 객체는 그대로 (userdata로 전달됨)
        return javaValue;
    }

    private static Object arrayToLuaTable(Object array) {
        try {
            // KahluaTable 생성 시도
            Class<?> tableClass = Class.forName("se.krka.kahlua.vm.KahluaTable");
            Object table = tableClass.getDeclaredConstructor().newInstance();

            int length = java.lang.reflect.Array.getLength(array);
            for (int i = 0; i < length; i++) {
                Object item = java.lang.reflect.Array.get(array, i);
                // Lua는 1-based 인덱스
                tableClass.getMethod("rawset", Object.class, Object.class)
                        .invoke(table, (double) (i + 1), javaToLua(item));
            }
            return table;
        } catch (Exception e) {
            // 테이블 생성 실패 시 원본 반환
            return array;
        }
    }

    private static Object listToLuaTable(List<?> list) {
        try {
            Class<?> tableClass = Class.forName("se.krka.kahlua.vm.KahluaTable");
            Object table = tableClass.getDeclaredConstructor().newInstance();

            int i = 1;
            for (Object item : list) {
                tableClass.getMethod("rawset", Object.class, Object.class)
                        .invoke(table, (double) i++, javaToLua(item));
            }
            return table;
        } catch (Exception e) {
            return list;
        }
    }

    private static Object mapToLuaTable(Map<?, ?> map) {
        try {
            Class<?> tableClass = Class.forName("se.krka.kahlua.vm.KahluaTable");
            Object table = tableClass.getDeclaredConstructor().newInstance();

            for (var entry : map.entrySet()) {
                Object key = javaToLua(entry.getKey());
                Object value = javaToLua(entry.getValue());
                tableClass.getMethod("rawset", Object.class, Object.class)
                        .invoke(table, key, value);
            }
            return table;
        } catch (Exception e) {
            return map;
        }
    }

    // ─────────────────────────────────────────────────────────────
    // Lua → Java
    // ─────────────────────────────────────────────────────────────

    /**
     * Lua 값을 Java 타입으로 변환.
     */
    @SuppressWarnings("unchecked")
    public static <T> T luaToJava(Object luaValue, Class<T> targetType) {
        if (luaValue == null) {
            return null;
        }

        // 이미 원하는 타입이면 그대로 반환
        if (targetType.isInstance(luaValue)) {
            return (T) luaValue;
        }

        // Lua number → 다양한 숫자 타입
        if (luaValue instanceof Double) {
            Double d = (Double) luaValue;
            if (targetType == Integer.class || targetType == int.class) {
                return (T) Integer.valueOf(d.intValue());
            }
            if (targetType == Long.class || targetType == long.class) {
                return (T) Long.valueOf(d.longValue());
            }
            if (targetType == Float.class || targetType == float.class) {
                return (T) Float.valueOf(d.floatValue());
            }
            if (targetType == Double.class || targetType == double.class) {
                return (T) d;
            }
        }

        // String 변환
        if (targetType == String.class) {
            return (T) String.valueOf(luaValue);
        }

        // Boolean 변환
        if (targetType == Boolean.class || targetType == boolean.class) {
            if (luaValue instanceof Boolean) {
                return (T) luaValue;
            }
            return (T) Boolean.TRUE; // Lua에서 nil과 false만 falsy
        }

        // KahluaTable → List
        if (targetType == List.class) {
            return (T) luaTableToList(luaValue);
        }

        // KahluaTable → Map
        if (targetType == Map.class) {
            return (T) luaTableToMap(luaValue);
        }

        // 변환 불가 - 원본 반환 시도
        try {
            return (T) luaValue;
        } catch (ClassCastException e) {
            return null;
        }
    }

    private static List<Object> luaTableToList(Object luaTable) {
        List<Object> result = new java.util.ArrayList<>();
        try {
            Class<?> tableClass = luaTable.getClass();
            java.lang.reflect.Method lenMethod = tableClass.getMethod("len");
            int len = ((Number) lenMethod.invoke(luaTable)).intValue();

            java.lang.reflect.Method rawgetMethod = tableClass.getMethod(
                    "rawget", Object.class);

            for (int i = 1; i <= len; i++) {
                Object value = rawgetMethod.invoke(luaTable, (double) i);
                result.add(value);
            }
        } catch (Exception e) {
            // 변환 실패
        }
        return result;
    }

    private static Map<Object, Object> luaTableToMap(Object luaTable) {
        Map<Object, Object> result = new java.util.LinkedHashMap<>();
        try {
            Class<?> tableClass = luaTable.getClass();

            // 테이블의 next() 메서드로 순회
            java.lang.reflect.Method nextMethod = tableClass.getMethod(
                    "next", Object.class);
            java.lang.reflect.Method rawgetMethod = tableClass.getMethod(
                    "rawget", Object.class);

            Object key = nextMethod.invoke(luaTable, (Object) null);
            while (key != null) {
                Object value = rawgetMethod.invoke(luaTable, key);
                result.put(key, value);
                key = nextMethod.invoke(luaTable, key);
            }
        } catch (Exception e) {
            // 변환 실패
        }
        return result;
    }
}
