package com.pulse.api.event;

/**
 * 이벤트 버스 계약.
 * 모듈 간 느슨한 결합 통신을 제공.
 * 
 * @since Pulse 1.0
 */
public interface IEventBus {
    /**
     * 이벤트 구독 (기존 EventBus와 동일한 시그니처).
     * 
     * @param eventType    이벤트 클래스
     * @param listener     이벤트 리스너
     * @param subscriberId 구독자 ID (모드 언로드 시 일괄 해제용)
     * @param <T>          이벤트 타입
     */
    <T extends Event> void subscribe(Class<T> eventType, EventListener<T> listener, String subscriberId);

    /**
     * 특정 구독자의 모든 구독 해제.
     * 모드 언로드 시 자동 호출됨.
     * 
     * @param subscriberId 구독자 ID
     */
    void unsubscribeAll(String subscriberId);

    /**
     * 이벤트 발행.
     * 등록된 모든 핸들러가 호출됨.
     * 
     * @param event 이벤트 인스턴스
     * @param <T>   이벤트 타입
     */
    <T extends Event> void publish(T event);

    /**
     * 모든 구독 해제.
     * 라이프사이클 종료 시 호출됨.
     */
    void clearAll();

    /**
     * 디버그 모드 설정.
     * 
     * @param debug 활성화 여부
     */
    void setDebug(boolean debug);
}
