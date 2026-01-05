package com.pulse.api.config;

/**
 * 설정 가능한 컴포넌트 인터페이스.
 * 
 * 런타임 설정 변경을 지원하는 컴포넌트가 구현합니다.
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>
 * {
 *     &#64;code
 *     public class MyComponent implements IConfigurable {
 *         private boolean enabled = true;
 * 
 *         &#64;Override
 *         public void applyConfig(Map<String, Object> config) {
 *             if (config.containsKey("enabled")) {
 *                 enabled = (Boolean) config.get("enabled");
 *             }
 *         }
 * 
 *         @Override
 *         public void reloadConfig() {
 *             // Reload from file or default values
 *         }
 *     }
 * }
 * </pre>
 * 
 * @since Pulse 1.1.0
 */
public interface IConfigurable {

    /**
     * 설정 적용.
     * 
     * @param config 키-값 설정 맵
     */
    void applyConfig(java.util.Map<String, Object> config);

    /**
     * 설정 리로드.
     * 파일 또는 기본값에서 설정을 다시 로드합니다.
     */
    void reloadConfig();

    /**
     * 현재 설정 반환.
     * 
     * @return 현재 설정 맵
     */
    default java.util.Map<String, Object> getCurrentConfig() {
        return java.util.Collections.emptyMap();
    }

    /**
     * 설정 검증.
     * 
     * @param config 검증할 설정
     * @return 유효하면 true
     */
    default boolean validateConfig(java.util.Map<String, Object> config) {
        return true;
    }
}
