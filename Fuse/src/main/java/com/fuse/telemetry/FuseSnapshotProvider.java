package com.fuse.telemetry;

import com.fuse.FuseMod;
import com.fuse.config.FuseConfig;
import com.fuse.governor.AdaptiveGate;
import com.fuse.governor.TickBudgetGovernor;
import com.fuse.hook.FuseHookAdapter;
import com.pulse.api.spi.IStabilizerSnapshotProvider;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Fuse Snapshot Provider - Echo 연동용 SPI 구현체 (Bundle B v4).
 * 
 * Fuse의 동작/차단/실패를 Echo 리포트로 증명하기 위한 스냅샷 제공자.
 * 
 * @since Fuse 2.5.0
 */
public class FuseSnapshotProvider implements IStabilizerSnapshotProvider {

    private static final String PROVIDER_ID = "fuse";
    private static final String PROVIDER_NAME = "Fuse Stabilizer";

    private final FuseHookAdapter hookAdapter;
    private final ReasonStats reasonStats;
    private final AdaptiveGate adaptiveGate;
    private final TickBudgetGovernor governor;

    private ProviderStatus status = ProviderStatus.INACTIVE;
    private String lastErrorCode = "";
    private String lastErrorMessage = "";

    // v4: delta 초기화 여부 추적 (미초기화 시 delta 필드 생략)
    private boolean deltaInitialized = false;
    private long prevUpdateCount;
    private long prevMotionMicros;
    private long prevPerceptionMicros;
    private long prevTrackingMicros;

    public FuseSnapshotProvider(FuseHookAdapter hookAdapter,
            ReasonStats reasonStats,
            AdaptiveGate adaptiveGate,
            TickBudgetGovernor governor) {
        this.hookAdapter = hookAdapter;
        this.reasonStats = reasonStats;
        this.adaptiveGate = adaptiveGate;
        this.governor = governor;
    }

    // ═══════════════════════════════════════════════════════════════
    // IProvider 구현
    // ═══════════════════════════════════════════════════════════════

    @Override
    public String getId() {
        return PROVIDER_ID;
    }

    @Override
    public String getName() {
        return PROVIDER_NAME;
    }

    @Override
    public String getVersion() {
        return FuseMod.VERSION;
    }

    // isEnabled()는 인터페이스 default 사용 (항상 true)

    // ═══════════════════════════════════════════════════════════════
    // IStabilizerSnapshotProvider 구현
    // ═══════════════════════════════════════════════════════════════

    @Override
    public ProviderStatus getProviderStatus() {
        return status;
    }

    /**
     * 상태 업데이트 (FuseLifecycle에서 호출).
     * FuseConfig.isThrottlingEnabled() 기준으로 상태 결정.
     */
    public void updateStatus() {
        if (status == ProviderStatus.FAILED) {
            return; // 실패 상태는 유지
        }
        // Fuse 기능 활성화 여부로 상태 결정
        this.status = FuseConfig.getInstance().isThrottlingEnabled()
                ? ProviderStatus.ACTIVE
                : ProviderStatus.INACTIVE;
    }

    /**
     * 실패 상태 설정 (등록 실패 등).
     * 
     * @param errorCode    에러 코드 (REGISTRATION_FAILED 등)
     * @param errorMessage 상세 메시지
     */
    public void setFailed(String errorCode, String errorMessage) {
        this.status = ProviderStatus.FAILED;
        this.lastErrorCode = errorCode;
        this.lastErrorMessage = errorMessage;
    }

    // ═══════════════════════════════════════════════════════════════
    // Snapshot Capture (no-throw 계약)
    // ═══════════════════════════════════════════════════════════════

    @Override
    public Map<String, Object> captureSnapshot() {
        Map<String, Object> snapshot = new LinkedHashMap<>();

        // 타임스탬프
        snapshot.put("captured_at_ms", System.currentTimeMillis());

        // Provider 상태 (문자열로 직렬화)
        snapshot.put("provider_status", status.name());

        // active는 FuseConfig.isThrottlingEnabled() 기준
        boolean isActive = status == ProviderStatus.ACTIVE;
        snapshot.put("active", isActive);

        // 실패 상태면 기본값 반환
        if (status == ProviderStatus.FAILED) {
            snapshot.put("snapshot_ok", false);
            snapshot.put("error_code", lastErrorCode);
            snapshot.put("error_message", lastErrorMessage);
            snapshot.put("total_interventions", 0L);
            snapshot.put("reason_counts", Collections.emptyMap());
            return snapshot;
        }

        // 정상 캡처 시도 (no-throw)
        try {
            snapshot.put("snapshot_ok", true);
            snapshot.put("error_code", "");
            snapshot.put("error_message", "");

            // Reason 카운트 (Bundle B 핵심 데이터)
            if (reasonStats != null) {
                snapshot.put("reason_counts", reasonStats.toMap());
                snapshot.put("total_interventions", reasonStats.getTotalCount());

                // v4: last_reason → top_reason (명칭 수정 - 실제로는 최빈값)
                var top = reasonStats.getTop(1);
                if (!top.isEmpty()) {
                    snapshot.put("top_reason", top.get(0).getKey().name());
                }
            } else {
                snapshot.put("reason_counts", Collections.emptyMap());
                snapshot.put("total_interventions", 0L);
            }

            // v4: delta 메트릭 - 초기화된 경우에만 포함
            if (deltaInitialized && hookAdapter != null) {
                snapshot.put("zombie_updates",
                        hookAdapter.getZombieUpdateCount() - prevUpdateCount);
                snapshot.put("motion_ms",
                        (hookAdapter.getTotalMotionMicros() - prevMotionMicros) / 1000.0);
                snapshot.put("perception_ms",
                        (hookAdapter.getTotalPerceptionMicros() - prevPerceptionMicros) / 1000.0);
                snapshot.put("tracking_ms",
                        (hookAdapter.getTotalTrackingMicros() - prevTrackingMicros) / 1000.0);
            }
            // deltaInitialized=false면 delta 필드 생략 (v4 안전 처리)

            // AdaptiveGate 상태
            if (adaptiveGate != null) {
                snapshot.put("gate_state", adaptiveGate.getState().name());
                snapshot.put("gate_transitions", adaptiveGate.getStateTransitions());
                snapshot.put("passthrough", adaptiveGate.isPassthrough());
                snapshot.put("intervention_blocked", adaptiveGate.isInterventionBlocked());

                // Bundle C 메트릭
                snapshot.put("escape_count", adaptiveGate.getEscapeCount());
                snapshot.put("escape_by_timeout", adaptiveGate.getEscapeByTimeoutCount());
                snapshot.put("escape_by_hard_streak", adaptiveGate.getEscapeByHardStreakCount());
                snapshot.put("hard_limit_streak_max", adaptiveGate.getHardLimitStreakMax());
            }

            // Bundle C: 정책 모드
            snapshot.put("policy_mode", FuseConfig.getInstance().isSustainedEarlyExitEnabled()
                    ? "SUSTAINED_EARLY_EXIT"
                    : "BASELINE");

            // Governor 오버헤드
            if (governor != null) {
                snapshot.put("fuse_overhead_ms", governor.getFuseConsumedMs());
            }

        } catch (Exception e) {
            // no-throw 계약: 예외를 데이터로 변환
            snapshot.put("snapshot_ok", false);
            snapshot.put("error_code", "SNAPSHOT_THROWN");
            snapshot.put("error_message", e.getMessage() != null ? e.getMessage() : "Unknown error");
            snapshot.put("total_interventions", 0L);
            snapshot.put("reason_counts", Collections.emptyMap());
        }

        // "present" 키는 넣지 않음 (Echo가 결정)
        return snapshot;
    }

    /**
     * 틱 시작 시 호출 - 현재 누적값 저장.
     */
    public void onTickStart() {
        if (hookAdapter != null) {
            prevUpdateCount = hookAdapter.getZombieUpdateCount();
            prevMotionMicros = hookAdapter.getTotalMotionMicros();
            prevPerceptionMicros = hookAdapter.getTotalPerceptionMicros();
            prevTrackingMicros = hookAdapter.getTotalTrackingMicros();
            deltaInitialized = true; // v4: 초기화 완료 마킹
        }
    }

    /**
     * 간단한 요약 문자열 반환 (로깅용).
     */
    public String getSummary() {
        return "Fuse Snapshot: status=" + status +
                ", interventions=" + (reasonStats != null ? reasonStats.getTotalCount() : 0);
    }
}
