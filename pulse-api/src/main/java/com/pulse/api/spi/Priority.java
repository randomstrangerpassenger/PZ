package com.pulse.api.spi;

/**
 * 프로바이더 우선순위 상수.
 * 높을수록 먼저 초기화되고 이벤트를 먼저 받음.
 */
public final class Priority {

    private Priority() {
    }

    /** 가장 높은 우선순위 - 시스템 레벨 */
    public static final int HIGHEST = 1000;

    /** 높은 우선순위 - 핵심 기능 */
    public static final int HIGH = 750;

    /** 기본 우선순위 */
    public static final int NORMAL = 500;

    /** 낮은 우선순위 */
    public static final int LOW = 250;

    /** 가장 낮은 우선순위 - 후처리 */
    public static final int LOWEST = 0;
}
