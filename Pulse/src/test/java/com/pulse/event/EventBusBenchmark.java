package com.pulse.event;

import com.pulse.api.event.Event;
import com.pulse.api.event.EventPriority;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

/**
 * EventBus Hot Path 벤치마크.
 * 
 * v4 Phase 0-B: 리팩토링 후 "느려짐(퇴행)"을 탐지하기 위한 기준선 기록.
 * "빨라졌다"를 증명하는 것이 아니라, "느려지지 않았다"를 확인.
 * 
 * 실행: ./gradlew test --tests "*EventBusBenchmark*" -Dtag=benchmark
 * 
 * 기준선 파일: src/test/resources/benchmarks/eventbus_baseline.txt
 */
@Tag("benchmark")
class EventBusBenchmark {

    private static final int ITERATIONS = 1000;
    private static final int WARMUP_ITERATIONS = 100;

    private EventBus eventBus;

    @BeforeEach
    void setUp() {
        eventBus = EventBus.getInstance();
        eventBus.clearAll();
    }

    /**
     * fire() 기준선 벤치마크: 10개 리스너.
     * 가장 일반적인 사용 패턴.
     */
    @Test
    void fire_baseline_10_listeners() {
        // Given: 10개 리스너 등록 (우선순위 혼합)
        List<String> sink = new ArrayList<>();
        for (int i = 0; i < 4; i++) {
            EventBus.subscribe(BenchmarkEvent.class, e -> sink.add("LOW"), EventPriority.LOW);
        }
        for (int i = 0; i < 3; i++) {
            EventBus.subscribe(BenchmarkEvent.class, e -> sink.add("NORMAL"), EventPriority.NORMAL);
        }
        for (int i = 0; i < 3; i++) {
            EventBus.subscribe(BenchmarkEvent.class, e -> sink.add("HIGH"), EventPriority.HIGH);
        }

        // Warmup
        for (int i = 0; i < WARMUP_ITERATIONS; i++) {
            sink.clear();
            eventBus.fire(new BenchmarkEvent());
        }

        // Benchmark
        sink.clear();
        long startNanos = System.nanoTime();
        for (int i = 0; i < ITERATIONS; i++) {
            eventBus.fire(new BenchmarkEvent());
        }
        long elapsedNanos = System.nanoTime() - startNanos;

        // Report
        double avgMicros = (elapsedNanos / 1000.0) / ITERATIONS;
        double totalMs = elapsedNanos / 1_000_000.0;

        System.out.println("═══════════════════════════════════════════════════════════");
        System.out.println("EventBus Benchmark: 10 listeners, " + ITERATIONS + " iterations");
        System.out.println("Total: " + String.format("%.2f", totalMs) + " ms");
        System.out.println("Average: " + String.format("%.3f", avgMicros) + " μs/fire");
        System.out.println("═══════════════════════════════════════════════════════════");

        // 퇴행 탐지 기준: 기준선 대비 200% 초과 시 경고 (엄격하지 않음)
        // 기준선은 첫 실행 후 baseline.txt에 기록
        // 현재는 정보 출력만 (자동 실패 없음)
    }

    /**
     * fire() 스트레스 벤치마크: 100개 리스너.
     * 대형 모드팩 시나리오.
     */
    @Test
    void fire_stress_100_listeners() {
        // Given: 100개 리스너 등록
        List<String> sink = new ArrayList<>();
        for (int i = 0; i < 40; i++) {
            EventBus.subscribe(BenchmarkEvent.class, e -> sink.add("LOW"), EventPriority.LOW);
        }
        for (int i = 0; i < 30; i++) {
            EventBus.subscribe(BenchmarkEvent.class, e -> sink.add("NORMAL"), EventPriority.NORMAL);
        }
        for (int i = 0; i < 30; i++) {
            EventBus.subscribe(BenchmarkEvent.class, e -> sink.add("HIGH"), EventPriority.HIGH);
        }

        // Warmup
        for (int i = 0; i < WARMUP_ITERATIONS; i++) {
            sink.clear();
            eventBus.fire(new BenchmarkEvent());
        }

        // Benchmark
        sink.clear();
        long startNanos = System.nanoTime();
        for (int i = 0; i < ITERATIONS; i++) {
            eventBus.fire(new BenchmarkEvent());
        }
        long elapsedNanos = System.nanoTime() - startNanos;

        // Report
        double avgMicros = (elapsedNanos / 1000.0) / ITERATIONS;
        double totalMs = elapsedNanos / 1_000_000.0;

        System.out.println("═══════════════════════════════════════════════════════════");
        System.out.println("EventBus Benchmark: 100 listeners, " + ITERATIONS + " iterations");
        System.out.println("Total: " + String.format("%.2f", totalMs) + " ms");
        System.out.println("Average: " + String.format("%.3f", avgMicros) + " μs/fire");
        System.out.println("═══════════════════════════════════════════════════════════");
    }

    // 벤치마크용 이벤트 클래스
    static class BenchmarkEvent extends Event {
        BenchmarkEvent() {
            super(false);
        }
    }
}
