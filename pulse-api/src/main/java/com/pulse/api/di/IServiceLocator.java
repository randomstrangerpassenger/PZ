package com.pulse.api.di;

/**
 * 서비스 로케이터 계약.
 * 
 * @since Pulse 1.0
 * @since Pulse 2.0 - registerService 추가
 */
public interface IServiceLocator {
    /**
     * 서비스 조회.
     * 
     * @param serviceClass 서비스 클래스
     * @param <T>          서비스 타입
     * @return 서비스 인스턴스
     * @throws IllegalArgumentException 서비스가 등록되지 않은 경우
     */
    <T> T getService(Class<T> serviceClass);

    /**
     * 서비스 존재 확인.
     * 
     * @param serviceClass 서비스 클래스
     * @param <T>          서비스 타입
     * @return 서비스 존재 여부
     */
    <T> boolean hasService(Class<T> serviceClass);

    /**
     * 서비스 등록.
     * 
     * @param serviceClass 서비스 인터페이스 클래스
     * @param instance     서비스 구현 인스턴스
     * @param <T>          서비스 타입
     */
    <T> void registerService(Class<T> serviceClass, T instance);
}
