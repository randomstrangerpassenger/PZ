package com.echo.ui;

import com.pulse.api.di.PulseServices;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.ui.IUIRenderContext;

/**
 * Echo HUD - 인게임 성능 오버레이.
 * 
 * Phase 4: IHUDOverlay.registerRenderer() 사용.
 * 기본 시스템 정보만 표시 (외부 의존성 최소화).
 * 
 * @since 2.0.0 - Pulse Native Integration
 * @since 4.0.0 - Restored with IHUDOverlay (Phase 4)
 */
public class EchoHUD {

    public static final String LAYER_ID = "echo_hud";
    private static boolean visible = false;
    private static boolean registered = false;

    // HUD 위치
    private static int posX = 10;
    private static int posY = 10;

    // 색상 상수
    private static final int COLOR_WHITE = 0xFFFFFFFF;
    private static final int COLOR_GREEN = 0xFF00FF00;
    private static final int COLOR_YELLOW = 0xFFFFFF00;
    private static final int COLOR_RED = 0xFFFF0000;
    private static final int COLOR_BG = 0x000000;
    private static final float BG_ALPHA = 0.7f;

    private EchoHUD() {
    }

    /**
     * HUD 레이어 등록.
     */
    public static void register() {
        if (registered)
            return;

        try {
            PulseServices.hud().registerRenderer(LAYER_ID, EchoHUD::render);
            registered = true;
            PulseLogger.info("Echo", "EchoHUD registered (Phase 4 - IHUDOverlay)");
        } catch (IllegalStateException e) {
            PulseLogger.warn("Echo", "EchoHUD registration failed: PulseServices not initialized");
        } catch (Exception e) {
            PulseLogger.error("Echo", "EchoHUD registration failed: " + e.getMessage());
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

        int lineHeight = 16;
        int padding = 5;
        int width = 200;
        int height = lineHeight * 4 + padding * 2;

        // 배경
        ctx.fillRect(posX, posY, width, height, COLOR_BG, BG_ALPHA);

        int y = posY + padding;
        ctx.drawText("═══ Echo Profiler ═══", posX + padding, y, COLOR_WHITE);
        y += lineHeight;

        // 메모리
        Runtime rt = Runtime.getRuntime();
        long usedMB = (rt.totalMemory() - rt.freeMemory()) / (1024 * 1024);
        long maxMB = rt.maxMemory() / (1024 * 1024);
        int memColor = usedMB < maxMB * 0.7 ? COLOR_GREEN : (usedMB < maxMB * 0.9 ? COLOR_YELLOW : COLOR_RED);
        ctx.drawText(String.format("Memory: %dMB / %dMB", usedMB, maxMB), posX + padding, y, memColor);
        y += lineHeight;

        // 시간
        long time = System.currentTimeMillis() / 1000;
        ctx.drawText("Uptime: " + time + "s", posX + padding, y, COLOR_WHITE);
        y += lineHeight;

        ctx.drawText("Status: Active", posX + padding, y, COLOR_GREEN);
    }

    public static void toggle() {
        visible = !visible;
        PulseLogger.info("Echo", "HUD: " + (visible ? "ON" : "OFF"));
    }

    public static boolean isShown() {
        return visible;
    }

    public static void setPosition(int x, int y) {
        posX = x;
        posY = y;
    }
}
