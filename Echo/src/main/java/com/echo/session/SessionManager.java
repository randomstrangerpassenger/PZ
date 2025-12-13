package com.echo.session;

import com.echo.config.EchoConfig;
import com.echo.measure.EchoProfiler;
import com.echo.report.EchoReport;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 * Echo 세션 관리자
 * 
 * 싱글플레이/멀티플레이 세션 단위로 프로파일링 데이터를 관리합니다.
 * - 세션 시작: 프로파일러 리셋
 * - 세션 종료: 비동기 리포트 저장
 * - Shutdown: 동기 리포트 저장 (비정상 종료 대비)
 * 
 * @since 2.1.0
 */
public class SessionManager {

    private static final SessionManager INSTANCE = new SessionManager();

    // --- 세션 상태 ---
    private volatile boolean sessionActive = false;
    private volatile boolean sessionSaved = false;
    private volatile boolean dirty = false;
    private volatile String currentWorldName = null;
    private volatile boolean isMultiplayer = false;

    // --- dirty 최소 조건 (10초 = 600틱) ---
    private volatile int tickCount = 0;
    private static final int MIN_TICKS_FOR_DIRTY = 600;

    // --- 비동기 저장 ---
    private final ExecutorService saveExecutor = Executors.newSingleThreadExecutor(r -> new Thread(r, "Echo-Save"));

    private SessionManager() {
        // Singleton
    }

    public static SessionManager getInstance() {
        return INSTANCE;
    }

    // --- 세션 라이프사이클 ---

    /**
     * 월드 로드 시 호출 (세션 시작)
     */
    public void onWorldLoad(String worldName, boolean multiplayer) {
        if (!sessionActive) {
            sessionActive = true;
            sessionSaved = false;
            dirty = false;
            tickCount = 0;
            currentWorldName = worldName;
            isMultiplayer = multiplayer;

            EchoProfiler.getInstance().reset();
            System.out.println("[Echo] Session started: " + worldName +
                    (multiplayer ? " (MP)" : " (SP)"));
        }
    }

    /**
     * 월드 언로드 시 호출 (세션 종료)
     */
    public void onWorldUnload() {
        if (sessionActive && dirty) {
            sessionActive = false; // 먼저 차단하여 추가 틱 방지
            saveAsync();
            System.out.println("[Echo] Session ended - saving report asynchronously");
        } else if (sessionActive) {
            sessionActive = false;
            System.out.println("[Echo] Session ended - no data to save (tickCount=" + tickCount + ")");
        }
    }

    /**
     * 틱 완료 시 호출 (데이터 수집 마킹)
     */
    public void onTick() {
        if (!sessionActive)
            return;

        tickCount++;
        if (tickCount >= MIN_TICKS_FOR_DIRTY && !dirty) {
            dirty = true;
            System.out.println("[Echo] Session marked dirty (sufficient data collected)");
        }
    }

    // --- 저장 ---

    /**
     * 비동기 저장 (메뉴 복귀 시 프리즈 방지)
     */
    private void saveAsync() {
        if (!EchoConfig.getInstance().isAutoSaveReports()) {
            sessionSaved = true;
            return;
        }

        EchoReport report = new EchoReport(EchoProfiler.getInstance());
        saveExecutor.submit(() -> {
            if (saveReport(report)) {
                sessionSaved = true; // 성공 시에만 플래그 설정
            }
        });
    }

    /**
     * 동기 저장 (shutdown hook용)
     */
    public void saveSync() {
        if (!hasUnsavedData())
            return;
        if (!EchoConfig.getInstance().isAutoSaveReports())
            return;

        EchoReport report = new EchoReport(EchoProfiler.getInstance());
        if (saveReport(report)) {
            sessionSaved = true;
        }
    }

    /**
     * 리포트 저장 실행
     * 
     * @return 성공 여부
     */
    private boolean saveReport(EchoReport report) {
        try {
            EchoConfig config = EchoConfig.getInstance();
            String path = report.saveWithTimestamp(config.getReportDirectory());
            report.printQualitySummary();
            System.out.println("[Echo] Report saved: " + path);
            return true;
        } catch (Exception e) {
            System.err.println("[Echo] Failed to save report: " + e.getMessage());
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
        return sessionActive && dirty && !sessionSaved;
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
        sessionSaved = false;
        dirty = false;
        tickCount = 0;
        currentWorldName = null;
        isMultiplayer = false;
    }
}
