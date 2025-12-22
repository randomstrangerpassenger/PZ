package com.fuse.guard;

import com.fuse.telemetry.TelemetryReason;

/**
 * Vehicle Guard.
 * 
 * 플레이어 차량 탑승/고속 이동 시 Fuse를 자동으로 보수화합니다.
 * 히스테리시스 적용: 진입 30km/h / 해제 20km/h (떨림 방지)
 * 
 * @since Fuse 1.1
 */
public class VehicleGuard {

    private static final String LOG = "Fuse";

    // --- 설정값 ---
    private float speedEntryKmh = 30f; // 진입 임계치
    private float speedExitKmh = 20f; // 해제 임계치

    // --- 상태 ---
    private boolean passiveMode = false;
    private boolean enabled = true;

    // 텔레메트리
    private TelemetryReason lastReason = null;

    public VehicleGuard() {
        System.out.println("[" + LOG + "] VehicleGuard initialized (entry: "
                + speedEntryKmh + "km/h, exit: " + speedExitKmh + "km/h)");
    }

    /**
     * Passive 모드 여부 반환.
     * true면 Fuse가 최소 개입합니다.
     */
    public boolean shouldPassive() {
        if (!enabled) {
            return false;
        }

        if (!isPlayerInVehicle()) {
            if (passiveMode) {
                passiveMode = false;
                lastReason = null;
            }
            return false;
        }

        float speed = getVehicleSpeed();

        // 히스테리시스 적용
        if (!passiveMode && speed > speedEntryKmh) {
            passiveMode = true;
            lastReason = TelemetryReason.GUARD_VEHICLE;
            System.out.println("[" + LOG + "] VehicleGuard: PASSIVE mode (speed: "
                    + String.format("%.1f", speed) + "km/h)");
        } else if (passiveMode && speed < speedExitKmh) {
            passiveMode = false;
            lastReason = null;
            System.out.println("[" + LOG + "] VehicleGuard: NORMAL mode (speed: "
                    + String.format("%.1f", speed) + "km/h)");
        }

        return passiveMode;
    }

    /**
     * 플레이어가 차량에 탑승 중인지 확인.
     * 리플렉션으로 IsoPlayer.isSeatedInVehicle 체크.
     */
    private boolean isPlayerInVehicle() {
        try {
            // IsoPlayer.getInstance() → isSeatedInVehicle()
            Class<?> isoPlayerClass = Class.forName("zombie.characters.IsoPlayer");
            Object player = isoPlayerClass.getMethod("getInstance").invoke(null);
            if (player == null) {
                return false;
            }

            // isSeatedInVehicle() 메서드 호출
            Boolean seated = (Boolean) isoPlayerClass.getMethod("isSeatedInVehicle").invoke(player);
            return seated != null && seated;
        } catch (Exception e) {
            // 메서드가 없거나 오류 발생 시 false
            return false;
        }
    }

    /**
     * 차량 속도 계산 (km/h).
     * 리플렉션으로 BaseVehicle 접근.
     */
    private float getVehicleSpeed() {
        try {
            Class<?> isoPlayerClass = Class.forName("zombie.characters.IsoPlayer");
            Object player = isoPlayerClass.getMethod("getInstance").invoke(null);
            if (player == null) {
                return 0f;
            }

            // getVehicle() 메서드 호출
            Object vehicle = isoPlayerClass.getMethod("getVehicle").invoke(player);
            if (vehicle == null) {
                return 0f;
            }

            // getCurrentSpeedKmHour() 메서드 호출
            Class<?> baseVehicleClass = Class.forName("zombie.vehicles.BaseVehicle");
            Object speedObj = baseVehicleClass.getMethod("getCurrentSpeedKmHour").invoke(vehicle);
            if (speedObj instanceof Number) {
                return ((Number) speedObj).floatValue();
            }
            return 0f;
        } catch (Exception e) {
            return 0f;
        }
    }

    /**
     * 마지막 텔레메트리 이유.
     */
    public TelemetryReason getLastReason() {
        return lastReason;
    }

    /**
     * 현재 Passive 모드 상태.
     */
    public boolean isPassiveMode() {
        return passiveMode;
    }

    // --- 설정 ---

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public void setSpeedEntryKmh(float speedEntryKmh) {
        this.speedEntryKmh = speedEntryKmh;
    }

    public void setSpeedExitKmh(float speedExitKmh) {
        this.speedExitKmh = speedExitKmh;
    }

    public void reset() {
        passiveMode = false;
        lastReason = null;
    }
}
