package com.pulse.api.status;

import java.util.Map;

/**
 * 상태 보고 인터페이스.
 * 
 * 상태 정보를 제공하는 컴포넌트가 구현합니다.
 * /pulse status, /echo status, /fuse status 등에서 사용됩니다.
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>
 * {
 *     &#64;code
 *     public class MyComponent implements IStatusProvider {
 *         &#64;Override
 *         public Map<String, Object> getStatus() {
 *             return Map.of(
 *                     "enabled", true,
 *                     "count", 42,
 *                     "lastUpdate", System.currentTimeMillis());
 *         }
 * 
 *         @Override
 *         public String getStatusSummary() {
 *             return "MyComponent: 42 items processed";
 *         }
 *     }
 * }
 * </pre>
 * 
 * @since Pulse 1.1.0
 */
public interface IStatusProvider {

    /**
     * 상세 상태 정보.
     * 
     * @return 키-값 맵
     */
    Map<String, Object> getStatus();

    /**
     * 한 줄 상태 요약.
     * 
     * @return 요약 문자열
     */
    String getStatusSummary();

    /**
     * 상태 제공자 이름.
     * 
     * @return 이름
     */
    default String getProviderName() {
        return getClass().getSimpleName();
    }

    /**
     * 상태 출력.
     * 콘솔에 상태 정보를 출력합니다.
     */
    default void printStatus() {
        System.out.println(getStatusSummary());
        getStatus().forEach((k, v) -> System.out.println("  " + k + ": " + v));
    }
}
