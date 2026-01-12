package com.pulse.api.profiler;

/**
 * Profiler Sink Interface.
 * 
 * Pulse 경유로 profiler 데이터를 전달하기 위한 인터페이스.
 * 프로파일러가 구현하여 등록하면, 옵티마이저가 ProfilerBridge를 통해 데이터를 전달함.
 * 
 * Hub and Spoke 패턴: 옵티마이저 → Pulse → 프로파일러 (직접 의존 없음)
 * 
 * @since Pulse 1.1
 */
public interface ProfilerSink {

    /**
     * 좀비 step 타이밍 기록.
     * 
     * @param step           Step 이름 (MOTION_UPDATE, SOUND_PERCEPTION,
     *                       TARGET_TRACKING)
     * @param durationMicros 소요 시간 (microseconds)
     */
    void recordZombieStep(String step, long durationMicros);

    /**
     * 좀비 업데이트 카운트 증가.
     */
    void incrementZombieUpdates();
}
