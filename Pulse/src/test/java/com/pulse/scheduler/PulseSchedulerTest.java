package com.pulse.scheduler;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Tag;

import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

@Tag("unit")
class PulseSchedulerTest {

    private PulseScheduler scheduler;

    @BeforeEach
    void setUp() {
        scheduler = PulseScheduler.getInstance();
        scheduler.cancelAll();
        // Note: currentTick is persistent across tests because it's in a singleton.
        // We cannot reset currentTick easily without reflection or adding a method.
        // But runLater uses (currentTick + delay). So relative delay should work
        // regardless of absolute tick.
    }

    @Test
    void runLater_executesAfterDelay() {
        AtomicInteger counter = new AtomicInteger(0);
        long startTick = PulseScheduler.getCurrentTick();

        // Run after 2 ticks
        PulseScheduler.runLater(() -> counter.incrementAndGet(), 2);

        // Tick 1 (Elapsed 1)
        scheduler.tick();
        // Should NOT run yet
        assertEquals(0, counter.get(),
                "Should not run after 1 tick. Start: " + startTick + ", Current: " + PulseScheduler.getCurrentTick());

        // Tick 2 (Elapsed 2)
        scheduler.tick();
        // Should run now (or next tick depending on implementation?)
        // Implementation: isReadyToExecute(currentTick) -> currentTick >= targetTick
        // targetTick = startTick + 2
        // currentTick after 2 calls = startTick + 2.
        // So it should run.
        assertEquals(1, counter.get(),
                "Should run after 2 ticks. Start: " + startTick + ", Current: " + PulseScheduler.getCurrentTick());
    }

    @Test
    void runTimer_executesMultipleTimes() {
        AtomicInteger counter = new AtomicInteger(0);

        // 0 ticks delay, period 1 tick
        PulseScheduler.runTimer(() -> counter.incrementAndGet(), 1, 0);

        scheduler.tick(); // Should run 1st time
        assertTrue(counter.get() >= 1, "Should run immediately (delay 0) or after 1 tick");

        int afterFirst = counter.get();
        scheduler.tick(); // Should run 2nd time
        assertTrue(counter.get() > afterFirst, "Should increment");

        scheduler.tick(); // Should run 3rd time
        assertTrue(counter.get() > afterFirst + 1, "Should increment again");
    }

    @Test
    void cancel_stopsExecution() {
        AtomicInteger counter = new AtomicInteger(0);

        TaskHandle handle = PulseScheduler.runTimer(() -> counter.incrementAndGet(), 1, 0);

        scheduler.tick();
        handle.cancel();

        int valueAtCancel = counter.get();

        scheduler.tick();
        scheduler.tick();

        assertEquals(valueAtCancel, counter.get(), "Counter should not increase after cancel");
    }

    @Test
    void cancelAll_stopsAllTasks() {
        AtomicInteger counter = new AtomicInteger(0);

        PulseScheduler.runTimer(() -> counter.incrementAndGet(), 1, 0);
        PulseScheduler.runTimer(() -> counter.incrementAndGet(), 1, 0);

        scheduler.tick();
        assertTrue(counter.get() > 0);

        scheduler.cancelAll();
        int valueAtCancel = counter.get();

        scheduler.tick();

        assertEquals(valueAtCancel, counter.get(), "All tasks should be cancelled");
    }

    @Test
    void getActiveTaskCount_returnsCorrectCount() {
        scheduler.cancelAll();
        assertEquals(0, scheduler.getActiveTaskCount());

        PulseScheduler.runTimer(() -> {
        }, 10, 0);
        PulseScheduler.runLater(() -> {
        }, 100);

        assertEquals(2, scheduler.getActiveTaskCount());

        scheduler.cancelAll();
        assertEquals(0, scheduler.getActiveTaskCount());
    }
}
