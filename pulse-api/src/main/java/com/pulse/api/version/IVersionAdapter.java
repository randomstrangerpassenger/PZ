package com.pulse.api.version;

/**
 * 버전별 어댑터 공통 인터페이스.
 * 
 * 모든 버전별 어댑터가 구현해야 하는 기본 계약을 정의합니다.
 * 
 * @since Pulse 1.4
 */
public interface IVersionAdapter {

    /**
     * 이 어댑터가 지원하는 빌드 버전.
     * 
     * @return GameVersion.BUILD_41 또는 GameVersion.BUILD_42
     */
    int getSupportedBuild();

    /**
     * 현재 게임 환경과 호환되는지 확인.
     * 
     * @return 호환 가능하면 true
     */
    boolean isCompatible();

    /**
     * 어댑터 이름 (로깅용).
     */
    default String getName() {
        return getClass().getSimpleName();
    }
}
