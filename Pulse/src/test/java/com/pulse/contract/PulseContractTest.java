package com.pulse.contract;

import com.pulse.api.util.ReflectionCache;
import com.pulse.event.EventBus;
import com.pulse.event.Event;
import com.pulse.scheduler.PulseScheduler;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class PulseContractTest {

    @Test
    void testEventBusContract() {
        EventBus bus = EventBus.getInstance();
        assertNotNull(bus, "EventBus instance should not be null");

        // Test subscription
        TestEvent event = new TestEvent();
        final boolean[] handled = { false };

        EventBus.subscribe(TestEvent.class, e -> handled[0] = true);
        EventBus.post(event);

        assertTrue(handled[0], "Event should be handled by subscriber");

        EventBus.getInstance().clearAll();
    }

    @Test
    void testSchedulerContract() {
        PulseScheduler scheduler = PulseScheduler.getInstance();
        assertNotNull(scheduler, "Scheduler instance should not be null");

        // Schedule a task
        PulseScheduler.runLater(() -> {
        }, 10);
        assertTrue(scheduler.getActiveTaskCount() > 0, "Task should be scheduled");
        scheduler.cancelAll();
        assertEquals(0, scheduler.getActiveTaskCount(), "Tasks should be cleared");
    }

    @Test
    void testReflectionCacheContract() throws Exception {
        ReflectionCache.clearAll();
        // Access a method (String.length is safe/standard)
        ReflectionCache.getMethodOrThrow(String.class, "length");
        assertTrue(ReflectionCache.getMethodCacheSize() > 0, "Method cache should contain entry");

        // Verify same instance returned (caching)
        java.lang.reflect.Method m1 = ReflectionCache.getMethodOrThrow(String.class, "length");
        java.lang.reflect.Method m2 = ReflectionCache.getMethodOrThrow(String.class, "length");
        assertSame(m1, m2, "Cached method instance should be identical");
    }

    // Concrete event implementation for testing
    public static class TestEvent extends Event {
        public TestEvent() {
            super(false);
        }
    }
}
