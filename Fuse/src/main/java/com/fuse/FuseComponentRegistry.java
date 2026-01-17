package com.fuse;

import com.fuse.area7.FusePathfindingGuard;
import com.fuse.governor.AdaptiveGate;
import com.fuse.governor.ItemGovernor;
import com.fuse.governor.RollingTickStats;
import com.fuse.governor.SpikePanicProtocol;
import com.fuse.governor.TickBudgetGovernor;
import com.fuse.guard.FailsoftController;
import com.fuse.guard.StreamingGuard;
import com.fuse.guard.VehicleGuard;
import com.fuse.hook.FuseHookAdapter;
import com.fuse.optimizer.FuseOptimizer;
import com.fuse.telemetry.FuseSnapshotProvider;
import com.fuse.telemetry.ReasonStats;
import com.fuse.throttle.FuseStepPolicy;
import com.fuse.throttle.FuseThrottleController;

/**
 * Fuse 컴포넌트 레지스트리.
 * 
 * 모든 Fuse 컴포넌트를 저장하고 접근을 제공합니다.
 * 컴포넌트 생성은 FuseLifecycle에서 수행합니다.
 * 
 * <h2>초기화 순서 (의존성 방향)</h2>
 * 
 * <pre>
 * 1. RollingTickStats (독립)
 * 2. TickBudgetGovernor (독립)
 * 3. SpikePanicProtocol (독립)
 * 4. ReasonStats (독립)
 * 5. VehicleGuard (독립)
 * 6. StreamingGuard (독립)
 * 7. FailsoftController (독립)
 * 8. FuseHookAdapter (독립)
 * 9. FuseThrottleController ← Governor, PanicProtocol, Stats, Guards, ReasonStats
 * 10. ItemGovernor (독립)
 * 11. FuseStepPolicy (독립)
 * 12. FusePathfindingGuard ← ReasonStats
 * 13. FuseOptimizer (Singleton)
 * </pre>
 * 
 */
public class FuseComponentRegistry {

    // Core Safety Components
    private RollingTickStats stats;
    private TickBudgetGovernor governor;
    private SpikePanicProtocol panicProtocol;
    private ReasonStats reasonStats;
    private AdaptiveGate adaptiveGate;
    private FuseSnapshotProvider snapshotProvider;

    // Guards
    private VehicleGuard vehicleGuard;
    private StreamingGuard streamingGuard;
    private FailsoftController failsoftController;

    // Hook & Throttle
    private FuseHookAdapter hookAdapter;
    private FuseThrottleController throttleController;
    private FuseStepPolicy stepPolicy;

    // Item & Pathfinding
    private ItemGovernor itemGovernor;
    private FusePathfindingGuard pathfindingGuard;

    // Optimizer
    private FuseOptimizer optimizer;

    // ═══════════════════════════════════════════════════════════════
    // Getters - Core Safety
    // ═══════════════════════════════════════════════════════════════

    public RollingTickStats getStats() {
        return stats;
    }

    public TickBudgetGovernor getGovernor() {
        return governor;
    }

    public SpikePanicProtocol getPanicProtocol() {
        return panicProtocol;
    }

    public ReasonStats getReasonStats() {
        return reasonStats;
    }

    public AdaptiveGate getAdaptiveGate() {
        return adaptiveGate;
    }

    public FuseSnapshotProvider getSnapshotProvider() {
        return snapshotProvider;
    }

    // ═══════════════════════════════════════════════════════════════
    // Getters - Guards
    // ═══════════════════════════════════════════════════════════════

    public VehicleGuard getVehicleGuard() {
        return vehicleGuard;
    }

    public StreamingGuard getStreamingGuard() {
        return streamingGuard;
    }

    public FailsoftController getFailsoftController() {
        return failsoftController;
    }

    // ═══════════════════════════════════════════════════════════════
    // Getters - Hook & Throttle
    // ═══════════════════════════════════════════════════════════════

    public FuseHookAdapter getHookAdapter() {
        return hookAdapter;
    }

    public FuseThrottleController getThrottleController() {
        return throttleController;
    }

    public FuseStepPolicy getStepPolicy() {
        return stepPolicy;
    }

    // ═══════════════════════════════════════════════════════════════
    // Getters - Item & Pathfinding
    // ═══════════════════════════════════════════════════════════════

    public ItemGovernor getItemGovernor() {
        return itemGovernor;
    }

    public FusePathfindingGuard getPathfindingGuard() {
        return pathfindingGuard;
    }

    // ═══════════════════════════════════════════════════════════════
    // Getters - Optimizer
    // ═══════════════════════════════════════════════════════════════

    public FuseOptimizer getOptimizer() {
        return optimizer;
    }

    // ═══════════════════════════════════════════════════════════════
    // Setters (Package-private for FuseLifecycle)
    // ═══════════════════════════════════════════════════════════════

    void setStats(RollingTickStats stats) {
        this.stats = stats;
    }

    void setGovernor(TickBudgetGovernor governor) {
        this.governor = governor;
    }

    void setPanicProtocol(SpikePanicProtocol panicProtocol) {
        this.panicProtocol = panicProtocol;
    }

    void setReasonStats(ReasonStats reasonStats) {
        this.reasonStats = reasonStats;
    }

    void setAdaptiveGate(AdaptiveGate adaptiveGate) {
        this.adaptiveGate = adaptiveGate;
    }

    void setSnapshotProvider(FuseSnapshotProvider snapshotProvider) {
        this.snapshotProvider = snapshotProvider;
    }

    void setVehicleGuard(VehicleGuard vehicleGuard) {
        this.vehicleGuard = vehicleGuard;
    }

    void setStreamingGuard(StreamingGuard streamingGuard) {
        this.streamingGuard = streamingGuard;
    }

    void setFailsoftController(FailsoftController failsoftController) {
        this.failsoftController = failsoftController;
    }

    void setHookAdapter(FuseHookAdapter hookAdapter) {
        this.hookAdapter = hookAdapter;
    }

    void setThrottleController(FuseThrottleController throttleController) {
        this.throttleController = throttleController;
    }

    void setStepPolicy(FuseStepPolicy stepPolicy) {
        this.stepPolicy = stepPolicy;
    }

    void setItemGovernor(ItemGovernor itemGovernor) {
        this.itemGovernor = itemGovernor;
    }

    void setPathfindingGuard(FusePathfindingGuard pathfindingGuard) {
        this.pathfindingGuard = pathfindingGuard;
    }

    void setOptimizer(FuseOptimizer optimizer) {
        this.optimizer = optimizer;
    }

    /**
     * 컴포넌트 개수 반환 (테스트용)
     */
    public int getComponentCount() {
        int count = 0;
        if (stats != null)
            count++;
        if (governor != null)
            count++;
        if (panicProtocol != null)
            count++;
        if (reasonStats != null)
            count++;
        if (vehicleGuard != null)
            count++;
        if (streamingGuard != null)
            count++;
        if (failsoftController != null)
            count++;
        if (hookAdapter != null)
            count++;
        if (throttleController != null)
            count++;
        if (stepPolicy != null)
            count++;
        if (itemGovernor != null)
            count++;
        if (pathfindingGuard != null)
            count++;
        if (optimizer != null)
            count++;
        return count;
    }
}
