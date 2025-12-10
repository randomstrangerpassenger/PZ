package com.pulse.api;

import java.nio.file.Path;
import java.util.Collection;
import java.util.Optional;

/**
 * Pulse 메인 API 인터페이스.
 * Pulse 모드 로더의 핵심 기능에 접근하기 위한 계약.
 */
public interface IPulse {

    /**
     * Pulse 버전 반환
     */
    String getVersion();

    /**
     * API 버전 반환 (호환성 체크용)
     */
    int getApiVersion();

    /**
     * 특정 모드가 로드되었는지 확인
     */
    boolean isModLoaded(String modId);

    /**
     * 모드 정보 가져오기
     */
    Optional<PulseModInfo> getModInfo(String modId);

    /**
     * 로드된 모든 모드 ID 목록
     */
    Collection<String> getLoadedModIds();

    /**
     * Pulse 초기화 완료 여부
     */
    boolean isInitialized();

    /**
     * 게임 디렉토리 경로
     */
    Path getGameDirectory();

    /**
     * mods 디렉토리 경로
     */
    Path getModsDirectory();

    /**
     * 설정 디렉토리 경로
     */
    Path getConfigDirectory();

    /**
     * 현재 실행 사이드 (CLIENT, SERVER 등)
     */
    PulseSide getSide();

    /**
     * 클라이언트 환경인지 확인
     */
    boolean isClient();

    /**
     * 서버 환경인지 확인
     */
    boolean isServer();

    /**
     * DevMode 활성화 여부
     */
    boolean isDevMode();
}
