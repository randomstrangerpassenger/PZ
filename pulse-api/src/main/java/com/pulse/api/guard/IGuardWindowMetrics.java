package com.pulse.api.guard;

/**
 * Guard 윈도우 메트릭 통일 인터페이스.
 * 
 * Rolling window 통계를 관리하는 모든 Guard가 구현할 수 있습니다.
 * 60초 윈도우 집계를 위한 상태 요약에 사용됩니다.
 * 
 * <h2>구현 예시</h2>
 * 
 * <pre>{@code
 * public class MyGuard implements IGuardWindowMetrics {
 *     private int activeTicks = 0;
 *     private int hardActiveTicks = 0;
 *     private float minMult = 1.0f;
 * 
 *     public void recordTick(float multiplier, boolean forced) {
 *         if (multiplier < 1.0f || forced) {
 *             activeTicks++;
 *             if (forced || multiplier <= HARD_MULT_THRESHOLD) {
 *                 hardActiveTicks++;
 *             }
 *             minMult = Math.min(minMult, multiplier);
 *         }
 *     }
 * 
 *     // ... implement interface methods
 * }
 * }</pre>
 * 
 * @since Pulse 1.1.0
 */
public interface IGuardWindowMetrics {

    /**
     * HARD 판정 임계치.
     * forced=true 또는 mult <= 이 값이면 hardTicks로 카운트.
     */
    float HARD_MULT_THRESHOLD = 0.75f;

    /**
     * 이번 윈도우에서 ACTIVE 상태였던 총 틱 수.
     * 
     * @return 0 이상
     */
    int getActiveTicksThisWindow();

    /**
     * 이번 윈도우에서 HARD ACTIVE 상태였던 총 틱 수.
     * HARD 조건: forced=true 또는 mult <= HARD_MULT_THRESHOLD
     * 
     * @return 0 이상
     */
    int getHardActiveTicksThisWindow();

    /**
     * 이번 윈도우에서 최소 multiplier.
     * 
     * 갱신 규칙: min(previous, currentMultiplier)
     * 리셋 시: 1.0f로 복귀
     * ACTIVE가 없으면: 1.0f 유지
     * 
     * @return 0.0 ~ 1.0 (1.0 = 개입 없음)
     */
    float getMinMultThisWindow();

    /**
     * 윈도우 메트릭 리셋.
     * 60초 요약 출력 후 호출.
     */
    void resetWindowMetrics();
}
