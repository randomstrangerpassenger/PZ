package com.echo.report;

/**
 * 데이터 품질 상태 표시자.
 * 
 * Echo 리포트에서 각 메트릭의 수집 상태를 나타냅니다.
 * 
 * @since Echo 2.1
 */
public enum DataQualityStatus {

    /**
     * 정상적으로 수집 중인 데이터.
     */
    ACTIVE("active"),

    /**
     * 해당 메트릭이 아직 관측되지 않음.
     * (예: 게임 시작 직후 일부 Phase가 아직 실행되지 않은 경우)
     */
    NOT_OBSERVED("not_observed"),

    /**
     * 싱글플레이어 모드에서 비활성화된 메트릭.
     * (예: NetworkMetrics는 MP 전용)
     */
    DISABLED_SP("disabled_sp"),

    /**
     * 멀티플레이어 모드에서 비활성화된 메트릭.
     */
    DISABLED_MP("disabled_mp"),

    /**
     * 오류로 인해 수집 불가.
     */
    ERROR("error");

    private final String jsonValue;

    DataQualityStatus(String jsonValue) {
        this.jsonValue = jsonValue;
    }

    /**
     * JSON 출력용 문자열 반환.
     */
    public String toJson() {
        return jsonValue;
    }

    /**
     * JSON 값에서 enum으로 변환.
     */
    public static DataQualityStatus fromJson(String json) {
        for (DataQualityStatus status : values()) {
            if (status.jsonValue.equals(json)) {
                return status;
            }
        }
        return NOT_OBSERVED;
    }
}
