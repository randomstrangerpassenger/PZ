package com.pulse.event;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * EventBus 회귀 테스트.
 * Lazy Sort 최적화 후 기존 동작이 유지되는지 검증.
 */
class EventBusTest {

    private EventBus eventBus;
    private boolean listenerCalled;
    private int callOrder;

    @BeforeEach
    void setUp() {
        eventBus = EventBus.getInstance();
        eventBus.clearAll();
        listenerCalled = false;
        callOrder = 0;
    }

    @Test
    void subscribe_and_fire_callsListener() {
        EventBus.subscribe(TestEvent.class, e -> listenerCalled = true);
        EventBus.post(new TestEvent());
        assertTrue(listenerCalled);
    }

    @Test
    void priority_highCalledFirst() {
        int[] order = new int[2];

        EventBus.subscribe(TestEvent.class, e -> order[0] = ++callOrder, EventPriority.LOW);
        EventBus.subscribe(TestEvent.class, e -> order[1] = ++callOrder, EventPriority.HIGH);

        EventBus.post(new TestEvent());

        // HIGH가 먼저 호출되므로 order[1] = 1, order[0] = 2
        assertEquals(1, order[1], "HIGH priority should be called first");
        assertEquals(2, order[0], "LOW priority should be called second");
    }

    @Test
    void unsubscribe_removesListener() {
        EventListener<TestEvent> listener = e -> listenerCalled = true;
        EventBus.subscribe(TestEvent.class, listener);
        EventBus.unsubscribe(TestEvent.class, listener);
        EventBus.post(new TestEvent());
        assertFalse(listenerCalled);
    }

    @Test
    void clearAll_removesAllListeners() {
        EventBus.subscribe(TestEvent.class, e -> listenerCalled = true);
        eventBus.clearAll();
        EventBus.post(new TestEvent());
        assertFalse(listenerCalled);
    }

    @Test
    void getListenerCount_returnsCorrectCount() {
        assertEquals(0, eventBus.getListenerCount(TestEvent.class));
        EventBus.subscribe(TestEvent.class, e -> {
        });
        assertEquals(1, eventBus.getListenerCount(TestEvent.class));
        EventBus.subscribe(TestEvent.class, e -> {
        });
        assertEquals(2, eventBus.getListenerCount(TestEvent.class));
    }

    // 테스트용 이벤트 클래스
    static class TestEvent extends Event {
        TestEvent() {
            super(false);
        }
    }
}
