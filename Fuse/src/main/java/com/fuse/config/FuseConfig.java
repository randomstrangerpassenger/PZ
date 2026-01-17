package com.fuse.config;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.pulse.api.log.PulseLogger;

import java.io.*;
import java.nio.file.*;

/**
 * Fuse Configuration.
 * 
 * Conservative Preset 기본값 + 신규 파라미터
 * JSON 파일 기반 영속화
 */
public class FuseConfig {

    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final String CONFIG_DIR = System.getProperty("user.home") + "/Zomboid/Fuse";
    private static final String CONFIG_FILE = "fuse.json";

    private static FuseConfig INSTANCE;

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
    // Hysteresis Settings
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
    // Guard Settings
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
    // Failsoft Settings
    // ========================================

    /** Max consecutive errors before intervention disabled */
    private int maxConsecutiveErrors = 3;

    // ========================================
    // Adaptive Gate Settings
    // ========================================

    /** Adaptive Gate master switch */
    private boolean enableAdaptiveGate = true;

    /** Zombie dedup (experimental, default OFF) */
    private boolean enableZombieDedup = false;

    /** Path dedup (experimental, default OFF) */
    private boolean enablePathDedup = false;

    // ========================================
    // Sustained Early Exit Settings
    // ========================================

    /** Sustained Early Exit master switch (opt-in, default OFF) */
    private boolean sustainedEarlyExitEnabled = false;

    /** ACTIVE state maximum duration before forced COOLDOWN (ms) */
    private long activeMaxMs = 2000;

    /** Hard limit streak threshold for forced COOLDOWN */
    private int hardStreakMax = 4;

    /** COOLDOWN duration before returning to PASSTHROUGH (ms) */
    private long cooldownMs = 2000;

    // ========================================
    // IOGuard/GCPressureGuard Settings removed
    // ========================================

    // ========================================
    // Singleton
    // ========================================

    public static FuseConfig getInstance() {
        if (INSTANCE == null) {
            INSTANCE = new FuseConfig();
            INSTANCE.load();
        }
        return INSTANCE;
    }

    private FuseConfig() {
        // Private constructor - load() called from getInstance()
    }

    public void load() {
        Path configPath = Paths.get(CONFIG_DIR, CONFIG_FILE);

        if (!Files.exists(configPath)) {
            PulseLogger.info("Fuse", "Config file not found, using defaults");
            save(); // Create default config file
            return;
        }

        try (Reader reader = new FileReader(configPath.toFile())) {
            FuseConfig loaded = GSON.fromJson(reader, FuseConfig.class);
            if (loaded != null) {
                copyFrom(loaded);
            }
            PulseLogger.info("Fuse", "Config loaded from: " + configPath);
        } catch (Exception e) {
            PulseLogger.error("Fuse", "Failed to load config: " + e.getMessage());
        }
    }

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
            PulseLogger.info("Fuse", "Config saved to: " + configPath);
        } catch (Exception e) {
            PulseLogger.error("Fuse", "Failed to save config: " + e.getMessage());
        }
    }

    private void copyFrom(FuseConfig other) {
        this.enableThrottling = other.enableThrottling;
        this.enableStepThrottling = other.enableStepThrottling;
        this.throttleIntensity = other.throttleIntensity;
        this.nearDistSq = other.nearDistSq;
        this.mediumDistSq = other.mediumDistSq;
        this.farDistSq = other.farDistSq;
        this.tickBudgetMs = other.tickBudgetMs;
        this.forceCutoffMs = other.forceCutoffMs;
        this.batchCheckSize = other.batchCheckSize;
        this.spikeThresholdMs = other.spikeThresholdMs;
        this.windowSizeMs = other.windowSizeMs;
        this.spikeCountThreshold = other.spikeCountThreshold;
        this.recoveryPhaseTicks = other.recoveryPhaseTicks;
        this.entryMax1sMs = other.entryMax1sMs;
        this.entryAvg5sMs = other.entryAvg5sMs;
        this.exitAvg5sMs = other.exitAvg5sMs;
        this.exitStabilityTicks = other.exitStabilityTicks;
        this.vehicleSpeedEntryKmh = other.vehicleSpeedEntryKmh;
        this.vehicleSpeedExitKmh = other.vehicleSpeedExitKmh;
        this.playerSpeedThreshold = other.playerSpeedThreshold;
        this.frameDropThresholdMs = other.frameDropThresholdMs;
        this.maxConsecutiveErrors = other.maxConsecutiveErrors;
        //
        this.enableAdaptiveGate = other.enableAdaptiveGate;
        this.enableZombieDedup = other.enableZombieDedup;
        this.enablePathDedup = other.enablePathDedup;
        //
        this.sustainedEarlyExitEnabled = other.sustainedEarlyExitEnabled;
        this.activeMaxMs = other.activeMaxMs;
        this.hardStreakMax = other.hardStreakMax;
        this.cooldownMs = other.cooldownMs;
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
    // IOGuard/GCPressureGuard Getters removed
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

    // Debug Force Getters removed

    // ========================================
    // Adaptive Gate Getters/Setters
    // ========================================

    public boolean isEnableAdaptiveGate() {
        return enableAdaptiveGate;
    }

    public void setEnableAdaptiveGate(boolean enable) {
        this.enableAdaptiveGate = enable;
        PulseLogger.info("Fuse", "Adaptive Gate: " + (enable ? "ON" : "OFF"));
    }

    public boolean isEnableZombieDedup() {
        return enableZombieDedup;
    }

    public boolean isEnablePathDedup() {
        return enablePathDedup;
    }

    // ========================================
    // Sustained Early Exit Getters
    // ========================================

    public boolean isSustainedEarlyExitEnabled() {
        return sustainedEarlyExitEnabled;
    }

    public long getActiveMaxMs() {
        return activeMaxMs;
    }

    public int getHardStreakMax() {
        return hardStreakMax;
    }

    public long getCooldownMs() {
        return cooldownMs;
    }
}
