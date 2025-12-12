package com.pulse.lua;

import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;

import static org.mockito.Mockito.*;

@Tag("benchmark")
class BatchLuaBridgeBenchmarkTest {

    @Test
    void benchmarkBatchVsDirect() {
        // Simple micro-benchmark to compare overhead of queueing vs direct calls
        // Note: This does NOT measure actual Lua execution time, only the Java-side
        // overhead.

        int iterations = 1_000_000;

        // 1. Direct Call Simulation
        long startDirect = System.nanoTime();
        for (int i = 0; i < iterations; i++) {
            // Simulate direct call overhead
            if (i % 100 == 0) {
                // Simulate JNI boundary check
            }
        }
        long endDirect = System.nanoTime();

        // 2. Batch Queueing Simulation
        BatchLuaBridge batcher = new BatchLuaBridge(1000);

        try (MockedStatic<LuaBridge> luaBridge = mockStatic(LuaBridge.class)) {
            luaBridge.when(LuaBridge::isAvailable).thenReturn(true);

            long startBatch = System.nanoTime();
            for (int i = 0; i < iterations; i++) {
                batcher.queueCall("test", "arg");
            }
            batcher.flush(); // Flush remaining
            long endBatch = System.nanoTime();

            System.out.printf("Direct (Simulated): %.2f ms%n", (endDirect - startDirect) / 1e6);
            System.out.printf("Batch Queueing:     %.2f ms%n", (endBatch - startBatch) / 1e6);
        }
    }
}
