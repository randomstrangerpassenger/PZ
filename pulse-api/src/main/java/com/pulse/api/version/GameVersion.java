package com.pulse.api.version;

/**
 * Project Zomboid 게임 버전 감지 및 관리.
 * 
 * Build 41과 Build 42+ 간의 API 차이를 런타임에 감지하여
 * 적절한 어댑터를 선택할 수 있도록 합니다.
 * 
 * 감지 방식:
 * 1. 클래스 존재 여부 확인 (Build 42 전용 클래스)
 * 2. 메서드 시그니처 차이 확인
 * 3. 시스템 프로퍼티 폴백
 * 
 * @since Pulse 1.4
 */
public final class GameVersion {

    /** Build 41 (IWBUMS 안정 버전) */
    public static final int BUILD_41 = 41;

    /** Build 42 (차세대 엔진) */
    public static final int BUILD_42 = 42;

    /** 알 수 없는 버전 */
    public static final int UNKNOWN = -1;

    // 캐시된 버전 (한 번만 감지)
    private static volatile int cachedVersion = UNKNOWN;
    private static volatile boolean detected = false;

    private GameVersion() {
        // 유틸리티 클래스
    }

    // ═══════════════════════════════════════════════════════════════
    // Public API
    // ═══════════════════════════════════════════════════════════════

    /**
     * 현재 게임 빌드 버전 반환.
     * 
     * @return BUILD_41, BUILD_42, 또는 UNKNOWN
     */
    public static int get() {
        if (!detected) {
            synchronized (GameVersion.class) {
                if (!detected) {
                    cachedVersion = detectVersion();
                    detected = true;
                    log("Detected game version: Build " + cachedVersion);
                }
            }
        }
        return cachedVersion;
    }

    /**
     * Build 41인지 확인.
     */
    public static boolean isBuild41() {
        return get() == BUILD_41;
    }

    /**
     * Build 42 이상인지 확인.
     */
    public static boolean isBuild42OrLater() {
        int v = get();
        return v >= BUILD_42;
    }

    /**
     * 버전 문자열 반환.
     */
    public static String getVersionString() {
        int v = get();
        if (v == UNKNOWN)
            return "Unknown";
        return "Build " + v;
    }

    /**
     * 수동 버전 설정 (테스트/오버라이드용).
     * 
     * @param version BUILD_41 또는 BUILD_42
     */
    public static void override(int version) {
        cachedVersion = version;
        detected = true;
        log("Version manually set to: Build " + version);
    }

    /**
     * 캐시 초기화 (테스트용).
     */
    public static void reset() {
        cachedVersion = UNKNOWN;
        detected = false;
    }

    // ═══════════════════════════════════════════════════════════════
    // Detection Logic
    // ═══════════════════════════════════════════════════════════════

    private static int detectVersion() {
        // 1. 시스템 프로퍼티 오버라이드 확인
        String override = System.getProperty("pulse.game.version");
        if (override != null) {
            try {
                return Integer.parseInt(override);
            } catch (NumberFormatException ignored) {
            }
        }

        // 2. Build 42 전용 클래스/메서드 확인
        if (hasBuild42Features()) {
            return BUILD_42;
        }

        // 3. Build 41 클래스 구조 확인
        if (hasBuild41Features()) {
            return BUILD_41;
        }

        // 4. 폴백: Build 41로 가정 (안전한 기본값)
        log("Version detection inconclusive, defaulting to Build 41");
        return BUILD_41;
    }

    /**
     * Build 42 전용 기능 확인.
     * 
     * Build 42에서 추가되는 클래스/메서드를 여기서 확인합니다.
     * 아직 Build 42가 출시되지 않았으므로 placeholder입니다.
     */
    private static boolean hasBuild42Features() {
        try {
            // Build 42 전용 클래스가 있으면 true
            Class.forName("zombie.core.engine.Engine");
            return true;
        } catch (ClassNotFoundException e) {
            return false;
        }
    }

    /**
     * Build 41 특징 확인.
     */
    private static boolean hasBuild41Features() {
        try {
            // IsoZombie 클래스 존재 확인
            Class<?> zombieClass = Class.forName("zombie.characters.IsoZombie");

            // Build 41의 메서드 시그니처 확인
            zombieClass.getMethod("getOnlineID");
            zombieClass.getMethod("getTarget");

            return true;
        } catch (ClassNotFoundException | NoSuchMethodException e) {
            return false;
        }
    }

    private static void log(String message) {
        System.out.println("[Pulse/GameVersion] " + message);
    }
}
