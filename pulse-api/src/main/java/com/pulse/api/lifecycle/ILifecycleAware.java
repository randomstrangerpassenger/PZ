package com.pulse.api.lifecycle;

/**
 * 라이프사이클 관리 인터페이스.
 * 
 * 초기화와 종료가 필요한 컴포넌트가 구현합니다.
 * 복잡도 완화를 위해 도입된 공통 추상화입니다.
 * 
 * <h2>라이프사이클 순서</h2>
 * <ol>
 * <li>{@link #initialize()} - 시작 시 호출</li>
 * <li>활성 상태 (isInitialized() = true)</li>
 * <li>{@link #shutdown()} - 종료 시 호출</li>
 * </ol>
 * 
 * @since Pulse 1.1.0
 */
public interface ILifecycleAware {

    /**
     * 컴포넌트 초기화.
     * 모든 의존성이 준비된 후 호출됩니다.
     */
    void initialize();

    /**
     * 컴포넌트 종료.
     * 리소스 해제 및 정리를 수행합니다.
     */
    void shutdown();

    /**
     * 초기화 완료 여부.
     * 
     * @return true면 초기화 완료
     */
    boolean isInitialized();

    /**
     * 컴포넌트 이름.
     * 디버깅 및 로깅용.
     * 
     * @return 컴포넌트 이름
     */
    default String getComponentName() {
        return getClass().getSimpleName();
    }

    /**
     * 초기화 우선순위.
     * 낮은 값이 먼저 초기화됩니다.
     * 
     * @return 우선순위 (기본값: 100)
     */
    default int getInitPriority() {
        return 100;
    }
}
