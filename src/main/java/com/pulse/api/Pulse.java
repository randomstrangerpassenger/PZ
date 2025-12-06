package com.pulse.api;

import com.pulse.PulseEnvironment;
import com.pulse.event.EventBus;
import com.pulse.mod.ModContainer;
import com.pulse.mod.ModLoader;

import java.nio.file.Path;
import java.util.Collection;
import java.util.Optional;

/**
 * Pulse API 메인 진입점.
 * 모드 개발자가 사용하는 안정적인 API.
 * 
 * 사용 예:
 * if (Pulse.isModLoaded("othermod")) {
 * // othermod와 연동
 * }
 */
public final class Pulse {

    private Pulse() {
    } // 인스턴스화 방지

    // ─────────────────────────────────────────────────────────────
    // 버전 정보
    // ─────────────────────────────────────────────────────────────

    public static final String VERSION = "1.0.0";
    public static final String NAME = "Pulse";
    public static final int API_VERSION = 1;

    /**
     * Pulse 버전 반환
     */
    public static String getVersion() {
        return VERSION;
    }

    /**
     * API 버전 반환 (호환성 체크용)
     */
    public static int getApiVersion() {
        return API_VERSION;
    }

    // ─────────────────────────────────────────────────────────────
    // 모드 관련
    // ─────────────────────────────────────────────────────────────

    /**
     * 특정 모드가 로드되었는지 확인
     */
    public static boolean isModLoaded(String modId) {
        return ModLoader.getInstance().isModLoaded(modId);
    }

    /**
     * 모드 컨테이너 가져오기
     */
    public static Optional<ModContainer> getMod(String modId) {
        return Optional.ofNullable(ModLoader.getInstance().getMod(modId));
    }

    /**
     * 로드된 모든 모드 목록
     */
    public static Collection<ModContainer> getAllMods() {
        return ModLoader.getInstance().getAllMods();
    }

    /**
     * 로드된 모드 수
     */
    public static int getModCount() {
        return ModLoader.getInstance().getModCount();
    }

    // ─────────────────────────────────────────────────────────────
    // 이벤트 시스템
    // ─────────────────────────────────────────────────────────────

    /**
     * 이벤트 버스 접근
     */
    public static EventBus getEventBus() {
        return EventBus.getInstance();
    }

    // ─────────────────────────────────────────────────────────────
    // 환경 정보
    // ─────────────────────────────────────────────────────────────

    /**
     * Pulse이 완전히 초기화되었는지 확인
     */
    public static boolean isInitialized() {
        return PulseEnvironment.isInitialized();
    }

    /**
     * 게임 디렉토리 경로
     */
    public static Path getGameDirectory() {
        return Path.of(System.getProperty("user.dir"));
    }

    /**
     * mods 디렉토리 경로
     */
    public static Path getModsDirectory() {
        return ModLoader.getInstance().getModsDirectory();
    }

    /**
     * 설정 디렉토리 경로
     */
    public static Path getConfigDirectory() {
        return getGameDirectory().resolve("config");
    }

    // ─────────────────────────────────────────────────────────────
    // DevMode
    // ─────────────────────────────────────────────────────────────

    /**
     * DevMode 활성화 여부 확인
     */
    public static boolean isDevMode() {
        return DevMode.isEnabled();
    }

    /**
     * DevMode 활성화
     */
    public static void enableDevMode() {
        DevMode.enable();
    }

    // ─────────────────────────────────────────────────────────────
    // 로깅
    // ─────────────────────────────────────────────────────────────

    /**
     * 모드별 로거 가져오기
     */
    public static ModLogger getLogger(String modId) {
        return ModLogger.getLogger(modId);
    }

    /**
     * Pulse 로그 출력
     */
    public static void log(String message) {
        System.out.println("[Pulse] " + message);
    }

    /**
     * 모드 로그 출력 (modId prefix 포함)
     */
    public static void log(String modId, String message) {
        System.out.println("[Mod/" + modId + "] " + message);
    }

    /**
     * Pulse 경고 출력
     */
    public static void warn(String message) {
        System.out.println("[Pulse/WARN] " + message);
    }

    /**
     * 모드 경고 출력
     */
    public static void warn(String modId, String message) {
        System.out.println("[Mod/" + modId + "/WARN] " + message);
    }

    /**
     * Pulse 에러 출력
     */
    public static void error(String message) {
        System.err.println("[Pulse/ERROR] " + message);
    }

    /**
     * 모드 에러 출력
     */
    public static void error(String modId, String message) {
        System.err.println("[Mod/" + modId + "/ERROR] " + message);
    }

    /**
     * Pulse 에러 출력 (예외 포함)
     */
    public static void error(String message, Throwable t) {
        System.err.println("[Pulse/ERROR] " + message);
        t.printStackTrace();
    }

    /**
     * 모드 에러 출력 (예외 포함)
     */
    public static void error(String modId, String message, Throwable t) {
        System.err.println("[Mod/" + modId + "/ERROR] " + message);
        t.printStackTrace();
    }
}
