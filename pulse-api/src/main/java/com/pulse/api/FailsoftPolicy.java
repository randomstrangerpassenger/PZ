package com.pulse.api;

import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Pulse Failsoft Policy
 * 
 * Pulse/Echo/Fuse/Nerve 전체에서 공유하는 에러 처리 정책.
 * 비정상 상태 발생 시 통일된 방식으로 보고하고 대응합니다.
 * 
 * @since Pulse 0.9
 */
public final class FailsoftPolicy {

    private FailsoftPolicy() {
    }

    // ═══════════════════════════════════════════════════════════════
    // Failsoft Action 타입
    // ═══════════════════════════════════════════════════════════════

    /**
     * Failsoft 액션 타입
     */
    public enum Action {
        /**
         * Phase 시퀀스 에러 (startPhase 후 endPhase 누락)
         */
        PHASE_SEQUENCE_ERROR,

        /**
         * Tick 계약 위반 (비정상 deltaTime)
         */
        TICK_CONTRACT_VIOLATION,

        /**
         * Lua 예산 초과 (Fuse/Nerve용)
         */
        LUA_BUDGET_EXCEEDED,

        /**
         * 일반 경고 (치명적이지 않은 문제)
         */
        WARNING,

        /**
         * 치명적 에러 (기능 비활성화 필요)
         */
        CRITICAL
    }

    // ═══════════════════════════════════════════════════════════════
    // 에러 기록
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
    // 보고 API
    // ═══════════════════════════════════════════════════════════════

    /**
     * Failsoft 이슈 보고 (기본)
     * 
     * @param action 액션 타입
     * @param detail 상세 설명
     */
    public static void report(Action action, String detail) {
        report(action, detail, null);
    }

    /**
     * Failsoft 이슈 보고 (컨텍스트 포함)
     * 
     * @param action    액션 타입
     * @param detail    상세 설명
     * @param contextId 컨텍스트 ID (예: modId, phaseId)
     */
    public static void report(Action action, String detail, String contextId) {
        if (action == null || detail == null)
            return;

        // 카운터 증가
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

        // 레포트 저장 (최근 N개만)
        Report report = new Report(action, detail, contextId);
        recentReports.offer(report);
        while (recentReports.size() > MAX_REPORTS) {
            recentReports.poll();
        }

        // 콘솔 출력
        String level = (action == Action.CRITICAL) ? "ERROR" : "WARN";
        System.err.printf("[Pulse/Failsoft/%s] %s%n", level, report);
    }

    // ═══════════════════════════════════════════════════════════════
    // 조회 API
    // ═══════════════════════════════════════════════════════════════

    /**
     * 전체 보고 수
     */
    public static long getTotalReports() {
        return totalReports.get();
    }

    /**
     * Phase 시퀀스 에러 수
     */
    public static long getPhaseSequenceErrors() {
        return phaseSequenceErrors.get();
    }

    /**
     * Tick 계약 위반 수
     */
    public static long getTickContractViolations() {
        return tickContractViolations.get();
    }

    /**
     * Lua 예산 초과 수
     */
    public static long getLuaBudgetExceeded() {
        return luaBudgetExceeded.get();
    }

    /**
     * 치명적 에러 수
     */
    public static long getCriticalErrors() {
        return criticalErrors.get();
    }

    /**
     * 최근 보고 목록 (복사본)
     */
    public static Report[] getRecentReports() {
        return recentReports.toArray(new Report[0]);
    }

    /**
     * 상태가 안전한지 확인
     * 
     * @return 치명적 에러가 없으면 true
     */
    public static boolean isSafe() {
        return criticalErrors.get() == 0;
    }

    /**
     * 카운터 리셋
     */
    public static void reset() {
        recentReports.clear();
        totalReports.set(0);
        phaseSequenceErrors.set(0);
        tickContractViolations.set(0);
        luaBudgetExceeded.set(0);
        criticalErrors.set(0);
    }
}
