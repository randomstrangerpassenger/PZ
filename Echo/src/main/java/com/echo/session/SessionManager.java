package com.echo.session;

import com.echo.EchoConstants;
import com.echo.config.EchoConfig;
import com.echo.measure.EchoProfiler;
import com.echo.report.EchoReport;
import com.pulse.api.log.PulseLogger;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 * Echo 세션 관리자
 * 
 * 싱글플레이/멀티플레이 세션 단위로 프로파일링 데이터를 관리합니다.
 * - 세션 시작: 프로파일러 리셋
 * - 세션 종료: 비동기 리포트 저장 (MainMenuRenderEvent)
 * - Shutdown: 동기 리포트 저장 (비정상 종료 대비)
 * 
 * @since 2.1.0 - MainMenuRenderEvent 기반 세션 종료 감지
 */
public class SessionManager {

    private static final SessionManager INSTANCE = new SessionManager();

    // --- 세션 상태 ---
    private volatile boolean sessionActive = false;
    private volatile boolean dirty = false;
    private volatile String currentWorldName = null;
    private volatile boolean isMultiplayer = false;

    // --- dirty 최소 조건 ---
    private volatile int tickCount = 0;

    // --- 메인 메뉴 렌더 기반 세션 종료 감지 ---
    private volatile int menuRenderCount = 0;

    // --- 메인 메뉴 상태 (false 세션 방지) ---
    private volatile boolean onMainMenu = true;

    // --- 메인 메뉴 이탈 감지 (틱 기반) ---
    private volatile int ticksSinceMenuRender = 0;

    // --- 비동기 저장 ---
    private final ExecutorService saveExecutor = Executors.newSingleThreadExecutor(r -> new Thread(r, "Echo-Save"));

    private SessionManager() {
    }

    public static SessionManager getInstance() {
        return INSTANCE;
    }

    // --- 세션 라이프사이클 ---

    /**
     * 월드 로드 시 호출 (세션 시작)
     */
    public void onWorldLoad(String worldName, boolean multiplayer) {
        // 메인 메뉴 플래그 해제 - 게임에 진입함
        onMainMenu = false;

        if (!sessionActive) {
            sessionActive = true;
            dirty = false;
            tickCount = 0;
            currentWorldName = worldName;
            isMultiplayer = multiplayer;

            EchoProfiler.getInstance().reset();
            PulseLogger.info("Echo", "Session started: " + worldName +
                    (multiplayer ? " (MP)" : " (SP)"));
        }
    }

    public void onWorldUnload() {
        if (sessionActive && dirty) {
            sessionActive = false;
            saveAsync();
            PulseLogger.info("Echo", "Session ended - saving report");
        } else if (sessionActive) {
            sessionActive = false;
            PulseLogger.debug("Echo", "Session ended - no data to save (tickCount=" + tickCount + ")");
        }
        menuRenderCount = 0;
    }

    /**
     * 메인 메뉴 렌더 시 호출 (세션이 활성 상태면 종료 감지)
     * 
     * 게임 중에는 MainScreenState.render()가 호출되지 않으므로,
     * 이 메서드가 호출되면 메인 메뉴로 돌아온 것입니다.
     */
    public void onMainMenuRender() {
        // 메인 메뉴 플래그 설정 - 새 세션 시작 방지
        onMainMenu = true;

        // 틱 카운터 리셋 - 메뉴 렌더가 호출되면 아직 메인 메뉴임
        ticksSinceMenuRender = 0;

        // 메인 메뉴에서는 wasWorldLoaded를 현재 상태로 동기화
        // 이렇게 하면 onTick()의 false→true 전환 감지가 작동하지 않음
        wasWorldLoaded = com.pulse.api.access.WorldAccess.isWorldLoaded();

        if (!sessionActive) {
            menuRenderCount = 0;
            return;
        }

        menuRenderCount++;

        if (menuRenderCount >= EchoConstants.MENU_RENDER_THRESHOLD && dirty) {
            PulseLogger.info("Echo", "Menu detected (" + menuRenderCount + " frames) - saving session");
            sessionActive = false;
            dirty = false;
            tickCount = 0;
            saveAsync();
            menuRenderCount = 0;
        }
    }

    // --- Mixin 실패 대비: 월드 상태 변화 감지 ---
    private volatile boolean wasWorldLoaded = false;

    /**
     * 틱 완료 시 호출 (데이터 수집 마킹)
     * 
     * Pulse GameStateAccess와 WorldAccess를 사용하여 정확한 상태 감지.
     * - GameStateAccess.isOnMainMenu(): 메인 메뉴 상태 확인
     * - WorldAccess.isWorldLoaded(): 월드 로드 상태 확인 (Cell 존재 여부 포함)
     * 
     * @since 2.1.1 - Pulse GameStateAccess 기반으로 개선
     */
    public void onTick() {
        // Phase 1: Pulse API로 현재 상태 확인
        boolean isOnMainMenuNow = com.pulse.api.access.GameStateAccess.isOnMainMenu();
        boolean isWorldLoaded = com.pulse.api.access.WorldAccess.isWorldLoaded();

        // 메인 메뉴 상태 동기화 (Pulse API 결과 반영)
        if (isOnMainMenuNow) {
            onMainMenu = true;
            ticksSinceMenuRender = 0;
        } else if (onMainMenu) {
            // 틱 기반 감지 (GameStateAccess 실패 시 폴백)
            ticksSinceMenuRender++;
            if (ticksSinceMenuRender >= EchoConstants.MENU_EXIT_THRESHOLD) {
                onMainMenu = false;
                wasWorldLoaded = false;
                PulseLogger.debug("Echo",
                        "Game entered (fallback: no menu render for " + ticksSinceMenuRender + " ticks)");
            }
        }

        // 세션이 없을 때: 게임 진입 및 월드 로드 감지
        if (!sessionActive) {
            // 메인 메뉴에서는 세션 시작하지 않음 (wasWorldLoaded 업데이트하지 않음)
            if (onMainMenu || isOnMainMenuNow) {
                // 중요: wasWorldLoaded를 업데이트하지 않음 - 게임 진입 후 false→true 감지 보장
                return;
            }

            // 월드 로드 상태가 false→true로 변경됐을 때 또는 게임 진입 직후 월드가 로드된 경우
            if (isWorldLoaded && !wasWorldLoaded) {
                sessionActive = true;
                dirty = false;
                tickCount = 0;
                currentWorldName = com.pulse.api.access.WorldAccess.getWorldName();
                if (currentWorldName == null || currentWorldName.isEmpty()) {
                    currentWorldName = "AutoDetected";
                }
                isMultiplayer = isMultiplayerWorld();

                EchoProfiler.getInstance().reset();
                PulseLogger.info("Echo", "Session started (world: " + currentWorldName + ")");
            }
            wasWorldLoaded = isWorldLoaded;
            return;
        }

        // 세션이 활성 상태: 틱 카운트 증가
        tickCount++;
        if (tickCount >= EchoConstants.MIN_TICKS_FOR_DIRTY && !dirty) {
            dirty = true;
            PulseLogger.debug("Echo", "Session marked dirty (sufficient data)");
        }

        wasWorldLoaded = isWorldLoaded;
    }

    private boolean isMultiplayerWorld() {
        try {
            Class<?> gameClient = Class.forName("zombie.network.GameClient");
            java.lang.reflect.Field bClient = gameClient.getField("bClient");
            return Boolean.TRUE.equals(bClient.get(null));
        } catch (Exception e) {
            return false;
        }
    }

    // --- 저장 ---

    /**
     * 비동기 저장 (메뉴 복귀 시 프리즈 방지)
     */
    private void saveAsync() {
        if (!EchoConfig.getInstance().isAutoSaveReports()) {
            return;
        }

        EchoReport report = new EchoReport(EchoProfiler.getInstance());
        saveExecutor.submit(() -> saveReport(report));
    }

    /**
     * 동기 저장 (shutdown hook용)
     */
    public void saveSync() {
        boolean shouldSave = sessionActive && tickCount > 0;

        if (!shouldSave) {
            return;
        }
        if (!EchoConfig.getInstance().isAutoSaveReports()) {
            return;
        }

        PulseLogger.info("Echo", "Shutdown - saving session...");
        EchoReport report = new EchoReport(EchoProfiler.getInstance());
        saveReport(report);
    }

    private boolean saveReport(EchoReport report) {
        try {
            EchoConfig config = EchoConfig.getInstance();
            String path = report.saveWithTimestamp(config.getReportDirectory());
            report.printQualitySummary();
            PulseLogger.info("Echo", "Report saved: " + path);
            return true;
        } catch (Exception e) {
            PulseLogger.error("Echo", "Failed to save report: " + e.getMessage());
            return false;
        }
    }

    // --- Executor 종료 ---

    /**
     * Executor 정리 (shutdown hook에서 호출)
     */
    public void shutdownExecutor() {
        saveExecutor.shutdown();
        try {
            if (!saveExecutor.awaitTermination(2, TimeUnit.SECONDS)) {
                saveExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            saveExecutor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }

    // --- 상태 조회 ---

    public boolean hasUnsavedData() {
        return sessionActive && dirty;
    }

    public boolean isSessionActive() {
        return sessionActive;
    }

    public String getCurrentWorldName() {
        return currentWorldName;
    }

    public boolean isMultiplayer() {
        return isMultiplayer;
    }

    public int getTickCount() {
        return tickCount;
    }

    /**
     * 테스트용 리셋
     */
    public void resetForTest() {
        sessionActive = false;
        dirty = false;
        tickCount = 0;
        currentWorldName = null;
        isMultiplayer = false;
        onMainMenu = true;
        ticksSinceMenuRender = 0;
        wasWorldLoaded = false;
    }
}
