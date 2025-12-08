package com.echo.lua;

import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.LongAdder;

/**
 * Lua 예산 관리자
 * 
 * Lua 스크립트 실행 시간을 예산 내에서 관리합니다.
 * 프레임당 할당된 Lua 예산과 실제 사용량을 추적합니다.
 */
public class LuaBudgetManager {

    private static final LuaBudgetManager INSTANCE = new LuaBudgetManager();

    // 기본 예산: 5ms (프레임당)
    private static final double DEFAULT_BUDGET_MS = 5.0;

    // 현재 예산 (밀리초)
    private volatile double budgetMs = DEFAULT_BUDGET_MS;

    // 현재 프레임 누적
    private final ThreadLocal<Long> frameStartMicros = ThreadLocal.withInitial(() -> 0L);
    private final ThreadLocal<Long> frameUsedMicros = ThreadLocal.withInitial(() -> 0L);

    // 전체 통계
    private final LongAdder totalUsedMicros = new LongAdder();
    private final LongAdder totalFrames = new LongAdder();
    private final LongAdder exceededCount = new LongAdder();
    private final AtomicLong maxUsedMicros = new AtomicLong(0);

    private LuaBudgetManager() {
    }

    public static LuaBudgetManager getInstance() {
        return INSTANCE;
    }

    // ============================================================
    // 프레임 라이프사이클
    // ============================================================

    /**
     * 프레임 시작 시 호출
     * 프레임당 Lua 예산 추적을 시작합니다.
     */
    public void beginFrame() {
        frameStartMicros.set(System.nanoTime() / 1000);
        frameUsedMicros.set(0L);
    }

    /**
     * Lua 실행 시간 추가
     * 
     * @param durationMicros 실행 시간 (마이크로초)
     */
    public void addUsage(long durationMicros) {
        frameUsedMicros.set(frameUsedMicros.get() + durationMicros);
    }

    /**
     * 프레임 종료 시 호출
     * 예산 초과 여부를 체크하고 통계를 업데이트합니다.
     */
    public void endFrame() {
        long used = frameUsedMicros.get();

        // 통계 업데이트
        totalUsedMicros.add(used);
        totalFrames.increment();

        // 최대값 업데이트
        long currentMax;
        do {
            currentMax = maxUsedMicros.get();
            if (used <= currentMax)
                break;
        } while (!maxUsedMicros.compareAndSet(currentMax, used));

        // 예산 초과 체크
        if (used > budgetMs * 1000) {
            exceededCount.increment();
        }
    }

    // ============================================================
    // 예산 설정
    // ============================================================

    /**
     * 예산 설정 (밀리초)
     * 
     * @param ms 프레임당 Lua 예산 (밀리초)
     */
    public void setBudgetMs(double ms) {
        this.budgetMs = Math.max(1.0, ms);
    }

    /**
     * 현재 예산 조회
     * 
     * @return 프레임당 Lua 예산 (밀리초)
     */
    public double getBudgetMs() {
        return budgetMs;
    }

    // ============================================================
    // 현재 상태 조회
    // ============================================================

    /**
     * 현재 프레임 사용량 조회
     * 
     * @return 현재 프레임 Lua 사용량 (밀리초)
     */
    public double getCurrentUsageMs() {
        return frameUsedMicros.get() / 1000.0;
    }

    /**
     * 현재 프레임 예산 사용률 조회
     * 
     * @return 예산 사용률 (0-100+%)
     */
    public double getCurrentUsagePercent() {
        return (getCurrentUsageMs() / budgetMs) * 100.0;
    }

    /**
     * 현재 프레임 예산 초과 여부
     * 
     * @return 초과 여부
     */
    public boolean isCurrentFrameExceeded() {
        return getCurrentUsageMs() > budgetMs;
    }

    // ============================================================
    // 통계 조회
    // ============================================================

    /**
     * 평균 사용량 조회
     * 
     * @return 프레임당 평균 Lua 사용량 (밀리초)
     */
    public double getAverageUsageMs() {
        long frames = totalFrames.sum();
        if (frames == 0)
            return 0;
        return (totalUsedMicros.sum() / 1000.0) / frames;
    }

    /**
     * 최대 사용량 조회
     * 
     * @return 최대 Lua 사용량 (밀리초)
     */
    public double getMaxUsageMs() {
        return maxUsedMicros.get() / 1000.0;
    }

    /**
     * 예산 초과 횟수 조회
     * 
     * @return 예산 초과 횟수
     */
    public long getExceededCount() {
        return exceededCount.sum();
    }

    /**
     * 예산 초과 비율 조회
     * 
     * @return 예산 초과 비율 (0-100%)
     */
    public double getExceededPercent() {
        long frames = totalFrames.sum();
        if (frames == 0)
            return 0;
        return (exceededCount.sum() * 100.0) / frames;
    }

    /**
     * 총 프레임 수 조회
     * 
     * @return 총 프레임 수
     */
    public long getTotalFrames() {
        return totalFrames.sum();
    }

    // ============================================================
    // 스냅샷
    // ============================================================

    /**
     * 현재 상태 스냅샷 생성
     * 
     * @return LuaBudgetSnapshot
     */
    public LuaBudgetSnapshot snapshot() {
        return new LuaBudgetSnapshot(
                getAverageUsageMs(),
                budgetMs,
                exceededCount.sum(),
                getMaxUsageMs(),
                totalFrames.sum());
    }

    // ============================================================
    // 초기화
    // ============================================================

    /**
     * 통계 초기화
     */
    public void reset() {
        totalUsedMicros.reset();
        totalFrames.reset();
        exceededCount.reset();
        maxUsedMicros.set(0);
        frameUsedMicros.set(0L);
    }

    // ============================================================
    // 스냅샷 레코드
    // ============================================================

    /**
     * Lua 예산 상태 스냅샷
     * 
     * @param actualMs      평균 실제 사용량 (밀리초)
     * @param budgetMs      예산 (밀리초)
     * @param exceededCount 예산 초과 횟수
     * @param maxMs         최대 사용량 (밀리초)
     * @param totalFrames   총 프레임 수
     */
    public record LuaBudgetSnapshot(
            double actualMs,
            double budgetMs,
            long exceededCount,
            double maxMs,
            long totalFrames) {
        /**
         * 예산 사용률 (%)
         */
        public double usagePercent() {
            return budgetMs > 0 ? (actualMs / budgetMs) * 100 : 0;
        }

        /**
         * 예산 초과 여부
         */
        public boolean isExceeded() {
            return actualMs > budgetMs;
        }

        /**
         * 예산 초과 비율 (%)
         */
        public double exceededPercent() {
            return totalFrames > 0 ? (exceededCount * 100.0) / totalFrames : 0;
        }

        /**
         * 상태 문자열
         */
        public String statusString() {
            return String.format("%.1fms / %.1fms (%.0f%%)", actualMs, budgetMs, usagePercent());
        }
    }
}
