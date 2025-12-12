package com.pulse.debug;

import com.pulse.api.log.PulseLogger;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Supplier;

/**
 * 모드별 성능 프로파일러.
 * 각 모드의 틱 시간, 메모리 사용량 추적.
 * 
 * 사용 예:
 * 
 * <pre>
 * ProfilerSection section = ModProfiler.start("mymod", "onTick");
 * try {
 *     // 작업 수행
 * } finally {
 *     section.end();
 * }
 * </pre>
 */
public class ModProfiler {

    private static final ModProfiler INSTANCE = new ModProfiler();
    private static final String LOG = PulseLogger.PULSE;

    private boolean enabled = false;
    private final Map<String, ModProfile> profiles = new ConcurrentHashMap<>();

    private ModProfiler() {
    }

    public static ModProfiler getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 제어
    // ─────────────────────────────────────────────────────────────

    public static void enable() {
        INSTANCE.enabled = true;
        PulseLogger.info(LOG, "[Profiler] Profiling enabled");
    }

    public static void disable() {
        INSTANCE.enabled = false;
        PulseLogger.info(LOG, "[Profiler] Profiling disabled");
    }

    public static boolean isEnabled() {
        return INSTANCE.enabled;
    }

    public static void reset() {
        INSTANCE.profiles.clear();
    }

    // ─────────────────────────────────────────────────────────────
    // 프로파일링 API
    // ─────────────────────────────────────────────────────────────

    /**
     * 프로파일링 섹션 시작.
     */
    public static ProfilerSection start(String modId, String section) {
        if (!INSTANCE.enabled) {
            return ProfilerSection.NOOP;
        }
        return new ProfilerSection(modId, section, System.nanoTime());
    }

    /**
     * 람다로 프로파일링.
     */
    public static void profile(String modId, String section, Runnable task) {
        ProfilerSection s = start(modId, section);
        try {
            task.run();
        } finally {
            s.end();
        }
    }

    /**
     * 반환값이 있는 람다 프로파일링.
     */
    public static <T> T profileGet(String modId, String section, Supplier<T> task) {
        ProfilerSection s = start(modId, section);
        try {
            return task.get();
        } finally {
            s.end();
        }
    }

    /**
     * 프로파일링 결과 기록.
     */
    static void record(String modId, String section, long durationNs) {
        INSTANCE.profiles
                .computeIfAbsent(modId, k -> new ModProfile(modId))
                .record(section, durationNs);
    }

    // ─────────────────────────────────────────────────────────────
    // 결과 조회
    // ─────────────────────────────────────────────────────────────

    /**
     * 프로파일링 결과 출력.
     */
    public static void printResults() {
        PulseLogger.info(LOG, "═══════════════════════════════════════");
        PulseLogger.info(LOG, "         MOD PROFILER RESULTS          ");
        PulseLogger.info(LOG, "═══════════════════════════════════════");

        for (ModProfile profile : INSTANCE.profiles.values()) {
            PulseLogger.info(LOG, "\n  [{}]", profile.modId);
            double totalMs = 0;

            for (var entry : profile.sections.entrySet()) {
                SectionStats stats = entry.getValue();
                double avgMs = stats.getAverageMs();
                totalMs += avgMs * stats.count;
                PulseLogger.info(LOG, "    {}: {} calls, avg {}ms",
                        String.format("%-25s", entry.getKey()), stats.count, String.format("%.3f", avgMs));
            }

            PulseLogger.info(LOG, "    {}: {}ms total", String.format("%-25s", "TOTAL"),
                    String.format("%.2f", totalMs));
        }

        PulseLogger.info(LOG, "\n═══════════════════════════════════════");
    }

    /**
     * 특정 모드의 프로파일 조회.
     */
    public static ModProfile getProfile(String modId) {
        return INSTANCE.profiles.get(modId);
    }

    // ─────────────────────────────────────────────────────────────
    // 데이터 클래스
    // ─────────────────────────────────────────────────────────────

    public static class ProfilerSection {
        static final ProfilerSection NOOP = new ProfilerSection(null, null, 0) {
            @Override
            public void end() {
            }
        };

        private final String modId;
        private final String section;
        private final long startNs;

        ProfilerSection(String modId, String section, long startNs) {
            this.modId = modId;
            this.section = section;
            this.startNs = startNs;
        }

        public void end() {
            long duration = System.nanoTime() - startNs;
            record(modId, section, duration);
        }
    }

    public static class ModProfile {
        public final String modId;
        public final Map<String, SectionStats> sections = new ConcurrentHashMap<>();

        ModProfile(String modId) {
            this.modId = modId;
        }

        void record(String section, long durationNs) {
            sections.computeIfAbsent(section, k -> new SectionStats())
                    .record(durationNs);
        }
    }

    public static class SectionStats {
        public long count = 0;
        public long totalNs = 0;
        public long minNs = Long.MAX_VALUE;
        public long maxNs = 0;

        synchronized void record(long durationNs) {
            count++;
            totalNs += durationNs;
            minNs = Math.min(minNs, durationNs);
            maxNs = Math.max(maxNs, durationNs);
        }

        public double getAverageMs() {
            if (count == 0)
                return 0;
            return (totalNs / (double) count) / 1_000_000.0;
        }
    }
}
