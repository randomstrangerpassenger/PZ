package com.echo.report;

import com.echo.aggregate.TickHistogram;
import com.echo.aggregate.TimingData;
import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class EchoReportTest {

    private EchoProfiler profiler;
    private EchoReport echoReport;

    @BeforeEach
    void setUp() {
        // Validation of strategy pattern implementation
        // Manual stubbing to avoid Mockito dependency issues
        profiler = new EchoProfilerStub();
        echoReport = new EchoReport(profiler);
    }

    @Test
    void testCollectReportData() {
        Map<String, Object> data = echoReport.collectReportData();
        assertNotNull(data);
        assertTrue(data.containsKey("echo_report"));

        @SuppressWarnings("unchecked")
        Map<String, Object> inner = (Map<String, Object>) data.get("echo_report");
        assertEquals(100L, inner.get("session_duration_seconds"));
    }

    @Test
    void testJsonGeneration() {
        String json = echoReport.generateJson();
        assertNotNull(json);
        assertTrue(json.contains("\"session_duration_seconds\": 100"));
        assertTrue(json.contains("\"echo_report\""));
    }

    @Test
    void testHtmlGeneration() {
        String html = echoReport.generateHtml();
        assertNotNull(html);
        assertTrue(html.contains("<!DOCTYPE html>"));
        // Check for embedded JSON
        assertTrue(html.contains("const data = {"));
    }

    @Test
    void testCsvGeneration() {
        String csv = echoReport.generateCsv();
        assertNotNull(csv);
        assertTrue(csv.contains("point,avgMs,maxMs,minMs,callCount"));
    }

    @Test
    void testTextGeneration() {
        String text = echoReport.generateText();
        assertNotNull(text);
        assertTrue(text.contains("ECHO PROFILING REPORT"));
        // Note: Stub might return empty/null data, checking basic structure
        // If stub returns valid TimingData, we can check content
    }

    // --- Stubs ---

    private static class EchoProfilerStub extends EchoProfiler {
        // Need to override used methods.
        // EchoProfiler dependencies: config, tracker (passed in constructor)
        // Since we didn't use the constructor with args in stub, we need to be careful.
        // But EchoProfiler has a no-arg constructor? No, we added
        // `EchoProfiler(EchoConfig)`
        // and commented out calling super.
        // Wait, default constructor of EchoProfiler might be missing if I added
        // parameterized one.
        // I need to check EchoProfiler constructors.
        // Assuming I can't call super easily if it has dependencies.
        // But internal logic of EchoProfiler uses fields.

        public EchoProfilerStub() {
            super(new com.echo.config.EchoConfig()); // Requires EchoConfig public constructor (I made it public in
                                                     // Phase 4.1)
        }

        @Override
        public long getSessionDurationSeconds() {
            return 100L;
        }

        @Override
        public TickHistogram getTickHistogram() {
            return new TickHistogram() {
                @Override
                public Map<String, Object> toMap() {
                    return new HashMap<>();
                }

                @Override
                public long[] getCounts() {
                    return new long[10];
                }

                @Override
                public double[] getBuckets() {
                    return new double[10];
                }
            };
        }

        @Override
        public com.echo.aggregate.SpikeLog getSpikeLog() {
            return new com.echo.aggregate.SpikeLog();
        }

        @Override
        public Map<ProfilingPoint, TimingData> getTimingData() {
            Map<ProfilingPoint, TimingData> map = new HashMap<>();
            map.put(ProfilingPoint.TICK, getTimingData(ProfilingPoint.TICK));
            return map;
        }

        @Override
        public TimingData getTimingData(ProfilingPoint point) {
            if (point == ProfilingPoint.TICK) {
                return new TimingDataStub("TICK"); // Manual stub
            }
            return new TimingDataStub(point.name());
        }
    }

    private static class TimingDataStub extends TimingData {
        public TimingDataStub(String name) {
            super(name);
        }

        @Override
        public long getCallCount() {
            return 1000L;
        }

        @Override
        public double getAverageMicros() {
            return 16000.0;
        }

        @Override
        public long getMaxMicros() {
            return 32000L;
        }

        @Override
        public long getMinMicros() {
            return 8000L;
        }

        @Override
        public TimingData.RollingStats getStats5s() {
            return new TimingData.RollingStats(5000) {
                @Override
                public long getAverage() {
                    return 16000L;
                }
            };
        }
    }
}
