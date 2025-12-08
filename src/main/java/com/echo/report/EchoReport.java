package com.echo.report;

import com.echo.aggregate.TimingData;
import com.echo.aggregate.TickHistogram;
import com.echo.aggregate.SpikeLog;
import com.echo.lua.LuaCallTracker;
import com.echo.measure.EchoProfiler;
import com.echo.measure.MemoryProfiler;
import com.echo.measure.ProfilingPoint;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.*;
import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.util.*;

import com.echo.util.StringUtils;

/**
 * Echo Report 생성기
 * 
 * JSON 및 텍스트 형식의 프로파일링 리포트 생성
 */
public class EchoReport {

    // Use ISO_INSTANT format consistently for all dates
    private static final Gson GSON = new GsonBuilder()
            .setPrettyPrinting()
            .create();

    private static final String VERSION = "0.2.0";

    private final EchoProfiler profiler;
    private final int topN;

    public EchoReport(EchoProfiler profiler) {
        this(profiler, 10);
    }

    public EchoReport(EchoProfiler profiler, int topN) {
        this.profiler = profiler;
        this.topN = topN;
    }

    /**
     * JSON 리포트 생성
     */
    public String generateJson() {
        Map<String, Object> report = new LinkedHashMap<>();
        Map<String, Object> echoReport = new LinkedHashMap<>();

        echoReport.put("version", VERSION);
        echoReport.put("generated_at", formatInstant(Instant.now()));
        echoReport.put("session_duration_seconds", profiler.getSessionDurationSeconds());

        echoReport.put("summary", generateSummary());
        echoReport.put("subsystems", generateSubsystems());
        echoReport.put("heavy_functions", generateHeavyFunctions());
        echoReport.put("tick_histogram", generateHistogram());
        echoReport.put("spikes", generateSpikes());
        echoReport.put("memory", generateMemoryStats());
        echoReport.put("lua_profiling", generateLuaProfiling());
        echoReport.put("recommendations", generateRecommendations());
        echoReport.put("metadata", generateMetadata());

        report.put("echo_report", echoReport);
        return GSON.toJson(report);
    }

    /**
     * 콘솔 출력용 텍스트 리포트
     */
    public String generateText() {
        StringBuilder sb = new StringBuilder();
        sb.append("\n═══════════════════════════════════════════════════════\n");
        sb.append("               ECHO PROFILER REPORT\n");
        sb.append("═══════════════════════════════════════════════════════\n\n");

        // Summary
        TimingData tickData = profiler.getTimingData(ProfilingPoint.TICK);
        if (tickData != null && tickData.getCallCount() > 0) {
            sb.append("📊 TICK SUMMARY\n");
            sb.append("───────────────────────────────────────────────────────\n");
            sb.append(String.format("  Total Ticks:    %,d\n", tickData.getCallCount()));
            sb.append(String.format("  Average:        %.2f ms\n", tickData.getAverageMicros() / 1000.0));
            sb.append(String.format("  Max Spike:      %.2f ms\n", tickData.getMaxMicros() / 1000.0));
            sb.append(String.format("  Min:            %.2f ms\n", tickData.getMinMicros() / 1000.0));
            sb.append(String.format("  Session:        %d seconds\n", profiler.getSessionDurationSeconds()));
            sb.append("\n");
        }

        // Subsystems
        sb.append("📈 SUBSYSTEM BREAKDOWN\n");
        sb.append("───────────────────────────────────────────────────────\n");

        List<Map.Entry<ProfilingPoint, TimingData>> sorted = profiler.getTimingData().entrySet().stream()
                .filter(e -> e.getValue().getCallCount() > 0)
                .filter(e -> e.getKey().getCategory() == ProfilingPoint.Category.SUBSYSTEM)
                .sorted((a, b) -> Long.compare(b.getValue().getTotalMicros(), a.getValue().getTotalMicros()))
                .toList();

        for (Map.Entry<ProfilingPoint, TimingData> entry : sorted) {
            ProfilingPoint point = entry.getKey();
            TimingData data = entry.getValue();
            sb.append(String.format("  %-15s │ avg: %6.2f ms │ max: %6.2f ms │ calls: %,d\n",
                    point.getDisplayName(),
                    data.getAverageMicros() / 1000.0,
                    data.getMaxMicros() / 1000.0,
                    data.getCallCount()));
        }

        // Rolling Stats (last 5s)
        sb.append("\n📉 ROLLING STATS (Last 5s)\n");
        sb.append("───────────────────────────────────────────────────────\n");

        if (tickData != null) {
            TimingData.RollingStats stats5s = tickData.getStats5s();
            sb.append(String.format("  Tick Avg (5s):  %.2f ms\n", stats5s.getAverage() / 1000.0));
            sb.append(String.format("  Tick Max (5s):  %.2f ms\n", stats5s.getMax() / 1000.0));
            sb.append(String.format("  Samples:        %d\n", stats5s.getSampleCount()));
        }

        // Heavy Functions
        sb.append("\n🔥 HEAVY FUNCTIONS (Top " + topN + ")\n");
        sb.append("───────────────────────────────────────────────────────\n");

        List<RankedFunction> heavyFunctions = collectHeavyFunctions();
        if (heavyFunctions.isEmpty()) {
            sb.append("  (No labeled function data collected)\n");
        } else {
            int rank = 1;
            for (RankedFunction func : heavyFunctions) {
                if (rank > topN)
                    break;
                sb.append(String.format("  #%d %-30s │ total: %6.2f ms │ max: %6.2f ms │ calls: %,d\n",
                        rank++,
                        StringUtils.truncate(func.label, 30),
                        func.totalMicros / 1000.0,
                        func.maxMicros / 1000.0,
                        func.callCount));
            }
        }

        sb.append("\n═══════════════════════════════════════════════════════\n");
        return sb.toString();
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
    public String generateCsv() {
        StringBuilder sb = new StringBuilder();

        // Header
        sb.append("Point,Category,CallCount,TotalMs,AvgMs,MaxMs,MinMs\n");

        // Data rows
        for (ProfilingPoint point : ProfilingPoint.values()) {
            TimingData data = profiler.getTimingData(point);
            if (data != null && data.getCallCount() > 0) {
                sb.append(String.format("%s,%s,%d,%.2f,%.2f,%.2f,%.2f\n",
                        point.name(),
                        point.getCategory().name(),
                        data.getCallCount(),
                        data.getTotalMicros() / 1000.0,
                        data.getAverageMicros() / 1000.0,
                        data.getMaxMicros() / 1000.0,
                        data.getMinMicros() / 1000.0));
            }
        }

        return sb.toString();
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
    public String generateHtml() {
        TimingData tickData = profiler.getTimingData(ProfilingPoint.TICK);
        TickHistogram histogram = profiler.getTickHistogram();

        StringBuilder sb = new StringBuilder();
        sb.append("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n");
        sb.append("  <meta charset=\"UTF-8\">\n");
        sb.append("  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n");
        sb.append("  <title>Echo Profiler Report</title>\n");
        sb.append("  <style>\n");
        sb.append("    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; ");
        sb.append("           background: #1a1a2e; color: #eee; padding: 20px; }\n");
        sb.append("    .container { max-width: 1200px; margin: 0 auto; }\n");
        sb.append("    h1 { color: #4ecdc4; border-bottom: 2px solid #4ecdc4; padding-bottom: 10px; }\n");
        sb.append("    h2 { color: #ff6b6b; margin-top: 30px; }\n");
        sb.append("    .card { background: #16213e; border-radius: 8px; padding: 20px; margin: 15px 0; }\n");
        sb.append("    table { width: 100%; border-collapse: collapse; margin-top: 10px; }\n");
        sb.append("    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }\n");
        sb.append("    th { background: #0f3460; color: #4ecdc4; }\n");
        sb.append("    tr:hover { background: #1a1a40; }\n");
        sb.append("    .metric { font-size: 2em; color: #4ecdc4; font-weight: bold; }\n");
        sb.append("    .label { color: #888; font-size: 0.9em; }\n");
        sb.append(
                "    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }\n");
        sb.append(
                "    .bar { height: 20px; background: linear-gradient(90deg, #4ecdc4, #44a08d); border-radius: 4px; }\n");
        sb.append("  </style>\n</head>\n<body>\n<div class=\"container\">\n");

        // Header
        sb.append("  <h1>🔊 Echo Profiler Report</h1>\n");
        sb.append("  <p>Generated: ").append(java.time.LocalDateTime.now()).append("</p>\n");

        // Summary Cards
        sb.append("  <h2>📊 Summary</h2>\n");
        sb.append("  <div class=\"grid\">\n");

        if (tickData != null && tickData.getCallCount() > 0) {
            sb.append("    <div class=\"card\"><div class=\"metric\">")
                    .append(String.format("%,d", tickData.getCallCount()))
                    .append("</div><div class=\"label\">Total Ticks</div></div>\n");
            sb.append("    <div class=\"card\"><div class=\"metric\">")
                    .append(String.format("%.2f ms", tickData.getAverageMicros() / 1000.0))
                    .append("</div><div class=\"label\">Avg Tick Time</div></div>\n");
            sb.append("    <div class=\"card\"><div class=\"metric\">")
                    .append(String.format("%.2f ms", tickData.getMaxMicros() / 1000.0))
                    .append("</div><div class=\"label\">Max Spike</div></div>\n");
            sb.append("    <div class=\"card\"><div class=\"metric\">")
                    .append(String.format("%.1f ms", histogram.getP95()))
                    .append("</div><div class=\"label\">P95</div></div>\n");
        }
        sb.append("  </div>\n");

        // Subsystems Table
        sb.append("  <h2>📈 Subsystems</h2>\n");
        sb.append("  <div class=\"card\">\n");
        sb.append("    <table>\n");
        sb.append("      <tr><th>Subsystem</th><th>Calls</th><th>Total</th><th>Avg</th><th>Max</th></tr>\n");

        for (ProfilingPoint point : ProfilingPoint.values()) {
            TimingData data = profiler.getTimingData(point);
            if (data != null && data.getCallCount() > 0 && point.getCategory() == ProfilingPoint.Category.SUBSYSTEM) {
                sb.append("      <tr>");
                sb.append("<td>").append(point.getDisplayName()).append("</td>");
                sb.append("<td>").append(String.format("%,d", data.getCallCount())).append("</td>");
                sb.append("<td>").append(String.format("%.2f ms", data.getTotalMicros() / 1000.0)).append("</td>");
                sb.append("<td>").append(String.format("%.2f ms", data.getAverageMicros() / 1000.0)).append("</td>");
                sb.append("<td>").append(String.format("%.2f ms", data.getMaxMicros() / 1000.0)).append("</td>");
                sb.append("</tr>\n");
            }
        }
        sb.append("    </table>\n  </div>\n");

        // Histogram
        sb.append("  <h2>📉 Tick Distribution</h2>\n");
        sb.append("  <div class=\"card\">\n");
        long[] counts = histogram.getCounts();
        double[] buckets = histogram.getBuckets();
        long maxCount = java.util.Arrays.stream(counts).max().orElse(1);

        for (int i = 0; i < buckets.length; i++) {
            String label = i == buckets.length - 1
                    ? String.format("≥%.1fms", buckets[i])
                    : String.format("%.1f-%.1fms", buckets[i], buckets[i + 1]);
            int barWidth = (int) ((counts[i] * 100) / Math.max(maxCount, 1));

            sb.append("    <div style=\"margin: 8px 0;\">");
            sb.append("<span style=\"display:inline-block;width:100px;\">").append(label).append("</span>");
            sb.append("<div class=\"bar\" style=\"width:").append(barWidth).append("%;display:inline-block;\"></div>");
            sb.append(" <span>").append(counts[i]).append("</span>");
            sb.append("</div>\n");
        }
        sb.append("  </div>\n");

        sb.append("</div>\n</body>\n</html>");
        return sb.toString();
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

        if (recommendations.isEmpty()) {
            recommendations.add("Performance looks good! No critical issues detected.");
        }

        return recommendations;
    }

    private Map<String, Object> generateMemoryStats() {
        return MemoryProfiler.toMap();
    }

    private Map<String, Object> generateLuaProfiling() {
        LuaCallTracker luaTracker = LuaCallTracker.getInstance();
        return luaTracker.toMap(topN);
    }

    private Map<String, Object> generateMetadata() {
        Map<String, Object> meta = new LinkedHashMap<>();
        meta.put("echo_version", VERSION);
        meta.put("java_version", System.getProperty("java.version"));
        meta.put("os", System.getProperty("os.name"));
        meta.put("session_start_time", formatInstant(
                Instant.ofEpochMilli(profiler.getSessionStartTime())));
        return meta;
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
}
