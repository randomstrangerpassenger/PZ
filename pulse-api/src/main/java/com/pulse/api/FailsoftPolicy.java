package com.pulse.api;

import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Pulse Failsoft Policy
 * 
 * Pulse/Echo/Fuse/Nerve 전체에서 공유하는 에러 처리 정책.
 * Mixin 실패, Lua 예산 초과 등의 오류가 발생해도 게임을 크래시하지 않고
 * 해당 기능만 비활성화합니다.
 * 
 * <pre>
 * // 사용 예시 (Pulse 내부)
 * try {
 *     // 위험한 작업
 * } catch (Exception e) {
 *     FailsoftPolicy.handle(FailsoftAction.WARN_AND_CONTINUE, "MyMod", e);
 * }
 * 
 * // 보고 전용 (외부 모드)
 * FailsoftPolicy.report(Action.WARNING, "Something happened");
 * </pre>
 * 
 * @since Pulse 0.9 / 1.1.0
 */
public final class FailsoftPolicy {

    private FailsoftPolicy() {
    }

    // ═══════════════════════════════════════════════════════════════
    // Failsoft Action 타입 (pulse-api용 - 보고 전용)
    // ═══════════════════════════════════════════════════════════════

    /**
     * Failsoft 액션 타입 (보고용)
     */
    public enum Action {
        /** Phase 시퀀스 에러 */
        PHASE_SEQUENCE_ERROR,
        /** Tick 계약 위반 */
        TICK_CONTRACT_VIOLATION,
        /** Lua 예산 초과 */
        LUA_BUDGET_EXCEEDED,
        /** 일반 경고 */
        WARNING,
        /** 치명적 에러 */
        CRITICAL
    }

    // ═══════════════════════════════════════════════════════════════
    // FailsoftAction (Pulse 내부용 - 처리 지시)
    // ═══════════════════════════════════════════════════════════════

    /**
     * Failsoft 액션 타입 (처리 지시용).
     */
    public enum FailsoftAction {
        /** 실패한 Mixin만 비활성화 */
        DISABLE_MIXIN_ONLY,
        /** 경고 로그 후 계속 */
        WARN_AND_CONTINUE,
        /** 해당 기능 스킵 */
        SKIP_FEATURE,
        /** 전체 기능 모듈 비활성화 */
        DISABLE_FEATURE,
        /** 페이즈 시퀀스 오류 */
        PHASE_SEQUENCE_ERROR,
        /** 안전하지 않은 월드 상태 접근 */
        UNSAFE_WORLDSTATE_ACCESS
    }

    // ═══════════════════════════════════════════════════════════════
    // 에러 기록 (pulse-api)
    // ═══════════════════════════════════════════════════════════════

    /**
     * Failsoft 보고 레코드
     */
    public static class Report {
        public final Action action;
        public final String detail;
        public final long timestamp;
        public final String contextId;

        public Report(Action action, String detail, String contextId) {
            this.action = action;
            this.detail = detail;
            this.timestamp = System.currentTimeMillis();
            this.contextId = contextId;
        }

        @Override
        public String toString() {
            return String.format("[%s] %s: %s", action, contextId != null ? contextId : "global", detail);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // 상태 관리
    // ═══════════════════════════════════════════════════════════════

    private static final int MAX_REPORTS = 100;
    private static final ConcurrentLinkedQueue<Report> recentReports = new ConcurrentLinkedQueue<>();

    private static final AtomicLong totalReports = new AtomicLong(0);
    private static final AtomicLong phaseSequenceErrors = new AtomicLong(0);
    private static final AtomicLong tickContractViolations = new AtomicLong(0);
    private static final AtomicLong luaBudgetExceeded = new AtomicLong(0);
    private static final AtomicLong criticalErrors = new AtomicLong(0);

    // ═══════════════════════════════════════════════════════════════
    // 보고 API (pulse-api - 외부 모드용)
    // ═══════════════════════════════════════════════════════════════

    /**
     * Failsoft 이슈 보고 (기본)
     */
    public static void report(Action action, String detail) {
        report(action, detail, null);
    }

    /**
     * Failsoft 이슈 보고 (컨텍스트 포함)
     */
    public static void report(Action action, String detail, String contextId) {
        if (action == null || detail == null)
            return;

        totalReports.incrementAndGet();
        switch (action) {
            case PHASE_SEQUENCE_ERROR:
                phaseSequenceErrors.incrementAndGet();
                break;
            case TICK_CONTRACT_VIOLATION:
                tickContractViolations.incrementAndGet();
                break;
            case LUA_BUDGET_EXCEEDED:
                luaBudgetExceeded.incrementAndGet();
                break;
            case CRITICAL:
                criticalErrors.incrementAndGet();
                break;
            default:
                break;
        }

        Report report = new Report(action, detail, contextId);
        recentReports.offer(report);
        while (recentReports.size() > MAX_REPORTS) {
            recentReports.poll();
        }

        String level = (action == Action.CRITICAL) ? "ERROR" : "WARN";
        System.err.printf("[Pulse/Failsoft/%s] %s%n", level, report);
    }

    // ═══════════════════════════════════════════════════════════════
    // 핵심 핸들러 (Pulse 내부용 - 스텁)
    // 실제 구현은 Pulse 프로젝트의 FailsoftPolicyImpl에서 제공
    // ═══════════════════════════════════════════════════════════════

    private static FailsoftHandler handler = null;

    /**
     * 핸들러 인터페이스 (Pulse에서 구현)
     */
    public interface FailsoftHandler {
        void handle(FailsoftAction action, String source, Throwable error);

        void handleMixinFailure(String mixinClass, String targetClass, Throwable error);
    }

    /**
     * 핸들러 등록 (Pulse 초기화 시 호출)
     */
    public static void registerHandler(FailsoftHandler h) {
        handler = h;
    }

    /**
     * Failsoft 액션 수행 (Pulse 내부용)
     */
    public static void handle(FailsoftAction action, String source, Throwable error) {
        if (handler != null) {
            handler.handle(action, source, error);
        } else {
            // 폴백: 콘솔 출력
            System.err.printf("[Pulse/Failsoft] %s: %s - %s%n",
                    action, source, error != null ? error.getMessage() : "Unknown");
        }
    }

    /**
     * Mixin 실패 처리
     */
    public static void handleMixinFailure(String mixinClass, String targetClass, Throwable error) {
        if (handler != null) {
            handler.handleMixinFailure(mixinClass, targetClass, error);
        } else {
            System.err.printf("[Pulse/Failsoft/Mixin] %s → %s FAILED: %s%n",
                    mixinClass, targetClass, error != null ? error.getMessage() : "Unknown");
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // 조회 API
    // ═══════════════════════════════════════════════════════════════

    public static long getTotalReports() {
        return totalReports.get();
    }

    public static long getPhaseSequenceErrors() {
        return phaseSequenceErrors.get();
    }

    public static long getTickContractViolations() {
        return tickContractViolations.get();
    }

    public static long getLuaBudgetExceeded() {
        return luaBudgetExceeded.get();
    }

    public static long getCriticalErrors() {
        return criticalErrors.get();
    }

    public static Report[] getRecentReports() {
        return recentReports.toArray(new Report[0]);
    }

    public static boolean isSafe() {
        return criticalErrors.get() == 0;
    }

    public static void reset() {
        recentReports.clear();
        totalReports.set(0);
        phaseSequenceErrors.set(0);
        tickContractViolations.set(0);
        luaBudgetExceeded.set(0);
        criticalErrors.set(0);
    }
}
