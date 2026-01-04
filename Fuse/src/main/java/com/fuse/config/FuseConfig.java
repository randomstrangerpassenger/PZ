package com.fuse.config;

import com.pulse.api.log.PulseLogger;

/**
 * Fuse Configuration.
 * 
 * Conservative Preset 기본값 + 신규 파라미터
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
    // Governor Settings
    // ========================================

    /** Tick budget for 60fps */
    private double tickBudgetMs = 16.67;

    /** Force cutoff threshold for 30fps */
    private double forceCutoffMs = 33.33;

    /** Batch check size (zombies per time check) */
    private int batchCheckSize = 20;

    // ========================================
    // Panic Protocol Settings
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
    // IOGuard/GCPressureGuard Settings removed in v2.3
    // ========================================

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
        PulseLogger.info("Fuse", "Config loaded (v2.3 - IO/GC guards removed)");
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
    // Governor Getters
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
    // Panic Getters
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
    // Hysteresis Getters
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
    // Guard Getters
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
    // Failsoft Getters
    // ========================================

    public int getMaxConsecutiveErrors() {
        return maxConsecutiveErrors;
    }

    // ========================================
    // IOGuard/GCPressureGuard Getters removed in v2.3
    // ========================================

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

    // Debug Force Getters removed in v2.3
}
