package com.pulse.api;

import com.pulse.api.log.PulseLogger;
import com.pulse.PulseEnvironment;
import com.pulse.event.EventBus;
import com.pulse.mod.ModContainer;
import com.pulse.mod.ModLoader;
import com.pulse.service.ProviderRegistry;
import com.pulse.api.spi.IProviderRegistry;

import java.nio.file.Path;
import java.util.Collection;
import java.util.Optional;

/** Pulse API 메인 진입점 - 모드 개발자용 안정적 API */
public final class Pulse {

    private static final String LOG = PulseLogger.PULSE;

    private Pulse() {
    } // 인스턴스화 방지

    // Version

    public static final String VERSION = "0.8.0";
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

    // Mod

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

    // Event Bus

    /**
     * 이벤트 버스 접근
     */
    public static EventBus getEventBus() {
        return EventBus.getInstance();
    }

    // SPI

    /**
     * 프로바이더 레지스트리 접근.
     * 모든 SPI 프로바이더를 등록하고 조회할 수 있음.
     * 
     * 사용 예:
     * Pulse.getProviderRegistry().register(myProfiler);
     * Pulse.getProviderRegistry().getProvider(IProfilerProvider.class);
     */
    public static IProviderRegistry getProviderRegistry() {
        return ProviderRegistry.getInstance();
    }

    /**
     * 특정 타입의 프로바이더가 있는지 확인
     */
    public static <T extends com.pulse.api.spi.IProvider> boolean hasProvider(Class<T> type) {
        return ProviderRegistry.getInstance().hasProvider(type);
    }

    // Environment

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
        return getGameDirectory().resolve(PulseConstants.CONFIG_DIR_NAME);
    }

    // Side API

    private static volatile PulseSide currentSide = PulseSide.UNKNOWN;

    /**
     * 현재 실행 사이드 반환.
     * 
     * @return 현재 사이드 (CLIENT, DEDICATED_SERVER, INTEGRATED_SERVER, UNKNOWN)
     */
    public static PulseSide getSide() {
        if (currentSide == PulseSide.UNKNOWN) {
            currentSide = detectSide();
        }
        return currentSide;
    }

    /**
     * 클라이언트 환경인지 확인.
     * 싱글플레이어(INTEGRATED_SERVER)도 클라이언트 역할을 포함.
     * 
     * @return 클라이언트면 true
     */
    public static boolean isClient() {
        return getSide().isClient();
    }

    /**
     * 서버 환경인지 확인.
     * 싱글플레이어(INTEGRATED_SERVER)도 서버 역할을 포함.
     * 
     * @return 서버면 true
     */
    public static boolean isServer() {
        return getSide().isServer();
    }

    /**
     * 데디케이티드 서버인지 확인.
     * 
     * @return 데디케이티드 서버면 true
     */
    public static boolean isDedicatedServer() {
        return getSide().isDedicated();
    }

    /**
     * 사이드 설정 (내부용).
     * 
     * @param side 설정할 사이드
     */
    @InternalAPI
    public static void setSide(PulseSide side) {
        if (side != null) {
            currentSide = side;
            PulseLogger.debug(LOG, "Side set to: {}", side);
        }
    }

    /**
     * 사이드 자동 감지.
     */
    private static PulseSide detectSide() {
        try {
            // GameServer 클래스 로드 시도
            Class<?> gameServerClass = Class.forName("zombie.network.GameServer");
            java.lang.reflect.Field bServerField = gameServerClass.getDeclaredField("bServer");
            bServerField.setAccessible(true);
            boolean isServer = bServerField.getBoolean(null);

            if (isServer) {
                // 서버 모드 - 헤드리스인지 확인
                try {
                    Class<?> gameWindowClass = Class.forName("zombie.GameWindow");
                    java.lang.reflect.Field bNoRenderField = gameWindowClass.getDeclaredField("bNoRender");
                    bNoRenderField.setAccessible(true);
                    boolean noRender = bNoRenderField.getBoolean(null);

                    return noRender ? PulseSide.DEDICATED_SERVER : PulseSide.INTEGRATED_SERVER;
                } catch (Exception e) {
                    // 렌더링 체크 실패 - 아마도 데디케이티드
                    return PulseSide.DEDICATED_SERVER;
                }
            } else {
                // 클라이언트 모드
                return PulseSide.CLIENT;
            }
        } catch (ClassNotFoundException e) {
            // 게임 클래스 로드 전 - 나중에 다시 감지
            return PulseSide.UNKNOWN;
        } catch (Exception e) {
            PulseLogger.warn(LOG, "Side detection failed: {}", e.getMessage());
            return PulseSide.UNKNOWN;
        }
    }

    // DevMode

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
    // 로깅 (PulseLogger로 위임)
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
        PulseLogger.info(LOG, message);
    }

    /**
     * 모드 로그 출력 (modId prefix 포함)
     */
    public static void log(String modId, String message) {
        PulseLogger.info(modId, message);
    }

    /**
     * Pulse 경고 출력
     */
    public static void warn(String message) {
        PulseLogger.warn(LOG, message);
    }

    /**
     * 모드 경고 출력
     */
    public static void warn(String modId, String message) {
        PulseLogger.warn(modId, message);
    }

    /**
     * Pulse 에러 출력
     */
    public static void error(String message) {
        PulseLogger.error(LOG, message);
    }

    /**
     * 모드 에러 출력
     */
    public static void error(String modId, String message) {
        PulseLogger.error(modId, message);
    }

    /**
     * Pulse 에러 출력 (예외 포함)
     */
    public static void error(String message, Throwable t) {
        PulseLogger.error(LOG, "{}: {}", message, t.getMessage());
        t.printStackTrace();
    }

    /**
     * 모드 에러 출력 (예외 포함)
     */
    public static void error(String modId, String message, Throwable t) {
        PulseLogger.error(modId, "{}: {}", message, t.getMessage());
        t.printStackTrace();
    }
}
