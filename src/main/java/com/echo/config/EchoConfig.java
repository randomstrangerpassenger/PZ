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

    // 사용자 홈 디렉토리 기반 설정 경로 (권한 문제 방지)
    private static final String CONFIG_DIR = System.getProperty("user.home") + "/Zomboid/Echo";
    private static final String CONFIG_FILE = "echo.json";

    private static EchoConfig instance;

    // ============================================================
    // 설정 필드
    // ============================================================

    /** 설정 버전 (마이그레이션용) */
    private int configVersion = 1;

    /** 스파이크 임계값 (ms) */
    private double spikeThresholdMs = EchoConstants.DEFAULT_SPIKE_THRESHOLD_MS;

    /** 핵심 프로파일링 활성화 (기본 ON) */
    private boolean coreProfilingEnabled = true;

    /** 심층 분석 활성화 (SubTiming, Fuse, TickPhase 등) */
    private boolean deepAnalysisEnabled = false;

    /** Lua 프로파일링 활성화 (Heavy) */
    private boolean luaProfilingEnabled = false;

    /** Lua Sampling Profiler 활성화 (sethook) */
    private boolean luaSamplingEnabled = false;

    /** Pathfinding 상세 분석 (LOS 등) */
    private boolean enablePathfindingDetails = false;

    /** Zombie 상세 분석 (Behavior/Motion 분리) */
    private boolean enableZombieDetails = false;

    /** IsoGrid 상세 분석 (Lighting/Recalc) */
    private boolean enableIsoGridDetails = false;

    // ============================================================
    // 기타 설정
    // ============================================================

    /** 게임 시작 시 자동으로 프로파일링 시작 */
    private boolean autoStartProfiling = true;

    /** 리포트 자동 저장 */
    private boolean autoSaveReports = true;

    /** 리포트 저장 경로 */
    private String reportDirectory = EchoConstants.DEFAULT_REPORT_DIR;

    /** 스택 캡처 활성화 (디버그용) */
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
                // Config Version Check
                if (loaded.configVersion < this.configVersion) {
                    System.out.println("[Echo] Config version mismatch (Found: " + loaded.configVersion + ", Current: "
                            + this.configVersion + "). Migrating defaults where necessary.");
                    // 마이그레이션 로직이 필요하면 여기에 추가
                }

                // this.configVersion = this.configVersion; // Keep current version (no-op)
                this.spikeThresholdMs = loaded.spikeThresholdMs;
                this.coreProfilingEnabled = loaded.coreProfilingEnabled;
                this.deepAnalysisEnabled = loaded.deepAnalysisEnabled;
                this.luaProfilingEnabled = loaded.luaProfilingEnabled;
                this.luaSamplingEnabled = loaded.luaSamplingEnabled;
                this.enablePathfindingDetails = loaded.enablePathfindingDetails;
                this.enableZombieDetails = loaded.enableZombieDetails;
                this.enableIsoGridDetails = loaded.enableIsoGridDetails;

                this.autoStartProfiling = loaded.autoStartProfiling;
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
        this.coreProfilingEnabled = true;
        this.deepAnalysisEnabled = false;
        this.luaProfilingEnabled = false;
        this.luaSamplingEnabled = false;
        this.enablePathfindingDetails = false;
        this.enableZombieDetails = false;
        this.enableIsoGridDetails = false;

        this.autoStartProfiling = true;
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

    public int getConfigVersion() {
        return configVersion;
    }

    public double getSpikeThresholdMs() {
        return spikeThresholdMs;
    }

    public void setSpikeThresholdMs(double spikeThresholdMs) {
        this.spikeThresholdMs = spikeThresholdMs;
    }

    public boolean isCoreProfilingEnabled() {
        return coreProfilingEnabled;
    }

    public void setCoreProfilingEnabled(boolean enabled) {
        this.coreProfilingEnabled = enabled;
    }

    public boolean isDeepAnalysisEnabled() {
        return deepAnalysisEnabled;
    }

    public void setDeepAnalysisEnabled(boolean enabled) {
        this.deepAnalysisEnabled = enabled;
    }

    public boolean isLuaProfilingEnabled() {
        return luaProfilingEnabled;
    }

    public void setLuaProfilingEnabled(boolean enabled) {
        this.luaProfilingEnabled = enabled;
    }

    public boolean isLuaSamplingEnabled() {
        return luaSamplingEnabled;
    }

    public void setLuaSamplingEnabled(boolean enabled) {
        this.luaSamplingEnabled = enabled;
    }

    public boolean isEnablePathfindingDetails() {
        return enablePathfindingDetails;
    }

    public void setEnablePathfindingDetails(boolean enablePathfindingDetails) {
        this.enablePathfindingDetails = enablePathfindingDetails;
    }

    public boolean isEnableZombieDetails() {
        return enableZombieDetails;
    }

    public void setEnableZombieDetails(boolean enableZombieDetails) {
        this.enableZombieDetails = enableZombieDetails;
    }

    public boolean isEnableIsoGridDetails() {
        return enableIsoGridDetails;
    }

    public void setEnableIsoGridDetails(boolean enableIsoGridDetails) {
        this.enableIsoGridDetails = enableIsoGridDetails;
    }

    public boolean isAutoStartProfiling() {
        return autoStartProfiling;
    }

    public void setAutoStartProfiling(boolean autoStartProfiling) {
        this.autoStartProfiling = autoStartProfiling;
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
        System.out.println("\n[Echo] Current Configuration (v" + configVersion + "):");
        System.out.println("───────────────────────────────────────────────────────");
        System.out.printf("  spike.threshold     = %.2f ms%n", spikeThresholdMs);
        System.out.printf("  core.profiling      = %s%n", coreProfilingEnabled);
        System.out.printf("  deep.analysis       = %s%n", deepAnalysisEnabled);
        System.out.printf("  lua.profiling       = %s%n", luaProfilingEnabled);
        System.out.printf("    - pathfinding     = %s%n", enablePathfindingDetails);
        System.out.printf("    - zombie          = %s%n", enableZombieDetails);
        System.out.printf("    - isogrid         = %s%n", enableIsoGridDetails);
        System.out.printf("  auto.start          = %s%n", autoStartProfiling);
        System.out.printf("  report.auto_save    = %s%n", autoSaveReports);
        System.out.printf("  report.directory    = %s%n", reportDirectory);
        System.out.printf("  stack.capture       = %s%n", stackCaptureEnabled);
        System.out.printf("  debug.mode          = %s%n", debugMode);
        System.out.printf("  top_n               = %d%n", topNFunctions);
        System.out.println();
    }
}
