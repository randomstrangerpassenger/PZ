package com.echo.ui;

import com.echo.EchoRuntime;
import com.echo.analysis.BottleneckDetector;
import com.echo.analysis.BottleneckDetector.*;
import com.echo.measure.*;

import com.pulse.ui.HUDOverlay;
import com.pulse.ui.UIRenderContext;

import java.util.*;

/**
 * Echo 확장 HUD - 추가 메트릭 표시
 * 
 * 병목 진단, 네트워크, 메모리 트렌드 등 고급 정보를 표시합니다.
 * F7 키로 토글할 수 있습니다.
 * 
 * @since 2.1.0
 */
public class EchoExtendedHUD extends HUDOverlay.HUDLayer {

    public static final String LAYER_ID = "echo_extended_hud";
    public static final int LAYER_PRIORITY = 101;

    private static final long UPDATE_INTERVAL_MS = 1000;
    private static final int PADDING = 6;
    private static final int LINE_HEIGHT = 14;
    private static final int BOX_WIDTH = 200;

    private static EchoExtendedHUD INSTANCE;
    private static boolean visible = false;

    private int hudX = 170;
    private int hudY = 10;

    private long lastCacheUpdate = 0;

    // 캐시된 값들
    private String cachedMemoryText = "Mem: --";
    private String cachedGcText = "GC: --";
    private String cachedNetworkText = "Net: --";
    private String cachedRenderText = "Render: --";
    private String cachedTopBottleneck = "Bottleneck: None";
    private String cachedBottleneckHint = "";

    private int memoryColor = EchoTheme.GOOD;
    private int networkColor = EchoTheme.GOOD;
    private int renderColor = EchoTheme.GOOD;
    private int bottleneckColor = EchoTheme.TEXT_SECONDARY;

    private EchoExtendedHUD() {
    }

    public static void register() {
        if (INSTANCE != null)
            return;

        INSTANCE = new EchoExtendedHUD();
        HUDOverlay.registerLayer(LAYER_ID, INSTANCE, LAYER_PRIORITY);
        System.out.println("[Echo] Extended HUD registered (F7 to toggle)");
    }

    public static void unregister() {
        if (INSTANCE == null)
            return;
        HUDOverlay.unregisterLayer(LAYER_ID);
        INSTANCE = null;
    }

    public static EchoExtendedHUD getInstance() {
        return INSTANCE;
    }

    public static void toggle() {
        visible = !visible;
        System.out.println("[Echo] Extended HUD: " + (visible ? "ON" : "OFF"));
    }

    public static boolean isShown() {
        return visible;
    }

    @Override
    public void render(UIRenderContext ctx) {
        if (!EchoRuntime.isEnabled() || !visible) {
            return;
        }

        try {
            updateCacheIfNeeded();
            renderExtendedHud(ctx);
        } catch (Exception e) {
            EchoRuntime.recordError("ExtendedHUD", e);
        }
    }

    @Override
    public void update(float deltaTime) {
    }

    private void updateCacheIfNeeded() {
        long now = System.currentTimeMillis();
        if (now - lastCacheUpdate < UPDATE_INTERVAL_MS)
            return;
        lastCacheUpdate = now;

        // 메모리
        double heapPercent = MemoryProfiler.getHeapUsagePercent();
        long gcCount = MemoryProfiler.getTotalGcCount();
        cachedMemoryText = String.format("Mem: %.0f%%", heapPercent);
        cachedGcText = String.format("GC: %d", gcCount);
        memoryColor = heapPercent > 85 ? EchoTheme.CRITICAL : heapPercent > 70 ? EchoTheme.WARNING : EchoTheme.GOOD;

        // 네트워크
        NetworkMetrics net = NetworkMetrics.getInstance();
        NetworkMetrics.ConnectionQuality quality = net.getConnectionQuality();
        cachedNetworkText = String.format("Net: %.0fms (%s)",
                net.getAvgPingMs(), qualityToShort(quality));
        networkColor = quality == NetworkMetrics.ConnectionQuality.POOR ? EchoTheme.CRITICAL
                : quality == NetworkMetrics.ConnectionQuality.FAIR ? EchoTheme.WARNING : EchoTheme.GOOD;

        // 렌더링
        RenderMetrics render = RenderMetrics.getInstance();
        RenderMetrics.RenderEfficiency efficiency = render.getRenderEfficiency();
        cachedRenderText = String.format("DC: %.0f B:%.0f%%",
                render.getAvgDrawCallsPerFrame(), render.getBatchingEfficiency());
        renderColor = efficiency == RenderMetrics.RenderEfficiency.POOR ? EchoTheme.CRITICAL
                : efficiency == RenderMetrics.RenderEfficiency.FAIR ? EchoTheme.WARNING : EchoTheme.GOOD;

        // 병목
        List<Bottleneck> bottlenecks = BottleneckDetector.getInstance().identifyTopN(1);
        if (!bottlenecks.isEmpty()) {
            Bottleneck top = bottlenecks.get(0);
            cachedTopBottleneck = String.format("⚠ %s (%.1f%%)",
                    shortenName(top.displayName), top.ratio * 100);
            cachedBottleneckHint = top.suggestedModule == OptimizationModule.FUSE ? "→ Fuse target" : "→ Nerve target";
            bottleneckColor = top.priority > 70 ? EchoTheme.CRITICAL
                    : top.priority > 40 ? EchoTheme.WARNING : EchoTheme.GOOD;
        } else {
            cachedTopBottleneck = "No bottleneck";
            cachedBottleneckHint = "";
            bottleneckColor = EchoTheme.GOOD;
        }
    }

    private void renderExtendedHud(UIRenderContext ctx) {
        int lineCount = 6;
        int boxHeight = PADDING * 2 + lineCount * LINE_HEIGHT;

        // 배경
        ctx.fillRect(hudX, hudY, BOX_WIDTH, boxHeight, EchoTheme.getBackgroundRGB(), EchoTheme.getBackgroundAlpha());

        int y = hudY + PADDING;

        // 헤더
        ctx.drawText("─ Extended ─", hudX + PADDING, y, EchoTheme.TEXT_HIGHLIGHT);
        y += LINE_HEIGHT;

        // 메모리
        ctx.drawText(cachedMemoryText, hudX + PADDING, y, memoryColor);
        ctx.drawText(cachedGcText, hudX + BOX_WIDTH - PADDING - 50, y, EchoTheme.TEXT_SECONDARY);
        y += LINE_HEIGHT;

        // 네트워크
        ctx.drawText(cachedNetworkText, hudX + PADDING, y, networkColor);
        y += LINE_HEIGHT;

        // 렌더링
        ctx.drawText(cachedRenderText, hudX + PADDING, y, renderColor);
        y += LINE_HEIGHT;

        // 병목
        ctx.drawText(cachedTopBottleneck, hudX + PADDING, y, bottleneckColor);
        y += LINE_HEIGHT;

        // 병목 힌트
        if (!cachedBottleneckHint.isEmpty()) {
            ctx.drawText(cachedBottleneckHint, hudX + PADDING + 10, y, EchoTheme.TEXT_SECONDARY);
        }
    }

    private String qualityToShort(NetworkMetrics.ConnectionQuality quality) {
        return switch (quality) {
            case EXCELLENT -> "EX";
            case GOOD -> "OK";
            case FAIR -> "FA";
            case POOR -> "PO";
        };
    }

    private String shortenName(String name) {
        return name.length() > 15 ? name.substring(0, 15) + "…" : name;
    }

    public void setPosition(int x, int y) {
        this.hudX = x;
        this.hudY = y;
    }
}
