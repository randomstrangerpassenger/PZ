package com.pulse.api;

/**
 * Pulse 메트릭 API 인터페이스.
 * 성능 메트릭 데이터에 접근하기 위한 계약.
 * Echo 프로파일러 등에서 사용.
 */
public interface IPulseMetrics {

    /**
     * 현재 FPS
     */
    double getFps();

    /**
     * 프레임 시간 (밀리초)
     */
    double getFrameTimeMs();

    /**
     * 틱 시간 (밀리초)
     */
    double getTickTimeMs();

    /**
     * 평균 틱 시간 (밀리초)
     */
    double getAverageTickTimeMs();

    /**
     * 최대 틱 시간 (밀리초)
     */
    double getMaxTickTimeMs();

    /**
     * TPS (Ticks Per Second)
     */
    double getTps();

    /**
     * 현재 로드된 청크 수
     */
    int getLoadedChunkCount();

    /**
     * 현재 엔티티 수
     */
    int getEntityCount();

    /**
     * 메모리 사용량 (MB)
     */
    long getUsedMemoryMB();

    /**
     * 최대 메모리 (MB)
     */
    long getMaxMemoryMB();
}
