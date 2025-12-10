package com.echo.ui;

import com.echo.EchoRuntime;
import com.echo.input.EchoKeyBindings;
import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;
import com.echo.aggregate.TimingData;
import com.echo.aggregate.SpikeLog;

import com.pulse.ui.HUDOverlay;
import com.pulse.ui.UIRenderContext;
import com.pulse.api.lua.LuaBudgetManager;
import com.pulse.api.lua.LuaBudgetManager.LuaBudgetStats;

import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;

/**
 * HotspotPanel - 상세 성능 분석 패널
 * 
 * Pulse HUDOverlay 시스템을 통해 렌더링됩니다.
 * F8 키로 토글할 수 있습니다.
 * 5초/60초 윈도우 핫스팟, 스파이크 로그, Lua 상태를 표시합니다.
 * 
 * @since 2.0.0 - Pulse Native Integration
 */
public class HotspotPanel extends HUDOverlay.HUDLayer {

    // ============================================================
    // 상수
    // ============================================================

    /** 패널 레이어 ID */
    public static final String LAYER_ID = "echo_hotspot_panel";

    /** 패널 레이어 우선순위 (EchoHUD보다 위에 렌더링) */
    public static final int LAYER_PRIORITY = 110;

    /** 패널 갱신 주기 (밀리초) */
    private static final long UPDATE_INTERVAL_MS = 1000; // 1초마다 정렬

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
    // 싱글톤 인스턴스
    // ============================================================

    private static HotspotPanel INSTANCE;

    // ============================================================
    // 인스턴스 필드
    // ============================================================

    /** 패널 위치 */
    private int panelX = 170;
    private int panelY = 10;

    // ============================================================
    // 캐시
    // ============================================================

    private long lastCacheUpdate = 0;

    // 5초 윈도우 핫스팟
    private final String[] cached5sHotspots = new String[TOP_N];
    private final int[] cached5sColors = new int[TOP_N];
    private int cached5sCount = 0;

    // 60초 윈도우 핫스팟
    private final String[] cached60sHotspots = new String[TOP_N];
    private final int[] cached60sColors = new int[TOP_N];
    private int cached60sCount = 0;

    // 스파이크 로그
    private final String[] cachedSpikes = new String[SPIKE_COUNT];
    private int cachedSpikeCount = 0;

    // Lua 상태
    private final String[] cachedLuaTop = new String[LUA_TOP_N];
    private int cachedLuaCount = 0;
    private String cachedLuaSummary = "";

    // ============================================================
    // 생성자 및 등록
    // ============================================================

    private HotspotPanel() {
        // Private constructor for singleton
    }

    /**
     * 패널 레이어 등록
     * EchoMod.init()에서 호출됨
     */
    public static void register() {
        if (INSTANCE != null) {
            System.out.println("[Echo] HotspotPanel already registered");
            return;
        }

        INSTANCE = new HotspotPanel();
        HUDOverlay.registerLayer(LAYER_ID, INSTANCE, LAYER_PRIORITY);
        System.out.println("[Echo] HotspotPanel registered as Pulse HUD layer");
    }

    /**
     * 패널 레이어 등록 해제
     */
    public static void unregister() {
        if (INSTANCE == null)
            return;
        HUDOverlay.unregisterLayer(LAYER_ID);
        INSTANCE = null;
        System.out.println("[Echo] HotspotPanel unregistered");
    }

    /**
     * 인스턴스 가져오기
     */
    public static HotspotPanel getInstance() {
        return INSTANCE;
    }

    // ============================================================
    // HUDLayer 구현
    // ============================================================

    @Override
    public void render(UIRenderContext ctx) {
        // F8 토글 체크 - HUDLayer.setVisible() 대신 KeyBindings 확인
        if (!EchoRuntime.isEnabled() || !EchoKeyBindings.isPanelVisible()) {
            return;
        }

        try {
            updateCacheIfNeeded();
            renderPanel(ctx);
        } catch (Exception e) {
            EchoRuntime.recordError("Panel", e);
        }
    }

    @Override
    public void update(float deltaTime) {
        // Panel은 render에서 캐시 갱신하므로 별도 업데이트 불필요
    }

    // ============================================================
    // 캐시 갱신
    // ============================================================

    /**
     * 캐시 갱신 (1초마다)
     */
    private void updateCacheIfNeeded() {
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
    private void updateHotspots(EchoProfiler profiler, boolean is5s) {
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

                // 전체 시간 대비 비율 계산: use EchoProfiler session time instead of deprecated
                // getWindowMs()
                long sessionMs = Math.max(1, EchoProfiler.getInstance().getSessionDurationMs());
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
    private void updateSpikes(EchoProfiler profiler) {
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
     * Pulse LuaBudgetManager에서 통계를 가져옴 (Phase 4 Native Integration)
     */
    private void updateLuaStats() {
        try {
            LuaBudgetManager budget = LuaBudgetManager.getInstance();

            // 주요 컨텍스트의 통계 수집
            LuaBudgetStats tickStats = budget.getStats(LuaBudgetManager.CTX_ON_TICK);

            // 요약 정보
            cachedLuaSummary = String.format("Avg: %.2fms / Exceeded: %d",
                    tickStats.avgExecutionMicros / 1000.0,
                    tickStats.budgetExceededCount);

            // 컨텍스트별 상세 정보
            String[] contexts = {
                    LuaBudgetManager.CTX_ON_TICK,
                    LuaBudgetManager.CTX_ON_PLAYER_UPDATE,
                    LuaBudgetManager.CTX_ON_RENDER_TICK
            };

            cachedLuaCount = 0;
            for (int i = 0; i < LUA_TOP_N && i < contexts.length; i++) {
                LuaBudgetStats stats = budget.getStats(contexts[i]);
                if (stats.totalExecutions > 0) {
                    String contextName = contexts[i].replace("lua.event.", "");
                    cachedLuaTop[i] = String.format("%-14s %5.1fms max",
                            truncate(contextName, 14),
                            stats.maxExecutionMicros / 1000.0);
                    cachedLuaCount++;
                } else {
                    cachedLuaTop[i] = null;
                }
            }
        } catch (Exception e) {
            // LuaBudgetManager 사용 불가 시 폴백
            cachedLuaSummary = "Lua stats unavailable";
            cachedLuaCount = 0;
        }
    }

    // ============================================================
    // 렌더링 (UIRenderContext 사용)
    // ============================================================

    /**
     * 패널 렌더링 (Pulse UI API 사용)
     */
    private void renderPanel(UIRenderContext ctx) {
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
        ctx.fillRect(panelX, panelY, PANEL_WIDTH, totalHeight, EchoTheme.getBackgroundRGB(),
                EchoTheme.getBackgroundAlpha());

        y += PADDING;

        // === Last 5 Seconds ===
        ctx.drawText("━━ Last 5 Seconds ━━", panelX + PADDING, y, EchoTheme.TEXT_HIGHLIGHT);
        y += LINE_HEIGHT;

        for (int i = 0; i < cached5sCount; i++) {
            if (cached5sHotspots[i] != null) {
                ctx.drawText(cached5sHotspots[i], panelX + PADDING, y, cached5sColors[i]);
                y += LINE_HEIGHT;
            }
        }

        y += SECTION_GAP;

        // === Last 60 Seconds ===
        ctx.drawText("━━ Last 60 Seconds ━━", panelX + PADDING, y, EchoTheme.TEXT_HIGHLIGHT);
        y += LINE_HEIGHT;

        for (int i = 0; i < cached60sCount; i++) {
            if (cached60sHotspots[i] != null) {
                ctx.drawText(cached60sHotspots[i], panelX + PADDING, y, cached60sColors[i]);
                y += LINE_HEIGHT;
            }
        }

        y += SECTION_GAP;

        // === Recent Spikes ===
        ctx.drawText("━━ Recent Spikes ━━", panelX + PADDING, y, EchoTheme.TEXT_HIGHLIGHT);
        y += LINE_HEIGHT;

        if (cachedSpikeCount == 0) {
            ctx.drawText("No spikes recorded", panelX + PADDING, y, EchoTheme.TEXT_SECONDARY);
            y += LINE_HEIGHT;
        } else {
            for (int i = 0; i < cachedSpikeCount; i++) {
                if (cachedSpikes[i] != null) {
                    int spikeColor = i == 0 ? EchoTheme.CRITICAL : EchoTheme.WARNING;
                    ctx.drawText(cachedSpikes[i], panelX + PADDING, y, spikeColor);
                    y += LINE_HEIGHT;
                }
            }
        }

        y += SECTION_GAP;

        // === Lua Status ===
        ctx.drawText("━━ Lua Status ━━", panelX + PADDING, y, EchoTheme.TEXT_HIGHLIGHT);
        y += LINE_HEIGHT;

        ctx.drawText(cachedLuaSummary, panelX + PADDING, y, EchoTheme.SUBSYSTEM_LUA);
        y += LINE_HEIGHT;

        for (int i = 0; i < cachedLuaCount; i++) {
            if (cachedLuaTop[i] != null) {
                ctx.drawText(cachedLuaTop[i], panelX + PADDING, y, EchoTheme.SUBSYSTEM_LUA);
                y += LINE_HEIGHT;
            }
        }
    }

    // ============================================================
    // 유틸리티
    // ============================================================

    private String truncate(String str, int maxLen) {
        if (str == null)
            return "";
        if (str.length() <= maxLen)
            return str;
        return str.substring(0, maxLen - 1) + "…";
    }

    private String getBar(double percent) {
        int bars = (int) Math.min(5, percent / 20);
        return "█".repeat(Math.max(0, bars)) + "░".repeat(Math.max(0, 5 - bars));
    }

    private String getSeverityIndicator(double ms) {
        if (ms > 100)
            return "!!!";
        if (ms > 50)
            return "!!";
        if (ms > 33.33)
            return "!";
        return "";
    }

    private int getPointColor(ProfilingPoint point) {
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
    // 설정
    // ============================================================

    public void setPosition(int x, int y) {
        this.panelX = x;
        this.panelY = y;
    }

    public int getX() {
        return panelX;
    }

    public int getY() {
        return panelY;
    }

    // Static 호환성 메서드 (기존 코드 호환)
    public static void setPanelPosition(int x, int y) {
        if (INSTANCE != null) {
            INSTANCE.setPosition(x, y);
        }
    }
}
