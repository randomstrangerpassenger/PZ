package com.pulse.event;

/**
 * 이벤트 리스너 함수형 인터페이스.
 * 
 * 사용 예:
 * EventBus.subscribe(GameTickEvent.class, event -> {
 *     System.out.println("Tick!");
 * });
 */
@FunctionalInterface
public interface EventListener<T extends Event> {
    
    /**
     * 이벤트 처리
     * @param event 발생한 이벤트
     */
    void onEvent(T event);
}
