package com.pulse.api.mixin;

import com.pulse.api.PublicAPI;

/**
 * Mixin 인젝션 이벤트 리스너 인터페이스.
 * 
 * <pre>
 * // 사용 예시
 * MixinInjectionValidator.addListener(new InjectionListener() {
 *     &#64;Override
 *     public void onInjectionSuccess(String mixinClass, String targetClass, long timeMs) {
 *         System.out.println("Mixin applied: " + mixinClass + " in " + timeMs + "ms");
 *     }
 * 
 *     &#64;Override
 *     public void onInjectionFailed(String mixinClass, String targetClass, String reason) {
 *         System.err.println("Mixin failed: " + mixinClass + " - " + reason);
 *     }
 * });
 * </pre>
 * 
 * @since 1.0.1
 */
@PublicAPI(since = "1.0.1", status = PublicAPI.Status.EXPERIMENTAL)
public interface InjectionListener {

    /**
     * Mixin 인젝션 성공 시 호출.
     * 
     * @param mixinClass  Mixin 클래스 전체 경로
     * @param targetClass 대상 클래스 전체 경로
     * @param timeMs      인젝션에 걸린 시간 (밀리초)
     */
    void onInjectionSuccess(String mixinClass, String targetClass, long timeMs);

    /**
     * Mixin 인젝션 실패 시 호출.
     * 
     * @param mixinClass  Mixin 클래스 전체 경로
     * @param targetClass 대상 클래스 전체 경로
     * @param reason      실패 사유
     */
    void onInjectionFailed(String mixinClass, String targetClass, String reason);

    // ═══════════════════════════════════════════════════════════════
    // 기본 구현 제공
    // ═══════════════════════════════════════════════════════════════

    /**
     * 성공만 로깅하는 리스너.
     */
    static InjectionListener successLogger() {
        return new InjectionListener() {
            @Override
            public void onInjectionSuccess(String mixinClass, String targetClass, long timeMs) {
                System.out.println("[Mixin] ✓ " + mixinClass + " → " + targetClass + " (" + timeMs + "ms)");
            }

            @Override
            public void onInjectionFailed(String mixinClass, String targetClass, String reason) {
                // 무시
            }
        };
    }

    /**
     * 실패만 로깅하는 리스너.
     */
    static InjectionListener failureLogger() {
        return new InjectionListener() {
            @Override
            public void onInjectionSuccess(String mixinClass, String targetClass, long timeMs) {
                // 무시
            }

            @Override
            public void onInjectionFailed(String mixinClass, String targetClass, String reason) {
                System.err.println("[Mixin] ✗ " + mixinClass + " → " + targetClass + ": " + reason);
            }
        };
    }

    /**
     * 모든 이벤트 로깅하는 리스너.
     */
    static InjectionListener fullLogger() {
        return new InjectionListener() {
            @Override
            public void onInjectionSuccess(String mixinClass, String targetClass, long timeMs) {
                System.out.println("[Mixin] ✓ " + mixinClass + " → " + targetClass + " (" + timeMs + "ms)");
            }

            @Override
            public void onInjectionFailed(String mixinClass, String targetClass, String reason) {
                System.err.println("[Mixin] ✗ " + mixinClass + " → " + targetClass + ": " + reason);
            }
        };
    }
}
