package com.pulse.api;

import com.pulse.runtime.PulseReflection;
import com.pulse.runtime.PulseRuntime;

/**
 * Pulse 환경 정보 API.
 * 
 * 게임 버전, 런타임 환경 등의 정보를 제공합니다.
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * // 게임 버전 확인
 * if (PulseEnvironment.isB42()) {
 *     // B42 전용 로직
 * }
 * 
 * // Pulse 버전
 * String version = PulseEnvironment.getPulseVersion();
 * }</pre>
 * 
 * @since Pulse 1.2
 */
public final class PulseEnvironment {

    private static final String PULSE_VERSION = "1.2.0";

    private PulseEnvironment() {
    }

    // ─────────────────────────────────────────────────────────────
    // Pulse 정보
    // ─────────────────────────────────────────────────────────────

    /**
     * Pulse 버전
     */
    public static String getPulseVersion() {
        return PULSE_VERSION;
    }

    // ─────────────────────────────────────────────────────────────
    // 게임 버전
    // ─────────────────────────────────────────────────────────────

    /**
     * 게임 버전 (B41/B42/UNKNOWN)
     */
    public static PulseRuntime.Version getGameVersion() {
        return PulseRuntime.getVersion();
    }

    /**
     * 게임 버전 문자열
     */
    public static String getGameVersionString() {
        return PulseRuntime.getVersionString();
    }

    /**
     * B41 여부
     */
    public static boolean isB41() {
        return PulseRuntime.isB41();
    }

    /**
     * B42 여부
     */
    public static boolean isB42() {
        return PulseRuntime.isB42();
    }

    // ─────────────────────────────────────────────────────────────
    // 런타임 환경
    // ─────────────────────────────────────────────────────────────

    /**
     * Java 버전
     */
    public static String getJavaVersion() {
        return System.getProperty("java.version");
    }

    /**
     * OS 이름
     */
    public static String getOsName() {
        return System.getProperty("os.name");
    }

    /**
     * 서버 환경 여부
     */
    public static boolean isDedicatedServer() {
        // zombie.network.GameServer 클래스의 bServer 필드 확인
        Object bServer = PulseReflection.findField("zombie.network.GameServer", "bServer");
        return Boolean.TRUE.equals(bServer);
    }

    /**
     * 클라이언트 환경 여부
     */
    public static boolean isClient() {
        return !isDedicatedServer();
    }

    // ─────────────────────────────────────────────────────────────
    // 유틸리티
    // ─────────────────────────────────────────────────────────────

    /**
     * 게임 클래스 존재 여부 확인
     */
    public static boolean classExists(String className) {
        return PulseReflection.classExists(className);
    }

    /**
     * 게임 메서드 존재 여부 확인
     */
    public static boolean methodExists(String className, String methodName) {
        return PulseReflection.methodExists(className, methodName);
    }

    /**
     * 환경 정보 요약
     */
    public static String getSummary() {
        return String.format(
                "Pulse %s | Game %s | Java %s | %s",
                PULSE_VERSION, getGameVersionString(), getJavaVersion(), getOsName());
    }
}
