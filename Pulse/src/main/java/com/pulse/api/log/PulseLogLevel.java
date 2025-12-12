package com.pulse.api.log;

/**
 * Pulse 로깅 레벨 정의.
 * 
 * 릴리즈 빌드에서는 INFO 이상만 출력됩니다.
 */
public enum PulseLogLevel {
    /** 가장 상세한 디버그 정보 */
    TRACE(0),
    /** 개발 디버깅용 */
    DEBUG(1),
    /** 일반 정보 */
    INFO(2),
    /** 경고 */
    WARN(3),
    /** 오류 */
    ERROR(4);

    private final int level;

    PulseLogLevel(int level) {
        this.level = level;
    }

    public int getLevel() {
        return level;
    }

    public boolean isEnabled(PulseLogLevel currentLevel) {
        return this.level >= currentLevel.level;
    }
}
