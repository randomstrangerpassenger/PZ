package com.echo.report.generator;

import java.util.List;
import java.util.Map;

/**
 * 텍스트 포맷 리포트 생성기 (콘솔 출력용).
 * 
 * @since 1.1.0
 */
public class TextReportGenerator implements ReportGenerator {

    @Override
    public String generate(Map<String, Object> data) {
        StringBuilder sb = new StringBuilder();

        sb.append("\n");
        sb.append("╔═══════════════════════════════════════════════════════════════╗\n");
        sb.append("║                    ECHO PROFILING REPORT                      ║\n");
        sb.append("╚═══════════════════════════════════════════════════════════════╝\n");
        sb.append("\n");

        // Summary section
        if (data.containsKey("summary")) {
            @SuppressWarnings("unchecked")
            Map<String, Object> summary = (Map<String, Object>) data.get("summary");
            sb.append("┌─ Summary ─────────────────────────────────────────────────────┐\n");
            sb.append(String.format("│  Sessions: %-10s  Tick Count: %-20s │\n",
                    "1", // Single session per report
                    summary.getOrDefault("total_ticks", 0)));
            sb.append(String.format("│  Avg Tick: %-10s  Max Tick: %-21s │\n",
                    formatMs(summary.get("average_tick_ms")),
                    formatMs(summary.get("max_tick_spike_ms"))));
            sb.append("└───────────────────────────────────────────────────────────────┘\n");
            sb.append("\n");
        }

        // Subsystems section
        if (data.containsKey("subsystems")) {
            @SuppressWarnings("unchecked")
            Map<String, Object> subsystems = (Map<String, Object>) data.get("subsystems");
            sb.append("┌─ Subsystems ──────────────────────────────────────────────────┐\n");
            for (Map.Entry<String, Object> entry : subsystems.entrySet()) {
                @SuppressWarnings("unchecked")
                Map<String, Object> subsystem = (Map<String, Object>) entry.getValue();
                sb.append(String.format("│  %-15s avg: %-8s  max: %-8s  calls: %-6s │\n",
                        entry.getKey(),
                        formatMs(subsystem.get("average_time_ms")),
                        formatMs(subsystem.get("max_time_ms")),
                        subsystem.getOrDefault("call_count", 0)));
            }
            sb.append("└───────────────────────────────────────────────────────────────┘\n");
            sb.append("\n");
        }

        // Heavy functions section
        if (data.containsKey("heavy_functions")) {
            @SuppressWarnings("unchecked")
            Map<String, Object> heavyRoot = (Map<String, Object>) data.get("heavy_functions");
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> heavy = (List<Map<String, Object>>) heavyRoot.get("by_total_time");
            if (heavy != null && !heavy.isEmpty()) {
                sb.append("┌─ Heavy Functions (Top 5) ─────────────────────────────────────┐\n");
                int count = 0;
                for (Map<String, Object> func : heavy) {
                    if (count++ >= 5)
                        break;
                    sb.append(String.format("│  %d. %-40s %8s │\n",
                            count,
                            truncate(String.valueOf(func.get("label")), 40),
                            formatMs(func.get("total_time_ms"))));
                }
                sb.append("└───────────────────────────────────────────────────────────────┘\n");
                sb.append("\n");
            }
        }

        // Recommendations section
        if (data.containsKey("recommendations")) {
            @SuppressWarnings("unchecked")
            List<String> recommendations = (List<String>) data.get("recommendations");
            if (!recommendations.isEmpty()) {
                sb.append("┌─ Recommendations ─────────────────────────────────────────────┐\n");
                for (String rec : recommendations) {
                    sb.append(String.format("│  • %-60s │\n", truncate(rec, 60)));
                }
                sb.append("└───────────────────────────────────────────────────────────────┘\n");
            }
        }

        return sb.toString();
    }

    @Override
    public String getFormatName() {
        return "Text";
    }

    @Override
    public String getFileExtension() {
        return ".txt";
    }

    private String formatMs(Object value) {
        if (value instanceof Number) {
            return String.format("%.2fms", ((Number) value).doubleValue());
        }
        return "N/A";
    }

    private String truncate(String s, int maxLen) {
        if (s == null)
            return "";
        return s.length() > maxLen ? s.substring(0, maxLen - 3) + "..." : s;
    }
}
