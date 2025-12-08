package com.echo.aggregate;

import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

/**
 * TimingData 단위 테스트
 */
class TimingDataTest {

    private TimingData data;

    @BeforeEach
    void setUp() {
        data = new TimingData("test");
    }

    @Test
    @DisplayName("Initial state")
    void testInitialState() {
        assertEquals("test", data.getName());
        assertEquals(0, data.getCallCount());
        assertEquals(0, data.getAverageMicros());
        assertEquals(0, data.getMaxMicros());
    }

    @Test
    @DisplayName("Add sample updates statistics")
    void testAddSample() {
        data.addSample(1000000); // 1ms in nanos

        assertEquals(1, data.getCallCount());
        assertEquals(1000, data.getAverageMicros()); // 1000 micros
    }

    @Test
    @DisplayName("Multiple samples average correctly")
    void testMultipleSamples() {
        data.addSample(1000000); // 1ms
        data.addSample(3000000); // 3ms

        assertEquals(2, data.getCallCount());
        assertEquals(2000, data.getAverageMicros()); // 2ms average
    }

    @Test
    @DisplayName("Max value tracking")
    void testMaxTracking() {
        data.addSample(1000000);
        data.addSample(5000000);
        data.addSample(2000000);

        assertEquals(5000, data.getMaxMicros());
    }

    @Test
    @DisplayName("Min value tracking")
    void testMinTracking() {
        data.addSample(5000000);
        data.addSample(1000000);
        data.addSample(3000000);

        assertEquals(1000, data.getMinMicros());
    }

    @Test
    @DisplayName("Labeled sub-timing data")
    void testLabeledData() {
        data.addSample(1000000, "func1");
        data.addSample(2000000, "func1");
        data.addSample(3000000, "func2");

        var labelStats = data.getLabelStats();
        assertEquals(2, labelStats.size());

        var func1Stats = labelStats.get("func1");
        assertEquals(2, func1Stats.getCallCount());
    }

    @Test
    @DisplayName("Top N by total time")
    void testTopN() {
        data.addSample(1000000, "slow");
        data.addSample(1000000, "slow");
        data.addSample(500000, "fast");

        var topN = data.getTopNByTotalTime(1);
        assertEquals(1, topN.size());
        assertEquals("slow", topN.get(0).getLabel());
    }

    @Test
    @DisplayName("Reset clears all data")
    void testReset() {
        data.addSample(1000000, "test");
        data.reset();

        assertEquals(0, data.getCallCount());
        assertTrue(data.getLabelStats().isEmpty());
    }
}
