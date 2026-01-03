package com.echo.analysis;

import com.echo.aggregate.TimingData;
import com.echo.measure.*;
import com.echo.subsystem.*;

import java.util.*;

/**
 * 자동 병목 식별기.
 * 
 * 성능 병목을 자동으로 식별하고 관측 요약을 제공합니다.
 * Echo는 "어디(Where)가 아픈지"만 분류하며, "누가(Who) 처리할지"는 판단하지 않습니다.
 * 
 * @since 1.0.1
 * @since 2.0 - Pulse 정화로 인해 Echo 내부 클래스로 이동
 * @since 3.0 - 헌법 정화: 제안/추천 API 제거, 관측 전용
 * @since 3.1 - Domain 기반 분류 채택: 모듈명(FUSE/NERVE) → 도메인명(ENGINE/RENDER)
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
                BottleneckDomain domain = classifyDomain(point);
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
                        domain,
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
                    BottleneckDomain.ENGINE,
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
                        BottleneckDomain.ENGINE,
                        (int) (ratio * 100)));
            }
        }
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
            bMap.put("domain", b.domain.name());
            bMap.put("priority", b.priority);
            bottleneckList.add(bMap);
        }
        map.put("top_bottlenecks", bottleneckList);

        // 이상 탐지 (관측 데이터만)
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

    /**
     * 도메인 분류 - "어디가 아픈지"만 분류.
     * Echo는 "누가 처리할지"를 지정하지 않음.
     */
    private BottleneckDomain classifyDomain(ProfilingPoint point) {
        return switch (point) {
            case ZOMBIE_AI, SIMULATION, PHYSICS -> BottleneckDomain.ENGINE;
            case RENDER, RENDER_WORLD, RENDER_UI -> BottleneckDomain.RENDER;
            case NETWORK -> BottleneckDomain.IO;
            case CHUNK_IO -> BottleneckDomain.WORLD;
            default -> BottleneckDomain.ENGINE;
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

    // --- 내부 클래스 ---

    public static class Bottleneck {
        public final String name;
        public final String displayName;
        public final double avgMs;
        public final double ratio;
        public final BottleneckType type;
        public final BottleneckDomain domain;
        public final int priority;

        public Bottleneck(String name, String displayName, double avgMs, double ratio,
                BottleneckType type, BottleneckDomain domain, int priority) {
            this.name = name;
            this.displayName = displayName;
            this.avgMs = avgMs;
            this.ratio = ratio;
            this.type = type;
            this.domain = domain;
            this.priority = priority;
        }
    }

    public enum BottleneckType {
        CPU_BOUND, GPU_BOUND, IO_BOUND, MEMORY_BOUND
    }

    /**
     * 병목 도메인 - "어디"가 아픈지 분류.
     * 모듈명(WHO)이 아닌 영역명(WHERE)만 사용.
     */
    public enum BottleneckDomain {
        ENGINE, // Java 레벨: 좀비AI, 물리, 시뮬레이션
        SCRIPT, // Lua 레벨: 이벤트, UI, 모드 스크립트
        RENDER, // 렌더링: 텍스처, 조명, 쉐이더
        IO, // 파일/네트워크
        MEMORY, // GC, 힙, 할당
        WORLD // 청크, 스트리밍, 월드 데이터
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
