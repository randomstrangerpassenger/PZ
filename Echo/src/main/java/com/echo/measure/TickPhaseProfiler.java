package com.echo.measure;

import com.echo.config.EchoConfig;

import java.util.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.LongAdder;

/**
 * Tick Phase 분해 프로파일러
 * 
 * 게임 틱을 여러 단계(AI, Physics, World Update, Rendering Prep, IsoGrid)로
 * 분해하여 각 단계별 소요 시간을 측정합니다.
 * 
 * Fuse 개발 시 "AI Phase만 20→10ms로 줄었다" 같은 정량화가 가능해집니다.
 * 
 * @since Echo 1.0
 */
public class TickPhaseProfiler {

    private static final TickPhaseProfiler INSTANCE = new TickPhaseProfiler();

    // --- TickPhase Enum ---

    public enum TickPhase {
        AI_PHASE("AI Phase", "#FF6B6B"),
        PHYSICS_PHASE("Physics Phase", "#4ECDC4"),
        WORLD_UPDATE("World Update", "#FFE66D"),
        RENDERING_PREP("Rendering Prep", "#95E1D3"),
        ISO_GRID_UPDATE("IsoGrid Update", "#DDA0DD");

        private final String displayName;
        private final String color;

        TickPhase(String displayName, String color) {
            this.displayName = displayName;
            this.color = color;
        }

        public String getDisplayName() {
            return displayName;
        }

        public String getColor() {
            return color;
        }
    }

    // --- PhaseTimingData - 단계별 타이밍 데이터 ---

    public static class PhaseTimingData {
        private final TickPhase phase;
        private final LongAdder callCount = new LongAdder();
        private final LongAdder totalMicros = new LongAdder();
        private final AtomicLong maxMicros = new AtomicLong(0);
        private final AtomicLong lastMicros = new AtomicLong(0);

        public PhaseTimingData(TickPhase phase) {
            this.phase = phase;
        }

        public void record(long durationMicros) {
            callCount.increment();
            totalMicros.add(durationMicros);
            lastMicros.set(durationMicros);

            // Update max (lock-free)
            long currentMax;
            do {
                currentMax = maxMicros.get();
                if (durationMicros <= currentMax)
                    break;
            } while (!maxMicros.compareAndSet(currentMax, durationMicros));
        }

        public TickPhase getPhase() {
            return phase;
        }

        public long getCallCount() {
            return callCount.sum();
        }

        public long getTotalMicros() {
            return totalMicros.sum();
        }

        public long getMaxMicros() {
            return maxMicros.get();
        }

        public long getLastMicros() {
            return lastMicros.get();
        }

        public double getAverageMicros() {
            long count = callCount.sum();
            return count > 0 ? (double) totalMicros.sum() / count : 0.0;
        }

        public double getTotalMs() {
            return totalMicros.sum() / 1000.0;
        }

        public double getAverageMs() {
            return getAverageMicros() / 1000.0;
        }

        public double getMaxMs() {
            return maxMicros.get() / 1000.0;
        }

        public double getLastMs() {
            return lastMicros.get() / 1000.0;
        }

        public void reset() {
            callCount.reset();
            totalMicros.reset();
            maxMicros.set(0);
            lastMicros.set(0);
        }

        public Map<String, Object> toMap() {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("phase", phase.getDisplayName());
            map.put("call_count", getCallCount());
            map.put("total_ms", getTotalMs());
            map.put("avg_ms", getAverageMs());
            map.put("max_ms", getMaxMs());
            map.put("last_ms", getLastMs());
            return map;
        }
    }

    // --- 필드 ---

    private final Map<TickPhase, PhaseTimingData> phaseTimings = new EnumMap<>(TickPhase.class);
    private final Map<TickPhase, Long> activeStarts = new EnumMap<>(TickPhase.class);

    // 현재 틱의 Phase별 시간 (틱 완료 시 리셋)
    private final Map<TickPhase, Long> currentTickPhases = new EnumMap<>(TickPhase.class);

    private TickPhaseProfiler() {
        for (TickPhase phase : TickPhase.values()) {
            phaseTimings.put(phase, new PhaseTimingData(phase));
        }
    }

    public static TickPhaseProfiler getInstance() {
        return INSTANCE;
    }

    // --- 측정 API ---

    /**
     * Phase 측정 시작
     */
    public void startPhase(TickPhase phase) {
        if (!isEnabled())
            return;
        activeStarts.put(phase, System.nanoTime());
    }

    /**
     * Phase 측정 종료
     */
    public void endPhase(TickPhase phase) {
        if (!isEnabled())
            return;

        Long startTime = activeStarts.remove(phase);
        if (startTime == null)
            return;

        long elapsedNanos = System.nanoTime() - startTime;
        long elapsedMicros = elapsedNanos / 1000;

        PhaseTimingData data = phaseTimings.get(phase);
        if (data != null) {
            data.record(elapsedMicros);
        }

        // 현재 틱 Phase 시간 누적
        currentTickPhases.merge(phase, elapsedMicros, Long::sum);
    }

    /**
     * Raw API - 시작 시간 반환 (Zero-Allocation)
     */
    public long startPhaseRaw(TickPhase phase) {
        if (!isEnabled())
            return -1;
        return System.nanoTime();
    }

    /**
     * Raw API - 종료 및 기록 (Zero-Allocation)
     */
    public void endPhaseRaw(TickPhase phase, long startNanos) {
        if (startNanos < 0)
            return;

        long elapsedNanos = System.nanoTime() - startNanos;
        long elapsedMicros = elapsedNanos / 1000;

        PhaseTimingData data = phaseTimings.get(phase);
        if (data != null) {
            data.record(elapsedMicros);
        }

        currentTickPhases.merge(phase, elapsedMicros, Long::sum);
    }

    /**
     * 틱 완료 시 현재 틱의 Phase 타이밍 리셋
     */
    public void onTickComplete() {
        currentTickPhases.clear();
    }

    // --- 조회 API ---

    public boolean isEnabled() {
        return EchoConfig.getInstance().isDeepAnalysisEnabled();
    }

    public PhaseTimingData getPhaseData(TickPhase phase) {
        return phaseTimings.get(phase);
    }

    public Collection<PhaseTimingData> getAllPhaseData() {
        return Collections.unmodifiableCollection(phaseTimings.values());
    }

    /**
     * 데이터가 있는 Phase 수 반환 (Quality Scorer용)
     * 
     * @since Echo 0.9.0
     */
    public int getTotalPhaseCount() {
        int count = 0;
        for (PhaseTimingData data : phaseTimings.values()) {
            if (data.getCallCount() > 0) {
                count++;
            }
        }
        return count;
    }

    /**
     * 현재 틱의 Phase별 시간 반환 (ms 단위)
     */
    public Map<TickPhase, Double> getCurrentTickPhaseMs() {
        Map<TickPhase, Double> result = new EnumMap<>(TickPhase.class);
        for (Map.Entry<TickPhase, Long> entry : currentTickPhases.entrySet()) {
            result.put(entry.getKey(), entry.getValue() / 1000.0);
        }
        return result;
    }

    /**
     * 전체 Phase 합계 대비 비율 반환
     */
    public Map<TickPhase, Double> getPhasePercentages() {
        Map<TickPhase, Double> result = new EnumMap<>(TickPhase.class);
        long total = 0;

        for (PhaseTimingData data : phaseTimings.values()) {
            total += data.getTotalMicros();
        }

        if (total > 0) {
            for (Map.Entry<TickPhase, PhaseTimingData> entry : phaseTimings.entrySet()) {
                double percentage = (entry.getValue().getTotalMicros() * 100.0) / total;
                result.put(entry.getKey(), percentage);
            }
        }

        return result;
    }

    /**
     * 초기화
     */
    public void reset() {
        for (PhaseTimingData data : phaseTimings.values()) {
            data.reset();
        }
        activeStarts.clear();
        currentTickPhases.clear();
    }

    /**
     * JSON 출력용 Map
     */
    public Map<String, Object> toMap() {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("enabled", isEnabled());

        List<Map<String, Object>> phases = new ArrayList<>();
        for (PhaseTimingData data : phaseTimings.values()) {
            if (data.getCallCount() > 0) {
                phases.add(data.toMap());
            }
        }
        result.put("phases", phases);

        // 비율 추가
        Map<String, Double> percentages = new LinkedHashMap<>();
        for (Map.Entry<TickPhase, Double> entry : getPhasePercentages().entrySet()) {
            percentages.put(entry.getKey().getDisplayName(),
                    Math.round(entry.getValue() * 100.0) / 100.0);
        }
        result.put("percentages", percentages);

        return result;
    }

    /**
     * 콘솔 출력
     */
    public void printStats() {
        if (!isEnabled()) {
            System.out.println("[Echo/TickPhase] Tick Phase Breakdown is disabled");
            return;
        }

        System.out.println("\n[Echo/TickPhase] Tick Phase Breakdown:");
        System.out.println("─────────────────────────────────────────────────────────────────");
        System.out.printf("%-20s %10s %10s %10s %8s%n",
                "Phase", "Total(ms)", "Avg(ms)", "Max(ms)", "%");
        System.out.println("─────────────────────────────────────────────────────────────────");

        Map<TickPhase, Double> percentages = getPhasePercentages();

        for (PhaseTimingData data : phaseTimings.values()) {
            if (data.getCallCount() > 0) {
                double pct = percentages.getOrDefault(data.getPhase(), 0.0);
                System.out.printf("%-20s %10.2f %10.2f %10.2f %7.1f%%%n",
                        data.getPhase().getDisplayName(),
                        data.getTotalMs(),
                        data.getAverageMs(),
                        data.getMaxMs(),
                        pct);
            }
        }
        System.out.println();
    }
}
