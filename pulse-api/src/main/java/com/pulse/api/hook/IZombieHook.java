package com.pulse.api.hook;

import com.pulse.api.profiler.IThrottlePolicy;

/**
 * Zombie Hook 인터페이스.
 * 
 * Pulse 플랫폼에서 제공하는 SPI로, 하위 최적화 모드가
 * 스로틀링 정책을 등록하고 좀비 처리 여부를 결정할 수 있게 합니다.
 * 
 * 사용 예:
 * 
 * <pre>
 * IZombieHook hook = PulseServices.getServiceLocator().getService(IZombieHook.class);
 * hook.setThrottlePolicy(myPolicy);
 * </pre>
 * 
 * @since Pulse 2.0
 */
public interface IZombieHook {

    /**
     * 스로틀링 정책 등록.
     * 
     * @param policy 스로틀링 정책 구현체
     */
    void setThrottlePolicy(IThrottlePolicy policy);

    /**
     * 현재 좀비를 처리해야 하는지 확인.
     * 
     * @return true면 처리, false면 스킵
     */
    boolean shouldProcessCurrentZombie();

    /**
     * 현재 처리 중인 좀비 설정 (Mixin에서 호출).
     * 
     * @param zombie 좀비 객체
     */
    void setCurrentZombie(Object zombie);

    /**
     * 현재 처리 중인 좀비 정리 (Mixin에서 호출).
     */
    void clearCurrentZombie();

    /**
     * 정책이 등록되어 있는지 확인.
     */
    boolean hasThrottlePolicy();

    /**
     * 스로틀링 정책 제거.
     */
    void clearThrottlePolicy();
}
