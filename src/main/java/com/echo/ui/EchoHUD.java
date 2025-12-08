package com.echo.ui;

import com.echo.EchoRuntime;
import com.echo.input.EchoKeyBindings;
import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;
import com.echo.aggregate.TimingData;
import com.echo.pulse.PulseMetricsAdapter;

import java.util.List;
import java.util.Map;

/**
 * Echo HUD - 인게임 성능 오버레이
 * 
 * 실시간 FPS, 프레임/틱 시간, 핫스팟 정보를 화면에 표시합니다.
 * F6 키로 토글할 수 있습니다.
 */
public class EchoHUD {

    // ============================================================
    // 상수
    // ============================================================

    /** HUD 갱신 주기 (밀리초) */
    private static final long UPDATE_INTERVAL_MS = 500;

    /** Top Hotspot 표시 개수 */
    private static final int TOP_HOTSPOT_COUNT = 3;

    /** HUD 위치 (왼쪽 상단 기준) */
    private static int hudX = 10;
    private static int hudY = 10;

    /** HUD 패딩 */
    private static final int PADDING = 6;

    /** 줄 높이 */
    private static final int LINE_HEIGHT = 14;

    // ============================================================
    // 캐시 (0.5초마다 갱신)
    // ============================================================

    private static final StringBuilder sb = new StringBuilder(512);
    private static long lastCacheUpdate = 0;

    // 캐시된 표시 값
    private static String cachedFpsText = "FPS: --";
    private static String cachedFrameTimeText = "Frame: --ms";
    private static String cachedTickTimeText = "Tick: --ms";
    private static String cachedProfileStatus = "[OFF]";
    private static String[] cachedHotspots = new String[TOP_HOTSPOT_COUNT];
    private static int[] cachedHotspotColors = new int[TOP_HOTSPOT_COUNT];

    private static int fpsColor = EchoTheme.GOOD;
    private static int frameTimeColor = EchoTheme.GOOD;
    private static int tickTimeColor = EchoTheme.GOOD;

    // ============================================================
    // 렌더링
    // ============================================================

    /**
     * HUD 렌더링
     * 렌더 루프에서 호출됨
     */
    public static void render() {
        // 안전 체크
        if (!EchoRuntime.isEnabled() || !EchoKeyBindings.isHudVisible()) {
            return;
        }

        try {
            updateCacheIfNeeded();
            renderHud();
        } catch (Exception e) {
            EchoRuntime.recordError("HUD", e);
        }
    }

    /**
     * 캐시 갱신 (0.5초마다)
     */
    private static void updateCacheIfNeeded() {
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
    private static void updateHotspots(EchoProfiler profiler) {
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

    /**
     * HUD 렌더링 (PZ UI API 사용)
     */
    private static void renderHud() {
        // 배경 박스 크기 계산
        int lineCount = 4; // FPS, Frame, Tick, Status
        for (String hotspot : cachedHotspots) {
            if (hotspot != null)
                lineCount++;
        }
        int boxWidth = 150;
        int boxHeight = PADDING * 2 + lineCount * LINE_HEIGHT;

        // 배경 렌더링 (PZ API 호출 - 실제 구현은 PZ 환경에서)
        drawRect(hudX, hudY, boxWidth, boxHeight, EchoTheme.getBackground());

        // 텍스트 렌더링
        int y = hudY + PADDING;

        // FPS
        drawText(cachedFpsText, hudX + PADDING, y, fpsColor);
        // 프로파일링 상태 (오른쪽)
        int statusColor = cachedProfileStatus.equals("[ON]") ? EchoTheme.GOOD : EchoTheme.TEXT_SECONDARY;
        drawText(cachedProfileStatus, hudX + boxWidth - PADDING - 30, y, statusColor);
        y += LINE_HEIGHT;

        // Frame Time
        drawText(cachedFrameTimeText, hudX + PADDING, y, frameTimeColor);
        y += LINE_HEIGHT;

        // Tick Time
        drawText(cachedTickTimeText, hudX + PADDING, y, tickTimeColor);
        y += LINE_HEIGHT;

        // 구분선
        y += 2;

        // Hotspots
        for (int i = 0; i < TOP_HOTSPOT_COUNT; i++) {
            if (cachedHotspots[i] != null) {
                drawText(cachedHotspots[i], hudX + PADDING, y, cachedHotspotColors[i]);
                y += LINE_HEIGHT;
            }
        }
    }

    // ============================================================
    // PZ 렌더링 API 래퍼 (실제 구현은 PZ 환경에서)
    // ============================================================

    /**
     * 사각형 그리기 (ARGB 색상)
     */
    private static void drawRect(int x, int y, int width, int height, int argbColor) {
        // Project Zomboid API 호출:
        // UIManager.DrawRect(...) 또는 IndieGL 사용
        // 개발 환경에서는 no-op
        try {
            Class<?> uiManager = Class.forName("zombie.ui.UIManager");
            java.lang.reflect.Method drawRect = uiManager.getMethod(
                    "DrawRect", int.class, int.class, int.class, int.class,
                    float.class, float.class, float.class, float.class);
            float a = ((argbColor >> 24) & 0xFF) / 255f;
            float r = ((argbColor >> 16) & 0xFF) / 255f;
            float g = ((argbColor >> 8) & 0xFF) / 255f;
            float b = (argbColor & 0xFF) / 255f;
            drawRect.invoke(null, x, y, width, height, r, g, b, a);
        } catch (Exception e) {
            // 개발 환경 - 무시
        }
    }

    /**
     * 텍스트 그리기
     */
    private static void drawText(String text, int x, int y, int rgbColor) {
        // Project Zomboid API 호출:
        // TextManager.DrawString(...) 사용
        // 개발 환경에서는 no-op
        try {
            Class<?> textManager = Class.forName("zombie.ui.TextManager");
            java.lang.reflect.Method drawString = textManager.getMethod(
                    "DrawString", Object.class, int.class, int.class,
                    float.class, float.class, float.class, float.class);
            float r = ((rgbColor >> 16) & 0xFF) / 255f;
            float g = ((rgbColor >> 8) & 0xFF) / 255f;
            float b = (rgbColor & 0xFF) / 255f;
            drawString.invoke(null, text, x, y, r, g, b, 1.0f);
        } catch (Exception e) {
            // 개발 환경 - 무시
        }
    }

    // ============================================================
    // 유틸리티
    // ============================================================

    /**
     * 문자열 자르기
     */
    private static String truncate(String str, int maxLen) {
        if (str == null)
            return "";
        if (str.length() <= maxLen)
            return str;
        return str.substring(0, maxLen - 1) + "…";
    }

    /**
     * ProfilingPoint별 색상
     */
    private static int getPointColor(ProfilingPoint point) {
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

    public static void setPosition(int x, int y) {
        hudX = x;
        hudY = y;
    }

    public static int getX() {
        return hudX;
    }

    public static int getY() {
        return hudY;
    }
}
