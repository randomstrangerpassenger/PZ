package com.fuse.area7.guard;

import com.fuse.area7.PathfindingInvariants;
import com.pulse.api.log.PulseLogger;

import java.util.function.Supplier;

/**
 * NavMesh 쿼리 가드.
 * 
 * <p>
 * Gemini 단독 제안 (채택): 경로탐색 무한루프/타임아웃 방어.
 * </p>
 * 
 * <h2>매커니즘</h2>
 * <ul>
 * <li>쿼리 시간 측정</li>
 * <li>50ms 초과 시 경고</li>
 * <li>100ms 초과 시 Silent Fail (DEFER)</li>
 * <li>Exception 던지지 않음</li>
 * </ul>
 * 
 * @since Fuse 2.2
 */
public class NavMeshQueryGuard {

    private static final String LOG = "Fuse";

    private int consecutiveTimeouts;
    private int totalTimeouts;
    private int totalWarnings;

    /**
     * 쿼리 실행 결과.
     */
    public enum QueryResult {
        /** 정상 완료 */
        SUCCESS,
        /** 경고 (50ms 초과) */
        WARNING,
        /** 타임아웃 (100ms 초과) - DEFER 권장 */
        TIMEOUT
    }

    /**
     * 경로탐색 쿼리 래핑.
     * 
     * @param computation 실제 경로탐색 연산
     * @param <T>         결과 타입
     * @return 결과 또는 null (타임아웃 시)
     */
    public <T> GuardedResult<T> guard(Supplier<T> computation) {
        long startNanos = System.nanoTime();

        T result = computation.get();

        long elapsedMs = (System.nanoTime() - startNanos) / 1_000_000;

        if (elapsedMs > PathfindingInvariants.NAVMESH_TIMEOUT_MS) {
            consecutiveTimeouts++;
            totalTimeouts++;

            // Silent Fail: 예외 던지지 않음
            PulseLogger.warn(LOG, "[NavMesh] Query timeout: {}ms", elapsedMs);

            return new GuardedResult<>(null, QueryResult.TIMEOUT, elapsedMs);
        }

        // 타임아웃 아니면 연속 카운터 리셋
        consecutiveTimeouts = 0;

        if (elapsedMs > PathfindingInvariants.NAVMESH_WARNING_MS) {
            totalWarnings++;
            PulseLogger.debug(LOG, "[NavMesh] Query slow: {}ms", elapsedMs);
            return new GuardedResult<>(result, QueryResult.WARNING, elapsedMs);
        }

        return new GuardedResult<>(result, QueryResult.SUCCESS, elapsedMs);
    }

    /**
     * 연속 타임아웃 횟수.
     * PanicProtocol에서 사용.
     */
    public int getConsecutiveTimeouts() {
        return consecutiveTimeouts;
    }

    public int getTotalTimeouts() {
        return totalTimeouts;
    }

    public int getTotalWarnings() {
        return totalWarnings;
    }

    public void resetTelemetry() {
        totalTimeouts = 0;
        totalWarnings = 0;
        consecutiveTimeouts = 0;
    }

    /**
     * 가드된 결과 래퍼.
     */
    public static class GuardedResult<T> {
        private final T result;
        private final QueryResult status;
        private final long elapsedMs;

        public GuardedResult(T result, QueryResult status, long elapsedMs) {
            this.result = result;
            this.status = status;
            this.elapsedMs = elapsedMs;
        }

        public T getResult() {
            return result;
        }

        public QueryResult getStatus() {
            return status;
        }

        public long getElapsedMs() {
            return elapsedMs;
        }

        public boolean isTimeout() {
            return status == QueryResult.TIMEOUT;
        }
    }
}
