package com.pulse.api.profiler;

/**
 * SubProfiler Hook API
 * 
 * Echo의 SubProfiler를 Pulse Mixin에서 호출하기 위한 인터페이스.
 * Echo가 로드되지 않은 환경에서도 안전하게 동작합니다.
 * 
 * @since Pulse 1.1 / Echo 1.0
 */
public final class SubProfilerHook {

    private static volatile ISubProfilerCallback callback = null;

    private SubProfilerHook() {
    }

    /**
     * 콜백 등록 (Echo 초기화 시 호출됨)
     */
    public static void setCallback(ISubProfilerCallback cb) {
        callback = cb;
        System.out.println("[Pulse/SubProfilerHook] Callback registered: " + (cb != null));
    }

    /**
     * 콜백 해제
     */
    public static void clearCallback() {
        callback = null;
    }

    /**
     * SubTiming 측정 시작
     * 
     * @param label SubLabel 이름 (예: "ZOMBIE_UPDATE", "PATHFINDING")
     * @return 시작 시간 (나노초), 비활성화 시 -1
     */
    public static long start(String label) {
        ISubProfilerCallback cb = callback;
        if (cb != null) {
            return cb.start(label);
        }
        return -1;
    }

    /**
     * SubTiming 측정 종료
     * 
     * @param label     SubLabel 이름
     * @param startTime start()에서 반환받은 시작 시간
     */
    public static void end(String label, long startTime) {
        if (startTime < 0)
            return;
        ISubProfilerCallback cb = callback;
        if (cb != null) {
            cb.end(label, startTime);
        }
    }

    /**
     * SubProfiler 콜백 인터페이스
     */
    public interface ISubProfilerCallback {
        long start(String label);

        void end(String label, long startTime);
    }
}
