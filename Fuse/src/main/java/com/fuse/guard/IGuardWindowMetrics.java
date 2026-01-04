package com.fuse.guard;

/**
 * Guard 윈도우 메트릭 통일 인터페이스.
 * 
 * Any guard that maintains rolling window stats can implement this interface.
 * Used for 60-second window aggregation in status summaries.
 * 
 * @since Fuse 2.2.0
 * @since Fuse 2.3.0 - IOGuard/GCPressureGuard implementations removed
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
