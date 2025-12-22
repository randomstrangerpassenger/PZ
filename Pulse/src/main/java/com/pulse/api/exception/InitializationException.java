package com.pulse.api.exception;

/**
 * 초기화 관련 예외.
 * 
 * 모듈 초기화 실패, 의존성 로드 실패, 환경 설정 오류 등에 사용.
 * 
 * @since 1.1.0
 */
public class InitializationException extends PulseException {

    private final String component;
    private final InitPhase phase;

    /**
     * 초기화 단계
     */
    public enum InitPhase {
        /** 의존성 로드 */
        DEPENDENCY_LOAD,
        /** 설정 읽기 */
        CONFIG_READ,
        /** 서비스 등록 */
        SERVICE_REGISTRATION,
        /** Mixin 적용 */
        MIXIN_APPLY,
        /** 모듈 시작 */
        MODULE_START,
        /** 기타 */
        OTHER
    }

    public InitializationException(String message) {
        super(message);
        this.component = null;
        this.phase = InitPhase.OTHER;
    }

    public InitializationException(String message, Throwable cause) {
        super(message, cause);
        this.component = null;
        this.phase = InitPhase.OTHER;
    }

    public InitializationException(String message, String component, InitPhase phase) {
        super(message);
        this.component = component;
        this.phase = phase;
    }

    public InitializationException(String message, String component, InitPhase phase, Throwable cause) {
        super(message, cause);
        this.component = component;
        this.phase = phase;
    }

    public String getComponent() {
        return component;
    }

    public InitPhase getPhase() {
        return phase;
    }

    // --- 팩토리 메서드 ---

    /**
     * 모듈 초기화 실패
     */
    public static InitializationException moduleStartFailed(String moduleName, Throwable cause) {
        return new InitializationException(
                String.format("Failed to start module '%s': %s", moduleName, cause.getMessage()),
                moduleName, InitPhase.MODULE_START, cause);
    }

    /**
     * 의존성 로드 실패
     */
    public static InitializationException dependencyLoadFailed(String dependency, Throwable cause) {
        return new InitializationException(
                String.format("Failed to load dependency '%s': %s", dependency, cause.getMessage()),
                dependency, InitPhase.DEPENDENCY_LOAD, cause);
    }

    /**
     * 설정 읽기 실패
     */
    public static InitializationException configReadFailed(String configFile, Throwable cause) {
        return new InitializationException(
                String.format("Failed to read configuration '%s': %s", configFile, cause.getMessage()),
                configFile, InitPhase.CONFIG_READ, cause);
    }

    /**
     * 서비스 등록 실패
     */
    public static InitializationException serviceRegistrationFailed(Class<?> serviceClass, Throwable cause) {
        return new InitializationException(
                String.format("Failed to register service '%s': %s", serviceClass.getName(), cause.getMessage()),
                serviceClass.getName(), InitPhase.SERVICE_REGISTRATION, cause);
    }

    /**
     * 필수 의존성 누락
     */
    public static InitializationException missingDependency(String moduleName, String dependency) {
        return new InitializationException(
                String.format("Module '%s' requires '%s' but it was not found", moduleName, dependency),
                moduleName, InitPhase.DEPENDENCY_LOAD);
    }
}
