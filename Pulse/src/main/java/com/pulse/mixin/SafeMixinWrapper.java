package com.pulse.mixin;

import com.pulse.api.log.PulseLogger;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;

/**
 * Mixin 로직의 안전한 실행을 보장하는 래퍼.
 * 
 * Fuse 같은 딥 엔진 후킹 모드에서 발생할 수 있는 예외를 격리하여
 * 게임 전체 크래시를 방지합니다.
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * // 반환값이 없는 경우
 * SafeMixinWrapper.execute("IsoZombieMixin.update", () -> {
 *     // 위험할 수 있는 Mixin 로직
 * });
 * 
 * // 반환값이 있는 경우
 * int result = SafeMixinWrapper.executeWithReturn("SomeMixin.calc", () -> {
 *     return complexCalculation();
 * }, 0); // 실패 시 기본값 0 반환
 * }</pre>
 * 
 * @since Pulse 1.2
 */
public final class SafeMixinWrapper {

    private static final String LOG = PulseLogger.PULSE;

    // Mixin별 오류 카운터 (로그 스팸 방지)
    private static final Map<String, AtomicInteger> errorCounts = new ConcurrentHashMap<>();

    // 동일 오류 로그 제한 (최대 N번까지만 출력)
    private static final int MAX_ERROR_LOGS_PER_MIXIN = 5;

    // 디버그 모드 (모든 오류 출력)
    private static volatile boolean debugMode = false;

    private SafeMixinWrapper() {
        // Utility class
    }

    /**
     * Mixin 로직을 안전하게 실행 (반환값 없음)
     * 
     * @param mixinId Mixin 식별자 (예: "IsoZombieMixin.update")
     * @param logic   실행할 로직
     */
    public static void execute(String mixinId, Runnable logic) {
        try {
            logic.run();
        } catch (Throwable t) {
            handleError(mixinId, t);
        }
    }

    /**
     * Mixin 로직을 안전하게 실행 (반환값 있음)
     * 
     * @param mixinId  Mixin 식별자
     * @param logic    실행할 로직
     * @param fallback 실패 시 반환할 기본값
     * @return 로직 결과 또는 fallback
     */
    public static <T> T executeWithReturn(String mixinId, Supplier<T> logic, T fallback) {
        try {
            return logic.get();
        } catch (Throwable t) {
            handleError(mixinId, t);
            return fallback;
        }
    }

    /**
     * 조건부 Mixin 로직 실행
     * 
     * @param condition 실행 조건
     * @param mixinId   Mixin 식별자
     * @param logic     실행할 로직
     */
    public static void executeIf(boolean condition, String mixinId, Runnable logic) {
        if (condition) {
            execute(mixinId, logic);
        }
    }

    /**
     * 오류 처리
     */
    private static void handleError(String mixinId, Throwable t) {
        AtomicInteger counter = errorCounts.computeIfAbsent(mixinId, k -> new AtomicInteger(0));
        int count = counter.incrementAndGet();

        // 오류 보고
        PulseErrorHandler.reportMixinFailure(mixinId, t);

        // 로그 스팸 방지 (디버그 모드가 아닌 경우)
        if (debugMode || count <= MAX_ERROR_LOGS_PER_MIXIN) {
            PulseLogger.error(LOG, "Error in {} (#{})): {}", mixinId, count, t.getMessage());
            if (debugMode) {
                t.printStackTrace();
            }
        } else if (count == MAX_ERROR_LOGS_PER_MIXIN + 1) {
            PulseLogger.warn(LOG, "Suppressing further errors for {}", mixinId);
        }
    }

    /**
     * 특정 Mixin의 오류 카운터 리셋
     */
    public static void resetErrorCount(String mixinId) {
        errorCounts.remove(mixinId);
    }

    /**
     * 모든 Mixin 오류 카운터 리셋
     */
    public static void resetAllErrorCounts() {
        errorCounts.clear();
    }

    /**
     * 디버그 모드 설정
     */
    public static void setDebugMode(boolean enabled) {
        debugMode = enabled;
        if (enabled) {
            PulseLogger.info(LOG, "SafeMixin debug mode enabled - all errors will be printed");
        }
    }

    /**
     * 현재 오류 통계 반환
     */
    public static Map<String, Integer> getErrorStats() {
        Map<String, Integer> stats = new ConcurrentHashMap<>();
        errorCounts.forEach((k, v) -> stats.put(k, v.get()));
        return stats;
    }
}
