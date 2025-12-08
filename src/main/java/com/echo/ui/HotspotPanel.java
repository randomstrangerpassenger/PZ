package com.echo.ui;

import com.echo.EchoRuntime;
import com.echo.input.EchoKeyBindings;
import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;
import com.echo.aggregate.TimingData;
import com.echo.aggregate.SpikeLog;
import com.echo.lua.LuaCallTracker;

import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;

/**
 * HotspotPanel - 상세 성능 분석 패널
 * 
 * F8 키로 토글할 수 있습니다.
 * 5초/60초 윈도우 핫스팟, 스파이크 로그, Lua 상태를 표시합니다.
 */
public class HotspotPanel {

    // ============================================================
    // 상수
    // ============================================================

    /** 패널 갱신 주기 (밀리초) */
    private static final long UPDATE_INTERVAL_MS = 1000; // 1초마다 정렬

    /** 패널 위치 */
    private static int panelX = 170;
    private static int panelY = 10;

    /** 패널 크기 */
    private static final int PANEL_WIDTH = 280;
    private static final int PADDING = 8;
    private static final int LINE_HEIGHT = 14;
    private static final int SECTION_GAP = 6;

    /** Top N 개수 */
    private static final int TOP_N = 5;
    private static final int SPIKE_COUNT = 3;
    private static final int LUA_TOP_N = 3;

    // 시간 포맷
    private static final DateTimeFormatter TIME_FORMAT = DateTimeFormatter.ofPattern("HH:mm:ss");

    // ============================================================
    // 캐시
    // ============================================================

    private static long lastCacheUpdate = 0;

    // 5초 윈도우 핫스팟
    private static String[] cached5sHotspots = new String[TOP_N];
    private static int[] cached5sColors = new int[TOP_N];
    private static int cached5sCount = 0;

    // 60초 윈도우 핫스팟
    private static String[] cached60sHotspots = new String[TOP_N];
    private static int[] cached60sColors = new int[TOP_N];
    private static int cached60sCount = 0;

    // 스파이크 로그
    private static String[] cachedSpikes = new String[SPIKE_COUNT];
    private static int cachedSpikeCount = 0;

    // Lua 상태 (Phase 3-2)
    private static String[] cachedLuaTop = new String[LUA_TOP_N];
    private static int cachedLuaCount = 0;
    private static String cachedLuaSummary = "";

    // ============================================================
    // 렌더링
    // ============================================================

    /**
     * 패널 렌더링
     * 렌더 루프에서 호출됨
     */
    public static void render() {
        if (!EchoRuntime.isEnabled() || !EchoKeyBindings.isPanelVisible()) {
            return;
        }

        try {
            updateCacheIfNeeded();
            renderPanel();
        } catch (Exception e) {
            EchoRuntime.recordError("Panel", e);
        }
    }

    /**
     * 캐시 갱신 (1초마다)
     */
    private static void updateCacheIfNeeded() {
        long now = System.currentTimeMillis();
        if (now - lastCacheUpdate < UPDATE_INTERVAL_MS) {
            return;
        }
        lastCacheUpdate = now;

        EchoProfiler profiler = EchoProfiler.getInstance();
        if (!profiler.isEnabled()) {
            cached5sCount = 0;
            cached60sCount = 0;
            cachedSpikeCount = 0;
            cachedLuaCount = 0;
            return;
        }

        // 5초 윈도우 핫스팟
        updateHotspots(profiler, true);

        // 60초 윈도우 핫스팟
        updateHotspots(profiler, false);

        // 스파이크 로그
        updateSpikes(profiler);

        // Lua 상태
        updateLuaStats();
    }

    /**
     * 핫스팟 갱신
     */
    private static void updateHotspots(EchoProfiler profiler, boolean is5s) {
        Map<ProfilingPoint, TimingData> allData = profiler.getTimingData();

        List<Map.Entry<ProfilingPoint, TimingData>> sorted = allData.entrySet().stream()
                .filter(e -> e.getValue().getCallCount() > 0)
                .sorted((a, b) -> {
                    double avgA = is5s ? a.getValue().getStats5s().getAverage()
                            : a.getValue().getStats60s().getAverage();
                    double avgB = is5s ? b.getValue().getStats5s().getAverage()
                            : b.getValue().getStats60s().getAverage();
                    return Double.compare(avgB, avgA);
                })
                .limit(TOP_N)
                .toList();

        String[] hotspots = is5s ? cached5sHotspots : cached60sHotspots;
        int[] colors = is5s ? cached5sColors : cached60sColors;
        int count = Math.min(sorted.size(), TOP_N);

        for (int i = 0; i < TOP_N; i++) {
            if (i < count) {
                Map.Entry<ProfilingPoint, TimingData> entry = sorted.get(i);
                ProfilingPoint point = entry.getKey();
                TimingData data = entry.getValue();

                double avgMs = (is5s ? data.getStats5s().getAverage() : data.getStats60s().getAverage()) / 1000.0;
                long total = data.getTotalMicros() / 1000; // total ms

                // 전체 시간 대비 비율 계산
                long sessionMs = Math.max(1, (System.currentTimeMillis() - data.getStats1s().getWindowMs()) / 1000);
                double percent = Math.min(100, (total * 100.0) / sessionMs);

                hotspots[i] = String.format("%-12s %5.1fms %4.0f%% %s",
                        truncate(point.name(), 12),
                        avgMs,
                        percent,
                        getBar(percent));
                colors[i] = getPointColor(point);
            } else {
                hotspots[i] = null;
            }
        }

        if (is5s) {
            cached5sCount = count;
        } else {
            cached60sCount = count;
        }
    }

    /**
     * 스파이크 로그 갱신
     */
    private static void updateSpikes(EchoProfiler profiler) {
        SpikeLog spikeLog = profiler.getSpikeLog();
        List<SpikeLog.SpikeEntry> recent = spikeLog.getRecentSpikes(SPIKE_COUNT);

        cachedSpikeCount = Math.min(recent.size(), SPIKE_COUNT);

        for (int i = 0; i < SPIKE_COUNT; i++) {
            if (i < cachedSpikeCount) {
                SpikeLog.SpikeEntry spike = recent.get(i);
                String time = TIME_FORMAT.format(spike.getTimestamp().atZone(java.time.ZoneId.systemDefault()));
                String severity = getSeverityIndicator(spike.getDurationMs());

                cachedSpikes[i] = String.format("%s %-10s %5.0fms %s",
                        time,
                        truncate(spike.getPoint().name(), 10),
                        spike.getDurationMs(),
                        severity);
            } else {
                cachedSpikes[i] = null;
            }
        }
    }

    /**
     * Lua 상태 갱신
     */
    private static void updateLuaStats() {
        LuaCallTracker tracker = LuaCallTracker.getInstance();

        // 총 Lua 시간
        double totalMs = tracker.getTotalTimeMs();
        long totalCalls = tracker.getTotalCalls();
        cachedLuaSummary = String.format("Total: %.1fms / %d calls", totalMs, totalCalls);

        // Top N 함수
        List<LuaCallTracker.LuaFunctionStats> topFuncs = tracker.getTopFunctionsByTime(LUA_TOP_N);
        cachedLuaCount = Math.min(topFuncs.size(), LUA_TOP_N);

        for (int i = 0; i < LUA_TOP_N; i++) {
            if (i < cachedLuaCount) {
                LuaCallTracker.LuaFunctionStats func = topFuncs.get(i);
                cachedLuaTop[i] = String.format("%-16s %5.1fms",
                        truncate(func.getName(), 16),
                        func.getTotalMs());
            } else {
                cachedLuaTop[i] = null;
            }
        }
    }

    /**
     * 패널 렌더링
     */
    private static void renderPanel() {
        int y = panelY;

        // 전체 높이 계산
        int totalHeight = PADDING * 2;
        totalHeight += LINE_HEIGHT; // 5s 타이틀
        totalHeight += cached5sCount * LINE_HEIGHT;
        totalHeight += SECTION_GAP + LINE_HEIGHT; // 60s 타이틀
        totalHeight += cached60sCount * LINE_HEIGHT;
        totalHeight += SECTION_GAP + LINE_HEIGHT; // Spikes 타이틀
        totalHeight += Math.max(1, cachedSpikeCount) * LINE_HEIGHT;
        totalHeight += SECTION_GAP + LINE_HEIGHT; // Lua 타이틀
        totalHeight += LINE_HEIGHT; // Lua summary
        totalHeight += cachedLuaCount * LINE_HEIGHT;

        // 배경
        drawRect(panelX, panelY, PANEL_WIDTH, totalHeight, EchoTheme.getBackground());

        y += PADDING;

        // === Last 5 Seconds ===
        drawText("━━ Last 5 Seconds ━━", panelX + PADDING, y, EchoTheme.TEXT_HIGHLIGHT);
        y += LINE_HEIGHT;

        for (int i = 0; i < cached5sCount; i++) {
            if (cached5sHotspots[i] != null) {
                drawText(cached5sHotspots[i], panelX + PADDING, y, cached5sColors[i]);
                y += LINE_HEIGHT;
            }
        }

        y += SECTION_GAP;

        // === Last 60 Seconds ===
        drawText("━━ Last 60 Seconds ━━", panelX + PADDING, y, EchoTheme.TEXT_HIGHLIGHT);
        y += LINE_HEIGHT;

        for (int i = 0; i < cached60sCount; i++) {
            if (cached60sHotspots[i] != null) {
                drawText(cached60sHotspots[i], panelX + PADDING, y, cached60sColors[i]);
                y += LINE_HEIGHT;
            }
        }

        y += SECTION_GAP;

        // === Recent Spikes ===
        drawText("━━ Recent Spikes ━━", panelX + PADDING, y, EchoTheme.TEXT_HIGHLIGHT);
        y += LINE_HEIGHT;

        if (cachedSpikeCount == 0) {
            drawText("No spikes recorded", panelX + PADDING, y, EchoTheme.TEXT_SECONDARY);
            y += LINE_HEIGHT;
        } else {
            for (int i = 0; i < cachedSpikeCount; i++) {
                if (cachedSpikes[i] != null) {
                    int spikeColor = i == 0 ? EchoTheme.CRITICAL : EchoTheme.WARNING;
                    drawText(cachedSpikes[i], panelX + PADDING, y, spikeColor);
                    y += LINE_HEIGHT;
                }
            }
        }

        y += SECTION_GAP;

        // === Lua Status ===
        drawText("━━ Lua Status ━━", panelX + PADDING, y, EchoTheme.TEXT_HIGHLIGHT);
        y += LINE_HEIGHT;

        drawText(cachedLuaSummary, panelX + PADDING, y, EchoTheme.SUBSYSTEM_LUA);
        y += LINE_HEIGHT;

        for (int i = 0; i < cachedLuaCount; i++) {
            if (cachedLuaTop[i] != null) {
                drawText(cachedLuaTop[i], panelX + PADDING, y, EchoTheme.SUBSYSTEM_LUA);
                y += LINE_HEIGHT;
            }
        }
    }

    // ============================================================
    // 유틸리티
    // ============================================================

    private static String truncate(String str, int maxLen) {
        if (str == null)
            return "";
        if (str.length() <= maxLen)
            return str;
        return str.substring(0, maxLen - 1) + "…";
    }

    private static String getBar(double percent) {
        int bars = (int) Math.min(5, percent / 20);
        return "█".repeat(Math.max(0, bars)) + "░".repeat(Math.max(0, 5 - bars));
    }

    private static String getSeverityIndicator(double ms) {
        if (ms > 100)
            return "!!!";
        if (ms > 50)
            return "!!";
        if (ms > 33.33)
            return "!";
        return "";
    }

    private static int getPointColor(ProfilingPoint point) {
        return switch (point) {
            case RENDER, RENDER_WORLD, RENDER_UI -> EchoTheme.SUBSYSTEM_RENDER;
            case ZOMBIE_AI, NPC_AI -> EchoTheme.SUBSYSTEM_AI;
            case PHYSICS, SIMULATION -> EchoTheme.SUBSYSTEM_PHYSICS;
            case NETWORK -> EchoTheme.SUBSYSTEM_NETWORK;
            case LUA_EVENT, LUA_FUNCTION, LUA_GC -> EchoTheme.SUBSYSTEM_LUA;
            case AUDIO -> EchoTheme.SUBSYSTEM_LIGHTING;
            default -> EchoTheme.SUBSYSTEM_OTHER;
        };
    }

    // ============================================================
    // PZ 렌더링 API 래퍼
    // ============================================================

    private static void drawRect(int x, int y, int width, int height, int argbColor) {
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

    private static void drawText(String text, int x, int y, int rgbColor) {
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
    // 설정
    // ============================================================

    public static void setPosition(int x, int y) {
        panelX = x;
        panelY = y;
    }

    public static int getX() {
        return panelX;
    }

    public static int getY() {
        return panelY;
    }
}
