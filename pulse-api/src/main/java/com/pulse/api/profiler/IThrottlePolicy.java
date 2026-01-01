package com.pulse.api.profiler;

/**
 * 스로틀링 정책 인터페이스.
 * 
 * Pulse 플랫폼의 SPI로, 하위 최적화 모드가 구현합니다.
 * Pulse는 정책의 존재와 의미를 모르며, 단순히 boolean 또는 예산값만 받습니다.
 * 
 * @since Pulse 2.0
 */
public interface IThrottlePolicy {

    /**
     * 주어진 컨텍스트에서 처리를 진행해야 하는지 결정.
     * 
     * @param context 실행 컨텍스트
     * @return true면 처리, false면 스킵
     */
    boolean shouldProcess(IHookContext context);

    /**
     * 허용 예산 반환 (0-100).
     * 
     * @param context 실행 컨텍스트
     * @return 0-100 사이 예산값
     */
    default int getAllowedBudget(IHookContext context) {
        return shouldProcess(context) ? 100 : 0;
    }

    /**
     * 정책 없음 (항상 처리).
     */
    IThrottlePolicy ALWAYS_PROCESS = ctx -> true;

    /**
     * 정책 없음 (항상 스킵).
     */
    IThrottlePolicy ALWAYS_SKIP = ctx -> false;
}
