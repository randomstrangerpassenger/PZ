package com.echo.report.generator;

import java.util.Map;

/**
 * CSV 포맷 리포트 생성기.
 * 
 * @since 1.1.0
 */
public class CsvReportGenerator implements ReportGenerator {

    @Override
    public String generate(Map<String, Object> data) {
        StringBuilder sb = new StringBuilder();

        // Header
        sb.append("point,avgMs,maxMs,minMs,callCount\n");

        // Subsystems data
        if (data.containsKey("subsystems")) {
            @SuppressWarnings("unchecked")
            Map<String, Object> subsystems = (Map<String, Object>) data.get("subsystems");
            for (Map.Entry<String, Object> entry : subsystems.entrySet()) {
                @SuppressWarnings("unchecked")
                Map<String, Object> subsystem = (Map<String, Object>) entry.getValue();
                sb.append(String.format("%s,%.4f,%.4f,%.4f,%d\n",
                        escapeCsv(entry.getKey()),
                        getDouble(subsystem, "avgMs"),
                        getDouble(subsystem, "maxMs"),
                        getDouble(subsystem, "minMs"),
                        getInt(subsystem, "callCount")));
            }
        }

        return sb.toString();
    }

    @Override
    public String getFormatName() {
        return "CSV";
    }

    @Override
    public String getFileExtension() {
        return ".csv";
    }

    private String escapeCsv(String value) {
        if (value == null)
            return "";
        if (value.contains(",") || value.contains("\"") || value.contains("\n")) {
            return "\"" + value.replace("\"", "\"\"") + "\"";
        }
        return value;
    }

    private double getDouble(Map<String, Object> map, String key) {
        Object value = map.get(key);
        return value instanceof Number ? ((Number) value).doubleValue() : 0.0;
    }

    private int getInt(Map<String, Object> map, String key) {
        Object value = map.get(key);
        return value instanceof Number ? ((Number) value).intValue() : 0;
    }
}
