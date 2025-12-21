package com.fuse.config;

/**
 * Fuse Configuration.
 * 
 * @since Fuse 0.3.0
 */
public class FuseConfig {

    private static final FuseConfig INSTANCE = new FuseConfig();
    private static final String CONFIG_FILE = "Fuse/fuse.json";

    // --- Throttling Settings ---

    /** Throttling master switch (default: ON) */
    private boolean enableThrottling = true;

    /** Step-level throttling (default: ON - ThrottleLevel 연동) */
    private boolean enableStepThrottling = true;

    /** Distance bands (squared) */
    private int nearDistSq = 400; // 20²
    private int mediumDistSq = 1600; // 40²
    private int farDistSq = 6400; // 80²

    /** 히스테리시스 마진 (플리커링 방지) */
    private int hysteresisMargin = 4; // ±2 타일

    public static FuseConfig getInstance() {
        return INSTANCE;
    }

    private FuseConfig() {
        load();
    }

    public void load() {
        // 간단한 기본값 사용 (파일 로드는 추후 구현)
        System.out.println("[Fuse] Config loaded (defaults)");
    }

    public void save() {
        // 추후 구현
    }

    // --- Getters ---

    public boolean isThrottlingEnabled() {
        return enableThrottling;
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

    public int getHysteresisMargin() {
        return hysteresisMargin;
    }

    public boolean isStepThrottlingEnabled() {
        return enableStepThrottling;
    }

    // --- Setters ---

    public void setThrottlingEnabled(boolean enabled) {
        this.enableThrottling = enabled;
        System.out.println("[Fuse] Throttling: " + (enabled ? "ON" : "OFF"));
    }
}
