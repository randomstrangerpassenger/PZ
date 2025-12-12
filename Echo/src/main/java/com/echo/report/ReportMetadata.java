package com.echo.report;

import java.util.*;

/**
 * Echo 리포트 메타데이터.
 * 
 * 리포트 재현성을 위한 환경 정보를 수집합니다.
 * A/B 비교나 최적화 효과 측정에 필수적입니다.
 * 
 * @since 1.0.1
 */
public class ReportMetadata {

    private String pulseVersion = "1.0.1";
    private String echoVersion = "1.0.1";
    private List<String> loadedMods = new ArrayList<>();
    private String jvmOptions = "";
    private String mapSeed = "unknown";
    private long sessionStartTime;
    private long samplingDurationMs;
    private String gameMode = "unknown";
    private boolean isMultiplayer = false;
    private int playerCount = 1;

    // 시스템 정보
    private String javaVersion;
    private String osName;
    private int availableProcessors;
    private long maxMemoryMB;

    public ReportMetadata() {
        this.sessionStartTime = System.currentTimeMillis();
        collectSystemInfo();
    }

    /**
     * 시스템 정보 자동 수집
     */
    private void collectSystemInfo() {
        this.javaVersion = System.getProperty("java.version");
        this.osName = System.getProperty("os.name");
        this.availableProcessors = Runtime.getRuntime().availableProcessors();
        this.maxMemoryMB = Runtime.getRuntime().maxMemory() / (1024 * 1024);

        // JVM 옵션 수집 시도
        try {
            java.lang.management.RuntimeMXBean runtimeMxBean = java.lang.management.ManagementFactory
                    .getRuntimeMXBean();
            List<String> arguments = runtimeMxBean.getInputArguments();
            this.jvmOptions = String.join(" ", arguments);
        } catch (Exception e) {
            this.jvmOptions = "unavailable";
        }
    }

    /**
     * Pulse에서 메타데이터 수집
     */
    public void collectFromPulse() {
        try {
            // GameAccess를 통해 맵 시드 수집
            Class<?> gameAccessClass = Class.forName("com.pulse.api.GameAccess");

            // 맵 시드
            try {
                java.lang.reflect.Method getMapSeed = gameAccessClass.getMethod("getMapSeed");
                Object seed = getMapSeed.invoke(null);
                if (seed != null) {
                    this.mapSeed = seed.toString();
                }
            } catch (Exception e) {
                // 무시
            }

            // 멀티플레이어 여부
            try {
                java.lang.reflect.Method isMultiplayer = gameAccessClass.getMethod("isMultiplayer");
                Object result = isMultiplayer.invoke(null);
                if (result instanceof Boolean) {
                    this.isMultiplayer = (Boolean) result;
                }
            } catch (Exception e) {
                // 무시
            }
        } catch (ClassNotFoundException e) {
            // Pulse 없이 실행 중
        }
    }

    /**
     * 샘플링 종료 시 호출
     */
    public void finalizeSampling() {
        this.samplingDurationMs = System.currentTimeMillis() - sessionStartTime;
    }

    // Getters and Setters

    public String getPulseVersion() {
        return pulseVersion;
    }

    public void setPulseVersion(String pulseVersion) {
        this.pulseVersion = pulseVersion;
    }

    public String getEchoVersion() {
        return echoVersion;
    }

    public void setEchoVersion(String echoVersion) {
        this.echoVersion = echoVersion;
    }

    public List<String> getLoadedMods() {
        return loadedMods;
    }

    public void setLoadedMods(List<String> loadedMods) {
        this.loadedMods = loadedMods;
    }

    public void addLoadedMod(String modId) {
        this.loadedMods.add(modId);
    }

    public String getJvmOptions() {
        return jvmOptions;
    }

    public String getMapSeed() {
        return mapSeed;
    }

    public void setMapSeed(String mapSeed) {
        this.mapSeed = mapSeed;
    }

    public long getSessionStartTime() {
        return sessionStartTime;
    }

    public long getSamplingDurationMs() {
        return samplingDurationMs;
    }

    public String getGameMode() {
        return gameMode;
    }

    public void setGameMode(String gameMode) {
        this.gameMode = gameMode;
    }

    public boolean isMultiplayer() {
        return isMultiplayer;
    }

    public void setMultiplayer(boolean multiplayer) {
        isMultiplayer = multiplayer;
    }

    public int getPlayerCount() {
        return playerCount;
    }

    public void setPlayerCount(int playerCount) {
        this.playerCount = playerCount;
    }

    /**
     * Map 형태로 변환 (JSON 직렬화용)
     */
    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();

        // 버전 정보
        Map<String, String> versions = new LinkedHashMap<>();
        versions.put("pulse", pulseVersion);
        versions.put("echo", echoVersion);
        map.put("versions", versions);

        // 세션 정보
        Map<String, Object> session = new LinkedHashMap<>();
        session.put("start_time", sessionStartTime);
        session.put("duration_ms", samplingDurationMs);
        session.put("game_mode", gameMode);
        session.put("multiplayer", isMultiplayer);
        session.put("player_count", playerCount);
        session.put("map_seed", mapSeed);
        map.put("session", session);

        // 시스템 정보
        Map<String, Object> system = new LinkedHashMap<>();
        system.put("java_version", javaVersion);
        system.put("os", osName);
        system.put("cpu_cores", availableProcessors);
        system.put("max_memory_mb", maxMemoryMB);
        system.put("jvm_options", jvmOptions);
        map.put("system", system);

        // 모드 정보
        map.put("loaded_mods", loadedMods);

        return map;
    }
}
