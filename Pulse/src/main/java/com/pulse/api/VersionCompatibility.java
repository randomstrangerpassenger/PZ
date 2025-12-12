package com.pulse.api;

import com.pulse.api.log.PulseLogger;

/**
 * 버전 호환성 검사 유틸리티.
 * Pulse API 버전과 게임 버전 호환성을 확인합니다.
 * 
 * <pre>
 * // 사용 예시
 * if (VersionCompatibility.isCompatible(2)) {
 *     // API v2 이상 필요한 기능 사용
 * }
 * 
 * if (!VersionCompatibility.isGameVersionCompatible()) {
 *     Pulse.warn("mymod", "Game version too old!");
 * }
 * </pre>
 * 
 * @since 1.1.0
 */
@PublicAPI(since = "1.1.0")
public final class VersionCompatibility {

    private static final String LOG = PulseLogger.PULSE;

    // ═══════════════════════════════════════════════════════════════
    // 버전 상수
    // ═══════════════════════════════════════════════════════════════

    /** Pulse API 버전 (정수) */
    public static final int PULSE_API_VERSION = 1;

    /** Pulse 버전 문자열 */
    public static final String PULSE_VERSION = "0.8.0";

    /** 최소 지원 PZ 버전 */
    public static final String MIN_GAME_VERSION = "41.78";

    /** 최대 테스트된 PZ 버전 */
    public static final String MAX_TESTED_GAME_VERSION = "41.78.16";

    // 캐시된 게임 버전
    private static volatile String cachedGameVersion = null;
    private static volatile Boolean cachedGameCompatible = null;

    private VersionCompatibility() {
    } // 인스턴스화 방지

    // ═══════════════════════════════════════════════════════════════
    // API 호환성
    // ═══════════════════════════════════════════════════════════════

    /**
     * 요청한 API 버전이 호환되는지 확인.
     * 
     * @param requiredApiVersion 필요한 API 버전
     * @return 호환되면 true
     */
    public static boolean isCompatible(int requiredApiVersion) {
        return PULSE_API_VERSION >= requiredApiVersion;
    }

    /**
     * 현재 Pulse API 버전 반환.
     * 
     * @return API 버전 정수
     */
    public static int getApiVersion() {
        return PULSE_API_VERSION;
    }

    /**
     * 현재 Pulse 버전 문자열 반환.
     * 
     * @return 버전 문자열 (예: "1.1.0")
     */
    public static String getPulseVersion() {
        return PULSE_VERSION;
    }

    // ═══════════════════════════════════════════════════════════════
    // 게임 버전 호환성
    // ═══════════════════════════════════════════════════════════════

    /**
     * 현재 게임 버전이 호환되는지 확인.
     * 
     * @return 호환되면 true
     */
    public static boolean isGameVersionCompatible() {
        if (cachedGameCompatible != null) {
            return cachedGameCompatible;
        }

        String gameVersion = getGameVersion();
        if (gameVersion == null || gameVersion.isEmpty()) {
            cachedGameCompatible = true; // 버전 확인 불가 시 호환으로 간주
            return true;
        }

        cachedGameCompatible = compareVersions(gameVersion, MIN_GAME_VERSION) >= 0;
        return cachedGameCompatible;
    }

    /**
     * 현재 게임 버전 문자열 반환.
     * 
     * @return 게임 버전 또는 "Unknown"
     */
    public static String getGameVersion() {
        if (cachedGameVersion != null) {
            return cachedGameVersion;
        }

        try {
            // Core.GameVersion 접근 시도
            Class<?> coreClass = Class.forName("zombie.core.Core");
            java.lang.reflect.Field versionField = coreClass.getDeclaredField("GameVersion");
            versionField.setAccessible(true);
            Object version = versionField.get(null);

            if (version != null) {
                cachedGameVersion = version.toString();
                return cachedGameVersion;
            }
        } catch (Exception e) {
            // 무시 - 게임 클래스 로드 전
        }

        // 대안: 시스템 프로퍼티
        String propVersion = System.getProperty("zomboid.version");
        if (propVersion != null) {
            cachedGameVersion = propVersion;
            return cachedGameVersion;
        }

        cachedGameVersion = "Unknown";
        return cachedGameVersion;
    }

    /**
     * 특정 Pulse 기능이 사용 가능한지 확인.
     * CapabilityFlags와 연동.
     * 
     * @param featureId 기능 ID
     * @return 사용 가능하면 true
     */
    public static boolean hasFeature(String featureId) {
        return CapabilityFlags.supports(featureId) && FeatureFlags.isEnabled(featureId);
    }

    // ═══════════════════════════════════════════════════════════════
    // 버전 비교 유틸리티
    // ═══════════════════════════════════════════════════════════════

    /**
     * 버전 문자열 비교.
     * 
     * @param v1 버전 1
     * @param v2 버전 2
     * @return v1 > v2 면 양수, v1 < v2 면 음수, 같으면 0
     */
    public static int compareVersions(String v1, String v2) {
        if (v1 == null || v2 == null) {
            return 0;
        }

        String[] parts1 = v1.split("\\.");
        String[] parts2 = v2.split("\\.");

        int maxLength = Math.max(parts1.length, parts2.length);

        for (int i = 0; i < maxLength; i++) {
            int num1 = i < parts1.length ? parseVersionPart(parts1[i]) : 0;
            int num2 = i < parts2.length ? parseVersionPart(parts2[i]) : 0;

            if (num1 != num2) {
                return num1 - num2;
            }
        }

        return 0;
    }

    private static int parseVersionPart(String part) {
        try {
            // 숫자가 아닌 문자 제거 (예: "78b" → "78")
            String numOnly = part.replaceAll("[^0-9]", "");
            return numOnly.isEmpty() ? 0 : Integer.parseInt(numOnly);
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    /**
     * 디버그 정보 출력.
     */
    public static void printInfo() {
        PulseLogger.info(LOG, "═══════════════════════════════════════");
        PulseLogger.info(LOG, "  Version Compatibility Info");
        PulseLogger.info(LOG, "═══════════════════════════════════════");
        PulseLogger.info(LOG, "  Pulse Version: {}", PULSE_VERSION);
        PulseLogger.info(LOG, "  API Version: {}", PULSE_API_VERSION);
        PulseLogger.info(LOG, "  Game Version: {}", getGameVersion());
        PulseLogger.info(LOG, "  Min Supported: {}", MIN_GAME_VERSION);
        PulseLogger.info(LOG, "  Max Tested: {}", MAX_TESTED_GAME_VERSION);
        PulseLogger.info(LOG, "  Compatible: {}", isGameVersionCompatible());
        PulseLogger.info(LOG, "═══════════════════════════════════════");
    }
}
