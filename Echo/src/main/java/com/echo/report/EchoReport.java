package com.echo.report;

import com.echo.aggregate.TimingData;
import com.echo.aggregate.TickHistogram;
import com.echo.aggregate.SpikeLog;
import com.echo.lua.LuaCallTracker;
import com.echo.measure.EchoProfiler;
import com.echo.measure.FreezeDetector;
import com.echo.measure.MemoryProfiler;
import com.echo.measure.ProfilingPoint;
import com.echo.measure.SubProfiler;
import com.echo.measure.TickPhaseProfiler;
import com.echo.validation.SelfValidation;
import com.echo.report.generator.CsvReportGenerator;
import com.echo.report.generator.HtmlReportGenerator;
import com.echo.report.generator.JsonReportGenerator;
import com.echo.report.generator.ReportGenerator;
import com.echo.report.generator.TextReportGenerator;

import java.io.*;
import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * Echo Report 생성기
 * 
 * JSON 및 텍스트 형식의 프로파일링 리포트 생성
 */
public class EchoReport {

    private static final String VERSION = "1.0.1";

    private final EchoProfiler profiler;
    private final int topN;

    private final Map<String, ReportGenerator> generators = new HashMap<>();

    // Phase 3: Metadata
    private String scenarioName = "default";
    private Set<String> scenarioTags = new HashSet<>();

    // Phase 1: Enhanced Metadata
    private final ReportMetadata reportMetadata = new ReportMetadata();

    // Phase 1: Quality Flag Aggregation
    private final java.util.EnumMap<com.echo.aggregate.DataQualityFlag, Integer> qualityFlagCounts = new java.util.EnumMap<>(
            com.echo.aggregate.DataQualityFlag.class);
    private final java.util.List<QualityEvent> recentQualityEvents = new java.util.ArrayList<>();
    private static final int MAX_QUALITY_EVENTS = 100;

    public EchoReport(EchoProfiler profiler) {
        this(profiler, 10);
    }

    public EchoReport(EchoProfiler profiler, int topN) {
        this.profiler = profiler;
        this.topN = topN;
        reportMetadata.collectFromPulse();

        // Initialize generators
        generators.put("json", new JsonReportGenerator());
        generators.put("text", new TextReportGenerator());
        generators.put("csv", new CsvReportGenerator());
        generators.put("html", new HtmlReportGenerator());
    }

    public void setScenarioName(String name) {
        this.scenarioName = name;
    }

    public void addScenarioTag(String tag) {
        this.scenarioTags.add(tag);
    }

    public void setScenarioTags(Set<String> tags) {
        this.scenarioTags = new HashSet<>(tags);
    }

    /**
     * JSON 리포트 생성
     */
    /**
     * 리포트 데이터 수집 (Map 형태)
     */
    public Map<String, Object> collectReportData() {
        Map<String, Object> report = new LinkedHashMap<>();
        Map<String, Object> echoReport = new LinkedHashMap<>();

        echoReport.put("version", VERSION);
        echoReport.put("generated_at", formatInstant(Instant.now()));
        echoReport.put("session_duration_seconds", profiler.getSessionDurationSeconds());

        echoReport.put("summary", generateSummary());
        echoReport.put("subsystems", generateSubsystems());
        echoReport.put("heavy_functions", generateHeavyFunctions());

        // Safely collect singleton-based data
        echoReport.put("tick_phase_breakdown", safeGetMap(() -> TickPhaseProfiler.getInstance().toMap()));
        echoReport.put("tick_histogram", generateHistogram());
        echoReport.put("spikes", generateSpikes());
        echoReport.put("freeze_history", generateFreezes());
        echoReport.put("memory", generateMemoryStats());
        echoReport.put("lua_profiling", generateLuaProfiling());
        echoReport.put("lua_gc", generateLuaGCStats());
        echoReport.put("fuse_deep_analysis", generateFuseDeepAnalysis());
        echoReport.put("validation_status", generateValidationStatus());
        echoReport.put("pulse_contract",
                safeGetMap(() -> com.echo.validation.PulseContractVerifier.getInstance().toMap()));
        echoReport.put("report_quality", generateReportQuality());
        echoReport.put("recommendations", generateRecommendations());
        echoReport.put("analysis", generateAnalysis());
        echoReport.put("metadata", generateMetadata());

        // Phase 2-5: Extended Analysis
        echoReport.put("extended_analysis",
                safeGetMap(() -> com.echo.analysis.ExtendedCorrelationAnalyzer.getInstance().analyze()));
        echoReport.put("memory_timeseries",
                safeGetMap(() -> com.echo.aggregate.MemoryTimeSeries.getInstance().toMap()));
        echoReport.put("bottleneck_detection",
                safeGetMap(() -> com.echo.analysis.BottleneckDetector.getInstance().toMap()));
        echoReport.put("network", safeGetMap(() -> com.echo.measure.NetworkMetrics.getInstance().toMap()));
        echoReport.put("render", safeGetMap(() -> com.echo.measure.RenderMetrics.getInstance().toMap()));
        echoReport.put("timeseries_summary",
                safeGetMap(() -> com.echo.aggregate.TimeSeriesStore.getInstance().toSummary()));

        report.put("echo_report", echoReport);
        return report;
    }

    /**
     * 특정 포맷의 리포트 생성
     */
    public String generate(String format) {
        ReportGenerator generator = generators.get(format.toLowerCase());
        if (generator == null) {
            throw new IllegalArgumentException("Unsupported report format: " + format);
        }
        return generator.generate(collectReportData());
    }

    /**
     * JSON 리포트 생성 (Delegated)
     */
    public String generateJson() {
        return generate("json");
    }

    /**
     * 콘솔 출력용 텍스트 리포트
     */
    /**
     * 콘솔 출력용 텍스트 리포트 (Delegated)
     */
    public String generateText() {
        return generate("text");
    }

    /**
     * 콘솔에 리포트 출력
     */
    public void printToConsole() {
        System.out.println(generateText());
    }

    /**
     * JSON 파일로 저장
     */
    public void saveToFile(String path) throws IOException {
        try (Writer writer = new FileWriter(path)) {
            writer.write(generateJson());
        }
        System.out.println("[Echo] Report saved to: " + path);
    }

    /**
     * 타임스탬프 파일명으로 자동 저장
     */
    public String saveWithTimestamp(String directory) throws IOException {
        // Check for empty data (Phase 2.3)
        if (profiler.getTickHistogram().getTotalSamples() == 0) {
            System.out.println("[Echo] Skipping report save: No data collected (0 ticks).");
            return null;
        }

        // Phase 5.2: Low Quality Report Handling
        int score = ReportQualityScorer.getInstance().calculateScore(profiler).score;
        int minQuality = com.echo.config.EchoConfig.getInstance().getMinQualityToSave();

        if (score < minQuality) {
            directory = directory + File.separator + "low_quality";
            System.out.println("[Echo] Report quality (" + score + ") below threshold (" + minQuality
                    + "). Saving to low_quality folder.");
        }

        String timestamp = DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss")
                .format(java.time.LocalDateTime.now());
        String filename = "echo_report_" + timestamp + ".json";
        String fullPath = directory + File.separator + filename;

        File dir = new File(directory);
        if (!dir.exists()) {
            dir.mkdirs();
        }

        saveToFile(fullPath);
        return fullPath;
    }

    /**
     * CSV 리포트 생성
     */
    private Map<String, Object> safeGetMap(java.util.function.Supplier<Map<String, Object>> supplier) {
        try {
            return supplier.get();
        } catch (Exception e) {
            Map<String, Object> err = new HashMap<>();
            err.put("error", "Data collection failed: " + e.getMessage());
            return err;
        }
    }

    /**
     * CSV 리포트 생성 (Delegated)
     */
    public String generateCsv() {
        return generate("csv");
    }

    /**
     * CSV 파일로 저장
     */
    public String saveCsv(String directory) throws IOException {
        String timestamp = DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss")
                .format(java.time.LocalDateTime.now());
        String filename = "echo_report_" + timestamp + ".csv";
        String fullPath = directory + File.separator + filename;

        File dir = new File(directory);
        if (!dir.exists()) {
            dir.mkdirs();
        }

        try (Writer writer = new FileWriter(fullPath)) {
            writer.write(generateCsv());
        }
        System.out.println("[Echo] CSV report saved to: " + fullPath);
        return fullPath;
    }

    /**
     * HTML 리포트 생성
     */
    /**
     * HTML 리포트 생성 (Interactive Dashboard)
     */
    /**
     * HTML 리포트 생성 (Delegated)
     */
    public String generateHtml() {
        return generate("html");
    }

    /**
     * HTML 파일로 저장
     */
    public String saveHtml(String directory) throws IOException {
        String timestamp = DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss")
                .format(java.time.LocalDateTime.now());
        String filename = "echo_report_" + timestamp + ".html";
        String fullPath = directory + File.separator + filename;

        File dir = new File(directory);
        if (!dir.exists()) {
            dir.mkdirs();
        }

        try (Writer writer = new FileWriter(fullPath)) {
            writer.write(generateHtml());
        }
        System.out.println("[Echo] HTML report saved to: " + fullPath);
        return fullPath;
    }

    // ============================================================
    // Private Methods
    // ============================================================

    private Map<String, Object> generateSummary() {
        Map<String, Object> summary = new LinkedHashMap<>();
        TimingData tickData = profiler.getTimingData(ProfilingPoint.TICK);

        if (tickData != null) {
            summary.put("total_ticks", tickData.getCallCount());
            summary.put("average_tick_ms", round(tickData.getAverageMicros() / 1000.0));
            summary.put("max_tick_spike_ms", round(tickData.getMaxMicros() / 1000.0));
            summary.put("min_tick_ms", round(tickData.getMinMicros() / 1000.0));
            summary.put("target_tick_ms", 16.67);

            // Performance score: 100 if avg <= 16.67ms, decreases by 5 per extra ms
            double avgMs = tickData.getAverageMicros() / 1000.0;
            double score = Math.max(0, 100 - Math.max(0, avgMs - 16.67) * 5);
            summary.put("performance_score", round(Math.min(100, score)));
        }

        return summary;
    }

    private List<Map<String, Object>> generateSubsystems() {
        List<Map<String, Object>> list = new ArrayList<>();

        for (ProfilingPoint point : ProfilingPoint.values()) {
            TimingData data = profiler.getTimingData(point);
            if (data != null && data.getCallCount() > 0) {
                Map<String, Object> item = new LinkedHashMap<>();
                item.put("name", point.name());
                item.put("display_name", point.getDisplayName());
                item.put("category", point.getCategory().name());

                Map<String, Object> stats = new LinkedHashMap<>();
                stats.put("call_count", data.getCallCount());
                stats.put("total_time_ms", round(data.getTotalMicros() / 1000.0));
                stats.put("average_time_ms", round(data.getAverageMicros() / 1000.0));
                stats.put("max_time_ms", round(data.getMaxMicros() / 1000.0));
                stats.put("min_time_ms", round(data.getMinMicros() / 1000.0));
                item.put("stats", stats);

                Map<String, Object> rolling = new LinkedHashMap<>();
                rolling.put("last_1s", createRollingStats(data.getStats1s()));
                rolling.put("last_5s", createRollingStats(data.getStats5s()));
                rolling.put("last_60s", createRollingStats(data.getStats60s()));
                item.put("rolling_stats", rolling);

                list.add(item);
            }
        }

        return list;
    }

    private Map<String, Object> createRollingStats(TimingData.RollingStats stats) {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("avg_ms", round(stats.getAverage() / 1000.0));
        map.put("max_ms", round(stats.getMax() / 1000.0));
        map.put("samples", stats.getSampleCount());
        return map;
    }

    private Map<String, Object> generateHeavyFunctions() {
        Map<String, Object> heavy = new LinkedHashMap<>();

        // SubProfiler 데이터 추가 (Echo 1.0)
        SubProfiler subProfiler = SubProfiler.getInstance();
        if (subProfiler.isEnabled()) {
            heavy.put("subtiming", subProfiler.toMap());
        }

        List<RankedFunction> byTotal = collectHeavyFunctions();

        List<Map<String, Object>> byTotalList = new ArrayList<>();
        int rank = 1;
        for (RankedFunction func : byTotal) {
            if (rank > topN)
                break;
            byTotalList.add(func.toMap(rank++));
        }
        heavy.put("by_total_time", byTotalList);

        // Sort by max spike
        List<RankedFunction> byMax = new ArrayList<>(byTotal);
        byMax.sort((a, b) -> Long.compare(b.maxMicros, a.maxMicros));

        List<Map<String, Object>> byMaxList = new ArrayList<>();
        rank = 1;
        for (RankedFunction func : byMax) {
            if (rank > topN)
                break;
            byMaxList.add(func.toMap(rank++));
        }
        heavy.put("by_max_spike", byMaxList);

        // Sort by call count
        List<RankedFunction> byCount = new ArrayList<>(byTotal);
        byCount.sort((a, b) -> Long.compare(b.callCount, a.callCount));

        List<Map<String, Object>> byCountList = new ArrayList<>();
        rank = 1;
        for (RankedFunction func : byCount) {
            if (rank > topN)
                break;
            byCountList.add(func.toMap(rank++));
        }
        heavy.put("by_call_frequency", byCountList);

        return heavy;
    }

    private List<RankedFunction> collectHeavyFunctions() {
        List<RankedFunction> functions = new ArrayList<>();

        // SubProfiler 데이터 수집 (Echo 1.0 - 우선순위 높음)
        SubProfiler subProfiler = SubProfiler.getInstance();
        if (subProfiler.isEnabled()) {
            for (SubProfiler.SubTimingData subData : subProfiler.getAllTimings()) {
                if (subData.getCallCount() > 0) {
                    functions.add(new RankedFunction(
                            subData.getLabel().getDisplayName(),
                            subData.getLabel().getCategory().getDisplayName(),
                            subData.getCallCount(),
                            subData.getTotalMicros(),
                            subData.getMaxMicros()));
                }
            }
        }

        // Legacy: TimingData 기반 라벨 통계 (기존 호환성)
        for (Map.Entry<ProfilingPoint, TimingData> entry : profiler.getTimingData().entrySet()) {
            ProfilingPoint point = entry.getKey();
            TimingData data = entry.getValue();

            for (TimingData.SubTimingData sub : data.getLabelStats().values()) {
                functions.add(new RankedFunction(
                        sub.getLabel(),
                        point.name(),
                        sub.getCallCount(),
                        sub.getTotalMicros(),
                        sub.getMaxMicros()));
            }
        }

        // Sort by total time
        functions.sort((a, b) -> Long.compare(b.totalMicros, a.totalMicros));
        return functions;
    }

    private Map<String, Object> generateHistogram() {
        TickHistogram histogram = profiler.getTickHistogram();
        return histogram.toMap();
    }

    private Map<String, Object> generateSpikes() {
        SpikeLog spikeLog = profiler.getSpikeLog();
        return spikeLog.toMap();
    }

    private Map<String, Object> generateFreezes() {
        Map<String, Object> map = new LinkedHashMap<>();
        List<FreezeDetector.FreezeSnapshot> freezes = FreezeDetector.getInstance().getRecentFreezes();

        map.put("total_freezes", freezes.size());

        List<Map<String, Object>> list = new ArrayList<>();
        for (FreezeDetector.FreezeSnapshot snapshot : freezes) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("timestamp", formatInstant(Instant.ofEpochMilli(snapshot.timestamp)));
            item.put("duration_ms", snapshot.freezeDurationMs);

            Map<String, Object> mem = new LinkedHashMap<>();
            mem.put("used_mb", snapshot.memory.used / 1024 / 1024);
            mem.put("total_mb", snapshot.memory.total / 1024 / 1024);
            item.put("memory", mem);

            // Stack Trace (Top 5 lines usually enough for quick check)
            List<String> stack = new ArrayList<>();
            int limit = 0;
            for (String line : snapshot.stackTrace) {
                if (limit++ > 10)
                    break;
                stack.add(line);
            }
            item.put("stack_trace", stack);

            list.add(item);
        }
        map.put("history", list);
        return map;
    }

    private List<String> generateRecommendations() {
        List<String> recommendations = new ArrayList<>();

        TimingData tickData = profiler.getTimingData(ProfilingPoint.TICK);
        TickHistogram histogram = profiler.getTickHistogram();
        SpikeLog spikeLog = profiler.getSpikeLog();

        if (tickData != null && tickData.getCallCount() > 0) {
            double avgMs = tickData.getAverageMicros() / 1000.0;
            double maxMs = tickData.getMaxMicros() / 1000.0;

            // 평균 틱 시간 권장사항
            if (avgMs > 33.33) {
                recommendations.add("CRITICAL: Average tick time (" + round(avgMs)
                        + "ms) exceeds 33ms. Game is running below 30 FPS.");
            } else if (avgMs > 16.67) {
                recommendations.add("WARNING: Average tick time (" + round(avgMs)
                        + "ms) exceeds 16.67ms target. Consider optimization.");
            }

            // 스파이크 권장사항
            if (spikeLog.getTotalSpikes() > 10) {
                recommendations.add("High spike count (" + spikeLog.getTotalSpikes() + "). Investigate: "
                        + spikeLog.getWorstSpikeLabel());
            }

            // 최대 스파이크 경고
            if (maxMs > 100) {
                recommendations.add("SEVERE: Max tick spike (" + round(maxMs) + "ms) exceeded 100ms.");
            }

            // P95 권장사항
            double p95 = histogram.getP95();
            if (p95 > 33.33) {
                recommendations.add("P95 tick time (" + round(p95) + "ms) is high. 5% of ticks are causing stutters.");
            }
        }

        // Hook Status Check
        SelfValidation.ValidationResult val = SelfValidation.getInstance().getLastResult();
        if (val != null && val.hookStatus != SelfValidation.HookStatus.OK) {
            recommendations.add("CRITICAL: Pulse hooks are MISSING or PARTIAL. Check Mixin logs.");
        }

        // Fallback Ticks Check
        if (com.echo.config.EchoConfig.getInstance().isUsedFallbackTicks()) {
            recommendations.add("WARNING: Fallback ticks were used. Timing data may be inaccurate.");
        }

        // Session Length Check
        long sessionMs = profiler.getSessionDurationMs();
        if (sessionMs < 10000) {
            recommendations.add("INFO: Short session (<10s). Data may be noisy.");
        }

        if (recommendations.isEmpty()) {
            recommendations.add("Performance looks good! No critical issues detected.");
        }

        return recommendations;
    }

    /**
     * 세션 종료 시 품질 요약 출력 (Phase 6.2)
     */
    public void printQualitySummary() {
        ReportQualityScorer.QualityResult result = ReportQualityScorer.getInstance().calculateScore(profiler);
        System.out.println("\n═══════════════════════════════════════════════════════");
        System.out.printf(" 🎯 ECHO SESSION QUALITY: %d/100%n", result.score);
        System.out.println("═══════════════════════════════════════════════════════");

        if (result.hasIssues()) {
            System.out.println(" Detected Issues:");
            for (Map<String, String> issue : result.issues) {
                String severity = issue.get("severity").toUpperCase();
                String desc = issue.get("description");
                System.out.printf("   [%s] %s%n", severity, desc);
            }
        } else {
            System.out.println(" ✅ No significant data quality issues.");
        }

        // Recommendations
        List<String> recs = generateRecommendations();
        if (!recs.isEmpty()) {
            System.out.println("\n Recommendations:");
            for (String rec : recs) {
                System.out.println("   - " + rec);
            }
        }
        System.out.println("═══════════════════════════════════════════════════════\n");
    }

    private Map<String, Object> generateMemoryStats() {
        return MemoryProfiler.toMap();
    }

    private Map<String, Object> generateLuaProfiling() {
        LuaCallTracker luaTracker = LuaCallTracker.getInstance();
        return luaTracker.toMap(topN);
    }

    private Map<String, Object> generateLuaGCStats() {
        return com.echo.lua.LuaGCProfiler.getInstance().toMap();
    }

    private Map<String, Object> generateFuseDeepAnalysis() {
        if (!com.echo.config.EchoConfig.getInstance().isDeepAnalysisEnabled()) {
            return null;
        }
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("pathfinding", com.echo.fuse.PathfindingProfiler.getInstance().toMap());
        map.put("zombie", com.echo.fuse.ZombieProfiler.getInstance().toMap());
        map.put("iso_grid", com.echo.fuse.IsoGridProfiler.getInstance().toMap());
        return map;
    }

    /**
     * Self-Validation 상태 생성 (Echo 0.9.0)
     */
    private Map<String, Object> generateValidationStatus() {
        return com.echo.validation.SelfValidation.getInstance().toMap();
    }

    /**
     * 리포트 품질 점수 생성 (Echo 0.9.0)
     */
    private Map<String, Object> generateReportQuality() {
        ReportQualityScorer.QualityResult result = ReportQualityScorer.getInstance().calculateScore(profiler);
        return result.toMap();
    }

    // Phase 3: Analysis
    private final com.echo.analysis.CorrelationAnalyzer correlationAnalyzer = new com.echo.analysis.CorrelationAnalyzer();

    public void onTick() {
        // Gather correlation data
        correlationAnalyzer.onTick();
    }

    private Map<String, Object> generateAnalysis() {
        // Integrate CorrelationAnalyzer
        return correlationAnalyzer.analyze();
    }

    private Map<String, Object> generateMetadata() {
        // Finalize sampling duration
        reportMetadata.finalizeSampling();

        Map<String, Object> meta = reportMetadata.toMap();

        // Add legacy fields for backward compatibility
        meta.put("echo_version", VERSION);
        meta.put("session_start_time", formatInstant(
                Instant.ofEpochMilli(profiler.getSessionStartTime())));

        // Phase 3: Scenario info
        meta.put("scenario_name", scenarioName);
        meta.put("scenario_tags", scenarioTags);

        // Phase 1: Quality flag summary
        meta.put("quality_flags", generateQualityFlagSummary());

        return meta;
    }

    /**
     * 품질 플래그 기록 (Phase 1)
     */
    public void recordQualityFlag(com.echo.aggregate.DataQualityFlag flag) {
        qualityFlagCounts.merge(flag, 1, Integer::sum);
        if (recentQualityEvents.size() < MAX_QUALITY_EVENTS) {
            recentQualityEvents.add(new QualityEvent(flag, System.currentTimeMillis()));
        }
    }

    /**
     * 품질 플래그 요약 생성
     */
    private Map<String, Object> generateQualityFlagSummary() {
        Map<String, Object> summary = new LinkedHashMap<>();

        // 플래그별 카운트
        Map<String, Integer> counts = new LinkedHashMap<>();
        for (var entry : qualityFlagCounts.entrySet()) {
            counts.put(entry.getKey().name(), entry.getValue());
        }
        summary.put("flag_counts", counts);

        // 총 플래그 수
        int totalFlags = qualityFlagCounts.values().stream().mapToInt(Integer::intValue).sum();
        summary.put("total_flags", totalFlags);

        // 데이터 품질 점수 (플래그가 많을수록 낮음)
        long totalTicks = profiler.getTickHistogram().getTotalSamples();
        double qualityScore = totalTicks > 0 ? Math.max(0, 1.0 - (double) totalFlags / totalTicks) : 1.0;
        summary.put("data_quality_score", round(qualityScore * 100));

        return summary;
    }

    /**
     * ReportMetadata 접근자
     */
    public ReportMetadata getReportMetadata() {
        return reportMetadata;
    }

    private String formatInstant(Instant instant) {
        return DateTimeFormatter.ISO_INSTANT.format(instant);
    }

    private double round(double value) {
        return Math.round(value * 100.0) / 100.0;
    }

    // truncate method removed - using StringUtils.truncate()

    // ============================================================
    // Helper Class
    // ============================================================

    private static class RankedFunction {
        final String label;
        final String parentPoint;
        final long callCount;
        final long totalMicros;
        final long maxMicros;

        RankedFunction(String label, String parentPoint, long callCount, long totalMicros, long maxMicros) {
            this.label = label;
            this.parentPoint = parentPoint;
            this.callCount = callCount;
            this.totalMicros = totalMicros;
            this.maxMicros = maxMicros;
        }

        Map<String, Object> toMap(int rank) {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("rank", rank);
            map.put("label", label);
            map.put("parent_point", parentPoint);
            map.put("call_count", callCount);
            map.put("total_time_ms", Math.round(totalMicros / 10.0) / 100.0);
            map.put("average_time_ms", callCount > 0
                    ? Math.round((double) totalMicros / callCount / 10.0) / 100.0
                    : 0);
            map.put("max_time_ms", Math.round(maxMicros / 10.0) / 100.0);
            return map;
        }
    }

    /**
     * 품질 이벤트 기록용 내부 클래스
     */
    @SuppressWarnings("unused") // Fields used for future detailed quality event history
    private static class QualityEvent {
        final com.echo.aggregate.DataQualityFlag flag;
        final long timestamp;

        QualityEvent(com.echo.aggregate.DataQualityFlag flag, long timestamp) {
            this.flag = flag;
            this.timestamp = timestamp;
        }

        public com.echo.aggregate.DataQualityFlag getFlag() {
            return flag;
        }

        public long getTimestamp() {
            return timestamp;
        }
    }
}
