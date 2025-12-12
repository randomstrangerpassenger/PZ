package com.echo.report.generator;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * HTML 포맷 리포트 생성기.
 * 인터랙티브 대시보드를 포함한 HTML 파일을 생성합니다.
 * 
 * @since 1.1.0
 */
public class HtmlReportGenerator implements ReportGenerator {

    private static final Gson GSON = new GsonBuilder()
            .setPrettyPrinting()
            .create();

    @Override
    public String generate(Map<String, Object> data) {
        // Embed JSON for JS to use
        String jsonChain = GSON.toJson(data);

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
        sb.append("  <div>").append(LocalDateTime.now()).append("</div>\n");
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

        Map<String, Object> echoReport = getMap(data, "echo_report"); // Check if wrapped in echo_report
        Map<String, Object> root = echoReport != null ? echoReport : data;

        Map<String, Object> summary = getMap(root, "summary");
        if (summary != null) {
            sb.append("    <div class=\"card\"><div>Avg Tick</div><div class=\"metric-value\">")
                    .append(String.format("%.2f ms", getDouble(summary, "average_tick_ms"))).append("</div></div>\n");
            sb.append(
                    "    <div class=\"card\"><div>Max Spike</div><div class=\"metric-value\" style=\"color:var(--warn)\">")
                    .append(String.format("%.2f ms", getDouble(summary, "max_tick_spike_ms"))).append("</div></div>\n");
            sb.append("    <div class=\"card\"><div>Total Ticks</div><div class=\"metric-value\">")
                    .append(String.format("%,d", getLong(summary, "total_ticks"))).append("</div></div>\n");
        }
        sb.append("  </div>\n");

        sb.append("  <div class=\"card\"><h3>Tick Distribution</h3>\n");
        Map<String, Object> histogram = getMap(root, "tick_histogram");
        if (histogram != null) {
            // Assuming histogram map has 'counts' and 'buckets' lists
            // Since traversing lists in untyped map maps is hard, and the JS can do it
            // easier...
            // But we want server-side rendering for static viewing.
            // We'll rely on JS for complex charts if possible, or simple HTML bars.
            // The original code used Java arrays. Here we have List<Double> and List<Long>.
            // Implementing purely in JS might be cleaner given we pass the full JSON.
            sb.append("    <div id=\"histogram-chart\">Loading Chart...</div>\n");
        }
        sb.append("  </div>\n");
        sb.append("</div>\n");

        // TAB 2: Heavy Functions
        sb.append("<div id=\"heavy\" class=\"content\">\n");
        sb.append("  <div class=\"card\"><h3>Top Heavy Functions (Java/Engine)</h3><table>\n");
        sb.append("    <tr><th>Function</th><th>Total (ms)</th><th>Avg (ms)</th><th>Count</th></tr>\n");

        Map<String, Object> heavyFuncs = getMap(root, "heavy_functions");
        if (heavyFuncs != null) {
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> byTotal = (List<Map<String, Object>>) heavyFuncs.get("by_total_time");
            if (byTotal != null) {
                for (int i = 0; i < Math.min(byTotal.size(), 20); i++) {
                    Map<String, Object> f = byTotal.get(i);
                    sb.append("<tr><td>").append(f.get("label")).append("</td>");
                    sb.append("<td>").append(f.get("total_time_ms")).append("</td>");
                    sb.append("<td>").append(f.get("average_time_ms")).append("</td>");
                    sb.append("<td>").append(f.get("call_count")).append("</td></tr>\n");
                }
            }
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
        sb.append("  const root = data.echo_report || data;\n"); // Handle wrapper
        sb.append(
                "  function showTab(id) { document.querySelectorAll('.content').forEach(c => c.classList.remove('active')); document.querySelectorAll('.tab').forEach(t => t.classList.remove('active')); document.getElementById(id).classList.add('active'); event.target.classList.add('active'); }\n");
        sb.append("  \n");

        // JS Histogram Rendering (replacing Java loop)
        sb.append("  if(root.tick_histogram) {\n");
        sb.append("      const h = root.tick_histogram;\n");
        sb.append("      let html = '';\n");
        sb.append("      const max = Math.max(...h.counts, 1);\n");
        sb.append("      for(let i=0; i<h.buckets.length; i++) {\n");
        sb.append("          const w = (h.counts[i] * 100) / max;\n");
        sb.append("          html += `<div style=\"display:flex; align-items:center; margin:5px 0\">`;\n");
        sb.append("          html += `<div style=\"width:60px\">${h.buckets[i].toFixed(1)}</div>`;\n");
        sb.append(
                "          html += `<div class=\"bar-container\" style=\"flex-grow:1\"><div class=\"bar-fill\" style=\"width:${w}%\\\"></div></div>`;\n");
        sb.append("          html += `<div style=\"width:50px; text-align:right\">${h.counts[i]}</div>`;\n");
        sb.append("          html += `</div>`;\n");
        sb.append("      }\n");
        sb.append("      document.getElementById('histogram-chart').innerHTML = html;\n");
        sb.append("  }\n");

        sb.append("  // Populate Lua\n");
        sb.append("  if(root.lua_profiling) {\n");
        sb.append("     const lua = root.lua_profiling;\n");
        sb.append("     // Contexts\n");
        sb.append("     if(lua.context_totals) {\n"); // context_stats or context_totals? check EchoReport
        sb.append("        let html = '<table><tr><th>Context</th><th>Total (ms)</th></tr>';\n");
        sb.append(
                "        for(const [k,v] of Object.entries(lua.context_totals)) html += `<tr><td>${k}</td><td>${Number(v).toFixed(2)}</td></tr>`;\n"); // Assuming
                                                                                                                                                       // simplified
                                                                                                                                                       // map
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
        sb.append("  if(root.fuse_deep_analysis) {\n");
        sb.append("     const deep = root.fuse_deep_analysis;\n");
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

    @Override
    public String getFormatName() {
        return "HTML";
    }

    @Override
    public String getFileExtension() {
        return ".html";
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> getMap(Map<String, Object> map, String key) {
        Object val = map.get(key);
        if (val instanceof Map) {
            return (Map<String, Object>) val;
        }
        return null;
    }

    private double getDouble(Map<String, Object> map, String key) {
        Object val = map.get(key);
        if (val instanceof Number)
            return ((Number) val).doubleValue();
        return 0.0;
    }

    private long getLong(Map<String, Object> map, String key) {
        Object val = map.get(key);
        if (val instanceof Number)
            return ((Number) val).longValue();
        return 0L;
    }
}
