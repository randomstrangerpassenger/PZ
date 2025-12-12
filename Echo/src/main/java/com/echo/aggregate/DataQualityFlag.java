package com.echo.aggregate;

/**
 * 데이터 품질 플래그.
 * 
 * 프로파일링 샘플에 영향을 미칠 수 있는 조건을 표시합니다.
 * 통계 계산 시 특정 플래그가 있는 샘플을 제외할 수 있습니다.
 * 
 * @since 1.0.1
 */
public enum DataQualityFlag {

    /**
     * 게임 시작 직후 불안정 구간 (Warmup)
     * 처음 몇 초는 클래스 로딩, JIT 컴파일 등으로 노이즈가 많음
     */
    WARMUP_PERIOD("Session warmup period - data may be noisy"),

    /**
     * 프로파일링 스택 불일치
     * push() 호출 후 pop()이 없거나 순서가 맞지 않음
     */
    PUSH_POP_MISMATCH("Profiling stack push/pop mismatch"),

    /**
     * 잘못된 스레드 접근
     * 메인 스레드가 아닌 곳에서 프로파일링 함수 호출
     */
    WRONG_THREAD_ACCESS("Profiling called from non-main thread"),

    /**
     * 비정상적으로 큰 델타 시간 (>100ms)
     * 틱이 정상 범위를 크게 벗어남
     */
    LARGE_DELTA_TIME("Abnormally large delta time (>100ms)"),

    /**
     * GC 일시정지 기간 중 샘플
     * GC가 발생하면 타이밍 데이터가 왜곡됨
     */
    GC_PAUSE_AFFECTED("Sample affected by GC pause"),

    /**
     * 게임 일시정지 중
     * 일시정지 상태에서는 틱이 멈추므로 데이터가 왜곡될 수 있음
     */
    GAME_PAUSED("Game was paused during sample"),

    /**
     * 세션 시간 부족
     * 충분한 샘플이 수집되지 않음
     */
    INSUFFICIENT_SAMPLES("Insufficient samples for reliable statistics");

    private final String description;

    DataQualityFlag(String description) {
        this.description = description;
    }

    public String getDescription() {
        return description;
    }

    @Override
    public String toString() {
        return name() + ": " + description;
    }
}
