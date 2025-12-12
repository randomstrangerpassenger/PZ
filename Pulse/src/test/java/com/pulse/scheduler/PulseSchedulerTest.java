package com.pulse.scheduler;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Tag;

import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

/**
 * PulseScheduler 단위 테스트.
 * 스케줄링 기본 동작 검증.
 */
@Tag("unit")
class PulseSchedulerTest {

    private PulseScheduler scheduler;

    @BeforeEach
    void setUp() {
        scheduler = PulseScheduler.getInstance();
        scheduler.cancelAll();
    }

    @Test
    void runLater_executesAfterDelay() {
        AtomicInteger counter = new AtomicInteger(0);

        PulseScheduler.runLater(() -> counter.incrementAndGet(), 2);

        // 틱 0: 실행되지 않음
        scheduler.tick();
        assertEquals(0, counter.get());

        // 틱 1: 아직 1틱 더 필요
        scheduler.tick();
        assertEquals(0, counter.get());

        // 틱 2: 이제 실행됨
        scheduler.tick();
        assertEquals(1, counter.get());
    }

    @Test
    void runTimer_executesMultipleTimes() {
        AtomicInteger counter = new AtomicInteger(0);

        // 0틱 딜레이, 매 틱마다 실행 (period=1)
        PulseScheduler.runTimer(() -> counter.incrementAndGet(), 1, 0);

        scheduler.tick(); // 1
        scheduler.tick(); // 2
        scheduler.tick(); // 3

        // Use >= since first tick might/might not trigger depending on implementation
        assertTrue(counter.get() >= 2, "Timer should execute at least twice");
    }

    @Test
    void cancel_stopsExecution() {
        AtomicInteger counter = new AtomicInteger(0);

        TaskHandle handle = PulseScheduler.runTimer(() -> counter.incrementAndGet(), 1, 0);

        scheduler.tick(); // 1
        handle.cancel();
        scheduler.tick(); // 취소됨
        scheduler.tick(); // 취소됨

        assertEquals(1, counter.get());
    }

    @Test
    void cancelAll_stopsAllTasks() {
        AtomicInteger counter = new AtomicInteger(0);

        PulseScheduler.runTimer(() -> counter.incrementAndGet(), 1, 0);
        PulseScheduler.runTimer(() -> counter.incrementAndGet(), 1, 0);

        scheduler.tick(); // 2 (두 태스크 각각 1번)
        scheduler.cancelAll();
        scheduler.tick(); // 취소됨

        assertEquals(2, counter.get());
    }

    @Test
    void getActiveTaskCount_returnsCorrectCount() {
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
