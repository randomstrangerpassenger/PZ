package com.pulse.runtime;

/**
 * Pulse 런타임 환경 정보.
 * 
 * 게임 버전(B41/B42)을 감지하고, 버전별 분기가 필요한 로직에서 사용합니다.
 * 로드맵의 "Version Abstraction" 요구사항을 충족합니다.
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * if (PulseRuntime.isB42()) {
 *     // B42 전용 로직
 * } else {
 *     // B41 로직
 * }
 * }</pre>
 * 
 * @since Pulse 1.2
 */
public final class PulseRuntime {

    /**
     * Project Zomboid 버전
     */
    public enum Version {
        B41("Build 41"),
        B42("Build 42"),
        UNKNOWN("Unknown");

        private final String displayName;

        Version(String displayName) {
            this.displayName = displayName;
        }

        public String getDisplayName() {
            return displayName;
        }
    }

    private static volatile Version detectedVersion = null;
    private static volatile String versionString = null;
    private static volatile boolean initialized = false;

    private PulseRuntime() {
    }

    /**
     * 게임 버전 감지 (게임 초기화 시 호출)
     */
    public static void detectVersion() {
        if (initialized) {
            return;
        }
        initialized = true;

        try {
            // 방법 1: Core.getInstance().getVersion() 시도
            Class<?> coreClass = Class.forName("zombie.core.Core");
            Object coreInstance = coreClass.getMethod("getInstance").invoke(null);
            Object versionObj = coreClass.getMethod("getVersion").invoke(coreInstance);

            if (versionObj != null) {
                versionString = versionObj.toString();
                detectedVersion = parseVersion(versionString);
                System.out
                        .println("[Pulse/Runtime] Detected game version: " + versionString + " -> " + detectedVersion);
                return;
            }
        } catch (Exception e) {
            // 방법 1 실패, 다음 시도
        }

        try {
            // 방법 2: GameVersion 클래스 확인
            Class.forName("zombie.GameVersion");
            java.lang.reflect.Field versionField = Class.forName("zombie.GameVersion").getField("VERSION");
            versionString = (String) versionField.get(null);
            detectedVersion = parseVersion(versionString);
            System.out.println(
                    "[Pulse/Runtime] Detected game version (GameVersion): " + versionString + " -> " + detectedVersion);
            return;
        } catch (Exception e) {
            // 방법 2 실패
        }

        try {
            // 방법 3: 클래스 존재 여부로 판단 (B42 전용 클래스)
            Class.forName("zombie.core.opengl.ShaderProgram"); // B42에만 존재하는 클래스 예시
            detectedVersion = Version.B42;
            versionString = "B42 (inferred)";
            System.out.println("[Pulse/Runtime] Inferred game version: B42");
            return;
        } catch (ClassNotFoundException e) {
            // B42 전용 클래스 없음 - B41로 추정
        }

        // 기본값: B41로 추정
        detectedVersion = Version.B41;
        versionString = "B41 (default)";
        System.out.println("[Pulse/Runtime] Defaulting to: B41");
    }

    private static Version parseVersion(String version) {
        if (version == null)
            return Version.UNKNOWN;
        String lower = version.toLowerCase();
        if (lower.contains("42") || lower.contains("b42")) {
            return Version.B42;
        } else if (lower.contains("41") || lower.contains("b41")) {
            return Version.B41;
        }
        return Version.UNKNOWN;
    }

    /**
     * 현재 감지된 버전
     */
    public static Version getVersion() {
        if (!initialized) {
            detectVersion();
        }
        return detectedVersion != null ? detectedVersion : Version.UNKNOWN;
    }

    /**
     * 버전 문자열
     */
    public static String getVersionString() {
        if (!initialized) {
            detectVersion();
        }
        return versionString != null ? versionString : "Unknown";
    }

    /**
     * B41 여부
     */
    public static boolean isB41() {
        return getVersion() == Version.B41;
    }

    /**
     * B42 여부
     */
    public static boolean isB42() {
        return getVersion() == Version.B42;
    }

    /**
     * 버전별 분기 실행
     */
    public static <T> T versionSwitch(T b41Value, T b42Value) {
        return isB42() ? b42Value : b41Value;
    }

    /**
     * 상태 요약
     */
    public static String getStatus() {
        return String.format("PulseRuntime: version=%s, string=%s, initialized=%s",
                detectedVersion, versionString, initialized);
    }
}
