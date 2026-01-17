package com.echo.baseline;

import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;
import org.junit.jupiter.api.*;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Phase 0: Performance Baseline Test
 * 
 * push/pop 핫패스 성능 기준선을 측정합니다.
 * 리팩토링 후 10% 이상 저하 시 롤백 대상.
 */
class PerformanceBaseline {

    private static final int WARMUP_ITERATIONS = 10_000;
    private static final int BENCHMARK_ITERATIONS = 1_000_000;

    private EchoProfiler profiler;

    @BeforeEach
    void setUp() {
        profiler = EchoProfiler.getInstance();
        profiler.reset();
        profiler.enable(true);
        EchoProfiler.setMainThread(Thread.currentThread());
    }

    @AfterEach
    void tearDown() {
        profiler.disable();
    }

    @Test
    @DisplayName("Baseline: push/pop 1M iterations")
    void baseline_pushPop_1M() {
        // Warmup
        for (int i = 0; i < WARMUP_ITERATIONS; i++) {
            profiler.push(ProfilingPoint.TICK);
            profiler.pop(ProfilingPoint.TICK);
        }
        profiler.reset();
        profiler.enable(true);

        // Benchmark
        long start = System.nanoTime();
        for (int i = 0; i < BENCHMARK_ITERATIONS; i++) {
            profiler.push(ProfilingPoint.TICK);
            profiler.pop(ProfilingPoint.TICK);
        }
        long elapsed = System.nanoTime() - start;

        double nsPerOp = (double) elapsed / BENCHMARK_ITERATIONS;
        double msTotal = elapsed / 1_000_000.0;

        System.out.println("=== Performance Baseline ===");
        System.out.println("Iterations: " + BENCHMARK_ITERATIONS);
        System.out.println("Total time: " + msTotal + " ms");
        System.out.println("Per operation: " + nsPerOp + " ns");
        System.out.println("Ops/sec: " + (1_000_000_000L / nsPerOp));

        // 기준선: push/pop 쌍이 1000ns 미만이어야 함 (매우 관대한 기준)
        assertTrue(nsPerOp < 1000,
                "push/pop should complete in < 1000ns, actual: " + nsPerOp + "ns");
    }

    @Test
    @DisplayName("Baseline: startRaw/endRaw 1M iterations (zero-allocation)")
    void baseline_rawApi_1M() {
        // Warmup
        for (int i = 0; i < WARMUP_ITERATIONS; i++) {
            long t = profiler.startRaw(ProfilingPoint.TICK);
            profiler.endRaw(ProfilingPoint.TICK, t);
        }
        profiler.reset();
        profiler.enable(true);

        // Benchmark
        long start = System.nanoTime();
        for (int i = 0; i < BENCHMARK_ITERATIONS; i++) {
            long t = profiler.startRaw(ProfilingPoint.TICK);
            profiler.endRaw(ProfilingPoint.TICK, t);
        }
        long elapsed = System.nanoTime() - start;

        double nsPerOp = (double) elapsed / BENCHMARK_ITERATIONS;
        double msTotal = elapsed / 1_000_000.0;

        System.out.println("=== Raw API Baseline ===");
        System.out.println("Iterations: " + BENCHMARK_ITERATIONS);
        System.out.println("Total time: " + msTotal + " ms");
        System.out.println("Per operation: " + nsPerOp + " ns");

        // Raw API는 push/pop보다 빨라야 함
        assertTrue(nsPerOp < 500,
                "startRaw/endRaw should complete in < 500ns, actual: " + nsPerOp + "ns");
    }

    @Test
    @DisplayName("Baseline: scope API with try-with-resources")
    void baseline_scopeApi() {
        // Warmup
        for (int i = 0; i < WARMUP_ITERATIONS; i++) {
            try (var scope = profiler.scope(ProfilingPoint.ZOMBIE_AI)) {
                // no-op
            }
        }
        profiler.reset();
        profiler.enable(true);

        int iterations = 100_000; // scope는 더 무거우므로 적게
        long start = System.nanoTime();
        for (int i = 0; i < iterations; i++) {
            try (var scope = profiler.scope(ProfilingPoint.ZOMBIE_AI)) {
                // no-op
            }
        }
        long elapsed = System.nanoTime() - start;

        double nsPerOp = (double) elapsed / iterations;
        System.out.println("=== Scope API Baseline ===");
        System.out.println("Per operation: " + nsPerOp + " ns");

        // scope는 객체 풀링으로 1500ns 미만이어야 함
        assertTrue(nsPerOp < 1500,
                "scope API should complete in < 1500ns, actual: " + nsPerOp + "ns");
    }
}
