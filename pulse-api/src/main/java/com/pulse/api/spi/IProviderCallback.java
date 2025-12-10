package com.pulse.api.spi;

/**
 * 프로바이더 이벤트 콜백 인터페이스.
 * 프로바이더 등록/해제 등의 이벤트를 수신할 수 있음.
 */
public interface IProviderCallback {

    /**
     * 프로바이더가 등록되었을 때 호출
     * 
     * @param provider 등록된 프로바이더
     */
    default void onProviderRegistered(IProvider provider) {
    }

    /**
     * 프로바이더가 해제되었을 때 호출
     * 
     * @param provider 해제된 프로바이더
     */
    default void onProviderUnregistered(IProvider provider) {
    }

    /**
     * 프로바이더 생명주기가 변경되었을 때 호출
     * 
     * @param provider 프로바이더
     * @param oldState 이전 상태
     * @param newState 새 상태
     */
    default void onLifecycleChanged(IProvider provider,
            ProviderLifecycle oldState,
            ProviderLifecycle newState) {
    }

    /**
     * 프로바이더에서 오류가 발생했을 때 호출
     * 
     * @param provider 프로바이더
     * @param error    발생한 오류
     */
    default void onProviderError(IProvider provider, Throwable error) {
    }
}
