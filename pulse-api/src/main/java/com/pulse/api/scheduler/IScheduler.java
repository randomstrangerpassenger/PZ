package com.pulse.api.scheduler;

/**
 * 스케줄러 인터페이스.
 * 
 * @since Pulse 2.0 (Phase 3 API Extraction)
 */
public interface IScheduler {
    /**
     * 스케줄러 틱.
     * 매 게임 틱마다 호출됨.
     */
    void tick();

    /**
     * 스케줄러 종료.
     * 라이프사이클 종료 시 호출됨.
     */
    void shutdown();
}
