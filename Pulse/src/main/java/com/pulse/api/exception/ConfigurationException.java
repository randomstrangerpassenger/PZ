package com.pulse.api.exception;

/**
 * 설정 관련 예외.
 * 
 * 잘못된 설정값, 설정 파일 파싱 오류 등에 사용.
 */
public class ConfigurationException extends PulseException {

    public ConfigurationException(String message) {
        super(message);
    }

    public ConfigurationException(String message, Throwable cause) {
        super(message, cause);
    }

    /**
     * 잘못된 설정값 예외 생성
     */
    public static ConfigurationException invalidValue(String key, Object value, String reason) {
        return new ConfigurationException(
                String.format("Invalid configuration value for '%s': %s. %s", key, value, reason));
    }

    /**
     * 누락된 필수 설정 예외 생성
     */
    public static ConfigurationException missingRequired(String key) {
        return new ConfigurationException(
                String.format("Required configuration key '%s' is missing.", key));
    }

    /**
     * 설정 파일 파싱 오류
     */
    public static ConfigurationException parseError(String file, Throwable cause) {
        return new ConfigurationException(
                String.format("Failed to parse configuration file: %s", file), cause);
    }
}
