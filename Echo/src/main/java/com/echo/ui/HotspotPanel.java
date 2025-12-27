package com.echo.ui;

import com.pulse.api.di.PulseServices;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.ui.IUIRenderContext;

/**
 * HotspotPanel - 성능 핫스팟 패널.
 * 
 * Phase 4: IHUDOverlay.registerRenderer() 사용.
 * 기본 성능 정보만 표시.
 * 
 * @since 2.0.0 - Pulse Native Integration
 * @since 4.0.0 - Restored with IHUDOverlay (Phase 4)
 */
public class HotspotPanel {

    public static final String LAYER_ID = "echo_hotspot_panel";
    private static boolean visible = false;
    private static boolean registered = false;

    private static int posX = 250;
    private static int posY = 10;

    private static final int COLOR_WHITE = 0xFFFFFFFF;
    private static final int COLOR_CYAN = 0xFF00FFFF;
    private static final int COLOR_BG = 0x000000;
    private static final float BG_ALPHA = 0.8f;

    private HotspotPanel() {
    }

    public static void register() {
        if (registered)
            return;

        try {
            PulseServices.hud().registerRenderer(LAYER_ID, HotspotPanel::render);
            registered = true;
            PulseLogger.info("Echo", "HotspotPanel registered (Phase 4)");
        } catch (Exception e) {
            PulseLogger.warn("Echo", "HotspotPanel registration failed");
        }
    }

    public static void unregister() {
        if (!registered)
            return;
        try {
            PulseServices.hud().unregisterRenderer(LAYER_ID);
            registered = false;
        } catch (Exception e) {
            // Ignore
        }
    }

    private static void render(IUIRenderContext ctx) {
        if (!visible)
            return;

        int lineHeight = 14;
        int padding = 5;
        int width = 220;
        int height = lineHeight * 3 + padding * 2;

        ctx.fillRect(posX, posY, width, height, COLOR_BG, BG_ALPHA);

        int y = posY + padding;
        ctx.drawText("═══ Hotspot Panel ═══", posX + padding, y, COLOR_CYAN);
        y += lineHeight;

        ctx.drawText("Status: Monitoring", posX + padding, y, COLOR_WHITE);
        y += lineHeight;

        // 스레드 수
        int threadCount = Thread.activeCount();
        ctx.drawText("Active Threads: " + threadCount, posX + padding, y, COLOR_WHITE);
    }

    public static void toggle() {
        visible = !visible;
        PulseLogger.info("Echo", "HotspotPanel: " + (visible ? "ON" : "OFF"));
    }

    public static boolean isShown() {
        return visible;
    }

    public static void setPanelPosition(int x, int y) {
        posX = x;
        posY = y;
    }

    public static int getPositionX() {
        return posX;
    }

    public static int getPositionY() {
        return posY;
    }
}
