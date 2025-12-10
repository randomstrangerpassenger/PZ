package com.pulse.api.spi;

/**
 * 모든 SPI 프로바이더의 기본 인터페이스.
 * Pulse 위에서 동작하는 모든 확장 모드가 구현해야 하는 기본 계약.
 * 
 * 사용 예:
 * public class MyProfiler implements IProvider, IProfilerProvider {
 * // ...
 * }
 */
public interface IProvider {

    /**
     * 프로바이더 고유 ID (예: "echo", "fuse", "nerve")
     */
    String getId();

    /**
     * 프로바이더 이름 (표시용)
     */
    String getName();

    /**
     * 프로바이더 버전
     */
    String getVersion();

    /**
     * 프로바이더 설명
     */
    default String getDescription() {
        return "";
    }

    /**
     * 우선순위 (높을수록 먼저 실행)
     */
    default int getPriority() {
        return Priority.NORMAL;
    }

    /**
     * 프로바이더 초기화
     * Pulse가 모드 로드 시 호출
     */
    default void onInitialize() {
    }

    /**
     * 프로바이더 종료
     * Pulse가 게임 종료 시 호출
     */
    default void onShutdown() {
    }

    /**
     * 프로바이더 활성화 여부
     */
    default boolean isEnabled() {
        return true;
    }
}
