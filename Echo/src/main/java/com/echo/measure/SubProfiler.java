package com.echo.measure;

import com.echo.config.EchoConfig;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.LongAdder;

/**
 * SubProfiler - Tick 내부 세부 측정 프로파일러
 * 
 * Tick 내에서 호출되는 주요 엔진 함수들의 실행 시간을 개별적으로 측정합니다.
 * Fuse 최적화 타겟을 자동으로 식별하기 위한 핵심 도구입니다.
 * 
 * 특징:
 * - Wave 기반 점진적 확장: 처음에는 최소한의 후킹 포인트만 사용
 * - Feature Flag: EchoConfig.enableSubTiming으로 활성화/비활성화
 * - Zero-Allocation 친화적 설계
 * 
 * @since Echo 1.0
 */
public class SubProfiler {

    private static final SubProfiler INSTANCE = new SubProfiler();

    // --- SubLabel ---

    /**
     * Wave 1: 최소 핵심 포인트 (3~5개)
     * Wave 2+: 점진적 확장
     */
    public enum SubLabel {
        // Wave 1 - 핵심 (첫 번째 구현)
        ZOMBIE_UPDATE(Category.AI, "ZombieUpdate", 1),
        PATHFINDING(Category.AI, "Pathfinding", 1),
        WORLD_UPDATE(Category.WORLD, "WorldUpdate", 1),

        // Wave 2 - 확장
        ISO_GRID_UPDATE(Category.WORLD, "IsoGrid.Update", 2),
        ISO_LIGHT_UPDATE(Category.RENDER, "IsoLight.Update", 2),
        ISO_GRID_RECALC(Category.WORLD, "IsoGrid.Recalc", 2),
        ISO_CELL_UPDATE(Category.WORLD, "IsoCell.Update", 2),
        RENDERING_PREP(Category.RENDER, "RenderingPrep", 2),
        SOUND_PROPAGATION(Category.AUDIO, "SoundManager", 2),

        // Wave 3 - 심층 분석 (Granular Configs)
        PATHFINDING_LOS(Category.AI, "Pathfinding.LOS", 3),
        PATHFINDING_GRID(Category.AI, "Pathfinding.Grid", 3),
        ZOMBIE_BEHAVIOR(Category.AI, "Zombie.Behavior", 3),
        ZOMBIE_MOTION(Category.AI, "Zombie.Motion", 3),
        ZOMBIE_PERCEPTION(Category.AI, "Zombie.Perception", 3),
        ZOMBIE_COLLISION(Category.AI, "Zombie.Collision", 3);

        private final Category category;
        private final String displayName;
        private final int wave; // 어느 Wave에서 활성화되는지

        SubLabel(Category category, String displayName, int wave) {
            this.category = category;
            this.displayName = displayName;
            this.wave = wave;
        }

        public Category getCategory() {
            return category;
        }

        public String getDisplayName() {
            return displayName;
        }

        public int getWave() {
            return wave;
        }

        /**
         * 현재 설정에서 이 라벨이 활성화되어야 하는지
         */
        public boolean isEnabledByConfig() {
            EchoConfig config = EchoConfig.getInstance();
            if (!config.isDeepAnalysisEnabled())
                return false;

            switch (this) {
                case PATHFINDING_LOS:
                case PATHFINDING_GRID:
                    return config.isEnablePathfindingDetails();
                case ZOMBIE_BEHAVIOR:
                case ZOMBIE_MOTION:
                case ZOMBIE_PERCEPTION:
                case ZOMBIE_COLLISION:
                case ZOMBIE_UPDATE:
                    // ZOMBIE_UPDATE is base, effectively guarded by deepAnalysis,
                    // but if details are on, we might want it too.
                    // Actually ZOMBIE_UPDATE exists in Wave 1.
                    // Wave 1 items should be enabled if deepAnalysisEnabled is true.
                    return this.wave == 1 || config.isEnableZombieDetails();
                case ISO_GRID_RECALC:
                case ISO_CELL_UPDATE:

                    return this.wave == 1 || config.isEnableIsoGridDetails();
                default:
                    return true;
            }
        }

        public enum Category {
            AI("AI", "#FF6B6B"),
            WORLD("World", "#4ECDC4"),
            RENDER("Render", "#FFE66D"),
            AUDIO("Audio", "#95E1D3"),
            PHYSICS("Physics", "#DDA0DD");

            private final String displayName;
            private final String color;

            Category(String displayName, String color) {
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
    }

    // --- SubTimingData ---

    public static class SubTimingData {
        private final SubLabel label;
        private final LongAdder callCount = new LongAdder();
        private final LongAdder totalMicros = new LongAdder();
        private final AtomicLong maxMicros = new AtomicLong(0);
        private final AtomicLong lastMicros = new AtomicLong(0);

        public SubTimingData(SubLabel label) {
            this.label = label;
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

        public SubLabel getLabel() {
            return label;
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

        public void reset() {
            callCount.reset();
            totalMicros.reset();
            maxMicros.set(0);
            lastMicros.set(0);
        }

        public Map<String, Object> toMap() {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("label", label.getDisplayName());
            map.put("category", label.getCategory().getDisplayName());
            map.put("call_count", getCallCount());
            map.put("total_ms", getTotalMs());
            map.put("avg_ms", getAverageMs());
            map.put("max_ms", getMaxMs());
            return map;
        }
    }

    // --- Fields ---

    private final Map<SubLabel, SubTimingData> subTimings = new ConcurrentHashMap<>();
    private final Map<SubLabel, Long> activeStarts = new ConcurrentHashMap<>();

    private SubProfiler() {
        // 모든 라벨에 대해 SubTimingData 초기화
        for (SubLabel label : SubLabel.values()) {
            subTimings.put(label, new SubTimingData(label));
        }
    }

    public static SubProfiler getInstance() {
        return INSTANCE;
    }

    // --- Measurement API ---

    /**
     * 서브타이밍 측정 시작
     * 
     * @param label 측정 라벨
     */
    public void start(SubLabel label) {
        if (!isEnabled() || !label.isEnabledByConfig()) {
            return;
        }
        activeStarts.put(label, System.nanoTime());
    }

    /**
     * 서브타이밍 측정 종료
     * 
     * @param label 측정 라벨
     */
    public void end(SubLabel label) {
        if (!isEnabled() || !label.isEnabledByConfig()) {
            return;
        }

        Long startTime = activeStarts.remove(label);
        if (startTime == null) {
            return; // start() 호출 없이 end() 호출됨
        }

        long elapsedNanos = System.nanoTime() - startTime;
        long elapsedMicros = elapsedNanos / 1000;

        SubTimingData data = subTimings.get(label);
        if (data != null) {
            data.record(elapsedMicros);
        }
    }

    /**
     * Raw API - 시작 시간 반환 (Zero-Allocation)
     */
    public long startRaw(SubLabel label) {
        if (!isEnabled() || !label.isEnabledByConfig()) {
            return -1;
        }
        return System.nanoTime();
    }

    /**
     * Raw API - 종료 및 기록 (Zero-Allocation)
     */
    public void endRaw(SubLabel label, long startNanos) {
        if (startNanos < 0) {
            return;
        }

        long elapsedNanos = System.nanoTime() - startNanos;
        long elapsedMicros = elapsedNanos / 1000;

        SubTimingData data = subTimings.get(label);
        if (data != null) {
            data.record(elapsedMicros);
        }
    }

    // --- Query API ---

    /**
     * SubTiming 활성화 여부
     */
    public boolean isEnabled() {
        return EchoConfig.getInstance().isDeepAnalysisEnabled();
    }

    /**
     * 데이터가 있는 엔트리 수 반환 (SelfValidation용)
     * 
     * @since Echo 0.9.0
     */
    public int getEntryCount() {
        int count = 0;
        for (SubTimingData data : subTimings.values()) {
            if (data.getCallCount() > 0) {
                count++;
            }
        }
        return count;
    }

    /**
     * 모든 SubTimingData 조회
     */
    public Collection<SubTimingData> getAllTimings() {
        return Collections.unmodifiableCollection(subTimings.values());
    }

    /**
     * 현재 실행 중인(종료되지 않은) 라벨들의 진행 시간(ms) 반환
     */
    public Map<SubLabel, Double> getActiveDurations() {
        Map<SubLabel, Double> result = new LinkedHashMap<>();
        long now = System.nanoTime();

        // activeStarts is concurrent, so safe to iterate
        for (Map.Entry<SubLabel, Long> entry : activeStarts.entrySet()) {
            double ms = (now - entry.getValue()) / 1000.0 / 1000.0;
            result.put(entry.getKey(), ms);
        }
        return result;
    }

    /**
     * 특정 라벨의 SubTimingData 조회
     */
    public SubTimingData getTimingData(SubLabel label) {
        return subTimings.get(label);
    }

    /**
     * Top N 반환 (총 시간 기준)
     */
    public List<SubTimingData> getTopNByTotalTime(int n) {
        List<SubTimingData> sorted = new ArrayList<>(subTimings.values());
        sorted.removeIf(d -> d.getCallCount() == 0);
        sorted.sort((a, b) -> Long.compare(b.getTotalMicros(), a.getTotalMicros()));
        return sorted.subList(0, Math.min(n, sorted.size()));
    }

    /**
     * Top N 반환 (최대 시간 기준 - 스파이크 탐지)
     */
    public List<SubTimingData> getTopNByMaxTime(int n) {
        List<SubTimingData> sorted = new ArrayList<>(subTimings.values());
        sorted.removeIf(d -> d.getCallCount() == 0);
        sorted.sort((a, b) -> Long.compare(b.getMaxMicros(), a.getMaxMicros()));
        return sorted.subList(0, Math.min(n, sorted.size()));
    }

    /**
     * 카테고리별 SubTimingData 조회
     */
    public List<SubTimingData> getByCategory(SubLabel.Category category) {
        List<SubTimingData> result = new ArrayList<>();
        for (SubTimingData data : subTimings.values()) {
            if (data.getLabel().getCategory() == category && data.getCallCount() > 0) {
                result.add(data);
            }
        }
        return result;
    }

    /**
     * 모든 SubTimingData를 heavy_functions 형식으로 반환
     */
    public List<Map<String, Object>> getHeavyFunctions(int topN) {
        List<Map<String, Object>> result = new ArrayList<>();
        List<SubTimingData> top = getTopNByTotalTime(topN);

        int rank = 1;
        for (SubTimingData data : top) {
            Map<String, Object> entry = data.toMap();
            entry.put("rank", rank++);
            result.add(entry);
        }

        return result;
    }

    /**
     * 초기화
     */
    public void reset() {
        for (SubTimingData data : subTimings.values()) {
            data.reset();
        }
        activeStarts.clear();
    }

    /**
     * JSON 출력용 Map
     */
    public Map<String, Object> toMap() {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("enabled", isEnabled());
        result.put("heavy_functions", getHeavyFunctions(10));

        // 카테고리별 요약
        Map<String, Double> categoryTotals = new LinkedHashMap<>();
        for (SubLabel.Category cat : SubLabel.Category.values()) {
            double total = 0;
            for (SubTimingData data : getByCategory(cat)) {
                total += data.getTotalMs();
            }
            if (total > 0) {
                categoryTotals.put(cat.getDisplayName(), total);
            }
        }
        result.put("category_totals_ms", categoryTotals);

        return result;
    }

    /**
     * 콘솔 출력
     */
    public void printStats(int topN) {
        if (!isEnabled()) {
            System.out.println("[Echo/SubProfiler] SubTiming is disabled");
            return;
        }

        System.out.println("\n[Echo/SubProfiler] Heavy Functions (Top " + topN + "):");
        System.out.println("─────────────────────────────────────────────────────────────────");
        System.out.printf("%-4s %-20s %-10s %10s %10s %10s%n",
                "Rank", "Label", "Category", "Total(ms)", "Avg(ms)", "Max(ms)");
        System.out.println("─────────────────────────────────────────────────────────────────");

        int rank = 1;
        for (SubTimingData data : getTopNByTotalTime(topN)) {
            System.out.printf("%-4d %-20s %-10s %10.2f %10.2f %10.2f%n",
                    rank++,
                    data.getLabel().getDisplayName(),
                    data.getLabel().getCategory().getDisplayName(),
                    data.getTotalMs(),
                    data.getAverageMs(),
                    data.getMaxMs());
        }
        System.out.println();
    }
}
