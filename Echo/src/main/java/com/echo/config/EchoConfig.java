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

    // --- Config Fields ---

    /** 설정 버전 (마이그레이션용) */
    private int configVersion = 1;

    /** 스파이크 임계값 (ms) */
    private double spikeThresholdMs = EchoConstants.DEFAULT_SPIKE_THRESHOLD_MS;

    /** 핵심 프로파일링 활성화 (기본 ON) */
    private boolean coreProfilingEnabled = true;

    /** 심층 분석 활성화 (SubTiming, Fuse, TickPhase 등) */
    private boolean deepAnalysisEnabled = true; // 기본 활성화 (tick_phase, heavy_functions 등)

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

    // --- Other Settings ---

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

    // --- Zero-Risk Engine (v0.9.0) ---

    /**
     * Fallback tick 허용 (디버그 전용, 기본 OFF)
     * 
     * @see com.pulse.api.TickContract
     */
    private boolean allowFallbackTicks = false;

    /**
     * Fallback tick 간격 (ms)
     * 기준: TickContract.DEFAULT_FALLBACK_INTERVAL_MS (200ms)
     * 
     * @see com.pulse.api.TickContract#DEFAULT_FALLBACK_INTERVAL_MS
     */
    private long fallbackTickIntervalMs = 200;

    /** 저장 최소 품질 임계값 (기본 0 = 모두 저장) */
    private int minQualityToSave = 0;

    /** Baseline 품질 임계값 (기본 30, 이상이면 baseline 폴더에 저장) */
    private int baselineQualityThreshold = 30;

    /** 사용자가 명시적으로 Lua OFF를 지정했는지 */
    private boolean userExplicitLuaOff = false;

    /** fallback tick이 사용되었는지 (런타임 상태) */
    private transient boolean usedFallbackTicks = false;

    // --- Singleton ---

    public EchoConfig() {
    }

    public static EchoConfig getInstance() {
        // 1. Try ServiceLocator (Hybrid DI)
        try {
            com.pulse.di.PulseServiceLocator locator = com.pulse.di.PulseServiceLocator.getInstance();
            EchoConfig service = locator.getService(EchoConfig.class);
            if (service != null) {
                return service;
            }
        } catch (NoClassDefFoundError | Exception ignored) {
            // Pulse might not be fully loaded or in standalone test mode
        }

        // 2. Fallback to Singleton
        if (instance == null) {
            instance = new EchoConfig();
            instance.load();

            // Register to ServiceLocator if available
            try {
                com.pulse.di.PulseServiceLocator.getInstance().registerService(EchoConfig.class, instance);
            } catch (NoClassDefFoundError | Exception ignored) {
                // Ignore
            }
        }
        return instance;
    }

    // --- Load/Save ---

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

                // Migrate if needed
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
        this.deepAnalysisEnabled = true; // 기본 활성화
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
        this.allowFallbackTicks = false;
        this.minQualityToSave = 0;
        this.userExplicitLuaOff = false;
        save();
        System.out.println("[Echo] Config reset to defaults");
    }

    /**
     * 설정 검증 및 자동 수정 (Echo 0.9.0 Zero-Risk)
     * enable() 전에 호출하여 잘못된 설정 자동 보정
     * 
     * @return 수정된 항목 수
     */
    public int sanitize() {
        int fixCount = 0;
        StringBuilder log = new StringBuilder();

        // 1. spikeThresholdMs < 0 → 기본값
        if (spikeThresholdMs < 0) {
            spikeThresholdMs = EchoConstants.DEFAULT_SPIKE_THRESHOLD_MS;
            log.append("  - spikeThresholdMs was negative → set to ").append(spikeThresholdMs).append("ms\n");
            fixCount++;
        }

        // 2. deepAnalysisEnabled=true인데 모든 detail 옵션이 false → Wave 1 자동 활성화
        if (deepAnalysisEnabled && !enablePathfindingDetails && !enableZombieDetails && !enableIsoGridDetails) {
            // Wave 1 기본 옵션을 켜줌 (최소한의 deep analysis)
            log.append("  - DeepAnalysis ON but all detail options OFF → enabling basic Wave 1\n");
            // Wave 1은 SubProfiler의 기본 라벨들로 deepAnalysisEnabled만 있으면 동작함
            // 추가 조치 없음 (Wave 1은 deepAnalysisEnabled가 true면 자동 활성화)
            fixCount++;
        }

        // 3. topNFunctions가 너무 작거나 큰 경우
        if (topNFunctions < 1) {
            topNFunctions = 1;
            log.append("  - topNFunctions was < 1 → set to 1\n");
            fixCount++;
        } else if (topNFunctions > 100) {
            topNFunctions = 100;
            log.append("  - topNFunctions was > 100 → set to 100\n");
            fixCount++;
        }

        // 4. minQualityToSave 범위 체크
        if (minQualityToSave < 0) {
            minQualityToSave = 0;
            log.append("  - minQualityToSave was < 0 → set to 0\n");
            fixCount++;
        } else if (minQualityToSave > 100) {
            minQualityToSave = 100;
            log.append("  - minQualityToSave was > 100 → set to 100\n");
            fixCount++;
        }

        if (fixCount > 0) {
            System.out.println("[Echo] Config.sanitize() auto-fixed " + fixCount + " issue(s):");
            System.out.print(log);
            save();
        }

        return fixCount;
    }

    // --- Getters/Setters ---

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

    // --- Zero-Risk Engine Getters/Setters ---

    public boolean isAllowFallbackTicks() {
        return allowFallbackTicks;
    }

    public void setAllowFallbackTicks(boolean allowFallbackTicks) {
        this.allowFallbackTicks = allowFallbackTicks;
    }

    public int getMinQualityToSave() {
        return minQualityToSave;
    }

    public void setMinQualityToSave(int minQualityToSave) {
        this.minQualityToSave = minQualityToSave;
    }

    public int getBaselineQualityThreshold() {
        return baselineQualityThreshold;
    }

    public void setBaselineQualityThreshold(int threshold) {
        this.baselineQualityThreshold = Math.max(0, Math.min(100, threshold));
    }

    public boolean isUserExplicitLuaOff() {
        return userExplicitLuaOff;
    }

    public void setUserExplicitLuaOff(boolean userExplicitLuaOff) {
        this.userExplicitLuaOff = userExplicitLuaOff;
    }

    public boolean isUsedFallbackTicks() {
        return usedFallbackTicks;
    }

    public void setUsedFallbackTicks(boolean usedFallbackTicks) {
        this.usedFallbackTicks = usedFallbackTicks;
    }

    public long getFallbackTickIntervalMs() {
        return fallbackTickIntervalMs;
    }

    public void setFallbackTickIntervalMs(long fallbackTickIntervalMs) {
        this.fallbackTickIntervalMs = Math.max(50, Math.min(1000, fallbackTickIntervalMs)); // 50-1000ms range
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
        System.out.println("  --- Zero-Risk Engine (v0.9.0) ---");
        System.out.printf("  fallback.ticks      = %s%n", allowFallbackTicks);
        System.out.printf("  min.quality.save    = %d%n", minQualityToSave);
        System.out.println();
    }
}
