package com.echo.report;

import com.echo.measure.EchoProfiler;
import com.echo.report.generator.ReportGenerator;
import com.echo.report.generator.JsonReportGenerator;
import com.echo.report.generator.TextReportGenerator;
import com.echo.report.generator.CsvReportGenerator;
import com.echo.report.generator.HtmlReportGenerator;

import java.io.*;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * Echo Report 생성기
 * 
 * JSON 및 텍스트 형식의 프로파일링 리포트 생성
 * 데이터 수집 로직은 ReportDataCollector로 위임.
 */
public class EchoReport {

    public static final String VERSION = "1.0.1";

    private final ReportDataCollector collector;
    private final Map<String, ReportGenerator> generators = new HashMap<>();

    public EchoReport(EchoProfiler profiler) {
        this(profiler, 10);
    }

    public EchoReport(EchoProfiler profiler, int topN) {
        this.collector = new ReportDataCollector(profiler, topN);

        // Initialize generators
        generators.put("json", new JsonReportGenerator());
        generators.put("text", new TextReportGenerator());
        generators.put("csv", new CsvReportGenerator());
        generators.put("html", new HtmlReportGenerator());
    }

    public void setScenarioName(String name) {
        collector.setScenarioName(name);
    }

    public void addScenarioTag(String tag) {
        collector.addScenarioTag(tag);
    }

    public void setScenarioTags(Set<String> tags) {
        collector.setScenarioTags(tags);
    }

    /**
     * 리포트 데이터 수집 (Map 형태)
     */
    public Map<String, Object> collectReportData() {
        return collector.collect();
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
        if (collector.getProfiler().getTickHistogram().getTotalSamples() == 0) {
            System.out.println("[Echo] Skipping report save: No data collected (0 ticks).");
            return null;
        }

        // Phase 5.2 + v0.9: Quality-based three-tier path separation
        int score = ReportQualityScorer.getInstance().calculateScore(collector.getProfiler()).score;
        int minQuality = com.echo.config.EchoConfig.getInstance().getMinQualityToSave();
        int baselineThreshold = com.echo.config.EchoConfig.getInstance().getBaselineQualityThreshold();

        // Determine save location based on quality score
        String subFolder;
        if (score >= baselineThreshold) {
            subFolder = "baseline";
            System.out.println("[Echo] High quality report (" + score + ") → baseline folder.");
        } else if (score >= minQuality) {
            subFolder = "normal";
            System.out.println("[Echo] Report quality (" + score + ") → normal folder.");
        } else {
            subFolder = "low_quality";
            System.out.println("[Echo] Low quality report (" + score + ") below threshold (" + minQuality
                    + ") → low_quality folder.");
        }
        directory = directory + File.separator + subFolder;

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

    /**
     * 세션 종료 시 품질 요약 출력 (Phase 6.2)
     */
    public void printQualitySummary() {
        ReportQualityScorer.QualityResult result = ReportQualityScorer.getInstance()
                .calculateScore(collector.getProfiler());
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
        System.out.println("═══════════════════════════════════════════════════════\n");
    }

    public void onTick() {
        collector.onTick();
    }

    /**
     * 품질 플래그 기록 (Phase 1)
     */
    public void recordQualityFlag(com.echo.aggregate.DataQualityFlag flag) {
        collector.recordQualityFlag(flag);
    }

    /**
     * ReportMetadata 접근자
     */
    public ReportMetadata getReportMetadata() {
        return collector.getReportMetadata();
    }
}
