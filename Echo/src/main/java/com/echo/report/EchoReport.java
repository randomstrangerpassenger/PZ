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

    private static final String VERSION = "1.0.1";

    private final EchoProfiler profiler;
    private final int topN;

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
    public String generateJson() {
        Map<String, Object> report = new LinkedHashMap<>();
        Map<String, Object> echoReport = new LinkedHashMap<>();

        echoReport.put("version", VERSION);
        echoReport.put("generated_at", formatInstant(Instant.now()));
        echoReport.put("session_duration_seconds", profiler.getSessionDurationSeconds());

        echoReport.put("summary", generateSummary());
        echoReport.put("subsystems", generateSubsystems());
        echoReport.put("heavy_functions", generateHeavyFunctions());
        echoReport.put("tick_phase_breakdown", TickPhaseProfiler.getInstance().toMap());
        echoReport.put("tick_histogram", generateHistogram());
        echoReport.put("spikes", generateSpikes());
        echoReport.put("freeze_history", generateFreezes());
        echoReport.put("memory", generateMemoryStats());
        echoReport.put("lua_profiling", generateLuaProfiling());
        echoReport.put("lua_gc", generateLuaGCStats());
        echoReport.put("fuse_deep_analysis", generateFuseDeepAnalysis());
        echoReport.put("validation_status", generateValidationStatus());
        echoReport.put("pulse_contract", com.echo.validation.PulseContractVerifier.getInstance().toMap());
        echoReport.put("report_quality", generateReportQuality());
        echoReport.put("recommendations", generateRecommendations());
        echoReport.put("analysis", generateAnalysis());
        echoReport.put("metadata", generateMetadata());

        // Phase 2-5: Extended Analysis
        echoReport.put("extended_analysis", com.echo.analysis.ExtendedCorrelationAnalyzer.getInstance().analyze());
        echoReport.put("memory_timeseries", com.echo.aggregate.MemoryTimeSeries.getInstance().toMap());
        echoReport.put("bottleneck_detection", com.echo.analysis.BottleneckDetector.getInstance().toMap());
        echoReport.put("network", com.echo.measure.NetworkMetrics.getInstance().toMap());
        echoReport.put("render", com.echo.measure.RenderMetrics.getInstance().toMap());
        echoReport.put("timeseries_summary", com.echo.aggregate.TimeSeriesStore.getInstance().toSummary());

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
    /**
     * HTML 리포트 생성 (Interactive Dashboard)
     */
    public String generateHtml() {
        TimingData tickData = profiler.getTimingData(ProfilingPoint.TICK);
        TickHistogram histogram = profiler.getTickHistogram();
        String jsonChain = generateJson(); // Embed JSON for JS to use

        StringBuilder sb = new StringBuilder();
        sb.append("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n");
        sb.append("  <meta charset=\"UTF-8\">\n");
        sb.append("  <title>Echo Profiler Report</title>\n");
        sb.append("  <style>\n");
        sb.append("    :root { --bg: #1a1a2e; --card: #16213e; --text: #eee; --accent: #4ecdc4; --warn: #ff6b6b; }\n");
        sb.append(
                "    body { font-family: sans-serif; background: var(--bg); color: var(--text); padding: 0; margin: 0; }\n");
        sb.append(
                "    .header { background: #0f3460; padding: 20px; display: flex; justify-content: space-between; align-items: center; }\n");
        sb.append("    .tabs { display: flex; background: #1a1a40; }\n");
        sb.append("    .tab { padding: 15px 25px; cursor: pointer; opacity: 0.7; transition: 0.3s; }\n");
        sb.append("    .tab:hover { opacity: 1; background: #2a2a50; }\n");
        sb.append("    .tab.active { border-bottom: 3px solid var(--accent); opacity: 1; }\n");
        sb.append("    .content { padding: 20px; display: none; }\n");
        sb.append("    .content.active { display: block; animation: fadein 0.3s; }\n");
        sb.append(
                "    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }\n");
        sb.append(
                "    .card { background: var(--card); padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }\n");
        sb.append("    .metric-value { font-size: 2em; font-weight: bold; color: var(--accent); }\n");
        sb.append("    table { width: 100%; border-collapse: collapse; margin-top: 10px; }\n");
        sb.append("    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }\n");
        sb.append("    th { background: rgba(255,255,255,0.05); color: var(--accent); }\n");
        sb.append("    .bar-container { background: #333; height: 10px; border-radius: 5px; overflow: hidden; }\n");
        sb.append("    .bar-fill { height: 100%; background: var(--accent); }\n");
        sb.append("    @keyframes fadein { from { opacity: 0; } to { opacity: 1; } }\n");
        sb.append("  </style>\n");
        sb.append("</head>\n<body>\n");

        // Header
        sb.append("<div class=\"header\">\n");
        sb.append("  <h1>🔊 Echo Profiler</h1>\n");
        sb.append("  <div>").append(java.time.LocalDateTime.now()).append("</div>\n");
        sb.append("</div>\n");

        // Tabs
        sb.append("<div class=\"tabs\">\n");
        sb.append("  <div class=\"tab active\" onclick=\"showTab('summary')\">Summary</div>\n");
        sb.append("  <div class=\"tab\" onclick=\"showTab('heavy')\">Heavy Functions</div>\n");
        sb.append("  <div class=\"tab\" onclick=\"showTab('lua')\">Lua / Context</div>\n");
        sb.append("  <div class=\"tab\" onclick=\"showTab('deep')\">Deep Analysis</div>\n");
        sb.append("  <div class=\"tab\" onclick=\"showTab('raw')\">Raw JSON</div>\n");
        sb.append("</div>\n");

        // TAB 1: Summary
        sb.append("<div id=\"summary\" class=\"content active\">\n");
        sb.append("  <div class=\"grid\">\n");
        if (tickData != null) {
            sb.append("    <div class=\"card\"><div>Avg Tick</div><div class=\"metric-value\">")
                    .append(String.format("%.2f ms", tickData.getAverageMicros() / 1000.0)).append("</div></div>\n");
            sb.append(
                    "    <div class=\"card\"><div>Max Spike</div><div class=\"metric-value\" style=\"color:var(--warn)\">")
                    .append(String.format("%.2f ms", tickData.getMaxMicros() / 1000.0)).append("</div></div>\n");
            sb.append("    <div class=\"card\"><div>Total Ticks</div><div class=\"metric-value\">")
                    .append(String.format("%,d", tickData.getCallCount())).append("</div></div>\n");
        }
        sb.append("  </div>\n");

        sb.append("  <div class=\"card\"><h3>Tick Distribution</h3>\n");
        long[] counts = histogram.getCounts();
        double[] buckets = histogram.getBuckets();
        long maxCount = java.util.Arrays.stream(counts).max().orElse(1);
        for (int i = 0; i < buckets.length; i++) {
            String label = i == buckets.length - 1 ? String.format("≥%.1f", buckets[i])
                    : String.format("%.1f", buckets[i]);
            int w = (int) ((counts[i] * 100) / maxCount);
            sb.append("<div style=\"display:flex; align-items:center; margin:5px 0\">");
            sb.append("<div style=\"width:60px\">").append(label).append("</div>");
            sb.append("<div class=\"bar-container\" style=\"flex-grow:1\"><div class=\"bar-fill\" style=\"width:")
                    .append(w).append("%\"></div></div>");
            sb.append("<div style=\"width:50px; text-align:right\">").append(counts[i]).append("</div>");
            sb.append("</div>");
        }
        sb.append("  </div>\n");
        sb.append("</div>\n");

        // TAB 2: Heavy Functions
        sb.append("<div id=\"heavy\" class=\"content\">\n");
        sb.append("  <div class=\"card\"><h3>Top Heavy Functions (Java/Engine)</h3><table>\n");
        sb.append("    <tr><th>Function</th><th>Total (ms)</th><th>Avg (ms)</th><th>Count</th></tr>\n");
        List<RankedFunction> funcs = collectHeavyFunctions();
        for (int i = 0; i < Math.min(funcs.size(), 20); i++) {
            RankedFunction f = funcs.get(i);
            sb.append("<tr><td>").append(f.label).append("</td>");
            sb.append("<td>").append(String.format("%.2f", f.totalMicros / 1000.0)).append("</td>");
            sb.append("<td>").append(String.format("%.2f", (double) f.totalMicros / f.callCount / 1000.0))
                    .append("</td>");
            sb.append("<td>").append(f.callCount).append("</td></tr>\n");
        }
        sb.append("  </table></div>\n");
        sb.append("</div>\n");

        // TAB 3: Lua
        sb.append("<div id=\"lua\" class=\"content\">\n");
        sb.append("  <div class=\"grid\">\n");
        sb.append("    <div class=\"card\"><h3>Lua Contexts</h3><div id=\"lua-context-list\"></div></div>\n");
        sb.append("    <div class=\"card\"><h3>Heavy Lua Files</h3><div id=\"lua-file-list\"></div></div>\n");
        sb.append("  </div>\n");
        sb.append("  <div class=\"card\"><h3>Top Lua Functions</h3><div id=\"lua-func-list\"></div></div>\n");
        sb.append("</div>\n");

        // TAB 4: Deep Analysis
        sb.append("<div id=\"deep\" class=\"content\">\n");
        sb.append("  <p>Granular breakdown of Pathfinding, Zombie, and IsoGrid.</p>\n");
        sb.append("  <div class=\"grid\">\n");
        sb.append("     <div class=\"card\"><h3>Pathfinding</h3><div id=\"deep-path\"></div></div>\n");
        sb.append("     <div class=\"card\"><h3>Zombie</h3><div id=\"deep-zombie\"></div></div>\n");
        sb.append("  </div>\n");
        sb.append("  <div class=\"card\"><h3>IsoGrid</h3><div id=\"deep-grid\"></div></div>\n");
        sb.append("</div>\n");

        // TAB 5: Raw
        sb.append("<div id=\"raw\" class=\"content\">\n");
        sb.append("  <textarea style=\"width:100%; height:400px; background:#111; color:#ccc; border:none;\">")
                .append(jsonChain).append("</textarea>\n");
        sb.append("</div>\n");

        // SCRIPT
        sb.append("<script>\n");
        sb.append("  const data = ").append(jsonChain).append(";\n");
        sb.append(
                "  function showTab(id) { document.querySelectorAll('.content').forEach(c => c.classList.remove('active')); document.querySelectorAll('.tab').forEach(t => t.classList.remove('active')); document.getElementById(id).classList.add('active'); event.target.classList.add('active'); }\n");
        sb.append("  \n");
        sb.append("  // Populate Lua\n");
        sb.append("  if(data.echo_report.lua_profiling) {\n");
        sb.append("     const lua = data.echo_report.lua_profiling;\n");
        sb.append("     // Contexts\n");
        sb.append("     if(lua.context_stats) {\n");
        sb.append("        let html = '<table><tr><th>Context</th><th>Total (ms)</th></tr>';\n");
        sb.append(
                "        for(const [k,v] of Object.entries(lua.context_stats)) html += `<tr><td>${k}</td><td>${v.toFixed(2)}</td></tr>`;\n");
        sb.append("        html += '</table>'; document.getElementById('lua-context-list').innerHTML = html;\n");
        sb.append("     }\n");
        sb.append("     // Files\n");
        sb.append("     if(lua.heavy_files) {\n");
        sb.append("        let html = '<table><tr><th>File</th><th>Total (ms)</th></tr>';\n");
        sb.append(
                "        lua.heavy_files.forEach(f => html += `<tr><td>${f.file}</td><td>${f.total_ms}</td></tr>`);\n");
        sb.append("        html += '</table>'; document.getElementById('lua-file-list').innerHTML = html;\n");
        sb.append("     }\n");
        sb.append("     // Functions\n");
        sb.append("     if(lua.top_functions_by_time) {\n");
        sb.append("        let html = '<table><tr><th>Name</th><th>Calls</th><th>Total (ms)</th></tr>';\n");
        sb.append(
                "        lua.top_functions_by_time.forEach(f => html += `<tr><td>${f.name}</td><td>${f.call_count}</td><td>${f.total_time_ms}</td></tr>`);\n");
        sb.append("        html += '</table>'; document.getElementById('lua-func-list').innerHTML = html;\n");
        sb.append("     }\n");
        sb.append("  }\n");
        sb.append("  \n");
        sb.append("  // Populate Deep\n");
        sb.append("  if(data.echo_report.fuse_deep_analysis) {\n");
        sb.append("     const deep = data.echo_report.fuse_deep_analysis;\n");
        sb.append("     const renderDeep = (obj) => {\n");
        sb.append("        if(!obj || !obj.steps) return 'No Data';\n");
        sb.append("        let html = '<table><tr><th>Step</th><th>Count</th><th>Total (ms)</th></tr>';\n");
        sb.append(
                "        for(const [k,v] of Object.entries(obj.steps)) html += `<tr><td>${k}</td><td>${v.count}</td><td>${v.total_ms.toFixed(2)}</td></tr>`;\n");
        sb.append("        return html + '</table>';\n");
        sb.append("     };\n");
        sb.append("     document.getElementById('deep-path').innerHTML = renderDeep(deep.pathfinding);\n");
        sb.append("     document.getElementById('deep-zombie').innerHTML = renderDeep(deep.zombie);\n");
        sb.append("     document.getElementById('deep-grid').innerHTML = renderDeep(deep.iso_grid);\n");
        sb.append("  }\n");
        sb.append("</script>\n");

        sb.append("</body>\n</html>");
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
