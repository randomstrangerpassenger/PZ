package com.echo.analysis;

import com.echo.aggregate.TimingData;
import com.echo.measure.*;
import com.echo.subsystem.*;

import java.util.*;

/**
 * 자동 병목 식별기.
 * 
 * 성능 병목을 자동으로 식별하고 최적화 타짓을 제안합니다.
 * 
 * @since 1.0.1
 * @since 2.0 - Pulse 정화로 인해 Echo 내부 클래스로 이동
 */
public class BottleneckDetector {

    private static final BottleneckDetector INSTANCE = new BottleneckDetector();

    // 임계값
    private static final double TICK_THRESHOLD_MS = 16.67;
    private static final double CRITICAL_RATIO = 0.3; // 전체의 30% 이상이면 병목

    public static BottleneckDetector getInstance() {
        return INSTANCE;
    }

    /**
     * 상위 N개 병목 식별
     */
    public List<Bottleneck> identifyTopN(int n) {
        List<Bottleneck> bottlenecks = new ArrayList<>();

        EchoProfiler profiler = EchoProfiler.getInstance();
        TimingData tickData = profiler.getTimingData(ProfilingPoint.TICK);
        if (tickData == null || tickData.getCallCount() == 0) {
            return bottlenecks;
        }

        double totalTickMs = tickData.getAverageMicros() / 1000.0;

        // 각 서브시스템 분석
        for (ProfilingPoint point : ProfilingPoint.values()) {
            if (point.getCategory() != ProfilingPoint.Category.SUBSYSTEM)
                continue;

            TimingData data = profiler.getTimingData(point);
            if (data == null || data.getCallCount() == 0)
                continue;

            double avgMs = data.getAverageMicros() / 1000.0;
            double ratio = totalTickMs > 0 ? avgMs / totalTickMs : 0;

            if (ratio >= 0.1) { // 10% 이상이면 병목 후보
                BottleneckType type = classifyBottleneck(point, ratio);
                OptimizationModule module = suggestModule(point);
                int priority = calculatePriority(point, ratio, avgMs);

                // CRITICAL_RATIO 이상이면 우선순위 가산
                if (ratio >= CRITICAL_RATIO) {
                    priority = Math.min(100, priority + 20);
                }

                bottlenecks.add(new Bottleneck(
                        point.name(),
                        point.getDisplayName(),
                        avgMs,
                        ratio,
                        type,
                        module,
                        priority));
            }
        }

        // Deep Analysis 병목 추가
        addDeepAnalysisBottlenecks(bottlenecks, totalTickMs);

        // 우선순위로 정렬
        bottlenecks.sort((a, b) -> Integer.compare(b.priority, a.priority));

        return bottlenecks.size() > n ? bottlenecks.subList(0, n) : bottlenecks;
    }

    private void addDeepAnalysisBottlenecks(List<Bottleneck> bottlenecks, double totalTickMs) {
        // 패스파인딩
        PathfindingProfiler pf = PathfindingProfiler.getInstance();
        double pfMs = pf.getTotalTimeMs();
        if (pfMs > 1.0) {
            double ratio = pfMs / totalTickMs;
            bottlenecks.add(new Bottleneck(
                    "PATHFINDING_DEEP",
                    "Pathfinding (Detailed)",
                    pfMs,
                    ratio,
                    BottleneckType.CPU_BOUND,
                    OptimizationModule.FUSE,
                    calculatePriority(null, ratio, pfMs)));
        }

        // 좀비 AI
        ZombieProfiler zp = ZombieProfiler.getInstance();
        int zombieCount = (int) zp.getZombieCount();
        if (zombieCount > 100) {
            // 좀비당 추정 시간
            double estimatedMs = zombieCount * 0.05; // 0.05ms per zombie
            double ratio = estimatedMs / totalTickMs;
            if (ratio > 0.1) {
                bottlenecks.add(new Bottleneck(
                        "ZOMBIE_PROCESSING",
                        "Zombie Processing (" + zombieCount + " zombies)",
                        estimatedMs,
                        ratio,
                        BottleneckType.CPU_BOUND,
                        OptimizationModule.FUSE,
                        (int) (ratio * 100)));
            }
        }
    }

    /**
     * CPU 최적화 타겟 제안 (Fuse 용)
     */
    public OptimizationPriority suggestFuseTarget() {
        List<Bottleneck> bottlenecks = identifyTopN(5);

        for (Bottleneck b : bottlenecks) {
            if (b.suggestedModule == OptimizationModule.FUSE) {
                return new OptimizationPriority(
                        b.name,
                        b.displayName,
                        b.priority,
                        generateFuseRecommendation(b));
            }
        }

        return new OptimizationPriority("NONE", "No CPU bottleneck identified", 0,
                "Current performance is acceptable.");
    }

    /**
     * IO/네트워크 최적화 타겟 제안 (Nerve 용)
     */
    public OptimizationPriority suggestNerveTarget() {
        List<Bottleneck> bottlenecks = identifyTopN(5);

        for (Bottleneck b : bottlenecks) {
            if (b.suggestedModule == OptimizationModule.NERVE) {
                return new OptimizationPriority(
                        b.name,
                        b.displayName,
                        b.priority,
                        generateNerveRecommendation(b));
            }
        }

        return new OptimizationPriority("NONE", "No IO/Network bottleneck identified", 0,
                "Current load is manageable.");
    }

    /**
     * 이상 탐지
     */
    public AnomalyReport detectAnomalies() {
        AnomalyReport report = new AnomalyReport();

        EchoProfiler profiler = EchoProfiler.getInstance();
        TimingData tickData = profiler.getTimingData(ProfilingPoint.TICK);

        if (tickData == null)
            return report;

        // 틱 시간 이상
        double avgMs = tickData.getAverageMicros() / 1000.0;
        double maxMs = tickData.getMaxMicros() / 1000.0;

        if (avgMs > TICK_THRESHOLD_MS * 2) {
            report.addAnomaly(AnomalySeverity.CRITICAL, "TICK_OVERLOAD",
                    String.format("Average tick time (%.2fms) is 2x over target", avgMs));
        } else if (avgMs > TICK_THRESHOLD_MS) {
            report.addAnomaly(AnomalySeverity.WARNING, "TICK_SLOW",
                    String.format("Average tick time (%.2fms) exceeds target", avgMs));
        }

        // 스파이크 이상
        if (maxMs > avgMs * 5) {
            report.addAnomaly(AnomalySeverity.WARNING, "SPIKE_DETECTED",
                    String.format("Max spike (%.2fms) is 5x average", maxMs));
        }

        // 메모리 이상
        double memUsage = MemoryProfiler.getHeapUsagePercent();
        if (memUsage > 90) {
            report.addAnomaly(AnomalySeverity.CRITICAL, "MEMORY_CRITICAL",
                    String.format("Heap usage at %.1f%%", memUsage));
        } else if (memUsage > 75) {
            report.addAnomaly(AnomalySeverity.WARNING, "MEMORY_HIGH",
                    String.format("Heap usage at %.1f%%", memUsage));
        }

        return report;
    }

    /**
     * JSON 출력
     */
    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();

        // Top 5 병목
        List<Map<String, Object>> bottleneckList = new ArrayList<>();
        for (Bottleneck b : identifyTopN(5)) {
            Map<String, Object> bMap = new LinkedHashMap<>();
            bMap.put("name", b.name);
            bMap.put("display_name", b.displayName);
            bMap.put("avg_ms", Math.round(b.avgMs * 100) / 100.0);
            bMap.put("ratio_percent", Math.round(b.ratio * 10000) / 100.0);
            bMap.put("type", b.type.name());
            bMap.put("suggested_module", b.suggestedModule.name());
            bMap.put("priority", b.priority);
            bottleneckList.add(bMap);
        }
        map.put("top_bottlenecks", bottleneckList);

        // 최적화 제안
        Map<String, Object> suggestions = new LinkedHashMap<>();
        OptimizationPriority fuse = suggestFuseTarget();
        suggestions.put("fuse_target", fuse.toMap());
        OptimizationPriority nerve = suggestNerveTarget();
        suggestions.put("nerve_target", nerve.toMap());
        map.put("optimization_suggestions", suggestions);

        // 이상 탐지
        map.put("anomalies", detectAnomalies().toMap());

        return map;
    }

    // --- 헬퍼 메서드 ---

    private BottleneckType classifyBottleneck(ProfilingPoint point, double ratio) {
        return switch (point) {
            case RENDER, RENDER_WORLD, RENDER_UI -> BottleneckType.GPU_BOUND;
            case NETWORK -> BottleneckType.IO_BOUND;
            case CHUNK_IO -> BottleneckType.IO_BOUND;
            default -> BottleneckType.CPU_BOUND;
        };
    }

    private OptimizationModule suggestModule(ProfilingPoint point) {
        return switch (point) {
            case ZOMBIE_AI, SIMULATION, PHYSICS -> OptimizationModule.FUSE;
            case RENDER, RENDER_WORLD -> OptimizationModule.NERVE;
            case NETWORK -> OptimizationModule.NERVE;
            default -> OptimizationModule.FUSE;
        };
    }

    private int calculatePriority(ProfilingPoint point, double ratio, double avgMs) {
        int base = (int) (ratio * 100);
        if (avgMs > TICK_THRESHOLD_MS)
            base += 20;
        if (avgMs > TICK_THRESHOLD_MS * 2)
            base += 30;
        return Math.min(100, base);
    }

    private String generateFuseRecommendation(Bottleneck b) {
        return switch (b.name) {
            case "ZOMBIE_AI" -> "Consider zombie AI pooling and LOD-based update frequency";
            case "SIMULATION" -> "Review high-frequency simulation updates for batching opportunities";
            case "PHYSICS" -> "Implement physics LOD or reduce collision check frequency";
            case "PATHFINDING_DEEP" -> "Cache pathfinding results and implement hierarchical pathfinding";
            default -> "Profile detailed call stacks to identify hot paths";
        };
    }

    private String generateNerveRecommendation(Bottleneck b) {
        return switch (b.name) {
            case "RENDER" -> "Implement occlusion culling and batch similar draw calls";
            case "RENDER_WORLD" -> "Consider LOD for distant objects and frustum culling";
            case "NETWORK" -> "Batch network packets and implement delta compression";
            default -> "Monitor I/O patterns for optimization opportunities";
        };
    }

    // --- 내부 클래스 ---

    public static class Bottleneck {
        public final String name;
        public final String displayName;
        public final double avgMs;
        public final double ratio;
        public final BottleneckType type;
        public final OptimizationModule suggestedModule;
        public final int priority;

        public Bottleneck(String name, String displayName, double avgMs, double ratio,
                BottleneckType type, OptimizationModule suggestedModule, int priority) {
            this.name = name;
            this.displayName = displayName;
            this.avgMs = avgMs;
            this.ratio = ratio;
            this.type = type;
            this.suggestedModule = suggestedModule;
            this.priority = priority;
        }
    }

    public enum BottleneckType {
        CPU_BOUND, GPU_BOUND, IO_BOUND, MEMORY_BOUND
    }

    public enum OptimizationModule {
        FUSE, NERVE, EITHER
    }

    public static class AnomalyReport {
        private final List<Anomaly> anomalies = new ArrayList<>();

        public void addAnomaly(AnomalySeverity severity, String type, String message) {
            anomalies.add(new Anomaly(severity, type, message));
        }

        public boolean hasAnomalies() {
            return !anomalies.isEmpty();
        }

        public boolean hasCritical() {
            return anomalies.stream().anyMatch(a -> a.severity == AnomalySeverity.CRITICAL);
        }

        public Map<String, Object> toMap() {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("count", anomalies.size());
            map.put("has_critical", hasCritical());

            List<Map<String, String>> list = new ArrayList<>();
            for (Anomaly a : anomalies) {
                Map<String, String> aMap = new LinkedHashMap<>();
                aMap.put("severity", a.severity.name());
                aMap.put("type", a.type);
                aMap.put("message", a.message);
                list.add(aMap);
            }
            map.put("items", list);

            return map;
        }
    }

    public static class Anomaly {
        public final AnomalySeverity severity;
        public final String type;
        public final String message;

        public Anomaly(AnomalySeverity severity, String type, String message) {
            this.severity = severity;
            this.type = type;
            this.message = message;
        }
    }

    public enum AnomalySeverity {
        INFO, WARNING, CRITICAL
    }
}
