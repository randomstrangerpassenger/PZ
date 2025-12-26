package com.pulse.api.spi;

/**
 * 프로파일링 프로바이더 인터페이스.
 * Echo와 같은 프로파일링 모드가 구현.
 * 
 * 다른 모드도 동일한 인터페이스를 구현하여 프로파일링 기능 제공 가능.
 */
public interface IProfilerProvider extends IProvider {

    /**
     * 틱 시작 시 호출
     */
    void onTickStart();

    /**
     * 틱 종료 시 호출
     * 
     * @param tickTimeNanos 틱 소요 시간 (나노초)
     */
    void onTickEnd(long tickTimeNanos);

    /**
     * 프레임 시작 시 호출
     */
    void onFrameStart();

    /**
     * 프레임 종료 시 호출
     * 
     * @param frameTimeNanos 프레임 소요 시간 (나노초)
     */
    void onFrameEnd(long frameTimeNanos);

    /**
     * 현재 FPS 조회
     */
    double getCurrentFps();

    /**
     * 현재 평균 틱 시간 (밀리초)
     */
    double getAverageTickTimeMs();

    /**
     * 현재 평균 프레임 시간 (밀리초)
     */
    double getAverageFrameTimeMs();

    /**
     * 프로파일링 활성화
     */
    void startProfiling();

    /**
     * 프로파일링 비활성화
     */
    void stopProfiling();

    /**
     * 프로파일링 중인지 확인
     */
    boolean isProfiling();

    /**
     * 프로파일링 데이터 리셋
     */
    void resetData();

    // ═══════════════════════════════════════════════════════════════
    // Scope-based Profiling (v1.1.0)
    // ═══════════════════════════════════════════════════════════════

    /**
     * Push a profiling scope.
     * Label format: area/subsystem/detail (e.g., zombie/ai/pathfinding)
     *
     * @param label Scope label
     */
    default void pushScope(String label) {
        // Default no-op for backward compatibility
    }

    /**
     * Pop the current profiling scope.
     */
    default void popScope() {
        // Default no-op for backward compatibility
    }

    /**
     * Execute action within a profiling scope.
     * Ensures proper push/pop even on exception.
     *
     * @param label  Scope label
     * @param action Action to execute
     */
    default void withScope(String label, Runnable action) {
        pushScope(label);
        try {
            action.run();
        } finally {
            popScope();
        }
    }
}
