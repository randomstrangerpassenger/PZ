package com.fuse.guard;

import com.fuse.telemetry.TelemetryReason;

/**
 * Streaming Guard.
 * 
 * 대규모 청크 로딩 시 CPU를 스트리밍에 양보합니다.
 * v1.1: 간접 신호 기반 (플레이어 이동 속도 + 프레임 드랍 감지)
 * TODO v1.2: WorldStream queue 직접 감지
 * 
 * @since Fuse 1.1
 */
public class StreamingGuard {

    private static final String LOG = "Fuse";

    // --- 설정값 ---
    private float playerSpeedThreshold = 15f; // 타일/초
    private long frameDropThresholdMs = 50; // 50ms 이상이면 프레임 드랍

    // --- 상태 ---
    private boolean yieldMode = false;
    private boolean enabled = true;

    // 프레임 드랍 감지용
    private long lastFrameTimeMs = 0;
    private int recentDropCount = 0;
    private static final int DROP_WINDOW_TICKS = 30;
    private int tickCounter = 0;

    // 텔레메트리
    private TelemetryReason lastReason = null;

    public StreamingGuard() {
        System.out.println("[" + LOG + "] StreamingGuard initialized (v1.1 indirect signals)");
    }

    /**
     * 스트리밍에 양보해야 하는지 반환.
     * true면 좀비 업데이트 예산을 0에 가깝게.
     */
    public boolean shouldYieldToStreaming() {
        if (!enabled) {
            return false;
        }

        tickCounter++;

        // 30틱마다 드랍 카운터 리셋
        if (tickCounter >= DROP_WINDOW_TICKS) {
            tickCounter = 0;
            recentDropCount = 0;
        }

        boolean wasPreviousYield = yieldMode;

        // 조건: 빠른 이동 + 최근 프레임 드랍
        boolean fastMoving = isPlayerMovingFast();
        boolean frameDropped = recentFrameDropDetected();

        yieldMode = fastMoving && frameDropped;

        // 상태 변경 시 로그
        if (yieldMode && !wasPreviousYield) {
            lastReason = TelemetryReason.GUARD_STREAMING;
            System.out.println("[" + LOG + "] StreamingGuard: YIELD mode (heavy streaming detected)");
        } else if (!yieldMode && wasPreviousYield) {
            lastReason = null;
            System.out.println("[" + LOG + "] StreamingGuard: NORMAL mode");
        }

        return yieldMode;
    }

    /**
     * 틱 시간 기록 (프레임 드랍 감지용).
     * FuseMod.onTick()에서 호출.
     */
    public void recordTickDuration(long durationMs) {
        if (durationMs >= frameDropThresholdMs) {
            recentDropCount++;
        }
        lastFrameTimeMs = System.currentTimeMillis();
    }

    /**
     * 플레이어가 빠르게 이동 중인지.
     */
    private boolean isPlayerMovingFast() {
        try {
            Class<?> isoPlayerClass = Class.forName("zombie.characters.IsoPlayer");
            Object player = isoPlayerClass.getMethod("getInstance").invoke(null);
            if (player == null) {
                return false;
            }

            // getMoveSpeed() 또는 유사한 메서드로 이동 속도 확인
            // 차량 탑승 시 차량 속도 사용
            Object vehicle = isoPlayerClass.getMethod("getVehicle").invoke(player);
            if (vehicle != null) {
                Class<?> baseVehicleClass = Class.forName("zombie.vehicles.BaseVehicle");
                Object speedObj = baseVehicleClass.getMethod("getCurrentSpeedKmHour").invoke(vehicle);
                if (speedObj instanceof Number) {
                    // 30km/h ≈ 8.3 타일/초 (rough estimate)
                    float kmh = ((Number) speedObj).floatValue();
                    return kmh > 20f; // 20km/h 이상
                }
            }

            // 도보 이동 속도 체크 (getPathSpeed 등)
            // 보수적으로 false 반환 (차량이 아니면 무시)
            return false;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * 최근 프레임 드랍이 감지되었는지.
     */
    private boolean recentFrameDropDetected() {
        return recentDropCount >= 2; // 30틱 내 2회 이상 드랍
    }

    /**
     * 마지막 텔레메트리 이유.
     */
    public TelemetryReason getLastReason() {
        return lastReason;
    }

    /**
     * 현재 Yield 모드 상태.
     */
    public boolean isYieldMode() {
        return yieldMode;
    }

    // --- 설정 ---

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public void setPlayerSpeedThreshold(float threshold) {
        this.playerSpeedThreshold = threshold;
    }

    public void setFrameDropThresholdMs(long threshold) {
        this.frameDropThresholdMs = threshold;
    }

    public void reset() {
        yieldMode = false;
        recentDropCount = 0;
        tickCounter = 0;
        lastReason = null;
    }
}
