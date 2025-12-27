package com.pulse.api.exception;

/**
 * 의존성 주입 관련 예외.
 * 
 * 서비스 등록/조회 실패, 순환 의존성 등에 사용.
 */
public class InjectionException extends PulseException {

    public InjectionException(String message) {
        super(message);
    }

    public InjectionException(String message, Throwable cause) {
        super(message, cause);
    }

    /**
     * 서비스 찾을 수 없음
     */
    public static InjectionException serviceNotFound(Class<?> serviceType) {
        return new InjectionException(
                String.format("Service not found: %s. Register it via PulseServiceLocator.", serviceType.getName()));
    }

    /**
     * 순환 의존성 감지
     */
    public static InjectionException circularDependency(Class<?> serviceType) {
        return new InjectionException(
                String.format("Circular dependency detected while resolving: %s", serviceType.getName()));
    }

    /**
     * 서비스 인스턴스화 실패
     */
    public static InjectionException instantiationFailed(Class<?> serviceType, Throwable cause) {
        return new InjectionException(
                String.format("Failed to instantiate service: %s", serviceType.getName()), cause);
    }
}
