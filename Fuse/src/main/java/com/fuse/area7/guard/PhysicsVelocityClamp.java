package com.fuse.area7.guard;

import com.fuse.telemetry.ReasonStats;
import com.fuse.telemetry.TelemetryReason;
import com.pulse.api.log.PulseLogger;

/**
 * 물리 속도 클램프.
 * 
 * <p>
 * Gemini 단독 제안 (채택): NaN/Infinity 방어.
 * </p>
 * 
 * <h2>매커니즘</h2>
 * <ul>
 * <li>속도 벡터 Sanity Check</li>
 * <li>NaN/Infinity 감지 시 이전 상태 복원</li>
 * <li>"리셋" 아닌 "복원" (수동적 방어)</li>
 * </ul>
 * 
 * @since Fuse 2.2
 */
public class PhysicsVelocityClamp {

    private static final String LOG = "Fuse";
    private final ReasonStats telemetry;

    private int sanityFailures;

    public PhysicsVelocityClamp(ReasonStats telemetry) {
        this.telemetry = telemetry;
    }

    /**
     * 속도 벡터 sanity check.
     * 
     * @param velocityX X 속도
     * @param velocityY Y 속도
     * @param velocityZ Z 속도 (또는 0)
     * @return true = 정상, false = sanity check 실패
     */
    public boolean isSane(float velocityX, float velocityY, float velocityZ) {
        return !Float.isNaN(velocityX) && !Float.isInfinite(velocityX)
                && !Float.isNaN(velocityY) && !Float.isInfinite(velocityY)
                && !Float.isNaN(velocityZ) && !Float.isInfinite(velocityZ);
    }

    /**
     * 속도 벡터 sanity check (2D).
     */
    public boolean isSane(float velocityX, float velocityY) {
        return isSane(velocityX, velocityY, 0f);
    }

    /**
     * Sanity check 실패 시 호출.
     * 
     * @param objectId  객체 식별자 (로깅용)
     * @param velocityX 실패한 X 속도
     * @param velocityY 실패한 Y 속도
     */
    public void onSanityCheckFailed(Object objectId, float velocityX, float velocityY) {
        sanityFailures++;

        PulseLogger.warn(LOG, "[Physics] Sanity check failed for {}: velocity=({}, {}), restoring previous state",
                objectId, velocityX, velocityY);

        if (telemetry != null) {
            telemetry.increment(TelemetryReason.PHYSICS_SANITY_FAILURE);
        }
    }

    /**
     * 값을 안전한 범위로 클램프.
     * NaN/Infinity인 경우 0 반환.
     */
    public float clampSafe(float value) {
        if (Float.isNaN(value) || Float.isInfinite(value)) {
            return 0f;
        }
        return value;
    }

    /**
     * 값을 범위 내로 클램프.
     */
    public float clamp(float value, float min, float max) {
        if (Float.isNaN(value) || Float.isInfinite(value)) {
            return 0f;
        }
        return Math.max(min, Math.min(max, value));
    }

    public int getSanityFailures() {
        return sanityFailures;
    }

    public void resetTelemetry() {
        sanityFailures = 0;
    }
}
