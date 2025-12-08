package com.echo.aggregate;

import com.echo.measure.ProfilingPoint;
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

/**
 * SpikeLog 단위 테스트
 */
class SpikeLogTest {

    private SpikeLog spikeLog;

    @BeforeEach
    void setUp() {
        spikeLog = new SpikeLog(10.0); // 10ms threshold
    }

    @Test
    @DisplayName("Initial state")
    void testInitialState() {
        assertEquals(0, spikeLog.getTotalSpikes());
        assertEquals(0.0, spikeLog.getWorstSpikeMs());
        assertEquals(10.0, spikeLog.getThresholdMs());
    }

    @Test
    @DisplayName("Spikes below threshold not logged")
    void testBelowThreshold() {
        spikeLog.logSpike(5000, ProfilingPoint.TICK, null); // 5ms < 10ms
        assertEquals(0, spikeLog.getTotalSpikes());
    }

    @Test
    @DisplayName("Spikes above threshold logged")
    void testAboveThreshold() {
        spikeLog.logSpike(15000, ProfilingPoint.TICK, null); // 15ms > 10ms
        assertEquals(1, spikeLog.getTotalSpikes());
    }

    @Test
    @DisplayName("Worst spike tracking")
    void testWorstSpike() {
        spikeLog.logSpike(20000, ProfilingPoint.TICK, "first");
        spikeLog.logSpike(50000, ProfilingPoint.TICK, "worst");
        spikeLog.logSpike(30000, ProfilingPoint.TICK, "third");

        assertEquals(50.0, spikeLog.getWorstSpikeMs());
        assertEquals("worst", spikeLog.getWorstSpikeLabel());
    }

    @Test
    @DisplayName("Threshold can be changed at runtime")
    void testThresholdChange() {
        spikeLog.setThresholdMs(5.0);
        assertEquals(5.0, spikeLog.getThresholdMs());

        spikeLog.logSpike(7000, ProfilingPoint.TICK, null); // 7ms > 5ms
        assertEquals(1, spikeLog.getTotalSpikes());
    }

    @Test
    @DisplayName("Recent spikes retrieval")
    void testRecentSpikes() {
        spikeLog.logSpike(15000, ProfilingPoint.TICK, "spike1");
        spikeLog.logSpike(20000, ProfilingPoint.RENDER, "spike2");

        var recent = spikeLog.getRecentSpikes(5);
        assertEquals(2, recent.size());
    }

    @Test
    @DisplayName("Reset clears all data")
    void testReset() {
        spikeLog.logSpike(20000, ProfilingPoint.TICK, "test");
        spikeLog.reset();

        assertEquals(0, spikeLog.getTotalSpikes());
        assertEquals(0.0, spikeLog.getWorstSpikeMs());
    }

    @Test
    @DisplayName("toMap generates valid output")
    void testToMap() {
        spikeLog.logSpike(20000, ProfilingPoint.TICK, "spike");

        var map = spikeLog.toMap();
        assertNotNull(map);
        assertTrue(map.containsKey("total_spikes"));
        assertTrue(map.containsKey("worst_spike_ms"));
    }
}
