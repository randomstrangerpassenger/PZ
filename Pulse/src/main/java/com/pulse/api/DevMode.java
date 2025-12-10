package com.pulse.api;

/**
 * Pulse DevMode 관리자.
 * 개발 모드 플래그를 관리하고 디버그 기능을 제어.
 * 
 * 활성화 방법:
 * 1. JVM 옵션: -DPulse.devMode=true
 * 2. 코드에서: DevMode.enable()
 * 
 * DevMode가 활성화되면:
 * - 상세한 Mixin 진단 로그 출력
 * - 이벤트 예외 세부 정보 출력
 * - 의존성 문제 추가 정보 출력
 */
public final class DevMode {

    private static boolean enabled = false;
    private static boolean initialized = false;

    private DevMode() {
    } // 인스턴스화 방지

    // ─────────────────────────────────────────────────────────────
    // 초기화
    // ─────────────────────────────────────────────────────────────

    /**
     * 시스템 프로퍼티에서 DevMode 상태 초기화
     */
    public static void initialize() {
        if (initialized)
            return;

        // 시스템 프로퍼티 확인
        String devModeProp = System.getProperty("Pulse.devMode", "false");
        enabled = "true".equalsIgnoreCase(devModeProp) || "1".equals(devModeProp);

        if (enabled) {
            System.out.println("[Pulse/DevMode] ═══════════════════════════════════════");
            System.out.println("[Pulse/DevMode] DEVELOPER MODE ENABLED");
            System.out.println("[Pulse/DevMode] Additional diagnostics will be shown");
            System.out.println("[Pulse/DevMode] ═══════════════════════════════════════");
        }

        initialized = true;
    }

    // ─────────────────────────────────────────────────────────────
    // 상태 관리
    // ─────────────────────────────────────────────────────────────

    /**
     * DevMode 활성화 여부 확인
     */
    public static boolean isEnabled() {
        if (!initialized) {
            initialize();
        }
        return enabled;
    }

    /**
     * DevMode 활성화
     */
    public static void enable() {
        enabled = true;
        if (!initialized) {
            initialized = true;
            System.out.println("[Pulse/DevMode] Developer mode enabled programmatically");
        }
    }

    /**
     * DevMode 비활성화
     */
    public static void disable() {
        enabled = false;
    }

    // ─────────────────────────────────────────────────────────────
    // 편의 메서드
    // ─────────────────────────────────────────────────────────────

    /**
     * DevMode일 때만 로그 출력
     */
    public static void log(String tag, String message) {
        if (isEnabled()) {
            System.out.println("[Pulse/Debug/" + tag + "] " + message);
        }
    }

    /**
     * DevMode일 때만 실행할 작업
     */
    public static void ifEnabled(Runnable action) {
        if (isEnabled()) {
            action.run();
        }
    }
}
