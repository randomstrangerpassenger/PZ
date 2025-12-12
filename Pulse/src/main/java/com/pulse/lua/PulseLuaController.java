package com.pulse.lua;

import com.pulse.api.log.PulseLogger;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Lua 실행 제어 및 샌드박스 관리.
 * 
 * Nerve 최적화에 필요한 기능들을 제공합니다:
 * - Lua 콜백 호출 시간 제한 (budget)
 * - 과도한 UI/Lua 이벤트 차단
 * - 비싼 함수 throttle/skip 결정
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * // 실행 시간 제한 설정 (밀리초)
 * PulseLuaController.setBudget(50);
 * 
 * // 특정 함수 차단
 * PulseLuaController.blockFunction("ISInventoryPane:refreshBackground");
 * 
 * // 이벤트 모니터링
 * PulseLuaController.monitorLuaEvent("OnTick");
 * }</pre>
 * 
 * @since Pulse 1.2
 */
public final class PulseLuaController {

    // 기본 예산 (밀리초)
    private static final long DEFAULT_BUDGET_MS = 100;
    private static final String LOG = PulseLogger.PULSE;

    // 현재 예산
    private static volatile long budgetMs = DEFAULT_BUDGET_MS;

    // 차단된 함수 목록
    private static final Set<String> blockedFunctions = ConcurrentHashMap.newKeySet();

    // Throttle 대상 함수 (호출 간격 제한)
    private static final Map<String, ThrottleConfig> throttledFunctions = new ConcurrentHashMap<>();

    // 모니터링 대상 이벤트
    private static final Set<String> monitoredEvents = ConcurrentHashMap.newKeySet();

    // 이벤트별 호출 통계
    private static final Map<String, LuaEventStats> eventStats = new ConcurrentHashMap<>();

    // 글로벌 활성화 상태
    private static volatile boolean enabled = true;

    // 로깅 활성화
    private static volatile boolean loggingEnabled = false;

    private PulseLuaController() {
    }

    // ─────────────────────────────────────────────────────────────
    // Budget 관리
    // ─────────────────────────────────────────────────────────────

    /**
     * Lua 실행 예산 설정 (밀리초)
     * 
     * @param ms 최대 실행 시간 (밀리초)
     */
    public static void setBudget(long ms) {
        if (ms <= 0) {
            throw new IllegalArgumentException("Budget must be positive");
        }
        budgetMs = ms;
        if (loggingEnabled) {
            PulseLogger.info(LOG, "[LuaController] Budget set to {}ms", ms);
        }
    }

    /**
     * 현재 예산 조회
     */
    public static long getBudget() {
        return budgetMs;
    }

    /**
     * 예산 초과 여부 확인
     * 
     * @param elapsedMs 경과 시간 (밀리초)
     * @return 예산 초과 시 true
     */
    public static boolean isBudgetExceeded(long elapsedMs) {
        return elapsedMs > budgetMs;
    }

    // ─────────────────────────────────────────────────────────────
    // 함수 차단
    // ─────────────────────────────────────────────────────────────

    /**
     * 함수 차단
     * 
     * @param funcName 차단할 함수 이름 (예: "ISInventoryPane:refreshBackground")
     */
    public static void blockFunction(String funcName) {
        if (funcName != null && !funcName.isEmpty()) {
            blockedFunctions.add(funcName);
            if (loggingEnabled) {
                PulseLogger.info(LOG, "[LuaController] Blocked function: {}", funcName);
            }
        }
    }

    /**
     * 함수 차단 해제
     */
    public static void unblockFunction(String funcName) {
        blockedFunctions.remove(funcName);
    }

    /**
     * 함수 차단 여부 확인
     */
    public static boolean isBlocked(String funcName) {
        return enabled && blockedFunctions.contains(funcName);
    }

    /**
     * 차단된 함수 목록
     */
    public static Set<String> getBlockedFunctions() {
        return new HashSet<>(blockedFunctions);
    }

    // ─────────────────────────────────────────────────────────────
    // 함수 Throttle (호출 빈도 제한)
    // ─────────────────────────────────────────────────────────────

    /**
     * 함수 호출 빈도 제한
     * 
     * @param funcName   함수 이름
     * @param intervalMs 최소 호출 간격 (밀리초)
     */
    public static void throttleFunction(String funcName, long intervalMs) {
        throttledFunctions.put(funcName, new ThrottleConfig(intervalMs));
    }

    /**
     * Throttle 해제
     */
    public static void unthrottleFunction(String funcName) {
        throttledFunctions.remove(funcName);
    }

    /**
     * 함수 호출 허용 여부 확인 (Throttle 체크)
     * 
     * @param funcName 함수 이름
     * @return 호출 허용 시 true
     */
    public static boolean shouldAllow(String funcName) {
        if (!enabled)
            return true;
        if (isBlocked(funcName))
            return false;

        ThrottleConfig config = throttledFunctions.get(funcName);
        if (config == null)
            return true;

        long now = System.currentTimeMillis();
        if (now - config.lastCallTime < config.intervalMs) {
            config.skippedCount.incrementAndGet();
            return false;
        }

        config.lastCallTime = now;
        return true;
    }

    // ─────────────────────────────────────────────────────────────
    // 이벤트 모니터링
    // ─────────────────────────────────────────────────────────────

    /**
     * Lua 이벤트 모니터링 등록
     * 
     * @param eventName 이벤트 이름 (예: "OnTick", "OnRenderTick")
     */
    public static void monitorLuaEvent(String eventName) {
        if (eventName != null && !eventName.isEmpty()) {
            monitoredEvents.add(eventName);
            eventStats.computeIfAbsent(eventName, k -> new LuaEventStats());
            if (loggingEnabled) {
                PulseLogger.info(LOG, "[LuaController] Monitoring event: {}", eventName);
            }
        }
    }

    /**
     * 이벤트 모니터링 해제
     */
    public static void unmonitorLuaEvent(String eventName) {
        monitoredEvents.remove(eventName);
    }

    /**
     * 이벤트 호출 기록
     * 
     * @param eventName     이벤트 이름
     * @param durationNanos 소요 시간 (나노초)
     */
    public static void recordEventCall(String eventName, long durationNanos) {
        if (!enabled || !monitoredEvents.contains(eventName))
            return;

        LuaEventStats stats = eventStats.get(eventName);
        if (stats != null) {
            stats.record(durationNanos);
        }
    }

    /**
     * 이벤트 통계 조회
     */
    public static Map<String, LuaEventStats> getEventStats() {
        return new HashMap<>(eventStats);
    }

    // ─────────────────────────────────────────────────────────────
    // 글로벌 제어
    // ─────────────────────────────────────────────────────────────

    /**
     * 컨트롤러 활성화/비활성화
     */
    public static void setEnabled(boolean enabled) {
        PulseLuaController.enabled = enabled;
    }

    public static boolean isEnabled() {
        return enabled;
    }

    /**
     * 로깅 활성화
     */
    public static void setLoggingEnabled(boolean enabled) {
        loggingEnabled = enabled;
    }

    /**
     * 모든 설정 초기화
     */
    public static void reset() {
        budgetMs = DEFAULT_BUDGET_MS;
        blockedFunctions.clear();
        throttledFunctions.clear();
        monitoredEvents.clear();
        eventStats.clear();
    }

    /**
     * 상태 요약
     */
    public static String getStatusSummary() {
        StringBuilder sb = new StringBuilder();
        sb.append("PulseLuaController Status:\n");
        sb.append("  Enabled: ").append(enabled).append("\n");
        sb.append("  Budget: ").append(budgetMs).append("ms\n");
        sb.append("  Blocked Functions: ").append(blockedFunctions.size()).append("\n");
        sb.append("  Throttled Functions: ").append(throttledFunctions.size()).append("\n");
        sb.append("  Monitored Events: ").append(monitoredEvents.size()).append("\n");
        return sb.toString();
    }

    // ─────────────────────────────────────────────────────────────
    // 내부 클래스
    // ─────────────────────────────────────────────────────────────

    /**
     * Throttle 설정
     */
    private static class ThrottleConfig {
        final long intervalMs;
        volatile long lastCallTime = 0;
        final AtomicLong skippedCount = new AtomicLong(0);

        ThrottleConfig(long intervalMs) {
            this.intervalMs = intervalMs;
        }
    }

    /**
     * Lua 이벤트 통계
     */
    public static class LuaEventStats {
        private final AtomicLong callCount = new AtomicLong(0);
        private final AtomicLong totalNanos = new AtomicLong(0);
        private volatile long maxNanos = 0;

        void record(long nanos) {
            callCount.incrementAndGet();
            totalNanos.addAndGet(nanos);
            if (nanos > maxNanos)
                maxNanos = nanos;
        }

        public long getCallCount() {
            return callCount.get();
        }

        public long getTotalNanos() {
            return totalNanos.get();
        }

        public long getMaxNanos() {
            return maxNanos;
        }

        public double getAverageMs() {
            long c = callCount.get();
            return c > 0 ? (totalNanos.get() / c) / 1_000_000.0 : 0;
        }

        @Override
        public String toString() {
            return String.format("calls=%d, avg=%.3fms, max=%.3fms",
                    callCount.get(), getAverageMs(), maxNanos / 1_000_000.0);
        }
    }
}
