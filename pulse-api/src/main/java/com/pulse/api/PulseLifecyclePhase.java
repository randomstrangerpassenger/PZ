package com.pulse.api;

/**
 * Pulse 라이프사이클 단계.
 * 
 * Phase 3.1: 부트스트랩 프로파일링 포인트.
 * 모드 로딩이 느린지 vs 런타임이 느린지 구분할 수 있습니다.
 * 
 * @since 1.0.1
 */
public enum PulseLifecyclePhase {

    /**
     * 모드 발견 단계
     * mods 폴더 스캔 및 모드 목록 구성
     */
    MOD_DISCOVERY("Mod Discovery", "모드 파일 탐색"),

    /**
     * 모드 로딩 단계
     * 모드 JAR 파일 로드 및 초기화
     */
    MOD_LOADING("Mod Loading", "모드 클래스 로딩"),

    /**
     * Mixin 적용 단계
     * 바이트코드 변환 수행
     */
    MIXIN_APPLICATION("Mixin Application", "Mixin 변환 적용"),

    /**
     * 엔트리포인트 실행 단계
     * 모드 초기화 메서드 호출
     */
    ENTRYPOINT_EXECUTION("Entrypoint Execution", "모드 초기화"),

    /**
     * 런타임 활성 단계
     * 게임 실행 중
     */
    RUNTIME_ACTIVE("Runtime Active", "게임 실행 중"),

    /**
     * 종료 단계
     * 게임 종료 및 정리
     */
    SHUTDOWN("Shutdown", "게임 종료");

    private final String displayName;
    private final String description;
    private long startTimeMs = 0;
    private long endTimeMs = 0;
    private boolean completed = false;

    PulseLifecyclePhase(String displayName, String description) {
        this.displayName = displayName;
        this.description = description;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getDescription() {
        return description;
    }

    public long getStartTimeMs() {
        return startTimeMs;
    }

    public long getEndTimeMs() {
        return endTimeMs;
    }

    public long getDurationMs() {
        if (startTimeMs == 0)
            return 0;
        if (endTimeMs == 0)
            return System.currentTimeMillis() - startTimeMs;
        return endTimeMs - startTimeMs;
    }

    public boolean isCompleted() {
        return completed;
    }

    /**
     * 단계 시작 기록
     */
    public void markStart() {
        this.startTimeMs = System.currentTimeMillis();
        this.completed = false;
    }

    /**
     * 단계 완료 기록
     */
    public void markEnd() {
        this.endTimeMs = System.currentTimeMillis();
        this.completed = true;
    }

    /**
     * 모든 단계 초기화
     */
    public static void resetAll() {
        for (PulseLifecyclePhase phase : values()) {
            phase.startTimeMs = 0;
            phase.endTimeMs = 0;
            phase.completed = false;
        }
    }

    /**
     * 전체 라이프사이클 타이밍 맵
     */
    public static java.util.Map<String, Object> toMap() {
        java.util.Map<String, Object> map = new java.util.LinkedHashMap<>();

        for (PulseLifecyclePhase phase : values()) {
            java.util.Map<String, Object> phaseData = new java.util.LinkedHashMap<>();
            phaseData.put("duration_ms", phase.getDurationMs());
            phaseData.put("completed", phase.isCompleted());
            if (phase.startTimeMs > 0) {
                phaseData.put("start_time", phase.startTimeMs);
            }
            map.put(phase.name().toLowerCase(), phaseData);
        }

        // 총 부트스트랩 시간 (MOD_DISCOVERY ~ ENTRYPOINT_EXECUTION)
        long bootstrapTotal = 0;
        for (PulseLifecyclePhase phase : values()) {
            if (phase != RUNTIME_ACTIVE && phase != SHUTDOWN) {
                bootstrapTotal += phase.getDurationMs();
            }
        }
        map.put("bootstrap_total_ms", bootstrapTotal);

        return map;
    }

    /**
     * 현재 활성 단계
     */
    public static PulseLifecyclePhase getCurrentPhase() {
        for (int i = values().length - 1; i >= 0; i--) {
            PulseLifecyclePhase phase = values()[i];
            if (phase.startTimeMs > 0 && !phase.completed) {
                return phase;
            }
        }
        // 모든 단계 완료 시 RUNTIME_ACTIVE 반환
        return RUNTIME_ACTIVE;
    }
}
