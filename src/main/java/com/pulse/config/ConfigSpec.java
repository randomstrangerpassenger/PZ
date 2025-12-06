package com.pulse.config;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;

/**
 * 설정 스펙.
 * 설정 클래스의 메타데이터를 담고 있음.
 */
public class ConfigSpec {

    private final Class<?> configClass;
    private final String modId;
    private final String fileName;
    private final String category;
    private final List<ConfigEntry> entries = new ArrayList<>();

    public ConfigSpec(Class<?> configClass) {
        this.configClass = configClass;

        Config config = configClass.getAnnotation(Config.class);
        if (config == null) {
            throw new IllegalArgumentException("Class must have @Config annotation");
        }

        this.modId = config.modId();
        this.fileName = config.fileName().isEmpty() ? modId + ".json" : config.fileName();
        this.category = config.category();

        // 필드 스캔
        scanFields();
    }

    private void scanFields() {
        for (Field field : configClass.getDeclaredFields()) {
            ConfigValue annotation = field.getAnnotation(ConfigValue.class);
            if (annotation != null) {
                field.setAccessible(true);

                String key = annotation.key().isEmpty() ? field.getName() : annotation.key();
                Object defaultValue = getFieldValue(field);

                ConfigEntry entry = new ConfigEntry(
                        key,
                        field,
                        annotation.comment(),
                        defaultValue,
                        annotation.min(),
                        annotation.max(),
                        annotation.requiresRestart());

                entries.add(entry);
            }
        }
    }

    private Object getFieldValue(Field field) {
        try {
            return field.get(null);
        } catch (IllegalAccessException e) {
            return null;
        }
    }

    // Getters

    public Class<?> getConfigClass() {
        return configClass;
    }

    public String getModId() {
        return modId;
    }

    public String getFileName() {
        return fileName;
    }

    public String getCategory() {
        return category;
    }

    public List<ConfigEntry> getEntries() {
        return entries;
    }

    /**
     * 단일 설정 엔트리
     */
    public static class ConfigEntry {
        private final String key;
        private final Field field;
        private final String comment;
        private final Object defaultValue;
        private final double min;
        private final double max;
        private final boolean requiresRestart;

        public ConfigEntry(String key, Field field, String comment, Object defaultValue,
                double min, double max, boolean requiresRestart) {
            this.key = key;
            this.field = field;
            this.comment = comment;
            this.defaultValue = defaultValue;
            this.min = min;
            this.max = max;
            this.requiresRestart = requiresRestart;
        }

        public String getKey() {
            return key;
        }

        public Field getField() {
            return field;
        }

        public String getComment() {
            return comment;
        }

        public Object getDefaultValue() {
            return defaultValue;
        }

        public double getMin() {
            return min;
        }

        public double getMax() {
            return max;
        }

        public boolean requiresRestart() {
            return requiresRestart;
        }

        public Class<?> getType() {
            return field.getType();
        }

        public Object getValue() {
            try {
                return field.get(null);
            } catch (IllegalAccessException e) {
                return defaultValue;
            }
        }

        public void setValue(Object value) {
            try {
                // 범위 검사 (숫자 타입)
                if (value instanceof Number num) {
                    double val = num.doubleValue();
                    if (min != Double.MIN_VALUE && val < min) {
                        value = convertToFieldType(min, field.getType());
                    }
                    if (max != Double.MAX_VALUE && val > max) {
                        value = convertToFieldType(max, field.getType());
                    }
                }
                field.set(null, value);
            } catch (IllegalAccessException e) {
                System.err.println("[Pulse/Config] Failed to set value for " + key);
            }
        }

        private Object convertToFieldType(double value, Class<?> type) {
            if (type == int.class || type == Integer.class)
                return (int) value;
            if (type == long.class || type == Long.class)
                return (long) value;
            if (type == float.class || type == Float.class)
                return (float) value;
            if (type == double.class || type == Double.class)
                return value;
            return value;
        }

        public void reset() {
            setValue(defaultValue);
        }
    }
}
