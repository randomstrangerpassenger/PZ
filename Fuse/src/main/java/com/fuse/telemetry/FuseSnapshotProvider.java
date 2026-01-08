package com.fuse.telemetry;

import com.fuse.governor.AdaptiveGate;
import com.fuse.governor.TickBudgetGovernor;
import com.fuse.hook.FuseHookAdapter;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Fuse Snapshot Provider - Echo 연동용 스냅샷 제공자 (v2.5).
 * 
 * 틱 시작/종료 시점의 델타 메트릭을 캡처하여 Echo 리포트에 제공합니다.
 * 
 * 제공 메트릭:
 * - zombie_updates: 틱당 좀비 업데이트 횟수
 * - motion_ms, perception_ms, tracking_ms: 각 단계별 소요 시간
 * - gate_state, gate_transitions: AdaptiveGate 상태
 * - fuse_overhead_ms: Fuse 자체 오버헤드
 * - reason_counts: 개입 이유별 카운트
 * 
 * @since Fuse 2.5.0
 */
public class FuseSnapshotProvider {

    private final FuseHookAdapter hookAdapter;
    private final ReasonStats reasonStats;
    private final AdaptiveGate adaptiveGate;
    private final TickBudgetGovernor governor;

    // 틱 시작 시점의 누적값 저장
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

    /**
     * 틱 시작 시 호출 - 현재 누적값 저장.
     */
    public void onTickStart() {
        if (hookAdapter != null) {
            prevUpdateCount = hookAdapter.getZombieUpdateCount();
            prevMotionMicros = hookAdapter.getTotalMotionMicros();
            prevPerceptionMicros = hookAdapter.getTotalPerceptionMicros();
            prevTrackingMicros = hookAdapter.getTotalTrackingMicros();
        }
    }

    /**
     * 현재 스냅샷 캡처 (틱 종료 시 호출).
     * 
     * @return 스냅샷 맵 (Echo 리포트용)
     */
    public Map<String, Object> captureSnapshot() {
        Map<String, Object> snapshot = new LinkedHashMap<>();

        // 좀비 델타 메트릭
        if (hookAdapter != null) {
            snapshot.put("zombie_updates",
                    hookAdapter.getZombieUpdateCount() - prevUpdateCount);
            snapshot.put("motion_ms",
                    (hookAdapter.getTotalMotionMicros() - prevMotionMicros) / 1000.0);
            snapshot.put("perception_ms",
                    (hookAdapter.getTotalPerceptionMicros() - prevPerceptionMicros) / 1000.0);
            snapshot.put("tracking_ms",
                    (hookAdapter.getTotalTrackingMicros() - prevTrackingMicros) / 1000.0);
        }

        // AdaptiveGate 상태
        if (adaptiveGate != null) {
            snapshot.put("gate_state", adaptiveGate.getState().name());
            snapshot.put("gate_transitions", adaptiveGate.getStateTransitions());
            snapshot.put("passthrough", adaptiveGate.isPassthrough());
        }

        // Governor 오버헤드
        if (governor != null) {
            snapshot.put("fuse_overhead_ms", governor.getFuseConsumedMs());
        }

        // Reason 카운트
        if (reasonStats != null) {
            snapshot.put("reason_counts", reasonStats.toMap());
            snapshot.put("total_interventions", reasonStats.getTotalCount());
        }

        return snapshot;
    }

    /**
     * 간단한 요약 문자열 반환 (로깅용).
     */
    public String getSummary() {
        Map<String, Object> snap = captureSnapshot();
        StringBuilder sb = new StringBuilder();
        sb.append("Fuse Snapshot: ");
        sb.append("updates=").append(snap.getOrDefault("zombie_updates", 0));
        sb.append(", gate=").append(snap.getOrDefault("gate_state", "N/A"));
        sb.append(", overhead=").append(
                String.format("%.3f", (Double) snap.getOrDefault("fuse_overhead_ms", 0.0))).append("ms");
        return sb.toString();
    }
}
