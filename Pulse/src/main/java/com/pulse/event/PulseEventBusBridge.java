package com.pulse.event;

import com.pulse.api.event.Event;
import com.pulse.api.event.EventListener;
import com.pulse.api.event.IEventBus;

/**
 * EventBus Bridge: IEventBus 인터페이스를 EventBus static 메서드로 위임.
 * 
 * <p>
 * 이 클래스는 타입 erasure 충돌 문제를 해결하기 위한 Bridge 패턴입니다.
 * EventBus의 기존 static API를 유지하면서 IEventBus 계약을 이행합니다.
 * </p>
 * 
 * @since Pulse 1.0 (Phase 2)
 */
public class PulseEventBusBridge implements IEventBus {

    private static final PulseEventBusBridge INSTANCE = new PulseEventBusBridge();

    private PulseEventBusBridge() {
        // Singleton
    }

    public static PulseEventBusBridge getInstance() {
        return INSTANCE;
    }

    /**
     * IEventBus 계약: 이벤트 구독.
     * EventBus의 static subscribe(eventType, listener, modId)로 위임.
     */
    @Override
    public <T extends Event> void subscribe(Class<T> eventType, EventListener<T> listener, String subscriberId) {
        EventBus.subscribe(eventType, listener, subscriberId);
    }

    /**
     * IEventBus 계약: 특정 구독자 모든 구독 해제.
     * EventBus의 static unsubscribeAllByModId(modId)로 위임.
     */
    @Override
    public void unsubscribeAll(String subscriberId) {
        EventBus.unsubscribeAllByModId(subscriberId);
    }

    /**
     * IEventBus 계약: 이벤트 발행.
     * EventBus의 static post(event)로 위임.
     */
    @Override
    public <T extends Event> void publish(T event) {
        EventBus.post(event);
    }

    /**
     * IEventBus 계약: 모든 구독 해제.
     * EventBus 인스턴스의 clearAll()로 위임.
     */
    @Override
    public void clearAll() {
        EventBus.getInstance().clearAll();
    }

    /**
     * IEventBus 계약: 디버그 모드 설정.
     * EventBus 인스턴스의 setDebug()로 위임.
     */
    @Override
    public void setDebug(boolean debug) {
        EventBus.getInstance().setDebug(debug);
    }
}
