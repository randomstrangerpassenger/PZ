package com.pulse.event;

import com.pulse.api.event.Event;
import com.pulse.api.event.EventListener;
import com.pulse.api.event.EventPriority;
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

    // ═══════════════════════════════════════════════════════════════
    // Phase 0-A/0-B: 스냅샷 테스트 (하드코딩 기대값)
    // 리팩토링 후 동작 의미 보존 검증
    // ═══════════════════════════════════════════════════════════════

    /**
     * 우선순위별 호출 순서 검증 (HIGH → NORMAL → LOW).
     * v4 Phase 0-B: 하드코딩 기대값으로 스냅샷 테스트.
     */
    @Test
    void fire_should_maintain_priority_order_snapshot() {
        java.util.List<String> callOrder = new java.util.ArrayList<>();

        EventBus.subscribe(TestEvent.class, e -> callOrder.add("LOW"), EventPriority.LOW);
        EventBus.subscribe(TestEvent.class, e -> callOrder.add("HIGH"), EventPriority.HIGH);
        EventBus.subscribe(TestEvent.class, e -> callOrder.add("NORMAL"), EventPriority.NORMAL);

        EventBus.post(new TestEvent());

        // 하드코딩 기대값 (스냅샷)
        assertEquals(java.util.List.of("HIGH", "NORMAL", "LOW"), callOrder,
                "Priority order should be HIGH → NORMAL → LOW");
    }

    /**
     * 예외 격리 검증: 한 리스너에서 예외가 발생해도 다른 리스너는 실행됨.
     * v4 Phase 0-B: 리팩토링 후에도 예외 격리 동작 유지 확인.
     */
    @Test
    void fire_should_isolate_exceptions() {
        java.util.List<String> callOrder = new java.util.ArrayList<>();

        EventBus.subscribe(TestEvent.class, e -> {
            throw new RuntimeException("intentional failure for test");
        }, EventPriority.HIGH, "mod-a");
        EventBus.subscribe(TestEvent.class, e -> callOrder.add("executed"),
                EventPriority.NORMAL, "mod-b");

        // 예외가 발생해도 테스트 자체는 실패하지 않아야 함
        EventBus.post(new TestEvent());

        // 두 번째 리스너는 실행되어야 함 (예외 격리)
        assertEquals(java.util.List.of("executed"), callOrder,
                "Second listener should execute despite first listener's exception");
    }

    /**
     * modId별 리스너 해제 검증.
     * v4 Phase 0-A: unsubscribeAllByModId 동작 확인.
     */
    @Test
    void unsubscribeAllByModId_removesOnlyTargetMod() {
        java.util.List<String> callOrder = new java.util.ArrayList<>();

        EventBus.subscribe(TestEvent.class, e -> callOrder.add("mod-a"),
                EventPriority.NORMAL, "mod-a");
        EventBus.subscribe(TestEvent.class, e -> callOrder.add("mod-b"),
                EventPriority.NORMAL, "mod-b");

        // mod-a의 리스너만 해제
        int removed = EventBus.unsubscribeAllByModId("mod-a");
        assertEquals(1, removed, "Should remove 1 listener from mod-a");

        EventBus.post(new TestEvent());

        // mod-b의 리스너만 실행되어야 함
        assertEquals(java.util.List.of("mod-b"), callOrder,
                "Only mod-b listener should execute after mod-a unsubscribe");
    }

    // 테스트용 이벤트 클래스
    static class TestEvent extends Event {
        TestEvent() {
            super(false);
        }
    }
}
