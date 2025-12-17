package com.pulse.api.profiler;

/**
 * Profiler Bridge - Pulse 경유 profiler 데이터 전달.
 * 
 * Fuse가 이 Bridge를 통해 데이터를 보내면,
 * Echo가 등록한 ProfilerSink로 전달됨.
 * 
 * Failsoft: Sink가 없으면 noop.
 * 
 * @since Pulse 1.1
 */
public final class ProfilerBridge {

    private static ProfilerSink sink;

    private ProfilerBridge() {
    }

    /**
     * Sink 등록 (Echo 초기화 시 호출).
     */
    public static void setSink(ProfilerSink s) {
        sink = s;
        if (s != null) {
            System.out.println("[Pulse] ProfilerSink registered");
        }
    }

    /**
     * Sink 해제.
     */
    public static void clearSink() {
        sink = null;
    }

    /**
     * Sink 등록 여부.
     */
    public static boolean hasSink() {
        return sink != null;
    }

    /**
     * 좀비 step 타이밍 기록 (Fuse에서 호출).
     * 
     * @param step           Step 이름
     * @param durationMicros 소요 시간 (microseconds)
     */
    public static void recordZombieStep(String step, long durationMicros) {
        if (sink != null) {
            try {
                sink.recordZombieStep(step, durationMicros);
            } catch (Throwable t) {
                // Failsoft: 무시하고 게임 진행
            }
        }
    }

    /**
     * 좀비 업데이트 카운트 증가 (Fuse에서 호출).
     */
    public static void incrementZombieUpdates() {
        if (sink != null) {
            try {
                sink.incrementZombieUpdates();
            } catch (Throwable t) {
                // Failsoft
            }
        }
    }
}
