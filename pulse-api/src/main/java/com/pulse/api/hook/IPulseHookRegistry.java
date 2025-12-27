package com.pulse.api.hook;

/**
 * 훅 레지스트리 인터페이스.
 * 훅 콜백 등록 및 관리.
 * 
 * @since Pulse 2.0
 */
public interface IPulseHookRegistry {

    /**
     * 훅 콜백 등록
     * 
     * @param type     훅 타입
     * @param callback 콜백 객체
     * @param ownerId  소유자 ID (모드 ID)
     * @param <T>      콜백 타입
     */
    <T> void register(HookType type, T callback, String ownerId);

    /**
     * 훅 콜백 해제
     * 
     * @param type     훅 타입
     * @param callback 콜백 객체
     */
    <T> void unregister(HookType type, T callback);

    /**
     * 소유자의 모든 훅 해제
     * 
     * @param ownerId 소유자 ID
     */
    void unregisterAll(String ownerId);

    /**
     * 특정 훅 타입의 콜백 개수
     * 
     * @param type 훅 타입
     * @return 등록된 콜백 개수
     */
    int getCallbackCount(HookType type);
}
