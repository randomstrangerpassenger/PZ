package com.echo.ui;

import com.echo.EchoRuntime;
import com.echo.EchoMod;
import com.echo.input.EchoKeyBindings;
import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;
import com.echo.aggregate.TimingData;
import com.echo.pulse.PulseMetricsAdapter;

import com.pulse.ui.HUDOverlay;
import com.pulse.ui.UIRenderContext;

import java.util.List;
import java.util.Map;

/**
 * Echo HUD - 인게임 성능 오버레이
 * 
 * Pulse HUDOverlay 시스템을 통해 렌더링됩니다.
 * F6 키로 토글할 수 있습니다.
 * 
 * @since 2.0.0 - Pulse Native Integration
 */
public class EchoHUD extends HUDOverlay.HUDLayer {

    // ============================================================
    // 상수
    // ============================================================

    /** HUD 레이어 ID */
    public static final String LAYER_ID = "echo_hud";

    /** HUD 레이어 우선순위 (낮을수록 먼저 렌더링) */
    public static final int LAYER_PRIORITY = 100;

    /** HUD 갱신 주기 (밀리초) */
    private static final long UPDATE_INTERVAL_MS = 500;

    /** Top Hotspot 표시 개수 */
    private static final int TOP_HOTSPOT_COUNT = 3;

    /** HUD 패딩 */
    private static final int PADDING = 6;

    /** 줄 높이 */
    private static final int LINE_HEIGHT = 14;

    // ============================================================
    // 싱글톤 인스턴스
    // ============================================================

    private static EchoHUD INSTANCE;

    // ============================================================
    // 인스턴스 필드
    // ============================================================

    /** HUD 위치 */
    private int hudX = 10;
    private int hudY = 10;

    // ============================================================
    // 캐시 (0.5초마다 갱신)
    // ============================================================

    private long lastCacheUpdate = 0;

    // 캐시된 표시 값
    private String cachedFpsText = "FPS: --";
    private String cachedFrameTimeText = "Frame: --ms";
    private String cachedTickTimeText = "Tick: --ms";
    private String cachedProfileStatus = "[OFF]";
    private final String[] cachedHotspots = new String[TOP_HOTSPOT_COUNT];
    private final int[] cachedHotspotColors = new int[TOP_HOTSPOT_COUNT];

    private int fpsColor = EchoTheme.GOOD;
    private int frameTimeColor = EchoTheme.GOOD;
    private int tickTimeColor = EchoTheme.GOOD;

    // ============================================================
    // 생성자 및 등록
    // ============================================================

    private EchoHUD() {
        // Private constructor for singleton
    }

    /**
     * HUD 레이어 등록
     * EchoMod.init()에서 호출됨
     */
    public static void register() {
        if (INSTANCE != null) {
            System.out.println("[Echo] EchoHUD already registered");
            return;
        }

        INSTANCE = new EchoHUD();
        HUDOverlay.registerLayer(LAYER_ID, INSTANCE, LAYER_PRIORITY);
        System.out.println("[Echo] EchoHUD registered as Pulse HUD layer");
    }

    /**
     * HUD 레이어 등록 해제
     */
    public static void unregister() {
        if (INSTANCE == null)
            return;
        HUDOverlay.unregisterLayer(LAYER_ID);
        INSTANCE = null;
        System.out.println("[Echo] EchoHUD unregistered");
    }

    /**
     * 인스턴스 가져오기
     */
    public static EchoHUD getInstance() {
        return INSTANCE;
    }

    // ============================================================
    // HUDLayer 구현
    // ============================================================

    @Override
    public void render(UIRenderContext ctx) {
        // 안전 체크
        if (!EchoRuntime.isEnabled() || !EchoKeyBindings.isHudVisible()) {
            return;
        }

        try {
            updateCacheIfNeeded();
            renderHud(ctx);
        } catch (Exception e) {
            EchoRuntime.recordError("HUD", e);
        }
    }

    @Override
    public void update(float deltaTime) {
        // HUD는 render에서 캐시 갱신하므로 별도 업데이트 불필요
    }

    // ============================================================
    // 캐시 갱신
    // ============================================================

    /**
     * 캐시 갱신 (0.5초마다)
     */
    private void updateCacheIfNeeded() {
        long now = System.currentTimeMillis();
        if (now - lastCacheUpdate < UPDATE_INTERVAL_MS) {
            return;
        }
        lastCacheUpdate = now;

        // FPS / Frame Time / Tick Time
        double fps = PulseMetricsAdapter.getFps();
        double frameTimeMs = PulseMetricsAdapter.getFrameTimeMs();
        double tickTimeMs = PulseMetricsAdapter.getTickTimeMs();

        cachedFpsText = String.format("FPS: %.0f", fps);
        cachedFrameTimeText = String.format("Frame: %.1fms", frameTimeMs);
        cachedTickTimeText = String.format("Tick: %.1fms", tickTimeMs);

        fpsColor = EchoTheme.getGradeColor(PulseMetricsAdapter.getFpsGrade());
        frameTimeColor = EchoTheme.getGradeColor(PulseMetricsAdapter.getFrameTimeGrade());
        tickTimeColor = EchoTheme.getGradeColor(PulseMetricsAdapter.getTickTimeGrade());

        // 프로파일링 상태
        EchoProfiler profiler = EchoProfiler.getInstance();
        cachedProfileStatus = profiler.isEnabled() ? "[ON]" : "[OFF]";

        // Top Hotspots
        updateHotspots(profiler);
    }

    /**
     * Top Hotspot 갱신
     */
    private void updateHotspots(EchoProfiler profiler) {
        if (!profiler.isEnabled()) {
            for (int i = 0; i < TOP_HOTSPOT_COUNT; i++) {
                cachedHotspots[i] = null;
            }
            return;
        }

        Map<ProfilingPoint, TimingData> allData = profiler.getTimingData();

        // 5초 윈도우 평균 기준 정렬
        List<Map.Entry<ProfilingPoint, TimingData>> sorted = allData.entrySet().stream()
                .filter(e -> e.getValue().getCallCount() > 0)
                .sorted((a, b) -> {
                    double avgA = a.getValue().getStats5s().getAverage();
                    double avgB = b.getValue().getStats5s().getAverage();
                    return Double.compare(avgB, avgA); // 내림차순
                })
                .limit(TOP_HOTSPOT_COUNT)
                .toList();

        for (int i = 0; i < TOP_HOTSPOT_COUNT; i++) {
            if (i < sorted.size()) {
                Map.Entry<ProfilingPoint, TimingData> entry = sorted.get(i);
                ProfilingPoint point = entry.getKey();
                TimingData data = entry.getValue();
                double avgMs = data.getStats5s().getAverage() / 1000.0; // micros → ms

                cachedHotspots[i] = String.format("%d. %-10s %.2fms",
                        i + 1,
                        truncate(point.name(), 10),
                        avgMs);
                cachedHotspotColors[i] = getPointColor(point);
            } else {
                cachedHotspots[i] = null;
            }
        }
    }

    // ============================================================
    // 렌더링 (UIRenderContext 사용)
    // ============================================================

    /**
     * HUD 렌더링 (Pulse UI API 사용)
     */
    private void renderHud(UIRenderContext ctx) {
        // 배경 박스 크기 계산
        int lineCount = 4; // FPS, Frame, Tick, Status
        for (String hotspot : cachedHotspots) {
            if (hotspot != null)
                lineCount++;
        }
        int boxWidth = 150;
        int boxHeight = PADDING * 2 + lineCount * LINE_HEIGHT;

        // 배경 렌더링
        ctx.fillRect(hudX, hudY, boxWidth, boxHeight, EchoTheme.getBackgroundRGB(), EchoTheme.getBackgroundAlpha());

        // 텍스트 렌더링
        int y = hudY + PADDING;

        // FPS
        ctx.drawText(cachedFpsText, hudX + PADDING, y, fpsColor);
        // 프로파일링 상태 (오른쪽)
        int statusColor = cachedProfileStatus.equals("[ON]") ? EchoTheme.GOOD : EchoTheme.TEXT_SECONDARY;
        ctx.drawText(cachedProfileStatus, hudX + boxWidth - PADDING - 30, y, statusColor);
        y += LINE_HEIGHT;

        // Frame Time
        ctx.drawText(cachedFrameTimeText, hudX + PADDING, y, frameTimeColor);
        y += LINE_HEIGHT;

        // Tick Time
        ctx.drawText(cachedTickTimeText, hudX + PADDING, y, tickTimeColor);
        y += LINE_HEIGHT;

        // 구분선
        y += 2;

        // Hotspots
        for (int i = 0; i < TOP_HOTSPOT_COUNT; i++) {
            if (cachedHotspots[i] != null) {
                ctx.drawText(cachedHotspots[i], hudX + PADDING, y, cachedHotspotColors[i]);
                y += LINE_HEIGHT;
            }
        }
    }

    // ============================================================
    // 유틸리티
    // ============================================================

    /**
     * 문자열 자르기
     */
    private String truncate(String str, int maxLen) {
        if (str == null)
            return "";
        if (str.length() <= maxLen)
            return str;
        return str.substring(0, maxLen - 1) + "…";
    }

    /**
     * ProfilingPoint별 색상
     */
    private int getPointColor(ProfilingPoint point) {
        return switch (point) {
            case RENDER, RENDER_WORLD, RENDER_UI -> EchoTheme.SUBSYSTEM_RENDER;
            case ZOMBIE_AI, NPC_AI -> EchoTheme.SUBSYSTEM_AI;
            case PHYSICS, SIMULATION -> EchoTheme.SUBSYSTEM_PHYSICS;
            case NETWORK -> EchoTheme.SUBSYSTEM_NETWORK;
            case LUA_EVENT, LUA_FUNCTION, LUA_GC -> EchoTheme.SUBSYSTEM_LUA;
            case AUDIO -> EchoTheme.SUBSYSTEM_LIGHTING; // 오디오는 조명 색상 재사용
            default -> EchoTheme.SUBSYSTEM_OTHER;
        };
    }

    // ============================================================
    // 설정
    // ============================================================

    public void setPosition(int x, int y) {
        this.hudX = x;
        this.hudY = y;
    }

    public int getX() {
        return hudX;
    }

    public int getY() {
        return hudY;
    }

    // Static 호환성 메서드 (기존 코드 호환)
    public static void setHudPosition(int x, int y) {
        if (INSTANCE != null) {
            INSTANCE.setPosition(x, y);
        }
    }
}
