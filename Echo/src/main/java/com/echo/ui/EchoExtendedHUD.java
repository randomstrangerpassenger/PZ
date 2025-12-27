package com.echo.ui;

import com.pulse.api.di.PulseServices;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.ui.IUIRenderContext;

/**
 * Echo 확장 HUD - GC 통계 표시.
 * 
 * Phase 4: IHUDOverlay.registerRenderer() 사용.
 * 
 * @since 2.1.0
 * @since 4.0.0 - Restored with IHUDOverlay (Phase 4)
 */
public class EchoExtendedHUD {

    public static final String LAYER_ID = "echo_extended_hud";
    private static boolean visible = false;
    private static boolean registered = false;

    private static int posX = 10;
    private static int posY = 100;

    private static final int COLOR_WHITE = 0xFFFFFFFF;
    private static final int COLOR_MAGENTA = 0xFFFF00FF;
    private static final int COLOR_BG = 0x000000;
    private static final float BG_ALPHA = 0.7f;

    private EchoExtendedHUD() {
    }

    public static void register() {
        if (registered)
            return;

        try {
            PulseServices.hud().registerRenderer(LAYER_ID, EchoExtendedHUD::render);
            registered = true;
            PulseLogger.info("Echo", "EchoExtendedHUD registered (Phase 4)");
        } catch (Exception e) {
            PulseLogger.warn("Echo", "EchoExtendedHUD registration failed");
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
        int width = 200;
        int height = lineHeight * 4 + padding * 2;

        ctx.fillRect(posX, posY, width, height, COLOR_BG, BG_ALPHA);

        int y = posY + padding;
        ctx.drawText("═══ Extended Stats ═══", posX + padding, y, COLOR_MAGENTA);
        y += lineHeight;

        // GC 통계
        long gcCount = getGcCount();
        long gcTime = getGcTimeMs();
        ctx.drawText(String.format("GC: %d runs, %dms", gcCount, gcTime), posX + padding, y, COLOR_WHITE);
        y += lineHeight;

        // Heap
        Runtime rt = Runtime.getRuntime();
        long free = rt.freeMemory() / (1024 * 1024);
        long total = rt.totalMemory() / (1024 * 1024);
        ctx.drawText(String.format("Heap: %dM free / %dM", free, total), posX + padding, y, COLOR_WHITE);
    }

    private static long getGcCount() {
        try {
            long count = 0;
            for (java.lang.management.GarbageCollectorMXBean gc : java.lang.management.ManagementFactory
                    .getGarbageCollectorMXBeans()) {
                count += gc.getCollectionCount();
            }
            return count;
        } catch (Exception e) {
            return 0;
        }
    }

    private static long getGcTimeMs() {
        try {
            long time = 0;
            for (java.lang.management.GarbageCollectorMXBean gc : java.lang.management.ManagementFactory
                    .getGarbageCollectorMXBeans()) {
                time += gc.getCollectionTime();
            }
            return time;
        } catch (Exception e) {
            return 0;
        }
    }

    public static void toggle() {
        visible = !visible;
        PulseLogger.info("Echo", "Extended HUD: " + (visible ? "ON" : "OFF"));
    }

    public static boolean isShown() {
        return visible;
    }

    public static void setPosition(int x, int y) {
        posX = x;
        posY = y;
    }
}
