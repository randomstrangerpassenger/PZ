package com.mutagen.api;

import com.mutagen.MutagenEnvironment;
import com.mutagen.event.EventBus;
import com.mutagen.mod.ModContainer;
import com.mutagen.mod.ModLoader;

import java.nio.file.Path;
import java.util.Collection;
import java.util.Optional;

/**
 * Mutagen API 메인 진입점.
 * 모드 개발자가 사용하는 안정적인 API.
 * 
 * 사용 예:
 * if (Mutagen.isModLoaded("othermod")) {
 *     // othermod와 연동
 * }
 */
public final class Mutagen {
    
    private Mutagen() {} // 인스턴스화 방지
    
    // ─────────────────────────────────────────────────────────────
    // 버전 정보
    // ─────────────────────────────────────────────────────────────
    
    public static final String VERSION = "1.0.0";
    public static final String NAME = "Mutagen";
    public static final int API_VERSION = 1;
    
    /**
     * Mutagen 버전 반환
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
     * Mutagen이 완전히 초기화되었는지 확인
     */
    public static boolean isInitialized() {
        return MutagenEnvironment.isInitialized();
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
    // 로깅
    // ─────────────────────────────────────────────────────────────
    
    /**
     * Mutagen 로그 출력
     */
    public static void log(String message) {
        System.out.println("[Mutagen] " + message);
    }
    
    /**
     * Mutagen 경고 출력
     */
    public static void warn(String message) {
        System.out.println("[Mutagen/WARN] " + message);
    }
    
    /**
     * Mutagen 에러 출력
     */
    public static void error(String message) {
        System.err.println("[Mutagen/ERROR] " + message);
    }
    
    /**
     * Mutagen 에러 출력 (예외 포함)
     */
    public static void error(String message, Throwable t) {
        System.err.println("[Mutagen/ERROR] " + message);
        t.printStackTrace();
    }
}
