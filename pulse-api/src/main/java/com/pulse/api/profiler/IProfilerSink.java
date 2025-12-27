package com.pulse.api.profiler;

/**
 * 프로파일러 싱크 인터페이스.
 * 프로파일링 데이터 수신.
 * 
 * @since Pulse 2.0
 */
public interface IProfilerSink {

    /**
     * 틱 프로파일 데이터 수신
     * 
     * @param tickNumber    틱 번호
     * @param durationNanos 소요 시간 (나노초)
     */
    void onTickProfile(long tickNumber, long durationNanos);

    /**
     * 렌더 프로파일 데이터 수신
     * 
     * @param frameNumber   프레임 번호
     * @param durationNanos 소요 시간 (나노초)
     */
    void onRenderProfile(long frameNumber, long durationNanos);
}
