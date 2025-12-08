package com.echo.config;

import com.echo.EchoConstants;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Echo 설정 관리
 * 
 * JSON 기반 설정 파일 로드/저장
 */
public class EchoConfig {

    private static final Gson GSON = new GsonBuilder()
            .setPrettyPrinting()
            .create();

    private static final String CONFIG_DIR = "./config";
    private static final String CONFIG_FILE = "echo.json";

    private static EchoConfig instance;

    // ============================================================
    // 설정 필드
    // ============================================================

    /** 스파이크 임계값 (ms) */
    private double spikeThresholdMs = EchoConstants.DEFAULT_SPIKE_THRESHOLD_MS;

    /** Lua 프로파일링 기본 활성화 */
    private boolean luaProfilingDefault = false;

    /** 리포트 자동 저장 */
    private boolean autoSaveReports = true;

    /** 리포트 저장 경로 */
    private String reportDirectory = EchoConstants.DEFAULT_REPORT_DIR;

    /** 스택 캡처 활성화 */
    private boolean stackCaptureEnabled = false;

    /** 디버그 모드 */
    private boolean debugMode = false;

    /** Top N 함수 표시 수 */
    private int topNFunctions = EchoConstants.DEFAULT_TOP_N;

    // ============================================================
    // Singleton
    // ============================================================

    private EchoConfig() {
    }

    public static EchoConfig getInstance() {
        if (instance == null) {
            instance = new EchoConfig();
            instance.load();
        }
        return instance;
    }

    // ============================================================
    // 로드/저장
    // ============================================================

    /**
     * 설정 파일 로드
     */
    public void load() {
        Path configPath = Paths.get(CONFIG_DIR, CONFIG_FILE);

        if (!Files.exists(configPath)) {
            System.out.println("[Echo] Config file not found, using defaults");
            save(); // 기본값으로 생성
            return;
        }

        try (Reader reader = new FileReader(configPath.toFile())) {
            EchoConfig loaded = GSON.fromJson(reader, EchoConfig.class);
            if (loaded != null) {
                this.spikeThresholdMs = loaded.spikeThresholdMs;
                this.luaProfilingDefault = loaded.luaProfilingDefault;
                this.autoSaveReports = loaded.autoSaveReports;
                this.reportDirectory = loaded.reportDirectory;
                this.stackCaptureEnabled = loaded.stackCaptureEnabled;
                this.debugMode = loaded.debugMode;
                this.topNFunctions = loaded.topNFunctions;
            }
            System.out.println("[Echo] Config loaded from: " + configPath);
        } catch (Exception e) {
            System.err.println("[Echo] Failed to load config: " + e.getMessage());
        }
    }

    /**
     * 설정 파일 저장
     */
    public void save() {
        Path configDir = Paths.get(CONFIG_DIR);
        Path configPath = configDir.resolve(CONFIG_FILE);

        try {
            if (!Files.exists(configDir)) {
                Files.createDirectories(configDir);
            }

            try (Writer writer = new FileWriter(configPath.toFile())) {
                GSON.toJson(this, writer);
            }
            System.out.println("[Echo] Config saved to: " + configPath);
        } catch (Exception e) {
            System.err.println("[Echo] Failed to save config: " + e.getMessage());
        }
    }

    /**
     * 설정 리셋
     */
    public void reset() {
        this.spikeThresholdMs = EchoConstants.DEFAULT_SPIKE_THRESHOLD_MS;
        this.luaProfilingDefault = false;
        this.autoSaveReports = true;
        this.reportDirectory = EchoConstants.DEFAULT_REPORT_DIR;
        this.stackCaptureEnabled = false;
        this.debugMode = false;
        this.topNFunctions = EchoConstants.DEFAULT_TOP_N;
        save();
        System.out.println("[Echo] Config reset to defaults");
    }

    // ============================================================
    // Getters / Setters
    // ============================================================

    public double getSpikeThresholdMs() {
        return spikeThresholdMs;
    }

    public void setSpikeThresholdMs(double spikeThresholdMs) {
        this.spikeThresholdMs = spikeThresholdMs;
    }

    public boolean isLuaProfilingDefault() {
        return luaProfilingDefault;
    }

    public void setLuaProfilingDefault(boolean luaProfilingDefault) {
        this.luaProfilingDefault = luaProfilingDefault;
    }

    public boolean isAutoSaveReports() {
        return autoSaveReports;
    }

    public void setAutoSaveReports(boolean autoSaveReports) {
        this.autoSaveReports = autoSaveReports;
    }

    public String getReportDirectory() {
        return reportDirectory;
    }

    public void setReportDirectory(String reportDirectory) {
        this.reportDirectory = reportDirectory;
    }

    public boolean isStackCaptureEnabled() {
        return stackCaptureEnabled;
    }

    public void setStackCaptureEnabled(boolean stackCaptureEnabled) {
        this.stackCaptureEnabled = stackCaptureEnabled;
    }

    public boolean isDebugMode() {
        return debugMode;
    }

    public void setDebugMode(boolean debugMode) {
        this.debugMode = debugMode;
    }

    public int getTopNFunctions() {
        return topNFunctions;
    }

    public void setTopNFunctions(int topNFunctions) {
        this.topNFunctions = topNFunctions;
    }

    /**
     * 콘솔 출력
     */
    public void printConfig() {
        System.out.println("\n[Echo] Current Configuration:");
        System.out.println("───────────────────────────────────────────────────────");
        System.out.printf("  spike.threshold     = %.2f ms%n", spikeThresholdMs);
        System.out.printf("  lua.default         = %s%n", luaProfilingDefault);
        System.out.printf("  report.auto_save    = %s%n", autoSaveReports);
        System.out.printf("  report.directory    = %s%n", reportDirectory);
        System.out.printf("  stack.capture       = %s%n", stackCaptureEnabled);
        System.out.printf("  debug.mode          = %s%n", debugMode);
        System.out.printf("  top_n               = %d%n", topNFunctions);
        System.out.println();
    }
}
