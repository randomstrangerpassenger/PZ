package com.pulse.api.config;

import java.nio.file.Path;

/**
 * Config Template 인터페이스.
 * 
 * v4 Phase 4: Echo/Fuse Config 공통 계약 정의.
 * 모든 모듈 Config 클래스는 이 인터페이스를 구현.
 * 
 * @since Pulse 0.8.0
 */
public interface ConfigTemplate {

    /**
     * 설정 파일에서 로드.
     * 파일이 없으면 기본값으로 생성.
     */
    void load();

    /**
     * 설정 파일로 저장.
     */
    void save();

    /**
     * 설정을 기본값으로 리셋.
     */
    default void reset() {
        // 기본 구현: 아무것도 안 함
        // 각 모듈에서 오버라이드
    }

    /**
     * 설정 검증 및 자동 수정.
     * 
     * @return 수정된 항목 수
     */
    default int sanitize() {
        // 기본 구현: 0 반환
        return 0;
    }

    /**
     * 설정 디렉토리 경로.
     * 
     * @return 설정 디렉토리 Path
     */
    Path getConfigDirectory();

    /**
     * 설정 파일명.
     * 
     * @return 설정 파일명 (예: "echo.json")
     */
    String getConfigFileName();

    /**
     * 설정 버전 (마이그레이션용).
     * 
     * @return 설정 버전
     */
    default int getConfigVersion() {
        return 1;
    }
}
