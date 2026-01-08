package com.echo.report;

import com.echo.aggregate.DataQualityFlag;
import com.echo.aggregate.TimingData;
import com.echo.aggregate.MemoryTimeSeries;
import com.echo.aggregate.TimeSeriesStore;
import com.echo.analysis.CorrelationAnalyzer;
import com.echo.analysis.ExtendedCorrelationAnalyzer;
import com.echo.analysis.BottleneckDetector;
import com.echo.config.EchoConfig;
import com.echo.subsystem.IsoGridProfiler;
import com.echo.subsystem.PathfindingProfiler;
import com.echo.subsystem.ZombieProfiler;
import com.echo.lua.LuaCallTracker;
import com.echo.lua.LuaGCProfiler;
import com.echo.measure.EchoProfiler;
import com.echo.history.MetricCollector;
import com.echo.measure.FreezeDetector;
import com.echo.measure.MemoryProfiler;
import com.echo.measure.NetworkMetrics;
import com.echo.measure.ProfilingPoint;
import com.echo.measure.RenderMetrics;
import com.echo.measure.SubProfiler;
import com.echo.measure.TickPhaseProfiler;
import com.echo.validation.PulseContractVerifier;
import com.echo.validation.SelfValidation;

import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * Report Data Collector.
 * Separated from EchoReport to handle data aggregation and collection.
 */
public class ReportDataCollector {

    private final EchoProfiler profiler;
    private final int topN;

    // Phase 3: Metadata
    private String scenarioName = "default";
    private Set<String> scenarioTags = new HashSet<>();

    // Phase 1: Enhanced Metadata
    private final ReportMetadata reportMetadata = new ReportMetadata();

    // Phase 1: Quality Flag Aggregation
    // EnumMap requires the key type class
    private final EnumMap<DataQualityFlag, Integer> qualityFlagCounts = new EnumMap<>(DataQualityFlag.class);

    // Phase 3: Analysis

    public ReportDataCollector(EchoProfiler profiler, int topN) {
        this.profiler = profiler;
        this.topN = topN;
        reportMetadata.collectFromPulse();
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

    public void onTick() {
        // Handled by PulseEventAdapter -> MetricCollector
    }

    public void recordQualityFlag(DataQualityFlag flag) {
        qualityFlagCounts.merge(flag, 1, Integer::sum);
    }

    public ReportMetadata getReportMetadata() {
        return reportMetadata;
    }

    public EchoProfiler getProfiler() {
        return profiler;
    }

    /**
     * 리포트 데이터 수집 (Map 형태)
     */
    public Map<String, Object> collect() {
        Map<String, Object> report = new LinkedHashMap<>();
        Map<String, Object> echoReport = new LinkedHashMap<>();

        echoReport.put("version", "1.0.1");
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
                safeGetMap(() -> PulseContractVerifier.getInstance().toMap()));
        echoReport.put("report_quality", generateReportQuality());
        echoReport.put("analysis", generateAnalysis());
        echoReport.put("metadata", generateMetadata());

        // Phase 2-5: Extended Analysis
        echoReport.put("extended_analysis",
                safeGetMap(() -> ExtendedCorrelationAnalyzer.getInstance().analyze()));
        echoReport.put("memory_timeseries",
                safeGetMap(() -> MemoryTimeSeries.getInstance().toMap()));
        echoReport.put("bottleneck_detection",
                safeGetMap(() -> BottleneckDetector.getInstance().toMap()));
        echoReport.put("network", safeGetMap(() -> NetworkMetrics.getInstance().toMap()));
        echoReport.put("render", safeGetMap(() -> RenderMetrics.getInstance().toMap()));
        echoReport.put("timeseries_summary",
                safeGetMap(() -> TimeSeriesStore.getInstance().toSummary()));

        report.put("echo_report", echoReport);
        return report;
    }

    private Map<String, Object> safeGetMap(java.util.function.Supplier<Map<String, Object>> supplier) {
        try {
            return supplier.get();
        } catch (Exception e) {
            Map<String, Object> err = new HashMap<>();
            err.put("error", "Data collection failed: " + e.getMessage());
            return err;
        }
    }

    private Map<String, Object> generateSummary() {
        Map<String, Object> summary = new LinkedHashMap<>();
        TimingData tickData = profiler.getTimingData(ProfilingPoint.TICK);

        if (tickData != null) {
            summary.put("total_ticks", tickData.getCallCount());
            summary.put("average_tick_ms", round(tickData.getAverageMicros() / 1000.0));
            summary.put("max_tick_spike_ms", round(tickData.getMaxMicros() / 1000.0));
            summary.put("min_tick_ms", round(tickData.getMinMicros() / 1000.0));
            summary.put("target_tick_ms", 16.67);

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

        functions.sort((a, b) -> Long.compare(b.totalMicros, a.totalMicros));
        return functions;
    }

    private Map<String, Object> generateHistogram() {
        return profiler.getTickHistogram().toMap();
    }

    private Map<String, Object> generateSpikes() {
        return profiler.getSpikeLog().toMap();
    }

    private Map<String, Object> generateFreezes() {
        Map<String, Object> map = new LinkedHashMap<>();
        // v1.1: 메인 루프 스택만 포함된 freeze 사용 (오염 제거)
        List<FreezeDetector.FreezeSnapshot> freezes = FreezeDetector.getInstance().getMainLoopFreezes();
        List<FreezeDetector.FreezeSnapshot> allFreezes = FreezeDetector.getInstance().getRecentFreezes();
        map.put("total_freezes", freezes.size());
        map.put("filtered_count", allFreezes.size() - freezes.size()); // v1.1: 필터링된 수

        List<Map<String, Object>> list = new ArrayList<>();
        for (FreezeDetector.FreezeSnapshot snapshot : freezes) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("timestamp", formatInstant(Instant.ofEpochMilli(snapshot.timestamp)));
            item.put("duration_ms", snapshot.freezeDurationMs);

            Map<String, Object> mem = new LinkedHashMap<>();
            mem.put("used_mb", snapshot.memory.used / 1024 / 1024);
            mem.put("total_mb", snapshot.memory.total / 1024 / 1024);
            item.put("memory", mem);

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

    private Map<String, Object> generateMemoryStats() {
        return MemoryProfiler.toMap();
    }

    private Map<String, Object> generateLuaProfiling() {
        return LuaCallTracker.getInstance().toMap(topN);
    }

    private Map<String, Object> generateLuaGCStats() {
        return LuaGCProfiler.getInstance().toMap();
    }

    private Map<String, Object> generateFuseDeepAnalysis() {
        Map<String, Object> result = new LinkedHashMap<>();

        // === Step 1: SPI 가용성 확인 ===
        com.pulse.api.spi.IProviderRegistry registry = null;
        try {
            registry = com.pulse.api.Pulse.getProviderRegistry();
        } catch (Exception e) {
            result.put("spi_available", false);
            result.put("error_code", "REGISTRY_UNAVAILABLE");
            result.put("error_message", e.getMessage());
            result.put("providers", createEmptyFuseEntry("REGISTRY_UNAVAILABLE", e.getMessage()));
            return result;
        }

        result.put("spi_available", true);

        // === Step 2: Provider 수집 (항상 기록 - 증명 파이프는 옵션화 금지) ===
        Map<String, Object> providers = new LinkedHashMap<>();

        // "fuse" 키는 항상 존재 (0 분해를 위해)
        providers.put("fuse", collectStabilizerSnapshot(registry, "fuse"));

        result.put("providers", providers);

        // === Step 3: Echo 내부 프로파일러 (이건 옵션) ===
        if (EchoConfig.getInstance().isDeepAnalysisEnabled()) {
            result.put("echo_profilers", generateEchoInternalProfilers());
        }

        return result;
    }

    /**
     * 개별 Stabilizer 스냅샷 수집 (no-throw).
     * 
     * Bundle B 핵심: "0 분해"를 위해 present/active/snapshot_ok 필드 보장.
     * v4: 불변 Map 대비 복사본 사용, 필수 키 정규화
     */
    private Map<String, Object> collectStabilizerSnapshot(
            com.pulse.api.spi.IProviderRegistry registry, String stabilizerId) {
        Map<String, Object> snapshot = new LinkedHashMap<>();

        // === Step 1: Provider 목록 조회 ===
        java.util.List<com.pulse.api.spi.IStabilizerSnapshotProvider> matchingProviders;
        try {
            matchingProviders = registry.getAllProviders().stream()
                    .filter(p -> p instanceof com.pulse.api.spi.IStabilizerSnapshotProvider)
                    .filter(p -> stabilizerId.equals(p.getId()))
                    .map(p -> (com.pulse.api.spi.IStabilizerSnapshotProvider) p)
                    .collect(java.util.stream.Collectors.toList());
        } catch (Exception e) {
            return createErrorSnapshot(false, "REGISTRY_QUERY_FAILED", e.getMessage());
        }

        // === Step 2: 중복 ID 감지 ===
        if (matchingProviders.size() > 1) {
            snapshot.put("present", true);
            return addErrorFields(snapshot, "DUPLICATE_PROVIDER_ID",
                    "Found " + matchingProviders.size() + " providers with id: " + stabilizerId);
        }

        // === Step 3: Provider 미존재 ===
        if (matchingProviders.isEmpty()) {
            return createErrorSnapshot(false, "PROVIDER_MISSING",
                    "No provider registered with id: " + stabilizerId);
        }

        // === Step 4: Provider 존재 - 스냅샷 캡처 ===
        com.pulse.api.spi.IStabilizerSnapshotProvider provider = matchingProviders.get(0);

        // present=true (Echo가 결정)
        snapshot.put("present", true);

        // Provider 메타 정보
        snapshot.put("provider_name", provider.getName());
        snapshot.put("provider_version", provider.getVersion());

        try {
            snapshot.put("provider_status", provider.getProviderStatus().name());
        } catch (Exception e) {
            snapshot.put("provider_status", "UNKNOWN");
        }

        // 스냅샷 캡처
        try {
            Map<String, Object> captured = provider.captureSnapshot();
            if (captured != null) {
                // v4: 불변 Map 대비 - 복사본으로 작업 (captured 직접 수정 금지)
                Map<String, Object> filtered = new LinkedHashMap<>(captured);
                filtered.remove("present"); // Echo가 결정하므로 제거
                snapshot.putAll(filtered);
            } else {
                return addErrorFields(snapshot, "SNAPSHOT_NULL", "Provider returned null snapshot");
            }
        } catch (Exception e) {
            return addErrorFields(snapshot, "SNAPSHOT_THROWN", e.getMessage());
        }

        // v4: 필수 키 정규화 (Provider 누락 대비)
        normalizeRequiredKeys(snapshot);

        return snapshot;
    }

    /**
     * v4: 필수 키 정규화 - Provider가 누락해도 리포트 일관성 보장.
     */
    private void normalizeRequiredKeys(Map<String, Object> snapshot) {
        if (!snapshot.containsKey("active")) {
            snapshot.put("active", false);
        }
        if (!snapshot.containsKey("snapshot_ok")) {
            snapshot.put("snapshot_ok", false);
            if (!snapshot.containsKey("error_code") || "".equals(snapshot.get("error_code"))) {
                snapshot.put("error_code", "SNAPSHOT_MALFORMED");
            }
        }
        if (!snapshot.containsKey("error_code")) {
            snapshot.put("error_code", "");
        }
        if (!snapshot.containsKey("total_interventions")) {
            snapshot.put("total_interventions", 0L);
        }
        if (!snapshot.containsKey("reason_counts")) {
            snapshot.put("reason_counts", Collections.emptyMap());
        }
    }

    /**
     * 에러 스냅샷 생성 헬퍼.
     */
    private Map<String, Object> createErrorSnapshot(boolean present, String errorCode, String errorMessage) {
        Map<String, Object> snapshot = new LinkedHashMap<>();
        snapshot.put("present", present);
        snapshot.put("active", false);
        snapshot.put("snapshot_ok", false);
        snapshot.put("error_code", errorCode);
        snapshot.put("error_message", errorMessage != null ? errorMessage : "");
        snapshot.put("total_interventions", 0L);
        snapshot.put("reason_counts", Collections.emptyMap());
        return snapshot;
    }

    /**
     * 기존 스냅샷에 에러 필드 추가 헬퍼.
     */
    private Map<String, Object> addErrorFields(Map<String, Object> snapshot, String errorCode, String errorMessage) {
        snapshot.put("active", false);
        snapshot.put("snapshot_ok", false);
        snapshot.put("error_code", errorCode);
        snapshot.put("error_message", errorMessage != null ? errorMessage : "");
        snapshot.put("total_interventions", 0L);
        snapshot.put("reason_counts", Collections.emptyMap());
        return snapshot;
    }

    /**
     * 빈 fuse 엔트리 생성 (registry 자체 실패 시).
     */
    private Map<String, Object> createEmptyFuseEntry(String errorCode, String errorMessage) {
        Map<String, Object> providers = new LinkedHashMap<>();
        Map<String, Object> fuse = new LinkedHashMap<>();
        fuse.put("present", false);
        fuse.put("active", false);
        fuse.put("snapshot_ok", false);
        fuse.put("error_code", errorCode);
        fuse.put("error_message", errorMessage != null ? errorMessage : "");
        fuse.put("total_interventions", 0L);
        fuse.put("reason_counts", Collections.emptyMap());
        providers.put("fuse", fuse);
        return providers;
    }

    /**
     * Echo 내부 프로파일러 데이터 (기존 로직 보존).
     */
    private Map<String, Object> generateEchoInternalProfilers() {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("pathfinding", PathfindingProfiler.getInstance().toMap());
        map.put("zombie", ZombieProfiler.getInstance().toMap());
        map.put("iso_grid", IsoGridProfiler.getInstance().toMap());
        return map;
    }

    private Map<String, Object> generateValidationStatus() {
        return SelfValidation.getInstance().toMap();
    }

    private Map<String, Object> generateReportQuality() {
        ReportQualityScorer.QualityResult result = ReportQualityScorer.getInstance().calculateScore(profiler);
        return result.toMap();
    }

    private Map<String, Object> generateAnalysis() {
        Map<String, Object> map = new LinkedHashMap<>();
        MetricCollector collector = profiler.getMetricCollector();
        if (collector != null) {
            double corr = collector.getCorrelation("zombie_count", "tick_time");
            map.put("zombie_tick_correlation", corr);
            map.put("interpretation", CorrelationAnalyzer.interpret(corr));
        }
        return map;
    }

    private Map<String, Object> generateMetadata() {
        reportMetadata.finalizeSampling();
        Map<String, Object> meta = reportMetadata.toMap();
        meta.put("echo_version", "1.0.1");
        meta.put("session_start_time", formatInstant(Instant.ofEpochMilli(profiler.getSessionStartTime())));
        meta.put("scenario_name", scenarioName);
        meta.put("scenario_tags", scenarioTags);
        meta.put("quality_flags", generateQualityFlagSummary());
        return meta;
    }

    private Map<String, Object> generateQualityFlagSummary() {
        Map<String, Object> summary = new LinkedHashMap<>();
        Map<String, Integer> counts = new LinkedHashMap<>();
        for (var entry : qualityFlagCounts.entrySet()) {
            counts.put(entry.getKey().name(), entry.getValue());
        }
        summary.put("flag_counts", counts);
        int totalFlags = qualityFlagCounts.values().stream().mapToInt(Integer::intValue).sum();
        summary.put("total_flags", totalFlags);
        long totalTicks = profiler.getTickHistogram().getTotalSamples();
        double qualityScore = totalTicks > 0 ? Math.max(0, 1.0 - (double) totalFlags / totalTicks) : 1.0;
        summary.put("data_quality_score", round(qualityScore * 100));
        return summary;
    }

    private String formatInstant(Instant instant) {
        return DateTimeFormatter.ISO_INSTANT.format(instant);
    }

    private double round(double value) {
        return Math.round(value * 100.0) / 100.0;
    }

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
            map.put("average_time_ms", callCount > 0 ? Math.round((double) totalMicros / callCount / 10.0) / 100.0 : 0);
            map.put("max_time_ms", Math.round(maxMicros / 10.0) / 100.0);
            return map;
        }
    }

}
