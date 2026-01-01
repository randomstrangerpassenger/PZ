package com.pulse.api.profiler;

/**
 * 스로틀링 정책 인터페이스.
 * 
 * Pulse 플랫폼의 SPI로, 하위 최적화 모드(예: Fuse)가 구현합니다.
 * Pulse는 정책의 존재와 의미를 모르며, 단순히 boolean 또는 예산값만 받습니다.
 * 
 * <p>
 * 구현 예시 (하위 모드에서):
 * </p>
 * 
 * <pre>
 * public class FuseThrottlePolicy implements IThrottlePolicy {
 *     @Override
 *     public boolean shouldProcess(IHookContext ctx) {
 *         // Fuse 내부 로직으로 FULL/REDUCED/LOW 결정
 *         return myInternalLevel != SKIP;
 *     }
 * }
 * </pre>
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
     * 100 = 전체 허용 (FULL)
     * 50 = 절반만 허용
     * 0 = 완전 스킵
     * 
     * 기본 구현은 shouldProcess() 결과를 100 또는 0으로 변환.
     * 
     * @param context 실행 컨텍스트
     * @return 0-100 사이 예산값
     */
    default int getAllowedBudget(IHookContext context) {
        return shouldProcess(context) ? 100 : 0;
    }

    /**
     * 확장 컨텍스트 지원 여부.
     * 
     * 하위 모드가 더 많은 정보(거리, 공격 상태 등)를 전달하려면
     * IHookContext를 확장한 인터페이스 사용 가능.
     * 
     * @param contextClass 확장 컨텍스트 클래스
     * @return 지원 여부
     */
    default boolean supportsContext(Class<? extends IHookContext> contextClass) {
        return IHookContext.class.equals(contextClass);
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
