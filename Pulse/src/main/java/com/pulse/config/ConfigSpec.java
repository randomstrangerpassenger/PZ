package com.pulse.config;

import com.pulse.api.log.PulseLogger;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;
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
    private static final String LOG = PulseLogger.PULSE;

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
                        annotation.requiresRestart(),
                        annotation.options(),
                        annotation.step(),
                        annotation.category());

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
     * @Validate 메서드 실행.
     * @return 검증 성공 여부
     */
    public boolean runValidation() {
        for (Method method : configClass.getDeclaredMethods()) {
            if (method.isAnnotationPresent(Validate.class)) {
                method.setAccessible(true);
                try {
                    Object result = method.invoke(null);
                    if (result instanceof Boolean b && !b) {
                        Validate validate = method.getAnnotation(Validate.class);
                        PulseLogger.error(LOG, "[Config] Validation failed: {}", validate.message());
                        return false;
                    }
                } catch (Exception e) {
                    PulseLogger.error(LOG, "[Config] Validation error: {}", e.getMessage());
                    return false;
                }
            }
        }
        return true;
    }

    /**
     * 모든 값을 기본값으로 리셋.
     */
    public void resetAll() {
        for (ConfigEntry entry : entries) {
            entry.reset();
        }
        PulseLogger.info(LOG, "[Config] Reset all values to defaults for: {}", modId);
    }

    public static class ConfigEntry {
        private final String key;
        private final Field field;
        private final String comment;
        private final Object defaultValue;
        private final double min;
        private final double max;
        private final boolean requiresRestart;
        private final String[] options;
        private final double step;
        private final String category;

        public ConfigEntry(String key, Field field, String comment, Object defaultValue,
                double min, double max, boolean requiresRestart,
                String[] options, double step, String category) {
            this.key = key;
            this.field = field;
            this.comment = comment;
            this.defaultValue = defaultValue;
            this.min = min;
            this.max = max;
            this.requiresRestart = requiresRestart;
            this.options = options;
            this.step = step;
            this.category = category;
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
                // options 검증 (String 타입)
                if (options != null && options.length > 0 && value instanceof String strVal) {
                    List<String> optionList = Arrays.asList(options);
                    if (!optionList.contains(strVal)) {
                        PulseLogger.warn(LOG, "[Config] Invalid option '{}' for {}, resetting to default", strVal, key);
                        value = defaultValue;
                    }
                }

                // 범위 검사 및 step 적용 (숫자 타입)
                if (value instanceof Number num) {
                    double val = num.doubleValue();

                    // step 적용 (반올림)
                    if (step > 0) {
                        val = Math.round(val / step) * step;
                    }

                    // min/max 범위 적용
                    if (min != Double.MIN_VALUE && val < min) {
                        val = min;
                    }
                    if (max != Double.MAX_VALUE && val > max) {
                        val = max;
                    }

                    value = convertToFieldType(val, field.getType());
                }

                field.set(null, value);
            } catch (IllegalAccessException e) {
                PulseLogger.error(LOG, "[Config] Failed to set value for {}", key);
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

        public String[] getOptions() {
            return options;
        }

        public double getStep() {
            return step;
        }

        public String getCategory() {
            return category;
        }

        public boolean hasOptions() {
            return options != null && options.length > 0;
        }
    }
}
