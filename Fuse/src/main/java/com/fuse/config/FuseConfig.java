package com.fuse.config;

import com.pulse.api.log.PulseLogger;

/**
 * Fuse Configuration.
 * 
 * v1.1: Conservative Preset 기본값 + 신규 파라미터
 * 
 * @since Fuse 0.3.0
 * @since Fuse 1.1.0 - Conservative Preset
 */
public class FuseConfig {

    private static final FuseConfig INSTANCE = new FuseConfig();
    /** Config file path (reserved for future file-based config loading) */
    @SuppressWarnings("unused")
    private static final String CONFIG_FILE = "Fuse/fuse.json";

    // ========================================
    // Throttling Settings
    // ========================================

    /** Throttling master switch */
    private boolean enableThrottling = true;

    /** Step-level throttling */
    private boolean enableStepThrottling = true;

    /** Throttle intensity (Conservative: 0.5) */
    private float throttleIntensity = 0.5f;

    /** Distance bands (squared) */
    private int nearDistSq = 400; // 20² tiles
    private int mediumDistSq = 1600; // 40² tiles
    private int farDistSq = 6400; // 80² tiles

    // ========================================
    // Governor Settings (v1.1)
    // ========================================

    /** Tick budget for 60fps */
    private double tickBudgetMs = 16.67;

    /** Force cutoff threshold for 30fps */
    private double forceCutoffMs = 33.33;

    /** Batch check size (zombies per time check) */
    private int batchCheckSize = 20;

    // ========================================
    // Panic Protocol Settings (v1.1)
    // ========================================

    /** Spike threshold (ms) */
    private long spikeThresholdMs = 100;

    /** Sliding window size (ms) */
    private long windowSizeMs = 5000;

    /** Spike count threshold for panic entry */
    private int spikeCountThreshold = 2;

    /** Ticks per recovery phase */
    private int recoveryPhaseTicks = 30;

    // ========================================
    // Hysteresis Settings (v1.1)
    // ========================================

    /** Entry: 1s max threshold */
    private double entryMax1sMs = 33.33;

    /** Entry: 5s avg threshold */
    private double entryAvg5sMs = 20.0;

    /** Exit: 5s avg threshold */
    private double exitAvg5sMs = 12.0;

    /** Exit: stability ticks required */
    private int exitStabilityTicks = 300;

    // ========================================
    // Guard Settings (v1.1)
    // ========================================

    /** Vehicle guard: entry speed */
    private float vehicleSpeedEntryKmh = 30f;

    /** Vehicle guard: exit speed */
    private float vehicleSpeedExitKmh = 20f;

    /** Streaming guard: player speed threshold */
    private float playerSpeedThreshold = 15f;

    /** Streaming guard: frame drop threshold (ms) */
    private long frameDropThresholdMs = 50;

    // ========================================
    // Failsoft Settings (v1.1)
    // ========================================

    /** Max consecutive errors before intervention disabled */
    private int maxConsecutiveErrors = 3;

    // ========================================
    // IOGuard Settings (v2.0)
    // ========================================

    /** IOGuard master switch */
    private boolean enableIOGuard = true;

    /** IO_ENTER 예산 배수 */
    private float ioEnterBudgetMultiplier = 0.7f;

    /** IO_ACTIVE 예산 배수 */
    private float ioActiveBudgetMultiplier = 0.3f;

    /** COOLDOWN 예산 배수 */
    private float ioCooldownBudgetMultiplier = 0.9f;

    /** IO_ENTER 틱 수 */
    private int ioEnterTicks = 5;

    /** IO_EXIT 복구 틱 수 */
    private int ioRecoveryTicks = 30;

    /** COOLDOWN 틱 수 */
    private int ioCooldownTicks = 10;

    /** Deadman Switch: IO_ACTIVE 최대 틱 (5초 @60fps) */
    private int ioActiveTimeoutTicks = 300;

    /** WORLD 타입만 IOGuard 적용 */
    private boolean ioGuardWorldSaveOnly = false;

    /** IOGuard 로그 활성화 */
    private boolean ioGuardLogEnabled = true;

    // ========================================
    // Singleton
    // ========================================

    public static FuseConfig getInstance() {
        return INSTANCE;
    }

    private FuseConfig() {
        load();
    }

    public void load() {
        // 간단한 기본값 사용 (파일 로드는 추후 구현)
        PulseLogger.info("Fuse", "Config loaded (v1.1 Conservative Preset)");
    }

    public void save() {
        // 추후 구현
    }

    // ========================================
    // Throttling Getters
    // ========================================

    public boolean isThrottlingEnabled() {
        return enableThrottling;
    }

    public boolean isStepThrottlingEnabled() {
        return enableStepThrottling;
    }

    public float getThrottleIntensity() {
        return throttleIntensity;
    }

    public int getNearDistSq() {
        return nearDistSq;
    }

    public int getMediumDistSq() {
        return mediumDistSq;
    }

    public int getFarDistSq() {
        return farDistSq;
    }

    // ========================================
    // Governor Getters (v1.1)
    // ========================================

    public double getTickBudgetMs() {
        return tickBudgetMs;
    }

    public double getForceCutoffMs() {
        return forceCutoffMs;
    }

    public int getBatchCheckSize() {
        return batchCheckSize;
    }

    // ========================================
    // Panic Getters (v1.1)
    // ========================================

    public long getSpikeThresholdMs() {
        return spikeThresholdMs;
    }

    public long getWindowSizeMs() {
        return windowSizeMs;
    }

    public int getSpikeCountThreshold() {
        return spikeCountThreshold;
    }

    public int getRecoveryPhaseTicks() {
        return recoveryPhaseTicks;
    }

    // ========================================
    // Hysteresis Getters (v1.1)
    // ========================================

    public double getEntryMax1sMs() {
        return entryMax1sMs;
    }

    public double getEntryAvg5sMs() {
        return entryAvg5sMs;
    }

    public double getExitAvg5sMs() {
        return exitAvg5sMs;
    }

    public int getExitStabilityTicks() {
        return exitStabilityTicks;
    }

    // ========================================
    // Guard Getters (v1.1)
    // ========================================

    public float getVehicleSpeedEntryKmh() {
        return vehicleSpeedEntryKmh;
    }

    public float getVehicleSpeedExitKmh() {
        return vehicleSpeedExitKmh;
    }

    public float getPlayerSpeedThreshold() {
        return playerSpeedThreshold;
    }

    public long getFrameDropThresholdMs() {
        return frameDropThresholdMs;
    }

    // ========================================
    // Failsoft Getters (v1.1)
    // ========================================

    public int getMaxConsecutiveErrors() {
        return maxConsecutiveErrors;
    }

    // ========================================
    // IOGuard Getters (v2.0)
    // ========================================

    public boolean isIOGuardEnabled() {
        return enableIOGuard;
    }

    public float getIOEnterBudgetMultiplier() {
        return ioEnterBudgetMultiplier;
    }

    public float getIOActiveBudgetMultiplier() {
        return ioActiveBudgetMultiplier;
    }

    public float getIOCooldownBudgetMultiplier() {
        return ioCooldownBudgetMultiplier;
    }

    public int getIOEnterTicks() {
        return ioEnterTicks;
    }

    public int getIORecoveryTicks() {
        return ioRecoveryTicks;
    }

    public int getIOCooldownTicks() {
        return ioCooldownTicks;
    }

    public int getIOActiveTimeoutTicks() {
        return ioActiveTimeoutTicks;
    }

    public boolean isIOGuardWorldSaveOnly() {
        return ioGuardWorldSaveOnly;
    }

    public boolean isIOGuardLogEnabled() {
        return ioGuardLogEnabled;
    }

    // ========================================
    // Setters
    // ========================================

    public void setThrottlingEnabled(boolean enabled) {
        this.enableThrottling = enabled;
        PulseLogger.info("Fuse", "Throttling: " + (enabled ? "ON" : "OFF"));
    }

    public void setThrottleIntensity(float intensity) {
        this.throttleIntensity = Math.max(0f, Math.min(1f, intensity));
        PulseLogger.info("Fuse", "Throttle intensity: " + this.throttleIntensity);
    }
}
