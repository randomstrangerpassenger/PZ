package com.pulse.api.mixin;

/**
 * Mixin 실패 심각도 수준.
 * 
 * SafeMixinWrapper에서 오류 처리 방식을 결정하는 데 사용됩니다.
 * 
 * @since 1.1.0
 */
public enum MixinSeverity {

    /**
     * 낮음 - 부가 기능 (통계, 로깅).
     * 조용히 무시, 레이트 리밋 없음.
     */
    LOW,

    /**
     * 중간 - 보조 기능 (배칭, 캐싱).
     * DevMode에서만 디버그 로그.
     */
    MEDIUM,

    /**
     * 높음 - 핵심 기능 (좀비 AI, 저장/로드).
     * 에러 로그 + 메트릭 기록.
     * 분당 10회 레이트 리밋.
     */
    HIGH
}
