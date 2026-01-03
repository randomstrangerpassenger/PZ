package com.fuse.area7;

import com.fuse.area7.cache.FrameLocalCollisionMemo;
import com.fuse.area7.governor.PathfindingBudgetGovernor;
import com.fuse.area7.governor.PathfindingPanicProtocol;
import com.fuse.area7.governor.PathRequestDeferQueue;
import com.fuse.area7.guard.NavMeshQueryGuard;
import com.fuse.area7.guard.PhysicsVelocityClamp;
import com.fuse.area7.throttle.DuplicatePathRequestFilter;
import com.fuse.telemetry.ReasonStats;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.spi.IPathfindingContext;
import com.pulse.api.spi.IPathfindingGuard;

/**
 * Fuse Area 7 통합 가드.
 * 
 * <p>
 * IPathfindingGuard SPI 구현체.
 * </p>
 * 
 * <p>
 * 모든 Area 7 컴포넌트를 통합하여 경로탐색 요청 검사 수행.
 * Pulse의 PathfindingHook에 등록되어 경로탐색 요청마다 호출됨.
 * </p>
 * 
 * @since Fuse 2.2
 */
public class FusePathfindingGuard implements IPathfindingGuard {

    private static final String LOG = "Fuse";

    // 컴포넌트
    private final PathRequestDeferQueue deferQueue;
    private final PathfindingBudgetGovernor budgetGovernor;
    private final DuplicatePathRequestFilter duplicateFilter;
    private final NavMeshQueryGuard navMeshGuard;
    private final PhysicsVelocityClamp physicsClamp;
    private final FrameLocalCollisionMemo collisionMemo;
    private final PathfindingPanicProtocol panicProtocol;

    private boolean enabled = true;

    public FusePathfindingGuard(ReasonStats telemetry) {
        // 컴포넌트 초기화
        this.deferQueue = new PathRequestDeferQueue(telemetry);
        this.budgetGovernor = new PathfindingBudgetGovernor(deferQueue);
        this.duplicateFilter = new DuplicatePathRequestFilter();
        this.navMeshGuard = new NavMeshQueryGuard();
        this.physicsClamp = new PhysicsVelocityClamp(telemetry);
        this.collisionMemo = new FrameLocalCollisionMemo();
        this.panicProtocol = new PathfindingPanicProtocol(
                deferQueue, navMeshGuard, budgetGovernor, duplicateFilter);

        PulseLogger.info(LOG, "[Area7] FusePathfindingGuard initialized");
    }

    /**
     * Area 7 활성화.
     * 
     * Note: PathfindingHook.setGuard() 통합은 빌드 문제로 인해
     * 향후 버전에서 구현 예정. 현재는 EventBus 기반 틱 리스너 사용.
     */
    public void register() {
        // TODO: PathfindingHook.setGuard(this) - 빌드 문제 해결 후 활성화
        PulseLogger.info(LOG, "[Area7] FusePathfindingGuard active (EventBus mode)");
    }

    /**
     * Area 7 비활성화.
     */
    public void unregister() {
        // TODO: PathfindingHook.setGuard(null) - 빌드 문제 해결 후 활성화
        PulseLogger.info(LOG, "[Area7] FusePathfindingGuard deactivated");
    }

    // ═══════════════════════════════════════════════════════════════
    // IPathfindingGuard 구현
    // ═══════════════════════════════════════════════════════════════

    @Override
    public boolean checkPathRequest(IPathfindingContext context) {
        if (!enabled) {
            return true; // 비활성화 시 통과
        }

        // 1. 중복 요청 필터
        if (duplicateFilter.isDuplicate(
                context.getZombieId(),
                context.getTargetX(),
                context.getTargetY())) {
            return true; // 중복이면 처리된 것으로 간주
        }

        // 2. 예산 검사 (COMBAT 우선 허용, 예산 초과 시 defer)
        return budgetGovernor.checkRequest(context);
    }

    @Override
    public void onTickStart(long gameTick) {
        if (!enabled)
            return;

        // 틱 시작 시 컴포넌트 초기화
        duplicateFilter.onTickStart(gameTick);
        collisionMemo.onTickStart(gameTick);
        budgetGovernor.onTickStart(gameTick);
    }

    @Override
    public void onTickEnd(long gameTick) {
        if (!enabled)
            return;

        // PanicProtocol 검사
        panicProtocol.checkSafetyEvents(gameTick);

        // 틱 종료 시 정리
        duplicateFilter.onTickEnd();
        collisionMemo.onTickEnd(); // TTL=1틱 엄수
        deferQueue.onTickEnd();
    }

    // ═══════════════════════════════════════════════════════════════
    // 설정
    // ═══════════════════════════════════════════════════════════════

    public boolean isEnabled() {
        return enabled;
    }

    // ═══════════════════════════════════════════════════════════════
    // 컴포넌트 접근자
    // ═══════════════════════════════════════════════════════════════

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public PathfindingBudgetGovernor getBudgetGovernor() {
        return budgetGovernor;
    }

    public PathRequestDeferQueue getDeferQueue() {
        return deferQueue;
    }

    public DuplicatePathRequestFilter getDuplicateFilter() {
        return duplicateFilter;
    }

    public NavMeshQueryGuard getNavMeshGuard() {
        return navMeshGuard;
    }

    public PhysicsVelocityClamp getPhysicsClamp() {
        return physicsClamp;
    }

    public FrameLocalCollisionMemo getCollisionMemo() {
        return collisionMemo;
    }

    public PathfindingPanicProtocol getPanicProtocol() {
        return panicProtocol;
    }

    /**
     * 60초 상태 요약 로깅.
     */
    public void logStatusSummary() {
        PulseLogger.info(LOG, "");
        PulseLogger.info(LOG, "╔═══════════════════════════════════════════╗");
        PulseLogger.info(LOG, "║        AREA 7 STATUS (60s Summary)        ║");
        PulseLogger.info(LOG, "╚═══════════════════════════════════════════╝");
        PulseLogger.info(LOG, "  Budget Governor:");
        PulseLogger.info(LOG, "    Total Requests:    {}", budgetGovernor.getTotalRequests());
        PulseLogger.info(LOG, "    Deferred:          {}", budgetGovernor.getDeferredRequests());
        PulseLogger.info(LOG, "    Combat Bypass:     {}", budgetGovernor.getCombatBypassCount());
        PulseLogger.info(LOG, "  Defer Queue:");
        PulseLogger.info(LOG, "    Current Size:      {}", deferQueue.getQueueSize());
        PulseLogger.info(LOG, "    Dropped:           {}", deferQueue.getDroppedCount());
        PulseLogger.info(LOG, "  Duplicate Filter:");
        PulseLogger.info(LOG, "    Duplicates:        {}", duplicateFilter.getDuplicatesFiltered());
        PulseLogger.info(LOG, "  Panic Protocol:");
        PulseLogger.info(LOG, "    State:             {}", panicProtocol.getState());
        PulseLogger.info(LOG, "");

        // 텔레메트리 리셋
        budgetGovernor.resetTelemetry();
        duplicateFilter.resetTelemetry();
        navMeshGuard.resetTelemetry();
        physicsClamp.resetTelemetry();
        collisionMemo.resetTelemetry();
    }
}
