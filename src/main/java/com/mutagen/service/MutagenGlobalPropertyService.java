package com.mutagen.service;

import org.spongepowered.asm.service.IGlobalPropertyService;
import org.spongepowered.asm.service.IPropertyKey;

import java.util.HashMap;
import java.util.Map;

/**
 * Mixin 전역 프로퍼티 서비스.
 * Mixin 시스템 전체에서 공유되는 설정값을 관리.
 */
public class MutagenGlobalPropertyService implements IGlobalPropertyService {

    private final Map<String, Object> properties = new HashMap<>();

    public MutagenGlobalPropertyService() {
        // 기본 프로퍼티 설정
        properties.put("mixin.debug", true);
        properties.put("mixin.env.disableRefMap", true);
    }

    @Override
    public IPropertyKey resolveKey(String name) {
        return new StringPropertyKey(name);
    }

    @Override
    @SuppressWarnings("unchecked")
    public <T> T getProperty(IPropertyKey key) {
        return (T) properties.get(key.toString());
    }

    @Override
    @SuppressWarnings("unchecked")
    public <T> T getProperty(IPropertyKey key, T defaultValue) {
        Object value = properties.get(key.toString());
        return value != null ? (T) value : defaultValue;
    }

    @Override
    public void setProperty(IPropertyKey key, Object value) {
        properties.put(key.toString(), value);
    }

    @Override
    public String getPropertyString(IPropertyKey key, String defaultValue) {
        Object value = properties.get(key.toString());
        return value != null ? value.toString() : defaultValue;
    }

    // 내부 키 구현
    private static class StringPropertyKey implements IPropertyKey {
        private final String key;

        StringPropertyKey(String key) {
            this.key = key;
        }

        @Override
        public String toString() {
            return key;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            return key.equals(((StringPropertyKey) o).key);
        }

        @Override
        public int hashCode() {
            return key.hashCode();
        }
    }
}
