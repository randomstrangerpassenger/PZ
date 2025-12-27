package com.pulse.api;

import com.pulse.api.event.Event;
import com.pulse.api.event.EventListener;
import com.pulse.api.event.EventPriority;
import com.pulse.event.EventBus;

/**
 * Pulse 이벤트 API.
 * 
 * 외부 모드에서 Pulse 이벤트를 쉽게 구독/발행할 수 있도록 하는 Facade입니다.
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * import com.pulse.api.PulseEvents;
 * import com.pulse.api.event.lifecycle.GameTickEvent;
 * 
 * // 이벤트 구독
 * PulseEvents.on(GameTickEvent.class, event -> {
 *     System.out.println("Tick: " + event.getTick());
 * });
 * 
 * // 우선순위 지정 구독
 * PulseEvents.on(GameTickEvent.class, event -> { ... }, PulseEvents.HIGHEST);
 * 
 * // 이벤트 발행
 * PulseEvents.fire(new MyCustomEvent());
 * }</pre>
 * 
 * @since Pulse 1.2
 */
public final class PulseEvents {

    // 우선순위 상수
    public static final EventPriority HIGHEST = EventPriority.HIGHEST;
    public static final EventPriority HIGH = EventPriority.HIGH;
    public static final EventPriority NORMAL = EventPriority.NORMAL;
    public static final EventPriority LOW = EventPriority.LOW;
    public static final EventPriority LOWEST = EventPriority.LOWEST;

    private PulseEvents() {
    }

    /**
     * 이벤트 구독 (기본 우선순위)
     * 
     * @param eventType 이벤트 클래스
     * @param listener  리스너
     */
    public static <T extends Event> void on(Class<T> eventType, EventListener<T> listener) {
        EventBus.subscribe(eventType, listener);
    }

    /**
     * 이벤트 구독 (우선순위 지정)
     */
    public static <T extends Event> void on(Class<T> eventType, EventListener<T> listener,
            EventPriority priority) {
        EventBus.subscribe(eventType, listener, priority);
    }

    /**
     * 이벤트 구독 (modId 지정)
     */
    public static <T extends Event> void on(Class<T> eventType, EventListener<T> listener,
            String modId) {
        EventBus.subscribe(eventType, listener, modId);
    }

    /**
     * 이벤트 구독 (우선순위 + modId)
     */
    public static <T extends Event> void on(Class<T> eventType, EventListener<T> listener,
            EventPriority priority, String modId) {
        EventBus.subscribe(eventType, listener, priority, modId);
    }

    /**
     * 이벤트 구독 해제
     */
    public static <T extends Event> void off(Class<T> eventType, EventListener<T> listener) {
        EventBus.unsubscribe(eventType, listener);
    }

    /**
     * 이벤트 발행
     */
    public static <T extends Event> void fire(T event) {
        EventBus.post(event);
    }

    /**
     * 특정 이벤트 리스너 수 조회
     */
    public static int listenerCount(Class<? extends Event> eventType) {
        return PulseServices.eventBus().getListenerCount(eventType);
    }

    /**
     * 모드의 모든 리스너 해제
     */
    public static int unsubscribeAll(String modId) {
        return EventBus.unsubscribeAllByModId(modId);
    }
}
