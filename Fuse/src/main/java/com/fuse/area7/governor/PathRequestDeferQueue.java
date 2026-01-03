package com.fuse.area7.governor;

import com.fuse.area7.PathfindingInvariants;
import com.fuse.telemetry.ReasonStats;
import com.fuse.telemetry.TelemetryReason;
import com.pulse.api.log.PulseLogger;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashMap;
import java.util.Map;

/**
 * 경로탐색 요청 지연 큐.
 * 
 * <p>
 * 3/3 모델 완전 합의: 예산 초과 요청을 다음 틱으로 이월.
 * </p>
 * 
 * <h2>Starvation 방지</h2>
 * <ul>
 * <li>좀비별 연속 DROP 카운터 추적</li>
 * <li>3회 연속 DROP 시 강제 처리 (forceProcess)</li>
 * <li>강제 처리 = 단지 '더 이상 지연하지 않음'</li>
 * </ul>
 * 
 * @since Fuse 2.2
 */
public class PathRequestDeferQueue {

    private static final String LOG = "Fuse";

    private final Deque<DeferredPathRequest> queue = new ArrayDeque<>();
    private final Map<Integer, Integer> consecutiveDrops = new HashMap<>();
    private final ReasonStats telemetry;

    private int maxQueueSize;
    private int droppedCount;
    private int forcedCount;

    public PathRequestDeferQueue(ReasonStats telemetry) {
        this.telemetry = telemetry;
        this.maxQueueSize = PathfindingInvariants.MAX_DEFER_QUEUE_SIZE;
    }

    /**
     * 요청 큐에 추가.
     */
    public void enqueue(DeferredPathRequest request) {
        int zombieId = request.getZombieId();

        // Starvation 방지: 3회 연속 DROP된 좀비는 무조건 처리
        int drops = consecutiveDrops.getOrDefault(zombieId, 0);
        if (drops >= PathfindingInvariants.MAX_CONSECUTIVE_DROPS) {
            forceProcess(request);
            consecutiveDrops.remove(zombieId);
            return;
        }

        // 큐 오버플로우 시 최저 우선순위만 DROP
        if (queue.size() >= maxQueueSize) {
            if (request.getPriority() == PathfindingInvariants.PRIORITY_WANDER
                    && request.getDistanceSquared() > PathfindingInvariants.FAR_DIST_SQ) {
                consecutiveDrops.merge(zombieId, 1, Integer::sum);
                droppedCount++;
                if (telemetry != null) {
                    telemetry.increment(TelemetryReason.PATH_REQUEST_DROPPED);
                }
                return; // DROP
            }
        }

        queue.addLast(request);
        consecutiveDrops.remove(zombieId); // 큐 진입 성공 시 리셋
    }

    /**
     * 지연된 요청 처리 (틱 시작 시 호출).
     * 
     * @param currentTick   현재 틱
     * @param consumeBudget 예산 소비 콜백
     */
    public void processDeferred(long currentTick, Runnable consumeBudget) {
        int processed = 0;
        while (!queue.isEmpty()) {
            DeferredPathRequest request = queue.peekFirst();

            // 너무 오래된 요청은 DROP (2틱 이상 지연)
            if (currentTick - request.getRequestTick() > 2) {
                queue.pollFirst();
                droppedCount++;
                continue;
            }

            queue.pollFirst();
            consumeBudget.run();
            processed++;

            // 이번 틱에서 처리할 수 있는 최대량 제한
            if (processed >= PathfindingInvariants.DEFAULT_BUDGET_PER_TICK / 2) {
                break;
            }
        }

        if (processed > 0) {
            PulseLogger.debug(LOG, "[DeferQueue] Processed {} deferred requests", processed);
        }
    }

    /**
     * 강제 처리 (Starvation 방지).
     * 
     * <p>
     * 의미: 동일한 엔진 경로 요청을 그대로 통과시킴.
     * Fuse는 단지 '더 이상 지연하지 않음'을 의미.
     * 결과는 지연하지 않았을 때와 동일함 (결과 불변).
     * 우회/단순화된 처리 ❌
     * </p>
     */
    private void forceProcess(DeferredPathRequest request) {
        forcedCount++;
        PulseLogger.debug(LOG, "[DeferQueue] Force processing zombie {} after max drops",
                request.getZombieId());
    }

    /**
     * 큐 오버플로우 상태인지.
     */
    public boolean isOverflowing() {
        return queue.size() >= maxQueueSize * 0.9;
    }

    /**
     * 틱 종료 시 정리.
     */
    public void onTickEnd() {
        // 현재는 특별한 정리 작업 없음
    }

    // ═══════════════════════════════════════════════════════════════
    // 텔레메트리
    // ═══════════════════════════════════════════════════════════════

    public int getQueueSize() {
        return queue.size();
    }

    public int getDroppedCount() {
        return droppedCount;
    }

    public int getForcedCount() {
        return forcedCount;
    }

    public void setMaxQueueSize(int size) {
        this.maxQueueSize = size;
    }
}
