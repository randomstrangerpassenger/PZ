package com.fuse.area7.governor;

import com.fuse.area7.guard.NavMeshQueryGuard;
import com.fuse.area7.throttle.DuplicatePathRequestFilter;
import com.pulse.api.log.PulseLogger;

/**
 * 경로탐색 폭주 프로토콜.
 * 
 * <p>
 * Claude 제안 + ChatGPT 병합: 안전 사건 기반 트리거.
 * </p>
 * 
 * <h2>상태 머신</h2>
 * <ul>
 * <li>NORMAL: 정상 동작</li>
 * <li>GUARDED: 보수적 모드 (고정된 동작 세트)</li>
 * </ul>
 * 
 * <h2>안전 사건 기반 트리거</h2>
 * <ul>
 * <li>DeferQueue 오버플로우</li>
 * <li>연속 타임아웃 발생 (NavMesh 3회 이상)</li>
 * </ul>
 * 
 * @since Fuse 2.2
 */
public class PathfindingPanicProtocol {

    private static final String LOG = "Fuse";

    /**
     * 프로토콜 상태.
     */
    public enum State {
        /** 정상 */
        NORMAL,
        /** 보수적 모드 */
        GUARDED
    }

    private State state = State.NORMAL;
    private long stateEnteredTick;
    private long guardedDurationTicks;

    // 연결된 컴포넌트
    private final PathRequestDeferQueue deferQueue;
    private final NavMeshQueryGuard navMeshGuard;
    private final PathfindingBudgetGovernor budgetGovernor;
    private final DuplicatePathRequestFilter duplicateFilter;

    // 설정
    private static final long MIN_GUARDED_DURATION = 120; // 2초
    private static final int CONSECUTIVE_TIMEOUT_THRESHOLD = 3;

    public PathfindingPanicProtocol(
            PathRequestDeferQueue deferQueue,
            NavMeshQueryGuard navMeshGuard,
            PathfindingBudgetGovernor budgetGovernor,
            DuplicatePathRequestFilter duplicateFilter) {
        this.deferQueue = deferQueue;
        this.navMeshGuard = navMeshGuard;
        this.budgetGovernor = budgetGovernor;
        this.duplicateFilter = duplicateFilter;
    }

    /**
     * 틱마다 호출하여 안전 사건 검사.
     */
    public void checkSafetyEvents(long gameTick) {
        boolean shouldEnterGuarded = false;

        // 1. DeferQueue 오버플로우
        if (deferQueue.isOverflowing()) {
            shouldEnterGuarded = true;
        }

        // 2. 연속 타임아웃 발생
        if (navMeshGuard.getConsecutiveTimeouts() >= CONSECUTIVE_TIMEOUT_THRESHOLD) {
            shouldEnterGuarded = true;
        }

        // 상태 전환 결정
        if (shouldEnterGuarded && state == State.NORMAL) {
            transitionTo(State.GUARDED, gameTick);
        } else if (state == State.GUARDED) {
            // 최소 지속 시간 후 복구 검사
            long duration = gameTick - stateEnteredTick;
            if (duration >= MIN_GUARDED_DURATION && !shouldEnterGuarded) {
                transitionTo(State.NORMAL, gameTick);
            }
        }
    }

    /**
     * 상태 전환.
     */
    private void transitionTo(State newState, long gameTick) {
        if (state == newState)
            return;

        State oldState = state;
        state = newState;
        stateEnteredTick = gameTick;

        PulseLogger.info(LOG, "[PanicProtocol] State transition: {} -> {}", oldState, newState);

        if (newState == State.GUARDED) {
            applyGuardedMode();
        } else {
            removeGuardedMode();
        }
    }

    /**
     * Guarded Mode 적용.
     * 고정된 보수 동작 세트 (승수 조절 아님).
     */
    private void applyGuardedMode() {
        // 캐시 재사용 강화
        duplicateFilter.setStricterMatching(true);

        // 예산 보수 모드
        budgetGovernor.setConservativeMode(true);

        guardedDurationTicks = 0;
    }

    /**
     * Guarded Mode 해제.
     */
    private void removeGuardedMode() {
        duplicateFilter.setStricterMatching(false);
        budgetGovernor.setConservativeMode(false);
    }

    // ═══════════════════════════════════════════════════════════════
    // 상태 조회
    // ═══════════════════════════════════════════════════════════════

    public State getState() {
        return state;
    }

    public boolean isGuarded() {
        return state == State.GUARDED;
    }

    public long getGuardedDurationTicks() {
        return guardedDurationTicks;
    }

    /**
     * 강제 상태 리셋 (테스트/디버깅용).
     */
    public void forceReset() {
        state = State.NORMAL;
        removeGuardedMode();
    }
}
