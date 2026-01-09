package com.fuse.throttle;

import com.fuse.guard.StreamingGuard;
import com.fuse.guard.VehicleGuard;
import com.fuse.telemetry.TelemetryReason;

/**
 * Guard 평가기.
 * 
 * <h2>설계 원칙 (Phase 1-B)</h2>
 * <ul>
 * <li>Guard 체크 로직만 담당</li>
 * <li>Hot-path: O(1) 비트마스크/단순 비교</li>
 * <li>파라미터로 필요한 값 전달 (전역 싱글톤 호출 최소화)</li>
 * </ul>
 * 
 * @since Fuse 2.4.0
 */
public class GuardEvaluator {

    // Guard 상태 플래그 (비트마스크)
    private static final int FLAG_VEHICLE_PASSIVE = 0x01;
    private static final int FLAG_STREAMING_YIELD = 0x02;

    private VehicleGuard vehicleGuard;
    private StreamingGuard streamingGuard;

    // 캐시된 상태 (틱당 1회 갱신)
    private int cachedFlags = 0;
    private TelemetryReason cachedReason = null;
    private ThrottleLevel cachedOverrideLevel = null;

    public void setGuards(VehicleGuard vehicleGuard, StreamingGuard streamingGuard) {
        this.vehicleGuard = vehicleGuard;
        this.streamingGuard = streamingGuard;
    }

    /**
     * 틱 시작 시 Guard 상태 갱신 (O(1) 이후 조회).
     * 
     * Hot-path에서 매번 Guard.shouldPassive() 호출 대신,
     * 틱당 1회만 평가하고 이후는 플래그로 체크.
     */
    public void updateForTick() {
        cachedFlags = 0;
        cachedReason = null;
        cachedOverrideLevel = null;

        if (vehicleGuard != null && vehicleGuard.shouldPassive()) {
            cachedFlags |= FLAG_VEHICLE_PASSIVE;
            cachedReason = vehicleGuard.getLastReason();
            cachedOverrideLevel = ThrottleLevel.FULL;
        }

        if (streamingGuard != null && streamingGuard.shouldYieldToStreaming()) {
            cachedFlags |= FLAG_STREAMING_YIELD;
            cachedReason = streamingGuard.getLastReason();
            cachedOverrideLevel = ThrottleLevel.MINIMAL;
        }
    }

    /**
     * Guard에 의해 개입이 차단되는지 확인 (O(1)).
     */
    public boolean isBlocked() {
        return cachedFlags != 0;
    }

    /**
     * Guard 차단 시 사용할 오버라이드 레벨.
     */
    public ThrottleLevel getOverrideLevel() {
        return cachedOverrideLevel;
    }

    /**
     * 마지막 Guard 이유.
     */
    public TelemetryReason getLastReason() {
        return cachedReason;
    }

    /**
     * 차량 Guard 활성 여부.
     */
    public boolean isVehiclePassive() {
        return (cachedFlags & FLAG_VEHICLE_PASSIVE) != 0;
    }

    /**
     * 스트리밍 Guard 활성 여부.
     */
    public boolean isStreamingYield() {
        return (cachedFlags & FLAG_STREAMING_YIELD) != 0;
    }
}
