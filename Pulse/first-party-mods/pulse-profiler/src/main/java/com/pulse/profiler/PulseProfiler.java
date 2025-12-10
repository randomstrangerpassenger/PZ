package com.pulse.profiler;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Pulse 프로파일러 유틸리티.
 * 코드 구간의 실행 시간을 측정.
 * 
 * 사용 예:
 * PulseProfiler.begin("my_section");
 * // ... 코드 ...
 * PulseProfiler.end("my_section");
 * 
 * // 또는 try-with-resources:
 * try (var section = PulseProfiler.section("my_section")) {
 * // ... 코드 ...
 * }
 */
public class PulseProfiler {

    private static final Map<String, ProfileSection> sections = new ConcurrentHashMap<>();
    private static final ThreadLocal<Map<String, Long>> startTimes = ThreadLocal.withInitial(HashMap::new);

    private static boolean enabled = true;

    // ─────────────────────────────────────────────────────────────
    // 프로파일링 API
    // ─────────────────────────────────────────────────────────────

    /**
     * 프로파일 구간 시작
     */
    public static void begin(String name) {
        if (!enabled)
            return;
        startTimes.get().put(name, System.nanoTime());
    }

    /**
     * 프로파일 구간 종료
     */
    public static void end(String name) {
        if (!enabled)
            return;

        Long startTime = startTimes.get().remove(name);
        if (startTime == null) {
            System.err.println("[Pulse/Profiler] end() called without matching begin() for: " + name);
            return;
        }

        long elapsed = System.nanoTime() - startTime;

        ProfileSection section = sections.computeIfAbsent(name, ProfileSection::new);
        section.record(elapsed);
    }

    /**
     * AutoCloseable 프로파일 구간 (try-with-resources 용)
     */
    public static ProfileScope section(String name) {
        begin(name);
        return new ProfileScope(name);
    }

    // ─────────────────────────────────────────────────────────────
    // 통계
    // ─────────────────────────────────────────────────────────────

    /**
     * 모든 구간 통계 가져오기
     */
    public static Collection<ProfileSection> getAllSections() {
        return Collections.unmodifiableCollection(sections.values());
    }

    /**
     * 특정 구간 통계 가져오기
     */
    public static ProfileSection getSection(String name) {
        return sections.get(name);
    }

    /**
     * 모든 통계 초기화
     */
    public static void reset() {
        sections.clear();
    }

    /**
     * 통계 로그 출력
     */
    public static void logStats() {
        if (sections.isEmpty()) {
            System.out.println("[Pulse/Profiler] No profiling data collected");
            return;
        }

        System.out.println("[Pulse/Profiler] ═══════════════════════════════════════");
        System.out.println("[Pulse/Profiler] PROFILING STATISTICS");
        System.out.println("[Pulse/Profiler] ═══════════════════════════════════════");

        // 평균 시간 기준 내림차순 정렬
        List<ProfileSection> sorted = new ArrayList<>(sections.values());
        sorted.sort((a, b) -> Long.compare(b.getAverageNanos(), a.getAverageNanos()));

        for (ProfileSection section : sorted) {
            if (section.getCallCount() == 0)
                continue;

            System.out.printf("[Pulse/Profiler] %-30s avg: %8.3fms  total: %10.3fms  calls: %d%n",
                    section.getName(),
                    section.getAverageNanos() / 1_000_000.0,
                    section.getTotalNanos() / 1_000_000.0,
                    section.getCallCount());
        }

        System.out.println("[Pulse/Profiler] ═══════════════════════════════════════");
    }

    // ─────────────────────────────────────────────────────────────
    // 제어
    // ─────────────────────────────────────────────────────────────

    public static void setEnabled(boolean enable) {
        enabled = enable;
    }

    public static boolean isEnabled() {
        return enabled;
    }

    // ─────────────────────────────────────────────────────────────
    // 내부 클래스
    // ─────────────────────────────────────────────────────────────

    /**
     * AutoCloseable 프로파일 스코프
     */
    public static class ProfileScope implements AutoCloseable {
        private final String name;

        ProfileScope(String name) {
            this.name = name;
        }

        @Override
        public void close() {
            end(name);
        }
    }
}
