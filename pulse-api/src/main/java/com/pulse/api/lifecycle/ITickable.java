package com.pulse.api.lifecycle;

/**
 * 틱 기반 컴포넌트 인터페이스.
 * 
 * 게임 틱에 맞춰 업데이트가 필요한 컴포넌트가 구현합니다.
 * 복잡도 완화를 위해 도입된 공통 추상화입니다.
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>
 * {
 *     &#64;code
 *     public class MyComponent implements ITickable {
 *         private boolean enabled = true;
 * 
 *         &#64;Override
 *         public void onTick(long tickCounter) {
 *             if (!enabled)
 *                 return;
 *             // Process tick logic
 *         }
 * 
 *         &#64;Override
 *         public boolean isEnabled() {
 *             return enabled;
 *         }
 * 
 *         @Override
 *         public void setEnabled(boolean enabled) {
 *             this.enabled = enabled;
 *         }
 *     }
 * }
 * </pre>
 * 
 * @since Pulse 1.1.0
 */
public interface ITickable {

    /**
     * 틱 콜백.
     * 
     * @param tickCounter 현재 틱 카운터
     */
    void onTick(long tickCounter);

    /**
     * 활성화 여부.
     * 
     * @return true면 onTick이 호출됨
     */
    default boolean isEnabled() {
        return true;
    }

    /**
     * 활성화 설정.
     * 
     * @param enabled 활성화 여부
     */
    default void setEnabled(boolean enabled) {
        // Default implementation does nothing
    }

    /**
     * 틱 우선순위.
     * 낮은 값이 먼저 실행됩니다.
     * 
     * @return 우선순위 (기본값: 100)
     */
    default int getTickPriority() {
        return 100;
    }

    /**
     * 컴포넌트 이름.
     * 디버깅 및 로깅용.
     * 
     * @return 컴포넌트 이름
     */
    default String getTickableName() {
        return getClass().getSimpleName();
    }
}
