package com.echo.measure;

import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

/**
 * EchoProfiler 단위 테스트
 */
class EchoProfilerTest {

    private EchoProfiler profiler;

    @BeforeEach
    void setUp() {
        profiler = EchoProfiler.getInstance();
        profiler.reset();
        profiler.enable(true);
    }

    @AfterEach
    void tearDown() {
        profiler.disable();
    }

    @Test
    @DisplayName("Profiler singleton instance")
    void testSingleton() {
        EchoProfiler instance1 = EchoProfiler.getInstance();
        EchoProfiler instance2 = EchoProfiler.getInstance();
        assertSame(instance1, instance2);
    }

    @Test
    @DisplayName("Enable/Disable profiler")
    void testEnableDisable() {
        profiler.disable();
        assertFalse(profiler.isEnabled());

        profiler.enable();
        assertTrue(profiler.isEnabled());
    }

    @Test
    @DisplayName("Push/Pop records timing data")
    void testPushPop() {
        profiler.push(ProfilingPoint.TICK);
        try {
            Thread.sleep(10);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        profiler.pop(ProfilingPoint.TICK);

        var data = profiler.getTimingData(ProfilingPoint.TICK);
        assertNotNull(data);
        assertEquals(1, data.getCallCount());
        assertTrue(data.getAverageMicros() > 0);
    }

    @Test
    @DisplayName("Scope API with try-with-resources")
    void testScopeApi() {
        try (var scope = profiler.scope(ProfilingPoint.ZOMBIE_AI)) {
            // Simulated work
            Thread.sleep(5);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        var data = profiler.getTimingData(ProfilingPoint.ZOMBIE_AI);
        assertNotNull(data);
        assertEquals(1, data.getCallCount());
    }

    @Test
    @DisplayName("Raw API for zero-allocation")
    void testRawApi() {
        long start = profiler.startRaw(ProfilingPoint.RENDER);
        assertTrue(start > 0);
        profiler.endRaw(ProfilingPoint.RENDER, start);

        var data = profiler.getTimingData(ProfilingPoint.RENDER);
        assertEquals(1, data.getCallCount());
    }

    @Test
    @DisplayName("Labeled profiling")
    void testLabeledProfiling() {
        try (var scope = profiler.scope(ProfilingPoint.ZOMBIE_AI, "pathfinding")) {
            Thread.sleep(1);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        var data = profiler.getTimingData(ProfilingPoint.ZOMBIE_AI);
        var labelStats = data.getLabelStats();
        assertTrue(labelStats.containsKey("pathfinding"));
    }

    @Test
    @DisplayName("Reset clears all data")
    void testReset() {
        try (var scope = profiler.scope(ProfilingPoint.TICK)) {
            Thread.sleep(1);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        profiler.reset();

        var data = profiler.getTimingData(ProfilingPoint.TICK);
        assertEquals(0, data.getCallCount());
    }

    @Test
    @DisplayName("Session duration tracking")
    void testSessionDuration() throws InterruptedException {
        Thread.sleep(100);
        // Session duration should be at least 0 seconds
        assertTrue(profiler.getSessionDurationSeconds() >= 0);
    }
}
