package com.pulse.api.profiler;

/**
 * 프로파일러 브릿지 인터페이스.
 * 외부 모듈이 프로파일러 싱크를 등록/해제.
 * 
 * @since Pulse 2.0
 */
public interface IProfilerBridge {

    /**
     * 프로파일러 싱크 설정
     * 
     * @param sink 싱크 구현체, null이면 해제
     */
    void setSink(IProfilerSink sink);

    /**
     * 현재 싱크 가져오기
     * 
     * @return 현재 등록된 싱크, 없으면 null
     */
    IProfilerSink getSink();

    /**
     * 싱크 해제
     */
    void clearSink();

    /**
     * 싱크가 등록되어 있는지 확인
     */
    boolean hasSink();
}
